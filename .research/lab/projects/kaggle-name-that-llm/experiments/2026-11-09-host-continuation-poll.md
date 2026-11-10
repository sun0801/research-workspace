# Host continuation poll

## 2026-11-09 22:15 JST

`codex_rate_limit.py --guard 15` passed at 22:15:21 JST (5-hour remaining 87%, weekly 55%). This is a read-only poll under the README handoff policy; no stop request was given.

- **Host142 (`142-X10DAi`)**: Qwen3-8B confirmation PID `3871913` remains active at 100% CPU. GPU0 UUID `GPU-135ac6e4-8006-058e-ae74-0bb708d0f143` uses 15 MiB / 15,960 MiB free, 0%; GPU1 UUID `GPU-8a059266-7ede-0427-ff30-08ba7a9b5224` uses 15,834 / 16,266 MiB, 32%. `MemAvailable` is 216,719,392 kB. Registered waiters/watchers `137077`, `3605360`, `3652967`, `3708652`, `3743539`, and `3748103` remain alive. Confirmation fold 3 OOF/logits are still the latest artifacts (20:51:44 JST); fold 4 setup is logged at 20:51:45 JST, with no newer checkpoint or OOF.
- **Host141 (`141-X9DAi`)**: candidate11 PID `2439031` (100% CPU) and candidate13 PID `2448742` (114% CPU) remain active. GPU0/1/2 use/free are `1405/14568`, `15/15960`, and `8549/7426 MiB`, utilization `14%/0%/41%`; `MemAvailable` is 113,716,060 kB. Candidate11 latest saved OOF is fold 1 at 14:32:30 JST, with fold 2 setup logged at 14:32:34. Candidate13 latest saved OOF is fold 2 at 17:47:05, with fold 3 setup logged at 17:47:08. No newer checkpoint or OOF appeared.
- Three GPUs remain assigned to existing runs and two are idle. Resource floors pass. Keep all jobs and watchers running in their registered queue order; do not allocate the idle GPUs to an unregistered candidate. No host/job/watcher was stopped or restarted, and no Kaggle write or submission occurred.

The refreshed DateRun search listed `bgunshui/ntl-v673-b08` with a Nov 9 run time, while `get_notebook_info` reports Nov 6; its metadata lists 20 datasets, 9 upstream notebooks, and 8 model sources. This is a metadata-only lead with an unresolved timestamp discrepancy, not evidence of a new score or a reason to change the candidate queue.

## 2026-11-09 22:25 JST

Official Kaggle MCP refresh at 22:19–22:20 JST: team count `5235`; public leaderboard remains tied at `.752` (Le Viet, Meni David Gottesman), with next scores `.747`. Competition metadata reports Jan 14, 2027, while the official Timeline states Jan 13, 2027 at 23:59 UTC; keep the earlier date. Rules still allow five submissions/day and two final selections. Code Requirements remain Notebook-only, Internet disabled, <=9 hours, and `submission.parquet`. Evaluation confirms unequal per-model test counts and a different public/private mix. Score-sorted Notebook titles still top out at `.681`; titles and search results are not verified scores. Sources: [competition](https://www.kaggle.com/competitions/name-that-llm), [Timeline](https://www.kaggle.com/competitions/name-that-llm/overview/timeline), [Evaluation](https://www.kaggle.com/competitions/name-that-llm/overview/evaluation).

`--guard 15` passed at 22:25:24 JST (5-hour remaining 87%, weekly 55%). Read-only host poll: Host142 Qwen8B confirmation PID `3871913` remains at 100% CPU; GPU0/1 use/free `15/15960`, `15834/16266 MiB`, utilization `0%/29%`; MemAvailable `216750612 kB`. Watchers `137077`, `3605360`, `3652967`, `3708652`, `3743539`, and `3748103` remain alive. Fold4 remains active; no checkpoint/OOF since fold3 OOF at 20:51:44 JST and fold4 setup at 20:51:45.

Host141 candidates11/13 PIDs `2439031`/`2448742` remain CPU-active at 100%/114%; GPU0/1/2 use/free `1405/14568`, `15/15960`, `8549/7426 MiB`, utilization `14%/0%/46%`; MemAvailable `113718432 kB`. Candidate11 is processing fold2 after its fold1 OOF (14:32:30 JST); candidate13 is processing fold3 after its fold2 OOF (17:47:05). No new checkpoint/OOF since the prior poll. Three GPUs remain assigned and two are idle, but no registered candidate is configured for those idle UUIDs. Preserve queue order and all running jobs; no stop, restart, new allocation, Kaggle write, or submission.

## 2026-11-09 22:35 JST

`--guard 15` passed at 22:35:33 JST (5-hour remaining 86%, weekly 55%). The same Host142 runner `3871913` and all six registered waiters/watchers (`137077`, `3605360`, `3652967`, `3708652`, `3743539`, `3748103`) remain alive. GPU0/1 use/free are `15/15960` and `15834/16266 MiB`, utilization `0%/29%`, with `MemAvailable` 216,742,660 kB. Qwen8B confirmation remains on fold4; the fold3 OOF at 20:51:44 JST is still latest, with no checkpoint/OOF change.

Host141 runners `2439031`/`2448742` remain alive at 100%/114% CPU. GPU0/1/2 use/free remain `1405/14568`, `15/15960`, `8549/7426 MiB`, utilization `16%/0%/45%`; `MemAvailable` is 113,712,620 kB. Candidate11 fold2 and candidate13 fold3 are still active, with no new checkpoint/OOF since their previous fold setups at 14:32:34 and 17:47:08 JST. GPU/RAM floors remain satisfied. Preserve both hosts and the registered queue; no action beyond this verified wait.

## 2026-11-09 22:45 JST

Official Kaggle MCP at 22:37 JST reports `5,238` teams (up from 5,235); leaderboard remains tied at `.752`. Metadata deadline is Jan 14, while Timeline remains Jan 13, 2027 23:59 UTC; 5 submissions/day, 2 final selections, Notebook-only/offline/<=9 hours/`submission.parquet` remain unchanged.

`--guard 15` passed at 22:45:59 JST (5-hour remaining 86%, weekly 55%). Host142 Qwen8B PID `3871913` is still at 100% CPU; registered watcher PIDs remain alive. GPU0/1 use/free `15/15960`, `15834/16266 MiB`, utilization `0%/29%`; MemAvailable `216752268 kB`. Fold4 setup remains the latest Qwen8B log state (11:51:45 UTC / 20:51:45 JST); no checkpoint or OOF has advanced.

Host141 candidate11/13 PIDs `2439031`/`2448742` remain active at 100%/114% CPU. GPU0/1/2 use/free `1405/14568`, `15/15960`, `8549/7426 MiB`, utilization `17%/0%/39%`; MemAvailable `113717384 kB`. Candidate11 fold2 and candidate13 fold3 remain in progress after their last logged setup at 14:32:34 and 17:47:08 JST; no checkpoint/OOF changed. The same three GPUs remain assigned and two idle. Safety floors pass; retain all running jobs and candidate order. No stop/restart/new run/Kaggle write/submission.

## 2026-11-09 22:56 JST

`--guard 15` passed at 22:56:38 JST (5-hour remaining 85%, weekly 55%). Host142 Qwen8B confirmation PID `3871913` and registered watcher PIDs remain alive; GPU0/1 use/free `15/15960`, `15834/16266 MiB`, utilization `0%/22%`; MemAvailable `216713040 kB`. Fold4 remains active with no newer checkpoint/OOF since fold3 OOF at 20:51:44 JST.

Host141 candidate11 PID `2439031` is still active at 100% CPU. It saved fold2 Stage1 epoch-001 checkpoint at 22:51:44 JST (`state.pt` 151,969,451 bytes; 45,000 examples; mean loss `1.620958`; peak VRAM 8,213 MiB; MemAvailable 108.45 GiB; `stop_requested=false`). Fold2 OOF has not been written yet. Candidate13 PID `2448742` remains active at 114% CPU, still processing fold3 with no newer checkpoint/OOF since fold3 setup at 17:47:08. Host141 GPU0/1/2 use/free `1405/14568`, `15/15960`, `8549/7426 MiB`, utilization `15%/0%/38%`; MemAvailable `113961968 kB`. All safety floors pass. Continue both registered runs and preserve queue order; no stop/restart/new allocation/Kaggle write/submission.

## 2026-11-09 23:08 JST

`--guard 15` passed at 23:08:16 JST (5-hour remaining 85%, weekly 55%). Host142 Qwen8B confirmation PID `3871913` and all registered waiters/watchers remain alive; GPU0/1 use/free `15/15960`, `15834/16266 MiB`, utilization `0%/30%`, MemAvailable `216630712 kB`. Fold4 remains active with no new checkpoint/OOF.

Host141 candidate11 PID `2439031` remains active at 100% CPU; its fold2 Stage1 epoch-001 checkpoint from 22:51:44 JST remains latest and fold2 OOF is pending. Candidate13 PID `2448742` remains active at 114% CPU and saved fold3 Stage1 epoch-001 at 22:58:26 JST (`state.pt` 59,746,003 bytes; 45,000 examples; mean loss `1.731300`; peak VRAM 1,034 MiB; MemAvailable 108.72 GiB; `stop_requested=false`). Fold3 OOF remains pending. Host141 GPU0/1/2 use/free `1461/14512`, `15/15960`, `8549/7426 MiB`, utilization `15%/0%/44%`; MemAvailable `114252272 kB`. Candidate13 is assigned to GPU0, candidate11 to GPU2; GPU1 remains idle. Safety floors pass. Continue existing runs, do not reroute or start another job; no stop/restart/Kaggle write/submission.

## 2026-11-09 23:20 JST

`--guard 15` passed at 23:20:09 JST (5-hour remaining 85%, weekly 55%). Host142 Qwen8B confirmation PID `3871913` and registered watchers remain alive; GPU0/1 use/free `15/15960`, `15834/16266 MiB`, utilization `0%/31%`; MemAvailable `216761596 kB`. Fold4 remains active; no new checkpoint or OOF.

Official Kaggle MCP refresh at 23:20 JST reports `5,241` teams; public LB remains tied at `.752`. Metadata deadline remains Jan 14, while the official Timeline cutoff remains Jan 13, 2027 23:59 UTC; retain the earlier date. The 22:37 JST Rules/Code Requirements refresh still applies: five submissions/day, up to two finals, Notebook-only/offline/<=9 hours/`submission.parquet`.

Host141 candidate11/13 PIDs `2439031`/`2448742` remain active at 100%/114% CPU. Candidate11 fold2 Stage2 epoch-001 checkpoint saved at 23:15:20 JST (`state.pt` 151,969,451 bytes; 2,159 examples; mean loss `1.348187`; peak VRAM 8,213 MiB; MemAvailable 108.94 GiB; `stop_requested=false`). Candidate13 fold3 Stage2 epoch-001 checkpoint saved at 23:13:02 JST (`state.pt` 59,746,003 bytes; 2,159 examples; mean loss `1.477638`; peak VRAM 1,034 MiB; MemAvailable 108.99 GiB; `stop_requested=false`). Both fold OOFs are still pending. Host141 GPU0/1/2 use/free `1461/14512`, `15/15960`, `8549/7426 MiB`, utilization `14%/0%/46%`; MemAvailable `114244216 kB`. The three current GPU assignments and the two idle devices remain unchanged; safety floors pass. Preserve all running jobs and queue order; no stop/restart/reallocation/Kaggle write/submission.

## 2026-11-09 23:32 JST

`--guard 15` passed at 23:32:29 JST (5-hour remaining 84%, weekly 55%). Host142 Qwen8B confirmation PID `3871913` and its watcher chain remain alive; GPU0/1 use/free `15/15960`, `15834/16266 MiB`, utilization `0%/27%`; MemAvailable `216776164 kB`. Fold4 remains active, with no new checkpoint/OOF since fold3.

Host141 candidate11/13 PIDs `2439031`/`2448742` remain CPU-active at 100%/114%. Candidate11 fold2 Stage2 epoch-001 at 23:15:20 JST remains its newest checkpoint; fold2 OOF is pending. Candidate13 completed primary fold3 at 23:28:31 JST with fold BA `.524074`, then started fold4 setup at 23:28:32 JST. This is partial five-fold progress only; no adoption/rejection/bootstrap decision before the complete registered OOF. Candidate13 fold3 OOF/logits are present. Host141 GPU0/1/2 use/free `1405/14568`, `15/15960`, `8549/7426 MiB`, utilization `15%/0%/52%`; MemAvailable `113777448 kB`. Three GPUs remain assigned, two idle, and all resource floors pass. Preserve active runs and queue order; no stop/restart/reallocation/Kaggle write/submission.

## 2026-11-09 23:44 JST

`--guard 15` passed at 23:44:41 JST (5-hour remaining 84%, weekly 55%). Host142 Qwen8B confirmation PID `3871913` and its watcher chain remain alive; GPU0/1 use/free `15/15960`, `15834/16266 MiB`, utilization `0%/26%`; MemAvailable `216713076 kB`. Fold4 remains active with no new checkpoint/OOF.

Host141 candidate11/13 PIDs `2439031`/`2448742` remain active at 100%/114% CPU. Candidate11 completed fold2 at 23:40:05 JST with fold BA `.544444`, peak VRAM 8,213 MiB, and MemAvailable 108.95 GiB; its OOF/logits are present. From fold2 setup at 14:32:34 to OOF completion took about 9h07m. Fold3 setup is logged at 23:40:06 JST. This is partial five-fold progress only; no bootstrap/adoption decision before all folds. Candidate13 fold3 OOF remains latest (BA `.524074` at 23:28:31); from its fold3 setup at 17:47:08 to OOF completion took about 5h41m. Fold4 setup is logged at 23:28:32. Host141 GPU0/1/2 use/free `1405/14568`, `15/15960`, `8553/7422 MiB`, utilization `15%/0%/46%`; MemAvailable `113286292 kB`. Three GPUs remain assigned, two idle, and safety floors pass. Preserve both hosts and the registered queue; no stop/restart/reallocation/Kaggle write/submission.

## 2026-11-09 23:47 JST official refresh

Official Kaggle MCP reports `5,242` teams, up one since 23:20 JST; public leaderboard remains tied at `.752`. Metadata deadline is Jan 14, with Timeline's earlier Jan 13, 2027 23:59 UTC retained. The current rules/Code Requirements snapshot from 22:37 JST remains: 5 submissions/day, 2 final selections, Notebook-only, offline, <=9 hours, `submission.parquet`.

## 2026-11-09 23:56 JST

`--guard 15` passed at 23:56:16 JST after the five-hour reset (100% remaining, weekly 54%). Host142 Qwen8B confirmation PID `3871913` and all registered watchers remain alive; GPU0/1 use/free `15/15960`, `15834/16266 MiB`, utilization `0%/20%`; MemAvailable `216791280 kB`. Fold4 remains active with no new checkpoint/OOF since fold3.

Host141 PIDs `2439031`/`2448742` remain alive at 100%/114% CPU. Candidate11 fold2 OOF at 23:40:05 and fold3 setup at 23:40:06 remain latest; candidate13 fold3 OOF at 23:28:31 and fold4 setup at 23:28:32 remain latest. GPU0/1/2 use/free `1405/14568`, `15/15960`, `8553/7422 MiB`, utilization `17%/0%/45%`; MemAvailable `113318768 kB`. No checkpoint/OOF changed since the previous poll. Three GPUs remain assigned, two idle, resource floors pass. Continue the current runs and registered queue; no stop/restart/reallocation/Kaggle write/submission.
