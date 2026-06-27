PROMPT FOR COPILOT - ORCHESTRATION REPO (aex-cma-ai-assistant)

Context: I'm adding a new dedicated validation endpoint to the CMA AI Orchestration service. The endpoint is POST /orchestrations/validate and it runs ground truth validation tests to check retrieval quality and AI summary generation quality.

The existing /orchestrations/instantiate endpoint should NOT be modified. This is a completely new endpoint.

Here's what I need you to do:

1. REQUEST HANDLER - Add a new route for POST /orchestrations/validate

In the request handler (the Lambda that handles incoming API requests), add support for the new /validate path.

It should:
- Accept a JSON body with:
  - validationType (required): string, one of "retrieval", "generation", or "all"
  - notificationMail (optional): string or array of strings
- Validate that validationType is provided and is one of the allowed values
- Return 400 if validationType is missing or invalid
- Create a new orchestration record in DynamoDB with:
  - status: PENDING
  - type: "validation" (to distinguish from normal orchestrations)
  - validationType: whatever was passed in
- Trigger the executor Lambda
- Return 202 with orchestrationId and status PENDING

Follow the same patterns used by the existing instantiate handler. Look at how it parses the body, creates the DynamoDB record, and triggers the executor.

2. EXECUTOR - Add validation handling

In the executor, add logic to handle validation orchestrations:

- Check if the orchestration type is "validation"
- If yes:
  - Update status to VALIDATING
  - Call run_validation(validation_type) where validation_type is "retrieval", "generation", or "all"
  - Store the validation result
  - If any part failed, update status to VALIDATION_FAILED
  - If all parts passed, update status to SUCCEEDED
  - Send notification if configured

3. VALIDATION MODULE - Create/update the validation logic

Create or update the validation module with a function:

def run_validation(validation_type: str) -> ValidationResult:
    """
    Runs ground truth validation.
    
    PLACEHOLDER IMPLEMENTATION.
    
    In the future this will:
    
    For retrieval validation:
    1. Load pre-defined ground truth keys (about 10-12 keys)
    2. For each key, call GenAI instantiate to generate a summary
    3. From the response, extract the referenced document IDs (from the JSON reference section)
    4. Compare referenced documents against expected ground truth documents
    5. Mark as passed if documents match, failed if they don't
    
    For generation validation:
    1. Load pre-defined ground truth keys
    2. For each key, call GenAI instantiate to generate a summary
    3. Compare the generated summary against the ground truth summary
    4. Use similarity scoring (cosine similarity or LLM-as-a-judge - approach TBD)
    5. Mark as passed if similarity is above threshold, failed if below
    
    For now, returns a stub result.
    """
    
    retrieval_result = None
    generation_result = None
    
    if validation_type in ("retrieval", "all"):
        retrieval_result = {
            "outcome": "PASSED",
            "testsRun": 0,
            "testsPassed": 0,
            "testsFailed": 0
        }
    
    if validation_type in ("generation", "all"):
        generation_result = {
            "outcome": "PASSED",
            "testsRun": 0,
            "testsPassed": 0,
            "testsFailed": 0
        }
    
    return {
        "retrieval": retrieval_result,
        "generation": generation_result,
        "overallOutcome": "PASSED",
        "reportLocation": "Validation placeholder - ground truth data and models not yet integrated"
    }

4. VALIDATION RESULT MODEL

Create a model/dataclass for the validation result:

class RetrievalValidationResult:
    outcome: str  # PASSED, FAILED, ERROR
    tests_run: int
    tests_passed: int
    tests_failed: int

class GenerationValidationResult:
    outcome: str  # PASSED, FAILED, ERROR
    tests_run: int
    tests_passed: int
    tests_failed: int

class ValidationResult:
    retrieval: Optional[RetrievalValidationResult]  # None if not requested
    generation: Optional[GenerationValidationResult]  # None if not requested
    overall_outcome: str  # PASSED, FAILED, ERROR
    report_location: str  # S3 URI or placeholder message

5. STATUS ENDPOINT

Update the status endpoint response to include validationResult when the orchestration type is "validation". The existing behavior for normal orchestrations should not change.

6. ORCHESTRATION STATUS ENUM

Add VALIDATING and VALIDATION_FAILED to the status enum if not already there.

7. TESTS

Add tests for:
- POST /orchestrations/validate with validationType "retrieval" returns 202
- POST /orchestrations/validate with validationType "generation" returns 202
- POST /orchestrations/validate with validationType "all" returns 202
- POST /orchestrations/validate with missing validationType returns 400
- POST /orchestrations/validate with invalid validationType returns 400
- Executor correctly handles validation type orchestrations
- Executor sets status to VALIDATING then SUCCEEDED for placeholder
- Status endpoint includes validationResult for validation orchestrations
- Status endpoint does NOT include validationResult for normal orchestrations
- Existing instantiate flow is completely unchanged

IMPORTANT:
- Do NOT modify the existing /orchestrations/instantiate endpoint or its handler
- Do NOT break any existing tests
- Follow the same code patterns and conventions already used in the codebase
- This is a placeholder - do not implement actual GenAI calls or document comparison
- Keep the validation logic in its own file/module so it can be filled in later without touching other code
