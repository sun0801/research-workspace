# Figure Manifest

## Source

- Experiment log: [../../2026-10-18-temporal-mamba-v3-mose-adapter.md](../../2026-10-18-temporal-mamba-v3-mose-adapter.md)
- Source data（SAM2 repo `/mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2`）:
  - V1: `runs/temporal_adapters/V1/20261022T211250+0900_ff78b57/`（142）の学習中のval
  - V3: `runs/temporal_adapters/V3/20261022T211148+0900_ff78b57/V3_val_log.jsonl`（141）。2026-10-23 07:25時点、step 1500まで
- 生成: `make_figure.py`（値はスクリプト内に転記）
- 使用先: [10/23 MTG資料](../../../materials/2026-10-23-weekly-progress-mtg-materials.md)

## Figures

| file | type | purpose | source | note |
|---|---|---|---|---|
| 01-train-val-jf-vs-f0.png | experiment | 学習中のval J&FをF0との差で示し、V1・V3ともstepとともに伸びる傾向がないことを見せる | V1・V3の学習中のvalログ | tuning先頭25動画・64対象。経過確認用でcheckpoint選択には使わない。V3は学習途中 |
