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

orchestrationService-v1-oas.yaml (the API spec)

This is the contract that defines what the API accepts and what it returns. It's like a menu at a restaurant. Before you cook anything, everyone agrees on what's on the menu.

What we added:
- retrievalEvaluation: a true/false parameter on the instantiate request. When true, run validation.
- VALIDATING status: tells the caller that validation tests are currently running.
- VALIDATION_FAILED status: tells the caller that validation did not pass, summaries were not generated.
- ValidationResult: a new object in the status response that shows how validation went (how many tests ran, how many passed, how many failed, where to find the full report).

Why it matters: Every team that calls this service (Foresight, Data Science, other internal tools) looks at this spec to know what's available. By updating the spec first, everyone can see the new capability and build against it.


common/models/validation.py (the data model)

This defines the shape of a validation result. It's a Python dataclass with these fields:
- outcome: did it pass, fail, or error out
- tests_run: how many test cases were evaluated
- tests_passed: how many met the quality bar
- tests_failed: how many did not
- details: where to find the full report (an S3 file path or a message)

Why it matters: Without a defined model, you'd pass around raw dictionaries and hope everyone spells the keys the same way. A model gives you consistency, type checking, and makes the code self-documenting.


functions/executor/validation.py (the validation function)

This is where the actual validation work will happen. Right now it's a placeholder that always returns "PASSED" with zero tests run.

In the future, this function will:
1. Load ground-truth test data (known inputs with known correct outputs)
2. For each test case, generate a summary using GenAI
3. Send the result to the Context Relevancy model for scoring
4. Compare scores against thresholds
5. Produce a detailed report
6. Return pass or fail

Why it's a placeholder: The Context Relevancy model isn't built yet. Kevin specifically said to build the structure now and fill in the real logic later. This way the data science team can work on the model independently, and when it's ready we just update this one file.


functions/executor/executor.py (the orchestration brain)

This is the main function that runs the orchestration. It already existed and handled the normal flow of processing keys and generating summaries.

What we added: A conditional branch at the top that checks if retrievalEvaluation is true. If it is:
1. Update the status to VALIDATING
2. Call run_retrieval_evaluation()
3. If the result is FAILED, update status to VALIDATION_FAILED and stop. Don't generate any summaries. Don't spend any money.
4. If the result is PASSED, continue with normal summary generation (if keys were provided) or just finish (if it was validation-only).

If retrievalEvaluation is false or not provided, everything works exactly as before. No change to existing behavior.

Why it matters: This is the actual decision point. It's what prevents bad summaries from being generated when quality has degraded.


functions/request_handler/ (the front door)

This is the Lambda that receives the HTTP request from API Gateway. It parses the JSON body, validates the input, creates a record in DynamoDB, and triggers the executor.

What we added:
- Parse the retrievalEvaluation field from the request body
- Validate that it's a boolean (reject if someone sends a string or number)
- Allow requests without keys when retrievalEvaluation is true (validation-only mode)
- Store the flag in DynamoDB so the executor and status endpoint can read it

Why it matters: This is the entry point. If it doesn't accept and validate the new field, nothing else works.


api_responses.py / status endpoint (the response)

When a user polls the status endpoint to check how their orchestration is going, the response now includes validationResult if validation was run.

Why it matters: The caller needs to know what happened. Did validation pass? How many tests ran? Where's the detailed report? Without this in the response, the validation results would be invisible.


test files (proving it works)

- test_executor.py: Tests that the executor correctly enters the validation branch, handles pass and fail, and doesn't break existing flows.
- conftest.py: Shared test setup for the new test scenarios.
- _data/instantiate_retrieval_evaluation_only.json: Sample request payload for validation-only mode.
- _data/instantiate_validation_error_10.json: Sample invalid request to test error handling.

Why it matters: 143 tests pass. This proves the new code works and the old code wasn't broken. Without tests you're guessing.


How the flow works end to end

Normal flow (no validation, same as before):
User sends: keys with a list of fault codes
Service does: PENDING, PROCESSING (generates summaries for each key), SUCCEEDED
Nothing changed here.

Validation with keys:
User sends: keys with a list, retrievalEvaluation true
Service does: PENDING, VALIDATING (runs ground-truth tests), if passed then PROCESSING (generates summaries), SUCCEEDED
If validation fails: PENDING, VALIDATING, VALIDATION_FAILED (stops, no summaries generated, saves money)

Validation only (no keys):
User sends: retrievalEvaluation true, no keys
Service does: PENDING, VALIDATING, SUCCEEDED (just runs tests and reports results)
Useful for the data science team to check quality without triggering a full batch.


What's left to do (future work, not this story)

- Integrate the actual Context Relevancy model when Ocelot delivers it
- Load real ground-truth test data (location TBD with Luba and data science team)
- Implement threshold comparison logic
- Generate detailed validation reports and store in S3
- Possibly add a second model for SIS summary quality evaluation

These are all future stories. This story was about building the structure and making the service ready.


Testing status

What passed:
- 143 unit tests via pytest (all existing plus new validation tests)
- Spec validation (no schema errors)
- Local handler invocation (accepts valid requests, rejects invalid ones)

What still needs testing (requires DEV deployment):
- End-to-end API calls against real infrastructure
- DynamoDB status transitions in a live environment
- Full request-to-status-poll cycle

Waiting on Kevin for DEV deployment guidance and on Luba for a code walkthrough.
