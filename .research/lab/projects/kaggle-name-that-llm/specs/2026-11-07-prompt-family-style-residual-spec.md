---
date: 2026-11-07
project: kaggle-name-that-llm
source: active-goal / public-sibling-stylometry-hypothesis
status: approved
execution_status: rejected-primary
tags: [spec, experiment, cpu, prompt-grouped, style, residual]
---

# Prompt-grouped family-local style residual

## Motivation

The adopted 0.10-weight prompt-centered SVC has complete primary and confirmation OOF. A recent public Notebook, `ozertuu/0-673-sibling-stylometry-forensic-apex`, describes adjusting only sibling-model probabilities while preserving each provider family's total score mass. Its score claim is not verified by the notebook source: metadata and search-index run dates conflict, and its attribution section explicitly says that a displayed 0.664 belongs to another notebook and the added model's score was not measured. Its large collection of neural checkpoints and prior shrinkage are outside this experiment. Use only the testable family-local residual idea, independently implemented and evaluated against the 0.10 SVC.

## Fixed method

- Use the adopted 0.10 prompt-centered SVC's saved primary and confirmation `decision-scores.npz` and matching OOF rows. Do not refit the SVC.
- For every outer fold, fit a separate multinomial logistic head per provider family (`claude`, `gemini`, `gpt`, `glm`) from deterministic handcrafted text-style features. Features include token/sentence/character lengths, type-token diversity, case/digit/Unicode/space ratios, punctuation rates, and fixed common-word rates. Feature extraction uses each row's response text only.
- Fit each head only on outer-training rows. Estimate its balanced accuracy with 5-fold `GroupKFold(prompt_id)` internal OOF on those rows. For a family with K classes, set reliability to `clip((inner_OOF_BA - 1/K) / 0.15, 0, 1)`.
- Fit a final family head on the full outer-training family rows. Within each family, convert baseline scores to conditional probabilities. Let `margin` be the top-1 minus top-2 conditional probability; use a fixed uncertainty gate `clip((0.65 - margin)/0.65, 0, 1)`. Blend with style-head probabilities at strength `0.10 * reliability * gate`.
- Reconstruct family scores so each row's family log-sum-exp is exactly preserved. Apply every family head to every validation row based only on response text and baseline scores. Never use validation labels to route rows or to decide whether an adjustment is applied. No cross-family adjustment, prompt-size assumption, hidden prompt ID, test label/count, or validation prompt information enters prediction. Prompt IDs are used only to make outer/inner splits and score bootstrap groups.
- Primary and confirmation use their independently saved outer fold assignments. Compare each full 2,699-row OOF against the same-split 0.10 SVC with 2,000 prompt-level paired bootstrap replicates, seed 42. Require primary CI lower >0 before confirmation; require confirmation CI lower >0 to adopt.
- All features, `C=0.03`, residual strength, margin gate, reliability transform, and family mapping are fixed before primary. No threshold/weight tuning after seeing primary.

## Scope and resources

- Implement a new CPU-only runner in `/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/src/`; save artifacts under `artifacts/cpu-prompt-family-style-residual-v1/`.
- Use two CPU threads, tree RSS <=32 GiB, host MemAvailable >=16 GiB. No GPU use, no Kaggle object or submission.
- Preserve current 0.10 SVC OOF, rejected 0.05 artifacts, and Qwen02/04 runs. Do not stop or modify either Qwen job.
- Validate complete and exactly aligned OOF rows, finite scores, all outer and inner heads converged, family mass conservation, and both paired-bootstrap gates.
- Authorized by the active first-place goal. This spec does not authorize submission.

## Retry and leakage correction

- The first run `artifacts/cpu-prompt-family-style-residual-v1/` had an OOF schema issue and is preserved.
- Retry1 `artifacts/cpu-prompt-family-style-residual-v1-retry1/` fixed the schema, but its family loop used held-out `true_model` to decide which validation rows received each family head. This is validation-label leakage. Its BA `0.506376` and paired CI are invalid and must not be used for selection or adoption.
- The runner now applies each family head to all validation rows using only the response text and baseline scores. The corrected run is in `artifacts/cpu-prompt-family-style-residual-v1-retry2/`. No result from the leaked run is considered a valid gate.

## Corrected primary result and decision (2026-11-07 13:08 JST)

- Complete 2,699-row, 150-prompt primary OOF; adjusted BA `0.509339`.
- Adopted 0.10 SVC primary BA `0.501934`; delta `+0.007405`.
- Prompt-paired bootstrap (2,000 replicates, seed 42): mean delta `+0.007472`, 95% CI `[-0.001481, +0.016664]`; primary gate failed.
- All outer and inner heads converged. Maximum family log-mass error remains at floating-point roundoff (`2.22e-16`).
- Decision: reject and skip confirmation. Retain the 0.10 SVC as OOF baseline. No Kaggle submission.
