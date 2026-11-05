# Figure Manifest

## Source

- Log: [../../2026-11-04-temporal-mamba-spatial-mixing.md](../../2026-11-04-temporal-mamba-spatial-mixing.md)（「固定した200区間のloss」の節）
- Script: `make_figures.py`（SAM2 repo の `.venv-sam2/bin/python -I make_figures.py` で実行）
- Source data（SAM2 repo `/mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2/runs/`）:
  - 固定した200区間のloss: `short_clip/diag_loss_curve_spatial/per_clip.jsonl`（F0・A・B・Cは `diag_loss_curve/per_clip.jsonl` のコピー、②・②'は `scripts/loss_fixed_clips.py` で追加、RTX PRO 4500）
  - 同じ区間どうしの差の集計: `paired_diffs.json`（このフォルダ。SAM2 repo の同じrunフォルダにもコピー）

## Figures

| file | type | purpose | source | note |
|---|---|---|---|---|
| 01-fixed-clip-loss.png | experiment | 固定した200区間でのlossの学習曲線（A・②・②'） | diag_loss_curve_spatial/per_clip.jsonl | 10/30 図04と同じ形式。mix（学習と同じプロンプトの混合）、F0との差の中央値 |
