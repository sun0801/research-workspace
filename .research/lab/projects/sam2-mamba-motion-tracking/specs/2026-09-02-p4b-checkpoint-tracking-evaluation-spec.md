---
date: 2026-09-02
project: sam2-mamba-motion-tracking
source: ../secretary/notes/brainstorm/2026-09-02-p4a-metric-parity.md
status: draft
tags: [spec, p4b, checkpoint-evaluation, tracking, trackeval, state-carry]
---

# P4b: Stateful checkpointの固定条件tracking評価 Spec

## ステータス

P4aで学習したstateful Mamba checkpointを、既存のtracking pipelineへ差し替えて評価するための個別spec。

P4aの学習方法・Mamba内部state更新・P3の入力分布混合は本specでは変更しない。P4aのpredictor単体評価を先に完了させ、その後にP4bのtracking評価を行う。

本specは計画段階であり、外部実装リポジトリの変更はまだ開始しない。

## 背景

P4aでは、GT-only入力に対するstateful unroll + TBPTT学習を実装した。実Mamba・CUDA上のsmoke、checkpoint再読み込み、legacy/stateful forward parity、finite性は確認済みである。

一方、現時点ではP4aのComet loggingがL0と同じ粒度ではなく、GT-only validation lossとfree rolloutの比較も完了していない。また、P4aの学習ループへHOTAを直接混ぜると、predictorの学習方法とtracker側の条件が再び混ざる。

そこで、P4aの成立確認とP4bのtracking評価を段階的に分離する。

## 目的

1. P4aをL0と比較可能なpredictor実験として完了させる。
2. P4a checkpointを、detector・association・cache update・track lifecycle・TrackEval条件を固定したtracking pipelineへ投入する。
3. L0 checkpointとP4a checkpointの差を、学習方法の差として解釈可能な形でHOTA等により比較する。

## 検証したい問い

P4aのstateful unroll + TBPTTで学習したMamba checkpointは、L0のfixed-window学習checkpointと比べて、同じtracking条件下でMOT性能およびstate carry時の安定性を改善するか。

## 仮説

P4a checkpointは、推論時のstate carryに近い時系列条件で学習されるため、L0 checkpointよりも長期的な予測誤差の蓄積やstate不安定性が小さくなり、trackingのAssA・IDF1・IDSWに改善が現れる可能性がある。

ただし、P4aのpredictor性能が改善しても、associationやcache updateとの相互作用によってHOTAが改善しない可能性がある。その場合も、predictor単体とtracking全体の差を切り分けられれば有効な結果とする。

## フェーズ構成

### Phase A: P4a closeout

P4bのtracking評価を開始する前に、P4aを次の条件で完了確認する。

- L0と同名・同頻度のtrain lossをCometへ記録する
  - `train/current_loss`
  - `train/mean_loss`
  - `train/epoch_mean_loss`
  - learning rate
- P4aのGT-only validation lossを記録する
  - `val_loss/epoch_mean`
  - trainと同じbbox形式、scale、unroll/mask規則を使用
  - validationではstateをtrack/sampleごとにresetする
- predictor単体のfree rolloutを評価する
  - horizon: `1, 4, 8, 16, 32`
  - IoU、MAEまたはSmooth L1
  - NaN/Inf率、発散率
- stateおよびgradientの有限性を確認する
- L0/P4aのconfig、seed、split、checkpoint、Git dirty diffを対応づける

`state_norm`または`state_max_abs`は診断用の補助指標として残すが、lossやtracking指標と同列の性能指標として解釈しない。

### Phase B: P4b checkpoint tracking evaluation

Phase Aを通過したcheckpointについて、L0とP4aで学習checkpointだけを差し替えてtrackingを実行する。

固定する条件:

- detector入力、検出ファイル、score threshold
- dataset splitと評価sequence
- association方式とmatching threshold
- accepted observationの扱い
- cache update、missing freeze、trusted gate、reset規則
- track開始・終了、lifecycle、track IDの管理
- bbox scaleとdelta scale
- SAM2/SAMURAI統合条件
- TrackEvalのdataset、config、metrics、評価対象sequence

P1/P2のどの条件を使うかは、評価開始前に1つ選び、L0/P4aの両方へ同一条件で適用する。比較途中でassociationやcache規則を変更しない。

## 比較対象

### L0

- `train_mamba_window.py`で学習したfixed-window checkpoint
- 現行のL0 architecture、入力形式、scale、split、seedを使用
- tracker側は既存の固定条件で実行

### P4a

- `train_mamba_stateful.py`で学習したGT-only stateful unroll + TBPTT checkpoint
- P4a closeoutで選択したcheckpointを使用
- tracker側の条件はL0と完全に一致させる

必要に応じて、epoch固定比較とvalidation lossまたはpredictor free rolloutに基づくcheckpoint比較を分けて記録する。checkpoint選択規則を後付けで変更しない。

## 評価指標

### P4a predictor単体

- train loss: current、running mean、epoch mean
- validation loss: epoch mean
- teacher-forced one-step IoU、MAEまたはSmooth L1
- free rollout horizon別IoU / MAE
- rollout発散率、NaN/Inf率
- state max absolute value、gradient finite率

### P4b tracking

- HOTA
- DetA
- AssA
- IDF1
- MOTA
- IDSW
- 必要に応じてtrack数、fragmentation、runtime

HOTA等はP4a学習ループのvalidation指標ではなく、P4bの固定条件tracking評価として記録する。

## Cometとprovenance

P4aの学習ExperimentとP4bのtracking評価Experimentは分ける。P4b側には次を記録する。

- `parent_training_run_id`
- checkpointの絶対パス、hash、epoch
- L0/P4aの区別
- 評価対象sequenceとsplit
- detector、association、cache、lifecycle、SAM2、TrackEvalの設定
- 実行コマンド
- repo commitとdirty diff

これにより、P4a学習時のloss曲線と、P4bで得たHOTA等を後から一対一に追跡できるようにする。

## 実施手順

1. P4a train/validation loggingをL0と同じ粒度へ揃える。
2. P4a GT-only validation lossを実行し、finite性とcheckpoint対応を確認する。
3. P4a predictorのfree rolloutを実行し、L0との差を記録する。
4. P4a closeoutの結果を確認し、比較対象checkpointを固定する。
5. L0 checkpointを固定条件でtracking評価し、基準結果を保存する。
6. 同じ条件でP4a checkpointをtracking評価する。
7. HOTA、DetA、AssA、IDF1、MOTA、IDSWとpredictor単体指標を対応づける。
8. 結果を、predictor改善・tracking条件との相互作用・失敗要因に分けて解釈する。

## 成功・失敗の判断基準

### P4a closeoutの必須条件

- L0/P4aのtrain・validation lossを同じmetric名と粒度で比較できる。
- P4a validation loss、state、gradientがfiniteである。
- free rolloutの全horizonで結果が再現可能である。
- checkpoint、config、seed、split、run_idの対応を追跡できる。

### P4bの必須条件

- L0/P4aでdetector、association、cache、lifecycle、TrackEval条件が一致する。
- checkpoint以外の条件を変えずに再実行できる。
- HOTA等のTrackEval結果がCometとローカルartifactの両方から確認できる。
- P4a checkpointの読み込み失敗、fallback、NaN/Infがない。

### 研究上の成功候補

- P4aがL0よりfree rolloutの長期horizon誤差または発散率を改善する。
- 同じtracking条件でP4aがHOTA、AssA、IDF1を改善する、またはIDSWを減少させる。
- predictor単体の改善とtracking指標の変化を因果的に切り分けられる。

研究上の改善が得られなくても、固定条件・provenance・再現性が成立すれば、P4bの比較実験は成功とする。

## 中止・差し戻し条件

- P4aのvalidationまたはfree rolloutにNaN/Infが発生する。
- L0/P4aで入力、split、checkpoint選択規則の対応が取れない。
- tracker側の条件がrun間で一致しない。
- P4a checkpointが読み込まれず、L0 checkpointやfallbackが使われる。
- P4bのHOTA差をpredictorの差として解釈できない混入要因が残る。

この場合はP4bの結果を採用せず、P4a closeout、checkpoint provenance、tracker条件のいずれかへ戻る。

## 対象外

- P3のaccepted-detection surrogate、self predictionの導入
- P1/P2の新しいassociation・cache制御の探索
- Mamba内部architecture、optimizer、lossの研究変更
- detector、ReID、SAM2 decoder自体の改変
- LSTM・Transformerとの比較
- P4b結果を根拠にしたSAM2統合条件の追加探索

これらはP4bの固定条件を壊すため、別specで扱う。

## 想定成果物

- P4a metric parityを反映した学習ログとvalidation artifact
- P4a predictor free rolloutの結果表
- L0/P4a checkpoint provenance manifest
- 固定条件tracking evaluation runnerまたは実行script
- L0/P4aのTrackEval summary
- Comet Experimentとローカルartifactの対応表
- 結果解釈を記録したexperiment Markdown

## Implementation Gate

- [x] P4a closeoutとP4b tracking評価の境界を定義
- [x] 検証する問いと仮説を定義
- [x] 比較対象をL0/P4a checkpointに固定
- [x] detector・association・cache・lifecycle・TrackEvalを固定条件として定義
- [x] predictor単体指標とtracking指標を分離
- [x] 成功・失敗・差し戻し条件を定義
- [x] ユーザーによるspec作成承認（2026-09-02）
- [ ] 外部実装の変更対象ファイルを最終確定
- [ ] 検証runner・smoke方法を最終確定
- [ ] ユーザーによる外部実装開始承認

## 関連ファイル

- `specs/2026-09-01-p4a-stateful-unroll-tbptt-spec.md`
- `../secretary/notes/brainstorm/2026-09-02-p4a-metric-parity.md`
- `../secretary/notes/brainstorm/2026-09-01-p1-p2-and-training-direction.md`
- `meetings/2026-08-28-mtg.md`
