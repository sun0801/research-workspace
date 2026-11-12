(b) 試さない — `.668 fork`の全体OOF/score provenanceが確認できず、構成は既存候補screenと大きく重複する。

---
date: 2026-11-12
project: kaggle-name-that-llm
type: public-notebook-audit
conclusion: b-no-test
---

# `ntl fuse33 (0.668 fork + response corpus)` Notebook audit

確認日時: 2026-11-12 19:02 JST。

- Official Kaggle MCP `search_notebooks`でName That LLMをscore降順検索し、[Notebook info](https://www.kaggle.com/code/whitegg/ntl-fuse33-0-668-fork-response-corpus)とcurrent version 10のsourceを確認。Metadataはpublic / GPU / Internet off / T4。検索結果のlast-runは2026-11-12 01:24:52 UTC、Notebook infoは2026-11-09 10:05:31 UTCで不一致。Notebook titleの`.668`や本文の`.685+`は、取得したmetadataで提出version・LB scoreと結び付けられなかった。
- Notebookは51 cellsで、metadataに21 dataset、8 kernel、6 model sourcesが登録される。6-backbone core、複数の外部分類器、Qwen3-Embedding fold expert、Sinkhorn/typography/family gatesを融合する大規模pipeline。本文のclaimed scoresだけではcombined pipelineのprompt-grouped OOF・独立confirmationを確認できない。内部style residualのGroupKFold記述だけではfull stackのvalidityを示さない。
- 重複するpublic dual-SVC/fusion approachは[既存audit](2026-11-09-duong-dual-svc-apex-audit.md)で、scoreとfull-stack OOF provenance不足により(b)としている。Sibling-style residualも手元blendでprimary paired CIが0をまたいだため不採用。[screen](2026-11-09-qwen-blend-sibling-style-residual.md)。Qwen3-Embedding expertはHost142に固定された登録candidate08の範囲と重なり、Host142の再割当てはしない。
- Decision: (b) 試さない。全体のreproductionは外部assetと実装が大きく、検証されたOOF/scoreが現best `.653828`を超えると確認できず、現在の公開首位`.768`との差も埋める根拠がない。新しい実装・Kaggle object・submissionは作成しない。
