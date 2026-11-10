# Host continuation poll

## 2026-11-10 00:06 JST

`codex_rate_limit.py --guard 15` passed at 00:06:26 JST after reset (5-hour remaining 99%, weekly 54%). The preserved CPU-best model still matches SHA-256 `ea73912adcdec42b25e3b785c211c7a8e64a8ee49b3ac35f776e9aa48f8af7a5`.

Official Kaggle MCP reports 5,242 teams, with Le Viet and Meni David Gottesman tied at public BA `.752`. Metadata says Jan 14, 2027, while Timeline specifies Jan 13 at 23:59 UTC; keep Jan 13 as the conservative deadline. Rules allow five submissions/day and up to two final selections. Code Requirements remain Notebook-only, Internet disabled, <=9 hours, output `submission.parquet`. Evaluation confirms unequal per-model test counts and a different public/private mix. Sources: [competition](https://www.kaggle.com/competitions/name-that-llm), [Timeline](https://www.kaggle.com/competitions/name-that-llm/overview/timeline), [Rules](https://www.kaggle.com/competitions/name-that-llm/rules), [Evaluation](https://www.kaggle.com/competitions/name-that-llm/overview/evaluation), [Code Requirements](https://www.kaggle.com/competitions/name-that-llm/overview/code-requirements).

### Host142 (`142-X10DAi`)

Qwen8B confirmation PID `3871913` and watcher chain PIDs `137077`, `3605360`, `3652967`, `3708652`, `3743539`, `3748103` remain alive. GPU0/1 use/free `15/15960`, `15834/16266 MiB`, utilization `0%/21%`; `MemAvailable` is 216,755,188 kB. Fold4 remains active with no newer checkpoint/OOF since fold3 OOF at Nov 9 20:51:44 JST and fold4 setup at 20:51:45.

### Host141 (`141-X9DAi`)

Candidate11/13 PIDs `2439031`/`2448742` remain active at 100%/114% CPU. Candidate11 fold2 OOF BA is `.544444` (completed 23:40:05); fold3 setup is the latest log position. Candidate13 fold3 OOF BA is `.524074` (completed 23:28:31); fold4 setup is the latest log position. These remain partial five-fold results; adoption gates are not evaluated yet. GPU0/1/2 use/free `1405/14568`, `15/15960`, `8553/7422 MiB`, utilization `14%/0%/44%`; `MemAvailable` is 113,332,040 kB.

Three GPUs remain assigned to these registered runs and two are idle. Resource floors pass. Preserve existing runs and queue order; no host/job/watcher stop, restart, reallocation, Kaggle write, or submission.

## 2026-11-10 00:16 JST

`codex_rate_limit.py --guard 15` passed at 00:16:14 JST (5-hour remaining 98%, weekly 54%). Read-only polling confirms all registered jobs remain active; no stop instruction was issued.

### Host142 (`142-X10DAi`)

Qwen8B confirmation PID `3871913` is alive at 100% CPU; watcher chain PIDs `137077`, `3605360`, `3652967`, `3708652`, `3743539`, `3748103` remains alive. GPU0/1 use/free `15/15960`, `15834/16266 MiB`, utilization `0%/28%`; `MemAvailable` is 221,962,678,272 bytes. Confirmation fold3 OOF BA `.571073` completed at Nov 9 20:51:44 JST; fold4 setup is the latest log position, with no newer checkpoint/OOF yet.

### Host141 (`141-X9DAi`)

Candidate11/13 PIDs `2439031`/`2448742` remain alive at 100%/114% CPU. Candidate11 fold2 OOF BA `.544444` completed at Nov 9 23:40:05 JST and fold3 remains active. Candidate13 fold3 OOF BA `.524074` completed at Nov 9 23:28:31 JST and fold4 remains active. GPU0/1/2 use/free `1405/14568`, `15/15960`, `8553/7422 MiB`, utilization `14%/0%/47%`; `MemAvailable` is 116,011,823,104 bytes. These are still partial five-fold results and do not meet adoption gates.

Host142 GPU0 and Host141 GPU1 are idle, while the other three GPUs are assigned to registered runs. Resource floors pass. Keep the current jobs and queue unchanged; no stop, restart, reallocation, Kaggle write, or submission.

## Official Kaggle refresh — 2026-11-10 00:18 JST

Official MCP still reports 5,242 teams. Public leaderboard top is Le Viet and Meni David Gottesman tied at `.752`; next entries are `.747`. Competition metadata deadline is Jan 14, 2027, while Timeline explicitly sets Jan 13, 2027 at 23:59 UTC; use the earlier date. Rules say five submissions/day and up to two final submissions. Code Requirements remain Notebook-only, Internet disabled, <=9 hours, and `submission.parquet`. Evaluation says per-model test counts are unequal and public/private mixes differ. The Data Description says interactive `test.csv` contains three example rows, while Evaluation says one example row; both say hidden rerun is about 4,000 passages. Keep this wording discrepancy and the unequal-count constraint visible when considering test-set postprocessing. Score-descending Notebook search still tops at a `.681` title, with no verified score above the official `.752` leader. Recent Qwen embedding + LR + Sinkhorn source audit found an equal-18-class-per-inferred-cluster assumption and non-nested OOF tuning; details in [audit](2026-11-10-handeakn-embedding-sinkhorn-audit.md). No candidate order, job, or submission changed.

## 2026-11-10 00:26 JST

The rate guard passed at 00:26:15 JST (5-hour remaining 97%, weekly 54%). Host142 `142-X10DAi` still has Qwen8B confirmation PID `3871913` alive at 100% CPU and its registered watcher chain alive. GPU0/1 use/free are `15/15960` and `15834/16266 MiB`, utilization `0%/22%`; `MemAvailable` is 221,912,711,168 bytes. No new confirmation checkpoint/OOF since the fold3 OOF at Nov 9 20:51:44 JST; fold4 remains active.

Host141 `141-X9DAi` still has candidate11/13 PIDs `2439031`/`2448742` alive at 100%/114% CPU. GPU0/1/2 use/free are `1405/14568`, `15/15960`, `8553/7422 MiB`, utilization `15%/0%/47%`; `MemAvailable` is 116,066,336,768 bytes. No artifact changed since 00:16: candidate11 fold2 OOF BA `.544444` is its latest result and fold3 remains active; candidate13 fold3 OOF BA `.524074` is its latest result and fold4 remains active. Both are partial five-fold results; no adoption decision is made.

Three GPUs remain allocated to those registered runs; Host142 GPU0 and Host141 GPU1 remain idle. Resource floors pass. Keep all active jobs and registered order intact; no stop, restart, reallocation, Kaggle write, or submission.

## Official Kaggle refresh — 2026-11-10 00:32 JST

Official MCP refresh found no change: team count 5,242; public leaders Le Viet and Meni David Gottesman tied at `.752`, next `.747`; metric balanced accuracy; daily cap five; Notebook-only / Internet-off / <=9 hours / `submission.parquet`. Metadata still lists Jan 14, while Timeline's final deadline is Jan 13, 2027 at 23:59 UTC, so keep Jan 13. Evaluation still warns test model counts and public/private mixes are unequal. No leaderboard evidence exceeds `.752`; no submission made.

## 2026-11-10 00:36 JST

At 00:36, `--guard 15` remained green from 00:32:39 (5-hour 96%, weekly 54%). Host142 Qwen8B confirmation PID `3871913` is alive and CPU-active; registered watcher PIDs `137077`, `3605360`, `3652967`, `3708652`, `3743539`, `3748103` remain alive. GPU0/1 use/free `15/15960`, `15834/16266 MiB`, utilization `0%/25%`; `MemAvailable` is 221,918,146,560 bytes. Fold4 remains active, with no new checkpoint/OOF since fold3 OOF at Nov 9 20:51:44 JST.

Host141 candidate11/13 PIDs `2439031`/`2448742` remain alive and CPU-active at 100%/114%. GPU0/1/2 use/free `1405/14568`, `15/15960`, `8553/7422 MiB`, utilization `14%/0%/39%`; `MemAvailable` is 116,045,516,800 bytes. Candidate11 fold3 and candidate13 fold4 remain active; latest OOFs are candidate11 fold2 BA `.544444` and candidate13 fold3 BA `.524074`, with no new checkpoint/OOF since 00:26.

Three GPUs remain assigned to registered runs; Host142 GPU0 and Host141 GPU1 are idle. Memory/VRAM floors pass. The elapsed portions of the active folds remain shorter than their previously observed fold runtimes. Continue all current jobs/queue without restart or reallocation; no Kaggle write/submission.

## Public Notebook search — 2026-11-10 00:37 JST

Kaggle MCP DateRun search produced no run newer than the Nov 9 15:11 UTC `muhammadasjad2008/ntl-v1-baseline`; the reviewed Qwen embedding/Sinkhorn and `.681` leads remain next in its list. ScoreDescending still tops at the `.681` Qwen3-Embedding + Qwen3.8-27B title. These are discovery metadata/title claims, not score verification; no public Notebook evidence above the official `.752` leader and no queue change.

## 2026-11-10 00:47 JST

Host polls were run read-only after the 00:46 minimum interval. Host142 `142-X10DAi` confirmation PID `3871913` remains alive at 100% CPU; watcher PIDs `137077`, `3605360`, `3652967`, `3708652`, `3743539`, and `3748103` remain alive. GPU0/1 use/free are `15/15960` and `15834/16266 MiB`, utilization `0%/27%`; `MemAvailable` is 216,718,400 kB. No newer OOF/checkpoint than fold3 OOF at Nov 9 20:51:44 and fold3 stage2 epoch-002 checkpoint at 20:50:43; confirmation fold4 remains active.

Host141 `141-X9DAi` candidate11 PID `2439031` and candidate13 PID `2448742` remain alive at 100%/114% CPU. GPU0/1/2 use/free are `1405/14568`, `15/15960`, and `8553/7422 MiB`, utilization `17%/0%/41%`; `MemAvailable` is 113,350,484 kB. No new artifacts since the 00:26 poll: candidate11 fold2 OOF remains the latest, with fold3 active; candidate13 fold3 OOF remains the latest, with fold4 active. The latest saved candidate11 checkpoint is fold2 stage2 epoch-002 (Nov 9 23:38:42); candidate13 is fold3 stage2 epoch-002 (Nov 9 23:27:44).

Three GPUs remain assigned to registered jobs; Host142 GPU0 and Host141 GPU1 remain idle. Resource floors pass, and the active folds remain within prior observed fold-duration ranges. Continue existing jobs and queue; no stop, restart, reallocation, Kaggle write, or submission.

## Official refresh and queue inspection — 2026-11-10 00:50 JST

Official Kaggle MCP reports 5,243 teams. The top public leaderboard remains Le Viet and Meni David Gottesman tied at `.752`; next scores are `.747`. Rules continue to allow five submissions/day and two final selections; Timeline sets Jan 13, 2027 at 23:59 UTC, earlier than metadata's Jan 14 date. Submission remains Notebook-only, Internet-disabled, <=9 hours, `submission.parquet`; test model counts and public/private mixtures differ. DateRun search still has no notebook run newer than Nov 9 15:11 UTC (`muhammadasjad2008/ntl-v1-baseline`); score-descending Notebook titles still top at `.681`, with no verified score above `.752`.

The `candidate08-gpu1-pilot-watcher.sh` (PID `3652967`) is alive and intentionally waits for registered watcher PID `3605360`. That watcher owns Qwen8B confirmation PID `3871913` on Host142 GPU1 and proceeds to the preregistered blend confirmation; candidate08's watcher will continue its queue after that dependency exits. The existing chain is live, so do not bypass it or launch a competing GPU1 job. Host141 candidate11/13 and Host142 confirmation remain untouched; no Kaggle write/submission.

## 2026-11-10 00:57 JST

The next scheduled read-only poll confirms Host142 Qwen8B confirmation PID `3871913` remains alive at 100% CPU; watcher PIDs `3605360`, `3652967`, `3708652`, `3743539`, and `3748103` are also alive. GPU0/1 use/free are `15/15960` and `15834/16266 MiB`, utilization `0%/21%`; `MemAvailable` is 216,680,016 kB. No new confirmation artifact since fold3 OOF at Nov 9 20:51:44 and fold3 stage2 epoch-002 checkpoint at 20:50:43; fold4 continues.

Host141 candidate11 PID `2439031` and candidate13 PID `2448742` remain alive at 100%/114% CPU. GPU0/1/2 use/free are `1405/14568`, `15/15960`, and `8553/7422 MiB`, utilization `17%/0%/51%`; `MemAvailable` is 113,309,712 kB. No new artifacts since 00:47: candidate11 fold2 OOF and fold2 stage2 epoch-002 checkpoint remain latest; fold3 continues. Candidate13 fold3 OOF and fold3 stage2 epoch-002 remain latest; fold4 continues.

Three GPUs remain assigned to registered runs and two remain idle. Resource floors pass. Candidate08 GPU1 pilot watcher PID `3652967` remains queued behind watcher PID `3605360`; preserve the registered dependency order. No stop, restart, reallocation, Kaggle write, or submission.

## CPU baseline preservation — 2026-11-10 01:00 JST

Read-only recheck confirms `artifacts/2026-11-06-cpu-cycle/09-05-function-view-candidate/model.joblib` still exists (9,971,269 bytes) with SHA-256 `ea73912adcdec42b25e3b785c211c7a8e64a8ee49b3ac35f776e9aa48f8af7a5`, matching the recorded CPU-best hash. No artifact was modified.

## Official status and new-discussion triage — 2026-11-10 01:00 JST

Official Kaggle MCP refresh remains at 5,243 teams, with Le Viet and Meni David Gottesman tied at public BA `.752`; the next entries score `.747`. Rules still permit five submissions/day and two final selections. Timeline specifies Jan 13, 2027 at 23:59 UTC (earlier than metadata's Jan 14); the submission remains Notebook-only, Internet-disabled, <=9 hours, `submission.parquet`. Evaluation still warns that model counts and public/private mixes differ.

Recent Discussion 757303 (Nov 9) reports a participant's transformer ensemble at public `.673` and a lightweight CatBoost/LightGBM/XGBoost/TF-IDF stack at `.336`; this is an unsupported participant report without code or OOF and gives no competitive CatBoost candidate. Discussion 757199's last reply is unchanged from the earlier GLM feasibility audit and adds no working inference recipe or new model source. Preserve the prior decisions and current queue; no Kaggle write/submission.

## 2026-11-10 01:08 JST

`--guard 15` passed at 01:08:10 JST (5-hour remaining 93%, weekly 53%). Host142 Qwen8B confirmation PID `3871913` remains alive at 100% CPU; registered watcher PIDs `3605360`, `3652967`, `3708652`, `3743539`, and `3748103` remain alive. GPU0/1 use/free are `15/15960` and `15834/16266 MiB`, utilization `0%/23%`; `MemAvailable` is 216,693,952 kB. No new confirmation artifact since fold3 OOF (Nov 9 20:51:44) and fold3 stage2 epoch-002 checkpoint (20:50:43); fold4 continues.

Host141 candidate11 PID `2439031` and candidate13 PID `2448742` remain alive at 100%/114% CPU. GPU0/1/2 use/free are `1405/14568`, `15/15960`, and `8553/7422 MiB`, utilization `16%/0%/39%`; `MemAvailable` is 113,335,436 kB. No new output since 00:57: candidate11 fold2 OOF/checkpoint (fold3 active) and candidate13 fold3 OOF/checkpoint (fold4 active) remain latest. Elapsed time in these folds is shorter than prior measured fold durations.

Three GPUs remain assigned to registered experiments; Host142 GPU0 and Host141 GPU1 remain idle. All resource floors pass. Candidate08's pilot watcher remains queued behind watcher PID `3605360`; preserve the dependency order. No stop, restart, reallocation, Kaggle write, or submission.

## Kaggle search refresh — 2026-11-10 01:13 JST

Official MCP remains at 5,243 teams, with public top `.752` tied by Le Viet and Meni David Gottesman, followed by `.747`. Deadline/rules remain unchanged: Jan 13, 2027 23:59 UTC on Timeline; five submissions/day, two finals, Notebook-only, Internet disabled, <=9 hours, and `submission.parquet`.

DateRun Notebook search's latest item is `xiangqizhang/ntl-0681-frontier` at Nov 9 14:55:28 UTC; no title or result exceeds the official `.752` top. A competition-filtered Notebook search by the `.673`/`.336` Discussion author `maxxakela` returned no kernels, so the transformer claim still has no publicly discoverable implementation through that author query. This search is limited evidence and does not prove that no alternate account copy exists; no candidate or queue change.

## 2026-11-10 01:18 JST

`--guard 15` passed at 01:18:21 (5-hour remaining 92%, weekly 53%). Host142 Qwen8B confirmation PID `3871913` is alive at 100% CPU; watchers `3605360`, `3652967`, `3708652`, `3743539`, `3748103` are alive. GPU0/1 use/free are `15/15960` and `15834/16266 MiB`, utilization `0%/29%`; `MemAvailable` is 216,593,388 kB. The correct runner log is `artifacts/gpu02-qwen3-8b-posttrained-openpool-v15/confirmation-run.log`: fold4 setup is Nov 9 20:51:45 JST and model loading completed at 20:51:46, with no later stage1 checkpoint yet. The prior fold's stage1 took about 7h02, followed by about 43 minutes for stage2 and OOF; current fold has run about 4h27, within that measured stage1 interval.

Host141 candidate11 PID `2439031` and candidate13 PID `2448742` remain alive at 100%/114% CPU. GPU0/1/2 use/free are `1405/14568`, `15/15960`, `8553/7422 MiB`, utilization `16%/0%/45%`; `MemAvailable` is 113,318,012 kB. No new output since 01:08: candidate11 remains in fold3 after fold2 OOF `.544444` and fold2 stage2 epoch-002 checkpoint; candidate13 remains in fold4 after fold3 OOF `.524074` and fold3 stage2 epoch-002. Both remain within previously measured fold durations.

Three GPUs remain assigned; Host142 GPU0 and Host141 GPU1 are idle. Resource floors pass. Candidate08 watcher remains queued behind the registered Qwen confirmation/blend chain; preserve it. No stop, restart, reallocation, Kaggle write, or submission.

## 2026-11-10 01:29 JST

The rate guard passed at 01:24:17 JST (5-hour remaining 91%, weekly 53%). I reread the README's `共同作業の引き継ぎ`: only use a host when it is actually free; a “141を止めて” or “142を止めて” request applies only to that named host and requires saving outputs/resume position, stopping its Kaggle jobs and auto-submit/relaunch chain, and verifying watcher absence and GPU release. The other host continues, and a stopped host stays unavailable until explicit reuse authorization. This is not a stop request.

Host141 (`141-X9DAi`) was confirmed read-only at 01:29:01. Candidate11 PID `2439031` and candidate13 PID `2448742` remain CPU-active at 100%/114%. GPU0/1/2 use/free are `1405/14568`, `15/15960`, and `8553/7422 MiB`; utilization is `15%/0%/39%`, and `MemAvailable` is `113296976 kB`. Candidate11's latest OOF/checkpoint is fold2 stage2 epoch-002 (23:40:05 JST); fold3 remains in progress. Candidate13's latest OOF/checkpoint is fold3 stage2 epoch-002 (23:27:44 JST); fold4 remains in progress. Both folds are within their previously observed runtime ranges.

Host142 could not be re-polled because SSH host-key verification failed. Do not bypass verification or treat it as available; the last verified 01:18 snapshot had Qwen8B confirmation PID `3871913` and its watcher chain active on GPU1. Host141 is active, and Host142 is not verified empty, so no new Kaggle run is started. Existing Host141 jobs and registered Host142/candidate08 queue are left untouched; no stop, restart, reallocation, Kaggle write, or submission.

## Official competition and public Notebook refresh — 2026-11-10 01:34 JST

Official Kaggle MCP reports 5,243 teams and public leaders Le Viet and Meni David Gottesman tied at balanced accuracy `.752`, followed by `.747`. `Timeline` sets the final deadline to Jan 13, 2027 at 23:59 UTC, earlier than competition metadata's Jan 14 timestamp. Rules still permit five submissions per day and two final selections. Code Requirements remain Notebook-only, Internet disabled, <=9 hours, with `submission.parquet`; Evaluation says per-model test counts and public/private mixes differ. The score-descending Notebook results still top at a `.681` title claim. DateRun's newest indexed result remains `xiangqizhang/ntl-0681-frontier` at Nov 9 14:55:28 UTC; search timestamps are discovery metadata, not verified LB evidence. No Notebook evidence above the `.752` official leader was found.

The preserved CPU-best model remains unchanged at 9,971,269 bytes, SHA-256 `ea73912adcdec42b25e3b785c211c7a8e64a8ee49b3ac35f776e9aa48f8af7a5`. Current registered execution remains the next candidate work: let Host141 candidate11/13 complete, preserve the Host142 Qwen8B confirmation/blend dependency, then continue the registered candidate08 watcher queue. No new candidate is selected while registered GPU work is active and Host142 cannot be safely re-polled.

## 2026-11-10 01:39 JST

`--guard 15` passed at 01:39:56 JST (5-hour remaining 91%, weekly 53%). Read-only Host141 poll at 01:39:30 confirms candidate11 PID `2439031` and candidate13 PID `2448742` are still active at 100%/114% CPU. GPU0/1/2 use/free remain `1405/14568`, `15/15960`, `8553/7422 MiB`, utilization `16%/0%/34%`; `MemAvailable` is `113337168 kB`. Latest output is unchanged: candidate11 fold2 OOF BA `.544444` and stage2 epoch-002 checkpoint at 23:40:05 JST, with fold3 active since 23:40:06; candidate13 fold3 OOF BA `.524074` and stage2 epoch-002 checkpoint at 23:28:31, with fold4 active since 23:28:32. Both active folds remain within their earlier measured runtime ranges.

Host142 remains unverified because no trusted host-key fingerprint is present for its configured aliases. The last verified 01:18 snapshot had confirmation PID `3871913` and registered watchers active. Do not accept an unverified key or treat Host142 as free. Host141 has active jobs, so no new GPU work is eligible under the host-availability instruction. Preserve current processes and the registered Host142/candidate08 queue; no stop, restart, reallocation, Kaggle write, or submission.

## Official status recheck — 2026-11-10 01:44 JST

Official Kaggle MCP now reports 5,242 teams, one fewer than the 01:34 response. Public leaderboard scores are unchanged: Le Viet and Meni David Gottesman tie at `.752`, followed by `.747`. Competition metadata still says Jan 14, 2027 at 23:59 UTC, while Timeline explicitly sets Jan 13 at 23:59 UTC; continue using the earlier Timeline date. The same current official response confirms five submissions/day and up to two final selections. The Code Requirements read shortly before this refresh remain Notebook-only, Internet-disabled, <=9 hours, and `submission.parquet`. New-sorted discussion search has no post-Nov-9 topic; no new evidence changes candidate priority or queue.

## Host142 key observation — 2026-11-10 01:45 JST

Read-only `ssh-keyscan` returned ED25519 fingerprint `SHA256:/eihdJOcW8jNvSL9x9j9QW2Mt5C9TnyhEwLQom2ZCww`, matching a prior observation in the Nov 6 initial-check log. Both observations are still untrusted and do not authenticate the host; the fingerprint was not written to `known_hosts`, and no command was run on Host142. Continue to require a trusted host-key source before remote access.

## 2026-11-10 01:50 JST

`--guard 15` passed at 01:49:48 JST (5-hour remaining 90%, weekly 53%). Host141 poll at 01:50 confirms candidate11 PID `2439031` and candidate13 PID `2448742` remain active at 100%/114% CPU. GPU0/1/2 use/free are `1405/14568`, `15/15960`, `8553/7422 MiB`, utilization `15%/0%/46%`; `MemAvailable` is `113350672 kB`. There is no new checkpoint or OOF since the prior poll: candidate11 remains in fold3 after fold2 OOF BA `.544444` and candidate13 remains in fold4 after fold3 OOF BA `.524074`. Both folds are still inside prior measured runtime ranges; resource floors pass.

Host142 is not considered free: latest verified state remains 01:18, with Qwen8B confirmation and registered watcher chain active. The observed SSH fingerprint remains untrusted. Host141 has active jobs. Preserve all current runs and the candidate08 dependency queue; no stop, restart, new allocation, Kaggle write, or submission.

## 2026-11-10 02:00 JST

`--guard 15` passed at 02:00:10 JST (5-hour remaining 89%, weekly 53%). Host141 poll at 02:00:22 confirms candidate11 PID `2439031` and candidate13 PID `2448742` remain alive at 100%/114% CPU. GPU0/1/2 use/free are `1405/14568`, `15/15960`, and `8553/7422 MiB`, utilization `15%/0%/38%`; `MemAvailable` is `113335780 kB`. No new checkpoint or OOF since 01:50: candidate11 stays in fold3 after fold2 OOF BA `.544444`, and candidate13 stays in fold4 after fold3 OOF BA `.524074`. Active-fold elapsed times remain inside the prior measured ranges; resource floors pass.

Host142 remains unverified and must not be treated as free; latest trusted process state is the 01:18 Qwen8B confirmation/watcher snapshot. Host141 jobs are active, so do not start another candidate or allocate its idle GPU1 under the host availability instruction. Preserve registered runs and queue; no stop, restart, reallocation, Kaggle write, or submission.

## 2026-11-10 02:10 JST — Host141 CPU evaluation readiness

The same read-only Host141 inspection confirms `src/gpu_analyze.py`, `data/train.csv`, and the adopted SVC baseline OOF (`artifacts/cpu-openpool-prompt-centered-low-pool-weight-v15/primary/oof-all.parquet`) are present. The expected early CPU and current Qwen+SVC blend OOF paths are absent there. Candidate11/13 primary OOFs remain partial; no analyzer ran. A fallback evaluation plan is recorded in [OOF comparator readiness](2026-11-10-oof-comparator-readiness.md); it requires locating or transferring only missing prediction OOF files from a trusted source before the three comparisons can run on Host141 CPU.

## Next validation priority — 2026-11-10 02:04 JST

The next candidate decision remains the frozen Spectral cluster mean-field correction's independent confirmation, not another hyperparameter search. Its completed primary result is BA `.664952` vs the adopted blend `.586408` (delta `+.078543`, 5,000 prompt-cluster bootstrap 95% CI `[+.065968,+.090741]`) and both predeclared unequal-retention simulations improved in 20/20 replicates. The approved spec permits only the same fixed transform and simulations on the independent Qwen+SVC blend-confirmation OOF; do not tune on that confirmation. Candidate08's public evidence still does not verify a score above `.752`, and its watcher stays in the existing queue. First complete current registered runs and preserve watcher dependencies; neither Host141's active jobs nor Host142's unverified state permits a new allocation now.

## 2026-11-10 02:21 JST

`--guard 15` passed at 02:20:59 JST (5-hour remaining 87%, weekly 52%). Official Kaggle MCP reports 5,244 teams; public top remains Le Viet and Meni David Gottesman tied at `.752`, next `.747`. Metadata still says Jan 14, 2027; Timeline specifies Jan 13 at 23:59 UTC. Rules remain five submissions/day, two final selections, Notebook-only, Internet disabled, <=9 hours, `submission.parquet`.

Host141 poll at 02:21:17 confirms candidate11 PID `2439031` and candidate13 PID `2448742` alive at 100%/114% CPU. GPU0/1/2 use/free are `1405/14568`, `15/15960`, `8553/7422 MiB`, utilization `15%/0%/48%`; `MemAvailable` is `113328788 kB`. No new checkpoint/OOF since 02:10; candidate11 remains in fold3 after fold2 BA `.544444`, and candidate13 in fold4 after fold3 BA `.524074`. The two active folds remain within the previously observed duration range; resource floors pass.

The same poll confirmed on Host141 that `src/gpu_analyze.py`, official `data/train.csv`, and adopted SVC primary OOF are present. A search for OOF artifacts found no early-CPU or Qwen+SVC blend OOF on this host; there are no full candidate OOFs yet. No analysis ran. Host142 remains unauthenticated; its 01:18 Qwen8B confirmation/watcher snapshot is the last trusted state.

New public source review: the latest DateRun result is `muhammadasjad2008/ntl-v1-baseline` (`NTL v1 baseline`), indexed at Nov 9 17:12:44 UTC. `get_notebook_info` instead reports current version 32, last run Nov 6 17:15 UTC; session status is `CANCEL_REQUESTED`. The title claims 0.742+, but the official leader remains `.752`. The notebook claims DeBERTa-v3-Large OOF about `.747`; its linked dependency dataset describes a single final DeBERTa asset trained on all competition train rows and reports standalone `.546`, with no fold-specific weights. The source does not reproduce that OOF claim. Full review, the author's noisiness caveats, and the related Discussion 753177's weak/selective m=2 correlation evidence are in [Jaime Oliver notebook review](2026-11-10-jaime-oliver-deberta-0742-notebook-review.md). DeBERTa remains a later fold-by-fold replication lead; current next validation stays the frozen Spectral confirmation. No run, queue, Kaggle object, or submission changed.

## 2026-11-10 02:24 JST — handoff policy and local comparator readiness

Re-read the README's "共同作業の引き継ぎ" and apply the user's host-scoped rule: a stop request for 141 or 142 saves that host's intermediate results and exact resume point, stops its Kaggle jobs and auto-injection/watchers, and verifies GPU release; the other host continues, and the stopped host stays reserved until explicit reuse. This is not a stop request: preserve the current runs and queue. Host141 candidate11/13 are active; Host142 is not considered free because its last trusted process snapshot is 01:18 and its SSH identity remains unconfirmed.

Local read-only checks found the implementation checkout's analyzer, official train file, virtualenv Python, and all three complete comparison baselines (early CPU, adopted SVC, current Qwen+SVC blend). After either Host141 candidate finishes all five primary folds, stage only those five prediction OOFs under `/tmp` and run the existing analyzer locally, one baseline per invocation, preserving each output before the next. No candidate artifacts were transferred or evaluated yet; no GPU, Kaggle object, or submission changed. See [OOF comparator readiness](2026-11-10-oof-comparator-readiness.md).

## 2026-11-10 02:31 JST — registered runs still active

Fresh `--guard 15` at 02:27:07 passed (5-hour remaining 86%, weekly 52%). Official Kaggle MCP refresh reports 5,245 teams; public top remains Le Viet and Meni David Gottesman tied at `.752`, next `.747`. The current competition pages still specify balanced accuracy, five submissions/day, up to two final selections, Notebook-only, Internet disabled, <=9 hours, and `submission.parquet`; Timeline remains Jan 13, 2027 at 23:59 UTC (metadata says Jan 14). Public Notebook search found no title-score claim above `.681`; a newly indexed `.680` fusion notebook reports session `RUNNING` with no session output, so it provides no new verified score or candidate evidence.

Host141 read-only poll at 02:31 confirms `141-X9DAi` runners PID `2439031` (candidate11, GPU2) and `2448742` (candidate13, GPU0) remain alive. Candidate11's latest full fold is fold2 BA `.544444`; fold3 is active. Candidate13's latest full fold is fold3 BA `.524074`; fold4 is active. There is no new OOF/checkpoint since the 02:21 poll. GPU0/1/2 use/free are `1405/14568`, `15/15960`, `8553/7422 MiB`, utilization `17%/0%/49%`; `MemAvailable` is `113357140 kB`. Both active folds and resource floors remain within expected limits. Host142 is still not considered free: its last trusted process snapshot is 01:18 and its SSH identity remains unconfirmed. Keep both current runs/queues intact; no new GPU allocation, stop/restart, Kaggle write, or submission.

CPU-best preservation remains verified: `09-05-function-view-candidate/model.joblib` is 9,971,269 bytes with SHA-256 `ea73912adcdec42b25e3b785c211c7a8e64a8ee49b3ac35f776e9aa48f8af7a5`.

## 2026-11-10 02:41 JST — active-fold poll

Official MCP recheck at 02:39 JST is unchanged: team_count 5,245, leaderboard `.752/.752/.747`, balanced accuracy, daily limit 5 and final limit 2. Timeline gives Jan 13, 2027 23:59 UTC; metadata's Jan 14 remains the later conflicting date. Code Requirements remain Notebook-only, Internet disabled, <=9h, `submission.parquet`. The current 02:38:47 guard remains valid (5h 86%, weekly 52%).

Host141 `141-X9DAi` was polled at 02:41:45 UTC. Runner and `flock` wrapper PIDs `2439031`/`2439029` (candidate11, GPU2) and `2448742`/`2448740` (candidate13, GPU0) remain alive. Candidate11's fold3 has been active since 14:40:06 UTC; the previous fold took about 9h and its current fold remains within that observed runtime. Candidate13's fold4 has been active since 14:28:32 UTC; its previous fold took about 5h41 and the current fold remains within range. Both main PIDs show CPU activity. No new OOF or checkpoint has appeared since 02:31 JST. Latest completed primary folds remain candidate11 fold2 BA `.544444` and candidate13 fold3 BA `.524074`.

GPU0/1/2 use/free are `1405/14568`, `15/15960`, `8553/7422 MiB`, utilization `15%/0%/53%`; `MemAvailable` is `113325476 kB`. Resource floors pass. Host142 remains unverified and is not free; Host141 has active jobs, so no new allocation. Preserve both jobs and queues without stop/restart. Existing CPU best and the three local comparator baselines remain intact; no OOF transfer or analyzer run until a candidate's complete five-fold primary OOF exists.
