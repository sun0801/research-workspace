# Host continuation log — 2026-11-12

## 00:50 JST — Host142 Qwen8B watcher exit; GPU1 idle

Strict SSH using the static alias `142` succeeded. The previously live Qwen3-8B watcher PID `905369` and final-fit worker/lock PIDs `1414477`/`1414475` are now absent. The prior Qwen8B final-fit success and local baseline asset staging remain recorded in the [2026-11-11 continuation log](2026-11-11-host-continuation-poll.md).

Two read-only resource snapshots found no compute applications. GPU1 is the registered UUID `GPU-8a059266-7ede-0427-ff30-08ba7a9b5224`, with 172 MiB used and 31,929 MiB free; `MemAvailable` was 222,241,656 kB and the Kaggle filesystem had 7,032 GiB free. The prior stopped Candidate09 watcher PID `3748103` remains in `T` state. No active GPU runner or matching run lock was found.

Candidate14 OLMo2 was not started: its approved spec requires the preceding Host142 GPU1 job/watcher handles to be terminal; the stopped Candidate09 watcher is still a live process. No process was resumed or terminated, and no new run or Kaggle write/submission was started. Resume only after the queue handle is resolved under its registered procedure; recheck the rate guard, exact UUID, processes, lock, RAM, and disk immediately before a pilot.

## 01:51 JST — Host142 poll blocked by SSH host-key verification

- The scheduled one-command read-only poll to alias `142` failed before connecting with `Host key verification failed`.
- Read-only SSH config resolves alias `142` to `10.10.40.142`, user `aburatani`, port 22. `ssh-keygen -F` found no entry for either alias or IP in `/home/aburatani/.ssh/known_hosts`.
- No host-key check was bypassed, no process was touched, and no host state was inferred from this failed connection. Last confirmed state remains the 00:50 JST entry above. Do not start or stop jobs on Host142 until its host key is safely confirmed. Retry only at a later scheduled poll if the trust entry is restored.

## 12:19 JST — host availability recheck

- A fresh `ssh -o BatchMode=yes 142 ...` read-only poll again failed with `Host key verification failed`; no Host142 GPU/RAM/process state was inferred and no trust check was bypassed. `ssh-keygen -F` also found no alias/IP record in `known_hosts.old`, so there is no local backup trust entry to use.
- Host141 snapshot: GPU0 had 171 MiB used / 0% utilization; GPU1 had 15 MiB / 0%; GPU2 had 5,777 MiB used and 100% utilization. `MemAvailable` was 116,713,696 kB. The filtered process-name check did not identify GPU2's owner, so do not use that GPU or infer its process is ours. No process was started or stopped. Existing queued specs remain tied to their recorded Host142 resource gates; no candidate was moved to Host141.


## 13:34 JST — Host141 GPU owner identified; leave in use

- Strict read-only `ssh -o BatchMode=yes -o ConnectTimeout=8 141 nvidia-smi` showed GPU0 171 MiB/0%, GPU1 15 MiB/0%, GPU2 6,093 MiB/100%. GPU2 compute PID 3126079 uses 6,070 MiB.
- A single-PID read-only `ps` query identified PID 3126079 as user `ogata`, running `token_aux/sample_text_only.py` (elapsed 48:21). This is another user's active research run; no process, GPU, lock, or files were changed. Do not use GPU2. No candidate was moved from its approved Host142 target.
- Host142 remains unverified because strict SSH host-key verification failed at 12:19; no state is inferred and no bypass was attempted.


## 14:39 JST — Host141 GPU2 owner run advanced

- Strict `ssh ... 141 nvidia-smi` showed GPU0 171 MiB/0%, GPU1 15 MiB/0%, GPU2 5,777 MiB/100%; compute PID changed from 3126079 to 3138642. The follow-up single-PID query shows `ogata` running `token_aux/eval_denoise.py` under the same research output tree. This is another user's active work; left untouched. Host141 GPU0/1 remain apparently idle, but no spec-target GPU was reassigned.
- Host142 poll at 14:38 JST again failed strict host-key verification; no state inferred and no bypass attempted.
