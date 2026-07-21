---
date: 2026-07-21
project: sam2-mamba-motion-tracking
status: proposal
tags: [spec, state-carry, mot, tracking, baseline, teacher-forcing, tbptt]
---

# State Carry型MOT: baseline基準化・association分離・cache更新制御・学習整合化 spec候補

## ステータス

**提案段階。実装開始は未承認。**

この文書は、横断調査とGT入力診断から導いた実装候補を固定するためのspecである。外部実装リポジトリや実験設定は変更していない。実装を始める際は、対象範囲と検証条件を本specから選択して承認を得る。

## 背景と問題定義

現行MambaStatefulは、GT-only fixed windowで学習する一方、推論ではtrackごとのcacheにaccepted detectionまたはself predictionを入れ、Mamba予測bboxをhard IoU associationの主位置として使う。

GT入力のsingle-video診断では、motion predictorのone-step IoUはzero-motionより高いが、prediction matchingではHOTA 5.27 / IDs 922、last-observed bbox matchingではHOTA 83.74 / IDs 4だった。したがって最初の対象はMambaの予測精度ではなく、**predictionをassociation主位置にした導線**と**無条件cache更新**である。
同時に、MambaTrack / TrackSSMは固定長sliding-windowを学習・推論の共通基盤とする既存モデルであり、MambaStatefulとの比較用baselineとして利用できる。ただし、これらも推論時には予測bboxをassociationへ使うため、Statefulより高い結果が得られても、学習設定だけの効果とは直ちには解釈しない。optimizer、scheduler、入力形式、window長、checkpoint選択を記録し、association条件と分離して評価する。

## 目的

次の四つを独立に検証できる状態にする。

1. MambaTrack / TrackSSM / MambaStatefulのas-is比較により、sliding-window型とStateful型の差を把握する。
2. observation優先matchingにより、motion predictionがID associationを壊さないか。
3. confidence / match qualityによるcache update・freeze・resetがstate汚染を抑えるか。
4. GT-only fixed windowと、入力分布混合・stateful TBPTTのどこがtracker改善へ寄与するか。

## 非目標

- 今回はSAM2/SAMURAI統合の変更を行わない。
- TrackEval計算導線を変更しない。
- 最初の段階で検出器、ReID、associationアルゴリズム全体を置き換えない。
- `InferenceParams`をautograd stateとして無検証で再利用しない。
- observation優先matchingを最終提案手法とみなさない。P1はassociationの因果効果を測る診断用baselineとして扱う。

## 実装フェーズ

### P0: 既存導線の再現（変更なし）

| 項目 | 内容 |
| --- | --- |
| 対象 | 既存GT-input single-video checkpoint / tracker |
| 実施 | A0 zero-motion matching と A1 current prediction matchingを再実行 |
| 成功条件 | HOTA 83.74、5.27近傍およびID数の傾向を再現 |
| 失敗時 | 以降の比較を始めず、データ・commit・評価入力差を診断 |

### P0.5: sliding-window baselineの基準化（変更なし）

| 項目 | 内容 |
| --- | --- |
| 対象 | MambaTrack、TrackSSM、現行MambaStatefulの既存checkpoint / tracker |
| 実施 | 同一detector入力、動画split、TrackEval設定でas-is推論を比較。predictorログとtrackerログを同じ形式で収集 |
| 記録 | 入力形式、window長、optimizer、LR scheduler、epoch、checkpoint選択、association方式 |
| 成功条件 | 3モデルの再現可能な比較表を作り、Statefulだけの学習設定差と、全モデルに共通するassociation導線を分離して解釈できる |
| 解釈 | MambaTrack / TrackSSMのみ改善しても、学習設定・入力形式・モデル構造・associationの寄与を個別に断定しない |

### P1: association分離（診断用baseline）

| 項目 | 内容 |
| --- | --- |
| 位置づけ | 最終提案ではなく、prediction-to-association接続の因果効果を測る診断用baseline |
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

### P4a: stateful predictor training + TBPTT（最小検証）

| 項目 | 内容 |
| --- | --- |
| 変更範囲 | 時系列dataset sampler、Mamba学習forward、loss mask、logging |
| 目的 | tracker associationを変更せず、sliding-window学習とstate carry学習の差をmotion predictor単体で検証する |
| 入力 | 初期比較はGT-onlyまたは制御した同一入力に限定し、P3の入力分布混合効果と分離する |
| state境界 | video / track開始でreset。別trackへのcarry禁止 |
| TBPTT | chunk間carry後detach。detach長を実験変数として記録 |
| loss | 初期warm-up以後の各有効時刻。padding / missingはmask |
| 前提検証 | fixed-windowとのforward parity、有限gradient、state norm/NaN監視 |
| 比較 | 現行L0とTBPTT版を、同一入力・同一モデル・同一評価動画で比較 |
| 成功条件 | forward parity、finite gradient、free rolloutのhorizon別指標を確認し、state carry学習の効果をpredictor指標で判断できる |
| 中止条件 | parity不一致、NaN、state発散が解消しない場合はtracker統合へ進まずTBPTT長/状態実装の診断へ戻る |

### P4b: TBPTT checkpointのtracker統合

| 項目 | 内容 |
| --- | --- |
| 変更範囲 | P4aで検証済みcheckpointのtracker接続。association / cache規則は固定し、新しい変更を同時導入しない |
| state境界 | P4aと同じvideo / track単位のresetを維持 |
| 比較 | P3またはP4aのcheckpointを同一tracker規則で比較。A3などのassociation条件を固定 |
| 成功条件 | predictor改善がHOTA / AssA / IDF1へつながるかを、P0.5 baselineと同一条件で確認 |
| 中止条件 | predictorのみ改善してtrackerが改善しない場合は、学習問題とassociation問題を分けて解釈し、association設計へ戻る |

## 評価出力

### baseline比較

- MambaTrack / TrackSSM / MambaStatefulのas-is結果を同一表にする。
- predictor指標とtracker指標を分離し、HOTA改善を学習設定の効果と直結させない。
- MambaTrack / TrackSSMにもprediction-primary associationが残るため、必要に応じて同一association条件の比較を追加する。

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

各フェーズは、実装または実験を開始する前に個別に承認する。次を確定する。

1. 承認するフェーズと範囲: P0.5、P1、P2、P3、P4a、P4bから対象を限定する。
2. 対象リポジトリ・変更対象ファイル: 既存推論のみか、tracker / tracklet / dataset / training forwardのどこを変更するかを明示する。
3. 検証方法: 対応するbaseline、比較条件、成功・失敗基準、TrackEvalまたはpredictor評価を明示する。
4. 実装・実験開始承認: ユーザーが対象フェーズの開始を明示する。

P0.5のas-is比較を含め、実行開始は本ゲートを通過した対象に限定する。P1以降は、前フェーズの結果を記録してから個別に承認する。

## 根拠

- [統合比較](../papers/sequence-learning-survey/comparison/2026-07-21-04-state-carry-synthesis.md)
- [GT入力根本原因診断](../experiments/2026-07-17-statecarry-root-cause-diagnosis.md)
- [現行State Carry経路分析](../experiments/2026-07-17-current-state-carry-analysis.md)

## 変更履歴

| 日付 | 内容 |
| --- | --- |
| 2026-07-21 | MambaTrack / TrackSSM / Statefulのbaseline基準化をP0.5として追加。P1を診断用baselineとして再定義し、P4をpredictor単体（P4a）とtracker統合（P4b）へ分割。フェーズ別Implementation Gateへ更新。 |
