---
date: 2026-11-09
project: kaggle-name-that-llm
source: active-goal / public-notebook-hypothesis
status: approved-under-active-goal
approval_basis: 2026-11-06-gpu-autonomous-first-place-spec
execution_status: completed-promising-followup-required
tags: [spec, prompt-clustering, source-reproduction, cpu-screen]
---

# Spectral Notebook prompt-cluster recovery screen

## Question

Does the text-only `normalised_content_groups` method in Robinamirbahar's public [Spectral Gaussian Attribution Notebook](https://www.kaggle.com/code/robinamirbahar/name-that-llm-spectral-gaussian-attribution), version 10, recover held-out prompt groups on the saved primary split well enough to justify a separate prompt-relative prediction experiment?

The Notebook claims high prompt-clustering ARI, but its retrieved metadata has no reproducible outputs and conflicting run recency. This screen reproduces only the clustering function used inside its fold loop; it is not a reproduction of the Notebook's model stack or score.

## Fixed procedure

- Use official `train.csv` text and the `fold` values from the adopted primary OOF table `gpu02-qwen3-8b-posttrained-openpool-v15/primary/oof-all.parquet` (2,699 IDs, 150 prompts, five saved folds). Check exact unique-ID alignment and that each true prompt belongs to one fold.
- For each fold, provide only that fold's validation texts to the clusterer. Never pass `prompt_id`, labels, predictions, or training-fold text to the clustering function. Use `prompt_id` only after clustering to calculate adjusted Rand index (ARI) and group-size diagnostics.
- Reproduce the retrieved version-10 `normalised_content_groups` defaults exactly: English-stopword TF-IDF, `sublinear_tf=True`, `max_features=80000`, float32, clipped cosine distance, median-distance normalization, average linkage, distance threshold `0.90`.
- Report ARI per fold and mean, predicted versus true cluster count, predicted cluster-size distribution, and the exact source/config/data hashes. Do not tune the threshold or choose a fold based on the result.
- CPU-only, one BLAS/OpenMP thread. Do not occupy or modify either GPU host's active runs. Do not train a classifier, use labels in clustering, infer hidden-test labels, change an existing queue, or write to Kaggle.

## Decision boundary

This is only a prompt-recovery diagnostic. Advance to a separately preregistered prompt-relative prediction screen only if mean ARI is at least `0.90`, every fold is at least `0.80`, and the predicted cluster-size distribution does not collapse to singleton or giant groups. Even a pass does not establish test-set performance: the follow-up must simulate variable prompt sizes and unequal class counts, use no true prompt IDs at inference, and compare classifier/post-processing effects under the main goal's grouped and nested evaluation rules. Otherwise reject this clusterer and do not add a prompt-cluster correction.

## Execution authorization and boundaries

This CPU-only diagnostic is within the active goal's approved automatic-candidate scope. It does not alter the accepted CPU baseline, any existing GPU config/runner, or any running job. Preserve its code and summary in the external Kaggle implementation/artifact directories and report the outcome in the project experiments log.
