---
date: 2026-11-09
last_updated: 2026-11-10
project: kaggle-name-that-llm
type: source-review
status: reviewed
tags: [public-notebook, stylometry, validation, submission-format]
---

# Yule's K stylometry Notebookの実装・評価手順確認

開始結論: (b) 試さない — prompt-grouped OOFがなく、fold外での前処理fitと公式submission schema不一致があり、Notebookの性能根拠もない。

## 出典と取得範囲

- URL: https://www.kaggle.com/code/duongynhi/name-that-llm-v6-hierarchical-prompt-cluster-apex
- 著者: Duong Y Nhi
- 取得日時: 2026-11-09 06:41 JSTごろ、公式Kaggle MCP
- 閲覧範囲: 最近実行Notebook一覧、公開Notebook metadata version 17、ソース全394行、Notebook cell outputs。実行・再現はしていない。
- Notebook検索は`last_run_time`を2026-11-08 21:30 UTCと表示する一方、metadataは11月5日21:42 UTC。sourceのタイトルはV15、コードbannerはV18。version/time provenanceに不一致がある。
- Notebookには実行出力・OOF値・LB scoreの根拠がない。

## 実装内容と重大な問題

- 約70k次元と称する特徴は、word/char TF-IDF、char SVD、stylometry、文字統計、Yule's K、Honore R、Yule等の指標、文頭語彙、Burrows' Delta風function-word特徴など。classifierはRidgeClassifierとSGDClassifierのblend。
- `StratifiedKFold(n_splits=10)`で分割するが、foldごとの学習後は各foldモデルでtest予測を平均するだけ。`val_idx`を評価に使わず、OOFやvalidation metricを出していない。`prompt_id`も参照しないため、prompt-grouped性能の根拠にならない。
- TF-IDF vocabulary、SVD、特徴量scalerを全trainでfitしてからfold分割する。specのfold-local preprocessing要件を満たさない。
- 出力は`id`と`prob_<class>`列であり、公式Code Requirementsの`submission.parquet`が求める`id`,`model`ではない。予測クラスへの復元処理がなく、提出schemaを満たさない。
- 入力が見つからない場合に人工train/testデータを作るfallbackがある。Kaggle inputを正しく取得した実行出力は確認できない。

## 判断

Public score/OOFとも証拠がなく、prompt-grouped評価も実装されず、現状の`submission.parquet`schemaも不適合。実験候補・提出候補として採用せず、GPUキューは変更しない。stylometry特徴そのものを評価するなら、別途prompt-groupedのfold-local実装と、公式`id`/`model`出力を持つ新しい実験計画が必要だが、本Notebookのタイトルや未検証の手法主張だけからは投入しない。

## 関連資料

- [元Notebook](https://www.kaggle.com/code/duongynhi/name-that-llm-v6-hierarchical-prompt-cluster-apex)
- [公式Code Requirements](https://www.kaggle.com/competitions/name-that-llm/overview/code-requirements)
- [プロジェクトREADME](../README.md)

最終結論: (b) 試さない — fold-localなprompt-grouped評価、検証可能なscore、公式submission schemaのいずれも満たさないため、このNotebookを候補として試さない。
