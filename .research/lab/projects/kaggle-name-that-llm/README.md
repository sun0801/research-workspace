---
project: kaggle-name-that-llm
status: active
summary: CPU baseline＋5候補を完了。4-view＋LRでOOF BA 0.384504（baseline比+7.00ポイント）、再CV完全一致・全件fit・再推論・比較報告を保存。
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
- CPU自動実験はbaseline＋5候補を完了。固定prompt-grouped 5-foldで、baseline OOF BA=0.3144792443450161、最良の大文字保持・句読点・shape・functionの4-view TF-IDF＋Logistic Regressionは0.3845041014168531（+7.00ポイント）。全完了CVのfoldが収束し、独立検査pass。
- 最良configの再CVで2,699行のOOF全列・score配列が完全一致。全trainでfitしたモデルを保存し、別workerでの再load推論と提出形式の整合性も確認した。公開test 3件のローカル出力で、Kaggleへは送信していない。性能改善は探索用CV上の結果で、未使用holdout/Private LBでは未確認。
- 16:53 JSTのユーザー指示による中断は履歴と時間を保持し、16:57 JSTの再開指示後に同一configから再開。runnerの明示再開処理を検証する6テストが成功。累積実験403.896秒 / 7,200秒、最大RSS 1.675GiB / 32GiB、最小MemAvailable 206.224GiB / 下限16GiB。候補数上限で探索を終了し、実験プロセス不在を確認。[最終比較・成果物・再実行コマンド](experiments/2026-11-06-cpu-cycle-results.md)を最新の入口とする。
- GPU段階の141/142選定条件も診断記録へ保存。初回specはCPUのみで、GPU学習・提出は未実施。

## マイルストーン

- [x] Kaggle共通ディレクトリとName That LLMプロジェクトを作成
- [x] 公式CLI・MCP設定・収集コマンドと共同作業スキルを整備
- [x] 初期のコンペ調査と有力資料の知見を保存
- [x] 公開Notebook 3本の精読と手法・検証条件・計算資源の比較を保存
- [x] 承認済みCPUサイクルのbaseline＋5候補、最良再CV、全件fit、保存モデル再推論、比較報告を完了

## 調査・判断の索引

- [初期調査と資料台帳](experiments/2026-11-02-competition-intelligence.md)
- [共同作業と自動化の設計メモ](../../../secretary/notes/brainstorm/2026-11-02-kaggle-collaboration-setup.md)

- [認証トラブルの診断とトークン方式](experiments/2026-11-02-kaggle-auth-troubleshooting.md)

- [認証後のNotebook取得確認](experiments/2026-11-02-authenticated-notebook-discovery.md)

- [公開Notebook 3本の精読比較](experiments/2026-11-02-public-notebook-comparison.md)

- [CPU自動実験サイクルspec](specs/2026-11-05-cpu-autonomous-cycle-spec.md)

- [CPU実装の検証結果・CLIへの引き継ぎ](experiments/2026-11-06-cpu-cycle-handoff.md)

- [CPU実験の最終比較・最良候補・再現確認・再実行コマンド](experiments/2026-11-06-cpu-cycle-results.md)

## 共同作業の引き継ぎ

ユーザーの希望: Kaggleコンペを複数管理したい。今回はNameThatLLM。基本作業はAIへ委ね、各タブの有力資料から知見を蓄積し、情報共有・指示出し・自動化を整える。

現時点の前提: チャット＋Markdownを入口にする。資料の主張・AIの推測・自分たちの実測を分ける。特定の予算、GPU、順位目標、定期実行時刻は未指定。

今回のCPUサイクルは完了。正本cycleは `name-that-llm/artifacts/2026-11-06-cpu-cycle`、最良configは `configs/05-function-view.json`、最終モデルは `09-05-function-view-candidate/model.joblib`。`src/cpu_finalize.py --cycle ...`で既存成果物を再検査でき、cycle内`reproduce_cycle.sh`には新規cycle向けの全再実行コマンドを保存。既存cycleをinitし直したり、予算残を理由に追加候補を起動したりしない。次段階のGPU・外部データ・Kaggle送信等は今回の承認に含まれず、必要なら別specで具体化する。

## 更新履歴

| 日付 | 内容 |
|---|---|
| 2026-11-02 | ユーザー依頼で新規作成。共通環境・公式MCP・調査ツール・スキル・初期調査を追加。 |
| 2026-11-02 | ユーザー指摘を受け、実装・実行環境を隣の `/mnt/HDD10TB-2/aburatani/kaggle/` へ移設。参照・共有スキル・仮想環境を修正。 |
| 2026-11-02 | APIトークン認証と収集9項目・公開コード3本の取得を確認。 |
| 2026-11-02 | 公開Notebook 3本のversionと全セルを照合・精読し、主要依存のメタデータ・計算資源・検証の注意点を比較記録。実験は未実施。 |
| 2026-11-05 | CPU自動実験の合意内容をspecへ保存。goal指示文を用意し、開始前の状態を記録。 |
| 2026-11-06 | 公式データ取得とCPU runner実装を確認。修正後の5テストが成功。実学習未開始の状態で、新規CLI用の引き継ぎとgoal文を保存。 |
| 2026-11-06 | CPU baseline CVと独立検査が成功（OOF BA 0.314479）。候補1実行中にユーザー指示で停止し、プロセス不在・累積69.276秒・再開位置を保存。 |
| 2026-11-06 | ユーザーの再開指示後、baseline＋5候補を完了。最良4-view＋LRのBA 0.384504、再CVのOOF/score完全一致、全件fit・保存モデル再推論・最終検査pass。比較報告と再実行コマンドを保存。 |
