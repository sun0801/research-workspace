---
date: 2026-11-09
project: kaggle-name-that-llm
type: source-review
status: reviewed
tags: [public-notebook, qwen3-embedding, ensemble, provenance]
---

# Qwen3-Embedding公開blend Notebookの確認

開始結論: (b) 試さない

## 出典と取得範囲

- URL: https://www.kaggle.com/code/lightningv08/0-681-qwen3-embedding-lora-qwen3-8-27b
- 著者: Vladislav Lavrentyev
- 取得日時: 2026-11-09 06:07 JSTごろ。version 16のmetadata/sourceは07:55 JSTと20:28 JSTに公式Kaggle MCPで再確認
- 閲覧範囲: score-descending Notebook一覧、Notebook metadata/version 16、公開ソース全体、Notebook output file一覧。実行セッション・OOFは未確認。
- Notebookタイトルの`.681`は著者申告値として扱い、独立再現値とは扱わない。公式leaderboardのトップは同時取得で`.752`。

## Notebookに記載された手法

- Qwen3-Embedding-8Bの5-fold状態をmulti-depth LoRA expertとして使い、geometric mixtureの50%を占めると説明する。40%から50%へ変更した比較で、ほかの設定を固定して`.680`から`.681`へ上げたという主張。
- 親branchはQwen3.8-27B等と複数の事前計算済み分類器・style headを含む大規模blend。metadataには21 dataset sources、8 Notebook sources、6 model sourcesがある。公開コードにはfold校正状態や外部passage由来入力が含まれ、各資産の学習範囲・ライセンス・prompt重複除去はこの確認では検証できていない。
- Notebookコードは、testが既知の公開3行と完全一致する場合、モデル推論なしに固定preview予測を書き出す分岐を含む。分岐の存在はコード上で確認したが、これだけから規約違反とは判断しない。隠しtest向けの全推論実行は未確認。
- Notebook metadataはversion 16。07:55 JSTの再取得では`last_run_time`は2026-11-05 22:56:13 UTCだった（以前の記録21:07 UTCを訂正）。20:28 JSTの再取得ではmetadataは2026-11-06 11:30:10 UTC、ScoreDescending/DateRun検索とoutput file作成時刻は2026-11-08 08:55 UTCで、時刻の不一致は解消していない。取得時点の公開metadataはGPU有効・Internet無効、192 votes。

## 判断

`.681`は現在の`.752`公開トップを超えず、大型blendと外部資産を移植する根拠にもならない。prompt-grouped OOF、外部資産のprovenance/licensing、採点versionとscoreの対応が未確認のため、採用・再現候補や現行GPUキューには追加しない。公開Notebookが`.752`を説明する根拠も得られなかった。2026-11-09 07:55 JST時点で進行中のHost141 candidate11/12/13とHost142 Qwen確認キューの順序は変更しない。

## 関連資料

- [公式Name That LLM leaderboard](https://www.kaggle.com/competitions/name-that-llm/leaderboard)
- [プロジェクトREADME](../README.md)

## 2026-11-09 12:13 JST related reproduction check

Kaggle MCPのScoreDescending/DateRun再検索で [`helen0/ntl-0681-repro`](https://www.kaggle.com/code/helen0/ntl-0681-repro) が見つかった。Notebook本文はCHEN Hanの`.679` native embedding weightsとVladislav Lavrentyevの`.666`親blendを基礎にし、Qwen3-Embedding-8B expert shareを50%にした`.681`を主張する。現在の公式public top `.752`を超えず、これは独立OOF/score検証ではない。

公式metadataではlast-runがNov 6 03:12 UTC、検索結果ではNov 9 01:46 UTC、output filesのcreationもNov 9 01:46 UTCで一致せず、session statusはCOMPLETE。取得できたoutputは658-byteの`submission.parquet`とmode情報のみでmetricは含まない。metadataには21 dataset、8 upstream Notebook、6 model sourcesがあり、長いblend依存と資産provenanceが残る。既存のQwen embedding監査を支持する追加例として扱い、再現候補・現行キューには加えない。

## 2026-11-09 20:28 JST metadata/source refresh

公式MCPのScoreDescending検索で本Notebookは引き続き`.681`タイトルの最上位。DateRun検索ではNov 9に実行された新しい`.673`系Notebookが上位に出るが、いずれも`.752`公式トップ超えを示す証拠ではない。Notebook version 16の取得sourceでも、Qwen3-Embedding-8B expert share 50%、Qwen3.8-27B task classifier share 3%、多数の事前計算済み外部資産という構成を再確認した。Kaggleのoutput一覧には`submission.parquet`と`submission.mode.json`があるだけで、scoreやhidden inferenceの実測は含まれない。title、source、metadata、output fileのどれも`.681`を独立に検証せず、再現候補・実験キューへの追加根拠にはならない。


## 2026-11-09 21:19 JST related source review

公式Kaggle MCPのDateRun検索で [`handeakn/qwen3-embeddings-lr-sinkhorn`](https://www.kaggle.com/code/handeakn/qwen3-embeddings-lr-sinkhorn) を確認。version 3のmetadata/sourceでは、Qwen3-14B 4-bitの4層平均埋め込み、word/char TF-IDF、各々のLR、blend、Sinkhorn後処理を実装している。GroupKFoldは`prompt_id`単位だが、各OOF fold内のvalidation行をテキスト類似性で約18行ずつにclusterし、テストも同じ方法でgroup化して、groupごとのクラス確率総量が均等（`n/K`）になるSinkhorn制約を適用する。公式Evaluationで確認した不均等なモデル数とpublic/private分布差に合わない仮定である。さらにlayer/C、blend比率、温度を同じOOF全体のbalanced accuracyで選んでおり、独立選択用foldは見当たらない。取得sourceには実行出力がなく、OOFスコアや提出スコアは検証できない。

検索の最終実行時刻は2026-11-09 11:47:59 UTCだが、notebook metadataのlast_run_timeはNov 6、version 3の`get_notebook_info`とも整合せず、session statusはRUNNINGを返した。したがって最新実行versionのコード・結果対応も未確認。方法の一部（prompt-grouped CV、TF-IDF/LR、埋め込み特徴）は既存研究と重なるが、同数クラス制約と同一OOF上での選択が採用根拠を弱める。`.752`公式トップを超える検証可能な証拠ではなく、現行実験キューには追加しない。

## 2026-11-09 21:58 JST public ensemble variant review

Official Kaggle MCP search surfaces [`heliosli/name-that-llm-lv681-a15`](https://www.kaggle.com/code/heliosli/name-that-llm-lv681-a15), version 5. DateRun search reports a run at 2026-11-09 21:44 JST, while `get_notebook_info` metadata says last run Nov 6 21:56 JST; the session-status response is empty and the output endpoint returns an empty log, so no current execution result or score is verifiable. The introduction says it copies the `.681` Qwen3-Embedding/27B ensemble (version 15), changes an ATLAS mixture from 0.10 to 0.15, and adds a WeMM-Embedding-4B expert at 0.05 geometric mass. Metadata lists 21 dataset sources, 8 upstream notebooks, and 7 model sources; among them are `mercurydust/ntllm-chatgpt-a-b` and `prvsiyan/prvsiyans-extended-name-that-llm-dataset`, which have unresolved competition-text provenance in the existing audit. A code path emits fixed predictions only when the exact three public test fixture rows match; full hidden-test execution is not shown by the empty session output. No verified score above `.681` is presented, still below official `.752`; no assets or predictions are used, and no queue change follows. Revisit the WeMM/embedding idea only through the already registered foldwise candidate and its own OOF gates, not by adopting this composite notebook.

## 2026-11-10 00:55 JST — related `.595` variant refresh

Kaggle MCP DateRun search returned [`lightningv08/0-595-five-fold-embeddings-qwen3-8-27b-lora`](https://www.kaggle.com/code/lightningv08/0-595-five-fold-embeddings-qwen3-8-27b-lora), title and metadata version 22. Search says last run Nov 9 14:51:32 UTC and its output files were created at 14:51 UTC, while `get_notebook_info` says last run Nov 6 15:54:46 UTC; preserve this version/run metadata mismatch. The files endpoint lists only a 698-byte `submission.parquet` and a 701-byte mode JSON, with no score output.

The visible source describes five prompt-fold Qwen3-Embedding-8B classifiers across eight depths, a 35% native branch, and a 6% Qwen3.8-27B task branch inside a large weighted parent. Metadata lists 21 Dataset sources, 8 Notebook sources and 6 Model sources. The notebook's title claim `.595` is not independently verified by the available output. Its multi-depth embedding branch overlaps the already preregistered candidate08; do not import the composite assets or reorder its queue. The code also contains an exact-public-three-row fixture path that emits fixed format-preview predictions; this is recorded as source behavior, not treated as evidence of hidden-test inference or a rules violation. No Kaggle assets were downloaded and no run, config or submission changed.

## 2026-11-10 01:11 JST — related parameterization discussion

Kaggle Discussion [757125](https://www.kaggle.com/competitions/name-that-llm/discussion/757125), posted Nov 9 at 11:09 JST by James Bedichek, says the author's best accuracy was `.64–.65` using a frozen Qwen3.8-27B with mean pooling from four probe layers and a linear head. The author reports that top-k logits and token-level expert routes did not beat that setup and mentions calibration difficulty. This is self-reported only: no OOF rows, split protocol, code, selected checkpoint, or score artifact is supplied. The broad frozen multi-depth representation idea is related to candidate08, but this post does not validate its score or provide an independently reproducible candidate; no queue/config/run change follows.

最終結論: (b) 試さない — `.681`/`.595` claims are unverified, the large composite overlaps registered candidate08, and neither provides evidence to exceed the current public leader.
