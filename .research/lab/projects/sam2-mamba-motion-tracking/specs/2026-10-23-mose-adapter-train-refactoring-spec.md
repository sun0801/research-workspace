---
date: 2026-10-23
project: sam2-mamba-motion-tracking
source: code-review
status: approved
approved: 2026-10-23
tags: [spec, refactoring, temporal-mamba, sam2, mose, adapter]
---

# temporal adapter 学習コード（`mose_adapter_train.py`）のリファクタリング Spec

## 目的

`training/mose_adapter_train.py`（1,127行）を、**学習の挙動を変えずに**整理する。各ステップで、変更前のコードの出力と照合して一致を確かめながら進める。

解消したい問題は次の3つ（2026-10-23 のコードレビューのフィードバックを、コードと実験記録で確認した結果）。

1. 学習中の val と本評価が、別々にコピーした追跡ループで測られている。一致は 10/18 に実測で確かめたが（`to_input` の全要素一致、step 0 の val と保存済み F0 の一致）、今後どちらかだけ直すとずれる。
2. `run_trajectory` が、学習アルゴリズム・入力の読み込み・高速化の切り替え・記録用の指標・parity 検証用の logits 収集を1つの関数で抱え、bool フラグ（`train`, `speedups`, `batch_encoder`, `collect_logits`）で切り替えている。`mode_train` と `mode_pilot` の1 update 分の処理もほぼ同じコピーになっている。
3. 記録と実際の処理が結びついていない。loss の重み `20/1/1/1` が args にも manifest にも残らない。manifest の `no_decay` / `freeze` は手書きの説明文で、adapter のパラメータ名が変わると weight decay の対象がエラーなしで変わる。

## 範囲

対象外とするもの：

- **学習方法の変更**（10/23 MTG の短い区間での学習、SAM2 準拠の学習）。別の spec で扱う。リファクタリングと挙動の変更を同時に進めると、結果が変わったときに原因を切り分けられないため。
- **DanceTrack の定期評価**。別の spec で扱う。
- SAM2 の private 属性（`_prepare_backbone_features`, `_last_multimask_ious`）への依存。SAM2 の内部を触る以上は避けにくい。
- `OLD_RUN` の固定パス（優先度が低い）。
- `enable_temporal_mamba_adapter` を使わない件。この関数は旧 `TemporalMambaAdapter` 専用で、V1/V3（`build_temporal_adapter`）には使えないため、FB の指摘は当たらない。

変更しないファイル：

- `training/eval_mose_fulltrack.py`, `training/mose_fulltrack.py`。lockbox 評価が自分自身の sha256 を `lockbox_eval_freeze.json` と照合しているため（`eval_mose_fulltrack.py` 250〜252行）。import して使うだけにする。
- `sam2/` 以下、`training/mose_adapter_eval.py`。

## 実装リポジトリ

- `/mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2`
- ブランチ：`1002_seminar`（開始時点 `ff78b57`）
- 1ステップにつき1コミットにする。

## 変更内容

| # | 内容 | 挙動への影響 |
|---|---|---|
| R0 | 照合の仕組みを用意する（下の「検証方法」）。変更前のコードで基準の出力を取る | なし |
| R1 | 記録まわりを直す（下に詳細） | manifest の記述のみ |
| R2 | 使い終わった検証経路を削除する | なし（`pilot` / `train` / `check` / `measure`） |
| R3 | `run_trajectory` を責務ごとに分ける | なし |
| R4 | 1 update の処理を `train_step` にまとめる | なし |
| R5 | `validate` を「J&F は `evaluate_track`、loss は学習経路」の2本立てにする | val loss の計算経路が変わる |

### R1：記録と実際の処理を結びつける

- loss の重み（`loss_mask: 20, loss_dice: 1, loss_iou: 1, loss_class: 1`）、val の seed の起点（`1000003`）、manifest に書く spec のパスを、args / YAML の設定に移す。既定値は今の値のままにする。
- manifest の `optimizer.no_decay` を、実際に weight decay から除外したパラメータ名の一覧にする。`freeze` は、凍結したパラメータ数と学習するパラメータ名にする。
- optimizer を作るときに、次を assert する。adapter のパラメータ名が変わり、weight decay の対象が黙って変わったときに止めるため。
  - 1次元以下のパラメータが、すべて除外されている
  - `A_log` が除外されている
  - 2026-10-23 時点の V1（除外8個）・V3 3段（除外26個）で、どちらも成り立つことを確認済み

### R2：使い終わった検証経路の削除

- 削除前のコミットにタグ `mose-adapter-train-pre-refactor-parity` を打ち、過去の検証は git から再現できるようにする。
- 削除するもの：
  - `parity` / `ckpt-parity` モードと、その引数（`parity_*`）
  - `run_trajectory` の `speedups=False` の経路と `batch_encoder` 引数
  - `speedups` は常に有効として扱う。本学習（`pilot` / `train`）はもともと `speedups=True` で実行している。
- 残すもの：
  - `check` が使う logits の収集
  - 先読みなしの `FrameSource`（`check` が使う）
- `main` の決定論的設定（今は parity 系のモードの fp32 だけで有効）は、R0 で `--deterministic` フラグにした場合はそちらに引き継ぐ。

### R3：`run_trajectory` を責務ごとに分ける

- 次の単位に分ける。
  - 入力：フレームの読み込み、正規化、エンコーダのバッチ化
  - 1フレーム分の `track_step` と loss
  - TBPTT の区間分割と、区間の終わりでの detach・古い出力の削除
  - 指標の集計：loss の内訳、J、`residual_ratio`
- 拡張の選び方（`choose_augmentation`）を `run_trajectory` の外に出し、呼び出し側が拡張を渡す形にする。R5 で、val loss に「従来の val と同じ前処理」を渡すため。
- `args` 全体ではなく、必要な値（`bf16`, `resolution`, `chunk_len`）だけを受け取る。精度（`bf16`）も呼び出し側が明示的に渡す。
- val・推論計測で使う前処理の dict を定数1つにまとめる（今は 404行と 751行に同じ dict がある）。この dict は flip・回転・shear・動画単位の色変換を無効にするが、`load_frame_uint8`（96〜99行）と凍結 `load_frame`（226〜229行）が、フレームの seed から決まる弱い色変換（brightness 0.9〜1.1 など）を常にかける。**完全な無拡張ではない**が、凍結評価・F0 の評価と同じ条件なので今回はそのまま保つ。完全な無拡張への変更は挙動の変更なので、扱うなら別 spec にする。`stream_inference_timing` の、古い出力の削除をその場で書いている部分は `prune_history` に揃える。削除の基準になるフレームは同じ（`idx - max(num_maskmem, max_obj_ptrs_in_encoder) - 1`）。

### R4：1 update の処理の共通化

- 「`run_trajectory`（学習）→ 勾配・重みの変化のノルム → `optimizer_update` → 結果の dict」を `train_step` にまとめ、`mode_train` と `mode_pilot` の両方から使う。
- 勾配ノルムを記録する間隔は今のまま（`train` は `grad_log_interval` ごとと1 step 目、`pilot` は毎 step）。呼び出し側から指定する。

### R5：val の2本立て

10/23 の相談で、Mamba_Trackers（`train_mamba_stateful.py`）の形に揃えることにした。Mamba_Trackers では、val loss を学習と同じ forward で計算し（`run_stateful_validation`）、追跡指標は推論スクリプトそのものを実行して計算している（`run_mot_metrics`）。

- **val J&F**：凍結されている `eval_mose_fulltrack.evaluate_track` を import して、対象ごとに呼ぶ。追跡ループのコピーはなくなる。精度は `evaluate_track` の中で bf16 に固定されている（134行）。今の `validate` も bf16 固定なので、変わらない。
- **val loss**：`run_trajectory` を勾配なしで実行して計算する。条件は次のとおりに固定する。

| 項目 | 条件 | 理由 |
|---|---|---|
| モデルのモード | `model.eval()`（SAM2 のトップ・子 module・adapter のすべてを eval） | 今の `validate` と同じ。Mamba_Trackers の `run_stateful_validation` も eval で計算している。SAM2 のトップは、train/eval でメモリ用マスクの二値化（`sam2_base.py` 1063行）、メモリの stride（864行）、出力の項目（1260行）が変わる。学習時の `set_frozen_modes`（トップだけ train）とは別の条件になる |
| adapter の経路 | state を明示的に渡す経路（学習と同じ forward） | adapter の経路は state の有無で決まり、モードには依存しない（`sam2_base.py` 1136〜1147行） |
| 精度 | bf16 に固定（`--bf16` / `--no-bf16` に依存しない） | 今の `validate` と同じ |
| 前処理 | R3 の val 用 dict と、val の prompt の seed（`1000003 + i`） | J&F 側と同じ入力・同じ prompt にするため |
| state | 対象ごとに `reset_motion_states` と `init_state` で初期化する | 今の `validate` と同じ |
| 終了時 | 正常終了でも例外でも、`set_frozen_modes` と `adapter.reset_state()` で学習時のモードに戻す | 今の `validate` と同じ |

- 集計の定義は今のまま保つ。loss は対象ごとに「フレームごとの `core_loss` の平均」を取り、それを対象について平均する。内訳も同様。J・F・J&F は、対象の平均を動画ごとに平均し、さらに動画について平均する。
- 対象ごとの jsonl は、今のキー（`video`, `object_id`, `prompt_seed`, `frames_scored`, `loss`, 内訳, `prompt_point_coords`, `J`, `F`, `J&F`）を保つ。2つの経路で prompt（座標・label）とフレーム数が一致したかどうかを記録する列を加える。
- val は2回流すことになるので、時間が延びる（今は1回あたり約10分。延びる分は未計測で、R5 で実測して記録する）。

## 検証方法

### 照合用の実行（R0 で用意する）

- 実行する場所：142 の RTX A4000。基準も、各ステップの後の照合も、同じ GPU で回す。実行は Claude が行う（2026-10-23 のユーザー指示）。
- 実行条件は、R0 で照合用の YAML（`configs/temporal_adapters/refactor_golden/`）と実行スクリプトに固定してコミットする。各実行の manifest に、LR・warmup・`chunk_len`・checkpointing・入力 index と SAM2 checkpoint の sha256・使った対象の ID とフレーム数・出力先を残す。
- 共通の設定：`--math-attention`、`--no-comet`、seed 123、LR 3e-4、`warmup_steps` 1、`grad_log_interval` 1。

**精度（経路ごと）**

`--no-bf16` で fp32 になるのは `run_trajectory` だけで、val・評価・推論計測はコードの中で bf16 に固定されている。照合実行での精度は次のとおり。

| 経路 | 照合実行での精度 |
|---|---|
| 学習・pilot の診断用 loss（`run_trajectory`） | fp32（`--no-bf16`） |
| val J&F（旧 `validate`、新 `evaluate_track`） | bf16（コード内で固定） |
| val loss（旧 `validate`、新 `run_trajectory`） | bf16（旧はコード内で固定、新は R5 で固定） |
| `measure` の推論（`stream_inference_timing`） | bf16（コード内で固定） |

**実行する条件**

| 条件 | adapter | 設定 |
|---|---|---|
| pilot | V1 | 2軌跡・3更新、`chunk_len` 4、checkpointing あり |
| pilot | V3（3段） | 2軌跡・3更新、`chunk_len` 2、checkpointing あり（10/18 の確認では、fp32・math attention の V3 3段を A4000 に収めるために TBPTT を 2 にした） |
| train | V1 | 2更新、`chunk_len` 4、checkpointing あり、`val_videos` 2、`val_interval_steps` 1（step 0・1・2 で val と checkpoint） |
| train | V3（3段） | 2更新、`chunk_len` 2、checkpointing あり、他は V1 と同じ |
| train（resume） | V1 | 上の train の出力ディレクトリを**別の場所にコピー**し、そのコピーの step 1 の checkpoint から step 2 まで再開する（resume は checkpoint と同じディレクトリに書き込むため、基準の成果物を壊さないようにする） |
| measure | V1・V3 | `short` と `typical` の軌跡で train → inference |
| check | V1 | `chunk_len` 4 |

**軌跡の長さの条件**

照合に使う軌跡（pilot・train・measure・val）のうち少なくとも1本が、次をすべて満たすようにする。R0 で使う軌跡のフレーム数を確かめ、満たさなければ照合用の seed を変えて選び直す。

- 履歴の保持幅（`max(num_maskmem, max_obj_ptrs_in_encoder) + 1`）より十分長く、古い出力の削除が実際に起きる（目安 40 フレーム以上）
- TBPTT の区間の境界をまたぎ、末尾に端数の区間が残る（長さが `chunk_len` で割り切れない）

**val loss の参照値（R5 用）**

R0 の照合スクリプトで、変更前（`ff78b57`）の `run_trajectory` を、R5 の val loss と同じ固定条件（eval モード、bf16、val 用の前処理、val の prompt の seed、勾配なし）で val 対象に流し、「意図する新しい val loss」の参照値を取っておく。変更前の `run_trajectory` は中で学習用の拡張を選ぶので、照合スクリプトの中だけで `choose_augmentation` を差し替える。実装ファイルは変更しない。

**照合スクリプトが比べるもの**

- 学習ログ・pilot ログ・val ログの数値（時間・VRAM・時刻の列は除く）
- checkpoint の中身：adapter の重み、optimizer・scheduler の状態、step、sample_order（`torch.equal` か完全一致）
- 対象ごとの val の結果（J・F・J&F・loss・内訳・prompt・フレーム数）
- `check` のレポート
- `measure` の行のうち、時間・VRAM 以外（label、kind、対象、フレーム数、OOM の有無）と、実行後に SAM2 の子 module が eval・adapter が train に戻っていること
- 古い出力の削除：R3 で書き換える削除処理と、変更前のその場で書いた処理に、同じ `output_dict` とフレーム番号の列を与え、各フレームの後に残るキーが一致すること（GPU なしの単体確認）

**決定論の確認**

最初に、変更前のコード（`ff78b57`）で上の全条件を2回回し、2回の結果が完全に一致することを確かめる。fp32 の学習経路だけでなく、bf16 の推論経路（val J&F・val loss・参照値）も対象にする（過去に bf16 で一致しなかったのは backward を含む学習で、推論だけの場合は未確認）。

- 一致しない場合は、R0 で `--deterministic`（cudnn の決定論的設定、TF32 の無効化。既定はオフ）を加え、それを有効にして基準を取り直す。
- それでも一致しない項目があれば、その項目は2回の差を「ノイズの基準」として記録し、判定を「差がこの基準の2倍以内」に切り替える。どの項目をこの扱いにするかは、進める前にユーザーに相談する。

### 各ステップの合格条件

- R0〜R4：上の照合対象がすべて完全一致すること。R1 では manifest だけが変わり、新しく加えた項目が入っていることも確かめる。
- R5：
  - val J&F：対象ごとに J・F・J&F が旧 `validate` と完全一致すること
  - val loss：対象ごとの loss・内訳が、R0 で取った**参照値と完全一致する**こと（これが合格条件）
  - 対象ごとの prompt（座標・label）とフレーム数が、J&F 側・旧 `validate`・参照値のすべてで一致すること
  - 旧 `validate` の val loss（推論経路）との差は、定義の変更による参考値として、対象ごとの最大差・平均差を記録する（合格条件にはしない）
  - 学習ログ・重み：完全一致すること（val は学習に影響しない）
  - val の時間：新旧を実測して記録する
- 全ステップの後に、本学習と同じ設定（bf16、`chunk_len` 8、checkpointing あり）で V3 の train を2更新・val 少数で流し、エラーなく完走すること、step 0 の val J&F が保存済みの F0 の値（該当対象）と一致することを確かめる。

## 実施手順

1. この spec の承認を受ける。
2. R0：照合用の YAML・実行スクリプト・照合スクリプトを書き、`ff78b57` で基準を2回取る。決定論的に一致するか、軌跡の長さの条件を満たすかを確かめる。val loss の参照値も取る。
3. R1〜R5：1ステップずつ「変更 → 照合 → コミット」を繰り返す。合格しなかったら次へ進まず、直すかユーザーに相談する。
4. 全ステップの後に bf16 で完走を確認し、結果を `experiments/` に記録する。README の更新履歴にも追記する。

## リスク・懸念

- fp32・math attention の照合では、bf16 の本学習で使う経路の一部（flash attention など）は通らない。全ステップの後の bf16 での完走確認で補う。
- 照合で使う軌跡は少数（2軌跡・数更新）に限られるので、すべての分岐を通る保証はない。履歴の削除・区間の境界・端数の区間は、「軌跡の長さの条件」で通ることを確かめる。
- R5 で val の時間が延びると、本学習の所要時間が延びる。
- resume は、変更前の resume と変更後の resume を比べる。連続実行と resume の結果は比べない（resume 時に重みの変化量の基準 `init_params` を作り直すので、`delta_norm` のログは連続実行と一致しない）。
- 並行して学習を回す場合、このブランチのコードは途中の状態になりうる。本学習は、リファクタリングを終えたコミットか、`ff78b57` で回す。

## 未決事項

R0 の結果で決まるもの（どちらも、決まり方は上に定めた）：

- bf16 の推論経路（val J&F・val loss）が、同じ条件の2回で完全に一致するか。一致しなければ、`--deterministic` を試し、それでも一致しない項目はノイズの基準での判定に切り替える（ユーザーに相談してから）。
- 照合用の seed 123 で、軌跡の長さの条件を満たすか。満たさなければ seed を変える。

## 関連

- レビュー FB と相談の経緯：2026-10-23 のセッション（この spec の「目的」「範囲」に要点をまとめた）
- [V3 MOSE adapter 学習 spec](2026-10-18-temporal-mamba-v3-mose-adapter-spec.md)、[実験記録](../experiments/2026-10-18-temporal-mamba-v3-mose-adapter.md)（照合の前例：経路の一致、`to_input` の1ulp修正、step 0 の val と F0 の一致）
- [10/23 MTG 議事録](../meetings/2026-10-23-mtg.md)（学習方法の変更は別 spec）

## 改訂履歴

| 日付 | 内容 |
|---|---|
| 2026-10-23 | 初版 |
| 2026-10-23 | レビュー（[検査メモ](../../../../secretary/notes/brainstorm/2026-10-23-mose-adapter-train-refactoring-spec-review.md)）を反映：経路ごとの精度の表、val loss の条件（eval モード・bf16 固定・state の初期化と復元）と参照値による合格基準、前処理の記述の修正（フレーム別の色変換は残る）、measure・履歴削除・端数の区間の照合、train の V3 設定と resume の手順、未決事項の更新 |
| 2026-10-23 | ユーザーが承認 |
