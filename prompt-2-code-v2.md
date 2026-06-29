PROMPT FOR COPILOT - ORCHESTRATION REPO (aex-cma-ai-assistant) - VERSION 2

Based on code review feedback from Luba (the lead developer), validation must be COMPLETELY SEPARATE from orchestration. This means:
- A new Lambda function (ValidationRunner), NOT using the existing Executor Lambda
- A new DynamoDB table (pfm-aex-cmaai-orchestration-svc-validations), NOT the existing orchestration table
- Dedicated DynamoDB classes, NOT mixing with Orchestration classes
- Separate folder structure for validation code

CRITICAL RULES BEFORE YOU START:
- Do NOT modify conftest.py at the top level (tests/conftest.py)
- Do NOT modify pytest.ini
- Do NOT modify any existing test configuration
- Do NOT add os.chdir or Path manipulation to conftest files
- Do NOT change pythonpath or testpaths in pytest.ini
- Follow the EXACT existing test patterns already in the codebase
- Do NOT touch the Executor Lambda or any orchestration code
- Do NOT modify the request handler's existing orchestration logic
- Look at how existing tests are structured and follow that pattern exactly

BACKGROUND:
The CMA AI Orchestration service generates AI summaries for Caterpillar machine fault codes. We are adding a completely separate validation capability that tests a pre-defined set of 10-12 keys against ground truth data.

The validation runs those keys through GenAI, then:
- Retrieval check: compares actual document IDs in the response against expected document IDs
- Generation check: compares generated summary against ground truth summary using similarity scoring

This is an async operation: submit validation -> get back an ID -> poll for status/results.

HERE IS WHAT I NEED:

1. NEW FOLDER STRUCTURE

Create a new validation service folder SEPARATE from orchestration_service:

src/
  validation_service/              # NEW - completely separate from orchestration_service
    __init__.py
    functions/
      __init__.py
      validation_runner/           # NEW Lambda - equivalent of executor but for validation
        __init__.py
        main.py                    # Lambda handler entry point
        validation_logic.py        # The actual validation logic (placeholder)
      request_handler/             # Handle /validations/ routes (or add to existing handler)
        __init__.py
        handler.py                 # Handles POST /validations/submit and GET /validations/{id}/status
    common/
      __init__.py
      models/
        __init__.py
        validation.py              # ValidationResult, RetrievalResult, GenerationResult dataclasses
      dynamodb/
        __init__.py
        validation_table.py        # DynamoDB operations for the validation table (SEPARATE from orchestration table)

tests/
  validation_service/              # NEW - separate test folder
    __init__.py
    functions/
      __init__.py
      validation_runner/
        __init__.py
        test_validation_runner.py
        test_validation_logic.py
      request_handler/
        __init__.py
        test_validation_handler.py

NOTE: If the existing project structure doesn't support this layout (e.g., everything must be under orchestration_service), then put it under:
  src/orchestration_service/functions/validation_runner/
  src/orchestration_service/common/models/validation.py
  src/orchestration_service/common/dynamodb/validation_table.py
But keep it CLEARLY separated from executor and orchestration logic. Ask the codebase structure for guidance.

2. DYNAMODB TABLE CLASS (validation_table.py)

Create a dedicated DynamoDB class for the validation table. Do NOT reuse the orchestration DynamoDB class.

Table name: pfm-aex-cmaai-orchestration-svc-validations

Schema:
- validationId (partition key): string (UUID)
- status: string (PENDING, RUNNING, PASSED, FAILED, ERROR)
- validationType: string (retrieval, generation, all)
- notificationMail: string or list (optional)
- createdAt: string (ISO timestamp)
- updatedAt: string (ISO timestamp)
- result: map/dict (the ValidationResult object, stored as JSON)

Methods needed:
- create_validation(validation_id, validation_type, notification_mail) -> creates new record with PENDING status
- update_status(validation_id, status) -> updates the status field
- store_result(validation_id, result) -> stores the validation result
- get_validation(validation_id) -> retrieves the full record

Look at how the existing orchestration DynamoDB class is built and follow the same patterns (error handling, logging, table name from environment variable, etc.) but do NOT inherit from it or import it.

3. REQUEST HANDLER FOR VALIDATION

Handle two new routes:
- POST /v1/validations/submit
- GET /v1/validations/{validationId}/status

This could be:
- Added as new routes to the existing request handler Lambda (if it handles routing by path)
- OR a separate Lambda if that's how the team structures things

Look at how the existing request handler routes /orchestrations/instantiate and follow the same pattern.

POST /validations/submit handler:
  - Parse JSON body
  - Extract validationType (required, must be "retrieval", "generation", or "all")
  - Extract notificationMail (optional)
  - Return 400 if validationType missing or invalid
  - Generate UUID for validationId
  - Call validation DynamoDB class to create record (status: PENDING)
  - Trigger ValidationRunner Lambda asynchronously
  - Return 202: {validationId, status: "PENDING"}

GET /validations/{validationId}/status handler:
  - Extract validationId from path
  - Call validation DynamoDB class to get record
  - Return 404 if not found
  - Return 200: {validationId, status, result (if present)}

4. VALIDATION RUNNER LAMBDA (main.py)

This is a NEW Lambda function, separate from the Executor Lambda.

Entry point:
def handler(event, context):
    validation_id = event["validationId"]
    
    # Read from validation DynamoDB table
    record = validation_table.get_validation(validation_id)
    validation_type = record["validationType"]
    
    # Update status to RUNNING
    validation_table.update_status(validation_id, "RUNNING")
    
    # Run validation (placeholder)
    result = run_validation(validation_type)
    
    # Store result
    validation_table.store_result(validation_id, result)
    
    # Update final status
    if result.overall_outcome == "PASSED":
        validation_table.update_status(validation_id, "PASSED")
    elif result.overall_outcome == "FAILED":
        validation_table.update_status(validation_id, "FAILED")
    else:
        validation_table.update_status(validation_id, "ERROR")
    
    # Send notification if configured
    if record.get("notificationMail"):
        send_notification(record["notificationMail"], result)

5. VALIDATION LOGIC (validation_logic.py)

PLACEHOLDER implementation. Same as before but in its own file:

def run_validation(validation_type: str) -> ValidationResult:
    """Placeholder - returns stub PASSED result."""
    
    retrieval = None
    generation = None
    
    if validation_type in ("retrieval", "all"):
        retrieval = RetrievalResult(outcome="PASSED", tests_run=0, tests_passed=0, tests_failed=0)
    
    if validation_type in ("generation", "all"):
        generation = GenerationResult(outcome="PASSED", tests_run=0, tests_passed=0, tests_failed=0)
    
    return ValidationResult(
        retrieval=retrieval,
        generation=generation,
        overall_outcome="PASSED",
        report_location="Validation placeholder - ground truth data not yet integrated"
    )

6. MODELS (validation.py)

@dataclass
class RetrievalResult:
    outcome: str
    tests_run: int
    tests_passed: int
    tests_failed: int

@dataclass
class GenerationResult:
    outcome: str
    tests_run: int
    tests_passed: int
    tests_failed: int

@dataclass
class ValidationResult:
    retrieval: Optional[RetrievalResult]
    generation: Optional[GenerationResult]
    overall_outcome: str
    report_location: str

7. TESTS

Follow the EXISTING test patterns in the codebase. Do NOT:
- Modify conftest.py at the root test level
- Modify pytest.ini
- Add os.chdir calls
- Change pythonpath configuration

Look at how tests in tests/orchestration_service/functions/executor/ are structured and follow the same pattern.

Test cases needed:

Validation handler tests:
- POST /validations/submit with validationType "all" returns 202 with validationId
- POST /validations/submit with validationType "retrieval" returns 202
- POST /validations/submit with validationType "generation" returns 202
- POST /validations/submit with missing validationType returns 400
- POST /validations/submit with invalid validationType returns 400
- POST /validations/submit with empty body returns 400
- GET /validations/{id}/status returns 200 with current status
- GET /validations/{nonexistent-id}/status returns 404

Validation runner tests:
- ValidationRunner updates status to RUNNING
- ValidationRunner calls run_validation with correct type
- ValidationRunner stores result in DynamoDB
- ValidationRunner sets status to PASSED when validation passes
- ValidationRunner sets status to FAILED when validation fails

Validation logic tests:
- run_validation("retrieval") returns retrieval result, generation is None
- run_validation("generation") returns generation result, retrieval is None
- run_validation("all") returns both retrieval and generation results
- All return overall_outcome "PASSED" (placeholder behavior)

ABSOLUTELY DO NOT:
- Modify any existing orchestration code
- Modify any existing test files
- Modify conftest.py at root level
- Modify pytest.ini
- Add new imports to existing files
- Change how existing tests run
- Mix validation classes with orchestration classes
- Use the orchestration DynamoDB table or class
- Use the Executor Lambda for validation
