---
date: 2026-07-22
project: sam2-mamba-motion-tracking
status: completed
tags: [experiment, p1, association, state-carry, trackeval, run-id]
---

# P1 association separation diagnostic

## 目的

同一のMambaStateful predictor・detector入力・track lifecycle・state carry更新のまま、IoU matchingの主位置だけをMamba predictionからlast trusted accepted observationへ変更し、prediction-primary associationの因果効果を診断する。

## 実装

対象repoの実験開始時点はHEAD `04f246b`（P0.8 artifact retentionを含む）で、origin/masterは`81a7a78`だった。P0.8変更をreset、checkout、stashせず、P1変更は未commitのまま保持している。

変更ファイル:

- `ssm_tracker/track_utils/stateful_tracklet.py`
  - accepted detector bboxだけを更新する`last_observed_xywh`を追加。
  - association専用の`association_tlwh`/`association_tlbr`を追加。
  - missing時のself-updateはlast observedを変更しない。
- `ssm_tracker/track_utils/stateful_tracker.py`
  - 1段目・2段目matchingのtrack側位置を`association_mode`で選択。
  - `prediction`は既存挙動、`observation`はlast accepted observationを使用。
  - assignment閾値、track lifecycle、state/cache更新は変更していない。
- `ssm_tracker/track_stateful.py`
  - `--association_mode`、`--sequences`を追加し、manifestへ記録。
- `experiments/inference_p1_association_separation.sh`
  - 同一条件をA1/A2のrun_idで実行するスクリプト。

P2 cache update guard、P3 input distribution mixing、P4 teacher forcing/TBPTTは未実装。

## 固定条件

- checkpoint: `ssm_tracker/saved_ckpts/mamba_stateful_dancetrack/epoch100.pth`
- config: `ssm_tracker/cfgs/MambaStateful.yaml`
- detector: `det_results/dancetrack/val/`
- sequence: `dancetrack0004`, `dancetrack0005`, `dancetrack0007`
- scale: bbox `1`、delta `50`
- lifecycle: `filter_thresh=0.2`、`new_track_thresh=0.6`、`max_time_lost=30`
- state/caching: `missing_mode=self_update`、`delta_clip=0.1`、track単位InferenceParams
- TrackEval: HOTA/CLEAR/Identity、`DO_PREPROC=False`、DanceTrack val seqmap、3系列
- device: CUDA visible GPU 2（tracker CLIのdevice引数は0、visible device経由）

## Run provenance

| 条件 | run_id | track output |
| --- | --- | --- |
| A1 prediction-primary | `p1_assoc_20260722_epoch100_3seq_prediction` | `track_results/dancetrack/MambaStateful/val/p1_assoc_20260722_epoch100_3seq_prediction/` |
| A2 observation-primary | `p1_assoc_20260722_epoch100_3seq_observation` | `track_results/dancetrack/MambaStateful/val/p1_assoc_20260722_epoch100_3seq_observation/` |

各runに3 sequence txt、`manifest.json`、`git.diff`を保存した。manifestからrun_id、command、checkpoint、config、scale、sequence、association mode、commit、dirty diffを照合できる。TrackEval成果物は各runの`artifacts/p1_association_separation/trackeval/<run_id>/mamba_statecarry/`に保存した。

## TrackEval結果

| 条件 | HOTA | DetA | AssA | IDF1 | MOTA | ID switches | IDs |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A1 prediction | 49.666 | 82.342 | 29.981 | 45.012 | 90.913 | 106 | 44 |
| A2 observation | **54.870** | **83.137** | **36.229** | **53.660** | **91.046** | **94** | **38** |
| A2 - A1 | +5.204 | +0.795 | +6.248 | +8.648 | +0.133 | -12 | -6 |

A1はP0.75で定義した3系列corrected baseline HOTA `49.666`と一致した。これはP1実装によるA1の既存挙動維持の確認になる。過去outputのHOTA `52.037`はprovenance不足のhistorical referenceであり、今回の成功基準には使わない。

## 検証結果

- targeted invariant: last observed observationはmissing/self-updateで不変、observation matchingの同一box距離は0。PASS
- `track_stateful.py --help`: 新規CLI表示。PASS
- `py_compile`: 対象3 Pythonファイル。PASS
- `sh -n experiments/inference_p1_association_separation.sh`: PASS
- `git diff --check`: PASS
- A1/A2 tracking: 各3系列、run_id付き新規directory、exit code 0。PASS
- TrackEval: 固定seqmapの3系列で両条件完走。PASS
- track output内の数値NaN/Inf: 検出なし
- 既存checkpoint・既存track output・既存TrackEval summary: 削除・上書きなし

TrackEval起動時のBURST `tabulate` missing warningは既存環境由来で、MOT評価自体は完走した。

## 因果解釈

A2はA1と比較してAssA、IDF1、ID switchesを改善し、HOTAも改善した。checkpoint、detector、scale、lifecycle、state/cache更新、TrackEvalを固定してassociation主位置だけを変えたため、少なくともこの3系列・このepoch100 checkpointでは、Mamba predictionをhard IoU matchingのprimary位置にすることがtracking退化へ寄与しているという診断を支持する。

ただしA2のmissing時は現行`self_update`を維持している。したがって今回の結果だけでは、残る退化がcache contaminationによるものか、prediction associationだけで説明できるかは確定しない。A2は最終手法ではなく、P2のcache update controlを検討するための診断baselineである。

## P2へ進む条件と未解決点

P1結果としてA2改善が確認されたため、次にP2を計画化する根拠は得られた。ただしP2の実装・実験は自動開始しない。P2へ進む前に、ユーザー承認済みの別specで以下を固定する。

- A2のobservation associationをreferenceとして維持する。
- trusted matchのみcache/historyをupdateするfreeze条件を定義する。
- missing/self prediction時のfreezeと、連続untrusted frame後resetを別条件として比較する。
- 25系列または別splitでの確認を行うか判断する。
- state norm、update/freeze/reset回数、long-miss後の再associationを記録する。

未解決点:

- 今回は3系列のみで、25系列full validationのP1結果は未取得。
- A2の改善が長期miss・多track条件でも維持されるか未確認。
- A2の出力はdetector observation主体だが、missing区間ではself-updateを含むため、P2の寄与とは分離できていない。
- P1変更は未commitであり、次のP2計画前にこのdiffとrun成果物を固定する必要がある。

## 関連ファイル

- `specs/2026-07-22-p1-association-separation-spec.md`
- `specs/2026-07-21-state-carry-improvement-spec-candidate.md`
- `specs/2026-07-22-experiment-artifact-retention-spec.md`
- `experiments/2026-07-21-p0-75-historical-baseline-audit.md`
- `meetings/2026-07-16-mtg.md`
