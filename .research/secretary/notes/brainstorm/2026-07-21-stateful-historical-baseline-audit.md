---
date: 2026-07-21
project: sam2-mamba-motion-tracking
source_todo: null
topic: stateful historical baseline audit before P1
status: exploratory
tags: [brainstorm, research, state-carry, baseline, reproducibility]
---

# Stateful過去HOTA 47と現行HOTA 4.7の乖離調査

## 読み込んだ文脈

- 2026-07-02 MTG議事録: State carry 100epochでそこそこの性能、validation/HOTA評価を5epochごとに導入する方針。
- 2026-07-21 P0.5: 既存25系列出力のMambaStateful HOTA 47.293、同じ既存出力の3系列HOTA 52.037。ただしcheckpoint provenanceは不明。
- 2026-07-21再現: 現行epoch1、現行epoch100、TrackEval組み込み前親commitの25epoch新規学習はいずれも3系列HOTA 4.7552。
- ユーザー提供の7/2 MTG時Comet画面: HOTA 0.47、DetA約0.75、AssA約0.30で、P0.5の47.293と整合。

## 問い

7/2時点で実在したHOTA約47の条件と、現在のHOTA約4.7の条件の差は何か。P1〜P3より先に解明すべきか。

## 仮説候補

1. 過去runが別checkpoint、別detector入力、別association、または未保存作業ツリーで生成された。
2. 47結果は現行epoch100の結果ではなく、過去のepoch25系checkpoint/outputだった。
3. 27b74b2のvalidation追加だけが原因である可能性は、親commit25epoch再現が4.7552だったため低い。
4. TrackEval計算差ではなく、追跡outputそのものの差である可能性が高い。

## 方針判断

P1〜P3の後回しにして長期調査するのではなく、P1の前に短いP0.75 historical-baseline auditを挿入する。理由は、P1でHOTAが改善しても「association改善」なのか「過去runの条件復元」なのか解釈できなくなるため。一方、P1はGT診断（prediction matching HOTA 5.27、last-observed matching HOTA 83.74）から独立した因果仮説があるため、監査が完全に詰まった場合は現行4.7552をcanonical baselineとしてP1を進められる。

## 推奨する次アクション候補

1. Comet experiment keyとartifactから、7/2 runのcommit、config、epoch、detector path、checkpoint、TrackEval summary/outputを回収する。
2. 回収できた旧outputを現行TrackEvalで再評価し、47.293が同じ条件で再現するか確認する。
3. 旧checkpointが無い場合は、47.293を「過去outputの参考値」と固定し、現行4.7552をcanonical baselineとしてP1を診断用に実行する。
4. P2/P3は、P0.75とP1の結果を記録した後に進める。

## 未解決の問い

- Cometに追跡outputまたはcheckpoint artifactが残っているか。
- 7/2 runの実行commitは何か。
- 過去runのdetector入力と現在のdetector入力は同一か。
- 47結果のassociationが現行prediction-primaryと同一か。
