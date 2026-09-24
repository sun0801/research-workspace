---
date: 2026-09-25
project: sam2-mamba-motion-tracking
type: experiment-log
status: completed
tags: [experiment, yolo, mamba, shuffle, tracking, trackeval, p4a]
---

# YOLO＋Mamba shuffle / non-shuffle再推論比較

## 目的

SAM2統合時に使用したshuffle/non-shuffleのP4a `MambaStateful` checkpointを、同一YOLO＋Mamba tracking条件で再推論し、shuffle学習の差がtracking-by-detectionへ伝播するかを確認する。

## 実験条件

### Mamba checkpoint

| 条件 | checkpoint | training run | SHA256 |
|---|---|---|---|
| non-shuffle | `/mnt/HDD10TB-2/aburatani/2025_09_aburatani_Mamba_Trackers/ssm_tracker/saved_ckpts/mamba_stateful_tbptt_p4a_full/p4a_full_100ep_20260903/epoch100.pth` | `p4a_full_100ep_20260903` | `30f6e700af27397658ee4c218f409484543dc3ff7c9bb49160a8a81f01010c09` |
| shuffle | `/mnt/HDD10TB-2/aburatani/2025_09_aburatani_Mamba_Trackers/ssm_tracker/saved_ckpts/p4a_shuffle_full_100ep_20260911/20260911T061814+0900_3489e78/epoch100.pth` | `20260911T061814+0900_3489e78` | `dab9619b38ea7b1b50e7511c33a84bccccd455d3075098920c207c3993ca3dd1` |

- Model: `MambaStateful`, P4a epoch100, seed 0
- Common inference config: `ssm_tracker/cfgs/MambaStatefulTBPTT.yaml`
- Common detector input: `/mnt/HDD10TB-2/aburatani/2025_09_aburatani_Mamba_Trackers/det_results/dancetrack/val`
- Dataset: DanceTrack val 25系列
- `association_mode=prediction`
- `missing_mode=self_update`
- `cache_update_mode=all`
- trusted update thresholds: IoU 0.5、score 0.6
- `reset_after_untrusted=0`
- TrackEval: HOTA / CLEAR / Identity、`DO_PREPROC=False`、25系列seqmap

推論側のMamba tracker commitは両条件とも`4988e5d26b18308cc67a6a51b76364ca134561db`で、生成manifest上はcleanだった。学習run自体は既存runの再利用であり、non-shuffleとshuffleのtraining commit/configは同一ではないため、新規の厳密なpaired training比較ではなく、既存checkpointの条件付き再評価として扱う。

## 実施結果

### Smoke

`dancetrack0004`を両checkpointで実行し、以下を確認した。

- checkpointのロード成功
- 1203フレームの最後まで完走
- 同一のYOLO検出入力・association・missing設定
- state nonfinite eventなし
- MOT出力生成成功

### Full val

- non-shuffle: 25/25系列完走、MOT出力25本
- shuffle: 25/25系列完走、MOT出力25本
- 両条件ともdiagnostics上の全state finite
- TrackEval: 25系列・GT_Dets 225,148

## TrackEval結果

### aggregate

| 指標 | non-shuffle | shuffle | shuffle - non-shuffle |
|---|---:|---:|---:|
| HOTA | 0.482148 | 0.484310 | **+0.002162** |
| DetA | 0.750912 | 0.750689 | -0.000223 |
| AssA | 0.311139 | 0.313970 | **+0.002831** |
| MOTA | 0.845719 | 0.846043 | +0.000324 |
| IDF1 | 0.461650 | 0.472625 | **+0.010975** |
| IDSW | 2,452 | 2,404 | **-48** |
| Dets | 204,554 | 204,863 | +309 |
| IDs | 995 | 881 | **-114** |

HOTA換算ではshuffleが+0.216ポイント、AssAが+0.283ポイント、IDF1が+1.098ポイント、IDSWが48減少した。DetAはほぼ不変でわずかに低下しているため、今回の改善は検出性能ではなくassociation側に現れている。

### sequence別分析

HOTAは25系列中14系列でshuffleが改善、11系列で低下した。sequence単位の単純平均差は+0.00631で、TrackEvalのaggregate差+0.00216より大きい。系列長・GT量による重み付けで、全体差が小さくなっている。

主な改善系列:

| sequence | HOTA差 | AssA差 | IDF1差 | IDSW差 |
|---|---:|---:|---:|---:|
| dancetrack0097 | +0.0930 | +0.1252 | +0.1023 | +1 |
| dancetrack0004 | +0.0451 | +0.0477 | +0.0522 | -6 |
| dancetrack0090 | +0.0429 | +0.0515 | +0.0504 | -9 |
| dancetrack0026 | +0.0313 | +0.0452 | +0.0676 | -2 |
| dancetrack0035 | +0.0259 | +0.0308 | +0.0222 | +6 |

主な低下系列:

| sequence | HOTA差 | AssA差 | IDF1差 | IDSW差 |
|---|---:|---:|---:|---:|
| dancetrack0065 | -0.0383 | -0.0390 | -0.0728 | -1 |
| dancetrack0058 | -0.0363 | -0.0458 | -0.0347 | +2 |
| dancetrack0047 | -0.0258 | -0.0330 | -0.0423 | +8 |
| dancetrack0079 | -0.0227 | -0.0378 | -0.0047 | 0 |
| dancetrack0077 | -0.0077 | -0.0113 | +0.0058 | 0 |

特に`dancetrack0097`ではAssA、IDF1が大きく改善した一方、`dancetrack0065`、`0058`、`0047`ではassociationが悪化した。shuffleの効果は一様な改善ではなく、sequence依存である。

## state / missing diagnostics

| 指標 | non-shuffle | shuffle |
|---|---:|---:|
| accepted detector updates | 201,078 | 196,823 |
| missing frames | 41,027 | 37,855 |
| missing self-updates | 41,027 | 37,855 |
| state nonfinite events | 0 | 0 |
| state finite checks | 484,210 | 469,356 |
| generated tracklets | 983 | 834 |
| max pending delta norm | 5.2011 | 4.2892 |
| max consecutive missing | 32 | 32 |

両条件ともstateは有限だった。shuffleではmissing/self-updateが3,172回少なく、max pending delta normも低かった。ただしこれはcheckpointの予測差がtrack lifecycle・matchingに影響した結果であり、YOLO detector自体の出力差ではない。`accepted_detector_updates`やtracklet数もtracking経路の結果として変化しているため、これらを単純な検出性能差とは解釈しない。

## SAM2統合結果との比較

既存のSAM2統合25系列では、shuffle P4aはnon-shuffle P4aに対してHOTA -0.447ポイント、AssA -0.619ポイント、IDF1 -0.879ポイント、IDSW +31だった。一方、今回のYOLO＋MambaではHOTA +0.216ポイント、AssA +0.283ポイント、IDF1 +1.098ポイント、IDSW -48だった。

したがって、shuffleの効果はtracking pipelineに依存する。今回の結果は、SAM2統合でshuffle差が見えなかった理由がMamba checkpoint差の不存在だけではなく、SAM2のメモリ・mask候補・統合側の挙動によって差が吸収または変換された可能性を支持する。ただし、両方とも単一seed・epoch100の既存checkpointであるため、shuffleの一般的な優位性までは主張できない。

## 結論

1. 既存shuffle/non-shuffle checkpointはYOLO＋Mambaへ問題なく移植でき、25系列推論・TrackEval評価が成立した。
2. 今回の固定条件では、shuffleがaggregate HOTAを0.216ポイント、IDF1を1.098ポイント改善し、IDSWを48減少させた。
3. 改善は主にAssA/IDF1側で、DetAはほぼ変わらないため、shuffle差はassociation・state更新経路に現れた可能性が高い。
4. sequence別には14改善・11低下であり、効果は一様ではない。
5. SAM2統合時の傾向とは異なるため、shuffle効果をSAM2結果だけから判断するのは不適切だった。
6. 単一seed・epoch100・GT学習からYOLO推論への分布差・既存training runのcommit差が残るため、最終的な一般化主張には追加seedまたは入力分布混合実験が必要である。

## 成果物

### 推論出力

- non-shuffle MOT: `/mnt/HDD10TB-2/aburatani/TrackEval/data/trackers/dancetrack/val/yolo_mamba_nonshuffle_full_20260925/data/`
- non-shuffle provenance: `/mnt/HDD10TB-2/aburatani/2025_09_aburatani_Mamba_Trackers/artifacts/yolo_mamba_shuffle_comparison/2026-09-25/yolo_mamba_nonshuffle/full/`
- shuffle MOT: `/mnt/HDD10TB-2/aburatani/TrackEval/data/trackers/dancetrack/val/yolo_mamba_shuffle_full_20260925/data/`
- shuffle provenance: `/mnt/HDD10TB-2/aburatani/2025_09_aburatani_Mamba_Trackers/artifacts/yolo_mamba_shuffle_comparison/2026-09-25/yolo_mamba_shuffle/full/`

25本のMOT txtはTrackEval側へ、manifest.json・diagnostics.json・git.diffはMamba repo側provenanceへ保存した。

### TrackEval

- non-shuffle summary: `/mnt/HDD10TB-2/aburatani/TrackEval/data/trackers/dancetrack/val/yolo_mamba_nonshuffle_full_20260925/trackeval_20260925/pedestrian_summary.txt`
- shuffle summary: `/mnt/HDD10TB-2/aburatani/TrackEval/data/trackers/dancetrack/val/yolo_mamba_shuffle_full_20260925/trackeval_20260925/pedestrian_summary.txt`
- sequence詳細CSV: `/mnt/HDD10TB-2/aburatani/TrackEval/data/trackers/dancetrack/val/yolo_mamba_nonshuffle_full_20260925/trackeval_20260925/pedestrian_detailed.csv` と `/mnt/HDD10TB-2/aburatani/TrackEval/data/trackers/dancetrack/val/yolo_mamba_shuffle_full_20260925/trackeval_20260925/pedestrian_detailed.csv`
- plot: 各runの`trackeval_20260925/pedestrian_plot.png` / `.pdf`

TrackEval起動時にBURST用`pycocotools`不足warningが出たが、DanceTrackの25系列評価、summary、detailed CSV、plotは正常生成された。

## 関連spec

- `.research/lab/projects/sam2-mamba-motion-tracking/specs/2026-09-24-yolo-mamba-shuffle-comparison-spec.md`
- `.research/secretary/notes/brainstorm/2026-09-24-yolo-mamba-shuffle-comparison-update.md`
