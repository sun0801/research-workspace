---
date: 2026-11-12
project: kaggle-name-that-llm
type: experiment
tags: [mistral, spectral, ensemble, prompt-grouped, cpu]
spec: ../specs/2026-11-12-mistral-spectral-complementarity-spec.md
---

# Mistral + Spectral fixed complementarity screen

## Question

Does the approved fixed 1/4 Mistral probability addition improve the frozen three-model Spectral primary OOF? This is a primary-only screen; Mistral was selected using primary OOF, so this is not independent confirmation or a Kaggle score.

## Frozen procedure and inputs

- Command: `/mnt/HDD10TB-2/aburatani/kaggle/.venv/bin/python scripts/evaluate_mistral_spectral_complementarity.py` from `/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm`.
- Runner: `scripts/evaluate_mistral_spectral_complementarity.py` (SHA-256 prefix `cfe33597`); it imports the unchanged Spectral transform and prompt clusterer. CPU only, one thread, saved primary OOF only; no model fitting, GPU, Kaggle writes, Notebook push, or submission.
- Fixed input probability: `(3 * baseline_probability + softmax(Mistral_logits)) / 4`. No weight fitting or scan.
- Inputs: official `data/train.csv`; `artifacts/cpu-qwen-prompt-centered-svc-probability-ensemble-v1/primary/`; `artifacts/gpu03-mistral-7b-v0-1-openpool-v15/primary/`; and the frozen `artifacts/cpu-spectral-cluster-meanfield-v1/primary-oof-postprocessed.parquet`.
- All 2,699 IDs, 150 prompts, labels, and 5 official folds aligned. Baseline and Mistral saved predictions were reproduced; all 2,699 original Spectral predictions reproduced exactly. Fold row counts: 540, 540, 540, 540, 539.
- Input integrity prefixes are in `artifacts/cpu-mistral-spectral-complementarity-screen-v1/summary.json`; no full hash is copied here.

## Results

- Raw three-model baseline BA: `.586408`.
- Raw fixed 1/4 Mistral addition BA: `.599769`.
- Existing three-model Spectral BA: `.664952` (reproduced exactly).
- Fixed Mistral addition followed by the unchanged Spectral transform: BA `.689791`, delta `+.024840` versus existing Spectral.
- 5,000 paired prompt bootstrap replicates, seed 42, versus existing Spectral: 95% CI `[+.013063, +.036412]`; lower bound is above zero.
- Fold BA, existing Spectral → Mistral+Spectral: fold0 `.646296 → .681481`; fold1 `.668519 → .681481`; fold2 `.685185 → .707407`; fold3 `.655556 → .675926`; fold4 `.669029 → .702490`.
- Primary class-recall diagnostic (not independent evidence): largest gains were `glm-5.3-flash` `.433 → .520`, `gpt-5.6-terra` `.600 → .680`, `claude-fable-5` `.369 → .436`, and `gemini-3.7-flash` `.533 → .593`. `glm-5.3` declined `.327 → .287`; inspect its confusion with `glm-5.3-flash` on the independent split before proposing any class-specific method.
- Class-retention simulations versus existing Spectral, 20 fixed seeds per condition: mild `.65–1.00` mean delta `+.021136`, positive in 20/20; moderate `.30–1.00` mean delta `+.021077`, positive in 20/20.
- Both primary screen gates pass. This authorizes consideration of an independent confirmation only; no Notebook or submission is authorized by this screen.

## Runtime and limitations

- CPU, one thread; wall time `70.456 s`, max RSS `243.7 MiB`.
- Two initial runner attempts stopped before evaluation because the implementation incorrectly expected `fold` in `train.csv`; corrected to use saved OOF fold assignments. The completed run passed alignment and exact Spectral reproduction.
- The positive result remains selection-biased primary evidence. Next decision is whether the fixed composition can be independently confirmed. Existing Mistral confirmation still requires a verified Host142 connection and a current-runner pilot; Host141 GPU2 belongs to another user's active job. Do not infer Host142 state from failed SSH host-key checks or move this run to Host141.

## Outputs

- `../../../../../../kaggle/name-that-llm/scripts/evaluate_mistral_spectral_complementarity.py`
- `../../../../../../kaggle/name-that-llm/artifacts/cpu-mistral-spectral-complementarity-screen-v1/summary.json`
- `../../../../../../kaggle/name-that-llm/artifacts/cpu-mistral-spectral-complementarity-screen-v1/primary-predictions.parquet`
