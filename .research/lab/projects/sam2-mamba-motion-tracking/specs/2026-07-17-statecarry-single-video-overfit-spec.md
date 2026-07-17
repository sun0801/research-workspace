---
date: 2026-07-17
project: sam2-mamba-motion-tracking
source: brainstorm
status: draft
tags: [spec, experiment, state-carry, overfitting, tracking]
---

# State Carry 1動画過学習・同一動画tracker推論 Spec

## 目的

MambaStatefulを1本の動画のtrajectoryデータで過学習させ、同じ動画に対して`track_stateful.py`を実行する。これにより、学習lossが下がるにもかかわらずstate carry推論がframe 6付近でNaN退化するのか、または学習・推論経路のどの段階で不整合が生じるのかを切り分ける。

## 背景

- 2026-07-16の診断で、epoch 10/90のmodel outputは異なる一方、`dancetrack0004`のtracking outputが一致した。
- frame 6付近で`pending_delta`と`predicted_last_bbox`がNaNになり、matching失敗・trackのlost化・再生成が発生している。
- 既存の`StatefulTrajDataset`は固定長windowで学習する一方、推論時は`InferenceParams`を用いたcached stateを引き継ぐため、学習と推論の状態伝播が一致しているか未確認である。
- 直近の承認済み[frame transition診断spec](2026-07-16-statecarry-frame-transition-diagnostic-spec.md)は推論診断を対象とし、本specでは1動画過学習と同一動画推論を追加対象とする。

## 検証したい問い

1. 現在のMambaStateful学習経路は、1動画のtrajectoryデータを十分に過学習できるか。
2. そのcheckpointを同じ動画のtracker推論に渡したとき、state carryの予測値は有限値を保ち、frame 6付近の退化を回避できるか。
3. 学習lossが低下してもtracker推論が失敗する場合、学習window経路とcached inference経路の不整合が示唆されるか。

## 仮説

### 主仮説

1動画で学習lossは低下するが、推論時のcached state・`pending_delta`更新は学習時の固定window経路と一致せず、frame 6付近でNaNまたはmatching失敗が再現する。

### 代替仮説

1. 1動画過学習でもlossが下がらないため、データ作成・入力スケーリング・loss計算に問題がある。
2. 学習lossと推論値は正常だが、detector出力とGT trajectoryの差によってtracker matchingだけが失敗する。
3. 1動画ではtracker推論が正常化し、問題は複数track・長時間運用・full validation条件でのみ発生する。

## 実験・実装内容

### 対象データ

- 第一候補sequence: `dancetrack0004`
- 理由: 既存のepoch 10/90比較とframe 1〜7診断で使用しており、比較対象を揃えられる。
- 学習: `dancetrack0004`のGT trajectoryから1動画用annotationを作る。
- 推論: 同じsequenceの既存detector出力`det_results/dancetrack/val/dancetrack0004.txt`を使う。
- 全体`dancetrack_train.json` / `dancetrack_val.json`は変更せず、一時annotationを使う。

### 学習条件

- モデル: `MambaStateful`
- 既存のモデル構造・入力スケーリング・loss設定を維持する。
- `window_size=12`、`loss_start_index=4`を初期条件とする。
- validationの全sequence実行と`mot_metrics`は無効化し、1動画過学習のlossと推論検証に集中する。
- 学習epoch数は最大100 epochを初期上限とし、epochごとのcheckpointとlossを保存する。
- 既存ソースコードは変更せず、一時annotation・一時config・実験出力だけを作成する。診断ログが必要な場合は、承認済みframe transition診断specの範囲内のopt-inログを利用する。

### 推論条件

- epoch 1 checkpointと最終checkpointを同じ条件で推論し、学習による変化を比較する。
- tracker: `ssm_tracker/track_stateful.py`
- sequence: `dancetrack0004`
- frame 1〜最終frameを処理する。
- frame 5〜7を重点的に、次を記録する。
  - `pending_delta`
  - `predicted_last_bbox`
  - 検出bbox
  - matching IoUとmatch結果
  - track state、lost、activate、reset
  - 通常出力の有無

## 使用データ・モデル・成果物

- 学習リポジトリ: `/mnt/HDD10TB-2/aburatani/2025_09_aburatani_Mamba_Trackers`
- 学習entrypoint: `ssm_tracker/train_stateful.py`
- 推論entrypoint: `ssm_tracker/track_stateful.py`
- config: `ssm_tracker/cfgs/MambaStateful.yaml`を基準にした一時config
- 学習annotation: `dancetrack0004`のみを含む一時JSON
- detector入力: `det_results/dancetrack/val/dancetrack0004.txt`
- 成果物:
  - 一時annotationと一時config
  - epochごとのcheckpoint
  - 学習lossログ
  - tracker output
  - frame transition診断ログ
  - 実験結果Markdown

## 比較対象・ベースライン

- epoch 1 checkpoint vs 最終checkpoint
- 既存epoch 10/90の`dancetrack0004`診断結果
- 学習lossのみが低下してtracker出力が改善しないケースを、学習・推論経路の不整合候補として扱う。

## 評価指標

### 学習側

- epochごとの平均training loss
- lossが有限値であること
- 初期lossから最終lossへの減少率
- 学習中のNaN / Inf発生有無

### 推論側

- `pending_delta`と`predicted_last_bbox`のNaN / Inf発生有無
- 全frame処理完了の可否
- frameごとの出力track数
- frame 5〜7のmatching成否とtrack状態遷移
- epoch 1と最終checkpointでのtracking output差

MOT Metricsは補助指標とし、推論値が有限でframe transitionが正常であることを確認した後に、必要な場合だけ1sequenceで実行する。NaN退化中のHOTA / IDF1は成功指標として扱わない。

## 成功・失敗の判断基準

### 成功

- 1動画学習のlossが有限値を保ちながら、初期値から少なくとも10分の1以下へ低下する。
- 最終checkpointの同一動画tracker推論で、全frameが処理される。
- `pending_delta`と`predicted_last_bbox`にNaN / Infが発生しない。
- frame 5〜7で、全trackが一斉にlostになる退化が再現しない。
- epoch 1と最終checkpointで、推論値またはtracking outputに学習による差が現れる。

### 失敗または追加切り分け

- lossが10分の1以下に下がらない: annotation、window、scale、loss計算を再確認する。
- lossは下がるが推論でNaNが発生する: 学習windowとcached inferenceの不整合を優先して調査する。
- 値は有限だがmatchingに失敗する: detector/GT差、座標系、threshold、track activationを切り分ける。
- 1動画では成功するがfull validationで失敗する: 複数track、長時間state、detectorノイズを次の実験要因とする。

## 実施手順

1. 外部リポジトリの現在のcommit、git status、対象ファイルdiffを記録する。
2. `dancetrack0004`だけを含む一時trajectory annotationを作成する。
3. 全validationを無効化した一時configを作成する。
4. 1 epochの学習smokeを実行し、データロード・checkpoint保存・loss計算を確認する。
5. 最大100 epochまで学習し、loss推移とcheckpointを保存する。
6. epoch 1と最終checkpointで同じ`dancetrack0004`を推論する。
7. frame 5〜7のstate transitionと全frameのNaN / Infを確認する。
8. 成功条件を満たした場合だけ、必要に応じて1sequenceのMOT Metricsを実行する。
9. 学習、推論、評価を分離して結果をexperiment logへ保存する。

## 期待される結果

- lossだけが下がって推論が退化する場合、現在の学習経路がstate carry推論を十分に学習していない可能性が高い。
- loss低下と推論正常化が同時に起きる場合、既存full validationの問題は学習規模・checkpoint・detector条件に依存する可能性がある。
- 1動画でもlossが下がらない場合、state carryの学習方法をRNN/LSTMのteacher forcing・free runningと比較する前に、データ・loss・入力scaleを確認する。

## リスク・懸念

- `StatefulTrajDataset`は固定長windowを作るため、1動画でlossが下がっても、真の長期state carry学習が成立したとは限らない。
- 学習はGT trajectory、推論はdetector出力のため、同じsequenceでも入力bboxは完全一致しない。
- `dancetrack0004`の有効track数やtrajectory長が少ない場合、window数が不足する可能性がある。
- 1動画の成功をfull validationや一般化性能の根拠にしない。

## 未決事項

- `dancetrack0004`以外のsequenceを追加する必要性
- detector出力の代わりにGT bboxをtracker入力へ使う分離実験の要否
- 100 epochで過学習しない場合の追加epoch数
- 1動画実験後にstate carry学習経路そのものを修正するか、診断specを追加するか

## Implementation Gate

- [x] 承認済みspecのパス: 本spec
- [x] 変更対象と変更範囲: 一時annotation・一時config・実験出力。既存ソースコードとcanonical configは初回実験では変更しない。
- [x] 検証方法: epoch 1/最終checkpoint比較、loss推移、全frame有限性、frame 5〜7 state transition確認。
- [x] ユーザーのspec化承認: 2026-07-17に明示承認済み。
- [ ] 実験実行開始: 本spec保存後に別途開始する。

## 関連brainstorm・spec

- [../experiments/2026-07-16-statecarry-frame-transition-diagnostic.md](../experiments/2026-07-16-statecarry-frame-transition-diagnostic.md)
- [../experiments/2026-07-16-statecarry-mot-metrics-diagnostic.md](../experiments/2026-07-16-statecarry-mot-metrics-diagnostic.md)
- [2026-07-16-statecarry-frame-transition-diagnostic-spec.md](2026-07-16-statecarry-frame-transition-diagnostic-spec.md)
- [../../../secretary/notes/brainstorm/2026-07-16-statecarry-metrics-degenerate-diagnosis.md](../../../secretary/notes/brainstorm/2026-07-16-statecarry-metrics-degenerate-diagnosis.md)
