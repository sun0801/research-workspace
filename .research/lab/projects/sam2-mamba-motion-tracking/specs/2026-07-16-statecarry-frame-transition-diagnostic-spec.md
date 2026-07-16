---
date: 2026-07-16
project: sam2-mamba-motion-tracking
source: brainstorm
status: draft
tags: [spec, diagnostic, state-carry, tracking, mot_metrics]
---

# MambaStateful frame transition 診断 Spec

## 目的

MambaStatefulでepoch 10とepoch 90のmodel outputが異なるにもかかわらず、tracking outputおよびHOTA / IDF1が完全一致する原因を、state carry predictionが有効になるframe transition付近で切り分ける。

本specは、学習条件・checkpoint・MOT評価指標を変更せず、診断用ログを追加してtracking pipelineの退化箇所を特定することを目的とする。

## 背景と既知の観測

- 対象実験: `mamba_stateful` / `MambaStateful`
- 学習設定: 100 epochs、`val_loss_period=5`、`mot_metrics_period=10`
- 比較checkpoint: epoch 10、epoch 90
- 比較sequence: `dancetrack0004`
- epoch 10/90の代表的なstateful model outputは異なる。
- しかし通常tracking outputは完全一致している。
- 両出力は3407行、1189 frames、861 unique IDsで、各IDの最大継続長は5 records。
- frame 6にoutputがなく、frame 7から新しいIDが現れる。
- `enable_time_thresh=5` 到達後にstate carry predictionが有効になる。

## 検証仮説

### 主仮説

`enable_time_thresh=5` 到達直後にstate carry predictionと検出のmatchingが失敗し、trackが一斉にlostになる。その後にactivateされたtrackが同一frameで出力されないため、epoch間で同じtrack break / reactivationパターンへ収束する。

### 代替仮説

1. `pending_delta` の座標変換、scale、clip、またはstate更新順序が誤っている。
2. predictionは妥当だが、matchingの座標系またはthresholdが不適切である。
3. matching失敗後のlost/reset処理、または新規trackのactivation・出力タイミングが意図と異なる。
4. model outputの差が実際のtracker updateに渡る前に破棄・上書きされている。

## 対象と固定条件

- checkpoint: epoch 10、epoch 90
- dataset: DanceTrack validation
- sequence: `dancetrack0004`
- 観測範囲: 少なくともframe 1〜7（frame 5〜7を重点記録）
- tracker: `track_stateful.py`
- config: `ssm_tracker/cfgs/MambaStateful.yaml`
- inference条件、threshold、`missing_mode`、`delta_clip`、scaleは変更しない
- 学習、checkpoint、TrackEval metric、Comet loggingは変更しない
- 比較可能性のためepoch 10/90で同一入力・同一device条件を使う

## 実装変更範囲

外部リポジトリでは、診断ログを取得するための最小限の変更だけを許可する。

対象候補:

- `ssm_tracker/track_stateful.py`
- `ssm_tracker/track_utils/stateful_tracklet.py`
- `ssm_tracker/track_utils/matching.py`

実装方針:

- `--diagnostic` など明示的な診断モードでのみログを有効化する。
- 通常のtracking output、checkpoint、config既定値、Comet記録は変更しない。
- 全frameの大量ログではなく、指定sequenceのframe 1〜7をJSONLまたはTSVで保存する。
- 診断終了後に診断ログ以外の差分が残っていないことを確認する。

## 必須ログ項目

frameごと、trackごとに以下を記録する。

- frame index
- track ID
- detection bbox
- `memo_bank` 最新bbox
- `predicted_last_bbox`
- `pending_delta`
- `enable_time_thresh` 判定結果、およびprediction使用/未使用
- matching候補とIoU、または選択されたmatchのIoU
- match成功/失敗
- track state（tracked / lost / removed等）
- `is_activated`
- 新規activate、update、mark_lost、resetのイベント
- 通常出力に採用されたbboxと、その出力有無

epoch 10/90で同じ形式にし、frame 5〜7を横並び比較できるようにする。

## 出力先

既存profiling成果物の下に保存する。

```text
artifacts/profiling/mamba_validation_2026-07-15/full_validation/statecarry_epoch_compare/frame_transition/
├── epoch10/
│   ├── diagnostic.jsonl
│   └── inference.log
└── epoch90/
    ├── diagnostic.jsonl
    └── inference.log
```

Research Workspaceには、実行結果と解釈を次のexperiment logへ保存する。

```text
.research/lab/projects/sam2-mamba-motion-tracking/experiments/2026-07-16-statecarry-frame-transition-diagnostic.md
```

## 検証手順

1. 外部リポジトリのgit status、現在のcommit、対象ファイルのdiffを記録する。
2. 診断モードを追加する。
3. epoch 10とepoch 90を同一sequenceで実行する。
4. frame 5〜7のprediction、matching、state transitionを比較する。
5. 診断モードを使わない通常trackingで、既存出力と同一であることを確認する。
6. 診断用変更を除く差分がないことを確認する。
7. 主仮説または代替仮説のどれを支持するかをexperiment logへ記録する。

## 判定基準

### 原因特定とみなす条件

- frame 6付近でprediction使用開始、IoU低下、match失敗、lost化の因果順序を確認できる。
- epoch 10/90のmodel output差が、どの段階でtracking結果から消えるか特定できる。
- 新規trackが同一frameで出力されない挙動が、意図した仕様か実装上の問題か判断できる。

### 未解決とみなす条件

- 必須ログ項目が欠けてepoch間比較ができない。
- frame 5〜7でmatchingが成功しているのにtracking outputが一致する。
- model outputが実際のstate carry updateへ渡っているか確認できない。

## 修正へ進む条件

診断結果をもとに、次のいずれか一つに絞った修正specまたは実装方針を別途確定する。

- prediction fallback / delta変換の修正
- matching条件または座標系の修正
- lost/reset・state contamination対策
- 新規trackのactivation・出力タイミング修正

原因未確定のまま、最新検出bboxの出力処理だけを変更しない。

## Implementation Gate

- [x] 承認済み研究方針: state carry結果を保留し、局所診断を先行する
- [x] 診断対象と観測範囲: epoch 10/90、`dancetrack0004`、frame 1〜7
- [x] 変更範囲: 診断モードとログ追加のみ
- [x] 検証方法: 同一条件比較、通常tracking非変更確認、git diff確認
- [ ] ユーザーによる外部リポジトリ実装開始承認

本spec保存時点では、外部リポジトリを編集しない。

## 関連資料

- [2026-07-16-statecarry-mot-metrics-diagnostic.md](../experiments/2026-07-16-statecarry-mot-metrics-diagnostic.md)
- [2026-07-16-statecarry-metrics-degenerate-diagnosis.md](../../../secretary/notes/brainstorm/2026-07-16-statecarry-metrics-degenerate-diagnosis.md)
- [2026-07-15-full-validation-correlation-analysis-spec.md](2026-07-15-full-validation-correlation-analysis-spec.md)
