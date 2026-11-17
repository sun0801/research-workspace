---
date: 2026-11-17
project: kaggle-name-that-llm
type: experiment-log
status: in-progress
---

# Public .684系 Notebook private runtime

## 候補とライセンス監査

- 2026-11-17: `lbjyang/ntl-684-ozertuu-mirror` current v4を確認。Notebook metadataは公開・T4・Internet off。タイトルは`.684`、本文は`.683` architectureと記載するが、版固定の提出refは確認できていない。SourceのWeMM fold workerに30,240秒（8時間24分）のdeadline設定があるが、Notebook全体の9時間以内を保証するgateではない。full hidden runtimeは未測定なので、候補スコアとして確定扱いせずLBで検証する。
- Active model configはQwen3-14B/8BとLlama adaptersがMITの`dhruvtibarewal/nlm-l24-adapters-v5`、NishantのQwen3-14B/Qwen2.5-14B/DeBERTa assetsがCC BY-SA 4.0の`ntl-handwriting-blend`。OQ1/OQ4はsource metadataにはあるがactive model configでは使われていない。
- `ntl636-updated-style/README.md`と`style-update.json`に記された5つの元CSVを取得して照合。`sha256sum -c /tmp/ntl636-style-audit/verified-style-sources.SHA256SUMS`は5件すべて`OK`。prefix: `ntl_extra_passages_claude.csv` `710dbe48`; `gen_passages.csv` `d037d212`; `ntl_generations.csv` `83003454`; `ntl_proxy_generations.csv` `593708f7`; `passages_clean.csv` `6ec42c0b`。対応元はCC BY 4.0の公開dataset version（Lucas v7、Abdullah v2、Prvsiyan v6を含む）。主要SVCのtraining poolは`ntl-handwriting-blend`由来でCC BY-SA 4.0。帰属情報をforkに残す。
- `ntl-olmo2-native24-final-inference-assets`はKaggle上で`Other`だが、descriptionとcomponent noticesは各assetの元license scopeを保持。`ntl636-updated-style`のsource provenanceは上記manifest照合で対応付けた。Qwen3-Embedding-8B Kaggle model variation v1はApache 2.0、Tencent WeMM-Embedding-4B upstreamもApache 2.0 ([Qwen model card](https://huggingface.co/Qwen/Qwen3-Embedding-8B), [Tencent model card](https://huggingface.co/tencent/WeMM-Embedding-4B))。GSQ Qwen3.8 componentのlicense/attributionはbundle内noticeに従う。
- 判定: **(a) 試す**。現best`.626`を超える可能性のある、今回監査した中で最も強いライセンス確認済み公開系統としてprivate runtimeへ進む。Areebの別`.684` Notebookはactive OQ4の利用条件が不明なため(c)保留のまま。

## Private pushとruntime

- 2026-11-17 19:29 JST pre-push gate: rate guard 5h 79% / weekly 67%; `kaggle quota` GPU 28.30h/30h（refresh 2026-11-21 09:00 JST）。Official Kaggle info: Notebook-only、Internet off、CPU/GPU runtime ≤9h、`submission.parquet`、1日最大5件・最終選択2件。Public top`.776`、6,174 teams。Competition metadata deadline Jan14 UTC、Timeline deadline Jan13 UTCの不一致は維持して記録。
- 19:32 JST: source code 55 cellsを変更せずprivate kernel `suntree0801/name-that-llm-ntl684-public-baseline` version 1へpush。初回status `RUNNING`。
- Remote readback: `is_private=true`, GPU/T4有効、Internet無効、competition source `name-that-llm`。Remote Notebookの55 cell sourcesはpull元と一致。
- 当日提出はref `58462545`を含め5/5使用済み。runtime検証が通っても、次の提出枠が空くまでは提出しない。submission ref `58462545`は19:29 JST時点で`PENDING`。

- 20:02 JST 30-minute poll: private kernel v1 returned `KernelWorkerStatus.COMPLETE`. `kaggle kernels output` recovered `submission.parquet`, `submission.mode.json`, and the session log. The parquet passed Kaggle-environment checks: 3 rows, columns `id,model`, no nulls or duplicate IDs, all three labels valid (`claude-fable-5`). However, mode metadata explicitly says `exact_public_format_preview`, `model_weights_loaded=false`, and `hidden_runtime_verified=false`. Source inspection confirms the public test's known 3-row fixture bypasses model loading; non-fixture hidden input follows the full ensemble path. The preview session log ends after notebook setup/conversion at about 22 seconds and does not establish GPU usage, peak memory, full hidden-test output, or the 9-hour runtime gate. No score or competition submission is available for this candidate yet; all 5 daily slots were already used. Do not treat this as a full runtime pass.

## 次

- `submission.mode.json`のpreviewはartifact format確認のみ。hidden full-test runtimeは未確認なので、日次枠が空いたら提出前にユーザーへ報告し、ref/score/runtimeを回収して`.626`と比較する。Public差`.005`未満はnoise扱い。Private LBは別途記録する。
- 他の実行中jobとsubmissionは30分以上の間隔で軽くpollし、状態変化時のみ記録する。
- 22:08 JST source/runtime recheck: pulled private v1 and public `lbjyang` v4 have identical 55-cell sources. The public output artifact is also `exact_public_format_preview` (3 rows, model weights not loaded, hidden runtime unverified); its log ends after approximately 20 seconds of Notebook setup. Therefore the prior cached 10,863-second evidence belongs to a different public lineage and does not establish runtime for this candidate. The exact source has no Notebook-wide `RUN_LIMIT_S`; the 30,240-second setting only bounds the WeMM fold worker. Keep this kernel as a trial candidate, not a scored or runtime-verified baseline. No submission has been made.

- 2026-11-18 01:02 JST read-only pull of private v1 reconfirmed private/GPU/offline metadata and the 55-cell source. The hidden path stages `ensemble.py`, then calls `finish_native_wemm`; the WeMM worker deadline is 30,240 seconds and is not a notebook-wide runtime guarantee. The existing Mistral NF4 add-on projects 2.995 hours by itself, so its addition must wait for the `.684` hidden scoring runtime and may need a runtime-feasibility decision under the 9-hour competition limit. Preserve the current order: submit the unchanged baseline first, then use measured runtime to select the next existing component.

- 2026-11-18 01:12 JST prepared a local private `.684` + existing Qwen17 candidate at `name-that-llm/notebooks/name-that-llm-ntl684-qwen17-addon/` in the Kaggle implementation repository (commit `70cd4b5`). Parent code cells 1–54 are byte-for-byte unchanged; the appended cell skips the known three-row public preview, reads the parent `final-logits.npz` on hidden input, runs the existing Qwen17 inference at fixed log-probability weight `.25`, and rewrites the aligned output only after the existing 64-row pilot, T4 reserve, and total eight-hour projection gates pass. Metadata is private/GPU/offline and adds the existing private Qwen17 assets plus pinned Qwen3-1.7B v1. Static AST parsing and source/metadata invariants pass. This is local preparation only: no push, runtime, or competition submission. Wait for the unchanged `.684` baseline's score and actual runtime before deciding whether this add-on fits the gate.
