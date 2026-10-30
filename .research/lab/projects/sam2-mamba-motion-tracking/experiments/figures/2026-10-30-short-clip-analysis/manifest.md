# Figure Manifest

## Source

- Material: [../../../materials/2026-10-30-weekly-progress-mtg-materials.md](../../../materials/2026-10-30-weekly-progress-mtg-materials.md)
- Script: `make_figures.py`（SAM2 repo の `.venv-sam2/bin/python -I make_figures.py` で実行）
- Source data（SAM2 repo `/mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2/runs/`）:
  - val の対象ごとの結果: 各runの `eval/tuning/<条件>/objects.jsonl`、F0 は `mose_temporal_mamba_20260930/tuning/F0_step_002789`、P0 は `short_clip/P0/eval/tuning/P0`
  - 対応つき比較: `short_clip/stage4_p0/paired_summary.json`（`training.mose_adapter_summary compare`、動画単位のpaired bootstrap、10,000回、seed 123）
  - 学習中の記録（Cometに送った値と同じ）: 各runの `samples.jsonl`・`val_history.jsonl`（B は141から142の同じパスへコピー）
  - 固定した200区間のloss: `short_clip/diag_loss_curve/per_clip.jsonl`（F0・A・B・C）、`short_clip/diag_loss_curve_p0/per_clip.jsonl`（F0・P0・D・E）

## Figures

| file | type | purpose | source | note |
|---|---|---|---|---|
| 01-p0-val-paired-diff.png | experiment | P0から始めたD・EのH5〜H7の判定と、外れ値1動画の影響 | stage4_p0/paired_summary.json、objects.jsonl | 白抜きは動画 e7b34ab6 を除いて同じ方法で再計算 |
| 02-jf-gain-by-frame-position.png | experiment | 学習の効果がフレームの経過とともに大きくなること | objects.jsonl の frame_metrics | 対象・フレームの重みの平均（動画平均ではない） |
| 03-training-log.png | experiment | Cometで見ていた学習lossとval-25の経過 | samples.jsonl、val_history.jsonl | 学習lossはepochごとの中央値 |
| 04-fixed-clip-loss.png | experiment | 固定した200区間でのlossの学習曲線（A〜E） | diag_loss_curve*/per_clip.jsonl | mix（学習と同じプロンプトの混合）、RTX PRO 4500 |
