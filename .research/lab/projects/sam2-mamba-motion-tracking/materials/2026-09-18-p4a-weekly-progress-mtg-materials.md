---
date: 2026-09-18
project: sam2-mamba-motion-tracking
type: meeting-materials
topic: p4a-weekly-progress
status: draft
target_meeting: 2026-09-18
notion_url: null
notion_export: null
tags: [meeting-materials, p4a, weekly-progress, tbptt, hyperparameter, sam2, trackeval]
---

# 2026-09-18 MTG資料: P4aの1週間の進捗と次の検証方針

対象期間: 2026-09-11〜2026-09-18

## 0. 今日のMTGで先生に相談したいこと

1. P4aの次の優先順位を、まず **U384T384など有力条件の追加seed・tracker・SAM2統合による再確認**に置くか、それとも **track全体でstateをcarryする学習設計**へ進めるか。
2. 今後のcheckpoint選択を、epoch100固定ではなく、事前に定めた `rollout/k48/h32/iou` のbest checkpointを主基準としてよいか。
3. offline rolloutの改善がtracker/SAM2へまだ明確に波及していない現状を、View原稿では「長期state学習の成立と、MOT性能への接続が残課題」と整理してよいか。
4. batch size・Mamba内部次元の探索は、追加seedによる再現性確認とtrack全体state carryの検証後へ回してよいか。

## 1. 現時点の結論

- 9/11に確認したepoch周期のloss振動は、TBPTT境界やstate発散ではなく、`shuffle=False`で **1 batchがほぼ1動画になり、同じ動画順を毎epoch巡回していたこと**で説明できた。
- `shuffle=True`により学習lossの見かけの振動は抑えられたが、shuffle版epoch100をSAM2へ統合した結果はHOTA `53.944`で、非shuffle P4aの`54.391`を`0.447`下回った。shuffleだけではSAM2性能の改善に至っていない。
- unroll/TBPTT探索では、全条件が100 epochをfiniteに完走した。offline長期rolloutの暫定首位はU384T384の`0.337499`で、baseline 3 seed平均`0.3165 ± 0.0039`を上回った。
- ただし探索条件は各1 seedであり、tracker単体で確認できた差も小さい。**長いunroll/TBPTTが実tracking性能を改善したとはまだ言えない**。
- 固定validation loss、最終epoch、長期rollout、tracker HOTAの順位は一致しない。checkpoint選択と評価段階を分ける必要がある。

## 2. 前回MTGからの1週間の流れ

| 日付 | 実施内容 | 得られたこと |
|---|---|---|
| 9/11 | 全batch loggingとshuffle対照を確認 | 固定順序runではepoch間loss系列のSpearman rhoが`0.997〜1.000`、shuffleでピーク再現が消失 |
| 9/17 | loss振動のデータ側機序を追加診断 | 1 batchが3〜10 track、ほぼ1動画で構成され、bbox移動量だけでlossの谷・山をモデル非依存に再現 |
| 9/17 | warm-up rollout、固定validation、provenance・VRAM記録を実装 | unroll/TBPTT条件を共通protocolで比較できる評価基盤を整備 |
| 9/17 | baseline 3 seedと探索・拡張条件を100 epoch実行 | U384T384がoffline主指標で暫定首位。全run finite、U384でもpeak VRAM約9.1GB |
| 9/17 | 一部候補をDanceTrack val 25系列でtracker評価 | U192T12はbaseline比HOTA `+0.404`だが差は小さく、確証には不足 |
| 9/18 | shuffle版epoch100をSAM2統合・25系列TrackEval | HOTA `53.944`。非shuffle P4a比`-0.447`、L0比`-1.576` |

## 3. Evidence: loss振動の原因をどこまで特定できたか

### 9/11時点の観測

- `shuffle=False`では各epochのloss系列がほぼ同じ形を再現した。
- epoch 1 vs 2のSpearman rhoは`0.9997`、top-10 peak overlapは`1.0`だった。
- loss最大は3 epochともlocal batch 93だった一方、state最大位置は一致しなかった。
- `shuffle=True`ではepoch間rhoが`-0.127〜0.029`、top-10 overlapが`0.0〜0.1`となり、固定位置のピークが消えた。

### 今週追加で分かった機序

- datasetは同一trackのchunkを連続配置し、同一動画のtrackも連続している。
- batch size 64では、1 batchに含まれるtrackは3〜10本程度で、そのほぼ全てが同じ動画に属していた。
- bboxを「変位ゼロ」と予測するモデル非依存proxyでも、実測lossのピークbatch 67・72・93を再現した。
- したがって、lossの周期形状は主に動画ごとの移動量と固定されたデータ順で決まっていた。

### 解釈

この結果は、P4aの数値不安定性やTBPTT境界がloss振動を生んだという見立てを弱める。一方で、`shuffle=False`では同一動画由来の相関した勾配を数十step続けて与えており、最適化上望ましくない状態だった可能性が高い。

## 4. Evidence: unroll/TBPTT探索

主指標は、48 stepのGT warm-up後に32 stepをfree rolloutする `rollout/k48/h32/iou` のrun内best値とした。固定validation lossだけでは長期stateの良否を選べないためである。

### 主要結果

| 条件 | best rollout IoU（epoch） | peak VRAM | padding率 |
|---|---:|---:|---:|
| U48T12 baseline seed 0/1/2 | 平均`0.3165 ± 0.0039` | 約1.2GB | 2.8% |
| U96T12 | `0.3302`（10） | 約2.4GB | 5.9% |
| U192T12 | `0.3346`（35） | 約4.6GB | 12.2% |
| U48T24 | `0.3344`（15） | 約1.2GB | 2.8% |
| U48T48 | `0.3324`（15） | 約1.2GB | 2.8% |
| U96T96 | `0.333740`（25） | 約2.3GB | 5.9% |
| U192T192 | `0.333248`（35） | 約4.6GB | 12.2% |
| U384T12 | `0.331462`（10） | 約9.1GB | 20.3% |
| U384T384 | **`0.337499`（40）** | 約9.1GB | 20.3% |

- 全探索runでwarm-up rolloutのvalid率は`1.0`、nonfinite/divergence率は`0`だった。
- unrollを48→384へ伸ばすとVRAMは約1.2GB→9.1GBへ増えた。
- 同じunrollでTBPTT長を伸ばしてもpeak VRAMはほぼ増えなかった。現実装のメモリ量はTBPTT長よりunroll長に支配される。
- U384T384は暫定首位だが、baseline平均との差`約0.0210`に対して探索条件は1 seedのみである。
- 長いunrollほどpadding率が増える。state normはpadding後の値を含むため、条件間比較には注意が必要である。

### checkpoint選択の重要性

baseline seed 0の主rollout IoUはepoch 5で`0.3154`だったが、epoch 100では`0.0312`まで低下した。一方、固定validation lossは終盤まで改善していた。最終epoch固定やvalidation loss単独では、長期rolloutに適したcheckpointを選べない。

## 5. Evidence: tracker単体とSAM2統合

### Mamba tracker単体の25系列評価

| checkpoint | HOTA | IDF1 | IDSW | 注記 |
|---|---:|---:|---:|---|
| U48T12 baseline seed1 epoch5 | 47.978 | 47.738 | 2,419 | baseline |
| U192T12 best rollout epoch35 | 48.382 | 47.793 | 2,417 | baseline比HOTA `+0.404` |
| U48T24 best rollout | 48.688 | 47.496 | 2,403 | checkpoint選択protocol差があり単純順位にはしない |
| U96T96 best rollout epoch25 | 48.127 | 47.396 | 2,411 | 拡張条件の同一protocol評価 |
| U192T192 best rollout epoch35 | 48.375 | 48.106 | 2,414 | 拡張条件の同一protocol評価 |

offline主指標の差に比べ、tracker HOTAの差は小さい。またU384T384はまだtracker評価していない。

### SAM2/SAMURAI統合の25系列評価

| model/checkpoint | HOTA | AssA | IDF1 | IDSW |
|---|---:|---:|---:|---:|
| L0 epoch100 | **55.520** | **62.482** | **64.154** | 1,535 |
| 非shuffle P4a epoch100 | 54.391 | 61.320 | 63.051 | **1,520** |
| shuffle P4a epoch100 | 53.944 | 60.701 | 62.172 | 1,551 |
| shuffle − 非shuffle | -0.447 | -0.619 | -0.879 | +31 |

shuffle版は学習lossの順序依存を改善したが、epoch100固定のSAM2統合性能は改善しなかった。これは「shuffleが無効」と断定する結果ではなく、epoch100が長期rollout上のbest checkpointとは限らない点、単一seedである点を残す。

## 6. 3つの評価段階の整理

| 段階 | 測っているもの | 今週の結果 | まだ不足するもの |
|---|---|---|---|
| Offline rollout | GT履歴からの長期bbox予測 | 長いU/T条件が有望、全条件finite | 追加seed、padding率の影響分離 |
| Tracker単体 | detector・associationを含むMOT | 一部候補でHOTA微増 | 全候補の同一protocol評価、seed確認 |
| SAM2統合 | SAM2/SAMURAI全体でのMOT | shuffle epoch100は非shuffle/L0を下回る | best rollout checkpointと有力U/T条件の評価 |

この3段階の数値はpipelineと条件が異なるため、HOTA値を段階間で直接比較しない。見るべき点は、各段階で同一条件のbaselineに対して改善が再現するかである。

## 7. Interpretation: 今回言えること / まだ言えないこと

### 今回言えること

- loss振動の主因は固定された動画順であり、state発散やTBPTT境界を主因とする証拠はない。
- warm-up付きrollout、固定validation、VRAM・provenance記録を含む探索基盤が整い、U48〜U384、T12〜T384を安全に実行できた。
- 現行のchunk-reset実装でも、unroll/TBPTTを伸ばすとoffline長期rolloutが改善する候補は得られた。
- 固定validation lossと長期rolloutは一致せず、checkpoint選択は追跡目的に近い指標で行う必要がある。
- shuffle版epoch100は、SAM2統合上で非shuffle P4aおよびL0を上回らなかった。

### まだ言えないこと

- U384T384がbaselineを再現性をもって上回るか。
- offline rolloutの改善がtracker単体、さらにSAM2統合まで伝播するか。
- shuffle自体がSAM2性能を悪化させたのか、seed・epoch100固定・checkpoint選択が原因なのか。
- chunk開始ごとのzero resetをやめ、track全体でstateをcarryすることが有効か。
- batch size・Mamba内部次元を変えた場合の性能・計算量の関係。
- 長いunrollで増えるpaddingがstate学習へ与える影響。

## 8. 方針候補・比較

| 方針 | 内容 | 利点 | 懸念 |
|---|---|---|---|
| A. 有力条件を再確認 | U384T384と比較候補を追加seedで学習し、同一protocolでtracker→SAM2を評価 | 現在の結果を主張可能な強さへ近づける | 計算時間を使う。差が小さい可能性 |
| B. track全体state carryへ進む | chunk間もtrack単位でstateを引き継ぐ別specを作る | 研究の中心課題に直接近い | sampler、state管理、backward設計の変更が大きい |
| C. batch・`d_m`探索を続ける | 最適化とモデル容量を探索 | 現構成の上限を確認できる | 探索軸が増え、state carryの問いがぼやける |
| D. decoder統合を優先 | bbox予測前の特徴へMambaを統合 | 新しい研究方向へ進める | 現P4aの未解決点を残し、原因分離が難しくなる |

## 9. 推奨する次の進め方

1. まず小さな確認セットとして、U384T384をseed 1/2でも実行し、既存のU48T12 baseline 3 seedと同一checkpoint選択protocolで比較する。
2. U384T384をtracker単体で評価し、baseline noise floorを超える場合だけSAM2統合へ進める。
3. SAM2統合ではepoch100固定ではなく、事前定義したbest rollout checkpoint同士を比較する。
4. 改善が再現しない、または差が小さい場合は、U/Tの細かな探索を止めてtrack全体state carryの別specへ進む。
5. batch size・`d_m`探索とdecoder統合は、その後の独立した比較として扱う。

## 10. Ask: MTGで決めたいこと

- 推奨順序「追加seed・同一protocol確認 → tracker → 必要時SAM2 → track全体state carry」で進めてよいか。
- 追加seedの対象をU384T384に絞るか、tracker HOTAが比較的高かったU48T24も含めるか。
- checkpoint主選択を`rollout/k48/h32/iou`に固定し、epoch100は補助結果として扱ってよいか。
- View原稿には、今回の結果を性能改善の確定結果ではなく、データ順序依存の解明と長期state評価protocolの整備として載せるか。

## 11. 前回MTG TODOの進捗

### 完了または大きく進展

- shuffle学習済みcheckpointのSAM2統合・25系列評価。
- `unroll_length` / `tbptt_length`探索と、追加のfull-BPTT条件のscreening。
- padding率・maskによるloss有効範囲・padding後state normの扱いの記録。
- `transition`、`chunk`、`batch`、`optimizer step`の実験ログ上の区別。

### 未完了・次週以降

- track全体state carryの実装・検証spec。
- batch sizeとMamba内部次元の探索。
- 正規化bbox lossのpixel換算。
- SAM2/SAMURAI/MOTの物体追加・消失と特徴対応の図示。
- decoder／memory側のMamba統合位置の比較。
- View原稿の定性的結果strip、ACCV旧・新結果の統一。

## 12. 参照ファイル

- [2026-09-11 MTG議事録](../meetings/2026-09-11-mtg.md)
- [P4a loss振動診断](../experiments/2026-09-11-p4a-loss-oscillation-diagnostic.md)
- [P4aハイパーパラメータ探索の整理](../../../../secretary/notes/brainstorm/2026-09-17-p4a-hyperparameter-search-scope.md)
- [P4a unroll/TBPTT探索spec](../specs/2026-09-17-p4a-unroll-tbptt-hyperparameter-search-spec.md)
- [P4a unroll/TBPTT探索結果](../experiments/2026-09-17-p4a-unroll-tbptt-hyperparameter-search.md)
- [P4a shuffle checkpointのSAM2統合評価](../experiments/2026-09-18-p4a-shuffle-sam2-trackeval.md)
- [9/4 P4a/P4b SAM2評価資料](2026-09-04-p4a-p4b-sam2-evaluation-mtg-materials.md)
- shuffle P4a TrackEval正本: `/mnt/HDD10TB-2/aburatani/TrackEval/data/trackers/dancetrack/val/sam2_p4a_shuffle_epoch100_25seq_20260917/trackeval_20260918/pedestrian_summary.txt`
- 非shuffle P4a TrackEval正本: `/mnt/HDD10TB-2/aburatani/TrackEval/data/trackers/dancetrack/val/sam2_p4a_epoch100_25seq_20260904/pedestrian_summary.txt`
