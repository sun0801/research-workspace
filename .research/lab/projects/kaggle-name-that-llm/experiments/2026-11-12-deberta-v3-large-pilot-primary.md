---
date: 2026-11-12
project: kaggle-name-that-llm
type: experiment
candidate: gpu16-deberta-v3-large-official-prompt-grouped
status: primary-running
---

# DeBERTa-v3-large pilot and primary OOF

## Pilot

- Target: Host141 GPU1, RTX A4000 (`GPU-51b57ca0-53ca-3266-7105-efc692a6c834`); Host141 GPU2's other-user process was left untouched.
- Local official model files were synchronized to Host141. `sha256sum -c SHA256SUMS`: 一致; `model.safetensors` SHA-256 prefix `7b9a354d`. Runner/config: `sha256sum -c .stage/gpu16-deberta/code.SHA256SUMS`: 一致; runner prefix `b42fbacc`, config prefix `cc762171`.
- Attempt 1 stopped during tokenizer initialization before GPU work: the official `tokenizer_config.json` supplies `extra_special_tokens` as a list, while installed Transformers 4.57.1 expects a mapping. `extra_special_tokens={}` on `AutoTokenizer.from_pretrained` preserves `[PAD]` 0, `[CLS]` 1, `[SEP]` 2, `[UNK]` 3. Original model files were not changed; the failed log is retained on Host141 as `pilot-attempt1-tokenizer-error.log`.
- Corrected pilot passed with 8 rows, microbatch 2, accumulation 4, one optimizer step, finite loss/gradients, elapsed 4.765 s, peak 8,301 MiB. Two-snapshot preflight showed 15,958 MiB free on the exact target and MemAvailable about 113.14 GiB.
- Resource gate: 8,301 MiB measured + 512 MiB transient estimate + 4,096 MiB reserve = 12,909 MiB, within 15,958 MiB free. Rate guard passed at 18:50 JST; 5-hour window 100%, weekly 22%.
- Host141 wrapper PID `3173439` completed with exit 0. Pilot evidence is in `artifacts/gpu16-deberta-v3-large-official-prompt-grouped/pilot.json`; attempt logs and the candidate config/runner are in the same Host141 project tree.

## Primary run status and next action

- Read-only baseline error profile from the preserved primary CPU OOF: adopted blend BA `.586408`; frozen Spectral output BA `.664952` on the same primary assignments, correcting 279 baseline errors while introducing 67 new errors. This supports using the frozen Spectral comparator as registered; no weights or thresholds were tuned from this profile.
- At 18:54 JST, after another passing rate guard and fresh two-snapshot preflight, started all five primary folds detached on Host141 GPU1. Wrapper PID `3174138`; lock `artifacts/.gpu1-run.lock`; log `artifacts/gpu16-deberta-v3-large-official-prompt-grouped/primary.log`; exit file `primary.exit`.
- Startup recorded hash result “一致” using `python hashlib.sha256(Path.read_bytes()).hexdigest()[:8]`, with config prefix `cc762171` and runner prefix `b42fbacc`. `fold_started` confirms fold 0, 2,159 train rows / 540 validation rows / 30 held-out prompts, 1,080 batches and 270 optimizer steps per epoch.
- Startup preflight: target GPU free 15,958 MiB; MemAvailable 113.19 GiB; resource snapshots matched; all shared locks free; 6.9 TiB disk free. Host141 cgroup memory limit reports unavailable. GPU2's other-user job remained untouched.
- Next scheduled active-job poll: 19:24 JST, one lightweight status command. Record only a state change. No Kaggle push or submission is part of this OOF screen.

## 19:24 JST — scheduled primary run poll

- One lightweight read-only Host141 poll resolved wrapper PID `3174138`'s working directory and inspected its log tail plus GPU status. The wrapper remains alive, no exit file exists, and the last event is `fold_started` for primary fold 1 at 19:19 JST (2,159 train rows, 540 validation rows, 30 held-out prompts); the run has advanced beyond fold 0. GPU1 UUID `GPU-51b57ca0-53ca-3266-7105-efc692a6c834` reports 13,759 MiB used / 2,216 MiB free and 56% utilization. This active-run snapshot shows no failure or OOM in the log tail.
- Host141 GPU2 remains the other user's process (6,093 MiB / 100% utilization) and was untouched. No action was taken on Host142. Next scheduled poll: 19:54 JST. No configuration change, push, or submission.

## 19:54 JST — scheduled primary run poll

- One lightweight read-only poll of wrapper PID `3174138` found it alive with no exit file. The last log event is primary fold 2, epoch 1 complete at 19:51:58 JST (`mean_loss=2.5710`, peak allocated 13,271 MiB); the five-fold run remains active. GPU1 reports 13,767 MiB used / 2,208 MiB free at 50% utilization. No error is visible in the tail.
- Host141 GPU2 remains the other user's process (6,093 MiB / 100% utilization) and was untouched. No action was taken on Host142. Next scheduled poll: 20:24 JST. No configuration change, push, or submission.


## 20:24 JST — scheduled primary run poll

- One lightweight read-only Host141 poll found wrapper PID `3174138` alive with no `primary.exit`. The latest log event is primary fold 3, epoch 1 complete at 20:16:27 JST (`mean_loss=2.4782`, peak allocated 13,283 MiB). The five-fold run remains active; no OOM or error appeared.
- GPU1 UUID `GPU-51b57ca0-53ca-3266-7105-efc692a6c834`: 13,771 MiB used / 2,204 MiB free, 6% utilization. Host MemAvailable is 113,871 MiB. GPU0 is idle (171 MiB used); GPU2 has a non-ours process at 5,777 MiB / 100% utilization and was left untouched.
- Rate guard at 20:24:46 JST passed (5h 90%, weekly 21%). No config change, push, or submission. Next scheduled poll: 20:54 JST.
