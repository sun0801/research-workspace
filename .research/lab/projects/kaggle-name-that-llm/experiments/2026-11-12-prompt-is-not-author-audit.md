---
date: 2026-11-12
project: kaggle-name-that-llm
type: public-notebook-audit
---

# (b) 試さない — “The Prompt Is Not the Author” v32

- Source: [prvsiyan, `The Prompt Is Not the Author`](https://www.kaggle.com/code/prvsiyan/the-prompt-is-not-the-author), public version 32. Read the metadata, opening claims, result table, and selected split/model code; no code was executed and no full dependency audit was done.
- The author says version 31 mirrors the `.684` lbjyang/ozertuu code unchanged. Version 32 clears outputs and changes only a complementary-stack weight from 0.15 to 0.10; it reports no new score. Kaggle metadata says version 32, while its last-run time predates the search listing, so there is no evidence this edit was scored.
- The author reports their own ModernBERT additions at 10%/20% lowered public score from `.683` to `.672`/`.669` (self-reported). Our prompt-paired fixed-addition screens independently rejected ModernBERT Base/Large. The notebook's public-data/prompt-geometry discussion does not supply a new registered candidate or a verified OOF gain over our adopted blend.
- Do not reproduce this version: its measured claims are below the current public leader`.765`, its latest weight change is unscored, and the directly relevant added-classifier path is already independently rejected. No implementation or trial started.
