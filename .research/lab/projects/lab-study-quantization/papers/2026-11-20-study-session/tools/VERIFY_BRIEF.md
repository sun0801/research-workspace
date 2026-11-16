# 検査者への共通指示（量子化勉強会スライド3案）

あなたは3案（A/B/C）の作者ではない．検査だけを行い，スライドは編集しない（指摘を書くだけ）．
対象（フォルダ: `.research/lab/projects/lab-study-quantization/papers/2026-11-20-study-session/`）:
- `2026-11-17-quantization-study-{a,b,c}.pptx` / `.pdf` と作者メモ `…-{a,b,c}-notes.md`
- 基準: spec `../../specs/2026-11-13-quantization-study-session-spec.md`（全文を読む．時間配分は spec の表が正．作者向けの `tools/BRIEF.md` には spec と区間名が食い違う箇所があり，B案はそれに従った．ずれは「B案の時間配分」の指摘として扱う），結果ログ `../../experiments/2026-11-13-quantization-handson-results.md`，引用ノート `2026-11-13-quantization-study-citations.md`，ハンズオン `/mnt/HDD10TB-2/aburatani/quantization_handson`，原典PDF `../../references/papers/`，見本の作法 `.research/lab/projects/sam2-mamba-motion-tracking/papers/journal-club-2026/2026-11-06-journal-club-sample-verification.md`（テンプレート準拠版以降）．
道具: `tools/render.sh`, `tools/check_overflow.py`, Python は `/tmp/claude-1123/-mnt-HDD10TB-2-aburatani-research-workspace/05d63be6-d3cd-4cbc-b291-459b52e857b9/scratchpad/pptvenv/bin/python`（python-pptx入り）．pptxの文字は python-pptx で，原典はpdftotext/画像で確認．
出力: 指定のファイル（`verification-raw/` 配下）に，案ごとに「指摘表（スライド番号，指摘，根拠，重大度: 必須修正／推奨／好み，修正案）」と「確認した範囲」を日本語で書く．確認していないものは確認していないと書く．
触れないもの: コミット・push，他案・既存ファイルの編集，GPU，Kaggle・sam2．最終報告は，案ごとの必須修正の件数と代表例を短く．
