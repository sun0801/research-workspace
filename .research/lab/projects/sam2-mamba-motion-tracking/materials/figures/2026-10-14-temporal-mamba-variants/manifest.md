# Figure Manifest

## Source

- Material: 10/16 MTG説明用（temporal Mamba統合方法の候補V1〜V4と進め方）。2026-10-13〜14の壁打ち内容を図示。実装・実測は未実施
- Source files:
  - ../2026-10-09-temporal-mamba-design-options/（①〜⑤の元図。V1〜V4との対応：①→V1、④→V2（②は64×64の場合としてV2に含む）、⑤→V3、③→V4）
  - ../../../meetings/2026-10-09-mtg.md（探索フェーズ・FPN的統合を含む複数案を並行）
  - ../../../experiments/2026-09-30-mose-temporal-mamba-finetuning.md（学習速度・tuning評価時間・VRAM）
  - SAM2 repo `sam2/modeling/temporal_mamba_adapter.py`, `sam2/modeling/sam2_base.py`, `setup.py`（現行adapter構造、高解像度特徴、mamba-ssm 2.2.2。読み取りのみ）
- Generator: `make_figs.py`（matplotlib。`python3 make_figs.py <出力dir>`）

## Figures

| file | type | purpose | source | note |
|---|---|---|---|---|
| 01-variants-v1-v4.png | concept | V1〜V4の比較（Mambaに入るもの・stateの持ち方・空間情報・根拠・リスク）。本命V2・V3・V4、対照V1 | generated | 挿入位置は現行のb（V3は高解像度特徴も含む）。10/9図の②（全位置）はV2のグリッド64×64として扱う。VRAMは未実測 |
| 02-v3-fpn-detail.png | concept | V3「FPN的」の具体案：64×64・128×128・256×256の各段でMambaを回し、段どうしをつなぐ（(a)出力・(b)state・(c)後で合成） | generated | 解釈案。10/16 MTGで先生の意図を確認する。2026-10-14に「粗い段だけでMamba」案から差し替え |
| 03-v4-streaming-scan.png | concept | V4時空間scan：VideoMamba型（オフライン）との違い、carry/reset比較、要確認事項 | generated | 初期state受け渡しは未確認 |
| 04-screening-plan.png | concept | 4段階の進め方（LR修正確認 → 共通化・実測 → スクリーニング → 本学習）と比較条件の読み方 | generated | 本学習18時間は前回F0速度からの概算 |
