---
date: 2026-11-12
project: kaggle-name-that-llm
status: approved-under-active-goal
approval_basis: 2026-11-06-gpu-autonomous-first-place-spec
execution_status: confirmation-running-host142-gpu1
tags: [spec, experiment, confirmation, prompt-grouped, mistral, spectral]
---

# Mistral + Spectral fixed composition confirmation

## Purpose

The fixed Mistral 1/4 addition followed by the frozen Spectral transform passed the primary-only screen in `2026-11-12-mistral-spectral-complementarity-spec.md` (BA `.689791`, paired prompt bootstrap 95% CI `[+.013063,+.036412]`). Because Mistral was selected using primary OOF, the independent confirmation split is required before treating this composition as a candidate. Passing this confirmation does not imply a Kaggle score or authorize a submission.

## Fixed procedure

- Use only the registered shuffled `GroupKFold(prompt_id, 5, random_state=42)` confirmation outputs: baseline probability ensemble from `artifacts/cpu-qwen-prompt-centered-svc-probability-ensemble-v1/confirmation/`; Mistral confirmation logits from `artifacts/gpu03-mistral-7b-v0-1-openpool-v15/confirmation/`; and original Spectral confirmation output from `artifacts/cpu-spectral-cluster-meanfield-confirmation-v1/confirmation-oof-postprocessed.parquet`.
- The Mistral confirmation must first be completed under the existing approved [Mistral run spec](2026-11-08-mistral-7b-v0-1-prompt-grouped-spec.md), on Host142 GPU1 only, after strict host-key verification, registered queue terminal state, a passing current-runner pilot, `--guard 15`, and full GPU/RAM/resource preflight. Do not move to Host141 or modify `src/gpu_experiment.py`.
- Align all IDs, labels, prompts, and confirmation folds; reproduce saved baseline and original Spectral predictions exactly. Candidate probability is `(3 * baseline_probability + softmax(Mistral_logits)) / 4`, followed by the unchanged Spectral text grouping and mean-field transform within each held-out fold.
- Main comparison: candidate versus the saved Spectral confirmation output, BA and 5,000 paired prompt bootstrap replicates, seed 42. Report per-fold BA and class recalls.
- Repeat the primary screen's fixed mild (`0.65–1.00`) and moderate (`0.30–1.00`) class-retention simulations with 20 seeds each; no tuning.

## Decision and outputs

- Confirmation passes only if the paired 95% CI lower bound is strictly above zero and both simulation means are positive with at least 60% positive replicates. Otherwise reject the composition for adoption.
- CPU evaluation only, one thread. Never overwrite primary/confirmation source outputs. Store new outputs under `artifacts/cpu-mistral-spectral-complementarity-confirmation-v1/` and add the runner only after Mistral confirmation OOF exists.
- Even if confirmed, compare the candidate to the current Public Leaderboard (latest official check: `.769` on 2026-11-14) and the v12/v13 BA-to-LB observations before deciding whether a private Notebook runtime check is worthwhile. Any push/submission still requires fresh pre-action official, privacy, runtime, and quota gates.

## Current execution state

- Host142 was checked locally. The registered queue/lock/resource gates and current-runner pilot passed on 2026-11-13, then confirmation started in tmux `mistral-confirm` on the pinned GPU1. The active process is PID `2872240`; do not stop it, duplicate it, or move it. Latest state and resume command are in the [continuation log](../experiments/2026-11-13-host-continuation-poll.md).
- At the 2026-11-14 13:20 JST poll, folds 0–2 were complete and fold 3 was in progress. After all five confirmation OOF folds finish, run only the fixed CPU evaluation above; do not alter weights, splits, or the frozen Spectral transform.
