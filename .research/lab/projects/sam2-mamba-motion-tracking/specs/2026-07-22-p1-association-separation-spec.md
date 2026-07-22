---
date: 2026-07-22
project: sam2-mamba-motion-tracking
source: user-request-and-2026-07-21-state-carry-improvement-spec-candidate
status: approved
tags: [spec, p1, association, state-carry, diagnosis, tracking]
---

# P1 association separation Spec

## 目的

MambaStatefulのprediction-primary associationがID associationを壊しているかを、predictionとassociation選択を分離して診断する。P1は最終提案手法ではなく、P2以降のcache更新制御を判断するための因果診断である。

## 検証したい問い

同じstate carry predictor・detector入力・track lifecycleのまま、IoU matchingの主位置をMamba predictionからlast trusted accepted observationへ変更すると、AssA / IDF1 / ID switchesが改善するか。

## 仮説

現行A1ではMamba predictionをtracked/lost trackのprimary matching位置に使うため、prediction誤差が検出との対応付けを壊し、AssAを低下させる。A2でaccepted detectionの最後の観測位置をmatching専用に使えば、associationが改善し、predictionをprimary matchingに使う場合を不必要に下回らない。

## 固定条件

- 元repo: `/mnt/HDD10TB-2/aburatani/2025_09_aburatani_Mamba_Trackers`
- 実装開始時の基準: 現行HEAD `04f246b`（P0.8 artifact retentionを含む）。origin/master `81a7a78`との差をreset/checkout/stashしない。
- checkpoint: 既存 `/ssm_tracker/saved_ckpts/mamba_stateful_dancetrack/epoch100.pth`。読み取り専用で使用し、コピー・削除・上書きしない。
- config: `ssm_tracker/cfgs/MambaStateful.yaml`
- detector入力: `det_results/dancetrack/val/`内の既存ファイル。小規模実験では0004/0005/0007だけを新規run directoryへ参照する。
- scale: `scale_factor_bbox=1`, `scale_factor_delta=50`
- track lifecycle: `max_time_lost=30`、既存のactivate/re_activate/lost/removed処理
- state carry: `InferenceParams`のtrack単位state、cache更新、`missing_mode=self_update`、`delta_clip=0.1`
- TrackEval: DanceTrack val seqmap（0004/0005/0007）、HOTA/CLEAR/Identity、`DO_PREPROC=False`、既存のTrackEval adapter/設定
- A1/A2でcheckpoint、入力、config、split、device、run provenanceを固定し、run_idだけを新規にする

## 変更範囲

- `ssm_tracker/track_utils/stateful_tracklet.py`: accepted detectionに対応するlast observed bboxを保持し、association用の観測位置を提供する。
- `ssm_tracker/track_utils/stateful_tracker.py`: primary/second-stage matchingのtrack側位置を、A1ではprediction、A2ではlast observed observationに切り替える。detector側とassignment閾値は変更しない。
- `ssm_tracker/track_stateful.py`: association modeと小規模sequence選択をCLIから指定し、manifestへ記録できるようにする。
- `experiments/inference_p1_association_separation.sh`: 同一checkpoint/config/inputに対してA1/A2を異なるrun_idで実行する。

P2のcache update guard、P3の入力分布混合、P4のteacher forcing/TBPTT、SAM2/SAMURAI統合、TrackEval計算方法の変更は行わない。

## 比較条件

| 条件 | association主位置 | state/cache/lifecycle |
| --- | --- | --- |
| A1 | Mamba prediction（現行） | 現行のまま |
| A2 | last trusted accepted observation | A1と同一 |

`last trusted accepted observation`はtrack生成時のdetector bbox、および`update`/`re_activate`でacceptedになったdetector bboxだけで更新する。missing時のself predictionは観測位置として記録しない。

## 評価指標

- TrackEval: HOTA、DetA、AssA、IDF1、MOTA、ID switches、track数
- 追跡出力: sequence別summary、run manifest、git diff、command、checkpoint/config/detector path
- 実装診断: A1の既存挙動との一致、A2のNaN/Inf、run directoryの非上書き、既存outputの不変性

## 成功・失敗の判断基準

- 成功: A2がA1よりAssAまたはIDF1を改善し、ID switchesを減らす傾向を示し、HOTAがA1を不必要に下回らない。A1/A2の固定条件と成果物がmanifestから照合できる。
- 失敗/保留: A2が改善しない、またはA0相当の観測優先referenceを大きく下回る場合、prediction matching単独を主因と断定せず、P2へ自動移行しない。
- 技術的中止: NaN/Inf、既存lifecycleの変化、A1再現不一致、TrackEval条件不一致、成果物上書きが発生した場合は比較を無効とする。

## 検証方法

1. 実装前後でrepo HEAD/status/diffを記録する。
2. targeted unit testでA1/A2のtrack-side matching boxが切り替わること、missing self-updateがlast observedを変更しないことを確認する。
3. `py_compile`、`git diff --check`、CLI helpを確認する。
4. 3系列に対してA1/A2をrun_id付き新規出力へ実行する。
5. 同じDanceTrack val seqmapと既存TrackEval条件で両runを評価する。
6. 結果と因果解釈をexperiment logへ保存し、P2進行はユーザー承認待ちにする。

## P2へ進む条件

P1結果を記録した後、A2の改善がprediction-primary matchingの因果効果として再現し、かつcache汚染が残る証拠がある場合だけ、P2 cache update controlを別specで計画する。P1結果だけでP2を自動実装・実行しない。

## Implementation Gate

- [x] 対象フェーズ: P1 association separationのみ
- [x] 承認済みspec: 本ファイル
- [x] 対象repo・変更範囲: 上記3コードファイルとP1実験スクリプト
- [x] 検証方法: targeted test、py_compile、git diff check、3系列A1/A2 TrackEval
- [x] ユーザーによるP1実装・実験開始承認: 2026-07-22の継続依頼により明示

## 関連ファイル

- `specs/2026-07-21-state-carry-improvement-spec-candidate.md`
- `specs/2026-07-22-experiment-artifact-retention-spec.md`
- `experiments/2026-07-21-p0-75-historical-baseline-audit.md`
- `meetings/2026-07-16-mtg.md`
