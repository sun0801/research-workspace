---
date: 2026-07-17
project: sam2-mamba-motion-tracking
status: completed
tags: [paper-note, sequence-learning-survey, comparison, tracking, mamba, batch-2]
---

# Batch 2 横断比較: Re3・MCITrack・MambaLCT

## 比較表

| 手法 | 学習時のstate | loss | 推論時のcontext | low-confidence / reset | self predictionの扱い |
| --- | --- | --- | --- | --- | --- |
| Re3 | sample内LSTM unroll。train sampleごとzero | 全unroll bbox回帰 | IDごとのLSTM state + 前bbox | 一定長後に再初期化 | model predictionを次cropへ利用。訓練cropにも混入 |
| MCITrack | 2 search frameにMamba neck stateをcarry | 各searchのGIoU/L1/focal | layer別hidden state + gated template memory | scoreが閾値未満ならhidden reset | 前predictionでsearch crop。template更新は高scoreのみ |
| MambaLCT | temporal queryをsearch間で渡すがdetach | 各searchのGIoU/L1/focal | temporal query + time-segmented template memory | inspected pathにはscore gateなし | 前predictionでcropし、memoryへ無条件追加 |
| 現行MambaStateful | window内Mambaのみ、sample間carryなし | warm-up後7時刻のdelta Smooth L1 | track別cached Mamba state | `freeze`/self-updateのみ。confidence guardなし | matching成功ならaccepted detection、失敗ならself prediction |

## 回答

### 学習時にもframe間stateをcarryするか

- Re3: **はい、sample内unroll**。ただし標準は短いunrollでsampleごとにzero state。
- MCITrack: **はい、sample内の2 search frame**。全時刻lossを置く。
- MambaLCT: **temporal queryを渡す**が、detachしており、Mamba cacheの長い微分可能state carryとは異なる。

### state汚染対策はあるか

- MCITrack: **ある**。low confidenceならhidden reset、template追加もconfidence gateで制御する。
- Re3: fixed intervalのre-initializationと、訓練時のprediction/noise crop混合がある。
- MambaLCT: long-term memoryはあるが、確認範囲のinference memory更新はscore gatedではない。
- 現行MambaStateful: matching成功のaccepted detectionにも、失敗時self predictionにもconfidenceを使ったstate guardがない。

## 現行モデルへの優先的な含意

1. **観測へのstate更新をconfidence-gatedにする**ことはMCITrackの直接的な先例であり、現行の`accepted detection / self prediction`の混在問題に最も近い。
2. **短いstateful unroll + 全時刻loss**はMCITrack・Re3にも共通する。現行のloss sliceを全時刻へ変える前に、まずstateをwindow外へどう持ち出すか／detachするかを設計する必要がある。
3. **prediction分布の学習への導入**はRe3が示す。MOTではGT noiseだけでなく、accepted detectionの誤差・欠測区間を模すのが対応物になる。
4. SOTのself-prediction cropをMOTのmatchingへ直結することはできない。MOTにはassociationによる誤観測という追加の汚染経路がある。

## 未決事項

- MCITrack/MambaLCTはSOTであり、MOTのmatching、ID switch、accepted detectionを評価しない。
- MambaLCTの`track_query`がtraining batch/sequence境界で外側からresetされるかは、inspected actor/model pathでは確認できなかった。存在しないと断定せず、実装上の確認事項として残す。
- 現行Mambaのcacheを微分可能なTBPTT stateとして使えるかは、まだ未確認である。

## 関連成果物

- [Re3](../individual/2026-07-17-04-re3.md)
- [MCITrack](../individual/2026-07-17-05-mcitrack.md)
- [MambaLCT](../individual/2026-07-17-06-mambalct.md)
- [Batch 1 RNN/LSTM/Seq2Seq比較](2026-07-17-01-rnn-lstm-basics.md)
