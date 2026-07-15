---
date: 2026-07-15
project: sam2-mamba-motion-tracking
source: brainstorm
status: draft
tags: [spec, validation, profiling, mot_metrics]
---

# Tracking validation計算時間profiling実行 Spec

## 目的

Mamba学習導線の計算時間増加を、学習本体・val loss・tracker推論・TrackEval評価に分解して特定する。その後、`val_loss_period=5` / `mot_metrics_period=10` の候補設定を現行設定と比較し、100epoch本学習へ進む設定を判断する。

## 背景と問い

現在はval lossを毎epoch、`mot_metrics`を5epochごとに実行する。`mot_metrics`はtracker推論 subprocessとTrackEval評価の両方を含む。TrackEval直接関数呼び出しのCLI/API parityは確認済みだが、tracker推論時間とTrackEval本体の時間は未分離である。

検証する問いは以下とする。

1. 時間増加は、学習本体・val loss・tracker推論・TrackEvalのどこで発生しているか。
2. 現行設定と候補設定で、1epochあたりの総時間と評価観測密度はどう変わるか。
3. 100epoch本学習へ進む前に、部分valで判断できるか。

## 仮説

- `mot_metrics`の主要コストはsummary parseではなくtracker推論 subprocessである。
- TrackEval直接関数呼び出し化では起動オーバーヘッドは減るが、評価本体の計算量は大きく変わらない。
- val lossはmot_metricsより軽く、5epochごとでも過学習の大きな傾向を観測できる。
- 100epochでmot_metricsを10epochごとにすれば約10点の観測が得られる。

## 変更対象と範囲

対象ファイル:

- `/mnt/HDD10TB-2/aburatani/2025_09_aburatani_Mamba_Trackers/ssm_tracker/train.py`
- `/mnt/HDD10TB-2/aburatani/2025_09_aburatani_Mamba_Trackers/ssm_tracker/train_stateful.py`
- `/mnt/HDD10TB-2/aburatani/2025_09_aburatani_Mamba_Trackers/ssm_tracker/train_utils/mot_metrics.py`

実装するもの:

- `val_loss_period`を通常運用設定として読み取り、未指定時は`1`として現行挙動を維持する。
- `timing_enabled`を分析用設定として読み取り、未指定時は`false`として通常学習時の追加処理を無効にする。
- `timing_enabled=true`の場合のみ、val loss区間、tracker推論subprocess全体、TrackEval直接関数呼び出し区間を`time.perf_counter()`で計測する。
- 計測結果は`timing_enabled=true`の場合のみ既存ログへ出力する。metric dictやCometの既存namespaceは変更しない。
- `mot_metrics_period`は通常運用設定として維持する。

実装しないもの:

- trackerアルゴリズム、モデル、optimizer、LR scheduler、TrackEval metricの変更
- 100epoch本学習の実行
- full valを毎回実行する運用への変更
- checkpoint選択基準の変更
- tracker subprocessの廃止
- 通常学習時に常時有効なPyTorch profilerやcProfileの導入

## 実験条件

### A. 現行設定baseline

- 5〜10epochの短い学習
- val loss: 毎epoch
- mot_metrics: 5epochごと
- timing: `timing_enabled=true`
- 3sequence程度の固定部分val
- 現在のTrackEval直接関数呼び出しadapterを使用

### B. 処理単独計測

- 固定checkpointでval lossのみを複数回実行
- 固定checkpointでtracker推論のみを実行
- 固定tracker出力でTrackEvalのみを複数回実行

### C. 候補周期比較

- Aと同じデータ範囲・seed・deviceを使用
- val loss: 5epochごと
- mot_metrics: 10epochごと
- timing: `timing_enabled=true`
- 10epoch程度の短い学習

full valは固定checkpointに対して必要最小限の回数だけ実行する。

## 計測方法と記録値

- `timing_enabled=true`の場合のみ、粗い区間時間を`time.perf_counter()`で測る。
- `timing_enabled=true`の場合のみ、GPU処理の前後で必要に応じて`torch.cuda.synchronize()`を呼ぶ。
- 親プロセスのPyTorch profilerでtracker子プロセス内部を測らない。
- 必要な場合のみ、専用のprofiling実行でTrackEvalにCPU profiler、tracker側に別計測を追加する。
- 通常学習（`timing_enabled=false`）では、追加のprofiler・同期・時間ログを実行しない。

記録する値:

- epoch、学習epoch時間、val loss実行時間
- tracker推論時間、TrackEval評価時間、summary parse時間
- HOTA / DetA / AssA / MOTA / IDF1
- model、config、device、sequence範囲、git commit

## 成功基準

- 現行baselineのmetric・summary・tracker出力を変えずに各区間の時間を記録できる。
- tracker推論とTrackEval評価の時間を別々に確認できる。
- `timing_enabled=false`で通常学習時の計測処理を無効化できる。
- 候補周期の時間削減量と観測点数を比較できる。
- 100epoch本学習へ進む設定について、時間と観測密度の根拠を実験ログに残せる。

## 実施手順

1. Mamba側のgit状態、TrackEval commit、config、deviceを記録する。
2. `timing_enabled`の有効・無効を切り替えられる計測コードを追加し、既存mock・py_compile・git diff checkを実行する。
3. 固定tracker出力でTrackEval直接呼び出し時間を測る。
4. 固定checkpointでtracker推論時間を測る。
5. 現行設定の5〜10epoch部分val baselineを実行する。
6. 候補周期設定を同条件で実行する。
7. baseline / 候補の時間とmetric観測点を比較する。
8. 比較結果を実験ログへ保存し、100epoch本学習の設定を確定する。

## リスク・未決事項

- trackerスクリプトにはsequence選択引数がないため、部分valは3sequenceだけを含む一時的な検出結果・GT範囲を用意する。
- GPU初回起動やI/Oの影響で短い実験の時間はぶれる可能性がある。
- MambaStatefulを100epochへ延長すると固定LRによる過学習リスクが増える。
- `best_val_loss` / `best_tracking_hota`は評価したepochの中でのみ更新される。
- `timing_enabled=true`でのGPU同期やログ出力は、分析時の計測オーバーヘッドを含む可能性がある。
- 初回計測でフレーム単位のtracker内部計測まで行うかは、粗い区間計測の結果を見て決める。

## 関連brainstorm

- [2026-07-15-validation-profiling-frequency.md](../../../secretary/notes/brainstorm/2026-07-15-validation-profiling-frequency.md)

## 関連spec・実験

- [2026-07-07-validation-implementation-spec.md](2026-07-07-validation-implementation-spec.md)
- [2026-07-15-mamba-trackeval-direct-call-spec.md](2026-07-15-mamba-trackeval-direct-call-spec.md)
- [2026-07-15-mamba-trackeval-direct-call.md](../experiments/2026-07-15-mamba-trackeval-direct-call.md)
