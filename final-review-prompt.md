FINAL REVIEW AND FIX PROMPT
============================

I have a PR with 12 review comments from Luba (oravel_cat). I need you to fix ALL issues. Here is exactly what the reviewer wants. Do not deviate from this.

CONTEXT:
- Repo: aex-cma-ai-assistant/orchestration
- The orchestration service has an existing Request Handler Lambda that routes all API requests
- The orchestration service has an existing Executor Lambda that runs orchestration logic
- We are adding validation as a separate capability but within the same Orchestration Service context
- CI/CD uses GitHub Actions, NOT Azure DevOps

THE REVIEWER'S REQUIREMENTS (non-negotiable):

1. STAY IN ORCHESTRATION SERVICE CONTEXT
   - Do NOT create a validation_service folder
   - Everything stays under orchestration_service
   - Validation is a new capability within the existing service, not a new service

2. REQUEST HANDLER IS THE GLOBAL ROUTER
   - Do NOT create a separate validation request handler Lambda
   - The existing Request Handler Lambda serves as a router for ALL endpoints
   - Just add /validations/submit and /validations/{validationId}/status as new routes in the existing request handler
   - Delete any CloudFormation template for a separate validation request handler Lambda (e.g., pfm-aex-cmaai-orchestration-svc-validation-request-handler-lam.yml)

3. EXECUTOR LAMBDA MUST NOT BE TOUCHED
   - Do NOT import anything from validation into the executor
   - Do NOT add validation checks or branches in the executor
   - Do NOT add _is_validation_orchestration() or _handle_validation_execution()
   - Revert executor/app.py to exactly what it was on master
   - Command: git checkout origin/master -- orchestration/src/orchestration_service/functions/executor/app.py

4. SEPARATE VALIDATIONRUNNER LAMBDA
   - Create a NEW Lambda called ValidationRunner
   - This lives at: orchestration/src/orchestration_service/functions/validation_runner/app.py
   - The CloudFormation template for this Lambda must point to the correct handler (e.g., orchestration_service.functions.validation_runner.app.handler or whatever pattern the executor uses)
   - This Lambda reads from the VALIDATION DynamoDB table, runs validation logic, stores results

5. SEPARATE DYNAMODB TABLE
   - Create a new table: pfm-aex-cmaai-orchestration-svc-validations
   - Create a SEPARATE DynamoDB operations class (e.g., validation_operations.py)
   - Do NOT modify the existing operations.py (orchestration DynamoDB class)
   - Do NOT add validation fields to the orchestration table or class
   - The new class should follow the same patterns as operations.py but be completely independent

6. SEPARATE RESPONSE MODELS
   - Create new response classes for validation (e.g., validation_responses.py)
   - Do NOT modify api_responses.py
   - Do NOT add validation_result to GetStatusResponse or any orchestration response class

7. NO __init__.py FILES
   - The codebase does not use __init__.py files
   - Delete ALL __init__.py files you created
   - Check: git diff origin/master --name-only | grep __init__

8. DO NOT MODIFY TEST INFRASTRUCTURE
   - Do NOT modify tests/conftest.py
   - Do NOT modify pytest.ini
   - Do NOT add os.chdir or Path manipulation
   - Do NOT change pythonpath or testpaths
   - Revert if changed: git checkout origin/master -- orchestration/tests/conftest.py
   - Revert if changed: git checkout origin/master -- orchestration/pytest.ini
   - Follow the EXACT existing test file structure and patterns

9. USE GITHUB ACTIONS NOT AZURE DEVOPS
   - Do NOT create or modify azure-pipelines/ files (build.yml, deploy.yml)
   - CI/CD is done via GitHub Actions
   - Reference workflow: https://github.com/cat-digital-platform/P-Stonecutters/blob/master/.github/workflows/cmaai-orchestration-svc-cicd.yml
   - If you need to add CI/CD for ValidationRunner, follow that workflow pattern
   - Delete any Azure pipeline files you created

10. ENDPOINT PATHS
    - Submit validation: POST /validations/submit (NOT /orchestrations/validate)
    - Check status: GET /validations/{validationId}/status (NOT /orchestrations/{id}/status)

---

FILES TO DELETE:
- orchestration/src/validation_service/ (entire folder if it exists)
- Any pfm-aex-cmaai-orchestration-svc-validation-request-handler-lam.yml
- Any __init__.py files you created
- Any azure-pipelines files you created or modified (build.yml, deploy.yml)

FILES TO REVERT TO MASTER (git checkout origin/master -- <file>):
- orchestration/tests/conftest.py
- orchestration/pytest.ini
- orchestration/src/orchestration_service/functions/executor/app.py
- orchestration/src/orchestration_service/common/dynamodb/operations.py
- orchestration/src/orchestration_service/common/models/api_responses.py

FILES TO CREATE (new):
- orchestration/src/orchestration_service/functions/validation_runner/app.py (ValidationRunner Lambda handler + placeholder validation logic)
- orchestration/src/orchestration_service/common/dynamodb/validation_operations.py (separate DynamoDB class for validation table)
- orchestration/src/orchestration_service/common/models/validation_responses.py (separate response models for validation)
- orchestration/cloudformation/orchestration-service/pfm-aex-cmaai-orchestration-svc-validation-runner-lam.yml (CloudFormation for ValidationRunner Lambda with correct handler reference)
- orchestration/cloudformation/orchestration-service/pfm-aex-cmaai-orchestration-svc-validations-ddb.yml (CloudFormation for validation DynamoDB table)
- Test files under orchestration/tests/ following existing patterns

FILES TO MODIFY (existing):
- orchestration/src/orchestration_service/functions/request_handler/app.py (ADD two new route cases: /validations/submit and /validations/{validationId}/status. Do NOT remove or change existing routes)

---

VALIDATION LOGIC (placeholder):
The validation_runner/app.py should contain or import a run_validation function that:
- Accepts validation_type ("retrieval", "generation", or "all")
- If "retrieval" or "all": returns a retrieval result with outcome=PASSED, tests_run=0, tests_passed=0, tests_failed=0
- If "generation" or "all": returns a generation result with outcome=PASSED, tests_run=0, tests_passed=0, tests_failed=0
- Returns overall_outcome=PASSED
- Returns report_location as a placeholder string

THE FLOW:
1. User sends POST /validations/submit {validationType: "all"}
2. Existing Request Handler Lambda receives it, routes to validation submit handler
3. Handler creates record in VALIDATION DynamoDB table (status: PENDING)
4. Handler triggers ValidationRunner Lambda asynchronously
5. Handler returns 202 {validationId, status: PENDING}
6. ValidationRunner Lambda picks up, reads validation table, updates status to RUNNING
7. ValidationRunner calls run_validation("all"), gets placeholder PASSED result
8. ValidationRunner stores result in validation table, updates status to PASSED
9. User polls GET /validations/{validationId}/status
10. Request Handler routes to validation status handler, reads from VALIDATION table, returns result

---

AFTER ALL CHANGES, VERIFY:
1. git diff origin/master -- orchestration/tests/conftest.py (should be empty - no changes)
2. git diff origin/master -- orchestration/pytest.ini (should be empty - no changes)
3. git diff origin/master -- orchestration/src/orchestration_service/functions/executor/app.py (should be empty - no changes)
4. git diff origin/master -- orchestration/src/orchestration_service/common/dynamodb/operations.py (should be empty - no changes)
5. git diff origin/master -- orchestration/src/orchestration_service/common/models/api_responses.py (should be empty - no changes)
6. find . -name "__init__.py" in your new files (should find NONE)
7. No validation_service folder exists
8. No azure-pipelines files were added/modified
9. No validation-request-handler-lam.yml exists
10. python3 -m compileall on all new files passes
11. All existing tests still pass
12. New tests pass
