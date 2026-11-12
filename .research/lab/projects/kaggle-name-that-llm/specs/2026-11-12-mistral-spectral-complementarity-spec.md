---
date: 2026-11-12
project: kaggle-name-that-llm
status: approved-under-active-goal
approval_basis: 2026-11-06-gpu-autonomous-first-place-spec
execution_status: primary-screen-not-started
tags: [spec, experiment, cpu, mistral, spectral, prompt-grouped]
---

# Mistral + Spectral fixed complementarity screen

## Question and rationale

The existing Mistral-7B-v0.1 primary OOF passed the adopted prompt-centered SVC gate, and a fixed 1/4 addition to the raw three-model blend improved primary BA from `.586408` to `.599769`. The frozen Spectral mean-field transform improved that raw three-model baseline to `.664952` on the same primary rows. Screen whether the Mistral probability addition remains complementary when it is applied before the already-approved fixed Spectral transform.

This is a primary-only screening experiment. Mistral was selected using primary OOF; neither this result nor the prior Mistral addition result is independent evidence.

## Frozen candidate and inputs

- Primary folds only: official `GroupKFold(prompt_id, 5)` OOF for the adopted Qwen3-8B + Qwen3-1.7B + prompt-centered SVC baseline and saved Mistral-7B-v0.1 fold logits.
- Candidate input probability: `(3 * baseline_probability + softmax(Mistral_logits)) / 4`. This is a fixed equal-component mean; do not fit or scan weights.
- Apply the unchanged `meanfield_probabilities` and `normalised_content_groups` implementation/defaults from `scripts/evaluate_spectral_cluster_meanfield.py` and its registered primary spec. Use only each fold's held-out texts and probabilities for clustering/correction; `prompt_id` is used only for paired analysis.
- Do not change or overwrite the saved baseline OOF, Mistral OOF, or original Spectral primary output. New outputs belong in `artifacts/cpu-mistral-spectral-complementarity-screen-v1/`.

## Evaluation and decision

- Verify all 2,699 IDs, labels, prompts, and folds align; verify Mistral logits reproduce its saved OOF predictions and raw baseline probabilities reproduce their saved predictions.
- Reproduce the original three-model Spectral primary predictions exactly before comparing the candidate.
- Main comparison: four-component-plus-Spectral candidate versus the frozen three-component Spectral primary output, using balanced accuracy and 5,000 paired prompt bootstrap replicates, seed 42. Also report raw baseline, Mistral-added raw, and Spectral-corrected values per fold.
- Repeat the Spectral spec's fixed mild (`0.65–1.00`) and moderate (`0.30–1.00`) class-retention simulations for 20 seeds each; report means and positive replicate rates. Do not tune from these simulations.
- Advance this combination only if its primary paired 95% CI lower bound against the existing Spectral primary is strictly above zero and both simulation means are positive with at least 60% positive replicates. Otherwise reject the combination. A pass authorizes only consideration of an independent confirmation; it does not authorize a Kaggle Notebook or submission.

## Scope and reproducibility

- CPU-only, one thread, saved OOF only. No model training, GPU process, test data/labels, Kaggle write, or submission.
- Add a dedicated runner `scripts/evaluate_mistral_spectral_complementarity.py`; do not modify the approved Spectral runner or existing candidate code.
- Save the command, runner, input paths, aligned row counts, metrics, bootstrap/simulation summaries, resource/time summary, and output under the new artifact directory. Keep the goal active after this screen.
