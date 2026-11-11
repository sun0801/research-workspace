---
date: 2026-11-09
project: kaggle-name-that-llm
source: Kaggle MCP and public Kaggle notebooks
status: reviewed
tags: [external-data, license, public-notebook, candidate-screen]
---

# 公開response corpusとNotebookの候補監査

開始結論: (b) 試さない

## 調査範囲と取得情報

2026-11-09 04:34 JSTに公式Kaggle MCPから、`olegzholobov/name-that-llm-response-corpus` version 1と関連Discussion/Notebookを確認した。Datasetは2026-10-15公開、397,046,759 bytes、Kaggle上のlicense表示は`Other (specified in description)`。Dataset descriptionによると全体135,171 canonical responses、短文viewは40–250 wordsの24,015 responses / 13,642 wide rows、18モデルすべてのresponseを持つ完全なuser-prompt groupが1,902ある。Dataset作者はtrain 2,699回答とのexact/正規化重複を検出しなかったと記載するが、paraphraseの全数否定ではない。

raw response/parquetは取得せず、READMEと`source_catalog.csv`だけを一時領域`/tmp/ntl-external-corpus-audit/`へ取得した。Source catalogは31 source、188,470 source occurrences。作者提供の`unknown_license_occurrences`合計は63,560（33.7%）で、各sourceのlicense欄にもunknown、output license未確認、provider terms適用などがある。Dataset説明はunderlying contentを再ライセンスしていないと明記する。したがってKaggleのDataset license表示だけを全responseの利用許諾として扱えない。

## 既存公開結果・主張

- [Dataset](https://www.kaggle.com/datasets/olegzholobov/name-that-llm-response-corpus)の[Discussion 749629](https://www.kaggle.com/competitions/name-that-llm/discussion/749629)には、source licensesを確認して利用した別参加者が、改行・Markdown・lengthのdistribution gapにより追加corpusがCVを悪化させたと報告している。同参加者が公開した[CPU Notebook v2](https://www.kaggle.com/code/mizuno0522/model-fingerprints-punctuation-external-data)のsourceでは、known-license行に絞るfilter、prompt_idでの5-fold GroupKFold、およびsingle-paragraph/flattened external dataの比較コードを確認した。Markdown本文はTF-IDFとfrozen Qwen embeddingsの複数weightで悪化したと記すが、Notebook内に実行出力や数値比較はなく、独立再現ではなく投稿者の主張として扱う。
- [cosmorinのPublic 0.636 reproduction guide](https://www.kaggle.com/code/cosmorin/name-that-llm-how-to-reproduce-0-636)は、SVC、Qwen3-14B/Qwen2.5-14B LoRA、DeBERTa-v3-large等をまとめた既存公開手法を保存している。本文が主張するblend CV `.642` / Public `.636`は今回の取得情報から独立検証していない。topic-cluster内のunique-author補正などLBで悪化した手法も著者ノートに列挙されており、新候補として採用する根拠は不足している。
- [train prompt reconstruction Discussion 749455](https://www.kaggle.com/competitions/name-that-llm/discussion/749455)は全150 prompt_idの推定promptを公開する。投稿者は平均self-rated confidence `.81`とする一方、本文はClaudeによる推定でground truthではないと明記。現行候補のprompt reconstruction leakage filterと同種の資料であり、新しいtrain/test情報として扱わない。

## 次候補への判断

このresponse corpusは現時点でGPU候補に登録しない。理由は、(1) Dataset全体に一律適用できる利用許諾を確認できない、(2) source単位でもoutput/provider termsが未確認の記録が多い、(3) known-license subsetを使ったという投稿者から性能悪化の報告があり、(4) CVの実測値と転移条件を独立確認できていないため。外部コーパスを試す場合は、後日、出力利用許諾まで確認したsourceだけでsubset件数・各クラス分布・重複/近似prompt除外・本文書式を監査し、実際のbest ensembleに対するnested prompt-grouped評価specを作ってから判断する。

cosmorinの`.636`再現手法は、Qwen/DeBERTa系とSVCを含む現行候補列と重複が多く、公開top`.752`にも届かない。新たな複製実験は追加せず、Host141の候補11/12/13とHost142の登録済みqueueを継続する。今回、実験コード・既存job・watcher・Kaggle objectは変更せず、GPUも使っていない。Kaggle `search_notebooks`はgeneric errorを3回返し、ローカル公式CLIのNotebook一覧はAuthentication requiredで取得できなかった。既知slugのsource確認は成功したが、Notebook一覧を網羅したとは扱わない。CLIの資格情報は参照・変更していない。

最終結論: (b) 試さない — response corpus全体の利用許諾が不明で、source provenance・性能転移も確認できず、公開手法も現行best/leaderを超える再現可能な根拠がない。
