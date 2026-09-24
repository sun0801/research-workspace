---
date: 2026-09-24
project: sam2-mamba-motion-tracking
source_todo: YOLO＋Mambaでshuffle / non-shuffleを同一条件で比較する
topic: YOLO＋Mambaにおけるshuffle / non-shuffle比較
status: exploratory
tags: [brainstorm, research, yolo, mamba, shuffle, tracking]
---

# YOLO＋Mambaにおけるshuffle / non-shuffle比較

## 読み込んだ文脈

- プロジェクトは、state carry型MambaをSAM2/SAMURAIのMOTへ統合し、hidden state contaminationと学習方法を検証している。
- P4aでは`shuffle=False`の固定chunk順序によりloss振動が生じ、`shuffle=True`では振動が抑制された。
- SAM2＋MambaのDanceTrack val 25系列・epoch100では、shuffle P4aのHOTA 53.944、非shuffle P4aのHOTA 54.391で、shuffleが0.447低かった。
- ただしSAM2統合側では、初期prompt、SAM2のメモリ、associationなどの影響が重なるため、shuffleの効果を直接解釈しにくい。
- 直近MTGでは、YOLO＋Mamba側でshuffle / non-shuffleを比較し、差がSAM2統合で見えにくい理由を切り分ける方針になっている。

## 相談の出発点

SAM2＋Mambaで見えたshuffle差が、Mambaの予測器そのものの差なのか、SAM2側の追跡・対応付けで吸収または増幅された差なのかを切り分けたい。

## 対象TODO

- YOLO＋Mambaでshuffle / non-shuffleを同一条件で比較する。

## 問い

1. chunkの学習順序をshuffleすることで、Mambaのbbox予測性能は改善するか？
2. 予測性能の差は、YOLO検出とHungarian matchingを含むtracking性能に伝播するか？
3. SAM2＋Mambaで差が小さかったのは、Mamba予測器の差が小さいためか、SAM2側の要因で差が隠れたためか？

## 仮説候補

- H1: `shuffle=True`は、同一動画由来のchunkが連続することによるoptimizer更新の偏りを緩和し、validationのfree rolloutとsequence平均性能を改善する。
- H2: training lossの振動は減るが、YOLOの全フレーム検出とHungarian matchingが強いため、最終HOTA差は小さい。
- H3: shuffle差は平均指標よりも、一部の難しいsequence・track・chunkで現れる。
- H4: DDPのsampler実装やsample重複がある場合、見かけ上のshuffle差がデータ順ではなくデータ露出量の差になる。

## 実験・実装案

### Phase 0: 比較条件の監査

最初にコードを変更する前に、両条件で以下が完全に一致することを確認する。

- train/validation split、対象sequence、chunk生成規則、過去フレーム長、予測 horizon
- batch size、epoch数、optimizer、learning rate、scheduler、weight decay、gradient clipping
- Mambaの層数・内部次元・state初期化・reset・detach・padding mask
- bboxの入力形式、scale、loss、検出入力の形式
- YOLO検出結果、confidence threshold、Hungarian matchingの閾値とcost
- checkpointの保存周期、評価時の重み、推論時の設定

特に、shuffleはchunkの順序だけを変えるものとし、各sequence内部のフレーム順を変えない。DDPを使う場合は、rankごとのsample ID一覧をepoch単位で保存し、重複・欠落・epoch間の露出差を確認する。最初の対照は、原因切り分けのためsingle GPUで実施するのが安全。

### Phase 1: 小規模paired smoke

- 同じ初期重み・同じseedのpaired runを1組だけ作る。
- 条件A: `shuffle=False`
- 条件B: `shuffle=True`
- 学習中にbatch内のsequence ID、sample/chunk ID、loss、valid mask率、state finite率を記録する。
- まず学習が同じstep数で完走し、paddingとmaskの扱いが一致することを確認する。

この段階では性能の優劣を主張せず、比較パイプラインの健全性だけを確認する。

### Phase 2: 本比較

最低3 seedで、各seedについて初期重みを共有したpaired比較を行う。epoch100だけでなく、同じcheckpoint時点で次を評価する。

- 予測器: train loss、validation loss、bbox IoU、center/size error、free rollout horizon 1/4/8/16/32
- tracker: HOTA、DetA、AssA、MOTA、IDF1、IDSW
- 安定性: nonfinite率、state norm、reset/fallback回数、推論時間

track evaluationは、全checkpointを評価できない場合、最終epochに加えてvalidation rollout基準で選んだcheckpointと、tracking指標基準で選んだcheckpointを分けて評価する。epoch100のみの比較は参考値として残すが、shuffleの優劣の結論には使わない。

### Phase 3: sequence / track / chunk分析

平均値だけでなく、同一sequence単位でshuffle−non-shuffleの差分を計算する。

- sequence別 HOTA / AssA / IDF1 / IDSW
- track別の予測誤差と失敗率
- chunk別のloss、valid mask率、sequence ID、動画内位置
- 大きな誤差の前後で、detector miss、matching変更、state異常が起きていないか

最終的には、paired bootstrapまたはsequence単位の差分分布で、単一sequenceの外れ値ではないかを確認する。

## 比較・評価軸

| 層 | 主目的 | 最低限の指標 |
|---|---|---|
| 学習挙動 | 固定chunk順序による振動の確認 | batch loss、epoch loss、sequence IDの連続性 |
| Mamba予測 | shuffleが動き予測を改善するか | validation loss、IoU、free rollout |
| YOLO＋Mamba tracking | downstreamへ伝播するか | HOTA、AssA、IDF1、IDSW |
| 失敗要因 | 差が出る条件を特定する | sequence/track/chunk別誤差、matching変更、stateログ |

## 今回見えた方向性

第一優先は、同じ初期重みを共有したsingle-GPUのpaired smoke、その後に3 seedの本比較。変えるのはDataLoaderのchunk順序だけに固定する。評価は「予測器」と「YOLO＋Mamba tracking」を分離し、SAM2側の要因を混ぜない。

期待される解釈は次の通り。

- validation rolloutもtrackingも改善: shuffleが予測器の汎化に寄与する可能性が高い。
- rolloutだけ改善しtracking差がない: YOLO検出・Hungarian matchingが差を吸収している可能性が高い。
- trackingだけ差が出る: 平均bbox誤差ではなく、matching境界付近の誤差が効いている可能性がある。
- どの指標も差がない: shuffleは主因ではないか、seed数・checkpoint選択・データ規模が不足している。
- sequence別に符号が分かれる: 平均値より、難易度やオクルージョン条件との関係を調べる。

## 次アクション候補

1. YOLO＋MambaのDataLoader/samplerが出すsample IDをepochごとにログし、shuffle/non-shuffleの実際の露出を確認する。
2. 同じ初期重み・single GPU・同じ設定でshuffle/non-shuffleのpaired smokeを実行する。
3. 2条件のvalidation rolloutとYOLO＋Mamba trackingを同一checkpoint時点で評価する。
4. 3 seed比較へ拡張し、sequence別差分とpaired bootstrapを出す。

## Spec化候補

Phase 0〜2の比較protocolはspec化可能。ただし、以下を確認するまでspec保存は保留する。

- 実際のYOLO＋Mamba学習entrypointとsamplerの場所
- 予測器評価・tracking評価の既存entrypoint
- single GPUで比較するか、DDPを含めるか
- 使えるGPU時間と、3 seed・複数checkpoint評価の現実的な範囲
- shuffle差の主評価指標をHOTAに置くか、予測器のfree rollout指標に置くか

## 未解決の問い

- YOLO＋MambaのMamba入力はGT軌跡由来か、YOLO検出由来か。train/inferenceで入力分布が一致しているか。
- shuffle対象はtrack/chunk単位か、sequence単位か。現在の実装でsequence内部の順序が保持されているか。
- DDPの`DistributedSampler`と独自shuffleの併用により、sampleの重複や欠落が起きていないか。
- 0-paddingがlossから除外されてもstateへ影響していないか。shuffle差とpadding差を分離できているか。

## 関連ファイル

- `.research/secretary/todos/2026-09-24.md`
- `.research/lab/projects/sam2-mamba-motion-tracking/README.md`
- `.research/lab/projects/sam2-mamba-motion-tracking/meetings/2026-09-18-mtg.md`
- `.research/lab/projects/sam2-mamba-motion-tracking/experiments/2026-09-18-p4a-shuffle-sam2-trackeval.md`
- `.research/lab/projects/sam2-mamba-motion-tracking/specs/2026-09-17-p4a-unroll-tbptt-hyperparameter-search-spec.md`
