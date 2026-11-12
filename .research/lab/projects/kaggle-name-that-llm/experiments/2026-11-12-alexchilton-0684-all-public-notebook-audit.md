---
date: 2026-11-12
project: kaggle-name-that-llm
type: public-source-audit
status: rejected
tags: [public-notebook, ensemble, prompt-shape, leaderboard]
---

# Alex Chilton “0.684: All Public + What Failed” Notebook audit

## Decision

**(b) 試さない** for importing or reproducing the complete multi-source inference stack. Its author-reported Public `.684` is below the current official leader `.768`; the stack overlaps several already-audited public `.684` sources and depends on many upstream assets. Its test-shape discussion is a separate diagnostic lead and was evaluated under a fixed CPU-only spec; see [mean-field small-prompt result](2026-11-12-spectral-meanfield-small-prompt-shape-screen.md).

## Source and evidence

- [Kaggle Notebook](https://www.kaggle.com/code/alexchilton/name-that-llm-0-684-all-public-what-failed), `alexchilton/name-that-llm-0-684-all-public-what-failed`, public version 25, GPU enabled, Internet disabled. Notebook metadata last-run is Nov 9; its prose reports a `.684` public submission on Nov 11. Treat `.684` as the author's account, not independently verified by this inspection.
- Version 25 session status is `COMPLETE`. Its available output includes inference-stage source files and checks that optional inputs are mounted; it does not independently expose the public score or hidden-rerun traceback.
- The described ensemble combines multiple Qwen/Llama LoRA readouts, Qwen3-14B adapters, Qwen2.5-14B, DeBERTa, stylometric classifiers, a five-fold Qwen3-Embedding expert, a Qwen3.8-27B GSQ expert, and Sinkhorn. Metadata lists 17 datasets, 8 upstream notebooks, and 8 model sources.
- The author reports several negative or weak tests: a five-backbone stack with nested CV `.6865` scored `.559–.560` on Public LB; Hungarian assignment scored `.524`; adding members moved the score at most `.004`; and repeated `.684`/`.680` submissions illustrate LB noise. These are author-reported results for their configurations, not results reproduced here.
- The author also summarizes Discussion 753177: for one related blend family, an OOF simulation with two answers per prompt correlated better with public LB than all-18-prompt OOF, but the author cautions that this is a weak signal affected by an outlier and selection of five later configurations from a 162-setting grid. It is not a verified statement about the hidden test's actual group-size distribution.

## Limits

This is not an isolated candidate with foldwise OOF probabilities or a small transplantable component. The `.684` stack has substantial dependency/provenance scope and does not exceed the current leader. No source was executed locally; no dataset, weight, or prediction asset was downloaded; no Kaggle push/submission was made. The discussion-derived prompt-shape hypothesis was tested separately without adopting the Notebook ensemble.
