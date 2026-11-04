---
date: 2026-11-02
project: kaggle-name-that-llm
type: source-inventory
---

# 認証後のNotebook取得確認

確認日時: 2026-11-02 16:55 JST。ユーザーが端末でAPIトークンを保存し、Notebook検索の成功を報告。こちらでも再確認した。

## 接続・取得結果

ローカルの公式MCPクライアントで9項目すべて成功。取得対象は概要・各ページ・データ一覧/要約・人気/新着Notebook・人気/新着Discussion・Modelキーワード検索。各一覧は先頭ページで、Model検索はコンペModelsタブの網羅を意味しない。

取得原本: `/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/.cache/kaggle/2026-11-02T165411-087539+0900`。manifest.jsonに入力・結果・hashを保存。

公式CLIでも以下の公開Notebookとメタデータのpullに成功。コードは未精読・未実行。version番号は今回のexportでは未確認のため、取得ファイルのSHA-256を残す。

| 対象 | URL | コードSHA-256 |
|---|---|---|
| 公式Starter | [Kaggle](https://www.kaggle.com/code/martynaplomecka/starter-notebook-for-name-that-llm-competition) | `10d87a3e76ae340aea6b05139ed970a27bd0c9c3f0ae4c0ac56baa33da211187` |
| Two-stage LoRA | [Kaggle](https://www.kaggle.com/code/nishantdahal/two-stage-lora-on-the-public-pool) | `12e1e65bbc48a2839842d439fd7ae3846b9bf0d9913c4cdc308ebc698974b3fb` |
| nlm-v27 | [Kaggle](https://www.kaggle.com/code/dhruvtibarewal/nlm-v27) | `c57238c44d772ad591ae527262dc3f2d63ab92d32c2c7fb31e4d3ab5f9a5076f` |

## 依存メタデータで確認できたこと

Two-stage LoRAはQwen3の8B/14B baseのversion 1を参照し、nishantdahal/ntl-two-stage-loraを入力に持つ。nlm-v27はLlama 3.1、Qwen3、Qwen2.5の複数versionと多数の公開データ/adapterを参照している。メタデータからの依存情報であり、全てが実際に実行されるか・必要なVRAM・学習条件はソース精読が必要。

## ネイティブMCPの状態

この会話で既に接続していたネイティブsearch_notebooksは引き続きUnauthenticatedを返した。トークン設定前の接続が更新されていない可能性がある。原因は未確定で、ネイティブ接続は再接続後の確認が必要。ローカルのMCPクライアントと公式CLIでは同じAPIトークンで取得が成功しているため、調査を進められる。

## 次の作業

取得した3本のコードを読み、指標・分割・追加データ・依存モデル・推論条件を比較して記録する。実験実装は計画化と既存の承認ゲートを経て進める。コンペの参加/ルール同意は未確認。データ本体・重みのダウンロード、学習、提出は未実施。
