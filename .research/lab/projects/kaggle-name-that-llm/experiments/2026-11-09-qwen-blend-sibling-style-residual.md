---
date: 2026-11-09
project: kaggle-name-that-llm
spec: ../specs/2026-11-09-qwen-blend-sibling-style-residual-spec.md
status: rejected-primary
tags: [experiment, postprocessing, sibling-style, cpu, prompt-grouped]
---

# Qwen blend sibling-style residual primary screen

## Fixed candidate and inputs

Independently implemented only the fixed family-local style residual from Areeb Ali's public Notebook v2; did not use its aggregate ensemble, external weights/data, A/B annotation dataset, shared-prompt Gaussian, inferred prompt clusters, Sinkhorn, or Hungarian assignment. The residual trains style-only logistic heads inside the outer training folds, estimates each head's reliability on 5-fold `GroupKFold(prompt_id)` OOF, and mixes at most 0.10 into uncertain sibling-class probabilities while preserving the original provider-family mass.

Input baseline: adopted Qwen3-8B + Qwen3-1.7B + prompt-centered SVC primary OOF, 2,699 rows / 150 prompts. The saved probabilities reproduced the baseline `prediction` on all rows before the candidate was scored. `prompt_id` was used only for inner grouped training diagnostics and the canonical paired bootstrap; it was not a prediction feature or validation-row routing signal. All 20 outer/inner/final logistic heads converged.

## Result

| Metric | Result |
|---|---:|
| Baseline balanced accuracy | 0.586408 |
| Candidate balanced accuracy | 0.587146 |
| Delta | +0.000738 |
| Prompt-paired bootstrap (5,000, seed 42) 95% CI | [-0.002618, +0.004442] |
| Bootstrap mean delta | +0.000749 |
| Changed predictions | 31 / 2,699 |

Fold BA deltas were `−0.007407`, `0`, `+0.011111`, `+0.001852`, and `−0.001852`. The family-mass conservation maximum absolute error was below `8e-9` for all four families; non-family probabilities were unchanged. Thus the small positive point estimate does not pass the preregistered gate: CI lower bound is below zero. Reject for this current Qwen blend and skip confirmation. No parameter, family, or fold selection followed the result.

## Resources, artifacts, and provenance

- CPU-only runtime: 58.21 seconds; two-thread native threadpool limit.
- Peak RSS: 255,901,696 bytes; minimum observed host `MemAvailable`: 216,681,050,112 bytes. Both preregistered resource floors passed.
- Runner: `/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/src/evaluate_qwen_blend_sibling_style_residual.py`, SHA-256 `852fd0569e7d9368f00786132b025b6137026b008b001fdb610b0143b08a2b2f`.
- Artifacts: `/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/artifacts/cpu-qwen-blend-sibling-style-residual-v1/`. The `summary.json` preserves all input hashes and hyperparameters. Summary SHA-256: `86cb7a696b4f8884ccb74da4846e707030cd8d2dca30625ce4efca5d1e78b2da`; OOF prediction SHA-256: `b690413acc31bfbf06af2994d18a46729f7d4693182fcf5aba4b1f9a46a8e8b0`.
- Exact command: `.venv/bin/python -u src/evaluate_qwen_blend_sibling_style_residual.py` from the external project root.
- Existing OOF/base artifacts were read-only. No GPU, Kaggle object, Notebook, or submission was used or changed.

## Decision and next step

The public residual is not adopted and receives no confirmation run. Its small gain is within sampling uncertainty, consistent with the earlier old-SVC residual screen that also failed its primary gate. Keep the active Qwen04/Qwen8B confirmation jobs untouched; the next registered step remains the frozen Spectral mean-field confirmation after both component OOFs are complete. The source audit is [Areeb v2 audit](2026-11-09-areeb-0-673-notebook-audit.md).
