---
date: 2026-11-07
project: kaggle-name-that-llm
source: active-goal / adopted-prompt-centered-svc
status: approved
execution_status: adopted
tags: [spec, experiment, cpu, prompt-grouped, svc, sample-weight]
---

# Prompt-centered SVC with lower Open Pool weight

## Motivation

The adopted prompt-centered SVC uses official rows at weight 1.0 and the balanced Open Pool rows at weight 0.35. Per class, this is roughly 875 weighted pool rows against about 120 official rows, so the public pool contributes about seven times the official-row weight. A fixed 0.10 pool weight reduces that ratio to about 250:120 while preserving all data selection and class balance. This tests whether a stronger emphasis on official competition text improves unseen-prompt generalization.

## Fixed method

- Use the adopted prompt-centered SVC runner, four feature views, prompt-centering/group inference, exact-text and held-prompt pool filtering, 2,500 pool rows per label, official row weight 1.0, and all saved fold assignments unchanged.
- Change only `external_data.row_sample_weight` from 0.35 to 0.10. Do not adjust C, features, clustering, sample selection, thresholds, or other settings.
- Compare all primary OOF rows to the adopted prompt-centered SVC with 2,000 prompt-level paired bootstrap replicates, seed 42. Primary CI lower bound must exceed zero before confirmation.
- If primary passes, run the exact same config on the independent confirmation split and require its paired CI lower bound versus the same-split adopted prompt-centered SVC to exceed zero. Otherwise reject without confirmation.
- Record per-fold convergence, pool counts, validation grouping, outputs, manifests, and resource readings.

## Scope and resources

- Config: `/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/configs/cpu-openpool-prompt-centered-low-pool-weight-v15.json`.
- Runner: existing `/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/src/cpu_openpool_prompt_centered_twin.py`; no runner changes.
- Artifact directory: `artifacts/cpu-openpool-prompt-centered-low-pool-weight-v15/`; preserve the existing adopted candidate and Qwen runs.
- CPU only, 2 threads, tree RSS <=32 GiB, host MemAvailable >=16 GiB. No GPU use or Kaggle submission.
- Validation: complete 2,699-row OOF, exact ID/prompt/fold/label alignment to the adopted SVC, finite score matrix/class order, all fold manifests/hashes valid, and paired-bootstrap gates above.
- Authorized by the active first-place goal. No submission is authorized by this spec alone.

## Primary result (2026-11-07 11:20 JST)

- Complete 2,699-row, 150-prompt primary OOF; overall BA `0.501934`.
- Same-split adopted prompt-centered SVC BA `0.465993`; delta `+0.035941`.
- Prompt-paired bootstrap (2,000 replicates, seed 42): mean delta `+0.035778`, 95% CI `[+0.024822, +0.046694]`; primary gate passed.
- All five folds converged; per-fold `n_iter` 36/35/34/34/35. Fold-level candidate BA: 0.485185, 0.481481, 0.503704, 0.529630, 0.509579.
- Independent confirmation started with the exact same config. Compare against `artifacts/cpu-openpool-prompt-centered-twin-v15-retry2/confirmation/oof-all.parquet`.

## Confirmation result and decision (2026-11-07 12:01 JST)

- Complete independent 2,699-row, 150-prompt confirmation OOF; overall BA `0.500818`.
- Same-split adopted SVC confirmation BA `0.469714`; delta `+0.031104`.
- Prompt-paired bootstrap (2,000 replicates, seed 42): mean delta `+0.031020`, 95% CI `[+0.020325, +0.041482]`; confirmation gate passed.
- All five folds converged; per-fold `n_iter` 35/35/36/35/35. Fold-level candidate BA: 0.492593, 0.505556, 0.505556, 0.518838, 0.481481.
- Decision: adopt the 0.10 pool-weight candidate as the next SVC OOF comparison baseline. This is a CV adoption only; it does not claim Kaggle LB improvement and does not authorize a submission.
