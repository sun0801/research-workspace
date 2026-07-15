---
date: 2026-07-15
project: sam2-mamba-motion-tracking
source: 2026-07-15-validation-profiling-execution-spec
status: smoke-passed
tags: [experiment, validation, profiling, mot_metrics]
---

# validation timing実装smoke

## 実施内容

承認済みspecに基づき、Mamba側へ以下を追加した。

- `train.py` / `train_stateful.py` に`val_loss_period`制御を追加
- `timing_enabled`を追加し、未指定時はfalseとして現行挙動を維持
- 学習区間、val loss区間、epoch全体のwall-clockログ
- tracker推論subprocess、TrackEval直接呼び出し、summary parseのwall-clockログ

変更対象:

- `/mnt/HDD10TB-2/aburatani/2025_09_aburatani_Mamba_Trackers/ssm_tracker/train.py`
- `/mnt/HDD10TB-2/aburatani/2025_09_aburatani_Mamba_Trackers/ssm_tracker/train_stateful.py`
- `/mnt/HDD10TB-2/aburatani/2025_09_aburatani_Mamba_Trackers/ssm_tracker/train_utils/mot_metrics.py`

## 検証結果

- `py_compile`: PASS
- `git diff --check`: PASS
- `should_run_mot_metrics`の周期判定smoke: PASS
- `timing_enabled=false`のmock: timingログなし、metric結果一致
- `timing_enabled=true`のmock: tracker推論・TrackEval・summary parseの3区間ログを確認
- mock metric結果（HOTA / DetA / AssA / MOTA / IDF1）: 既存形式と一致

## 現時点の判定

計測機能は通常学習時に無効化できる状態で実装できた。canonical configのepoch数・評価周期は変更していない。

## 未実施

- 固定checkpointを使った実tracker推論時間の計測
- 固定tracker出力を使った実TrackEval時間の計測
- 現行設定の5〜10epoch baseline学習
- `val_loss_period=5` / `mot_metrics_period=10`候補との比較
- 全モデル100epoch学習
