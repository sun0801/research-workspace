---
project: sam2-mamba-motion-tracking
date: 2026-07-17
experiment: statecarry-single-video-overfit
status: completed
---

# State Carry 1動画過学習・同一動画tracker推論

## 目的

`dancetrack0004` 1本の動画とそのGTで `MambaStateful` を学習し、epoch 1とepoch 100のcheckpointを同じ動画の検出結果へ入力する。学習lossの低下がState Carry trackerの推論安定化につながるかを確認する。

## 実験条件

- 対象動画: `dancetrack0004`
- フレーム数: 1203
- annotation: TrackEval GTから生成した一時annotation（4 objects、1203 frames）
- detector input: 既存の`dancetrack0004.txt`
- window size: 12
- 最大epoch: 100
- validation: 同一動画で実施、`val_loss_period=1`
- MOT metrics: 無効（`mot_metrics_period=0`）
- timing: 無効
- 外部リポジトリのソースコード: 変更なし
- 一時ファイル置き場: `/tmp/statecarry-single-video-20260717/`

使用したspec:

- [`2026-07-17-statecarry-single-video-overfit-spec.md`](../specs/2026-07-17-statecarry-single-video-overfit-spec.md)

## 学習結果

- smoke（1 epoch）: 71 steps完走、validation loss `0.1117426806`
- 本学習 epoch 1: validation loss `0.1116820633`
- 本学習 epoch 100: validation loss `0.0565291941`
- epoch 1からepoch 100へのloss比: 約`0.51`
- checkpoint:
  - `/tmp/statecarry-single-video-20260717/checkpoints/statecarry_dancetrack0004_overfit/epoch1.pth`
  - `/tmp/statecarry-single-video-20260717/checkpoints/statecarry_dancetrack0004_overfit/epoch100.pth`

lossは低下したが、specで設定した「初期lossの1/10以下」には到達しなかった。

## tracker推論結果

既存検出結果を同じ入力として、`--debug`付きで同一動画を推論した。

| checkpoint | 出力行数 | 出力フレーム数 | 出力ID数 | 全track欠落フレーム | NaN/Inf |
|---|---:|---:|---:|---:|---|
| epoch 1 | 4200 | 1203 | 104 | 0 | なし |
| epoch 100 | 3407 | 1189 | 861 | 14 | なし |

frame 5〜7の出力track数:

| checkpoint | frame 5 | frame 6 | frame 7 |
|---|---:|---:|---:|
| epoch 1 | 3 | 3 | 2 |
| epoch 100 | 3 | 0 | 2 |

epoch 100の全track欠落フレームは次の14フレームだった。

`6, 11, 21, 293, 317, 323, 331, 592, 597, 775, 797, 802, 807, 812`

## 判定

### 達成

- 1本の動画だけで100 epochの学習を完走した。
- epoch 1とepoch 100のcheckpointを同じ動画でtracker推論できた。
- 出力ファイルにNaN/Infは現れなかった。

### 未達

- validation lossは約半分までしか低下せず、強い過学習の基準には未達だった。
- epoch 100の推論ではframe 6を含む14フレームで全trackが欠落した。
- epoch 100ではtrack ID数が861まで増加し、epoch 1の104より推論が不安定化した。

## 結論と次の切り分け

学習lossの低下だけでは、State Carry trackerのフレーム遷移安定性は改善しなかった。むしろ今回のepoch 100 checkpointでは、既存のState Carry推論不具合が顕在化した可能性がある。

次に確認すべき項目は、frame 6付近での`pending_delta`、`predicted_last_bbox`、`InferenceParams`の状態である。これらは現行の`track_stateful.py`の`--debug`出力だけでは直接観測できないため、既存の診断specに沿った一時的な状態ログ追加を別実験として行う。
