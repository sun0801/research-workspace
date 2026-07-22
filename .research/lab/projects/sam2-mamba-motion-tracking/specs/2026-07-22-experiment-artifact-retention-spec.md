---
date: 2026-07-22
project: sam2-mamba-motion-tracking
source: p0-75-historical-baseline-audit
status: approved
tags: [spec, experiment-infrastructure, provenance, comet, reproducibility]
---

# Experiment artifact retention spec

## 目的

学習・推論・TrackEvalの成果物を実験run単位で保存し、checkpoint・config・コード状態・入力・評価結果を後から照合できるようにする。P1以降の実験で過去runの重みやTrack outputが上書きされないことを保証する。

## 背景

現行実装は、checkpointを`save_path/exp_name`へ保存し、Track outputを固定の`track_results/{dataset}/{tracker}/{split}`へ保存する。同じexperiment名・同じ系列で再実行すると既存ファイルを上書きする。またCometにはparameter、metric、config assetは保存されるが、checkpoint、git dirty diff、detector入力manifest、TrackEval summaryはrun成果物としてまとまって保存されない。

## 変更範囲

- 既存の保存rootは変更しない。
- `train.py` / `train_stateful.py`のcheckpoint保存にrun_idを追加する。
- `track.py` / `track_stateful.py`のTrack output保存にrun_idを追加する。
- `train_utils/mot_metrics.py`のepoch別TrackEval出力をrun_id・epoch別に分離し、既存結果を削除しない。
- `train_utils/comet_logger.py`からrun manifestと選択checkpointをComet assetとして保存する。
- checkpoint payloadへformat version、run_id、epoch、git commit、dirty状態、config snapshot、command等のmetadataを追加する。

## 保存構造

```text
ssm_tracker/saved_ckpts/<exp_name>/<run_id>/
  ├── <config>.yaml
  ├── manifest.json
  ├── epoch*.pth
  ├── best_val_loss.pth
  └── best_tracking_hota.pth

track_results/<dataset>/<tracker>/<split>/<run_id>/
  ├── <sequence>.txt
  └── manifest.json
```

学習中TrackEvalの中間成果物も`<trackeval_root>/<run_id>/epoch<epoch>/`以下に保存し、epoch間で削除しない。

## run_id

- CLIで明示指定できる。
- 未指定時は`YYYYMMDDTHHMMSS+0900_<short-git>`形式で生成する。
- run_idの保存先が既に存在する場合は、明示的なoverwrite指定なしに開始しない。
- checkpoint run_idとTrack output run_idはmanifestで照合可能にする。

## Comet保存

Comet runには既存のparameters・metrics・config assetに加えて、次を保存する。

- run manifest
- 最終checkpoint
- best checkpoint（存在するもの）
- git commit、branch、dirty状態、実行時のdiff情報
- command line、config snapshot、detector入力のパスとmanifest
- TrackEval設定とsummaryのパスまたはasset

全epoch checkpointと全動画outputの無条件uploadは行わず、ローカルrun directoryを正本とし、Cometには再現に必要な選択成果物を保存する。

## 互換性・非目標

- 既存checkpointの`model`キーを維持し、metadataがない旧checkpointも推論・resume時に読み込めるようにする。
- TrackEvalのmetrics計算方法、association、track lifecycle、モデル構造は変更しない。
- P1 association変更はこのspecの対象外とする。
- `references/`や既存の旧outputは変更・削除しない。

## 検証方法

1. 同じ`exp_name`で2回smoke trainingを実行し、異なるrun_idのcheckpointが共存することを確認する。
2. 同じdataset・tracker・splitで2回trackingを実行し、sequence outputが別run directoryに保存され、既存outputが変化しないことを確認する。
3. checkpointを`torch.load`し、model/optimizer/epochとmetadataを読み戻せることを確認する。
4. manifestにgit commit、command、config、run_idが記録されることを確認する。
5. Comet無効環境でもローカルmanifestとcheckpoint保存が成立することを確認する。
6. 学習中TrackEvalを2 epoch以上実行し、epochごとのoutputとsummaryが残ることを確認する。

## 成功基準

- 同一experiment名での再実行によって過去checkpoint・Track output・TrackEval summaryが上書きされない。
- checkpoint単体とmanifestから、少なくともrun_id、epoch、config、git commit、commandを特定できる。
- Comet assetから、選択checkpointとmanifestを取得できる。
- 既存checkpointを用いた推論導線のmetricsとTrackEval条件を変更しない。

## 関連ファイル

- `experiments/2026-07-21-p0-75-historical-baseline-audit.md`
- `specs/2026-07-21-state-carry-improvement-spec-candidate.md`
