# Host continuation log — 2026-11-12

## 00:50 JST — Host142 Qwen8B watcher exit; GPU1 idle

Strict SSH using the static alias `142` succeeded. The previously live Qwen3-8B watcher PID `905369` and final-fit worker/lock PIDs `1414477`/`1414475` are now absent. The prior Qwen8B final-fit success and local baseline asset staging remain recorded in the [2026-11-11 continuation log](2026-11-11-host-continuation-poll.md).

Two read-only resource snapshots found no compute applications. GPU1 is the registered UUID `GPU-8a059266-7ede-0427-ff30-08ba7a9b5224`, with 172 MiB used and 31,929 MiB free; `MemAvailable` was 222,241,656 kB and the Kaggle filesystem had 7,032 GiB free. The prior stopped Candidate09 watcher PID `3748103` remains in `T` state. No active GPU runner or matching run lock was found.

Candidate14 OLMo2 was not started: its approved spec requires the preceding Host142 GPU1 job/watcher handles to be terminal; the stopped Candidate09 watcher is still a live process. No process was resumed or terminated, and no new run or Kaggle write/submission was started. Resume only after the queue handle is resolved under its registered procedure; recheck the rate guard, exact UUID, processes, lock, RAM, and disk immediately before a pilot.

## 01:51 JST — Host142 poll blocked by SSH host-key verification

- The scheduled one-command read-only poll to alias `142` failed before connecting with `Host key verification failed`.
- Read-only SSH config resolves alias `142` to `10.10.40.142`, user `aburatani`, port 22. `ssh-keygen -F` found no entry for either alias or IP in `/home/aburatani/.ssh/known_hosts`.
- No host-key check was bypassed, no process was touched, and no host state was inferred from this failed connection. Last confirmed state remains the 00:50 JST entry above. Do not start or stop jobs on Host142 until its host key is safely confirmed. Retry only at a later scheduled poll if the trust entry is restored.
