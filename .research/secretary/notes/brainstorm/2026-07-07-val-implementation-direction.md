---
date: 2026-07-07
project: sam2-mamba-motion-tracking
tags: [brainstorm, validation, trackeval, implementation]
---

# val実装方針の整理

## 相談の出発点

TODO「本来の意味のvalを実装する（過学習チェック用 + 5エポックごとのHOTA評価）」を、どのような構成で実装するか整理した。

## 現在の理解

- `val loss` と `tracking validation` は別物として扱うべき
- `val loss` は、学習中の過学習チェック用の next-step bbox / delta prediction loss
- `tracking validation` は、学習中に checkpoint を使って tracker を動かし、TrackEval で HOTA などを算出する評価
- `DanceTrack val` は official split をそのまま使う

## 決めた方針

### 1. validationを2系統に分ける

- `val loss`
  - `dancetrack_val.json` を使って計算する
  - ログは `val_loss/*` 系で分ける
- `tracking validation`
  - 5エポックごとに実行する
  - 既存 checkpoint で推論し、TrackEval で HOTA / DetA / AssA / MOTA / IDF1 を算出する
  - ログは `tracking_val/*` 系で分ける

### 2. TrackEvalは既存リポジトリをそのまま使う

- 利用先: `/mnt/HDD10TB-2/aburatani/TrackEval`
- GT: `/mnt/HDD10TB-2/aburatani/TrackEval/data/gt/dancetrack/val`
- 実行スクリプト: `/mnt/HDD10TB-2/aburatani/TrackEval/scripts/run_mot_challenge.py`
- tracker result 置き場:
  `/mnt/HDD10TB-2/aburatani/TrackEval/data/trackers/dancetrack/val/<tracker_name>/data/*.txt`

初回実装では、推論スクリプトや TrackEval を大きくリファクタせず、既存 CLI をそのまま呼ぶ方向で進める。

### 3. subprocess相当の呼び方で最小変更にする

- `track.py` / `track_stateful.py` は既存 CLI のまま使う
- 学習コードから epoch 後フックとして呼ぶ
- TrackEval 実行後、`pedestrian_summary.txt` を parse して Comet に記録する

## 実装順

1. `dancetrack_train.json` / `dancetrack_val.json` を生成できるようにする
2. `train.py` / `train_stateful.py` に `val loss` 用 dataloader と evaluation loop を追加する
3. 5エポックごとの tracking validation hook を追加する
4. TrackEval の summary を parse して Comet に記録する
5. `best_val_loss.pth` と `best_tracking_hota.pth` を分けて保存する

## 注意点

- `val loss` と `HOTA best` は一致しない可能性が高いので、best checkpoint の基準を分ける
- tracking validation は train loop 本体に埋め込まず、epoch 後フックとして分離する
- TrackEval 入力ディレクトリには古い結果が残らないように管理する
- 将来 DDP 対応する場合は `rank0` のみで tracking validation を回す設計にする

## 次アクション

- まずは最小変更で `val loss` と `TrackEval hook` を実装する
- 初回は既存スクリプトをそのまま呼ぶ形で通し、必要になってから関数化を検討する
