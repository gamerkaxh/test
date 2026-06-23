# CMA AI Assistant (MVP) - Easy Understanding Guide

## AVT: DRB 149 - AEX and Provisioning

**Author:** Dmitry Ornatsky  
**Lead:** Justin Rice  
**Systems Architect:** Harini Anand  
**Engineering Champion:** Travis Busen (current) / Harinath Manchana (before AI re-org)  
**Platform Product Management:** NAVED BAIG  
**Facilitator:** Roshan Hindia  

---

## Table of Contents

1. [What Is This Project?](#what-is-this-project)
2. [High-Level Architecture](#high-level-architecture)
3. [Core Services & Components](#core-services--components)
4. [API Endpoints](#api-endpoints)
5. [Data Models & Schemas](#data-models--schemas)
6. [Work Breakdown (Teams & Responsibilities)](#work-breakdown-teams--responsibilities)
7. [Key Decisions & Assumptions](#key-decisions--assumptions)
8. [Project Files & References](#project-files--references)
9. [Questions for Kevin Gasiorowski](#questions-for-kevin-gasiorowski)

---

## What Is This Project?

The **CMA AI Assistant MVP** is an AI-powered tool that helps Caterpillar Maintenance Advisors (CMAs) by:

1. **Generating SIS (Service Information System) Summaries** - Automatically summarizes relevant technical documentation for a given machine event
2. **Finding Past Recommendations** - Uses AI to find similar past recommendations that CMAs wrote for similar issues
3. **Masking PII** - Removes personal identifiable information from recommendation text before processing

### How It Works (Simple Flow):

```
Machine Event Occurs (e.g., "Low Engine Oil Pressure")
        |
        v
[GenAI Service] receives request with event details
        |
        v
[AI Context Service] provides the right prompts & configuration
        |
        v
[Knowledge Base Service] searches vector DB for relevant docs
        |
        v
[Azure OpenAI] generates a summary from relevant chunks
        |
        v
Quality check (BERTScore) - retry if below threshold
        |
        v
Result stored in S3 -> Available to Foresight UI
```

### MVP Scope:
- **IN SCOPE:** PL (Product Link) Events only
- **OUT OF SCOPE:** poSOS and CAT INSPECT

---

## High-Level Architecture

The system consists of **4 new services** and integrations with existing services:

### New Services:
| Service | Owner Team | Purpose |
|---------|-----------|---------|
| **AI Context Service** | Delta (Atul Ankola) | Manages prompts, configurations, and AI context objects |
| **Knowledge Base Service** | Lima (Vasile Glijin / Sergio Penavades Suarez) | Manages vector databases (OpenSearch), document storage, and semantic search |
| **GenAI Service** | Delta (Atul Ankola) | Orchestrates the AI workflow - calls prompts, knowledge base, OpenAI, quality checks |
| **Masking Service** | Stonecutters (Kevin Gasiorowski) | PII masking using ML model + OpenAI |

### Existing Services Modified:
| Service | Owner Team | Changes |
|---------|-----------|---------|
| **Condition Monitoring V3** | Piccadilly (Alexey Zyuzin) | New endpoints for AI content reference, ratings |
| **Recommendations** | Leo/Nightwing | New fields for AI-assisted indicator, timestamps |
| **AEX (Model Execution)** | Stonecutters (Kevin Gasiorowski) | Hosts ML models, orchestrates SIS + Past Reco generation |
| **Foresight UI** | Tigris (Kaunish Patel) | Frontend changes per Figma designs |

---

## Core Services & Components

### 1. AI Context Service

**What it does:** Stores and manages the configuration for each AI use case (which prompts to use, which knowledge base, quality thresholds, etc.)

**Key APIs:**
- `POST /create` - Create a new AI context
- `PUT /update/{id}` - Update an AI context
- `DELETE /delete/{id}` - Delete an AI context
- `GET /approved` - Get all approved AI contexts

**Key Concept:** Each AI context ties together:
- System prompt + Human prompt + Query prompt
- Knowledge base criteria (which vectors to search, weights)
- Quality model & threshold
- LLM model selection
- Token limits, temperature, max retries

**Example AI Context:**
```json
{
  "contextId": "782e86f6-94f3-4f04-9c5d-8df9458863",
  "name": "recommendation_extraction",
  "systemPrompt": "extraction",
  "humanPrompt": "recommendation_extraction",
  "queryPrompt": "pl_event_similiarity",
  "knowledgeBaseCriteria": {
    "searchVectors": [
      { "name": "possible_causes", "weight": 70.0 },
      { "name": "recommended_action", "weight": 30.0 }
    ]
  },
  "qualityModel": "aex.endpoint",
  "qualityThreshold": 0.65,
  "largeLanguageModel": "ChatGPT4.0",
  "tokenThreshold": 3000,
  "temperature": 50.0,
  "maxTries": 3
}
```

---

### 2. Knowledge Base Service

**What it does:** Manages vector databases in OpenSearch for semantic search. Stores document embeddings (SIS docs and Recommendations) and provides search capabilities.

**Two Knowledge Bases:**

#### SIS Knowledge Base:
- Vectors: `child_chunk` (768 dimensions)
- Attributes: `parent_chunk_text`, `ie_number`, `doc_title`, `serialPrefix`, `rollupKey`, `safetyLink`, `updateTime`

#### Recommendations Knowledge Base:
- Vectors: `possible_causes` (768), `recommended_actions` (768), `consequence_of_action` (768)
- Attributes: `recommendationNumber`, `recommendationText`, `serialPrefix`, `rollupKey`, `updateTime`

**Key APIs:**
- `GET /{knowledgeBaseId}` - Get metadata
- `GET /documents/{knowledgeBaseId}/{id}` - Get a document
- `POST /documents/{knowledgeBaseId}/create/{id}` - Create a document
- `PUT /documents/{knowledgeBaseId}/update/{id}` - Update a document
- `DELETE /documents/{knowledgeBaseId}/delete/{id}` - Delete a document
- `DELETE /documents/{knowledgeBaseId}/delete` - Delete by filter
- `POST /documents/{knowledgeBaseId}/search` - Semantic search

**Important Notes:**
- Schema managed via GIT
- Embedding/chunking model changes require a NEW knowledge base
- Past versions kept for 6 months
- Safety information appended to results (by ie_number reference)

---

### 3. GenAI Service

**What it does:** The main orchestration engine. Takes a request, figures out what prompts and knowledge bases to use, calls OpenAI, checks quality, and returns results.

**Pattern:** Async (fire and poll)

**Key APIs:**
- `POST /genAI/instantiate` - Start an AI generation task
- `GET /genAI/getResults/{requestId}` - Poll for results
- `POST /mask` - PII masking endpoint

**Instantiate Request:**
```json
{
  "aiContextId": "569e86f6-94f3-4f04-9c5d-8dff39s54f",
  "input": ["Low Engine Oil Pressure"],
  "filters": [
    { "name": "serial_prefix", "value": "LAJ" },
    { "name": "event_id", "value": "4530" }
  ]
}
```

**Success Response:**
```json
{
  "requestId": "57661b35-6f47-4732-9dd1-49c6fee27143",
  "name": "recommendation_extraction",
  "systemPrompt": "extraction",
  "humanPrompt": "recommendation_extraction",
  "queryPrompt": "pl_event_similiarity",
  "statusDescription": "Success",
  "status": 200,
  "retryable": false,
  "result": "The recommended action to resolve Product Link Event code 8090 is to...",
  "QualityScore": 0.78,
  "externalLinks": "self signed S3 url"
}
```

**Failure Response:**
```json
{
  "requestId": "UUID",
  "statusDescription": "Open AI Timeout",
  "status": 503,
  "retryable": true,
  "result": null
}
```

**GenAI Algorithm (Pseudo Code):**
1. Get AI context by ID (returns knowledge bases, prompts, weights)
2. Get embedding model endpoint from Knowledge Base Service
3. Embed input text
4. Search Knowledge Base using embeddings for each vector (with defined weights)
5. If LLM is configured: reduce results to token limit, call OpenAI
6. Compute quality score using BERTScore model
7. If below threshold: retry up to maxTries
8. Return result (or failure status with quality score)

**Important:** 4 deployed Azure OpenAI resources - GenAI distributes requests across them, prioritizing approved prompts.

---

### 4. Masking Service (Owned by AEX/Kevin's team)

**What it does:** Removes PII from text using regex + ML model + OpenAI

**API:** `POST /mask`

**Request:**
```json
{
  "input": "Recommended action is to replace the oil filter, please call John Doe at 570-738-2232 for further details"
}
```

**Response:**
```json
{
  "result": "Recommended action is to replace the oil filter, please call ******* at ***-***-**** for further details"
}
```

**Note:** PII masking is NOT full-proof. CMAs are responsible for validating AI-generated content before using it.

---

## API Endpoints

### New Endpoints Summary:

| Endpoint | Service | Method | Description |
|----------|---------|--------|-------------|
| `/genAI/instantiate` | GenAI | POST | Start AI generation |
| `/genAI/getResults/{requestId}` | GenAI | GET | Poll for results |
| `/mask` | Masking (AEX) | POST | PII masking |
| `/create` | AI Context | POST | Create AI context |
| `/update/{id}` | AI Context | PUT | Update AI context |
| `/delete/{id}` | AI Context | DELETE | Delete AI context |
| `/approved` | AI Context | GET | Get approved contexts |
| `/documents/{kbId}/search` | Knowledge Base | POST | Semantic search |
| `/documents/{kbId}/create/{id}` | Knowledge Base | POST | Add document |
| `/documents/{kbId}/update/{id}` | Knowledge Base | PUT | Update document |
| `/documents/{kbId}/delete/{id}` | Knowledge Base | DELETE | Delete document |
| `/documents/{kbId}/delete` | Knowledge Base | DELETE | Delete by filter |
| `events/search` | Condition Monitoring V3 | POST | Modified - adds AI content reference |
| `events/ai/rating` | Condition Monitoring V3 | POST | NEW - store AI ratings |
| `/recommendations/{recoNum}/events` | Recommendations | POST | Modified - adds AI usage info |

### Swagger References (Azure DevOps):
- Knowledge Base: Work Item 1302389
- GenAI: Work Item 1311897
- AI Context: Work Item 1310229

---

## Data Models & Schemas

### CoLocation Database Tables:

#### `events.ai_generated_content_ref`
| Column | Description |
|--------|-------------|
| Id | Primary key |
| standard_manufacturer_code | Composite key (hardcoded "CAT") |
| Serial Number Prefix | Composite key |
| Rollup key | Composite key |
| Create Time | Composite key |
| Summary Storage Reference | ID/URL for storage service |
| Update Time | Timestamp |

#### `events.ai_generated_content_user_rating`
| Column | Description |
|--------|-------------|
| Id | Primary key |
| AI Generated Content Ref Id | FK to content_ref (Composite key) |
| assetId | Composite key |
| cat_rec_id | Composite key (tagged from entitlements) |
| source type | Enum: "SIS SUMMARY", "AI PAST RECOMMENDATION" (Composite key) |
| rating | Boolean (thumbs up/down) |
| comments | User feedback text |
| Create/Update Time | Timestamps |

#### `events.ai_generated_content_usage`
| Column | Description |
|--------|-------------|
| Id | Primary key |
| AI Generated Content Ref Id | FK to content_ref |
| Recommendation Number | Linked recommendation |
| Source Type | Enum: "SIS SUMMARY", "AI PAST RECOMMENDATION" |
| Reference Id | e.g., Reco Text Id for Past Reco |
| Create Time | Timestamp |

**Data Retention:** Usage and rating tables purged to hold only 6 months of data.

#### `recommendation.recommendation_common` (Modified)
- `reco_instantiation_timestamp` - Time user opened create reco drawer
- `AI Assisted Indicator` - Whether reco was AI-assisted

### GenAI Service Schema:
| Column | Type |
|--------|------|
| requestId | GUID |
| status | TEXT |
| resultUrl | TEXT |
| result | TEXT |
| error | TEXT |

### Prompt Table:
```sql
CREATE TABLE prompts (
  promptId UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  promptName TEXT NOT NULL UNIQUE,
  promptType TEXT NOT NULL CHECK (promptType IN ('system', 'human', 'query')),
  version NUMERIC(2, 1) NOT NULL UNIQUE,
  input TEXT[],
  approved BOOLEAN,
  text TEXT
);
```

### Prompt Context Table:
```sql
CREATE TABLE prompt_context (
  contextId UUID PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  systemPrompt TEXT,
  humanPrompt TEXT,
  queryPrompt TEXT,
  knowledgeBaseCriteria JSONB,
  qualityModel TEXT,
  qualityThreshold NUMERIC(3, 2),
  largeLanguageModel TEXT,
  tokenThreshold INTEGER,
  temperature NUMERIC(4, 1),
  maxTries INTEGER
);
```

---

## Work Breakdown (Teams & Responsibilities)

### Team Assignments:

| # | Component | Team | Owner | Key Deliverables |
|---|-----------|------|-------|-----------------|
| 1 | Infrastructure | Bravo | Sergio Penavades Suarez | RDS, Debezium, CDC stream |
| 2 | Snowflake S3 Extract | Nightwing | Thoufeeq/Pratap | Daily S3 extract from Snowflake recommendations |
| 3 | AEX Model Hosting | Stonecutters | **Kevin Gasiorowski** | Deploy ML models (quality, embedding, chunking, PII masking, language) |
| 4 | Data Science Models | Ocelot | Travis Busen | Package models to AEX/JFrog/Sagemaker |
| 5 | Knowledge Base Service | Lima | Vasile Glijin | Implement new service with OpenSearch |
| 6 | AI Context Service | Delta | Atul Ankola | Implement new service |
| 7 | Prompt Engineering | Ocelot | Travis Busen | Create prompts and knowledge base configs |
| 8 | SIS Pipeline | Constellation | Samuel Soto | Vectorize SIS docs, chunk/embed/store |
| 9 | GenAI Service (Core) | Delta | Atul Ankola | Core orchestration logic |
| 10 | GenAI Service (S3 Async) | Delta | Atul Ankola | SQS listener, S3 output |
| 11 | GenAI Service (API Async) | Delta | Atul Ankola | API Gateway, async pattern |
| 12 | Reco Pipeline | Constellation | Samuel Soto | Vectorize recommendations |
| 13 | AEX Orchestration | Stonecutters | **Kevin Gasiorowski** | Orchestrate SIS + Past Reco for Foresight |
| 14 | CoLocation Data Model | Koopa | Ayu Saraswati | Database table schemas |
| 15 | Snowflake Archival | Delta | Evgeny Kochnev | CDC from rating/usage tables |
| 16 | Condition Monitoring V3 | Piccadilly | Alexey Zyuzin | events/search, rating, usage APIs |
| 17 | Recommendations | Leo | Siran.Jadhav | reco_instantiation_timestamp, AI indicator |
| 18 | LTA for OpenAI | Telemetry Arch | Justin Rice | LTA approval |
| 19 | OpenSearch PoC | Telemetry Arch | Justin Rice | Evaluate OpenSearch |
| 20 | AI Content Storage Lambda | Delta | Evgeny Kochnev | Store reference in content_ref table |
| 21 | Purge Batch Job | Delta | Evgeny Kochnev | 6-month retention purge |
| 22 | Snowflake Archival | Nightwing | Lee Brown | Archive rating/usage to Snowflake |
| 23 | Events Summary Lambda | Piccadilly | Alexey Zyuzin | Update events summary with AI ref |
| 24 | Provisioning CDC | Delta | Evgeny Kochnev | CDC content_ref to Kinesis |
| 25 | Foresight UI | Tigris | Kaunish Patel | Frontend per Figma |
| 26 | WalkMe Survey | - | Shareen Wahab | Survey forms |
| 27 | SIT Testing | - | Pratik Mehra | End-to-end testing |
| 28 | Masking Service | Stonecutters | **Kevin Gasiorowski** | ML model + OpenAI masking API |
| 29 | Data Models (KB + AI Context) | Ocelot/Koopa/Constellation/Delta | Multiple | Shared data model ownership |
| 30 | Data Model Documentation | Koopa | Tejas/Ayu | Document all schemas |

---

## Key Decisions & Assumptions

### Assumptions:
1. PII AI steps are NOT full-proof - CMAs validate AI content before using it
2. Using Microsoft's global OpenAI instance - NO guaranteed SLA (runtime not guaranteed)
3. MVP is limited to **PL Events only** (no poSOS, no CAT INSPECT)

### Key Decisions:
1. **Model Registry** - Within Sagemaker Studio (Daniela's team handles training/versioning)
2. **AEX hosts models** and creates endpoints for GenAI Service
3. **Safety info** - Only include safety links from chunks used in the OpenAI request (not all returned chunks)
4. **Masking** owned by AEX team (Stonecutters/Kevin), NOT GenAI
5. **GenAI returns results without masking** - downstream teams mask if needed
6. **Async pattern** agreed for GenAI (instantiate + poll)
7. **Separate AI context per use case** (no version management needed, no /instantiateTest)
8. **External links** - GenAI returns the self-signed S3 URL for safety links
9. **OpenSearch** used as vector database (not in-cluster embedding - we create embeddings ourselves)
10. **S3 notifications NOT needed** for AEX (Kevin confirmed async approach)
11. **Delta team owns the DB repo** - teams collaborate and jointly approve changes

---

## Project Files & References

### Azure DevOps Work Items:
| ID | Description |
|----|-------------|
| Epic 1143831 | CMA AI Assistant MVP |
| Feature 1190753 | AVT DRB 149 CMA AI Assistant (MVP) - AEX and Provisioning |
| Feature 1293416 | AI DBAPI: Create Service |
| Feature 1293121 | Knowledge Base Service |
| Feature 1297207 | AI Context: Create service |
| Feature 1297236 | Gen AI: Create service |
| Feature 1296270 | SIS Vectorization Pipeline |
| Feature 1296266 | Past Recommendations Vectorization Pipeline |
| Feature 1300185 | GEN AI Constellations - Helpers |
| Feature 1231330 | AEX Orchestration |
| Feature 1221353 | CoLocation Data Model |
| Feature 1221366 | Debezium CDC for CMA AI Tables |
| Feature 1231334 | Add AI Content Reference Id |
| Feature 1245499 | Suggested Reco for Events Linking |
| Feature 1245491 | events/ai/rating API |
| Feature 1226615 | LTA for OpenAI |
| Feature 1226653 | OpenSearch Vector DB PoC |
| Feature 1199685 | CMA AI Assistant MVP: UI Requirements |
| Feature 1152910 | WalkMe Survey |
| Feature 1215980 | SIT Validation |
| Feature 1306690 | Masking Service |
| Feature 1302099 | Gen AI and AI Context Data Model |
| Decision 1346961 | Exclude SIS Safety Messages from Gen AI Data Processing |
| Work Item 1302389 | Knowledge Base Swagger |
| Work Item 1311897 | GenAI Swagger |
| Work Item 1310229 | AI Context Swagger |
| User Story 1274447 | Snowflake S3 Extract for Past Recommendations |
| 1279644 | AEX Model Hosting |
| 1305083 | Quality model deployment |
| 1305092 | Embedding model deployment |
| 1305096 | Chunking model deployment |
| 1305099 | PII Masking model deployment |
| 1305103 | Language model deployment |
| 1285710, 1285708, 1285704, 1285727, 1293393 | Data Science model packaging |
| 1294384, 1296441 | Prompt engineering |

### Documents Referenced:
- `SIS_Pastreco_Logging_Monitoring_Robustness_Security 2.docx` - Logging/monitoring design
- CMA AI Assistant HLA (High-Level Architecture)
- OpenSearch Vector DB PoC document
- LTA documents (Confidential Yellow - stored in SharePoint)

### Key Confluence Links:
- CMA AI Assistant HLA
- Open Search Vector DB PoC
- Managing Confluence Confidential Green and Yellow Content
- Cat Digital Platform AWS Accounts
- Localization: Translation Initiation Process
- Entitlements Training Video
- New and Existing Application On-boarding to Helios Entitlements

### Recording Files Referenced:
- Knowledge Base Safety Info-20240226_103151-Meeting Recording.mp4
- Multiple AVT session recordings (Nov 2023 - Feb 2024)

---

## Questions for Kevin Gasiorowski

Based on Kevin's role as the **AEX/Stonecutters team lead** responsible for:
- ML model hosting and execution (Work Items #3, #13, #28)
- Masking Service (Feature 1306690)
- AEX orchestration for SIS + Past Recommendations (Feature 1231330)

### Technical Questions:

1. **Model Deployment Status:**
   - What is the current deployment status of the 5 ML models (quality, embedding, chunking, PII masking, language)?
   - Are all model endpoints (1305083, 1305092, 1305096, 1305099, 1305103) operational?

2. **AEX Orchestration (Feature 1231330):**
   - How does AEX orchestrate the end-to-end flow for generating SIS summaries and Past Recommendation content?
   - What is the interface between AEX and the GenAI Service? (Does AEX call GenAI instantiate, or does it use the SQS/S3 async pattern?)
   - How are results made available for Foresight consumption?

3. **Masking Service (Feature 1306690):**
   - What is the `/mask` endpoint architecture? (Regex first, then ML model, then OpenAI confirmation?)
   - Is the masking service deployed as a separate Lambda or part of AEX?
   - What is the latency expectation for masking calls?
   - How are false negatives handled (PII that slips through)?

4. **Async Pattern Confirmation:**
   - You confirmed S3 notifications are NOT needed - does AEX poll GenAI's `/getResults/{requestId}` directly?
   - What is the polling interval?
   - What is the timeout before AEX considers a GenAI request failed?

5. **Model Inference & Monitoring:**
   - AEX is responsible for inference monitoring - what metrics are tracked?
   - What are the SLA targets for model endpoint latency?
   - How does AEX handle model endpoint failures (failover, retry logic)?

6. **Load & Scaling:**
   - With ~215,000 distinct event rollup keys per month, what is the expected load on AEX model endpoints?
   - How are the 4 Azure OpenAI instances load-balanced?
   - Is there rate limiting on the model endpoints?

7. **Safety Links:**
   - Per Justin's decision, only safety links from chunks used in the OpenAI request should be included - how does AEX filter these?
   - Are you okay with receiving `externalLinks` as a URL, or does AEX need to extract and append the actual safety data?

8. **Integration Dependencies:**
   - What are the blocking dependencies from Data Science (Ocelot/Travis) for model packaging?
   - Is there a specific model artifact format required (binary, Docker image, Python package)?
   - What is the timeline for model endpoints to be ready for GenAI Service integration?

9. **Error Handling:**
   - How does AEX handle OpenAI timeout scenarios (currently 4 deployed instances)?
   - What retry strategy does AEX use when a model endpoint is unavailable?
   - How are partial failures reported back to consumers?

10. **Testing:**
    - What test data is needed for end-to-end AEX testing?
    - Are there mock/stub endpoints for the ML models in lower environments?
    - How is the quality model (BERTScore) validated against expected thresholds?

### Process/Coordination Questions:

11. **API Swagger:** When will the AEX/Masking API swagger be finalized for downstream teams?

12. **Data Model:** The GenAI schema needs `requestId, status, resultUrl, result, error` fields - has this been coordinated with Koopa (Work Item #30)?

13. **S3 Result Format:** Can you confirm the final JSON structure that AEX writes to S3 for Foresight to consume?

14. **Timeline:** What is the estimated delivery date for:
    - Model endpoints being operational?
    - Masking service API being available?
    - Full AEX orchestration flow being testable end-to-end?

---

## Summary Flow Diagram (Text)

```
[CMA opens Event in Foresight UI]
         |
         v
[Foresight calls events/search] --> Returns AI Content Reference (if exists)
         |
         v
[If no AI content] --> [AEX triggers GenAI for SIS Summary + Past Reco]
         |
         v
[GenAI/instantiate] --> Gets AI Context --> Gets Prompts
         |
         v
[Knowledge Base Search] --> Embeds input --> Searches OpenSearch vectors
         |
         v
[Rank results by weights] --> Reduce to token limit
         |
         v
[Call Azure OpenAI] --> Generate summary
         |
         v
[Quality Check (BERTScore)] --> Retry if below threshold
         |
         v
[Store result in S3] --> [Update events.ai_generated_content_ref]
         |
         v
[CDC to Kinesis] --> [Lambda updates events summary]
         |
         v
[Foresight UI displays AI content with thumbs up/down]
         |
         v
[CMA creates Recommendation] --> [Track AI-assisted indicator + timing]
```

---

## Key Metrics & Monitoring

| Metric | Purpose |
|--------|---------|
| BERTScore | Quality of AI-generated content (alarm on degrading performance) |
| Individual Lambda latency | Built-in CloudWatch metrics |
| Overall latency | End-to-end for a single context |
| Completion latency | Time from instantiate to result |
| Retry count | Step function CloudWatch metrics |
| Custom embedding/chunking metrics | Track model performance |

---

## Dependencies

1. Microsoft Azure OpenAI instances must be created
2. LTA for AEX to interact with each OpenAI instance must be approved
3. Model packaging by Data Science team (Ocelot)
4. Knowledge Base Service must be ready before pipelines can load data
5. AI Context Service must be ready before GenAI Service can function
6. Infrastructure (RDS, Debezium, CDC) must be provisioned first

---

*Document generated from AVT: DRB 149 CMA AI Assistant (MVP) - AEX and Provisioning Confluence page*
*Last AVT sessions: November 2023 - February 2024*
