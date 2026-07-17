---
date: 2026-07-17
project: sam2-mamba-motion-tracking
status: completed
tags: [paper-note, sequence-learning-survey, pytorch, seq2seq, teacher-forcing, batch-1]
---

# PyTorch公式 Seq2Seq: Teacher ForcingとFree Running

## 対象と公式性

- tutorial: [Translation with a Sequence to Sequence Network and Attention](https://pytorch.org/tutorials/intermediate/seq2seq_translation_tutorial.html)
- repository: `pytorch/tutorials`
- repository owner: `pytorch`
- branch / commit: `main` / `8e14c2a355fe79268016e2be53a11797285ef428`
- license: BSD-3-Clause
- clone: `/mnt/HDD10TB-2/aburatani/research/external-repos/sequence-learning/sequence-prediction/pytorch-tutorials`

この公式tutorialのdecoderはGRUだが、teacher forcing/free runningの入力規則とloss配置はRNN/LSTM decoderにも共通する。

## コードから確認できること

| 項目 | 訓練時 | 推論時 | 根拠 |
| --- | --- | --- | --- |
| decoder初期入力 | `<SOS>` | `<SOS>` | `seq2seq_translation_tutorial.py:382-389` |
| decoder state | encoder final hiddenで初期化 | 同じ | `:382-385` |
| 次時刻入力 | target token（teacher forcing） | 前時刻のargmax prediction | `:392-402` |
| self predictionのgradient | 該当なし | `detach()`したtokenを再入力 | `:396-398` |
| loss対象 | decoderの全出力位置をflattenしてNLL loss | 生成評価ではtarget lossを計算しない | `:612-636, 724-750` |

## 重要な整理

Teacher forcingは「stateを持ち越さない」ことではない。decoder hiddenは各decode stepで連続して更新される一方、**次入力だけを正解targetに置き換える**手法である。

公式tutorialの訓練では常に`target_tensor`をdecoderへ渡すためfull teacher forcingである。各時刻のdecoder outputを保存し、target sequence全体にNLL lossを計算する。評価ではtargetを渡さず、predictionを次入力に再利用するfree runningである。tutorial自身も、teacher forcingは収束を速め得る一方で推論時の不安定性を生み得ると説明している。

## 現行MambaStatefulへの示唆

- 現行学習はGT bbox列を入力とするため、motion predictor単体としてはteacher-forcing相当である。
- MOTの通常推論でmatching成功した場合は、次入力はGTでもmodel predictionでもなく**accepted detection**である。この第三の入力種別をteacher forcing/free runningの二分法に無理に押し込めない。
- self predictionを連続利用するfree runningは、通常MOTの全時刻評価ではなく、accepted detectionが欠けた区間のrollout診断として分けるべきである。
- scheduled samplingは、このtutorialのコードには実装されていない。必要性はBatch 3以降のsequence prediction手法で別に調査する。
