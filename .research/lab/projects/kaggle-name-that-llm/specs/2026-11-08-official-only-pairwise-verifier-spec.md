---
date: 2026-11-08
project: kaggle-name-that-llm
status: rejected-primary
execution_status: complete
tags: [spec, experiment, cpu, pairwise, prompt-grouped]
---

# Official-data-only pairwise same-model verifier

## Purpose and source signal

Kaggle Notebook [`prvsiyan/the-prompt-is-not-the-author`](https://www.kaggle.com/code/prvsiyan/the-prompt-is-not-the-author) describes a lightweight pairwise same-model verifier, but its V34.1 implementation depends on public A/B annotations generated from competition text; organizer guidance on that processing remains unresolved. This candidate reproduces only the general pairwise-comparison idea using official `train.csv` labels and text. It must not read or depend on A/B annotations, matched data, external model outputs, or the public notebook's trained assets.

Test whether a pairwise verifier can identify a passage's source model by comparing it with a small, fixed set of known examples per class. Its role is a standalone CPU candidate screen and a possible future source of complementary OOF evidence. No blend weight will be selected in this spec.

## Data and evaluation

- Official competition `train.csv` only: `id`, `prompt_id`, `text`, and `model`. No test text, external responses, external annotations, models, or labels are used.
- Reuse the exact saved primary `GroupKFold(prompt_id, n_splits=5)` assignments from the adopted Qwen8B + Qwen1.7B + prompt-centered SVC OOF artifact. The candidate's OOF IDs, labels, prompts, and fold numbers must match that artifact one-to-one.
- Compare raw candidate OOF predictions against the adopted Qwen blend (`BA=0.5864081531`) using the existing prompt-level paired bootstrap with 2,000 replicates and seed 42. Also report comparison with the prompt-centered SVC (`BA=0.5019338802`), fold BAs, class recall, confusion matrix, and word-length strata.
- Adoption gate: the candidate must improve on the adopted blend and have a 95% prompt-paired bootstrap lower bound greater than zero. If its interval includes zero, mark it uncertain; if its point estimate does not improve, reject it as a standalone candidate. A possible ensemble with a complementary but non-adopted verifier requires a separate nested-evaluation spec before any weight is chosen.
- Only if the primary gate passes, prepare an independent confirmation split under the active goal's confirmation rule. No submission, Notebook, Kaggle object, or external implementation change beyond the bounded CPU runner is authorized by this candidate spec.

## Fixed pairwise method

- Per outer fold, fit `char_wb` TF-IDF (3–5 grams, sublinear TF, `min_df=2`, maximum 100,000 features) and word TF-IDF (1–2 grams, sublinear TF, `min_df=2`, maximum 80,000 features) on outer-training text only. Add a fixed set of label-free per-passage length, punctuation, token-length, lexical-diversity, and sentence-length features.
- Training pairs use outer-training rows only. Positive pairs have the same `model` and different `prompt_id`. Negative pairs comprise same-prompt/different-model pairs and different-prompt/different-model pairs. Draw 18,000 positive pairs, up to 18,000 unique same-prompt negatives, and 18,000 cross-prompt negatives with a fixed seed. Do not include IDs, model names, prompt IDs, family metadata, or fold labels as pair-classifier features.
- Fit a fixed L2 logistic regression pair classifier with balanced class weights. Pair features are character cosine, word cosine, and absolute differences in the fixed style features.
- For each validation passage and each of the 18 classes, select 12 reference passages from distinct outer-training prompts, deterministically and without validation labels. Score all query-reference pairs with the pair classifier; average pair logits within each class, apply a row-wise softmax to those 18 class scores, and predict the argmax. No validation labels may affect references, features, pair selection, or calibration.
- Save per-fold OOF rows and class probabilities, input/config hashes, pair-count audits, feature definitions, runtime, peak RAM, and all metric outputs under `artifacts/cpu-pairwise-official-only-v1-retry1/primary/` outside Git.

## Implementation and safety

- Implementation repo: `/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/`.
- Add only `src/cpu_pairwise_verifier.py`; do not edit existing runners, configs, OOFs, or baseline artifacts. Use the project's existing virtual environment and saved official OOF fold assignments. Run CPU-only with BLAS/OpenMP threads capped at 2; do not request a GPU.
- Before execution, pass `.agents/skills/kaggle-workflow/scripts/codex_rate_limit.py --guard 15`. Require host `MemAvailable >=16 GiB` before launch and monitor it during execution. Stop safely between folds if the floor is breached, preserving completed folds and recording the exact resume position; never interrupt Host142 GPU runs/watchers.
- Verify exact OOF alignment, unique IDs, class order, finite features/probabilities, row-sum tolerance `1e-5`, no validation prompt in pair-training rows, positive pairs cross prompt IDs, and negative-pair label mismatch. Fail closed on any mismatch.
- A successful primary run completes five folds, reports all required metrics and hashes, and records whether it passed the stated adoption gate. No public/private Kaggle operation is part of this experiment.

## Primary result

- The initial run failed before writing any fold output because a reference-prompt audit attempted to hash NumPy arrays; its manifest is retained at `artifacts/cpu-pairwise-official-only-v1/run-manifest.json` with the failure recorded.
- The corrected runner also fixed mapping of fold-local reference rows into the validation feature matrix. The retry completed all five folds using official `train.csv` only; runner SHA-256: `7de030020be0430f87dfd4ce2dfcb65e418ce371decbc03ca6361bd1a45dba6f`.
- Candidate OOF balanced accuracy was `0.0911509` versus adopted blend `0.5864082`, delta `−0.4952573`; 2,000-replicate prompt-paired 95% CI was `[−0.5151870, −0.4744444]`. The adoption gate is rejected; confirmation and blending were skipped.
- Full OOF, probabilities, per-fold audits, class recall, confusion matrix, and word-length metrics are preserved under the retry run directory. The CPU best artifact and both GPU hosts' running jobs were left untouched.
