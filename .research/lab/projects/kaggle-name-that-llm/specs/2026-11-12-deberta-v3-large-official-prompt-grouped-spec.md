---
date: 2026-11-12
project: kaggle-name-that-llm
source: active-goal / official DeBERTa-v3-large weights
status: approved-under-active-goal
approval_basis: 2026-11-06-gpu-autonomous-first-place-spec
execution_status: primary-rejected
tags: [spec, experiment, gpu, deberta-v3-large, prompt-grouped]
---

# DeBERTa-v3-large official-base prompt-grouped OOF

## Purpose and candidate decision

Test a clean fold-local DeBERTa-v3-large classifier as a possible source of complementary author-style signal. A public Notebook claims `.747` OOF for a large DeBERTa branch, but its supplied dependency was trained on the full competition training set and its OOF provenance is unresolved; none of that checkpoint or the claimed score is used as evidence. The only starting point is the unmodified Microsoft model mirror below. A local DeBERTa-v3-small full-finetune was rejected on its primary gate (`.290050` BA versus `.501934` for the prompt-centered SVC), so the large model is a separate, explicitly exploratory scale hypothesis, not an assumed improvement.

## Immutable source and implementation scope

- Kaggle model: [`illuminatep/deberta-v3-plain/Transformers/large/1`](https://www.kaggle.com/models/illuminatep/deberta-v3-plain/Transformers/large). Official Kaggle model metadata says the weights are unmodified `microsoft/deberta-v3-large`, MIT license, 434.0M parameters, 24 layers, hidden size 1024; version 1 has a 1,736,094,384-byte `model.safetensors`, SentencePiece model, tokenizer JSON/config, and model config. Pin this exact version and verify all files after download.
- New config: `/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/configs/gpu16-deberta-v3-large-official-prompt-grouped.json`. Run artifacts: `/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/artifacts/gpu16-deberta-v3-large-official-prompt-grouped/`; model cache is the existing `artifacts/model-cache/` convention. Preserve the DeBERTa-small run and all existing OOF artifacts.
- Reuse the existing `src/deberta_experiment.py` architecture and append configurable gradient accumulation with default `1` so old configs retain their behavior. Do not change other runners or the registered folds. Candidate config pins microbatch 2, gradient accumulation 4 (effective batch 8), evaluation batch 2, three epochs, AdamW LR `2e-5`, weight decay `.01`, max length 384, gradient checkpointing, multi-sample dropout `[.1,.2,.3,.4,.5]`, BF16 autocast, seed 42 plus fold. Fully train the backbone and 18-class head on each fold's training rows. Use no extra passages, labels, checkpoints, or fitted adapters.

## Validation and advancement gates

- Primary split is the saved five-fold `GroupKFold(prompt_id)` assignment in `artifacts/2026-11-06-cpu-cycle/folds.parquet`. Confirmation is the registered `GroupKFold(prompt_id, n_splits=5, shuffle=True, random_state=42)` split matching the active Mistral+Spectral confirmation procedure. Save the exact IDs, prompts, and fold assignments and verify every prompt belongs to one fold. Reinitialize the classification head per fold; all trained parameters and preprocessing are fold-local.
- First compare standalone DeBERTa OOF against the adopted Qwen3-8B + Qwen3-1.7B + prompt-centered SVC raw primary. Also run one preregistered fixed equal-member addition `(3 * baseline_probabilities + softmax(DeBERTa_logits)) / 4`; no blend/temperature/threshold scan. Apply the unchanged Spectral mean-field transform within each held-out fold to both the fixed addition and baseline, and compare fixed-addition-plus-Spectral with saved three-member Spectral OOF. Report BA, per-fold BA, per-class recall, exact OOF coverage, and 5,000 paired prompt-bootstrap replicates (seed 42).
- Repeat the fixed mild (`.65–1.00`) and moderate (`.30–1.00`) class-retention simulations with 20 seeds each. No tuning from primary. Advance only if the candidate-plus-Spectral paired 95% CI lower bound is strictly above zero and both simulation means are positive with at least 60% positive replicates. Otherwise record rejection and stop this candidate.
- If primary passes, produce independent confirmation OOF on the pinned confirmation split and compare against the saved Spectral confirmation output with the same fixed formula and gates. A primary pass is not submission approval. If confirmation passes, compare the measured result with current Public Leaderboard `.768` and the single v12 CV-LB reference (primary `.586408`, Public `.541`) before deciding whether to prepare a private Notebook. Any push or submission needs a fresh official/private/quota/runtime gate.

## Resource gates and run operation

- Target only Host141 GPU1, RTX A4000 UUID `GPU-51b57ca0-53ca-3266-7105-efc692a6c834`. Do not move Host142-pinned Mistral/Qwen/OLMo candidates. Before download/pilot/full fold, pass `.agents/skills/kaggle-workflow/scripts/codex_rate_limit.py --guard 15`; require two consistent resource snapshots, no conflicting compute PID/lock, `MemAvailable >= 16 GiB`, and the exact target UUID. Pilot peak plus subsequent estimate must fit free VRAM after reserving `max(4 GiB, 25% of total VRAM)` per the parent spec. Check disk for the 1.75 GB model and checkpoints.
- The first run must be an isolated 8-row optimizer-step pilot with finite loss/gradients, full-model loading, checkpointing enabled, and peak VRAM/RAM/time recorded. Start no fold unless the exact-config/current-runner pilot passes. Stop on OOM/safety breach; at most one retry after a concrete, recorded safe adjustment, never by overlapping another GPU.
- Run detached with candidate-only logs/checkpoints and a precise resume command. Poll every 30 minutes with one light command and record only state changes. No Kaggle object, push, or submission during this OOF screen.
- 2026-11-12: official model cache and runner/config synchronized to Host141; all manifests verified with `sha256sum -c` (model prefix `7b9a354d`, runner `b42fbacc`, config `cc762171`). Attempt 1 exposed a Transformers 4.57.1 tokenizer-config type incompatibility before GPU work; explicit empty `extra_special_tokens` mapping preserved standard token IDs and the single retry passed. Eight-row pilot peak was 8,301 MiB; adding a 512 MiB transient estimate and 4,096 MiB reserve requires 12,909 MiB of 15,958 MiB free. Details: [pilot and primary log](../experiments/2026-11-12-deberta-v3-large-pilot-primary.md).
