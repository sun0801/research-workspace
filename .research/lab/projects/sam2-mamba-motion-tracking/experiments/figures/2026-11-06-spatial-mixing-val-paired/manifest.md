# Figure Manifest

## Source

- Experiment: [../../2026-11-04-temporal-mamba-spatial-mixing.md](../../2026-11-04-temporal-mamba-spatial-mixing.md)
- Material: [../../../materials/2026-11-06-weekly-progress-mtg-materials.md](../../../materials/2026-11-06-weekly-progress-mtg-materials.md)
- Source data（SAM2 repo `/mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2`、動画単位の paired bootstrap 10,000回・seed 123）:
  - `runs/spatial_mixing/summary/compare.json`、`runs/spatial_mixing/summary/did.json`
  - `runs/spatial_mixing/D2/summary/did.json`
- 生成: `make_figure.py`（`python3 make_figure.py` でこのフォルダに出力）

## Figures

| file | type | purpose | source | note |
|---|---|---|---|---|
| 01-val-jf-paired-diff.png | experiment | ②・②' と A・F0 の差、state の寄与 R と増加 I（M0・M1）を 95% 区間で並べる | 上の JSON | スタイルは 2026-10-30-short-clip-val-paired に合わせた |
