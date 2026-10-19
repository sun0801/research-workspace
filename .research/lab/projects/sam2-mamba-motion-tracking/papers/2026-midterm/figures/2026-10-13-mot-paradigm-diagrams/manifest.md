# TBD / TBA の概念図（3枚目「従来のMOT手法」）

指摘「図を見てもわからない。重要な要素がわかる図にする。全体はいらない」（2026-10-13にユーザーが共有）に合わせ、論文の全体構成図（[Ding+, CVPR2024]）を、処理の流れだけを示す概念図に置き換えた。図はPowerPointの図形で描いており、スライド上で編集できる。

- **TBD**: フレーム → ①検出器 → 検出結果（IDなし）→ ②対応付け（前時刻までの軌跡を参照）→ ID付きbbox。要点は「検出と対応付けを別々に行う。対応付けはIoUや動き予測（KF）で判断」。
- **TBA**（MOTRに合わせた模式図）: フレーム → Transformer（encoder＋decoder。decoderに detect query と、前時刻から引き継いだ track query を入力）→ ID付きbbox。decoderが出す各物体の特徴（hidden state）が、次の時刻の track query になる（新しい物体は追加、消えた物体は削除）。要点は「検出と対応付けを1つのモデルで同時に行う。同じ track query が同じ物体を追い続ける」。

| ファイル | 中身 |
|---|---|
| `frame.png` | dancetrack0052 frame 1（最初のフレーム）の入力画像。4人の範囲を切り出し |
| `detections.png` | 同じ画像に、GTの枠を白（IDなし）で描いたもの。検出結果の例として使う |
| `tracks.png` | 同じ画像に、GTの枠とIDを色付きで描いたもの。追跡結果の例として使う |

- どれも正解データを使った模式図で、特定の手法の出力ではない（スライドに注記あり）。
- `make_thumbnails.py` で作り直せる。
- 2026-10-13: 画像をframe 125からframe 1に変更。TBAの代表例をTransTrackからMOTR [Zeng+, ECCV2022]（https://arxiv.org/abs/2105.03247）に変更した。描いた図（track queryがそのままIDになる）に合うのはMOTRで、TransTrackは最後にIoUで対応付けるため。
- 2026-10-13: MOTR論文（arXiv 2105.03247）と照合し、TBAの引き継ぎの矢印を「出力の枠から」ではなく「decoderの出力（各物体の特徴）から」出すよう修正した。MOTRで次の時刻に渡るのはdecoderのhidden stateで、Query Interaction Moduleが新しい物体（detect queryのスコア ≥ τ_en）を追加し、スコアが τ_ex 未満のまま続いた物体を削除する。あわせて箱の表記を「Transformer（encoder＋decoder）」にした。
- 2026-10-13: 図の文字を18pt中心にするため、各図を2段に組み替えた。TBDは「フレーム → 検出器 → 検出結果」の下に「前時刻までの軌跡 → 対応付け → ID付きbbox」を置き、検出結果と軌跡が対応付けに合流する形にした。TBAはdetect queryを上、track queryを下に置いた。本文の箇条書きは手法名と代表手法の2行に縮め、要点（18pt）を図の下に置いた。補足の文字（encoder＋decoder、引き継ぎの説明など）は12〜14pt。
- 2026-10-13: フレーム間の関係が見えるよう、TBDの「前時刻までの軌跡」を灰色の箱から、IDの色（1赤・2青・3緑・4紫。画像の枠と同じ）の点を t−3〜t−1 に並べた軌跡に変えた。時刻 t の列は破線の白丸で示し、出力から「時刻 t の位置を軌跡に追加」の矢印で戻す。TBAは track query に「（時刻 t−1 から）」、引き継ぎの説明に「時刻 t+1 のtrack queryへ」と時刻を書き込んだ。
