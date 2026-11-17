---
project: lab-study-quantization
status: active
summary: 11/20の研究室勉強会「量子化」（90分・演習付き）の準備。ハンズオンとスライド3案（A/B/C）・検査・比較メモが完成。発表者の選択待ち（推奨: B＋Cの演習先行を一部）。
created: 2026-11-13
last_updated: 2026-11-14
---

# 研究室勉強会「量子化」

## 概要

研究室メンバー向けに、量子化の勉強会（90分）を行う。聞き手は全員コンピュータビジョンを専門とするが、タスク（生成、動画認識など）はばらばら。LLMに限らず、CNN・ViT・生成モデルにも通じる一般論として話す。

- 日時: 2026-11-20（締切）
- 形式: 講義の区切りごとに、手元で動かす短い演習を挟む。待ち時間が出ない構成にする。
- 成果物:
  - スライド（研究室テンプレート）。3パターン作って比較し、1つを選ぶか統合する。
  - ハンズオン用リポジトリ（`/mnt/HDD10TB-2/aburatani/quantization_handson`、新規）。研究室の `simple_cnn_training` の書き方に合わせる。
- 成果物の置き場: [papers/2026-11-20-study-session/](papers/2026-11-20-study-session/)

## 現在の状況

- spec承認済み（[spec](specs/2026-11-13-quantization-study-session-spec.md)）。tmux `quant-study`（アプリでは「量子化勉強会」）で作成中。
- 完了: 既存資料の調査と採用判断、原典PDF15本の取得と引用箇所の抽出、ハンズオン（`/mnt/HDD10TB-2/aburatani/quantization_handson`、未コミット）、先行検証・全比較表・QATの事前計算（[結果ログ](experiments/2026-11-13-quantization-handson-results.md)）。新しいvenvでREADMEの手順だけから再現でき、演習①〜④は時間の目安内。
- スライド3案（各本編45枚）を作成し，別エージェントで検査①〜⑤→修正→再検査まで完了（[検査記録](papers/2026-11-20-study-session/2026-11-14-quantization-study-verification.md)，[比較メモ](papers/2026-11-20-study-session/2026-11-14-quantization-study-comparison.md)）。
- 次: 発表者が3案から選ぶ／統合する（目安 11/18）。演習の配布方法を決める。通し練習。
- 本編に影響する発見: 今回の DeiT-Tiny には LLM型の極端な外れ値チャネルがなく（チャネルごとの最大/中央値は最大4.3）、A4での崩れを外れ値だけでは説明できない。SmoothQuant の動機は「原典（LLM）の主張」とし、③のViTの観測とは分けて語る。演習④では、同じINT8でも ResNet18 は速くなり（約0.7倍）、DeiT-Tiny は weight-only で少し遅く dynamic は約16倍遅い（実行時間の約88%が `aten::_int_mm`）。

## マイルストーン

- [x] 構成・演習・検査方針を決める（2026-11-13）
- [x] specを承認する（2026-11-13）
- [x] 既存の公開資料の調査と採用判断（2026-11-13）
- [x] 原典PDF15本の取得と引用箇所の抽出（2026-11-13、[出典メモ](papers/2026-11-20-study-session/2026-11-13-quantization-study-citations.md)）
- [x] ハンズオン用リポジトリを作り、全演習が時間内に動くことを確認する（2026-11-13、[結果ログ](experiments/2026-11-13-quantization-handson-results.md)）
- [x] スライド3案を作り、検査（事実照合・演習との整合・見た目・時間配分・聞き手目線）を通す
- [ ] 3案から1つを選ぶか統合する（目安: 2026-11-18）
- [ ] 通しで確認する（目安: 2026-11-19）
- [ ] 勉強会を行う（2026-11-20）

## 更新履歴

| 日付 | 内容 |
|---|---|
| 2026-11-13 | プロジェクト作成。brainstorm（[2026-11-13-quantization-study-session.md](../../../secretary/notes/brainstorm/2026-11-13-quantization-study-session.md)）とspec案を追加。 |
| 2026-11-13 | specのレビューを受けて改訂（量子化の範囲・時間の測り方・評価条件・後半の絞り込み・調整権限・GPUの割り当て）。承認待ち。 |
| 2026-11-13 | specに既存の公開資料の調査を追加し、GPUの使い方を緩めた。MTG資料の記録対象外にした（AGENTS.mdに追記、作成済みのエントリ1件を削除）。コミットのスコープ名を `quant` にした。 |
| 2026-11-13 | 改訂specを[再レビュー](experiments/2026-11-13-quantization-spec-rereview.md)。前回の主要な懸念はほぼ解消。fake-quantの性能説明・出典と停止条件・端数group・基準checkpoint作成順に修正案を記録。spec本文は未変更、承認待ち。 |
| 2026-11-13 | 再レビューの4点をspecに反映。承認待ち。 |
| 2026-11-13 | specを承認。tmux `quant-study` で作成を開始。 |
| 2026-11-13 | 既存資料の調査（約15分、[調査メモ](papers/2026-11-20-study-session/2026-11-13-quantization-study-existing-materials.md)）。採用判断: 演習①〜③は自作を維持（確認できた資料にfake-quantの対象・粒度・較正3種・固定seedを満たすものがない。MIT Labの中身は未確認）。既存資料は構成の参考・出典付き引用・「さらに学ぶ資料」として使う。演習の下敷きにできるライセンス明記の資料はPozdnyakov（MIT license）のみで、演習④の周辺の参考にとどめる。原典PDF15本を `references/papers/` に取得。ハンズオン用リポジトリの環境（Python 3.12 / torch 2.15 / torchao 0.18 / timm 1.0.31 / bitsandbytes 0.50.2）を作成。 |
| 2026-11-13 | 原典PDF15本の引用箇所を[出典メモ](papers/2026-11-20-study-session/2026-11-13-quantization-study-citations.md)にまとめた（percentileの出典はFP8論文のみ、STE原典は量子化のroundの話ではない、8本の取得元IDは要確認）。ハンズオン完成: 演習①〜④、事前計算（全比較表・QAT・層感度）。QAT（W4A8）は同じ更新回数のfine-tune→PTQより3 seedすべてで高い（ResNet18 93.1 vs 91.2、DeiT-Tiny 93.7 vs 91.8）。 |
| 2026-11-14 | スライド3案（A積み上げ/B問題駆動/C実験先行）を作成。検査①〜⑤→修正→再検査。引用ノートの誤り（JacobはSTEを述べない）と結果ログのBN folding数値（再現せず，再測定）を訂正。結果ログに§7（演習①出力，CPU/GPU差）を追記。比較メモの推奨はB＋Cの演習先行。 |
| 2026-11-14 | 最終ラウンド検査（別エージェント）で必須5件を直し，再確認で未解決の必須0件。比較メモを最終版の枚番号で書き直し。未決: 3案の選択，演習の配布方法，発表者名・所属の書式，ファイル名の日付（2026-11-17 のまま）。未確認: PowerPoint実表示，通し練習，nf4再実行。 |
| 2026-11-16 | 3案の数式をPowerPointの数式オブジェクト（OMML，Fallback画像つき）に置換（A 4枚・B 6枚・C 4枚）。A S9・B S9・C S12 は主役の2式を大きく2行に。別エージェントで見た目③・数値②を検査→修正→再確認（未解決の必須0）。PowerPoint実機での確認枚は[検査記録](papers/2026-11-20-study-session/2026-11-14-quantization-study-verification.md)末尾。 |
