---
date: 2026-07-23
project: sam2-mamba-motion-tracking
status: completed
tags: [experiment, p1, association, state-carry, trackeval, 25-seq]
---

# P1 association separation: 25-sequence validation

## 目的

3系列で確認したP1 association separationの改善が、DanceTrack val 25系列でも維持されるかを検証する。P0.75の再調査ではなく、同一provenance条件でA1/A2のassociation差分を評価する。

## 条件

- checkpoint: `ssm_tracker/saved_ckpts/mamba_stateful_dancetrack/epoch100.pth`
- config: `ssm_tracker/cfgs/MambaStateful.yaml`
- detector: `det_results/dancetrack/val/`
- scale: bbox `1`、delta `50`
- lifecycle/state carry/cache: 3系列P1と同一
- TrackEval: HOTA/CLEAR/Identity、`DO_PREPROC=False`
- sequences: DanceTrack val 25系列
- run provenance: 各runの`manifest.json`と`git.diff`

## Run

| 条件 | run_id |
| --- | --- |
| A1 prediction-primary | `p1_assoc_20260722_epoch100_25seq_new_prediction` |
| A2 observation-primary | `p1_assoc_20260722_epoch100_25seq_new_observation` |

tracking outputは`track_results/dancetrack/MambaStateful/val/<run_id>/`に保存した。

## TrackEval結果

| 条件 | HOTA | DetA | AssA | IDF1 | MOTA | IDSW | IDs |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A1 prediction | 47.233 | 74.975 | 29.907 | 45.886 | 84.477 | 2578 | 880 |
| A2 observation | **47.910** | 74.777 | **30.843** | **47.315** | **84.607** | **2386** | **735** |
| A2 - A1 | +0.677 | -0.198 | +0.936 | +1.429 | +0.130 | -192 | -145 |

TrackEval成果物:

- `artifacts/p1_association_separation/trackeval_25seq_corrected/p1_assoc_20260722_epoch100_25seq_new_prediction/mamba_statecarry/`
- `artifacts/p1_association_separation/trackeval_25seq_corrected/p1_assoc_20260722_epoch100_25seq_new_observation/mamba_statecarry/`

## 系列別確認

- HOTA改善: 17/25系列
- AssA改善: 19/25系列
- IDF1改善: 17/25系列
- 効果は一様ではなく、`dancetrack0097`ではA2がHOTA -0.103、AssA -0.126となった。

## 解釈

25系列でもA2はA1に対してAssA、IDF1、IDSWを改善し、HOTAも改善した。predictionをhard IoU matchingのprimary位置に使うことがassociation退化へ寄与するというP1仮説は、3系列だけでなく25系列のaggregateでも支持される。

ただし、3系列で観測したHOTA +5.204より効果は小さく、系列依存の失敗例もある。P1は「observation associationをreferenceとしてP2を検討する根拠」を与えるが、最終手法の性能保証ではない。

## P2への判断

P2 cache update controlの計画化へ進む。A2 observation associationを固定referenceとし、trusted match時のみcache/stateを更新する条件と、missing時freeze・reset条件を別々にspec化する。P3/P4はP2の因果評価後まで実装しない。

## 注意点

初回のTrackEval実行では、既存の`dancetrack-val.txt`が0004/0005/0007だけを含んでいたため、25系列tracking outputを用いながら3系列のみが評価された。既存結果は保持し、`SEQ_INFO`で25系列を明示した修正版を正式結果とした。
