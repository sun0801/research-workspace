# xiangqizhang/ntl-0681-frontier source audit

開始結論: (b) 試さない — `.681`は版に紐づくLB scoreも独立OOFも確認されず、leader`.768`より低い。preview経路を除く再現に必要なlarge stackのsource/依存物が特定できない。

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

最終結論: (b) 試さない — 現top`.768`・confirmation待ち候補を明確に超える根拠がなく、score/OOFは未検証、previewを除く再現sourceも揃わない。

## 2026-11-12 follow-up after baseline CV-LB check

基準blend v12がPublic`.541`、primary OOF BA`.586408`で採点成功したため、当初の「CV-LB対応待ち」は解消した。一方、CV-LB対応点は1件のみ。sourceの`.681`はKaggleの該当version scoreとして確認できず、3件previewはweights未読込・hidden runtime未検証とsource sidecarが示す。previewを使わないOOF/score provenanceと再現可能なdependency setが依然ない。Qwen embedding branch単体では既存complementarity screensも独立候補を通していない。よって(b)試さないで終了する。
