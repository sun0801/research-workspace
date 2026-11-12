---
date: 2026-11-09
project: kaggle-name-that-llm
spec: ../specs/2026-11-09-spectral-prompt-cluster-recovery-screen-spec.md
status: diagnostic-positive-followup-completed
tags: [experiment, prompt-clustering, public-notebook, cpu]
---

# Spectral Notebook prompt-cluster recovery screen

## Source and scope

- Source: [Robinamirbahar, Spectral Gaussian Attribution](https://www.kaggle.com/code/robinamirbahar/name-that-llm-spectral-gaussian-attribution), official Kaggle Notebook Info, current version 10.
- Retrieved source metadata last-run time is Nov 5, 2026, while the earlier recent-run search listed Nov 8. The notebook claims `0.9892` prompt-clustering ARI but that claim has no accompanying verified OOF artifact in our records.
- Reproduced only the version-10 `normalised_content_groups` function used inside its five-fold loop. This is not a reproduction of its classifier stack, submitted score, or a Public LB score.

## Frozen procedure and integrity

- For each fold in the accepted Qwen8B primary OOF table, clustered only that fold's validation text using source defaults: English-stopword TF-IDF, sublinear TF, up to 80,000 float32 features, clipped cosine distance divided by the median pairwise distance, average linkage, threshold `0.90`.
- No prompt IDs, labels, model predictions, or train-side text entered the clusterer. After clustering, true `prompt_id` was used only for ARI and group-size evaluation.
- Validated 2,699 unique IDs align between official train and OOF, all 150 prompt groups remain within one saved fold, and folds contain `540/540/540/540/539` rows.
- Train SHA-256: `40a22ce8d88c5f46feb4637a099db815bef5f713ffe53e89dbe1b7b21de77707`.
- Primary OOF SHA-256: `acccc818b3f484856bd852285178c0b47b14501bcb2f605f73fa7896418da9aa`.
- Runner SHA-256: `a27b5a1a7ae8dcf4a352d3360aa431e2872febdfd225ce315ad2f341cce64328`.
- Summary SHA-256: `3fdf0aa2cf94681e8749f0530689248e84eb5afff871995a9464366cb9e6fab6`.

## Result

| Saved fold | Rows | True prompts | Inferred clusters | ARI | Inferred singleton groups |
|---:|---:|---:|---:|---:|---:|
| 0 | 540 | 30 | 45 | 0.949955 | 9 |
| 1 | 540 | 30 | 39 | 0.964554 | 3 |
| 2 | 540 | 30 | 42 | 0.949091 | 7 |
| 3 | 540 | 30 | 52 | 0.942134 | 14 |
| 4 | 539 | 30 | 46 | 0.956282 | 8 |
| **Mean** | — | — | — | **0.952403** | — |

The preregistered screen gate passed: mean ARI at least `0.90`, each fold at least `0.80`, and no degenerate giant/singleton-only partition. However, the method predicts 39–52 clusters where each fold contains 30 true prompts; it fragments several prompts into singleton groups. High ARI therefore supports further testing, but does not establish a reliable one-cluster-per-prompt mapping.

## Decision and limits

Advance only to a separately preregistered prediction screen. It must use inferred clusters without true prompt IDs, include variable group sizes and unequal class totals in test-like simulations, and compare any fixed or nested-tuned cluster correction against unmodified OOF predictions. The current diagnostic does not show a classification or Public LB gain and does not justify a submission.

CPU-only, one BLAS/OpenMP thread; no GPU, Kaggle write, submission, queue change, or edit to existing runs. Result JSON is `artifacts/cpu-spectral-prompt-cluster-recovery-v1/summary.json`; runner is `scripts/evaluate_spectral_prompt_cluster_recovery.py` in the external Kaggle project.


## Follow-up completion (recorded 2026-11-12)

The fixed prompt-relative mean-field prediction screen and independent confirmation were completed under separate registered specs. Both passed their prompt-paired confidence-interval gates; the adopted confirmation BA is `.653828`. See [primary spec](../specs/2026-11-09-spectral-cluster-meanfield-primary-spec.md), [primary result](2026-11-09-spectral-cluster-meanfield-primary.md), and [confirmation result](2026-11-10-spectral-meanfield-confirmation.md). The original cluster recovery diagnostic itself remains a diagnostic only; this reconciliation closes its follow-up action.
