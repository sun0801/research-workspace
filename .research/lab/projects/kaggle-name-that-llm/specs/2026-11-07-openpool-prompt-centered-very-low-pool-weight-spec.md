---
date: 2026-11-07
project: kaggle-name-that-llm
source: active-goal / adopted-pool-weight-0.10-svc
status: approved
execution_status: rejected-primary
tags: [spec, experiment, cpu, prompt-grouped, svc, sample-weight]
---

# Prompt-centered SVC with 0.05 Open Pool weight

## Motivation

The preregistered 0.10 pool-weight candidate passed primary and independent confirmation against the 0.35 candidate (primary prompt-paired 95% CI `[+0.024822, +0.046694]`; confirmation CI `[+0.020325, +0.041482]`). Test a further reduction to 0.05 to check whether the public-pool contribution is still too dominant. This is a new fixed candidate and will be compared only with the adopted 0.10 SVC.

## Fixed method

- Use the adopted prompt-centered SVC runner, four feature views, prompt-centering/group inference, exact-text and held-prompt pool filtering, 2,500 pool rows per label, official row weight 1.0, and unchanged saved fold assignments.
- Change only `external_data.row_sample_weight` from 0.10 to 0.05. Keep C, features, clustering, sample selection, thresholds, and all other settings fixed.
- Config: `/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/configs/cpu-openpool-prompt-centered-low-pool-weight-v05-v15.json`.
- Artifact directory: `artifacts/cpu-openpool-prompt-centered-low-pool-weight-v05-v15/`.
- Compare the complete primary OOF to the adopted 0.10 candidate primary OOF using 2,000 prompt-level paired bootstrap replicates, seed 42. Run independent confirmation only if the primary CI lower bound exceeds zero.
- Adopt this candidate as the next OOF comparison baseline only if the same-split confirmation comparison to the 0.10 SVC has CI lower bound above zero. Otherwise retain 0.10.

## Scope and resources

- CPU only, 2 threads, tree RSS <=32 GiB, host MemAvailable >=16 GiB. Do not use the GPUs or submit to Kaggle.
- Preserve all existing SVC and Qwen artifacts. Do not stop or change Qwen02/04.
- Validation: complete 2,699-row OOF per split, exact ID/prompt/fold/label alignment to the adopted 0.10 SVC, finite score matrix/class order, valid fold manifests/hashes, and both paired-bootstrap gates.
- Authorized by the active first-place goal. No submission is authorized by this spec alone.

## Primary result and decision (2026-11-07 12:47 JST)

- Complete 2,699-row, 150-prompt primary OOF; overall BA `0.506366`.
- Adopted 0.10 SVC primary BA `0.501934`; delta `+0.004432`.
- Prompt-paired bootstrap (2,000 replicates, seed 42): mean delta `+0.004535`, 95% CI `[-0.004460, +0.012970]`; primary gate failed because its lower bound does not exceed zero.
- All five folds converged; per-fold `n_iter` 34/34/35/33/34. Fold-level candidate BA: 0.498148, 0.492593, 0.505556, 0.518519, 0.516986.
- Decision: reject this candidate and do not run confirmation. Retain the 0.10 SVC as the OOF comparison baseline. No Kaggle submission.
