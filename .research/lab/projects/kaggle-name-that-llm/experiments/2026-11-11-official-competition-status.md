---
date: 2026-11-11
project: kaggle-name-that-llm
type: official-competition-status
source: Kaggle official MCP
---

# Official competition status — 2026-11-11

Checked once for today's operations at 00:02 JST using Kaggle official MCP.

## Current official status

- Public leaderboard: James Liebel leads at `.755`; Le Viet and Meni David Gottesman are next at `.752`.
- Team count: 5,365.
- Rules: up to five submissions per day and two final submissions.
- Timeline page: Final Submission Deadline is January 13, 2027, 23:59 UTC. Competition metadata separately reports January 14, 2027; keep the earlier Timeline date as the conservative deadline.
- Code Requirements: submissions must use Notebooks; internet disabled; CPU or GPU runtime at most nine hours; output file `submission.parquet`. Freely and publicly available external data and pretrained models are allowed.
- Evaluation metric: balanced accuracy.

## Operational consequence

The adopted baseline-blend Notebook remains the first submission target. Keep the same Qwen3-8B + Qwen3-1.7B + prompt-centered SVC composition, pass the measured nine-hour runtime gate, then submit once to map OOF BA to public LB. Recheck official pages immediately before Notebook push or submission, as required by the 2026-11-10 operating amendment. No Kaggle object was pushed or submitted during this status check.

## Sources

- [Competition overview](https://www.kaggle.com/competitions/name-that-llm)
- [Official rules](https://www.kaggle.com/competitions/name-that-llm/rules)
- [Timeline](https://www.kaggle.com/competitions/name-that-llm/overview#timeline)
- [Code requirements](https://www.kaggle.com/competitions/name-that-llm/overview/code-requirements)
- [Public leaderboard](https://www.kaggle.com/competitions/name-that-llm/leaderboard)
