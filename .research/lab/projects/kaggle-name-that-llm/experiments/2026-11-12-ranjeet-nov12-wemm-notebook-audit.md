---
date: 2026-11-12
project: kaggle-name-that-llm
type: source-audit
status: rejected
tags: [public-notebook, wemm, ensemble, fast-commit]
---

# ranjeet258/ntl-nov12-confidence-gated-wemm Notebook audit

開始結論: **(b) 試さない** — Kaggle sessionのCOMPLETEは3行用FAST_COMMIT経路のみで、性能を示すOOFまたは採点scoreは確認できない。大規模blend全体は独立再現条件もない。

## 出典・取得範囲

- [公開Notebook](https://www.kaggle.com/code/ranjeet258/ntl-nov12-confidence-gated-wemm)、著者RanJeet Gupta、version 1。2026-11-12 19:40–19:46 JSTに公式Kaggle MCPでmetadata/session/outputを読み、`uv run --env-file ../.env kaggle kernels pull ... --metadata`でコードを取得。セル本文を静的に読んだ。Notebookは公開、GPU有効、Internet無効、T4指定。
- metadataには17 dataset sources、8 upstream Notebook、9 model sources。説明ではQwen3-Embedding-8B 40%、WeMM-Embedding-4B 7%、6-backbone causal-LM stack、GSQ-27B、cluster/Sinkhorn補正を含む。
- 実行時刻に食い違いがある。検索結果は11/12のrunを示したが、`get_notebook_info`の`last_run_time`は11/9、Notebook内Papermill metadataは10/27を示す。取得したsession statusは`COMPLETE`で`submission.parquet`を返す。

## 実行経路と根拠

- Sourceは`FAST_COMMIT = len(test.csv) < 50`で可視3行時に別経路へ入る。`FAST_COMMIT=True`では`submission.parquet`へ全行`gpt-5.5`を直接書き、prefit SVC/TF-IDF/distortのshape・finite smokeだけ行う。6-backbone推論・WeMM worker・最終`infer.py`の呼出しは`else`側であり、この3行sessionでは実行されない。
- session logで実際に`FAST_COMMIT True`、constant出力後にcore-vote smoke成功を確認。`COMPLETE`や出力ファイルの存在はhidden rerun完了・score・OOFの証拠ではない。API結果には採点scoreもOOF評価もない。
- full branchは17 datasets/8 kernels/9 model sourcesに加え、多段LoRA・外部response・複数backbone・prompt geometry・Sinkhornを組み合わせる。著者申告のOOF、ablation、予測出所とLB scoreの対応をこのNotebook source/sessionから検証できない。WeMM componentの元weight provenance/licenseにも別途未解決事項がある（[component audit](2026-11-12-wemm4-expanded-lora-component-audit.md)）。

## 判断

このfull stackは再現・移植しない。ユーザーgoal specに沿ったprimary/confirmation OOFを持ち、単独または固定追加として比較可能な独立候補を優先する。Kaggle資産の取得、Notebook push、提出、手元config変更はしていない。
