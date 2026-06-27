What We Built and Why - Full Explanation
Story 2586135 / Task 2887001


The Problem

Caterpillar has CMAs (Condition Monitoring Advisors) who monitor heavy equipment remotely. When a machine raises a fault code (like "hydraulic oil level low"), the CMA AI Assistant automatically generates a summary explaining what the fault means, probable causes, and recommended actions.

This system processes hundreds or thousands of fault codes per batch run. Each one calls OpenAI which costs money. If something breaks (prompt changed, model updated, documents went stale), you could generate thousands of bad summaries before anyone notices. That's wasted money and garbage content going to dealers.

We need a way to automatically check that the system is still producing good results before running a full expensive batch.


The Solution

We built a new dedicated endpoint: POST /orchestrations/validate

Instead of generating summaries for real fault codes, this endpoint runs a small set of known test cases (about 10-12 keys) where we already know what the correct answers are. It checks two things:

1. Retrieval: Are we finding the right documents? When the system searches for information about a fault code, does it pull back the correct troubleshooting guides? We compare the document IDs that come back against the document IDs we know should come back.

2. Generation: Is the AI writing a good summary? Once the system generates a summary, is it similar enough to the correct summary that humans already verified? We compare the generated text against the known-good text using similarity scoring.

If both checks pass, we're confident the system is working well and it's safe to run a full batch. If either check fails, we stop and investigate before wasting money.


Where We Made Changes

There are two separate repositories involved:


REPO 1: P-Apigee-APIResources (the spec repo)

This repo contains only the API specification. It defines what the service accepts and returns. Think of it as the menu that everyone reads before calling the service.

File changed:
APISpecifications/INTERNAL/AnalyticsExecution/aexCMAAIAssistantOrchestrationService/catDigitalPlatform-aexCMAAIOrchestrationService-v1-oas.yaml

What we added to this file:

New endpoint definition (POST /orchestrations/validate):
This tells everyone that a new endpoint exists. It defines that you send a validationType ("retrieval", "generation", or "all") and you get back an orchestrationId with status PENDING. Just like the existing instantiate endpoint, it's async - you start it and then poll for results.

New request schema (ValidateOrchestrationRequest):
Defines exactly what the request body looks like. validationType is required and must be one of the three allowed values. notificationMail is optional.

New response schema (ValidationResult):
Defines what the validation results look like when you poll the status endpoint. It has two sections (retrieval and generation), each showing how many tests ran, passed, and failed. Plus an overall outcome and a link to the full report in S3.

New statuses (VALIDATING, VALIDATION_FAILED):
Added to the OrchestrationStatus enum. VALIDATING means tests are currently running. VALIDATION_FAILED means the tests didn't pass the quality bar.

New examples:
Shows exactly what the requests and responses look like for different scenarios (validation in progress, validation passed, validation failed, only retrieval requested, etc.).

Why this file matters: Every team that interacts with this service (Foresight, Data Science, other platform teams) looks at this spec. It's the source of truth for what the API does. If it's not in the spec, it doesn't exist as far as consumers are concerned.


REPO 2: aex-cma-ai-assistant / orchestration (the code repo)

This repo contains the actual Python code that makes the service work. When someone calls the API, this code runs.

Files we changed:


Request handler (functions/request_handler/)

What it does: This is the Lambda function that receives the HTTP request from API Gateway. It's the front door.

What we added: A new route for /orchestrations/validate. When a POST comes in to that path, it:
- Reads the JSON body
- Checks that validationType is present and valid
- Returns 400 if anything is wrong
- Creates a record in DynamoDB saying "hey, someone requested a validation run"
- Triggers the executor Lambda to do the actual work
- Returns 202 immediately with an orchestrationId so the caller can check back later

Why: Without this, the service would return 404 for /validate because it wouldn't know how to handle that path.


Executor (functions/executor/)

What it does: This is the Lambda that does the heavy lifting. After the request handler creates the record and triggers it, this is what actually runs.

What we added: A check at the beginning that says "is this a validation run or a normal orchestration?" If it's validation:
- Set the status to VALIDATING so the caller knows we started
- Call the validation function with the requested type
- Save the results
- Set status to SUCCEEDED or VALIDATION_FAILED based on the outcome
- Send notification email if configured

If it's NOT validation, it does exactly what it always did (generate summaries for keys). We didn't touch that path at all.

Why: The executor needs to know about the new type of work it can be asked to do.


Validation module (functions/executor/validation.py)

What it does: This is where the actual validation logic lives. Right now it's a placeholder that always returns PASSED with zero tests run.

What it will do in the future:
- Load the 10-12 ground truth test keys from storage
- For each key, call GenAI to generate a summary
- For retrieval: extract the document IDs from the response, compare against expected documents
- For generation: extract the summary text, compare against the ground truth summary using similarity scoring
- Produce a detailed per-key report
- Return pass/fail

Why it's a placeholder: The ground truth test data doesn't exist yet in a stored format. The similarity scoring approach hasn't been finalized (cosine similarity vs LLM-as-judge). Kevin said to build the plumbing now and fill in the logic later. This way when those pieces are ready, we just update this one file.

Why it's in its own file: Separation of concerns. The validation logic is complex and independent. Having it isolated means the data science team or whoever implements the real logic later doesn't need to understand the executor or request handler. They just fill in this function.


Validation result models (common/models/)

What it does: Defines the data structures for validation results.

RetrievalValidationResult: outcome (PASSED/FAILED/ERROR), tests_run, tests_passed, tests_failed
GenerationValidationResult: outcome (PASSED/FAILED/ERROR), tests_run, tests_passed, tests_failed  
ValidationResult: combines retrieval + generation results, overall_outcome, report_location

Why: Having defined models means everyone uses the same structure. The executor creates a ValidationResult, stores it in DynamoDB, and the status endpoint reads it back out. If it were just a loose dictionary, typos and inconsistencies would creep in.


Status endpoint updates (request_handler / api_responses)

What we added: When someone calls GET /orchestrations/{id}/status, if that orchestration was a validation run, include the validationResult in the response. If it was a normal orchestration, don't include it (keep existing behavior exactly the same).

Why: The caller needs to see what happened. After they send a validate request, they poll this endpoint to find out: is it still running? Did it pass? Which part failed? Where's the detailed report?


Tests

What we added: Tests covering:
- Valid requests return 202 (all three validationTypes)
- Invalid requests return 400 (missing validationType, wrong values, bad JSON)
- Executor enters validation flow for validation orchestrations
- Executor does NOT enter validation flow for normal orchestrations
- Status endpoint includes validationResult for validation runs
- Status endpoint does NOT include validationResult for normal runs
- All existing tests still pass (nothing broken)

Why: Tests prove it works. They also protect against future developers accidentally breaking the feature when they make changes to other parts of the code.


How It All Fits Together

1. Someone sends: POST /orchestrations/validate {"validationType": "all"}

2. API Gateway receives the HTTP request, routes it to the Request Handler Lambda

3. Request Handler:
   - Parses the body, validates validationType is "all"
   - Creates DynamoDB record: {id: "abc", status: "PENDING", type: "validation", validationType: "all"}
   - Triggers Executor Lambda
   - Returns 202: {orchestrationId: "abc", status: "PENDING"}

4. Executor Lambda picks up the work:
   - Reads DynamoDB record, sees type is "validation"
   - Updates status to "VALIDATING"
   - Calls run_validation("all")
   - Gets back: {retrieval: PASSED, generation: PASSED, overall: PASSED}
   - Stores validationResult in DynamoDB
   - Updates status to "SUCCEEDED"
   - Sends notification email

5. Caller polls: GET /orchestrations/abc/status
   - Response: {status: "SUCCEEDED", validationResult: {retrieval: {outcome: "PASSED", ...}, generation: {outcome: "PASSED", ...}}}

6. Caller sees everything passed. Safe to run a full batch of thousands of keys via the normal /instantiate endpoint.


What's a Key?

A key is a combination of serial number prefix + rollup key that identifies a specific fault code on a specific type of machine. Format: "PREFIX-TYPE|NUMBER,TYPE"

Examples:
- "KYD-PL|2126,PL" means serial prefix KYD, Product Link fault code 2126
- "BXD-PL|100-3" means serial prefix BXD, fault code 100-3

The ground truth test set has about 10-12 of these keys where we already know:
- Which SIS documents should be retrieved (document IDs like "i05380240")
- What a correct summary looks like (written and verified by humans)


What's Left (Future Work)

- Store the ground truth test data somewhere (S3 or config)
- Implement actual GenAI calls in the validation function
- Implement document ID comparison logic for retrieval validation
- Decide and implement similarity scoring for generation validation (cosine similarity or LLM-as-judge)
- Generate detailed per-key reports and store in S3
- Determine pass/fail thresholds

These are all future stories. What we built is the complete structure that's ready to receive the real logic.


Testing Status

- All unit tests pass (143+)
- Spec validates with no errors
- Request handling logic tested locally
- Cannot test against real infrastructure without DEV deployment (need Luba's help for that)
