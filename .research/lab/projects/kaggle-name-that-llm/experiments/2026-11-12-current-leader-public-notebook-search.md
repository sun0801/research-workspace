# 公開Leaderboard首位のNotebook source検索

**(b) 試さない。** Kaggle CLIのコンペNotebook一覧で、Leaderboardに表示されたteam label `NguyenThanhNhan` と小文字表記 `nguyenthanhnhan` のuser filter、およびtitle/content searchを試したが、いずれも`Not found`で再現可能なsourceを特定できなかった。

- 確認日: 2026-11-12 JST
- CLI: `uv run --env-file ../.env kaggle kernels list --competition name-that-llm --user <query> --sort-by dateRun --page-size 20`
- title/content search: `uv run --env-file ../.env kaggle kernels list --competition name-that-llm --search NguyenThanhNhan --sort-by relevance --page-size 20`
- Follow-up on 2026-11-12 17:52 JST: official Kaggle MCP `search_notebooks` with user `NguyenThanhNhan`, competition `name-that-llm`, sorted by run date, also returned zero kernels.
- Kaggle official web search: `site:kaggle.com/competitions/name-that-llm/discussion "0.768"` and `"NguyenThanhNhan"`; no relevant Name That LLM discussion with a reproducible method was returned. The search results were unrelated pages, so this is not proof that no such discussion exists.
- 対象: 公開Leaderboardのteam label `NguyenThanhNhan`（pre-push時点の首位`.768`）。Notebook本文・source・versionは未取得。
- 制約: team labelとKaggle owner slugが異なる可能性がある。この検索結果は、本人が公開NotebookやDiscussionを一切持たない証拠ではない。現時点で追試可能なsourceが見つからないため、試行候補にしない。
