---
date: 2026-09-25
project: sam2-mamba-motion-tracking
source: candidate-debug
status: exploratory
tags: [experiment, sam2, visualization, sequence-analysis, failure-analysis, shuffle]
---

# SAM2＋Mamba sequence別可視化候補

## 位置づけ

この候補リストは、`sam2_p4a_shuffle_epoch100_25seq_20260917` のcandidate debugから抽出したshuffle run限定の探索結果である。shuffle比較の結論や、SAM2＋Mambaの正式なsequence失敗分析の主証拠にはしない。

正式分析では、non-shuffle P4a epoch100の基準run `sam2_p4a_epoch100_25seq_20260904` など、採用する単一条件を固定して候補を再抽出する。

## 対象

shuffle P4a epoch100のSAM2統合runにあるcandidate debug CSVから、低い選択IoUとmissing/stateful stepが集中するframeを抽出した。

## 可視化候補

| 群 | sequence | 主なframe候補 | 目的 |
|---|---|---|---|
| 共通失敗 | dancetrack0094 | 40–42, 228–229, 518 | Mamba高lossとSAM2失敗の対応確認 |
| SAM2側候補 | dancetrack0026 | 222–223 | 複数objectの同時低IoUと対応崩れの確認 |
| SAM2側候補 | dancetrack0014 | 60–63, 834–842, 1126–1127 | 長いsequence内の誤対応・回復過程の確認 |
| SAM2側候補 | dancetrack0063 | 96–106, 600–601, 689–709 | low IoUとstateful stepの関係確認 |
| Mamba誤差吸収候補 | dancetrack0097 | 610, 1064–1069 | Mamba loss高だがsequence HOTA高の理由確認 |
| Mamba誤差吸収候補 | dancetrack0018 | 45–72, 106, 128 | Mamba loss高だがSAM2が維持する区間確認 |

## 最初に見る3系列

1. `dancetrack0094`: 共通失敗の代表
2. `dancetrack0026`: Mamba lossが低いのにSAM2 HOTAが最悪の代表
3. `dancetrack0097`: Mamba lossが高いのにSAM2 HOTAが高い代表

各系列で、候補frameの前後20〜30 frameを対象に、GT bbox、Mamba予測、SAM2出力bbox/mask、candidate IoU、missing、stateful step、ID switchを同時に確認する。

## 注意

- `selected_sam_iou=0`だけではID switch原因を断定しない。candidate bbox、GT、matchingログを併せて確認する。
- candidate debugの`obj_id`はSAM2側のobject indexであり、DanceTrack GT IDと同一とは限らない。
- 画像・動画上の見た目を確認するまで、遮蔽・交差・検出欠損などの原因ラベルは付与しない。

## 関連

- `experiments/2026-09-25-p4a-loss-sequence-comparison.md`
- `experiments/2026-09-18-p4a-shuffle-sam2-trackeval.md`
- `materials/2026-07-27-miru-qualitative-candidate-selection.md`
- `experiments/2026-09-25-sam2-sequence-failure-analysis.md`
