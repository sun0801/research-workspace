---
date: 2026-09-02
project: sam2-mamba-motion-tracking
status: completed
tags: [experiment, p4a, p4b, checkpoint, dancetrack, trackeval]
---

# P4a closeout and P4b checkpoint tracking evaluation

## 条件

- Dataset: DanceTrack val 25 sequences
- Checkpoint epoch: 5（L0/P4aで一致）
- P4a: `p4a_pilot_epoch5_20260902`, `--epochs 5`, seed 0
- L0 checkpoint: `ssm_tracker/saved_ckpts/mamba_stateful_dancetrack/epoch5.pth`
- Tracking固定条件: observation association、missing freeze、cache update all、IoU 0.5、score 0.6、reset無効
- detector入力、config、bbox/delta scale、lifecycle、TrackEval条件は同一

## P4a closeout

- `val_loss/epoch_mean`: 0.0489752309
- state finite rate: 1.0
- free rollout（各validation trackの先頭から、horizon 1/4/8/16/32）:
  - h1 IoU 0.784533、MAE 0.012587
  - h4 IoU 0.529549、MAE 0.036442
  - h8 IoU 0.436481、MAE 0.044314
  - h16 IoU 0.332386、MAE 0.054302
  - h32 IoU 0.248007、MAE 0.069681
  - 全horizonでnonfinite rate=0、divergence rate=0

## P4b TrackEval結果

| model | HOTA | DetA | AssA | MOTA | IDF1 | IDSW |
|---|---:|---:|---:|---:|---:|---:|
| L0 | 53.971 | 83.095 | 35.073 | 90.971 | 53.165 | 98 |
| P4a | 53.240 | 82.400 | 34.414 | 90.993 | 52.365 | 100 |
| P4a - L0 | -0.731 | -0.695 | -0.659 | +0.022 | -0.800 | +2 |

両方とも25 sequenceでstate finite、nonfinite event 0。今回のepoch5固定比較ではP4aのtracking改善は確認できず、HOTA/AssA/IDF1はL0を下回った。これはP4aの長期rolloutがh32までfiniteだったこととtracking性能が同義でないことを示す初期結果であり、epoch100設定の本学習結果とは分けて扱う。

## Artifact / provenance

- P4a metrics: `ssm_tracker/saved_ckpts/mamba_stateful_tbptt_p4a_pilot/p4a_pilot_epoch5_20260902/p4a_metrics_epoch5.json`
- P4a checkpoint manifest: `ssm_tracker/saved_ckpts/mamba_stateful_tbptt_p4a_pilot/p4a_pilot_epoch5_20260902/checkpoint_manifest.json`
- P4b summary: `track_results/p4b_epoch5_20260902/summary.json`
- P4b evaluation manifest: `track_results/p4b_epoch5_20260902/evaluation_manifest.json`
- TrackEval summaries: `track_results/p4b_epoch5_20260902/trackeval/{L0,P4a}/pedestrian_summary.txt`

Cometは今回の実行では`--disable_comet`で無効化した。コード上はL0と同じmetric名・step/epoch粒度でloggingする。P3、SAM2変更、association/cache探索、pushは行っていない。
