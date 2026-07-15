---
date: 2026-07-15
project: sam2-mamba-motion-tracking
source: brainstorm
status: draft
tags: [spec, trackeval, validation, parity]
---

# TrackEval CLI/API parity確認 Spec

## 目的

TrackEvalリポジトリ内の既存CLI評価導線を再利用可能なPython関数へ分離し、CLI実行と関数実行が同じ評価結果を返すことを確認する。

本specの対象はTrackEvalリポジトリだけとし、Mamba側の学習コード・`mot_metrics.py`・tracker推論導線は変更しない。

## 背景

2026-07-09 MTGでは、TrackEvalの関数化と学習ループへの統合を同時に評価せず、まずTrackEval側の導線を単体で確認する方針になった。

TrackEvalには `Evaluator.evaluate()`、`MotChallenge2DBox`、HOTA/CLEAR/Identityのmetric APIが既にある。一方、`scripts/run_mot_challenge.py` では、CLI引数解析、config構築、評価実行が `__main__` 内にまとまっている。

## 検証したい問い

既存CLIと、CLIと同じ設定を受け取るPython関数呼び出しは、同じtracker出力に対して同じ評価結果を返すか。

## 仮説

CLI処理を「引数/config構築」と「評価実行」に分離し、CLIから評価関数を呼ぶ構造にしても、GT・tracker・metric設定が同じなら評価結果は一致する。

## 対象範囲

### 変更対象

- `/mnt/HDD10TB-2/aburatani/TrackEval/scripts/run_mot_challenge.py`
- 必要に応じて、TrackEvalリポジトリ内の評価テストまたは小規模fixture

### 非対象

- `/mnt/HDD10TB-2/aburatani/2025_09_aburatani_Mamba_Trackers/ssm_tracker/train_utils/mot_metrics.py`
- `train.py` / `train_stateful.py`
- `track.py` / `track_stateful.py`
- tracker推論 subprocess
- TrackEval本体のmetric計算ロジック
- 計算時間の最適化
- summaryファイルparseの廃止

## 実験・実装内容

### 1. CLI処理の分離

以下の責務を分ける。

- `parse_args(argv=None)` または同等の引数/config変換処理
- `run_mot_evaluation(config)` または同等の評価関数
- `main(argv=None)` によるCLI入口

既存CLIは、最終的に評価関数を呼び出すだけの構造にする。Dataset、metric、Evaluatorの設定値と評価順序は変更しない。

### 2. 固定tracker出力による比較

入力は既存のDanceTrack tracker出力を使い、tracker推論は実行しない。

- GT: `/mnt/HDD10TB-2/aburatani/TrackEval/data/gt/dancetrack/val`
- tracker: 既存の `mamba_statecarry_smoke` 出力
- benchmark: `dancetrack`
- split: `val`
- `SKIP_SPLIT_FOL=True`
- metrics: `HOTA`, `CLEAR`, `Identity`
- `DO_PREPROC=False`
- `USE_PARALLEL=False`

最初は1シーケンスのsmoke評価で確認し、成功後に同じ固定tracker出力でval全体を確認する。

### 3. CLI/API結果比較

以下を比較する。

- CLI実行の終了成否
- 関数実行の `output_msg`
- HOTA / DetA / AssA / MOTA / IDF1
- `pedestrian_summary.txt` のヘッダと値
- 評価対象tracker数・sequence数

初回は既存summary出力を維持し、関数化によるプロセス境界の変更だけを検証する。

## 使用データ・成果物

### 入力

- TrackEvalの既存DanceTrack val GT
- TrackEvalの既存固定tracker出力

### 成果物

- TrackEval内の関数化されたCLI導線
- CLI/API parity確認結果
- 必要に応じたTrackEval内テスト

## 比較対象・ベースライン

- ベースライン: 関数化前の既存 `run_mot_challenge.py` CLI
- 比較対象: 評価関数を呼ぶように整理したCLI、および同じ評価関数の直接呼び出し

## 評価指標

- HOTA
- DetA
- AssA
- MOTA
- IDF1
- `output_msg` の成功状態
- summaryファイルの生成・内容

## 成功/失敗の判断基準

### 成功

- 既存CLIが従来どおり完走する
- 直接関数呼び出しが完走する
- CLI/APIの主要metricが許容誤差 `1e-6` 以内で一致する
- summaryのヘッダ・値・出力先が一致する
- Mamba側リポジトリに変更がない

### 失敗

- CLIが関数化後に動かない
- CLI/APIでmetric値が一致しない
- tracker・GT・split・metric設定が意図せず変わる
- staleな出力を読み込む、またはsummary出力先がずれる
- TrackEval本体の計算ロジック変更が必要になる

## 実施手順

1. 現在のTrackEvalリポジトリのコミットとCLI結果を記録する。
2. CLI処理をconfig構築・評価関数・CLI入口へ分離する。
3. 1シーケンスでCLI/API parityを確認する。
4. 固定tracker出力のval全体でCLI/API parityを確認する。
5. 結果と変更範囲を記録し、Mamba側統合は別specとして扱う。

## リスク・懸念

- CLIスクリプトのimport時に、現在の `sys.path` 設定へ依存している可能性がある。
- `OUTPUT_FOLDER` / `OUTPUT_SUB_FOLDER` の違いで、CLIと関数のsummary出力先がずれる可能性がある。
- 既存tracker出力を上書きしないよう、比較時の出力先を分離する必要がある。
- 直接関数化しても、TrackEval本体の計算時間が減るとは限らない。

## 未決事項

- 関数名とconfigの受け渡し形式
- TrackEval内に新規テストfixtureを追加するか、既存DanceTrack出力だけでsmokeするか
- 1シーケンスとして使用するsequence名

## 関連brainstorm

- [2026-07-15-trackeval-direct-call-direction.md](../../../secretary/notes/brainstorm/2026-07-15-trackeval-direct-call-direction.md)

## 関連ファイル

- `/mnt/HDD10TB-2/aburatani/TrackEval/scripts/run_mot_challenge.py`
- `/mnt/HDD10TB-2/aburatani/TrackEval/trackeval/eval.py`
- `/mnt/HDD10TB-2/aburatani/TrackEval/trackeval/datasets/mot_challenge_2d_box.py`
