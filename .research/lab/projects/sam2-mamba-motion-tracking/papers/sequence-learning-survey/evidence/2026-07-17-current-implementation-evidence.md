---
date: 2026-07-17
project: sam2-mamba-motion-tracking
status: completed
tags: [paper-note, sequence-learning-survey, evidence, state-carry, batch-0]
---

# 現行MambaStateful: コード根拠一覧

repository: `/mnt/HDD10TB-2/aburatani/2025_09_aburatani_Mamba_Trackers`  
commit: `d52bb81553e0d124f428a8f5c5e915d4208def88`

## Dataset

- 判断: 1 sampleはtrajectoryから切り出す重複fixed windowである。
  - confidence: 確実
  - file: `ssm_tracker/dataset/stateful_dataset.py`
  - class_or_function: `StatefulTrajDataset.__init__`, `__getitem__`
  - lines: 17–25, 42–48, 75–85
  - evidence: `sample_count = traj_len - window_size + 1`、`traj_start`を1ずつ進め、`traj[traj_start:traj_start + window_size]`を返す。
  - 現行実装への示唆: sampleは動画全体・track全体の連続状態ではない。

- 判断: 入力はbbox、targetは次時刻bboxとの差分である。
  - confidence: 確実
  - file: `ssm_tracker/dataset/stateful_dataset.py`
  - class_or_function: `StatefulTrajDataset.__getitem__`
  - lines: 77–85
  - evidence: `condition = traj[:-1]`、`label = traj[1:] - traj[:-1]`。configでbbox scale=1、delta scale=50。

## 学習とloss

- 判断: 学習DataLoaderはshuffleされ、batch間でstateを持ち越さない。
  - confidence: 確実
  - file: `ssm_tracker/train_stateful.py`
  - class_or_function: `train`
  - lines: 86–101, 162–177
  - evidence: train loaderは`shuffle=True`。各stepで`model.forward(x, label)`を独立に呼び、state引数・cache引数・detach処理がない。
  - 現行実装への示唆: trainはstateful trackerと異なるstate reset単位である。

- 判断: `loss_start_index=4`で、最終時刻だけでなくindex 4–10にlossを与える。
  - confidence: 確実
  - file: `ssm_tracker/cfgs/MambaStateful.yaml`; `ssm_tracker/models/MambaStateful.py`
  - class_or_function: `StatefulBboxLoss.forward`
  - lines: config 5, 9–10, 26–28; model 83–100
  - evidence: `window_size=12`なのでcondition/label lengthは11。`pred[:, start_idx:, :]`に既定meanのSmoothL1を適用する。
  - 現行実装への示唆: 「最終時刻lossだけ」が性能低下の直接仮説ではない。

- 判断: 通常forward内では因果stateを全11 tokenへ展開し、BPTTはそのwindow全体に及ぶ。
  - confidence: 高い
  - file: `ssm_tracker/models/MambaStateful.py`; `ssm_tracker/train_stateful.py`
  - class_or_function: `MambaStateful.forward`; `train`
  - lines: model 61–70; train 166–177
  - evidence: token列を一括forwardし、loss.backwardを呼ぶ。window内detachはない。
  - 現行実装への示唆: TBPTTではなくfixed-window BPTTである。

## Validation

- 判断: validation lossはtrainと同じDataset/forward/loss sliceであり、tracker推論を含まない。
  - confidence: 確実
  - file: `ssm_tracker/train_utils/validation.py`; `ssm_tracker/train_stateful.py`
  - class_or_function: `build_dataloader`, `run_validation_loss`, `train`
  - lines: validation 31–53, 62–86; train 94–101, 217–224
  - evidence: val annotationを使う`StatefulTrajDataset`、`shuffle=False`、`model.forward(x, label)`を`no_grad`で評価する。

## Cached tracker inference

- 判断: state/cacheはtracklet単位で初期化・保持される。
  - confidence: 確実
  - file: `ssm_tracker/track_utils/stateful_tracklet.py`
  - class_or_function: `StateCarryTracklet.__init__`, `_new_inference_params`, `_rebuild_state_from_history`, `_advance_state`
  - lines: 43–65, 106–176
  - evidence: 各trackletが`memo_bank`, `InferenceParams`, `pending_delta`を持つ。inference cacheをallocateし、逐次token後に`seqlen_offset`を進める。

- 判断: 現行コードだけからcacheのautograd対応は確認できない。
  - confidence: 確実（未確認という判断）
  - file: `ssm_tracker/track_utils/stateful_tracklet.py`
  - class_or_function: `_rebuild_state_from_history`, `_advance_state`
  - lines: 122–146, 171–176
  - evidence: cache利用箇所はすべて`torch.no_grad()`内である。
  - 現行実装への示唆: cacheをTBPTTに直接使用する実装は、外部調査・別検証なしに仮定しない。

- 判断: 5観測以降のmatching位置はMamba予測bboxである。
  - confidence: 確実
  - file: `ssm_tracker/track_utils/stateful_tracklet.py`; `ssm_tracker/track_utils/matching.py`
  - class_or_function: `StateCarryTracklet.tlwh`, `predict`; `iou_distance`
  - lines: tracklet 67–74, 178–190; matching 84–102
  - evidence: `tlwh`は`predicted_last_bbox`を優先し、`iou_distance`はtrackの`tlbr`を使う。

## Observation update / lost

- 判断: matching成功時はaccepted detection、失敗時は既定でself predictionがstate入力となる。
  - confidence: 確実
  - file: `ssm_tracker/track_utils/stateful_tracker.py`; `ssm_tracker/track_utils/stateful_tracklet.py`
  - class_or_function: `MambaStatefulTracker.update`; `StateCarryTracklet.update`
  - lines: tracker 58–99; tracklet 211–230
  - evidence: match後は`track.update(det, ...)`、unmatchedは`track.update(None, ...)`。`self_update`は`predicted_last_bbox`をappend/advanceする。

- 判断: matched observationのconfidenceを用いたstate skip/resetはない。
  - confidence: 確実
  - file: `ssm_tracker/track_utils/stateful_tracker.py`; `ssm_tracker/track_utils/stateful_tracklet.py`
  - class_or_function: `MambaStatefulTracker.update`; `StateCarryTracklet.update`
  - lines: tracker 18–20, 37–54, 62–99; tracklet 211–230
  - evidence: scoreは`filter_thresh`と`new_track_thresh`で用いられるのみ。matched detectionへのstate更新は無条件。

## Output / metrics

- 判断: 通常のMOT出力はlast memo bboxであり、debug時のみprediction bboxを出力する。
  - confidence: 確実
  - file: `ssm_tracker/track_stateful.py`
  - class_or_function: `main`
  - lines: 168–195
  - evidence: debugフラグ時は`predicted_last_bbox`、通常時は`get_bbox()`を用いる。

- 判断: mot_metricsはtracker subprocess、TrackEval API、summary parseを分離している。
  - confidence: 確実
  - file: `ssm_tracker/train_utils/mot_metrics.py`
  - class_or_function: `run_mot_metrics`
  - lines: 101–199
  - evidence: tracker出力を生成後、`run_mot_evaluation`を呼び、summaryからHOTA/DetA/AssA/MOTA/IDF1を読む。
