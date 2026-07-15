---
date: 2026-07-15
project: sam2-mamba-motion-tracking
source: 2026-07-15-mamba-trackeval-direct-call-spec
status: smoke-passed
tags: [experiment, mot_metrics, trackeval, validation, integration]
---

# Mamba側TrackEval直接呼び出し確認

## 目的

tracker推論 subprocessを維持したまま、Mamba側のTrackEval評価だけを直接関数呼び出しへ置き換え、結果一致を確認する。

## 変更対象

- `/mnt/HDD10TB-2/aburatani/2025_09_aburatani_Mamba_Trackers/ssm_tracker/train_utils/mot_metrics.py`

追加した処理:

- TrackEval `run_mot_challenge.py` のpath importとcache
- `parse_args()` による旧CLI設定の構築
- `run_mot_evaluation()` の直接呼び出し
- TrackEval失敗時の例外ラップ

変更していない処理:

- `track.py` / `track_stateful.py` のtracker推論 subprocess
- `train.py` / `train_stateful.py`
- summary parse

## 検証結果

### mock検証

- tracker subprocess呼び出し: 1回
- TrackEval subprocess呼び出し: 0回
- TrackEval関数へのtracker名・metric設定: 期待値どおり
- summary parse結果: HOTA / DetA / AssA / MOTA / IDF1を取得

結果: PASS

### 実TrackEval adapter smoke

- 既存 `my_samurai_model` のDanceTrack val 25 sequence出力を使用
- Mamba側 `_run_trackeval()` から実TrackEval関数を呼び出し
- `pedestrian_summary.txt` 生成: 成功
- combined HOTA: `54.109`
- combined IDF1: `62.327`

結果: PASS

### CLIとのfull-val parity

- 同じ25 sequence tracker出力をCLI経由とadapter経由で評価
- `pedestrian_summary.txt` 完全一致

結果: PASS

## 補足

- `pycocotools` / `tabulate` 不在に関するTrackEval import warningは出るが、MOT評価は完走した。
- `mamba_statecarry_smoke` は3 sequence分しかないため、adapter実評価には25 sequence分ある既存tracker fixtureを使った。
- 学習ループを実際に回すsmokeと、summary parse廃止はまだ実施していない。

### 実tracker推論end-to-end

- CPU: `mamba_ssm` のCUDA専用 `selective_scan` のため実行不可。
- GPU: 対応configでcheckpoint読み込み後、2/25 sequenceまで進行したが、全val完走に長時間を要するため中断。
- 部分出力は削除済み.

## 判定

Mamba側でTrackEval評価subprocessだけを直接関数呼び出しへ置き換える経路は、mock・実TrackEval・full-val CLI parityの範囲で成立した。tracker推論subprocessは変更していない。実tracker推論を含む全val end-to-endは、CUDA依存と計算時間のため未完了.
