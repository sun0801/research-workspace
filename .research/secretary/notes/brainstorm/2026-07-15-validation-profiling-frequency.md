---
date: 2026-07-15
project: sam2-mamba-motion-tracking
source_todo: tracking validationの計算時間増加要因をprofilerで特定する
topic: validation-profiling-frequency
status: exploratory
tags: [brainstorm, validation, profiling, mot_metrics]
---

# Tracking validationの計算時間分析と評価周期

## 読み込んだ文脈

- 2026-07-09 MTGで、tracking validationの計算時間増加要因をprofilerで切り分ける方針になった。
- TrackEval側のCLI/API parityと、Mamba側のTrackEval直接呼び出しadapterは2026-07-15時点で確認済み。
- 現在のMamba学習導線は、毎epochのval lossと、5epochごとのmot_metricsを実行する。
- mot_metricsはtracker推論 subprocessとTrackEval評価を含むため、TrackEvalの関数呼び出し化だけではtracker推論時間は減らない。

## 相談の出発点

25epoch設定では学習不足に見えるモデルがあり、全モデルを100epochに延ばし、val lossを5epochごと、mot_metricsを10epochごとにする案が出た。一方、計算時間の原因分析前に設定を変えると、処理自体の遅さと実行回数削減の効果を分離できなくなる。

## 問い

1. tracking validationの増加時間は、学習・val loss・tracker推論・TrackEvalのどこで発生しているか。
2. 現行設定と候補設定の評価周期は、過学習監視と実行コストのバランスとして妥当か。
3. 100epoch化を行う前に、どの範囲の短い実験で判断できるか。

## 仮説候補

- mot_metricsの主要コストは、TrackEvalのsummary parseではなくtracker推論 subprocessである。
- val lossはmot_metricsより軽く、5epochごとでも過学習の大きな傾向を観察できる。
- 25epochモデルを100epochへ延ばすことで、学習不足の可能性を検証できるが、MambaStatefulは固定LRのため過学習リスクも増える。
- mot_metricsを10epochごとにしても、100epochでは約10点の評価が得られるため、広い性能推移は確認できる。ただし25epochでは評価点が少なすぎるため、まず全モデル100epoch化した後の方が整合的である。

## 実験・実装案

### 段階A: 現行設定のbaseline timing

- 5〜10epochの短い学習を使う。
- 現行設定（val loss毎epoch、mot_metrics 5epochごと）を変更しない。
- 3sequence程度の部分valを使い、学習本体、val loss、tracker推論、TrackEvalを計測する。
- mot_metrics内のtracker subprocessとTrackEval関数呼び出しを別々に計測する。

### 段階B: 処理単独の比較

- 固定checkpointでval lossを複数回測る。
- 固定tracker出力でTrackEvalのみを複数回測る。
- 固定checkpointでtracker推論のみを測る。
- 学習を伴わないため、処理ごとの固有コストを比較できる。

### 段階C: 候補周期の比較

- 同じ短い学習条件で、`val_loss_period=5`、`mot_metrics_period=10`を試す。
- baselineと候補で、1epochあたりの平均時間、評価回数、指標観測点数を比較する。
- full valは固定checkpointで1回だけ確認し、部分valの時間をfull valへ単純に外挿しすぎない。

### 段階D: 100epoch本学習

- baseline timingと候補周期の比較後に、全モデル100epochを実行する。
- val loss 5epochごと、mot_metrics 10epochごと、最終epoch評価を基本案とする。
- `best_val_loss`と`best_tracking_hota`が評価したepochだけを対象にすることを記録する。

## 計測方法

- 学習・val loss: `time.perf_counter()`による粗い区間計測と、必要な区間だけPyTorch profiler。
- tracker subprocess: 親プロセスからsubprocess全体のwall-clockを計測。内部の詳細が必要ならtracker側を別途計測する。
- TrackEval: 直接関数呼び出し区間をwall-clockで計測し、必要に応じてCPU profilerを使う。
- GPU計測では必要に応じて`torch.cuda.synchronize()`を前後に入れ、非同期実行による過小計測を避ける。

## 比較・評価軸

- 学習1epochあたりの時間
- val loss 1回の時間
- tracker推論1回の時間
- TrackEval評価1回の時間
- baselineと候補設定の総時間
- HOTA / IDF1などの観測点数と推移
- 100epoch終了時とbest checkpointの差

## 今回見えた方向性

先に現行設定をbaselineとして計測し、処理ごとのコストを分ける。その後、候補周期を別条件として比較する。profiler用の短い実験では100epoch本学習を行わず、10epoch程度と部分valで十分な情報を取る。100epoch化と評価周期変更は、baselineの記録を残した後に適用する。

## 次アクション候補

1. Mamba側にval loss、tracker subprocess、TrackEvalの区間計測を追加する。
2. 現行設定の5〜10epoch baseline timingを取得する。
3. `val_loss_period=5`、`mot_metrics_period=10`の候補条件を同じデータ範囲で比較する。
4. 比較結果を踏まえて100epoch本学習の設定を確定する。

## Spec化候補

- `2026-07-15-validation-timing-profiling-spec.md`
- 対象はまずMamba側の計測導線。現行挙動を変えない計測をbaselineとし、周期変更は比較条件として扱う。

## 未解決の問い

- 3sequence部分valをどのsequenceで固定するか。
- tracker側のフレーム単位計測まで初回specに含めるか。
- full valを100epoch中に何回実行するか。
- MambaStatefulの100epoch化とLR scheduler見直しを同時に行うか。

## 関連ファイル

- `/mnt/HDD10TB-2/aburatani/2025_09_aburatani_Mamba_Trackers/ssm_tracker/train.py`
- `/mnt/HDD10TB-2/aburatani/2025_09_aburatani_Mamba_Trackers/ssm_tracker/train_stateful.py`
- `/mnt/HDD10TB-2/aburatani/2025_09_aburatani_Mamba_Trackers/ssm_tracker/train_utils/mot_metrics.py`
- `.research/lab/projects/sam2-mamba-motion-tracking/specs/2026-07-07-validation-implementation-spec.md`
- `.research/lab/projects/sam2-mamba-motion-tracking/experiments/2026-07-15-mamba-trackeval-direct-call.md`
