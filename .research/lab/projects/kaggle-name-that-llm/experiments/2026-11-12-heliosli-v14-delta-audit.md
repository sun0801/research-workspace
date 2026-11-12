---
date: 2026-11-12
project: kaggle-name-that-llm
type: public-source-audit
status: rejected
tags: [public-notebook, qwen-embedding, sinkhorn, ensemble]
---

# Heliosli Qwen3 embedding ensemble v14 delta audit

## Decision

**(b) 試さない。** Version 14's title claims `.683`; its source says the single change from v13 is `sinkhorn_target_mix` `.35` → `.50`. The version-13 parent is described as an unchanged copy of the public `.684` ensemble. Neither the v14 claim nor its available session evidence exceeds the current official leader `.768` or provides prompt-grouped OOF evidence. It is another parameter variant of an already audited multi-source embedding/LoRA stack, so it is not added to our experiment queue.

## Source and evidence

- [Kaggle Notebook](https://www.kaggle.com/code/heliosli/name-that-llm-lv683-a15), `heliosli/name-that-llm-lv683-a15`, public version 14, GPU enabled, Internet disabled.
- Search listed a Nov 12 run; current Notebook metadata reports last run Nov 9. Version 14 session status is `COMPLETE`; available output shows mounted inference-stage files but no competition score or OOF metric.
- Notebook markdown says v13 is a copy of lbjyang's `.684` mirror and that v14 changes only the Sinkhorn target mix from `.35` to `.50`. The `.683` value is the title/source claim, not an independently verified measurement here.
- Metadata lists 18 dataset inputs, 8 upstream Notebook inputs, and 8 model inputs. The source describes substantial overlap with already audited Clean LoRA + Qwen3 Embedding / GSQ ensemble lineage.
- A Nov 9 audit covered the older `lv681-a15` version 5 and found no verifiable execution result. This note records the current version 14 delta; it does not treat a current search timestamp as a verified run timestamp.

No source code was run locally, no data or weights were downloaded, and no Kaggle push or submission was made.
