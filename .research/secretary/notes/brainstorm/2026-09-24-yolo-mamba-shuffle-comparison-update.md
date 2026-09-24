---
date: 2026-09-24
project: sam2-mamba-motion-tracking
source_todo: YOLO＋Mambaでshuffle / non-shuffleを同一条件で比較する
topic: YOLO＋Mamba shuffle / non-shuffle比較の方針更新
status: exploratory
tags: [brainstorm, research, yolo, mamba, shuffle, tracking, update]
---

# YOLO＋Mamba shuffle / non-shuffle比較の方針更新

## 決定した方向性

前回のSAM2統合比較に使用したshuffle/non-shuffleの学習済みMamba checkpointを再利用できるため、初期スコープでは新規再学習を行わない。

画像や既存TrackEval summaryを再利用するのではなく、SAM2統合時に実際にロードしたMamba checkpointをYOLO＋Mamba推論へ投入し、YOLO側のtracking結果を新たに評価する。

## 実施内容

1. non-shuffle / shuffleの実checkpointを実行ログまたはmanifestから特定する。
2. YOLO検出結果、matching、missing mode、threshold、TrackEval条件を両条件で固定する。
3. single-sequence smokeでcheckpoint load、入力scale、state finite性、出力形式を確認する。
4. 問題がなければDanceTrack val 25系列で両条件を推論・評価する。

主比較のmissing modeは既存P4a baselineとの連続性から`self_update`に固定し、`freeze`は別の感度分析へ分離する。

## 新規学習へ進む条件

- 実checkpointを特定できない。
- YOLO＋Mamba側とSAM2統合側でMambaの入力形式、scale、architectureが一致しない。
- checkpointのprovenance、config、commitが不明で対照性を保証できない。
- YOLO検出ノイズを含む入力でMambaを学習する別の研究問いを検証する。

この場合でも、まず同一初期重み・single GPU・1 seedのpaired再学習を行い、結果を見てから3 seedへ拡張する。

## 昇格先

- `.research/lab/projects/sam2-mamba-motion-tracking/specs/2026-09-24-yolo-mamba-shuffle-comparison-spec.md`

## 関連brainstorm

- `.research/secretary/notes/brainstorm/2026-09-24-yolo-mamba-shuffle-comparison.md`
