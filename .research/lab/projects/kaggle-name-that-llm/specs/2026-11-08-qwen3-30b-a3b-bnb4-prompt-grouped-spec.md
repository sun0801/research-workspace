---
date: 2026-11-08
project: kaggle-name-that-llm
source: autonomous-goal
status: approved
execution_status: pilot-failed-vram-reserve
tags: [spec, experiment, gpu, qwen3, mixture-of-experts, prompt-grouped]
---

# Qwen3-30B-A3B-Base NF4 frozen-feature candidate

## Hypothesis and motivation

A frozen Qwen3-30B-A3B-Base representation may separate model-writing styles more strongly than the current 8B and 1.7B candidates. This is a targeted follow-up to the public discussion by the new leaderboard leader, Meni David Gottesman, asking about throughput for a roughly 30B MoE model on 2xT4. The discussion is a public question, not evidence that the leader used this model or achieved a specific score. Current public top is 0.751.

Use the official Qwen3-30B-A3B-Base checkpoint, loaded in 4-bit NF4 at inference time, and fit a small supervised readout on official training rows only. Do not use generated text, third-party adapters, external OOF predictions, or test-set labels. The candidate is complementary to the existing post-trained Qwen LoRA runs.

## Exact model and environment

- Official Kaggle Model input: [`qwen-lm/qwen-3/Transformers/30b-a3b-base`, version 1](https://www.kaggle.com/models/qwen-lm/qwen-3/Transformers/30b-a3b-base). Kaggle metadata lists Apache 2.0 and 61,079,769,470 uncompressed bytes. The official model card describes 30.5B total / 3.3B active parameters, 48 layers, and Qwen3-MoE support in Transformers 4.51.0 or newer.
- Load with `AutoModel` and Transformers `BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_use_double_quant=True, bnb_4bit_compute_dtype=torch.float16)`. Pin `bitsandbytes==0.50.2`, Torch 2.9.0, Transformers 4.57.1, Accelerate 1.10.1, Python 3.12, and the Kaggle Model version in the candidate-only lock/config. The current runner environment has Torch 2.9.0+CUDA 12.8 / Transformers 4.57.1 / Accelerate 1.10.1 but no bitsandbytes installation; the pilot must verify the package and kernels on the actual selected GPU.
- Prefer this official base checkpoint over the surfaced community AWQ fork: the fork is ~16.8 GB and lists Apache 2.0, but its Kaggle model description is empty, while AutoAWQ is archived/deprecated and was last tested with older Torch/Transformers. Do not switch to AWQ or another quantization in this experiment; a switch requires a separate preregistered candidate.
- The official Qwen3-30B-A3B-Base files are about 61 GB on disk; load from the attached Kaggle Model input for Notebook inference. Do not copy model weights into the source repository or upload new public artifacts.

## Scope and frozen protocol

- Add a candidate-specific inference/embedding runner, config, and dependency lock under `/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/`. Do not alter the active Qwen02/Qwen04 runners or their artifacts, the adopted CPU SVC, or any other project files.
- The model stays frozen and processes only the official `text` column, with the tokenizer's ordinary model input formatting, truncation at 384 tokens, and no chat prompt. Extract the final-layer masked mean of `last_hidden_state` for each passage. Do not use `prompt_id`, label, or other passage embeddings as model input. Fixed pretrained feature extraction may be cached once across folds; it must not fit any transform or use labels.
- Fit `StandardScaler` on each fold's training embeddings only, followed by `LinearSVC(C=1.0, class_weight="balanced", max_iter=10000, random_state=42)`. No hyperparameter selection, epoch/checkpoint choice, or threshold tuning on outer-fold labels.
- Primary evaluation: exact established `primary` prompt-grouped five-fold assignments. Report OOF balanced accuracy, per-fold BA, class recall, coverage, and aligned comparisons against the adopted Open Pool v15 prompt-centered SVC (`artifacts/cpu-openpool-prompt-centered-low-pool-weight-v15/primary/oof-all.parquet`). Compare at identical IDs/folds/labels with a prompt-level paired bootstrap (>=2,000 resamples, seed 42).
- Adoption gate: the candidate's primary paired-bootstrap 95% CI lower bound for BA difference must exceed zero. If it passes, evaluate on the existing independent `blend-confirm` GroupKFold assignment (`shuffle=True`, seed 271828) and compare against the prompt-centered SVC refit on that exact assignment. Apply the same gate. Do not blend before both base-model gates pass; any blend needs its own preregistered nested/fresh-split test.
- Only after both gates pass, fit the scaler/readout on all official train rows and prepare a private Kaggle Notebook. The Notebook must load the exact public model input, run with Internet disabled, finish the complete hidden-test inference and submission write within 8 hours (one-hour margin under the 9-hour cap), and create exactly one valid prediction per test `id` in `submission.parquet`. Recheck official rules, deadline, daily count, final-submission count, and public top immediately before any submission.

## GPU and host resource gate

- Target only host 142, GPU index 1, currently mapped to `GPU-8a059266-7ede-0427-ff30-08ba7a9b5224` (RTX PRO 4500 Blackwell, 32,623 MiB), pending a fresh multiple-sample host/UUID confirmation immediately before execution. The smaller A4000 is not a target for this 30B model.
- This target is occupied by the active Qwen3-8B run (`GPU-8a059266-7ede-0427-ff30-08ba7a9b5224`). Do not share it or start this pilot until that run is terminal and a fresh preflight shows no compute PID on the selected UUID. A busy device is a wait condition.
- Run a candidate-specific frozen-inference pilot (model load + one batch at the maximum 384-token length). Record model/version hashes, GPU UUID/name, process list, free/peak VRAM, host MemAvailable, elapsed load/forward time, and finite output shape/value checks. Proceed only if measured peak plus estimated remaining allocations fits while preserving `max(4 GiB, 25% of total VRAM)` and host MemAvailable stays >=16 GiB. Since this candidate has no model-weight backward pass, do not add optimizer/backward work to the pilot.
- Pilot and full extraction must use only the chosen UUID (set `CUDA_VISIBLE_DEVICES` to it, then `torch.cuda.set_device(0)`); no auto-distribution to other GPUs. Full extraction is detached/resumable and writes per-batch cached embeddings/checkpoints. Observe at >=10-minute intervals. On OOM or a guard breach, stop only this candidate's child process, preserve completed rows and record the next resume position.
- Benchmark extraction throughput on the pilot and project it to both all 2,699 train rows and the eventual ~4,000-row Kaggle test. If the expected end-to-end Kaggle Notebook runtime exceeds the 8-hour target, stop before full OOF and record the result; do not silently change sequence length, quantization, model, or batch protocol.

## Provenance and technical references

- [Official Qwen3-30B-A3B-Base model card](https://huggingface.co/Qwen/Qwen3-30B-A3B-Base): model size, architecture, Apache 2.0 license, and Transformers support.
- [Official Kaggle Qwen3 model variation](https://www.kaggle.com/models/qwen-lm/qwen-3/Transformers/30b-a3b-base): competition-accessible model input, version 1.
- [Meni David Gottesman's public MoE throughput discussion](https://www.kaggle.com/competitions/name-that-llm/discussion/752198): motivation only; no claim that it reveals their final approach.
- [BitsAndBytes 0.50.2 release](https://github.com/bitsandbytes-foundation/bitsandbytes/releases/tag/0.50.2) and [CUDA build targets](https://github.com/bitsandbytes-foundation/bitsandbytes/blob/main/docs/source/installation.mdx) indicate NF4 support on T4-class SM75 and Blackwell SM120 with CUDA 12.8 wheels. [Transformers AWQ integration](https://github.com/huggingface/transformers/blob/main/src/transformers/quantizers/quantizer_awq.py) was checked when choosing NF4 over the unmaintained community AWQ path. Official docs support is not a substitute for the required runtime pilot; the installed package and actual Blackwell/T4 execution remain unverified.

This screen measures transfer to held-out official prompts. It does not establish hidden-test/Public LB performance; the independent confirmation split is still drawn from the same 150 official prompts.

## Execution amendment log

- 2026-11-08 13:22 JST: The registered GPU142 pilot first failed before model loading because PyTorch reports the selected UUID without the `GPU-` prefix. Candidate runner `src/gpu_qwen30b_embeddings.py` was corrected to normalize only that prefix; updated runner SHA-256 is `a7e260dec3a7a0b8cff44d60b5235f156dd3e08d9c94bc03b5d201f117a9a24a` (config remains `ffcb9f217afc552835afea24d3c8c7f2748756d294905118d9c6f115de72d933`). The retry passed the UUID/resource preflight on GPU1 UUID `GPU-8a059266-7ede-0427-ff30-08ba7a9b5224`, but the 4-bit 30B model load reached 27,718 MiB GPU use, leaving 4,382 MiB free against the required 8,156 MiB reserve, then raised CUDA OOM with 8 MiB free. The candidate process was terminated and GPU1 release verified. No `pilot.json`, embedding cache, or OOF was produced. Do not start full OOF or repeat the unchanged pilot; this candidate requires a separately preregistered, resource-safe method/placement before reconsideration.
