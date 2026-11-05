---
project: kaggle-name-that-llm
status: active
summary: CPU実験runner実装と5件のテストが完了。公式データ取得済み、実学習は未開始。新規CLI用の引き継ぎを保存。
created: 2026-11-02
last_updated: 2026-11-06
---

# Kaggle — Name That LLM

## 概要

18種類のLLMの生成文章からモデル名を識別するコンペ。ユーザーは主に方針・制約を伝え、AIが調査・記録・承認済み範囲の実装を担当する。知見と作業履歴をMarkdownで共有して会話をまたいで再開する。

- [公式コンペ](https://www.kaggle.com/competitions/name-that-llm)
- [コードの作業場所](../../../../../kaggle/name-that-llm/README.md)
- [環境・認証・操作ガイド](../../../../../kaggle/README.md)

## 現在の状況

- 実装・データ・環境はResearch Workspaceの外の `/mnt/HDD10TB-2/aburatani/kaggle/`、研究記録はこの `.research/` に置く。2026-11-02のユーザー指摘に合わせて移設済み。

- 公式Kaggle CLI 2.2.5を `/mnt/HDD10TB-2/aburatani/kaggle/.venv/` に導入し、`uv.lock` で依存を固定。
- 公式MCPへ接続。ローカルの収集ツールとCodexのネイティブツールの両方で概要取得に成功。
- トークン認証後、収集9項目すべて成功。Notebook人気/新着とデータファイル一覧も取得できた。一覧は先頭ページ。
- 有力Discussion 4件と公開Notebook 3本を精読。Starter v4 / Two-stage LoRA v2 / nlm-v27 v1と取得コードの一致を確認。コードは未実行。
- 比較では、Starterのprompt-grouped CV、二段階LoRAの再現条件、nlm-v27の有効構成・時間制約・CV上の注意を整理。CPU基準の次に8Bを検討する順を提案。
- APIトークンでローカルMCPクライアントと公式CLIの認証付き取得を確認。この会話のネイティブMCP接続は再接続後の認証確認が必要。
- CPU自動実験はspecを参照するgoalの開始指示を受け、runner・独立検査・baseline設定を実装済み。2026-11-06に合成データの5テストが成功。公式train/test/sample取得済みだが、実データのCV・学習は未開始。
- ユーザーは新規CLIを起動済み。[引き継ぎ記録](experiments/2026-11-06-cpu-cycle-handoff.md)に再開コマンドとgoal文を保存。2026-11-06の確認時点で、この会話のgoalは未設定、実験workerは不在。
- GPU段階の141/142選定条件も診断記録へ保存。初回specはCPUのみで、GPU学習・提出は未実施。

## マイルストーン

- [x] Kaggle共通ディレクトリとName That LLMプロジェクトを作成
- [x] 公式CLI・MCP設定・収集コマンドと共同作業スキルを整備
- [x] 初期のコンペ調査と有力資料の知見を保存
- [x] 公開Notebook 3本の精読と手法・検証条件・計算資源の比較を保存

## 調査・判断の索引

- [初期調査と資料台帳](experiments/2026-11-02-competition-intelligence.md)
- [共同作業と自動化の設計メモ](../../../secretary/notes/brainstorm/2026-11-02-kaggle-collaboration-setup.md)

- [認証トラブルの診断とトークン方式](experiments/2026-11-02-kaggle-auth-troubleshooting.md)

- [認証後のNotebook取得確認](experiments/2026-11-02-authenticated-notebook-discovery.md)

- [公開Notebook 3本の精読比較](experiments/2026-11-02-public-notebook-comparison.md)

- [CPU自動実験サイクルspec](specs/2026-11-05-cpu-autonomous-cycle-spec.md)

- [CPU実装の検証結果・CLIへの引き継ぎ](experiments/2026-11-06-cpu-cycle-handoff.md)

## 共同作業の引き継ぎ

ユーザーの希望: Kaggleコンペを複数管理したい。今回はNameThatLLM。基本作業はAIへ委ね、各タブの有力資料から知見を蓄積し、情報共有・指示出し・自動化を整える。

現時点の前提: チャット＋Markdownを入口にする。資料の主張・AIの推測・自分たちの実測を分ける。特定の予算、GPU、順位目標、定期実行時刻は未指定。

次は新規CLIで引き継ぎ記録と承認済みspecを読み、既存コードと取得済みデータから実験を開始する。実装開始承認は受領済み。初回範囲はCPU、baseline + 最大5候補、実験2時間、メモリ制限付き。既存workerとcycleを確認してから再開し、GPU段階へ自動で拡張しない。

## 更新履歴

| 日付 | 内容 |
|---|---|
| 2026-11-02 | ユーザー依頼で新規作成。共通環境・公式MCP・調査ツール・スキル・初期調査を追加。 |
| 2026-11-02 | ユーザー指摘を受け、実装・実行環境を隣の `/mnt/HDD10TB-2/aburatani/kaggle/` へ移設。参照・共有スキル・仮想環境を修正。 |
| 2026-11-02 | APIトークン認証と収集9項目・公開コード3本の取得を確認。 |
| 2026-11-02 | 公開Notebook 3本のversionと全セルを照合・精読し、主要依存のメタデータ・計算資源・検証の注意点を比較記録。実験は未実施。 |
| 2026-11-05 | CPU自動実験の合意内容をspecへ保存。goal指示文を用意し、開始前の状態を記録。 |
| 2026-11-06 | 公式データ取得とCPU runner実装を確認。修正後の5テストが成功。実学習未開始の状態で、新規CLI用の引き継ぎとgoal文を保存。 |
