Hi Kevin,

Quick update on the validation work.

I went with the separate endpoint approach as you and Luba discussed. Created a new POST /orchestrations/validate endpoint that takes a validationType parameter (retrieval, generation, or all). Same async pattern as instantiate, returns orchestrationId, caller polls status to get results.

The status response includes a validationResult showing pass/fail for retrieval and generation separately, test counts, and a report location. Added VALIDATING and VALIDATION_FAILED statuses. The actual validation logic is a placeholder for now, ready for the real implementation once ground truth data and scoring approach are finalized.

All existing functionality untouched. 143+ tests pass. Draft PR is up for Luba to review.

A couple things when you get a chance:
1. Does retrieval/generation/all as the validation options match what you had in mind?
2. Where should the ground truth data live (S3, config, etc.)?
3. On the document ID matching issue you mentioned with SIS, will we have a clean mapping by the time we implement?

Thanks,
Sowndarya
