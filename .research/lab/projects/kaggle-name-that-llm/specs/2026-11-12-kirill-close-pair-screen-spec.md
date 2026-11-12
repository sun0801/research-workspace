---
date: 2026-11-12
project: kaggle-name-that-llm
status: approved-under-active-goal
approval_basis: 2026-11-06-gpu-autonomous-first-place-spec
execution_status: primary-screen-rejected; no-advance
tags: [spec, experiment, cpu, pair-correction, prompt-grouped]
---

# Fixed close-pair conditional correction screen

## Question and source

Test whether the close-pair probability rule described in Kirill Tymchishin's public Notebook improves the current fixed Mistral+Spectral primary OOF. This is a narrow adaptation: use the already-frozen `normalised_content_groups` clusters from our Spectral method instead of the source Notebook's Qwen embedding groups. Do not reproduce the Notebook's large public ensemble.

Source: `https://www.kaggle.com/code/kirilltym/lora-trained27-evidence-for-close-calls` current version 18 at 2026-11-12 retrieval. The author reports version 17 Public `.684`; version 18 score is pending in the Notebook text and its latest interactive log is only a format preview. See `experiments/2026-11-12-kirill-close-pair-audit.md`.

## Frozen rule and inputs

- Use baseline primary probabilities and Mistral logits already used by `2026-11-12-mistral-spectral-complementarity-spec.md`.
- Form the fixed Mistral 1/4 addition `(3 * baseline_probability + softmax(Mistral_logits)) / 4`, then apply the unchanged Spectral mean-field transform.
- Pair eligibility: a Spectral text cluster has exactly two rows, and the pair's row-wise TF-IDF cosine overlap is at least `.10`, with English stop words, sublinear TF, and 1–2 grams.
- For each eligible pair, compute `q_i(c) ∝ p_i(c) * (1 - p_j(c))` and `q_j(c) ∝ p_j(c) * (1 - p_i(c))`; mix each original row probability 50/50 with its conditional distribution. Keep non-pairs unchanged. No parameter fitting or scans.
- The pair clustering and all probability processing are within each held-out primary fold. `prompt_id` is used only for paired analysis.
- Verify the same 2,699 IDs, labels, prompts and folds; reproduce the Mistral+Spectral predictions from the prior screen before pair correction. Do not overwrite either prior screen's outputs.

## Evaluation and gates

- Compare pair-corrected predictions to the frozen Mistral+Spectral predictions with BA and 5,000 paired prompt bootstrap replicates, seed 42. Report eligible pair counts and prediction changes per fold.
- Repeat class-retention simulations for mild `.65–1.00` and moderate `.30–1.00`, 20 seeds each, using the same fixed rule and report mean BA delta and positive-replicate fraction versus Mistral+Spectral.
- Advance only if the paired 95% CI lower bound is strictly above zero and both simulation means are positive with at least 60% positive replicates. Otherwise reject this adaptation.
- A pass authorizes consideration of an independent confirmation only; it does not authorize a Notebook or submission.

## Scope and outputs

- CPU only, one thread, existing saved primary outputs, no model fitting, GPU, test data/labels, Kaggle write or submission.
- Add dedicated runner `scripts/evaluate_kirill_pair_correction.py`. Save outputs under `artifacts/cpu-mistral-spectral-pair-correction-screen-v1/`; refuse overwrite.
