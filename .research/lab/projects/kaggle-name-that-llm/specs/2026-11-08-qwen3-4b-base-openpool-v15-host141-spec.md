---
project: kaggle-name-that-llm
status: approved-under-active-goal
execution_status: pilot-passed-primary-running
created: 2026-11-08
last_updated: 2026-11-08
tags: [spec, experiment, gpu, qwen, kaggle]
---

# Qwen3-4B-Base + Open Pool v15 Host141 Spec

## 目的と位置づけ

公開LBトップ超えを目指す承認済み自動実験goalの候補比較として、Qwen3-4B-Baseのprompt-grouped OOF性能と既存Qwen/SVCとの誤り補完性を評価する。4Bは既評価のQwen3-1.7Bと8Bの間の容量であり、別の公開pretraining checkpointを検証できる。一方、Kaggle上の採用実績や当コンペでの性能は確認していないため、規模だけから改善を仮定しない。

## 出典と固定条件

- Kaggle公式model variation: [Qwen3-4B-Base](https://www.kaggle.com/models/qwen-lm/qwen-3/Transformers/4b-base), version 1、取得確認 2026-11-08。
- 公式metadata: 4.0B parameters、36 layers、Q 32/KV 8、fine-tunable、Apache 2.0、uncompressed size 8,056,508,540 bytes。
- 学習データは既存 `crtproduction/name-that-llm-open-pool` version 15 と公式competition trainのみ。v15のprompt近似除外、完全一致除外、class-uniform cap、未使用の`match_weight`等の既存protocolを変更しない。
- primaryは既存保存済み5-fold `GroupKFold(prompt_id)`を再使用する。seed 42、max length 384、device micro-batch 1、BF16、gradient checkpointing、LoRA rank 16/alpha 32/dropout 0.05、適用layer 0–19、pooled layers `[2,4,6,8,12,16,20,24]`を固定し、モデルcheckpoint以外を変えない。
- 既存CPU best、Qwen3-1.7B、Qwen3-8Bの成果物を上書きしない。runは独立ディレクトリ `artifacts/gpu11-qwen3-4b-base-openpool-v15/` に保存する。

## 実装範囲と実行先

- 実装repo: `/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/`。
- 変更は専用config `configs/gpu11-qwen3-4b-base-openpool-v15.json` の追加のみ。既存runnerはAutoModel/hidden-states/LoRA構成であり、Qwen3 4Bの互換性をpilotで確認する。runner修正が必要と判明した場合は実装を止め、変更範囲を本specへ追記してから着手する。
- 実行host: `141-X9DAi`、GPU2 UUID `GPU-48a73ba5-62ab-e9ff-b15b-e4eceae66c58` に限定する。Host142 GPU0/GPU1の実験とwatcherは変更しない。他GPUとの同居はしない。
- 重みは公式Kaggle model version 1からローカルcacheに取得し、Gitへ入れない。cache、データ、OOF、checkpointは実装repoの既存gitignore対象領域に置く。

## 検証手順と安全条件

1. 起動直前にrate guardを通し、141/142を複数回観測する。Host141 GPU2に他計算プロセスがなく、UUIDが一致し、free VRAMがpilot開始条件を満たし、`MemAvailable >= 16 GiB`であることを確認する。Host142の稼働jobはそのままにする。
2. config hashとrunner hashを記録し、`src/gpu_experiment.py --pilot`でmodel load、forward、backward、optimizer stepを実測する。pilotで測ったpeak plus追加見積が空きVRAMから`max(4 GiB, GPU全体の25%)`を残す範囲に収まり、RAM床も満たす場合のみ本runへ進む。pilot失敗時はOOM等の原因と資源量を記録し、同一設定を再実行しない。
3. primary 5 foldsを実行し、各foldのprompt holdout、除外行数、checkpoint、OOF/logits、BA、GPU/RAM、所要時間を記録する。runnerはSIGTERM後batch境界で安全停止し、epoch完了時checkpointからresumeする。進行中epochの未checkpoint分は再学習になるため、停止時に保存済みepochと未保存範囲を記録する。別GPUへ自動配置しない。
4. 現行のprompt-level paired bootstrap採否規則でCPU bestとの差を評価する。candidate BAと既存Qwen blendへの追加価値もOOFで測る。改善または有意な補完がなければ棄却し、confirmationやKaggle Notebook作成へ進まない。有望な場合のみ、別split confirmationのspec条件を確認して再現を続ける。

## 実行コマンド・成果

- pilot: `.venv/bin/python -u src/gpu_experiment.py --config configs/gpu11-qwen3-4b-base-openpool-v15.json --model-path <verified-local-model-cache> --run-dir artifacts/gpu11-qwen3-4b-base-openpool-v15 --pilot`
- primary: 同コマンドから`--pilot`を外して`--resume`を追加する。`CUDA_VISIBLE_DEVICES`はGPU UUIDに固定する。
- 成果物: 専用run directory、stdout log、config/runner/cache hash、pilot report、fold checkpoints、OOF/logits、paired-bootstrap report。
- Kaggle上への作成・提出は本候補の範囲に含めない。提出検討は採否・confirmation・Notebook runtime/provenance gateを通過後、親specと現行公式規則に従う。
