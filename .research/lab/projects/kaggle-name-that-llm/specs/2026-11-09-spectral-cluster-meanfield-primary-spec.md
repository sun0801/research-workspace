---
date: 2026-11-09
project: kaggle-name-that-llm
source: active-goal / public-notebook-component
status: approved-under-active-goal
approval_basis: 2026-11-06-gpu-autonomous-first-place-spec
execution_status: primary-and-independent-confirmation-gates-passed
tags: [spec, postprocessing, prompt-clustering, mean-field, primary-oof]
---

# Spectral cluster mean-field primary screen

## Rationale

The version-10 Spectral Gaussian Notebook's text-only `normalised_content_groups` recovered held-out prompt groups with mean ARI `.9524`, though it over-split prompts and created some singletons. The Notebook also applies an at-most-once mean-field repulsion inside inferred clusters. The prior `cpu-inferred-test-prompt-sinkhorn-v1` used round(N/18) grouping and forces equal class marginals, which remains ineligible for Notebook use because official Evaluation states test class counts and public/private mixes differ. This candidate tests a distinct, fixed local correction without global class balancing.

## Frozen candidate

- Input baseline: the adopted Qwen3-8B + Qwen3-1.7B + prompt-centered SVC primary OOF probability arrays under `artifacts/cpu-qwen-prompt-centered-svc-probability-ensemble-v1/primary/`.
- For each saved outer fold, infer clusters from that fold's texts alone using version-10 `normalised_content_groups` defaults: English-stopword TF-IDF, sublinear TF, up to 80,000 float32 features, clipped cosine distance / median pairwise distance, average linkage, threshold `0.90`.
- Reproduce the Notebook's group-local mean-field block with fixed defaults: row z-normalized log probabilities; global column z-normalization over the current unlabeled batch; clusters of size 2–18 only; four iterations with `temperature=0.65`, `gamma=0.55`, `q=softmax(L/temperature)`, `lo=log(clip(1-q,1e-6,1))`, `L=base + gamma * (sum_rows(lo)-lo)`; row z-normalize corrected cluster scores; final softmax at temperature `0.72`.
- Exclude its orthographic rule masks and all global Sinkhorn scaling. Do not alter labels, tune parameters, choose a fold, or use true `prompt_id` in clustering or correction. Verify the baseline probabilities reproduce the saved `prediction` column before scoring.
- Main primary metric: balanced accuracy versus the unchanged blend argmax on identical rows. Use 5,000 prompt-cluster paired-bootstrap replicates, seed 42, through the canonical `gpu_analyze.paired_prompt_bootstrap` implementation.
- Robustness simulations: 20 deterministic replicates under each of two fixed class-specific row-retention schedules (`mild`: class retention from 0.65 to 1.0; `moderate`: 0.30 to 1.0). For replicate seeds 42–61, assign a seeded random permutation of 18 equally spaced retention probabilities to the saved class order; use that same class-to-rate mapping across folds and independent Bernoulli row retention within each fold. Apply row sampling using labels only to generate the held-out test-like missing-row pattern; clustering/correction receive only retained texts and probabilities. Require all labels remain represented in each fold. These simulations are sensitivity checks, not new CV splits or hidden-test estimates.

## Decision gates

Proceed to an independent confirmation screen only if (a) the full primary candidate's prompt-bootstrap 95% CI lower bound for BA delta is strictly above zero, (b) mean BA delta is positive under both fixed retention schedules, and (c) at least 60% of replicate-level deltas are positive in each schedule. Otherwise reject this correction for the current blend. Passing primary does not authorize a Kaggle Notebook: confirmation OOF, official hidden-test group-size uncertainty, runtime and output checks remain required.

## Scope and reproducibility

CPU-only, one thread; no GPU run, Kaggle write/submission, change to existing OOF/base model, or queue mutation. Save the runner, input hashes, predictions, summary and exact command under a new ignored implementation-artifact directory. Use only the active goal's authorized implementation scope.
