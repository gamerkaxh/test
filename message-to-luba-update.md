Hi Luba,

Quick update. I went ahead with the separate endpoint approach you suggested. Created a new POST /orchestrations/validate with a validationType parameter (retrieval, generation, or all). Same async pattern as instantiate. Added VALIDATING and VALIDATION_FAILED statuses, and a validationResult in the status response.

The validation logic is a placeholder for now, returns PASSED with zero tests. All 143+ existing tests pass plus the new ones I added for the validation paths. Draft PR is up for you to review.

On your question about test execution time, right now it returns instantly since it's a placeholder. Once we plug in the real GenAI calls for the 10-12 ground truth keys, I'd estimate 5 to 15 minutes depending on model latency. Do you think we need to handle a timeout or set a ceiling for the validation step?

Let me know if anything looks off in the PR or if you'd like me to adjust anything.

Thanks,
Sowndarya
