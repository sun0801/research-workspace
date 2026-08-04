---
date: 2026-08-04
project: sam2-mamba-motion-tracking
status: completed
tags: [experiment, TrackEval, HOTA, sequence-level, MIRU]
---

# Sequence単位のHOTA比較

## 条件

- Dataset: DanceTrack validationの共通25系列
- Metric: TrackEvalの`HOTA(0)`
- 比較対象: SAM2、SAMURAI、SAM2 + Mamba stateful
- 既存のTrackEval詳細結果からsequence行を抽出
- statefulはepoch100の25系列runを使用

## 結果

| sequence | SAM2 | SAMURAI | stateful |
|---|---:|---:|---:|
| dancetrack0004 | 0.578 | 0.624 | **0.741** |
| dancetrack0005 | **0.614** | 0.585 | 0.552 |
| dancetrack0007 | 0.662 | 0.607 | **0.715** |
| dancetrack0010 | **0.979** | 0.974 | 0.974 |
| dancetrack0014 | 0.578 | **0.389** | 0.424 |
| dancetrack0018 | **0.874** | 0.798 | 0.796 |
| dancetrack0019 | 0.454 | 0.585 | **0.604** |
| dancetrack0025 | 0.641 | 0.859 | **0.942** |
| dancetrack0026 | 0.324 | **0.376** | 0.326 |
| dancetrack0030 | **0.964** | 0.869 | 0.957 |
| dancetrack0034 | 0.526 | 0.607 | **0.620** |
| dancetrack0035 | 0.776 | 0.804 | **0.832** |
| dancetrack0041 | 0.300 | 0.485 | **0.486** |
| dancetrack0043 | **0.717** | 0.698 | 0.700 |
| dancetrack0047 | 0.659 | 0.707 | **0.735** |
| dancetrack0058 | **0.951** | 0.874 | 0.948 |
| dancetrack0063 | **0.505** | 0.467 | 0.471 |
| dancetrack0065 | 0.858 | **0.906** | 0.906 |
| dancetrack0073 | **0.785** | 0.685 | 0.688 |
| dancetrack0077 | 0.883 | **0.946** | 0.946 |
| dancetrack0079 | 0.581 | 0.809 | **0.810** |
| dancetrack0081 | 0.581 | **0.595** | 0.585 |
| dancetrack0090 | 0.532 | **0.651** | 0.644 |
| dancetrack0094 | 0.484 | **0.561** | 0.538 |
| dancetrack0097 | 0.960 | **0.970** | 0.970 |
| **COMBINED** | **0.645** | **0.676** | **0.694** |

## 観察

- statefulの全系列平均は`0.694`で、SAM2の`0.645`、SAMURAIの`0.676`を上回る。
- statefulが両ベースラインを上回る主な系列は、`dancetrack0004`、`0007`、`0019`、`0025`、`0034`、`0035`、`0041`、`0047`、`0079`。
- `dancetrack0034`は、SAM2 `0.526`、SAMURAI `0.607`に対してstateful `0.620`で、前回の局所改善候補とも整合する。
- HOTAが最大級の系列は`dancetrack0010`（SAM2 `0.979`、SAMURAI/stateful `0.974`）だが、ベースラインも高く、stateful固有の改善例ではない。
- `dancetrack0041`はSAM2 `0.300`、SAMURAI `0.485`、stateful `0.486`で、難系列に対する改善はほぼなく、statefulの限界例に近い。

## 参照artifact

- SAM2: `/mnt/HDD10TB-2/aburatani/TrackEval/data/trackers/dancetrack/val/my_sam2_model/pedestrian_detailed.csv`
- SAMURAI: `/mnt/HDD10TB-2/aburatani/TrackEval/data/trackers/dancetrack/val/my_samurai_model/pedestrian_detailed.csv`
- stateful: `/mnt/HDD10TB-2/aburatani/2025_09_aburatani_Mamba_Trackers/artifacts/sam2_minimal_integration/trackeval/sam2_stateful_minimal_20260723T_sam2_minimal_25seq_epoch100_seqinfo/sam2_stateful_minimal_20260723T_sam2_minimal_25seq_epoch100/pedestrian_detailed.csv`
