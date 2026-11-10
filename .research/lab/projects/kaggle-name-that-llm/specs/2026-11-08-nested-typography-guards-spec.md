---
date: 2026-11-08
project: kaggle-name-that-llm
source: active-goal / public-notebook-hypothesis
status: approved
execution_status: rejected-primary
tags: [spec, experiment, cpu-evaluation, prompt-grouped, typography]
---

# Fold-local typography class guards

## Motivation and evidence boundary

The public Kaggle Notebook [muhammadasjad2008/ntl-v1-baseline](https://www.kaggle.com/code/muhammadasjad2008/ntl-v1-baseline) has a recent search-index run timestamp but `get_notebook_info` reports an older last-run time; its current version is 23 and its introduction describes a later “v8” change. The introduction claims three typography rules: curly quotes exclude Claude/GLM, a spaced em dash permits only four Claude/GLM labels, and any em dash excludes Gemini 3.1/3.6/3.8. The retrieved code instead documents an older `--post` switch for spaced-em-dash/Hungarian processing and does not implement all three claimed rules. The complete notebook also attaches many external artifacts, including a dataset with an unresolved provenance question. Treat its claims and score as unverified; do not reuse its predictions, weights, or external assets.

Test only the underlying text-only class-guard hypothesis against our adopted primary OOF. Learn the permitted classes separately inside each outer training fold so no held-out labels determine a validation-row rule.

## Fixed method and evaluation

- Baseline: adopted Qwen blend probabilities and the `prediction` column from `artifacts/cpu-qwen-prompt-centered-svc-probability-ensemble-v1/primary/`; canonical primary folds are the saved prompt-grouped GroupKFold split. In `oof-all.parquet`, `baseline_prediction` refers to the older SVC comparator, not the adopted Qwen blend; do not use it as the guardrail baseline.
- Patterns, applied case-sensitively to official response text: (1) any U+2018/U+2019/U+201C/U+201D curly quote; (2) U+2014 em dash with whitespace on both sides; (3) any U+2014 em dash.
- For each outer fold and each pattern, count pattern-matching rows by class using only the other four folds. Enable a pattern only if training support is at least 20 rows; its permitted classes are those with at least 2 training matches. Disable a pattern if fewer than 2 classes remain. These thresholds are fixed before evaluation.
- At validation, intersect the enabled permitted-class sets for every matching pattern. Apply the intersection only when it contains at least 2 classes and the baseline assigns positive probability mass to it; set other class probabilities to zero and renormalize. If no pattern matches, the intersection has fewer than 2 classes, or retained mass is zero, preserve the baseline probabilities unchanged. No validation labels, prompt IDs, label counts, or test-set statistics enter rule construction or prediction.
- Primary gate: all 2,699 rows / 150 prompts, balanced accuracy, fold-level scores, per-class recall, and 2,000 prompt-level paired bootstrap replicates (seed 42) against the adopted baseline. The joint three-pattern method is the only candidate gate; single-pattern ablations/coverage are descriptive diagnostics and cannot be selected post hoc on this split. Proceed to the independent confirmation split only if the joint primary CI lower bound is positive and the completed same-split confirmation blend exists. No threshold/weight tuning on primary results.

## Scope, resources, and outputs

- Implement one read-only-input CPU evaluator at `/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/src/cpu_typography_guards.py`.
- Read official `train.csv`, complete adopted primary OOF/probability files, and canonical fold IDs. Write only to the new Git-ignored directory `artifacts/cpu-typography-guards-v1/`; refuse to overwrite existing output.
- Limit computation to two CPU threads; require process RSS <=32 GiB and host `MemAvailable` >=16 GiB throughout. No GPU, model download, external data, code competition object, Notebook, or submission is part of this candidate.
- Record source/model/config/OOF hashes, pattern counts per fold, coverage, masking fallbacks, metrics, bootstrap CI, command, runtime, and resource peak. Preserve all existing candidate artifacts.

Authorized under the active first-place goal. Passing primary only allows the registered confirmation evaluation; it does not authorize submission or adoption before both split gates pass.
