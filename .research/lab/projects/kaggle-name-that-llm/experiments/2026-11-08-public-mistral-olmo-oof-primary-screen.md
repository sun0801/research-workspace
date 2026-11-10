---
date: 2026-11-08
project: kaggle-name-that-llm
type: experiment
status: primary-screen-complete-positive-provenance-unverified
spec: ../specs/2026-11-08-public-mistral-olmo-oof-primary-screen-spec.md
tags: [oof, ensemble, prompt-grouped, public-data]
---

# Public Mistral/OLMo OOF primary screen

## 2026-11-08 21:43 JST Kaggle notebook follow-up

Official Kaggle MCP inspection of [`lightningv08/0-680-modernbert-lora-sparse-ensemble`](https://www.kaggle.com/code/lightningv08/0-680-modernbert-lora-sparse-ensemble) identifies a different/current notebook version63 (257 votes; metadata last run 2026-11-05 12:43 UTC) from the earlier version12 lead logged below. Its visible description combines five prompt-fold Qwen3-Embedding-8B classifiers (40% geometric mixture mass) with a cited `.666` public parent and a 3% Qwen3.8-27B branch. It depends on 21 dataset sources, 8 notebook sources and six model versions. `.680` appears in the notebook title; metadata does not independently attest to that score. The approach overlaps the queued candidate08, and the artifact-heavy parent stack is not directly reproducible from the local candidate spec. This inspection does not warrant reordering, a new run or importing any artifacts. No Kaggle write/submission.

## Setup and validation

- Spec: [fixed primary screen](../specs/2026-11-08-public-mistral-olmo-oof-primary-screen-spec.md). CPU-only analysis; no GPU job, Kaggle write, Notebook, or submission.
- Source: Kaggle dataset `emmanuelocheme/ntl-oof-mistral-olmo-lora`, version 1 (CC0), downloaded through the official Kaggle CLI. Source discussion: [Name That LLM discussion 756294](https://www.kaggle.com/competitions/name-that-llm/discussion/756294).
- `oof_mistral7b.csv` SHA-256: `dbd5ed08420da4397e931f49495e3541799e0ea9e0a11dafe435599a962e3126`.
- `oof_olmo2_7b.csv` SHA-256: `b5380b4183b2b929a20a9c0b6cda8e5e4b52444f06e9a86167312cef571679cb`.
- Both files contain 2,699 rows, all 2,699 official IDs exactly once, 18 canonical class-probability columns, and 150 prompt groups. `id`, `prompt_id`, and saved primary GroupKFold membership match the official train data exactly. Values are finite and nonnegative; maximum row-sum errors are `4e-6` (Mistral) and `5e-6` (OLMo), within the registered `1e-4` tolerance.
- Recomputed individual BA matches the source's rounded claims: Mistral `0.5860477`, OLMo `0.5764057`. Candidate is their fixed 50/50 probability mean; no weights, temperature, or thresholds were tuned. Comparator is the existing primary Qwen3-8B + Qwen3-1.7B + prompt-centered SVC equal-probability blend (`0.5864081531`).

## Primary results

| OOF candidate | Balanced accuracy | Delta vs. current blend |
|---|---:|---:|
| Mistral-7B-v0.1 | 0.5860477 | -0.0003605 |
| OLMo-2-1124-7B | 0.5764057 | -0.0100025 |
| Fixed 50/50 Mistral + OLMo | **0.6023490** | **+0.0159408** |
| Current Qwen8B + Qwen1.7B + prompt-SVC | 0.5864082 | reference |

Fold BA, candidate versus current blend: fold 0 `0.58889 / 0.56481`; fold 1 `0.58148 / 0.58333`; fold 2 `0.60556 / 0.59444`; fold 3 `0.62407 / 0.58519`; fold 4 `0.61162 / 0.60441`.

The registered 2,000-replicate prompt-cluster paired bootstrap (seed 42, existing `paired_prompt_bootstrap` implementation) gives a 95% CI for candidate-minus-comparator of `[+0.0011260, +0.0307410]`. Its fixed primary screen is positive.

Per-class recall for the fixed Mistral/OLMo mean (macro average `0.602349`; comparator recalls are the saved Qwen blend `class-recall.csv` candidate column):

| Class | Mistral/OLMo | Current blend |
|---|---:|---:|
| `gpt-5.5` | 0.593333 | 0.613333 |
| `gpt-5.6-luna` | 0.640000 | 0.520000 |
| `gpt-5.6-sol` | 0.440000 | 0.453333 |
| `gpt-5.6-terra` | 0.533333 | 0.453333 |
| `gpt-6-astra` | 0.826667 | 0.813333 |
| `gemini-3.1-pro-preview` | 0.820000 | 0.840000 |
| `gemini-3.6-flash` | 0.666667 | 0.646667 |
| `gemini-3.7-flash` | 0.453333 | 0.380000 |
| `gemini-3.8-flash` | 0.620000 | 0.653333 |
| `claude-opus-4-6` | 0.820000 | 0.806667 |
| `claude-opus-4-8` | 0.593333 | 0.673333 |
| `claude-opus-5` | 0.826667 | 0.820000 |
| `claude-sonnet-5` | 0.706667 | 0.673333 |
| `claude-fable-5` | 0.342282 | 0.302013 |
| `qwen3.8-max` | 0.713333 | 0.786667 |
| `glm-5.3` | 0.326667 | 0.313333 |
| `glm-5.3-flash` | 0.400000 | 0.360000 |
| `kimi-k3` | 0.520000 | 0.446667 |

## Interpretation and next step

This is a priority signal, not adoption or final evidence. The public source says it used five-fold GroupKFold by `prompt_id`; exact row/fold alignment is verified, but the external training-pool contents, model revisions, and prompt-leakage controls are not documented enough to establish eligible, independent predictions. Candidate03 already covers a local Mistral reproduction. Preserve its queued run and compare after its OOF completes. Do not start OLMo training until its official model/license/data provenance is verified and a separate preregistered spec is approved. No GPU slot was available at the latest 21:00 JST poll, so no run or queue was changed.

Official Kaggle Models MCP follow-up confirms a feasible named OLMo source: [AllenAI OLMo 2 / Transformers / 1124-7b](https://www.kaggle.com/models/allenai/olmo-2/transformers/1124-7b), version 1 (`version_id=202589`). The publisher metadata identifies the model license as Apache 2.0 and describes OLMo 2 7B pretraining on OLMo-Mix-1124 and Dolmino-Mix-1124, with Tulu 3 SFT/DPO/PPO post-training. The version file listing contains six safetensors shards totaling 29,194,510,544 bytes. In the existing Transformers 4.57.1 environment, read-only inspection confirms `Olmo2Config` maps to `Olmo2Model`, and a tiny random config exposes all seven module names expected by the generic LoRA target pattern. This is architecture compatibility evidence only: no official weights were loaded and no GPU pilot ran. It does not identify the exact base/model version or pool used to create the released OOF CSVs; that remains a material limitation. A queued local candidate spec now records the next exact validation and resource gates.
