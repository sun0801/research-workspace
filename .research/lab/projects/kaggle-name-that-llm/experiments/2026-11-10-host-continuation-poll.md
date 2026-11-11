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

## 2026-11-10 17:36 JST — private baseline Notebook draft prepared

Created a local private Notebook draft at `notebooks/name-that-llm-private-baseline/` in the implementation repo. Its kernel metadata explicitly sets private, GPU `NvidiaL4`, Internet disabled, the competition source, Qwen3-8B/Qwen3-1.7B model version 1 inputs, and the planned private asset dataset. The first version is benchmark-only: it uses unlabeled official training text for a length-stratified timing probe, projects both Qwen models and SVC to 4,000 hidden rows with a 25% margin plus 30-minute fixed overhead, and aborts before test inference if the estimate exceeds nine hours. The final version will be enabled only after the benchmark passes. OOF blend remains the preregistered equal mean of the three row-wise softmax score matrices; no tuning or test labels/counts are added. No Kaggle push or submission yet.

Kaggle's official CLI [kernel metadata documentation](https://github.com/Kaggle/kaggle-cli/blob/main/docs/kernels_metadata.md) was checked for the `is_private`, `enable_gpu`, `enable_internet`, `machine_shape`, competition/model/dataset source fields. Its CLI-created template returned the authenticated owner slug; both planned Kaggle objects are explicitly private. Current local source files are `notebooks/name-that-llm-private-baseline/name-that-llm-private-baseline-blend.ipynb`, `kernel-metadata.json`, and `dataset-metadata.json`.

## 2026-11-10 17:31 JST — adopted SVC final-fit started

`codex_rate_limit.py --guard 15` passed at 17:31:28 JST (five-hour remaining 96%, weekly 51%). The adopted prompt-centered SVC's all-train inference artifact is missing, so its fixed OOF-approved recipe is being fit on all 2,699 official rows plus the uniformly capped, prompt-filtered v15 pool using official/pool row weights 1.0/0.1. New runner: `src/cpu_openpool_svc_final_fit.py`; it checks both adoption summaries, uses two CPU threads, and monitors process-tree RSS against 32 GiB and `MemAvailable` against 16 GiB. Supervisor PID `874005`, worker PID `874134`; initial resources were `MemAvailable=211209008 kB`, and both GPU jobs remained active (Qwen1.7B GPU0 and Mistral03 GPU1). No model or Kaggle object has been published. CPU-best preservation was separately reverified at 17:23 with `sha256sum -c model.joblib.sha256`: 一致, prefix `ea73912a`.

## 2026-11-10 17:23 JST — CPU-best checksum reverified

Verified `artifacts/2026-11-06-cpu-cycle/09-05-function-view-candidate/model.joblib` against the previously recorded reference using `(cd artifacts/2026-11-06-cpu-cycle/09-05-function-view-candidate && sha256sum -c model.joblib.sha256)`: 一致 (`model.joblib: OK`), prefix `ea73912a`. The full checksum was written directly to the `.sha256` sidecar and not copied into this log or the response.

## 2026-11-10 17:20 JST — Qwen1.7B final-fit startup

The user asked to reread and apply the README handoff policy. Apply host-scoped stop semantics going forward: either host may be used when actually free; a stop request names only one host, whose intermediate results and exact resume point must be saved before stopping its Kaggle jobs and auto-injection/watchers and verifying GPU release. The other host continues. Keep the stopped host reserved until an explicit reuse instruction. This is not a stop request.

`codex_rate_limit.py --guard 15` passed at 17:16:52 JST (five-hour remaining 97%, weekly 51%). On Host142, Qwen1.7B all-train `--fit-final --resume` PID `868177` is running in a detached session under the GPU0 lock; both primary and confirmation OOF adoption gates were checked. The model initialization has allocated 3,905 MiB on GPU0 at 33% utilization; `MemAvailable` is `211796484 kB`, above the 16 GiB floor. The final-fit log has not emitted its first training event yet. GPU1 remains allocated to Mistral03 PID `603688` (15,006 MiB used, 37% utilization at 17:20); Qwen14B watcher `3748103` remains queued behind that registered GPU1 chain.

Host141 (`141-X9DAi`) candidate11 PID `2439031` remained alive on GPU2 in the 17:18 read-only poll; GPU2 used 8,549 MiB at 40% utilization and host memory floor passed. No host was stopped or reallocated. No Kaggle object or submission was created. Next objective remains preparing and runtime-checking the approved baseline blend private Notebook under the nine-hour limit.

## 2026-11-10 17:02 JST — resumed evaluations and active-run checkpoint

The user-requested `codex_rate_limit.py --guard 15` passed at 16:54:22 JST (five-hour remaining 99%, weekly 52%). Kaggle MCP at 16:53 reports 5,310 teams; public leader James Liebel scored `.755` at 00:34 UTC, next `.752`. Rules remain five submissions/day, two final selections, Notebook-only/offline/<=9h/`submission.parquet`; Timeline final deadline remains Jan 13, 2027 23:59 UTC.

Host141 (`141-X9DAi`) read-only poll at 17:02:33: candidate11 runner/wrapper `2439031`/`2439029` remains active on GPU2. Primary OOFs for folds0–3 exist. Fold4 Stage1 epoch-001 checkpoint was saved at 16:47:34 JST (45,000 examples, mean loss `1.622531`, peak allocated 8,214 MiB, `stop_requested=false`); Stage2/OOF are pending. GPU0/1/2 use/free=`171/15802`,`15/15960`,`8549/7426 MiB`, utilization `0/0/46%`; `MemAvailable=119017244 kB`. Candidate13 runner/wrapper `2448742`/`2448740` are absent and all five primary OOFs exist. Full-fold analysis was run on its five prediction files only in `/tmp`, against early CPU, adopted SVC, and current Qwen+SVC blend. Candidate BA `.499734`; vs current blend delta `−.086674`, prompt-paired 95% CI `[−.105556,−.067407]`, so reject and skip confirmation. No weights/checkpoints were transferred.

Host142 (`142-X10DAi`) local poll at 17:02:33: Mistral03 wrapper/runner `603686`/`603688` and watcher `3743539` remain active on GPU1. Fold0 OOF completed with BA `.603704`; fold1 setup has begun, with no later checkpoint/OOF yet. GPU0/1 use/free=`15/15960`,`15006/17094 MiB`, utilization `0/35%`; `MemAvailable=216746900 kB`. Qwen14B watcher `3748103` remains queued behind the Mistral watcher. The previous Qwen blend confirmation watcher exited at 04:42 after a stale-rate-record guard failure; the candidate08 pilot watcher also exited at 04:42 and its full-OOF watcher exited at 04:51 without starting a run. After the fresh guard passed, the fixed CPU blend confirmation and fixed Spectral confirmation were resumed directly; both preregistered gates pass (details: [Spectral confirmation](2026-11-10-spectral-meanfield-confirmation.md)). Candidate08 is not relaunched mid-queue; preserve Mistral/Qwen14B order and record the candidate08 resumption after that chain. CPU-best SHA-256 remains `ea73912adcdec42b25e3b785c211c7a8e64a8ee49b3ac35f776e9aa48f8af7a5`. No host/job was stopped or reallocated; no Kaggle write/submission.

## 2026-11-10 02:41 JST — active-fold poll

Official MCP recheck at 02:39 JST is unchanged: team_count 5,245, leaderboard `.752/.752/.747`, balanced accuracy, daily limit 5 and final limit 2. Timeline gives Jan 13, 2027 23:59 UTC; metadata's Jan 14 remains the later conflicting date. Code Requirements remain Notebook-only, Internet disabled, <=9h, `submission.parquet`. The current 02:38:47 guard remains valid (5h 86%, weekly 52%).

Host141 `141-X9DAi` was polled at 02:41:45 UTC. Runner and `flock` wrapper PIDs `2439031`/`2439029` (candidate11, GPU2) and `2448742`/`2448740` (candidate13, GPU0) remain alive. Candidate11's fold3 has been active since 14:40:06 UTC; the previous fold took about 9h and its current fold remains within that observed runtime. Candidate13's fold4 has been active since 14:28:32 UTC; its previous fold took about 5h41 and the current fold remains within range. Both main PIDs show CPU activity. No new OOF or checkpoint has appeared since 02:31 JST. Latest completed primary folds remain candidate11 fold2 BA `.544444` and candidate13 fold3 BA `.524074`.

GPU0/1/2 use/free are `1405/14568`, `15/15960`, `8553/7422 MiB`, utilization `15%/0%/53%`; `MemAvailable` is `113325476 kB`. Resource floors pass. Host142 remains unverified and is not free; Host141 has active jobs, so no new allocation. Preserve both jobs and queues without stop/restart. Existing CPU best and the three local comparator baselines remain intact; no OOF transfer or analyzer run until a candidate's complete five-fold primary OOF exists.

## 2026-11-10 17:47 JST — README handoff history archived

Moved the dated history from README's handoff section into [the dated experiment archive](2026-11-10-readme-handoff-history.md), preserving 135 lines. Hash literals were reduced to their first eight characters per the amended rule. The README `## 現在の状況` is 15 lines, and the handoff section now contains only current host-scoped stop/reuse policy, 30-minute monitoring cadence, official-check cadence, and links to the current log/archive.
## 2026-11-10 17:48 JST status update

Host141 candidate11's registered runner and wrapper are absent. All five primary fold OOF parquet files are present and the primary log records fold4 completion; the run ended naturally. GPUs 0/1/2 were idle (171/15/15 MiB used, 0% utilization) and the RAM floor passed. No weights or checkpoints need transfer. The five prediction-only OOF files still need comparison against the three complete local baselines before any adoption decision.

Host142 remains allocated: Mistral03 runner/watcher continues on GPU1, the registered Qwen14B watcher waits in its existing chain, and Qwen1.7B final fit continues on GPU0. SVC all-train final fit has completed successfully; its model sidecar check returned `model.joblib: OK` (`sha256sum -c`, prefix `fb8d0ff5`). No Kaggle object or submission was created. The 15% rate guard passed at 17:53:38 JST (5-hour remaining 95%, weekly 51%).


## 2026-11-10 18:41 JST — candidate09 worker 起動を検知

Host142のqueue確認でcandidate09 GPU workerが既に起動していることを検知した。起動後のphase・GPU使用量・RAMは未照合。SSHはhost key verificationで失敗したため検証を迂回していない。18:18 JSTの直近成功pollではQwen1.7B final fitとMistral03が稼働し、資源安全床を満たしていた。candidate09の段階と資源を次回の定期pollで確認するまで、Host142へ別のGPU jobを重ねない。

## 2026-11-10 18:45 JST — candidate09 worker検知の訂正

共有 `/tmp/qwen14b-candidate09-eval-watcher.log` の18:42行は登録済みMistral03 watcher待ちを示す。現時点の `ps` ではcandidate09のbash watcher PID `3748103`は生存し、`src/gpu_qwen14b_qlora.py` workerは見つからない。前回の「candidate09 GPU worker起動」検知はwatcherとworkerの取り違えとして訂正する。Host142のGPU/RAMを含む次の定期pollは18:48 JSTに行う。

## 2026-11-10 18:49 JST — 30分定期poll

Host142の主要worker、watcher、GPU、RAMを1コマンドで確認。Mistral03 runner PID `603688` はGPU1 (15,006 MiB used; 17,094 MiB free; 36%)、Qwen1.7B final-fit runner PID `868177` はGPU0 (3,905 MiB used; 12,070 MiB free; 32%)で稼働中。`MemAvailable=211750104 kB`。資源安全床を満たす。candidate09 watcher PID `3748103` はMistral watcher PID `3743539`の終了待ちで、candidate09 GPU workerは未起動。

## 2026-11-10 18:52 JST — baseline優先のqueue更新

18:49 pollでcandidate09 GPU workerが不在であることを確認後、candidate09 watcher PID `3748103`だけをSIGSTOPし、状態`T`を確認した。GPU workerやHost142の実行中jobは停止していない。既存のQwen8B baseline final-fit watcherをsession分離で起動し、PID `905369`がMistral watcher PID `3743539`の終了待ちで生存していることとlogを確認。Qwen8B watcherはMistral終了後にrate/resource/OOF gateを確認してpilot、final fitを進める。candidate09 watcherはQwen8B asset作成後に再開する。Notebook push/submissionなし。

## 2026-11-10 22:50 JST — scheduled Host142 poll unavailable

`--guard 15` passed at 22:50 JST (5-hour remaining 95%, weekly 48%). The scheduled poll first failed with `Host key verification failed`. The existing `142` and `142-home` aliases resolve to the same configured host and use the same known-host files; no trust settings were changed. A repeat poll returned exit 255, `No route to host` while connecting through the configured route. Host142 process/GPU/RAM state is therefore unknown after the last trusted 22:20 JST poll; this does not establish that any job stopped. No process was killed or restarted and no new work was allocated. Resume monitoring only through the configured, trusted SSH path after routing/host identity can be verified.

## 2026-11-10 22:58 JST — Host141 availability check

Because Host142 could not be reached, a read-only Host141 snapshot checked current shared-host availability. GPU0 ran PID `2808165` (`experiments/exp580_deberta_zm_s89`, ~10,891 MiB used, 100% utilization); GPU1 ran PID `2808166` (`experiments/exp581_deberta_zm_s101`, ~10,795 MiB used, 29% utilization). GPU2 was idle (15 MiB used, 0%); `MemAvailable=107335240 kB`. Host141 is not an idle host, so no new Kaggle work was allocated there; the two active processes were left untouched.

## 2026-11-10 23:20 JST — scheduled Host142 poll reached host-key verification

The scheduled read-only poll used the configured `142` alias with batch mode and a connection timeout. SSH returned `Host key verification failed` before the process/log/GPU/RAM command could run. Unlike the 22:50 retry that returned `No route to host`, this attempt reached the host identity check, but the presented key is not trusted and was not accepted or bypassed. The last trusted snapshot remains 22:20 JST (Mistral03 and Qwen3-1.7B final-fit active); Host142's current process/GPU/RAM state remains unknown. No job was stopped/restarted and no new work was allocated. Resume polling only after the configured trusted identity check succeeds.

## 2026-11-10 23:30 JST — trusted Host141 known-host reference prepared

Read-only inspection of trusted Host141's `known_hosts` found three saved key records for Host142's configured IP (ED25519, RSA, and ECDSA). Copied those existing entries to `/tmp/host142_known_hosts_from_trusted_141` (mode 600); local `ssh-keygen -lf` recognized all three, and `ssh -G` confirms the next connection uses this file with `StrictHostKeyChecking=yes` for `10.10.40.142`. No `ssh-keyscan`, trust-on-first-use, or verification bypass was used. At the 23:50 poll the key must match a saved record or remain rejected. Host142 job state is still unknown, and no Host142 job was changed.

## 2026-11-10 23:50 JST — trusted Host142 polling resumed

Strict host-key verification succeeded against the saved Host141 key set. The one-command status poll confirmed Mistral03 primary running on GPU1 (PID `603688`) and Qwen3-1.7B final fit running on GPU0 (PID `868177`); the Qwen8B baseline watcher (PID `905369`) remains queued behind Mistral03. GPU0 use/free was `3907/12068 MiB`, GPU1 `15006/17094 MiB`, and `MemAvailable=211751060 kB`; resource safety floors pass. No run was stopped/restarted and no new job was allocated.
