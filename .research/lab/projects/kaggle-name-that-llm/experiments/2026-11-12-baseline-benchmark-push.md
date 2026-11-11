---
date: 2026-11-12
project: kaggle-name-that-llm
type: private-baseline-benchmark-push
---

# Private baseline benchmark push — 2026-11-12

## 01:06 JST — private Notebook version 1 queued

- Kaggle CLI authentication succeeded through the implementation repository's `.env` flow. No credential value was displayed or recorded.
- Created `suntree0801/name-that-llm-private-blend-assets` with `kaggle datasets create --path notebooks/name-that-llm-private-baseline/dataset-assets --dir-mode tar` (no `--public`). Kaggle MCP confirmed version 1 is `Ready`, `is_private=true`, 213,121,948 bytes.
- Immediately before the Notebook push, official MCP showed public leader James Liebel at `.765`, 5,506 teams, and Timeline Final Submission Deadline 2027-01-13 23:59 UTC. Rules: max 5 submissions/day and 2 final selections. Code Requirements: Notebook-only, offline, <=9 hours, output `submission.parquet`. Metadata deadline remains Jan 14, so Timeline is the conservative date. CLI reported `numAllowedNow=5` and `No submissions found` (zero prior submissions/final selections).
- Local `kernel-metadata.json` was inspected: private, GPU enabled, TPU disabled, Internet disabled, NvidiaL4; input sources are the competition, the private asset Dataset, and official Qwen3 8B/1.7B model versions. The notebook has `BENCHMARK_ONLY = True`.
- Pushed with `uv run --env-file ../.env kaggle kernels push --path notebooks/name-that-llm-private-baseline --timeout 32400`. Kaggle returned version 1. Kaggle MCP then confirmed remote `is_private=true`, `enable_gpu=true`, `enable_internet=false`, `machine_shape=NvidiaL4`, current version 1, and the expected private dataset/model inputs.
- `uv run --env-file ../.env kaggle kernels status suntree0801/name-that-llm-private-baseline-blend` returned `KernelWorkerStatus.QUEUED`. Runtime has not been measured; benchmark-only mode skips hidden test-text inference and creates no submission file. No scored submission has been made.

## Resume point after v1 push (superseded by its error below)

At 01:36 JST, poll the same Kaggle Kernel once with a lightweight status command. If still queued/running, continue at 30-minute intervals and record only changes. On completion, read the runtime estimate and gate result. Do not change the adopted blend if the projection exceeds nine hours; report the measured shortfall first. If it passes, conduct a fresh official/rate/submission-limit check immediately before the final private Notebook push, verify its privacy/version, then submit once and record the returned Public LB score.

## 01:09 JST — remote asset file listing

Kaggle MCP `list_dataset_files` for private Dataset version 1 returned all 35 expected files: asset manifest and provenance, both Qwen adapter/head/tokenizer bundles and their manifests, and the SVC pipeline/model files. This supplements the remote `Ready`/private metadata check; no files or Dataset versions were changed.

## 01:17 JST — runtime projection correction

The official competition Data Description says an interactive Notebook sees only three sample `test.csv` rows, while the hidden scoring rerun contains about 4,000 passages. The pushed version 1 used the visible `test.csv` length as the hidden projection count, so its `runtime_gate_pass` alone is not authoritative if it runs interactively. Updated the local Notebook to project `max(4,000, visible test-ID rows)`, log both counts, and retain the existing 25% margin, model-load accounting, and 30-minute allowance. JSON parsing and compilation of all four code cells passed. The remote version 1 was not altered; if its probe finishes, recompute its measured per-row timings at 4,000 rows. Include the corrected projection in the final private Notebook. No blend component or weight changed.

## 01:36–01:40 JST — v1 environment assertion failure; v2 pushed

- The scheduled lightweight status command `uv run --env-file ../.env kaggle kernels status suntree0801/name-that-llm-private-baseline-blend` changed from `QUEUED` to `ERROR`.
- Retrieved the kernel log. Version 1 stopped in its first code cell after about 61.9 seconds: metadata requested NvidiaL4, but the runtime reported `Tesla T4`; the fixed L4-name assertion failed before loading assets or running the timing probe. No per-row runtime or 4,000-row estimate was produced, and no test-text inference or scored submission ran.
- Removed only the fixed device-name assertion. CUDA availability is still required, and the first cell already records the actual `torch.cuda.get_device_name(0)`. Notebook JSON parsed and all four code cells compiled; `BENCHMARK_ONLY=True`, 4,000-row projection, asset inputs, and blend composition remain unchanged.
- Immediately before repush, official Kaggle MCP reconfirmed Rules, Timeline, Code Requirements, public leaderboard and teams; CLI submission limits showed 5 remaining today and no prior submissions. Leader remains `.765`; team count is 5,508; metadata deadline Jan 14 and Timeline deadline Jan 13 (both 23:59 UTC); max five submissions/day and two final selections; Notebook-only, offline, <=9h, `submission.parquet`. Codex guard: 5h remaining 88%, weekly 37%.
- Pushed the corrected benchmark-only Notebook as version 2 with `uv run --env-file ../.env kaggle kernels push --path notebooks/name-that-llm-private-baseline --timeout 32400`. The next lightweight status poll is scheduled 30 minutes after this push (about 02:09 JST); do not poll earlier. Version 1 remains an error record; it is not treated as a benchmark result.

## Resume point after v2 push (superseded by its error below)

At about 02:09 JST, run one lightweight status command for version 2. If still queued/running, poll every 30 minutes and log only changes. If it errors, retrieve the log to identify whether any timing was produced. If it completes, use the measured per-row timings with the 4,000-row projection, both model-load passes, 25% margin and fixed 30-minute overhead. If the estimate exceeds nine hours, report before changing the blend. If it passes, repeat official/rate/submission-limit checks immediately before the final private Notebook push and one scored submission.

## 02:09–02:11 JST — v2 input-path failure; v3 pushed

- Scheduled command `uv run --env-file ../.env kaggle kernels status suntree0801/name-that-llm-private-baseline-blend` reported `KernelWorkerStatus.ERROR` for version 2. CLI output log shows failure after about 42.9 seconds at the offline-input assertion: `/kaggle/input/name-that-llm/test.csv` did not exist. No model loading or timing probe began; no per-row runtime, hidden inference, or submission was produced.
- Changed only `COMP_DIR` to the official Code Requirements path `/kaggle/input/competitions/name-that-llm`. The local Notebook JSON parsed and all four code cells compiled; `BENCHMARK_ONLY=True`, GPU name logging, >=4,000 hidden-row projection, and adopted blend composition are unchanged.
- Immediately before v3 push, official checks reconfirmed leader `.765`, 5,518 teams, Timeline deadline 2027-01-13 23:59 UTC (metadata still Jan 14), Rules max five submissions/day and two final selections, Code Requirements offline/<=9h/`submission.parquet`, and submission limits 0 used / 5 remaining. Codex guard was 88% (5h), 36% (weekly).
- `uv run --env-file ../.env kaggle kernels push --path notebooks/name-that-llm-private-baseline --timeout 32400` returned version 3 successfully. No scored submission was made.

## Resume point after v3 push (superseded by its error below)

At about 02:42 JST, run one lightweight status command for version 3. If queued/running, continue at 30-minute intervals and log only changes. If it errors, inspect output for the next environmental/input issue; if it completes, calculate the 4,000-row gate from its measured per-row timing, model loads, 25% margin and fixed 30-minute overhead. If runtime exceeds nine hours, report before changing composition. Before any subsequent Notebook push or scored submission, repeat the official, rate-guard and submission-limit checks.

## 02:42–02:47 JST — v3 asset mount mismatch; v4 pushed

- Scheduled status command reported `KernelWorkerStatus.ERROR` for v3. Its log failed after about 66.9 seconds at the offline-input assertion for `/kaggle/input/name-that-llm-private-blend-assets/qwen8/final-model/head.pt`. The competition CSV path and Qwen base configs had passed; no model load or runtime probe began.
- Read-only remote metadata pull confirmed the Kernel remains private, GPU-enabled, Internet-disabled, requests NvidiaL4, and includes `suntree0801/name-that-llm-private-blend-assets` as a Dataset source. Kaggle Dataset version 1 file listing contains `qwen8/final-model/head.pt` (2,624,221 bytes); local staged bundle has the same relative file. Thus the remaining mismatch is the runtime mount root, not a missing uploaded file.
- Updated Notebook initialization to search the common direct, owner-qualified, and `/kaggle/input/datasets/<owner>/<slug>` layouts for exactly one `qwen8/final-model/head.pt`, derive the asset root from that path, and report mounted input roots. No asset contents, model settings, blend components, or weights changed. JSON and all four code cells passed static validation; benchmark-only and 4,000-row runtime gate remain enabled.
- Immediately before v4 push, official checks found leader `.768` (NguyenThanhNhan), 5,523 teams, unchanged Rules/Timeline/Code Requirements, and 5 submissions remaining. The Timeline deadline remains 2027-01-13 23:59 UTC; metadata still reports Jan 14. Codex guard was 87% (5h), 36% (weekly).
- Private Notebook version 4 pushed successfully with `uv run --env-file ../.env kaggle kernels push --path notebooks/name-that-llm-private-baseline --timeout 32400`. Next status poll is due about 30 minutes later, 03:16 JST. No scored submission or test-text inference has run.
- Post-push `kaggle kernels pull --metadata` confirmed the remote Notebook is private, GPU-enabled, Internet-disabled, NvidiaL4-requested, and still attached to the expected private Dataset and competition inputs.

## Resume point after v4 push (superseded by its error below)

At about 03:16 JST, run one lightweight status command for version 4. If queued/running, continue at 30-minute intervals and record only changes. If it errors, inspect output for any remaining input/runtime issue. If it completes, calculate the gate using measured per-row timings projected to 4,000 hidden rows, both Qwen load passes, 25% margin, and 30-minute overhead. If it exceeds nine hours, report before changing the baseline composition. If it passes, perform the final official/rate/submission-limit checks immediately before one scored baseline submission.


## 03:16–03:23 JST — v4 sklearn version mismatch; v5 pushed

- Scheduled status command reported `KernelWorkerStatus.ERROR` for v4. The log failed after about 47.7 seconds at the version gate: SVC artifact metadata requires scikit-learn `1.9.1`; Kaggle runtime provides `1.6.1`. Asset mount and all input-file checks passed. Joblib model loading / SVC probe and Qwen loading did not begin; no runtime estimate exists.
- Local implementation environment has Python 3.12 and scikit-learn 1.9.1. No Python 3.13 wheel was found in the checked local wheel cache. Did not suppress the version gate or assume compatibility. Generated a local reference decision-function matrix for the first 64 text-only timing rows (18 classes; no labels/prompt IDs) with the exact SVC artifact and sklearn 1.9.1.
- Notebook now logs expected and runtime sklearn versions, loads the existing artifact, and compares its 64×18 decision outputs with the local reference using `np.allclose(rtol=1e-5, atol=1e-5)`. A mismatch fails before timing; a match allows the unchanged baseline runtime probe. The SVC artifact, blend weights/components, GPU precision and scoring method are unchanged. Notebook JSON and all four code cells compile.
- Immediately before v5 push, official sources showed leader `.768`, 5,532 teams; Rules/Timeline/Code Requirements unchanged; submission count 0/5. Codex guard was 85% (5h), 36% (weekly).
- Private benchmark-only version 5 pushed successfully with `uv run --env-file ../.env kaggle kernels push --path notebooks/name-that-llm-private-baseline --timeout 32400`. Next light status poll due about 03:54 JST. No scored submission or test-text inference has run.

## Resume point after v5 push (superseded by its error below)

At about 03:54 JST, run one lightweight status command for v5. If queued/running, continue at 30-minute intervals and record only changes. If it errors at the compatibility gate, compare the reported max absolute delta and stop before changing the baseline composition. If it passes the gate and completes, recompute runtime using measured per-row values projected to 4,000 hidden rows, both Qwen load passes, 25% margin and 30-minute overhead. If the estimate exceeds nine hours, report before changing the blend. If it passes, do the final just-before-push/submit official, rate, and submission-limit checks, then submit the baseline once.

## 03:54–03:59 JST — v5 SVC compatibility passed; torchao LoRA dispatch failure; v6 pushed

- Scheduled status command reported `KernelWorkerStatus.ERROR` for v5. The SVC artifact loaded under Kaggle scikit-learn 1.6.1 with `InconsistentVersionWarning`; its 64×18 `decision_function` matrix matched the local scikit-learn 1.9.1 reference exactly (max absolute difference `0.0`). The compatibility gate passed.
- Qwen base-model loading reached PEFT LoRA injection but failed after about 42 seconds because Kaggle ships torchao 0.10.0 while its PEFT LoRA TorchAO dispatcher requires >=0.16.0. The Qwen base is loaded unquantized with no `quantization_config`; no Qwen inference or runtime probe completed.
- This matches the resolved PEFT issue [#3964](https://github.com/huggingface/peft/issues/3964): an unused old torchao install can break ordinary LoRA injection. The official fix makes unsupported torchao unavailable to PEFT; we applied the same narrow behavior only when the base is unquantized and torchao <0.16.0, while keeping the explicit guard against quantized bases. Baseline models/adapters, dtype, blend weights, and inference code are unchanged.
- Notebook JSON and all four code cells compile. Immediately before v6 push, official leader `.768`, team count 5,534, Rules/Timeline/Code Requirements, and CLI submissions 0/5 were reconfirmed. Codex guard was 99% (5h), 36% (weekly).
- Private benchmark-only version 6 pushed successfully. Post-push remote metadata confirms `is_private=true`, GPU enabled, Internet disabled, NvidiaL4 requested, and expected private Dataset/competition sources. Next light status poll due about 04:28 JST. No scored submission or test-text inference has run.

## Resume point after v6 push (superseded by its error below)

At about 04:28 JST, run one lightweight status command for v6. If queued/running, continue at 30-minute intervals and log only changes. If the PEFT workaround passes and the benchmark completes, use measured per-row values projected to 4,000 hidden rows, both Qwen load passes, 25% margin, and 30-minute overhead. If a new error occurs, record it and do not alter baseline composition without reporting first. If the gate passes, perform the final just-before-push/submit official, rate, and submission-limit checks before one scored baseline submission.

## 04:28–04:33 JST — v6 Qwen8B inference probe OOM; baseline held for user decision

- Scheduled status command reported `KernelWorkerStatus.ERROR` for v6. The SVC cross-version check again passed exactly: local scikit-learn 1.9.1 and Kaggle 1.6.1 produced 64×18 decision outputs with max absolute difference `0.0`. The conditional PEFT workaround also passed and the unquantized Qwen base/LoRA loaded.
- Failure occurred during Qwen8 inference on the first 64-row timing probe, in Transformers Qwen3 SDPA `scaled_dot_product_attention`, after about 242.6 seconds. Kaggle actually assigned Tesla T4 despite the Kernel metadata requesting NvidiaL4. GPU total was 14.56 GiB, process usage 14.55 GiB (PyTorch 14.35 GiB), only 8.81 MiB free; a 16 MiB allocation failed.
- No per-row timing or 4,000-row projection was produced; Qwen17 probe did not run, no test-text inference or scored submission occurred. The adopted baseline composition, weights, dtype, and sequence length remain unchanged.
- Per the approved 2026-11-10 operations clause, report the inability to run the adopted configuration as assigned before changing baseline composition. Hold further Notebook changes/pushes and do not substitute a model or alter blend weights until the user decides how to proceed. Kaggle v6 remains private.

## Resume point after v6 (superseded by v7 push)

The next decision is whether to wait for an actual L4 allocation or authorize a separately evaluated inference configuration change (for example memory-saving attention/precision/offload, with output consistency checks). No new scored submission is ready: the runtime gate is unmeasured and the current public leader is `.768`. Keep the adopted blend intact until an explicit direction resolves this blocker.

## 04:34–04:38 JST — v7 L4X1 request; remote GPU flag discrepancy

- Before the v7 push, the official Rules, Timeline, Code Requirements, public leaderboard, and team count were checked. Leader was`.768`, teams 5,534; the Timeline final deadline was 2027-01-13 23:59 UTC, Rules allowed five submissions/day and two final selections, and Code Requirements remained Notebook-only, offline, <=9 hours, with `submission.parquet`. CLI reported five submissions available today and zero prior submissions. Codex guard showed 5h remaining 97%, weekly 35%; Kaggle GPU usage was 0.15h/30h.
- The benchmark-only Notebook was pushed as private version 7 with the CLI-supported `NvidiaL4X1` accelerator. No model, blend, inference, or scoring configuration changed.
- Post-push remote metadata reported `is_private=true`, `machine_shape=NvidiaL4X1`, expected private Dataset and competition sources, but `enable_gpu=false`; local metadata still says GPU enabled. Treat actual execution/GPU allocation as unresolved until the scheduled status check. Do not infer that L4X1 was allocated from `machine_shape` alone.
- No test-text inference, runtime estimate, or scored submission has occurred. The adopted baseline is unchanged. If the same baseline cannot pass the <=9-hour requirement, report the measured limit before changing its composition.

## 05:05–05:10 JST — v7 T4 OOM; accelerator identifier diagnosis

- The scheduled one-command `kaggle kernels status` returned `KernelWorkerStatus.ERROR`. Downloaded the private kernel log. Its startup output reported Tesla T4, CUDA available, and Internet disabled. During the first 64-text Qwen8 inference probe, Qwen3 SDPA failed after about 230.4 seconds: GPU0 had 14.56 GiB total, 14.54 GiB in use, 22.81 MiB free, and a 20 MiB allocation failed. The model was loaded with bfloat16 and the adopted `MAX_LENGTH=384`; the error stack was `scaled_dot_product_attention`.
- No Qwen8 probe timing, Qwen17 probe, hidden-text inference, 4,000-row runtime estimate, or `submission.parquet` was produced. v7 remains private; the blend members, model weights, mean probabilities, dtype, and max length are unchanged. This does not establish whether a second T4 was also present because the Notebook did not log `torch.cuda.device_count()`.
- Current official Kaggle CLI metadata documentation gives `NvidiaL4` and `NvidiaTeslaT4` as accelerator examples, without mentioning `NvidiaL4X1`. A Kaggle CLI maintainer response identifies `NvidiaTeslaT4` as the backend identifier for two T4s. This makes `NvidiaTeslaT4` a documented dual-T4 route to investigate; it does not explain why v6, which requested documented `NvidiaL4`, also ran on a T4. Sources: [kernel metadata docs](https://github.com/Kaggle/kaggle-cli/blob/main/docs/kernels_metadata.md), [accelerator identifier clarification](https://github.com/Kaggle/kaggle-cli/issues/1196).
- At 05:10 JST, read-only Host141 checks showed GPUs 1 and 2 at 15 MiB each, GPU0 at 171 MiB with only Xorg/GNOME processes, 0% compute, and 115 GiB `MemAvailable`. The local Qwen8 base checkpoint is not mounted there and the host has no Transformers/PEFT/Accelerate installation; no run was started. Host142 remains unverified due the earlier strict host-key failure.
- The user's pre-change report condition has been met: the adopted blend as executed on the assigned T4 cannot complete even the first Qwen8 timing probe. Keep model/blend members and weights intact. The current CLI docs identify `NvidiaTeslaT4` as the T4×2 shape; a private v8 is staged to request that documented shape and distribute Qwen8 across both GPUs, with a 10 GiB per-GPU model memory cap (over 4 GiB headroom), while retaining bfloat16, max length 384, adapters, head, and pooling. It asserts two GPUs and that Qwen8 maps to both before probing. Static JSON parsing and compilation of all four code cells passed. This has not yet run; no accuracy/runtime result is claimed.
- Before the v8 push, official MCP confirmed leader`.768`, team count 5,541, Rules max five submissions/day and two final selections, Timeline Jan 13 23:59 UTC (metadata Jan 14), Code Requirements Notebook-only/offline/<=9h/`submission.parquet`; CLI showed five submissions currently allowed. Private asset Dataset v1 is Ready. Kaggle quota is 0.22/30.00 GPU hours used and 29.78 remaining; rate guard is 5h 96%, weekly 35%. Repeat official and quota checks immediately before the push if the staged version or relevant data changes.

## Resume point after v7 error

v7 is terminal; do not poll it again. The staged private v8 is at `/tmp/name-that-llm-v8-dual-t4`; its push-before checks are documented above. If pushed and queued/running, poll every 30 minutes and record only changes. If it exposes fewer than two GPUs or cannot map Qwen8 across both, stop before inference and inspect the log. If the 64-row inference probe completes, use its measurements for the existing 4,000-row projection and 9-hour gate. If dual-T4 execution still cannot run the adopted setup, report before changing precision, max length, or blend composition.

## 05:20–05:32 JST — v8 dual-T4 benchmark pushed; first status running

- Immediately before push, official Rules, Timeline, Code Requirements, public leaderboard, team count, and CLI submission limits were checked. Leader was`.768` (NguyenThanhNhan), teams 5,541; max five submissions/day and two final selections; Timeline deadline 2027-01-13 23:59 UTC (metadata still Jan 14); Notebook-only, offline, <=9h, `submission.parquet`; five submissions available today. Private asset Dataset v1 was Ready/private. Codex guard showed 5h remaining 94%, weekly 35%.
- Pushed private benchmark-only Notebook version 8 using `NvidiaTeslaT4`; remote metadata confirms private, GPU enabled, Internet disabled, expected competition and private Dataset/model inputs. The source was prepared with Qwen8 mapped across both GPUs, 10 GiB per-GPU model memory caps, and an early two-GPU assertion. No baseline model, adapter, blend member/weight, bfloat16 precision, or 384-token limit changed.
- Preserved the pushed source as `/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/notebooks/name-that-llm-private-baseline-v8-dual-t4/`; the pre-v8 directory remains untouched.
- JSON parsing and compilation of all four code cells passed before push. This is static validation only; no runtime, accuracy, or submission result is implied.
- The initial lightweight `kaggle kernels status` returned `KernelWorkerStatus.RUNNING` at about 05:30 JST. Next poll is due about 06:00 JST. No test-text inference, 4,000-row runtime estimate, or scored submission has occurred.

## Resume point after v8 push

At about 06:00 JST, run one lightweight status command for v8. If still queued/running, poll every 30 minutes and record only a state/result/resource change. If it errors, inspect the output log once and record the cause. If it completes, calculate the existing 4,000-row projection, both model-load passes, 25% margin, and fixed 30-minute overhead against the nine-hour gate. Submit the unchanged adopted blend once only after that gate passes and the just-before-submit official/quota/privacy checks pass.

## 06:00–06:05 JST — v8 dual-T4 runtime gate passed; v9 scored run prepared

- The scheduled light `kaggle kernels status` changed to `KernelWorkerStatus.COMPLETE`. Retrieved the private output log and `runtime_estimate.json`.
- Runtime reports two Tesla T4 GPUs (14.56 GiB each), Qwen8 layer mapping across both devices, and after load 8.184/6.135 GiB reserved. SVC compatibility check passed (local sklearn 1.9.1 vs Kaggle 1.6.1; max absolute decision-output difference 0.0). Qwen17 also loaded; no OOM or runtime error was logged.
- For 64-row probes, Qwen8 used 66.06s (1.0321 s/row), Qwen17 14.83s (0.2317 s/row), SVC 0.16s. Projected 4,000-row inference: 5,146.54s; two passes of Qwen loads: 291.98s; fixed overhead: 1,800s; with 25% margin: 9,048.14s = 2.5134h. `runtime_gate_pass=true` against 9h.
- v8 was explicitly benchmark-only and skipped all test-text inference; no `submission.parquet` or scored submission was created. The result proves runtime feasibility of the measured path, not a score or prediction-quality result.
- Before push, official MCP reconfirmed leader`.768` (NguyenThanhNhan), 5,543 teams, max five submissions/day and two final selections, Timeline Jan 13 23:59 UTC (metadata Jan 14), Notebook-only/offline/<=9h/`submission.parquet`; CLI reported five submissions available and no prior submissions. Last reported Kaggle GPU quota before v8 was 29.78h remaining; the 282s v8 runtime is about 0.08h, so the predicted 2.51h scored run fits within that recorded reserve with over 27h left. CLI exposes no direct quota subcommand in its kernel command set.
- Prepared a separate final-scoring private source at `/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/notebooks/name-that-llm-private-baseline-v9-scored/`; only `BENCHMARK_ONLY = True` was changed to `False`. JSON parsed, all four code cells compiled, and metadata remains private/GPU-enabled/Internet-disabled/`NvidiaTeslaT4`. v8 and its source remain intact.
- Next: push v9, wait for the sample run to complete, then immediately recheck official status and submission allowance before `kaggle competitions submit --kernel suntree0801/name-that-llm-private-baseline-blend --version <v9>`. This is the one baseline submission intended to establish primary BA`.586408` vs public LB correspondence; it must not be used to tune weights.

## 06:05–06:06 JST — private scored-run Notebook v9 pushed

- `kaggle kernels push --accelerator NvidiaTeslaT4 --path notebooks/name-that-llm-private-baseline-v9-scored --timeout 32400` succeeded as private kernel version 9.
- The initial single-command status returned `KernelWorkerStatus.RUNNING`. Next scheduled light status is due about 06:36 JST; record only a state/result/resource change.
- v9 is the same adopted Qwen3-8B + Qwen3-1.7B + prompt-centered SVC mean-probability blend, and changes only `BENCHMARK_ONLY` to run the actual test-inference/output path. No score or submission exists yet. After this kernel run completes, do the just-before-submission official/quota/privacy check, then make exactly one code-competition submission for version 9.
- Post-push source comparison confirms v8→v9 changed only `BENCHMARK_ONLY = True` to `False`; kernel metadata is byte-identical.

## 06:37–06:39 JST — baseline version 9 submitted for scoring

- Immediately before submission, official MCP reconfirmed public leader`.768` (NguyenThanhNhan), team count 5,545, daily limit five and final-selection limit two, Timeline deadline Jan 13 23:59 UTC (metadata remains Jan 14), Notebook-only/offline/GPU <=9h/`submission.parquet`. CLI showed five allowed and no previous submissions. Remote pull of v9 metadata confirmed private, GPU enabled, Internet disabled, T4 accelerator, and expected competition/model/private Dataset inputs. Rate guard: 5h 92%, weekly 35%.
- Notebook version 9 completed its sample run and produced `/kaggle/working/submission.parquet`. Downloaded output has 3 interactive sample rows, columns `id`,`model`, no nulls, and 3 unique IDs; the official hidden scoring rerun contains about 4,000 rows. The v9 runtime projection (including two Qwen load passes, fixed 30-minute overhead, 25% margin) is 9,109.17s = 2.5303h, below 9h. This is not a hidden-set score.
- Submitted the Notebook output through `uv run --env-file ../.env kaggle competitions submit name-that-llm --file submission.parquet --kernel suntree0801/name-that-llm-private-baseline-blend --version 9 --message "Adopted baseline blend; primary BA 0.586408 to public LB correspondence"`. Kaggle accepted submission ref `58251076`; submission date `2026-11-11 21:39:01 UTC` (`2026-11-12 06:39:01 JST`); 4 submissions remain today.
- Initial `kaggle competitions submission 58251076` status is `PENDING`; public/private scores are not available yet. This is the single baseline submission for the CV-to-public-LB correspondence check. Next light status query is due about 07:09 JST; record only a status/score change.

## 07:09–07:13 JST — hidden scoring rerun failed; baseline unchanged

- The scheduled status check for submission ref `58251076` returned `COMPLETE` with Kaggle's error: the Notebook hit an unhandled error during the hidden-dataset rerun. Public and private scores are blank. Treat this as a failed submission; it does not establish the baseline's Public LB score or CV-LB correspondence.
- The v9 interactive/sample run did complete in about 303 seconds and wrote a valid three-row `submission.parquet` (`id`,`model`, no nulls or duplicate IDs). Its runtime projection is 9,109.17s = 2.5303h with two Qwen load passes, fixed 30-minute overhead, and 25% margin. The hidden failure therefore remains unexplained by the available output; do not infer a runtime or memory cause from the generic error.
- `kaggle kernels logs` for the kernel and explicit version 9 both returned the successful sample-run log, not a hidden-rerun stack trace. The CLI submission detail exposes only the generic error. No distinct submission-diagnostic API is available through the enabled Kaggle tools; the separate Kaggle MCP notebook info/output tools previously returned permission denied, so they were not retried.
- A read-only `kaggle competitions submission-download 58251076` attempt returned HTTP 403 Forbidden (“You don't have access to this resource”); it did not provide a hidden output or further error detail.
- No Notebook/config/blend changes or second submission were made. The model members, weights, bfloat16, 384-token limit, and T4×2 path remain intact. Per the approved operations clause, report this failure and the 2.5303h estimate before changing the baseline configuration. The precise hidden-run failure and Public LB result remain unknown.
