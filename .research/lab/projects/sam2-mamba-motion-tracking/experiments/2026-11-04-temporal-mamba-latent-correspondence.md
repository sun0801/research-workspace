---
date: 2026-11-04
project: sam2-mamba-motion-tracking
spec: ../specs/2026-11-04-temporal-mamba-latent-correspondence-spec.md
status: in-progress
tags: [experiment, temporal-mamba, sam2, mose, correspondence, sinkhorn]
---

# V3の64段のstateを、潜在空間の対応で運ぶ（案①-b） 実験ログ

承認済みspec：[2026-11-04-temporal-mamba-latent-correspondence-spec.md](../specs/2026-11-04-temporal-mamba-latent-correspondence-spec.md)（2026-11-04 承認）。関連：[②・②'とD2の実験ログ](2026-11-04-temporal-mamba-spatial-mixing.md)。

## A' 学習（2026-11-04 19:46〜）

- 条件：既存のV3、設定 `A_v3.yaml`（Aと同じ設定で `adapter_checkpointing: true`）。コードの変更なし。
- run：141 SAM2 repo `runs/short_clip/A_v3/20261104T194605+0900_2f90e77`（141のGPU 1、RTX A4000、tmux `aprime`、19:46開始）。
- 開始直後の確認（19:48、Claudeがsshで確認）：
  - 141のGPU 0〜2はすべてRTX A4000（段階1の④の「GPU 1と2が同じ機種」を満たす）。
  - resolved configは `adapter_checkpointing: true`、manifestは条件A・`2f90e77`・dirty。
  - `git.diff` は0b'のパッチ（`temporal_adapters.py`・`check_spatial_mixing.py`・`mose_adapter_eval.py`・`A_sml1` の設定2つ）だけで、V3の経路は変わっていない（1b・1b'の⑤で確認済み）。
  - F0の重みの読み込みまで、エラーなし。
- 見込み：Aの実績（RTX A4000・checkpointingあり、1更新1.8〜2.1秒）から、val-25を含めて約16〜18時間（11/5の昼ごろ）。

## 段階0 実装（対応の計算、2026-11-04）

SAM2 repoのworktree `/mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2_corr`（ブランチ `feat/latent-correspondence`、`191ca8b` から）。142の作業ツリー（②'の自動実行が使う）は切り替えていない。worktreeには、元の作業ツリーと同じ `data` のリンクだけを置き、`runs/` などは絶対パスで元の作業ツリーのものを使う。未コミット。

- `sam2/modeling/latent_correspondence.py`（新規）：
  - `local_similarity`：15×15の窓のcosine類似度。タイル（16×16マス）とその周り（halo）の行列積で計算し、窓の帯だけを取り出す。
  - `correspondence_weights`：identity・argmax・softmax・sinkhorn。sinkhornはlog領域でdustbin付き。周辺分布は正規化しない値（各マス1、dustbin N）で、残差（列を更新した後の行の和の1からのずれの最大）を5回ごとに判定し、1e-3以下か最大回数で止める。その後、行→列の順に1を超えた分を縮める（後処理）。反復回数・残差・後処理での縮小量を返す。
  - `transport_tokens`：stateをトークンの並び `[B, H*W, D]` のまま、タイルとhaloの行列積で運ぶ。自前のautograd関数で、保存するのは重みのブロックだけ（backwardは転置の行列積と `index_add`）。既定はTF32なしのFP32。
  - `weight_stats`：行の和・エントロピー・期待移動距離・列の和の最大。
- `training/check_latent_correspondence.py`（新規）：単体テスト（`units`）とコストの計測（`cost`）。

### 単体テスト（142のRTX A4000、すべて合格）

結果：SAM2 repo `runs/latent_corr/stage0/dev3/units.json`。

| 確認 | 結果 |
|---|---|
| 既知のずれ（(0,3)・(2,−1)・(−4,−4)マス、ランダムな特徴）の復元 | argmax・softmax（τ=0.02）・sinkhorn（τ=0.02）とも、内側のマスで期待移動の誤差が最大1e-10以下 |
| タイルでの類似度と、窓のループでの計算の一致 | 窓15・5、タイル8・16で最大誤差2.4e-7、−∞の位置も一致 |
| sinkhornの後処理 | τ 3通り × dustbin 3通り × 反復5・20・100回で、行・列の和の最大が1+1e-6以下、重みは非負。反復5回では残差0.58でも、後処理で縮めて制約を満たす（縮小量0.17%） |
| dustbinに全部入る場合 | 運んだstateの最大が1e-37 |
| 輸送（タイル）・ループ・密な行列の一致（FP64、forward・backward） | 窓15・5とも最大誤差3e-14 |
| 物体どうしが混ざらない / identityで完全一致 / ‖Wh‖∞ ≤ ‖h‖∞ | 差0 / 差0 / 比0.70（softmax）・0.53（sinkhorn） |

- ランダムな特徴の既知のずれでは、sinkhorn（τ=0.02）は100回で収束しなかった（残差0.006〜0.007。端のマスの出入りがあるため）。実データの反復回数は0cで記録する。

### 段階0a 輸送のコスト（142のRTX A4000）

specでは141のA4000で測る予定だったが、141のGPU 2と同じ機種（RTX A4000）で、空いていた142のGPU 0で測った。1物体・64×64マス・窓15、64段のstate（512 × (16+4) = 10,240チャネル）。結果：SAM2 repo `runs/latent_corr/stage0/dev3/cost.json`（タイルの大きさ・chunkの比較は `dev2/cost.json`）。

| 処理（1フレーム） | 時間 |
|---|---|
| 類似度 | 0.8 ms |
| softmax | 0.3 ms |
| sinkhorn 20回 / 100回 | 28 ms / 138 ms（1回あたり約1.4 ms） |
| 輸送 forward / forward＋backward（タイル16、FP32） | 13 ms / 29 ms（追加のVRAM 約1.0〜1.3 GB） |
| 同（TF32） | 9 ms / 22 ms |

- 最初の実装（オフセットごとのループ・unfold）は、類似度48 ms、輸送のforward＋backward 150 msだった。タイルの行列積に書き換えて上の値になった。
- 8フレームの1更新あたりの追加時間の見込み：softmax 約0.24秒、sinkhorn 20回 約0.47秒、100回 約1.35秒。輸送をactivation checkpointの中に入れる場合は、さらに約0.10秒。
- A'（1更新1.8〜2.1秒）に対して、softmaxは約1.1倍、sinkhornは約50回までなら1.5倍以内、100回では約1.7倍になる見込み。実際の反復回数は実データ（0c）で決まるので、この時点では相談の条件（1.5倍を超えそう）に当たるとは判断せず、0cで反復回数を記録してから段階1の⑥で判定する。

## 段階0 実装（診断スクリプト、2026-11-04）

- `training/measure_correspondence.py`（新規）：サブコマンド `features`（0cのデータ）・`dustbin`（s_dの格子、低ノルムの区切り、速さの3分位）・`weights`（0cの指標）・`hungarian`（0cの参照）・`translate`（0b）・`summary`（集計・層別・関門と選択）。
  - 100動画：短区間学習のtrainの1,121動画から、seed 123で無作為に選ぶ。
  - 各物体を、最初に写るフレームのGTマスクをプロンプトにしてF0で追跡し、`pix_feat`（memory attention後、デコーダの手前）をフックで記録する。画像エンコーダ特徴は全フレーム。
  - 使う（物体、組 t−1→t）：t−1 がプロンプトのフレームより後（`pix_feat` がある）、tに前景のマスが1つ以上、t−1にも物体が写っている。画像エンコーダ特徴も同じ組で比べる。
  - 類似度を組ごとにfp16で保存し（`cache/`）、s_d（前景の最大類似度の1・5・10パーセンタイル）を全動画から決めてから重みを計算する。
  - 0bの平行移動はゼロ埋め（正規化後の0＝平均色）。0.25・0.5マスは4・8 px。
- `correspondence_weights` は、τ・s_d をバッチ要素ごとに指定できるようにした（9通りのsinkhornを1回で計算）。収束した要素は作業中のバッチから外すので、単独で計算したときと同じ重みになる（差は最大2e-6、FP32の丸め）。
- 単体テストに、sinkhornと密なSuperGlueのlog-OT（周辺分布 [1, …, 1, N]、窓が画面全体を覆う8×8）の一致を加えた：最大誤差2.9e-7（`runs/latent_corr/stage0/units/units.json`、すべて合格）。
- 142で2動画・数サンプルの通し確認をした（`runs/latent_corr/stage0/smoke/`。数値は判断に使わない）。
  - 所見（通し確認の3サンプルでの観察。判断には使わない）：平行移動での前景のマスの行の和は、softmaxでは1、sinkhornでは0.02〜0.5と小さかった。密なSuperGlueの実装でも同じ値になるので、実装の誤りではなく、dustbinの容量Nと、s_dを前景の最大類似度の低いパーセンタイルに置いたことによる性質と考えている。0cの M と行の和で確かめる。
  - 画像エンコーダ特徴では、1マス単位（16 px）の平行移動はパッチの格子と揃うので、期待変位誤差がほぼ0になる。関門(a)は1・2・4マスで判定するので、画像エンコーダ特徴には易しい条件である。0.25・0.5マスの結果も合わせて読む。
- 141へは、worktreeのコードを `/mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2_corr`（gitではないコピー）に送った。sha256：`latent_correspondence.py` 7245e90e…、`measure_correspondence.py` 59e83f7f…。

## 段階0e 実装（①-bのadapter、2026-11-04、診断と並行して先に着手）

診断（0b・0c）の結果を待たずに書ける部分を先に実装した（方式・特徴・τ・s_d は引数）。設定ファイル `A_corr_ckpt.yaml` は、診断で値が決まってから作る。未コミット。

- `sam2/modeling/temporal_adapters.py`：
  - `CorrespondencePyramidAdapter`（`adapter_type: v3_corr`）。V3を継承し、64段だけ、Mambaを1ステップ進める前に ssm_state・conv_state をトークンの並びのままFP32で運ぶ（autocastを切る）。重みは勾配なし。前の特徴は stateの `"corr_prev"` に、更新のたびに保存する（resetの後も更新）。`corr_method="identity"` と推論時の `corr_override="identity"` は輸送そのものを通らない。
  - 推論時の上書き `corr_override`：identity / shuffle（`shuffle_scores`：窓の中の有限なスコアを位置の間で並べ替え、同じ正規化をかける。seed 123の生成器を物体ごとにresetする）/ diag（diag(W 1)）。`log_corr` で更新ごとに `weight_stats` とsinkhornの統計を記録する。
  - 基底クラス：`reset_levels`（評価専用。指定した段のstateだけ毎フレーム0に戻す。V3にも使える）と、`corr_feat` の受け渡し（`needs_corr_feat` を持つadapterにだけ渡す）。`detach_state` に通常のTensorの分岐を加えた。
- `sam2/modeling/latent_correspondence.py`：`shuffle_scores` を追加。
- `sam2/modeling/sam2_base.py`：adapterが `needs_corr_feat` を持つときだけ、`current_vision_feats[-1]` を `[B, C, 64, 64]` にして渡す（学習・推論の両方）。
- `training/mose_adapter_eval.py`：`v3_corr` は学習パラメータがV3と同じなので、runの `config_resolved.yaml` から種類と設定を読んで復元する。`--reset-levels`、`--corr-override` を追加。v3_corrのときは物体ごとのWの統計の平均を `corr_stats.jsonl` に書く。
- `training/short_clip_trainer.py`：manifestの `adapter` に対応の設定を記録する（v3_corrのときだけ）。

簡単な確認（142のRTX A4000。段階1の正式な確認ではない）：

- 同じseedで作ると、v3_corrとV3のパラメータの集合・初期値が一致。identityでは、4フレームの出力と64段のstateがV3と差0。
- softmax・sinkhornで、64段のMambaに勾配が届く（9個のパラメータ）。`corr_prev` は勾配を持たない。B=1・checkpointingありでピーク5.0 GB（adapter単体）。
- `reset_levels=("64",)`、shuffle・diagの上書きが動く。shuffleは窓の外の位置を保ち、各行のスコアの集合も保つ。
- 実モデル（F0にAの重み、tuningの1対象 `03c21af7`/1、36フレーム）：v3_corr（identity）はAとフレームごとのJ・Fまで完全に一致（J&F 0.9728）。softmax（τ=0.05）0.9727、sinkhorn（τ=0.05、s_d=0.5）0.9722で、35回の更新すべてで輸送が通った（最初のフレームは前の特徴がないので通らない）。この1対象では、sinkhornの行の和の平均は0.69、softmaxの列の和の最大は2.9だった。

## 段階0 試行（10動画、2026-11-04 20:13〜20:28、141のGPU 2）

100動画の最初の10動画で、features → dustbin → weights を通した（`runs/latent_corr/stage0/pilot10/`、141）。時間の見積もりのための試行で、**判断には使わない**（s_d・速さの区切りも10動画だけから決めている）。

- 時間：features 2.7分（10動画・518フレーム・1,665組）、weights 12.3分。100動画では、features 約30分、weights 約2時間、translate 約30分の見込み。cacheは10動画で3.4 GB。
- 参考の数値（中速、10動画、探索的）：

| 特徴・方式 | M | H | 行の和 |
|---|---|---|---|
| identity | 0.51 | 0.51 | 1 |
| image softmax τ=0.02 / 0.05 / 0.1 | 0.79 / 0.75 / 0.62 | 同じ | 1 |
| image sinkhorn τ=0.02（s_d 1・5・10%） | 0.62 / 0.42 / 0.29 | 0.79〜0.80 | 0.75 / 0.48 / 0.33 |
| image sinkhorn τ=0.05・0.1 | 0.05〜0.25 | 0.62〜0.75 | 0.06〜0.30 |
| pix softmax τ=0.02 / 0.05 / 0.1 | 0.83 / 0.79 / 0.72 | 同じ | 1 |
| pix sinkhorn τ=0.02（s_d 1%） | 0.55 | 0.82 | 0.63 |
| image / pix argmax | 0.80 / 0.84 | 同じ | 1 |

- 所見（10動画での観察）：sinkhornの同一物体率Hはsoftmaxと同程度だが、行の和（保持率）が小さく、Mが大きく下がる。dustbinの容量Nと、前景の最大類似度の低いパーセンタイルに置いたs_dのために、多くの質量がdustbinに流れる（通し確認の所見と同じ）。softmaxでは、前景の物体のマスの約2割で列の和が1.5を超える（複製）。
- specの決め方（結果を見る前に決めた格子と規則）は変えずに、100動画で本番を回す。

## 段階0 本番（100動画、2026-11-04 20:30ごろ〜、141のGPU 2）

- ユーザーがtmux `corr0` で開始。出力：141 SAM2 repo `runs/latent_corr/stage0/full100/`（ログは `full100.log`）。features → dustbin → weights → translate → hungarian → summary の順。0時ごろ完了の見込み。
- 141のコード：`measure_correspondence.py` は142のworktreeと同じ（sha256 59e83f7f…）。`latent_correspondence.py`（7245e90e…）は、送った後に142で `shuffle_scores` を足す前の版で、違いはこの関数（診断では使わない）の有無だけ。診断の計算は142のworktreeと同じ。
- 開始直後（20:31）：4動画まで進み、各動画の時間は試行と同じ。A'（GPU 1）は動き続けている。

### 結果（2026-11-04 23:34 完了、141 SAM2 repo `runs/latent_corr/stage0/full100/summary.json`）

- 規模：100動画・5,761フレーム・242物体・12,596組（物体×組）。features 24分。ログにエラーなし。
- s_d（前景の最大類似度の1・5・10パーセンタイル）：画像エンコーダ特徴 0.50 / 0.62 / 0.67、`pix_feat` 0.62 / 0.73 / 0.77。速さの3分位の区切り（100動画のGT、動きを測れた240物体）：0.567・1.261マス。中速は160物体。

**関門と選択（specの5の規則どおり）**

| 候補（選んだτ・s_d） | 中速の M̄ | M̄_id | 改善余地に対する割合 | (a) E の中央値（d=1・2・4） | 別物体率（id 0.035） | 判定 |
|---|---|---|---|---|---|---|
| image softmax（τ=0.02） | **0.820** | 0.606 | 0.54 | 0.12 / 0.06 / 0.07 | 0.028 | **通過** |
| image sinkhorn（τ=0.02、s_d 1%） | 0.606 | 0.606 | 0.0001 | 0.10 / 0.05 / 0.06 | 0.027 | (b)で不合格 |
| pix softmax（τ=0.02） | 0.853 | 0.606 | 0.63 | 1.73 / 1.59 / 1.51 | 0.020 | (a)で不合格 |
| pix sinkhorn（τ=0.02、s_d 1%） | 0.558 | 0.606 | −0.12 | 1.55 / 1.41 / 1.33 | 0.020 | (a)(b)で不合格 |

→ **選択：画像エンコーダ特徴・softmax・τ=0.02**（関門を通ったのはこの1つだけ）。

**その他の結果（中速、探索的）**

| 特徴・方式 | M | H | 行の和 | 拡大（>1.1）のM | 境界帯 / 内側のM | 前景の複製（列の和>1.5の割合） |
|---|---|---|---|---|---|---|
| identity | 0.606 | 0.606 | 1 | 0.507 | 0.525 / 0.752 | 0 |
| image softmax τ=0.02 / 0.05 / 0.1 | 0.820 / 0.792 / 0.699 | 同じ | 1 | 0.773 / 0.742 / 0.638 | 0.782 / 0.929（τ=0.02） | 0.19 / 0.16 / 0.09 |
| image argmax | 0.824 | 0.824 | 1 | 0.779 | 0.786 / 0.933 | 0.21 |
| image hungarian（参照、200組） | 0.749 | 0.749 | 1 | 0.584 | 0.706 / 0.865 | 0 |
| image sinkhorn τ=0.02（s_d 1・5・10%） | 0.606 / 0.400 / 0.277 | 0.82 | 0.68 / 0.43 / 0.29 | 0.495（1%） | — | 0 |
| image sinkhorn τ=0.05・0.1 | 0.05〜0.24 | 0.70〜0.80 | 0.05〜0.26 | — | — | 0 |
| pix softmax τ=0.02 | 0.853 | 0.853 | 1 | 0.811 | 0.818 / 0.952 | 0.20 |

- 速さの層別（image softmax τ=0.02 / identity のM）：遅い 0.888 / 0.830、中くらい 0.847 / 0.717、速い 0.811 / 0.545。速い物体ほど改善が大きい。
- sinkhornは、行き先の正しさ（H 0.82）はsoftmaxと同じだが、保持率（行の和）が低く、Mがidentityを上回らない。τ=0.02・s_d 1% は99.9%の組で100回では収束しなかった（後処理での縮小は0.02%）。列の和の制約とdustbinの容量が、stateを大きく削る（レビューの指摘4と一致）。
- `pix_feat` は、同一物体率では最も高いが、既知の平行移動での変位誤差が大きい（d=1〜4マスで1.5〜1.7マス、広がり約2.2マス）。argmaxでは整数マスの移動を誤差0で当てるので、`pix_feat` の類似度は平らで、softmaxでも重みが広く散ると考えられる（推論）。
- 1マス未満の移動（0bの0.25・0.5マス、画像エンコーダ特徴）では、softmax τ=0.02 のEの中央値は0.36〜0.78 / 0.65〜1.17マスで、identity（0.25〜0.35 / 0.5〜0.71）より大きい（重みの広がり0.8〜1.1マス）。1マス未満の動きでは、対応で運ぶとかえって位置がぼやける。MOSEの動きの中央値は0.63マスなので、学習後の評価で遅い物体の層を合わせて見る。
- 選んだτ=0.02は格子の端（最小）。τを下げるほどMが上がり、τ→0の極限のargmaxでも0.824なので、これより小さいτでの上積みは小さいと見込む。
- 計算時間：softmaxは1更新あたり約0.24秒の追加（段階0a）で、A'の1.5倍の条件に収まる見込み。段階1の⑥で確かめる。

## 段階1 確認（2026-11-05〜）

- 設定：`sam2/configs/sam2.1_training/short_clip/A_corr_ckpt.yaml`（`A_v3` を元に、`v3_corr`・softmax・画像エンコーダ特徴・窓15・τ=0.02。条件名 A_corr）。
- 確認スクリプト：`training/check_latent_corr_adapter.py`（c1〜c9。specの段階1の①〜⑨に対応）。⑦の単体テストのうち、対応の計算の部分は `check_latent_correspondence.py units`（段階0、合格済み）。
- worktreeと141のコピーに、`runs/mose_temporal_mamba_20260930`（F0とtuningの索引）へのリンクを置いた（学習設定の相対パスのため。git管理外）。
- 結果：SAM2 repo `runs/latent_corr/stage1/20261105/`（c1・c2・c3〜c4・c6〜c9は141のGPU 2、c5は142のGPU 0。どちらもRTX A4000）。

| 確認 | 結果 |
|---|---|
| c1 identityでの一致（①） | 合格。マスク・クリック・boxの3種類、初期化直後とW_outに同じ非ゼロ値を入れた場合の両方で、全フレームのマスクのlogit・IoUと全段のstateがAと差0。softmaxのv3_corrは、adapterの呼び出しのうち最初以外のすべてで輸送した（マスクのプロンプトでは最初のフレームがadapterを通らないので、呼び出し3回・輸送2回） |
| c2 パラメータ（②） | 合格。v3_corr（identity・softmax）のパラメータの名前と初期値がAと完全に一致 |
| c5 オフのときの一致（⑤） | 合格。F0とAを最初の1動画・4対象で評価し、`191ca8b`（git worktree）とJ・F・J&Fとも差0 |
| c3 数回の更新（③） | 合格。3更新で、学習するのはadapterだけ（46個のパラメータがすべて動いた）、固定したパラメータはF0から不変。学習パラメータの名前・最適化のグループ・weight decayの除外がAと同じ。manifestに対応の設定（softmax・image・窓15・τ=0.02）が記録された |
| c4 サンプル列（④） | 合格。最初の3更新の動画・物体・フレーム・augmentation後の画像の和・プロンプトの種類が、A'（141のGPU 1）と一致。この3更新では、クリックの座標と修正したフレームも一致した。GPU 0〜2はすべてRTX A4000 |
| c6 時間とVRAM（⑥） | 300更新で1更新の平均1.94秒（中央値2.10秒）。同じ300更新のA'は平均1.76秒（中央値1.90秒）で、**比は1.10倍**（1.5倍の条件の内）。24,662更新で約13.3時間（val-25を除く）。VRAMはtrainerのログで最大11 GB（A'も最大11 GB）。lossはすべて有限 |
