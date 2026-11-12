---
date: 2026-11-12
project: kaggle-name-that-llm
source: autonomous-goal
status: approved
approval_basis: active-goal-2026-11-06-gpu-autonomous-first-place-spec
execution_status: completed-rejected-both-ci-gates
tags: [spec, cpu, oof, 4view-svc, spectral, complementarity]
---

# 4-view SVC + frozen Spectral complementarity screen

## Motivation

The existing four-view TF-IDF SVC uses lexical, punctuation, shape, and function-word views. Its standalone OOF BA is below the current Spectral result, but it provides a distinct error source. Test once whether a fixed low-weight contribution improves frozen Spectral on both the primary and independent confirmation splits.

## Fixed inputs and method

- Use the saved baseline probability ensemble and OOF from `artifacts/cpu-qwen-prompt-centered-svc-probability-ensemble-v1/{primary,confirmation}/`.
- Use existing 4-view SVC decision scores and OOF from `artifacts/cpu-openpool-4view-svc-v15/{primary,confirmation}/`; read `scores`, `classes`, and `ids` from each fold's `decision-scores.npz`.
- Align unique IDs and class order; verify fold, prompt, label, and that softmax of saved decision scores reproduces saved SVC predictions. Reproduce the saved Spectral-only prediction from unchanged baseline probabilities.
- Fixed formula within each fold: `mixed_probability = (3 * baseline_probability + softmax(4view_decision_scores, T=1.0)) / 4`. Apply the unchanged text-only fold-local Spectral content grouping and mean-field transform. Clustering must not use prompt IDs, labels, folds, or predictions.
- Evaluate the saved primary prompt-grouped split and independent shuffled `GroupKFold(prompt_id, n_splits=5, shuffle=True, random_state=42)` confirmation split. Use 5,000 prompt-paired bootstrap replicates, seed 42, against Spectral-only. Report BA, paired delta/CI, fold scores, class recall, confusion matrix, and clustering diagnostics.

## Decision gates

- All source and alignment checks pass, baseline probabilities reproduce baseline argmax predictions, and candidate softmax reproduces saved candidate OOF predictions.
- The paired 95% CI lower bound for 4-view SVC + Spectral minus Spectral-only must be strictly positive on both primary and confirmation. No tuning or alternate weights after observing either split.
- If either gate fails, reject this candidate for Notebook use. Passing both permits a separate hidden-test feasibility review only; it does not by itself authorize a Kaggle push or submission.

## Scope and safety

- CPU-only, one thread, existing OOF inputs only. Preserve all source artifacts. No GPU/Kaggle jobs, Notebook, asset, or submission changes.
- Before the run, use the active utilization guard and verify source files using `sha256sum -c`. Date logs may include “一致”, the command, and 8-character hash prefixes only; never reproduce full hashes in responses.
- Save outputs under a new `artifacts/cpu-4view-svc-spectral-complementarity-screen-v1[-retryN]/` directory; refuse overwrite and preserve failed attempts.

## Reproduction

Runner: `scripts/evaluate_4view_svc_spectral_complementarity.py`; use the shared project Python environment from the implementation root.
