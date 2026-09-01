---
date: 2026-07-23
project: sam2-mamba-motion-tracking
source: P1 association separation 25-sequence validation
status: implemented
tags: [spec, p2, state-carry, cache-update, freeze, reset, tracking]
---

# P2 cache update control Spec

## ステータスと実装制限

本specは2026-07-23にユーザー承認を受け、P2a〜P2cの実装・診断実験まで完了した。作成時点ではdraftだったため、承認後に確定した実装上の補足と結果は末尾の実験ログに記録する。

P2はP1のA2（last accepted observation association）を固定referenceとして扱う。P3の入力分布混合、P4のteacher forcing/TBPTT、MambaTrack/TrackSSMの変更、SAM2/SAMURAI統合は本specの対象外とする。

## 背景

P1では、同一epoch100 checkpoint、detector、config、scale、lifecycle、state/cache更新、TrackEval条件を固定し、prediction-primary associationとlast accepted observation associationを比較した。25系列でA2はA1に対してHOTA +0.677、AssA +0.936、IDF1 +1.429、IDSW -192となった。

一方、A2でもmissing時の`missing_mode=self_update`は維持されている。detectorが無いフレームで予測bboxを`memo_bank`へ追加し、Mambaのstate/cacheを進めるため、モデル自身の誤差を次のstate入力として再利用する可能性が残っている。

したがってP1はassociation経路の退化を切り分けたが、hidden state/cache contaminationの抑制効果はまだ未検証である。

## 目的

last accepted observation associationを固定した状態で、missing時にMambaのstate/cacheを更新するか凍結するかを比較し、self-updateがtracking退化とstate driftに寄与しているかを診断する。

## 検証したい問い

P1 A2のassociation条件下で、missing時のself-updateをfreezeへ変更すると、state/cache contaminationが抑制され、AssA・IDF1・IDSW・HOTAが改善または安定するか。

## 仮説

### H1: missing時self-updateがstate driftを増幅する

missing時の予測bboxをhistory/cacheへ入力し続けると、予測誤差が次の予測へ累積し、長いmissing区間や再association後のID associationを悪化させる。missing時のfreezeにより、少なくともstate/cacheへの誤入力は止められる。

### H2: freezeには長期occlusion時の副作用がある

freezeはstateを古い観測時点に保持するため、対象が大きく移動した長期missing区間では再associationを弱める可能性がある。したがってaggregate metricsだけでなく、missing長別の再associationとsequence別結果を記録する。

### 代替仮説

- 退化の主因はcache更新ではなく、detectorとの誤associationそのものである。
- freezeはstate driftを抑えても、通常時の予測性能を活かせず、HOTAを改善しない。
- 改善は特定sequenceの分布に依存し、25系列全体では再現しない。

## P2の段階構成

P2は一度に複数の制御を入れず、以下の順で扱う。

### P2a: missing update control（初期対象）

missing時の`self_update`と`freeze`だけを比較する。accepted detector match時の更新、association方式、track lifecycleは変更しない。

### P2b: low-quality match gate（後続候補）

低IoU・低confidenceなどのuntrusted detector matchをhistory/cacheへ更新しない条件を検討する。P2aの結果を確認した後、quality定義とthresholdを別途固定する。P2aと同時には実装しない。

### P2c: prolonged-untrusted reset（後続候補）

freeze後も長期間再associationできないtrackに対するstate resetを検討する。reset発火長、reset対象、track ID lifecycleへの影響を別途定義し、P2a/P2bの結果なしに実装しない。

## 比較条件

### 初期比較: P2a

| 条件 | association | missing時 | accepted detector match時 | 位置づけ |
| --- | --- | --- | --- | --- |
| B0 | last accepted observation | `self_update` | 現行どおりstate/cache更新 | P1 A2 reference / control |
| B1 | last accepted observation | `freeze` | 現行どおりstate/cache更新 | P2a treatment |

P2aでは、`predict()`による予測bbox生成とtracking outputは維持する。ただしmissing時の`update(None)`では、B1は以下を行わない。

- `memo_bank`への予測bbox追加
- Mamba inference cacheのadvance
- `pending_delta`の更新
- missing予測を次時刻のstate入力として扱うこと

trackの`mark_lost`、`max_time_lost`、reactivation、track ID lifecycleは変更しない。freezeはstate/cache/historyだけを対象とする。

### 後続比較候補（実装・検証済み）

| 条件 | association | missing時 | match quality gate | reset |
| --- | --- | --- | --- | --- |
| B2 | observation | freeze | trusted matchのみ更新 | なし |
| B3 | observation | freeze | trusted matchのみ更新 | 連続untrusted後にreset |

B2/B3はユーザーの「P2すべての外部repo実装を開始してよい」という明示承認後に実装・検証した。

### 実装上の確定事項

- trusted matchは、association IoU `>= 0.5` かつ detector score `>= 0.6` とした。
- B3のresetは、trustedでないdetector matchが5回連続した場合に発火する。missing freezeはuntrusted detector matchには数えない。
- untrusted detector matchでも、tracking outputには対応するdetector bboxを使い、state/history/cacheだけを更新しない。これによりP2のcache update controlと出力bboxの変更を分離した。
- B3 resetはtrusted historyからstate/cacheを再構築し、track ID/lifecycleは維持する。

## 固定条件

- checkpoint: `ssm_tracker/saved_ckpts/mamba_stateful_dancetrack/epoch100.pth`
- config: `ssm_tracker/cfgs/MambaStateful.yaml`を基準とし、P2 modeだけを変更する
- detector入力: `det_results/dancetrack/val/`
- sequence: P1正式評価と同じDanceTrack val 25系列
- scale: `scale_factor_bbox=1`, `scale_factor_delta=50`
- association: last accepted observation（P1 A2）
- track lifecycle: `filter_thresh=0.2`、`new_track_thresh=0.6`、`max_time_lost=30`、その他P1と同一
- TrackEval: HOTA/CLEAR/Identity、`DO_PREPROC=False`、同一GT、同一sequence指定
- device: P1と同一条件を記録する
- P1/P2以外のmodel、training、detector、input distribution、TrackEval実装は変更しない

TrackEvalは既存val seqmapが3系列に限定されているため、25系列評価ではP1と同じく`SEQ_INFO`で25系列を明示する。

## 実装変更範囲（承認後の候補）

P2aの実装開始時に、次の範囲だけを対象とする。

- `ssm_tracker/track_utils/stateful_tracklet.py`: missing時のhistory/state/cache更新規則
- `ssm_tracker/track_stateful.py`: P2 modeのCLI・manifest記録（必要な場合）
- `ssm_tracker/cfgs/MambaStateful.yaml`またはP2専用config: B0/B1の明示設定（既存configを上書きしない）
- P2 run script: 新規run_id、25系列指定、artifact path
- 必要最小限のdiagnostic logging: update/freeze回数、missing長、state/cacheの有限性

変更しないもの:

- `MambaTrack` / `TrackSSM`のコード
- `stateful_tracker.py`のassociation位置とassignment threshold
- track lifecycleとID生成規則
- checkpoint、detector output、既存track output、既存TrackEval output
- P3/P4のdataset・training forward・TBPTT

## 検証手順

1. 実装前にP1 artifactのmanifest、commit、dirty diff、25系列runをreferenceとして固定する。
2. P2a実装後、targeted testで以下を確認する。
   - B0はP1 A2と同じassociation modeを使う。
   - B1のmissing frameで`memo_bank`、cache offset、pending stateが進まない。
   - accepted detector matchではB0/B1ともstate/cacheが更新される。
   - freezeしてもtrack lifecycleと出力ディレクトリ規則が変わらない。
   - state norm、cache offset、tracking outputにNaN/Infがない。
3. 3系列でB0/B1のsmokeを実施し、run provenanceとoutput非上書きを確認する。
4. 25系列でB0/B1を新規run_idへ実行する。P2実装後のB0 controlも新規runで再実行し、P1 A2との挙動差を確認する。
5. 同一TrackEval条件で評価し、aggregateとsequence別の結果を比較する。
6. missing区間長別に、state update/freeze回数、再association成功、IDSW、state normを集計する。
7. 結果を`experiments/`へ記録し、B2/B3へ進むかを別途判断する。

## 評価指標

### Primary

- HOTA
- AssA
- IDF1
- ID switches（IDSW）

### Secondary

- DetA、MOTA
- track数、IDs、fragmentation
- sequence別metrics
- missing区間長別の再association率

### State/cache diagnostics

- accepted detector update回数
- missing self-update回数 / freeze回数
- 連続missing長の分布
- state/cache update時のfinite率
- state normまたはcache offsetの推移
- reactivation後のID維持率
- resetはP2aでは0回であること

## 成功・失敗の判断基準

### P2aの成功

B1がB0に対して、AssAまたはIDF1を改善し、IDSWを減らす傾向を示すこと。HOTAがB0を大きく下回らず、state/cacheのdriftまたは非有限値が悪化しないこと。改善が一部sequenceに依存する場合は、missing長・sequence特性と併記する。

### P2aの保留・失敗

- B1がaggregateで改善しない。
- HOTAまたはIDF1が明確に悪化し、long-miss後の再association低下で説明できる。
- B0 controlがP1 A2を再現せず、P2比較の前提が崩れる。
- state/cacheのfreeze以外の変更が混入する。
- NaN/Inf、既存outputの上書き、TrackEval条件不一致が発生する。

P2aが失敗しても、直ちにB2/B3やP4へ進まない。まずmissing区間・association quality・state診断を確認する。

## B2/B3へ進む条件

- B1が改善するが、低品質なaccepted detector match後にstate driftまたはID switchが残る場合、B2のquality gateを計画する。
- B1が改善するが、長期missing後の再associationだけが悪化する場合、B3のreset候補を計画する。
- B1が改善しない場合、B2/B3は自動実装せず、P2仮説を再評価する。

## 成果物とprovenance

各runは既存成果物と別のrun_id付き新規directoryへ保存する。

- command
- checkpoint pathとhash
- configのコピー
- detector path
- association mode
- missing/cache update mode
- sequence list
- TrackEval設定
- repo commitとdirty diff
- manifest.json
- tracking output
- TrackEval summary/detailed output
- diagnostics summary

## 未決事項

- P2aで既存`missing_mode=freeze`をそのまま利用できるか、P2用modeとして明示するか。
- freeze時に保持する対象を`memo_bank`、InferenceParams cache、`pending_delta`の3つすべてとするか。
- B2のtrusted match定義（association IoU、detector score、first/second-stage match）とthreshold。
- B3のreset発火条件、候補連続missing長、reset後のstate再構築方法。
- 25系列結果のsequence依存性を、P2の主評価にどの程度組み込むか。

## Implementation Gate

- [x] P2の問い・仮説・P2a/B2/B3の段階構成を定義
- [x] P1 reference、固定条件、評価指標、成果物規則を定義
- [x] 外部repoを変更しないdraftとして保存
- [x] ユーザーによるP2a spec確認・承認
- [x] P2aの外部repo変更範囲の最終確定
- [x] P2aの検証方法とrun_idの承認
- [x] ユーザーによるP2実装開始承認
- [x] P2a〜P2cの実装・3系列smoke・25系列評価

## 関連ファイル

- `experiments/2026-07-23-p1-association-separation-25seq.md`
- `experiments/2026-07-22-p1-association-separation-diagnostic.md`
- `specs/2026-07-22-p1-association-separation-spec.md`
- `experiments/2026-07-23-p2-cache-update-control.md`
- `specs/2026-07-21-state-carry-improvement-spec-candidate.md`
