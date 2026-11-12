# Figure Manifest

## Source

- 資料：[../../2026-11-13-weekly-progress-mtg-materials.md](../../2026-11-13-weekly-progress-mtg-materials.md)（11/13 MTG、手法2の位置づけと A-b の改善の候補）
- 生成：2026-11-13、host 142、SAM2 repo の `.venv-sam2`。SAM2 repo のコードは読み取りだけ（変更なし）。
  - `python per_cell.py`、`python concept.py`（説明用の概念図。データは使っていない）
  - SAM2 repo のルートで `CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=0 PYTHONPATH=$PWD .venv-sam2/bin/python <このフォルダ>/example_weights.py`（GPU 0、RTX A4000）
- 入力（02）：MOSE train の動画 91b754c5（フレーム 23・24）、F0 の画像エンコーダ、11/12 の `runs/latent_corr/shape_coherence/20261112/fields.pt`（RAFT と A-b の移動）
- sha256：
  - 7a20e857d92f9df7194bccbf7f7c543b69b6188a2e97ff0064f5e72f5c4c4369  00-per-cell-vs-one-sequence.png
  - 976722177d989ee8d34d6947a12392c9a794c5fb24c4a381ad9eba67dc5658d3  01a-similarity.png
  - 7e8e26295a1ac9a8ed40629de8b7dda9330eaa85db3f8cdfd365479cfaab0b89  01b-constraint.png
  - aaf8336fb293ae2d7d85dad60e1adb442b41a770bcfe98db3610a95ef4f43bf7  01c-surroundings.png
  - 865448548c8c817b24049838aa1fc347346c94a0be25637cc7934fbdc5555a93  02-example-weights.png
  - fe4fba3baf0020625f68bfdb0096c380d06686d550793da948de5752dc544c34  example_weights.json

## Figures

図の中には描いたものの情報（題、凡例）だけを入れ、読み取りは資料の本文に書く。

| file | type | purpose | source | note |
|---|---|---|---|---|
| 00-per-cell-vs-one-sequence.png | explanatory | マスごとの Mamba（今の V3）と、全マスを1本の系列にする形の違い | なし（概念図） | 64×64 を 4×4 に簡略化。state の大きさ 10,240 は 64×64 の段の値（512 × (16+4)） |
| 01a-similarity.png・01b-constraint.png・01c-surroundings.png | explanatory | 対応の取り方の3段（類似度最大・制約を入れる案・周りごと照合する案）を1枚ずつ | なし（概念図） | 窓は 7×7 に簡略化（実際は 15×15）。重みは説明用の例。01c の線は対応する9組だけ描いた（実際は81組） |
| 02-example-weights.png | experiment（説明用の1例） | 1マスについて、A-b の重みが窓のどこに付くかと、RAFT の移動先 | MOSE train・F0・fields.pt | マスは規則で選んだ：11/12 の中くらいの層の中央値の例（91b754c5、物体3、フレーム24）の、物体の内側のマス（8近傍がすべて物体）のうち、A-b と RAFT の移動の差が最大のマス（行25・列30、差 3.95 マス）。τ=0.02 |

## 注意

- 02 の重みは、画像エンコーダを bf16 で計算し直している。同じスクリプトを2回実行すると、重みが最大の位置が (dy, dx) = (−1, −3) と (−2, −2) で入れ替わった（最大の重みは 0.108 と 0.112）。重みが平らなので、数値の小さな差で最大の位置が動く。図は2回目の実行。
- `example_weights.json` の `box3` は、周りごと照合のいちばん簡単な形（学習なしで、周り 3×3 の類似度を同じ移動について平均し、τ=0.02 で softmax）。このマスでは期待移動 (−3.48, −0.70) マスで、RAFT の移動 (0.79, 0.31) マスには近づかなかった（図には描いていない）。
