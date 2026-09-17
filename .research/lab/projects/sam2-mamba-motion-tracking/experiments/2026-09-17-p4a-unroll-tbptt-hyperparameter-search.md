---
project: sam2-mamba-motion-tracking
type: experiment-log
status: completed
date: 2026-09-17
---

# P4a unroll/TBPTT hyperparameter search

## Status

承認済みspecに従った実装と実験を完了した。baseline `(U48, T12)` のseed 0/1/2、およびscreening 4条件を100 epochまで実行し、offline rollout分析とbaseline/U192のDanceTrack val tracker評価を完了した。

## 実装

対象リポジトリ: `/mnt/HDD10TB-2/aburatani/2025_09_aburatani_Mamba_Trackers`

- `p4a_metrics.py`: `K={0,8,24,48,96}` のGT warm-up後 `H={1,4,8,16,32}` free rolloutを追加。trackをKごとにbatch化し、K/H別のIoU、MAE、valid/nonfinite/divergence率、sample数を保存。
- `stateful_unroll_dataset.py`: track数、総transition数、padding数を記録。
- `train_mamba_stateful.py`: validation unrollを訓練条件から分離して48に固定。peak VRAM、chunk/batch/optimizer step、transition/padding統計をepoch metricsへ保存。checkpoint主選択を `rollout/k48/h32/iou` に固定し、validation loss bestは診断用に保持。
- search config: `U48T12`, `U96T12`, `U192T12`, `U48T24`, `U48T48`。screeningは100 epoch、shuffle=true、MOT評価なし、validation U48、warm-up rollout period 5。

## 検証済み事項

- 対象3ファイルの `py_compile`: PASS。
- warm-up rolloutの単体smoke（K/H sample数・valid率・legacy wrapper）: PASS。
- train 1 batch smoke: PASS。
- train dataset実測: U48/U96/U192で総transition数は348,493。padding率はそれぞれ約2.8%、5.9%、12.2%。
- U96T12 3 epoch VRAM smoke: peak allocated約2,354 MiB、reserved約2,536 MiB、finite。
- U192T12 3 epoch VRAM smoke: peak allocated約4,566 MiB、reserved約4,974 MiB、finite。16GB GPU上でOOMなし。
- batch化後の実モデル5 epoch smoke: 固定validationとK/H rolloutが完了。rolloutはK=96を含み、旧batch=1実装の5分超に対して約10秒で完了。
- gradient norm・train state normをepoch metricsへ保存する1 batch logging smoke: PASS。

## 本実験の進捗

| run | config | seed | status |
|---|---|---:|---|
| `p4a_search_u48t12_seed0` | U48T12 | 0 | 100 epoch完了。run directory `20260917T103316+0900_0aae9f6` |
| `p4a_search_u48t12_seed1` | U48T12 | 1 | 100 epoch完了。run directory `20260917T103319+0900_0aae9f6` |
| `p4a_search_u48t12_seed2` | U48T12 | 2 | 100 epoch完了。初回23 epoch + resume run |
| `p4a_search_u192t12_seed0` | U192T12 | 0 | 100 epoch完了。初回20 epoch + resume run |
| `p4a_search_u96t12_seed0` | U96T12 | 0 | 100 epoch完了（GPU0） |
| `p4a_search_u48t24_seed0` | U48T24 | 0 | 100 epoch完了（GPU0） |
| `p4a_search_u48t48_seed0` | U48T48 | 0 | 100 epoch完了（GPU1） |

中断した初回 run（`20260917T102058+0900_0aae9f6` / `20260917T102059+0900_0aae9f6`）はepoch 5 rolloutの逐次実装が遅かったため主比較から除外する。再実行runとは別directoryに保存されている。

## baseline seed 0/1 noise floor（seed 2完了前）

完了済み2 seedの20回のwarm-up rollout評価から、`rollout/k48/h32/iou` のbest値はseed 0=`0.3154`（epoch 5）、seed 1=`0.3132`（epoch 5）で、平均=`0.3143`、標準偏差=`0.0016`だった。epoch 100の値はseed 0=`0.0312`、seed 1=`0.3051`であり、最終epoch固定は不安定である。共通epochでのIoUは次の通り。

| epoch | seed 0 | seed 1 |
|---:|---:|---:|
| 5 | 0.3154 | 0.3132 |
| 10 | 0.3099 | 0.3111 |
| 15 | 0.3085 | 0.2678 |
| 20 | 0.2587 | 0.2604 |
| 50 | 0.1648 | 0.2283 |
| 75 | 0.2240 | 0.0856 |
| 100 | 0.0312 | 0.3051 |

これは候補条件の比較で、best checkpointだけでなく共通epochの曲線とseed 2を併記する根拠になる。

## 途中分析（baseline seed 2・screening完了前）

再実行済みbaselineの同一epoch時点で、`rollout/k48/h32/iou` は以下のように変動している。100 epoch完了後も、seed 0のepoch100は0.0312、seed 1は0.3051であり、最終epochだけの比較は不安定である。主比較では各runのrollout選択基準に従ったcheckpointと、共通の評価epochを併記する。

| epoch | seed 0 | seed 1 |
|---:|---:|---:|
| 5 | 0.3154 | 0.3132 |
| 10 | 0.3099 | 0.3111 |
| 15 | 0.3085 | 0.2678 |
| 20 | 0.2587 | 0.2604 |
| 25 | — | 0.2910 |

これは固定validation loss（同時期は約0.0426〜0.0468）と長期rolloutの順位が一致しないことを示す途中 evidence であり、最終的な改善判定にはseed 0/1/2と全screening条件の共通比較を使う。

## 追加の途中所見

baselineのepoch 40〜55では、固定validation lossは約0.0412から0.0410へ改善している一方、validation末端state normは約7.2から10.9へ増加した。`rollout/k48/h32/iou` はseed 0で0.158（epoch 40）、0.120（45）、0.165（50）、seed 1で0.171（40）、0.194（45）、0.228（50）と大きく揺れている。このため、長期rolloutとstate安定性を主評価に含める必要性が途中結果でも確認できる。いずれも当該epoch時点でdivergence rateは0だった。

## 解釈上の注意

- `start_stride=0` のwarm-up rolloutは各trackの先頭から開始するprotocol。K/H別の有効sample数を併記する。
- validationのstate normは現実装ではpadding後のchunk末端stateであり、padding率と併せて解釈する。主比較は固定validation lossとwarm-up rolloutの両方で行う。
- 長期horizonの候補判定は `rollout/k48/h32/iou` を主checkpoint基準とし、baseline seed 0/1/2のnoise floorを作った後に行う。seed 0単独の差は改善と断定しない。

## 次の作業

1. baseline seed 0/1は完了済み。中断checkpointからseed2/U192をresumeし、U96T12・U48T24・U48T48も5条件並列実行中。
2. U96T12、U192T12、U48T24、U48T48を同一100 epoch protocolで実行。
3. metrics JSONを集約し、固定validation、K/H rollout、padding、VRAM、学習時間を比較。
4. baseline noise floorを超える候補を1〜2条件に絞り、必要ならDanceTrack valのtracker評価へ接続。


## 最終集計と分析

主指標は各runの `rollout/k48/h32/iou` 最大値。baseline seed 0/1/2のbest値は0.3154/0.3132/0.3208（平均0.3165、標本標準偏差0.0039）だった。

| condition | best IoU (epoch) | final IoU | val loss best/final | peak VRAM MB | padding |
|---|---:|---:|---:|---:|---:|
| U48T12 seed0 | 0.3154 (5) | 0.0312 | 0.04684 / 0.04110 | 1224 | 2.8% |
| U48T12 seed1 | 0.3132 (5) | 0.3051 | 0.04749 / 0.04076 | 1177 | 2.8% |
| U48T12 seed2 | 0.3208 (10) | 0.1279 | 0.04487 / 0.04099 | 1224 | 2.8% |
| U96T12 | 0.3302 (10) | 0.2197 | 0.04528 / 0.04080 | 2354 | 5.9% |
| U192T12 | **0.3346 (35)** | 0.2167 | 0.04429 / 0.04103 | 4566 | 12.2% |
| U48T24 | 0.3344 (15) | 0.1579 | 0.04515 / 0.04007 | 1224 | 2.8% |
| U48T48 | 0.3324 (15) | 0.2342 | 0.04423 / 0.03964 | 1178 | 2.8% |

offlineのbest rolloutではU192T12、U48T24、U48T48、U96T12がbaseline noise floorを上回った。ただしscreening条件は各1 seedなので、改善を確定的には主張しない。全条件でwarm-up rolloutのvalid率は1.0、nonfinite/divergenceは0だった。epoch100のK0/K8/K24/K48・H32 IoUは、U96T12=`0.2461/0.2740/0.1966/0.2197`、U192T12=`0.2280/0.2753/0.2508/0.2167`、U48T24=`0.0430/0.1464/0.1424/0.1579`、U48T48=`0.1499/0.2094/0.2609/0.2342`で、warm-up効果は条件・epochに依存し一貫しなかった。

U192T12のpeak allocatedは4566MBで、U48T12の約1224MBの約3.7倍。一方Tを12から24/48へ増やしても約1.2GBであり、今回の実装ではpeak activation memoryはunroll長に支配され、tbptt長にはほぼ依存しないというspec修正を支持する。padding率は2.8%/5.9%/12.2%で、state norm比較にはpadding後stateである点に注意する。

## DanceTrack val tracker評価

baseline seed1 epoch5（`epoch5.pth`）とU192T12 best rollout epoch35を同一設定で25 sequence評価した。

| checkpoint | HOTA | IDF1 | MOTA | IDSW |
|---|---:|---:|---:|---:|
| baseline U48T12 seed1 epoch5 | 47.978 | 47.738 | 84.599 | 2419 |
| U192T12 best rollout epoch35 | **48.382** | **47.793** | 84.590 | **2417** |

U192はoffline主指標では baseline平均を約0.018、baseline最大を約0.014上回ったが、tracker指標の改善はHOTA +0.404、IDF1 +0.055、IDSW -2と小さい。現時点では長いunrollが実tracker性能を改善したとは結論しない。

U48T24 best rolloutのtracker評価は、GPU0でdancetrack0007処理中にCUDA `unspecified launch failure`、GPU1再試行はCUDA初期化失敗で完遂できなかった。offline結果は有効だがtracker結果は欠測として扱う。失敗後はGPU0のdevice handleがUnknown Errorとなったため追加tracker評価は停止した。

## 結論と残課題

- 実験とoffline分析は完了。主指標上の暫定1位はU192T12（0.3346）、次点はU48T24（0.3344）。
- fixed validation lossだけでは条件順位を決められず、warm-up/free-rolloutを主指標にしたspec修正は妥当だった。
- U192T12はVRAM約4.6GBで、32GB GPU上の並列実行でもOOMなく完了した。
- ただしscreening条件は各1 seed、tracker評価はbaselineとU192のみで、確定的な改善主張には不足する。
- 次段階はU192T12とU48T24またはU48T48をseed 1/2で再実行し、GPU再初期化後に同じbest checkpoint protocolでtracker評価を再試行すること。U48T24はCUDA failureの再現性とstate値・入力範囲を追加診断する。


## 2026-09-17 config-only extension execution

承認済みspec `2026-09-17-p4a-config-only-unroll-detach-extension-spec.md` に従い、U48T24の未完了tracker評価を再試行し、新規3条件のsmokeと100 epoch screeningを開始した。track全体state carry、segmentごとのbackward、Optunaは本実験に含めない。

### U48T24 tracker再試行

- `dancetrack0007`単独評価: 完走（CUDA failureなし）。
- DanceTrack val 25系列評価: 完走。出力は外部repoの `track_results/dancetrack/p4a_u48t24_retry_full/val/p4a_u48t24_retry_full_20260917/`。
- TrackEval: HOTA=`48.688`、DetA=`74.844`、AssA=`31.825`、MOTA=`84.627`、IDF1=`47.496`、IDSW=`2403`。
- 以前のU192T12評価（HOTA 48.382、IDF1 47.793、MOTA 84.590、IDSW 2417）とはtracker条件とcheckpoint選択が異なるため、直接の優劣判定は候補条件の同一protocol評価後に行う。

### 新規条件smoke

| condition | epochs | peak allocated / reserved | status |
|---|---:|---:|---|
| U96T96 | 3 | 約2308 / 2492 MiB | finite、完走 |
| U192T192 | 3 | 約4568 / 4974 MiB | finite、完走 |
| U384T12 | 3 | 約9086 / 9114 MiB | finite、完走 |

### 100 epoch screening（進行中）

U96T96（GPU1）、U384T12（GPU0）、U192T192（GPU0）をseed 0、batch size 64、shuffle=true、validation U48、`mot_metrics_period=0`で開始した。開始後のmetrics生成数はU96T96=8 epoch、U384T12=7 epoch、U192T192=5 epoch（2026-09-17 19:48時点）で、いずれもOOM・CUDA failure・NaN/Infなし。各runのmetrics/checkpoint/provenanceは外部repoの `ssm_tracker/saved_ckpts/p4a_extension_*` に保存中であり、完了後にoptimizer step数、時間、主rollout指標、tracker候補を追記する。


### 100 epoch screening・候補tracker評価の実績

3条件の100 epoch screeningは、すべてseed 0・同一protocolで正常終了した。各runのprovenance（config、commit、dirty diff、manifest、checkpoint manifest）は各artifact directoryに保存されている。commitは `0aae9f630cb45b74eaeb62efb655b54bc4aea14e`、dirty diffは各runの `git.diff` である。

| condition | run artifact | dataloader batches/epoch | total optimizer steps | total transitions | padding | peak allocated / reserved MiB | best rollout/k48/h32/iou (epoch) | final val loss | finite |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| U96T96 | `ssm_tracker/saved_ckpts/p4a_extension_u96t96_seed0/20260917T193916+0900_0aae9f6` | 61 | 6,100 | 348,493 | 5.93% | 2308.0 / 2492.0 | 0.333740 (25) | 0.040065 | yes |
| U192T192 | `ssm_tracker/saved_ckpts/p4a_extension_u192t192_seed0/20260917T194119+0900_0aae9f6` | 33 | 3,300 | 348,493 | 12.23% | 4615.5 / 5018.0 | 0.333248 (35) | 0.040657 | yes |
| U384T12 | `ssm_tracker/saved_ckpts/p4a_extension_u384t12_seed0/20260917T193916+0900_0aae9f6` | 18 | 1,800 | 348,493 | 20.32% | 9133.5 / 9158.0 | 0.331462 (10) | 0.042267 | yes |

最終epochの rollout/k48/h32/iou は順に 0.215220、0.142289、0.277833であり、最終epochだけではbest checkpointの順位を代表しない。全100個のmetrics JSONを監査し、全scalarがfiniteであることを確認した。U96T96/U192T192/U384T12の100 epoch所要時間はおおよそ1時間43分、1時間53分、2時間1分で、U384T12は極端な時間増加には該当しない。

### 任意条件 U384T384

U384T12の実測peak VRAMが約9.13/9.16GBで30GB級GPUに対し安全な範囲、かつ学習時間も比較可能だったため、specの判断基準に基づきU384T384を「実施可」と判断した。U384T384のconfig `ssm_tracker/cfgs/MambaStatefulP4aSearchU384T384.yaml` を追加し、3 epoch smokeはfinite、peak allocated/reserved 9135.0/9158.0 MiBで完走した。100 epoch screeningは `ssm_tracker/saved_ckpts/p4a_extension_u384t384_seed0/20260917T214551+0900_0aae9f6` で完了した。最終監査結果は末尾の「U384T384完了・最終監査」に記録する。

### 候補trackerの同一protocol評価

offline best rollout上位のU96T96とU192T192について、単独sequence smoke後にDanceTrack val 25系列を評価した。TrackEvalはGT/trackersの既存symlink構造に合わせ、`SKIP_SPLIT_FOL=True`、`DO_PREPROC=False`、HOTA/CLEAR/Identityで実行した。

| checkpoint | TrackEval output | HOTA | DetA | AssA | MOTA | IDF1 | IDSW |
|---|---|---:|---:|---:|---:|---:|---:|
| U96T96 best_rollout.pth (epoch 25) | `track_results/dancetrack/p4a_extension_u96t96_seed0/trackeval/p4a_extension_u96t96_tracker_full_20260917` | 48.127 | 74.709 | 31.154 | 84.595 | 47.396 | 2411 |
| U192T192 best_rollout.pth (epoch 35) | `track_results/dancetrack/p4a_extension_u192t192_seed0/trackeval/p4a_extension_u192t192_tracker_full_20260917` | 48.375 | 74.609 | 31.515 | 84.587 | 48.106 | 2414 |

U48T24の再試行結果（HOTA 48.688、IDF1 47.496、MOTA 84.627、IDSW 2403）と、今回のU96/U192はcheckpoint選択・評価protocolを揃えていないため、単純な優劣ではなく同一protocol内の比較として扱う。U384T384完了後、全runの最終比較と本specの結論を更新する。


### U384T384完了・最終監査

U384T384の100 epoch screeningは2026-09-17 23:38 JSTにexit code 0で完了した。100個のmetrics JSON（epoch 1〜100）を数値epoch順に監査し、全scalarがfiniteであることを確認した。artifact directoryは `ssm_tracker/saved_ckpts/p4a_extension_u384t384_seed0/20260917T214551+0900_0aae9f6` で、config、manifest、checkpoint manifest、git diff、epoch 1〜100、`final.pth`、`best_val_loss.pth`、`best_rollout.pth`を保持する。manifest上のcommitは `0aae9f630cb45b74eaeb62efb655b54bc4aea14e`、seedは0、working treeはdirtyであることが記録されている。

| condition | dataloader batches/epoch | total optimizer steps | total transitions | padding | peak allocated / reserved MiB | best rollout/k48/h32/iou (epoch) | final val loss | finite |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| U384T384 | 18 | 1,800 | 348,493 | 20.32% | 9135.0 / 9158.0 | **0.337499 (40)** | 0.042531 | yes |

U384T384のepoch 100におけるK=0/8/24/48/96・H=32 IoUは `0.2505 / 0.1286 / 0.1606 / 0.1698 / 0.1159`、best rollout epoch 40では `0.3211 / 0.3401 / 0.3234 / 0.3375 / 0.3257`だった。warm-up rolloutのvalid rateは全評価で1.0、nonfinite/divergence rateは0だった。peak VRAMはU384T12（9133.5 / 9158.0 MiB）と同水準で、Tを12から384へ増やしてもpeak activation memoryは増えなかった。これは、この実装ではactivation保持がunroll長に支配され、detach/TBPTT長単独ではほぼ増えないというspecの整理を支持する。

### config-only extensionの結論

U96T96、U192T192、U384T12、任意条件として追加したU384T384はすべて100 epochを完走し、全scalar finiteだった。主rollout best値はそれぞれ0.333740、0.333248、0.331462、0.337499で、U384T384が今回の1 seed screeningでは最大だった。ただしbaseline noise floor（seed 0/1/2のbest値の標本標準偏差0.0039）と各条件1 seedという制約があるため、改善を確定的には主張しない。候補tracker評価はU96T96とU192T192までを実施し、U384T384はscreening結果の記録に留める。

今回の実験では、track全体state carry、segmentごとのbackward、Optuna導入はいずれも実施していない。したがって、今回確認できたのは現行のchunk-reset実装におけるunroll/TBPTT設定差であり、track全体carryの有効性は後続タスクとして残る。
