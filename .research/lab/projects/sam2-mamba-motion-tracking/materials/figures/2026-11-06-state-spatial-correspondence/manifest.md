# Figure Manifest

## Source

- Material: ../../2026-11-06-weekly-progress-mtg-materials.md（週次資料）、../../2026-11-06-state-spatial-correspondence-mtg-materials.md（提案手法だけの短い版）
- Source files:
  - Claude Docs「MTG資料：潜在相関による state 運搬（①-b）と空間混合（②・②'）」（2026-11-04、https://claude.ai/artifact/Gfboj2uoaWB3ktmNbjciEn）の図1〜6を、2026-11-05 に SVG のまま取り出したもの
- Source data: なし（すべて概念図。図3の実効範囲の曲線は推論で、実験値ではない）

## Figures

| file | type | purpose | source | note |
|---|---|---|---|---|
| fig6-four-families-simple.svg | concept | 4 パターンの絵・一言説明・本研究の位置だけ | fig6-four-families.svg を編集 | 資料の主図。前例と注記を外し、絵を拡大（2026-11-05）。前例は資料の表に書く |
| fig6-four-families.svg | concept | 4 パターンと前例・注記 | Claude Docs 図6 | 元の版。資料では使わない |
| fig7-1b-in-model.png | concept | ①-b を V3 の 64 段にどう組み込んだか | generated（make_figs.py） | 資料で使用。`feat/latent-correspondence` の `CorrespondencePyramidAdapter` を読んで描いた |
| fig8-2-2p-in-model.png | concept | ②・②' を V3 の 64 段にどう組み込んだか | generated（make_figs.py） | 資料で使用。`feat/spatial-mixing-adapter` の `SpatialPyramidAdapter` を読んで描いた |
| fig1-v3-vs-1b-concept.svg | concept | V3 の state は元のマスに残り、①-b は物体についていく | Claude Docs 図1 | 図6・図7 と重なるので資料では使わない |
| fig3-2-2p-reach.svg | concept | ② は 2r で頭打ち、②' は実効 √s | Claude Docs 図3 | 設定例は ②' 3×3。実装は 7×7（L1 正規化） |
| fig4-plan-and-conditions.svg | concept | 進める順番と比較条件 | Claude Docs 図4 | ②' を 3×3 と表記（実装は 7×7） |
| fig2-1b-pipeline.svg | concept | ①-b の 1 フレームの処理 | Claude Docs 図2 | **古い設計**（argmax＋往復チェック＋0 リセット）。実装は softmax（τ=0.02）の重みつき輸送 |
| fig5-1b-vs-2-2p.svg | concept | ①-b と ②・②' の比較表 | Claude Docs 図5 | ①-b を argmax と表記（古い設計） |
