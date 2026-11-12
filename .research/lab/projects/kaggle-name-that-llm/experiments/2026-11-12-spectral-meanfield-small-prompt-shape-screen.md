---
date: 2026-11-12
project: kaggle-name-that-llm
type: experiment-result
status: completed-primary-shape-robustness-flagged
tags: [spectral, mean-field, prompt-shape, cpu, prompt-grouped]
spec: ../specs/2026-11-12-spectral-meanfield-small-prompt-shape-screen-spec.md
---

# Spectral mean-field under small prompt groups

## Decision and interpretation

The fixed mean-field correction is **not robust on the primary OOF under m=2/3 prompt subsampling**: both uniform primary means are non-positive and fewer than 60% of draws improve. Confirmation remains positive under the same uniform simulations. This does not erase the full-prompt confirmation result or estimate hidden-test performance; it lowers confidence that the full-prompt gain will transfer if the hidden rerun has small prompt groups. No parameter tuning or submission follows from this diagnostic.

The inspiration is Kaggle [Discussion 753177](https://www.kaggle.com/competitions/name-that-llm/discussion/753177). Its author describes `m=2` as a weak sanity check over 15 related blend-family submissions, with one influential outlier and selection effects. The hidden prompt-group size was not verified here.

## Procedure

- Spec: [fixed screen specification](../specs/2026-11-12-spectral-meanfield-small-prompt-shape-screen-spec.md).
- Candidate: unchanged, already-confirmed version-10 Spectral local mean-field transform; comparator: raw saved Qwen3-8B + Qwen3-1.7B + prompt-centered SVC probability argmax.
- Evaluated both registered primary and independent confirmation OOFs. Per saved fold, each of 150 prompts contributed either 2 or 3 rows sampled without replacement. `m=2` and `m=3` were nested from the same seeded row ordering. Conditions were uniform, mild per-class weight skew (`.65–1.0`), and moderate skew (`.30–1.0`), using 20 seeds `42–61`.
- Sampler used prompt/model IDs to construct the synthetic shape; clusterer and mean-field received only selected texts and probabilities. No true prompt ID or label entered the transform.
- Official train structure was preserved: 149 prompts have 18 distinct model answers and one has 17; no within-prompt duplicate labels. Every simulation replicate retained all 18 labels globally. The fold-level scorer emitted sklearn warnings when a class was absent from a particular small fold sample; aggregate replicate BA was calculated over the globally represented 18 classes.
- Run command: `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 uv run --env-file ../.env python scripts/evaluate_spectral_meanfield_small_prompt_shape.py`.
- CPU-only; no existing OOF, model, or Kaggle object was modified. The external implementation runner is `scripts/evaluate_spectral_meanfield_small_prompt_shape.py`.

## Aggregate results

Deltas are mean candidate-minus-baseline balanced accuracy across 20 deterministic samples; `positive` is the fraction of replicates with delta > 0. Full metrics are in the machine-readable artifact summary.

| Split | Sampling | m=2 mean Δ / positive | m=3 mean Δ / positive |
|---|---|---:|---:|
| Primary | Uniform | `-0.012948` / 0.25 | `-0.001217` / 0.45 |
| Primary | Mild class skew | `-0.009922` / 0.35 | `+0.003135` / 0.50 |
| Primary | Moderate class skew | `-0.012856` / 0.30 | `-0.000635` / 0.55 |
| Confirmation | Uniform | `+0.006320` / 0.70 | `+0.010591` / 0.75 |
| Confirmation | Mild class skew | `-0.004319` / 0.35 | `+0.007985` / 0.80 |
| Confirmation | Moderate class skew | `-0.004263` / 0.30 | `+0.003163` / 0.65 |

Selected OOF rows per replicate were 300 for m=2 and 450 for m=3. Uniform confirmation sampling preserved positive means, but primary uniform results failed the spec's shape-robustness flag. Class-skewed conditions are further sensitivity checks, not chosen settings.

## Failed starts and artifact

- The first run stopped during preflight because the initial code incorrectly required 18 rows for every prompt. Inspection confirmed one prompt has 17; the spec and sampler were corrected to use the observed 17/18 unique-row structure.
- The second run stopped before output because the frame constructor omitted the text column needed by the clusterer. The runner was corrected and the final run completed.
- Final artifacts are `artifacts/cpu-spectral-cluster-meanfield-small-prompt-screen-v1/summary.json` and `replicate-metrics.csv` in the Kaggle implementation workspace. Output directory creation is exclusive; no previous artifact was overwritten.
