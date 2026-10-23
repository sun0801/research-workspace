# Figure Manifest

## Source

- Material: [../../2026-10-23-weekly-progress-mtg-materials.md](../../2026-10-23-weekly-progress-mtg-materials.md)（3.1節 V3の構造）
- Source files:
  - SAM2 repo `/mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2`、ブランチ `feat/temporal-mamba-v3` の `ff78b57`（本学習に使ったcommit）
    - `sam2/modeling/temporal_adapters.py`（`MambaCell`、`PyramidAdapter`、`GlobalPoolAdapter`）
    - `sam2/modeling/sam2_base.py`（adapterの呼び出し位置、メモリエンコーダの入力）
  - [V3 spec](../../../specs/2026-10-18-temporal-mamba-v3-mose-adapter-spec.md)
  - [10/14のV3の解釈案の図](../2026-10-14-temporal-mamba-variants/02-v3-fpn-detail.png)（つなぎ方(a)(b)(c)の候補。今回の図は(a)で実装したものを描いた）
- パラメータ数・d_innerは、上のcommitのコードでモデルを組み立てて数えた（V3 570,563、V1 504,065）
- 生成: `make_figs.py`（matplotlib、`python3 make_figs.py` でこのフォルダに出力）

## Figures

| file | type | purpose | source | note |
|---|---|---|---|---|
| 01-v3-position-in-sam2.png | concept | V3がSAM2のどこに入り、何を変えるか（3段の特徴、メモリにはマスク経由でだけ効く） | generated | 概念図。灰色＝固定、橙＝学習 |
| 02-v3-inside-one-frame.png | concept | 1フレームの中の計算（段ごとのLayerNorm→Mamba→W_out→α、段間のtop-down） | generated | 数値はコードから |
| 03-v3-state-over-time.png | concept | マスごとのstateの持ち越しと、位置固定のstateの問題 | generated | 8×8に縮めた模式図。位置ずれの影響の大小は未検証 |
