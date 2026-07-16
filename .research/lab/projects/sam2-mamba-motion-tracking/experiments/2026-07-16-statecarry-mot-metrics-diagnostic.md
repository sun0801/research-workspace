# State carry の MOT metrics epoch 間不変に関する診断

## 対象

- 対象実験: `mamba_stateful` / `MambaStateful`
- 学習設定: 100 epochs、`val_loss_period=5`、`mot_metrics_period=10`
- 比較したチェックポイント: epoch 10 と epoch 90
- 比較シーケンス: `dancetrack0004`
- 生ログ・比較結果: `artifacts/profiling/mamba_validation_2026-07-15/full_validation/statecarry_epoch_compare/`

## 結論

Comet 上で state carry の `mot_metrics` が 1 点に見えるのは、記録処理が 1 回しか実行されていないためではない。validation log では epoch 10, 20, ..., 80 で同じ値が繰り返し返され、epoch 90 も実行開始している。値が完全に重なっているため、グラフ上では水平な 1 本の線に見えている。

一方で、epoch 10 と epoch 90 のチェックポイントは異なるモデル出力を生成している。代表的な実入力に対する最終的な stateful model output は次の通りだった。

```text
epoch 10: [-0.03230805,  0.40133941, 0.07352956, -0.45183820]
epoch 90: [-0.17897239, -0.03901222, 0.89995265,  0.72872525]
```

それにもかかわらず、通常出力の tracking result は epoch 10 と epoch 90 で完全一致した。

```text
normal epoch10 == normal epoch90
SHA256: 73631b0c658520ca332e9926ece7d4399d801fd4266a8d25ca767ae4c27297f7
```

※上記の SHA256 は比較ログに記録された値を転記したもの。

## 観測された挙動

- 通常出力は epoch 10/90 とも 3407 行、1189 frames、861 unique IDs。
- 各 ID の最大継続長は 5 records。
- frame 1--5 には track output があるが、frame 6 は output がなく、frame 7 から新しい ID が現れる。
- epoch 10/90 の通常出力ファイルは完全一致した。
- `--debug` 出力は通常出力とは異なるが、epoch 10/90 間では完全一致した。
- したがって、チェックポイント差が最終 MOT result に反映される前に、同じ deterministic な track break / reactivation パターンへ収束している可能性が高い。

## 実装上の切り分け

`track.py` と `track_stateful.py` は、通常出力時に最新検出 bbox を使うという点では同じ挙動である。両者の差は、主に track prediction の生成経路にある。

- 通常 `track.py`: `memo_bank` と `diff_memo_bank` から各フレームに prediction を再計算する。
- `track_stateful.py`: `InferenceParams` を使って cached state / `pending_delta` を更新し、state carry prediction を生成する。
- `StateCarryTracklet.predict()` は、履歴が `enable_time_thresh=5` 未満では最新 bbox を使い、それ以降は `pending_delta` に基づく予測 bbox を `predicted_last_bbox` に設定する。
- matching は予測 bbox を用いる。予測が検出とマッチしない場合、旧 track は lost になり、後から activate された新 track は frame 1 以外では直ちに出力されない実装になっている。

このため、frame 6 付近で全 track が一斉に prediction/matching に失敗し、frame 7 以降に新しい track が再生成される挙動が、今回の「metrics が変わらない」現象の有力な説明である。ただし、現時点では frame 6 の IoU、`pending_delta`、match/no-match 判定を直接記録していないため、実装上の根本原因としては未確定である。

## 次に確認すべきこと

1. epoch 10/90 の frame 5--7 について、検出 bbox、`predicted_last_bbox`、`pending_delta`、matching IoU、track state を同時に記録する。
2. `enable_time_thresh=5` 到達直後に prediction が有効になる条件と、state carry の delta のスケール・clip が妥当か確認する。
3. frame 6 で match 失敗した場合に、新規 track を同一フレームで出力しない仕様が意図通りか確認する。

現段階では、学習結果や既存 tracker 実装を変更せず、まず上記の局所的な診断を行う。

## 参照ファイル

- `ssm_tracker/track.py`
- `ssm_tracker/track_stateful.py`
- `ssm_tracker/track_utils/tracklet.py`
- `ssm_tracker/track_utils/stateful_tracklet.py`
- `ssm_tracker/track_utils/matching.py`
- `ssm_tracker/cfgs/MambaStateful.yaml`
