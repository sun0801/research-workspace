---
date: 2026-11-12
project: kaggle-name-that-llm
source: autonomous-goal
status: approved
approval_basis: active-goal-2026-11-06-gpu-autonomous-first-place-spec
execution_status: completed-rejected-both-ci-gates
tags: [spec, cpu, oof, prompt-centered-twin, spectral, complementarity]
---

# Prompt-centered Twin SVC + frozen Spectral complementarity screen

## Motivation

The prompt-centered Twin SVC has complete primary and independent confirmation OOF with prompt-paired gains over the older flat SVC reference. Its value as an addition to the current Qwen/SVC baseline plus stronger Spectral correction has not been evaluated. Test this distinct, pre-existing score source once with the same fixed 1/4 addition used by the approved model-complementarity screens.

## Fixed inputs and method

- Use saved baseline probabilities/OOF from `artifacts/cpu-qwen-prompt-centered-svc-probability-ensemble-v1/{primary,confirmation}/`.
- Use Twin SVC primary scores from `artifacts/cpu-openpool-prompt-centered-twin-v15-retry1/primary/` and confirmation scores from `artifacts/cpu-openpool-prompt-centered-twin-v15-retry2/confirmation/`.
- Use existing frozen Spectral outputs for both splits. Align unique IDs and class order; verify fold, prompt, labels, and that softmax of Twin decision scores reproduces saved Twin OOF predictions. Reproduce Spectral-only predictions from unchanged baseline probabilities.
- Fixed formula within each fold: `(3 * baseline_probability + softmax(twin_decision_scores, T=1.0)) / 4`; then apply the unchanged text-only fold-local Spectral content grouping and mean-field transform. Clustering must not use prompt IDs, labels, folds, or predictions.
- Evaluate saved primary and independent shuffled `GroupKFold(prompt_id, n_splits=5, shuffle=True, random_state=42)` confirmation. Use 5,000 prompt-paired bootstrap replicates, seed 42, against Spectral-only. Report BA, paired delta/CI, fold scores, class recall, confusion matrix, and clustering diagnostics.

## Decision gates

- All source and alignment checks pass; baseline and Twin score argmax predictions reproduce their OOF outputs.
- The paired 95% CI lower bound for Twin + Spectral minus Spectral-only must be strictly positive on both primary and confirmation. No tuning or alternate weights after observing either split.
- If either gate fails, reject for Notebook use. Passing both permits only a separate hidden-test feasibility review; it does not itself authorize a Kaggle push or submission.

## Scope and safety

- CPU-only, one thread, existing OOF inputs only. Preserve all source artifacts. No GPU/Kaggle jobs or Notebook/asset/submission changes.
- Before the run, use the active utilization guard and verify source files with `sha256sum -c`. Record “一致”, the command, and 8-character hash prefixes only; never reproduce full hashes in responses.
- Save outputs under a new `artifacts/cpu-twin-spectral-complementarity-screen-v1[-retryN]/` directory; refuse overwrite and preserve failed attempts.

## Reproduction

Runner: `scripts/evaluate_prompt_centered_twin_spectral_complementarity.py`; use the shared project Python environment from the implementation root.
