---
project: lab-study-quantization
status: active
summary: 11/20の研究室勉強会「量子化」（90分・演習付き）の準備。spec承認済み、tmux quant-study で作成中。
created: 2026-11-13
last_updated: 2026-11-13
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

壁打ちで構成・演習・検査の方針を決め、spec案（[specs/2026-11-13-quantization-study-session-spec.md](specs/2026-11-13-quantization-study-session-spec.md)）を作成した。2026-11-13にユーザーが承認。Remote Control付きの別セッション（tmux `quant-study`、アプリでは「量子化勉強会」）で作成中。

## マイルストーン

- [x] 構成・演習・検査方針を決める（2026-11-13）
- [x] specを承認する（2026-11-13）
- [ ] ハンズオン用リポジトリを作り、全演習が時間内に動くことを確認する
- [ ] スライド3案を作り、検査（事実照合・演習との整合・見た目・時間配分・聞き手目線）を通す
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
