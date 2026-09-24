---
date: 2026-09-25
project: sam2-mamba-motion-tracking
status: exploratory
tags: [experiment, sam2, sequence-analysis, failure-analysis, non-shuffle, canonical]
---

# SAM2＋Mamba sequence別失敗分析

## 目的

SAM2＋Mambaの平均性能が十分に出ていない理由を、sequence単位・frame単位の失敗例から確認する。shuffle/non-shuffleの優劣を比較する資料ではない。

## 分析条件

主分析の基準runは、non-shuffle P4a epoch100のSAM2統合結果に固定する。

- SAM2 run: `sam2_p4a_epoch100_25seq_20260904`
- 対象: DanceTrack validation 25系列
- TrackEval aggregate HOTA: `54.391`
- 対応するTrackEval正本: `/mnt/HDD10TB-2/aburatani/TrackEval/data/trackers/dancetrack/val/sam2_p4a_epoch100_25seq_20260904/pedestrian_summary.txt`

shuffle版の結果、loss、candidate debugは、この主分析の条件には混ぜない。shuffleに関する比較は、`2026-09-25-yolo-mamba-shuffle-comparison.md` および既存のshuffle評価ログで扱う。

## 既存情報の扱い

既存の以下のメモと図は、shuffle版SAM2出力とnon-shuffle lossを横断した探索記録である。候補発見には使えるが、正式な原因分類や条件間の性能差の根拠にはしない。

- `2026-09-25-p4a-loss-sequence-comparison.md`
- `2026-09-25-checkpoint-loss-sequence-failure-linkage.md`
- `2026-09-25-sam2-sequence-visualization-candidates.md`
- `2026-09-25-sam2-sequence-candidate-figures-corrected.md`

これらの探索では、Mamba loss上位とSAM2 HOTA下位が一致しない傾向が見えている。ただし、SAM2側がshuffle runであるため、現時点では仮説として扱う。

## 解析項目

| 段階 | 確認内容 | 主な出力 |
|---|---|---|
| 1 | 基準runのsequence別HOTA / AssA / IDF1 / IDSW | 低性能sequenceの一覧 |
| 2 | 低性能sequenceのID switch・missing・matching変更 | 失敗frameと遷移 |
| 3 | 同じ基準checkpointのMamba lossをsequence / track / chunkへ対応付け | Mamba予測誤差の分布 |
| 4 | GT、Mamba予測、SAM2出力、candidate IoUを同一frame軸で可視化 | 代表失敗例の図 |
| 5 | Mamba起因、SAM2 / association起因、検出・欠損起因を切り分け | 原因仮説 |

## 代表候補の選び方

まず基準runのsequence別HOTA下位から代表を選ぶ。その後、同一条件のMamba loss、IDSW、missing、candidate IoUを確認する。lossが高いsequenceだけを先に選ばない。

最低限、以下の3タイプを同一条件で比較する。

1. SAM2 HOTAが低く、Mamba lossも高いsequence
2. Mamba lossは高くないが、SAM2 HOTAが低いsequence
3. Mamba lossは高いが、SAM2 HOTAが維持されるsequence

## 未完了

- 基準runのsequence別TrackEval行を抽出する
- 基準runに対応するcandidate debugの有無とパスを確認する
- 基準runのMamba lossとtrack / frameを対応付ける
- 代表3タイプの同一frame軸の可視化を生成する
- shuffle版候補図を正式分析用の図として再利用しないことを確認する

## 関連

- `meetings/2026-09-18-mtg.md`
- `experiments/2026-09-04-l0-p4a-tracker-sam2-comparison.md`
- `experiments/2026-09-18-p4a-shuffle-sam2-trackeval.md`
- `specs/2026-09-24-yolo-mamba-shuffle-comparison-spec.md`
