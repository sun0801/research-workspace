---
date: 2026-09-11
project: sam2-mamba-motion-tracking
source: ../../../../secretary/notes/brainstorm/2026-09-08-next-priority-after-0904-mtg.md
status: draft
tags: [spec, experiment, p4a, logging, diagnosis]
---

# P4a loss oscillation diagnostic Spec

## 目的

Comet上で`train/current_loss`がepochごとに振動して見える現象について、実際のbatch単位のloss変動なのか、疎なloggingによる見かけなのかを切り分ける。学習アルゴリズムやデータセットの利用方法は変更しない。本runはTBPTTやstate carryの因果性を証明するものではなく、再現するbatchと追加調査対象を特定する診断である。

## 背景

- 学習データは7,471個の48-transition chunkで、batch size 64のため1 epochは117 batch。
- 現在の`train/current_loss`は`step % 50 == 0`のときだけ記録され、1 epochあたりlocal step 0, 50, 100の3点しか観測できない。
- DataLoaderは`shuffle=False`で、毎epochのbatch順序は固定される。
- 現在の`train/state_max_abs`はepoch末に記録するepoch内最大値であり、lossと同じbatch粒度ではない。`_train_batch`が返すbatch終了時のstate normを追加ログする必要がある。
- 特定のtrajectory群の難しさとloggingの疎さが、epoch周期の振動として見えている可能性がある。

## 検証したい問い

1. lossのピークは毎epoch同じlocal batch位置に現れるか。
2. 全batchを記録すると、Comet上の周期的な振動はどのように見えるか。
3. lossのピークと同じglobal stepのbatch終了時state normが併発するか。併発したbatchを、trajectory構成・frame gap・state carry/TBPTTの追加調査候補として特定できるか。

## 仮説

- **H1: 固定batch順序の影響** — `shuffle=False`により、難しいtrajectory群が毎epoch同じ位置に現れる。難しさの候補には、bbox軌跡そのものに加え、frame gapを1-frame transitionとして扱っている可能性を含める。
- **H2: 疎なloggingの影響** — 全batchを見れば、現在のepoch周期は少なくとも一部がlogging間隔による見かけだと分かる。
- **H3: state/TBPTTの追加調査候補** — lossとbatch終了時state normが同じbatch位置で反復して跳ねても、TBPTT境界が原因とは直ちに断定しない。まず当該batchのtrajectory構成とframe gapを確認し、その後にstate carry/TBPTTのsegment単位ログへ進む。

## 実験内容

### 変更範囲

外部実装リポジトリの`ssm_tracker/train_mamba_stateful.py`にある診断loggingだけを一時的に変更する。

```python
if step % 50 == 0:
```

上記を全batchで記録する条件へ一時変更し、次の値を同じbatch/global stepで記録する。

- `train/current_loss`: 現在batchのloss
- `train/current_state_max_abs`: `_train_batch`が返す現在batch終了時のstate norm
- `train/mean_loss`: epoch内running mean
- `train/local_batch`: `step`（0始まりのlocal batch index）

既存の`train/state_max_abs`（epoch内最大値）は残す。Cometの`step`には既存のglobal step式、`epoch`にはepoch番号を使う。global step、loss計算、optimizer更新、state carry、detach、TBPTT、checkpoint処理は変更しない。

### 固定する条件

- config: `ssm_tracker/cfgs/MambaStatefulTBPTT.yaml`
- epochs: `3`
- seed: `0`
- batch size: `64`
- DataLoader: `shuffle=False`
- unroll length: `48`
- TBPTT length: `12`
- model、optimizer、learning rate、loss、gradient clipping: 現行設定のまま
- frame gap修正やdataset再生成は行わず、現状のP4a datasetをそのまま使う。
- 実行開始時に`len(dataloader)`を確認し、`117`であることを記録する。
- Comet logging: 有効

association modeとmissing modeは今回のloss振動診断の対象外とする。`prediction + self_update`は別のtracker評価条件として扱う。

### 実行例

```bash
./.mamba_trackenv/bin/python ssm_tracker/train_mamba_stateful.py \
  --exp_name p4a_loss_oscillation_diag_3ep_20260911 \
  --config_file ssm_tracker/cfgs/MambaStatefulTBPTT.yaml \
  --device 0 \
  --epochs 3
```

GPU番号やexperiment名は実行環境に合わせて変更してよいが、同一experimentとして識別できる名前を使う。

## 記録・評価項目

- 実行時の`num_train_batches = len(dataloader)`。現設定では`117`を確認する。117でなければ351点とは呼ばず、実測値を記録して原因を確認する。
- `train/current_loss`: 117 batch/epoch、合計351点が記録されること。
- `train/current_state_max_abs`: lossと同じglobal stepで合計351点が記録されること。
- `train/mean_loss`、`train/local_batch`、Cometのglobal `step`、`epoch`の対応。
- 既存の`train/state_max_abs`: epoch内最大値として3点が記録されること。
- 各epochでlossが高くなるlocal batch位置と、そのbatch終了時state norm。
- 既存Cometログのstep 0/50/100付近との対応。
- 3 epochではvalidation period 5、MOT metrics period 10に達しないため、validation/MOT評価は主目的に含めない。

### 数値化する再現性指標

各epochの117 batch loss系列を`L_e=(l_e,0,...,l_e,116)`として、次をオフラインで算出する。

- epoch pairごとのSpearman順位相関: `(epoch 1, 2)`, `(1, 3)`, `(2, 3)`。
- 各epochのloss上位10 batch集合について、pairwise top-10 overlap `|Top10_e ∩ Top10_e'| / 10`。
- これらは3 epochの記述的な診断値であり、統計的検定やTBPTT原因の証明とは扱わない。

`shuffle=False`なので、同じlocal batch位置の再現性を直接比較できる。再現したbatchは、datasetの決定的な順序から該当chunk群を特定し、trajectory構成とframe gapを追加確認する。

## 成功基準

1. 3 epochがエラーなく完了する。
2. 実行時に`len(dataloader) == 117`を確認する。異なる場合は実測batch数を優先し、351点という期待値を適用しない。
3. Comet上で`train/current_loss`と`train/current_state_max_abs`を同じglobal stepで合計351点確認できる。
4. epoch境界、global step、local batch位置を対応づけられる。
5. epoch間Spearman相関とtop-10 overlapを算出し、lossピークのbatch位置再現性を数値で説明できる。
6. 周期的なピークが固定batch位置に対応するか、疎なloggingの観測不足で説明できるかを判断できる。
7. 実行前後のdiffまたはmanifestにより、logging条件以外の設定・コードが変わっていないことを確認できる。
8. 繰り返しピークが見つかった場合、trajectory/frame gap確認を追加調査として切り出せる。

## 解釈方針

- 全batchログで周期性が弱まり、特定のlocal batch位置にピークがある場合は、固定順序とtrajectory難易度の影響を第一候補とする。frame gapが含まれていれば、その交絡も候補に含める。
- 全batchログでも同じ位置のピークが繰り返され、state normも併発する場合は、state carry/TBPTT境界を追加調査する。
- ただし、同じ位置でlossとstate normが跳ねても、batch lossは48-transition内の4つの12-transition TBPTT segmentを集約した値であるため、12-frame detach境界が原因とは断定しない。
- 全batchログで周期性自体が見えなくなった場合は、元のCometログにおける疎なsamplingが主因と判断する。
- frame gapやtrajectory構成で説明できない再現ピークだけを、次段階のstate carry/TBPTT segment-level診断候補とする。

## 対象外

- `shuffle=True`への変更
- batch sizeやデータセット分割・生成方法の変更
- model、optimizer、learning rate、unroll length、TBPTT lengthの変更
- association mode、missing modeの比較
- `prediction + self_update`によるtracker評価
- 学習アルゴリズムそのものの変更

## 実装・復元・再現性

診断用の一時patchであり、実験開始前に変更前のdiffを保存する。実行完了後はloss/stateのbatch loggingと`train/local_batch`追加を元に戻し、Comet experiment名、設定、実行コマンド、変更diffを実験記録に残す。学習コードに恒久的な変更は残さない。なお、今回のrunで得たピークは旧P4aの病理解剖用であり、frame gap確認・dataset修正後の正式モデル性能として扱わない。

## 次の段階

本spec承認後にのみ外部実装リポジトリを一時変更し、3 epochの実行を開始する。

1. 全batch loss/stateログで再現ピークを特定する。
2. 該当batchのtrajectory構成とframe gapを確認する。
3. それでも説明できない場合に限り、`tbptt_segment`、segment loss、detach前後stateを記録する追加診断specを作成する。
4. 診断終了後、frame gap修正済みdatasetでP4aを再学習する。

## 関連ファイル

- `../../../../secretary/notes/brainstorm/2026-09-08-next-priority-after-0904-mtg.md`
- `../2026-09-01-p4a-stateful-unroll-tbptt-spec.md`
- `../experiments/2026-09-04-l0-p4a-tracker-sam2-comparison.md`
