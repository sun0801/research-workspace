---
date: 2026-07-07
project: sam2-mamba-motion-tracking
source: 2026-07-07-validation-implementation-spec
status: draft
tags: [plan, implementation, validation]
---

# Validation Implementation Plan

## 対象

- trajectory annotation の train / val 分離
- 学習中 val loss の追加
- 5 エポックごとの TrackEval hook の追加
- best checkpoint 保存基準の分離

## 対象ファイル

- `tools/gen_traj_data.py`
- `ssm_tracker/cfgs/MambaTrack.yaml`
- `ssm_tracker/cfgs/TrackSSM.yaml`
- `ssm_tracker/cfgs/MambaStateful.yaml`
- `ssm_tracker/train.py`
- `ssm_tracker/train_stateful.py`
- `ssm_tracker/train_utils/` 配下の新規共通 utility
- 必要なら tracking / evaluation 呼び出し用の新規 utility

## 実装方針

### Phase 1. annotation split 対応

1. `gen_traj_data.py` が `train` / `val` の両 split を出力できるようにする
2. `dancetrack_train.json` と `dancetrack_val.json` を生成する
3. config で train と val の annotation path を分けられるようにする

### Phase 2. val loss loop 追加

1. `train.py` に val dataloader を追加する
2. `train_stateful.py` に val dataloader を追加する
3. 共通 `run_validation_loss(...)` を `train_utils` に切り出す
4. Comet logging を `train/*` と `val_loss/*` に分離する
5. `best_val_loss.pth` を保存する

### Phase 3. TrackEval hook 追加

1. tracking validation 周期と評価先を config か CLI で指定できるようにする
2. periodic checkpoint 保存後に tracker 推論を実行する
3. TrackEval tracker directory に結果を配置する
4. `run_mot_challenge.py` を呼ぶ
5. `pedestrian_summary.txt` から HOTA / DetA / AssA / MOTA / IDF1 を parse する
6. Comet に `tracking_val/*` として記録する
7. `best_tracking_hota.pth` を保存する

### Phase 4. 検証

1. val loss のみを使う smoke run で train / val logging を確認する
2. `tracking_val_period=5` で TrackEval hook を確認する
3. summary parse と best checkpoint 更新が意図どおりか確認する

## 完了条件

- train / val split が分離されている
- 学習中に val loss が記録される
- 5 エポックごとに TrackEval が動く
- `best_val_loss.pth` と `best_tracking_hota.pth` が保存される
- Comet に tracking validation 指標が残る

## 懸念

- TrackEval 実行時間が学習をどれだけ押すか
- tracker result directory の掃除方法
- 将来 DDP 化したときの rank0 制御
