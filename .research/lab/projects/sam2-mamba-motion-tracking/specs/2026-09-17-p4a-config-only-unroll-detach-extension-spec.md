---
date: 2026-09-17
project: sam2-mamba-motion-tracking
source: 2026-09-17-p4a-unroll-tbptt-hyperparameter-search-spec.md
status: approved
tags: [spec, experiment, p4a, tbptt, unroll, tracker-evaluation]
---

# P4a config-only unroll / detach timing extension Spec

## 目的

前回のP4a unroll/TBPTT screeningで残ったU48T24のtracker評価を完了し、実装変更を伴わずに設定だけで比較できる以下の条件を追加評価する。

1. `unroll_length`と`tbptt_length`を一致させた条件
2. `unroll_length`を既存のU192よりさらに延長した条件

本specでは、track全体をまたぐstate carryは扱わない。現在の`StatefulUnrollDataset`が作るchunk単位のstate carryを前提とし、dataset、sampler、training loop、モデルstate管理の変更は行わない。

## 背景と位置づけ

前回の探索では、以下の条件を実行済みである。

| 条件 | 状態 |
|---|---|
| U48T12 | baseline seed 0/1/2完了 |
| U96T12 | seed 0完了 |
| U192T12 | seed 0完了 |
| U48T24 | seed 0完了。tracker評価のみ未完了 |
| U48T48 | seed 0完了 |

前回のscreeningではU192T12のoffline rolloutが暫定1位、U48T24が次点だった。ただしscreening条件は各1 seedであり、改善は未確定である。また、U48T24のbest checkpoint tracker評価は`dancetrack0007`処理中のCUDA failureにより未完了である。

現在の実装では、`unroll_length`はdataset chunkの長さであり、track全体の長さではない。chunk開始時にstateを初期化し、chunk内のsegment間ではstateをcarryするが、chunk境界ではstateをresetする。したがって、今回Uを延長しても「track全体carry」の検証にはならず、「1 chunk内でより長いstate carryを使う設定」の比較となる。

また、現在のtraining loopはchunk末尾で一度だけbackwardするため、peak activation memoryは主に`unroll_length`に依存する。`tbptt_length`を変更しても、固定Uではpeak VRAMが大きく変化しにくい。この挙動は前回のU48/U192測定結果と整合する。

## 検証したい問い

1. `unroll_length`と`tbptt_length`を一致させたfull-BPTT型の条件は、短いTBPTT条件と異なるrollout特性を示すか。
2. U192より長いU384でchunk内state carry範囲を延長すると、長期warm-up rolloutが改善するか。
3. 観測された差が、U/Tの時間設定によるものか、epochあたりoptimizer step数の減少によるunder-trainingなのか。
4. offline predictor指標の差が、tracker評価でも再現するか。

## 仮説

- H1: `U96T96`および`U192T192`ではdetach間隔とchunk長が一致するため、現在の実装におけるU/Tの意味が単純になり、長い勾配伝播が長期rolloutに影響する可能性がある。
- H2: `U384T12`では、勾配伝播長を12に保ったままchunk内state carry範囲を延長できるため、U192T12との差から「長い数値state carry」と「長い勾配伝播」を切り分けやすい。
- H3: Uを延長するとepochあたりoptimizer step数が減るため、nominal epoch固定の差は長期文脈の効果と学習budgetの差が混ざる可能性がある。
- H4: U384はU192よりpeak VRAMが増えるが、30GB GPUではscreening可能な範囲に収まる可能性がある。実測前に安全性を仮定しない。
- H5: offline rolloutの改善がtracker性能に直結しない可能性があるため、U48T24のtracker再評価と候補条件のtracker評価は別に記録する。

## 実験範囲

### A. 未完了tracker評価の再試行

再学習は行わず、既存のU48T24 best rollout checkpointを使用する。

- checkpoint: U48T24 `best_rollout.pth`（前回の主指標best epoch 15）
- dataset: DanceTrack val 25系列
- tracker条件: 前回のbaseline/U192評価と同一
- association: `prediction`
- missing mode: `self_update`
- TrackEval条件: 前回と同一

最初に`dancetrack0007`のみを単独評価する。単独評価が完了した場合に25系列全体を実行する。単独評価が再度CUDA failureになる場合は、原因未確定の欠測として記録し、設定探索の学習runを停止させない。

### B. U/T一致条件

既存のU48T48を基準として、Uを延長した一致条件を追加する。

| 条件ID | `unroll_length` | `tbptt_length` | 状態 |
|---|---:|---:|---|
| U48T48 | 48 | 48 | 前回実行済み |
| U96T96 | 96 | 96 | 新規 |
| U192T192 | 192 | 192 | 新規 |

これらは現在の実装では、chunk内の全segmentをdetachせずに処理し、chunk末尾でbackward・optimizer stepするfull-BPTT型の比較となる。

### C. U延長・短TBPTT条件

既存のU96T12/U192T12にU384T12を追加する。

| 条件ID | `unroll_length` | `tbptt_length` | 状態 |
|---|---:|---:|---|
| U96T12 | 96 | 12 | 前回実行済み |
| U192T12 | 192 | 12 | 前回実行済み |
| U384T12 | 384 | 12 | 新規 |

U384T12は、長いchunk内state carryと短い勾配伝播を分けて確認するための条件である。track全体carryの代替とは解釈しない。

### D. 任意の追加条件

U384T12のVRAM smokeと学習時間が許容範囲内で、U/T一致条件の結果を補う必要がある場合のみ、U384T384を追加する。

U384T384は初期screeningの必須条件ではない。U384T12でOOM、CUDA failure、極端な学習時間増加が発生した場合は実行しない。

## 固定条件

前回の現行protocolから以下を変更しない。

- dataset annotation、train/val split
- `batch_size=64`
- `d_m=256`
- `d_state=16`
- `d_conv=4`
- `expand=2`
- `L=3`
- optimizer: Adam
- learning rate: `1e-4`
- scheduler: `none`
- loss: Smooth L1
- `loss_start_index=4`
- gradient clipping: `1.0`
- `shuffle=True`
- validation unroll length: `48`
- validation loss period: `5`
- warm-up rollout period: `5`
- warm-up steps: `K={0,8,24,48,96}`
- rollout horizon: `H={1,4,8,16,32}`
- screening中の`mot_metrics_period=0`
- seed: `0`（初回screening）
- nominal epochs: `100`

今回、model architecture、input format、batch size、learning rate、association、missing/cache制御、SAM2統合を変更しない。

## 既存結果との比較方法

### 主比較

前回のU48T12/U96T12/U192T12/U48T24/U48T48のmetricsと、新規条件のmetricsを同じ形式で比較する。

主predictor指標は前回と同じく、`rollout/k48/h32/iou`のrun内best値とする。validation loss bestは診断用に併記する。

U/T一致条件については、少なくとも次を比較する。

- U48T48 vs U96T96 vs U192T192
- U96T12 vs U96T96
- U192T12 vs U192T192

U延長条件については、少なくとも次を比較する。

- U48T12 vs U96T12 vs U192T12 vs U384T12

### optimizer budgetの注意

nominal epochは100に固定するが、Uを長くするとepochあたりのchunk数とoptimizer step数が減る。したがって、各runで以下を必ず記録する。

- dataset sample/chunk数
- dataloader batch数
- optimizer step数
- 総transition数
- epochあたり学習時間
- 総学習時間

このspecの初回比較では、epoch固定結果をscreeningとして扱う。U192/U384で差が大きく、optimizer update不足の影響が疑われる場合のみ、step数を揃える追加対照を別途設計する。step固定条件をepoch固定条件と同じ主比較として混在させない。

## VRAM・実行リソース計画

1. U96T96とU192T192は、既存のU96/U192 smoke結果を基準に1〜3 epochのfinite性・VRAM smokeを行う。
2. U384T12は、まず単独でVRAM smokeを行う。既存U192T12の約4.6GBから単純増加する可能性があるため、peak allocated/reservedを実測する。
3. U384T12のVRAM smokeが成功した後に100 epoch screeningへ進む。
4. 複数GPUの並列実行は、U384T12の単独smokeが成功し、GPUごとの空き容量が確認できた場合のみ行う。
5. CUDA failure、OOM、driver異常が発生した場合は、そのrunを再試行する前にGPU状態と実行条件を記録する。

U384T12のVRAMが安全マージンを超える場合、segmentごとのbackward実装をこのspecに追加して混在させない。その場合は本specを中断し、実装変更を伴う別specを作成する。

## tracker評価計画

predictor単体のscreening後、以下の条件をtracker評価へ接続する。

1. U48T24 best checkpointの未完了評価を再試行する。
2. 新規条件では、`rollout/k48/h32/iou`のbest値がbaseline noise floorを明確に上回るものを最大2条件まで選ぶ。
3. 各候補についてDanceTrack val 25系列を同一tracker条件で評価する。
4. HOTA、DetA、AssA、MOTA、IDF1、IDSWを記録する。
5. tracker評価が失敗した場合、predictor結果とは分離して欠測扱いにする。

前回のbaseline seed 0/1/2のbest rollout値（0.3154/0.3132/0.3208、平均0.3165、標本標準偏差0.0039）をnoise floorの参考にする。新規条件は初回seed 0のみのため、screening結果だけで改善を確定しない。

## 成功条件

### 必須

- U48T24 tracker評価を、単独sequence smoke後に可能なら25系列まで完了する。
- U96T96、U192T192、U384T12のVRAM smokeがfiniteに完了する。
- 必須条件の100 epoch screeningが完了する。
- loss、gradient、state、rolloutにNaN/Infが発生しない。
- padding maskがlossに正しく適用されていることを前回実装から変更しない。
- 各runのconfig、commit、dirty diff、seed、checkpoint、metrics、VRAM、optimizer step数を保存する。

### 研究上の成功

- U/T一致条件と短TBPTT条件の差を、rollout・state安定性・計算量と併せて説明できる。
- U384T12で、U延長による改善可能性とoptimizer step減少の影響を区別できる。
- tracker評価まで到達した候補について、offline predictor指標との一致・不一致を記録できる。

特定条件がbaselineを上回らなくても、U/T一致とU延長が性能・安定性・VRAMに与える関係を説明できれば有効な結果とする。

## 中止条件

- U384T12でOOM、CUDA failure、またはfinite性崩壊が発生する。
- U384T12の学習時間が他条件に対して過大で、同一protocolでの比較が現実的でない。
- U/T以外のconfig差やdirty code差が判明する。
- tracker評価のCUDA failureが再発し、GPU再初期化後も安全に再試行できない。

中止した条件については、途中checkpointを削除せず、停止epochと停止理由を記録する。

## 実施手順

1. 外部リポジトリのcommit、dirty diff、既存config、dataset hash、GPU状態を記録する。
2. U48T24 best checkpointの`dancetrack0007`単独tracker評価を実行する。
3. 単独評価が成功した場合、U48T24のDanceTrack val 25系列tracker評価を実行する。
4. U96T96、U192T192、U384T12のconfigを作成し、config差分を確認する。
5. U96T96/U192T192/U384T12の1〜3 epoch VRAM・finite性smokeを実行する。
6. U384T12 smokeが安全範囲内なら、3条件を100 epoch screeningする。各runは同一seed 0とする。
7. 既存条件とmetricsを集約し、rollout、validation loss、state/gradient、optimizer step、VRAM、時間を比較する。
8. `rollout/k48/h32/iou`とbaseline noise floorを使ってtracker候補を最大2条件に絞る。
9. 必要な候補についてDanceTrack val tracker評価を実施する。
10. U384T384は、U384T12の結果とVRAMに基づいて追加可否を判断する。
11. 結果を本specに対応する実験ログへ追記し、track全体carry実装の次タスクとは分離して記録する。

## 本specで実施しないこと

- track全体のstate carry
- 同一trackのchunkを時系列順に処理するsamplerの実装
- batch内trackごとのstate管理
- segmentごとのbackwardによるメモリ最適化
- optimizer stepをsegment単位へ変更する実験
- Mamba architecture、`d_m`、`d_state`、batch size、learning rateの探索
- SAM2 decoderへの新規統合

これらはconfig-only extensionの結果を混ぜない別specで扱う。

## 関連ファイル

- `2026-09-17-p4a-unroll-tbptt-hyperparameter-search-spec.md`
- `../experiments/2026-09-17-p4a-unroll-tbptt-hyperparameter-search.md`
- `../../../../secretary/notes/brainstorm/2026-09-17-p4a-hyperparameter-search-scope.md`
- 外部実装: `/mnt/HDD10TB-2/aburatani/2025_09_aburatani_Mamba_Trackers`

