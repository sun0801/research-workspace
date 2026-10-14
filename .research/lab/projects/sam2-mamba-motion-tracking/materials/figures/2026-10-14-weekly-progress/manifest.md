# Figure Manifest

## Source

- Material: ../../2026-10-14-weekly-progress-mtg-materials.md
- Source files:
  - ../../../experiments/2026-10-09-sam2mot-test-runs.md（S1 test は 2026-10-13 追記）
  - ../../../experiments/2026-10-13-sam2mot-o365tococo-val.md（3x_coco の val 行）
- Source data: 上記ログに記載された集計値を手入力（matplotlib）
- Generator: `make_figs.py`（`python3 make_figs.py <出力dir>`）

## Figures

| file | type | purpose | source | note |
|---|---|---|---|---|
| 01-sam2mot-test-gap-by-stage.png | experiment（再構成） | SAM2MOTの段ごとのHOTAを論文test・本再現testで比べ、差がAdd・CoIで開くことを示す | generated | 本再現valは別splitの参考。検出器は3x_coco、S4はQ-R補正方式 |

temporal Mamba の統合候補の図は [2026-10-14-temporal-mamba-variants](../2026-10-14-temporal-mamba-variants/manifest.md) を参照している（このフォルダには複製していない）。
