Per-File Prompts for Fixing the PR (Steps 7-13)
=================================================

STEP 7: ValidationRunner Lambda Handler
File to create: orchestration/src/orchestration_service/functions/validation_runner/app.py
--------

Create a new Lambda handler file at orchestration/src/orchestration_service/functions/validation_runner/app.py

This is the handler for the ValidationRunner Lambda. It is completely separate from the Executor Lambda. Do NOT import anything from the executor.

Look at how orchestration/src/orchestration_service/functions/executor/app.py is structured and follow the same patterns for logging, error handling, and environment variable usage. But do NOT copy orchestration logic.

The handler should:
1. Receive an event with a validationId
2. Read the validation record from the VALIDATION DynamoDB table (not the orchestration table). Use the validation_operations class (which will be created separately).
3. Update status to "RUNNING"
4. Read the validationType from the record ("retrieval", "generation", or "all")
5. Call run_validation(validation_type) which returns a ValidationResult (placeholder function, defined in this same file or a separate validation_logic module in this same folder)
6. Store the result back in the validation DynamoDB table
7. If overall_outcome is "PASSED", update status to "PASSED"
8. If overall_outcome is "FAILED", update status to "FAILED"
9. If an error occurs, update status to "ERROR" and log the error
10. Send notification email if notificationMail was configured in the record

The placeholder run_validation function:
- If validation_type is "retrieval" or "all": create a retrieval result with outcome="PASSED", tests_run=0, tests_passed=0, tests_failed=0
- If validation_type is "generation" or "all": create a generation result with outcome="PASSED", tests_run=0, tests_passed=0, tests_failed=0
- Return overall_outcome="PASSED" with report_location as a placeholder message

Use a logger. Add appropriate try/except around the main logic. Follow the same error handling patterns as the executor.

Do NOT create __init__.py files. There are none in this codebase.
Do NOT import from executor or orchestration modules.
The DynamoDB table name should come from an environment variable (e.g., VALIDATION_TABLE_NAME).


STEP 8: Validation DynamoDB Operations Class
File to create: orchestration/src/orchestration_service/common/dynamodb/validation_operations.py
--------

Create a new file at orchestration/src/orchestration_service/common/dynamodb/validation_operations.py

This is a SEPARATE DynamoDB class for the validation table. Do NOT modify the existing operations.py file. Do NOT inherit from or import the existing Orchestration DynamoDB class.

Look at how orchestration/src/orchestration_service/common/dynamodb/operations.py is structured and follow the same patterns for:
- How it initializes the boto3 resource
- How it reads the table name from environment variables
- How it handles errors
- How it logs operations
- The general class structure

But create a completely independent class for the validation table.

Table name: should come from environment variable VALIDATION_TABLE_NAME
Table schema:
- validationId (string, partition key)
- status (string: PENDING, RUNNING, PASSED, FAILED, ERROR)
- validationType (string: retrieval, generation, all)
- notificationMail (string or list, optional)
- createdAt (string, ISO timestamp)
- updatedAt (string, ISO timestamp)
- result (map/dict, the validation result stored as JSON)

Methods needed:
- create_validation(validation_id, validation_type, notification_mail=None) -> creates record with status PENDING and createdAt timestamp
- get_validation(validation_id) -> returns the full record, raises appropriate error if not found
- update_status(validation_id, status) -> updates status and updatedAt timestamp
- store_result(validation_id, result_dict) -> stores the validation result object and updates updatedAt

Follow the same boto3 patterns (get_item, put_item, update_item) as the existing operations.py.
Do NOT create __init__.py files.
Do NOT import from the existing operations.py.


STEP 9: Validation Response Models
File to create: orchestration/src/orchestration_service/common/models/validation_responses.py
--------

Create a new file at orchestration/src/orchestration_service/common/models/validation_responses.py

This contains response models for the validation endpoints. Do NOT modify the existing api_responses.py file. Do NOT add validation fields to existing orchestration response classes.

Look at how orchestration/src/orchestration_service/common/models/api_responses.py is structured (what base classes it uses, how fields are defined, etc.) and follow the same patterns.

Create these classes:

1. RetrievalResult
   - outcome: str (PASSED, FAILED, ERROR)
   - tests_run: int
   - tests_passed: int
   - tests_failed: int

2. GenerationResult
   - outcome: str (PASSED, FAILED, ERROR)
   - tests_run: int
   - tests_passed: int
   - tests_failed: int

3. ValidationResult
   - retrieval: Optional[RetrievalResult] (None if retrieval was not requested)
   - generation: Optional[GenerationResult] (None if generation was not requested)
   - overall_outcome: str (PASSED, FAILED, ERROR)
   - report_location: str (S3 URI or placeholder message)

4. ValidationSubmitResponse
   - validation_id: str
   - status: str

5. ValidationStatusResponse
   - validation_id: str
   - status: str
   - result: Optional[ValidationResult] (None if validation hasn't completed yet)

Use the same base class pattern that api_responses.py uses (if it uses Pydantic BaseModel, use that. If it uses dataclasses, use that. If it uses a custom OrchestrationBaseModel, create an equivalent or just use the same base). Check what the existing file does and match it.

Do NOT create __init__.py files.
Do NOT modify api_responses.py.


STEP 10: Update Request Handler with New Routes
File to modify: orchestration/src/orchestration_service/functions/request_handler/app.py
--------

In the existing request handler file, add two new route cases. Do NOT change any existing routes. Do NOT rename or remove anything.

Add these cases to the match/case block (or if/elif block, whatever pattern exists):

case '/validations/submit':
  - Only accept POST method
  - Parse JSON body
  - Extract validationType (required, must be "retrieval", "generation", or "all")
  - Extract notificationMail (optional)
  - Return 400 if validationType is missing or invalid
  - Generate a new UUID for validationId
  - Call the validation DynamoDB class (validation_operations.py) to create a new record with status PENDING
  - Trigger the ValidationRunner Lambda asynchronously (NOT the Executor Lambda)
  - Return 202 with {validationId, status: "PENDING"}
  - Use the ValidationSubmitResponse model for the response

case '/validations/{validationId}/status':
  (or however the pattern matching works for path parameters in this codebase)
  - Only accept GET method
  - Extract validationId from the path
  - Call validation DynamoDB class to get the record
  - Return 404 if not found
  - Return 200 with {validationId, status, result (if present)}
  - Use the ValidationStatusResponse model for the response

IMPORTANT:
- The ValidationRunner Lambda function name should come from an environment variable (e.g., VALIDATION_RUNNER_FUNCTION_NAME)
- Import validation_operations and validation_responses from their new files
- Do NOT modify the existing /orchestrations/instantiate, /cancel, or /status cases
- Do NOT import anything from executor
- Follow the exact same patterns used by the existing _instantiate function for how it creates records, invokes lambdas, and returns responses
- Look at how path parameters are extracted in the existing /orchestrations/{orchestrationId}/status handler and do the same for /validations/{validationId}/status


STEP 11: Fix CloudFormation Template for ValidationRunner
File to modify: orchestration/cloudformation/orchestration-service/pfm-aex-cmaai-orchestration-svc-validation-runner-lam.yml
--------

The CloudFormation template for the ValidationRunner Lambda exists but Luba said "I don't see handler for this Lambda."

Look at how the existing executor Lambda CloudFormation template (pfm-aex-cmaai-orchestration-svc-executor-lam.yml) defines its handler and follow the same pattern.

The Handler property should point to: orchestration_service.functions.validation_runner.app.handler
(or whatever the correct module path format is based on how executor-lam.yml does it)

Also make sure:
- The Lambda has the VALIDATION_TABLE_NAME environment variable set pointing to the validation DynamoDB table
- It has appropriate IAM permissions to read/write the validation DynamoDB table
- It does NOT have references to the orchestration DynamoDB table (unless needed for something specific)
- Follow the same timeout, memory, runtime settings as the executor Lambda (or adjust if needed)

Also check the DynamoDB CloudFormation template. Make sure the validation table (pfm-aex-cmaai-orchestration-svc-validations) is properly defined with validationId as the partition key.


STEP 12: Delete __init__.py Files
--------

Delete ALL __init__.py files that you created. The codebase does not use them.

Check these locations and delete if they exist:
- Any __init__.py under validation_service/ (if that folder still exists, delete the whole folder)
- Any __init__.py under validation_runner/
- Any __init__.py under common/dynamodb/ that you created
- Any __init__.py under common/models/ that you created

Only delete ones YOU added. If an __init__.py existed on master before your changes, leave it alone. Check with:
  git diff origin/master --name-only | grep __init__


STEP 13: Tests
Files to create: Under orchestration/tests/ following existing patterns
--------

Look at the existing test structure under orchestration/tests/orchestration_service/functions/executor/ and follow exactly the same pattern.

Do NOT modify conftest.py at any level.
Do NOT modify pytest.ini.
Do NOT add os.chdir or Path manipulation anywhere.
Do NOT create __init__.py files in test folders unless they already exist in the existing test structure.

Create test files for:

1. Test file for ValidationRunner (e.g., test_validation_runner.py):
   - Test that handler reads validation record from DynamoDB
   - Test that handler updates status to RUNNING
   - Test that handler calls run_validation with correct validation_type
   - Test that handler stores result in DynamoDB
   - Test that handler sets status to PASSED when validation passes
   - Test that handler sets status to FAILED when validation fails
   - Test that handler sets status to ERROR on exception

2. Test file for validation logic (e.g., test_validation_logic.py):
   - Test run_validation("retrieval") returns retrieval result with generation as None
   - Test run_validation("generation") returns generation result with retrieval as None
   - Test run_validation("all") returns both retrieval and generation results
   - Test all return overall_outcome "PASSED" (placeholder)
   - Test report_location is a non-empty string

3. Test file for validation request handling (e.g., test_validation_handler.py):
   - Test POST /validations/submit with validationType "all" returns 202
   - Test POST /validations/submit with validationType "retrieval" returns 202
   - Test POST /validations/submit with validationType "generation" returns 202
   - Test POST /validations/submit with missing validationType returns 400
   - Test POST /validations/submit with invalid validationType returns 400
   - Test POST /validations/submit with empty body returns 400
   - Test GET /validations/{id}/status returns 200 with status
   - Test GET /validations/{nonexistent-id}/status returns 404

4. Test file for validation DynamoDB operations (e.g., test_validation_operations.py):
   - Test create_validation creates record with PENDING status
   - Test get_validation returns the record
   - Test get_validation raises error for non-existent id
   - Test update_status changes the status field
   - Test store_result saves the result object

Use whatever mocking pattern the existing tests use (moto, unittest.mock, etc.). Look at how existing DynamoDB tests mock the table and do the same.

Place test files in the location that matches the existing test folder structure. If executor tests are at tests/orchestration_service/functions/executor/test_executor.py then validation tests should be at tests/orchestration_service/functions/validation_runner/test_validation_runner.py (or wherever makes sense following the pattern).
