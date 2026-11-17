---
date: 2026-11-17
project: kaggle-name-that-llm
type: experiment-log
spec: ../specs/2026-11-17-mistral-nf4-publicbest-addon-spec.md
status: private-runtime-running
---

# NF4 Mistral add-on to Public `.626`

## Candidate and implementation

The candidate starts from private baseline ref `58456880` (Public `.626`) and uses the five existing primary Mistral folds. It computes `0.75 * P_626 + 0.25 * P_Mistral`, followed by the unchanged baseline Sinkhorn. The prior unquantized v14 path remains rejected at its VRAM reserve gate; this is the separately authorized NF4 comparison. No model was trained or weights changed.

- Builder: `/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/scripts/build_mistral_nf4_publicbest_notebook.py`
- Candidate directory: `/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/notebooks/name-that-llm-private-publicbest-mistral-nf4/`
- Uses NF4 double quantization, FP16 compute, a 64-row pilot from official `train.csv`, per-GPU 10% VRAM reserve, and 1.25× projection for at least 4,000 hidden rows. It stops before test inference if the internal 8-hour projection gate fails.

## Preflight and runtime

- 2026-11-17 21:40 JST: Official Kaggle Rules/Code Requirements rechecked. Notebook submissions must run offline within 9 hours; up to five submissions/day. The competition's example session uses three rows; hidden scoring reruns on about 4,000 rows. The selected Mistral model is already attached by the private metadata.
- Authenticated CLI showed today's five competition submissions already used. GPU quota was 28.03h/30h (refresh `2026-11-21 09:00 JST`). This candidate was **not** submitted to the competition.
- Notebook JSON and every code cell passed local syntax parsing. Metadata is private, GPU enabled, Internet disabled, and `NvidiaTeslaT4`; the fixed blend feeds the original final Sinkhorn cell.
- Private Kaggle kernel version 1 was pushed at 21:41 JST as `suntree0801/name-that-llm-private-publicbest-mistral-nf4`. Immediate session status: `RUNNING`. This is a preview runtime only; the T4 memory/runtime gates, submission artifact, and Public LB result remain pending.
- 21:50 JST resource refresh: Kaggle GPU quota was 27.80h/30h remaining (refresh `2026-11-21 09:00 JST`). Host141 GPUs 0–2 and Host142 GPU1 showed no compute load; no local job was started. Host142 GPU0 retains its unrelated `view` tmux session and was left untouched.

## Decision and resume point

Priority remains (1) NF4 Mistral because independent five-fold confirmation gave BA `.676823`, delta `+.022995`, and bootstrap lower bound `+.011596`; (2) existing Qwen3-8B-on-`.626` blend as a secondary LB check, since its earlier `.623` result was only `+.003` over the `.620` baseline and below the `.005` noise threshold. Do not spend a submission on Qwen3-8B unless the Mistral gate/result warrants it or a slot is otherwise available under the daily-use policy.

Resume with the next scheduled Kaggle session poll. If the pilot passes, record measured per-GPU reserved memory, fold timing, projected hidden runtime, and preview artifact checks before asking the user for the required pre-submission report. Do not submit before that report.
