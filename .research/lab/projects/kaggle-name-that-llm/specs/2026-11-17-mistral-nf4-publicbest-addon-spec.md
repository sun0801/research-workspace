---
date: 2026-11-17
project: kaggle-name-that-llm
status: approved-under-user-directive
authorization_date: 2026-11-17
tags: [spec, kaggle, mistral, nf4, private-notebook, public-lb]
---

# Mistral NF4 add-on to the Public `.626` baseline

## Authorization and candidate value

The user explicitly requested preparing a T4-compatible lightweight Mistral candidate and LB add-ons on 2026-11-17. The prior unquantized v14 runtime stopped at the per-GPU VRAM-reserve gate; this spec defines the new quantized inference comparison required by the 2026-11-15 Mistral runtime spec. It reuses already trained, independently confirmed Mistral components; no new model training is included.

Priority is high: the five-fold Mistral + frozen Spectral composition passed independent confirmation (BA `.676823`, delta `+.022995`, paired prompt-bootstrap lower bound `+.011596`, both retention simulations 20/20 positive). Its unquantized Kaggle path failed only the 10% per-GPU reserve gate before full inference. The current LB baseline is Public `.626` (ref `58456880`). This candidate tests whether NF4 inference allows the existing Mistral signal to add value to that stronger baseline.

## Fixed candidate

- Start from the private `.626` OLMo add-on source that produced ref `58456880`; preserve its model weights, OLMo weight `.25`, classes, offline data/model inputs, and final hidden-run Sinkhorn path.
- Use the five existing **primary** Mistral fold adapters and matching classifier/norm heads. Do not use confirmation-fold models, alter training artifacts, or retrain.
- Load pinned `mistral-ai/mistral/pytorch/7b-v0.1-hf/1` in NF4 4-bit with double quantization and FP16 compute on Kaggle T4. Attach the existing private offline bitsandbytes wheel and Mistral asset bundle. Keep Kaggle Notebook private and Internet disabled.
- Average the five fold row-wise softmax probabilities. At the existing `.626` baseline score boundary, form `P_candidate = 0.75 * P_626 + 0.25 * P_mistral`; then run the baseline's unchanged full-hidden-test Sinkhorn step once. No weight or post-processing tuning.

## Files and scope

- Add builder `scripts/build_mistral_nf4_publicbest_notebook.py` and a new local-only Notebook directory `notebooks/name-that-llm-private-publicbest-mistral-nf4/` in the Kaggle implementation repository.
- Preserve the existing v14 builder, source, and runtime logs. The new builder derives from the `.626` OLMo source and inserts NF4 Mistral inference, pilot/projection, and the fixed probability blend.
- Use only existing private dataset/model assets. Do not create public Kaggle artifacts or change trained weights, fold assignment, class order, the `.626` base branch, or the OLMo component.

## Resource and runtime gates

- Rate guard `--guard 15` before long work and major checkpoints. Kaggle weekly GPU quota must be checked with the user's authorized `kaggle quota` command.
- Host142 is inspected locally, never via SSH. Its GPU1 Mistral reservation is released; inspect processes, GPU UUID/memory, and `/proc/meminfo` before any local use. Do not touch the unrelated `view_bench` tmux session observed on GPU0.
- If using Host141, run `ssh 141` immediately before launch. Require the selected 16-GB GPU to have no other compute process, verify UUID and memory, and require host `MemAvailable >= 16 GiB`. Pilot peak plus planned allocation must fit after reserving `max(4 GiB, 25% of total VRAM)`; retain at least 2 GiB additional post-pilot free VRAM. Do not displace other work.
- First run a bounded 64-row, five-fold inference pilot using official training text only for timing and numeric checks. Require finite normalized fold probabilities, no OOM, and measured per-GPU peak/runtime.
- On Kaggle T4×2, require at least 10% free VRAM on each GPU at peak, all offline inputs to resolve, a passing 64-row pilot, and 1.25× extrapolation for 4,000 hidden rows below 8 hours (internal limit; official ceiling is 9 hours). If any gate fails, do not submit or alter blend weights.
- The public 3-row fixture is format-only and does not prove model inference. Validate `submission.parquet` schema and labels; use the competition hidden rerun to measure full inference runtime and public score.

## Evaluation and submission

- Existing prompt-grouped primary and independent confirmation results establish the Mistral candidate; no additional fitting or CV tuning is permitted in this comparison.
- Once resource/runtime gates pass and a daily slot is available, report the measured runtime, memory, source, and remaining submissions before submitting this single private candidate.
- Compare its Public LB to `.626`; use `.005` as the noise threshold. The current `.776` leader is context, not a reason to skip this comparison. Record Private LB separately.
- If the T4 gate fails, keep the failure diagnosis and stop this quantized path. Choose the next candidate from measured results and public evidence.
