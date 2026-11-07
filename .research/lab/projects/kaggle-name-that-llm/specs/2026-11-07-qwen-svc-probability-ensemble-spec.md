---
date: 2026-11-07
project: kaggle-name-that-llm
source: active-goal / exploratory-fold0-error-analysis
status: approved
execution_status: superseded-by-2026-11-07-qwen-prompt-centered-svc-probability-ensemble-spec
tags: [spec, experiment, ensemble, gpu, kaggle]
---

# Qwen + Open Pool SVC probability ensemble

## Motivation and exploratory evidence

The active autonomous first-place goal authorizes selecting and evaluating another candidate. On 2026-11-07, exploratory analysis aligned the already-completed primary fold 0 predictions for Qwen3-8B post-trained candidate02, Qwen3-1.7B candidate04, and adopted Open Pool v15 flat SVC by all 540 `id`, true labels, and fold assignments.

- Fold0 BA: candidate02 `.544444`, candidate04 `.518519`, flat SVC `.431481`.
- An untuned, equal arithmetic mean of each model's per-row softmax probabilities (temperature 1.0) scored `.564815` for all three models. Pairwise equal-probability candidate02 + SVC scored `.550000`; candidate04 + SVC scored `.524074`.
- This is a single-fold exploratory result used to select the hypothesis. It is not an unbiased estimate and cannot establish adoption. Fold0 error overlap candidate02/SVC was 184 rows, with 123 SVC-only errors and 62 candidate02-only errors, indicating potential complementarity.

## Fixed method

- Inputs are OOF outputs only: `logits.npy` from candidates02 and04 and `decision-scores.npz` from the adopted flat SVC. No model is refit for the fusion step.
- For every row, align IDs and class columns explicitly. Require exactly one prediction per official `id`, all 18 labels in the fixed sorted order, identical true label/prompt/fold metadata, finite scores, and complete 2,699-row coverage.
- Convert each base model's 18 scores independently to probabilities using row-wise softmax at fixed temperature 1.0. Candidate02 logits, candidate04 logits, and SVC decision margins are used without extra calibration.
- Predict from `p = (p_qwen8 + p_qwen1.7 + p_svc) / 3`. No weights, thresholds, test-set counts, or label-frequency adjustment are tuned.
- Use both existing prompt-grouped splits: the saved primary GroupKFold and the fixed shuffled confirmation GroupKFold. Validation prompt IDs may be used only to group evaluation/bootstrap rows; they are never model inputs or prediction-time grouping constraints.

## Evaluation and decision

- Primary OOF evaluation may proceed once both Qwen candidates have complete primary OOF. Report overall/fold BA, per-class recall, confusion matrix, prompt-level paired bootstrap versus the adopted SVC (2,000 replicates, seed 42), and comparisons versus each individual Qwen base model.
- Because fold0 informed this candidate's selection, treat primary results as screening only and disclose the selection. If the primary paired 95% CI lower bound versus adopted SVC is above zero, run the same fixed fusion on the independent confirmation split. Adoption requires the confirmation paired CI lower bound also above zero. Do not tune using either validation set.
- If primary does not pass its gate, reject and retain flat SVC; do not run confirmation. If confirmation fails, reject. No Kaggle submission unless the parent's final-fit, runtime, Notebook, privacy, and two-final-selection rules also pass.

## Resources and artifacts

- Fusion and bootstrap are CPU-only, maximum two threads, process-tree RSS <=32 GiB and MemAvailable >=16 GiB. They must not stop, restart, or modify the live GPU base runs.
- Save analysis to a new, private/ignored artifact directory. Preserve all base OOFs, logits, SVC scores, and existing CPU baselines.
- CPU analyzer is implemented at `/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/src/gpu_probability_ensemble.py` (SHA-256 `7e2caa5bcff16b4c97e705917dd14fe7e68ca0ffabb28631cfff1e6b9eeaa9ee`). It verifies the canonical fold assignment, 2,699 unique IDs, matching labels/prompts/folds/class order, score shapes, and per-base paired bootstrap, then delegates the SVC comparison report to `gpu_analyze.py`. It passed `py_compile`; no experiment run was started because both Qwen primary OOFs still contain only fold0.
- Once all five primary folds exist, run: `.venv/bin/python src/gpu_probability_ensemble.py --split primary --run-dir artifacts/cpu-qwen-svc-probability-ensemble-v1`. The default run directory is ignored/private. Run confirmation only if the primary paired-CI gate passes.
- Do not use hidden test labels, test class counts, or assumptions of 18 rows per prompt. Do not publish Kaggle objects for this candidate.

## Status update (2026-11-07)

The prompt-centered SVC has since passed its primary and independent confirmation gates against this flat SVC. Keep the original flat-SVC evaluator and exploratory artifacts intact, but use [the follow-up spec](2026-11-07-qwen-prompt-centered-svc-probability-ensemble-spec.md) for the next ensemble evaluation.
