---
project: kaggle-name-that-llm
date: 2026-11-08
status: primary-running
spec: ../specs/2026-11-08-modernbert-large-openpool-v15-host141-spec.md
tags: [experiment, gpu, modernbert, kaggle]
---

# ModernBERT-Large + Open Pool v15

## Candidate and source

Candidate13 compares ModernBERT-Large with the concurrently running ModernBERT-Base using the same Open Pool v15 / prompt-grouped protocol. The lead is a capacity-scaling hypothesis, not a performance claim. Kaggle Discussion [754860, comment 3551013](https://www.kaggle.com/competitions/name-that-llm/discussion/754860) reports ModernBERT CV `.616` and public LB `.575`, but pool version, split, and leakage controls are unspecified; both remain author-reported and unverified.

Kaggle's [Answer.AI ModernBERT-Large model](https://www.kaggle.com/models/answer-ai/modernbert/PyTorch/large), PyTorch version 2, is fine-tunable and Apache 2.0. The official file listing contains seven files totaling 1,585,746,891 bytes; downloaded files match official byte sizes. Weight SHA-256: `fabb014a0b62d28ec5f2de530d2ade920b9293f170a4ec38acfa1b8096531adc`. Model config: `model_type=modernbert`, `hidden_size=1024`, `num_hidden_layers=28`, architecture `ModernBertForMaskedLM`.

## Implementation and fixed protocol

- Implementation root: `/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/`.
- Added isolated `src/gpu_modernbert_large_experiment.py` and `configs/gpu13-modernbert-large-openpool-v15.json`; candidate12 runner/config and shared Qwen runner were left intact. Runner SHA-256 `910c493f9f73aa31bc7dcadb644055cf4dd3e0039aa25cfecb28db2328be824f`; config SHA-256 `ec8f9687ec9bebdbe0f965b166c5483cf7afb3f344e6339ed387de1f78da13c7`. Host141 copies match. Data/folds/pool/prompt-reconstruction hashes are the verified Host141 files recorded in [candidate12's log](2026-11-08-modernbert-base-openpool-v15.md); they were reused without modification.
- Same saved `GroupKFold(prompt_id)` primary folds, Open Pool v15 exact-text and validation-prompt filtering, uniform 2,500 rows/class, seed42, max length384, BF16, microbatch1, gradient checkpointing, effective rows18, stage1 one epoch, stage2 two epochs, LoRA rank16/alpha32/dropout `.05`. LoRA targets all 28 layers and four projections (`attn.Wqkv`, `attn.Wo`, `mlp.Wi`, `mlp.Wo`); pooled states `[2,4,8,12,16,20,24,28]`.
- Host141 `141-X9DAi`, GPU0 UUID `GPU-c542e903-dac3-5541-ea10-2b66b06e5f61`. Concurrent candidate12 uses GPU1 and candidate11 uses GPU2; no GPU is shared. Run directory `artifacts/gpu13-modernbert-large-openpool-v15/`, model cache `artifacts/model-cache/modernbert-large-kaggle-v2/` (Git-excluded).

## Pilot

Rate guard passed at 20:18:20 JST (5h88%, weekly72%), then again at 20:20:40 JST (5h88%, weekly72%). Host141 GPU0 double-snapshot preflight passed with minimum free 15,799 MiB, minimum MemAvailable 111.22 GiB, no external compute PID, and exact UUID match. Local load, forward, backward, optimizer step passed. The runner confirmed all 28 target layer IDs and 112 intended LoRA modules. Optimizer step took 20.2626 seconds; peak reserved VRAM 1,036 MiB against an 11,538 MiB reserve-adjusted ceiling; MemAvailable 108.59 GiB; `pass_reserve=true`.

## Primary and resume point

Primary started at 20:20 JST. Wrapper/lock PID `2448740`; Python runner PID `2448742`; log `artifacts/gpu13-modernbert-large-openpool-v15/primary.log`; PID file `primary.pid`; lock `artifacts/.gpu0-run.lock`. At 20:21:09, both ModernBERT-Large runner and wrapper were alive; no epoch checkpoint/OOF had appeared yet. GPU0 showed 174 MiB used / 15,799 MiB free, utilization 0%; host MemAvailable was `116,573,160 kB`. The runner was CPU-active during initialization. Do not restart based on elapsed time. Incomplete epochs are not saved; resume from latest completed epoch checkpoint.

At 20:21:35Z, fold0 setup held out 540 rows / 30 prompts; two external prompt groups and 31 rows were removed, then 45,000 rows were sampled uniformly. All 28 encoder layers and 112 intended LoRA projection modules were verified. At 20:22:48 JST the runner remained CPU-active; GPU0 used 1,405 MiB / free 14,568 MiB / 17%, and host MemAvailable was `111,697,596 kB`. No epoch checkpoint or OOF existed yet.

At 20:26:22 JST, candidate13 runner PID `2448742` remained CPU-active (elapsed 5:29, CPU time 7:39). GPU0 remained at 1,405 MiB used / 14,568 MiB free / 13%; host MemAvailable was `111,657,036 kB`. The primary log was unchanged after the fold0 setup/112-target verification at 20:21:40; no checkpoint/OOF had been written. Candidate12 and candidate11 also remained live and CPU-active on GPU1/GPU2, with resource floors passing. Do not interrupt based on an incomplete epoch.

Run/resume command (check fresh guard, current PIDs, exact UUID, GPU/RAM floors, and latest checkpoint first):

```bash
cd /mnt/HDD10TB-2/aburatani/kaggle/name-that-llm
flock -n artifacts/.gpu0-run.lock env CUDA_VISIBLE_DEVICES=GPU-c542e903-dac3-5541-ea10-2b66b06e5f61 \
  .venv/bin/python -u src/gpu_modernbert_large_experiment.py \
  --config configs/gpu13-modernbert-large-openpool-v15.json \
  --model-path artifacts/model-cache/modernbert-large-kaggle-v2 \
  --run-dir artifacts/gpu13-modernbert-large-openpool-v15 --resume --split primary
```

No Kaggle object, Notebook, or submission was created. Adoption/confirmation wait for complete primary OOF and paired analysis.

At 20:40:57 JST, Host141 runner PID `2448742` and wrapper `2448740` remained live (elapsed 20:04, CPU time 24:11). GPU0 UUID `GPU-c542e903-dac3-5541-ea10-2b66b06e5f61` used 1,405 MiB / free 14,568 MiB / 11%; host MemAvailable was `111,441,924 kB`. `primary.log` is unchanged since fold0 setup and 112-target verification at 20:21:40; no epoch checkpoint/OOF exists. CPU time advanced since the prior poll. Keep the current first-stage epoch; incomplete epoch work is unsaved and resume starts from the latest completed epoch (none yet).
### 2026-11-08 21:00 JST status

Host141 (`141-X9DAi`) runner PID `2448742` remains live and CPU-active (elapsed `39:58`, CPU `46:48`) on GPU0 UUID `GPU-c542e903-dac3-5541-ea10-2b66b06e5f61`. Host GPU0 has `1405 MiB` used / `14568 MiB` free; host MemAvailable is `113625309184` bytes. No checkpoint or OOF has been saved; resume from the latest completed epoch (none), preserving the in-progress fold0 epoch. User requested continuation, not a stop. Do not restart.
### 2026-11-08 21:21 JST status

Host141 (`141-X9DAi`) runner PID `2448742` remains live and CPU-active (elapsed `1:00:42`, CPU `1:10:30`) on GPU0 UUID `GPU-c542e903-dac3-5541-ea10-2b66b06e5f61`. GPU0 has `1405 MiB` used / `14568 MiB` free; host MemAvailable is `112464785408` bytes. No checkpoint or OOF was written in the last 15 minutes; preserve the in-progress fold0 epoch and resume from the latest completed epoch (none). User's instruction is to continue; do not restart.

### 2026-11-09 05:15 JST live progress

Host141 PID `2448742` remains alive on GPU0 UUID `GPU-c542e903-dac3-5541-ea10-2b66b06e5f61` (1,405 MiB used / 14,568 MiB free, 11% utilization), using 114% CPU at the 05:15:32 poll. Candidate13 fold0 OOF BA `.4962962963` and fold1 setup at 03:29:45 JST remain the latest saved primary outputs; there is no newer epoch checkpoint/OOF. GPU0 utilization was 37% and host MemAvailable `109420360 kB`, so the process is still active, not established as stopped. Preserve it and do not restart based solely on the older checkpoint timestamp. No candidate adoption decision or Kaggle object/submission.

### 2026-11-09 10:02 JST checkpoint

Host141 PID `2448742` remains CPU-active on GPU0 UUID `GPU-c542e903-dac3-5541-ea10-2b66b06e5f61` (CPU time `15:35:59`, about 113%). The primary fold1 Stage1 `epoch-001/state.pt` was saved at 10:01:54 JST (59,746,003 bytes); `stage1/latest.json` points to `epoch-001`. Fold0 OOF BA `.4962962963` remains the latest OOF; fold1 OOF is pending. GPU0 has `1405 MiB` used / `14568 MiB` free, host MemAvailable is `109870728 kB`. Preserve the live run; no restart, stop, adoption, or Kaggle write/submission.

### 2026-11-09 10:18 JST verified wait

Host141 PID `2448742` remains CPU-active on GPU0 (CPU time `15:52:32`, about 113%). No checkpoint or OOF newer than the 10:01:54 fold1 Stage1 epoch-001 checkpoint was found. Fold0 OOF BA `.4962962963` remains the latest result; fold1 OOF is pending. GPU0 has `1405 MiB` used / `14568 MiB` free and host MemAvailable is `109959316 kB`. Preserve the live run without restart.

### 2026-11-09 10:29 JST fold1 Stage2 checkpoint

Host141 PID `2448742` remains CPU-active on GPU0. Fold1 Stage2 `epoch-001/state.pt` was saved at 10:20:36 JST (59,746,003 bytes), and `stage2/latest.json` points to `epoch-001`. The fold1 OOF is still pending; fold0 OOF BA `.4962962963` remains the only completed fold result. GPU0 has `1405 MiB` used / `14568 MiB` free; host MemAvailable is `109908136 kB`. Preserve the run and its checkpoint; do not restart.

### 2026-11-09 10:41 JST fold1 OOF / fold2 start

Candidate13 fold1 completed at 10:40:33 JST and wrote `primary/fold-1/oof.parquet` and `logits.npy` (540 rows / 30 prompts). Its fold BA is `.4722222222`; peak allocated VRAM was `1034 MiB`, and MemAvailable at fold completion was `105.18 GiB`. Fold2 setup began at 10:40:35: one validation prompt group was excluded and 11 external rows removed, with 45,000 Open Pool rows retained; 28 model layers / 112 LoRA modules mapped. The runner PID `2448742` remains active. This is a two-fold interim result only; continue all five primary folds, with no adoption decision or restart.

### 2026-11-09 10:56 JST verified wait

Host141 PID `2448742` remains CPU-active (CPU time `16:38:25`, about 113%). No fold2 checkpoint or OOF newer than the fold1 completion at 10:40:33 was found. The durable resume point remains fold1 Stage2 epoch-002; fold2 is in progress. GPU0 has `1405 MiB` used / `14568 MiB` free; MemAvailable is `109272684 kB`. Preserve the runner without restart.

### 2026-11-09 11:06 JST verified wait

Host141 PID `2448742` remains CPU-active (CPU time `16:49:18`, about 113%). No fold2 checkpoint or OOF newer than the fold1 completion at 10:40:33 was found. The durable resume point remains fold1 Stage2 epoch-002; fold2 is in progress. GPU0 has `1405 MiB` used / `14568 MiB` free; MemAvailable is `109295008 kB`. Preserve the runner without restart.

### 2026-11-09 11:16 JST verified wait

Host141 PID `2448742` remains CPU-active (CPU time `17:00:15`, about 113%). No fold2 checkpoint or OOF newer than the fold1 completion at 10:40:33 was found. The durable resume point remains fold1 Stage2 epoch-002; fold2 is in progress. GPU0 has `1405 MiB` used / `14568 MiB` free; MemAvailable is `109257300 kB`. Preserve the runner without restart.

### 2026-11-09 11:26 JST verified wait

Host141 PID `2448742` remains CPU-active (CPU time `17:12:17`, about 113%). No fold2 checkpoint or OOF newer than the fold1 completion at 10:40:33 was found. The durable resume point remains fold1 Stage2 epoch-002; fold2 is in progress. GPU0 has `1405 MiB` used / `14568 MiB` free; MemAvailable is `109275720 kB`. Preserve the runner without restart.

### 2026-11-09 11:38 JST verified wait

Host141 PID `2448742` remains CPU-active (CPU time `17:24:19`, about 113%). No fold2 checkpoint or OOF newer than the fold1 completion at 10:40:33 was found. The durable resume point remains fold1 Stage2 epoch-002; fold2 is in progress. GPU0 has `1405 MiB` used / `14568 MiB` free; MemAvailable is `109277660 kB`. Preserve the runner without restart.

### 2026-11-09 11:49 JST verified wait

Host141 PID `2448742` remains CPU-active (CPU time `17:37:03`, about 113%). No fold2 checkpoint or OOF newer than the fold1 completion at 10:40:33 was found. The durable resume point remains fold1 Stage2 epoch-002; fold2 is in progress. GPU0 has `1405 MiB` used / `14568 MiB` free; MemAvailable is `109276796 kB`. Preserve the live run without restart.

### 2026-11-09 12:00 JST verified wait

Host141 PID `2448742` remains CPU-active (CPU time `17:49:33`, about 113%). No fold2 checkpoint or OOF newer than the fold1 completion at 10:40:33 was found. The durable resume point remains fold1 Stage2 epoch-002; fold2 is in progress. GPU0 has `1405 MiB` used / `14568 MiB` free; MemAvailable is `109205256 kB`. Preserve the live run without restart.

### 2026-11-09 12:11 JST verified wait

Host141 PID `2448742` remains CPU-active (CPU time `18:02:08`, about 113%). No fold2 checkpoint or OOF newer than the fold1 completion at 10:40:33 was found. The durable resume point remains fold1 Stage2 epoch-002; fold2 is in progress. GPU0 has `1405 MiB` used / `14568 MiB` free; MemAvailable is `109270388 kB`. Preserve the live run without restart.

### 2026-11-09 12:20 JST verified wait

Host141 PID `2448742` remains CPU-active (CPU time `18:12:07`, about 113%). No fold2 checkpoint or OOF newer than the fold1 completion at 10:40:33 was found. The durable resume point remains fold1 Stage2 epoch-002; fold2 is in progress. GPU0 has `1405 MiB` used / `14568 MiB` free; MemAvailable is `109257048 kB`. Preserve the live run without restart.

### 2026-11-09 12:21 JST verified wait

Host141 PID `2448742` remains CPU-active (CPU time `18:13:53`, about 113%). No fold2 checkpoint or OOF newer than the fold1 completion at 10:40:33 was found. The durable resume point remains fold1 Stage2 epoch-002; fold2 is in progress. GPU0 has `1405 MiB` used / `14568 MiB` free; MemAvailable is `109301112 kB`. Preserve the live run without restart.

### 2026-11-09 12:45 JST verified wait

Host141 PID `2448742` remains CPU-active (CPU time `18:40:40`, about 113%). No fold2 checkpoint or OOF newer than the fold1 completion at 10:40:33 was found. The durable resume point remains fold1 Stage2 epoch-002; fold2 is in progress. GPU0 has `1405 MiB` used / `14568 MiB` free; MemAvailable is `109324504 kB`. Preserve the live run without restart.

### 2026-11-09 16:44 JST partial paired comparison

Candidate13 primary folds0–1 were aligned to the adopted SVC OOF at `artifacts/cpu-openpool-prompt-centered-low-pool-weight-v15/primary/oof-all.parquet`. The shared 1,080 rows (60 prompts, 18 classes) match on ID, prompt, true label, and fold. Candidate BA is `.484259` vs SVC `.483333` (delta `+.000926`); fold deltas are `+.011111` and `−.009259`. The registered `gpu_analyze.paired_prompt_bootstrap` with 2,000 prompt resamples, seed 42, gives 95% CI `[−.028704,+.027778]` and mean delta `+.000288`; partial result is uncertain and does not pass or fail the full five-fold gate. At 16:43 PID `2448742` remained alive on Host141 GPU0 (`1,405 MiB` used / `14,568 MiB` free, 13% utilization); fold2 is still active. Preserve the existing run.

### 2026-11-09 17:15 JST fold2 checkpoint

Host141 PID `2448742` remains alive on GPU0; at 17:15 GPU0 had `1,461 MiB` used / `14,512 MiB` free and host MemAvailable was `109493932 kB`. Fold2 Stage1 epoch-001 checkpoint was saved at 17:08:34; `latest.json` points to `epoch-001`, and `state.pt` is 59,746,003 bytes. The log records mean loss `1.735614`, 45,000 examples, peak allocated 1,034 MiB, and `stop_requested=false`. Fold2 OOF is not present yet; resume from the saved epoch-001 checkpoint and preserve the live run. The 17:26 poll still found the runner alive with no newer checkpoint or OOF; GPU0 had `1,461 MiB` used / `14,512 MiB` free and host MemAvailable was `109498184 kB`.

### 2026-11-09 17:38 JST fold2 Stage2 checkpoint

PID `2448742` remains alive on Host141 GPU0; at 17:38 GPU0 had `1,461 MiB` used / `14,512 MiB` free and host MemAvailable was `109484656 kB`. Fold2 Stage2 epoch-001 checkpoint was saved at 17:27:17; `latest.json` points to `epoch-001`, and `state.pt` is 59,746,003 bytes. The log records mean loss `1.472540`, 2,159 examples, peak allocated 1,034 MiB, and `stop_requested=false`. Fold2 OOF remains pending; preserve the live run.

### 2026-11-09 17:50 JST interim folds0–2 comparison

Fold2 OOF/logits were saved at 17:47:05 JST with BA `.475926`; `primary.log` records fold completion at 17:47:05 and fold3 data setup immediately after (540 validation rows, 30 prompts, five excluded prompt groups, 19 external rows removed before the 45,000-row sample, 112 adapted modules). PID `2448742` remains live. A read-only in-memory comparison aligned the 1,620 candidate rows to official train and the adopted SVC by ID, prompt, true label, and fold (90 prompts, 18 classes). Candidate BA `.481481` vs SVC `.490123`, delta `−.008642`; fold deltas are `+.011111`, `−.009259`, `−.027778`. The registered prompt-paired bootstrap (2,000 reps, seed 42) gives 95% CI `[−.032716,+.017284]`, mean delta `−.008509`. This is adverse partial evidence only; folds3–4 remain, so no full-primary decision is recorded. At 17:49 GPU0 had `1,405 MiB` used / `14,568 MiB` free and MemAvailable was `108914860 kB`. Preserve the live run.

### 2026-11-09 18:45 JST fold3 still active

Host141 PID `2448742` remains alive (CPU about 113%) and GPU2 utilization was 46%; the preceding 30-minute artifact scan found no checkpoint/OOF newer than fold2 OOF at 17:47. GPU2 remains at `8,549 MiB` used / `7,426 MiB` free; MemAvailable `113766300 kB`. Fold3 is still in progress. Preserve the run; no restart based on quiet logs alone.

### 2026-11-09 18:56 JST fold3 still active

Host141 PID `2448742` remains alive. The 18:56 poll still finds no checkpoint/OOF newer than fold2 OOF at 17:47; GPU2 has `8,549 MiB` used / `7,426 MiB` free with 42% utilization, and MemAvailable is `113688152 kB`. Fold3 remains in progress; preserve the run and do not restart from log quietness alone.

### 2026-11-09 19:06 JST fold3 still active

Host141 PID `2448742` remains alive. The 19:06 poll still finds no checkpoint/OOF newer than fold2 OOF at 17:47; GPU2 has `8,549 MiB` used / `7,426 MiB` free with 39% utilization, and MemAvailable is `113748100 kB`. Fold3 remains in progress; preserve the run and do not restart from log quietness alone.

### 2026-11-09 20:49 JST fold3 active, no new checkpoint

Host141 PID `2448742` remains CPU-active on GPU0 (GPU process memory 1,226 MiB; total GPU use/free `1,405/14,568 MiB`; utilization 17%). Host MemAvailable is `113677348 kB`. The latest durable output remains fold2 OOF at 17:47:05; no fold3 checkpoint/OOF or fold3 artifact directory exists yet, and the process remains live. Preserve the current fold3 Stage1 work without restarting. If later stopped before its first checkpoint, resume from the fold2 OOF/checkpoint and repeat fold3 Stage1 from the beginning.
