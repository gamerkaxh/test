Hi Kevin,

Wanted to give you an update on where things stand with the validation work.

Based on your latest thinking and Luba's suggestion, I went with the separate dedicated endpoint approach. Here's what I've done:

I created a new POST /orchestrations/validate endpoint that accepts a validationType parameter. The caller can pass "retrieval" to only check if the correct documents are being retrieved, "generation" to only check if the summaries match ground truth, or "all" to run both checks. It follows the same async pattern as the existing instantiate endpoint, returns a 202 with an orchestrationId, and the caller polls status to get the results.

The status response now includes a validationResult object when it's a validation run. This shows the outcome for retrieval and generation separately (how many of the test keys passed and failed), an overall pass/fail, and a link to where the full detailed report would live in S3.

I added VALIDATING and VALIDATION_FAILED as new orchestration statuses. VALIDATING means the tests are in progress. VALIDATION_FAILED means the quality bar wasn't met.

On the code side, I updated the request handler to accept and validate the new endpoint, added the conditional branch in the executor to run validation when it's that type of orchestration, and created a placeholder validation function that's ready for the real logic once we have the ground truth data stored and the similarity scoring approach decided.

The validation function itself is a placeholder right now. It returns PASSED with zero tests. But the structure is all there so that when we're ready to plug in the real GenAI calls and document comparison, it's just that one module that changes and nothing else needs to be restructured.

All existing functionality is untouched. The instantiate endpoint works exactly as before. All 143 unit tests pass plus the new ones I added for the validation paths.

I've updated the spec in P-Apigee-APIResources and created a draft PR for Luba to review. Also have the code changes ready in my branch on the orchestration repo.

Luba asked about expected test execution time. Since it's a placeholder right now it returns instantly. Once the real implementation is in with about 10-12 test keys, each needing a GenAI call plus scoring, I'd estimate roughly 5 to 15 minutes for a full validation run depending on model latency. But we can nail that down once the pieces are in place.

A few things I'd like to confirm with you when you get a chance:

1. Does the separate endpoint approach with validationType as retrieval/generation/all match what you had in mind?

2. For the retrieval check, you mentioned the document IDs from our search might not match exactly with what the CMAs provided due to how SIS stores documents. Is that something we need to account for in the comparison logic, or will we have a clean mapping by the time we implement it?

3. Where will the ground truth data live? Is there a specific S3 bucket or config file where the test keys, expected documents, and ground truth summaries should be stored?

No rush on these. Happy to walk through the changes whenever works for you.

Thanks,
Sowndarya
