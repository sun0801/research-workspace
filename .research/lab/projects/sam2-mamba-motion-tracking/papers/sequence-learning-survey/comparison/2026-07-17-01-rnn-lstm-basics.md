---
date: 2026-07-17
project: sam2-mamba-motion-tracking
status: completed
tags: [paper-note, sequence-learning-survey, comparison, rnn, lstm, seq2seq, batch-1]
---

# Batch 1 横断比較: RNN・LSTM・Seq2Seq

## 回答

| 調査問い | 結論 |
| --- | --- |
| next-step predictionで各時刻にlossを与えるか | 公式言語モデル・Seq2Seqはいずれも各予測時刻にlossを与える。現行MambaStatefulもwarm-up後の全7時刻にlossを与えており、この点はmany-to-manyとして妥当。 |
| 最終時刻だけのlossはいつ使うか | sequence分類やsequence全体を1つの表現へ圧縮するmany-to-oneで自然。次時刻deltaを毎時刻出すmotion predictionの第一候補ではない。 |
| RNN/LSTMで学習方法は異なるか | stateの中身はRNN=`h`、LSTM=`(h,c)`で異なるが、sequence reset、carry、TBPTT detach、時刻別lossの原則は共通。 |
| stateをsequence間で持ち越す例 | PyTorch公式language modelは連続streamのchunk間でhiddenをcarryし、各chunk開始でdetachするTBPTT。 |
| teacher forcingの次入力 | decoderの前時刻予測ではなく正解target。state自体は時系列に継続更新する。 |
| free runningとの差 | 推論では自己予測を再入力するため誤差が入力分布へ戻る。公式Seq2Seqはこのギャップを明示している。 |

## 現行モデルとの対応

| 観点 | PyTorch公式例 | 現行MambaStateful | 判断 |
| --- | --- | --- | --- |
| 時刻別loss | full chunk / full decoder target | warm-up後 index 4–10 | loss配置は主問題ではない |
| training state | LMはstream間carry + detach | shuffled windowでreset | TBPTTを比較する根拠あり |
| training input | 正解履歴（teacher forcing） | GT bbox | 同種だがMOTの観測雑音は未学習 |
| inference input | LMは生成token、Seq2Seqはpred token | accepted detection / self prediction | 現行は三分類で考える必要がある |
| free running | 生成の主経路 | 欠測時だけが相当 | MOT通常経路と混同しない |

## Batch 2への持ち越し問い

1. Re3等のtrackingでは、observed crop / bboxをどの時点でstateへ反映するか。
2. Mamba trackerは学習時にもframe間stateをcarryするか、それともwindow forwardか。
3. observation-first matching、confidence gate、lost時resetを実際に持つtrackerはあるか。

## 関連成果物

- [Vanilla RNN](../individual/2026-07-17-01-pytorch-vanilla-rnn.md)
- [LSTM](../individual/2026-07-17-02-pytorch-lstm.md)
- [Seq2Seq](../individual/2026-07-17-03-pytorch-seq2seq.md)
- [Batch 0 現行実装マップ](2026-07-17-00-current-implementation-map.md)
