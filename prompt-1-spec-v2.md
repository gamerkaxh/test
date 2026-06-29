PROMPT FOR COPILOT - SPEC REPO (P-Apigee-APIResources) - VERSION 2

Based on code review feedback, validation must be COMPLETELY SEPARATE from orchestration. Different path, different status endpoint.

Open this file:
APISpecifications/INTERNAL/AnalyticsExecution/aexCMAAIAssistantOrchestrationService/catDigitalPlatform-aexCMAAIOrchestrationService-v1-oas.yaml

IMPORTANT RULES:
- Do NOT modify ANY existing endpoints, schemas, or responses
- Do NOT modify the OrchestrationStatus enum (validation has its own status)
- Do NOT add validationResult to OrchestrationStatusResponse
- Validation is a completely separate world from orchestration
- Only ADD new paths and schemas

Add the following:

1. NEW TAG

Add a new tag:
- name: Validation
  description: |
    Validation endpoints allow to submit and monitor ground truth validation runs.
    Validation tests a pre-defined set of keys (approximately 10-12) against saved ground truth data
    to verify retrieval quality and AI summary generation quality before running full orchestration batches.

2. NEW PATH: POST /validations/submit

This is the endpoint to start a validation run. It is completely separate from /orchestrations/instantiate.

Tags: Validation
OperationId: submitValidation
Summary: Submit a ground truth validation run

x-amazon-apigateway-integration same pattern as other endpoints pointing to RequestHandlerLambdaArn (or a separate ValidationRunner Lambda ARN if applicable).

Request body:
- required: true
- schema: $ref ValidateRequest

Examples:
  runAllValidation:
    summary: Run all validation checks
    value:
      validationType: "all"
      notificationMail: "generic.user@cat.com"
  runRetrievalOnly:
    summary: Run retrieval validation only
    value:
      validationType: "retrieval"
  runGenerationOnly:
    summary: Run generation validation only
    value:
      validationType: "generation"
      notificationMail: "generic.user@cat.com"

Responses:
  202: Validation run submitted successfully
    schema: $ref ValidateResponse
    example:
      validationId: "3fa85f64-5717-4562-b3fc-2c963f66afa6"
      status: "PENDING"
  400, 401, 403, 429, 500, 503: same error responses as other endpoints

3. NEW PATH: GET /validations/{validationId}/status

This is a SEPARATE status endpoint for validation. It does NOT share with /orchestrations/{orchestrationId}/status.

Tags: Validation
OperationId: getValidationStatus
Summary: Get a validation run status

Parameters:
  - name: validationId
    in: path
    required: true
    schema:
      type: string
      format: uuid

Responses:
  200: Validation status retrieved successfully
    schema: $ref ValidationStatusResponse
    examples:
      validationPending:
        summary: Validation pending
        value:
          validationId: "3fa85f64-5717-4562-b3fc-2c963f66afa6"
          status: "PENDING"
      validationRunning:
        summary: Validation in progress
        value:
          validationId: "3fa85f64-5717-4562-b3fc-2c963f66afa6"
          status: "RUNNING"
      validationPassed:
        summary: Validation passed
        value:
          validationId: "3fa85f64-5717-4562-b3fc-2c963f66afa6"
          status: "PASSED"
          result:
            retrieval:
              outcome: "PASSED"
              testsRun: 12
              testsPassed: 12
              testsFailed: 0
            generation:
              outcome: "PASSED"
              testsRun: 12
              testsPassed: 11
              testsFailed: 1
            overallOutcome: "PASSED"
            reportLocation: "s3://aex-cmaai-orchestration-output/validations/3fa85f64-5717-4562-b3fc-2c963f66afa6/report.json"
      validationFailed:
        summary: Validation failed
        value:
          validationId: "3fa85f64-5717-4562-b3fc-2c963f66afa6"
          status: "FAILED"
          result:
            retrieval:
              outcome: "PASSED"
              testsRun: 12
              testsPassed: 11
              testsFailed: 1
            generation:
              outcome: "FAILED"
              testsRun: 12
              testsPassed: 7
              testsFailed: 5
            overallOutcome: "FAILED"
            reportLocation: "s3://aex-cmaai-orchestration-output/validations/3fa85f64-5717-4562-b3fc-2c963f66afa6/report.json"
      retrievalOnlyPassed:
        summary: Only retrieval validation requested and passed
        value:
          validationId: "3fa85f64-5717-4562-b3fc-2c963f66afa6"
          status: "PASSED"
          result:
            retrieval:
              outcome: "PASSED"
              testsRun: 12
              testsPassed: 12
              testsFailed: 0
            generation: null
            overallOutcome: "PASSED"
            reportLocation: "s3://aex-cmaai-orchestration-output/validations/3fa85f64-5717-4562-b3fc-2c963f66afa6/report.json"
  400, 401, 403, 404, 429, 500, 503: same error responses

4. NEW SCHEMAS (add to components/schemas)

ValidateRequest:
  type: object
  description: Request to submit a ground truth validation run.
  required:
    - validationType
  properties:
    validationType:
      type: string
      enum:
        - retrieval
        - generation
        - all
      description: |
        Specifies which ground truth validation tests to run.
        - "retrieval": For each pre-defined test key, checks if the correct SIS documents are retrieved 
          by comparing actual document IDs in the GenAI response against expected ground truth document IDs.
        - "generation": For each pre-defined test key, checks if the generated summary is similar enough 
          to the known-correct ground truth summary using similarity scoring.
        - "all": Runs both retrieval and generation validation.
    notificationMail:
      oneOf:
        - type: string
          format: email
          maxLength: 30
        - type: array
          items:
            type: string
            format: email
            maxLength: 30
          maxItems: 10
      description: Email(s) to notify when validation completes.

ValidateResponse:
  type: object
  description: Response confirming validation run was submitted.
  properties:
    validationId:
      type: string
      format: uuid
      description: ID of the validation run.
      example: "b8bc2535-5896-4638-9987-17540b417c69"
    status:
      $ref: "#/components/schemas/ValidationStatus"

ValidationStatusResponse:
  type: object
  description: Status and results of a validation run.
  properties:
    validationId:
      type: string
      format: uuid
      description: ID of the validation run.
      example: "b8bc2535-5896-4638-9987-17540b417c69"
    status:
      $ref: "#/components/schemas/ValidationStatus"
    result:
      $ref: "#/components/schemas/ValidationResult"
  required:
    - validationId
    - status

ValidationStatus:
  type: string
  description: |
    Status of a validation run.
    - PENDING: Validation request received, not yet started.
    - RUNNING: Validation tests are currently executing.
    - PASSED: All requested validation checks met quality thresholds.
    - FAILED: One or more validation checks did not meet quality thresholds.
    - ERROR: An unexpected error occurred during validation.
  enum:
    - PENDING
    - RUNNING
    - PASSED
    - FAILED
    - ERROR
  example: PENDING

ValidationResult:
  type: object
  description: Detailed results from a ground truth validation run.
  properties:
    retrieval:
      $ref: "#/components/schemas/RetrievalResult"
    generation:
      $ref: "#/components/schemas/GenerationResult"
    overallOutcome:
      type: string
      enum: [PASSED, FAILED, ERROR]
      description: PASSED only if all requested validation types passed.
    reportLocation:
      type: string
      description: S3 URI to the full detailed report with per-key results.
      example: "s3://aex-cmaai-orchestration-output/validations/b8bc2535-5896-4638-9987-17540b417c69/report.json"
  required:
    - overallOutcome

RetrievalResult:
  type: object
  description: Results from retrieval validation. Checks if correct documents were retrieved for each test key.
  properties:
    outcome:
      type: string
      enum: [PASSED, FAILED, ERROR]
    testsRun:
      type: integer
      description: Number of ground truth keys tested.
      example: 12
    testsPassed:
      type: integer
      description: Keys where retrieved documents matched expected.
      example: 11
    testsFailed:
      type: integer
      description: Keys where retrieved documents did NOT match expected.
      example: 1
  required: [outcome, testsRun, testsPassed, testsFailed]

GenerationResult:
  type: object
  description: Results from generation validation. Checks if generated summaries match ground truth.
  properties:
    outcome:
      type: string
      enum: [PASSED, FAILED, ERROR]
    testsRun:
      type: integer
      description: Number of ground truth keys tested.
      example: 12
    testsPassed:
      type: integer
      description: Keys where summary similarity met threshold.
      example: 10
    testsFailed:
      type: integer
      description: Keys where summary similarity was below threshold.
      example: 2
  required: [outcome, testsRun, testsPassed, testsFailed]

5. NEW PARAMETER (add to components/parameters)

ValidationId:
  name: validationId
  in: path
  required: true
  description: Validation run ID.
  schema:
    type: string
    format: uuid
  example: "1d81abbe-4f5a-4ef8-8d05-7bf89f66b9ad"

6. Bump version from 1.0.1 to 1.1.0

CRITICAL:
- Do NOT touch /orchestrations/instantiate
- Do NOT touch /orchestrations/{orchestrationId}/cancel
- Do NOT touch /orchestrations/{orchestrationId}/status
- Do NOT touch OrchestrationStatus enum
- Do NOT touch OrchestrationStatusResponse
- Do NOT touch InstantiateOrchestrationRequest
- Validation is its OWN world with its OWN schemas, statuses, and endpoints
