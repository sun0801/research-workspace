---
date: 2026-07-21
project: sam2-mamba-motion-tracking
status: proposal
tags: [spec, state-carry, mot, tracking, teacher-forcing, tbptt]
---

# State Carry型MOT: association分離・cache更新制御・学習整合化 spec候補

## ステータス

**提案段階。実装開始は未承認。**

この文書は、横断調査とGT入力診断から導いた実装候補を固定するためのspecである。外部実装リポジトリや実験設定は変更していない。実装を始める際は、対象範囲と検証条件を本specから選択して承認を得る。

## 背景と問題定義

現行MambaStatefulは、GT-only fixed windowで学習する一方、推論ではtrackごとのcacheにaccepted detectionまたはself predictionを入れ、Mamba予測bboxをhard IoU associationの主位置として使う。

GT入力のsingle-video診断では、motion predictorのone-step IoUはzero-motionより高いが、prediction matchingではHOTA 5.27 / IDs 922、last-observed bbox matchingではHOTA 83.74 / IDs 4だった。したがって最初の対象はMambaの予測精度ではなく、**predictionをassociation主位置にした導線**と**無条件cache更新**である。

## 目的

次の三つを独立に検証できる状態にする。

1. observation優先matchingにより、motion predictionがID associationを壊さないか。
2. confidence / match qualityによるcache update・freeze・resetがstate汚染を抑えるか。
3. GT-only fixed windowと、入力分布混合・stateful TBPTTのどこがtracker改善へ寄与するか。

## 非目標

- 今回はSAM2/SAMURAI統合の変更を行わない。
- TrackEval計算導線を変更しない。
- 最初の段階で検出器、ReID、associationアルゴリズム全体を置き換えない。
- `InferenceParams`をautograd stateとして無検証で再利用しない。

## 実装フェーズ

### P0: 既存導線の再現（変更なし）

| 項目 | 内容 |
| --- | --- |
| 対象 | 既存GT-input single-video checkpoint / tracker |
| 実施 | A0 zero-motion matching と A1 current prediction matchingを再実行 |
| 成功条件 | HOTA 83.74、5.27近傍およびID数の傾向を再現 |
| 失敗時 | 以降の比較を始めず、データ・commit・評価入力差を診断 |

### P1: association分離（最優先の最小変更）

| 項目 | 内容 |
| --- | --- |
| 変更範囲 | State Carry trackerのmatching位置選択のみ |
| 仕様 | primary matchingにはlast trusted accepted observationを使う。Mamba predictionはunmatched trackの補助候補またはmissing出力に限定 |
| 不変条件 | checkpoint、detector入力、TrackEval、track lifecycleは維持 |
| 比較 | A1 vs A2 |
| 成功判定 | A2がA1よりAssA/IDF1を改善し、A0を不必要に下回らない |
| 主な失敗解釈 | A2が改善しない場合、主因はprediction matching単独ではない。cache更新またはtrack lifecycleを次に切り分ける |

### P2: cache更新ガード

| 項目 | 内容 |
| --- | --- |
| 変更範囲 | State Carry trackletのcache/history更新規則 |
| 仕様 | trusted matchのみupdate、low-quality matchはfreeze、unmatched/self predictionは初期版でfreeze |
| quality候補 | detection score、IoU match quality、track age。初期実装は前二者だけ |
| reset | P2本体では導入しない。連続untrusted frame後のresetは別ablation |
| 比較 | A2 vs A3、self-update vs freeze、freeze vs reset |
| 成功判定 | AssA/IDF1、state finite率、長いmiss後の再associationを併記して評価 |

### P3: fixed-window入力分布混合

| 項目 | 内容 |
| --- | --- |
| 変更範囲 | State Carry dataset / training forwardの入力生成のみ |
| 入力 | GT、accepted-detection surrogate、self prediction |
| 教師 | 常にGT next bbox / delta |
| 進め方 | GT-onlyを起点に、surrogate比率とself-prediction比率を別々に増やす |
| 比較 | L0 vs L1、A3のtracker規則を固定 |
| 成功判定 | rollout horizon別誤差とtracker HOTA/AssA/IDF1の両方が悪化しない |

### P4: stateful unroll + TBPTT

| 項目 | 内容 |
| --- | --- |
| 変更範囲 | 時系列dataset sampler、Mamba学習forward、loss mask、logging |
| state境界 | video / track開始でreset。別trackへのcarry禁止 |
| TBPTT | chunk間carry後detach。detach長を実験変数として記録 |
| loss | 初期warm-up以後の各有効時刻。padding / missingはmask |
| 前提検証 | fixed-windowとのforward parity、有限gradient、state norm/NaN監視 |
| 比較 | L1 vs L2、A3のtracker規則を固定 |
| 中止条件 | parity不一致、NaN、またはP1/P2よりassociation悪化が大きい場合はTBPTT長/状態実装の診断へ戻る |

## 評価出力

### predictorログ

- teacher-forced 1-step bbox IoU / delta MAE / Smooth L1
- free rolloutのhorizon別IoU / MAE / NaN率
- GT、surrogate、self predictionの入力種別ごとの誤差
- cache/state norm、cosine similarity、update/freeze/reset回数

### trackerログ

- HOTA、DetA、AssA、IDF1、MOTA、ID switches、track数
- matching位置の種類、accepted / frozen / self-updated / resetされたframe数
- 動画別metricsとmiss区間別metrics

### 公平性

- checkpoint、動画split、detection入力、TrackEval版・設定を固定する。
- thresholdはvalidationでのみ選び、testは選定後に一度実行する。
- A0/A1の再現を各実装変更の前後で確認する。

## 実装開始ゲート

P1の実装を始めるには、次を確定する。

1. 承認するフェーズ: **P1のみ**（P2以降は含めない）。
2. 対象リポジトリ・変更対象ファイル: tracker / trackletのmatching位置選択に限定する。
3. 検証方法: P0再現、A1 vs A2、GT-input single-videoでのTrackEval比較。
4. 実装開始承認: ユーザーが本specのP1開始を明示する。

P2〜P4は、前フェーズの結果を記録してから個別に承認する。

## 根拠

- [統合比較](../papers/sequence-learning-survey/comparison/2026-07-21-04-state-carry-synthesis.md)
- [GT入力根本原因診断](../experiments/2026-07-17-statecarry-root-cause-diagnosis.md)
- [現行State Carry経路分析](../experiments/2026-07-17-current-state-carry-analysis.md)
