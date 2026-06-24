Retrieval Evaluation - Implementation Summary
Story 2586135


What is this project about

The CMA AI Assistant helps Caterpillar's Condition Monitoring Advisors (CMAs) by automatically generating summaries for machine fault codes. Instead of manually searching through hundreds of pages of service manuals, the AI reads the relevant documents and produces a summary with probable causes, recommended actions, and consequences of inaction.

The system processes hundreds or thousands of fault codes in a single batch run. Each one costs money because it calls OpenAI. If something goes wrong (bad prompt, model change, stale documents), you could generate thousands of useless summaries before anyone notices.


What problem are we solving

Right now there's no automated way to check if the system is still producing good results before running a full batch. The data science team manually reviews samples, which is slow and doesn't scale.

We want to add a validation step that runs automatically before the batch starts. Think of it like a health check. Run a few known test cases, compare the results against what we know is correct, and only proceed if quality looks good. If it doesn't look good, stop early and save the money.


What we built

We added a new option called retrievalEvaluation to the orchestration service. When you set it to true, the service runs validation tests before generating summaries.

The implementation is a placeholder right now. The actual validation model (Context Relevancy) is still being built by the data science team. What we've done is build all the plumbing so that when that model is ready, it plugs right in without needing to restructure anything.


The files and what each one does


1. orchestrationService-v1-oas.yaml

Location: orchestration/src/orchestration_service/resources/

This is the API specification, the formal contract that defines what the service accepts and returns. Every team that calls this service (Foresight, Data Science, internal tools) reads this to know what's available.

What we added:
- retrievalEvaluation: a true/false parameter on the instantiate request. When true, tells the service to run validation before generating summaries. Defaults to false so existing behavior is unchanged.
- VALIDATING status: a new orchestration state that means validation tests are currently running.
- VALIDATION_FAILED status: means validation did not pass the quality bar, summaries were not generated, money was saved.
- ValidationResult schema: a new object in the status response showing the outcome (PASSED/FAILED/ERROR), how many tests ran, how many passed, how many failed, and where to find the detailed report.

Why we did it: The spec comes first because it's the agreement between everyone. Before writing any code, we define what the API looks like so other teams can build against it and the API gateway can validate incoming requests automatically.


2. common/models/validation.py

Location: orchestration/src/orchestration_service/common/models/

This is a Python dataclass that defines the shape of a validation result:

    class ValidationResult:
        outcome: str          -> "PASSED", "FAILED", or "ERROR"
        tests_run: int        -> how many ground-truth test cases were evaluated
        tests_passed: int     -> how many met the quality threshold
        tests_failed: int     -> how many did not meet the threshold
        details: str          -> S3 path to full report or a message

Why we did it: Without a defined model you'd pass around raw dictionaries and hope everyone spells the keys the same way. A dataclass gives you type safety, makes the code self-documenting, and means if someone adds a new field later it's obvious where it lives.


3. functions/executor/validation.py

Location: orchestration/src/orchestration_service/functions/executor/

This is where the actual validation logic lives. Right now it's a placeholder function called run_retrieval_evaluation() that always returns PASSED with zero tests run.

What it does now:
    def run_retrieval_evaluation() -> ValidationResult:
        return ValidationResult(
            outcome="PASSED",
            tests_run=0,
            tests_passed=0,
            tests_failed=0,
            details="Validation placeholder - Context Relevancy model integration pending"
        )

What it will do in the future when the data science team delivers the Context Relevancy model:
1. Load ground-truth test data (known inputs with known correct outputs)
2. For each test case, call GenAI to generate a summary
3. Send the generated summary plus the retrieved documents to the Context Relevancy model
4. Get back quality scores (context relevancy, faithfulness, answer relevancy, context recall, context precision)
5. Compare each score against configured thresholds
6. Produce a detailed report and store it in S3
7. Return pass or fail based on how many tests met the bar

Why it's separate: Kevin said build the structure now, fill in the logic later. By putting validation in its own file, when the model is ready we only change this one file. Nothing else in the system needs to be touched.


4. functions/executor/executor.py (modified)

Location: orchestration/src/orchestration_service/functions/executor/

This is the main orchestration function that already existed. It handles the normal flow of resolving keys, calling GenAI for each one, and storing results.

What we added (a conditional branch at the beginning):

    def execute_orchestration(request):
        retrieval_evaluation = request.get("retrievalEvaluation", False)

        if retrieval_evaluation:
            update_status(orchestration_id, "VALIDATING")
            validation_result = run_retrieval_evaluation()
            store_validation_result(orchestration_id, validation_result)

            if validation_result.outcome == "FAILED":
                update_status(orchestration_id, "VALIDATION_FAILED")
                return  # Stop here. Don't generate summaries. Save money.

            if not keys:
                update_status(orchestration_id, "SUCCEEDED")
                return  # Validation-only mode. Done.

        # Everything below is existing code, unchanged
        update_status(orchestration_id, "PROCESSING")
        for key in resolve_keys(keys):
            generate_summary(key)
        update_status(orchestration_id, "SUCCEEDED")

Why we did it: This is the core decision point. If retrievalEvaluation is true, check quality first. If quality is bad, stop. If quality is good, proceed. If retrievalEvaluation is false or missing, skip the whole thing and run the normal flow exactly as before.


5. functions/request_handler/ (modified)

Location: orchestration/src/orchestration_service/functions/request_handler/

This is the Lambda that receives the HTTP POST from API Gateway. It's the front door of the service.

What we added:

    def handle_instantiate(event):
        body = parse_body(event)
        retrieval_evaluation = body.get("retrievalEvaluation", False)

        # Validate it's actually a boolean
        if not isinstance(retrieval_evaluation, bool):
            return error_response(400, "retrievalEvaluation must be a boolean")

        # Allow requests without keys if doing validation only
        if not keys and not retrieval_evaluation:
            return error_response(400, "Either keys or retrievalEvaluation must be provided")

        # Store everything including the new flag
        create_orchestration_record(
            keys=keys,
            retrieval_evaluation=retrieval_evaluation,
            ...
        )

Why we did it: The front door needs to accept the new field, make sure it's valid (reject garbage like "yes" or 123 instead of true/false), and store it so the executor knows what to do later. We also had to relax the validation that previously required keys on every request, since validation-only mode doesn't need keys.


6. api_responses.py / status endpoint (modified)

Location: orchestration/src/orchestration_service/functions/request_handler/

When someone polls GET /orchestrations/{id}/status, the response now includes validationResult if validation was run:

    def handle_get_status(orchestration_id):
        record = get_record(orchestration_id)
        response = {
            "orchestrationId": record["orchestrationId"],
            "status": record["status"]
        }
        if record.get("validationResult"):
            response["validationResult"] = record["validationResult"]
        return response

Why we did it: The caller needs to see what happened with validation. Without this they'd have no way to know if it passed, failed, how many tests ran, or where the report is.


7. Test files

Modified:
- tests/orchestration_service/functions/executor/test_executor.py
- tests/orchestration_service/functions/request_handler/conftest.py
- tests/orchestration_service/functions/request_handler/test_request.py

New test data files:
- tests/.../request_handler/_data/instantiate_retrieval_evaluation_only.json (simulates validation-only request)
- tests/.../request_handler/_data/instantiate_validation_error_10.json (simulates invalid input for error handling)

What the tests verify:
- Executor enters validation branch when retrievalEvaluation is true
- Executor skips validation when retrievalEvaluation is false (existing behavior unchanged)
- Validation-only mode works (no keys, just validation)
- Request handler accepts valid retrievalEvaluation input
- Request handler rejects invalid input (non-boolean values)
- All 143 tests pass including all previously existing tests

Why we did it: Tests prove the new code works and the old code wasn't broken. If someone changes something later and a test fails, they know immediately what went wrong.


How the flow works end to end

Normal flow (no validation, same as before):
Someone sends a list of fault codes. Service goes PENDING then PROCESSING then SUCCEEDED. Summaries are generated for each key. Nothing about this changed.

Validation with fault codes:
Someone sends fault codes and sets retrievalEvaluation to true. Service goes PENDING then VALIDATING (runs ground-truth tests). If tests pass, continues to PROCESSING (generates summaries) then SUCCEEDED. If tests fail, goes to VALIDATION_FAILED and stops. No summaries generated, no money wasted.

Validation only (no fault codes):
Someone sends just retrievalEvaluation true with no keys. Service goes PENDING then VALIDATING then SUCCEEDED. Just runs tests and reports results. Useful for the data science team to check quality without triggering a full batch.


What's left to do (future work, not this story)

- Integrate the actual Context Relevancy model when the data science team (Ocelot) delivers it
- Load real ground-truth test data (location to be determined with Luba and data science team)
- Implement threshold comparison logic
- Generate detailed validation reports and store them in S3
- Possibly add a second model for SIS summary quality evaluation

These are all future stories. This story was about building the structure and making the service ready to receive the real validation logic when it comes.


Testing status

What passed:
- 143 unit tests (all existing plus new ones for the validation paths)
- API spec validation (no schema errors)
- Local testing of request handling (correctly accepts valid requests, rejects invalid ones)

What still needs testing and requires deployment to the DEV environment:
- End-to-end API calls against real infrastructure
- Status transitions in the actual database
- Full request-to-status-poll cycle

Waiting on Kevin for DEV deployment guidance and on Luba for a code walkthrough.
