# Figure Manifest

## Source

- Experiment log: [../../2026-10-27-temporal-mamba-short-clip-official-trainer.md](../../2026-10-27-temporal-mamba-short-clip-official-trainer.md)（段階4 評価）
- Source data（SAM2 repo `/mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2`、142）:
  - `runs/short_clip/stage4/paired_summary.json`（動画単位のpaired bootstrap、95%区間）
- 生成: `make_figure.py`（JSONを直接読む）
- 使用先: [10/30 MTG資料](../../../materials/2026-10-30-weekly-progress-mtg-materials.md)

## Figures

| file | type | purpose | source | note |
|---|---|---|---|---|
| 01-val-jf-paired-diff.png | experiment | 短区間学習のA・B・CがF0を上回った一方、Mambaの効果（A−B・C−B）とstateの持ち越し（reset比較）は区間が0を含むことを1枚で見せる | paired_summary.json | MOSE val 125動画・313対象、単一seed。塗りつぶしは95%区間が0を含まない比較 |
