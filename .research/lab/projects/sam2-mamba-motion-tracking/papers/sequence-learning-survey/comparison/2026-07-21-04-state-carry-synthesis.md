---
date: 2026-07-21
project: sam2-mamba-motion-tracking
status: completed
tags: [paper-note, sequence-learning-survey, comparison, batch-4, state-carry, synthesis]
---

# Batch 4 統合: State Carry型MOTの設計判断と実装ベースライン

## 結論

現行の低HOTAを「teacher forcingだけが原因」とは扱わない。既存のGT入力診断では、Mambaの教師強制1-step予測はzero-motionより良いにもかかわらず、予測bboxをhard IoU matchingの主位置にするとHOTAが5.27まで低下し、最終観測bboxによるmatchingでは83.74だった。このため、改善は次の順に分離する。

1. **associationをmotion predictionから切り離す**: 観測bbox優先matchingを基準にし、Mamba予測はunmatched時の補助へ限定する。
2. **cache更新を信頼度で制御する**: accepted detection、self prediction、低信頼観測を同じ重みでcacheへ入れない。
3. **学習入力分布を実運用へ近づける**: GTだけでなく、accepted-detection相当の誤差とself predictionを、時刻内rolloutとして導入する。
4. **state carry学習は明示的なTBPTTとして設計する**: 現行のshuffled fixed window学習を「state carry学習」とは呼ばない。

この順序なら、association設計の誤りを学習設定の問題と誤認せず、各変更のHOTA/IDF1への寄与を切り分けられる。

## 証拠から得た設計原則

| 原則 | 根拠 | 現行との差 | 設計への反映 |
| --- | --- | --- | --- |
| 予測誤差とassociation安全性は別 | 現行GT入力で1-step IoUは改善するが、予測bboxmatchingはHOTA 5.27、観測bboxmatchingは83.74 | delta lossを最適化してもID維持を保証しない | matching位置とmotion prediction評価を別アブレーションにする |
| self-generated inputを学習にも含める | PredRNNのscheduled sampling、Social GAN / Trajectron++のrollout、Re3のprediction/noise crop | 学習はGTのみ、推論はaccepted detection/self prediction | GT・観測誤差surrogate・self predictionを時刻単位で混合する |
| 全時刻に損失を置く | Re3/MCITrack、PredRNN、Social GAN、Trajectron++ | 現行はwarm-up後7時刻のみ | 初期warm-upを除きchunk内の全教師あり時刻を損失対象にする候補 |
| state carryには信頼度付き更新/再初期化が必要 | MCITrackのlow-confidence reset、Re3の再初期化 | matched detection/self predictionにconfidence guardなし | update / freeze / resetを明示的に分ける |
| Mamba採用はframe間state carryを意味しない | Mamba-FETrackはMamba feature extractionでありcacheをframe間に渡さない | 名称が実態を覆い隠す | 学習・推論でcacheがtrack境界をまたぐかを必ず検査する |

## 提案する比較ベースライン

以下の番号は、実装・実験を始める際の比較順である。全て同一checkpoint・同一動画集合・同一detection入力・同一TrackEval設定で比較する。

| ID | association位置 | cache入力・更新 | 学習 | 目的 |
| --- | --- | --- | --- | --- |
| A0 | 最終accepted observation（zero-motion） | 観測成功時だけ履歴更新。Mamba cacheは使わない | なし | GT入力時の強い下限ではなく**回帰ガードレール**。現状HOTA 83.74を再現する |
| A1 | 現行: Mamba予測bboxを主位置 | accepted detection / self predictionを既定どおり更新 | 現行fixed-window GT学習 | 既知の失敗基線。HOTA 5.27を再現する |
| A2 | accepted observation優先。未対応trackだけ予測bboxを補助利用 | 現行更新規則のまま | A1と同一checkpoint | **associationのみ**の因果効果を測る |
| A3 | A2 | high-confidenceかつ高quality matchのaccepted detectionだけcache更新。unmatchedはfreeze | A1と同一checkpoint | **更新規則のみ**の因果効果を測る |
| A4 | A3 | A3と同一 | GT / observation-surrogate / self prediction混合のfixed-window学習 | **入力分布のみ**の因果効果を測る |
| A5 | A3 | A3と同一 | 明示的なstateful unroll + TBPTT + 入力混合 | state carry学習自体の追加効果を測る |

### A2の「観測優先」の意味

各trackの主matching位置には最後に信頼できるaccepted detectionを使う。Mambaの予測bboxは、(a) 観測位置とのmatchingが成立しないtrackの候補補助、または (b) missing区間の出力bbox、に限定する。予測bboxを全trackのhard IoU matchingの唯一の主位置にはしない。

これはMambaを無効化する提案ではない。motion modelの役割を、安定な観測associationを壊さずにgapを補うものへ置き直す提案である。

### A3の信頼度判定

具体閾値は先に固定しない。validationだけで校正し、testは一度だけ実行する。判定に使う候補は次の三つであり、最初の実装では検出scoreとmatching qualityだけに限定する。

| 入力イベント | cacheへの処理 | 理由 |
| --- | --- | --- |
| high-confidence accepted detection + 良いIoU match | update | 観測に戻して誤差累積を抑える |
| low-confidenceまたは境界的match | freeze | 誤associationのcache汚染を避ける |
| unmatched / self prediction | 初期候補はfreeze。連続missが所定長を超えた場合だけresetを比較 | 自己予測の無制限な再入力を避ける |

`freeze`、`reset`、`self update`は同時に導入せず、A3でfreeze、後続アブレーションでresetを追加する。これにより、改善が「更新しないこと」によるのか「状態を消すこと」によるのかを分離できる。

## 学習設計候補

### L0: 現行fixed-window（比較対照）

- track/video境界をまたぐstateなし。
- 12 bbox window、GTのみ、warm-up後7時刻のSmooth L1。
- A1〜A3の共通checkpointとして使い、推論導線を先に検証する。

### L1: 入力分布混合fixed-window

状態の持越しは増やさず、各時刻のmotion model入力だけを次の三種類で混合する。

| 入力種別 | 定義 | 目的 |
| --- | --- | --- |
| GT | 正解bbox | 安定なmotion signalを学ぶ |
| accepted-detection surrogate | GT bboxに、訓練split上のdetector residualまたは定義済みの幾何noiseを加えた観測 | 「matched detection = GT」ではないことを学習へ反映する |
| self prediction | 直前のmodel outputから作るbbox | missing時の誤差蓄積を学習時に露出する |

損失の教師は各時刻のGT next bbox / deltaに置き続ける。混合率は最初から決め打ちせず、GT-onlyから始めてself prediction比率を段階的に増やすscheduled sampling候補として扱う。detector residualが取得できる場合は、任意のGaussian noiseよりそちらを優先する。

### L2: track/video単位のstateful unroll + TBPTT

- minibatchは同一track・同一videoの時間順chunkで構成し、異なるtrackのstateを混ぜない。
- sequence開始でstateをzero初期化し、chunk間では同じtrackのstateだけをcarryする。
- 各chunk終端でstateをdetachするTBPTTとし、detach長は検証対象の明示的なハイパーパラメータにする。
- 最初のwarm-upを除き、chunk内の全教師あり時刻を損失対象にする。padding/missingはmaskで除外する。
- L1の三種類の入力を、このunroll内で選ぶ。

現行`InferenceParams`は推論で`torch.no_grad()`下に使われるcacheであり、autogradを通すTBPTT stateとして安全だとは未確認である。L2ではこれをそのまま再利用せず、**微分可能なstate入出力を持つ学習用forwardを別途定義し、固定window forwardとの数値parity・gradient finite性を確認してから**進める。

## 評価設計

### 1. motion predictor単体

| 評価 | 入力 | 指標 | 分かること |
| --- | --- | --- | --- |
| teacher-forced one-step | GT history | bbox IoU、delta MAE、Smooth L1 | 純粋な局所予測精度 |
| free rollout | GTで開始後、self predictionを再入力 | horizon別IoU / MAE、発散率 | 自己入力時の蓄積誤差 |
| observation-surrogate rollout | noisy accepted-detection相当を入力 | 上記 + quality別集計 | detector/association誤差への頑健性 |
| cache state診断 | 上記各条件 | norm、cosine、NaN率、reset回数 | 汚染/発散がいつ生じるか |

### 2. tracker全体

全A0〜A5についてHOTA、DetA、AssA、IDF1、ID switches、track数を報告する。HOTAだけを一つの成功判定にせず、次のように読む。

| 現象 | 解釈 |
| --- | --- |
| DetAは高くAssA/IDF1が低い | matching / ID維持が主因。motion lossだけを変えない |
| A2で大きく改善 | predictionをhard matchingへ直結したことが主因 |
| A3で改善 | cacheへの低品質更新が主因の一部 |
| L1でrolloutが改善しA4でHOTAも改善 | train/inference入力分布差が寄与 |
| L2だけ改善 | state carry学習の不足が寄与 |
| one-stepだけ改善しHOTA不変/低下 | predictor指標とassociation指標が不整合 |

### 回帰ガードレール

1. GT-input / zero-motion matchingで既存の強い結果（HOTA 83.74、IDs 4）を再現する。
2. 現行A1の低HOTA（5.27前後）を再現し、意図しない評価条件変更を検知する。
3. stateful training forwardは、state carryを無効化したとき既存fixed-window forwardと数値parityを確認する。
4. 各chunkでloss・gradient・state normのfinite性を記録する。

## 実装開始前の判断

最初に実装する候補は **A2 → A3** である。これは既存checkpointで検証でき、training変更を伴わず、現在確認済みの主因（hard prediction matching）を直接検証できる。その結果を踏まえてL1、最後にL2へ進む。

本ノートは設計候補であり、外部実装リポジトリは変更していない。実装開始には、下記spec候補の承認、対象ファイル、検証コマンド、実装開始承認を別途満たす必要がある。

## 関連成果物

- [Batch 0: 現行経路](2026-07-17-00-current-implementation-map.md)
- [Batch 1: RNN/LSTM/Seq2Seq](2026-07-17-01-rnn-lstm-basics.md)
- [Batch 2: 直接比較](2026-07-17-02-direct-tracking-comparison.md)
- [Batch 3: 補助手法](2026-07-21-03-supporting-methods.md)
- [根本原因診断](../../../experiments/2026-07-17-statecarry-root-cause-diagnosis.md)
