PROMPT FOR COPILOT - SPEC REPO (P-Apigee-APIResources)

Open this file:
APISpecifications/INTERNAL/AnalyticsExecution/aexCMAAIAssistantOrchestrationService/catDigitalPlatform-aexCMAAIOrchestrationService-v1-oas.yaml

I need to add a new endpoint to this OpenAPI spec. Keep everything that already exists exactly as it is. Do not modify the existing /orchestrations/instantiate, /orchestrations/{orchestrationId}/cancel, or /orchestrations/{orchestrationId}/status endpoints.

Add the following:

1. A new path: POST /orchestrations/validate

This is a separate dedicated endpoint for running ground truth validation tests. It validates retrieval quality and AI summary generation against saved ground truth data for a pre-defined set of approximately 10-12 keys.

The request body should accept:
- validationType: a required string enum with values "retrieval", "generation", or "all"
  - "retrieval" means only validate that the correct documents were retrieved
  - "generation" means only validate that the generated summary is similar to the ground truth summary
  - "all" means run both retrieval and generation validation
- notificationMail: optional, same format as the existing instantiate endpoint (single email or array of emails)

The response should be 202 with the same InstantiateOrchestrationResponse schema (returns orchestrationId and status PENDING).

Add appropriate 400, 401, 403, 404, 429, 500, 503 error responses same as the other endpoints.

Add the x-amazon-apigateway-integration same as the other endpoints pointing to RequestHandlerLambdaArn.

2. Add a new example under the new endpoint showing:
{
  "validationType": "all",
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
      description: What type of ground truth validation to run. "retrieval" checks if correct documents are retrieved. "generation" checks if generated summaries match ground truth. "all" runs both.
    notificationMail: (same as existing - oneOf string or array)

4. Update OrchestrationStatus enum to add:
- VALIDATING
- VALIDATION_FAILED

Keep the existing values (PENDING, PROCESSING, SUCCEEDED, FAILED, ABORTED) as they are.

5. Add a new schema ValidationResult:
  properties:
    retrieval (optional object):
      outcome: string enum [PASSED, FAILED, ERROR]
      testsRun: integer
      testsPassed: integer
      testsFailed: integer
    generation (optional object):
      outcome: string enum [PASSED, FAILED, ERROR]
      testsRun: integer
      testsPassed: integer
      testsFailed: integer
    overallOutcome: string enum [PASSED, FAILED, ERROR]
    reportLocation: string (S3 URI to the full detailed report)

6. Update OrchestrationStatusResponse to include an optional validationResult field that references the ValidationResult schema.

7. Add response examples on the /orchestrations/{orchestrationId}/status endpoint showing:
- Validation in progress (status: VALIDATING)
- Validation passed (status: SUCCEEDED with validationResult showing retrieval and generation both PASSED)
- Validation failed (status: VALIDATION_FAILED with validationResult showing which part failed)

8. Bump the version from 1.0.1 to 1.1.0

Do not remove or modify anything that already exists. Only add.
