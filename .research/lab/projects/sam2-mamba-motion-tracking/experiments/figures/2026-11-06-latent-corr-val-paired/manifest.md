# Figure Manifest

## Source

- Experiment: [../../2026-11-04-temporal-mamba-latent-correspondence.md](../../2026-11-04-temporal-mamba-latent-correspondence.md)（評価1巡目・2巡目の集計）
- Material: [../../../materials/2026-11-06-weekly-progress-mtg-materials.md](../../../materials/2026-11-06-weekly-progress-mtg-materials.md)
- Source data: 141 SAM2 repo `runs/latent_corr/summary/` の集計（動画単位の paired bootstrap 10,000回・seed 123）を `data/` に複製（2026-11-06）
  - cb3e735e811892885d5c2b26a1f9b4af103a9d415e1172c32ed4bf1a2d759094  Ap_compare.json
  - 86adf894ad227b075b6fc11e45312f4313ac58b2a4974cf7a113122d4d740a3e  round1_did_all.json
  - c496607251ab477f1486b7a5d9f50b3a14a406daab63efe016a8f4903aae8671  round2_did_all.json
- 生成: `make_figure.py`（`python3 make_figure.py` でこのフォルダに出力）

## Figures

| file | type | purpose | source | note |
|---|---|---|---|---|
| 01-val-jf-paired-diff.png | experiment | ①-b の F0・A' との差、state の寄与 R と増加 I、推論だけ対応を壊す対照（U_id・U_shuf）を 95% 区間で並べる | data/round1_did_all.json、data/Ap_compare.json | U_diag は diag = identity のため描かない |
