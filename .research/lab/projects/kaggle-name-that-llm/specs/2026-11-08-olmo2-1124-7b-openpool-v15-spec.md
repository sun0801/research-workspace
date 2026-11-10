---
date: 2026-11-08
project: kaggle-name-that-llm
source: active-goal / public Mistral-OLMo OOF screen
status: approved-under-active-goal
execution_status: config-prepared-queued-behind-host142-gpu1-chain
tags: [spec, experiment, gpu, olmo, prompt-grouped]
---

# OLMo 2 1124 7B + Open Pool v15 prompt-grouped evaluation

## Purpose and evidence

The fixed public OOF screen found that equal-probability Mistral-7B-v0.1 + OLMo-2-1124-7B predictions scored BA `0.602349` (`+0.015941` vs. the current Qwen8B + Qwen1.7B + prompt-centered SVC blend; prompt-paired 95% CI `[+0.001126, +0.030741]`). This is only a candidate-priority signal: the OOF publisher does not document all model/pool revisions or its prompt-leakage controls. Local foldwise training on a known, public pool is needed before using an OLMo member.

Use the official [AllenAI OLMo 2 / Transformers / 1124-7b](https://www.kaggle.com/models/allenai/olmo-2/transformers/1124-7b) version 1 (`version_id=202589`). Official Kaggle model metadata reports Apache-2.0, 7B parameters, 32 layers, hidden size 4096, and training sources OLMo-Mix-1124, Dolmino-Mix-1124, and Tulu 3 post-training. The six published weight shards total 29,194,510,544 bytes. Train only on official competition folds plus the public/free [Open Pool v15](https://www.kaggle.com/datasets/crtproduction/name-that-llm-open-pool) (CC BY-SA 4.0); do not use the external OOF files as training labels or features.

Compatibility was read-only inspected in the existing implementation environment (Transformers 4.57.1): `AutoConfig` resolves `Olmo2Config`, `AutoModel` resolves `Olmo2Model`, and a tiny random config exposes the expected `layers.N.self_attn.{q,k,v,o}_proj` and `layers.N.mlp.{gate,up,down}_proj` module names used by the generic runner's LoRA target pattern. No official weights have been downloaded and no full model load or pilot has run. After this spec was registered, its candidate-specific config was prepared without changing the generic runner or launching a job; see the config path and hash recorded below and in the experiment log.

## Fixed candidate and scope

- Candidate ID: `gpu14-olmo2-1124-7b-openpool-v15`.
- Implementation path: `/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/configs/gpu14-olmo2-1124-7b-openpool-v15.json`; reuse the generic `src/gpu_experiment.py` without editing it unless preflight identifies a concrete incompatibility. Run artifacts go under `artifacts/gpu14-olmo2-1124-7b-openpool-v15/` and remain outside Git.
- Prepared config SHA-256: `ad2f29ab59c9778d16048f2100c99e7d855635938add4d5d822e47d7b15a556b`. It is preregistered, not run. The generic runner's static config validator passed before any pilot.
- Load the official version 1 model in BF16 with `AutoModel`, local files only. Use the existing pooled-layer classifier head and first 24 of 32 transformer layers for LoRA, rank 16, alpha 32, dropout 0.05, pooled layers `[2,4,6,8,12,16,20,24]`, max length 384, and gradient checkpointing.
- Use the registered Open Pool v15 preparation: up to 2,500 rows per label, seed 42; exclude normalized exact training-text matches and, independently per validation fold, external rows matching reconstructed validation prompts at the registered char/word TF-IDF cosine threshold `0.40`; log prompt groups and rows removed. Do not use publisher-generated `match_weight` in OOF.
- Stage 1: one epoch on the filtered external pool, AdamW, LoRA LR `1e-4`, head LR `1e-3`, cosine schedule, warmup ratio `0.1`. Stage 2: two epochs on only that fold's official training rows, LoRA LR `5e-5`, head LR `5e-4`, same optimizer/schedule. Microbatch 1, effective batch 18, seed 42. Preserve candidate-specific identity-checked checkpoints and resume state.
- Primary: saved official `GroupKFold(prompt_id, n_splits=5)` unchanged. Compare raw argmax OOF against the current adopted primary Qwen8B + Qwen1.7B + prompt-centered SVC blend on exact matching IDs/folds. Report overall BA, fold BA, per-class recall, confusion matrix, and prompt-paired bootstrap (at least 2,000 replicates, seed 42). No coefficient, threshold, temperature, or test-derived tuning.
- If local Mistral candidate03 primary OOF is complete with identical IDs and folds, additionally report its fixed 50/50 probability mean with OLMo as a separately labeled, preregistered diagnostic matching the public OOF claim. Do not use that blend for adoption unless Mistral itself has passed its registered primary and confirmation gates; do not tune its weight.
- Continue to the independent confirmation `GroupKFold(prompt_id, n_splits=5, shuffle=True, random_state=42)` only if the standalone OLMo primary 95% BA-difference CI lower bound is positive. This is the split constructed by the generic runner and used by the active Qwen02/Qwen04 confirmation runs. Existing Qwen02 and Qwen04 `confirmation-folds.parquet` files and the current SVC confirmation OOF have exact matching `(id,prompt_id,fold)` assignments. The candidate must use this same assignment and compare against the completed Qwen8B + Qwen1.7B + SVC confirmation blend; do not analyze confirmation until that comparator artifact exists. Adopt the standalone member only if the same confirmation gate passes. A positive Mistral/OLMo secondary blend alone does not bypass either model's independent validation gates.

## Queue and resource gates

- Target Host142 GPU1 UUID `GPU-8a059266-7ede-0427-ff30-08ba7a9b5224` (RTX PRO 4500 Blackwell, 32 GiB). The 2026-11-08 21:10 JST poll confirms this GPU is occupied by the Qwen8B confirmation run and its registered queue remains active. Candidate14 stays after the existing Host142 GPU1 chain through candidate09; do not add a watcher or launch a download/run while waiting. Start only after that chain's exact job/watcher handles are terminal, the shared run lock is free, and two fresh resource snapshots show the same UUID and no conflicting compute process.
- Before any model download/pilot/full run, re-run `.agents/skills/kaggle-workflow/scripts/codex_rate_limit.py --guard 15`. Require exit 0, available host MemAvailable >=16 GiB, >=4,096 MiB free VRAM above the runner's measured peak/reserve, and sufficient disk for the 29.2 GB published model plus checkpoints. Recheck the exact UUID, all compute PIDs, free VRAM, RAM, disk and lock immediately before each start. Never stop or alter another process.
- The first run must be an exact-version pilot that loads official weights/tokenizer locally, exercises forward/backward/optimizer-step with finite outputs, and records peak VRAM/RAM and speed. The generic runner pilot does not save/reload checkpoints; verify its identity-checked checkpoint path during the first completed OOF fold and resume only from its recorded `latest.json` if a later restart is needed. Do not start primary OOF if pilot fails, violates reserves, or projects full offline hidden-test inference to 8 hours or more (one-hour margin below Kaggle's 9-hour Notebook limit).
- Poll long jobs at the registered 10-minute cadence. Do not restart based only on quiet logs; save and record checkpoint/resume positions and candidate-only termination if a safety floor is breached.

## Kaggle and completion constraints

- Current official metadata says at most 5 submissions/day; official Rules allow at most 2 final submissions. Timeline gives Jan 13, 2027 23:59 UTC, earlier than metadata's Jan 14 date; use Jan 13 conservatively. Notebook-only, Internet disabled, CPU/GPU <=9 hours, required file `submission.parquet`. Reconfirm all before any Kaggle object or submission.
- This candidate creates no Kaggle object or submission. Any later candidate inclusion is private-only and requires both OOF gates, full-test offline inference/runtime validation, and a fresh official rules/leaderboard/quota check. Preserve the existing CPU best artifact and all active Host141/142 jobs.
