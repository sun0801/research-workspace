---
date: 2026-10-23
project: sam2-mamba-motion-tracking
spec: specs/2026-10-23-mose-adapter-train-refactoring-spec.md
status: completed
tags: [experiment, refactoring, temporal-mamba, sam2, mose, adapter]
---

# temporal adapter 学習コード（`mose_adapter_train.py`）のリファクタリング記録

[spec](../specs/2026-10-23-mose-adapter-train-refactoring-spec.md) に従い、学習の挙動を変えずに `training/mose_adapter_train.py` を整理した。各ステップで、変更前のコードの出力と照合した。

- 実装リポジトリ：`/mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2`、ブランチ `1002_seminar`（開始時点 `ff78b57`）
- 照合を回した GPU：142 の RTX A4000（すべての実行で同じ GPU）
- 照合の出力：同リポジトリの `runs/refactor_golden/<label>/`（`.git/info/exclude` で git 管理外）

## R0：照合の仕組みと基準

コミット `c2b85f6`。

- 照合条件は `configs/temporal_adapters/refactor_golden/` に固定した（学習経路は fp32、math attention、seed 123、LR 3e-4、warmup 1）。V1 は `chunk_len` 4、V3（3段）は 2 で、どちらも checkpointing あり。
  - pilot：V1・V3、2軌跡・3更新
  - train：V1・V3、2更新、val 2動画（8対象）を step 0・1・2 で実行
  - train の resume：train V1 の出力をコピーし、step 1 から再開
  - measure：V1・V3、short（9フレーム）・typical（55フレーム）で train → inference
  - check：V1
- 実行は `experiments/temporal_adapters/refactor_golden.sh`、照合は `training/refactor_golden_compare.py`。時間・VRAM・時刻の列は比べない。
- 軌跡の長さ：seed 123 で pilot・train に使う軌跡は 25・22 フレーム、measure の typical は 55 フレーム、val は 36・65 フレーム。履歴の保持幅（`max(num_maskmem=7, max_obj_ptrs_in_encoder=16) + 1 = 17`）を超えるので、古い出力の削除が実際に起きる。末尾に端数の区間も残る（例：25 は 4 でも 2 でも割り切れない）。seed は変えずに済んだ。

### 決定論の確認

| 実行 | 設定 | 2回の結果 |
|---|---|---|
| `base_a` / `base_b` | fp32・math attention（`--deterministic` なし） | **一致しない**。初回の更新の勾配から差が出た（V1 の `grad_norm_total` で相対 2e-6 程度、重みの差は最大 2.3e-4）。その結果、step 1 以降の val も対象ごとの J・F・loss が最大 5.7e-3 ずれた。重みが同じ step 0 の val（bf16 の推論）と、check・measure は一致した |
| `base_det_a` / `base_det_b` | 上に `--deterministic`（cuDNN の決定論的設定、TF32 無効、`torch.use_deterministic_algorithms(warn_only=True)`）と `CUBLAS_WORKSPACE_CONFIG=:4096:8` を追加 | **全項目が完全一致**（学習・pilot のログ、checkpoint の重み・optimizer・scheduler、val の対象ごとの結果、check、measure、val loss の参照値） |

- spec の手順どおり、R0 で `--deterministic`（既定はオフ）を加えて基準を取り直した。以後の照合の基準は `base_det_a` とする。
- 決定論的な実装がない演算の警告（`warn_only`）は出なかった。
- 所要時間：1組あたり約30分（`--with-ref` あり）。

### val loss の参照値（R5 用）

`training/refactor_golden_val_loss_ref.py` で、変更前の `run_trajectory` を、R5 と同じ固定条件（eval モード、bf16、評価と同じ前処理、val の prompt の seed、勾配なし）で流した。adapter の重みは、step 0 が初期値、step 1・2 が train の checkpoint。2回の実行で完全一致した。旧 `validate`（推論経路）の val loss とは、step 0 の 1 対象目で 0.0692 対 0.0686 程度の差がある（定義は同じで、計算経路が違う）。

## R1：記録と実際の処理を結びつける

コミット `b18f22b`。照合 `r1`：`base_det_a` と全項目が完全一致（manifest は比べない）。

- `--loss-weights`（既定 `20/1/1/1`）、`--val-seed-base`（既定 `1000003`）、`--spec` を追加した。
- manifest の `optimizer.no_decay` は、実際に除外したパラメータ名の一覧になった（V1 は8個、V3 は26個）。`freeze` には、凍結した SAM2 のパラメータ数（46,060,354）、SAM2 で学習するパラメータ名（空）、train モードの SAM2 子 module（空）、adapter の学習パラメータ名を記録する。`loss_weights` も記録する。
- optimizer を作るときに「1次元以下のパラメータがすべて除外されている」「`A_log` が除外されている」を確認する。bias を除外対象から外した場合と、`A_log` を外した場合に、どちらもエラーで止まることを確かめた。

## R2：使い終わった検証経路の削除

コミット `db58e94`（削除前のコミット `b18f22b` にタグ `mose-adapter-train-pre-refactor-parity`）。照合 `r2`：`base_det_a` と全項目が完全一致。

- `parity` / `ckpt-parity` モードと `parity_*` 引数、`run_trajectory` の `speedups` / `batch_encoder` 引数を削除した。GPU 正規化・エンコーダのチャンク単位のバッチ化・有限値チェックの同期遅延は常に有効（`pilot` / `train` / `measure` / `check` はもともとこの設定）。
- 決定論的設定は `--deterministic` だけで有効になる。`training/README_temporal_adapters.md` に、削除したモードはタグから実行することを書いた。

## R3：`run_trajectory` を責務ごとに分ける

コミット `ac75eb1`。照合 `r3`：`base_det_a` と全項目が完全一致。

- `encode_chunk`（読み込み・正規化・エンコーダのバッチ化）、`track_frame`（1フレームの `track_step` と loss）、`end_chunk`（TBPTT の境界での detach と古い出力の削除）、`TrajectoryMetrics`（loss の内訳・J・`residual_ratio` の集計）に分けた。
- `run_trajectory` は、`args` 全体ではなく `TrajectoryConfig`（`bf16`, `resolution`, `chunk_len`）と拡張 `(aug, retry, frame0)` を受け取る。学習用の拡張は `train_trajectory`（`choose_augmentation` → `run_trajectory`）で選ぶ。
- val・推論計測の前処理の dict を `eval_augmentation` にまとめた。フレーム別の弱い色変換は従来どおり残る。
- `stream_inference_timing` の古い出力の削除を `prune_history` と `history_keep` に揃えた。単体確認（`training/refactor_golden_prune_check.py`）で、変更前のその場で書いた処理と、各フレームの後に残るフレームが一致した（保持幅4通り×長さ6通り×区間長3通り、1,768状態）。
- `measure` の推論の後に、SAM2 の子 module が eval、adapter が train に戻ることを確認した。

## R4：1 update の処理の共通化

コミット `5d904c9`。照合 `r4`：`base_det_a` と全項目が完全一致。

- 「`train_trajectory` → 勾配・重みの変化のノルム → `optimizer_update` → 記録行」を `train_step` にまとめ、`mode_train` と `mode_pilot` から使う。勾配ノルムを記録する間隔は従来どおり（train は `grad_log_interval` ごとと 1 step 目、pilot は毎 step）。

## R5：val の2本立て

コミット `09a30a7`。照合 `r5`（判定は `training/refactor_golden_r5_check.py`）：**合格**。

- val J/F は、凍結済みの `eval_mose_fulltrack.evaluate_track` を対象ごとに呼ぶ形にした。学習コード側の追跡ループのコピーはなくなった。
- val loss は `run_trajectory` を eval モード・bf16・勾配なしで、評価と同じ前処理と prompt の seed で流して計算する（adapter は state を明示的に渡す、学習と同じ forward）。対象ごとの jsonl に、loss 側と J/F 側で prompt とフレーム数が一致したかの列（`loss_pass_prompt_match`, `loss_pass_frames`）を加えた。

| 判定項目 | 結果 |
|---|---|
| 学習・pilot のログ、checkpoint、check、measure | `base_det_a` と完全一致 |
| val の J・F・J&F・prompt・`frames_scored`（対象ごと、step 0・1・2） | `base_det_a`（旧 `validate`）と完全一致 |
| val loss と内訳（対象ごと） | 変更前のコードで作った参照値と完全一致 |
| loss 側と J/F 側の prompt・フレーム数 | 全対象で一致 |

旧 `validate`（推論経路）の val loss との差（参考値。72 対象・step）：

| 項目 | 差の最大 | 差の平均 |
|---|---|---|
| loss | 6.3e-3 | 9.1e-4 |
| loss_mask | 1.2e-4 | 1.6e-5 |
| loss_dice | 2.3e-3 | 2.9e-4 |
| loss_iou | 5.7e-3 | 8.3e-4 |
| loss_class | 6.7e-5 | 8.6e-6 |

val 全体の平均（8 対象）では、たとえば V1 の step 0 で 0.12927（旧）→ 0.12910（新）。過去の V1/V3 のログの val loss とは、この程度ずれる。

val の時間（照合条件：math attention、8 対象）：V1 は 1 回あたり約 97 秒 → 約 208 秒、V3 は約 110 秒 → 約 235 秒（約 2.1 倍）。J/F 用と loss 用で2回流すため。

## 最後の確認：本学習と同じ設定での完走

コミット `09a30a7` で、`configs/temporal_adapters/train_v3.yaml`（bf16、`chunk_len` 8、checkpointing あり、flash attention、`--deterministic` なし）を、2更新・val 2動画（8対象）・step ごとの val に変えて流した（出力 `runs/refactor_golden/final_bf16_v3/`、所要約7分）。**合格**。

- エラーなく完走した。VRAM のピークは 12.43 GiB、学習は約 0.23 秒/フレーム（10/18 の記録と同じ水準）。
- step 0 の val は、8 対象すべてで、保存済みの F0（`runs/mose_temporal_mamba_20260930/tuning/F0_step_002789`、A4000）と J・F・J&F・`frames_scored`・prompt が完全一致した。
- val の時間は 8 対象で約 125 秒だった。照合条件での倍率（約 2.1 倍）を当てはめると、本学習の val（64 対象。V1 の本学習では 1 回あたり約 480 秒）は 1 回あたり約 17 分になる見込み（未実測）。1 周（2,789 更新、val 13 回）では、合計で約 2 時間延びる見込み。

## まとめ

- R0〜R5 のすべてで照合に合格し、1 ステップ 1 コミットで `1002_seminar` に入れた（`c2b85f6`, `b18f22b`, `db58e94`, `ac75eb1`, `5d904c9`, `09a30a7`）。R0〜R4 は学習の挙動を一切変えていない（fp32・決定論的設定で完全一致）。
- 挙動として変わったのは、R5 の val loss の計算経路（推論経路 → 学習と同じ forward）だけ。J/F は変わらない。過去の V1/V3 のログと val loss を比べるときは、対象ごとに最大 6e-3 程度ずれることに注意する。
- 照合に使ったスクリプトはリポジトリに残した（`experiments/temporal_adapters/refactor_golden.sh` など）。ただし、`training/refactor_golden_val_loss_ref.py` は変更前（R2 まで）の `run_trajectory` 専用で、R3 以降のコードでは動かない。
- 今後 `mose_adapter_train.py` を変えるとき（短い区間での学習など）も、同じ照合（`base_det_a` との比較）で既存の全軌跡学習が変わっていないことを確かめられる。照合用の YAML は `--deterministic` を使うので、`CUBLAS_WORKSPACE_CONFIG=:4096:8` が必要（スクリプトで設定済み）。
