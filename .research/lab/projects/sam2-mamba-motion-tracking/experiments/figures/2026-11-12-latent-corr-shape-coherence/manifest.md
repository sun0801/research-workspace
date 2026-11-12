# Figure Manifest

## Source

- Experiment: [../../2026-11-12-latent-corr-shape-coherence.md](../../2026-11-12-latent-corr-shape-coherence.md)（A-b の形の崩れの計測、11/6 MTG の指摘）
- 生成：2026-11-12、host 142、GPU 0（RTX A4000）、SAM2 repo の `.venv-sam2`（torch 2.10.0+cu128）。SAM2 repo は `dev`（`190787c`）の `training/measure_correspondence.py`・`sam2/modeling/latent_correspondence.py` を読み取りだけで使った（変更なし）。
- コマンド（SAM2 repo のルートで、`D` はこのフォルダ）：
  1. `CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=0 PYTHONPATH=$PWD .venv-sam2/bin/python $D/compute.py --out $D/data`（16:23〜16:35、ログは `data/compute.log`）
  2. `fields.pt`（375 MB、マスごとの移動と運んだマスク）は `runs/latent_corr/shape_coherence/20261112/fields.pt` に移した（git の管理外）。
  3. `.venv-sam2/bin/python $D/fig.py --data $D/data`（図5枚と `data/summary.md`）
- 入力：MOSE train の tuning 125動画（`runs/spatial_mixing/motion/20261104/tuning_object_motion.jsonl` の物体と、速さの三分位の区切り 0.620・1.233 マス）、F0（`runs/mose_temporal_mamba_20260930/F0_step_002789.pt`）の画像エンコーダ、torchvision の RAFT large の重み。
- sha256：
  - 8dcd859e8a2a5717c6e88fdf5b242c03114b64c1b7a9a61e2331caa0adae41ab  data/pairs.jsonl
  - 71d72b14fbe34345dd7a4633319367f7b350ea8c925f16ccfeddb91682a1d9c3  fields.pt（SAM2 repo 側）
  - 0b3608b49d1925edd3970b8aff917a2f81dcdc4dc74b60c3e10e57c1b419a5fa  data/summary.md

## Figures

図の中には、描いたものの情報（列・行の名前、軸、凡例）だけを入れ、読み取りは実験ログとMTG資料に書く（11/12 ユーザーの指摘で作り直した）。

| file | type | purpose | source | note |
|---|---|---|---|---|
| 01-arrows-median.png | experiment | 速さの層ごとに1例。A-b と RAFT で、物体の各マスが t−1 のどこから state を持ってくるかを矢印で示す | pairs.jsonl・fields.pt・MOSE train | 例は規則で選んだ：各層で、目標のマスが40以上ある組のうち、A-b の「隣と1マス以上ずれる辺の割合」が中央値（50%点）の組。マスは物体の大きさで1・2・3マスおきに間引き。色は隣のマスとの差の最大が1マスを超えるか |
| 02-arrows-p90.png | experiment | 同じ図で、90%点の例（崩れが大きい側） | 同上 | 同上 |
| 03-coherence.png | experiment | 隣と1マス以上ずれる辺の割合・折り返しの割合（A-b、argmax、RAFT） | pairs.jsonl | 物体ごとに組の平均を取り、層で物体の平均。ひげは物体の bootstrap 95% 区間（10,000回、seed 123） |
| 04-masks-median.png | experiment | 01 と同じ組で、t−1 の物体の被覆率を A-b・RAFT で運んだ結果と正解の輪郭 | pairs.jsonl・fields.pt・MOSE train | 被覆率0.05未満は表示しない |
| 05-iou.png | experiment | 運んだマスク（0.5以上）と正解の IoU（4方式） | pairs.jsonl | 集計は03と同じ |
