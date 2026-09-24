---
date: 2026-09-25
project: sam2-mamba-motion-tracking
source: candidate-debug-visualization
status: exploratory
tags: [experiment, sam2, visualization, figures, shuffle]
---

# SAM2＋Mamba sequence候補の確認用図

## 位置づけ

これらの図は `sam2_p4a_shuffle_epoch100_25seq_20260917` 由来の探索用contact sheetであり、正式なsequence失敗分析の確定図ではない。shuffle runに紐づく候補確認図として保持する。

代表3系列について、候補frame前後の画像に以下を重ねたcontact sheetを生成した。

- 緑: DanceTrack GT bbox
- 赤: SAM2 selected bbox
- 青: candidate debugに記録されたMamba予測bbox（存在する場合）

## 図

- [dancetrack0094 contact sheet](figures/2026-09-25-sam2-sequence-candidates/dancetrack0094_candidate_contact_sheet.jpg)
- [dancetrack0026 contact sheet](figures/2026-09-25-sam2-sequence-candidates/dancetrack0026_candidate_contact_sheet.jpg)
- [dancetrack0097 contact sheet](figures/2026-09-25-sam2-sequence-candidates/dancetrack0097_candidate_contact_sheet.jpg)

## 対応

- `dancetrack0094`: frame 39–43。loss高・SAM2低HOTAの共通候補。
- `dancetrack0026`: frame 220–224。Mamba lossは低いがSAM2 HOTAが最も低い候補。
- `dancetrack0097`: frame 608–612。Mamba lossは高いがSAM2 HOTAが高い候補。

## 注意

この図は候補確認用であり、赤いbboxの選択誤りだけからID switch原因を断定しない。次段階ではframe範囲を広げ、candidate IoU、matching、missing、ID switchを時系列で併記する。
