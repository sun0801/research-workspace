---
date: 2026-09-25
project: sam2-mamba-motion-tracking
source: checkpoint-diagnostic
status: exploratory
tags: [experiment, p4a, loss, sequence-analysis, sam2, failure-analysis, cross-condition]
---

# P4a checkpoint lossとSAM2 sequence失敗の探索的対応付け

## 位置づけ

このメモは、非shuffle checkpointのMamba lossと、既存のshuffle版SAM2統合結果を横断的に照合した探索記録である。checkpoint条件とSAM2統合条件が異なるため、同一条件の性能差や因果関係を示す主分析には用いない。

主目的である「SAM2＋Mambaがどのsequenceで失敗しているか」の分析は、shuffle比較から切り離し、`2026-09-25-sam2-sequence-failure-analysis.md` で整理する。

## 目的

checkpoint後のMamba予測lossが大きいsequenceを特定し、SAM2＋Mambaのsequence別失敗可視化候補を絞る。

## 実施内容

- 対象checkpoint: 非shuffle P4a epoch100
- checkpoint: `mamba_stateful_tbptt_p4a_full/p4a_full_100ep_20260903/epoch100.pth`
- split: DanceTrack val
- 条件: `loss_start_index=4`、`tbptt_length=12`、Smooth L1、既存P4aのforward/state carryを再利用
- 対象: 272 tracks、4,817 unroll samples、paddingをlossから除外
- trajectory JSONはsequence名を保持していないため、元DanceTrack GTのobject順とfilter規則からtrack ID→sequence対応を復元した

## 非shuffle checkpointの高loss sequence

| sequence | mean Smooth L1 | 備考 |
|---|---:|---|
| dancetrack0097 | 0.0894 | SAM2 HOTAは0.9057で高い |
| dancetrack0018 | 0.0814 | SAM2 HOTAは0.8013 |
| dancetrack0094 | 0.0753 | SAM2 HOTA 0.5363、失敗候補 |
| dancetrack0073 | 0.0634 | SAM2 HOTA 0.6942 |
| dancetrack0043 | 0.0608 | SAM2 HOTA 0.7140 |

track単位では、`dancetrack0073/track177`、`dancetrack0094/track257`、`dancetrack0058/track148`などが高lossだった。

## SAM2失敗との比較

既存のshuffle P4a SAM2統合結果（25系列）のHOTA最下位は以下だった。

| sequence | HOTA | IDF1 | IDSW | Mamba loss |
|---|---:|---:|---:|---:|
| dancetrack0026 | 0.3359 | 0.3190 | 168 | 0.0341 |
| dancetrack0014 | 0.3670 | 0.3564 | 132 | 0.0304 |
| dancetrack0063 | 0.4463 | 0.4267 | 84 | 0.0279 |
| dancetrack0041 | 0.4894 | 0.4598 | 222 | 0.0300 |
| dancetrack0094 | 0.5363 | 0.4806 | 146 | 0.0753 |

## 探索的解釈

- Mamba loss上位とSAM2 HOTA下位は一致しない。
- `dancetrack0094`は両方に現れるため、Mamba予測誤差とSAM2追跡失敗の対応候補。
- `dancetrack0026`、`0014`、`0063`はMamba lossが高くないにもかかわらずSAM2 HOTAが低く、SAM2 memory・association・検出欠損などの下流要因を調べる候補。
- `dancetrack0097`、`0018`はMamba lossが高いがSAM2 HOTAが比較的高く、SAM2側が予測誤差を吸収している比較候補。

したがって、現時点では可視化候補をloss上位だけでなく、次の3群から探索的に選べる。ただし、以下の分類はshuffle版SAM2出力と非shuffle lossの組合せに基づくため、正式な原因分類ではない。

1. Mamba・SAM2双方で失敗する群: `dancetrack0094`
2. SAM2のみ失敗する群: `dancetrack0026`, `dancetrack0014`, `dancetrack0063`
3. Mamba lossは高いがSAM2が維持する群: `dancetrack0097`, `dancetrack0018`

## 次に同一条件で確認すること

- 正式な基準runを固定し、そのrunのsequence別HOTA / AssA / IDF1 / IDSWを抽出する
- 同じrunのcandidate debugとMamba lossをsequence・track・frameで対応付ける
- 高loss区間、ID switch、missing、matching変更を同一frame軸で可視化する
- lossとHOTA / IDSWの相関は、同一条件のデータだけで定量化する

## 関連ファイル

- `meetings/2026-09-18-mtg.md`
- `experiments/2026-09-18-p4a-shuffle-sam2-trackeval.md`
- `specs/2026-09-24-yolo-mamba-shuffle-comparison-spec.md`
- `experiments/2026-09-25-sam2-sequence-failure-analysis.md`
