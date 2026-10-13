---
date: 2026-10-12
project: sam2-mamba-motion-tracking
source_todo: 検出器checkpointを公式版（Objects365→COCO、AP 64.1）に差し替え、valで比較する / CoIの寄与が論文より小さい原因（AssA低下）を調べる
topic: sam2mot-val-improvement-plan
status: exploratory
tags: [brainstorm, research, sam2mot, dancetrack]
---

# SAM2MOTのvalを引き上げる進め方（検出器差し替え・CoIのAssA低下）

## 読み込んだ文脈

- 2026-10-09 MTG: valとtestの差は1ポイント程度なので、まずvalを引き上げる。testは毎回提出せず確認用に使う。候補は検出器checkpointとCoI。
- test結果（`experiments/2026-10-09-sam2mot-test-runs.md`）: S4 HOTA 70.6（論文 75.5）。CoI ΔHOTA +3.6（論文 +5.9）、ΔAssA −2.0。ΔMOTA +17.9 は論文 +17.7 と一致。MOTAはS2時点で論文より8.4低い。
- A7切り分け（`experiments/2026-09-30-sam2mot-s3-a7-ablation.md`）: A7は既定で無効化済み。A6のみでもAssA −1.16。低下は0019 −13.8、0063 −11.2、0026 −8.0に集中し、0014・0034・0077では+5〜6。
- 実装リポジトリ: o365tococoの重みはダウンロード済み、`--checkpoint` で切替可能。検出はdancetrack0026の100フレーム分のみ存在した。
- 0026の100フレームでは、det conf 0.5でのrecallがo365tococo 59.9%、3x_coco 49.9%。スコアの出方が検出器で異なる。

## 問い

- 検出器を公式README版（o365tococo）にすると、valの各段（S1〜S4）はどう変わるか。S2時点のMOTA差（−8.4）は検出器で説明できるか。
- CoIでAssAが下がるのは、除外判定の誤り（正しいトラックをBと判定）か、正しい除外の後のトラック分断か、IDの入れ替わりか。

## 実験・実装案

### A. 検出器差し替え（先行）

- 変えるのは検出器のみ。コード、det conf 0.5、A7無効、Q-R補正方式、追跡GPU 0は固定。
- S1〜S4すべてを回し、段ごとの寄与とS2のMOTA差の変化を見る。
- 閾値0.5は論文値のまま固定し、合わせ込みはしない。
- 採否基準の案: val S4 HOTAが+1以上なら主設定にし、spec A8の行に理由を記録する（結果を見る前に確定させる）。

### B. CoIのAssA低下の診断（Aがある程度進んでから）

- 既存のS2・S3（A6のみ）出力とGTで、(1) 除外したBが本当にずれたトラックだったか（除外の正解率）、(2) AssA低下を分断（lost削除→再追加）とIDの入れ替わりに分解、を調べる。
- 判定誤り → A6の範囲（Stage 1を厳しく、Stage 2必須など）。判定は正しいがトラックが消える → A9（メモリフレーム選択）。
- 改善案の実行は、Aで決まった検出器の上で行う。

## 今回見えた方向性

- ユーザー判断: Aは空いているGPU 2枚を使って開始。Bは並行すると分かりにくくなるので、Aがある程度進んでから着手する。
- mmdet用venv（torch 2.1.0+cu121）はBlackwell（GPU 0、sm_120）に非対応のため、検出はGPU 1のみ。追跡（S1〜S4）はvalの既存runと同じGPU 0で、検出が系列ごとに完了するのを待って順に回す構成にした。
- S1のtest提出は、提出ファイルが既にあり計算コストがないため、提出を推奨（論文と比較できるのはtestだけで、MOTA差がbaselineとAddのどちらで生じるかを切り分けられる）。

## 次アクション候補

- A完了後: S1〜S4のval結果を `experiments/` に記録し、3x_cocoとの比較と採否判断を行う。
- S1 test（`results/submissions/test_s1/tracker.zip`）をCodaBenchへ提出する（ユーザー作業）。
- Aの結果を見てBの分析に着手する。

## 未解決の問い

- 採否基準（+1）の確定。
- o365tococoで主設定を変えた場合、test再提出を行うタイミング。
- 論文本文（COCO pretrained）と公式README（Objects365→COCO）のどちらを「再現条件」とするかの扱い。

## 関連ファイル

- `.research/lab/projects/sam2-mamba-motion-tracking/meetings/2026-10-09-mtg.md`
- `.research/lab/projects/sam2-mamba-motion-tracking/experiments/2026-10-09-sam2mot-test-runs.md`
- `.research/lab/projects/sam2-mamba-motion-tracking/experiments/2026-09-30-sam2mot-s3-a7-ablation.md`
- `.research/lab/projects/sam2-mamba-motion-tracking/specs/2026-09-08-sam2mot-reproduction-spec.md`
- `.research/secretary/notes/brainstorm/2026-10-06-sam2mot-performance-gap-investigation.md`
