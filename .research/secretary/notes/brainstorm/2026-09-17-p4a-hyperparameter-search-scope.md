---
date: 2026-09-17
project: sam2-mamba-motion-tracking
source_todo: "P4aのchunk/TBPTT長、batchサイズ、Mamba内部次元を探索する"
topic: P4aハイパーパラメータ探索の対象整理
status: exploratory
tags: [brainstorm, research, p4a, tbptt, hyperparameter]
---

# P4aハイパーパラメータ探索の対象整理

## 読み込んだ文脈

- 2026-09-11 MTG議事録
- `specs/2026-09-01-p4a-stateful-unroll-tbptt-spec.md`
- `experiments/2026-09-11-p4a-loss-oscillation-diagnostic.md`
- `experiments/2026-09-04-l0-p4a-tracker-sam2-comparison.md`
- プロジェクトREADMEと2026-09-11 TODO

## 相談の出発点

`unroll_length`、`tbptt_length`、chunk/batchサイズ、Mamba内部次元の探索が、9/11 MTGで話したハイパーパラメータ探索に当たるかを確認する。

## 問い

P4aの学習時系列長、勾配のtruncation長、optimizer updateあたりのchunk数、モデル容量を、どの順番と比較条件で探索すれば、stateful学習の性能・安定性への影響を切り分けられるか。

## 現在の基準値

- `unroll_length=48`: 現実装ではdatasetのchunk長に対応する。
- `tbptt_length=12`: chunk内部で勾配グラフをdetachする長さ。stateの数値はcarryする。
- `batch_size=64`: 1 optimizer updateで処理するchunk数。
- `d_m=256`: Mambaの主な内部特徴次元。`d_state=16`は別のstate容量パラメータ。

## 今回の整理

- `unroll_length`と`tbptt_length`は、stateful学習の時間文脈・勾配伝播範囲を決める主要ハイパーパラメータ。
- 現実装ではchunk長と`unroll_length`が同じため、「chunkサイズ」と`unroll_length`を独立因子として二重に探索しない。
- `batch_size`は最適化・計算量に関するハイパーパラメータであり、まずは他条件を固定して評価する。
- `d_m`はハイパーパラメータではあるが、意味としてはモデル容量・アーキテクチャ探索に近い。変更時はパラメータ数、GFLOPS、速度、VRAMも記録する。
- 4因子の全組合せを一度に回すより、時間文脈（unroll/TBPTT）→ batch → model capacityの段階探索が妥当。

## 有力な探索順序

1. padding/maskingがlossとstate更新に混入しないことを確認する。
2. `shuffle=True`を固定し、`unroll_length/tbptt_length`を基準値周辺で比較する。
3. 有力な時系列設定を固定して、`batch_size`を比較する。学習率を同時に変える場合は別要因として記録する。
4. 有力な学習設定を固定して、`d_m`を比較する。必要なら`d_state`は別の容量因子として分離する。
5. predictor単体で候補を絞り、最後にSAM2統合側で評価する。

## 評価軸

- validation loss
- free rolloutのhorizon別IoU / MAE（1, 4, 8, 16, 32）
- divergence率、NaN/Inf率、state norm
- DanceTrack val 25系列のHOTA、DetA、AssA、IDF1、IDSW
- 学習時間、推論速度、GPUメモリ、`d_m`変更時のパラメータ数/GFLOPS

## 未解決の問い

- `unroll_length`を変更した場合、dataset chunk長の変更として扱うのか、別のchunk設定を導入するのか。
- `unroll_length`と`tbptt_length`の候補値をどこまで広げるか。
- batch size変更時に学習率を固定するか、線形スケーリング条件を別途試すか。
- `d_m`の探索を単なる性能比較にするか、同程度GFLOPS・速度の比較へ接続するか。
- predictor単体の最良をSAM2統合へ渡す選抜基準をどう定めるか。

## 関連ファイル

- `.research/lab/projects/sam2-mamba-motion-tracking/meetings/2026-09-11-mtg.md`
- `.research/lab/projects/sam2-mamba-motion-tracking/specs/2026-09-01-p4a-stateful-unroll-tbptt-spec.md`
- `.research/lab/projects/sam2-mamba-motion-tracking/experiments/2026-09-11-p4a-loss-oscillation-diagnostic.md`
- `.research/lab/projects/sam2-mamba-motion-tracking/experiments/2026-09-04-l0-p4a-tracker-sam2-comparison.md`
