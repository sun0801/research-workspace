---
project: kaggle-name-that-llm
date: 2026-11-08
status: primary-running
spec: ../specs/2026-11-08-qwen3-4b-base-openpool-v15-host141-spec.md
tags: [experiment, gpu, qwen, kaggle]
---

# Qwen3-4B-Base + Open Pool v15

## Candidate and source

Candidate11 tests whether the official Qwen3-4B-Base pretraining checkpoint gives useful prompt-held-out classification or complementary OOF errors between the existing 1.7B and 8B candidates. This is a hypothesis; no contest result or Kaggle notebook use is claimed. Kaggle MCP metadata for [Qwen3-4B-Base version 1](https://www.kaggle.com/models/qwen-lm/qwen-3/Transformers/4b-base) reports 4.0B parameters, 36 layers, Q32/KV8, fine-tunable, Apache 2.0, and 8,056,508,540 uncompressed bytes. Files were downloaded with KaggleHub 1.0.3 to the ignored model cache. Ten of eleven files match the official file-size list; only auxiliary `vocab.json` (2,776,833 bytes) was unavailable due to KaggleHub HTTP 1994, including one isolated retry. The remaining model/tokenizer files are exact-size matches, and `AutoTokenizer.from_pretrained(..., local_files_only=True)` succeeds as `Qwen2TokenizerFast` (151,669 tokens, pad 151,643, eos 151,645). Kaggle download completeness is recorded as partial; the missing file is not assumed present.

## Fixed protocol and implementation

- Approved parent goal: [GPU autonomous first-place spec](../specs/2026-11-06-gpu-autonomous-first-place-spec.md); candidate spec: [Host141 candidate11 spec](../specs/2026-11-08-qwen3-4b-base-openpool-v15-host141-spec.md).
- Implementation root: `/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/`. Dedicated config: `configs/gpu11-qwen3-4b-base-openpool-v15.json` (SHA-256 `bae7bcd5cd5cd52b855c9b87eef31d53f13c2e9854cc368f4d718591aaf6a42a`). Existing generic runner was not edited; SHA-256 `3bd614d95d8cdda0b521d98f940a5c127ded2981f1399bd64e1f3f3222c63aca` on Host141 and Host142.
- Host141 has an independent local repo/data/cache. Runner, config, train/folds, Open Pool v15, and reconstructed prompts were hash-compared. Host141 training environment imports Torch 2.9.0+cu128, Transformers 4.57.1, PEFT 0.17.1, Accelerate 1.10.1, sklearn 1.9.1. Host141 `train.csv` SHA-256 `40a22ce8d88c5f46feb4637a099db815bef5f713ffe53e89dbe1b7b21de77707`.
- Fixed settings: same saved `GroupKFold(prompt_id)` primary folds, v15 prompt-leakage and exact-text filtering, row cap 2,500/class, seed 42, max length 384, BF16, microbatch 1, LoRA rank 16 / alpha 32 / dropout .05 / layers 0–19, pooled layers `[2,4,6,8,12,16,20,24]`. No class weights or `match_weight` in OOF.
- Execution host/GPU: `141-X9DAi`, GPU2 `GPU-48a73ba5-62ab-e9ff-b15b-e4eceae66c58` (RTX A4000, 16,376 MiB). No same-GPU co-location. The Qwen04 and Qwen8B confirmation jobs on Host142 continue unchanged.

## Pilot

At 2026-11-08 19:30 JST the 15% quota guard passed (5h 93%, weekly 73%). Host141 GPU2 was idle in two snapshots 10s apart (15,960 MiB free; no compute PID) and host MemAvailable was ~121 GiB. Runner double-preflight also passed with exact UUID, 15,958 MiB minimum free, 121.1 GiB minimum MemAvailable, no compute processes, cgroup hard limit unavailable. Model load, forward, backward and optimizer step passed; LoRA layer IDs were 0–19 of 36. Optimizer step took 2.083 s; peak reserved VRAM 8,298 MiB, allowed limit after 4,096 MiB reserve 11,696 MiB; `pass_reserve=true`; pilot loss 2.734375. Host141 pilot runner/config hashes are recorded in `artifacts/gpu11-qwen3-4b-base-openpool-v15/pilot.json`.

## Primary run and resume point

Primary 5-fold run started on Host141 at 2026-11-08 19:32 JST after another guard pass (5h 93%, weekly 73%) and two clear GPU2 snapshots. Wrapper/lock PID `2439029`, Python PID `2439031`; log: `artifacts/gpu11-qwen3-4b-base-openpool-v15/primary.log`; saved PID: `artifacts/gpu11-qwen3-4b-base-openpool-v15/primary.pid`; lock: `artifacts/.gpu2-run.lock`. Startup log confirms preflight passed, creator flags removed (0 rows), 2,699 official train rows, 212,623 external pool rows, 18 labels, five folds. Initial GPU sample immediately after launch showed runner attached to GPU2; process CPU-active. No fold checkpoint/OOF was present at the initial startup check.

At 19:34 JST, runner remained CPU-active on GPU2 (8,545 MiB used / 7,430 MiB free, 41% utilization; host MemAvailable `122,620,240 kB`). Fold0 setup confirmed 540 validation rows across 30 prompts; two near-matching pool prompt groups removed, 31 external rows filtered, then 45,000 rows sampled uniformly at 2,500/class. LoRA layer IDs 0–19/36 were verified. No fold checkpoint/OOF yet.

At 19:37 JST, PID `2439031` remained CPU-active, GPU2 showed 8,545 MiB used / 7,430 MiB free at 41%, and MemAvailable was `122,681,928 kB`. No checkpoint/OOF had appeared after fold0/stage1 initialization. Host142 Qwen04/Qwen8B PIDs remained active; no newer Qwen04 confirmation artifact than fold0 OOF/logits at 16:43:17.

At 19:42 JST, the same runner PIDs remained alive; GPU2 was at 8,545 MiB used / 7,430 MiB free and 40%, MemAvailable `122,759,476 kB`. The run directory still contains only `pilot.json`, `pilot.log`, `primary.pid`, and `primary.log`, with no epoch checkpoint/OOF. This is a verified wait, not a failure; preserve fold0/stage1 rather than restart.

Runner writes resumable checkpoints at completed-epoch boundaries. SIGTERM is handled at the next batch boundary, but the current incomplete epoch is not saved and will repeat on resume. At the 19:34 check, fold0/stage1 had not completed an epoch, so no checkpoint existed yet; the exact recoverable position was fold0/stage1 epoch1 from its beginning, with the in-progress work unsaved. There is no separate watcher/autoinjector targeting Host141 for this run.

Run/restart command (only after checking current PID, GPU UUID, host memory, quota guard, and whether a newer checkpoint exists):

```bash
cd /mnt/HDD10TB-2/aburatani/kaggle/name-that-llm
flock -n artifacts/.gpu2-run.lock env CUDA_VISIBLE_DEVICES=GPU-48a73ba5-62ab-e9ff-b15b-e4eceae66c58 \
  .venv/bin/python -u src/gpu_experiment.py \
  --config configs/gpu11-qwen3-4b-base-openpool-v15.json \
  --model-path artifacts/model-cache/qwen3-4b-base-v1 \
  --run-dir artifacts/gpu11-qwen3-4b-base-openpool-v15 --resume
```

No Kaggle object, Notebook, or submission was created. Candidate adoption and any confirmation remain pending primary OOF and paired-bootstrap analysis.

### 2026-11-09 13:51 JST fold1 Stage1 checkpoint

Host141 PID `2439031` completed primary fold1 Stage1 epoch-001 and saved `artifacts/gpu11-qwen3-4b-base-openpool-v15/primary/fold-1/stage1/epoch-001/state.pt` at 13:41:50 JST. The epoch processed 45,000 external examples; mean loss `1.616284`, peak allocated VRAM `8,213 MiB`, MemAvailable `104.50 GiB`. At 13:51:22 the process remained active on GPU2; GPU2 use/free `8,549/7,426 MiB`, MemAvailable `109872248 kB`. Fold1 OOF is pending. Resume from this saved Stage1 checkpoint through the existing live runner; preserve it and do not restart.

### 2026-11-09 14:08 JST fold1 Stage2 checkpoint

PID `2439031` saved primary fold1 Stage2 epoch-001 at 14:06:22 JST to `artifacts/gpu11-qwen3-4b-base-openpool-v15/primary/fold-1/stage2/epoch-001/state.pt`; mean loss `1.335897`, 2,159 official rows, peak allocated VRAM `8,213 MiB`. Fold1 OOF is still pending. At 14:08:31 the runner remained live on GPU2 (`8,549/7,426 MiB` used/free), with Host141 MemAvailable `109476816 kB`. Preserve the checkpoint and let the existing runner continue through Stage2 epoch-002 and OOF.

### 2026-11-09 14:40 JST fold1 OOF verified

Host141 PID `2439031` saved primary fold1 OOF at 14:32:30. Read-only integrity validation against official `data/train.csv` passed: 540 unique IDs, 30 prompts, 18 classes, no nulls, exact ID/prompt/label alignment, and identical ID/prompt/fold assignments to candidate12's fold1. Balanced accuracy is `0.511111`. This is one of five folds and is not an adoption result. At 14:40:03 the runner remained active on GPU2 (`8,549/7,426 MiB` used/free, 39% utilization); Host141 MemAvailable was `109170468 kB`. Continue the existing runner without restart.

### 2026-11-09 16:26 JST partial paired comparison

Candidate11 primary folds0–1 were aligned to the adopted SVC OOF at `artifacts/cpu-openpool-prompt-centered-low-pool-weight-v15/primary/oof-all.parquet`. The shared 1,080 rows (60 prompts, 18 classes) match exactly on ID, prompt, label, and fold. Candidate BA is `.526852` vs SVC `.483333` (delta `+.043519`); fold deltas are `+.057407` and `+.029630`. The registered `gpu_analyze.paired_prompt_bootstrap` with 2,000 prompt resamples, seed 42, gives 95% CI `[+.010185,+.075023]` and mean delta `+.043026`. This is only 2/5 folds and is descriptive; keep the full five-fold gate pending. The 16:22 poll still showed PID `2439031` active and all five GPUs assigned; no process, queue, Kaggle object, or submission changed.

### 2026-11-09 05:15 JST live progress

Host141 PID `2439031` remains live on GPU2 UUID `GPU-48a73ba5-62ab-e9ff-b15b-e4eceae66c58` (8,549 MiB used / 7,426 MiB free, 44% utilization). At 05:10:02 JST primary fold0 completed and saved OOF/logits: balanced accuracy `0.5425925926`, peak allocated VRAM `8,209 MiB`. Fold1 setup began at 05:10:14 with 2,159 official training rows, 540 validation rows / 30 prompts, 2 prompt groups excluded, and 45,000 Open Pool rows; the runner remains active. This is one of five folds, not the adoption metric. Latest durable point includes fold0 Stage2 epoch-002 and OOF. Keep the current process; no restart, candidate decision, Kaggle object, Notebook, or submission.

At 20:40:57 JST, Host141 runner PID `2439031` and wrapper `2439029` remained live (elapsed 1:08:34, CPU time 1:10:07). GPU2 UUID `GPU-48a73ba5-62ab-e9ff-b15b-e4eceae66c58` used 8,545 MiB / free 7,430 MiB / 49%; host MemAvailable was `111,441,924 kB`. `primary.log` and run files remain at the fold0 setup from 19:33:01; no checkpoint/OOF exists. The process CPU time advanced during the 10-minute poll interval, so retain the in-progress first stage epoch; current work is unsaved and resume begins from the latest completed epoch (none yet). Do not restart due to the missing epoch event alone.

### 2026-11-09 20:49 JST fold2 active, no new checkpoint

Host141 PID `2439031` and its lock wrapper remain alive on GPU2; GPU2 use/free is `8,549/7,426 MiB`, utilization 48%, and host MemAvailable is `113677348 kB`. The latest saved candidate11 artifacts remain fold0 and fold1; `primary.log` still records fold2 setup at 14:32:32, with no fold2 checkpoint/OOF. This is an in-progress, unsaved Stage1 epoch; keep the live runner and do not restart. If later stopped, resume from the latest durable fold1 OOF/checkpoint and rerun fold2 Stage1 from its start.
### 2026-11-08 21:00 JST status

Host141 (`141-X9DAi`) runner PID `2439031` remains live and CPU-active (elapsed `1:28:27`, CPU `1:30:00`) on GPU2 UUID `GPU-48a73ba5-62ab-e9ff-b15b-e4eceae66c58`. Host GPU2 has `8545 MiB` used / `7430 MiB` free; host MemAvailable is `113625309184` bytes. No checkpoint or OOF has been saved; resume from the latest completed epoch (none), preserving the in-progress fold0 epoch. User requested continuation, not a stop. Do not restart.
### 2026-11-08 21:21 JST status

Host141 (`141-X9DAi`) runner PID `2439031` remains live and CPU-active (elapsed `1:49:11`, CPU `1:50:44`) on GPU2 UUID `GPU-48a73ba5-62ab-e9ff-b15b-e4eceae66c58`. GPU2 has `8545 MiB` used / `7430 MiB` free; host MemAvailable is `112464785408` bytes. No checkpoint or OOF was written in the last 15 minutes; preserve the in-progress fold0 epoch and resume from the latest completed epoch (none). User's instruction is to continue; do not restart.
