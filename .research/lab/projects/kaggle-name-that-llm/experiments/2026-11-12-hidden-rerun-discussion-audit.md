---
date: 2026-11-12
project: kaggle-name-that-llm
type: public-discussion-audit
decision: (b) 試さない
tags: [audit, kaggle-rerun, notebook]
---

# “Late post-processing cell never seems to affect the score in the hidden rerun”

**判定: (b) 試さない。** The post reports one participant's unobserved fallback during hidden scoring; a commenter speculates about `KAGGLE_IS_COMPETITION_RERUN`, but provides no verified Kaggle behavior or reproducible fix.

- [Discussion 758021](https://www.kaggle.com/competitions/name-that-llm/discussion/758021), opened 2026-11-11; one comment was available in the read.
- Read-only source inspection of our v9, v10, v11, and v12 notebooks found no `KAGGLE_IS_COMPETITION_RERUN` conditional. Therefore this suggestion does not explain our refs by itself.
- Our v9 source reads `sample_submission.parquet`; v10/v11 retain that dependency; v12 removes it and resolves `test.csv` from the competition input path. The v12 scored result was pending at audit time. The 15:51 JST follow-up confirmed ref `58261829` as `COMPLETE` with Public `.541`; see the [benchmark log](2026-11-12-baseline-benchmark-push.md). This supports the input-file assumption as an explanation, but does not establish the root cause without a hidden traceback.
- Kaggle exposes only the generic hidden-rerun error for refs `58251076`/`58253257`; public Notebook logs do not contain the hidden scoring trace. No submission configuration was changed based on this discussion.
