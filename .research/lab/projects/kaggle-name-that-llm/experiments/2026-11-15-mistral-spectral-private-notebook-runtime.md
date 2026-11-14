---
date: 2026-11-15
project: kaggle-name-that-llm
type: experiment-log
spec: ../specs/2026-11-15-mistral-spectral-private-notebook-runtime-spec.md
status: host141-pilot-pass-kaggle-runtime-pending
---

# Mistral + Spectral private Notebook runtime check

## Decision

The independent confirmation passed with BA `.676823` vs `.653828` baseline, delta `+.022995`, paired prompt-bootstrap 95% CI `[+.011596, +.034074]`, and both fixed class-retention simulations positive in 20/20 replicates. Because the only CV-to-Public observations are v12 `.586` → `.541` and v13 `.654` → `.560`, a single private candidate runtime/submission check is worthwhile to measure transfer; the `.771` public top remains the actual target.

## Local implementation and packaging

- Approved scope: [runtime spec](../specs/2026-11-15-mistral-spectral-private-notebook-runtime-spec.md). New source: `/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/notebooks/name-that-llm-private-baseline-v14-mistral-spectral-source/`; v13 source is preserved.
- Five primary-fold stage2 epoch-2 LoRA adapters and matching classifier/norm heads were packaged from completed checkpoints. Head export excludes optimizer and RNG state. Existing v13 dataset assets were copied to an isolated private staging tree; source artifacts remain unchanged.
- Package command: `./.venv/bin/python scripts/package_mistral_v14_assets.py --baseline-assets notebooks/name-that-llm-private-baseline/dataset-assets --run-dir artifacts/gpu03-mistral-7b-v0-1-openpool-v15/primary --output artifacts/mistral-v14-private-dataset-staging`.
- Package result: five folds, 61 files, 855,657,969 bytes. Integrity: 一致, verified by `sha256sum -c ASSET-SHA256SUMS`.
- Notebook builder: `./.venv/bin/python scripts/build_mistral_v14_notebook.py`. Static source validation passed for all code cells, fixed blend formula, private metadata, and disabled internet. v13 preservation check: 一致 via `sha256sum -c /tmp/mistral-v13-preserved.sha256`.

## Pending gates

- The Host141 64-row five-fold pilot passed on GPUs 1–2 (two RTX A4000, 15,974 MiB each). Per-fold load took 20.4–29.4 s and 64-row inference 9.1–11.8 s; peak reserved was 6,776 / 7,222 MiB, leaving over 8 GiB per card. The fixed 4,000-row Mistral-only projection with 1.25 margin is 1.754 hours; reserve and runtime gates passed. Input was the three unlabeled visible test rows repeated to 64, matching the v13 timing-probe policy. Result JSON: `/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/artifacts/mistral-v14-host141-pilot/pilot.json`.
- Three setup attempts exited before inference/GPU allocation: Host141 did not have the new script; the visible test file had only three rows; then one launch used the wrong staging prefix. The script/assets were staged, the spec clarified repetition of visible unlabeled test rows, and paths corrected. No weights, checkpoints, or other jobs changed.
- Host141's existing base cache matched all nine pinned files: 一致 via `ssh 141 'cd ...candidate10-mistral-7b-v0-1-hf && sha256sum -c /tmp/mistral-v14-base-files.sha256'`; model shard prefix `9742cb47`. Transferred bundle: 一致 via `sha256sum -c ASSET-SHA256SUMS`; fold-0 adapter prefix `052be7d0`. v13 source preservation: 一致 via `sha256sum -c /tmp/mistral-v13-preserved.sha256`; Notebook prefix `344b65ab`.
- No Kaggle push or submission was made. Kaggle write credential sources were absent (`KAGGLE_USERNAME`, `KAGGLE_KEY`, `KAGGLE_API_TOKEN`, configured credential files); credential values were not read. The connected Kaggle tools are read-only. Recheck official rules/leaderboard, privacy, runtime, and quota immediately before any Kaggle write.
- Current independent job: OLMo primary continues on Host142 GPU0; Host142 GPU1 is idle and was not used. The 02:40 JST checkpoint is recorded in the [OLMo log](2026-11-14-olmo2-7b-4bit-openpool-lora.md).
