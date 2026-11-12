---
date: 2026-11-12
project: kaggle-name-that-llm
type: experiment-result-audit
spec: ../specs/2026-11-07-openpool-family-mass-rerank-spec.md
status: rejected-primary-gate
tags: [cpu, open-pool, rerank, prompt-grouped]
---

# Family-mass rerank primary result recovery

This is a read-only recovery of the already completed `cpu-openpool-family-mass-rerank-v15-retry1` artifacts, not a new run. The primary fold worker completed all five folds with convergence recorded. The original non-retry artifact is terminal `worker_failed` on fold 0 because `decision_prob` called `len()` on a SciPy sparse matrix; it must not be resumed because retry1 contains the complete result.

## Preregistered primary result

- Candidate BA: `.434154`; flat 4-view SVC BA: `.433776`; delta `+.000378` across 2,699 rows and 150 prompt groups.
- Prompt-paired bootstrap: 2,000 replicates, seed 42, 95% CI `[-.007778, +.008534]`, mean delta `+.000336`; adoption is `uncertain` in the saved analysis manifest.
- The lower bound does not exceed zero, so the spec's primary gate fails. Do not run confirmation and do not adopt this reranker. The current Spectral blend remains the project best.
- Existing run recorded CPU affinity `[0,1]` and about 203.8 GiB host memory available at preflight. No GPU, Kaggle object, Notebook, or submission was involved.
- Source files and outputs remain in the external artifact directories. No artifact was altered. Provenance stays in the existing manifest; no full hash is copied into this Markdown.

## Decision

**Reject and close this candidate at the primary gate.** No parameter, family, or fold selection follows. Keep the adopted flat SVC and Spectral outputs unchanged.
