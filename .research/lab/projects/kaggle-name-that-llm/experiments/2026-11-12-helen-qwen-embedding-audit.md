---
date: 2026-11-12
project: kaggle-name-that-llm
type: public-notebook-audit
decision: (b) 試さない
tags: [audit, notebook, embeddings, qwen3]
---

# (b) 試さない — Qwen3-Embedding-8B public blend

- Source: [helen0/NTL V25 MBDoc SVC4](https://www.kaggle.com/code/helen0/ntl-v25-mbdoc-svc4), public version 2. `get_notebook_info` showed a Nov 9 last-run time while the search listing showed Nov 12 06:30 UTC. Read the overview and architecture markdown and inspected dependency metadata; did not execute code or audit all assets.
- The author describes five prompt-fold Qwen3-Embedding-8B heads using all 36 layers, 50% probability mass, plus a large multi-model stack. The text claims a one-parameter comparison changing the native expert from 40% to 50% against a `.680` reference. This is a notebook claim, not an independently verified score or standalone embedding OOF result.
- The official Kaggle model variation is `qwen-lm/qwen-3-embedding/transformers/8b`, version 1, fine-tunable; listed model shards total about 15.1 GB. The [official Qwen3-Embedding-8B model card](https://huggingface.co/Qwen/Qwen3-Embedding-8B) identifies Apache-2.0. The official Kaggle description documents last-token pooling and normalized embeddings.
- **Decision: (b) 試さない as a separate candidate.** The repo already has an approved Qwen3-Embedding-8B multi-depth LoRA OOF spec, with primary and independent confirmation gates, and the existing candidate is explicitly pinned to Host142 GPU1. This Notebook does not provide standalone fold logits that justify a second, frozen-linear-head branch or changing that queue. Keep this public score claim as context for the existing candidate; do not duplicate it on Host141.
- Existing candidate: [Qwen3-Embedding-8B multi-depth LoRA spec](../specs/2026-11-08-qwen3-embedding-8b-multidepth-prompt-grouped-spec.md). Wait for its registered Host142 queue and strict host-key gates; do not move it.
