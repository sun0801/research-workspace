---
date: 2026-10-26
project: sam2-mamba-motion-tracking
type: experiment
tags: [view, benchmark, fps, gpu-memory]
spec: ../specs/2026-10-26-view-speed-memory-benchmark-spec.md
---

# ViEW 表2：推論速度とGPUメモリの計測結果

## 条件

- worktree `/mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2_bench`（a6253e7 + 評価run `20260723T_sam2_minimal_25seq` の `git.diff`），`scripts/benchmark_mot_speed.py`
- venv `.venv-sam2`（torch 2.10.0+cu128）。`sam2/_C.so` が読み込めないため，**SAM2 のマスクの後処理（fill_hole_area=8）なし**。評価runの出力とは一致しない（spec の進捗を参照）。
- SAM2.1 Hiera-tiny，fp16 autocast，`offload_video_to_cpu=True`，`offload_state_to_cpu=True`。各ID は初出フレームの GT bbox で初期化。
- 計測の範囲：`init_state`（フレームの読み込み）とモデルの構築は含めない。IDの追加・`propagate_in_video`・マスクからボックスへの変換を含める。各手法の前に dancetrack0043 でウォームアップ。
- **GPU1（PRO 4500）で25系列の計測を同時に流していた**。処理は CPU 側で律速されているので，同時に流したことが値に影響している可能性がある。

## 結果（GPU0：RTX A4000，5系列，計5516フレーム，物体×フレーム数 61,395）

run名 `20261026_5seq_a4000`。結果は `results/view_benchmark/20261026_5seq_a4000/summary.json`。

| 手法 | FPS | 1物体・1フレームあたり | ピークメモリ（allocated） |
|---|---|---|---|
| SAM2 | 2.95 | 30.5 ms | 860 MB |
| SAMURAI | 2.85 | 31.6 ms | 863 MB |
| Ours（sliding window型） | 2.28 | 39.4 ms | 938 MB |
| Ours（state carry型） | 2.74 | 32.8 ms | 873 MB |

- 系列ごとの FPS は対象の人数でほぼ決まる（例：state carry型は 4人の0005で6.07，20人の0081で1.72）。
- **再現性**：state carry型の2回目（`20261026_5seq_a4000_repeat`）は FPS 2.59（1物体・1フレームあたり 34.6 ms）で，1回目（2.74）との差は5.4%。spec の基準（5%以内）をわずかに超えた。
- SAM2・SAMURAI・state carry型の差（2.95 / 2.85 / 2.74）は，この繰り返しによるばらつきと同じ程度。sliding window型だけがはっきり遅く（約2割），メモリも約75 MB多い。
- モデルを構築した直後の GPU メモリは，state carry型で 280 MB，sliding window型で 325 MB。

## 解釈

- 1物体・1フレームあたりの時間で見ると，state carry型が SAMURAI より余分にかかる時間は 1.2〜3.0 ms。Mamba 単体で既に測っていた値（約2.3 ms）と矛盾しない。
- sliding window型は，毎フレーム窓全体を入力し直すことと，パラメータ数が約10倍であることの両方が効いていると考えられる（どちらが効いているかは分けて確かめていない）。

## 結果（GPU1：RTX PRO 4500 Blackwell，val 25系列，計25508フレーム）

run名 `20261026_25seq_pro4500`（2026-10-27 06:09 完了）。sliding window型（18:17〜21:32）は GPU0 の計測と同時に流れていたが，SAM2・SAMURAI・state carry型は単独で流れた。

| 手法 | FPS | 1物体・1フレームあたり | ピークメモリ（allocated） |
|---|---|---|---|
| SAM2 | 2.94 | 35.3 ms | 1039 MB |
| SAMURAI | 2.87 | 36.2 ms | 1040 MB |
| Ours（sliding window型） | 2.48 | 42.0 ms | 1119 MB |
| Ours（state carry型） | 2.67 | 39.0 ms | 1051 MB |

- 速い順（SAM2 > SAMURAI > state carry型 > sliding window型）は A4000 の5系列と同じ。
- ピークメモリが A4000 より大きいのは，対象が25人の系列（dancetrack0094）など人数の多い系列を含むため。

## 測り直しは不要と判断（2026-10-27）

- GPU・系列数・同時実行の有無が異なる2つの計測で，手法の順序と「state carry型の増分は小さく，sliding window型だけがはっきり遅い」という結論が同じだった。
- 論文で FPS の小さな差（SAM2・SAMURAI・state carry型の間）を主張しない限り，ばらつき（約5%）は結論に影響しない。
