---
date: 2026-11-09
project: kaggle-name-that-llm
source: active-goal / Kaggle Discussion 756294
status: approved-under-active-goal
approval_basis: active-goal-2026-11-06-gpu-autonomous-first-place-spec
execution_status: preflight-failed-fold-partition-mismatch-no-score
tags: [spec, oof, ensemble, prompt-grouped, public-data]
---

# Anto Pil cross-stack public OOF screen

## Question and scope

Test whether a fixed family-balanced mean of Anto Pil's public Qwen3/Llama/SVM OOF probabilities and the already-screened Mistral/OLMo OOF mean shows complementary errors against the current adopted primary blend. This is a CPU-only priority screen; it does not establish eligibility for hidden-test use.

Source: Kaggle Discussion [756294](https://www.kaggle.com/competitions/name-that-llm/discussion/756294) and dataset [`antopil/ntl-oof-anto-pil`](https://www.kaggle.com/datasets/antopil/ntl-oof-anto-pil), version 1. Kaggle metadata describes four probability-only files over all 2,699 official train rows under CC BY 4.0. The author says the three LoRA files share one prompt-grouped five-fold split; the SVM uses GroupKFold on prompt_id in train.csv order. The exact training pools and external-prompt overlap checks are not independently documented, so keep provenance and leakage unresolved.

## Frozen comparison

- Align by exact official `id`, `prompt_id`, canonical 18 classes, and saved primary fold. Require all four datasets to match the saved primary GroupKFold assignment exactly; stop without scoring if any file is misaligned, missing, duplicated, nonfinite, negative, or has row-sum error above `1e-4`.
- Public family A: equal-probability mean of Anto's three LoRA files and SVM file. Family B: the already-registered equal-probability mean of Mistral-7B and OLMo-2 OOF files.
- Sole candidate under test: `0.5 * Family A + 0.5 * Family B`. Do not tune weights, temperatures, thresholds, class priors, or select a member using labels. Report member and family BA descriptively, but do not treat them as independent tests.
- Comparator: the current adopted Qwen3-8B + Qwen3-1.7B + prompt-centered SVC primary OOF on the exact same rows/folds.
- Report overall/fold BA, per-class recall, fixed candidate-minus-comparator BA, and at least 2,000 prompt-cluster paired bootstrap replicates with seed 42.

## Adoption boundary

Even a positive interval is only a prioritization signal. These predictions cannot support a Notebook or hidden-test blend until the local model/data recipes and all external prompt-overlap controls are identified and the corresponding candidates pass the approved local primary and independent confirmation gates. Existing queued Mistral/OLMo runs remain unchanged. Do not create or update any Kaggle object, Notebook, model, dataset, or submission for this screen.

## Execution

Read-only dataset download to `/tmp`, local OOF validation and CPU analysis only. Record exact dataset version, source file hashes, alignment checks, metrics and limitations in the paired dated experiment note. No changes to `/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm`.

## Preflight outcome

The exact-fold gate failed before any score was calculated: the three LoRA files are prompt-grouped but their fold partition differs from the saved primary split. The SVM file matches the saved split exactly. See the follow-up cross-fitted screen spec for a separately preregistered row-wise OOF comparison; no metric from this spec was computed.
