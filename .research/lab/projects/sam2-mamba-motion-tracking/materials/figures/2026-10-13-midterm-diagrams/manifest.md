# 中間発表スライドの自作図（抜き出し版）

[中間発表スライド（再構成版）](../../2026-10-12-midterm-slides-restructured.pptx)のうち、自分で描いた図だけを残したpptx。本体のpptxを壊したり上書きしたりしたときに、ここから図をコピーして戻すために置く。図はPowerPointの図形・表のままで、編集できる。

`2026-10-13-midterm-diagrams.pptx`（2026-10-13 夜の本体から抜き出し。スライド全体を残す）:

| # | 本体での位置 | 図 |
|---:|---|---|
| 1 | 3枚目 従来のMOT手法 | TBD / TBA の概念図（[説明](../2026-10-13-mot-paradigm-diagrams/manifest.md)） |
| 2 | 4枚目 関連研究：SAM2ベースの追跡 | SAM2とSAMURAIの構成図。ユーザー作成の `関連研究.pptx` の図の配色・入力画像を使い、1列に収まるよう要素を絞って組み直した（SAM2のpromptとSAMURAIのobject headは省略） |
| 3 | 5枚目 既存手法の整理 | 動き予測とMOT対応の比較表 |
| 4 | 6枚目 研究の目的 | SAMURAI → 本研究の比較図 |
| 5 | 9枚目の直後（新規） 動き予測の2つの構成 | (a) sliding window型（新規作図。state carryの図と同じ配色・帯の構成）と (b) state carry型（既存の図をコピー） |
| 7 | 9枚目 Mambaを用いた動き予測 | 課題点のスライドの図を「正しく追跡できている場合」に描き直したもの |
| 6 | 末尾（非表示） | （旧）bbox系とマスク系がSAM2MOTで合流する流れ図 |

- 本体で図を直したら、この抜き出し版も作り直す。
- pptxは `.gitignore` の対象なので、このファイルはGitに入らない。

## 画像での確認（png/）

`export_png.py` で、抜き出し版の各スライドをPNG（200dpi、2667×1500）に書き出す。

```bash
SOFFICE=/path/to/soffice python export_png.py   # 既定: このフォルダのpptx → ./png
```

| ファイル | 図 |
|---|---|
| `png/01-tbd-tba.png` | TBD / TBA の概念図 |
| `png/02-related-work.png` | 関連研究（SAM2 / SAMURAI） |
| `png/03-method-table.png` | 比較表 |
| `png/04-research-goal.png` | 目的の比較図 |
| `png/05-old-bbox-mask-merge.png` | （旧）合流図 |
| `png/06-sliding-window-vs-state-carry.png` | Mambaによる時系列情報の取り込み方（sliding window型とstate carry型を左右に並べた図） |
| `png/07-motion-prediction.png` | Mambaを用いた動き予測（正常な場合の模式図） |
| `png/08-proposed-method.png` | 提案手法（SAM2 より後ろを ID 1〜4 の4枚重ねにし，矢印も4本ずつ描いた図。2026-10-16 先生のFB F3 で上下に並べた版から変更） |
| `png/09-proposed-method-stacked.png` | （旧）提案手法：IDごとのマスクを重ねた図（差し替え用に残す） |
| `png/10-proposed-method-issue.png` | 提案手法の課題点（8枚目の4枚重ねの図をそのまま使い，手前の ID 1 の取り違えを ①② で示す。2026-10-16 先生のFB F4） |

- PNGはLibreOfficeで描いたもの。この環境にないフォントは置き換わる（テーマの「Noto Sans JP」→「Noto Sans CJK JP」）ため、PowerPointの表示と少しずれることがある。
- 図を直したら、pptxと一緒にPNGも書き出し直す。
