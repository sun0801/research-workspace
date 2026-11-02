---
date: 2026-11-02
project: kaggle-name-that-llm
type: source-review
status: initial-survey
---

# Name That LLM — 初期調査と資料台帳

取得日: 2026-11-02 (JST)。公式MCPの公開情報とKaggleの公開Web情報を参照。**学習・提出・自分たちのスコア再現は未実施**。

## コンペの前提

| 項目 | 確認した内容 | 根拠 |
|---|---|---|
| タスク | 18種類のLLMのうち、文章を書いたモデル名を分類 | [Description](https://www.kaggle.com/competitions/name-that-llm/overview/description) / get_competition |
| 評価 | Balanced accuracy。各クラスのrecallを等しく平均 | [Evaluation](https://www.kaggle.com/competitions/name-that-llm/overview/evaluation) |
| train | 2,699文章、150プロンプト。id / prompt_id / text / model | [Data](https://www.kaggle.com/competitions/name-that-llm/data) |
| test | 本番再実行で約4,000文章。trainにないプロンプト。testにはprompt_idなし | 同上 |
| 提出 | Notebookの再実行でsubmission.parquetを生成。idとmodel、id重複/欠損なし | Evaluation |
| 実行条件 | CPU/GPUとも9時間以内、インターネット無効 | [Code Requirements](https://www.kaggle.com/competitions/name-that-llm/overview/code-requirements) |
| データ/モデル | 公開外部データ・事前学習モデルが利用可能。個別の利用条件・公開性は別途確認 | [Rules](https://www.kaggle.com/competitions/name-that-llm/rules)、Code Requirements |
| 提出回数 | MCPメタデータとRulesはいずれも1日5回 | get_competition / rules |

### 一次資料どうしの不一致

- **最終締切**: MCPのTimeline本文は2027-01-13 23:59 UTC（2027-01-14 08:59 JST）だが、`get_competition.deadline` は2027-01-14T23:59:00.817Z（2027-01-15 08:59 JST）。この記録では確定しない。参加・提出の計画前にライブの公式Timelineと主催者告知を再確認する。
- **対話実行時のtest行数**: Data本文は3行、Evaluation本文は1行と書かれている。本番は約4,000行との説明。固定行数を前提にせず、取得したtestを実際に読む設計が必要。
- Timeline本文には参加・チーム締切の未展開テンプレートもある。新規参加締切のメタデータは2027-01-06 23:59 UTCだが、未展開の文字列を日付として扱わない。

## 取得範囲と接続状態

公式MCP `https://www.kaggle.com/mcp` へinitializeとtools/listを実行。76ツールを確認し、今回の設定では読み取り32ツールのみ有効にした。Codexにネイティブツールが追加され、概要取得も成功。

| 対象 | 今回の結果 | 限界 |
|---|---|---|
| 概要・Rules等 | 取得成功、ページ本文を確認 | メタデータと本文に不一致あり |
| Data | ファイル要約の取得成功 | ファイル一覧は認証要求。データ本体は未取得 |
| Code | 公式Web検索で候補を発見 | MCPのNotebook検索は認証要求。ソース未取得 |
| Discussion | 人気/新着の先頭ページと4件の本文、一部コメントを取得 | 全91件・全コメントを網羅していない |
| Models | キーワード検索に成功 | 無関係な結果を含む。コンペのModelsタブを網羅したものではない |
| Leaderboard | 今回は表の取得なし | 紹介したスコアは投稿者の記載であり現在順位ではない |

初回の機械収集は9項目中6項目が成功し3項目が認証要求で失敗。部分取得として終了コード1を返した。認証情報の設定・OAuth完了・コンペ参加同意は未実施。

キャッシュ: `/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/.cache/kaggle/2026-11-02T161614-890004+0900/`。`manifest.json` に初回9項目の時刻・入力・hash・失敗を記録。後から精読のため取得した4件のDiscussion原本は同フォルダの `cv-baseline.json` / `open-pool.json` / `punctuation.json` / `cv-lb-gap.json`。これらの追加取得は初回manifestの集計には含めていない。永続的な要約の正本は本ファイル。

## 本文を読んだ有力資料

### 1. プロンプト単位の検証とCPUベースライン

[Grouped CV、CPU baseline、落とし穴](https://www.kaggle.com/competitions/name-that-llm/discussion/750390) — Adisak Sukul。初回投稿日2026-10-18。本文と取得範囲のコメントを確認。コード例はDiscussion内を読んだが未実行。

投稿者は文字/単語TF-IDFとLogistic Regressionを提示し、prompt_idを用いたgrouped CV 0.343、Public LB 0.353を報告。句読点や大小文字を保つ処理を採用している。ランダム分割が、このデータ配置では悲観的になる報告もあり、一般的な「ランダム分割なら高く出る」という説明をそのまま当てはめない。

同じ投稿では、プロンプトごとにモデルが一度ずつ現れる制約を利用した後処理がCVでは改善し、LBでは悪化したと報告。コメントには、外部poolを入れた学習でgrouped CVとLBに差が生じたという別投稿者の結果がある。

**今回への候補**: まず安価な基準を作り、後続手法との比較を可能にする。プロンプト単位の分割、文章長別・クラス別の評価を計画候補にする。テストの同一プロンプトあたりの回答数をtrainと同じと仮定しない。実験設計は未承認。

### 2. Open Pool v11 — 量だけでなくラベルと分布を確認

[Open Pool v11の報告](https://www.kaggle.com/competitions/name-that-llm/discussion/752766) — Carrot Production / crtproduction。[データセット](https://www.kaggle.com/datasets/crtproduction/name-that-llm-open-pool)。本文と取得範囲のコメントを確認。データ自体は未取得。

取得時の本文は190,588文章のv11を紹介。Geminiの経路とラベルの確度、文字表現・長さを合わせる重み、復元したプロンプトによるグループ情報を論点にしている。報告内の比較は小規模Qwen3-1.7B LoRA、45,000文章、2 seedsなどの条件が付いており、pool全体や大型モデルでの効果をそのまま保証しない。

**今回への候補**: 外部データはversion・取得元・ラベルの来歴・重複・プロンプト構造・文字表現分布を台帳に残す。公式train全体に合わせて作った重みをそのままCVに持ち込むと、validation側の情報が入る点を確認する。データの規模だけで採用しない。

### 3. 句読点・文章長・同系統モデルの誤り

[Punctuation audit](https://www.kaggle.com/competitions/name-that-llm/discussion/750664) — Masood Ahmed。本文と取得範囲のコメントを確認。元データを自分たちで集計してはいない。

投稿者は、句読点や表記の特徴が提供元の識別には役立つ一方、同じ提供元内のモデル識別が残ると報告。grouped CVでTF-IDF 0.345、特徴の追加とblendで0.372という値を記載。短文ほど難しく、外部データではtrain上の表記傾向が崩れる例もコメントにある。

**今回への候補**: 提供元の正答率と18クラスの正答率を混同しない。句読点を消す前処理や、特定の記号がないことによるハードなラベル除外は慎重に検討する。

### 4. 単体OOF改善とアンサンブルの価値は別

[Qwen2.5-14B再学習とCV/LBの乖離](https://www.kaggle.com/competitions/name-that-llm/discussion/753177) — Harshita Kumari。本文と取得範囲のコメントを確認。実行ログや重みの独立確認は未実施。

投稿者は同じQwen2.5-14B枠を追加データで再学習し、5-fold OOFが0.569から0.605へ改善した一方、既存ensemble内の置換でPublic LBが0.651から0.647へ低下したと報告。コメントでは旧モデルを残して追加する比較も記載される。学習データの違いによる多様性やblend weightが候補原因だが、原因が確定したとは扱わない。

**今回への候補**: OOF予測とデータversionを残し、後で相関・置換・追加を比較できるようにする。単体スコアだけでアンサンブルの採否を決めない。

## Notebook候補 — ソース精読はこれから

| 候補 | 発見した根拠 | 閲覧範囲 / 次に見る点 |
|---|---|---|
| [nlm-v27](https://www.kaggle.com/code/dhruvtibarewal/nlm-v27) | 上記753177の比較対象 | Discussionで手法とスコアの報告を確認。実Notebookのversion・依存先・コード未確認 |
| [Gaussian Prompt Heads + OLMo2 LoRA](https://www.kaggle.com/code/lightningv08/gaussian-prompt-heads-olmo2-lora) | 公式Kaggle Web検索で発見 | タイトル・ライセンス・依存先の一部。MCPメタデータ取得は失敗。コード未読 |
| [Qwen blend](https://www.kaggle.com/code/lucasboesen/qwen-blend) | 公式Kaggle Web検索で発見 | 公開ページの情報のみ。ソース・比較条件未確認 |

これらを現在の「最強」と断定しない。認証後に人気・新着・scoreの各観点で検索し直し、versionを固定してソースを読む。Modelsは各Notebookの実際の依存先を追う。コードの見た目やタイトルから手法・ライセンス条件を推測して採用しない。

## 現時点の解釈

重要なのは、モデルを大きくすることだけでなく、検証の配置、外部データの品質、同系統モデルの区別、文章長、ensembleの多様性を揃えて比較すること。この判断は初期調査に基づく提案であり、我々の実測による結論ではない。

## 環境の検証

- CLI 2.2.5のversion表示とhelpを実行。最初は未宣言のsix依存で失敗し、明示依存の追加後に起動成功。
- 通信JSON/SSE、認証エラー、書き込みツール拒否、部分取得の記録と既存snapshotを上書きしないことを4件の自動テストで確認。
- 公式MCP接続と初回の部分取得を実サービスで確認。
- `codex mcp login kaggle` がKaggleの認証URLを発行することを確認。本人ログインは未完了で、認証成功とは扱わない。
- GPU/学習環境、Notebookソースの取得、データ取得、提出の検証はまだ行っていない。

## 再開候補

認証を完了してNotebookソースを調べる。次に、計算環境・予算・目標を踏まえてベースラインと検証のspecを計画化する。日次TODOや未承認specには自動登録しない。
