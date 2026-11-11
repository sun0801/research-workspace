# xiangqizhang/ntl-0681-frontier source audit

開始結論: (c) 保留 — `.681`は版に紐づくscoreとして未検証。基準blendのCV-LB対応を確認後、preview経路を使わないprompt-grouped OOFでembedding branchの補完性を測る証拠が必要。

- 確認日時: 2026-11-10 00:12 JST
- URL: https://www.kaggle.com/code/xiangqizhang/ntl-0681-frontier
- version: 1 / public / GPU enabled / Internet disabled
- 取得範囲: Kaggle MCP `get_notebook_info` source全文、session status、session output一覧。sourceは約264.7k文字。

## 確認できた内容

- 冒頭の説明は、親ensembleの公開`.680` Notebookを基にQwen3-Embedding-8B native expertの幾何平均重みを40%から50%へ変更し、他のモデル・重み・補正は固定した1パラメータ比較と主張する。Notebook本文にはこの構成の`.681`という自己申告があるが、Notebookタイトルと説明だけではKaggleの該当versionに紐づくLBスコアを検証できない。
- 推論実装はQwen3-Embedding-8Bを両T4へ分割し、5-fold native headと複数の既存stackを合わせる構成。本文は512 token windowで全文を処理しtailを捨てないと説明する。多数のdataset、upstream Notebook、modelへの依存があるため、完全な再現には添付と固定パスの監査が必要。
- `emit_known_preview` はtest CSVが完全一致する3レコードだけの場合に、ID・本文byte数・fingerprintを照合して固定の3予測を出し、重みをロードせずparquetを作る。その際のsidecarは `model_weights_loaded=false`、`hidden_runtime_verified=false` と記録する。それ以外の行構成では通常の全推論へ進む。よってpreview経路の成功はhidden推論やモデル性能の確認にならない。
- session statusは`COMPLETE`で、output一覧には`submission.mode.json`と`submission.parquet`がある。ただしこの一覧・完了statusから、出力が全hidden test由来であることやLBスコアは確認できない。`get_notebook_info`の`last_run_time`は2026-11-06 15:13 UTC。一方、直近のDateRun検索表示は2026-11-09の実行時刻だったため、run時刻メタデータには不一致がある。

## 判断

`.681`は未検証の公開主張として扱う。3件previewの仕組みは通常hidden入力の評価に使えず、scoreやOOFの根拠にもならない。現行のGPU割当や登録済み実験キューは変更しない。Kaggle上の作成・更新・提出は行っていない。

最終結論: (c) 保留 — 必要な証拠は、previewを使わないprompt-grouped OOF、同一splitの採用blend比較、該当版のscore source確認。
