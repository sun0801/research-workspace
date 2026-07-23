---
date: 2026-07-23
project: sam2-mamba-motion-tracking
type: meeting-materials
topic: p1-p2-results-and-next-direction
status: draft
target_meeting: null
notion_url: null
notion_export: null
tags: [meeting-materials, research, state-carry, association, cache-update, sam2]
---

# 2026-07-23 MTG資料: P1/P2結果と次の研究方針

## 0. 今日のMTGで先生に相談したいこと

1. scale修正後のP1 A2を、state carry側のreferenceとして固定してよいか。
2. P2 B1を「missing self-updateがstate instabilityの一因であることを支持する診断」として位置づけてよいか。
3. B2/B3の単純trusted gate/resetは採用せず、SAM2/SAMURAI最小統合を先に進めてよいか。
4. quality-aware observation保持とMamba state/cache更新の分離を、B2/B3とは別specで検討する順序でよいか。

## 1. 現時点の結論

- HOTA 4.7552付近への大幅な退化は、主に学習時のbbox/delta scaleがtracker推論へ伝播されていなかったことによる。scale修正後、同一条件でHOTA 4.7552から49.666へ回復した。
- したがって、7/17のHOTA 5.27 / 83.74はscale修正前の参考診断値であり、canonical baselineや低HOTAの主因を示す正式な根拠には使わない。
- scale修正後のP1では、association主位置だけを変更し、25系列でA1 prediction-primaryからA2 observation-primaryへ変更すると、HOTA 47.233から47.910へ改善した。AssA、IDF1、IDSWも改善したため、scale問題とは別にassociationの残存劣化を支持する。
- P2ではmissing freeze（B1）がnonfinite state eventを4,515回から115回へ減らし、HOTA/AssA/IDF1を小さく改善した。一方、単純trusted gate/reset（B2/B3）はassociationを悪化させた。

## 2. 前回MTGからの1週間の進行

| 日付 | 段階 | 実施内容 | 判断・次へ進んだ理由 |
|---|---|---|---|
| 7/16 | 方針決定 | epoch間MOT metrics不変を、TrackEvalではなくtracker推論側で切り分ける方針を決定。小規模過学習とRNN/LSTMのteacher forcing/free-running調査を設定。 | 学習・推論・評価を分離する必要を確認。 |
| 7/17 | state carry診断 | 1動画学習、同一動画推論、GT bbox入力評価、train/inference経路分析を実施。 | HOTA 5.27 / 83.74の差を観測したが、後の監査でscale伝播欠落が判明。値はpre-fix診断として保留。 |
| 7/17–7/21 | 関連手法調査 | RNN/LSTM、Seq2Seq、Re3、MCITrack、MambaLCT、PredRNN等を比較。 | association、cache更新、入力分布、TBPTTを分離して検証する順序を整理。 |
| 7/21 | baseline監査 | HOTA 4.7552の再現、過去HOTA 47系とのprovenance比較、scale伝播欠落の修正検証、P0.5比較を実施。 | scale修正後の導線をcanonical baselineとしてP1へ進む。 |
| 7/22 | P1 3系列 | A1 prediction-primaryとA2 observation-primaryだけを比較。 | A2改善を確認し、A2を固定してP2へ進む。 |
| 7/23 | P1 25系列・P2 | P1を25系列へ拡張し、B0〜B3を比較。 | P1の残存association差と、P2のfreeze/gate/resetの効果を分離した。 |

重要なのは、scale伝播欠落によるbaseline退化と、scale修正後にも残るassociation差を別の問題として扱うことである。P1/P2の正式な比較はscale修正後の条件で実施している。

## 3. Evidence: baselineのscale修正

| 条件 | 3系列HOTA | 解釈 |
|---|---:|---|
| 修正前の推論導線 | 4.7552 | bbox/delta scaleの伝播欠落を含むregression baseline |
| scale伝播修正版 | 49.666 | corrected baseline anchor |
| 7/2保存作業ツリー | 49.666 | scale修正版と一致 |

過去の25系列HOTA 47.293、3系列HOTA 52.037はprovenanceが完全ではないためhistorical referenceとして扱い、P1の成功基準には使わない。

## 4. Evidence: P1 association separation

scale修正後、checkpoint、detector、lifecycle、state/cache更新、TrackEval条件を固定し、association主位置だけを変更した。

| 条件 | association | HOTA | AssA | IDF1 | IDSW |
|---|---|---:|---:|---:|---:|
| A1 | prediction-primary | 47.233 | 29.907 | 45.886 | 2,578 |
| A2 | last accepted observation-primary | **47.910** | **30.843** | **47.315** | **2,386** |
| A2 - A1 |  | +0.677 | +0.936 | +1.429 | -192 |

- HOTA改善: 17/25系列
- AssA改善: 19/25系列
- IDF1改善: 17/25系列
- 改善は一様ではなく、`dancetrack0097`ではA2のHOTAがA1より -0.103

## 5. Evidence: P2 cache update control

P1 A2を固定し、missing時のstate/cache更新とdetector matchの品質制御を比較した。

| 条件 | missing | cache update | reset | HOTA | AssA | IDF1 | IDSW |
|---|---|---|---:|---:|---:|---:|---:|
| B0 | self-update | all | 0 | 47.910 | 30.843 | 47.315 | 2,386 |
| B1 | freeze | all | 0 | **48.035** | **31.077** | **47.661** | 2,392 |
| B2 | freeze | trustedのみ | 0 | 46.962 | 29.510 | 44.179 | 3,836 |
| B3 | freeze | trustedのみ | 5回連続untrusted後 | 46.855 | 29.380 | 44.177 | 3,833 |

### State/cache診断

| 条件 | self-update | freeze | untrusted match | reset | nonfinite events |
|---|---:|---:|---:|---:|---:|
| B0 | 37,833 | 0 | 0 | 0 | 4,515 |
| B1 | 0 | 36,157 | 0 | 0 | 115 |
| B2 | 0 | 50,742 | 19,898 | 0 | 0 |
| B3 | 0 | 50,634 | 19,877 | 2,874 | 0 |

## 6. Interpretation

### 今回支持される見立て

- scale修正後もA1/A2に差が残るため、predictionをhard IoU matchingのprimary位置に使う設計はassociation退化へ寄与する可能性がある。
- missing予測をhistory/cacheへ継続投入することは、state driftまたはnonfinite stateの一因である可能性がある。
- detector matchを単純にtrusted / untrustedで分け、untrusted時にstate/cacheを止めるだけでは、観測が古くなりassociation continuityを損なう。

### まだ確定できないこと

- P1の改善が長期occlusionや別splitでも同じ大きさで得られるか。
- B1のnonfinite event削減が、最終tracking性能の安定改善につながる条件。
- B2/B3の悪化がthresholdの問題か、観測保持とstate更新を同じgateで制御した設計の問題か。
- P1/P2の効果がSAM2/SAMURAIのmask候補分布でも再現するか。

## 7. 次に進む候補

1. P1 A2をscale修正後のreferenceとして固定する。
2. B1はcontamination抑制の診断結果として保存し、最終手法とは扱わない。
3. B2/B3の単純trusted gate/resetは採用しない。
4. SAM2/SAMURAIで元のMambaStatefulをstrict loadする最小統合（S0/S1）を実施する。
5. その後、観測bboxの保持とMamba state/cache更新を分離したquality-aware updateを別specで検討する。
6. 入力分布混合（P3）と明示的stateful unroll/TBPTT（P4）は、上記の因果を混ぜない条件で後段に比較する。

## 8. 今回言えること / まだ言えないこと

### 今回言えること

- 低HOTAの大幅な退化はscale伝播欠落で再現・修正できた。
- scale修正後のP1で、association主位置の差による残存劣化を25系列で診断できた。
- P2 B1はstate instabilityの一因を抑制するが、改善は限定的である。
- 単純trusted gate/resetは現条件では採用しない。

### まだ言えないこと

- state carry型Mambaがsliding window型より優れている、または劣っているという結論。
- P1/P2の改善をそのままSAM2/SAMURAIの改善と主張すること。
- HOTAだけからhidden state contaminationの大きさを定量化すること。

## 9. 参照ファイル

- [前回MTG議事録](../meetings/2026-07-16-mtg.md)
- [baseline監査とscale修正](../experiments/2026-07-21-p0-75-historical-baseline-audit.md)
- [P1 25系列結果](../experiments/2026-07-23-p1-association-separation-25seq.md)
- [P2 cache update control結果](../experiments/2026-07-23-p2-cache-update-control.md)
- [P2 spec](../specs/2026-07-23-p2-cache-update-control-spec.md)
- [SAM2最小統合spec](../specs/2026-07-23-sam2-stateful-mamba-minimal-integration-spec.md)
- [時系列学習手法の比較資料](2026-07-23-sequence-learning-comparison-and-roadmap-mtg-materials.md)
