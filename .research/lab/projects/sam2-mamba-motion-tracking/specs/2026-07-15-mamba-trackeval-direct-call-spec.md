---
date: 2026-07-15
project: sam2-mamba-motion-tracking
source: 2026-07-15-trackeval-cli-api-parity-spec
status: draft
tags: [spec, mot_metrics, trackeval, validation, integration]
---

# Mamba側TrackEval評価直接呼び出し Spec

## 目的

Mamba側のtracking validationで、tracker推論 subprocessは維持したまま、TrackEval評価 subprocessだけをTrackEvalの関数呼び出しへ置き換える。

これにより、tracker推論とTrackEval評価の問題・計算時間を分離して確認できる状態を作る。

## 前提

TrackEval側では、以下の関数化とCLI/API parity確認が完了している。

- `parse_args(argv=None)`
- `run_mot_evaluation(config)`
- `main(argv=None)`

対象ファイル:

- `/mnt/HDD10TB-2/aburatani/TrackEval/scripts/run_mot_challenge.py`

## 検証したい問い

Mamba側の `run_mot_metrics()` が、tracker推論結果を同じTrackEval設定へ渡したとき、評価 subprocess経由と直接関数呼び出しで同じmetric結果を返せるか。

## 仮説

TrackEval側のCLI/API parityが成立しているため、Mamba側で評価 subprocessだけを関数呼び出しへ置き換えても、HOTA / DetA / AssA / MOTA / IDF1は一致する。

## 対象範囲

### 変更対象

- `/mnt/HDD10TB-2/aburatani/2025_09_aburatani_Mamba_Trackers/ssm_tracker/train_utils/mot_metrics.py`

### 非対象

- `train.py`
- `train_stateful.py`
- `track.py`
- `track_stateful.py`
- tracker推論 subprocess
- checkpoint保存ロジック
- Comet loggingのnamespace
- summary parseの廃止
- 計算時間最適化そのもの

## 実装方針

### 1. tracker推論は維持

`track_proc = subprocess.run(track_cmd, ...)` は変更しない。checkpoint、device、det_path、tracker output生成の挙動を固定する。

### 2. TrackEvalモジュールを読み込む

`validation_cfgs["trackeval_repo"]` にある `scripts/run_mot_challenge.py` をimport可能な形で読み込み、`parse_args()` と `run_mot_evaluation()` を利用する。

評価設定は現在の `eval_cmd` と同じ値から構築する。

- GT_FOLDER
- TRACKERS_FOLDER
- BENCHMARK
- SPLIT_TO_EVAL
- SKIP_SPLIT_FOL
- TRACKERS_TO_EVAL
- METRICS
- DO_PREPROC
- USE_PARALLEL
- OUTPUT_SUB_FOLDER

### 3. 初回はsummary parseを維持

直接関数呼び出し後も、既存の `pedestrian_summary.txt` を読み、`_parse_summary()` でmetric dictを作る。

これにより、初回変更は「TrackEval subprocessを関数呼び出しへ置き換えた」範囲に限定できる。

### 4. エラー処理を維持

以下の場合は従来どおり例外にする。

- tracker推論 subprocessが失敗
- TrackEval関数が例外を返す
- summaryが生成されない
- 必要metricがsummaryに存在しない

## 比較対象・ベースライン

- ベースライン: 現在の `run_mot_metrics()`。tracker推論とTrackEval評価の両方をsubprocessで実行。
- 変更後: tracker推論subprocess + TrackEval直接関数呼び出し。

同じcheckpoint、同じdet_path、同じtracker output設定でmetric結果を比較する。

## 検証方法

### 単体テスト

- `should_run_mot_metrics()` の既存テストを維持する。
- TrackEval評価呼び出しをmockし、`run_mot_metrics()` がtracker subprocessを1回だけ実行し、TrackEval subprocessを実行しないことを確認する。
- TrackEval関数へ渡すconfigが、旧eval_cmdと同じ内容であることを確認する。

### smoke確認

- 固定checkpointまたは既存tracker出力を使う。
- HOTA / DetA / AssA / MOTA / IDF1を変更前後で比較する。
- summaryファイルの出力先・内容が一致することを確認する。

## 成功/失敗の判断基準

### 成功

- tracker推論 subprocessが従来どおり動作する
- TrackEval subprocessが呼ばれない
- TrackEval関数が成功し、summaryが生成される
- 変更前後の主要metricが許容誤差 `1e-6` 以内で一致する
- `train.py` / `train_stateful.py` の変更なしでvalidation呼び出しが成立する

### 失敗

- tracker推論の挙動が変わる
- TrackEvalモジュールimport時に環境依存で失敗する
- CLIと関数でmetric値・summary出力が異なる
- summary出力先がずれる
- 学習ループ側の変更が必要になる

## 実施手順

1. Mamba側の現在のgit状態を記録する。
2. `mot_metrics.py` にTrackEval関数ローダーと直接呼び出しを追加する。
3. subprocess呼び出し回数とconfig伝播をmockで確認する。
4. 固定checkpointまたはsmoke設定で変更前後のmetricを比較する。
5. tracker推論時間とTrackEval評価時間を別々に記録する。

## リスク・懸念

- TrackEvalスクリプトをpath importする場合、Python module cacheと複数呼び出し時の再利用を管理する必要がある。
- TrackEval import時に、MOT評価に不要な依存（例: `pycocotools`）のwarningが出る可能性がある。
- `tracker_dir` の削除処理は既存のまま残るため、tracker_nameの衝突に注意する。
- 直接呼び出し化だけではTrackEval本体の計算量は減らない。

## 未決事項

- TrackEvalモジュールのpath importをmodule cacheするか、毎回読み込むか。
- 実際のsmokeに使うcheckpointとtracker output範囲。
- 変更後にsummary parseを残す期間。

## 関連spec

- [2026-07-15-trackeval-cli-api-parity-spec.md](2026-07-15-trackeval-cli-api-parity-spec.md)

## 関連実験

- [2026-07-15-trackeval-cli-api-parity.md](../experiments/2026-07-15-trackeval-cli-api-parity.md)
