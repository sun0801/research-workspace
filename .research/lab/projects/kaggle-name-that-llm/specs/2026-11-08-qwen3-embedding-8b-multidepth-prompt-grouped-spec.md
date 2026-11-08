---
date: 2026-11-08
project: kaggle-name-that-llm
source: autonomous-goal
status: approved
approval_basis: active-goal-2026-11-06-gpu-autonomous-first-place-spec
execution_status: pilot-queued-behind-registered-gpu-jobs
tags: [spec, experiment, gpu, qwen3-embedding, prompt-grouped]
---

# Qwen3-Embedding-8B multi-depth LoRA prompt-grouped candidate

## 目的と根拠

Qwen3-Embedding-8Bの8深度表現を用いたfoldwise LoRA classifierが、採用済みOpen Pool v15 prompt-centered SVCより未見promptのbalanced accuracyを改善するか評価する。

Kaggle公式Notebook `concyclics/0-679`（version 1, last run 2026-11-04）には、Qwen3-Embedding-8Bを使う独立five-fold native candidateが含まれる。Notebookの公開ソースを実行せず静的解析した結果、このcandidateは36層の`[3, 6, 9, 12, 18, 24, 30, 36]`でmasked last-token poolingし、8×4,096 = 32,768次元をLoRA・LayerNorm・linear headで学習する。Notebookの最終rootは`native_q8_40`を選び、WeMM-4B重みは0である。したがってこの公開スコアはQwen multi-depthの候補動機にはなるが、Qwen単体の寄与を分離した測定値ではない。公開full-fit expert群はOOF根拠に転用しない。

このcandidateは、active goalが許可する次候補の選定・実装・prompt-grouped検証範囲に含める。Kaggle private asset作成・Notebook push・提出は、primary/confirmationと提出前gateの後に限る。

## モデル・データ

- Official Kaggle model: `qwen-lm/qwen-3-embedding/Transformers/8b`, version 1。Upstream model cardはApache-2.0、8B/36 layers/4096 native embedding dimension、32K contextを記載。Transformers 4.51.0以上が必要。
- Kaggle version-1 model file list: 4 safetensors shard合計15,134,634,568 bytes、`model.safetensors.index.json`, config, tokenizerなど。各shard名・sizeをrunner manifestに固定する。取得物全体のSHA-256も保存する。
- Input formatting: official model instruction template `Instruct: Identify the language model that generated the text based on its writing style.\nQuery: {text}`。Maximum length 512; truncation is fixed. No prompt ID or label enters the encoder.
- Backbone: all 36 transformer layers; PEFT LoRA target suffixes `q_proj,k_proj,v_proj,o_proj,gate_proj,up_proj,down_proj`, rank 16, alpha 32, dropout 0.05. Backbone uses FP16 for T4 compatibility with gradient checkpointing. LoRA, eight per-depth LayerNorms, and the plain 18-class head use FP32.
- Features: masked last-token pooling at layers `[3,6,9,12,18,24,30,36]`. The official Transformers example pools the final hidden state directly and then L2-normalizes it; it does not insert a separate learned projection in this inference path. This candidate concatenates the eight selected 4,096-dimensional states (32,768 dimensions), applies one trainable LayerNorm per segment, dropout 0.1, and a linear 18-class head. Do not use a centered/test-group head because test rows have no prompt IDs and same-prompt inference grouping has not been independently validated.
- Training rows: official `train.csv` plus Open Pool v15 only. For each fold, use the fixed balanced sample of 2,500 external rows/class (45,000 total), remove exact normalized official-text matches, and remove validation-prompt near matches using the existing registered char/word TF-IDF threshold 0.40 before external warmup. Do not use the pool publisher's `match_weight` feature.
- The public notebook's released fold adapters/predictions are not used for fitting or OOF. Every outer-fold model is initialized from the official base and trained independently.

## Frozen training protocol

下記のbatch size、optimizer、epoch数、学習率は本workspaceのQwen02 runner設定から候補08向けに調整した事前登録値であり、公開Notebookの学習recipeを再現したものではない。公開ソースから確認できたのは層選択・pooling・head構成とLoRA対象moduleまでである。

- Tokenization cached once per fixed input; no label-dependent transform. A single batch is padded dynamically within its microbatch.
- Stage 1: external rows only, one epoch, microbatch 1 / effective batch 18, AdamW, adapter LR `1e-4`, head LR `1e-3`, weight decay `0.01`, cosine schedule with `0.1` warmup.
- Stage 2: official training rows for the current fold only, two epochs, microbatch 1 / effective batch 18, AdamW, adapter LR `5e-5`, head LR `5e-4`, weight decay `0.01`, cosine schedule with `0.1` warmup. Carry forward the Stage 1 adapter and head. No outer-validation labels, model choice, or early stopping.
- Fixed seed 42; save optimizer, scheduler, scaler, RNG, and per-epoch checkpoints for exact resume. If implementation-level feasibility requires changing a frozen parameter, stop before full OOF and register a new candidate/version rather than silently adjusting this protocol.

## Evaluation and adoption

- Primary: existing saved prompt GroupKFold assignment, 5 folds. Preserve ID, prompt, label, and fold alignment. Fit each fold solely on the other four prompt groups and report OOF balanced accuracy, fold scores, class recall, confusion matrix, lengths, and runtime/resource measures.
- Comparator: adopted `cpu-openpool-prompt-centered-low-pool-weight-v15` OOF on identical rows/folds. Use at least 2,000 prompt-cluster paired bootstrap resamples with a fixed seed. Only a 95% CI lower bound above 0 advances to confirmation.
- Confirmation: `GroupKFold(n_splits=5, shuffle=True, random_state=42)` with independently trained fold models and the same-split SVC comparator. Require the same paired-bootstrap lower-bound gate. Any blend requires a separately preregistered fresh evaluation.
- A full-train-fit or public-LB score does not replace either OOF gate. Do not tune hyperparameters on either outer validation split.

## Resource, pilot, and runtime gate

- Target only host 142 GPU1 UUID `GPU-8a059266-7ede-0427-ff30-08ba7a9b5224` (RTX PRO 4500 Blackwell, 32,623 MiB), after the current Qwen8B run and any candidate06 work on that UUID are terminal. Do not overlap jobs. Run the standard two-snapshot preflight for UUID, compute PIDs, free VRAM, host MemAvailable, and the `--guard 15` immediately before the pilot.
- Pilot uses one full 512-token representative training batch with model load, forward, backward, and optimizer step. Use microbatch 1 and gradient checkpointing. Record peak VRAM/RSS, measured elapsed time, finite logits/loss/gradients, and actual model/runner/config hashes. Require host MemAvailable >=16 GiB and preserve `max(4 GiB, 25% total VRAM)` after measured plus estimated allocations.
- Estimate complete five-fold training duration from measured pilot and local reference runs. The local OOF may run longer than Kaggle's submission budget, but it must checkpoint/resume and not displace another research job. Separately project the 4,000-row hidden-test inference from a measured 512-token local forward, using a fixed conservative 4× local-to-T4 time factor and two T4s; require <=8 projected hours, leaving one hour under the official 9-hour cap. This is a planning projection, not a T4 benchmark.
- Stop before full OOF if the pilot fails, if model sharding/precision is not reproducible on T4, or if the Notebook runtime estimate exceeds the gate. Do not degrade the protocol silently to fit.

## Kaggle submission gate

- Reconfirm official rules, deadline, leaderboard top, daily submission count, and final slots before submission. The competition is Notebook-only and Internet-disabled; exact model files and candidate adapter must be attached as private Kaggle inputs.
- Submit only after both OOF gates, full-train fit, offline runtime, T4 numerical parity, complete hidden-test execution, and `submission.parquet` identity/schema verification pass. Keep all Kaggle creations private.

## Public sources and limits

- [Qwen3-Embedding-8B official model card](https://huggingface.co/Qwen/Qwen3-Embedding-8B): license, dimensions, architecture, official embedding usage.
- [QwenLM Qwen3-Embedding official repository](https://github.com/QwenLM/Qwen3-Embedding): upstream inference implementation.
- [Public Kaggle Notebook `concyclics/0-679`](https://www.kaggle.com/code/concyclics/0-679): source architecture only; score is a multi-component author result and does not establish isolated OOF improvement.
- [Primary goal spec](2026-11-06-gpu-autonomous-first-place-spec.md): shared evaluation, leak prevention, safety, and submission rules.
