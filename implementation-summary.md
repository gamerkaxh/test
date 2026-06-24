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

Specifically we did the following:

1. Updated the API contract so that the service now accepts a new retrievalEvaluation parameter. This tells the service whether to run validation or not. We also defined what the validation results look like in the response so that anyone polling for status can see whether validation passed or failed, how many tests ran, and where to find the detailed report.

2. Added two new statuses that the orchestration can be in. VALIDATING means the validation tests are currently running. VALIDATION_FAILED means the tests did not pass the quality bar and summary generation was stopped to avoid wasting resources.

3. Created a data model that represents a validation result. This gives us a consistent structure for passing validation information around the system rather than relying on loose dictionaries that could have typos or missing fields.

4. Created a placeholder validation function. This is where the real Context Relevancy model calls will eventually live. Right now it just returns a passing result with zero tests run. When the data science team delivers the model, we update this one piece and everything else stays the same.

5. Updated the main orchestration logic to check the retrievalEvaluation flag. If it's true, the service enters validation mode first. If validation passes it continues with generating summaries. If validation fails it stops immediately without generating anything. If the flag is false or not provided, everything works exactly as it did before.

6. Updated the entry point that receives API requests so it can accept, validate, and forward the new parameter. It also now allows requests without keys when validation is the only thing being requested.

7. Updated the status response so that when someone checks how their orchestration is going, they can see the validation results alongside the usual progress information.

8. Added tests covering all the new paths plus verified that all existing functionality still works. 143 tests pass.


How the flow works

Normal flow (unchanged):
Someone sends a list of fault codes. The service generates AI summaries for each one. Status goes from pending to processing to succeeded. Nothing about this changed.

Validation with fault codes:
Someone sends fault codes and sets retrievalEvaluation to true. The service first runs the validation tests. If they pass, it proceeds with generating summaries as normal. If they fail, it stops and reports the failure. No summaries are generated, no money is wasted.

Validation only:
Someone sets retrievalEvaluation to true but doesn't send any fault codes. The service just runs the validation tests and reports the results. This is useful for the data science team to check quality without triggering a full batch.


What's left to do (not this story)

- Integrate the actual Context Relevancy model when the data science team delivers it
- Load real ground-truth test data
- Implement threshold comparison logic
- Generate detailed validation reports and store them
- Possibly add a second model for summary quality evaluation

These are future stories. This story was about building the structure and making the service ready to receive the real validation logic when it comes.


Testing status

What passed:
- 143 unit tests (all existing plus new ones for the validation paths)
- API spec validation (no errors)
- Local testing of the request handling (correctly accepts valid requests, rejects invalid ones)

What still needs testing and requires deployment to the DEV environment:
- End-to-end API calls against real infrastructure
- Status transitions in the actual database
- Full request-to-status-poll cycle

Waiting on Kevin for DEV deployment guidance and on Luba for a code walkthrough.
