---
date: 2026-11-09
project: kaggle-name-that-llm
source: active-goal / Kaggle Discussion 756294
status: approved-under-active-goal
approval_basis: active-goal-2026-11-06-gpu-autonomous-first-place-spec
execution_status: completed-priority-positive-provenance-unverified
tags: [spec, oof, ensemble, prompt-grouped, public-data]
---

# Anto Pil cross-fold public OOF screen

## Rationale

The initial fixed screen required exact fold-label equality and stopped before scoring. Read-only validation found that the three Anto LoRA files use a different partition from the saved primary split, while each still assigns every prompt to exactly one of five folds; the SVM file exactly matches the saved split. Fold number equality is not required for row-wise OOF: every component prediction for a row is eligible for a grouped screen if that row's entire prompt group was excluded from that component's training fold. This protocol correction is made before inspecting any metric from these predictions. Public-pool overlap controls and source training details remain unverified, so results remain a priority signal only.

Source dataset: [`antopil/ntl-oof-anto-pil`](https://www.kaggle.com/datasets/antopil/ntl-oof-anto-pil), version 1, CC BY 4.0; four probability-only CSVs, 2,699 rows each. The author describes 5-fold prompt-grouped OOF for the three LoRAs and GroupKFold on prompt_id in train.csv order for the SVM.

## Frozen comparison

- Require exact `id`, `prompt_id`, all 18 canonical classes, unique 2,699 rows, finite nonnegative probabilities, row sums within `1e-4`, five nonempty fold IDs, and every prompt assigned to exactly one fold in every file. Verify the same rules for the existing Mistral/OLMo files and the adopted comparator OOF. Fold IDs and partition membership may differ across components; report the cross-fold contingency table, but do not relax the prompt-held-out requirement.
- Family A: equal-probability mean of Anto's Qwen3-14B LoRA, Qwen3-8B LoRA, Llama-3-8B LoRA, and TF-IDF SVM predictions.
- Family B: the already-screened fixed 50/50 Mistral-7B and OLMo-2 OOF mean.
- Sole candidate: `0.5 * Family A + 0.5 * Family B`. No weights, temperatures, thresholds, priors, or members may be tuned. Individual/family argmax BA is descriptive only.
- Comparator: current adopted Qwen3-8B + Qwen3-1.7B + prompt-centered SVC primary OOF. Join one-to-one by exact ID and verify labels and prompt IDs; each compared prediction must itself be out-of-fold with the full prompt group held out.
- Report overall/fold BA, per-class recall, paired candidate-minus-comparator delta, and at least 2,000 prompt-cluster paired bootstrap replicates with seed 42 using the existing `gpu_analyze.paired_prompt_bootstrap` implementation.

## Adoption boundary

A positive interval is only a prioritization signal. The third-party training recipe and possible public-pool prompt overlap are unknown. Do not use these predictions for hidden-test inference or a Kaggle Notebook. Any promising architecture must be reproduced locally on the registered primary and independent confirmation splits. Do not alter existing runners or queue.

## Execution

Download only the CC BY 4.0 prediction CSVs to `/tmp`; CPU-only alignment and fixed analysis. Record exact version, hashes, split-validity checks, metrics and provenance limits in `experiments/2026-11-09-antopil-crossfold-oof-screen.md`. No edits to the external implementation repository and no Kaggle writes.

## Outcome

The frozen candidate scored BA `0.646068` versus adopted comparator `0.586408`; prompt-cluster paired bootstrap delta was `+0.059588` (95% CI `[+0.045185, +0.074099]`, 2,000 replicates, seed 42). This is a priority-positive screen only. Unknown training-pool overlap and unavailable source recipe/weights prevent adoption or hidden-test use. Full alignment, per-fold and per-class results are in the experiment note.
