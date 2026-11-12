# Figure Manifest

## Source

- Experiment: [../../2026-11-12-latent-corr-shape-coherence.md](../../2026-11-12-latent-corr-shape-coherence.md)（A-b の形の崩れの計測、11/6 MTG の指摘）
- 生成：2026-11-12、host 142、GPU 0（RTX A4000）、SAM2 repo の `.venv-sam2`（torch 2.10.0+cu128）。SAM2 repo は `dev`（`190787c`）の `training/measure_correspondence.py`・`sam2/modeling/latent_correspondence.py` を読み取りだけで使った（変更なし）。
- コマンド（SAM2 repo のルートで、`D` はこのフォルダ）：
  1. `CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=0 PYTHONPATH=$PWD .venv-sam2/bin/python $D/compute.py --out $D/data`（16:23〜16:35、ログは `data/compute.log`）
  2. `fields.pt`（375 MB、マスごとの移動と運んだマスク）は `runs/latent_corr/shape_coherence/20261112/fields.pt` に移した（git の管理外）。
  3. `.venv-sam2/bin/python $D/fig.py --data $D/data`（図3枚と `data/summary.md`）
- 入力：MOSE train の tuning 125動画（`runs/spatial_mixing/motion/20261104/tuning_object_motion.jsonl` の物体と、速さの三分位の区切り 0.620・1.233 マス）、F0（`runs/mose_temporal_mamba_20260930/F0_step_002789.pt`）の画像エンコーダ、torchvision の RAFT large の重み。
- sha256：
  - 8dcd859e8a2a5717c6e88fdf5b242c03114b64c1b7a9a61e2331caa0adae41ab  data/pairs.jsonl
  - 71d72b14fbe34345dd7a4633319367f7b350ea8c925f16ccfeddb91682a1d9c3  fields.pt（SAM2 repo 側）
  - 0b3608b49d1925edd3970b8aff917a2f81dcdc4dc74b60c3e10e57c1b419a5fa  data/summary.md

## Figures

| file | type | purpose | source | note |
|---|---|---|---|---|
| 01-examples-median.png | experiment | 速さの層ごとに1例。A-b と RAFT で物体のマスを運んだ結果と、各マスの移動（どこから state を持ってくるか）を並べる | pairs.jsonl・fields.pt・MOSE train | 例は規則で選んだ：各層で、目標のマスが40以上ある組のうち、A-b の「隣と1マス以上ずれる辺の割合」が中央値（50%点）の組。矢印はマスを間引いて表示（物体の大きさで1・2・3マスおき）。色は隣のマスとの差の最大が1マスを超えるか |
| 02-examples-p90.png | experiment | 同じ図で、90%点の例（崩れが大きい側） | 同上 | 同上 |
| 03-summary.png | experiment | 4つの対応の取り方（A-b、argmax、RAFT、identity）で、隣とのずれ・折り返し・運んだマスクの IoU を速さの層ごとに比べる | pairs.jsonl | 物体ごとに組の平均を取り、層で物体の平均。ひげは物体の bootstrap 95% 区間（10,000回、seed 123） |
