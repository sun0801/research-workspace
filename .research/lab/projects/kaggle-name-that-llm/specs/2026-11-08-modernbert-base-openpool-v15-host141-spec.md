---
project: kaggle-name-that-llm
status: approved-under-active-goal
execution_status: pilot-passed-primary-running
created: 2026-11-08
last_updated: 2026-11-08
tags: [spec, experiment, gpu, modernbert, kaggle]
---

# ModernBERT-Base + Open Pool v15 Host141 Spec

## 目的と根拠

評価する仮説は、bidirectional ModernBERT-Baseに対するOpen Pool pretrainingとofficial-train foldwise LoRAが、prompt-held-out分類で有望なOOFを出し、既存Qwen/SVCの補完モデルになり得ること。Kaggle Discussion 754860のcomment 3551013でRayan Baburが「Open Pool pretraining後、train.csvで5-fold LoRA」としてCV `.616`、public LB `.575`を自己申告している。split、pool version、リーク制御など条件が記載されていないため、この値は再現済み・比較可能なスコアとして扱わない。

公式Kaggle model variation [Answer.AI ModernBERT-Base](https://www.kaggle.com/models/answer-ai/modernbert/PyTorch/base) version 2はfine-tunable、Apache 2.0、600,829,754 uncompressed bytes。公式model cardはbaseを149M parameters/22 layersと記載。Hugging Face Transformers公式実装では各layerに`attn.Wqkv`, `attn.Wo`, `mlp.Wi`, `mlp.Wo`がある。この情報は専用runnerのmodule mappingをpilotで確認する根拠とする。

## 固定条件・評価

- 外部データ: `crtproduction/name-that-llm-open-pool` version 15のみ。既存Qwen runner同様のexact-text除外、fold validation prompt近似除外、uniform 2,500/class cap、`match_weight`不使用を守る。
- primary splitは保存済み`GroupKFold(prompt_id)` 5 folds。seed 42、max length 384、BF16、device microbatch 1、gradient checkpointing、effective batch rows 18を固定。stage1はfiltered pool 1 epoch、stage2は現fold official train 2 epochs。LoRA rank16/alpha32/dropout .05、全22層の4投影へ適用。Pooled hidden layers `[2,4,6,8,12,16,20,22]`。
- primary BA/OOFを現CPU bestと同一prompt-level paired bootstrap 2,000回以上で比較し、95% CI lower bound >0を adoption gateとする。採用済みQwen blendへ加えたOOF補完性も測る。pass時だけ独立confirmation splitへ進む。
- model architecture、対象層名、hidden-state数、有限値をpilotで確認する。module mapping不一致・モデル出力不一致ならfull runへ進まない。

## 実装・実行範囲

- 実装repo: `/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/`。
- 新規`src/gpu_modernbert_experiment.py`と`configs/gpu12-modernbert-base-openpool-v15.json`のみ追加。既存`src/gpu_experiment.py`と他candidate configは変更しない（candidate11のpilot hashとlive runを保全）。新runnerは既存Qwen runnerを基にし、ModernBERT target-module mappingとhidden-state適合性のみを分岐させる。
- host: `141-X9DAi` GPU1 UUID `GPU-51b57ca0-53ca-3266-7105-efc692a6c834`。現在のcandidate11が占めるGPU2とは別device。host141のGPU0/1で直前の独立preflightを行い、選択GPUに他processがないこと、VRAM/RAM safety floor、lockを確認する。
- run directory `artifacts/gpu12-modernbert-base-openpool-v15/`、model cache `artifacts/model-cache/modernbert-base-kaggle-v2/`。大容量成果物はGit対象外。

## 安全条件・手順

1. 新しい長時間作業前に`.agents/skills/kaggle-workflow/scripts/codex_rate_limit.py --guard 15`を通す。host141を複数回観測し、GPU UUID/device, compute PIDs, free VRAM, MemAvailableを記録する。
2. KaggleHub公式version 2 modelをlocal cacheへ取得し、Kaggle MCP file-size一覧と照合する。train/folds/Open Pool/prompt reconstruction、runner/config hashesを記録してHost141のisolated repoへ転送する。
3. GPU1をUUID固定してpilot（load/forward/backward/optimizer step）する。free VRAMから`max(4 GiB, 25% total VRAM)`を残し、MemAvailable >=16 GiBが続く場合のみprimaryを開始する。OOM等の同条件再試行はしない。
4. primary OOF完了後にadoption gateを評価し、失敗ならrejectしてconfirmationを開始しない。Notebook作成・Kaggle書込・提出はこのcandidateの対象外。

## 再開と停止

Epoch完了ごとにoptimizer/RNG/model stateをcheckpointし、SIGTERMはbatch境界で停止する。進行中epochはcheckpoint外なので未保存範囲として記録し、再開時は最新完了epochから進める。watcherを起動する場合はHost141専用にし、別host/GPUへ自動移動しない。

