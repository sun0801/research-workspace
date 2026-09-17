---
date: 2026-09-17
project: sam2-mamba-motion-tracking
source: ../../../../secretary/notes/brainstorm/2026-09-17-p4a-hyperparameter-search-scope.md
status: draft
tags: [spec, experiment, p4a, tbptt, hyperparameter]
---

# P4a unroll length / TBPTT length hyperparameter search Spec

## 目的

P4a stateful unroll学習において、学習時系列長（`unroll_length`）と勾配伝播のtruncation長（`tbptt_length`）が、予測精度、長期rolloutの安定性、stateの挙動、tracking性能に与える影響を切り分ける。

15GB GPUに対して現行U48T12では約3GBしか使用していないため、現行の48 transition / 12 transitionより長い設定を含めて探索する。ただし、現在の学習実装ではpeak VRAMの主な増加要因は`tbptt_length`ではなく`unroll_length`である。U192はscreening前に必ずVRAM smokeを行う。

## 背景

現実装では、datasetが同一trackのtransitionを`unroll_length`ごとの非重複chunkに分割する。chunk末尾はpaddingされ、maskで有効transitionと区別される。学習時はchunk開始時にstateを初期化し、chunk内部では`tbptt_length`ごとに勾配グラフをdetachするが、stateの数値はcarryする。

現実装の評価には、次の制約がある。free rolloutは`start_stride=0`では各trackの先頭から毎回cold stateで開始するため、長いGT履歴を経たstateからのfree rolloutを測っていない。また、validation datasetは訓練条件と同じ`unroll_length`でchunk分割され、`loss_start_index=4`も各validation chunkの先頭で適用される。したがって、`unroll_length`条件間でvalidation lossをそのまま比較しない。

さらに、現在のtraining loopはTBPTT境界でstateをdetachする一方、全segmentのlossを保持して最後に一度だけbackwardする。そのため、固定`unroll_length`では`tbptt_length`を変えても保持するactivation量は大きく変わらず、`unroll_length`を伸ばした場合にactivation memoryが増える。padding部分はloss maskで除外されるが、forward自体はpadding入力にも行われるため、chunk末端のstate normはpadding後の値として扱う。

現行基準設定は以下である。

- `unroll_length=48`
- `tbptt_length=12`
- `batch_size=64`
- `d_m=256`
- `d_state=16`
- `shuffle=True`
- optimizer: Adam、`lr=1e-4`
- `loss_start_index=4`

9/11 MTGでは、padding/maskingの確認後、`unroll_length`、`tbptt_length`、batchサイズ、Mamba内部次元を段階的に探索する方針を確認した。今回のspecではそのうち`unroll_length`と`tbptt_length`だけを対象にする。

## 検証したい問い

1. `unroll_length`を48から96、192へ拡大すると、長いstate carry文脈の学習によりfree rolloutやtracking性能が改善するか。
2. `tbptt_length`を12から24、48へ拡大すると、より長い勾配伝播が学習性能・安定性に寄与するか。
3. 長いunrollと長いTBPTTを組み合わせた場合、個別の変更より追加の効果があるか。
4. 改善または悪化が、時系列長・勾配伝播長そのものによるのか、chunk数・optimizer step数・計算量の変化によるのか。

## 仮説

- H1: `unroll_length=96`または192では、chunk内でstateをcarryできる実時間範囲が伸び、長期rollout誤差またはtracking性能が改善する可能性がある。
- H2: `tbptt_length=24`または48では、state carryの影響をより長い勾配範囲で学習できるため、12より長期依存を学習しやすくなる可能性がある。
- H3: `unroll_length`を伸ばしても、optimizer step数の減少やpadding/maskingの不備により改善しない可能性がある。
- H4: `tbptt_length=48`のfull BPTTは改善する可能性がある一方、勾配・stateの不安定化のリスクがある。現行実装では、固定`unroll_length=48`における`tbptt_length`変更だけでpeak VRAMが比例的に増えるとは仮定しない。

## 実験・実装内容

### 探索条件

#### A. unroll sweep

`tbptt_length=12`を固定し、次を比較する。

| 条件ID | `unroll_length` | `tbptt_length` | 備考 |
|---|---:|---:|---|
| U48T12 | 48 | 12 | 現行baseline |
| U96T12 | 96 | 12 | unroll 2倍 |
| U192T12 | 192 | 12 | unroll 4倍 |

#### B. TBPTT sweep

`unroll_length=48`を固定し、次を比較する。

| 条件ID | `unroll_length` | `tbptt_length` | 備考 |
|---|---:|---:|---|
| U48T12 | 48 | 12 | 現行baseline |
| U48T24 | 48 | 24 | TBPTT 2倍 |
| U48T48 | 48 | 48 | chunk全体でBPTT |

#### C. 追加対照

A/Bで傾向を確認し、peak VRAMと安定性に問題がなければ、unrollに対するTBPTT比率を1/4に保つ次の条件を追加する。

- `(unroll_length, tbptt_length)=(96,24)`
- `(unroll_length, tbptt_length)=(192,48)`

### 固定条件

- dataset annotationとtrain/val split: 現行P4aと同一
- bbox入力: 現行の4次元`xywh`
- bbox scale: `1`
- delta scale: `50`
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
- seed: `0`（screening）
- screening epochs: `100`（VRAM smokeは`1〜3` epoch）
- validation loss period: `5`
- warm-up付きfree rollout period: `5`
- screening中の`mot_metrics_period`: `0`（tracker評価は候補選抜後に実施）
- validation unroll length: `48`（訓練条件から独立）
- free rollout warm-up steps: `0, 8, 24, 48, 96`
- association、missing mode、detector、SAM2統合条件: 変更しない

batch size、Mamba内部次元、learning rate、入力形式、association/cache制御を同時に変更しない。

### 実験開始前の必須プロトコル

以下はscreeningを開始する前に満たす。これらが未実施の場合、run自体は診断目的に実行できるが、条件間の優劣や長期state carryの効果を主張しない。

1. **warm-up付きfree rollout**：各trackの評価開始時にstateをresetし、GTをK step入力してstateをwarm-upした後、H stepを予測入力だけでrolloutする。`K={0, 8, 24, 48, 96}`、`H={1, 4, 8, 16, 32}`を固定し、K=0は現行のcold-start protocolとする。K/Hごとの有効sample数も記録する。
2. **validation条件の固定**：訓練条件とは独立したvalidation datasetを用い、validation unrollを常に48に固定する。validation lossは共通の`loss_start_index=4`以降で計算し、長いstate文脈の評価はwarm-up付きfree rolloutで行う。
3. **U192 VRAM smoke**：U96T12とU192T12を1〜3 epoch実行し、peak allocated/reserved VRAM、finite性、学習時間を実測する。U192が安全マージンを超える場合はscreeningを中止し、segmentごとのbackwardによる勾配蓄積を追加対照として設計する。

warm-up rolloutと固定validationの追加は、設定ファイル複製だけでは完了しない。`p4a_metrics.py`およびvalidation dataset生成側の実装変更・単体確認を必要な作業として扱う。

## 使用データ・モデル

- モデル: `MambaStateful`
- 学習entrypoint: `ssm_tracker/train_mamba_stateful.py`
- 設定: `ssm_tracker/cfgs/MambaStatefulTBPTT.yaml`を条件ごとに複製・変更して使用
- dataset: 現行P4aの`traj_anno_data/dancetrack_train.json` / `traj_anno_data/dancetrack_val.json`
- validation: 訓練条件からunrollを切り離した、validation unroll固定48のGT-only predictor validation
- tracker評価: predictor候補を絞った後、同一条件のDanceTrack val 25系列で実施

実験前に外部リポジトリのcommit、dirty diff、config、dataset、seedを記録する。既存の未コミット変更を破棄しない。

## 比較対象・ベースライン

主baselineは`(48,12)`とする。9/11以前のP4a runは`shuffle=False`で、現行YAMLの`shuffle=True`、`missing_mode=self_update`、`association_mode=prediction`等と一致しないため、U48T12は現行config・同一runnerで再実行する。以後の条件比較では、既存runを再利用せず、commit、dataset、config、seed、checkpoint provenanceをmanifestに記録する。

P4aとL0の既存比較値は参考値として保持するが、今回の条件間比較では、学習条件以外を変更しない。

## 評価指標

### 学習・predictor評価

- epoch mean loss
- 固定validation windowでのvalidation loss
- warm-up K/H別free rolloutのIoU / MAE: `K={0,8,24,48,96}`, `H={1,4,8,16,32}`
- checkpoint選択は固定validation lossではなく、`K=48, H=32`のfree-rollout IoU（`rollout/k48/h32/iou`）のbestを主基準とする。validation lossのbestは診断用に併記する。
- free rolloutのnonfinite率・divergence率
- K/Hごとの有効sample数
- state norm、gradient norm、finite率
- checkpoint保存・再読み込みの成否

### 計算資源・provenance

- train sample/chunk数
- `len(dataloader)`
- epochあたりoptimizer step数
- 総transition数
- 学習時間
- peak allocated/reserved VRAM
- 実験時のcommit、config、seed、dirty diff

### tracking評価

predictor単体で候補を絞った後、DanceTrack val 25系列について以下を記録する。

- HOTA
- DetA
- AssA
- MOTA
- IDF1
- IDSW

tracker評価では、detector、association、missing、cache update、TrackEval条件を固定し、学習checkpointだけを差し替える。SAM2統合評価は本specの必須範囲外とし、最終候補の確認段階に分離する。

## 成功・失敗の判断基準

### 必須成功条件

- screening開始前に、warm-up付きfree rollout、validation unroll固定、U192 VRAM smokeの3つを完了する。
- 全対象runが設定した条件で起動・完了する。
- loss、gradient、state、free rolloutがnonfiniteにならない。
- padding maskがloss計算の有効範囲を正しく制御し、padding部分がstate normの比較を歪めることを記録・回避する。
- checkpointを保存・再読み込みできる。
- 各runのchunk数、batch数、optimizer step数、総transition数、peak VRAMを記録できる。

### 探索上の成功候補

- baselineと比較して、同じK/H protocolのfree rollout長期horizonでIoU向上またはMAE低下が見られる。
- state normやdivergence率を悪化させずに、predictorまたはtracker指標の一部が改善する。
- 長い設定でも15GB GPUの安全マージン内で学習が完了する。
- seed 0の差はscreening上の候補差として扱い、「改善」と断定する前にbaseline seed 0/1/2と最終候補の追加seedで確認する。

特定条件がbaselineを上回らなくても、時系列長・TBPTT長と性能・安定性・計算量の関係を説明できれば探索は有効な結果とする。

### 中止条件

- peak VRAMが安全マージンを超える、またはOOMが発生する。
- loss、gradient、state、rolloutにNaN/Infが発生する。
- paddingのlossへの混入、またはpadding後stateの扱いを記録・解釈できない。
- 学習条件以外の実装・設定差を解消できない。
- `unroll_length=192`が安全なVRAM範囲に入らない場合は、screeningを中止し、segmentごとのbackwardによる勾配蓄積を追加対照として設計する。

## 実施手順

1. 現行コードのcommit、dirty diff、config、dataset hash、seedを保存する。
2. warm-up付きfree rolloutとvalidation unroll固定48の実装を追加し、K/Hごとのsample数と固定validation lossを単体確認する。
3. padding/maskingの実装を確認し、短いstubまたは1 batchでlossへのpadding混入を検証する。state normはpadding前後を分けて記録する。
4. 現行configで`(48,12)`のbaselineを再実行する。過去runは参考値として扱い、主比較には使用しない。
5. baselineのseed 0/1/2を同一protocolで実行し、改善判定に使うnoise floorを作る。
6. `(96,12)`で1〜3 epochのVRAM・finite性smokeを実施する。
7. `(192,12)`で1〜3 epochのVRAM・finite性smokeを実施する。peak VRAMが安全範囲内ならscreeningへ進む。
8. U48T12/U96T12/U192T12を同一seed・同一100 epoch条件で学習する。実測optimizer step数と総transition数を記録する。
9. U48T24/U48T48を学習する。screening中は`mot_metrics_period=0`とする。
10. 固定validation loss、K/H別free rollout、state/gradient、計算資源を比較し、有力候補を1〜2条件へ絞る。validation lossだけでcheckpointや条件の優劣を決めない。
11. 有力候補についてtracker単体のDanceTrack val 25系列評価を行い、必要ならseed 1/2で最終候補の頑健性を確認する。
12. 結果に応じて`(96,24)`、`(192,48)`を追加する。
13. 最終候補のみSAM2統合側で評価する場合は、別specまたは既存の固定評価条件へ接続する。

### 学習budgetの扱い

初回screeningでは、同じデータを同じ回数見る比較としてnominal epochを100に固定し、総transition数が同じであることとoptimizer step数の違いを併記する。`unroll_length`を長くするとepochあたりのchunk数とoptimizer step数が減るため、差がunder-trainingに由来する可能性は残る。

optimizer step固定は、初回screeningの主比較にはせず、順位や学習曲線がoptimizer update不足の影響を受けている場合の追加対照とする。step固定ではtransition exposureが変わるため、同じ問いを測る条件ではなく、別budgetの結果として報告する。

## 期待される結果

- `unroll_length`を96または192へ伸ばすと、長い時系列文脈を使える一方、optimizer step数の減少と計算量増加のトレードオフが現れる。
- `tbptt_length`を24または48へ伸ばすと、長期依存を学習できる可能性がある一方、勾配・stateの不安定化が現れる可能性がある。固定Uにおけるpeak VRAM差は実測で確認する。
- predictor単体の改善がtrackingやSAM2統合へ直結しない可能性があるため、評価段階を分けて解釈する。

## リスク・懸念

- `unroll_length`変更でchunk数が変わり、epochあたりoptimizer step数が変わる。
- 長いunrollでpaddingの割合やtrack末尾の扱いが変わる。padding率自体は記録するが、state normはpadding前後を分けて解釈する。
- 現行の一括backwardでは、U192のactivation memoryが主なOOMリスクになる。`tbptt_length=48`だけでpeak VRAMが比例増加すると解釈しない。
- seed 0のみでは順位が偶然の可能性があるため、baseline seed 0/1/2でnoise floorを作り、最終候補は追加seedで確認する。
- validation lossとtracking性能が一致しない可能性があるため、checkpoint選択基準を`rollout/k48/h32/iou`に事前固定する。baselineの旧実行分は保存済みepoch checkpointから同じ指標で事後選択する。
- predictor validationの改善とMOT/SAM2 trackingの改善は一致しない可能性がある。

## 未決事項

- U192の安全なpeak VRAM閾値と、OOM時にsegmentごとのbackwardへ移行するか。
- warm-up付きfree rolloutをどのstart位置・track長制約で集計するか。
- baseline seed間のnoise floorを踏まえた、最終的な改善判定の実務的閾値。
- 15GB GPUに対する具体的なVRAM安全閾値。
- 追加対照の`(96,24)`、`(192,48)`をどの候補結果で採用するか。

## 関連brainstorm

- `../../../../secretary/notes/brainstorm/2026-09-17-p4a-hyperparameter-search-scope.md`

## 関連ファイル

- `../meetings/2026-09-11-mtg.md`
- `2026-09-01-p4a-stateful-unroll-tbptt-spec.md`
- `../experiments/2026-09-11-p4a-loss-oscillation-diagnostic.md`
- `../experiments/2026-09-04-l0-p4a-tracker-sam2-comparison.md`
