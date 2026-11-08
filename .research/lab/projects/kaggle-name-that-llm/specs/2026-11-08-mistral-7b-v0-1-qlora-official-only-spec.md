---
date: 2026-11-08
project: kaggle-name-that-llm
source: autonomous-goal
status: approved
execution_status: preregistered-pilot-pending
approval_basis: active-goal-2026-11-06-gpu-autonomous-first-place-spec
tags: [spec, experiment, qlora, mistral, prompt-grouped]
---

# Mistral-7B-v0.1 NF4 QLoRA official-train-only candidate

## Purpose and evidence

Measure whether Mistral-7B-v0.1's representation can classify the official 18 model labels from unseen prompts when directly fine-tuned on each fold's official training rows. This is a separate, small-data ablation from the approved two-stage Open Pool candidate03. It tests the Mistral backbone and the host141-compatible NF4 QLoRA path without importing external OOF scores or pool passages.

The public discussion author reports Mistral-7B OOF BA `.586` and an approximately `+.004` gain when blending Mistral+OLMo with a different team stack on held-out prompts; these are participant reports, not independent evidence or the expected score for this method. The public current leaderboard top is `.752`; this candidate advances only if its own prompt-grouped OOF passes the registered comparator gate. [Discussion 756294](https://www.kaggle.com/competitions/name-that-llm/discussion/756294)

This candidate is authorized by the active autonomous goal and its launch-time implementation approval. It does not alter candidate03, candidate02/Qwen02, candidate04/Qwen04, or their configs, runs, checkpoints, or GPU allocation.

## Fixed method and implementation scope

- Reuse the already audited, architecture-generic `src/gpu_qwen14b_qlora.py`. Permit one candidate-neutral correctness fix before the pilot: derive the pilot's projected OOF optimizer-update count from configured `micro_batch_size` instead of a hard-coded value of 2. The current fixed value underestimates this candidate's OOF time by about 2x at batch size 1, so its runtime gate would be invalid. Record the resulting runner hash in all pilot and OOF identities. No training, checkpoint, or prediction behavior may otherwise change. A CPU-only structural check with Transformers 4.57.1 confirmed Mistral's `score` classifier is a Linear layer with 18 outputs and all seven configured LoRA projection names exist.
- New external config: `/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/configs/gpu10-mistral-7b-v0-1-qlora-official-only.json`. Candidate-specific run outputs go under `artifacts/gpu10-mistral-7b-v0-1-qlora-official-only/`.
- Model: Kaggle's public `mistral-ai/mistral/PyTorch/7b-v0.1-hf` version 1, Apache-2.0, with the already verified local revision `mistralai/Mistral-7B-v0.1@27d67f1b5f57dc0953326b2601d68371d40ea8da`. Use its 4-bit NF4 double-quantized weights with FP16 compute. Do not use generated text, the Open Pool, third-party adapters, public OOF predictions, or test labels.
- Foldwise official-train-only QLoRA: 18 labels, 512-token truncation, rank 16/alpha 32/dropout .05, targets `q_proj`, `k_proj`, `v_proj`, `o_proj`, `gate_proj`, `up_proj`, and `down_proj`, `score` as the only saved classification head, one epoch, batch 1 with gradient accumulation 16, 8-bit AdamW, seed 42. Pilot and full run use identical settings.
- Primary uses the saved official prompt GroupKFold assignment, unchanged. Confirmation uses the already registered independent `blend-confirm` prompt GroupKFold assignment (seed 271828) shared with the adopted SVC comparator. Require 2,699 unique IDs, all 150 prompt groups, exactly one OOF prediction per row, matching labels/folds, finite logits, and one fold per prompt.
- Compare raw argmax OOF against adopted prompt-centered low-pool SVC on identical IDs/folds. Run at least 5,000 prompt-paired bootstrap replicates, seed 42. Continue to confirmation only if the primary 95% CI lower bound for BA delta is above zero; adopt only if the confirmation lower bound is also above zero. No split-specific temperature, class prior, Sinkhorn, or post-hoc class adjustment is part of this candidate.

## GPU, runtime, and safety gates

- Target only host141 GPU2 UUID `GPU-48a73ba5-62ab-e9ff-b15b-e4eceae66c58` (RTX A4000, 16 GiB). At the 2026-11-08 11:00 JST recheck, GPU2 was idle with 15,960 MiB free; other GPUs were not assigned to this candidate, MemAvailable was 118.1 GiB, and the host filesystem had 6.9 TiB free. Recheck UUID, all compute PIDs, free VRAM, host RAM, disk space, and the shared runner lock immediately before pilot. Use a candidate-specific lock; do not stop or modify other processes.
- Reserve at least 4,096 MiB VRAM and keep host MemAvailable >=16 GiB. Pilot must load the exact model/config, run finite forward/backward/gradient/optimizer steps, record peak VRAM and RAM, and pass the runtime projection. The existing runner does not save or reload checkpoints during pilot; checkpoint save/resume is exercised by the full OOF runner and must remain identity-checked. On pilot failure, OOM, or safety-floor breach, do not start full OOF.
- Use the dedicated dependency pin `bitsandbytes==0.50.2` with the existing host141 environment (PyTorch 2.9.0+cu128, Transformers 4.57.1, PEFT 0.17.1); capture the complete environment lock. The official bitsandbytes guide supports NF4 on NVIDIA compute capability 6.0+ and current CUDA 12.8 builds include SM86, which matches the A4000. [Official installation guide](https://huggingface.co/docs/bitsandbytes/main/en/installation)
- Full OOF is detached/resumable with candidate-only checkpoints and a 10-minute resource watcher that terminates only this runner if the registered floor is breached. Proceed only if the measured pilot projects under 8 hours for the full offline Notebook test inference (one-hour margin under Kaggle's 9-hour cap).
- No Kaggle Model, Dataset, Notebook, or Submission is created by this spec. Any later Notebook consideration requires both OOF gates, a final fit, offline/runtime/license checks, private-only objects, and a fresh review of the current leaderboard and submission limits.

## Stop and result handling

If primary fails, skip confirmation and preserve its OOF and pilot records. If confirmation fails, preserve both splits and reject. If both pass, retain this as an OOF-validated member for later nested ensemble evaluation; do not claim a leaderboard improvement before a valid Kaggle Notebook submission. Record config/runner/model hashes, split hashes, resource samples, commands, metrics, bootstrap intervals, and stop/resume location in the experiment log.

## Related records

- [Two-stage Mistral-7B Open Pool spec](2026-11-08-mistral-7b-v0-1-prompt-grouped-spec.md)
- [Qwen3-14B QLoRA reference spec](2026-11-08-qwen3-14b-qlora-prompt-grouped-spec.md)
- [Public-LB goal spec](2026-11-06-gpu-autonomous-first-place-spec.md)
- [Experiment log](../experiments/2026-11-06-gpu-autonomous-initial-check.md)
