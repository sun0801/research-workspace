---
date: 2026-11-08
project: kaggle-name-that-llm
source: autonomous-goal
status: approved
approval_basis: active-goal-2026-11-06-gpu-autonomous-first-place-spec
execution_status: model-cache-verified-analysis-prepared-watcher-queued
tags: [spec, experiment, gpu, qwen3, qlora, prompt-grouped]
---

# Qwen3-14B-Base fixed-epoch QLoRA prompt-grouped candidate

## Hypothesis and public evidence

The official Qwen3-14B-Base model may learn the writing-style distinctions in the official rows better than the current prompt-centered SVC. Kaggle Notebook [`handeakn/fine-tuning-with-sinkhorn-oof-proba`](https://www.kaggle.com/code/handeakn/fine-tuning-with-sinkhorn-oof-proba) contains a workable Qwen3-14B 4-bit NF4 classification/LoRA path and 5-fold prompt GroupKFold scaffold. It only runs fold 0, however, and uses `load_best_model_at_end=True` with validation balanced accuracy. That is not valid outer-fold checkpoint selection and gives no trustworthy five-fold result. This candidate fixes the protocol at one epoch and never uses validation labels for training, checkpoint selection, or stopping.

## Exact model and training protocol

- Use official Kaggle Model `qwen-lm/qwen-3/Transformers/14b-base`, version 1. Kaggle lists 14.8B parameters and its version-1 model files total 29,548,195,881 bytes across 8 safetensors shards. The official [Qwen3-14B-Base model card](https://huggingface.co/Qwen/Qwen3-14B-Base) lists Apache-2.0. Do not upload model weights into a new public object.
- `AutoModelForSequenceClassification`, 18 labels, max length 512, text only. Use 4-bit NF4 with double quantization and FP16 compute for T4 compatibility; leave the classification `score` head unquantized and trainable.
- Freeze the base and apply sequence-classification LoRA with rank 16, alpha 32, dropout 0.05, targets `q_proj,k_proj,v_proj,o_proj,gate_proj,up_proj,down_proj`, and save the `score` module. Enable gradient checkpointing and input gradients. Use only the official training rows; do not use public pool rows, generated data, or existing adapter artifacts.
- Fixed fold training: one epoch on the current fold's official training rows, microbatch 2, gradient accumulation 8 (effective batch 16), AdamW 8-bit, learning rate `1e-4`, cosine schedule with 10% warmup, weight decay `0.01`, max grad norm `1.0`, seed 42. Save at the fixed epoch end. Disable validation-driven checkpoint choice, early stopping, or hyperparameter changes.
- Primary: exact saved official prompt GroupKFold 5-fold assignment. Confirmation: the existing independent `blend-confirm` GroupKFold assignment used by the adopted SVC comparator. OOF must cover exactly all 2,699 rows once per split.

## Fixed inferred-prompt postprocessing

Apply the already registered `cpu-inferred-test-prompt-sinkhorn-v1` transform as a predeclared part of this candidate: cluster the entire split's held-out texts using default word-unigram TF-IDF (`stop_words="english"`, `sublinear_tf=True`) and average-linkage cosine agglomeration with `n_clusters=round(N/18)`, then run 100 Sinkhorn iterations at `T=0.3` on the model's stored multiclass logits. Cluster construction may not read prompt IDs, labels, folds, or predictions. Report raw argmax as a diagnostic; do not choose between raw and postprocessed output after seeing the split scores. The required adoption gate is applied to the fixed postprocessed candidate against the current adopted SVC argmax OOF on identical IDs/folds/labels.

For each split, report raw and postprocessed balanced accuracy, per-fold BA, class recall, confusion matrix, prompt-cluster paired bootstrap (>=2,000; fix 5,000, seed 42), cluster ARI/purity/size diagnostics after predictions are fixed, and resource/runtime records. Run confirmation only if the primary prompt-paired 95% CI lower bound exceeds zero; require the same lower-bound gate on confirmation.

## Resource, runtime, and execution order

- Target only host142 GPU1 UUID `GPU-8a059266-7ede-0427-ff30-08ba7a9b5224`. Run after currently registered candidate06 and candidate08 GPU1 evaluations and the already approved Mistral03 queue clear. Do not overlap GPU1 jobs. Before pilot and every full split: `--guard 15`, two-snapshot UUID/process/free-memory preflight, exact UUID `CUDA_VISIBLE_DEVICES`, VRAM reserve >=8,156 MiB, and host `MemAvailable` >=16 GiB.
- Pilot the same frozen 4-bit model, LoRA configuration, sequence length, microbatch, and optimizer step. Require finite logits/loss/gradients, measure peak VRAM/RSS, and estimate full 5-fold local OOF plus 4,000-row hidden-test inference. Do not start full OOF unless the measured resource gates pass and projected offline Notebook inference is <=8 hours (one-hour margin under the 9-hour cap). Save resumable fold checkpoints and stop only this candidate process on a resource breach.
- Keep all candidate artifacts private/local. After both OOF gates pass, perform a fixed full-train fit, validate offline inference and `submission.parquet` against the hidden-test rerun shape, then recheck the live leaderboard, rules, deadline, daily submission count and final slots before any private Notebook submission.

## Reproducibility and limits

Pin the model version, dependency lock, source/config/model hashes, primary/confirmation fold files, raw and postprocessed OOF predictions, bootstrap summaries, and exact run commands. The public Notebook's single fold and validation-selected checkpoint are motivation only; they are not evidence of candidate performance. No public/private leaderboard score is inferred from OOF metrics.
