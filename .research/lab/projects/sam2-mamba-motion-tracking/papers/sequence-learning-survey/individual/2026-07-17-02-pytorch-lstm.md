---
date: 2026-07-17
project: sam2-mamba-motion-tracking
status: completed
tags: [paper-note, sequence-learning-survey, pytorch, lstm, batch-1]
---

# PyTorch公式 LSTM

## 対象と公式性

- PyTorch API: [torch.nn.LSTM](https://docs.pytorch.org/docs/stable/generated/torch.nn.modules.rnn.LSTM.html)
- 公式実装例: `pytorch/examples` の `word_language_model`
- repository owner: `pytorch`
- branch / commit: `main` / `acc295dc7b90714f1bf47f06004fc19a7fe235c4`
- license: BSD-3-Clause

## RNNとの差

LSTMはhidden state `h_t`に加えcell state `c_t`を持つ。PyTorch APIのforwardは各時刻のoutputと、最終`(h_n, c_n)`を返す。学習・推論でstateを持ち越す際は、このtuple全体を同じ単位で扱う。

公式`word_language_model`では、`--model LSTM`時に`nn.LSTM`を選択し、`init_hidden`が各layer・batchのzero `(h_0, c_0)`を返す。その後のstate carryとdetach規則はVanilla RNNと共通である。

| 項目 | 確認結果 | 根拠 |
| --- | --- | --- |
| model選択 | `nn.LSTM` | `model.py:14-22` |
| initial state | zero `(h_0, c_0)` | `model.py:56-62` |
| forward return | 時刻別outputと更新済み`hidden` tuple | `model.py:48-54` |
| state carry | 次BPTT chunkへ`hidden`を渡す | `main.py:169-185` |
| detach | tupleを再帰的に`.detach()` | `main.py:117-123, 171-186` |
| loss時刻 | 全chunk時刻の次token NLL | `main.py:136-140, 185-186` |

## 現行MambaStatefulへの示唆

- LSTMのcell stateを増やすことが解決策なのではない。重要なのは、**状態をどのtrajectoryに属するものとして持ち、どこでdetach/resetするか**である。
- 通常forwardでwindow内だけstateを展開する現行学習は、LSTMであっても同じtrain/inference mismatchを生む。
- Mambaのcacheがautograd対応か未確認なため、LSTMのTBPTTをそのまま`InferenceParams`へ適用できるとは結論しない。微分可能なstate表現または再計算型state展開を別途検討する必要がある。

## 制約

公式例は完全な連続テキストstreamを前提とする。MOTのlost/再検出・track ID変化には直接答えない。
