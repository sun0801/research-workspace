---
date: 2026-11-17
project: kaggle-name-that-llm
type: experiment-log
status: in-progress
---

# Public .684系 Notebook private runtime

## 候補とライセンス監査

- 2026-11-17: `lbjyang/ntl-684-ozertuu-mirror` current v4を確認。Notebook metadataは公開・T4・Internet off。タイトルは`.684`、本文は`.683` architectureと記載するが、版固定の提出refは確認できていない。source codeの`RUN_LIMIT_S`は8h。full hidden runtimeは未測定なので、候補スコアとして私側で確定扱いせずLBで検証する。
- Active model configはQwen3-14B/8BとLlama adaptersがMITの`dhruvtibarewal/nlm-l24-adapters-v5`、NishantのQwen3-14B/Qwen2.5-14B/DeBERTa assetsがCC BY-SA 4.0の`ntl-handwriting-blend`。OQ1/OQ4はsource metadataにはあるがactive model configでは使われていない。
- `ntl636-updated-style/README.md`と`style-update.json`に記された5つの元CSVを取得して照合。`sha256sum -c /tmp/ntl636-style-audit/verified-style-sources.SHA256SUMS`は5件すべて`OK`。prefix: `ntl_extra_passages_claude.csv` `710dbe48`; `gen_passages.csv` `d037d212`; `ntl_generations.csv` `83003454`; `ntl_proxy_generations.csv` `593708f7`; `passages_clean.csv` `6ec42c0b`。対応元はCC BY 4.0の公開dataset version（Lucas v7、Abdullah v2、Prvsiyan v6を含む）。主要SVCのtraining poolは`ntl-handwriting-blend`由来でCC BY-SA 4.0。帰属情報をforkに残す。
- `ntl-olmo2-native24-final-inference-assets`はKaggle上で`Other`だが、descriptionとcomponent noticesは各assetの元license scopeを保持。`ntl636-updated-style`のsource provenanceは上記manifest照合で対応付けた。Qwen3-Embedding-8B Kaggle model variation v1はApache 2.0、Tencent WeMM-Embedding-4B upstreamもApache 2.0 ([Qwen model card](https://huggingface.co/Qwen/Qwen3-Embedding-8B), [Tencent model card](https://huggingface.co/tencent/WeMM-Embedding-4B))。GSQ Qwen3.8 componentのlicense/attributionはbundle内noticeに従う。
- 判定: **(a) 試す**。現best`.626`を超える可能性のある、今回監査した中で最も強いライセンス確認済み公開系統としてprivate runtimeへ進む。Areebの別`.684` Notebookはactive OQ4の利用条件が不明なため(c)保留のまま。

## Private pushとruntime

- 2026-11-17 19:29 JST pre-push gate: rate guard 5h 79% / weekly 67%; `kaggle quota` GPU 28.30h/30h（refresh 2026-11-21 09:00 JST）。Official Kaggle info: Notebook-only、Internet off、CPU/GPU runtime ≤9h、`submission.parquet`、1日最大5件・最終選択2件。Public top`.776`、6,174 teams。Competition metadata deadline Jan14 UTC、Timeline deadline Jan13 UTCの不一致は維持して記録。
- 19:32 JST: source code 55 cellsを変更せずprivate kernel `suntree0801/name-that-llm-ntl684-public-baseline` version 1へpush。初回status `RUNNING`。
- Remote readback: `is_private=true`, GPU/T4有効、Internet無効、competition source `name-that-llm`。Remote Notebookの55 cell sourcesはpull元と一致。
- 当日提出はref `58462545`を含め5/5使用済み。runtime検証が通っても、次の提出枠が空くまでは提出しない。submission ref `58462545`は19:29 JST時点で`PENDING`。

## 次

- Jobは30分以上の間隔で軽くpollする。完了時にruntime/error log、hidden full-test projection、`submission.parquet`の全ID・label・null・重複検査を記録する。
- Gate通過後、利用可能な日次枠で一度提出し、Public LBを現在の`.626`と比較する。Public `.005`未満はnoise扱い。Private LBは別途記録する。
