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

## 残りの実施項目

- 10epochの候補周期比較（epoch1 smokeは完了）
- 全モデル100epoch学習
- full valでの時間確認

## 実測baseline（MambaStateful、3sequence）

現行設定の10epoch実験を開始したが、epoch1完了時点で主要な時間が取得できたため、epoch2途中で停止した。canonical configは変更していない。

epoch1の実測:

- 学習: `146.172`秒
- val loss: `24.573`秒
- epoch全体: `170.805`秒

epoch1 checkpointを使った`mot_metrics`単独計測:

- tracker推論 subprocess: `316.973`秒
- TrackEval直接呼び出し: `3.490`秒
- summary parse: `0.000081`秒
- 3sequence combined HOTA: `4.7552`
- 3sequence combined IDF1: `0.44802`

判定: tracking validationの時間増加要因は、今回の部分val条件ではTrackEvalではなくtracker推論 subprocessが支配的である。val lossは約25秒、TrackEvalは約3.5秒だった。

補足: epoch2途中停止のため、10epochの候補周期比較とfull valは未実施。候補設定の総時間は、今回得た1回あたり時間と評価回数から見積もり、必要な場合のみ短い追加実験を行う。

## 候補周期1epoch smoke

候補config（val loss 5epochごと、mot_metrics 10epochごと、`timing_enabled=true`）をepoch1だけ実行した。

- 学習: `146.621`秒
- epoch全体: `146.666`秒
- epoch1のval loss: 実行されず
- epoch1のmot_metrics: 実行されず

候補周期の制御は期待どおり動作した。

## 周期変更の概算

今回の3sequence実測を単純利用すると、100epochでのvalidation部分は次の概算になる。

- 現行（val毎epoch、MOT 5epochごと）: val約`41.0`分 + MOT約`105.7`分
- 候補（val 5epochごと、MOT 10epochごと）: val約`8.2`分 + MOT約`52.8`分

これは部分valでの概算であり、full valの絶対時間を保証するものではない。ただし、評価周期を半分・5分の1にすることで、総時間が大幅に減る方向は確認できた。
