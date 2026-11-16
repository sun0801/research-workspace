---
date: 2026-11-16
project: kaggle-name-that-llm
type: experiment-log
spec: ../specs/2026-11-15-mistral-spectral-private-notebook-runtime-spec.md
status: private-runtime-rerun-queued
---

# Mistral v14 private push and Kaggle runtime

## Candidate and authorization

This is the fixed v14 Mistral + Spectral candidate approved by the active goal and the [runtime spec](../specs/2026-11-15-mistral-spectral-private-notebook-runtime-spec.md). It uses the five primary-fold Mistral adapters/heads, averages fold probabilities, combines them with the frozen three-component baseline at `(3 * baseline + Mistral) / 4`, then applies the unchanged Spectral transform. No weights or test labels were tuned.

## Fresh pre-write gates — 2026-11-16 JST

- Official Kaggle MCP recheck: public leaderboard top `.774`; 6,035 teams; own Public best remains `.560` (v13 ref `58300703`). The spec's new comparison baseline is `.560`; the public leader is context only. Metadata deadline says 2027-01-14 23:59 UTC while the official Timeline says final submission deadline 2027-01-13 23:59 UTC; retain this discrepancy and use the Timeline date for planning.
- Rules/Code Requirements recheck: external models/data are allowed subject to the public/equally accessible or reasonable-access rules; code competition requires a Notebook, offline execution, valid `submission.parquet`, and a maximum of 9 hours. Rules allow at most five submissions per day and two final selections.
- Authenticated read-only `kaggle competitions submissions name-that-llm --format json --page-size 200`: zero submissions dated 2026-11-16 at pre-write. No final selection was made.
- Existing asset Dataset `suntree0801/name-that-llm-private-blend-assets` was remote-private before update (v1). The update uploaded with `kaggle datasets version --path artifacts/mistral-v14-private-dataset-staging --message 'Add Mistral v14 fold adapters and heads' --dir-mode zip`; remote v2 is `Ready`, `is_private=true`, CC BY-SA 4.0, 60 mounted files including all five Mistral adapter files. Kaggle's dataset listing exposes the nested file paths expected by the Notebook.
- Asset integrity: 一致, verified with `sha256sum -c ASSET-SHA256SUMS`. v13 source preservation: 一致, verified with `sha256sum -c /tmp/mistral-v13-preserved.sha256`. Only “一致” and commands are recorded; no full digest is copied.
- Local v14 metadata was `is_private=true`, `enable_internet=false`, `machine_shape=NvidiaTeslaT4`, with Qwen 8B/1.7B and Mistral model sources. All five code cells compiled. The Notebook contains the 64-row unlabeled test-text probe, per-GPU 10% reserve check, fixed 1.25× projection for 4,000 hidden rows, and 9-hour stop gate. A CLI archive-layout check confirmed extracted subdirectory paths; the code supports both zipped and directly mounted layouts.
- Local A4000 evidence remains the 64-row/five-fold pilot pass (peak reserved 6,776/7,222 MiB); its combined Kaggle runtime projection was 4.34h using the v13 T4 baseline estimate plus the Mistral-only estimate. This is an estimate only; the Kaggle T4 measurement remains pending.

## Private push and runtime status

- First `kaggle kernels push --no-run` returned HTTP 400: “The title cannot exceed 50 characters.” No v14 kernel appeared in the authenticated `kernels list --mine` after that attempt. This was fixed inside the approved Notebook scope by shortening the matching slug/title to `suntree0801/name-that-llm-private-v14-mistral-spectral` / “Name That LLM Private v14 Mistral Spectral” (42 characters).
- Builder regeneration and static validation passed; the title slug matches the metadata ID. The v13 source hash still reports 一致.
- Private no-run push saved Notebook version 1. `kaggle kernels pull ... --metadata` verified the remote metadata: `is_private=true`, GPU enabled, internet disabled, `NvidiaTeslaT4`, and the expected private Dataset/model sources.
- Default `kaggle kernels push` saved Notebook version 2 and started the runtime check. The immediate status was `KernelWorkerStatus.QUEUED`. This is not a competition submission; the daily submission count remained zero after version 1 was saved.
- Runtime gate is pending. On completion, recover `runtime_estimate.json` and output logs, verify both GPUs retained at least 10% VRAM, `runtime_gate_pass=true` with the 1.25× hidden-row estimate below 9h, and the exact interactive test ID sequence/valid output schema. If any runtime gate fails, do not submit.
- Before a competition submission, report the measured runtime, memory, gate result, and candidate context to the user. The current public-top score is not a reason to reject a candidate; compare any score to the hand-held `.560` baseline under the 2026-11-16 policy.

## Runtime v2 failure diagnosis and v3 rerun — 2026-11-16 JST

- The first Kaggle runtime ended `ERROR` after 315 seconds during the Mistral base-model load. Kaggle exposed two Tesla T4 GPUs (14.56 GiB each); Transformers' allocator warmup requested 6.31 GiB on GPU0 with 5.77 GiB free and 8.79 GiB already used. Qwen8B and Qwen1.7B had completed their 64-row probes. The failure occurred before the Mistral probe, so the 10% VRAM and runtime-projection gates remain unmeasured; no submission artifact or competition submission was produced.
- Diagnosis from the source and trace: `unload_qwen()` deleted only its local parameters. The notebook-level `model` and `tokenizer` names still referenced the final Qwen model when Mistral loading began, retaining its GPU allocation. This is a reference-lifetime bug; no evidence indicates the approved unquantized Mistral path itself exceeds the T4 pair.
- Fixed the builder and regenerated v14 to explicitly delete the caller references after each Qwen probe and before final Mistral inference. Added a diagnostic of allocated VRAM immediately before Mistral loading. Model weights, precision, device placement, five-fold averaging, blend weights, and Spectral transform are unchanged. All five code cells compile. v13 source remains 一致 under `sha256sum -c /tmp/mistral-v13-preserved.sha256`.
- Pre-push gates on 2026-11-16: Codex rate guard passed (5h remaining 95%, weekly 80%); official rules and Evaluation reconfirmed; official leaderboard top `.774`, 6,043 teams; authenticated competition submission list showed zero submissions on 11/16. Remote kernel metadata was verified `is_private=true`, GPU enabled, internet disabled, `NvidiaTeslaT4`, with the approved data/model sources.
- Pushed private Notebook version 3. Kaggle reports `KernelWorkerStatus.QUEUED`; the immediate post-push metadata check reconfirmed private/offline/T4. This is a runtime rerun only, not a competition submission. Next action is to recover the terminal runtime log and check the pre-Mistral memory diagnostic, 10% VRAM reserve, and 4,000-row/9-hour projection. Do not submit unless every gate passes, and report to the user before any competition submission.
