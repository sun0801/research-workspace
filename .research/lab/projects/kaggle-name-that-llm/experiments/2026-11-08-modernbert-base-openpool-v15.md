---
project: kaggle-name-that-llm
date: 2026-11-08
status: primary-running
spec: ../specs/2026-11-08-modernbert-base-openpool-v15-host141-spec.md
tags: [experiment, gpu, modernbert, kaggle]
---

# ModernBERT-Base + Open Pool v15

## Candidate and source

Candidate12 evaluates ModernBERT-Base with Open Pool v15 pretraining and foldwise official-train LoRA. Kaggle Discussion [754860, comment 3551013](https://www.kaggle.com/competitions/name-that-llm/discussion/754860) reports CV `.616` and public LB `.575` after Open Pool pretraining, but the author does not specify the pool version, split, or leakage controls. Treat both scores as self-reported and unverified.

Kaggle's [Answer.AI ModernBERT-Base model](https://www.kaggle.com/models/answer-ai/modernbert/PyTorch/base), version 2, is Apache 2.0 and fine-tunable. The official file listing contains 7 files; all 7 were downloaded with Kaggle CLI via the existing non-displayed `.env` configuration and match their official sizes (total 600,829,754 bytes). The cache is `artifacts/model-cache/modernbert-base-kaggle-v2/` and is excluded from Git. Architecture config identifies `modernbert`, 768 hidden size, 22 layers, and `ModernBertForMaskedLM`; local `AutoModel` loading succeeds. No model claim or candidate score is inferred from the discussion report.

## Implementation and fixed protocol

- Implementation root: `/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/`.
- Added only dedicated `src/gpu_modernbert_experiment.py` and `configs/gpu12-modernbert-base-openpool-v15.json`; shared Qwen runner/configs were not modified by this candidate. Runner SHA-256 `14cd0c40b60272081db3196e8c075f21d6aee083eaf9559eaf9e956be59fc252`; config SHA-256 `fc6690625946449e2d88436f4ec49211d1a72ae645f3e7e58f5648b8f1a969bc`. Both files were synchronized to Host141 with matching hashes.
- Host141 isolated input hashes: `train.csv` `40a22ce8d88c5f46feb4637a099db815bef5f713ffe53e89dbe1b7b21de77707`; saved primary folds `0569600bdc2aea862b207828218770ba84e2a696faa1d19bf2617a04355f65a4`; Open Pool rows `1e4200aed80f52d655d4900a301cb427ca1341e06be31a8b7d5fde9ea3ef425f`; pool prompts `6c18c6df3aff5e33034062bf3bbb06428986c055608181c22daebb132e3269ae`; reconstructed official prompts `41357f850c4309528a59f92ecda5323e2b1c2a925eb69dfc87ea92a4f68d6d6e`.
- Fixed settings are the registered prompt-grouped five-fold split, Open Pool v15 with prompt and exact-text filtering, uniform 2,500 rows/class, max length 384, BF16, microbatch 1, gradient checkpointing, effective rows 18, LoRA rank 16/alpha 32/dropout `.05` on all 22 layers, one stage1 epoch, and two stage2 epochs.
- Host141 `141-X9DAi`, GPU1 UUID `GPU-51b57ca0-53ca-3266-7105-efc692a6c834`; candidate11 continues separately on GPU2 UUID `GPU-48a73ba5-62ab-e9ff-b15b-e4eceae66c58`. No GPU co-location. Run directory: `artifacts/gpu12-modernbert-base-openpool-v15/`.

## Pilot

On 2026-11-08, the requested rate guard passed at 19:58:16 (5h91%, weekly72%) and again at 20:02:51 (5h90%, weekly72%). Official Kaggle model version 2 files were confirmed against `list_model_variation_version_files`. Host141's installed Transformers 4.57.1 source confirms ModernBERT's `layers[i].attn.Wqkv`, `attn.Wo`, `mlp.Wi`, and `mlp.Wo`, and its forward method does not accept `use_cache`; the dedicated runner omits that Qwen-specific argument.

The pilot passed its two-snapshot preflight on GPU1 (minimum free 15,958 MiB; minimum MemAvailable 116.52 GiB; no other compute PID). Model load, forward, backward, and optimizer step completed. PEFT inspection confirmed all 22 layers and exactly 88 intended projection modules. Optimizer step took 26.7967 seconds; peak reserved VRAM was 446 MiB, against a 11,696 MiB reserve-adjusted limit; MemAvailable was 113.84 GiB; `pass_reserve=true`. The step time includes first-call setup/compilation; it is not treated as a steady-state throughput estimate.

## Primary run and resume point

Primary started on Host141 at 20:03 JST after a fresh guard pass and two-snapshot GPU preflight. Wrapper/lock PID `2444872`; Python runner PID `2444874`; log `artifacts/gpu12-modernbert-base-openpool-v15/primary.log`; PID file `primary.pid`; lock `artifacts/.gpu1-run.lock`. At 20:03:45Z, fold0 held out 540 rows / 30 prompts. Two external prompt groups and 31 external rows were removed; 45,000 rows were sampled uniformly (2,500 per class). All 88 LoRA projection targets were verified again. The process remained CPU-active while preparing the first stage1 batches; no epoch checkpoint or OOF existed yet. At the initial 20:04 poll, GPU1 used 679 MiB/free 15,296 MiB, utilization 9%; candidate11 remained CPU-active on GPU2 with 8,545 MiB used/free 7,430 MiB. Do not restart based on elapsed time. An incomplete epoch is not saved; resume from the most recently completed epoch checkpoint.

At 20:06:41 JST, runner `2444874` and candidate11 runner `2439031` remained CPU-active. GPU1 was at 679 MiB used / 15,296 MiB free / 12%; GPU2 at 8,545 / 7,430 MiB / 42%; MemAvailable `117,145,904 kB`. The ModernBERT log remained at first-batch setup, with no epoch checkpoint or OOF. Resource floors were still satisfied; preserve both jobs without restart.

At 20:08:34 JST, both Host141 runners remained active. ModernBERT remained at 679 MiB used / 15,296 MiB free / 12% on GPU1; MemAvailable was `117,252,772 kB`. No new log line or checkpoint appeared after the first-batch setup. Candidate11 continued on GPU2 at 8,545 MiB used / 7,430 MiB free / 37%. Host142 Qwen04/Qwen8B remained CPU-active on their assigned GPUs; no newer Qwen04 confirmation OOF than fold0 at 16:43:17 was present. Official leaderboard refresh at 20:09 still showed a `.752` tie; see [official leaderboard](https://www.kaggle.com/competitions/name-that-llm/leaderboard).

Host142 jobs were left untouched: Qwen04 PID `3771645` on GPU0 and Qwen8B confirmation PID `3871913` on GPU1 remained active; registered watchers stayed alive. At 20:03:51, GPU0 used 3,907 MiB/free 12,068 MiB, GPU1 used 15,828 MiB/free 16,272 MiB, and host MemAvailable was `212,815,936 kB`. Qwen04's latest saved confirmation OOF remained fold0 (16:43:17).

Run/resume command (check the guard, exact UUID, current PIDs, memory floor, and latest checkpoint first):

```bash
cd /mnt/HDD10TB-2/aburatani/kaggle/name-that-llm
flock -n artifacts/.gpu1-run.lock env CUDA_VISIBLE_DEVICES=GPU-51b57ca0-53ca-3266-7105-efc692a6c834 \
  .venv/bin/python -u src/gpu_modernbert_experiment.py \
  --config configs/gpu12-modernbert-base-openpool-v15.json \
  --model-path artifacts/model-cache/modernbert-base-kaggle-v2 \
  --run-dir artifacts/gpu12-modernbert-base-openpool-v15 --resume --split primary
```

No Kaggle object, Notebook, or submission was created. Primary adoption and any confirmation remain pending full OOF and prompt-paired analysis.

At 20:40:57 JST, Host141 runner PID `2444874` and wrapper `2444872` remained live (elapsed 37:48, CPU time 47:27). GPU1 UUID `GPU-51b57ca0-53ca-3266-7105-efc692a6c834` used 679 MiB / free 15,296 MiB / 10%; host MemAvailable was `111,441,924 kB`. `primary.log` is unchanged since fold0 setup at 20:03:45; no epoch checkpoint/OOF exists. CPU time advanced by about 14 minutes since the previous observation, consistent with ongoing first-stage work. Keep the job; incomplete epoch work is unsaved and resume starts from the latest completed epoch (none yet).
### 2026-11-08 21:00 JST status

Host141 (`141-X9DAi`) runner PID `2444874` remains live and CPU-active (elapsed `57:41`, CPU `1:12:33`) on GPU1 UUID `GPU-51b57ca0-53ca-3266-7105-efc692a6c834`. Host GPU1 has `679 MiB` used / `15296 MiB` free; host MemAvailable is `113625309184` bytes. No checkpoint or OOF has been saved; resume from the latest completed epoch (none), preserving the in-progress fold0 epoch. User requested continuation, not a stop. Do not restart.
### 2026-11-08 21:21 JST status

Host141 (`141-X9DAi`) runner PID `2444874` remains live and CPU-active (elapsed `1:18:26`, CPU `1:42:38`) on GPU1 UUID `GPU-51b57ca0-53ca-3266-7105-efc692a6c834`. GPU1 has `679 MiB` used / `15296 MiB` free; host MemAvailable is `112464785408` bytes. No checkpoint or OOF was written in the last 15 minutes; preserve the in-progress fold0 epoch and resume from the latest completed epoch (none). User's instruction is to continue; do not restart.

### 2026-11-09 00:21 JST live progress / resume state

Host141 poll via the recorded `ssh 141` path confirms candidate12 runner PID `2444874` remains CPU-active on GPU1 UUID `GPU-51b57ca0-53ca-3266-7105-efc692a6c834`; GPU1 used 679 MiB / free 15,296 MiB / 11%, host MemAvailable `111197596 kB`. Host141 candidate11 and candidate13 runners are also live on GPU2/GPU0; all three devices remain assigned. Candidate12 now has a completed fold0 Stage1 epoch-001 checkpoint (saved 00:06 JST) and a Stage2 epoch-001 checkpoint (saved 00:18 JST); `primary/fold-0/stage2/latest.json` points to `epoch-001`. No fold0 OOF exists yet. Keep the current runner; if an explicit stop/restart later requires resuming, the latest durable point is `artifacts/gpu12-modernbert-base-openpool-v15/primary/fold-0/stage2/epoch-001/`, then continue the registered primary folds with the command above and `--resume --split primary`. No run was stopped or restarted in this poll.
### 2026-11-09 00:31 JST latest checkpoint / resume point

Host141 live poll confirms PID `2444874` remains CPU-active on GPU1 UUID `GPU-51b57ca0-53ca-3266-7105-efc692a6c834` (GPU1 679 MiB used / 15,296 MiB free / 13%; MemAvailable `111001788 kB`). The durable fold0 point advanced from Stage2 epoch-001 to epoch-002 at 00:30 JST: `artifacts/gpu12-modernbert-base-openpool-v15/primary/fold-0/stage2/epoch-002/state.pt`; `stage2/latest.json` points to `epoch-002`. Fold0 OOF is not present yet and the runner is still alive, so do not relaunch. If an explicit future stop/restart requires resume, use the frozen command above with `--resume --split primary`; the latest completed checkpoint is Stage2 epoch-002.
### 2026-11-09 00:41 JST fold0 OOF and fold1 resume state

Host141 read-only poll confirms PID `2444874` remains CPU-active on GPU1 UUID `GPU-51b57ca0-53ca-3266-7105-efc692a6c834` (659 MiB used / 15,316 MiB free / 9%; MemAvailable `109295572 kB`). Fold0 completed and saved OOF at 00:31:31 JST: 540 rows, 30 held-out prompts, balanced accuracy `0.4407407407`; peak allocated VRAM `418 MiB`. This is only one fold and does not trigger the registered adoption gate. The runner began fold1 setup at 00:31:38: 2,159 official-train rows, 540 validation rows / 30 prompts, two validation-prompt groups excluded (49 external rows), then 45,000 uniform Open Pool rows (2,500/class), with 22 layers / 88 LoRA modules mapped. At 00:41 the runner remained CPU-active; preserve it. Latest durable checkpoint remains fold0 Stage2 epoch-002 at `primary/fold-0/stage2/epoch-002/`; no fold1 checkpoint exists yet. If an explicit stop/restart requires resuming, use the frozen command above with `--resume --split primary`; do not restart the live process.

### 2026-11-09 05:15 JST live progress

Host141 PID `2444874` remains live on GPU1 UUID `GPU-51b57ca0-53ca-3266-7105-efc692a6c834` (659 MiB used / 15,316 MiB free, 11% utilization). Fold1 completed at 05:08:56 JST with OOF/logits for 540 rows / 30 prompts: balanced accuracy `0.4222222222`, peak allocated VRAM `418 MiB`. Fold2 setup began at 05:08:58 with 2,159 training rows, 540 validation rows / 30 prompts, 1 prompt group excluded, and 45,000 Open Pool rows. Stage2 epoch-002 is the latest saved checkpoint at 05:08:12. The runner remains active; two of five folds are complete, so do not infer the full OOF result or stop early. No Kaggle object, Notebook, or submission.

### 2026-11-09 09:09 JST checkpoint / continuation

Host141 candidate12 runner PID `2444874` remained CPU-active. Fold2 Stage1 epoch-001 checkpoint was saved at 09:08:17 JST: `artifacts/gpu12-modernbert-base-openpool-v15/primary/fold-2/stage1/epoch-001/state.pt`; `stage1/latest.json` points to `epoch-001`. The checkpoint records `mean_loss=1.83142446`, `examples=45000`, `peak_allocated_mib=418`, and `stop_requested=false`; the runner log reported MemAvailable `104.46 GiB`. Preserve the live run and continue the registered five-fold primary; do not restart or interpret two earlier folds as the full OOF gate. The user reaffirmed continuation, not a stop. No Kaggle object, Notebook, or submission.

### 2026-11-09 09:21 JST continuation checkpoint

Host141 PID `2444874` remains CPU-active on GPU1. Fold2 Stage2 epoch-001 checkpoint advanced at 09:19:43 JST: `artifacts/gpu12-modernbert-base-openpool-v15/primary/fold-2/stage2/epoch-001/state.pt`; `stage2/latest.json` points to `epoch-001`. The epoch log reports `mean_loss=1.59754199`, `examples=2159`, `peak_allocated_mib=418`, and MemAvailable `104.68 GiB`; no fold2 OOF has been written. Keep the live run and continue all five registered folds. Host142 Qwen04 and Qwen8B confirmation runners also remain CPU-active; latest saved OOFs remain Qwen04 fold2 and Qwen8B fold1, so the full blend confirmation and downstream fixed Spectral confirmation are still waiting. No restart, stop, new run, Kaggle write, or submission.

### 2026-11-09 09:31 JST Stage2 checkpoint

The read-only host poll confirms candidate12 PID `2444874` is still CPU-active on Host141 GPU1. Fold2 Stage2 epoch-002 checkpoint is now durable at `artifacts/gpu12-modernbert-base-openpool-v15/primary/fold-2/stage2/epoch-002/state.pt`, and `stage2/latest.json` points to `epoch-002` (saved 09:31:01 JST). Its epoch log records `mean_loss=1.38801129`, `examples=2159`, `peak_allocated_mib=418`, `MemAvailable=104.72 GiB`, and `stop_requested=false`. Fold2 OOF is not yet present; retain the live process and wait for the fold output before considering any gate. The other four GPU runs remain assigned and active, so the registered queue is unchanged.

### 2026-11-09 09:41 JST fold2 OOF / fold3 start

Candidate12 fold2 OOF is now saved at `artifacts/gpu12-modernbert-base-openpool-v15/primary/fold-2/oof.parquet` (540 rows, 30 held-out prompts). The runner-reported fold balanced accuracy is `0.4444444444` with peak allocated VRAM `418 MiB`; this is a single-fold partial result, not the five-fold adoption gate. Fold3 setup has begun: 540 validation rows / 30 prompts, 5 validation prompt groups excluded from the Open Pool with 19 external rows removed, and 45,000 external rows retained (2,500 per class). Runner PID `2444874` remains CPU-active. Continue without restart; full OOF and prompt-paired bootstrap remain pending.

### 2026-11-09 09:51 JST verified wait

The 10-minute Host141 poll confirms PID `2444874` remains alive on GPU1 and CPU-active (about 126% CPU); CPU time advanced from `17:17:42` to `17:30:46` since the 09:41 poll. No new fold3 checkpoint or OOF is present yet. The latest durable candidate12 state remains fold2 Stage2 epoch-002 plus fold0–2 OOF files. Fold3 had begun setup at 09:31:52 JST; preserve it without restart while the runner continues. No adoption decision or queue change.

### 2026-11-09 10:02 JST verified continuation

Host141 PID `2444874` remains CPU-active on GPU1 (CPU time `17:46:14`, about 126%). Its durable state has not advanced since the 09:31 fold2 Stage2 epoch-002 checkpoint and fold2 OOF; fold3 remains in progress with folds0–2 complete. Preserve the live runner without restart. Host141 candidates11/12/13 remain active; candidate11's latest OOF is fold0 (05:10), and candidate13's fold1 checkpoint advanced separately (see its log). Host141 GPUs0/1/2 use/free are `1405/14568`, `659/15316`, `8549/7426 MiB`; MemAvailable is `109870728 kB`. All host GPUs remain assigned. No adoption/queue decision, stop, restart, or Kaggle write/submission.

### 2026-11-09 10:18 JST verified wait

Host141 PID `2444874` remains CPU-active on GPU1 (CPU time `18:04:49`, about 126%), with no fold3 checkpoint or OOF newer than the 09:31 fold2 Stage2 epoch-002 / OOF. Candidate11 and candidate13 also remain CPU-active; no relevant OOF/checkpoint changed since 10:02. GPU0/1/2 use/free are `1405/14568`, `659/15316`, `8549/7426 MiB`; MemAvailable is `109959316 kB`. Preserve all runs and the registered queue; no stop, restart, or adoption decision.

### 2026-11-09 10:41 JST verified wait

Host141 PID `2444874` remains CPU-active on GPU1 (CPU time `18:34:44`, about 126%). No fold3 checkpoint or OOF newer than the 09:31 fold2 Stage2 epoch-002 / OOF was found. Folds0–2 remain the only candidate12 OOF folds. GPU0/1/2 use/free are `1405/14568`, `659/15316`, `8549/7426 MiB`; MemAvailable is `109090116 kB`. Preserve the live run and registered queue; no stop, restart, or adoption decision.

### 2026-11-09 10:56 JST verified wait

Host141 PID `2444874` remains CPU-active on GPU1 (CPU time `18:54:19`, about 126%). No fold3 checkpoint or OOF newer than the 09:31 fold2 Stage2 epoch-002 / OOF was found; folds0–2 remain the only OOF folds. GPU0/1/2 use/free are `1405/14568`, `659/15316`, `8549/7426 MiB`; MemAvailable is `109272684 kB`. Preserve the live run and registered queue.

### 2026-11-09 11:06 JST verified wait

Host141 PID `2444874` remains CPU-active on GPU1 (CPU time `19:06:25`, about 126%). No fold3 checkpoint or OOF newer than the 09:31 fold2 Stage2 epoch-002 / OOF was found; folds0–2 remain the only OOF folds. GPU0/1/2 use/free are `1405/14568`, `659/15316`, `8549/7426 MiB`; MemAvailable is `109295008 kB`. Preserve the live run and registered queue.

### 2026-11-09 11:16 JST verified wait

Host141 PID `2444874` remains CPU-active on GPU1 (CPU time `19:18:34`, about 126%). No fold3 checkpoint or OOF newer than the 09:31 fold2 Stage2 epoch-002 / OOF was found; folds0–2 remain the only OOF folds. GPU0/1/2 use/free are `1405/14568`, `659/15316`, `8549/7426 MiB`; MemAvailable is `109257300 kB`. Preserve the live run and registered queue.

### 2026-11-09 11:26 JST verified wait

Host141 PID `2444874` remains CPU-active on GPU1 (CPU time `19:31:45`, about 126%). No fold3 checkpoint or OOF newer than the 09:31 fold2 Stage2 epoch-002 / OOF was found; folds0–2 remain the only OOF folds. GPU0/1/2 use/free are `1405/14568`, `659/15316`, `8549/7426 MiB`; MemAvailable is `109275720 kB`. Preserve the live run and registered queue.

### 2026-11-09 11:28 JST read-only activity diagnosis

The runner's stdout remains unchanged since fold3 data/LoRA setup at 09:31:54 JST, but PID `2444874` is in runnable state with CPU time advancing and about 126% CPU. Five `nvidia-smi dmon` samples show GPU1 at 9–11% SM utilization with its process still present. This is consistent with the prior folds' approximately four-hour Stage1 over 45,000 rows (fold0 and fold2), so the quiet log is not evidence of a dead process. Keep the live process and do not restart.

### 2026-11-09 11:38 JST verified wait

Host141 PID `2444874` remains CPU-active on GPU1 (CPU time `19:44:26`, about 126%). No fold3 checkpoint or OOF newer than the 09:31 fold2 Stage2 epoch-002 / OOF was found; folds0–2 remain the only completed OOF folds. GPU0/1/2 use/free are `1405/14568`, `659/15316`, `8549/7426 MiB`; MemAvailable is `109277660 kB`. Preserve the live run and registered queue.

### 2026-11-09 11:49 JST verified wait

Host141 PID `2444874` remains CPU-active on GPU1 (CPU time `19:57:51`, about 126%). No fold3 checkpoint or OOF newer than the 09:31 fold2 Stage2 epoch-002 / OOF was found; folds0–2 remain the only completed OOF folds. GPU0/1/2 use/free are `1405/14568`, `659/15316`, `8549/7426 MiB`; MemAvailable is `109276796 kB`. Preserve the live run and registered queue.

### 2026-11-09 12:00 JST verified wait

Host141 PID `2444874` remains CPU-active on GPU1 (CPU time `20:11:02`, about 126%). No fold3 checkpoint or OOF newer than the 09:31 fold2 Stage2 epoch-002 / OOF was found; folds0–2 remain the only completed OOF folds. GPU0/1/2 use/free are `1405/14568`, `659/15316`, `8549/7426 MiB`; MemAvailable is `109205256 kB`. Preserve the live run and registered queue.

### 2026-11-09 12:11 JST verified wait

Host141 PID `2444874` remains CPU-active on GPU1 (CPU time `20:24:36`, about 126%). No fold3 checkpoint or OOF newer than the 09:31 fold2 Stage2 epoch-002 / OOF was found; folds0–2 remain the only completed OOF folds. GPU0/1/2 use/free are `1405/14568`, `659/15316`, `8549/7426 MiB`; MemAvailable is `109270388 kB`. Preserve the live run and registered queue.

### 2026-11-09 12:20 JST verified wait

Host141 PID `2444874` remains CPU-active on GPU1 (CPU time `20:35:07`, about 126%). No fold3 checkpoint or OOF newer than the 09:31 fold2 Stage2 epoch-002 / OOF was found; folds0–2 remain the only completed OOF folds. GPU0/1/2 use/free are `1405/14568`, `659/15316`, `8549/7426 MiB`; MemAvailable is `109257048 kB`. Preserve the live run and registered queue.

### 2026-11-09 12:21 JST verified wait

Host141 PID `2444874` remains CPU-active on GPU1 (CPU time `20:37:01`, about 126%). No fold3 checkpoint or OOF newer than the 09:31 fold2 Stage2 epoch-002 / OOF was found; folds0–2 remain the only completed OOF folds. GPU0/1/2 use/free are `1405/14568`, `659/15316`, `8549/7426 MiB`; MemAvailable is `109301112 kB`. Preserve the live run and registered queue.

### 2026-11-09 12:45 JST verified wait

Host141 PID `2444874` remains CPU-active on GPU1 (CPU time `21:05:22`, about 126%). No fold3 checkpoint or OOF newer than the 09:31 fold2 Stage2 epoch-002 / OOF was found; folds0–2 remain the only completed OOF folds. GPU0/1/2 use/free are `1405/14568`, `659/15316`, `8549/7426 MiB`; MemAvailable is `109324504 kB`. Preserve the live run and registered queue.

### 2026-11-09 13:40 JST fold3 Stage1 checkpoint

Host141 PID `2444874` completed fold3 Stage1 epoch-001 and saved `artifacts/gpu12-modernbert-base-openpool-v15/primary/fold-3/stage1/epoch-001/state.pt` at 13:31:06 JST. It trained on 45,000 external examples; mean loss was `1.834451`, peak allocated VRAM `418 MiB`, and MemAvailable at save was `104.21 GiB`. Fold3 OOF is not yet present; the runner remains active and can resume from this checkpoint. At the 13:40:53 poll its CPU use was ~125%, GPU1 use/free was `659/15316 MiB`, and Host141 MemAvailable was `109540704 kB`. Preserve the run and await Stage2/OOF.

### 2026-11-09 13:51 JST fold3 Stage2 checkpoint

Host141 PID `2444874` saved primary fold3 Stage2 epoch-001 at 13:42:43 JST to `artifacts/gpu12-modernbert-base-openpool-v15/primary/fold-3/stage2/epoch-001/state.pt`; mean loss `1.568249`, 2,159 official training rows, peak allocated VRAM `418 MiB`. The fold3 OOF remains pending. At 13:51:22 the runner was still live on GPU1, use/free `659/15316 MiB`, Host141 MemAvailable `109872248 kB`; preserve the current Stage2 work and resume point.

### 2026-11-09 13:57 JST fold3 OOF and fold4 setup

Fold3 Stage2 epoch-002 was saved at 13:54:14 JST (mean loss `1.370397`, 2,159 training rows, peak VRAM `418 MiB`); fold3 OOF completed at 13:54:52 with BA `0.462962963`. Its parquet has 540 unique IDs, 30 prompts and 18 classes; ID, prompt and true-model labels match `data/train.csv`, and the stored fold is 3. Partial primary across folds0–3 is BA `0.442592593` (equal 540-row folds); this is descriptive only pending fold4 and the full paired gate. Fold4 setup began at 13:54:54: 2,160 train rows, 539 validation rows / 30 prompts, one prompt group excluded (7 external rows removed), 45,000 external examples retained; all 22 model layers were selected. PID `2444874` remains active on GPU1 (13:56:49 poll: use/free `659/15316 MiB`, MemAvailable `109337960 kB`); fold4 checkpoint/OOF are pending. Resume at the live fold4 runner and keep the saved fold3 checkpoint/OOF.

### 2026-11-09 14:01 JST interim paired comparison

Compared candidate12 folds0–3 against the adopted prompt-centered SVC primary OOF after confirming identical IDs, prompt IDs, fold assignments and labels. On 2,160 rows / 120 prompts, partial observed BA delta is `-0.021759`; a 2,000-replicate prompt-paired bootstrap (seed 42) gives 95% CI `[-0.045382,+0.001852]`. The helper's partial-only return labels this as reject because the observed delta is negative, but this is not the preregistered full-fold decision: fold4 is running, so retain the candidate until its fifth fold is complete, then apply the full primary gate. No GPU or runner was changed by this CPU-only analysis.

### 2026-11-09 18:08 JST fold4 Stage1 checkpoint

Host141 PID `2444874` remains alive on GPU1; at 18:08 GPU1 had `659 MiB` used / `15,316 MiB` free and host MemAvailable was `109266220 kB`. Fold4 Stage1 epoch-001 checkpoint was saved at 17:57:05; `latest.json` points to `epoch-001`, and `state.pt` is 28,674,595 bytes. The log records mean loss `1.849857`, 45,000 examples, peak allocated 418 MiB, and `stop_requested=false`. Fold4 OOF is pending; preserve the live final-fold run.

### 2026-11-09 18:19 JST fold4 Stage2 checkpoint

Host141 PID `2444874` remains alive on GPU1; at 18:19 GPU1 had `659 MiB` used / `15,316 MiB` free and host MemAvailable was `109240512 kB`. Fold4 Stage2 epoch-001 checkpoint was saved at 18:08:32; `latest.json` points to `epoch-001`, and `state.pt` is 28,674,595 bytes. The log records mean loss `1.614874`, 2,160 official training rows, peak allocated 418 MiB, and `stop_requested=false`. Fold4 OOF is pending; preserve the live run.

### 2026-11-09 18:36 JST full primary decision

Fold4 Stage2 epoch-002 was saved at 18:19:59 (mean loss `1.415334`, 2,160 official rows, peak allocated 418 MiB); fold4 OOF completed at 18:20:38 with BA `0.465261814` on 539 rows. All five fold OOFs (2,699 rows / 150 prompts / 18 classes) match official train and the adopted SVC exactly on IDs, prompts, labels, and fold assignments. Candidate BA is `0.447121551` vs SVC `0.501933880`, delta `-0.054812329`; fold candidate BAs are `.440741/.422222/.444444/.462963/.465262`, with deltas `-.044444/-.059259/-.059259/-.066667/-.044317`. The registered prompt-paired bootstrap (2,000 reps, seed 42) gives 95% CI `[-.076297,-.034049]`, mean delta `-.054939`; reject candidate12 under the full primary gate and skip confirmation. PID `2444874` and wrapper `2444872` have exited; at 18:34 GPU1 showed `15 MiB` used / `15,960 MiB` free, effectively released. Other runs on Host141/142 continue. No new run was started.
