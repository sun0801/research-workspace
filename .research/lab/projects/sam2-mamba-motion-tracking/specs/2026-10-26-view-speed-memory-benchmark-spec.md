---
date: 2026-10-26
project: sam2-mamba-motion-tracking
type: spec
status: draft
tags: [view, benchmark, fps, gpu-memory]
---

# ViEW 表2：推論速度とGPUメモリの計測

## 目的

ViEW 8ページ版の表2（`overleaf/view/main_text.tex` の `tab:result`）にある FPS と GPUメモリの列を埋める。
4手法（SAM2，SAMURAI，Ours sliding window型，Ours state carry型）を，同じGPU・同じ条件で計測する。
追跡の精度は既存の評価runの値をそのまま使い，この計測では変えない。

## 計測に使うコード

- リポジトリ：`/mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2`
- state carry型の評価runと同じコードにするため，**評価runの `git_commit.txt`（a6253e7）から git worktree を作り，同じrunの `git.diff` を当てる**（作業中の `1002_seminar` は temporal adapter の変更を含むので使わない）。
  - worktree：`/mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2_bench`，ブランチ `view-benchmark`
  - `git.diff` には state carry型の yaml（checkpoint のパス，`motion_enable_time_thresh: 5`，`motion_delta_clip: 0.1` など）が含まれるので，yaml の override は要らない。`kf_score_weight` は4手法とも 0.25，`stable_frames_threshold` は1であることを確認済み。
  - 他の3手法も同じ worktree で計測する。sliding window型の評価runは別の commit（f1edd2b と推定）で回しているので，検証1の出力の一致で同じ挙動かどうかを確かめる。
  - `checkpoints/` と `data/` は元のリポジトリへのシンボリックリンクにする。
- 追加するのは計測用スクリプト `scripts/benchmark_mot_speed.py` の1ファイルだけ。既存のファイルは変えない。
  - `main_inference_mot.py` の推論部分（`init_state`，ID の追加，`propagate_in_video`，マスクからボックスへの変換）を同じ手順で写す。
  - 動画の書き出し，Comet へのログ，debug CSV は行わない。

## 計測の条件

- GPU：RTX A4000（`cuda:0`）。計測中はほかのジョブを流さない（開始前に `nvidia-smi` で確認）。
- SAM2.1 Hiera-tiny，`torch.inference_mode()` と fp16 autocast，`offload_video_to_cpu=True`，`offload_state_to_cpu=True`（いずれも評価runと同じ）。
- 各手法の設定：
  - SAM2：`configs/sam2.1`
  - SAMURAI：`configs/samurai`
  - sliding window型：`configs/samurai_mamba_window`（`MambaTrack_epoch25.pth`）
  - state carry型：`configs/samurai_mamba_stateful`（`mamba_stateful_dancetrack/epoch100.pth`。`git.diff` で設定される）
- 計測の範囲：
  - `init_state`（全フレームの読み込み）は含めない。
  - `propagate_in_video` の各ステップ（途中のIDの追加を含む）と，マスクからボックスへの変換を含める。
  - 各ステップの前後で `torch.cuda.synchronize()` を呼んで時間を測る。
  - ウォームアップとして，最初の系列の前に1系列分（短い dancetrack0043，183フレーム）を流し，その結果は使わない。
- 記録する値（系列ごとに JSON で保存する）：
  - 処理したフレーム数，各フレームで追跡している対象の数の合計（物体×フレーム数），合計時間
  - `torch.cuda.reset_peak_memory_stats()` を系列の開始時に呼び，`torch.cuda.max_memory_allocated()` のピーク値
- 表に載せる値：
  - **FPS** = 全系列の合計フレーム数 ÷ 合計時間（全対象を処理する時間を含む）
  - **GPUメモリ** = 系列ごとのピーク値の最大
  - 補足として，1物体・1フレームあたりの時間（合計時間 ÷ 物体×フレーム数）も記録する。対象数によって FPS が大きく変わるため，本文で説明に使う。

## 対象の系列

DanceTrack val の25系列（全25508フレーム，物体×フレーム数は最大で約25万）を基本とする。
時間が足りない場合は，対象数の幅をカバーする5系列（dancetrack0005：4人，0007：8人，0014：12人，0034：14人，0081：20人）に絞る。絞った場合は，本文にその旨を書く。

## 検証

1. **評価runとの出力の一致**：計測時に出力した MOT 形式の txt を，既存の評価runの txt と比べ，対象の系列で一致することを確かめる。
   - SAM2：`results/sam2/sam2_tiny/`
   - SAMURAI：`results/samurai/samurai_tiny/`
   - sliding window型：`results/samurai_mamba/samurai_mamba_tiny/`
   - state carry型：`results/sam2_stateful_minimal/20260723T_sam2_minimal_25seq/samurai_mamba_stateful_tiny/`
   - 一致しない場合は，計測値を論文に載せる前に原因を確かめる（fp16 の非決定性による小さなずれか，設定の違いか）。
2. **再現性**：1手法（state carry型）を2回計測し，FPS の差が5%以内であることを確かめる。

## 実行

長時間のGPUジョブなので，実装後にコマンドを渡し，ユーザーが tmux で実行する。

## 論文への反映

- 表2の FPS・GPUメモリの列を埋め，計測の条件（GPU，対象の系列，`init_state` を含めないこと，状態をCPUに退避していること）を実験設定に1〜2文で書く。
- Mamba 単体のコスト（1物体・1フレームあたり約2.3 ms，ピークメモリ約15 MB。既存の記録）は本文で補足に使える。

## 進捗（2026-10-26，サーバー停止のため中断）

- 承認を受けて，worktree `/mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2_bench`（ブランチ `view-benchmark`，a6253e7 + 評価runの `git.diff`，未コミット）と `scripts/benchmark_mot_speed.py` を作った。
- スモーク（state carry型，dancetrack0043，183フレーム，ウォームアップなし）：FPS 2.38，1物体・1フレームあたり 39.1 ms，ピーク 873 MB。
- **評価runの出力とは一致しなかった**（1970行中636行が異なり，2フレーム目から食い違う）。
  - 原因：venv の torch が 2026-09-01 に 2.10.0+cu128 へ更新され，5/19 にビルドした `sam2/_C.so` が読み込めなくなっている（undefined symbol）。そのため，SAM2 のマスクの後処理（`fill_hole_area=8`）が飛ばされている。7/23 の評価runのログにはこの警告がなく，当時は後処理が効いていた。
  - editable install の finder が `sam2._C` を元リポジトリの .so に固定しているので，worktree だけで再ビルドしても読み込まれない。CUDA toolkit も 13.4 で，torch の cu128 と合わない。
- 未決定：今の環境のまま4手法を同じ条件で計測するか（出力の一致による検証は諦め，後処理なしで測ったことを記録する）。
- 未実施：sliding window型・SAM2・SAMURAI のスモーク。
- 実行時間の目安（39 ms/物体・フレームの場合）：5系列で1手法あたり約40分，25系列で約2.7時間。
- 別件：torch 更新後（9/1以降）に元のリポジトリで回した評価も，同じく後処理なしで動いている可能性がある。

## 再開（2026-10-26 18:17）

- ユーザーの「再開して，必要ならGPU2枚使ってよい」を受けて，今の環境（後処理なし）のまま計測を始めた。出力の一致による検証は行わず，4手法を同じGPU・同じ環境で測ったことで比較の条件をそろえる。
- サーバー復旧後，GPU は2枚で，機種が異なる（0: RTX A4000，1: RTX PRO 4500 Blackwell）。FPS は同じGPUで測った値どうしでしか比べられないので，表にはどちらか一方の値だけを使う。
  - GPU0（A4000）：5系列 × 4手法，そのあと state carry型をもう一度（再現性の確認）。run名 `20261026_5seq_a4000`。
  - GPU1（PRO 4500）：25系列 × 4手法。run名 `20261026_25seq_pro4500`。
- 実行：tmux セッション `view_bench`（ウィンドウ `a4000`，`pro4500`）。スクリプト `results/view_benchmark/run_view_benchmark.sh`，ログ `results/view_benchmark/<run名>.log`。
