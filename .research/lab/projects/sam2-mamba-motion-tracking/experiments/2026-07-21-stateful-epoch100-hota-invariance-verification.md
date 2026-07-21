# MambaStateful epoch100 HOTA不変性確認

## 目的

epoch1だけでなく100epoch checkpointを使ってもHOTAが4.7付近から改善しない、という仮説を確認する。

## 条件

- checkpoint: `ssm_tracker/saved_ckpts/mamba_stateful_dancetrack/epoch100.pth`
- 比較対象: 今回生成したepoch1 checkpoint
- 対象sequence: DanceTrack val `dancetrack0004`, `dancetrack0005`, `dancetrack0007`
- 入力: 同一の既存detector bbox
- 推論: 同一の`track_stateful.py`、同一の`MambaStateful.yaml`
- TrackEval: HOTA/CLEAR/Identity、`DO_PREPROC=False`
- 出力先: `/tmp/mamba_stateful_epoch100_verify_20260721/`
- 外部実装リポジトリのソースコード・既存checkpointは変更していない

## 結果

| checkpoint | HOTA | DetA | AssA | IDF1 | MOTA | ID switches |
|---|---:|---:|---:|---:|---:|---:|
| epoch1（今回生成） | 4.7552 | 68.551 | 0.33101 | 0.44802 | 54.203 | 3,526 |
| epoch100（既存） | **4.7552** | **68.551** | **0.33101** | **0.44802** | **54.203** | **3,526** |

epoch1とepoch100の追跡結果テキストは、3sequenceすべてで`diff`上同一だった。checkpointのmodel stateは同一ではなく、epoch番号は1と100、35個のmodel keyすべてに差分があった（最大絶対差4.60957）。

## 解釈

100epoch checkpointでもHOTAが4.7552から動かないことは確認できた。したがって、今回の低HOTAは単なるepoch1の学習不足ではない。

一方、epoch1とepoch100で追跡結果が完全一致したため、学習された重みの差が現行の追跡出力へ反映されていない、または予測bboxがassociationに効かない形で抑制されている可能性がある。GT-input診断で確認済みの「Mamba予測bboxを主matching位置に使うとAssAが崩れる」というassociation問題とは整合するが、重み差が出力に反映されない箇所は別途コード診断が必要である。

なお、`train_stateful_tracker.sh`の現行設定では`epochs: 100`だが、`mot_metrics_period: 10`のため学習中のHOTA評価はepoch10, 20, ..., 100で実行される。今回の確認は、実際のepoch100 checkpointを同一の3sequence評価経路に通したものなので、100epoch時点のHOTA不変性を直接確認している。
