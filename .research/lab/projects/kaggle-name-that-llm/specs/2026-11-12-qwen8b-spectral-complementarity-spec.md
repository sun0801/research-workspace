---
date: 2026-11-12
project: kaggle-name-that-llm
source: autonomous-goal
status: approved
approval_basis: active-goal-2026-11-06-gpu-autonomous-first-place-spec
execution_status: completed-rejected-both-ci-gates
tags: [spec, cpu, oof, qwen3-8b, spectral, complementarity]
---

# Qwen3-8B post-trained + frozen Spectral complementarity screen

## Motivation

The saved `gpu02-qwen3-8b-posttrained-openpool-v15` OOF candidate improves over the low-pool SVC baseline on both the primary and shuffled confirmation splits. The current best Spectral correction is stronger, so this screen asks only whether a fixed, low-weight Qwen addition complements it. The positive primary-only Mistral + Spectral screen motivates reusing its fixed 1/4 probability weight; no weight search is allowed.

## Fixed inputs and method

- Use the existing baseline probabilities and OOF rows from `artifacts/cpu-qwen-prompt-centered-svc-probability-ensemble-v1/{primary,confirmation}/`.
- Use the existing foldwise logits and OOF rows from `artifacts/gpu02-qwen3-8b-posttrained-openpool-v15/{primary,confirmation}/`.
- Use official train text/labels only for scoring and text-only clustering. Align by unique `id`; verify class order, fold assignment, prompt group, and true label consistency across all sources. Do not refit a model or modify source artifacts.
- For each split and each of its five folds, fixed addition: `mixed_probability = (3 * baseline_probability + softmax(qwen_logits, temperature=1.0)) / 4`.
- Apply the unchanged local Spectral content grouping and mean-field transform separately to each fold's held-out probabilities and texts. Do not use prompt IDs, labels, or predictions in clustering. Reproduce the saved foldwise Spectral-only predictions from unchanged baseline probabilities before evaluating the mix.
- Evaluate both the saved primary prompt-grouped split and independent shuffled `GroupKFold(prompt_id, n_splits=5, shuffle=True, random_state=42)` confirmation split. Use 5,000 prompt-paired bootstrap replicates with seed 42 against the unchanged Spectral-only output. Report BA, paired delta/CI, folds, class recall, confusion matrix, and clustering diagnostics.

## Decision gates

- Source and row alignment checks must pass, and baseline probabilities must reproduce their saved OOF argmax predictions.
- The Qwen + Spectral paired 95% CI lower bound must be strictly positive on **both** primary and confirmation splits. No tuning or alternate weights after observing either result.
- Failure of either gate rejects the candidate for Notebook use. Passing both permits only a separate hidden-test feasibility review; it does not authorize a Kaggle push or submission by itself.

## Scope and safety

- CPU-only, one thread, existing OOF data only. Do not start or interfere with GPU/Kaggle jobs. Preserve all CPU source outputs.
- Before the run, check the active utilization guard and verify source files with `sha256sum -c`. Record only “一致”, the command, and each input hash's first eight characters in the dated experiment log; never copy full hashes into reports.
- Write derived outputs only under `artifacts/cpu-qwen8b-spectral-complementarity-screen-v1[-retryN]/`; each attempt refuses to overwrite an existing output directory. Keep failed attempt directories as evidence.
- Do not create or change a Notebook, Kaggle asset, or submission in this screen.

## Reproduction

Implementation: `scripts/evaluate_qwen8b_spectral_complementarity.py`; the successful run is under `artifacts/cpu-qwen8b-spectral-complementarity-screen-v1-retry2/`. The first attempt and retry1 stopped at OOF column-alignment checks before scoring and remain preserved.

Run from `/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm` with the shared project Python environment and single-thread CPU limits. Save a source manifest, fixed formula, predictions, metrics, diagnostics, runtime, and exact command in the derived output directory.
