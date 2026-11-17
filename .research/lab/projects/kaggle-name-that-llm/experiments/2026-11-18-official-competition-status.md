---
date: 2026-11-18
project: kaggle-name-that-llm
type: official-competition-status
---

# 2026-11-18 Official Competition Status

確認時刻: 00:00 JST（Kaggle MCP、competition metadata / leaderboard / pages）

- Public leaderboard top: `.776`; team count: `6,201`. Current project Public best remains `.626` (ref `58456880`); the top score is context, not the add-on rejection threshold.
- Evaluation remains balanced accuracy. The public and private test sets have different model mixes.
- Code Requirements: Notebook-only submissions, Internet disabled, CPU/GPU runtime at most 9 hours, output `submission.parquet`. Interactive `test.csv` has 3 preview rows; scoring reruns against about 4,000 hidden rows.
- Limits: maximum 5 submissions/day; up to 2 final submissions.
- Deadline discrepancy remains: competition metadata says `2027-01-14 23:59 UTC`; Timeline page says `2027-01-13 23:59 UTC`. Continue treating the earlier Timeline date as operational.
- Authenticated `kaggle competitions submissions` returned the five most recent refs `58462545`, `58459599`, `58456880`, `58453689`, `58452056`, all dated 2026-11-17 UTC. It shows no newer submission; the daily reset/available-slot interpretation is not inferred from this list alone.
- Authenticated `kaggle quota`: GPU used `2.64h`, remaining `27.36h / 30h`; refresh `2026-11-21 09:00 JST`.

Sources: [competition overview](https://www.kaggle.com/competitions/name-that-llm), [rules](https://www.kaggle.com/competitions/name-that-llm/rules), [timeline](https://www.kaggle.com/competitions/name-that-llm/overview#timeline), [evaluation](https://www.kaggle.com/competitions/name-that-llm/overview#evaluation), [code requirements](https://www.kaggle.com/competitions/name-that-llm/overview#code-requirements).

## 00:21 JST pre-submission refresh

- Rechecked official metadata/pages and Public leaderboard immediately before the planned `.684` baseline submission: top remains `.776`; team count is now `6,203`. The 5/day and 2-final-submission limits, Notebook-only/offline/9-hour/output requirements, balanced-accuracy evaluation, and Jan 13 vs Jan 14 UTC deadline discrepancy are unchanged.
- Authenticated submission list still shows the latest five refs dated 2026-11-17 UTC and no 11/18 UTC entry. The daily slot has not been confirmed as available; do not infer reset from JST date alone.
- GPU quota is `27.36h/30h`, refresh `2026-11-21 09:00 JST`; rate guard passed at 00:21 JST (5-hour 85%, weekly 64%).
