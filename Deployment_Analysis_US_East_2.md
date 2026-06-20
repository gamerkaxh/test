# Gemma 4 31B Deployment Analysis (US East 2)

## About This Document
- **User Story:** 2748133 - Explore deployment of Gemma model
- **Model:** google/gemma-4-31b-it
- **Sprint:** Cat Digital 2026 | Sprint 12 (Jun 10 - Jun 23)
- **Author:** Sowndarya Kurapati
- **Date:** June 18, 2026
- **Region:** us-east-2 (Ohio)
- **Pricing:** On-Demand

---

## What Is This Model?

Gemma 4 31B is a large language model from Google with 31 billion parameters. It's a dense model (not mixture-of-experts), which means all parameters are active during inference. Here's what we're working with:

| Spec | Value |
|---|---|
| Model | google/gemma-4-31b-it |
| Parameters | 31 Billion (Dense) |
| Size on Disk | ~65 GB (BF16 format) |
| GPU Memory Needed (Full Precision) | ~71 GB |
| GPU Memory Needed (Quantized NVFP4) | ~45 GB |
| Minimum GPU | 1x NVIDIA A100 80GB, or 2x A100 40GB with tensor parallelism |
| Best Serving Engine | vLLM v0.8.0+ |
| Max Context | 256K tokens |
| Where It Lives | JFrog Artifactory (artifacts.cat.com) at `cat-huggingface-repo/models/google/gemma-4-31B-it/` |

---

## How Can We Deploy It Through AEX?

The AEX Model Service (CMAAI-Model-Service workflow) gives us 5 model-type options. Here's how each one stacks up against Gemma 4 31B:

| # | model-type | What It Does | Works for Gemma 4 31B? |
|---|---|---|---|
| 1 | huggingface | Deploys HuggingFace models on AEX workers | Probably not - storage and GPU limits |
| 2 | sagemaker | Deploys to a SageMaker endpoint | Best shot - but has packaging challenges |
| 3 | mlflow | Deploys MLflow models | No - wrong format entirely |
| 4 | pythonpackage | Deploys Python packages | No - wrong format |
| 5 | llmobject | Deploys LLM objects | Maybe - we need to investigate this one |

---

## Option 1: Using the "huggingface" Model Type

This path pulls model files from S3 onto an AEX worker node and loads them into GPU memory. Sounds straightforward, but here's where it breaks down for a 65 GB model:

### What We'd Need to Enter in the Workflow

| Input | Value |
|---|---|
| environment | datahub-dev |
| model-name | gemma-4-31b-it |
| model-version | v1 |
| model-type | huggingface |
| deploy-on-gpu | true |
| artifact-location | s3://pfn-aex-cmaai-mr-s3-bucket-dev/models/google/gemma-4-31b-it/ |
| network-type | non-routable |

### Why It Won't Work for now

| What's Needed | What We Have | The Problem |
|---|---|---|
| 65+ GB storage on worker | 20 GiB (default) | Model literally can't fit |
| 71 GB GPU memory | Unknown - depends on instance | Likely not enough |
| 5-10 min to download from S3 | Unknown timeout | Might get killed before download finishes |
| 2-5 min for model to warm up | Unknown health check timer | Health check may fail before model is ready |
| Fit model in container image | ECR max layer = 52 GB | Model too big for a container layer |

**Bottom line:** This path has too many critical blockers right now. The 20 GiB storage limit alone makes it impossible.

---

## Option 2: Using the "sagemaker" Model Type (Best Bet)

This path packages the model as a tar.gz file, uploads it to S3, and deploys it to a SageMaker endpoint. It has the best chance of working because SageMaker handles the heavy lifting of GPU provisioning and storage.

### What We'd Need to Enter in the Workflow

| Input | Value |
|---|---|
| environment | datahub-dev |
| model-name | gemma-4-31b-it |
| model-version | v1 |
| model-type | sagemaker |
| sagemaker-model-artifact-filename | model.tar.gz |
| sagemaker-requirements-filename | requirements.txt |
| deploy-on-gpu | true |
| artifact-location | s3://pfn-aex-cmaai-mr-s3-bucket-dev/models/google/gemma-4-31b-it/model.tar.gz |
| network-type | routable |

### Can SageMaker Handle It?

| Requirement | SageMaker's Capability | What We Need | Verdict |
|---|---|---|---|
| Package model as tar.gz | S3 multipart upload, no hard size limit | 65 GB tar.gz | Possible, but takes a very long time |
| Storage on the endpoint | Configurable EBS volume | 65+ GB | Good to go |
| GPU instances | ml.g5, ml.p4d, ml.p5 families available | A100 80GB minimum for full precision | Available |
| Cold start time | Takes as long as it takes | 5-15 minutes to load model | Acceptable, just slow |
| Response timeout | 60 seconds max for real-time | Varies by output length | Risky for long outputs |

### What's Still Blocking Us

1. **No staging server** - We need somewhere to download 65 GB from JFrog, compress it, and upload to S3. There's no server set up for this for now.
2. **The tar.gz step is painful** - Safetensors files barely compress at all. Creating a 65 GB tar.gz takes hours and the output is almost the same size.
3. **Can't pick the GPU instance** - The workflow only lets us say "yes GPU" or "no GPU." We can't specify that we need an ml.p4d.24xlarge with A100 GPUs.
4. **No automated JFrog-to-S3 pipeline** - We have to manually move 65 GB from Artifactory to S3, and Lambda can only handle 10 GB max.

### What Would It Cost? (SageMaker - us-east-2 Ohio)

These are the SageMaker instances that could run Gemma 4 31B. Prices are On-Demand per hour.

| Instance | GPUs | GPU Type | Total VRAM | Can It Run the Model? | Parallelism | $/Hour | $/Day | $/Week | $/Month |
|---|---|---|---|---|---|---|---|---|---|
| ml.g5.12xlarge | 4 | NVIDIA A10G | 96 GB | Only if quantized (NVFP4) | TP=4 | $7.09 | $170.16 | $1,191.12 | $5,175.70 |
| ml.g5.48xlarge | 8 | NVIDIA A10G | 192 GB | Yes | TP=4 | $20.36 | $488.64 | $3,420.48 | $14,862.80 |
| ml.p4d.24xlarge | 8 | NVIDIA A100 40GB | 320 GB | Yes | TP=2 | $25.25 | $606.00 | $4,242.00 | $18,433.44 |
| ml.p4de.24xlarge | 8 | NVIDIA A100 80GB | 640 GB | Yes - can fit on 1 GPU | TP=1 | $31.56 | $757.44 | $5,302.08 | $23,041.80 |
| ml.p5.48xlarge | 8 | NVIDIA H100 80GB | 640 GB | Yes - fastest option | TP=1 | $63.29 | $1,518.96 | $10,632.72 | $46,206.08 |

**Best bet for testing:** ml.p4d.24xlarge at $25.25/hr gives us plenty of VRAM without breaking the bank.

---

## Option 3: SageMaker JumpStart (Skips AEX Entirely)

 Gemma 4 models have been available in SageMaker JumpStart since April 2026. This means we can deploy directly from SageMaker Studio without any manual packaging - JumpStart handles everything.

The catch? It bypasses the AEX pipeline completely, so it doesn't help us understand what AEX needs to fix.

| What's Good | What's Not |
|---|---|
| No tar.gz needed - JumpStart handles artifacts | Not managed through CMAAI-Model-Service |
| Deploy with a few clicks or SDK calls | Doesn't integrate with our existing workflow |
| Same pricing as Option 2 above | Separate from AEX monitoring/management |

**Use this for:** Quick proof that the model actually works on our infrastructure. Good for dev/testing right now.

---

## Option 4: Self-Hosted on EC2 with GPU (Also Skips AEX)

This is the DIY approach - spin up a GPU instance, install vLLM, download the model, and serve it yourself. It's the cheapest option but you're responsible for everything.

### EC2 GPU Pricing (us-east-2 Ohio, On-Demand)

| Instance | GPUs | GPU Type | Total VRAM | Can Run? | Parallelism | $/Hour | $/Day | $/Week | $/Month |
|---|---|---|---|---|---|---|---|---|---|
| g6.12xlarge | 4 | NVIDIA L4 | 96 GB | Only quantized (NVFP4) | TP=4 | $4.6016 | $110.44 | $773.07 | $3,359.17 |
| g6.48xlarge | 8 | NVIDIA L4 | 192 GB | Yes | TP=4 | $13.3504 | $320.41 | $2,242.87 | $9,745.79 |
| g5.12xlarge | 4 | NVIDIA A10G | 96 GB | Tight - quantization helps | TP=4 | $5.672 | $136.13 | $952.90 | $4,140.56 |
| g5.48xlarge | 8 | NVIDIA A10G | 192 GB | Yes | TP=4 | $16.288 | $390.91 | $2,736.38 | $11,890.24 |
| p4d.24xlarge | 8 | NVIDIA A100 40GB | 320 GB | Yes | TP=2 | $21.9576 | $527.00 | $3,688.88 | $16,029.05 |
| p4de.24xlarge | 8 | NVIDIA A100 80GB | 640 GB | Yes - single GPU | TP=1 | $27.4471 | $658.73 | $4,611.11 | $20,036.38 |
| p5.48xlarge | 8 | NVIDIA H100 80GB | 640 GB | Yes - fastest | TP=1 | $55.04 | $1,320.96 | $9,246.72 | $40,179.20 |

**Cheapest viable:** g6.12xlarge at $4.60/hr (but requires quantizing the model first).

---

## Option 5: Amazon Bedrock

Short answer: **Not possible.** Bedrock only supports Gemma v3, not Gemma 4. No timeline for when (or if) Gemma 4 will be added.

---

## Full Cost Comparison (Ranked Cheapest to Most Expensive)

| Rank | Path | Through AEX? | Instance | GPU Config | $/Hour | $/Week | $/Month | Works for now? |
|---|---|---|---|---|---|---|---|---|
| 1 | EC2 Self-Hosted | No | g6.12xlarge | 4x L4 (96GB) | $4.60 | $773 | $3,359 | Yes (manual) |
| 2 | EC2 Self-Hosted | No | g5.12xlarge | 4x A10G (96GB) | $5.67 | $953 | $4,141 | Yes (manual) |
| 3 | AEX SageMaker | Yes | ml.g5.12xlarge | 4x A10G (96GB) | $7.09 | $1,191 | $5,176 | Likely |
| 4 | EC2 Self-Hosted | No | g6.48xlarge | 8x L4 (192GB) | $13.35 | $2,243 | $9,746 | Yes (manual) |
| 5 | EC2 Self-Hosted | No | g5.48xlarge | 8x A10G (192GB) | $16.29 | $2,736 | $11,890 | Yes (manual) |
| 6 | AEX SageMaker | Yes | ml.g5.48xlarge | 8x A10G (192GB) | $20.36 | $3,420 | $14,863 | Likely |
| 7 | EC2 Self-Hosted | No | p4d.24xlarge | 8x A100-40GB | $21.96 | $3,689 | $16,029 | Yes |
| 8 | AEX SageMaker | Yes | ml.p4d.24xlarge | 8x A100-40GB | $25.25 | $4,242 | $18,433 | Yes |
| 9 | EC2 Self-Hosted | No | p4de.24xlarge | 8x A100-80GB | $27.45 | $4,611 | $20,036 | Yes |
| 10 | AEX SageMaker | Yes | ml.p4de.24xlarge | 8x A100-80GB | $31.56 | $5,302 | $23,042 | Yes |
| 11 | EC2 Self-Hosted | No | p5.48xlarge | 8x H100-80GB | $55.04 | $9,247 | $40,179 | Yes |
| 12 | AEX SageMaker | Yes | ml.p5.48xlarge | 8x H100-80GB | $63.29 | $10,633 | $46,206 | Yes |

---

## What's Stopping Us? (Gap Analysis)

Here's everything that's preventing a smooth deployment through AEX for now:

| # | The Problem | Where It Stands Now | What We Need | How Bad Is It |
|---|---|---|---|---|
| 1 | Worker storage way too small | 20 GiB default | 100+ GiB | Critical - can't even start |
| 2 | No way to move files from JFrog to S3 | Manual download only | Automated pipeline for 65+ GB | Critical - blocks everything |
| 3 | Container image layer too small | 52 GB max (AWS hard limit) | Need to pull model at runtime from S3 | High - architectural change needed |
| 4 | Can't pick GPU instance type | Workflow just has a true/false flag | Need to select ml.p4d, ml.g5, etc. | High - simple workflow fix |
| 5 | No tensor parallelism setting | Not configurable anywhere | Need TP=1,2,4,8 options | Medium - needed for multi-GPU |
| 6 | Health checks timeout before model loads | Unknown timeout (probably < 5 min) | Need 10-15 min for large models | Medium - config change |
| 7 | No quantization option | Not available | NVFP4 would shrink model from 65 to ~20 GB | Low priority but would solve a lot |

---

## Possible Solutions to Deploy Gemma 4 31B with AEX

After researching extensively, here are 4 confirmed approaches that can make Gemma 4 31B deployment work through the AEX pipeline at justifiable cost.

### Solution 1: SageMaker Uncompressed Model Deployment (Skip the tar.gz)

The biggest blocker we identified was having to package 65 GB into a tar.gz file. Turns out, **SageMaker supports deploying models directly from S3 without any compression.**

AWS calls this "Deploying Uncompressed Models" and it works by setting `CompressionType: None` with `S3DataType: S3Prefix` in the `S3ModelDataSource` configuration.

**How it works:**
1. Upload the raw model files (safetensors, config.json, etc.) to an S3 prefix
2. Point SageMaker to that S3 prefix
3. SageMaker automatically downloads them to `/opt/ml/model` on the endpoint instance

**What this means for AEX:**
- Eliminates the entire tar.gz packaging step
- No staging server needed for compression
- Just need to get files from JFrog → S3 (which we solve with an ECS transfer task)
- The CMAAI workflow needs a small code change to pass `CompressionType: None`

**Source:** [AWS Official Documentation - Deploying Uncompressed Models](https://docs.aws.amazon.com/sagemaker/latest/dg/large-model-inference-uncompressed.html)

---

### Solution 2: Use the NVFP4 Quantized Model (~20 GB instead of 65 GB)

NVIDIA maintains an official quantized version of Gemma 4 31B called `nvidia/Gemma-4-31B-IT-NVFP4`. This shrinks the model dramatically while keeping quality nearly identical.

| Spec | Full Model | NVFP4 Quantized |
|---|---|---|
| Size on disk | ~65 GB | ~20 GB |
| GPU VRAM needed | ~71 GB | ~45 GB |
| Quality loss | Baseline | 1-3% degradation |
| Minimum GPU | 1x A100 80GB | 4x A10G with TP=4 (96 GB total) |

**Why this is a game-changer for AEX:**
- 20 GB is much easier to transfer, store, and deploy
- Fits comfortably within increased ECS ephemeral storage (even 50 GiB would work)
- Tar.gz of 20 GB is practical (if still needed for older workflow path)
- Makes the cheapest instances viable (ml.g5.12xlarge at $7.09/hr)

**Important note:** Native NVFP4 execution requires Blackwell-architecture GPUs (sm_120+). On A10G/A100 GPUs, the model still runs but may use a slightly different precision path. This needs testing.

**Source:** [nvidia/Gemma-4-31B-IT-NVFP4 on HuggingFace](https://huggingface.co/nvidia/Gemma-4-31B-IT-NVFP4)

---

### Solution 3: SageMaker Async Inference with Scale-to-Zero (Pay Only When Testing)

For dev and testing, there's no reason to keep a $25/hr GPU instance running 24/7. SageMaker Async Inference lets you **scale to zero instances** when there are no requests — meaning you pay absolutely nothing when idle.

**How it works:**
- Deploy an async endpoint instead of a real-time endpoint
- Set `MinInstanceCount: 0` in the auto-scaling policy
- When a request comes in, SageMaker spins up the instance (cold start ~5-15 min)
- After processing, if no more requests come, it scales back to zero
- Processing timeout: up to **60 minutes** (vs 60 seconds for real-time)

**Cost impact:**

| Scenario | Real-time Endpoint (24/7) | Async (Scale to Zero) |
|---|---|---|
| ml.g5.12xlarge running all day | $170.16/day | Only hours you actually use it |
| 2 hours of testing per day | Still $170.16/day | **$14.18/day** |
| Weekend (no testing) | Still $170.16/day | **$0/day** |
| Monthly (testing 2hr/day weekdays) | $5,175/month | **~$310/month** |

**What this means for AEX:**
- The CMAAI workflow would need an option to deploy as async vs real-time
- Perfect for the exploration/dev phase of this story
- Solves the 60-second timeout problem for long outputs (async allows 60 min)

**Source:** [AWS Async Inference Documentation](https://docs.aws.amazon.com/sagemaker/latest/dg/async-inference.html), [Scale to Zero](https://docs.aws.amazon.com/sagemaker/latest/dg/endpoint-auto-scaling-zero-instances.html)

---

### Solution 4: AWS vLLM Deep Learning Container on ECS on EC2 (Free Container)

AWS provides official, pre-built vLLM containers specifically optimized for deploying LLMs on ECS, EC2, and EKS. These containers are **completely free** — you only pay for the compute.

**What's included:**
- vLLM inference engine (latest version)
- NVIDIA GPU drivers and CUDA
- OpenAI-compatible API server on port 8000
- Tensor parallelism support built-in
- Continuous batching for high throughput

**How this helps the AEX "huggingface" path:**
- No need to build a custom container — AWS maintains it
- Model is pulled from S3 at container startup (not baked into image) — **bypasses the ECR 52 GB layer limit**
- Tensor parallelism is configurable at launch
- The AEX `huggingface` model-type would use this container on ECS with EC2 GPU instances

**What AEX needs to change:**
- Switch from ECS Fargate → ECS on EC2 with GPU instances
- Use the AWS vLLM DLC image instead of a custom image
- Configure ephemeral storage to 200 GiB
- Pass model S3 path as environment variable to the container

**Cost:** Just the EC2 instance — cheapest is g6.12xlarge at **$4.60/hr**

**Source:** [AWS Deep Learning Containers](https://aws.github.io/deep-learning-containers/), [Deploy on ECS](https://aws.amazon.com/blogs/architecture/deploy-llms-on-amazon-eks-using-vllm-deep-learning-containers/)

---



## Findings from Technical Discussion with Phil Hall (June 17, 2026)

After reviewing the initial analysis, Phil provided key architectural context about how the Model Repo actually works.

### How the Model Repo Works

The Model Repo is built on a **handler pattern**:
- The core code doesn't know or care how individual models work
- It has a contract with **two handler methods** per model type:
  1. **Registration handler** — knows where to get the model and how to store its metadata
  2. **Inference handler** — knows how to run the model and return results
- Existing handlers: `huggingface`, `sagemaker`, `mlflow`, `pythonpackage`, `llmobject`
- Handlers are lightweight — just a few methods each

### Phil's Recommended Solution

1. Deploy Gemma 4 31B on **SageMaker JumpStart** (it's already there, ready to use)
2. Write a **new handler** (e.g., `jumpstart` model type) that:
   - **Registration:** Stores the SageMaker endpoint info (endpoint name, region, input/output format)
   - **Inference:** Proxies requests from Model Repo → SageMaker endpoint → returns response
3. To end-users, the model looks like any other Model Repo model

### Architecture

```
Caterpillar Teams → Model Repo API → "jumpstart" handler → SageMaker JumpStart Endpoint → Response
```

### Why AEX Hosts Centrally

- Many teams at Caterpillar would all try to host the same model separately
- Costs would explode with duplicate infrastructure
- AEX team hosts once, handles the complexity, other teams just call the API

### Next Steps

1. Deploy Gemma 4 31B on SageMaker JumpStart (Ankush has SageMaker experience)
2. Write a `jumpstart` handler for the Model Repo (reference existing handlers as templates)
3. Register the model and test end-to-end inference through Model Repo

## Acceptance Criteria Status

| Criteria | Status | Evidence |
|---|---|---|
| Attempt to deploy gemma-4-31b-it in Dev through AEX | Explored | Identified all 5 AEX model-types; documented which work and which don't |
| Summarize issues or gaps preventing deployment | Complete | 12 gaps documented + solution identified (JumpStart handler) |
| If successfully deployed, verify inference | Next sprint | Deploy on JumpStart + write handler (Phil's recommended approach) |
