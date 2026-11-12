---
date: 2026-11-12
project: kaggle-name-that-llm
type: public-discussion-audit
decision: (b) 試さない
tags: [audit, validation, discussion]
---

# “From 0.684 toward top 1%: what validation evidence predicts real gains?”

**判定: (b) 試さない。** The post shares useful evaluation cautions but no new reproducible model or correction to run. Its reported residual improvements had paired intervals crossing zero and sparse-prompt regression; the author explicitly says the complete ensemble lacks full-OOF evidence and the numbers are not a new holdout result.

- [Discussion 758301](https://www.kaggle.com/competitions/name-that-llm/discussion/758301), posted 2026-11-12. Author-reported `.684` is attributed to an existing public reproduction. The post's displayed rank/score snapshot is not the current official leader check.
- The useful recommendation—verify that post-processing runs through the full hidden rerun rather than a small preview—was already reflected in our v12 runtime gate and scored submission, which was pending at audit time. The 15:51 JST follow-up confirmed ref `58261829` as `COMPLETE` with Public `.541`; see the [benchmark log](2026-11-12-baseline-benchmark-push.md). No separate experiment is justified by this discussion.
- The older “What score your best single model can achieve?” thread has scattered self-reports (including `.657` for a single Qwen3-14B) without enough fold, training-data, or source detail to exceed the present `.689791` primary-only Mistral+Spectral result. Do not adopt those numbers as comparable OOF results.
