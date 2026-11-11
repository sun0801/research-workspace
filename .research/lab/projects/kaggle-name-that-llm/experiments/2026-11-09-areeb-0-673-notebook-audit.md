---
date: 2026-11-09
project: kaggle-name-that-llm
type: source-review
---

# Areeb Aliの0.673表記Notebook v2監査

開始結論: (b) 試さない

## 出典と取得範囲

- URL: https://www.kaggle.com/code/areebbb/0-673-i-m-better
- 著者: Areeb Ali
- 取得日時・version: 2026-11-09、`get_notebook_info` current version 2、46 votes。Notebook本文の最終実行日時はAPI metadataでは2026-11-05 22:27 UTC、score-sorted search indexでは2026-11-08 21:42 UTCと不一致。
- 読んだ範囲: Notebook metadata、全20セルのMarkdown/コード本文。出力実行結果、private依存資産、全参照Notebookの内容は未取得。
- 自分たちの再現: 未実施

## 確認した内容

NotebookのKaggle表示タイトルは「0.673 | I'M BETTER !」だが、version 2の本文は「NTL-22c | 0.672 + DeBERTa-v3 + Our ModernBERT」と名乗る。冒頭は、公開0.672/0.673 Notebookのコピーを実行すると0.664–0.669になること、入力のprivate dataset欠落時にfallbackが別blendへ切り替わること、fallback重みが“decoy”と記された版があることを著者主張として説明する。これらの比較・コード経路は本監査では独立再現していない。

本文は複数の先行パイプラインを束ね、以下を含む。

- Qwen系LoRA、n-gram SVC、DeBERTa-v3、著者が学習したModernBERT-large等を使う大規模ensemble。
- 共有prompt Gaussian、family内style residual、pairwise verifier。
- 本文のmain pipelineはtextからprompt clusterを推定し、cluster内のHungarian one-to-one割当とSinkhorn補正を持つ。`--sim_k`で各promptからの不均等な行数をsampleするsimulatorもあるが、これだけで実際のhidden testのclass・cluster分布への適合が確認されたとは言えない。
- Pairwise verifierは追加datasetのRevision 03を要求し、その中のcanonical train ID、本文、model labelを公式trainと完全一致照合する。これは元データ由来と利用条件の独立確認が必要なため、今回の評価には持ち込まない。
- Notebookはvisible testが50行未満ならheavy inferenceを飛ばす`FAST_COMMIT`経路を持ち、3行のplaceholder testには固定クラス予測を出す。従ってその表示用commitの成功はhidden-test推論の実証ではない。

## 投稿者の結果と検証条件

| 手法 | データ/version | 分割・seed | 指標 | CV | Public LB | スコアの出典 |
|---|---|---|---|---|---|---|
| Notebook titleの0.673 | version 2本文はNTL-22c/0.672系と記載 | 未記載 | Balanced accuracyと推定 | 未記載 | 0.673はタイトル表記。v2の採点version/出力は未取得 | 公開Notebook表示と本文の自己申告のみ |
| 公開0.672/0.673のコピー比較 | 著者はprivate dataset欠落とfallback切替を報告 | 未記載 | Balanced accuracy | 著者は0.664–0.669を報告 | 0.664–0.669 | 著者の本文記述。本監査で未再現 |
| 著者ModernBERT/事前fit SVC追加 | Open Pool等の多数の公開datasetを記載 | 「未見公式passage」とだけ説明、完全な分割条件は未記載 | Balanced accuracy | 未記載 | v2の独立スコア未取得 | 著者の本文記述 |

## 解釈・限界・反証

- Search indexとNotebook API metadataの実行日時が食い違い、表示titleと本文versionの識別も一致しない。0.673をv2の再現済み結果として扱わない。
- 数十のdataset、Notebook output、model依存があり、aggregate poolとscoreだけでは行単位の出所・prompt overlap・license・採点時versionを確認できない。
- Pairwise verifierの入力に公式trainの複製が含まれることを本文自体が照合しているため、その外部datasetはこのgoalでは再利用しない。
- Cluster内one-to-one割当やglobal prior補正は、公式Evaluationが示す非均等なclass countおよびpublic/private mix差と整合する証拠が別途必要。Notebookのsimulation設定はその証拠の代替にならない。
- Family-local style residualの考え方自体は、過去にSVCでprimary BA差 `+0.007405`、prompt-paired CI `[-0.001481,+0.016664]`となり採用gateを通らなかった。旧base結果を現行Qwen blendへ直接外挿せず、固定手法の単独screenに限って再評価する余地がある。

## 今回への候補と未決事項

大規模Notebook、A/B pairwise data、Gaussian、Sinkhorn/assignment、外部weightsは使わない。fixed family-style residualのみを現行Qwen8B+Qwen1.7B+prompt-centered SVCのsaved primary OOF上で評価した。差は `+0.000738`、5,000 prompt-grouped bootstrap CI `[-0.002618,+0.004442]`でprimary gateを通らず、不採用・confirmation省略。[結果](2026-11-09-qwen-blend-sibling-style-residual.md)。

## 関連ファイル

- [style residual primary spec](../specs/2026-11-09-qwen-blend-sibling-style-residual-spec.md)
- [過去のfamily-local residual試験](../specs/2026-11-07-prompt-family-style-residual-spec.md)
- [Spectral mean-field primary](2026-11-09-spectral-cluster-meanfield-primary.md)

最終結論: (b) 試さない — `.673`は版に紐づくscoreとして未検証で、大規模compositeの外部data/provenanceとcluster補正が未確認。唯一screen済みのfamily residualも現行blendで採用gateを通らなかった。
