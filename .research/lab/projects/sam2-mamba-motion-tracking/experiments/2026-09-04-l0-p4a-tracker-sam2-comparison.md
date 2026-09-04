---
date: 2026-09-04
project: sam2-mamba-motion-tracking
type: experiment-log
status: in_progress
tags: [experiment, l0, p4a, tracker-only, sam2, trackeval, epoch100]
---

# L0/P4a epoch100 tracker単体・SAM2統合比較

> 注意: `sam2_p4a_epoch100_25seq_20260904` はSAM2統合後の**25系列**TrackEval結果であり、P4a tracker単体の`p4a_full_100ep_20260903`とは別の評価である。前者のHOTA 54.391は25系列の確定値として扱う。

## 目的

L0とP4aのepoch100 checkpointについて、元のtracker単体とSAM2統合後のDanceTrack validation結果を整理し、P4aの単体性能改善がSAM2上でも維持されるかを確認する。

## 確定した評価結果

### L0 tracker単体の25系列再評価

L0の旧epoch100 checkpointを、旧条件に合わせて再評価した。TrackEvalの`COMBINED`行は25系列分で、`GT_Dets=225148`となっている。

正本:

```text
/mnt/HDD10TB-2/aburatani/TrackEval/data/trackers/dancetrack/val/l0_epoch100_repro_20260904/epoch100/mamba_statecarry/
```

| 指標 | L0 |
|---|---:|
| HOTA | 47.293 |
| DetA | 74.885 |
| AssA | 30.020 |
| MOTA | 84.493 |
| IDF1 | 45.852 |
| IDSW | 2,588 |

この再評価により、過去の実験ログに記録されていたL0 HOTA 47.293が、現在の環境でも再現されることを確認した。

### P4a tracker単体のepoch100結果（25系列・確定）

P4a tracker単体のepoch100出力を、L0と同じ25系列・同じTrackEval条件で再集計した。

| 指標 | P4a tracker単体 |
|---|---:|
| HOTA | 48.121 |
| DetA | 74.583 |
| AssA | 31.191 |
| MOTA | 84.575 |
| IDF1 | 47.764 |
| IDSW | 2,409 |

正本:

```text
/mnt/HDD10TB-2/aburatani/TrackEval/data/trackers/dancetrack/val/p4a_full_100ep_20260903/trackeval_epoch100_25seq/mamba_stateful_tbptt/pedestrian_summary.txt
```

`GT_Dets=225148`、`GT_IDs=273`であり、L0の25系列再評価と同じ評価対象である。L0（HOTA 47.293）に対して、P4a tracker単体はHOTA +0.828、AssA +1.171、IDF1 +1.912、IDSW -179となった。

### P4aを用いたSAM2統合後の25系列比較（確定）

SAM2上では、L0の既存epoch100結果と、P4a epoch100 checkpointを用いた25系列再評価を比較した。

| 指標 | L0 | P4a | P4a - L0 |
|---|---:|---:|---:|
| HOTA | 55.520 | 54.391 | -1.129 |
| DetA | 49.601 | 48.511 | -1.090 |
| AssA | 62.482 | 61.320 | -1.162 |
| MOTA | 36.587 | 35.521 | -1.066 |
| IDF1 | 64.154 | 63.051 | -1.103 |
| IDSW | 1,535 | 1,520 | -15 |

P4aの25系列SAM2 TrackEval結果の正本:

```text
/mnt/HDD10TB-2/aburatani/TrackEval/data/trackers/dancetrack/val/sam2_p4a_epoch100_25seq_20260904/pedestrian_summary.txt
```

この結果では`GT_Dets=225148`、`GT_IDs=273`であり、25系列集計であることを確認した。L0の25系列結果と同じ`GT_Dets=225148`を持つため、上表を直接比較に使用する。

## 解釈

現時点で確定できる結論は次のとおりである。

- L0 epoch100のtracker単体HOTA 47.293は再評価で確認できた。
- SAM2統合の25系列比較では、P4aはL0よりHOTA、DetA、AssA、MOTA、IDF1で低い。
- SAM2統合では、P4aのIDSWだけはL0より15少ない。
- P4a tracker単体では、25系列の再集計でL0よりHOTAが0.828高く、単体性能の改善を確認した。
- 現時点では、「P4aのstateful unroll + TBPTTによる学習上の差が、SAM2統合後のtracking性能改善へ直結しない」という解釈が最も安全である。

## 次の確認

- [ ] 必要に応じて、L0/P4aのtracker単体とSAM2統合の4条件を1枚の比較図にまとめる。

## 関連記録

- [P0.5 sliding-window baseline比較](2026-07-21-p0-5-sliding-window-baseline-comparison.md)
- [P4b checkpoint tracking評価](2026-09-02-p4b-checkpoint-tracking-evaluation.md)
- [P4a/P4b/SAM2 MTG資料](../materials/2026-09-04-p4a-p4b-sam2-evaluation-mtg-materials.md)
