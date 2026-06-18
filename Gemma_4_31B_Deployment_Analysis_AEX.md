# Gemma 4 31B-IT Deployment Options via AEX Model Service

## Document Information
- **User Story:** 2748133 - Explore deployment of Gemma model
- **Model:** google/gemma-4-31b-it
- **Sprint:** Cat Digital 2026 | Sprint 12 (Jun 10 - Jun 23)
- **Author:** Sowndarya Kurapati
- **Date:** June 18, 2026
- **Region:** us-east-1 (pricing based on this region)

---

## Model Requirements

| Specification | Value |
|---|---|
| Model Name | google/gemma-4-31b-it |
| Parameters | 31 Billion (Dense) |
| Model Size on Disk | ~65 GB (BF16 safetensors) |
| VRAM Required (FP16/BF16) | ~71 GB |
| VRAM Required (NVFP4 Quantized) | ~45 GB |
| Minimum GPU | 1x A100 80GB (single GPU) or 2x A100 40GB (tensor parallel) |
| Recommended Serving Engine | vLLM v0.8.0+ |
| Context Length | Up to 256K tokens |
| Source | JFrog Artifactory (artifacts.cat.com) - Approved |

---

## AEX Model Service Deployment Paths

The CMAAI-Model-Service GitHub Actions workflow (cmaai-model-service.yaml) supports the following model-type options:

| # | model-type | Description | Applicable to Gemma 4 31B? |
|---|---|---|---|
| 1 | huggingface | Deploy HuggingFace model on AEX infrastructure | Yes |
| 2 | sagemaker | Deploy via Amazon SageMaker endpoint | Yes |
| 3 | mlflow | Deploy MLflow model | No - not applicable for LLMs |
| 4 | pythonpackage | Deploy Python package model | No - not applicable |
| 5 | llmobject | Deploy LLM object | Possibly - needs investigation |

---

## DEPLOYMENT OPTION 1: AEX model-type = "huggingface"

### How It Works
Model artifacts are stored in S3, pulled to a worker node, loaded into GPU memory for inference.

### Workflow Inputs Required
| Input | Value |
|---|---|
| environment | datahub-dev |
| model-name | gemma-4-31b-it |
| model-version | v1 |
| model-type | huggingface |
| deploy-on-gpu | true |
| artifact-location | s3://pfn-aex-cmaai-mr-s3-bucket-dev/models/google/gemma-4-31b-it/ |
| network-type | non-routable |

### Feasibility Assessment

| Requirement | Current AEX Limit | Gemma 4 31B Needs | Status |
|---|---|---|---|
| Worker Ephemeral Storage | 20 GiB (default) | 65+ GB | FAILS |
| GPU VRAM | Unknown | 71 GB (FP16) | UNKNOWN |
| S3 Download Timeout | Unknown | ~5-10 min for 65 GB | RISK |
| Cold Start Time | Unknown | 2-5 minutes (model loading) | RISK |
| Container Image Size (ECR) | 52 GB max per layer | 65 GB model | FAILS |

### Verdict: LIKELY FAILS - Storage and container size limits are insufficient.

---

## DEPLOYMENT OPTION 2: AEX model-type = "sagemaker"

### How It Works
Model is packaged as model.tar.gz, uploaded to S3, deployed to a SageMaker real-time inference endpoint.

### Workflow Inputs Required
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

### Instance Options and Pricing (SageMaker Real-Time Inference - us-east-1)

All prices below are On-Demand, per-instance, for the us-east-1 region.

| Instance Type | vCPUs | RAM (GiB) | GPUs | GPU Type | VRAM per GPU | Total VRAM | Can Run Gemma 4 31B? | Tensor Parallel | Price/Hour | Price/Day (24h) | Price/Week (168h) | Price/Month (730h) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ml.g5.12xlarge | 48 | 192 | 4 | NVIDIA A10G | 24 GB | 96 GB | Yes (tight, needs quantization) | TP=4 | $7.09 | $170.16 | $1,191.12 | $5,175.70 |
| ml.g5.48xlarge | 192 | 768 | 8 | NVIDIA A10G | 24 GB | 192 GB | Yes | TP=4 | $20.36 | $488.64 | $3,420.48 | $14,862.80 |
| ml.p4d.24xlarge | 96 | 1152 | 8 | NVIDIA A100 40GB | 40 GB | 320 GB | Yes | TP=2 | $25.25 | $606.00 | $4,242.00 | $18,432.50 |
| ml.p4de.24xlarge | 96 | 1152 | 8 | NVIDIA A100 80GB | 80 GB | 640 GB | Yes (single GPU capable) | TP=1 | $33.52 | $804.48 | $5,631.36 | $24,469.60 |
| ml.p5.48xlarge | 192 | 2048 | 8 | NVIDIA H100 80GB | 80 GB | 640 GB | Yes (single GPU capable, fastest) | TP=1 | $63.29 | $1,518.96 | $10,632.72 | $46,201.70 |

**Notes:**
- SageMaker pricing includes managed infrastructure (auto-scaling, health checks, endpoint management)
- SageMaker pricing is approximately 15-25% higher than raw EC2 equivalent
- Prices sourced from [cloudprice.net](https://cloudprice.net/aws/sagemaker) and AWS pricing pages

### Feasibility Assessment

| Requirement | SageMaker Capability | Gemma 4 31B Needs | Status |
|---|---|---|---|
| Model tar.gz upload | S3 multipart upload, no size limit | 65 GB tar.gz | PASS (but slow to package) |
| Storage on endpoint | Configurable EBS volume | 65+ GB | PASS |
| GPU availability | Multiple GPU instances | A100 80GB minimum for FP16 | PASS |
| Cold start | Instance launch + model load | 5-15 minutes | PASS (but slow) |
| Inference timeout | Up to 60 seconds (real-time) | Depends on output length | RISK |

### Verdict: MOST LIKELY TO SUCCEED via AEX - but requires packaging 65 GB into tar.gz and appropriate instance type.

---

## DEPLOYMENT OPTION 3: SageMaker JumpStart (Bypasses AEX - Direct)

### How It Works
Gemma 4 models are pre-registered in SageMaker JumpStart (available since April 2026). Deploy directly from SageMaker Studio or Python SDK with no manual model packaging needed.

### Feasibility Assessment

| Requirement | Status | Notes |
|---|---|---|
| Model availability | PASS | Confirmed available since April 2026 |
| No manual packaging | PASS | JumpStart handles model artifacts |
| GPU instances | PASS | Same instances as Option 2 |
| Integration with AEX | FAILS | Not managed through CMAAI-Model-Service workflow |

### Pricing (Same SageMaker instances as Option 2)

| Instance Type | Price/Hour | Price/Day | Price/Week | Price/Month |
|---|---|---|---|---|
| ml.g5.12xlarge | $7.09 | $170.16 | $1,191.12 | $5,175.70 |
| ml.g5.48xlarge | $20.36 | $488.64 | $3,420.48 | $14,862.80 |
| ml.p4d.24xlarge | $25.25 | $606.00 | $4,242.00 | $18,432.50 |
| ml.p5.48xlarge | $63.29 | $1,518.96 | $10,632.72 | $46,201.70 |

### Verdict: WORKS TODAY - but not integrated with AEX pipeline. Best for immediate dev/testing.

---

## DEPLOYMENT OPTION 4: Self-Hosted on EC2 with GPU (Bypasses AEX)

### How It Works
Launch a GPU EC2 instance, install vLLM, download model from S3, serve via OpenAI-compatible API.

### Instance Options and Pricing (EC2 On-Demand - us-east-1)

| Instance Type | vCPUs | RAM (GiB) | GPUs | GPU Type | VRAM per GPU | Total VRAM | Can Run Gemma 4 31B? | Tensor Parallel | Price/Hour | Price/Day (24h) | Price/Week (168h) | Price/Month (730h) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| g6.12xlarge | 48 | 192 | 4 | NVIDIA L4 | 24 GB | 96 GB | Yes (quantized NVFP4 only) | TP=4 | $4.60 | $110.40 | $772.80 | $3,358.00 |
| g6.48xlarge | 192 | 768 | 8 | NVIDIA L4 | 24 GB | 192 GB | Yes | TP=4 | $13.35 | $320.40 | $2,242.80 | $9,745.50 |
| g5.12xlarge | 48 | 192 | 4 | NVIDIA A10G | 24 GB | 96 GB | Yes (quantized or tight FP16) | TP=4 | $5.67 | $136.08 | $952.56 | $4,139.00 |
| g5.48xlarge | 192 | 768 | 8 | NVIDIA A10G | 24 GB | 192 GB | Yes | TP=4 | $16.29 | $390.96 | $2,736.72 | $11,892.00 |
| p4d.24xlarge | 96 | 1152 | 8 | NVIDIA A100 40GB | 40 GB | 320 GB | Yes | TP=2 | $21.96 | $526.98 | $3,688.87 | $16,029.08 |
| p4de.24xlarge | 96 | 1152 | 8 | NVIDIA A100 80GB | 80 GB | 640 GB | Yes (single GPU) | TP=1 | $27.45 | $658.73 | $4,611.10 | $20,036.35 |
| p5.48xlarge | 192 | 2048 | 8 | NVIDIA H100 80GB | 80 GB | 640 GB | Yes (single GPU, fastest) | TP=1 | $55.04 | $1,320.96 | $9,246.72 | $40,179.20 |

**Notes:**
- Prices sourced from [instances.vantage.sh](https://instances.vantage.sh) and [economize.cloud](https://economize.cloud)
- EC2 pricing is raw compute only - does not include management overhead
- Requires manual setup: vLLM installation, model download, monitoring, scaling

### Verdict: CHEAPEST OPTION - but requires manual infrastructure management, not AEX-integrated.

---

## DEPLOYMENT OPTION 5: Amazon Bedrock

| Model | Availability | Verdict |
|---|---|---|
| Gemma 4 31B | NOT AVAILABLE | Bedrock only supports Gemma v3 |
| Gemma 3 (various sizes) | Available | Different model, not what story requires |

### Verdict: NOT POSSIBLE - Gemma 4 is not supported on Bedrock.

---

## COST COMPARISON SUMMARY (Cheapest to Most Expensive)

### Recommended Instance for Each Path

| Rank | Deployment Path | Through AEX? | Instance | GPU | $/Hour | $/Day | $/Week | $/Month | Feasible Today? |
|---|---|---|---|---|---|---|---|---|---|
| 1 | EC2 Self-Hosted | No | g6.12xlarge | 4x L4 (96GB) | $4.60 | $110.40 | $772.80 | $3,358.00 | Yes (manual setup) |
| 2 | EC2 Self-Hosted | No | g5.12xlarge | 4x A10G (96GB) | $5.67 | $136.08 | $952.56 | $4,139.00 | Yes (manual setup) |
| 3 | AEX → SageMaker | Yes | ml.g5.12xlarge | 4x A10G (96GB) | $7.09 | $170.16 | $1,191.12 | $5,175.70 | Likely Yes |
| 4 | EC2 Self-Hosted | No | g6.48xlarge | 8x L4 (192GB) | $13.35 | $320.40 | $2,242.80 | $9,745.50 | Yes (manual setup) |
| 5 | EC2 Self-Hosted | No | g5.48xlarge | 8x A10G (192GB) | $16.29 | $390.96 | $2,736.72 | $11,892.00 | Yes (manual setup) |
| 6 | AEX → SageMaker | Yes | ml.g5.48xlarge | 8x A10G (192GB) | $20.36 | $488.64 | $3,420.48 | $14,862.80 | Likely Yes |
| 7 | EC2 Self-Hosted | No | p4d.24xlarge | 8x A100-40GB (320GB) | $21.96 | $526.98 | $3,688.87 | $16,029.08 | Yes |
| 8 | AEX → SageMaker | Yes | ml.p4d.24xlarge | 8x A100-40GB (320GB) | $25.25 | $606.00 | $4,242.00 | $18,432.50 | Yes |
| 9 | EC2 Self-Hosted | No | p4de.24xlarge | 8x A100-80GB (640GB) | $27.45 | $658.73 | $4,611.10 | $20,036.35 | Yes |
| 10 | AEX → SageMaker | Yes | ml.p4de.24xlarge | 8x A100-80GB (640GB) | $33.52 | $804.48 | $5,631.36 | $24,469.60 | Yes |
| 11 | EC2 Self-Hosted | No | p5.48xlarge | 8x H100-80GB (640GB) | $55.04 | $1,320.96 | $9,246.72 | $40,179.20 | Yes |
| 12 | AEX → SageMaker | Yes | ml.p5.48xlarge | 8x H100-80GB (640GB) | $63.29 | $1,518.96 | $10,632.72 | $46,201.70 | Yes |

---

## GAPS IDENTIFIED IN AEX MODEL SERVICE

| # | Gap | Current State | Required State | Priority | Impact |
|---|---|---|---|---|---|
| 1 | Worker ephemeral storage too small | 20 GiB default | 100+ GiB | P0 - Critical | Cannot load 65 GB model |
| 2 | No JFrog-to-S3 transfer automation | Manual download required | Automated pipeline | P0 - Critical | 65 GB cannot be manually transferred efficiently |
| 3 | ECR image layer size limit | 52 GB max per layer | N/A (use runtime pull) | P1 - High | Cannot bake model into container |
| 4 | No GPU instance type selection in workflow | No input for instance type | User-selectable GPU instance | P1 - High | Cannot specify A100/H100 for large models |
| 5 | No tensor parallelism configuration | Not configurable | TP=1,2,4,8 configurable | P2 - Medium | Required for multi-GPU inference |
| 6 | Cold start timeout too short | Unknown (likely < 5 min) | 10-15 minutes for large models | P2 - Medium | Model loading takes 2-5 minutes |
| 7 | No model quantization pipeline | Not available | NVFP4/INT8 quantization | P3 - Low | Would reduce size from 65GB to ~20GB |

---

## RECOMMENDATIONS

### For Immediate Dev Testing (This Sprint)
1. Deploy via **SageMaker JumpStart** on **ml.g5.12xlarge** ($7.09/hr) - fastest path to working inference
2. Document results as proof that model CAN run on AWS infrastructure

### For AEX Integration (Next 2-3 Sprints)
1. Use AEX model-type **"sagemaker"** with **ml.g5.12xlarge** or **ml.p4d.24xlarge**
2. Requires: ability to tar.gz 65 GB and upload to S3 (needs staging infrastructure)
3. Add GPU instance type selection to CMAAI-Model-Service workflow

### For Production (Long-term)
1. Recommended instance: **ml.p4d.24xlarge** ($25.25/hr) - best balance of performance and cost
2. Cheapest viable: **g6.12xlarge** ($4.60/hr) with NVFP4 quantization
3. Implement model caching, auto-scaling, and monitoring

---

## PRICING SOURCES AND VERIFICATION

| Source | URL | Date Accessed |
|---|---|---|
| instances.vantage.sh (EC2 pricing) | https://instances.vantage.sh | June 18, 2026 |
| economize.cloud (EC2 pricing) | https://economize.cloud | June 18, 2026 |
| cloudprice.net (SageMaker pricing) | https://cloudprice.net/aws/sagemaker | June 18, 2026 |
| AWS EC2 Instance Types - G6 | https://aws.amazon.com/ec2/instance-types/g6/ | June 18, 2026 |
| AWS EC2 Instance Types - P4 | https://aws.amazon.com/ec2/instance-types/p4/ | June 18, 2026 |
| AWS EC2 Instance Types - P5 | https://aws.amazon.com/ec2/instance-types/p5/ | June 18, 2026 |
| AWS SageMaker JumpStart Gemma 4 | https://aws.amazon.com/about-aws/whats-new/2026/04/gemma-4-models-on-sagemaker-jumpstart/ | June 18, 2026 |

---

## IMPORTANT DISCLAIMERS

1. All prices are **On-Demand** pricing for **us-east-1** region. Actual prices may vary by region.
2. SageMaker Savings Plans can reduce costs by up to 64% with 1-3 year commitments.
3. EC2 Spot instances can reduce costs by 60-90% but may be interrupted.
4. Prices do not include data transfer, S3 storage, or other ancillary costs.
5. **Always verify current pricing at https://aws.amazon.com/sagemaker/pricing/ and https://aws.amazon.com/ec2/pricing/on-demand/ before making purchasing decisions.**
6. GPU instance availability may be limited and may require quota increase requests via AWS Service Quotas console.
