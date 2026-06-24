# GPT Agent Prompt: Add Retrieval Evaluation to CMA AI Orchestration Service

## Context

I am working on User Story #2586135: "Introduce validation into Orchestration service" for the CMA AI Assistant project (P-Stonecutters / aex-cma-ai-assistant).

The CMA AI Orchestration service generates AI summaries for Caterpillar machine fault codes by:
1. Receiving a request with keys (serial number prefix + rollup key combinations)
2. For each key: querying a Knowledge Base, sending context + prompt to OpenAI, getting a summary
3. Storing results and producing an execution report

We need to add an optional **retrieval evaluation** step that runs ground-truth validation tests BEFORE generating summaries. This ensures retrieval quality meets thresholds before spending money on thousands of OpenAI calls.

## What Has Already Been Done

The OpenAPI spec has been updated (see below) to add:
- A new `retrievalEvaluation` boolean property on `InstantiateOrchestrationRequest`
- New orchestration statuses: `VALIDATING` and `VALIDATION_FAILED`
- A new `ValidationResult` schema with fields: outcome, testsRun, testsPassed, testsFailed, details
- The `validationResult` field added to `OrchestrationStatusResponse`

## What I Need You To Do

Update the orchestration service **source code** to support the new `retrievalEvaluation` parameter. The implementation should be a **placeholder/stub** for now — we don't need to actually call the Context Relevancy model yet. The data science team is still finalizing that.

### Specific Code Changes Required:

#### 1. Request Handler (the Lambda that receives /orchestrations/instantiate POST requests)
- Parse the new `retrievalEvaluation` field from the request body (boolean, default: false)
- Add input validation: `retrievalEvaluation` must be a boolean if provided
- Pass the `retrievalEvaluation` flag downstream to the executor/orchestration logic
- If `retrievalEvaluation` is true and NO keys are provided, that should be valid (validation-only mode)

#### 2. Request Model / Schema (wherever the input request model is defined in code)
- Add `retrieval_evaluation: bool` field (default False) to the orchestration request model/dataclass

#### 3. Executor / Orchestration Logic (the Lambda or function that runs the orchestration)
- Add a conditional branch at the beginning of execution:
  - If `retrieval_evaluation` is True:
    1. Update orchestration status to `VALIDATING`
    2. Call a new `run_retrieval_evaluation()` function (stub/placeholder)
    3. If validation result is `FAILED`:
       - Update status to `VALIDATION_FAILED`
       - Store the validation result
       - Send notification if configured
       - STOP — do not proceed with summary generation
    4. If validation result is `PASSED`:
       - Store the validation result
       - Continue with normal orchestration flow (if keys were provided)
       - Or complete successfully (if no keys — validation-only mode)
  - If `retrieval_evaluation` is False:
    - Continue with existing logic unchanged

#### 4. Create a New Validation Module/Function
Create a new file or function for the retrieval evaluation logic (placeholder):

```python
# Placeholder implementation
def run_retrieval_evaluation() -> ValidationResult:
    """
    Placeholder for retrieval quality evaluation using Context Relevancy model.
    
    In future implementation, this will:
    1. Load ground-truth test data (known inputs with expected outputs)
    2. For each test case:
       a. Call GenAI/instantiate to generate a summary
       b. Call the Context Relevancy model with:
          - input: query header, document IDs, HTML context chunks
          - query_template: system prompt
       c. Receive quality scores (context relevancy, faithfulness, 
          answer relevancy, context recall, context precision)
    3. Compare scores against configured thresholds
    4. Produce a validation report
    
    For now, returns a stub PASSED result.
    """
    return ValidationResult(
        outcome="PASSED",  # Placeholder - always passes for now
        tests_run=0,
        tests_passed=0,
        tests_failed=0,
        details="Validation placeholder - actual Context Relevancy model tests not yet implemented"
    )
```

#### 5. Validation Result Model
Create a model/dataclass for the validation result:

```python
@dataclass
class ValidationResult:
    outcome: str  # "PASSED", "FAILED", or "ERROR"
    tests_run: int
    tests_passed: int
    tests_failed: int
    details: str  # S3 URI to full report or message
```

#### 6. Status Updates
- Add `VALIDATING` and `VALIDATION_FAILED` to the orchestration status enum (wherever it's defined)
- Make sure the DynamoDB status update logic (or wherever status is persisted) supports these new values

#### 7. Status Endpoint
- When `GET /orchestrations/{id}/status` is called, include the `validationResult` in the response if retrieval evaluation was run

### Important Constraints:
- Do NOT break existing functionality — list and count modes must work exactly as before
- The validation is a STUB/PLACEHOLDER — do not implement actual model calls
- Keep changes minimal and focused
- Follow existing code patterns and conventions in the repository
- Add appropriate logging for the new validation flow
- The `retrievalEvaluation` field should be stored with the orchestration record so the status endpoint knows whether to include validation results

### Files to Look At:
- `orchestration/src/orchestration_service/` — main service code
- `orchestration/src/common/` — shared utilities/models
- `orchestration/src/tests/` — add unit tests for the new validation path
- `orchestration/cloudformation/orchestration-service/pfm-aex-cmaai-orchestration-svc-executor-lam.yml` — executor Lambda config
- `orchestration/cloudformation/orchestration-service/pfm-aex-cmaai-orchestration-svc-request-handler-lam.yml` — request handler Lambda config

### Updated API Spec Reference:

The key new schema additions:

```yaml
# New property on InstantiateOrchestrationRequest
retrievalEvaluation:
  type: boolean
  description: When true, runs ground-truth validation before generating summaries.
  default: false

# New orchestration statuses
OrchestrationStatus:
  enum: [PENDING, VALIDATING, PROCESSING, SUCCEEDED, FAILED, VALIDATION_FAILED, ABORTED]

# New schema
ValidationResult:
  properties:
    outcome:
      type: string
      enum: [PASSED, FAILED, ERROR]
    testsRun:
      type: integer
    testsPassed:
      type: integer
    testsFailed:
      type: integer
    details:
      type: string
      description: S3 URI to validation report

# Added to OrchestrationStatusResponse
validationResult:
  $ref: "#/components/schemas/ValidationResult"
```

## Expected Behavior After Changes

### Request: Validation only (no keys)
```json
POST /orchestrations/instantiate
{
  "retrievalEvaluation": true,
  "notificationMail": "user@cat.com"
}
```
→ Returns 202 with orchestrationId
→ Status goes: PENDING → VALIDATING → SUCCEEDED (with validationResult)

### Request: Validation + keys
```json
POST /orchestrations/instantiate
{
  "keys": { "list": ["KYD-PL|2126,PL", "KYD-PL|237,PL"] },
  "retrievalEvaluation": true
}
```
→ Returns 202 with orchestrationId
→ Status goes: PENDING → VALIDATING → PROCESSING → SUCCEEDED (with validationResult + overallProgress)
→ If validation fails: PENDING → VALIDATING → VALIDATION_FAILED (with validationResult, no summary generation)

### Request: Normal flow (no validation — existing behavior unchanged)
```json
POST /orchestrations/instantiate
{
  "keys": { "list": ["KYD-PL|2126,PL"] }
}
```
→ Works exactly as before, no validationResult in response

## Summary

Make these changes incrementally:
1. First update the request model to include `retrievalEvaluation`
2. Update the request handler to parse and pass it through
3. Update the status enum with new values
4. Create the ValidationResult model
5. Create the placeholder `run_retrieval_evaluation()` function
6. Add the conditional branch in the executor
7. Update the status response to include validationResult
8. Add unit tests for the new paths
