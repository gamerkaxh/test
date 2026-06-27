PROMPT FOR COPILOT - ORCHESTRATION REPO (aex-cma-ai-assistant)

BACKGROUND:
The CMA AI Orchestration service generates AI summaries for Caterpillar machine fault codes. Each fault code is identified by a "key" which is a combination of serial number prefix + rollup key (e.g., "KYD-PL|2126,PL"). The service uses a RAG pattern: it searches a Knowledge Base for relevant SIS documents, sends them to OpenAI via GenAI service, and gets back a summary.

We are adding a new dedicated validation endpoint: POST /orchestrations/validate. This endpoint runs ground truth validation tests to check retrieval quality and AI summary generation quality.

HOW THE VALIDATION WORKS (for context, implementation is placeholder for now):
There are approximately 10-12 pre-defined ground truth test keys. For each key we know:
- The expected document IDs that should be retrieved (e.g., "i05380240", "i01392966")
- The expected correct summary (verified by humans)

When validation runs:
1. For each ground truth key, call GenAI/instantiate (same as normal orchestration does)
2. Get the response which contains:
   - Referenced document IDs (in the JSON reference section of the result)
   - The generated summary text
3. For retrieval validation: compare actual document IDs against expected document IDs for each key
4. For generation validation: compare generated summary against ground truth summary using similarity scoring

The existing /orchestrations/instantiate endpoint should NOT be modified. This is a completely new, separate endpoint.

Here's what I need you to do:

1. REQUEST HANDLER - Add a new route for POST /orchestrations/validate

In the request handler (the Lambda that handles incoming API requests), add support for the new /validate path.

It should:
- Accept a JSON body with:
  - validationType (required): string, one of "retrieval", "generation", or "all"
    - "retrieval": only check if the right documents were retrieved for each test key
    - "generation": only check if the generated summary is similar to the ground truth summary for each test key
    - "all": run both retrieval and generation checks for each test key
  - notificationMail (optional): string or array of strings
- Validate that validationType is provided and is one of the three allowed values ("retrieval", "generation", "all")
- Return 400 with clear error message if validationType is missing
- Return 400 with clear error message if validationType is not one of the allowed values
- Return 400 if the body is not valid JSON
- Create a new orchestration record in DynamoDB with:
  - orchestrationId: generate a new UUID
  - status: PENDING
  - type: "validation" (to distinguish from normal orchestrations)
  - validationType: whatever was passed in ("retrieval", "generation", or "all")
  - notificationMail: if provided
  - createdAt: current timestamp
- Trigger the executor Lambda asynchronously
- Return 202 with orchestrationId and status PENDING

Follow the same patterns used by the existing instantiate handler. Look at how it parses the body, creates the DynamoDB record, and triggers the executor.

2. EXECUTOR - Add validation handling

In the executor, add logic to handle validation orchestrations:

- Check if the orchestration type is "validation" (read from the DynamoDB record)
- If yes:
  - Update status to VALIDATING
  - Read the validationType from the record
  - Call run_validation(validation_type) where validation_type is "retrieval", "generation", or "all"
  - Store the validation result in the DynamoDB record (so the status endpoint can return it)
  - If any part failed (retrieval or generation outcome is FAILED), update status to VALIDATION_FAILED
  - If all requested parts passed, update status to SUCCEEDED
  - Send notification email if notificationMail was configured
- If the orchestration type is NOT "validation", continue with existing orchestration logic exactly as before

3. VALIDATION MODULE - Create/update the validation logic

Create or update the validation module with a function. This is a PLACEHOLDER for now. Do NOT implement actual GenAI calls or document comparison. The real implementation will come later when ground truth data and models are available.

def run_validation(validation_type: str) -> ValidationResult:
    """
    Runs ground truth validation tests.
    
    PLACEHOLDER IMPLEMENTATION - returns stub results.
    
    In the FUTURE, this function will:
    
    For retrieval validation (validation_type == "retrieval" or "all"):
    1. Load pre-defined ground truth test keys (approximately 10-12 keys stored in S3 or config)
       Example keys: "KYD-PL|2126,PL", "BXD-PL|100-3", etc.
    2. For each key:
       a. Call GenAI/instantiate with the key (same call the normal orchestration makes)
       b. Poll GenAI/getResults until response is ready
       c. From the response JSON, extract the referenced document IDs
          (these are SIS document numbers like "i05380240", "i01392966")
       d. Compare the actual retrieved document IDs against the expected ground truth document IDs
       e. Mark the key as PASSED if documents match, FAILED if they don't
    3. Aggregate results: how many keys passed, how many failed
    
    For generation/summary validation (validation_type == "generation" or "all"):
    1. Load pre-defined ground truth test keys (same keys as above)
    2. For each key:
       a. Call GenAI/instantiate with the key (or reuse the result from retrieval step if "all")
       b. Poll GenAI/getResults until response is ready
       c. Extract the generated summary text from the response
       d. Load the ground truth summary for this key (the known-correct summary)
       e. Compare generated summary vs ground truth summary using similarity scoring
          (approach TBD: cosine similarity on embeddings, or LLM-as-a-judge)
       f. Mark the key as PASSED if similarity >= threshold, FAILED if below
    3. Aggregate results: how many keys passed, how many failed
    
    For now, returns a stub PASSED result with zero tests run.
    """
    
    retrieval_result = None
    generation_result = None
    
    if validation_type in ("retrieval", "all"):
        retrieval_result = RetrievalValidationResult(
            outcome="PASSED",
            tests_run=0,
            tests_passed=0,
            tests_failed=0
        )
    
    if validation_type in ("generation", "all"):
        generation_result = GenerationValidationResult(
            outcome="PASSED",
            tests_run=0,
            tests_passed=0,
            tests_failed=0
        )
    
    overall = "PASSED"
    
    return ValidationResult(
        retrieval=retrieval_result,
        generation=generation_result,
        overall_outcome=overall,
        report_location="Validation placeholder - ground truth data and models not yet integrated"
    )

4. VALIDATION RESULT MODELS

Create models/dataclasses for the validation results:

@dataclass
class RetrievalValidationResult:
    """Result of retrieval validation - checks if correct documents were retrieved for each test key."""
    outcome: str  # "PASSED", "FAILED", or "ERROR"
    tests_run: int  # number of ground truth keys tested
    tests_passed: int  # keys where retrieved documents matched expected
    tests_failed: int  # keys where retrieved documents did NOT match expected

@dataclass
class GenerationValidationResult:
    """Result of generation validation - checks if generated summaries match ground truth summaries."""
    outcome: str  # "PASSED", "FAILED", or "ERROR"
    tests_run: int  # number of ground truth keys tested
    tests_passed: int  # keys where summary similarity met threshold
    tests_failed: int  # keys where summary similarity was below threshold

@dataclass
class ValidationResult:
    """Overall validation result containing retrieval and/or generation results."""
    retrieval: Optional[RetrievalValidationResult]  # None if retrieval validation was not requested
    generation: Optional[GenerationValidationResult]  # None if generation validation was not requested
    overall_outcome: str  # "PASSED" only if ALL requested checks passed, "FAILED" if any failed
    report_location: str  # S3 URI to detailed per-key report, or placeholder message

5. STATUS ENDPOINT

Update the status endpoint response to include validationResult when the orchestration type is "validation":
- Read the orchestration record from DynamoDB
- If the record has type "validation" and has a stored validationResult, include it in the response
- If the record is a normal orchestration (not validation), do NOT include validationResult
- The existing behavior for normal orchestrations must not change at all

6. ORCHESTRATION STATUS ENUM

Add VALIDATING and VALIDATION_FAILED to the status enum (wherever it's defined in the codebase). Keep all existing values.

7. TESTS

Add tests for ALL of the following scenarios:

Request handling tests:
- POST /orchestrations/validate with validationType "retrieval" returns 202 with orchestrationId and status PENDING
- POST /orchestrations/validate with validationType "generation" returns 202 with orchestrationId and status PENDING
- POST /orchestrations/validate with validationType "all" returns 202 with orchestrationId and status PENDING
- POST /orchestrations/validate with validationType "all" and notificationMail returns 202
- POST /orchestrations/validate with missing validationType returns 400
- POST /orchestrations/validate with invalid validationType (e.g., "invalid", "both", "everything") returns 400
- POST /orchestrations/validate with empty body returns 400
- POST /orchestrations/validate with non-JSON body returns 400
- POST /orchestrations/validate with validationType as integer returns 400
- POST /orchestrations/validate with validationType as null returns 400

Executor tests:
- Executor correctly identifies validation type orchestration and enters validation flow
- Executor updates status to VALIDATING before running validation
- Executor calls run_validation with correct validation_type parameter
- Executor updates status to SUCCEEDED when placeholder validation passes
- Executor stores validationResult in DynamoDB record
- Executor does NOT enter validation flow for normal orchestrations (type != "validation")
- Existing instantiate/executor flow is completely unchanged and all existing executor tests still pass

Validation function tests:
- run_validation("retrieval") returns result with retrieval populated and generation as None
- run_validation("generation") returns result with generation populated and retrieval as None
- run_validation("all") returns result with both retrieval and generation populated
- run_validation with any valid type returns overall_outcome "PASSED" (placeholder behavior)
- run_validation returns a report_location string

Status endpoint tests:
- Status endpoint includes validationResult for validation orchestrations that have completed
- Status endpoint does NOT include validationResult for normal (non-validation) orchestrations
- Status endpoint returns status VALIDATING while validation is in progress
- Status endpoint returns status VALIDATION_FAILED when validation failed
- Status endpoint returns status SUCCEEDED when validation passed
- Existing status endpoint behavior for normal orchestrations is unchanged

CRITICAL RULES:
- Do NOT modify the existing /orchestrations/instantiate endpoint or its handler in ANY way
- Do NOT modify the existing /orchestrations/{orchestrationId}/cancel endpoint
- Do NOT break any existing tests - ALL existing tests must still pass
- Do NOT implement actual GenAI calls, document comparison, or similarity scoring - this is a PLACEHOLDER
- Follow the same code patterns, naming conventions, and file structure already used in the codebase
- Keep the validation logic in its own file/module so it can be filled in later without touching other code
- Add appropriate logging (logger.info for key events, logger.error for failures)
- Make sure all new code is importable and doesn't have circular dependencies
- Run python3 -m compileall on all changed files to verify no syntax errors
