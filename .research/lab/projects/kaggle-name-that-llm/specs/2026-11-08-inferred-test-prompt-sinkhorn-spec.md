---
date: 2026-11-08
project: kaggle-name-that-llm
source: autonomous-goal
status: approved
approval_basis: active-goal-2026-11-06-gpu-autonomous-first-place-spec
execution_status: offline-gates-passed-notebook-gate-unresolved
tags: [spec, cpu, prompt-group-inference, sinkhorn, postprocessing]
---

# Text-only inferred prompt grouping with Sinkhorn postprocessing

## Motivation and evidence

Kaggle Notebook [`handeakn/fine-tuning-with-sinkhorn-oof-proba`](https://www.kaggle.com/code/handeakn/fine-tuning-with-sinkhorn-oof-proba) groups text-only test rows with TF-IDF and average-linkage agglomerative clustering, then uses Sinkhorn scaling to assign balanced model marginals within each inferred group. The public Notebook tunes postprocessing against OOF labels grouped by the true `prompt_id`; that does not validate whether its text-only test-time clustering preserves those groups. This experiment isolates the postprocessing idea and evaluates it on held-out OOF texts without using their prompt IDs or labels to create clusters.

The official task has 18 candidate model labels and the test data does not expose prompt IDs. The candidate tests the explicit structural assumption that the hidden test set contains approximately one passage from each candidate model for each prompt. It does not assume that TF-IDF clustering recovers prompts correctly; this is measured as a diagnostic.

## Fixed data and method

- Reuse the adopted `cpu-openpool-prompt-centered-low-pool-weight-v15` decision scores and exact OOF rows for `primary` and, only after the primary gate passes, `confirmation`. Do not refit or change the SVC.
- Align decision-score rows to OOF rows by unique `id`, and confirm class order against the stored `classes` array. Use only the official passage `text` column as clustering input. Do not pass `prompt_id`, `model`, labels, fold, or SVC predictions into the vectorizer or clusterer.
- Cluster all OOF texts in a split together, matching test-time transductive clustering over the full hidden test set. Fixed transform: `TfidfVectorizer(stop_words="english", sublinear_tf=True)` with default word unigrams; `AgglomerativeClustering(n_clusters=round(N/18), metric="cosine", linkage="average")`.
- Treat the stored multiclass SVC decision scores as logits. Within each inferred cluster, apply 100 Sinkhorn iterations at fixed `T=0.3`, with row sums 1 and each label's column sum `cluster_size/18`. Predict the largest adjusted score. Do not search group counts, text features, temperatures, iteration counts, or assignment variants.
- This is an unsupervised transductive transform over held-out texts only. It may see all held-out texts in the split, as inference sees all test texts; it must not see validation labels or prompt IDs until after predictions are fixed.

## Evaluation gates

- Compare against the unchanged adopted SVC argmax predictions on identical row IDs, labels, and saved folds. Report balanced accuracy, fold scores, class recalls, confusion matrix, and paired BA delta.
- Use the existing prompt-level paired bootstrap implementation with at least 2,000 resamples; fix 5,000 replicates and seed 42. The primary 95% CI lower bound for the postprocessing-minus-argmax delta must exceed zero before evaluating confirmation. Confirmation uses the saved independent `blend-confirm` assignment and the same fixed transform and gate.
- Report adjusted Rand index, cluster purity, cluster sizes, and the count of groups not sized 18 only as diagnostics after clustering. Do not change the method based on these diagnostics or use true `prompt_id` to repair clusters.
- If either required gate fails, do not create a Notebook or Kaggle object. If both pass, treat this only as a possible inference postprocessor; separately verify the hidden-test group-size assumption and offline runtime before any private Notebook.

## Scope and resource gate

- This is a CPU-only local analysis of existing OOF scores. Read but do not modify the adopted SVC model, predictions, configs, or baseline artifacts. Save all derived outputs to a new candidate directory.
- Before implementation, preserve the source OOF and score hashes. Before the analysis, run the active-goal utilization guard. Use no GPU and do not interfere with running Qwen jobs.
- No Kaggle Notebook, Model/Dataset, or submission is created by this experiment. Any future submission must follow the parent goal's offline, Notebook-only, privacy, daily/final submission, and leaderboard gates.

## Reproducibility

Save the source manifests/hashes, fixed parameters, candidate OOF predictions, bootstrap summary, cluster diagnostics, and exact command under `artifacts/cpu-inferred-test-prompt-sinkhorn-v1/` in the external experiment repository. Record the result and decision in the workspace experiment log and project README.

## Notebook eligibility review (2026-11-08)

- The local primary and confirmation paired-bootstrap gates pass, but they validate this transform on held-out OOF texts from the training design, not on the hidden-test prompt structure.
- The official [Evaluation page](https://www.kaggle.com/competitions/name-that-llm/overview/evaluation) says test passage counts are unequal across models and that the public/private model mix differs. If every hidden-test prompt had exactly one passage from each of the 18 models, full-test class counts would be equal; that conflicts with the official description. A participant reply in [discussion 755733](https://www.kaggle.com/competitions/name-that-llm/discussion/755733) also says prompt groups may be incomplete, but treat that reply as unverified community interpretation.
- Therefore the equal-per-model-per-prompt Sinkhorn marginal is unsupported for the hidden test. This candidate is not eligible for a private Notebook under the current fixed transform. Keep the offline OOF gain as research evidence; do not create a Kaggle Notebook/Model/Dataset or submission from it. Any revised postprocessor needs a separate preregistered evaluation that addresses unequal/partial prompt groups and checks offline runtime before Notebook creation.
