---
date: 2026-11-12
project: kaggle-name-that-llm
type: experiment-result
status: rejected
tags: [spectral, punctuation, prompt-grouped, cpu]
---

# Spectral punctuation support prior screen

## Decision

**(b) 試さない。** The fixed fold-local punctuation prior did not change any primary OOF prediction. Per the registered gate, do not run confirmation and do not tune the markers or penalty.

## Setup

- Spec: [fixed screen spec](../specs/2026-11-12-spectral-punctuation-prior-screen-spec.md)
- Source candidate: Kirill Tymchishin, `kirilltym/lora-trained27-evidence-for-close-calls`, version 19; only the fixed punctuation prior was evaluated, not the public multi-source ensemble.
- Split: registered primary GroupKFold, 2,699 rows / 150 prompts / five folds.
- Baseline: reconstructed current Spectral mean-field probabilities. Candidate: same probabilities with the pre-registered fold-local four-marker support penalty (`0.70`), with no search.
- Run: `evaluate_spectral_punctuation_prior.py --split primary`; CPU-only, one BLAS/OpenMP thread. Output: `artifacts/cpu-spectral-punctuation-prior-screen-v1/primary/`.

## Results

- Baseline BA `0.664952`; candidate BA `0.664952`; delta `0.000000`.
- Prompt-paired bootstrap: 5,000 draws, seed 42; 95% CI `[0, 0]`, mean delta `0`, adoption `reject`.
- Changed predictions `0`; corrected errors `0`; introduced errors `0`. Fold BA was unchanged in all five folds.
- The rule had active markers and penalty applications, but no argmax prediction changed. This is a null result for the exact registered formula, not evidence against every possible punctuation feature.
- Confirmation, parameter tuning, Kaggle push, and submission were not run. No GPU or model/data asset was used.

## Provenance

The machine-readable metrics and per-class/fold summaries are in the ignored run artifact `artifacts/cpu-spectral-punctuation-prior-screen-v1/primary/summary.json` in the Kaggle implementation workspace. This Research Workspace note preserves the decision and headline results.
