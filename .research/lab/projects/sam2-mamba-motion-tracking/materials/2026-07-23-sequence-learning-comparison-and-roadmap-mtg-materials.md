---
date: 2026-07-23
project: sam2-mamba-motion-tracking
type: meeting-materials
topic: sequence-learning-comparison-and-roadmap
status: draft
target_meeting: null
notion_url: null
notion_export: null
tags: [meeting-materials, research, sequence-learning, state-carry, roadmap]
---

# 2026-07-23 MTG資料: 時系列学習手法の比較と研究の進め方

## 0. この資料の目的

RNN/LSTM、Seq2Seq、Mamba系tracking、video/trajectory predictionの調査結果を、現行MambaStatefulと同じ軸で比較する。

また、scale伝播欠落によるbaseline退化を先に修正したうえで、調査結果がP1→P2→P3/P4という実験順序にどうつながるかを整理する。

## 1. 先に結論

1. **Mamba使用とframe間state carryは別である。** Mamba-FETrackのようにMambaを特徴抽出へ使っても、frame間cacheをcarryしない手法がある。
2. **MOTの入力はteacher forcing / free-runningの二択ではない。** `GT`、`accepted detection`、`self prediction`の3種類に分ける必要がある。
3. **低HOTAの大幅な退化はscale問題を含む。** 7/17のHOTA 5.27 / 83.74はscale修正前の参考診断値であり、association単独の根拠にはしない。
4. **scale修正後もassociation差は残る。** P1ではA1 prediction-primaryがHOTA 47.233、A2 observation-primaryが47.910となり、AssA/IDF1改善とIDSW減少を確認した。
5. **state carryにはstateの持越し単位とgradientのdetach単位が必要である。** そのため、associationとcache更新を先に固定・診断し、入力分布混合とTBPTTを後段に置く。

## 2. 比較する軸

| 軸 | 確認すること |
|---|---|
| 学習時のstate | window内だけか、sample/track/videoをまたいでcarryするか |
| 学習時の次入力 | GT、前時刻の予測、観測noise、scheduled samplingのどれか |
| loss | 最終時刻だけか、unroll内の各時刻へ置くか |
| 推論時のstate | frame間hidden/cacheを持つか、前bboxだけを持つか |
| 更新制御 | confidence gate、freeze、reset、re-initializationがあるか |
| MOTへの直接性 | association、accepted detection、ID switchを扱うか |

## 3. 手法比較A: RNN/LSTM・Seq2Seq

| 手法 | 学習時のstate | 次入力 | loss / 推論 | 現行への知見 |
|---|---|---|---|---|
| Vanilla RNN | chunk内でhidden更新。公式LM例ではchunk間carry＋detach | 正解token | 各時刻loss、長系列はTBPTT | stateはcarryしgradientだけ切る設計が基準 |
| LSTM | `h` と `c` をsequence内で更新 | teacher forcing / free-running | 各時刻の出力loss | Mambaのstate設計でもreset/detach単位が重要 |
| Seq2Seq / GRU | encoder stateからdecoderをunroll | 学習はtarget、推論は自己予測 | decoder全時刻loss | train/testの入力分布差を明示する先例 |

### 知見

- 各時刻にlossを置くことは標準的だが、それだけで推論時の入力分布差は解決しない。
- 現行MambaStatefulのwarm-up後7時刻lossを、単独で低HOTAの主因とは断定しない。

## 4. 手法比較B: 予測値を学習入力へ戻す手法

| 手法 | state / unroll | 次入力 | 主な特徴 | 現行への知見 |
|---|---|---|---|---|
| PredRNN / PredRNN++ | sample内でST-LSTM stateを更新 | GTと生成frameをscheduled samplingで混合 | 全future frameへloss | GT-onlyとself-generated inputの差を訓練中から調整 |
| Social GAN | future decoder内でLSTM更新 | 前stepの自己予測 | future全時刻の軌跡loss | free-runningを学習時から扱う。MOT associationはない |
| Trajectron++ | history encoder＋future GRU | sampled actionを再入力 | future全時刻の確率的loss | rolloutの先例。MOTのID管理とは別問題 |
| ARTrack | bbox座標token内のcausal decoder | 推論時に予測tokenを追加 | token loss＋box loss | token内TFとframe間state carryを分ける必要 |

現行MOTでは、入力を次の3種類として扱う。

```text
GT bbox              : teacher-forcedで安定
accepted detection  : detectorとassociationを通った観測
self prediction     : missing時にモデルが生成した入力
```

`accepted detection`はGTでもself predictionでもなく、低品質観測や誤associationを含み得る第三の入力分布である。

## 5. 手法比較C: tracking・Mamba系

| 手法 | 学習時のstate | 推論時のstate / feedback | confidence・reset | MOTへの直接性 |
|---|---|---|---|---|
| Re3 | sample内LSTM unroll、開始時zero | IDごとにLSTM stateと前bbox | 一定長後re-initialization | SOT。ID単位stateの先例だがMOT matchingなし |
| MCITrack | 2 search frameにMamba stateをcarry | hidden state＋template memory | low confidenceでreset、更新gate | SOT。confidence制御の近い先例 |
| MambaLCT | temporal queryをcarryしdetach | 前predictionでcrop、memoryへ追加 | 調査経路ではscore gateなし | SOT。無条件memory更新の対照例 |
| Mamba-FETrack | pair内feature extraction | frame間Mamba cacheはcarryせず前bboxでcrop | Mamba state reset問題は対象外 | SOT。「Mamba使用≠state carry」の例 |
| 現行MambaStateful | 学習はshuffle fixed window、window外carryなし | trackごとMamba cache、accepted detection / self predictionを更新 | 基本self-update、confidence guardなし | MOT。associationとIDSWを直接評価 |

### 知見

- Re3/MCITrackは短いunroll、state初期化、confidence制御の参照になる。
- SOTのconfidenceやtemplate memoryは、MOTのdetector score・IoU・ID lifecycleへそのまま移植できない。
- 現行MambaStatefulは、Mamba predictionをhard IoU associationの主位置へ直接使う点が、SOTとの重要な違いである。

## 6. 調査と実験をつないだEvidence

### 6.1 scale修正前の診断（参考）

7/17のGT入力診断では、Mambaのteacher-forced one-step bbox IoUはzero-motionより良かった（0.920対0.904）。同時に、Mamba prediction-primaryとlast-observed matchingでHOTAに大きな差が出た。

ただし、この時点の推論経路にはscale伝播欠落が含まれていた。後の監査で、HOTA 4.7552付近への退化はscale mismatchで再現・修正でき、corrected baselineは49.666となった。したがって、以下はassociationを検証する動機になった参考診断であり、低HOTAの絶対値や単独の主因証拠には使わない。

| 診断条件（scale修正前） | HOTA | AssA | IDF1 |
|---|---:|---:|---:|
| Mamba予測bboxをprimary | 5.27 | 0.35 | 0.46 |
| 最終観測bboxをprimary | 83.74 | 74.10 | 85.90 |

### 6.2 scale修正後の正式なP1 Evidence

scale修正後、checkpoint、detector、lifecycle、state/cache更新、TrackEval条件を固定し、association主位置だけを比較した。

| 条件 | association | HOTA | AssA | IDF1 | IDSW |
|---|---|---:|---:|---:|---:|
| A1 | prediction-primary | 47.233 | 29.907 | 45.886 | 2,578 |
| A2 | last accepted observation-primary | **47.910** | **30.843** | **47.315** | **2,386** |
| A2 - A1 |  | +0.677 | +0.936 | +1.429 | -192 |

このP1比較が、scale問題とは別に残るassociation差の正式なEvidenceである。HOTA改善は17/25系列で、全系列に一様ではない。

### 6.3 P2 cache update control

P1 A2を固定し、missing時のstate/cache更新とtrusted match gate/resetを比較した。

| 条件 | missing | cache update | HOTA | AssA | IDF1 | IDSW |
|---|---|---|---:|---:|---:|---:|
| B0 | self-update | all | 47.910 | 30.843 | 47.315 | 2,386 |
| B1 | freeze | all | **48.035** | **31.077** | **47.661** | 2,392 |
| B2 | freeze | trustedのみ | 46.962 | 29.510 | 44.179 | 3,836 |
| B3 | freeze | trustedのみ＋reset | 46.855 | 29.380 | 44.177 | 3,833 |

B1はnonfinite state eventを4,515回から115回へ減らした。一方B2/B3では、観測をstate/cacheから単純に除外したことで、古い観測の保持とassociation continuityの問題が大きくなった。

## 7. 調査から得た設計原則

| 知見 | 根拠 | 実験への反映 |
|---|---|---|
| 低HOTAの大幅退化とassociation差は別 | scale修正前4.7552→修正後49.666。修正後もA1/A2差が残る | scale修正をStep 0、P1を正式association診断にする |
| 予測精度とassociation安全性は別 | scale修正後もA1 47.233に対しA2 47.910 | associationをcache・学習方式より先に分離 |
| Mamba使用とstate carryは別 | Mamba-FETrackはframe間cacheをcarryしない | 実装経路でcache carryを確認 |
| accepted detectionは第三の入力分布 | MOTではGTとself predictionの中間に観測がある | GT / accepted detection / self predictionを分ける |
| state carryにはreset/detach設計が必要 | RNN/LSTM公式LM、MCITrack等 | P4を明示的TBPTTとして後段に置く |
| 単純cache gateは危険 | P2 B2/B3でAssA/IDF1低下、IDSW増加 | observation保持とstate更新を分離して再設計 |

## 8. なぜこの順番で進めたか

```text
Step 0: 評価導線・scale・過去baselineを整理
        └─ TrackEval/API parity、scale伝播欠落を修正しcanonical baselineを確立
              ↓
Step 1: 学習・推論の差と関連手法を調査
        └─ GT window学習、track cache推論、RNN/LSTM等の標準例を比較
              ↓
Step 2: associationだけを変更（P1）
        └─ scale修正後のprediction-primaryとobservation-primaryを比較
              ↓
Step 3: missing/cache更新だけを変更（P2）
        └─ self-update、freeze、trusted gate、resetを分離して診断
              ↓
Step 4: 入力分布を変更（P3候補）
        └─ GT / accepted-detection surrogate / self predictionを混合
              ↓
Step 5: 学習時state carryを変更（P4候補）
        └─ track/video単位unroll、detach、TBPTTを導入
```

## 9. 今後の進め方

| 候補 | 次にすること | 得られるもの | 懸念 |
|---|---|---|---|
| A: SAM2最小統合 | 元のMambaStatefulをstrict loadしS0/S1を比較 | corrected stateful baselineのSAM2移植可否 | P1/P2の改善はまだ統合しない |
| B: quality-aware update | observation保持とstate/cache更新を分離 | B2/B3の悪化原因を検証 | 追加specが必要 |
| C: P3入力分布混合 | GT / accepted-detection surrogate / self predictionを学習へ導入 | train/inference mismatchの寄与 | association/cacheと混ざると解釈困難 |
| D: P4明示的TBPTT | track/video単位unrollとdetach | state carry学習の効果 | InferenceParamsのautograd利用は未確認 |

### 提案する順序

1. P1 A2をscale修正後reference、P2 B1をcontamination診断として固定する。
2. B2/B3の単純gate/resetは採用しない。
3. SAM2/SAMURAI最小統合でcorrected stateful baselineを確認する。
4. quality-aware updateを別specで再設計する。
5. P3、P4はA/Bの因果を混ぜない条件で比較する。

## 10. Ask: MTGで確認したいこと

1. scale修正前の5.27 / 83.74を参考診断として残し、正式EvidenceをP1 A1/A2へ置く整理でよいか。
2. P1/P2の結果を現時点のdiagnostic baselineとして固定してよいか。
3. 次はSAM2最小統合を先に行い、その後quality-aware update、P3、P4へ進む順序でよいか。

## 11. 参照ファイル

- [前回MTG議事録](../meetings/2026-07-16-mtg.md)
- [baseline監査とscale修正](../experiments/2026-07-21-p0-75-historical-baseline-audit.md)
- [現行MambaStateful実装マップ](../papers/sequence-learning-survey/comparison/2026-07-17-00-current-implementation-map.md)
- [RNN・LSTM・Seq2Seq比較](../papers/sequence-learning-survey/comparison/2026-07-17-01-rnn-lstm-basics.md)
- [Re3・MCITrack・MambaLCT比較](../papers/sequence-learning-survey/comparison/2026-07-17-02-direct-tracking-comparison.md)
- [補助手法比較](../papers/sequence-learning-survey/comparison/2026-07-21-03-supporting-methods.md)
- [State Carry設計の統合整理](../papers/sequence-learning-survey/comparison/2026-07-21-04-state-carry-synthesis.md)
- [P1 25系列結果](../experiments/2026-07-23-p1-association-separation-25seq.md)
- [P2 cache update control結果](../experiments/2026-07-23-p2-cache-update-control.md)
