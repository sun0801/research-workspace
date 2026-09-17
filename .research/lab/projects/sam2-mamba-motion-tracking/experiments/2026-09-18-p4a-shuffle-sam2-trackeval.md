---
project: sam2-mamba-motion-tracking
type: experiment-log
status: completed
date: 2026-09-18
---

# P4a shuffle checkpointのSAM2統合・TrackEval評価

## 目的

`shuffle=True`で学習したP4a `MambaStateful` checkpointをSAM2/SAMURAI統合側で推論し、既存の非shuffle P4aおよびL0の25系列結果と比較する。

## 条件

- SAM2 mode: `samurai_mamba_stateful`
- SAM2 config: `configs/samurai_mamba_stateful/sam2.1_hiera_t.yaml`
- SAM2 checkpoint: `checkpoints/sam2.1_hiera_tiny.pt`
- Mamba checkpoint（実行ログで確認した実体）:
  `/mnt/HDD10TB-2/aburatani/2025_09_aburatani_Mamba_Trackers/ssm_tracker/saved_ckpts/p4a_shuffle_full_100ep_20260911/20260911T061814+0900_3489e78/epoch100.pth`
- DanceTrack val: 25系列
- SAM2 run ID: `sam2_p4a_shuffle_epoch100_25seq_20260917`
- TrackEval: HOTA / CLEAR / Identity、`DO_PREPROC=False`、`SKIP_SPLIT_FOL=True`
- GT集計: `GT_Dets=225148`、`GT_IDs=273`

注意：SAM2 wrapperの`manifest.json`には旧`mamba_stateful_dancetrack/epoch100.pth`が記録されているため、checkpoint provenanceはmanifestではなく、実行時ログの`Loaded exact MambaStateful checkpoint`行を正本とする。

## SAM2出力

```text
/mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2/results/sam2_stateful_minimal/sam2_p4a_shuffle_epoch100_25seq_20260917/samurai_mamba_stateful_tiny/
```

25系列分のMOT出力（`.txt`）とcandidate debug CSVが生成され、全系列の推論が完了した。

## TrackEval結果

正本summary:

```text
/mnt/HDD10TB-2/aburatani/TrackEval/data/trackers/dancetrack/val/sam2_p4a_shuffle_epoch100_25seq_20260917/trackeval_20260918/pedestrian_summary.txt
```

| 指標 | shuffle P4a | 非shuffle P4a | shuffle - 非shuffle | L0 | shuffle - L0 |
|---|---:|---:|---:|---:|---:|
| HOTA | **53.944** | 54.391 | -0.447 | 55.520 | -1.576 |
| DetA | 48.198 | 48.511 | -0.313 | 49.601 | -1.403 |
| AssA | 60.701 | 61.320 | -0.619 | 62.482 | -1.781 |
| MOTA | 34.814 | 35.521 | -0.707 | 36.587 | -1.773 |
| IDF1 | 62.172 | 63.051 | -0.879 | 64.154 | -1.982 |
| IDSW | 1,551 | 1,520 | +31 | 1,535 | +16 |

## 解釈

今回のepoch100・単一checkpointの比較では、shuffle条件がSAM2統合後の性能を改善する結果にはならなかった。非shuffle P4aに対してHOTA、AssA、IDF1が低下し、IDSWも増加した。

ただし、これはshuffleの有効性を否定する結果ではない。seedが1つであり、epoch100固定の比較であるため、P4aのchunk長・TBPTT長・batchサイズ・Mamba内部次元の探索と合わせて判断する。今回の結果は、以後のハイパーパラメータ探索におけるSAM2統合baselineとして扱う。

また、TrackEval起動時にBURST用`pycocotools`不足のimport warningが出たが、DanceTrack 25系列の評価は正常終了し、summary・detailed CSV・plotが生成された。

## 生成物

- SAM2推論: 上記SAM2出力ディレクトリ
- TrackEval: `.../trackeval_20260918/pedestrian_summary.txt`
- TrackEval詳細: `.../trackeval_20260918/pedestrian_detailed.csv`
- TrackEval plot: `.../trackeval_20260918/pedestrian_plot.png` / `.pdf`

## 参照

- [P4a unroll/TBPTT hyperparameter search](2026-09-17-p4a-unroll-tbptt-hyperparameter-search.md)
- [L0/P4a epoch100 tracker単体・SAM2統合比較](2026-09-04-l0-p4a-tracker-sam2-comparison.md)
- [P4b checkpoint tracking evaluation spec](../specs/2026-09-02-p4b-checkpoint-tracking-evaluation-spec.md)
