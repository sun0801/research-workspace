---
date: 2026-11-12
project: kaggle-name-that-llm
type: public-source-audit
status: rejected
tags: [public-notebook, clean-lora, qwen-embedding, ensemble]
---

# Evgen Dvorkin forensic EDA / inference Notebook v28 audit

## Decision

**(b) 試さない。** Current version 28 is a credited reproduction of the public Clean LoRA + Qwen3-Embedding ensemble lineage, whose documented result is `.684`; this does not approach the current official public leader `.768`. The version adds no verified OOF or score above that public result. It is a large multi-source stack and overlaps the already audited `.684`/embedding/LoRA candidates, so it does not justify importing dependencies or changing the current registered queue.

## Source and inspection

- [Kaggle Notebook](https://www.kaggle.com/code/evgendvorkin/name-that-llm-deep-forensic-eda-with-analogie), `evgendvorkin/name-that-llm-deep-forensic-eda-with-analogie`, current version 28, public, GPU enabled, Internet disabled. Current metadata lists 17 datasets, 8 upstream notebooks, and 8 model sources.
- ScoreDescending search listed the Notebook on 2026-11-12. Notebook metadata says `last_run_time` 2026-11-09 11:11 UTC. The v28 session is `COMPLETE`; its available session output contains inference-stage source files, while the embedded forensic evaluation log reports random-split fold BA `.1700/.1422/.1356` and prompt-grouped fold BA `.2633/.2933/.2713`. These are the small forensic classifier results, not the large ensemble's competition score.
- Static source inspection describes the inference branch as reproducing a public `.684` Clean LoRA + Qwen3-Embedding implementation, with native embedding 40%, GSQ 3%, complementary component 15%, and Sinkhorn adjustment. The version trail also lists prior `.668`–`.683` public scores. The current v28 score itself is not verified by the inspected session evidence.
- A Nov 6 note covered version 21; this is a version update, not an independent reproduction. Version 28's expanded dependency list and credited `.684` lineage were checked directly this turn.

## Limits and overlap

The Notebook is a multi-source inference stack, not an isolated new learner with prompt-grouped OOF evidence. Its forensic visualization is descriptive and does not establish that the reproduced inference stack improves our registered split. No source code was executed locally, no weights or datasets were fetched, and no Kaggle push/submission was made.

Related prior records: [public `.684` source audit](2026-11-12-public-0684-notebook-audit.md), [RanJeet WEMM Notebook audit](2026-11-12-ranjeet-nov12-wemm-notebook-audit.md), and [WEMM component audit](2026-11-12-wemm4-expanded-lora-component-audit.md).
