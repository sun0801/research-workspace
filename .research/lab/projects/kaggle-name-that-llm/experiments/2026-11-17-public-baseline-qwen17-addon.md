---
date: 2026-11-17
project: kaggle-name-that-llm
type: experiment-log
status: preview-runtime-complete
---

# Qwen17 add-on to the Public `.620` blend: private preview runtime

## Candidate and result

- The Notebook source identifies the parent as the Public `.620` blend and adds Qwen3-8B, five-fold OLMo2-7B, and Qwen3-1.7B with fixed log-probability weight `.25` each. Its primary OOF screen reports BA `.596428` for Qwen8+OLMo and `.594937` after adding Qwen17 (delta `−.001491`, prompt-bootstrap 95% CI `[−.009310,+.006296]`). This is not clear OOF degradation; Public LB remains the decision.
- Private kernel `suntree0801/name-that-llm-qwen-olmo-qwen17-addon` v3 was `COMPLETE` when checked at 22:20 JST. The session output contains `submission.parquet`; no competition submission or Public LB result was produced.
- Kaggle session elapsed about 831 seconds. The preview input had 2,699 training rows, 3 test rows, and 2 GPUs. The model pipeline completed in 789 seconds before notebook conversion/output packaging.
- Qwen3-8B: 64-row pilot completed in 15.3s; projected hidden inference was 1,994.6s, with GPU0 peak reserved memory 7,236 MiB.
- Qwen3-1.7B: 64-row pilot completed in 2.7s; projected hidden inference was 2,202.1s, with GPU0 peak reserved memory 4,238 MiB.
- OLMo2-7B: five fold probes completed; peak reserved memory was 6,450 MiB. For the 3-row preview, the notebook projected 10,253.8s for 4,000 hidden rows, below its 28,800s internal gate. Adapter loading took 125.1s. This is a runtime projection from the notebook's pilot, not a measured full hidden run.
- This runtime supports the internal runtime/memory gate for the candidate pipeline. The downloaded preview `submission.parquet` has 3 rows and columns `id, model`, with no nulls or duplicate IDs. The three preview IDs and order match official `test.csv`; all predicted classes are within the 18-class `train.csv` domain. This preview is not the full hidden-scoring artifact, and improvement over `.626` on Public LB remains unverified.

## Next decision

Keep the candidate pending one Public LB comparison against current best ref `58456880`. The runtime candidate is authored as `.620` + Qwen8/OLMo/Qwen17 fixed additions; the `.626` comparison ref is the current OLMo-enhanced best. At the time of recovery, today's five competition submissions were already used, so no submission was made. Report the candidate and its preview-only runtime basis before submitting when a slot is available. No new model training was performed in this run.
