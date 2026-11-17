---
date: 2026-11-17
project: kaggle-name-that-llm
type: official-status
---

# Official competition status — 2026-11-17

- Kaggle competition metadata checked at 12:25 JST: Name That LLM, 6,138 teams; final deadline `2027-01-14T23:59:00.817Z` (2027-01-15 08:59 JST); new-entrant deadline `2027-01-06T23:59:00Z`; kernel submissions only; five submissions per day; two final submissions.
- Public leaderboard checked at 12:34 JST: top score `.776`; 2nd `.771`, 3rd `.770`. The selected public Notebook baseline remains `.620`; the official leader is recorded as context only.
- Rules page: external data/models are allowed when publicly available at no cost or otherwise reasonably accessible with minimal cost. Winner obligations include an OSI-approved license for winning code; incompatible data/model licenses are excepted. Dataset access/use license is CC BY-SA 4.0.
- Evaluation page: balanced accuracy across 18 labels; interactive `test.csv` has one example row, while hidden scoring reruns on about 4,000 passages. Submission must contain every `id` once and valid `model` labels in `submission.parquet`.
- Selected baseline and OLMo addition sources use public CC BY-SA 4.0 data and Apache-2.0 model weights; the OLMo asset Dataset and Notebook remain private.
- Pre-push gate rechecked at 18:31 JST: metadata now lists 6,169 teams; public top remains `.776`; Notebook-only, Internet disabled, and CPU/GPU runtime cap ≤9h remain in Code Requirements. CLI showed today's five submission slots already used. Metadata deadline remains Jan 14 23:59 UTC while Timeline says Jan 13 23:59 UTC; preserve the official-page discrepancy.

Sources: [competition overview](https://www.kaggle.com/competitions/name-that-llm/overview), [rules](https://www.kaggle.com/competitions/name-that-llm/rules), [evaluation](https://www.kaggle.com/competitions/name-that-llm/evaluation).
