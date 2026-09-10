---
date: 2026-09-11
project: sam2-mamba-motion-tracking
spec: ../specs/2026-09-11-p4a-loss-oscillation-diagnostic-spec.md
status: completed
tags: [experiment, p4a, loss, logging, diagnosis]
---

# P4a loss oscillation diagnostic

## 目的

既存P4aの`train/current_loss`に見えるepoch周期の振動が、実際のbatch位置に依存するのか、疎なComet loggingの見かけなのかを診断した。学習条件・dataset・optimizer・TBPTT設定は変更していない。

## 実行条件

- command: `ssm_tracker/train_mamba_stateful.py --exp_name p4a_loss_oscillation_diag_3ep_20260911 --config_file ssm_tracker/cfgs/MambaStatefulTBPTT.yaml --device 0 --epochs 3`
- Comet: [experiment 264bc223673c41ddb15202c2f0c0ff79](https://www.comet.com/sun0801/mamba-mot/264bc223673c41ddb15202c2f0c0ff79)
- Comet run name: `p4a_loss_oscillation_diag_3ep_20260911__20260911T044503+0900_3489e78`
- train samples: `7471`
- train batches: `117`（batch size 64、`drop_last=False`）
- epochs: `3`
- unroll length: `48`
- TBPTT length: `12`
- seed: `0`
- DataLoader: `shuffle=False`
- validation/MOT metrics: 3 epochのため未実行（period 5/10）

## 実施した一時変更

`train_mamba_stateful.py`について、以下だけを一時変更した。

- `step % 50 == 0`の条件を外し、全batchをlogging
- `train/current_state_max_abs`としてbatch終了時state normを追加
- `train/local_batch`を追加
- `num_train_batches`を起動時にlogging
- 既存HEADの285行目にあった`log_metri...pycs`というSyntaxErrorを、意図された`log_metrics`へ一時修復

model forward、loss計算、optimizer更新、state carry、detach、TBPTT、dataset、YAML設定は変更していない。SyntaxError修復を含む一時変更は実行後に元へ戻した。

## Comet記録結果

- `train/current_loss`: `351`点（117点/epoch）
- `train/current_state_max_abs`: `351`点
- `train/local_batch`: `351`点、値域0〜116
- `train/epoch_mean_loss`: `3`点
- `train/state_max_abs`: `3`点
- epoch mean loss: epoch1 `0.0736350`、epoch2 `0.0732819`、epoch3 `0.0711331`
- epoch state max: epoch1 `0.9999547`、epoch2 `1.0751431`、epoch3 `1.5560551`

## loss系列の再現性

| epoch pair | Spearman rho | top-10 peak overlap |
|---|---:|---:|
| 1 vs 2 | 0.9997 | 1.0 |
| 1 vs 3 | 0.9971 | 1.0 |
| 2 vs 3 | 0.9977 | 1.0 |

各epochのloss上位10 batchはほぼ完全に同じで、共通する上位位置は`93, 67, 72, 71, 68, 99, 98, 106, 94, 101`だった。

## lossとstate normの対応

- 全351点でのlossとbatch-end state normのSpearman rho: `0.1113`
- loss top-10とstate top-10のoverlap: epoch1 `0.1`、epoch2 `0.0`、epoch3 `0.1`
- loss最大位置は3 epochともlocal batch `93`
- state最大位置はepoch1 `109`、epoch2 `90`、epoch3 `112`

lossピークとstateピークは同じbatch位置に再現しておらず、今回の観測だけからstate/TBPTT境界をloss振動の原因とは解釈しない。

## 解釈

今回の結果は、epoch周期に見えたloss振動の主因として、`shuffle=False`で固定されたbatch順序と、batch位置ごとのtrajectory難易度を強く支持する。元のCometログでは各epoch3点しか見えていなかったが、全batchを見ると同じlocal batch位置のlossパターンがほぼ完全に再現した。

ただし、同じbatch位置の難しさがframe gapに由来するか、trajectoryの運動難易度に由来するかは未確定である。また、batch lossは48-transition内の4つの12-transition segmentを集約しているため、12-transition detach境界の影響はこのrunだけでは判定できない。

## 復元確認

- 実行前コードhash: `540cf68013c6a27b13768d90fc3af5fff3537cd5`
- 実行後コードhash: `540cf68013c6a27b13768d90fc3af5fff3537cd5`
- 実行後の対象コードdiff: なし
- 既存の`MambaStatefulTBPTT.yaml`変更（`prediction + self_update`）は保持
- run artifact: `ssm_tracker/saved_ckpts/p4a_loss_oscillation_diag_3ep_20260911/20260911T044503+0900_3489e78/`
- artifact内の`manifest.json`と`git.diff`に、実行時条件と一時変更の記録を保存済み

## 次の候補

1. loss上位batch（特にlocal batch 93, 67, 72, 71, 68）のtrajectory構成とframe gapを確認する。
2. state normが大きい後半batchについて、lossピークとは別のstate値増加要因を確認する。
3. frame gapとtrajectory構成で説明できない場合に限り、TBPTT segment単位のloss・detach前後stateを追加診断する。
