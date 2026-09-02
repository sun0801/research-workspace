---
date: 2026-09-02
project: sam2-mamba-motion-tracking
source_todo: null
topic: P4aとL0の学習・評価logging粒度を揃える方針
status: exploratory
tags: [brainstorm, research, p4a, validation, comet, metrics]
---

# P4aとL0の学習・評価logging粒度を揃える方針

## 読み込んだ文脈

- P4aはstateful unroll + TBPTTによるMamba予測器学習として実装済み。
- P4aの現行Comet loggingは`train/epoch_mean_loss`と`train/state_norm`のみ。
- L0はtrain loss、val loss、10 epochごとのHOTA/TrackEvalを記録する。
- P4a specではdetector、association、TrackEvalはP4bへ分離している。
- 2026-08-28 MTGではstate carry学習の適切な評価、SAM2 decoder統合、比較実験を優先する方針だった。

## 相談の出発点

P4aでもL0と同じ粒度の情報を残し、Comet上で学習曲線・validation・評価結果を比較可能にしたい。

## 問い

P4aへL0相当のlogging・validation・HOTA評価を追加する場合、既存P4a specへ追記するか、別specとして切り出すべきか。

## 候補

1. 既存P4a specへ全て追記する
   - 実装箇所はまとまりやすい。
   - ただし、stateful学習の成立条件と、比較用の評価運用が混ざる。

2. P4a metric parity specを新設する
   - train/val logging、provenance、比較条件を独立して固定できる。
   - P4a学習実装の再変更と誤解されにくい。

3. train/val loggingとHOTAを分離する
   - train loss・val lossはP4a predictor単体の評価としてP4a側へ追加する。
   - HOTAはdetector・association・cache・TrackEvalを固定したP4b評価runnerで取得する。
   - P4aの「TrackEvalを使用しない」という境界を守れる。

## 有力な方向性

新しい小規模specを作り、候補3を採用する。

### P4a側で揃えるもの

- batch単位の`train/current_loss`と`train/mean_loss`
- epoch単位の`train/epoch_mean_loss`とlearning rate
- 5 epochごとのGT-only predictor validation loss
- epoch、run_id、config、split、seed、checkpointとの対応
- `state_max_abs`などの診断値は補助metricとして明示する

### P4b側へ残すもの

- HOTA、DetA、AssA、MOTA、IDF1、IDSW
- detector、association、cache update、track lifecycle、TrackEval条件
- P4a checkpointを差し替えるだけの評価runner

## 仮説

P4aとL0でtrain/val lossの記録粒度を揃えると、Comet上で学習の収束・過学習・長期state安定性を比較しやすくなる。一方、HOTAをP4a学習スクリプトへ直接混ぜると、学習方式の比較とtracker条件の比較が再び混ざる。

## 成功基準候補

- P4aのCometにL0と同名・同頻度のtrain/val lossが残る。
- P4a validationはGT-only、state reset、mask処理を明示してfiniteになる。
- P4a checkpointのprovenanceから、どのepochのloss・checkpoint・configか追跡できる。
- HOTAはP4a学習の副作用ではなく、固定条件のP4b評価として再現できる。

## 未解決の問い

- P4a validationのunroll長とloss maskをtrainと同じ48 stepにするか。
- Comet上でHOTAを同じExperimentへ追加するか、評価runを別Experimentにするか。
- P4aのval lossを5 epochごと、HOTAを10 epochごとにする必要が本当にあるか。
- `state_norm`を`state_max_abs`へ改名するか。

## 次アクション候補

- [ ] P4a metric parity specを作成し、train/val loggingとP4b HOTA評価の境界を固定する。
- [ ] 承認後、P4a train/val loggingを実装する。
- [ ] P4a checkpoint用の固定条件HOTA evaluation runnerを別途作成する。

## Spec化候補

`2026-09-02-p4a-metric-parity-spec.md`として、P4a train/val loggingとP4b checkpoint evaluationの運用を独立spec化する。

## 関連ファイル

- `.research/lab/projects/sam2-mamba-motion-tracking/specs/2026-09-01-p4a-stateful-unroll-tbptt-spec.md`
- `.research/lab/projects/sam2-mamba-motion-tracking/README.md`
- `.research/lab/projects/sam2-mamba-motion-tracking/meetings/2026-08-28-mtg.md`
- `.research/secretary/notes/brainstorm/2026-09-01-p1-p2-and-training-direction.md`
