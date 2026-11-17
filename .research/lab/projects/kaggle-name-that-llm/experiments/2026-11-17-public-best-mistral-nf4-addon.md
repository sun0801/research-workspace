---
date: 2026-11-17
project: kaggle-name-that-llm
type: experiment-log
spec: ../specs/2026-11-17-mistral-nf4-publicbest-addon-spec.md
status: runtime-gate-passed-awaiting-public-baseline
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
- 22:02 JST resource refresh: Kaggle GPU quota was 27.66h/30h remaining (same refresh). No local GPU process was started.
- 22:11 JST: private v1 reached `ERROR` after about 12m30s. Baseline and OLMo computations completed, including OLMo's five-fold probe. Mistral inference stopped in `load_mistral_fold(0)` at the exact class-order equality check, before loading Mistral weights. No Mistral probabilities, VRAM/runtime projection, `submission.parquet`, or competition submission were produced; this was not an OOM or a failed T4 memory gate.
- Fix: each primary-fold head's labels must be a unique permutation of baseline `LABELS`. The builder now validates the set and reorders each fold probability matrix into baseline column order before averaging/blending. No model weights, fold membership, blend weight, or evaluation were changed. All Notebook code cells passed static syntax parsing; metadata remains private, GPU enabled, Internet disabled, T4.
- 22:12 JST v2 pre-push gate: official metadata reported 6,190 teams and the same Jan 14 UTC deadline; Timeline remains Jan 13 UTC; Code Requirements remain Notebook-only, Internet off, ≤9h. Daily submissions were 5/5 used; GPU quota 27.66h/30h. This was a runtime rerun, not a competition submission.
- 22:14 JST: private kernel version 2 pushed to the same slug. MCP's first status response was empty; the authenticated CLI status then confirmed `KernelWorkerStatus.QUEUED`. Await the next scheduled poll before inspecting output. Do not restart v2 based on the earlier empty response.

## Decision and resume point

Priority remains (1) NF4 Mistral because independent five-fold confirmation gave BA `.676823`, delta `+.022995`, and bootstrap lower bound `+.011596`; (2) existing Qwen3-8B-on-`.626` blend as a secondary LB check, since its earlier `.623` result was only `+.003` over the `.620` baseline and below the `.005` noise threshold. Do not spend a submission on Qwen3-8B unless the Mistral gate/result warrants it or a slot is otherwise available under the daily-use policy.

Resume with the next scheduled Kaggle session poll. If the pilot passes, record measured per-GPU reserved memory, fold timing, projected hidden runtime, and preview artifact checks before asking the user for the required pre-submission report. Do not submit before that report.

## 2026-11-17 23:44 JST — private v2 started

- The scheduled 30-minute session poll returned `RUNNING` for `suntree0801/name-that-llm-private-publicbest-mistral-nf4` (v2), changing from the prior authenticated CLI `QUEUED` state at 22:44 JST. No restart or duplicate push was made. Runtime gates, artifact checks, and submission remain pending.
- Codex rate guard passed at 23:44 JST: 5-hour remaining 87%, weekly remaining 64%.

## 2026-11-18 00:14 JST — NF4 runtime and preview gates passed

- The scheduled session poll returned `COMPLETE`. Session log reports `done in 1024s`; the output bundle conversion finished by 1063s. This is the 3-row preview session, not a measured hidden run.
- The 64-row, five-fold T4 pilot took 251.4s total. Per-fold peak reserved memory was 2,064 MiB on GPU0 and 2,434 MiB on GPU1 (both T4, 14,911 MiB each); the 10% reserve gate passed. The fixed `.626` + Mistral probability blend was `0.75 * P_626 + 0.25 * P_Mistral`.
- For 4,000 rows the projected hidden Mistral inference was 5,721.7s; total projection with the 1.25× margin was 2.995 hours, below the internal 8-hour limit. The runtime gate passed. This is a pilot projection; the scoring run is still needed for actual hidden runtime and Public LB.
- Downloaded `mistral-nf4-runtime.json` and `submission.parquet`. The preview artifact has 3 rows, columns `id, model`, exact local `test.csv` ID order, no nulls or duplicate IDs, and all predictions in the 18-label training domain. Predictions: `claude-opus-4-8`, `gpt-5.6-sol`, `gemini-3.1-pro-preview`.
- No competition submission was made. Under the 2026-11-16 policy, first submit the license-audited `.684` public Notebook baseline; then add this passing NF4 Mistral branch to that new baseline for its LB check. At the latest CLI read, the five newest submissions were all dated 2026-11-17 UTC, so the UTC-day allowance had not reset at 00:14 JST. Report before the `.684` submission.
- Current quota at 00:00 JST: 27.36 GPU hours remaining of 30; refresh `2026-11-21 09:00 JST`.
