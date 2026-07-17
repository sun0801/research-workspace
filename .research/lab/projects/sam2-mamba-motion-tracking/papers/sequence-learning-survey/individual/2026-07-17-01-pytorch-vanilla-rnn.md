---
date: 2026-07-17
project: sam2-mamba-motion-tracking
status: completed
tags: [paper-note, sequence-learning-survey, pytorch, rnn, batch-1]
---

# PyTorch公式 Vanilla RNN

## 対象と公式性

- PyTorch API: [torch.nn.RNN](https://docs.pytorch.org/docs/main/generated/torch.nn.RNN.html)
- 公式実装例: `pytorch/examples` の `word_language_model`
- repository owner: `pytorch`
- branch / commit: `main` / `acc295dc7b90714f1bf47f06004fc19a7fe235c4`
- license: BSD-3-Clause
- clone: `/mnt/HDD10TB-2/aburatani/research/external-repos/sequence-learning/rnn-lstm-baselines/pytorch-examples`

## コードから確認できること

| 項目 | 確認結果 | 根拠 |
| --- | --- | --- |
| recurrent update | 各時刻で`x_t`と`h_{t-1}`から`h_t`を計算 | API docs `RNN` |
| 一括 / step入力 | 両方可能。入力全体で`output[t]`、最終stateで`h_n`を返す | API docs `RNN` outputs |
| many-to-many | `output`は各時刻のhidden state。言語モデル例は各時刻をdecoderへ通す | `model.py:48-54` |
| initial state | `hx`を与えない場合はzero initial state | API docs `RNN` inputs |
| carry | forwardが返す`hidden`を次chunkの入力に渡す | `model.py:48-54`, `main.py:169-185` |
| detach | chunk開始時に`hidden.detach()` | `main.py:117-123, 171-186` |
| loss | shifted targetの全BPTT時刻をflattenしてNLL loss | `main.py:109, 136-140, 171-186` |

## 学習方法の読み解き

公式言語モデルは、長い時系列をbatchifyして各列を連続streamとして扱う。`bptt`長のchunkごとに、前chunkのhiddenを次chunkへ渡す。ただし、chunk開始時にhiddenをdetachするため、gradientは過去全体へ遡らない。これは**状態はcarryし、勾配だけをchunk境界で切るTBPTT**である。

lossは、各入力トークンの次トークンをtargetにした全chunk時刻のNLL lossである。これはcurrent MambaStatefulの「warm-up後の全時刻delta loss」と同じmany-to-many側の設計であり、最終時刻だけのsupervisionではない。

## 現行MambaStatefulへの示唆

- 長い連続trajectoryでstateを持ち越したい場合、標準的な候補は「state carry + chunk境界detach」である。
- ただし言語モデルのstream列とMOTのtrack IDは異なる。MOTでは**trackごとにstateを分離**し、動画切替・track開始・lost/reset時を明示する必要がある。
- `loss_start_index=4`を維持するかは別途比較可能だが、全時刻にlossを与えるという基本方針自体は妥当である。

## 制約

この例はtoken言語モデルであり、accepted detection・matching・欠測時self predictionを持たない。MOTへの移植候補はTBPTTのstate/detach規則であり、association方針ではない。
