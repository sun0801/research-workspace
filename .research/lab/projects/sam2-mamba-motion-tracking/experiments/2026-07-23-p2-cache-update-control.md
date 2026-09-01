---
date: 2026-07-23
project: sam2-mamba-motion-tracking
type: experiment-log
status: completed
tags: [experiment, p2, state-carry, cache-update, freeze, reset, dancetrack]
---

# P2 cache update control

## 結論

P1 A2（last accepted observation association）を固定し、missing時のstate/cache更新とdetector matchの品質ゲートを診断した。

- P2aのfreeze（B1）はself-update control（B0）に対し、25系列でHOTA `+0.125`、AssA `+0.234`、IDF1 `+0.346`となった。一方、IDSWは`+6`で、改善は小さく、全面的な成功とはいえない。
- B0では25系列中11系列に合計4,515回の非有限状態イベントが発生した。B1ではdancetrack0073の115回に縮小した。missing予測をstate/cacheへ入れないことは、state drift抑制の診断結果として支持される。
- B2のtrusted match gate（IoU `>=0.5`かつscore `>=0.6`）は、DetAは上がったが、AssA `-1.567`、IDF1 `-3.482`、IDSW `+1,444`となり、25系列aggregateでは悪化した。低品質matchをstate/cacheから除外すると、last accepted observationが古いまま残り、association continuityを損なう副作用が大きい。
- B3の5回連続untrusted detector match後resetは、B2からHOTA `-0.107`、AssA `-0.130`、IDF1 `-0.002`、IDSW `-3`で、25系列では改善を回復しなかった。resetは2,874回発生したが、B2のgateによるassociation悪化を解消できなかった。
- したがって、P2aは「missing self-updateがstate contaminationの一因」という診断を支持するが、aggregate tracking改善は限定的である。B2/B3の現在の単純なquality gate/resetは採用せず、P3へ自動移行しない。

## 固定条件

- checkpoint: `ssm_tracker/saved_ckpts/mamba_stateful_dancetrack/epoch100.pth`
- config: `ssm_tracker/cfgs/MambaStateful.yaml`
- detector: `det_results/dancetrack/val/`
- association: `observation`（P1 A2、last accepted observation）
- scale: bbox `1`、delta `50`
- lifecycle: P1と同一
- TrackEval: HOTA/CLEAR/Identity、`DO_PREPROC=False`
- sequence: DanceTrack val 25系列（`--SEQ_INFO`で明示）
- primary評価は同一最終実装版の25系列runを使用

## 条件とrun

| 条件 | missing | cache update | reset | 25系列run |
|---|---|---|---:|---|
| B0 | self_update | all | 0 | `p2_cache_20260723_epoch100_25seq_v4_b0` |
| B1 | freeze | all | 0 | `p2_cache_20260723_epoch100_25seq_v4_b1` |
| B2 | freeze | trusted (IoU≥0.5, score≥0.6) | 0 | `p2_cache_20260723_epoch100_25seq_v3_b2` |
| B3 | freeze | trusted (IoU≥0.5, score≥0.6) | 5 consecutive untrusted detector matches | `p2_cache_20260723_epoch100_25seq_v3_b3` |

3系列の初期smokeはB0/B1の`v1`、修正後B2/B3の`v4`で実施した。旧B2/B3の`v1`/`v2`は、untrusted match時の出力bboxとmissing freezeのresetカウントに実装上の混入があったため、成果物を削除せず保持するが、主結果には使わない。

## 25系列 TrackEval結果

| 条件 | HOTA | DetA | AssA | IDF1 | MOTA | IDSW | IDs |
|---|---:|---:|---:|---:|---:|---:|---:|
| B0 | 47.910 | 74.777 | 30.843 | 47.315 | 84.607 | 2,386 | 735 |
| B1 | 48.035 | 74.585 | 31.077 | 47.661 | 84.605 | 2,392 | 748 |
| B2 | 46.962 | 75.081 | 29.510 | 44.179 | 83.793 | 3,836 | 1,101 |
| B3 | 46.855 | 75.070 | 29.380 | 44.177 | 83.795 | 3,833 | 1,104 |

TrackEval正本:

- B0: `artifacts/p2_cache_update_control/trackeval_eval/p2_cache_20260723_epoch100_25seq_v4_b0/mamba_statecarry/`
- B1: `artifacts/p2_cache_update_control/trackeval_eval/p2_cache_20260723_epoch100_25seq_v4_b1/mamba_statecarry/`
- B2: `artifacts/p2_cache_update_control/trackeval_eval/p2_cache_20260723_epoch100_25seq_v3_b2/mamba_statecarry/`
- B3: `artifacts/p2_cache_update_control/trackeval_eval/p2_cache_20260723_epoch100_25seq_v3_b3/mamba_statecarry/`

全てのsummaryは`COMBINED`に25系列を含むことを確認した。共有seqmapは変更していない。

## State/cache diagnostics

| 条件 | detector update | missing | self-update | freeze | untrusted match | reset | nonfinite events | max consecutive untrusted |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| B0 | 198,403 | 37,833 | 37,833 | 0 | 0 | 0 | 4,515 | 0 |
| B1 | 194,997 | 36,157 | 0 | 36,157 | 0 | 0 | 115 | 0 |
| B2 | 172,442 | 50,742 | 0 | 50,742 | 19,898 | 0 | 0 | 574 |
| B3 | 172,837 | 50,634 | 0 | 50,634 | 19,877 | 2,874 | 0 | 5 |

`state_nonfinite_events=0`はB2/B3で全25系列、B1ではdancetrack0073のみ115回、B0では11系列で発生した。B3のresetはmissing freezeではなく、trustedでないdetector matchの連続5回だけを発火条件とした。

## 実装内容

- `stateful_tracklet.py`
  - missing `self_update`/`freeze`の分離
  - `all`/`trusted` cache update mode
  - accepted detector update、missing、untrusted match、reset、finite checkの診断
  - freeze時は予測bboxを出力し、state/history/cacheを保持
  - untrusted detector match時はdetector bboxをtracking outputに使い、state/history/cacheだけを保持
- `stateful_tracker.py`
  - association IoUとdetector scoreによるtrusted判定
  - first/second association stage双方へのstate update制御
  - per-sequence diagnostics集約
- `track_stateful.py`
  - P2 CLI、manifest、diagnostics JSON
- `experiments/inference_p2_cache_update_control.sh`
  - B0〜B3のrun_id付き実験スクリプト
- `experiments/p2_cache_update_control_smoke.py`
  - freeze/self-update/untrusted output/stateのtargeted invariant test

## 検証

- targeted smoke: PASS
- Python `py_compile`: PASS
- `git diff --check`: PASS
- 3系列: B0〜B3を実行し、各TrackEval summaryを生成
- 25系列: B0〜B3を実行し、各TrackEval summary/detailed CSVを生成
- 全25系列runでtracking output、`manifest.json`、`git.diff`、`diagnostics.json`を確認
- 既存checkpoint、既存track output、既存TrackEval outputの削除・上書きなし

## 因果解釈と次の判断

P2aのB1はB0よりstate非有限イベントを大幅に減らし、HOTA/AssA/IDF1を小さく改善した。これはmissing時の予測を毎回history/cacheへ入力することがstate instabilityの一因であるという仮説と整合する。ただしIDSWは増加し、改善は限定的である。

B2/B3は、detector matchをstate/cacheへ入れないだけではassociation観測が古くなり、tracking continuityを損なうことを示した。P2の単純gate/resetをそのまま採用せず、次はP2結果を踏まえたquality-aware observation保持または別のstate update設計をspec化してから判断する。P3/P4はこのログの結果だけを根拠に自動開始しない。

## 関連成果物

- Spec: `specs/2026-07-23-p2-cache-update-control-spec.md`
- P1 reference: `experiments/2026-07-23-p1-association-separation-25seq.md`
- External repo: `/mnt/HDD10TB-2/aburatani/2025_09_aburatani_Mamba_Trackers`
