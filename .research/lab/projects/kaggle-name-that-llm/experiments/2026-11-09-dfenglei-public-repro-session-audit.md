---
date: 2026-11-09
project: kaggle-name-that-llm
type: source-review
status: reviewed
tags: [public-notebook, session-status, reproduction]
---

# dfenglei public reproduction Notebook session check

## Scope

On 2026-11-09 around 09:56 JST, queried the official Kaggle MCP session status and output listing for [`ntl-repro-0681`](https://www.kaggle.com/code/dfenglei/ntl-repro-0681) and [`ntl-repro-0680-fix`](https://www.kaggle.com/code/dfenglei/ntl-repro-0680-fix). Both status responses were `COMPLETE`. Each output listing included `submission.mode.json` and `submission.parquet`.

## What this establishes

The queried sessions have completed and have submission-shaped output files. The output listing did not provide a score, validation metric, scored Notebook version, or evidence that the displayed title score corresponds to this session. The returned stdout/stderr entries were empty. Earlier Notebook metadata had `last_run_time` on Nov 6 UTC while search DateRun results showed Nov 9 UTC, so the timestamp discrepancy remains unresolved. Completion alone does not establish reproducibility or a score above the public leaderboard.

## Decision

Do not change the registered GPU queue or treat these sessions as validation evidence. Keep the titles' scores as author claims pending a version-linked Kaggle result and a documented prompt-grouped OOF protocol. No Kaggle Notebook was created or edited, and no submission was made by us.
