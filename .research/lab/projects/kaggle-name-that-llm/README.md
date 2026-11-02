---
project: kaggle-name-that-llm
status: active
summary: Kaggle共通環境・公式MCP・調査スキルを整備し初期調査を保存。Notebook検索とデータ取得は認証待ち。
created: 2026-11-02
last_updated: 2026-11-02
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
- 概要・各ページ・データ要約・Discussion一覧/本文を取得。Notebook検索とデータファイル一覧は認証が必要。特定Notebookのメタデータ取得も今回の試行は失敗。
- 有力Discussion 4件を本文まで確認。コード候補は見つかったが、Notebookソースは未取得・未実行。
- データ取得・GPU学習・提出は未実施。実験計画はまだ承認されていない。

## マイルストーン

- [x] Kaggle共通ディレクトリとName That LLMプロジェクトを作成
- [x] 公式CLI・MCP設定・収集コマンドと共同作業スキルを整備
- [x] 初期のコンペ調査と有力資料の知見を保存

## 調査・判断の索引

- [初期調査と資料台帳](experiments/2026-11-02-competition-intelligence.md)
- [共同作業と自動化の設計メモ](../../../secretary/notes/brainstorm/2026-11-02-kaggle-collaboration-setup.md)

## 共同作業の引き継ぎ

ユーザーの希望: Kaggleコンペを複数管理したい。今回はNameThatLLM。基本作業はAIへ委ね、各タブの有力資料から知見を蓄積し、情報共有・指示出し・自動化を整える。

現時点の前提: チャット＋Markdownを入口にする。資料の主張・AIの推測・自分たちの実測を分ける。特定の予算、GPU、順位目標、定期実行時刻は未指定。

再開時は初期調査を読み、認証状態を確認する。認証後のNotebook検索・ソース精読が候補。ベースライン実装へ進む際は、実験計画・検証方法・範囲を具体化して既存のImplementation Gateを確認する。

## 更新履歴

| 日付 | 内容 |
|---|---|
| 2026-11-02 | ユーザー依頼で新規作成。共通環境・公式MCP・調査ツール・スキル・初期調査を追加。 |

| 2026-11-02 | ユーザー指摘を受け、実装・実行環境を隣の `/mnt/HDD10TB-2/aburatani/kaggle/` へ移設。参照・共有スキル・仮想環境を修正。 |
