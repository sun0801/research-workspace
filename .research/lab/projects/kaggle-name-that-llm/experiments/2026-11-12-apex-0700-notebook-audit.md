---
date: 2026-11-12
project: kaggle-name-that-llm
type: public-notebook-audit
decision: (b) 試さない
tags: [audit, notebook, provenance]
---

# (b) 試さない — `ntl-v30-apex-0700`

- Source: [ruixidai/ntl-v30-apex-0700](https://www.kaggle.com/code/ruixidai/ntl-v30-apex-0700). Public version 1, one vote; source overview inspected, not executed. Search indexed a Nov 12 run, but Notebook Info reported Nov 9. Metadata lists 17 datasets, 8 Notebook sources and 8 model sources.
- Despite `.700` in the slug, the opening identifies itself as “NTL-29 | 0.684 Reproduced” and describes the same large ATLAS/Qwen-Embedding/GSQ stack family. No inspected artifact substantiates a `.700` score for this version; no prompt-grouped OOF gain is isolated.
- **Decision: (b) 試さない.** The title claim is unsupported by the inspected source, the stack is not separable, and the reported `.684` family remains below the current `.768` leader. No implementation or Kaggle action.
