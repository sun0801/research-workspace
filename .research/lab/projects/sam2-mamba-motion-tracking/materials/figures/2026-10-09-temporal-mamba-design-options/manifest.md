# Figure Manifest

## Source

- Material: 10/9 MTG口頭説明用（temporal Mambaの画像側挿入の設計候補）。brainstorm（2026-10-09）で整理した内容を図示
- Source files:
  - ../../../meetings/2026-09-30-mtg.md（9/30 MTGの「次元を落とす必要があるか」「FPNなどの工夫」）
  - ../../2026-10-09-midterm-slide-review.md（「tokenと混ざる前に視覚特徴へ時間情報を加える」）
  - SAM2 repo `sam2/modeling/sam/mask_decoder.py`, `sam2/modeling/sam2_base.py`（デコーダ構造の確認）
- Generator: `make_figs.py`（matplotlib。`python3 make_figs.py <出力dir>`）

## Figures

| file | type | purpose | source | note |
|---|---|---|---|---|
| 01-insertion-positions.png | concept | 軸1：画像側の挿入位置 a〜d とSAM2の流れ | generated | b が現行位置 |
| 02-representation-options.png | concept | 軸2：Mambaへの渡し方①〜⑤と9/30の議論との対応 | generated | state量は次元からの概算、未実測 |
| 03-motion-misalignment.png | concept | 場所ごとのstateが物体移動でずれる問題と対処候補 | generated | 模式図 |
| 04-tradeoff-summary.png | concept | 空間情報と重さのトレードオフ、進め方の提案 | generated | 進め方は提案段階 |
