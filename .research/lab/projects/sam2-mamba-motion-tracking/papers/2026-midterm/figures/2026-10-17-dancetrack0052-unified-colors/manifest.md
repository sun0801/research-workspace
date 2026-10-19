# dancetrack0052 の図の色をそろえた版（2・3枚目, 2026-10-17）

4枚目以降の図（[SAMURAI・提案手法の構成図](../2026-10-15-samurai-per-id/manifest.md)の `masks_all.png`）では、frame 1 の左から順に4人を **紫（ID 1）・緑（ID 2）・赤（ID 3）・黄（ID 4）** で塗っている。2枚目の動画と3枚目の図は、元のGTのID順に赤・青・緑・紫で、左端の人が「ID 2」になっていた。そこで、同じ人に同じ色・同じ番号が付くように作り直した。

| 元のGTのID | 位置（frame 1） | 表示のID | 色（BGR） |
|---:|---|---|---|
| 1 | 左端 | ID 1 | 紫 (225, 48, 101) |
| 0 | 左から2人目 | ID 2 | 緑 (44, 184, 22) |
| 2 | 左から3人目 | ID 3 | 赤 (99, 76, 226) |
| 3 | 右端 | ID 4 | 黄 (8, 179, 216) |

色は `masks_all.png` の枠線から取った。

| ファイル | 中身 | 元の素材 |
|---|---|---|
| `2026-10-17-dancetrack0052-whole-gt.mp4`（+poster） | 2枚目上段。GTの枠とID、全1203フレーム、1280×720、20fps | [2026-10-13 の whole-gt](../2026-10-13-dancetrack0052-mot-example/manifest.md) |
| `2026-10-17-dancetrack0052-whole-mask.mp4`（+poster） | 2枚目下段。GT bboxからSAM2で作った擬似マスク（IDラベルなし）、全1203フレーム、20fps | [2026-10-14 のマスク動画](../2026-10-14-dancetrack0052-mask-example/manifest.md) |
| `2026-10-17-trk_{0,1,2}.png` | 3枚目の「ID付き」（frame 7 / 15 / 23）。IDの番号なし、太い枠 | [2026-10-15 の trk_k.png](../2026-10-15-mot-paradigm-timeline/manifest.md) |

- `make_unified_colors.py` が元の3つのスクリプトの色だけを差し替えて呼ぶ。描き方・切り出し・マスクの作り方は元と同じ。SAM2 repo の `.venv-sam2` で実行する（マスク動画はGPUで約8分）。
- マスクは元と同じくSAM2の擬似マスクで、GTではない。
