---
date: 2026-07-15
project: sam2-mamba-motion-tracking
source: brainstorm
status: approved
tags: [spec, experiment, validation, correlation, mot_metrics]
---

# 100epoch full validationと相関分析 Spec

## 目的

MambaTrack、TrackSSM、MambaStatefulを100epoch条件に揃え、epoch 10, 20, ..., 100でfull valのmot_metricsを取得する。モデルごとにval lossとHOTA / IDF1の推移、Pearson相関、Spearman順位相関、best epoch一致を探索的に分析し、checkpoint選択と次の学習設定検討の根拠を残す。

## 背景

val lossとmot_metricsの学習導線、周期制御、TrackEval直接呼び出しは実装・smoke済みである。MambaStatefulの3sequence計測ではtracker推論 subprocessが約316.973秒、TrackEvalが約3.490秒で、tracking評価コストはtracker推論が支配的だった。

25epochでは学習不足に見えるモデルがあるため全モデルを100epochへ揃える。一方、評価コストを抑えるためval lossは5epoch周期、full valのmot_metricsは10epoch周期とする。MambaStatefulのLR schedulerは今回変更せず、scheduler変更を別要因として分離する。

## 検証したい問い

1. val lossとHOTA / IDF1には、モデルごとにどの程度の線形・単調関係があるか。
2. val loss最小epochと、HOTA最大epoch・IDF1最大epochは一致するか。
3. val lossをtracking性能のcheckpoint選択補助として利用できる傾向があるか。
4. その傾向はsliding window型とstate carry型で異なるか。

## 仮説

- val lossとtracking性能が対応する場合、val lossとHOTA / IDF1には負の相関が現れる。
- 非線形だが単調な関係では、PearsonよりSpearmanの絶対値が大きくなる可能性がある。
- val lossは1-step予測誤差、HOTA / IDF1はtracking全体性能なので、best epochは一致しない可能性がある。
- MambaStatefulは固定LRとstate carry固有の誤差蓄積を含むため、sliding window型と異なる推移になる可能性がある。

## 実験・実装内容

### canonical YAML変更

対象:

- /mnt/HDD10TB-2/aburatani/2025_09_aburatani_Mamba_Trackers/ssm_tracker/cfgs/MambaTrack.yaml
- /mnt/HDD10TB-2/aburatani/2025_09_aburatani_Mamba_Trackers/ssm_tracker/cfgs/TrackSSM.yaml
- /mnt/HDD10TB-2/aburatani/2025_09_aburatani_Mamba_Trackers/ssm_tracker/cfgs/MambaStateful.yaml

設定:

- epochs: 100
- val_loss_period: 5
- mot_metrics_period: 10

変更しないもの:

- MambaStateful.yamlのlr_scheduler: none
- optimizer、モデル構造、trackerアルゴリズム、TrackEval metric
- Python実装
- checkpoint選択ロジック
- timing_enabledの通常運用での有効化

### full validation

- epoch 10, 20, ..., 100でfull valのmot_metricsを実行する。
- 各観測点でHOTA、IDF1、および既存のDetA、AssA、MOTAを保存する。
- 相関分析には、mot_metricsと共通する10epochのval lossを使用する。
- full valの初回実測時間と、全10回の累積時間をモデルごとに記録する。

### 相関分析

モデルごとに次を実施し、モデルを跨いだpooled correlationは主結果にしない。

- epoch、val loss、HOTA、IDF1の10行対応表
- val loss対HOTAのPearson相関
- val loss対IDF1のPearson相関
- val loss対HOTAのSpearman順位相関
- val loss対IDF1のSpearman順位相関
- val loss最小epochとHOTA最大epoch・IDF1最大epochの一致

同率bestがある場合は最小epochを代表値とし、同率候補も併記する。欠測値は補間せず、観測数と理由を記録する。

## 使用データ・モデル

- データセット: DanceTrack
- 評価範囲: full official validation
- モデル: MambaTrack、TrackSSM、MambaStateful
- 学習epoch: 100
- val loss観測周期: 5epoch
- mot_metrics観測周期: 10epoch
- 相関分析対象epoch: 10, 20, ..., 100

実行時にmodel、config、seed、device、データ範囲、git commitを記録する。

## 比較対象・ベースライン

- 時間baseline: 3sequenceでtracker推論約316.973秒、TrackEval約3.490秒
- 周期baseline: 従来のval loss毎epoch、mot_metrics 5epoch周期
- 本実験設定: val loss 5epoch周期、mot_metrics 10epoch周期
- checkpoint比較: best_val_loss、best_tracking_hota、best IDF1 epoch、epoch 100

## 評価指標

- val loss
- HOTA
- IDF1
- 補助指標: DetA、AssA、MOTA
- Pearson相関係数
- Spearman順位相関係数
- best epoch一致
- 観測数
- full val実行時間

val lossは小さいほど良く、HOTA / IDF1は大きいほど良いため、性能が対応する場合の相関符号は負を期待する。

## 成功・失敗の判断基準

成功:

- 3モデルのcanonical YAMLが100epoch・val loss 5・mot_metrics 10に設定される。
- MambaStatefulのlr_schedulerが変更されていない。
- 各モデルでepoch 10〜100のfull val 10点が揃う。
- モデルごとの対応表、推移、Pearson、Spearman、best epoch一致を保存できる。
- 10点という制約を明示し、探索的結論として解釈できる。

失敗または要再実行:

- canonical YAMLが読み込めない、または周期が期待どおり動かない。
- full val結果とepochの対応が追跡できない。
- metric欠測・実行失敗により10点が揃わず、欠測理由も特定できない。
- 異なるデータ範囲や設定の結果が混在する。

相関係数の大きさや統計的有意性には事前の成功閾値を置かない。相関が弱い、またはbest epochが不一致でも、val lossがtracking性能の代替にならないという有効な探索結果として扱う。

## 検証方法

YAML変更直後:

- git diffで対象3ファイル以外が変わっていないことを確認する。
- git diff --checkを実行する。
- 3つの設定を読み込み、epochs、val_loss_period、mot_metrics_periodを確認する。
- MambaStatefulのlr_schedulerがnoneのままであることを確認する。
- 既存の周期判定smoke結果と矛盾しないことを確認する。

本実験後:

- 各モデルの10epoch分のval loss、HOTA、IDF1がepochで一意に対応することを確認する。
- 相関計算に用いた観測数を記録する。
- 対応表からbest epochを独立に再計算し、集計結果と一致することを確認する。

## 実施手順

1. Implementation Gateを確認する。
2. 外部リポジトリのgit状態、commit、対象YAMLの現値を記録する。
3. 対象3 YAMLをepochs 100、val_loss_period 5、mot_metrics_period 10へ変更する。
4. YAML設定、diff、scheduler据え置きを検証する。
5. MambaTrack、TrackSSM、MambaStatefulを100epoch学習する。
6. epoch 10, 20, ..., 100のfull val結果をモデルごとに保存する。
7. 10点の対応表、推移、Pearson、Spearman、best epoch一致を算出する。
8. 実験条件、時間、結果、探索的解釈をexperiments配下へ保存する。

## 期待される結果

- val lossとHOTA / IDF1が対応するモデルでは負の相関が見える。
- PearsonとSpearmanの差から、線形関係か単調関係かの手掛かりが得られる。
- best epoch一致から、val loss checkpointをtracking性能選択に使えるか判断する材料が得られる。
- モデルごとの差から、state carry固有の不安定性を次の研究仮説へ接続できる。

## リスク・懸念

- 10点のみなので、相関係数は外れ値や局所的な学習変動の影響を受けやすい。
- full val 10回のtracker推論コストが大きい。3sequence時間から単純外挿せず、初回full valで実測する。
- MambaStatefulは固定LRのままなので、過学習が見えてもscheduler変更の効果は今回判断できない。
- モデルごとのoptimizerや入力表現が異なるため、相関係数のモデル間差を単一要因へ帰属しない。
- 学習中断やmetric欠測が発生した場合、補間によって10点を擬似的に埋めない。

## 未決事項

- 100epoch学習の実行順序と使用GPUは、実行開始時の空き状況を記録して決める。
- 結果保存用experimentsファイル名は、実験開始日を使って決める。
- scheduler見直しは今回の結果確認後に別brainstorm/specとして扱う。

## 関連brainstorm

- [2026-07-15-full-validation-correlation-analysis.md](../../../../secretary/notes/brainstorm/2026-07-15-full-validation-correlation-analysis.md)

## 関連spec・実験

- [2026-07-15-validation-profiling-execution-spec.md](2026-07-15-validation-profiling-execution-spec.md)
- [2026-07-15-validation-timing-implementation-smoke.md](../experiments/2026-07-15-validation-timing-implementation-smoke.md)
