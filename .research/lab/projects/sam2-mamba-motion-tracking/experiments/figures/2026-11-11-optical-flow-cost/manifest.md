# Figure Manifest

## Source

- Experiment: [../../2026-11-11-optical-flow-cost.md](../../2026-11-11-optical-flow-cost.md)（A-a の宿題、11/6 MTG）
- Source data: このフォルダのスクリプトで生成し、`data/` に保存（2026-11-11、host 142、`.venv-sam2` の Python 3.12.3・cv2 4.13.0）
  - 18126a947a923f1ebf755d60df9d35b7338f3ce01d02fab7e98ab1f0d51ae8f1  selected_videos.json
  - e15da00621fb1a03215825dabc924980f1eeded7aafad667b081375a0f9f9bb7  timing.json
  - 09ea1cdc2ab7bad70ab7559ab3e09e861e10368fbb7d7b930900c1c4c6749a3f  timing_repeat.json
  - 0bc81f6713007d690f528f583b224836eb1dc72f2532769398729e502f900f04  timing_raft.json（RTX A4000、torch 2.10.0、torchvision 0.25.0）
- 生成（このフォルダで、`P=/mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2/.venv-sam2/bin/python`）:
  1. `$P select_videos.py --out data/selected_videos.json`
  2. `$P flow_cost.py --selection data/selected_videos.json --out data/timing.json`
  3. `$P flow_cost.py --selection data/selected_videos.json --sizes 1024sq 256sq --threads 1 --out data/timing_repeat.json`
  4. `$P summarize.py > data/summary.md`
  5. `$P flow_viz.py --selection data/selected_videos.json --stratum fast --out 01-flow-fast.png`、`--stratum slow --out 02-flow-slow.png`
  6. `CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=0 $P flow_raft.py --selection data/selected_videos.json --updates 12 6 --out data/timing_raft.json`（`CUDA_DEVICE_ORDER` を付けないと cuda:0 が GPU 1 になる）
  7. 同じ環境変数で `$P flow_viz.py --selection data/selected_videos.json --stratum fast --panels raft --out 03-raft-fast.png`、`--stratum slow --out 04-raft-slow.png`
- 入力：MOSE train（`/mnt/HDD10TB-2/aburatani/dataset/MOSE-v1-data/MOSE_release/train`）と、SAM2 repo `runs/spatial_mixing/motion/20261104/`（物体ごとの動きの中央値・三分位の区切り）。

## Figures

| file | type | purpose | source | note |
|---|---|---|---|---|
| 01-flow-fast.png | experiment | 速い動画3本で、Farneback・DIS 3設定（1024）と DIS ultrafast（256）の flow の見た目を並べる | selected_videos.json、MOSE train | 各動画1組。最初の20組のうち、最初の物体の重心の移動が中央値に最も近い組。色の明るさは正解の移動の1.5倍で飽和 |
| 02-flow-slow.png | experiment | 遅い動画3本で同じ比較 | 同上 | 同上 |
| 03-raft-fast.png | experiment | 速い動画3本で、DIS ultrafast（1024）と RAFT small・large（1024・256、更新12回）を並べる | selected_videos.json、MOSE train、torchvision の RAFT の重み | 組の選び方と色は 01 と同じ |
| 04-raft-slow.png | experiment | 遅い動画3本で同じ比較 | 同上 | 同上 |
