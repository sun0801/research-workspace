---
date: 2026-11-10
last_updated: 2026-11-11
project: kaggle-name-that-llm
type: source-review
---

# Hande Akin: Qwen3 embeddings + LR + Sinkhorn audit

開始結論: (b) 試さない

## 出典と取得範囲

- URL: https://www.kaggle.com/code/handeakn/qwen3-embeddings-lr-sinkhorn
- 著者: Hande Akin
- 取得日時・version: 2026-11-10 00:21 JST時点、public version 4。`get_notebook_info`の最終実行時刻はNov 6 15:20 UTCだが、DateRun検索結果はNov 9 14:46 UTCで不一致。
- 読んだ範囲: MCP経由でNotebook source全体、metadata、該当関数。公開run output/スコアを示す出力はsource取得結果に含まれない。
- 自分たちの再現: 未実施

## 確認した内容

NotebookはTF-IDF + Logistic Regressionと、Qwen3-14Bの複数層mean-pooled embedding + Logistic Regressionを比較・blendする。prompt-grouped `GroupKFold`でOOFを作り、Trainでは真の`prompt_id`、validation/testでは文章クラスタを使ったグループ中心化を行う。

`cluster_prompts`は全test文書をTF-IDF + average-linkage agglomerative clusteringし、クラスタ数を`round(n/18)`に設定する。`sinkhorn_within_groups`は各クラスタ内で18クラスの列合計を`cluster_size / 18`にそろえる。したがって、各testクラスタが完全な18モデル集合を含むという仮定を後処理に置いている。

OOF全行のbalanced accuracyを見ながら温度を選び、同じOOFに対する最高値を使って特徴layer・centering・C・blend weightも選択する。sourceからnested CVや独立確認splitは確認できず、このOOF最大値は候補選択後の独立推定ではない。

## 投稿者の結果と検証条件

| 手法 | データ/version | 分割・seed | 指標 | CV | Public LB | スコアの出典 |
|---|---|---|---|---|---|---|
| Qwen3 layer embeddings + LR、TF-IDF blend、group centering、Sinkhorn | Qwen3-14B base v1と公式コンペdata | `GroupKFold(5)`、seed記載なし | 再取得sourceに数値出力なし | Notebook内OOFで温度・特徴・blendを選択 | 未取得 | 検証可能なスコア主張を確認できず |

## 解釈・限界・反証

Kaggle公式Evaluationは、testのモデル別件数が不均等で、public/privateでモデル構成も異なると明記する。公式Data Descriptionはinteractive時の3 example rowsとhidden rerunの約4,000 passagesを説明し、Evaluationページはinteractive時1行と表現しているため、この表示間には不一致がある。いずれの記述も、各推定prompt clusterに全18モデルが均等に含まれるという仮定を保証しない。

結果表示がないことと、DateRun / metadata時刻の不一致により、最近の完了runやNotebookタイトルから性能を判断できない。従ってSinkhorn仮定は現行test分布で未検証であり、OOF探索値もnested・独立確認値として扱えない。

## 今回への候補と未決事項

Qwen3 embedding層の特徴量とprompt中心化は将来の候補として調査可能。ただし、現行test不均等性を模したsimulationとfold内nested選択を用意しない限り、Sinkhornを採用判断・提出へ使わない。このNotebookは現在のGPUキューを変更せず、作成・提出もしない。

最終結論: (b) 試さない — equal-18仮定が不均等test分布と不整合で、OOF選択もnested/independentでなく、採用bestを超える検証可能なscoreがない。

## 関連ファイル

- [公式Leaderboard・rules・timeline確認](2026-11-10-host-continuation-poll.md)
- [近いQwen embedding ensembleのsource audit](2026-11-10-xiangqizhang-0681-notebook-audit.md)
