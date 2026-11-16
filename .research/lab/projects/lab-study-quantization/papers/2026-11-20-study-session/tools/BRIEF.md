# スライド作成者への共通指示（量子化勉強会，3案共通）

## 目的
2026-11-20 の研究室勉強会「量子化」（90分，聞き手はCV研究室メンバー，量子化は初学者）のスライド1案を作る．
案の違い（A 積み上げ型 / B 問題駆動型 / C 実験先行型）は spec の該当節に従う．

## 必読（この順）
1. spec: `.research/lab/projects/lab-study-quantization/specs/2026-11-13-quantization-study-session-spec.md`（全文．担当案の構成・時間配分・禁止事項）
2. 実験結果ログ: `.../experiments/2026-11-13-quantization-handson-results.md`（数値の出所．スライドの実測値は全てここから）
3. 原典の引用箇所: `.../papers/2026-11-20-study-session/2026-11-13-quantization-study-citations.md`（Appendix B の注意点を必ず守る）
4. 既存資料の調査: `.../2026-11-13-quantization-study-existing-materials.md`（「さらに学ぶ」と引用図の候補）
5. 見本の作法: `.research/lab/projects/sam2-mamba-motion-tracking/papers/journal-club-2026/2026-11-06-journal-club-sample-verification.md` の「テンプレート準拠版」以降（引用書式，句読点，配置，ノート）
6. ハンズオンリポジトリ `/mnt/HDD10TB-2/aburatani/quantization_handson`（README と ex1〜ex4．スライドから「演習①〜④」へ正しく誘導するため）

## 道具（作成済み，変更不要．必要なら tools/ に自分用の拡張を追加）
- `tools/slidekit.py`: `Deck` クラス（研究室テンプレートのマスター `tools/template.pptx` を使用．title_slide / section / bullets / two_col / image / table / textbox / source / save）．docstring 参照．言語タグ・フォント参照・ノート・出典(12pt)を自動で付ける．
- `tools/render.sh deck.pptx outdir`: LibreOffice で PDF と PNG（p-XX.png）を作る．
- `tools/check_overflow.py deck.pptx deck.pdf`: 枠外にはみ出した文字を数える（`OVERFLOW 0` が合格）．
- Python は `/tmp/claude-1123/-mnt-HDD10TB-2-aburatani-research-workspace/05d63be6-d3cd-4cbc-b291-459b52e857b9/scratchpad/pptvenv/bin/python`（python-pptx, pillow, matplotlib 入り）．
- 図の日本語は matplotlib でフォント（Noto Sans CJK JP / Noto Sans JP）を先に設定する．
- Excalidraw 等は使わない．概念図は matplotlib か python-pptx の図形で描く．

## 成果物（担当案 X = a / b / c）
- スライド: `papers/2026-11-20-study-session/2026-11-17-quantization-study-X.pptx` と同名 `.pdf`
- 作成スクリプト: `papers/2026-11-20-study-session/tools/build_X.py`（再生成できること）
- 図: 概念図は `papers/2026-11-20-study-session/figures/X/`（他案とファイル名が衝突しないよう必ず X のサブフォルダ）．実験由来の図は `.../experiments/figures/` にある正本を参照（コピー可，正本は変更しない）．実験由来の新しい図が要るときは，ハンズオンの `results/*.json` から作り，正本は `experiments/figures/` に保存．
- 作者メモ: `papers/2026-11-20-study-session/2026-11-17-quantization-study-X-notes.md`（枚数，時間配分表（枚ごとの分），数値と出典の対応表，不確かな点，案の特徴）．これは検査者が使う．

## 守ること
- 本編 35〜45 枚，各本編スライドのノートに読み上げ原稿．補足（付録）は本編外．節の扉は節ごと．
- 時間配分（spec の表が正．2026-11-14 訂正: 初版のこの行は誤っていた）: 0–10 なぜ量子化するのか／10–28 数値表現と一様量子化（演習①）／28–45 粒度と外れ値（演習②）／45–62 活性の量子化と較正・BN folding・WxAy（演習③）／62–80 PTQ と QAT・SmoothQuant・分類表（演習④）／80–90 判断基準・まとめ・質疑．
- 1枚の主張は1つ．タイトルは1行（40pt，約25字以内）．本文 28/24pt を継承，出典 12pt，図の注記・表は 16〜20pt 以上．文字が収まらないなら言い回しを短くし，補足はノートへ．
- 文体: 「，」を使う．文末に「。」を付けない．引用は「名前 [第一著者+, 会議名年]」．結果は 定量→Ablation→定性 の順．文字は上，図は下．
- 数値・主張は次の4種に分け，スライド上で区別する（出典欄に「原典: …」「本環境の実測」「説明用の計算例」「発表者の解釈」のいずれかを書く）:
  原典由来 / 本環境の実測（結果ログの節番号まで追える）/ 説明用の計算例（実測ではないと明記）/ 発表者の解釈（解釈と明記）．
- fake-quant（誤差シミュレーション，FP32で計算）と実際の低精度実行（演習④）を必ず区別する．fake-quant の結果を「高速化」と結び付けない．
- 実測の核心（結果ログ参照）: W8A8 はどの較正でもほぼ無劣化／W4 は per-tensor で崩れ per-channel・per-group で回復／DeiT-Tiny は A4 で較正法により大きく変わる（minmax 24.9, percentile 71.05, mse 47.6）／この DeiT-Tiny には LLM 型の極端な外れ値チャネルは見られない（max/median ≤4.3）．A4 崩壊の機序は未検証の解釈と明記する／QAT は1設定の結果で一般化しない（3 seed 平均）／INT8 の速度はモデルとカーネル次第（ResNet18 FX は約0.69×，DeiT torchao 重みのみ INT8 は同等〜やや遅い，動的 INT8 は約16倍遅い．共有マシンで雑音あり）．
- 原典の注意点（citations Appendix B）: percentile は FP8 論文 §4.2 のみ／Bengio の STE は確率的ニューロンの文脈／ViT の外れ値を直接扱うのは PTQ4ViT のみ／BRECQ と AdaRound は FP32 基準が違うので同じ表に載せない／arXiv ID 8本と PTQ4ViT・Q-Diffusion の会議名・年は未確認なので，スライドの引用に使うときは出典欄に「要確認」と作者メモに記録し，引用書式の会議名・年は確認済みのもの（原典 PDF の表紙で確認できるもの）だけ書く．式は PDF を目で見て確かめてから載せる．
- 演習への誘導: 演習①〜④のどこで何をするかを，該当スライドと，80–90 分の前のスライドで示す．演習の所要時間（結果ログ §2-4）を超える作業を求めない．
- 触れないもの: コミット・push，materials/entries，Kaggle・sam2 のファイル，GPU1，既存の他案のファイル．GPU は使わない（必要な図はCPU/既存JSONで作る）．
- 作成後に自分で: render → 全ページを画像で確認 → check_overflow が 0 → 直す．最終報告は「枚数，時間配分，作者メモのパス，未解決の不確かな点」を短く．検査は別のエージェントが行うので，検査はしなくてよい（自分の目視確認は必須）．
