---
date: 2026-11-12
project: kaggle-name-that-llm
type: experiment
tags: [pair-correction, spectral, prompt-grouped, cpu]
spec: ../specs/2026-11-12-kirill-close-pair-screen-spec.md
---

# Fixed close-pair conditional correction screen

## Procedure

- Command: `/mnt/HDD10TB-2/aburatani/kaggle/.venv/bin/python scripts/evaluate_kirill_pair_correction.py` from `/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm`.
- Fixed public-source rule: clusters of exactly two from our frozen Spectral text grouping; TF-IDF cosine overlap at least `.10` (English stop words, sublinear TF, uni/bigrams); mix probability with the distinct-label conditional marginal at strength `.50`.
- Base is the exact Mistral 1/4 addition followed by the unchanged Spectral mean-field transform (primary BA `.689791`). It was reproduced exactly before applying the pair rule. The source Notebook uses Qwen embedding groups; this screen instead uses our Spectral groups, so it tests an adaptation, not a full reproduction.
- All 2,699 IDs and 150 prompts aligned. CPU-only, one thread, no GPU/Kaggle writes. Wall time `80.993 s`, max RSS `251.8 MiB`.
- Runner SHA-256 prefix `7f5374d4`; input/runner prefixes and output files are in `artifacts/cpu-mistral-spectral-pair-correction-screen-v1/summary.json`. No full hash is copied here.

## Result and decision

- Only one eligible pair appeared across all five folds (fold4); no OOF prediction changed.
- BA remained `.689791`, delta `0.0`; 5,000 paired prompt bootstrap replicates, seed 42, CI `[0.0, 0.0]`.
- Mild `.65–1.00` and moderate `.30–1.00` class-retention simulations each had mean delta `0.0`, with 0/20 positive replicates.
- Gate failed. Reject this adaptation; do not independently confirm it or prepare it for submission. The public audit concludes **(b) 試さない** for this source's close-pair rule on the current Spectral grouping. The broader public ensemble was not reproduced.

## Outputs

- `../../../../../../kaggle/name-that-llm/scripts/evaluate_kirill_pair_correction.py`
- `../../../../../../kaggle/name-that-llm/artifacts/cpu-mistral-spectral-pair-correction-screen-v1/summary.json`
- `../../../../../../kaggle/name-that-llm/artifacts/cpu-mistral-spectral-pair-correction-screen-v1/primary-predictions.parquet`
