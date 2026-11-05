---
date: 2026-11-06
project: sam2-mamba-motion-tracking
source: chat
status: draft
tags: [spec, evaluation, temporal-mamba, sam2, dancetrack, trackeval, samurai-protocol]
---

# temporal Mambaの各手法を、動き予測と同じSAMURAIの設定でDanceTrackで評価する Spec

## 目的

temporal Mamba（A・②・②'・①-b）は、これまでMOSEのval（125動画・313対象）でしか評価していない。最終的な評価はDanceTrackで行う（10/23 MTGの方針）ため、次の2つを行う。

1. 手法1（動き予測）の評価と同じ設定で、DanceTrack val 25系列を評価できる仕組みを作る。
2. 今ある手法の参考の値を取り、①-bのMOSEの評価が出たら、checkpointを差し替えるだけで評価できる状態にする。

位置づけは**参考の評価**とする。MOSEでstateの寄与が0を含んでいるA・②・②'では、DanceTrackで差が出ないことが、いちばんありそうな結果である。

## 評価の設定（手法1と同じ）

前回の動き予測の評価（[ViEW原稿の実装確認](../papers/2026-view/2026-10-23-method-implementation-check.md)、[7/27の実験ログ](../experiments/2026-07-27-sam2-minimal-integration-best-hota-25seq.md)）と同じにする。

| 項目 | 設定 |
|---|---|
| データ | DanceTrack val 25系列（`data/DanceTrack/val/val`、`data/DanceTrack/testing_set.txt`） |
| 初期化 | 各IDの初めて現れるフレームで、GTのbboxをboxプロンプトにする（全ID。検出器は使わない） |
| 推論 | `scripts/main_inference_mot.py`。`torch.inference_mode()` とfp16のautocast、`offload_video_to_cpu=True`、`offload_state_to_cpu=True` |
| 評価 | TrackEval（HOTA/CLEAR/Identity）、`DO_PREPROC=False`、25系列を `SEQ_INFO` で明示 |

**前回と違う点**：SAM2のモデルの大きさ。前回はtiny、temporal MambaはSmall（F0）で学習しているので、今回はすべてSmallにする。前回のtinyの数値とは直接比べず、Smallの基準（P0）と比べる。

## 条件

| 段階 | 条件 | SAM2の重み | adapter | 目的 |
|---|---|---|---|---|
| 1 | P0 | 配布されたSmall（`checkpoints/sam2.1_hiera_small.pt`） | なし | 基準 |
| 1 | F0 | MOSEで全軌跡を追加学習したSmall | なし | MOSEでの追加学習の影響 |
| 1 | A（持ち越し） | F0 | V3（`runs/short_clip/A_v3_nockpt/20261027T154219+0900_1895c45`、22 epoch） | 主な比較 |
| 1 | A（reset1） | 同上 | 同上、stateを毎フレーム初期化 | Aのstateの寄与 |
| 1（任意） | SAMURAI-Small | P0 | なし（カルマンフィルタあり） | 手法1の系統の参考 |
| 2 | ②（持ち越し / reset1） | F0 | `runs/short_clip/A_rw_k7_nockpt/20261104T155733+0900_2f90e77` | 参考 |
| 2 | ②'（持ち越し / reset1） | F0 | `runs/short_clip/A_sml1_k7_nockpt/20261105T005211+0900_191ca8b` | 参考 |
| 3 | ①-b（持ち越し / reset1） | F0 | `runs/short_clip/A_corr_ckpt/20261105T123304+0900_354e415`（学習中） | 本命。MOSEの評価のあと |

- temporal Mambaの比較は、カルマンフィルタを入れない素のSAM2のモード（`--mode sam2`、`configs/sam2.1/sam2.1_hiera_s.yaml`）で行う。動き予測の効果と混ざらないようにするため。
- 段階2は段階1の確認に合格してから、段階3は①-bのMOSEの評価が出てから行う。
- **未決**：10/23の全軌跡で1周学習したV3を段階2に入れるか（下の「決めること」）。

## 実装

### 作業場所

- `2025_03_aburatani_sam2` の `feat/latent-correspondence` から、新しいブランチ `feat/dancetrack-adapter-eval` を作り、新しいworktreeで作業する。
  - `feat/latent-correspondence` には、V3・②・②'（L1正規化の版）・①-bのadapterがすべて入っている。`origin/mot` は両方のfeatブランチの祖先なので、`main_inference_mot.py` もそのまま入っている（2026-11-06に確認）。
  - ①-bの学習が `feat/latent-correspondence` のworktreeを `PYTHONPATH` で読んでいるため、そのworktreeでは作業しない。

### 変更

1. **`main_inference_mot.py` にオプションを足す**（指定しなければ、今までと同じ動き）
   - `--sam2-checkpoint`：SAM2の重みを差し替える（F0用）。
   - `--trainer-checkpoint`：公式trainerのcheckpointから、adapterを含むすべての重みを読み込む。adapterの種類の判定は `training/mose_adapter_eval.py` の `load_trainer_checkpoint` と同じ規則にする（できれば関数を共通にする）。strictに読み込み、足りない重みがあれば止める。
   - `--reset-every-frame`、`--reset-levels`：MOSEの評価と同じ意味。
   - manifestに、checkpointのパスとSHA256、adapterの種類、resetの設定を残す。
2. **物体ごとのstate**
   - 今のadapterの逐次推論（`TemporalAdapterBase.stream_step`）は、1つの物体しか扱えない（2つ目の `obj_id` が来ると止まる）。MOSEの評価は物体を1つずつ流しているため、これで足りていた。
   - DanceTrackでは1つの推論stateで全IDを同時に追うので、`obj_id` ごとにstate（`_stream_state`・最後のフレーム番号・更新回数）を持つ包み（wrapper）をMOT推論側に作る。呼ぶたびに、その物体の分をadapterに入れ替えてから `stream_step` を呼ぶ。
   - `temporal_adapters.py` と学習のコードは変えない。①-bの `corr_prev`（前のフレームの特徴）はstateの中にあるので、物体ごとに分ければそのまま動く。
   - フレームの順番の確認（同じ物体で同じフレームを2回通したら止まる）は残す。IDを途中で足したときに伝播をやり直す処理で、同じフレームを2回通していないかを、これで確認できる。

### VRAMの見積もり

- adapterのstateは、物体1つあたり約0.54 GB（SSMのstateがfp32で、64段 134 MB・128段 134 MB・256段 268 MB）。
- DanceTrack valの同時に映るIDは最大23（`dancetrack0094`）なので、stateだけで最大約12 GBになる。Smallのモデルと合わせて、RTX A4000（16 GB）では足りないおそれがある。段階1で実測して、足りなければ32 GBのGPU（RTX PRO 4500）で行う。

## 確認（段階1。合格してから本評価）

| # | 確認 | 合格の条件 |
|---|---|---|
| ① | 既定の動作が変わらないこと | オプションなしの `--mode sam2 --model_name small` で、変更前のコードと1系列の出力が一致する |
| ② | adapterを付けて素通しにしたとき | F0に、Aのadapterを `bypass=True` で付けたときの出力が、F0（adapterなし）と1系列で一致する |
| ③ | 物体ごとのstate | 1系列で、物体ごとの更新回数が、その物体を追ったフレーム数と一致する。フレームの順番のエラーが出ない |
| ④ | MOSEの評価との整合 | MOSE valの数動画・数対象を、同じプロンプト（最初のフレームのGTのマスク）で予測器の経路でも流し、`mose_adapter_eval.py` とのJ&Fの差を、F0とAで比べる。Aの差がF0の差と同じくらいであること（2つの経路は、モデルの組み立て方と計算の精度が違うので、完全には一致しない） |
| ⑤ | reset1が効いていること | 1系列で、Aの持ち越しとreset1の出力が異なる |
| ⑥ | 時間とVRAM | 1系列の時間とピークのVRAMを測り、25系列の時間を見積もる |

本評価（25系列）は、ユーザーがtmuxで実行する。Claudeはコマンドを渡し、確認①〜⑥のような短い確認は自分で回してよい。

## 結果の読み方

- **主な比較**：Aの持ち越し − reset1（HOTA・AssA・IDF1）。系列単位のpaired bootstrapで区間を出す。25系列しかないので、区間は広くなる前提で読む。
- **ほかの比較**：F0 − P0（追加学習の影響）、②・②' − A（参考）。条件が多いので、たまたま差が出たように見えるものは、主な比較の結論には使わない。
- DanceTrackは、1フレームあたりの動きがMOSEの約3分の1（段階0mの測定で、中央値0.22マス）。stateの寄与が出ないときに、「DanceTrackでは効かない」とまでは言わない。
- GTのboxで初期化する設定なので、検出器を使う既存のMOTの手法とは比べられない（手法1と同じ制約）。

## 範囲外

- SAM2MOT（検出器の入力、Co-DINO-L）への組み込み
- DanceTrack testへの提出
- DanceTrackでの学習・追加学習
- `temporal_adapters.py`・学習のコードの変更

## 決めること（承認の前に）

1. 10/23の全軌跡で1周学習したV3を、段階2に入れるか（形式が違い、`--adapter-checkpoint` の読み込みも要る）。入れない場合、AがV3と同じ構造の代表になる。
2. SAMURAI-Smallを、段階1で回すか。
3. 段階1の確認④の、MOSEの動画・対象の数。

## 履歴

- 2026-11-06：作成（draft）。ブランチの関係、adapterの逐次推論の制約、VRAMの見積もりは、読み取りだけの調査に基づく。
