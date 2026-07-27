---
date: 2026-07-27
project: sam2-mamba-motion-tracking
status: completed
tags: [experiment, sam2, samurai, mamba-stateful, checkpoint-selection, trackeval, 25-seq]
---

# SAM2最小stateful Mamba統合: best-HOTA checkpoint 25系列評価

## 目的

2026-07-23のepoch100 checkpoint評価と同一条件で、元Mamba repoが保存した`best_tracking_hota.pth`をSAM2/SAMURAIへ読み込み、checkpoint選択の影響を確認する。

## 条件

- run_id: `20260727T_sam2_minimal_25seq_best_hota_epoch20`
- mode: `samurai_mamba_stateful`
- SAM2 model: `tiny`
- input: `data/DanceTrack/val/val`
- sequence split: `data/DanceTrack/testing_set.txt`（25系列）
- Mamba checkpoint: `best_tracking_hota.pth`（metadata上はepoch20）
- architecture / scale / lifecycle / state carry: 2026-07-23 epoch100 runと同一
- P1/P2: `false`
- fallback: 不許可
- TrackEval: HOTA/CLEAR/Identity、`DO_PREPROC=False`、25系列を`SEQ_INFO`で明示

## TrackEval結果

| 指標 | best-HOTA checkpoint | epoch100 | best-HOTA - epoch100 |
|---|---:|---:|---:|
| HOTA | **54.606** | 55.520 | -0.914 |
| DetA | 48.609 | 49.601 | -0.992 |
| AssA | 61.691 | 62.482 | -0.791 |
| MOTA | 34.595 | 36.587 | -1.992 |
| IDF1 | 62.813 | 64.154 | -1.341 |
| IDSW | 1,525 | 1,535 | -10 |
| tracker detections | 240,892 | 241,284 | -392 |

best-HOTA checkpointはIDSWだけ10減少したが、HOTA、DetA、AssA、MOTA、IDF1はepoch100を下回った。したがって、このSAM2統合・DanceTrack val 25系列条件では、元repoのvalidation HOTAで選択されたepoch20 checkpointがSAM2上の最良checkpointになるとは限らない。

## state carry診断

- `motion_model_loaded=True`: 245,291 / 245,291行
- `fallback_mode`: 全行空欄
- `used_window_recompute=False`: 245,291 / 245,291行
- `used_true_state_carry=True`: 233,875 / 245,291行（95.34%）
- `last_update_reliable=False`: 4,422 / 245,291行（1.80%）
- `miss_count`: 0〜1
- `stateful_step`: 0〜1,651

checkpoint未ロードやconstant-velocity fallbackへの退化は確認されなかった。epoch100 runと比較して、stateful推論導線の成立性は同じである。

## 成果物

- manifest: [`manifest.json`](/mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2/results/sam2_stateful_minimal/20260727T_sam2_minimal_25seq_best_hota_epoch20/manifest.json)
- Track output: `/mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2/results/sam2_stateful_minimal/20260727T_sam2_minimal_25seq_best_hota_epoch20/samurai_mamba_stateful_tiny/`
- TrackEval summary: [`pedestrian_summary.txt`](/mnt/HDD10TB-2/aburatani/2025_09_aburatani_Mamba_Trackers/artifacts/sam2_minimal_integration/trackeval/sam2_stateful_minimal_20260727T_sam2_minimal_25seq_best_hota_epoch20_seqinfo/sam2_stateful_minimal_20260727T_sam2_minimal_25seq_best_hota_epoch20/pedestrian_summary.txt)
- TrackEval detailed CSV: [`pedestrian_detailed.csv`](/mnt/HDD10TB-2/aburatani/2025_09_aburatani_Mamba_Trackers/artifacts/sam2_minimal_integration/trackeval/sam2_stateful_minimal_20260727T_sam2_minimal_25seq_best_hota_epoch20_seqinfo/sam2_stateful_minimal_20260727T_sam2_minimal_25seq_best_hota_epoch20/pedestrian_detailed.csv)

## 結論

「元repoのHOTAが最大のcheckpointをSAM2へ持ち込めば、SAM2のHOTAも最大になる」という仮説は今回の比較では支持されなかった。SAM2上のcheckpoint選択を最適化する場合は、SAM2の固定validation split上でcheckpointごとの評価を行う必要がある。ただし、epoch100とbest-HOTAの2点だけでは最適epochの推定には不十分であり、追加評価は必要に応じて計画する。

