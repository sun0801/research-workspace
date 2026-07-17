---
date: 2026-07-17
project: sam2-mamba-motion-tracking
source: experiment-revision
status: completed
tags: [spec, experiment, state-carry, ground-truth, mot-metrics]
---

# State Carry GT入力・MOT Metrics再実験 Spec

## 目的

detector bboxの誤差を除外し、1動画で学習したState Carryモデルのtracker associationがHOTAを改善できるか確認する。

## 条件

- sequence: `dancetrack0004`のみ
- 学習annotation: 同sequenceのGT trajectory
- tracker入力: 同sequenceのGT bboxをMOT入力形式へ変換
- `val_loss_period: 1`
- `mot_metrics_period: 5`
- epoch上限: 100
- Comet logging: 有効
- 外部ソースコード・canonical config: 変更なし

## 評価

- epochごとのtraining/validation loss
- epoch 5, 10, ..., 100のHOTA、DetA、AssA、MOTA、IDF1
- GT入力時のDetAとassociation指標（AssA/IDF1）の乖離
- epoch 1から最終epochまでのlossとMOT Metricsの関係

## 成功・失敗の解釈

- GT入力でもDetAが高くAssA/IDF1/HOTAが低い場合、detectorではなくState Carry推論・association・state propagation側の問題を示唆する。
- lossが低下してもHOTAが改善しない場合、lossとtracking qualityの乖離を示す。
- lossが初期値の1/10以下に到達しない場合、「完全な過学習」ではなく「loss低下中のtracking評価」として解釈する。

## 実行承認

- ユーザー承認: 2026-07-17にGT入力条件で実行を明示承認済み。
- 結果: [`2026-07-17-statecarry-gt-input-mot-metrics.md`](../experiments/2026-07-17-statecarry-gt-input-mot-metrics.md)
