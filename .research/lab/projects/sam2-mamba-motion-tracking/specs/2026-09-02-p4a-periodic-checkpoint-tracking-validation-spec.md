---
date: 2026-09-02
project: sam2-mamba-motion-tracking
source: ../secretary/notes/brainstorm/2026-09-02-p4a-periodic-hota-validation.md
status: approved
tags: [spec, p4a, p4b, checkpoint, tracking-validation, hota, trackeval]
---

# P4a学習中の周期的checkpoint tracking validation Spec

## ステータス

既存のP4b固定条件tracking評価specに対する追補spec。P4aの学習中に、L0と同じ運用で一定epochごとのcheckpointをtracking pipelineへ投入し、HOTA等を記録する。

本specはP4aの学習方法、Mamba内部architecture、入力分布、P3、SAM2本体を変更しない。P4a predictor単体のtrain/validation/free rolloutと、P4b tracking評価の境界は維持する。

## 背景

L0の`train_stateful.py`では、`mot_metrics_period`に従ってepoch checkpointを保存し、既存の`run_mot_metrics`を用いてtracker推論とTrackEvalを実行している。L0設定では10epochごとにHOTA等をCometへ記録する。

一方、P4aの`train_mamba_stateful.py`はtrain loss、GT-only validation loss、free rollout、checkpoint保存までを実行するが、学習中のtracking validationを起動しない。そのため、P4aを100epoch実行してもlossは得られるが、途中epochのHOTA等は自動的には残らない。

P4aについてもL0と同じ粒度で途中checkpointを評価することで、学習の進行に伴うpredictor指標とtracking性能の関係を確認する。

## 目的

1. P4aのepoch10, 20, ..., 100 checkpointを、L0と同じtracking条件で評価する。
2. train/validation/free rolloutとHOTA等を同じ学習runへ追跡可能な形で保存する。
3. epoch100のL0/P4a固定比較を主結果として維持し、途中epochのtracking結果は学習過程の補助分析として扱う。

## 検証する問い

P4aのstateful unroll + TBPTT学習では、epochの進行に伴ってtracking性能がどのように変化するか。また、predictor単体のloss/free rollout改善がHOTA、AssA、IDF1、IDSWの改善と対応するか。

## 仮説

P4aは推論時のstate carryに近い条件で学習するため、学習が進むと長期free rolloutの安定性が改善し、trackingではAssA・IDF1の改善またはIDSWの減少が現れる可能性がある。ただし、predictor単体の改善がassociation、cache update、track lifecycleとの相互作用でHOTAに反映されない可能性もある。

## 固定する評価条件

L0/P4aの差分は学習checkpointだけとする。次の条件は評価runの途中で変更しない。

- detector入力と検出ファイル
- score threshold
- dataset splitと評価sequence
- association方式とmatching threshold
- accepted observationの扱い
- cache update、missing freeze、trusted gate、reset規則
- track開始・終了、lifecycle、track ID管理
- bbox scaleとdelta scale
- SAM2/SAMURAI統合条件
- TrackEvalのdataset、split、metrics、preprocessing、parallel設定

P4bで採用するP2-B1固定条件を使用する。P3の入力分布混合や新しいassociation/cache探索は行わない。

## 実装方針

### P4a training entrypoint

`ssm_tracker/train_mamba_stateful.py`へ、L0と同じtracking validation起動処理を追加する。

- `should_run_mot_metrics`で周期を判定する。
- tracking validation対象epochでは、推論前に`epoch{epoch}.pth`を保存する。
- 保存したcheckpointを`run_mot_metrics`へ渡し、既存のstateful tracker推論とTrackEvalを起動する。
- 結果をCometへ次の名前で記録する。
  - `mot_metrics/HOTA`
  - `mot_metrics/DetA`
  - `mot_metrics/AssA`
  - `mot_metrics/MOTA`
  - `mot_metrics/IDF1`
  - `mot_metrics/IDSW`（TrackEval summaryから取得できる場合）
- 同じepochのローカル`p4a_metrics_epoch{epoch}.json`にもtracking指標を保存する。
- HOTAが最高のcheckpointは`best_tracking_hota.pth`として保存する。ただし、研究上の主比較checkpointはepoch100固定とし、best HOTAは補助結果として扱う。

tracking validationはP4a predictor validation lossの代替ではなく、学習entrypointから外部tracking評価を起動するP4b評価である。

### P4a configuration

`ssm_tracker/cfgs/MambaStatefulTBPTT.yaml`へ、L0と同等の設定を追加する。

```yaml
validation:
  enabled: true
  val_loss_period: 5
  free_rollout_period: 5
  mot_metrics_period: 10
  det_path: 'det_results/dancetrack/val'
  trackeval_repo: '/mnt/HDD10TB-2/aburatani/TrackEval'
  trackeval_gt_folder: '/mnt/HDD10TB-2/aburatani/TrackEval/data/gt/dancetrack/val'
  trackeval_trackers_folder: '/mnt/HDD10TB-2/aburatani/TrackEval/data/trackers/dancetrack/val'
  trackeval_benchmark: 'dancetrack'
  trackeval_split: 'val'
  trackeval_tracker_name: 'mamba_stateful_tbptt'
  trackeval_metrics: ['HOTA', 'CLEAR', 'Identity']
  trackeval_do_preproc: false
  trackeval_use_parallel: false
  trackeval_output_sub_folder: ''
```

実際のdetector、GT、TrackEvalパスは環境上の既存L0設定と一致させる。パスが存在しない場合にloss-onlyで黙って完走しないよう、tracking validationを有効化したrunでは開始前または最初の対象epoch前に必要パスを検査する。

### Provenance

各tracking評価について、次をローカルartifactから追跡できるようにする。

- 学習`run_id`
- checkpointの絶対パス、epoch、SHA256
- P4a/L0の区別
- 評価sequence、split、detector、association、cache、lifecycle、TrackEval設定
- tracker推論・TrackEvalの実行コマンド
- repo commit、branch、dirty diff
- `parent_training_run_id`

既存の`run_mot_metrics`、`track_stateful.py`、checkpoint manifestの仕組みを優先して再利用する。不要な共通基盤の作り直しは行わない。

## 評価頻度と比較規則

- P4a training: epoch1〜100
- predictor validation/free rollout: 既存設定どおり5epochごと
- tracking validation: 10epochごと（epoch10, 20, ..., 100）
- 主比較: L0 epoch100 vs P4a epoch100
- 補助比較: epochごとのHOTA等の推移、best HOTA checkpoint

best HOTAの選択をepoch100比較へ後付けで適用しない。epoch100固定比較とbest HOTA比較は別行・別結果として保存する。

## 評価指標

### predictor単体

- train current/running mean/epoch mean loss
- GT-only validation loss
- free rollout horizon別IoU、MAEまたはSmooth L1
- rollout発散率、NaN/Inf率
- state max absolute value、gradient finite率

### tracking

- HOTA
- DetA
- AssA
- MOTA
- IDF1
- IDSW
- 必要に応じてruntime、fragmentation、track数

HOTA等はtracking validationの指標であり、P4a predictor単体のvalidation lossと同一の性能指標として混同しない。

## 実施手順

1. P4a configへ`mot_metrics_period: 10`と既存L0相当のtracking設定を追加する。
2. P4a training entrypointから既存tracking評価adapterを呼び出す。
3. 1epochまたは小規模データでcheckpoint保存、tracker読み込み、TrackEval summary、Comet/local artifactを確認する。
4. epoch10の実データ評価で、HOTA等がlossと同じrunへ記録されることを確認する。
5. 100epoch実行ではepoch10〜100のtracking結果を保存する。
6. L0 epoch100とP4a epoch100を同一条件で比較する。
7. 途中epochの曲線とpredictor単体指標を対応づけ、epoch100主結果と補助結果を分けて解釈する。

## 成功基準

- P4aの10epochごとのcheckpointでtracker推論が実行される。
- TrackEvalのHOTA等がCometとローカルartifactへ保存される。
- P4a training loss、predictor validation、free rollout、tracking metricsがepochとrun IDで対応づく。
- L0/P4aのtracking条件が一致し、checkpoint以外の差分を説明できる。
- epoch100固定比較が再現可能である。
- checkpoint読み込み失敗、fallback、NaN/Inf、評価条件不一致がない。

## 失敗・差し戻し条件

- tracking validationが設定されているのにHOTA等が出力されず、loss-onlyで完走する。
- P4a checkpointではなく別checkpointまたはfallbackが推論に使われる。
- tracker推論またはTrackEvalが失敗する。
- L0/P4aでdetector、association、cache、lifecycle、TrackEval条件が一致しない。
- HOTA差をpredictorの差として解釈できない追加変更が混入する。

この場合は100epoch結果を主比較へ採用せず、provenance、設定、checkpointロード、評価adapterの順に切り分ける。

## 実行時間に関する注意

tracking validationはpredictor validationより大幅に重い。10epochごとにfull validationを実行すると、100epoch本学習の実行時間と保存容量が増加する。そのため、実行前にruntimeを記録し、必要に応じてsmokeでは小規模sequence、正式比較では固定したfull validationを使い分ける。

正式比較の評価sequenceを途中で変更してはならない。

## 対象外

- P3の実装・評価
- 新しいassociation、cache update、track lifecycleの探索
- SAM2/SAMURAI本体やdecoderの変更
- Mamba内部architecture、optimizer、lossの変更
- LSTM・Transformer比較
- tracking結果を根拠にした評価条件の途中変更
- push、外部repoへの不要な変更

## 変更対象

- `ssm_tracker/train_mamba_stateful.py`
- `ssm_tracker/cfgs/MambaStatefulTBPTT.yaml`
- 必要最小限のtracking metric/provenance adapter
- P4a tracking validation用のtestまたはsmoke runner

## 想定成果物

- epoch10〜100のP4a checkpoint
- 各対象epochのtracking推論結果とTrackEval summary
- `mot_metrics/*`のComet時系列
- `p4a_metrics_epoch*.json`内のtracking指標
- checkpoint manifest、evaluation manifest、git diff
- L0/P4a epoch100比較表

## Implementation Gate

- [x] 既存P4b固定条件specとの境界を確認
- [x] 周期、比較対象、固定条件、評価指標を定義
- [x] 変更対象と検証方法を定義
- [x] ユーザーによるspec作成承認（2026-09-02）
- [ ] 外部実装リポジトリの変更開始承認

## 関連ファイル

- `specs/2026-09-02-p4b-checkpoint-tracking-evaluation-spec.md`
- `../secretary/notes/brainstorm/2026-09-02-p4a-periodic-hota-validation.md`
- `../secretary/notes/brainstorm/2026-09-02-p4a-metric-parity.md`
- `meetings/2026-08-28-mtg.md`
