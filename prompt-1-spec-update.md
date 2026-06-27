PROMPT FOR COPILOT - SPEC REPO (P-Apigee-APIResources)

Open this file:
APISpecifications/INTERNAL/AnalyticsExecution/aexCMAAIAssistantOrchestrationService/catDigitalPlatform-aexCMAAIOrchestrationService-v1-oas.yaml

I need to add a new endpoint to this OpenAPI spec. Keep everything that already exists exactly as it is. Do not modify the existing /orchestrations/instantiate, /orchestrations/{orchestrationId}/cancel, or /orchestrations/{orchestrationId}/status endpoints.

BACKGROUND:
The CMA AI Orchestration service generates AI summaries for Caterpillar machine fault codes. Each fault code is identified by a "key" which is a combination of serial number prefix + rollup key (e.g., "KYD-PL|2126,PL"). The service uses a RAG pattern: it searches a Knowledge Base for relevant SIS documents, sends them to OpenAI, and gets back a summary.

We need to validate that this process is working correctly by testing against known ground truth data. There are approximately 10-12 pre-defined keys where we know:
- Which documents SHOULD be retrieved (expected document IDs like "i05380240", "i01392966")
- What a correct summary SHOULD look like (ground truth summaries verified by humans)

The validation runs these known keys through the system and checks:
1. Retrieval check: Did the system retrieve the correct documents? Compare actual document IDs in the response against expected document IDs.
2. Generation check: Is the generated summary similar enough to the ground truth summary? Compare using similarity scoring (cosine similarity or LLM-as-judge).

Add the following:

1. A new path: POST /orchestrations/validate

This is a separate dedicated endpoint for running ground truth validation tests. It validates retrieval quality and AI summary generation against saved ground truth data for a pre-defined set of approximately 10-12 keys.

The request body should accept:
- validationType: a required string enum with values "retrieval", "generation", or "all"
  - "retrieval" means only validate that the correct documents were retrieved for each test key. The system will run each key through GenAI, look at the document IDs referenced in the JSON response, and compare them against expected ground truth document IDs.
  - "generation" means only validate that the generated summary is similar to the ground truth summary. The system will run each key through GenAI, get the generated summary, and compare it against the known-correct ground truth summary using similarity scoring.
  - "all" means run both retrieval and generation validation for each test key.
- notificationMail: optional, same format as the existing instantiate endpoint (single email or array of emails)

The response should be 202 with the same InstantiateOrchestrationResponse schema (returns orchestrationId and status PENDING).

Add appropriate 400, 401, 403, 404, 429, 500, 503 error responses same as the other endpoints.

Add the x-amazon-apigateway-integration same as the other endpoints pointing to RequestHandlerLambdaArn.

2. Add examples under the new endpoint showing:

Example 1 - Run all validation:
{
  "validationType": "all",
  "notificationMail": "generic.user@cat.com"
}

Example 2 - Run only retrieval validation:
{
  "validationType": "retrieval"
}

Example 3 - Run only generation/summary validation:
{
  "validationType": "generation",
  "notificationMail": "generic.user@cat.com"
}

3. Add to the components/schemas section:

ValidateOrchestrationRequest:
  type: object
  required: [validationType]
  properties:
    validationType:
      type: string
      enum: [retrieval, generation, all]
      description: |
        Specifies which ground truth validation tests to run.
        - "retrieval": Validates that the correct SIS documents are being retrieved for each test key. 
          For each of the pre-defined ground truth keys, the system runs GenAI instantiate, extracts 
          the referenced document IDs from the response, and compares them against the expected 
          ground truth document IDs.
        - "generation": Validates that the AI-generated summaries are similar to known-correct ground 
          truth summaries. For each test key, the system generates a summary and compares it against 
          the ground truth summary using similarity scoring.
        - "all": Runs both retrieval and generation validation for each test key.
    notificationMail: (same as existing - oneOf string or array)

4. Update OrchestrationStatus enum to add:
- VALIDATING
- VALIDATION_FAILED

Keep the existing values (PENDING, PROCESSING, SUCCEEDED, FAILED, ABORTED) as they are.

5. Add a new schema ValidationResult:
  description: |
    Results from ground truth validation. Contains separate results for retrieval 
    and generation checks depending on what was requested. Each section shows how many 
    of the pre-defined test keys passed or failed validation.
  properties:
    retrieval (optional object):
      description: Results from retrieval validation. Checks if correct documents were retrieved for each test key.
      outcome: string enum [PASSED, FAILED, ERROR]
      testsRun: integer (number of ground truth keys tested)
      testsPassed: integer (number of keys where retrieved documents matched expected)
      testsFailed: integer (number of keys where retrieved documents did NOT match expected)
    generation (optional object):
      description: Results from generation/summary validation. Checks if generated summaries are similar to ground truth summaries.
      outcome: string enum [PASSED, FAILED, ERROR]
      testsRun: integer (number of ground truth keys tested)
      testsPassed: integer (number of keys where summary similarity met threshold)
      testsFailed: integer (number of keys where summary similarity was below threshold)
    overallOutcome: string enum [PASSED, FAILED, ERROR]
      description: PASSED only if all requested validation types passed. FAILED if any failed.
    reportLocation: string
      description: S3 URI to the full detailed report containing per-key results showing which specific keys passed/failed and why.
      example: "s3://aex-cmaai-orchestration-output/validation/b8bc2535-5896-4638-9987-17540b417c69/report.json"

6. Update OrchestrationStatusResponse to include an optional validationResult field that references the ValidationResult schema.

7. Add response examples on the /orchestrations/{orchestrationId}/status endpoint showing:

Example: Validation in progress
{
  "orchestrationId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "status": "VALIDATING"
}

Example: Retrieval validation passed, generation failed
{
  "orchestrationId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "status": "VALIDATION_FAILED",
  "validationResult": {
    "retrieval": {
      "outcome": "PASSED",
      "testsRun": 12,
      "testsPassed": 11,
      "testsFailed": 1
    },
    "generation": {
      "outcome": "FAILED",
      "testsRun": 12,
      "testsPassed": 7,
      "testsFailed": 5
    },
    "overallOutcome": "FAILED",
    "reportLocation": "s3://aex-cmaai-orchestration-output/validation/3fa85f64-5717-4562-b3fc-2c963f66afa6/report.json"
  }
}

Example: All validation passed
{
  "orchestrationId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "status": "SUCCEEDED",
  "validationResult": {
    "retrieval": {
      "outcome": "PASSED",
      "testsRun": 12,
      "testsPassed": 12,
      "testsFailed": 0
    },
    "generation": {
      "outcome": "PASSED",
      "testsRun": 12,
      "testsPassed": 11,
      "testsFailed": 1
    },
    "overallOutcome": "PASSED",
    "reportLocation": "s3://aex-cmaai-orchestration-output/validation/3fa85f64-5717-4562-b3fc-2c963f66afa6/report.json"
  }
}

Example: Only retrieval validation requested and passed
{
  "orchestrationId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "status": "SUCCEEDED",
  "validationResult": {
    "retrieval": {
      "outcome": "PASSED",
      "testsRun": 12,
      "testsPassed": 12,
      "testsFailed": 0
    },
    "generation": null,
    "overallOutcome": "PASSED",
    "reportLocation": "s3://aex-cmaai-orchestration-output/validation/3fa85f64-5717-4562-b3fc-2c963f66afa6/report.json"
  }
}

8. Bump the version from 1.0.1 to 1.1.0

CRITICAL RULES:
- Do not remove or modify anything that already exists
- Do not touch the /orchestrations/instantiate endpoint
- Do not touch the /orchestrations/{orchestrationId}/cancel endpoint
- Do not change the existing schemas (InstantiateOrchestrationRequest, etc.)
- Only ADD new content
- Make sure the YAML is valid OpenAPI 3.0.3
- Follow the same formatting and indentation patterns used in the existing spec
