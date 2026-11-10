---
date: 2026-11-09
project: kaggle-name-that-llm
type: source-review
status: reviewed
tags: [public-notebook, svm, ensemble, provenance]
---

# Duong Dual-SVC Apex Notebook audit

## Source and verification

- [Notebook](https://www.kaggle.com/code/duongynhi/name-that-llm-dual-svc-apex), author Duong Y Nhi; official Kaggle MCP lookup on 2026-11-09 around 10:22 JST.
- Notebook search (`DateRun`) listed a run at 2026-11-09 01:01:54 UTC. Notebook metadata is version 3 but reports `last_run_time` 2026-11-06 01:23 UTC; embedded Papermill metadata says 2026-10-27 18:05 UTC. The timestamps disagree, so the Nov 9 run cannot be tied to the inspected source version from these responses.
- Session status is `COMPLETE`; listed output files include `submission.parquet`, model weights, `open_pool.parquet`, `extra_matched.parquet`, and pairwise probability/audit artifacts. The session log supplied no non-empty stdout/stderr and no score.
- Viewed Notebook markdown and selected code paths via official MCP. It describes a T4 x2 blend of Dual-SVC stylometry, multi-LoRA models, sibling-style residuals, and Sinkhorn, and gives a historical A/B table up to `0.672`; the title says `0.675+`. These are author claims and do not approach the current public `0.752` top.

## Validation and provenance limits

Metadata lists 19 dataset sources, 8 Notebook sources, and 8 model sources. The source includes a five-fold `GroupKFold` inside a sibling-style residual component, but this inspection did not verify a complete prompt-grouped OOF result for the submitted full stack or connect an OOF score to the claimed LB score. The many external inputs' licenses, prompt overlap controls, and exact scored version remain unverified.

## Decision

Treat this as a static method lead only. Do not reuse its external weights/outputs or add it to the GPU queue. It has no verified result above the public leader and insufficient provenance for a reproducible candidate. Keep the registered candidate order unchanged. No Kaggle object was created or edited and no submission was made by us.
