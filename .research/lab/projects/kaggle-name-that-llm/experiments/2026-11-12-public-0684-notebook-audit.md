---
date: 2026-11-12
project: kaggle-name-that-llm
type: public-notebook-audit
---

# (b) 試さない — Areeb Ali 0.684 Notebook mirror

- Source: [Areeb Ali, `0.684 | I'M BETTER !`](https://www.kaggle.com/code/areebbb/0-684-i-m-better), current version 11, public. Kaggle MCP source inspection read its opening/score description and relevant code sections; no code was executed and no full dependency/data audit was performed.
- The notebook says this version reproduces the public `lbjyang/ntl-684-ozertuu-mirror` with code cells unchanged. Its table attributes public LB `.684` to that mirror; treat this as the author's attribution, not a verified score for this exact version. Notebook-info `last_run_time` was Nov 8 while search listing showed Nov 11, so the displayed timestamps disagree.
- The reported `.684` is above our confirmation BA`.653828` but below the current public leader`.768`; the multi-model stack includes ATLAS LoRA, Qwen3 embeddings, and GSQ-27B. The score alone does not establish a prompt-grouped gain or a route to first place.
- The initial hold condition is now resolved: baseline v12 scored Public`.541` against primary OOF BA`.586408`. Reconsidering the mirror still leaves its exact scored version unverified and no isolated component with prompt-grouped evidence to reproduce. Close as **(b) 試さない**; no trial or implementation started.

## 17:18–17:22 JST — related dual-embedding Notebook audit

- Inspected [Krish Shah, `Dual Embedding LoRA Ensemble v16`](https://www.kaggle.com/code/krshs90/dual-embedding-lora-ensemble-v16): public v1, GPU enabled, internet disabled. Kaggle search indexed a Nov 12 run, while `get_notebook_info` reported Nov 9. Its source describes a six-backbone stack, two embedding heads, a GSQ-27B boundary head, semantic prompt clustering, and Sinkhorn balancing; metadata lists 17 dataset, 8 Notebook, and 9 model sources. No isolated prompt-grouped score or reproducible component gain is provided in the inspected source.
- **Decision: (b) 試さない.** The source is a large, multi-asset stack with unresolved run-time metadata and no separable validation evidence; spending a GPU confirmation run on it is not justified against the current`.768` leader and the stronger local Mistral primary screen. No Notebook or submission was created.
