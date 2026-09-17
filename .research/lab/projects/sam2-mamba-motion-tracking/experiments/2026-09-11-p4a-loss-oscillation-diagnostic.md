---
date: 2026-09-11
project: sam2-mamba-motion-tracking
spec: ../specs/2026-09-11-p4a-loss-oscillation-diagnostic-spec.md
status: completed
tags: [experiment, p4a, loss, logging, diagnosis, dataset-order]
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


## 追加対照: shuffle=True

固定batch順序がloss振動の主因かを確認するため、学習DataLoaderのみ`shuffle=True`に変更した3epoch対照runを実施した。前回runと同様に、`train/current_loss`は全batchで記録した。

- command: `ssm_tracker/train_mamba_stateful.py --exp_name p4a_shuffle_diag_3ep_20260911 --config_file ssm_tracker/cfgs/MambaStatefulTBPTT.yaml --device 0 --epochs 3 --seed 0`
- Comet: [experiment 27bdd0adb5ea4416ac6198987b6b3c83](https://www.comet.com/sun0801/mamba-mot/27bdd0adb5ea4416ac6198987b6b3c83)
- Comet run name: `p4a_shuffle_diag_3ep_20260911__20260911T054041+0900_3489e78`
- `train/current_loss`: 351点（117点/epoch）
- 一時変更: train DataLoaderの`shuffle=False`→`True`、logging条件を全batch化、既存SyntaxErrorの`log_metrics`を実行時のみ修復
- 学習終了後、学習コードは実験前の状態へ復元した。既存のYAML設定変更は保持した。

### 固定順序runとの比較

| run | epoch pair Spearman rho | top-10 overlap | batch loss std |
|---|---:|---:|---:|
| `shuffle=False`、1 vs 2 | 0.9997 | 1.0 | 0.0433 / 0.0428 |
| `shuffle=False`、1 vs 3 | 0.9971 | 1.0 | 0.0433 / 0.0412 |
| `shuffle=False`、2 vs 3 | 0.9977 | 1.0 | 0.0428 / 0.0412 |
| `shuffle=True`、1 vs 2 | -0.0458 | 0.0 | 0.0084 / 0.0089 |
| `shuffle=True`、1 vs 3 | 0.0290 | 0.0 | 0.0084 / 0.0085 |
| `shuffle=True`、2 vs 3 | -0.1270 | 0.1 | 0.0089 / 0.0085 |

`shuffle=True`では、固定順序runで再現していたlocal batch 93などのピーク位置がepochごとに再現しなかった。epoch mean lossは`0.07391 → 0.07012 → 0.06670`で、固定順序runの`0.07363 → 0.07328 → 0.07113`よりも安定して低下した。

### 解釈

今回の対照runは、Comet上のepoch周期的なloss振動が、主に`shuffle=False`で同じchunk群を毎epoch同じlocal batch位置に配置していたことによる観測・更新順序の影響だと強く支持する。一方、shuffleによって各batchの構成とoptimizer更新順序も変わるため、これだけで個々のchunkの固有難度やframe gapの原因まで特定したとは扱わない。

現在の`dancetrack_train.json`は417個のtrackを`dancetrack`配下にまとめ、bbox列だけを保存しており、元sequence名とframe IDを保持していない。そのため、ピークbatchのglobal track IDとchunk開始位置までは復元できるが、元sequence・frame gapの確定には元DanceTrack GTまたはsequence情報付きannotationが必要である。


## 追記 (2026-09-17): 振動機序の特定 — 1 batch ≒ 1動画

上記「追加対照: shuffle=True」の結論（固定batch順序が主因）は維持する。本追記はそれを否定するものではなく、**なぜ固定順序が振動を生んだのか**という機序を特定したものである。

### 特定した機序

`StatefulUnrollDataset`はtrackを時系列順に`unroll_length`ずつ切って`samples`へ順に積むだけで、並べ替えを行わない（`ssm_tracker/dataset/stateful_unroll_dataset.py:39-48`）。同一trackのchunkは連続配置され、同一動画に属するtrackも連続したobj_idで並ぶ。

その結果、64 chunkからなる1 batchは3〜10 trackしか含まず、そのほぼ全てが同じ動画に属する。**`shuffle=False`の1 epochは、訓練動画を1本ずつ順に巡回する処理**になっていた。batch lossは、その区間の動画の1frameあたりbbox中心移動量のほぼ単調関数である。

### epoch冒頭の谷とepoch内の山は同一原因

Comet上では、epoch冒頭約12 stepにわたって`train/current_loss`が0.02〜0.05と低く、local batch 14付近で0.146へ跳ね上がる谷が観測されていた。当初これを`train/mean_loss`のepoch内累積平均リセットによる表示上のartifactと考えたが、**生系列の`train/current_loss`自体が同じ谷を示しており、この仮説は棄却された**。`train/mean_loss`は谷をV字に均していただけである。

epoch冒頭の谷とlocal batch 93等の山は別現象ではなく、動画巡回という同一原因の別部分である。

### 証拠（モデル非依存の再現）

`dancetrack_train.json`をdataset順（`unroll_length=48`、batch size 64）に走査し、「変位ゼロと予測した場合のsmooth L1」を`loss_start_index=4`とmaskを適用して算出、batch単位で平均した。モデルの重みを一切使わない。

| local batch | track | 解像度 | 1frameあたり中心移動量 | 変位ゼロ予測時のsmooth L1 |
|---|---|---|---:|---:|
| 0 | 0–9 | 1280x720 | 0.0066 | 0.082 |
| 2 | 13–15 | 1280x720 | 0.0045 | 0.050 |
| 8 | 33–38 | 1920x1080 | 0.0042 | 0.032 |
| 11 | 50–56 | 1920x1080 | 0.0039 | 0.026（最小） |
| 14 | 66–69 | 1920x1080 | 0.0073 | 0.129 |
| 16 | 71–74 | 1920x1080 | 0.0085 | 0.146 |
| 67 | 214–216 | 1280x720 | 0.0108 | 0.193 |
| 93 | 314–317 | 1280x720 | 0.0124 | 0.234（最大） |

- この計算の累積平均は batch 0 で 0.082、batch 11 で最小 0.045、batch 116 で 0.074 となり、実測`train/mean_loss`の 0.072 → 0.043（step≒11）→ 0.070 と一致する。
- proxyのピーク位置 67 / 72 / 93 は、本実験が実測したピーク位置`93, 67, 72, 71, 68, ...`と一致する。
- epoch冒頭の谷の実体は、local batch 2〜11に並ぶtrack 25〜56の1920x1080動画群が訓練セット中で最も動きが遅いことである（track 54、55は0.0018）。
- **loss系列の形状がモデル非依存に再現できたため、この振動は学習の挙動ではなくデータ並び順で決まっていたと確定する。**

再現手順:

```python
import json, math
anno = json.load(open("ssm_tracker/traj_anno_data/dancetrack_train.json"))["dancetrack"]
U, B, START, SD = 48, 64, 4, 50.0
chunks = []
for oid, od in anno.items():
    if oid in {"total_objs", "obj_id_start"}:
        continue
    bb = od["bboxes"]
    for s in range(0, max(0, len(bb) - 1), U):
        chunks.append((bb, s, min(U, len(bb) - 1 - s)))
sl1 = lambda x: 0.5 * x * x if abs(x) < 1 else abs(x) - 0.5
def chunk_loss(bb, s, vl):
    vals = [sum(sl1((bb[t + 1][k] - bb[t][k]) * SD) for k in range(4)) / 4
            for t in range(s, s + vl) if (t - s) >= START]
    return sum(vals) / len(vals) if vals else None
per = [chunk_loss(*c) for c in chunks]
batches = [[v for v in per[i * B:(i + 1) * B] if v is not None] for i in range(math.ceil(len(chunks) / B))]
batch_loss = [sum(v) / len(v) for v in batches]
```

### 「次の候補」1への部分回答

本実験の「次の候補」1（loss上位batchのtrajectory構成とframe gapの確認）は、trajectory構成の側では上表で回答された。ピークbatchは移動量の大きい動画に対応する。

また「元sequence名とframe IDを保持していない」という制約に対し、**`dancetrack_train.json`の各objectが持つ`image_h`/`image_w`の切り替わりから動画境界が部分的に復元できる**ことがわかった（local batch 6と18が境界に当たる）。ただし復元できるのは1280x720と1920x1080の切り替わり点のみで、同一解像度の動画が連続する区間の境界は依然として不明である。frame gapの確定には引き続き元DanceTrack GTが必要である。

### logging上の注意（対応は先送り）

`train/mean_loss`は「そのepochの先頭からn batch分の累積平均」であり、x軸上でnが1→117と変化するため、点ごとに定義の異なる量を時系列として描いている。epoch平均は`train/epoch_mean_loss`が別途1点/epochで記録しているため冗長でもある。

この整理（`train/mean_loss`の削除、記録間隔を`len(dataloader)//10`基準へ変更、`--max_batches`時のstep軸ずれ修正）は、2026-09-17のunroll×TBPTT探索runが実行中であるため今回は実施せず、探索完了後に再検討する。
