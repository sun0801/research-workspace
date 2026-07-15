---
date: 2026-07-15
project: sam2-mamba-motion-tracking
source: 2026-07-15-trackeval-cli-api-parity-spec
status: smoke-passed
tags: [experiment, trackeval, validation, parity]
---

# TrackEval CLI/API parity確認

## 目的

TrackEval内で関数分離した評価導線が、既存CLI導線と同じ結果を返すか確認する。

## 変更対象

- `/mnt/HDD10TB-2/aburatani/TrackEval/scripts/run_mot_challenge.py`

変更内容は、CLI引数処理を `parse_args(argv=None)` に分離し、評価本体を `run_mot_evaluation(config)` として公開し、CLI入口を `main(argv=None)` に整理したもの。

Mamba側リポジトリには変更なし。

## 検証条件

- GT: DanceTrack val
- tracker: `mamba_statecarry_smoke`
- metrics: HOTA / CLEAR / Identity
- `DO_PREPROC=False`
- `USE_PARALLEL=False`
- 出力: CLI用と関数用で別ディレクトリ

## 結果

### 1シーケンス

- sequence: `dancetrack0004`
- CLI: 成功
- 関数: 成功
- `output_msg`: `Success`
- `pedestrian_summary.txt`: 完全一致

### 3シーケンス

- sequences: `dancetrack0004`, `dancetrack0005`, `dancetrack0007`
- CLI: 成功
- 関数: 成功
- `output_msg`: `Success`
- `pedestrian_summary.txt`: 完全一致

## 追加確認

- `python3 -m py_compile scripts/run_mot_challenge.py`: 成功
- CLI `--help`: 成功
- `git diff --check`: 成功
- Mamba側リポジトリ: 未変更

## 注意点

- `mamba_statecarry_smoke` はval全25 sequenceではなく3 sequence分のtracker出力だけを持つため、今回の全val確認は3 sequence範囲。
- TrackEval import時に `pycocotools` 不在のBURST警告が出るが、MOT評価は完走した。
- 今回はsummaryファイル経由を維持しており、Mamba側の評価subprocess置換やsummary parse廃止は未実施。

## 判定

TrackEval内のCLI/API parityは、固定tracker出力の1 sequenceおよび3 sequence smoke範囲で確認できた。次段階のMamba側統合は、別spec・別変更として扱う。
