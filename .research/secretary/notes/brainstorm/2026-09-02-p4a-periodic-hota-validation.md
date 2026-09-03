---
date: 2026-09-02
project: sam2-mamba-motion-tracking
source_todo: null
topic: P4a学習中の周期的checkpoint tracking評価
status: exploratory
tags: [brainstorm, p4a, p4b, hota, trackeval, checkpoint]
---

# P4a学習中の周期的checkpoint tracking評価

## 相談の出発点

L0では、学習途中のcheckpointを使って一定epochごとにtracker推論とTrackEvalを実行し、HOTA等をloggingしている。P4aでも同じ運用に揃え、学習曲線とtracking性能の関係を確認したい。

## 現状確認

- L0の`train_stateful.py`は`mot_metrics_period`に従い、checkpoint保存後に`run_mot_metrics`を呼び出す。
- L0設定では`mot_metrics_period: 10`である。
- P4aの`train_mamba_stateful.py`はtrain loss、GT-only validation loss、free rolloutのみを計算する。
- P4a設定にはtracking評価用の`mot_metrics_period`、detector、TrackEval等の設定がない。
- 固定条件のL0/P4a比較runnerは別途実装済みであり、既存の`run_mot_metrics`を再利用できる可能性が高い。

## 結論候補

P4a学習中にも、L0と同じくepoch10ごとにcheckpointを保存して追跡推論・TrackEvalを実行する。ただし、HOTA等はP4a predictor validationではなく、固定条件P4b tracking評価として扱う。

## 追補specに固定する内容

- 実行周期: `mot_metrics_period: 10`
- 評価対象: P4a epoch10, 20, ..., 100 checkpoint
- 固定条件: detector、association、cache update、track lifecycle、TrackEval、split
- logging名: `mot_metrics/HOTA`, `mot_metrics/DetA`, `mot_metrics/AssA`, `mot_metrics/MOTA`, `mot_metrics/IDF1`
- provenance: 学習run ID、checkpoint epoch/hash、評価コマンド、git状態を保存
- checkpoint選択: epoch100固定比較を維持し、途中のbest HOTAは補助結果として記録する
- 失敗時: tracker推論、TrackEval、checkpoint読み込み、NaN/Infを明示的にエラーまたはskip条件として記録する

## 注意点

- full validationは1回あたり数分以上かかる可能性があるため、100epochでは合計実行時間が大きく増える。
- HOTAを学習lossのvalidation指標へ混ぜず、学習entrypointから外部tracking評価を起動する構造にする。
- 既存のP4b固定条件specに対する追補としてspec化し、承認後に外部実装を変更する。

## 次アクション候補

- [ ] 追補specを作成し、評価周期・固定条件・保存形式を承認する。
- [ ] P4a trainerへL0と同じ周期評価呼び出しを追加する。
- [ ] P4a configへtracking評価設定を追加する。
- [ ] 1周期のsmokeとepoch10相当のtracking評価を検証する。
