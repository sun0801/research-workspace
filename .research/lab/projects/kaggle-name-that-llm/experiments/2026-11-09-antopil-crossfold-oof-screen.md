---
date: 2026-11-09
project: kaggle-name-that-llm
spec: ../specs/2026-11-09-antopil-crossfold-oof-screen-spec.md
status: completed-priority-positive-provenance-unverified
tags: [experiment, public-oof, cross-validation, ensemble]
---

# Anto Pil cross-fold public OOF screen

## Question and fixed recipe

Does a frozen, family-balanced blend of Anto Pil's public OOF probabilities and the existing Mistral/OLMo OOF mean improve on the adopted Qwen3-8B + Qwen3-1.7B + prompt-centered SVC primary OOF?

The sole candidate was `0.5 * Family A + 0.5 * Family B`, where Family A is the equal-probability mean of Qwen3-14B LoRA, Qwen3-8B LoRA, Llama3-8B LoRA, and TF-IDF/SVM, and Family B is the existing equal-probability Mistral-7B/OLMo-2 mean. No weights or thresholds were tuned. The test was CPU-only and did not write to Kaggle.

## Source and integrity

Anto's public dataset [`antopil/ntl-oof-anto-pil`](https://www.kaggle.com/datasets/antopil/ntl-oof-anto-pil), version 1, is labeled CC BY 4.0 and contains four probability-only CSVs. The author describes prompt-grouped five-fold OOF for the three LoRAs and GroupKFold for the SVM. Predictions and the existing Mistral/OLMo files cover 2,699 official training rows and 18 classes.

A follow-up read of the author's [Discussion 756294](https://www.kaggle.com/competitions/name-that-llm/discussion/756294) says their three LoRA models used a two-stage recipe on an unspecified public pool. The author also described another contributor's pool-based pipeline as quite close to theirs. The discussion does not identify either pool version, training code, or prompt-overlap controls. This reinforces that the positive OOF screen is only a reproduction lead; it does not resolve contamination risk or support test inference.

| File | SHA-256 |
|---|---|
| `oof_llama3_8b_lora.csv` | `1cb17de22891db51d116c64fc1c7dfe771f30b95ecb34ec024f240a638c83db1` |
| `oof_qwen3_14b_lora.csv` | `58822e8d71d6b6ae1d77a3eb62a5f3a2d4f1757c239392d1b5d9e227646ab9e9` |
| `oof_qwen3_8b_lora.csv` | `5d8e1448ef30b8a7eac67a22bf6ad010a10a4b90bdde0d736be53abc1ccb07b5` |
| `oof_tfidf_svm.csv` | `eebb75135af1015af5d354661b839f5a8aa012f28dcdede7eb39b6f7fcf9d504` |
| `oof_mistral7b.csv` | `dbd5ed08420da4397e931f49495e3541799e0ea9e0a11dafe435599a962e3126` |
| `oof_olmo2_7b.csv` | `b5380b4183b2b929a20a9c0b6cda8e5e4b52444f06e9a86167312cef571679cb` |

All six files passed exact ID, prompt, class, uniqueness, finite/nonnegative probability, row-sum tolerance, and five-fold prompt-group checks. Each prompt is wholly assigned to one fold within each file. Fold membership is not identical across all components: the three LoRA files use a different prompt-group partition from the adopted reference split. Their row-wise predictions remain out-of-fold according to the author's stated grouped protocol; the fold contingency table (external LoRA folds 0–4 by reference folds 0–4) was:

```text
216  72 108 108  36
 72  90 126  90 162
 90  54 126 144 126
 72 162 108 108  90
 90 161  72  90 126
```

The exact-fold-equality preregistration was stopped before scoring in [the initial spec](../specs/2026-11-09-antopil-cross-stack-oof-screen-spec.md). The separate cross-fold spec above authorized this row-wise OOF analysis before any metric was inspected.

## Results

| Fixed output | Balanced accuracy |
|---|---:|
| Anto four-member Family A, descriptive | 0.646460 |
| Existing Mistral/OLMo Family B, descriptive | 0.602349 |
| Sole candidate: 50/50 family mean | **0.646068** |
| Adopted Qwen/SVC comparator | 0.586408 |

Individual OOF member BA (descriptive only):

| Member | Balanced accuracy |
|---|---:|
| Qwen3-14B LoRA | 0.634609 |
| Qwen3-8B LoRA | 0.614599 |
| Llama3-8B LoRA | 0.596818 |
| TF-IDF/SVM | 0.501931 |
| Mistral-7B | 0.586048 |
| OLMo-2-7B | 0.576406 |

Candidate minus comparator was `+0.059659` by point estimate. Prompt-cluster paired bootstrap (2,000 replicates, seed 42, existing `gpu_analyze.paired_prompt_bootstrap`) gave mean delta `+0.059588`, 95% interval `[+0.045185, +0.074099]`.

Reference-fold balanced accuracy, candidate / comparator:

| Fold | Candidate | Comparator |
|---:|---:|---:|
| 0 | 0.635185 | 0.564815 |
| 1 | 0.625926 | 0.583333 |
| 2 | 0.655556 | 0.594444 |
| 3 | 0.650000 | 0.585185 |
| 4 | 0.663665 | 0.604406 |

Candidate per-class recall (support, recall):

| Class | Support | Recall |
|---|---:|---:|
| claude-fable-5 | 149 | 0.382550 |
| claude-opus-4-6 | 150 | 0.866667 |
| claude-opus-4-8 | 150 | 0.660000 |
| claude-opus-5 | 150 | 0.853333 |
| claude-sonnet-5 | 150 | 0.740000 |
| gemini-3.1-pro-preview | 150 | 0.886667 |
| gemini-3.6-flash | 150 | 0.766667 |
| gemini-3.7-flash | 150 | 0.453333 |
| gemini-3.8-flash | 150 | 0.626667 |
| glm-5.3 | 150 | 0.326667 |
| glm-5.3-flash | 150 | 0.380000 |
| gpt-5.5 | 150 | 0.653333 |
| gpt-5.6-luna | 150 | 0.673333 |
| gpt-5.6-sol | 150 | 0.520000 |
| gpt-5.6-terra | 150 | 0.646667 |
| gpt-6-astra | 150 | 0.880000 |
| kimi-k3 | 150 | 0.540000 |
| qwen3.8-max | 150 | 0.773333 |

The fixed cross-stack candidate is `0.000393` below Family A alone, so this mix did not show added value from Mistral/OLMo. Qwen3-14B is the strongest individual public component in this screen. The already-registered local Qwen14B and Qwen8B confirmation work therefore remains relevant; the current GPU1 queue order is unchanged. A Llama reproduction would need a separate source/recipe and license audit before registration.

## Interpretation and limits

This is a priority-positive signal for local reproduction, not an adopted model or a hidden-test result. The public dataset does not establish the source models' training-pool versions, external-prompt overlap controls, or full recipes, and it provides no weights or training code. No exact public Notebook reproduction was located. The numerical advantage therefore may reflect unknown contamination or an irreproducible pipeline. Do not use these probabilities for test inference, create a Kaggle Notebook from them, or submit them. Local Qwen14B/Qwen8B and Mistral/OLMo candidates remain the appropriate next evidence; current runners and queues were not changed.

## Kaggle constraints refreshed 2026-11-09

Official Kaggle metadata lists 5,151 teams, at most five submissions per day, and a metadata deadline of Jan 14, 2027. The official Timeline page says Jan 13, 2027 at 23:59 UTC; use Jan 13 conservatively. Code Requirements remain Notebook-only, Internet disabled, runtime at most nine hours, and output `submission.parquet`. The public leaderboard top is tied at 0.752 (Le Viet and Meni David Gottesman), followed by 0.747. No Kaggle object or submission was created by this experiment.
