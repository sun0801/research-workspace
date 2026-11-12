---
date: 2026-11-12
project: kaggle-name-that-llm
status: approved-under-active-goal
approval_basis: 2026-11-06-gpu-autonomous-first-place-spec
execution_status: rejected-primary-screen
tags: [spec, punctuation, spectral, prompt-grouped, cpu]
---

# Spectral punctuation support prior screen

## Purpose and source

Test one fixed, fold-local punctuation support prior on the current best Spectral mean-field OOF. The hypothesis comes from Kirill Tymchishin's public [LoRA + Trained27 | Evidence for Close Calls](https://www.kaggle.com/code/kirilltym/lora-trained27-evidence-for-close-calls), current version 19 (metadata last run Nov 9; search run time differs). Its README reports V17 public BA`.684`, V18`.683`, current punctuation version pending, and four prompt-held-out checks on older cached predictions adding 4–10 correct of 2,159 rows. These are author reports, not our measurements; the full multi-source ensemble is not a candidate here.

## Fixed method

- Official `train.csv` only. For each saved validation fold, derive counts from that fold's training rows and labels only. No external data, test labels, or validation labels enter support counts.
- Four fixed query markers: literal `" — "`, literal `"—"`, both curly double quotes `“` and `”`, and curly apostrophe `’`.
- A marker is active for a fold only if it occurs in at least 20 training rows overall. A class is eligible for a marker penalty only if it has at least 80 training rows and zero examples containing that active marker.
- For each query/class, subtract `0.70` from the Spectral model's log probability once if the query has any active marker unsupported by that class. This is the only candidate transform; no threshold, marker, score, or weight search.
- Recompute the current Spectral mean-field probabilities from the registered per-fold Qwen blend probabilities and fold text clusters, then apply this prior after mean-field calibration, matching the public source's order. Preserve baseline and candidate outputs separately.

## Evaluation and gates

- Primary split: exact saved primary GroupKFold from `artifacts/2026-11-06-cpu-cycle/folds.parquet`; baseline: `cpu-spectral-cluster-meanfield-v1` reconstructed from its existing per-fold Qwen probabilities and source procedure.
- Main metric: all-row balanced accuracy. Report fold BA, per-class recall and changed predictions. Compare candidate minus baseline with at least 5,000 prompt-paired bootstrap draws, seed 42.
- If the primary 95% CI lower bound is above zero, repeat the unchanged formula on the registered independent confirmation split (`cpu-openpool-prompt-centered-low-pool-weight-v15/confirmation-folds.parquet`) using the confirmation-specific baseline probabilities and Spectral transform. Confirmation uses the same gate. Otherwise reject and do not tune.
- CPU only, one BLAS/OpenMP thread, no GPU allocation. Write all outputs to `artifacts/cpu-spectral-punctuation-prior-screen-v1/`; never overwrite existing probabilities, predictions, or summaries. No Kaggle push or submission is part of this screen.


## Execution result (2026-11-12)

Primary screen completed: baseline/candidate BA `0.664952`, delta `0`, prompt-paired 95% CI `[0, 0]`, and zero changed predictions. The pre-registered gate rejects the candidate; confirmation and tuning were not run. See [result log](../experiments/2026-11-12-spectral-punctuation-prior-screen.md).
