---
date: 2026-11-15
project: kaggle-name-that-llm
status: approved-under-active-goal
approval_basis: active-goal-started-2026-11-06-and-confirmation-spec
tags: [spec, kaggle, private-notebook, mistral, spectral, runtime]
---

# Mistral + Spectral private Notebook runtime check

**Authorization date: 2026-11-06 (active goal); candidate gate passed 2026-11-15.** This spec is a deployment/runtime extension of the approved [Mistral confirmation spec](2026-11-12-mistral-spectral-complementarity-confirmation-spec.md), not a new model comparison. It authorizes local implementation and a single private Notebook runtime/submission check under the active goal's existing privacy, quota, GPU, and pre-action gates.

## Decision basis

- The fixed candidate passed independent confirmation: BA `.676823` vs frozen baseline `.653828` (`+.022995`), paired prompt-bootstrap 95% CI `[+.011596, +.034074]`; the two class-retention simulations were positive in 20/20 replicates. Fourteen of 18 fold-averaged class recalls improved; four declined.
- Existing baseline/Spectral Notebook results are v12 CV `.586` → Public `.541` and v13 confirmation `.654` → Public `.560`. This is only two CV-to-Public observations, so the transfer estimate is uncertain. A single Public check is worthwhile because the candidate is independent-confirmation positive and the leaderboard gain cannot be inferred reliably from those two observations.
- Current public top is `.771` (official check 2026-11-15). This candidate is a measured incremental component, not evidence that the top has been reached. Continue the broader goal after the one check unless the overall goal succeeds.

## Fixed candidate and inference

- Base model: Kaggle `mistral-ai/mistral/pytorch/7b-v0.1-hf`, version 1, Apache-2.0; pin to the approved training revision and use FP16 inference where the accelerator does not support BF16.
- Use the five primary-fold `stage2/epoch-002/adapter` checkpoints from `artifacts/gpu03-mistral-7b-v0-1-openpool-v15/primary/fold-{0..4}/`. Do not use confirmation-fold models for prediction or change training weights.
- For each test row, obtain each fold model's row-wise softmax probabilities and average the five fold probabilities. Compose the fourth component using `(3 * baseline_probability + mean_mistral_fold_probability) / 4`, then apply the already frozen Spectral mean-field transform exactly as in v13. Do not tune weights, labels, or post-processing on test scores.
- Keep the current three-component Qwen8/Qwen1.7/SVC predictions unchanged. Preserve the test-only input, ID sequence, 4,000-row hidden-run behavior, `submission.parquet` schema, and offline runtime. Notebook and all Kaggle artifacts must remain private.

## Scope

- Create a new source directory `notebooks/name-that-llm-private-baseline-v14-mistral-spectral-source/` by deriving from the scored v13 source. Add only Mistral inference and the fixed four-component composition; preserve v13 unchanged.
- Add the five selected adapter files to a private, versioned inference asset bundle. Keep model weights, datasets, submission files, and generated outputs outside Git. Use the existing Kaggle asset dataset if its private update can be made; otherwise stop before any public creation.
- Expected code changes are the new v14 Notebook and its metadata, plus a narrowly scoped asset packaging helper only if needed. No training runner, OOF source, baseline, Spectral implementation, or split changes.

## Pilot, resource, and runtime gates

- Before any local GPU use, run `codex_rate_limit.py --guard 15`. Host142 may only be inspected locally; do not use GPU1. Check Host141 with `ssh 141` immediately before use and require an available approved 16-GB GPU, no conflicting owner, adequate host RAM, and at least 2 GiB free VRAM after the measured pilot peak. Do not kill or displace another process.
- Run a bounded 64-row, five-adapter inference pilot with the same sequence length, model precision, adapter loading order, and Spectral code intended for Kaggle. Require finite aligned probabilities, no OOM, and measured runtime/peak memory. If BF16 is unsupported, FP16 casting is allowed; changing to 4-bit or another model/runtime path requires a new comparison spec.
- Kaggle runtime gate: configured private `NvidiaTeslaT4`, GPU count verified, each GPU retains at least 10% memory headroom at peak, offline model/data sources resolve, a 64-row probe passes, and 1.25× extrapolation for all hidden rows remains below the 9-hour cap. If any gate fails, do not submit; preserve the notebook and diagnosis privately/local-only.
- Before Kaggle writes, recheck official rules/deadline/current leaderboard, notebook privacy and attached assets, the actual runtime configuration, daily submission count (maximum five), and final-submission count (maximum two). Submit only one candidate run under this spec. No push is permitted if privacy cannot be verified or local Kaggle write authentication is unavailable.

## Validation and decision

- Locally verify only code/data alignment: five adapters map to folds 0–4, output probabilities are finite and normalized, the existing v13 path is unchanged, and Spectral receives the same test texts and candidate probability matrix. The bounded GPU pilot supplies runtime and resource evidence.
- At Kaggle runtime, verify the exact hidden test ID sequence/row count, labels only from the fixed class list, no internet access, and valid `submission.parquet`; record job state and Public score without exposing any private code.
- Compare the returned Public LB to v13 `.560`, v12 `.541`, and the then-current top. The goal is reached only if a valid submission exceeds the contemporaneous top. Otherwise retain the measured score and continue toward a stronger candidate.
- Record command, input/adapters, runtime, per-GPU peak, any failures, submission reference, and score in the existing Mistral confirmation/host log. Never transcribe full SHA-256 values; use `sha256sum -c` and record only “一致”, command, and optional first eight characters.
