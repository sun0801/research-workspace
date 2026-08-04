---
date: 2026-08-04
project: sam2-mamba-motion-tracking
status: completed
tags: [experiment, TrackEval, HOTA, sequence-level, MIRU]
---

# Sequence単位の標準HOTA比較

TrackEval詳細結果の`HOTA___AUC`（`alpha=0.05`〜`0.95`の19点平均）を比較した。

| sequence | SAM2 | SAMURAI | stateful |
|---|---:|---:|---:|
| dancetrack0004 | 0.449 | 0.511 | **0.557** |
| dancetrack0005 | **0.514** | 0.494 | 0.471 |
| dancetrack0007 | 0.572 | 0.518 | **0.623** |
| dancetrack0010 | **0.875** | 0.867 | 0.863 |
| dancetrack0014 | 0.428 | 0.289 | 0.308 |
| dancetrack0018 | **0.771** | 0.721 | 0.721 |
| dancetrack0019 | 0.375 | 0.494 | **0.503** |
| dancetrack0025 | 0.505 | 0.694 | **0.772** |
| dancetrack0026 | 0.228 | **0.276** | 0.229 |
| dancetrack0030 | **0.766** | 0.693 | 0.761 |
| dancetrack0034 | 0.378 | 0.462 | **0.480** |
| dancetrack0035 | 0.577 | 0.618 | **0.627** |
| dancetrack0041 | 0.184 | 0.361 | **0.361** |
| dancetrack0043 | **0.487** | 0.477 | 0.479 |
| dancetrack0047 | 0.493 | 0.531 | **0.535** |
| dancetrack0058 | **0.870** | 0.793 | 0.865 |
| dancetrack0063 | **0.368** | 0.330 | 0.318 |
| dancetrack0065 | 0.747 | **0.793** | 0.792 |
| dancetrack0073 | **0.575** | 0.501 | 0.501 |
| dancetrack0077 | 0.724 | 0.774 | **0.778** |
| dancetrack0079 | 0.459 | 0.627 | **0.635** |
| dancetrack0081 | 0.405 | 0.427 | **0.429** |
| dancetrack0090 | 0.389 | **0.478** | 0.468 |
| dancetrack0094 | 0.373 | **0.448** | 0.434 |
| dancetrack0097 | 0.862 | **0.872** | 0.871 |
| **COMBINED** | **0.513** | **0.541** | **0.555** |

`COMBINED`はsequenceごとの単純平均ではなく、TrackEvalが全25系列を統合して算出した値。

参照artifact:

- SAM2: `/mnt/HDD10TB-2/aburatani/TrackEval/data/trackers/dancetrack/val/my_sam2_model/pedestrian_detailed.csv`
- SAMURAI: `/mnt/HDD10TB-2/aburatani/TrackEval/data/trackers/dancetrack/val/my_samurai_model/pedestrian_detailed.csv`
- stateful: `/mnt/HDD10TB-2/aburatani/2025_09_aburatani_Mamba_Trackers/artifacts/sam2_minimal_integration/trackeval/sam2_stateful_minimal_20260723T_sam2_minimal_25seq_epoch100_seqinfo/sam2_stateful_minimal_20260723T_sam2_minimal_25seq_epoch100/pedestrian_detailed.csv`
