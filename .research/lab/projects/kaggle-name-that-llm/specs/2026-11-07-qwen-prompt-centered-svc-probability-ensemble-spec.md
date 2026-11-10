---
date: 2026-11-07
project: kaggle-name-that-llm
source: active-goal / adopted-low-pool-weight-prompt-centered-svc
status: approved
execution_status: primary-screen-passed-confirmation-running
tags: [spec, experiment, ensemble, gpu, prompt-grouped]
---

# Qwen + prompt-centered SVC probability ensemble

## Purpose

Evaluate whether the independently trained Qwen3-8B post-trained candidate02 and Qwen3-1.7B candidate04 add complementary signal to the newly adopted prompt-centered Open Pool SVC with pool row weight 0.10. This SVC passed both preregistered primary and independent confirmation paired-bootstrap gates against the prior 0.35-weight prompt-centered SVC. Neither method has yet been validated on Kaggle LB.

The fold0 equal-probability mean that motivated the earlier flat-SVC ensemble was selected on fold0. This follow-up uses the same un-tuned formula with the adopted prompt-centered SVC; primary is screening only and confirmation is the independent adoption gate.

## Fixed method

- Inputs: completed OOF logits from candidate02 and candidate04, and OOF `decision-scores.npz` from `cpu-openpool-prompt-centered-low-pool-weight-v15`. No model is refit for ensembling.
- For each row, align all three components by `id`; require identical true label, `prompt_id`, and fold; require exactly 2,699 unique training IDs and the same fixed 18-class column order; reject missing, duplicate, or nonfinite outputs.
- Convert each base score vector to a row-wise softmax at temperature 1.0 and average equally:
  `p = mean(softmax(qwen8_logits), softmax(qwen1.7_logits), softmax(prompt_centered_svc_margins))`.
- Predict by argmax. Do not fit calibration, weights, thresholds, prompt constraints, class-count corrections, or hyperparameters.
- Run the primary split only after both Qwen primary OOFs contain all five folds. Compare against prompt-centered SVC with a 2,000-replicate prompt-level paired bootstrap, seed 42; also report paired comparisons against each Qwen base.
- Since fold0 informed selection of the original three-model mean, treat primary as screening. If the primary CI lower bound versus prompt-centered SVC is above zero, run the same formula on the independent confirmation split. Adopt the ensemble only if confirmation CI lower bound is also above zero.

## Leakage and Kaggle constraints

- Fold membership remains the saved prompt GroupKFold. Validation `prompt_id` may group bootstrap rows only; it is not passed into prediction.
- Do not use test labels/counts, assume 18 rows per hidden prompt, or apply injective assignment.
- No Kaggle submission or public object is created by this experiment. A passing OOF gate still requires Notebook, license/provenance, Kaggle runtime, privacy, and final-selection checks before any submission.
- Preserve current GPU jobs, their checkpoints, existing flat-SVC analysis, and prompt-centered SVC artifacts.

## Implementation and validation

- Evaluator: `/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/src/gpu_probability_ensemble.py`.
- Change scope: allow a candidate ID to be supplied for the ensemble manifest; use the existing alignment, finite-score, full-OOF and bootstrap checks. Do not change model training or the original flat-SVC ensemble artifacts.
- Output: `artifacts/cpu-qwen-prompt-centered-svc-probability-ensemble-v1/` (ignored/private). Pass `--svc-dir artifacts/cpu-openpool-prompt-centered-low-pool-weight-v15` for both splits; this candidate contains the independently validated primary and confirmation OOFs.
- Candidate identity: `cpu-openpool-prompt-centered-low-pool-weight-v15` (set `--candidate-id` accordingly).
- Verification: five-fold complete OOF manifests, exact ID/label/prompt/fold/class alignment for all inputs, full-row ensemble artifact, 2,000 paired-bootstrap reps per comparator, memory guard <=32 GiB tree RSS and >=16 GiB MemAvailable.
- This analysis is authorized by the active first-place goal. Do not submit to Kaggle from this spec alone.
