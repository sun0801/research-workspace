---
date: 2026-10-18
project: sam2-mamba-motion-tracking
source: brainstorm
status: approved
approved: 2026-10-18
revised: 2026-10-18
tags: [spec, experiment, temporal-mamba, sam2, mose, fpn, adapter]
---

# V3（FPN的なtemporal Mamba）のMOSE adapter学習 Spec

## 目的

FPNの各段でMambaを回すV3を、SAM2本体をF0で固定した状態で学習する。これを、次の2つを調べる**探索実験**として行う。

- F0にV3を足した価値
- 学習済みV3が、Mambaのstateの持ち越しにどれだけ依存しているか

あわせて、共通の計算経路の正しさを確かめ、学習の高速化を入れて、今後の候補（V2・V4など）の比較を回しやすくする。今回の結果は、同じtuningを使った探索的な比較であり、独立した評価での優越性は主張しない。

## 背景

- 10/9 MTG：MOSEのF1はadapterのLR（5e-6）が小さすぎて実質学習されておらず、Mambaの効果は未検証のまま。temporal Mambaは探索フェーズとし、LRを直したうえで複数の統合方法を試す方針になった。
- 10/14 MTG：V3（FPN的な統合）から始め、難しければ他の案に移る。来週までにある程度形にする。
- 統合方法の候補はV1〜V4に整理した（[brainstorm](../../../../secretary/notes/brainstorm/2026-10-18-temporal-mamba-integration-variants.md)、[図](../materials/figures/2026-10-14-temporal-mamba-variants/manifest.md)）。V3は9/30 MTGの「FPNなどを工夫し、サイズを削減せずに入れる」の解釈で、各段でMambaを回し、段どうしをつなぐ形。
- 既存adapterに、学習と推論で計算経路が違う箇所があった（2026-10-18のレビューで発見し、コードで確認）。
  - 推論の `step()`（`temporal_mamba_adapter.py` 147〜150行）は、Mambaの出力に外側の `self.output_proj` をかけてから残差にする。
  - 学習の `training_step()`（270〜272行）は、`self.output_proj` を通さずに残差にしている。
  - このため、F1の学習では `output_proj` が使われず更新されなかった。一方、F1の評価では学習されていない `output_proj` が推論時にかかっていた。10/9の事後診断で見た「出力層の重みがほぼ不変」は、LRが小さかったことに加え、この未使用経路も原因の候補になる。F1のスコアへの影響量は確定していない（αが約2e-4以下と小さかったため、影響は小さいと見込まれるが未検証）。
- 前回のF1の学習は1周（2,789軌跡・200,794フレーム）で60,580秒（約16.8時間）、約0.30秒/フレームかかった。CPUでのデータ読み込みだけで約0.14秒/フレーム（1動画60フレームで測定）かかり、メインスレッドで同期的に処理しているため、その間GPUが待っている。SAM2公式の学習コードは、DataLoaderのworker 10個、clip単位でのまとめ計算、`freeze_image_encoder` を持つが、今の `mose_fulltrack.py` は軌跡全体のTBPTT用に書き直した際にこれらが抜けている。
- 今のスクリプトは公式のMOSE学習configを読み込み、`model.train()` で学習する。そのため、画像エンコーダのDropPath（`drop_path_rate: 0.1`）とmemory attentionのDropout（`dropout: 0.1`）が有効になっている。パラメータを固定しても、`no_grad` にしても、これらの乱数処理は止まらない。

## 検証したい問い

- FPN的なtemporal Mamba（V3）を足すと、F0よりマスクの品質が上がるか。
- 学習済みV3は、Mambaのstateをフレーム間で持ち越すことに依存しているか。

## 仮説

- H1（追加効果）：V3はF0を上回る（tuningの動画平均J&F）。
- H2（stateへの依存）：V3（stateを持ち越す）は、V3-reset（同じ重みで推論時だけ毎フレームstateをリセット）を上回る。
- H3（副次）：同じ学習レシピのもとで、V3はV1（1 token）を上回る。

H2は「Mambaのstateを持ち越すことへの依存」を調べる診断である。V3-resetは、stateを持ち越す前提で学習した重みを、推論時だけ異なるstateの分布で動かす介入であり、性能の低下には「過去の情報を失った影響」と「学習時と違うstateの分布になった影響」の両方が含まれる。また、リセットするのはMambaのstateだけで、SAM2自身のmemoryは残る。したがって、H2が支持されても「時間方向の記憶が有用である」ことの単独の証拠とはしない。

## 実験・実装内容

SAM2 repo（`/mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2`）で、`dev` から新しいブランチを切って実装する。

### 1. 共通の枠

- `MambaCell`：今の `TemporalMambaAdapter._mamba_training_step` を切り出し、`[系列の本数, C]` の入力を1歩進める部品にする。SSMのstateはFP32、convのstateは計算時のdtype（bf16）で持つ。
- `TemporalAdapterBase`：`init_state()`・`step(特徴, state) → (特徴, state)`・`reset()` を全手法で共通にする。学習と推論は**同じforward**を使い、推論ではそれを `no_grad` で回すだけにする（今の推論専用cacheの経路は使わない）。
- 残差の形：`特徴 + α・W_out(LayerNorm を通した入力に対するMambaの出力)`。
  - `W_out` は1×1の線形射影で、重みとbiasをゼロで初期化する。
  - αは学習可能なスカラーで、初期値は1。
  - 初期状態では残差がゼロなので、出力はF0と一致する。
- `reset_every_frame` フラグを付け、毎フレームstateを初期化した版を作れるようにする。
- adapter呼び出しの分岐は、`self.training` ではなく明示的な引数で切り替える（SAM2本体をevalにしてもadapterの学習経路が選ばれるようにするため）。

### 2. `GlobalPoolAdapter`（V1）

今の1 tokenの処理（空間平均 → LayerNorm → `MambaCell` → `W_out` → 全マスに同じ値を足す）を共通の枠に移す。

### 3. `PyramidAdapter`（V3）

- 対象の段：64段（`pix_feat`、256ch。Memory Attentionの後の対象別特徴）、128段（`feat_s1`、64ch）、256段（`feat_s0`、32ch）。128段と256段は、画像エンコーダのFPN特徴を `conv_s1` / `conv_s0` で射影した後の特徴で、対象の情報は含まない。
- 各段に `LayerNorm → MambaCell → W_out` を1組ずつ置く。各マスをbatch次元に畳み、マスごとに時系列を持つ（`expand=2`、`d_state=16`、`d_conv=4`）。
- 段のつなぎ方は(a)：上の段の**Mambaの出力**（`W_out` の前）を×2にbilinearで拡大し、1×1 conv（bias付き、標準の初期化）で下の段のチャネル数に合わせて、下の段のLayerNorm後の入力に足す。これにより、64段の対象の情報が128段・256段にも伝わる。
- 各段の結果は、その段の特徴に `α_k・W_out,k(…)` として足す（段ごとにαを持つ）。
- 挿入位置は対象ごと（現行の位置b）。

### 4. SAM2本体の固定とモード

- `--freeze-sam2` のとき、SAM2本体の全パラメータを `requires_grad=False` にする。
- SAM2本体のsubmoduleはすべて `eval()` にし、DropPathとDropoutを止める。adapterだけ `train()` にする。学習ループの中で `model.train()` が呼ばれても、SAM2本体のevalが戻らないようにする。
- 画像エンコーダの計算は `no_grad` にする（その手前に学習するパラメータがないため）。
- デコーダ、memory encoder、memory attentionは勾配を流せる状態のままにする。adapterの出力が、デコーダを通してlossに届き、memoryを通して次のフレームのadapterにも届くようにするため。
- TBPTTの区間の境界では、今と同じようにMambaのstateとSAM2のmemoryをdetachする。

### 5. `sam2_base.py`

adapterが `pix_feat` と `high_res_features` の両方を受け取り、書き換えて返せるようにする。stateは段ごとにまとめて持つ。

### 6. `training/mose_fulltrack.py`

次のオプションを追加する。

- `--adapter-type {v1,v3}`、`--v3-levels`（使う段の組み合わせ）
- `--freeze-sam2`
- `--adapter-lr`、`--warmup-steps`、`--max-steps`（学習に使う軌跡の数）
- 高速化
  - ① DataLoaderによる先読み：`load_frame` を別のworkerで先に処理する。軌跡の順序、フレームの順序、augmentationのretry、プロンプトのtensorは変えない。
  - ② `--freeze-sam2` のとき、画像エンコーダを `no_grad`・evalにして、TBPTTの1区間（8フレーム）ごとにまとめて計算する。
  - ③ フレームごとにGPUを待たせる処理（lossやfinite判定の `.item()` / `.cpu()`）を、区間ごとにまとめる。

### 7. 学習経過の記録（Comet）

- Mamba_Trackersと同じ形でCometに記録する。APIキーは `~/.comet.config` から読む。記録先はSAM2 repoの `.comet.config` で一元管理し、既存のプロジェクト `samurai-mot`（workspace `sun0801`）に統合する。MOT推論の記録と区別するため、全experimentにタグ `temporal-mamba` を付け、Cometではこのタグで絞り込んだ表示で見る。
- 記録の形はsimple_cnnに揃え、横軸はstep（1 step＝1更新＝1軌跡）とする（2026-10-22改訂）。`epoch`（step÷fitの軌跡数2,789）を補助の値として記録する。
  - train（毎step）：`train_loss_step` とlossの内訳（`train_loss_mask_step`・`train_loss_dice_step`・`train_loss_iou_step`・`train_loss_class_step`。公式SAM2のtrainerと同じ内訳）、`train_J_step`（学習中の予測マスクと正解の、1024解像度でのIoU。先頭フレームを除く）、`train_lr`。
  - train（valの区間ごと）：`train_loss_avg`、`train_J_avg`（直前のvalからの平均。simple_cnnの `_epoch` に当たる）。
  - val：`val_loss` とその内訳、`val_J`・`val_F`・`val_J&F`（下の「学習中のval」）。
  - 診断用（25 stepごと）：`diag/…`（各段のα、残差の大きさ、各部の勾配ノルム、初期値からの重みの変化量）、`system/…`（1フレームあたりの時間、VRAMのピーク）。
  - pilotの診断用loss（学習に使った16軌跡で測るもの）は `pilot/…` として分ける。
- valのたびにadapterのcheckpointを保存し、Cometにも上げる（simple_cnnと同じ）。実行時の引数、gitのcommit、manifest、`git.diff` も保存する。
- Cometに接続できなくても学習は止めない（記録だけ無効になる）。`--no-comet` で無効化できる。

### 8. 学習中のval（2026-10-22追加）

- 目的：学習につれてadapterが効いてくるかを、学習中に確認する（simple_cnn・公式SAM2 trainerのvalと同じ位置づけ）。
- データ：tuningの先頭25動画（64対象、5,159フレーム）。F0の学習には使っていない。tuningは最終評価にも使うため、**valは経過を見るためだけに使い、途中のcheckpointの選択や学習の打ち切りには使わない**（最終評価には最後のstepの重みを使う、という既存の規則のまま）。fitの一部はF0が学習済みのため、MOSE公式のvalidは先頭フレームにしか正解がないため、使わない。
- 計算：評価と同じ経路（SAM2本体はeval、勾配なし、augmentationなし、プロンプトのseedは評価と同じ `1000003 + i`、先頭フレームはJ・Fから除外、動画単位で平均）で、J・F・J&Fと、学習と同じloss（とその内訳）を計算する。
- 頻度：学習前（step 0。adapterは初期化直後でF0と同じ出力になるので、F0の基準値になる）、250 stepごと、最終step。所要は1回あたり約10分の見込み。
- 確認：step 0のvalのJ・Fが、保存済みのF0のtuning結果（A4000）の該当25動画と一致することを確かめる。

### 9. 評価・集計

- `training/eval_mose_fulltrack.py`：条件 V1・V3・V3-reset（と、使う段を減らした場合の条件）を評価できるようにする。
- `training/summarize_mose_fulltrack.py`：今は条件名（`P0/F0/F1/F1-reset`）と比較の組（`F1−F0`、`F1−F1-reset`、`F0−P0`）が固定されているので、条件名・比較の組・入力パスを引数で指定できるようにする。比較の前に、125動画・313対象の期待するID集合、frameの網羅率、プロンプト、除外理由が条件間で一致することを確認する。

## 使用データ・モデル

- データ：MOSEv1（`/mnt/HDD10TB-2/aburatani/dataset/MOSE-v1-data/MOSE_release`）。前回と同じfit・tuningの分け方を使う。lockboxは使わない。
- ベースモデル：F0 step 2789（`runs/mose_temporal_mamba_20260930/F0_step_002789.pt`、SHA-256 `5d4cd955a177d40afddba65082df647a64bf6774a40dd210a9099543c8bc0ae9`）。
- プロンプトなどの条件：1対象、先頭フレームのboxのみ、後続フレームでのGT補正なし、解像度1024、TBPTT=8、bf16（前回と同じ）。
- GPU：学習はGPU1（RTX PRO 4500、32GB）。GPU0（RTX A4000、16GB）は評価に使えるかを段階1で確認する。

## 比較対象・ベースライン

| 条件 | 中身 | 新たに学習するか |
|---|---|---|
| F0 | F0 step 2789。adapterなし | 不要。ただし、新しい評価経路でadapterを無効にしたときに旧F0の結果と一致することを確認してから、既存のtuning結果を再利用する。一致しなければ新しい評価経路で評価し直す |
| V1 | F0を固定し、1 tokenのadapterを学習 | 要 |
| V3 | F0を固定し、`PyramidAdapter` を学習 | 要 |
| V3-reset | V3と同じ重みで、推論時だけ毎フレームstateをリセット | 不要（評価のみ） |

- V1とV3は、F0＋新しく初期化したadapterから、同じ軌跡の列・同じ更新回数N・seed（123）・LRの設定・augmentationで学習する。段階0bのpilotの重みは引き継がない。
- 同じLRを使うことは「共通のレシピでの比較」であり、両構造それぞれの最適な性能を比べたことにはならない。
- 段階1で使う段を減らした場合は、条件名を `V3-64-128`、`V3-64-only` のように分ける。`V3-64-only` は段どうしの接続がなくなり、実質的にV2の64×64グリッド案に近いので、3段のV3の結果としては扱わない。

## 評価指標

- tuning（125動画・313対象）での動画平均J&F。JとFも併記する。差は百分率ポイントで示す。
- 条件間の差は、動画単位のpaired bootstrap（10,000回、seed 123、95% percentile）で信頼区間を出す。この信頼区間が表すのは、固定した重みと条件のもとでの動画間のばらつきだけで、設計の選び方や学習seedの不確かさは含まない。
- 補助指標：
  - 各段の残差の大きさ（`‖α・W_out(…)‖ / ‖特徴‖`）とαの値
  - 推論時間（1フレームあたり）
  - 学習時のVRAMのピークと、1フレームあたりの学習時間

## 成功/失敗の判断基準

| 観察 | 言えること |
|---|---|
| H1・H2とも支持（V3−F0、V3−V3-reset の95%信頼区間の下限がいずれも0より大きい） | この評価で、V3の追加効果を確認した。学習済みV3はMambaのstateの持ち越しに依存している。時間方向の記憶が有用であることと整合するが、その仕組みの切り分けは済んでいない |
| H1のみ支持 | V3の追加効果を確認した。Mambaのstateの持ち越しによる追加の寄与は確認できない |
| H2のみ支持 | 学習済みV3はstateの持ち越しに依存しているが、F0を上回る実用的な追加価値は確認できない |
| どちらも支持されない | 今回の条件・予算・標本では改善を確認できない。学習不足、効果量の小ささ、推定の不確かさが残る |

- 支持されないことは「効果がない」ことの証明ではない。
- H3は、同じ学習レシピのもとでの比較に限る。V3とV1の差には、空間解像度だけでなく、使う特徴の段、パラメータ量、計算量、段どうしの接続の違いも含まれるので、H3が支持されても「空間情報を保ったことだけの効果」とは言わない。
- seedは1つだけなので、seedを越えた再現性は主張しない。
- F0のcheckpoint選択にも、今回の比較にも同じtuningを使うので、独立した評価での優越性は未確認として扱う。
- 時間方向の記憶の効果をより強く切り分けたくなった場合の追加候補として、**学習時から毎フレームstateをリセットする同じ構造の対照**を置く（今回は行わない）。

## 実施手順

| 段階 | 内容 | 判定 |
|---|---|---|
| 0a 正しさの確認 | 1. 実際の初期化（α=1、`W_out`=0）で、出力がF0と一致する<br>2. αと `W_out` をゼロでない値にして、同じ重み・入力・初期stateのとき、勾配ありと勾配なしの共通forwardで、複数フレームとTBPTTの境界をまたいだ出力とconv/SSMのstateが一致する<br>3. `reset_every_frame` で毎フレームstateが初期化されている<br>4. SAM2本体がevalのまま保たれ（`model.train()` の後も）、学習後もSAM2本体のパラメータが変化していない（ハッシュで確認）<br>5. 新しい評価経路でadapterを無効にしたとき、代表10動画で旧F0の結果と一致する<br>旧実装との互換（旧F1のlossの再現）は、新しい共通forwardの合格条件にしない | 全部通らなければ次に進まない |
| 0a' 高速化の確認 | 同じ新しいadapter・初期重み・固定条件・モード・optimizer・乱数条件のもとで、高速化①〜③のオンとオフを比べる。まずFP32・deterministicの設定で照合し、その後bf16で、logit・loss・勾配・更新後の重みの絶対誤差と相対誤差を記録する。DataLoaderで軌跡の順序、フレームの順序、augmentationのretry、プロンプトのtensorが変わらないことも確認する | FP32で一致し、bf16の差がその精度で説明できる範囲であること。説明できない差が出たら原因を調べるまで高速化を使わない |
| 0b LRの確認 | 固定した少数の軌跡（16本）で、V1とV3それぞれについてadapter LR 1e-4・3e-4・1e-3の短いpilotを行う（warmupは20更新）。同じ診断用の入力でlossを比べる | 採用するのは、lossがF0（adapterなし）より下がり、数値が有限で安定しているLR。あわせて、数回の更新の後に、各段のMamba・LayerNorm・`W_out`・段どうしの1×1 convに勾配が届き、重みがweight decay以外の理由で変化していることを確認する（最初の1回の更新ではMamba内部の勾配がゼロでも正常）。残差の大きさが育つだけでは合格としない |
| 1 実測 | V3で、短い・典型的な・長い（最長500フレーム）軌跡について、forward・backward・optimizerの更新を含めたVRAMのピークと1フレームあたりの時間を測る。推論時間も測る | VRAMのピークが30GiBを超えたら256段を外して `V3-64-128` として測り直す（それでも超えたら `V3-64-only`）。測った速度から共通の更新回数Nを決める |
| 2 学習 | V3で8時間以内に収まる更新回数Nを決め、V1も同じNで学習する。軌跡は前回保存したseed付きの並び順（`sample_order`）の先頭からN本を使い、使った軌跡のindexの一覧と合計フレーム数を記録する。optimizerはAdamW、weight decayは0.1（LayerNorm・bias・α・`A_log`・`D` は0）、勾配のclipは0.1、warmupの後はNまでcosineで0に下げる。1更新＝1軌跡（区間ごとにbackwardして勾配をためて、軌跡の最後に1回だけ更新する、今のやり方を踏襲） | 途中でcheckpointは選ばず、最後の更新の重みを使う（学習中のvalは経過の確認のみ）。pilot・評価・val・checkpointの保存にかかった時間は、8時間の学習予算とは分けて記録する |
| 3 評価 | V1・V3・V3-resetをtuningの313対象で評価し、F0と比べる | 上の基準で判定する |

GPUを使う実行（段階0bのpilot、段階1の実測、段階2の学習、段階3の評価）は、ユーザーが手元でtmuxを使って行う。実装が終わったら、各段階の実行コマンド（tmuxセッション名、GPU、出力先、ログの場所、終了後に確認すること）を渡す。

各段階の結果は実験ログ `experiments/2026-10-18-temporal-mamba-v3-mose-adapter.md` に記録する。学習結果はSAM2 repoの `runs/mose_temporal_mamba_v3_20261018/` に保存する。

## 期待される結果

- V3がF0を上回り（H1）、学習済みV3がstateの持ち越しに依存している（H2）。
- 高速化①〜③により、1フレームあたりの学習時間が前回（約0.30秒）より短くなる（どこまで短くなるかは未実測）。

## リスク・懸念

- stateのメモリが大きい。現行の設定（`expand=2`、`d_state=16`）を引き継ぐと、SSMのstateだけで64段128MiB・128段128MiB・256段256MiB、合計で約512MiB（FP32）になる。TBPTT=8で8フレーム分を保持するとそれだけで約4GiBになり、さらにautogradの中間値やSAM2本体の分が加わる。32GBに収まるかは段階1で測る必要がある。
- 各マスのstateは画面上の位置に固定されているので、物体が動くと、同じ位置が同じ物体の部位を指さなくなる。粗い段の広い受容野や、memoryで条件付けた特徴が補う可能性はあるが未検証。改善しなかった場合の原因の候補として残し、動きや遮蔽のある代表動画で、carry版とreset版の差や残差の位置を見ておくと、V2・V4の検討につながる。
- SAM2本体を固定したスクリーニングで分かるのは「F0に足した価値」であり、本体と同時に学習したときの効果とは異なりうる。
- 「FPN的」の解釈（各段でMambaを回し、(a)でつなぐ）が先生の意図と合っているかは未確認。
- 次回MTGまでに段階3まで終わらない可能性がある。その場合は、段階0〜1の結果と学習途中の状況を報告する。

## 未決事項

- 段階0bで採用するadapter LR。
- 段階1の結果による、V3で使う段の組み合わせと更新回数N。
- 旧F1の結果に、学習と推論の経路の不一致がどれだけ影響していたか（今回の範囲では調べない）。

## 関連

- [brainstorm（2026-10-18）](../../../../secretary/notes/brainstorm/2026-10-18-temporal-mamba-integration-variants.md)
- [このspecのレビュー（2026-10-18）](../../../../secretary/notes/brainstorm/2026-10-18-temporal-mamba-v3-spec-review.md)
- [V1〜V4の図](../materials/figures/2026-10-14-temporal-mamba-variants/manifest.md)
- [10/14 MTG議事録](../meetings/2026-10-14-mtg.md)
- [10/9 MTG議事録](../meetings/2026-10-09-mtg.md)
- [MOSE追加学習の実験ログ](../experiments/2026-09-30-mose-temporal-mamba-finetuning.md)
- [前回のMOSE追加学習spec](2026-09-30-temporal-mamba-mose-finetuning-spec.md)
- [SAM 3.1 multiplexの論文メモ](../papers/2026-10-14-sam3-multiplex-object-sharing.md)

## 改訂履歴

- 2026-10-18：初版作成・承認。
- 2026-10-18：レビュー（[2026-10-18-temporal-mamba-v3-spec-review.md](../../../../secretary/notes/brainstorm/2026-10-18-temporal-mamba-v3-spec-review.md)）を反映。
  - 既存adapterの学習と推論の経路の不一致（外側の `output_proj`）を背景に追加し、正しさの確認をゼロでない残差・複数フレーム・TBPTTの境界で行うように変更した。
  - H2を「stateへの依存」の診断とし、判定表を「追加効果」「stateへの依存」「未確認」で言い直した。「支持されない＝効果がない」とは読まない。
  - SAM2本体の固定範囲とtrain/evalのモードを定義し、高速化の確認を同じ新しい学習条件の中での比較に変えた。
  - LRの確認をV1とV3の両方で行い、各段のMamba内部の勾配と重みの変化、SAM2本体の不変性を合格条件に加えた。
  - 共通の更新回数Nの決め方、軌跡の並び順、optimizerの設定、段を減らした場合の条件名を明記した。
  - 集計スクリプトを変更範囲に加え、F0の既存結果を再利用する条件を明記した。
- 2026-10-19：Cometでの学習経過の記録を変更範囲に追加した。記録先は `.comet.config` で一元管理し、`samurai-mot` に統合する（一時的に作った `sam2-temporal-mamba` プロジェクトは空のまま削除）。
- 2026-10-21：実装ファイルの構成を記録。旧F0/F1の学習・評価・集計スクリプトはlockboxの実装ハッシュを保つため変更せず、新しいファイル（`training/mose_adapter_train.py`・`mose_adapter_eval.py`・`mose_adapter_summary.py` など）として実装した。実行はMamba_Trackersと同じ形（`configs/temporal_adapters/*.yaml` と `experiments/temporal_adapters/*.sh`）。SAM2 repo `feat/temporal-mamba-v3` の `c2e928b`〜`80610fe`。
- 2026-10-22：学習経過の記録をsimple_cnnの形（横軸step、`train_*_step`・`train_*_avg`・`val_*`、valごとのcheckpoint保存）に揃え、学習中のval（tuningの先頭25動画、250 stepごと、経過確認のみ）を追加した。
