---
date: 2026-11-12
project: kaggle-name-that-llm
type: experiment
tags: [mistral, spectral, prompt-shape, cpu, primary-oof]
spec: ../specs/2026-11-12-mistral-spectral-small-prompt-shape-spec.md
---

# Mistral + Spectral small-prompt shape screen

## Result

The fixed primary-screen candidate `(0.75 * baseline probabilities + 0.25 * softmax(Mistral logits))`, followed by the frozen Spectral mean-field transform, retained positive average gains in uniform pseudo-test shapes `m=2` and `m=3`. The registered uniform shape-robustness flag passed. This is primary-only, selection-biased diagnostic evidence; it is not independent confirmation, a hidden-test estimate, or an LB score.

## Frozen evaluation

- Spec: [fixed Mistral + Spectral under small-prompt shape screen](../specs/2026-11-12-mistral-spectral-small-prompt-shape-spec.md).
- Command: `/mnt/HDD10TB-2/aburatani/kaggle/.venv/bin/python scripts/evaluate_mistral_spectral_small_prompt_shape.py` from `/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm`.
- CPU-only, one thread, 20 seeds `42–61`, three fixed class-retention scenarios, and nested `m=2/3` samples. Official texts/labels/prompts were used only for sampling/scoring; each fold's clustering/correction received sampled text and probabilities only.
- Verified all 2,699 IDs, 18 labels, and five primary folds aligned; baseline probabilities and Mistral logits reproduced their saved OOF predictions; frozen baseline Spectral predictions reproduced exactly. All 120 replicate records retained 18 classes globally and contained 300–450 rows.
- Runtime 18.0s; peak RSS 506.6 MiB; no GPU, training, Kaggle write, push, or submission. New outputs only: `artifacts/cpu-mistral-spectral-small-prompt-shape-v1/summary.json` and `replicate-metrics.csv`. Existing CPU result artifacts were left untouched.
- The sklearn scorer emitted fold-level warnings where a sampled fold omitted a class present in its prediction vector. Replicate-level scoring included all 18 classes globally; no replicate omitted a class.

## Aggregate results

| Scenario | m | Mean delta vs baseline-only Spectral | Positive replicates | Mean baseline BA | Mean Mistral+Spectral BA |
|---|---:|---:|---:|---:|---:|
| Uniform | 2 | `+0.017271` | 0.80 | `.573963` | `.591233` |
| Uniform | 3 | `+0.025419` | 1.00 | `.581975` | `.607394` |
| Mild class skew | 2 | `+0.022273` | 0.90 | `.586551` | `.608824` |
| Mild class skew | 3 | `+0.019011` | 0.80 | `.596996` | `.616007` |
| Moderate class skew | 2 | `+0.027548` | 0.95 | `.576410` | `.603958` |
| Moderate class skew | 3 | `+0.020665` | 1.00 | `.589612` | `.610277` |

## Interpretation and next gate

Unlike the Spectral-only primary uniform shape screen, the fixed Mistral+Spectral composition passes the pseudo-test shape flag. This raises its priority for independent confirmation but does not resolve selection bias: Mistral was selected from primary OOF. Continue to require the independent confirmation split and Host142's verified host-key, queue, and current-runner pilot gates before any GPU continuation. Do not tune the fixed mixture from this screen or submit based on these results.
