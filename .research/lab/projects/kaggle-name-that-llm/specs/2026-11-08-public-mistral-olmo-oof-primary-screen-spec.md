---
date: 2026-11-08
project: kaggle-name-that-llm
source: active-goal / Kaggle Discussion 756294
status: approved-under-active-goal
execution_status: public-mistral-compared-to-local; olmo-local-reproduction-pending
tags: [spec, experiment, oof, ensemble, prompt-grouped]
---

# Public Mistral/OLMo OOF primary screen

## Purpose and evidence

Screen whether the publicly released Mistral-7B-v0.1 and OLMo-2-1124-7B OOF predictions could be useful candidates relative to the currently adopted primary stack, Qwen3-8B + Qwen3-1.7B + prompt-centered SVC (`BA=0.586408`). This is a candidate-priority screen only; it does not make the external predictions eligible for a final Notebook.

Kaggle Discussion [756294](https://www.kaggle.com/competitions/name-that-llm/discussion/756294), comments `3550759`, `3551186`, and `3551199`, reports Mistral `.586`, OLMo `.576`, their equal-probability mean `.602`, and about `+.004` for adding both to a different Qwen blend on a held-out half of prompts. These are author reports, not our reproduction. Dataset [`emmanuelocheme/ntl-oof-mistral-olmo-lora`](https://www.kaggle.com/datasets/emmanuelocheme/ntl-oof-mistral-olmo-lora), version 1, is CC0 and contains only two OOF CSVs (788,410 bytes total); the author describes two-stage training on an expanded public in-style pool but does not identify all pool/model versions in the dataset metadata.

## Fixed screen

- Use `oof_mistral7b.csv` and `oof_olmo2_7b.csv` as released. Convert probabilities to float64 and align by exact `id` and class name.
- Candidate is the dataset's published fixed equal-probability mean: `0.5 * Mistral + 0.5 * OLMo`. Do not tune weights, temperature, thresholds, or class priors.
- Comparator is the existing complete primary OOF from `cpu-qwen-prompt-centered-svc-probability-ensemble-v1`, fixed equal mean of Qwen8B, Qwen1.7B, and prompt-centered SVC. Also report individual source models for context.
- Require exact agreement with official train IDs, `prompt_id`, saved primary GroupKFold membership, and the canonical 18 labels. Require unique IDs, finite nonnegative values, and row sums within `1e-4` of one. Stop without scoring if any check fails.
- Recompute full OOF BA, per-fold BA, per-class recall, and the fixed candidate-minus-comparator difference. Compute 2,000 prompt-cluster paired bootstrap replicates with seed 42 using the existing analysis implementation/convention. Do not use labels to select a coefficient.

## Interpretation and gates

- The result is a primary screen of public OOF artifacts. Even if its 95% CI lower bound is positive, this does not adopt the external candidate and does not authorize use of the probabilities for hidden test predictions.
- Before any local candidate is considered for adoption, reproduce the models with versioned, public/free, license-compatible sources and known data provenance; complete prompt-grouped primary evaluation and an independently trained confirmation split under the active goal's adoption gate. Mistral-7B-v0.1 is already represented by the queued local candidate03; compare that run to this external reference only after its OOF completes. OLMo requires a separate preregistered local candidate before any model training.
- No GPU job, external implementation change, Kaggle object, Notebook, or submission is part of this CPU-only screen. Preserve existing Host141/142 jobs and watcher order.

## Execution artifacts

- Temporary source download: `/tmp/ntl-oof-mistral-olmo-lora-v1/`; verified official version 1 files and hashes are recorded in the resulting experiment log.
- Existing comparison OOF: `/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/artifacts/cpu-qwen-prompt-centered-svc-probability-ensemble-v1/primary/oof-all.parquet`.
- Record exact file hashes, alignment, metrics, bootstrap CI, limitations, and next candidate decision in `experiments/2026-11-08-public-mistral-olmo-oof-primary-screen.md`.

## Screen result

The fixed equal mean scored BA `0.6023489933` versus `0.5864081531` for the current primary Qwen8B + Qwen1.7B + prompt-centered SVC blend (delta `+0.0159408402`). The 2,000-replicate prompt-paired bootstrap CI (seed 42) was `[+0.0011260368, +0.0307409893]`. The screen is positive, but adoption remains blocked on source training-pool/model provenance and independent local reproduction. See the experiment log for per-fold results and exact input hashes.


## Local Mistral comparison (2026-11-12)

After the approved local Mistral primary OOF completed, its prediction alignment and BA were compared with the public OOF reference; see [dated result addendum](../experiments/2026-11-08-public-mistral-olmo-oof-primary-screen.md#2026-11-12--public-mistral-oof-compared-with-completed-local-mistral-oof). Aggregate BA was similar, but only 68.58% of predictions agreed. This does not establish source provenance or permit use of the public OOF. The OLMo reproduction and any candidate adoption remain pending.
