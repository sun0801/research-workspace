---
date: 2026-11-16
project: kaggle-name-that-llm
type: experiment-log
spec: ../specs/2026-11-15-mistral-spectral-private-notebook-runtime-spec.md
status: private-runtime-queued
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
