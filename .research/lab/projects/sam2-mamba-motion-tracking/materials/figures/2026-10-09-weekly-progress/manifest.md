# Figure Manifest

## Source

- Material: ../../2026-10-09-weekly-progress-mtg-materials.md
- Source files:
  - ../../../experiments/2026-09-30-mose-temporal-mamba-finetuning.md（2026-10-08 closeout）
  - ../../../experiments/2026-10-03-sam2mot-s4-qr-results.md（2026-10-08 追記）
  - ../../../experiments/2026-10-09-sam2mot-test-runs.md
- Source data: 上記ログに記載された集計値を手入力（matplotlib）

## Figures

| file | type | purpose | source | note |
|---|---|---|---|---|
| 01-sam2mot-hota-by-stage.png | experiment（再構成） | SAM2MOTの段ごとのHOTAを論文test・本再現test・本再現valで比較 | generated | S1 testは未提出。valとtestは別split |
| 02-mose-paired-jf-diff.png | experiment（再構成） | MOSE lockboxのJ&F差と95% CI | generated | 単一seed。F1 adapterは実質未学習 |
