---
date: 2026-11-12
project: kaggle-name-that-llm
source: autonomous-goal
status: approved
approval_basis: active-goal-2026-11-06-gpu-autonomous-first-place-spec
execution_status: completed-rejected-both-ci-gates
tags: [spec, cpu, oof, qwen3-1.7b, spectral, complementarity]
---

# Qwen3-1.7B post-trained + frozen Spectral complementarity screen

## Motivation

The saved Qwen3-1.7B Open Pool v15 candidate improves over its low-pool SVC reference on both primary and shuffled confirmation OOF, but its complementarity to the stronger Spectral correction is unmeasured. Screen this distinct trained checkpoint once, using the same fixed addition as the completed Qwen3-8B/Spectral screen. Do not tune weight or transform from either split.

## Fixed inputs and method

- Use existing baseline probabilities/OOF from `artifacts/cpu-qwen-prompt-centered-svc-probability-ensemble-v1/{primary,confirmation}/`, Qwen3-1.7B logits/OOF from `artifacts/gpu04-qwen3-1-7b-openpool-v15/{primary,confirmation}/`, and saved frozen Spectral outputs.
- Align all sources by unique `id`; verify class order, fold assignment, prompt group, and label. Reproduce the saved fold-local Spectral-only predictions from the unchanged baseline probabilities before evaluating the candidate.
- Fixed formula in each fold: `(3 * baseline_probability + softmax(qwen_logits, temperature=1.0)) / 4`; then apply the unchanged text-only fold-local Spectral content grouping and mean-field transform. Clustering must not use prompt IDs, labels, folds, or predictions.
- Evaluate the existing prompt-grouped primary split and independent shuffled `GroupKFold(prompt_id, n_splits=5, shuffle=True, random_state=42)` confirmation split. Use 5,000 prompt-paired bootstrap replicates, seed 42, against Spectral-only. Report BA, paired delta/CI, fold scores, class recall, confusion matrix, and clustering diagnostics.

## Decision gates

- All source, ID, class, label, and fold checks pass, and baseline probabilities reproduce baseline OOF argmax predictions.
- The paired 95% CI lower bound for Qwen3-1.7B + Spectral minus Spectral-only must be strictly positive on both primary and confirmation. No tuning or alternate weights after seeing either split.
- If either gate fails, reject for Notebook use. Passing both permits a separate hidden-test feasibility review only; it does not itself authorize a Kaggle push or submission.

## Scope and safety

- CPU-only, one thread, saved OOF inputs only. Preserve source artifacts; no GPU/Kaggle jobs or Notebook/asset/submission changes.
- Before the run, use the active rate guard and verify source files using `sha256sum -c`. In date logs record “一致”, command, and 8-character hash prefixes only; never copy full hashes into responses.
- Save derived outputs to a new retry-safe `artifacts/cpu-qwen17b-spectral-complementarity-screen-v1[-retryN]/` directory and refuse overwrite.

## Reproduction

Runner: `scripts/evaluate_qwen17b_spectral_complementarity.py`; use the shared project Python environment from the implementation root.
