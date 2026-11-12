---
date: 2026-11-12
project: kaggle-name-that-llm
status: approved-under-active-goal
approval_basis: 2026-11-06-gpu-autonomous-first-place-spec
execution_status: planned
tags: [spec, experiment, cpu, mistral, spectral, prompt-grouped]
---

# Fixed Mistral + Spectral under small-prompt shape screen

## Question and rationale

The primary-only fixed Mistral `1/4` addition followed by the frozen Spectral mean-field transform reached BA `.689791` and passed its paired bootstrap gate. A separate Spectral-only diagnostic found primary degradation at pseudo-test group sizes `m=2/3`. Measure whether the Mistral+Spectral combination retains its advantage under the same small-prompt pseudo-test construction before allocating GPU time for independent confirmation.

This remains primary-only, selection-biased diagnostic evidence. It is not a CV split, independent confirmation, estimate of hidden-test structure, LB estimate, or permission to submit.

## Frozen procedure and inputs

- Use only the registered primary five-fold OOF for the adopted Qwen3-8B + Qwen3-1.7B + prompt-centered SVC baseline, the saved primary Mistral-7B-v0.1 logits, and official training texts/labels for sampling and scoring.
- Fixed candidate probabilities: `(3 * baseline_probability + softmax(Mistral_logits)) / 4`, followed by the unchanged `meanfield_probabilities` and `normalised_content_groups` functions/defaults used by the approved Spectral screen. No fitted or scanned weights/parameters.
- Construct 20 deterministic pseudo-test replicates with seeds `42–61`, at `m=2` and `m=3`; `m=2` is nested in `m=3` by selecting from one weighted Gumbel ordering per prompt. Run uniform class weights and the same fixed mild (`0.65–1.00`) and moderate (`0.30–1.00`) class-skew sensitivity scenarios as the Spectral-only screen.
- The sampler may use official prompt/model labels to draw rows. Both the Spectral clustering step and correction receive only the selected rows' texts and probabilities, never prompt IDs or labels. Prompt IDs and labels are retained only for sampling and scoring.
- Verify row IDs, labels, primary folds, class order, baseline probability predictions, Mistral logit predictions, and all input row counts before evaluation. Do not modify any source OOF, probabilities, logits, model files, or existing screen artifacts.

## Decision and reporting

- Compare fixed Mistral+Spectral predictions with the frozen baseline-only Spectral transform on each sampled pseudo-test set. Report each replicate and aggregate deltas, positive fraction, fold deltas, represented classes, inferred-cluster diagnostics, runtime, and peak RSS.
- A shape-robustness flag requires positive mean delta and at least 60% positive replicates in both `m=2` and `m=3` uniform scenarios. Skew scenarios are sensitivity checks and do not select or tune a setting.
- A failed flag does not erase the full-size primary screen; it lowers confidence and must be reported before any independent GPU confirmation. A passed flag still does not replace the independent confirmation required by the main spec.

## Scope and reproducibility

- CPU only, one thread, existing primary OOF artifacts only. No training, GPU use, Kaggle write, Notebook push, or submission.
- Add a separate runner `scripts/evaluate_mistral_spectral_small_prompt_shape.py` and write only to the previously unused `artifacts/cpu-mistral-spectral-small-prompt-shape-v1/` directory. Refuse to overwrite existing output.
- Preserve the existing Spectral-only shape screen, Mistral+Spectral full-size screen, and all underlying CPU results unchanged.
