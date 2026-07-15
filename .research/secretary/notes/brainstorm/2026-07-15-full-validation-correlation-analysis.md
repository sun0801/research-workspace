---
date: 2026-07-15
project: sam2-mamba-motion-tracking
source_todo: 全モデル100epoch学習とvalidation指標の関係を確認する
topic: full-validation-correlation-analysis
status: exploratory
tags: [brainstorm, validation, correlation, mot_metrics]
---

# 100epoch full validationと相関分析

## 読み込んだ文脈

- 2026-07-09 MTGでは、val lossとtracking全体評価を分離し、tracking validationの計算時間増加要因を切り分ける方針になった。
- TrackEvalのCLI/API parityと、Mamba側のTrackEval直接呼び出しadapterは確認済みである。
- val_loss_period / mot_metrics_period の周期制御と1epoch smokeは完了している。
- MambaStatefulの3sequence計測では、tracker推論 subprocess が約316.973秒、TrackEval直接呼び出しが約3.490秒だった。今回の条件ではtracker推論が主要コストである。
- canonical YAMLの100epoch・評価周期設定、100epoch本学習、full val系列の取得は未実施である。

## 相談の出発点

25epoch設定では学習不足に見えるモデルがある。一方、full valのmot_metricsはtracker推論コストが大きい。全モデルを100epochに揃え、val lossを5epochごと、full valのmot_metricsを10epochごとに取得することで、実行コストを抑えながら学習推移とcheckpoint選択の関係を調べる。

## 対象TODO

- 全モデルを100epoch設定に揃える。
- epoch 10, 20, ..., 100 でfull valのHOTA / IDF1を取得する。
- val lossとHOTA / IDF1の関係をモデルごとに探索的に分析する。

## 問い

1. val lossが低下するepochでは、HOTA / IDF1も改善する傾向があるか。
2. val loss最小epochと、HOTA最大epoch・IDF1最大epochは一致するか。
3. この関係はMambaTrack、TrackSSM、MambaStatefulで共通か、それともモデルごとに異なるか。
4. 10点のfull val観測で、次のcheckpoint選択方針を判断できるだけの傾向が見えるか。

## アイデア候補

- mot_metricsと共通するepoch 10, 20, ..., 100だけを使い、val lossとHOTA / IDF1を対応付ける。
- 全モデルをまとめて相関分析せず、モデルごとに算出する。
- 線形関係を見るPearsonと、単調関係を見るSpearmanを併記する。
- 相関係数だけでなく、推移図、対応表、best epoch一致を併記する。
- 欠測値は補間せず、観測数と欠測理由を残す。

## 仮説候補

- val lossは低いほど良く、HOTA / IDF1は高いほど良いため、性能が対応する場合は負の相関が現れる。
- 関係が非線形でも単調であれば、PearsonよりSpearmanの絶対値が大きくなる可能性がある。
- val lossは1-step予測誤差、HOTA / IDF1はtracking全体性能を表すため、best epochは一致しない可能性がある。
- state carry型ではhidden state contaminationなどの影響があるため、MambaStatefulの相関はsliding window型と異なる可能性がある。

## 実験・実装案

### 学習・評価設定

- 全モデルのepochsは100とする。
- val_loss_periodは5とする。
- mot_metrics_periodは10とする。
- epoch 10, 20, ..., 100 の各点でfull valを実行する。
- MambaStatefulのLR schedulerは今回変更せず、固定LRの影響を含む現行条件として評価する。
- timing_enabledは通常運用では有効化しない。

### 相関分析

- モデルごとにepoch、val loss、HOTA、IDF1の10行の対応表を作る。
- val lossとHOTA、val lossとIDF1のPearson相関を算出する。
- val lossとHOTA、val lossとIDF1のSpearman順位相関を算出する。
- val loss最小epoch、HOTA最大epoch、IDF1最大epochを比較する。
- 同率bestがある場合は最小epochを代表値とし、同率であることも記録する。

## 比較・評価軸

- val loss / HOTA / IDF1のepoch推移
- Pearson相関
- Spearman順位相関
- best epochの一致・不一致
- 観測数と欠測の有無
- モデル間での傾向差
- full val 1回および全10回の実測時間

## 今回見えた方向性

時間profilingは、tracker推論が主要コストであることを確認する段階まで完了した。次はprofilingの延長ではなく、独立した100epoch full validation実験として扱う。val lossとtracking指標の関係はモデル別・10観測点の探索的分析とし、因果関係や汎用的なcheckpoint選択基準は主張しない。

## 次アクション候補

1. 独立したfull validation相関分析specを保存する。
2. Implementation Gateでspec承認、変更対象YAML、検証方法、実装開始承認を確認する。
3. Gate通過後にcanonical YAMLを変更する。
4. 100epoch本学習とfull val系列取得を実施する。
5. 相関分析を実験ログへ保存する。

## Spec化候補

- .research/lab/projects/sam2-mamba-motion-tracking/specs/2026-07-15-full-validation-correlation-analysis-spec.md

## 未解決の問い

- 10点の探索的分析なので、相関係数に事前の有意差・成功閾値は置かない。
- full valの絶対時間は3sequence計測から単純外挿せず、初回full valで実測する。
- scheduler変更は今回分離し、結果確認後の別spec候補とする。

## 関連ファイル

- .research/secretary/notes/brainstorm/2026-07-15-validation-profiling-frequency.md
- .research/lab/projects/sam2-mamba-motion-tracking/specs/2026-07-15-validation-profiling-execution-spec.md
- .research/lab/projects/sam2-mamba-motion-tracking/experiments/2026-07-15-validation-timing-implementation-smoke.md
- .research/lab/projects/sam2-mamba-motion-tracking/README.md
