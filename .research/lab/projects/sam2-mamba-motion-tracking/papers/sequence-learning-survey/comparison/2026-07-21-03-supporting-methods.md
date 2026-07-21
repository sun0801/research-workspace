---
date: 2026-07-21
project: sam2-mamba-motion-tracking
status: completed
tags: [paper-note, sequence-learning-survey, comparison, batch-3, teacher-forcing, free-running]
---

# Batch 3 補助手法の分類: video prediction・trajectory prediction・SOT

## このバッチの位置付け

本バッチは、現在の MOT 用 State Carry 実装へそのまま移植する手法を探すものではない。周辺分野での **教師信号・予測値の再入力・状態の持ち方** を、現行の `GT / accepted detection / self prediction` という三種類の入力と混同しないための分類である。

以下は公式実装を静的に確認した結果であり、学習・評価は実行していない。

## 参照実装

| 手法 | 公式性の根拠 | 確認commit |
| --- | --- | --- |
| PredRNN / PredRNN++ | [THUML公式実装](https://github.com/thuml/predrnn-pytorch) | `49d3b0f3a2757ad9c299716ec455a96868455d67` |
| Social GAN | [著者公開実装](https://github.com/agrimgupta92/sgan) | `691231e1adb6a344c7bcea9ebf2534518b226ead` |
| Trajectron++ | [Stanford ASL公式実装](https://github.com/StanfordASL/Trajectron-plus-plus) | `1031c7bd1a444273af378c1ec1dcca907ba59830` |
| ARTrack | [著者公式実装](https://github.com/MIV-XJTU/ARTrack) | `5931f4af8dd3f3f04af52f9ca7d6f2d5da54592e` |
| Mamba-FETrack | [論文が案内する公開実装](https://github.com/Event-AHU/Mamba_FETrack) | `175797191425a55087ee8a6a01d0fe7c2d7bd1c5` |

取得先は `/mnt/HDD10TB-2/aburatani/research/external-repos/sequence-learning/` 以下であり、参照用の浅いcloneのみを行った。

## 横断比較

| 手法 | 学習時の時系列状態 | 学習時の次入力 | loss | 推論時のフレーム間状態 | 現行への位置付け |
| --- | --- | --- | --- | --- | --- |
| PredRNN | sample内でST-LSTM state/memoryを時系列更新。sample開始時はzero | scheduled samplingでGT frameと直前生成frameを混合 | 全ての次frame出力に対するMSE | この実装の標準評価はsample内のrollout。track ID単位の永続cacheではない | **予測値を学習入力へ混ぜる**先例 |
| PredRNN++ | PredRNNと同じ分類。reverse scheduled samplingを利用可能 | `mask_true`でGT / 生成frameを時刻ごとに選択 | 全時刻MSE | 同上 | TF/free-running比率を制御する先例 |
| Social GAN | 観測軌跡をLSTM encoderへ入力し、future decoder内で状態を更新 | decoderは直前の**自分の予測相対変位**を次入力にする | future全時刻のL2（best-of-K）+ GAN loss | 1つの観測windowからfuture horizonをrollout。動画をまたぐ永続hidden stateではない | **train時からfree-running**の明確な先例 |
| Trajectron++ | history encoderとfuture GRU decoder。decoder stateをfuture horizon内で更新 | 前時刻にsampled actionを再入力（robot futureを含む設定ではその条件も追加） | future全時刻のGMM対数尤度を和、ELBO化 | online実行はあるが、ここで確認したdecoder stateは予測horizon内の状態 | probabilistic rollout。MOTのaccepted detectionとは別概念 |
| ARTrack (V1) | frame pairごとのTransformer。座標token decoderの因果状態はbbox 4 token内 | 学習時は開始token + **GT座標token列**、推論時は開始tokenから予測tokenを逐次追加 | 座標token CE + box IoU/L1系 | 前frameの予測bboxで次frameのsearch cropを作る。hidden/cacheは保持しない | token内TF/free-runningと、crop feedbackを分けて考える先例 |
| Mamba-FETrack | template/search（RGB + event）pair内のMamba feature extraction/fusion | 次frameへ渡すMamba cache入力は確認経路にない | 1 template・1 searchのbox / heatmap loss | 前予測bboxで次search cropを作る。tracker呼び出しに`inference_params`は渡していない | **Mamba使用 = State Carryではない**反例 |
| 現行MambaStateful | 12-box window内のMamba。学習sample間はstate reset | GT bbox deltaのみ | warm-up後7時刻のSmooth L1 | trackごとのMamba cache。matching成功ならaccepted detection、失敗ならself prediction | 比較対象 |

## 実装から確認した根拠

### PredRNN / PredRNN++: scheduled sampling は「状態を止める」仕組みではない

`core/models/predrnn.py:41-75` はforwardごとに `h_t`、`c_t`、`memory` をzeroで初期化し、同一sample内の全時刻で更新する。各時刻の次入力は、`mask_true * GT frame + (1-mask_true) * x_gen` であり、最後に生成した全next frameと全GT next frameのMSEを計算する。

`run.py` はPredRNNにscheduled sampling、PredRNN++にreverse scheduled samplingを渡す。したがって、ここから得るべき点は「stateをsample外までcarryする」ことではなく、**教師信号だけの入力分布と自己予測を含む入力分布の間を、時刻・訓練進行に応じて連続的に調整する**ことである。

### Social GAN: future horizonの最初からfree-running

`sgan/models.py:125-162` のdecoderは、最終観測相対位置から開始し、各future stepで得た `rel_pos` を次stepの入力へ戻す。GT futureをdecoder入力へ代入する分岐はない。`scripts/train.py:400-435` は生成future軌跡とGT future軌跡の全時刻L2を計算し、best-of-Kで集約する。

これは「trainingではGTを再入力し、testでだけpredictionを再入力する」設定ではなく、**lossをGTに置きつつ、状態遷移の入力分布は初めからmodel-induced**である例である。ただし、MOTの観測受理やassociationは存在しない。

### Trajectron++: sampled futureを再入力し、全horizonの尤度で学習する

`trajectron/model/mgcvae.py:779-861` のGRU decoderは、各時刻のGMMから `rsample()`（predict modeの設定時はmodeも選択可）した `a_t` を次時刻入力に使う。`decoder()` はfuture labelの各時刻対数尤度を計算して時刻方向に和を取り、`train_loss()` はそれをELBOの尤度項にする（同:924-1004）。

したがって、同手法もfuture GTそのものを逐次decoder入力へ強制する単純なteacher forcingではない。ただしこれはマルチモーダルな軌道予測であり、MOTの検出器出力・track association・ID維持を扱わない。

### ARTrack: 自己回帰の単位は「4座標token」であり、動画stateではない

V1のactorはGT bboxを量子化し、`[begin, gt_x1, gt_y1, gt_x2, gt_y2]` を`seq_input`、一つshiftした列をtargetとしてモデルへ渡す（`lib/train/actors/artrack.py:210-230`）。headはcausal mask付きdecoderでこのGT prefixを読む（`lib/models/layers/head.py:800-819`）。推論時はbegin tokenから4回、直前の予測tokenをappendする（同:820-840）。これは座標token内ではteacher forcing / free-running差がある。

一方、trackerは前frameの`self.state`からsearch cropを作り、出力bboxを次の`self.state`へ無条件更新する（`lib/test/tracker/artrack.py:120-150`）。呼び出しごとのhidden/cache保存は確認されなかった。よってARTrackは「前予測bboxによる視野feedback」の先例ではあるが、Mamba cacheをtrackごとにcarryする現在の問題の直接解ではない。

### Mamba-FETrack: SSMの内部stateとフレーム間state carryを区別する

Mambaモジュール自体は`inference_params`を受け取れる実装を含む。しかし、公式actorは1 template・1 searchだけをassertし（`lib/train/actors/mamba_fetrack.py:38-80`）、trackerの各frame呼び出しもtemplate/searchを通常forwardするだけで`inference_params`を渡さない（`lib/test/tracker/mamba_fetrack.py:82-112`）。そのtrackerが跨frameで保持するのは前予測bbox `self.state`であり、次search cropに用いる。

従って、調査対象の実行経路ではMambaはframe/eventのtoken特徴抽出・融合に使われるが、**MambaのSSM stateを時刻をまたいでcarryするモデルではない**。Mambaを採用した追跡手法を、State Carry学習の先例として自動的に数えてはいけない。

## 現行モデルへ残る結論

1. **teacher forcing と state carry は別軸である。** PredRNN、Social GAN、Trajectron++はいずれもsample / forecast horizon内で状態を更新するが、sample境界を越えるtrack stateの管理問題は直接解かない。
2. 現行の `GT / accepted detection / self prediction` は、scheduled samplingのGT / generatedという二値より一段多い。導入するなら、少なくとも`accepted detection`をGTと同一視せず、confidence・IoU・track ageなどに基づく第三の入力分布として設計・計測する必要がある。
3. **全時刻lossは必要条件ではあるが十分条件ではない。** PredRNN・Social GAN・Trajectron++はいずれもrolloutの各時刻を損失で拘束する。現行の7時刻lossもこの原則から外れてはいない。主な未解決点は、学習時にself/accepted-detection由来の入力分布とtrack stateの更新規則をどう再現するかである。
4. ARTrack/Mamba-FETrackは、前予測bboxをcropへ戻すため、誤差が次frameの入力へ波及する点は共有する。しかしassociationを持たないSOTなので、MOTへは信頼度ゲート・再同定・ID単位のcache隔離を追加して初めて対応関係が作れる。

## 次バッチへ持ち込む設計論点

- state carryを**短いunroll内に限定してdetachするTBPTT**にするか、現行どおりfixed windowだけで教師あり学習するか。
- training入力を `GT / noisy accepted detection surrogate / self prediction` のどの比率で混合するか。その比率を訓練進行でscheduleするか。
- cacheを更新・freeze・resetする判定を、match confidence、prediction uncertainty、連続miss数のどれで定義するか。
- それぞれについて、one-step box errorとtracker HOTA/IDF1を分けて検証するか。

## 関連成果物

- [Batch 0: 現行実装の経路図](2026-07-17-00-current-implementation-map.md)
- [Batch 1: RNN/LSTM/Seq2Seq](2026-07-17-01-rnn-lstm-basics.md)
- [Batch 2: Re3/MCITrack/MambaLCT](2026-07-17-02-direct-tracking-comparison.md)
