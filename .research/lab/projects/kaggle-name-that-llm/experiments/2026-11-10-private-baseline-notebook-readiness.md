---
date: 2026-11-10
project: kaggle-name-that-llm
type: private-notebook-readiness
---

# Private baseline Notebook readiness

## SVC asset staging

- Adopted prompt-centered SVC all-train model, metadata, and `model.joblib.sha256` were copied into `notebooks/name-that-llm-private-baseline/dataset-assets/svc/`.
- Source and staged model each returned `model.joblib: OK` under `sha256sum -c model.joblib.sha256`; recorded prefix `fb8d0ff5`.
- Loading the trusted joblib artifact for a read-only dependency inspection exposed its reference to `cpu_pipeline`. The Notebook could not load the SVC with the initial asset list because this module was absent. Copied the exact `src/cpu_pipeline.py` source into the private asset directory and inserted that directory into `sys.path` before SVC deserialization. The module defines the custom `function_text`/`shape_text` pipeline callables and imports only standard, NumPy, pandas, scikit-learn, and threadpoolctl dependencies.
- The local implementation environment reports scikit-learn `1.9.1`; staged SVC metadata records that version, and the Notebook now stops at startup if the offline runtime version differs. The benchmark-only Kaggle run remains the authoritative compatibility check; no Notebook has been pushed or run.

## Current submission gate

- Upload path: `notebooks/name-that-llm-private-baseline/dataset-assets/`. It currently contains only the SVC component and dataset metadata; Qwen3-8B and Qwen3-1.7B all-train files are not yet staged.
- Keep the dataset and Notebook private. Wait for the Qwen final-fit artifacts, complete the asset layout, perform the just-before-push official check, and run the benchmark-only Notebook. Only if its projected runtime is within nine hours should the fixed baseline be submitted once.
- No Kaggle object was created or pushed in this preparation.

## Qwen8B final-fit gate and hash-safe bundle

- Qwen8B candidate02 confirmation had five OOF fold files but no analyzer summary. Ran the existing local analyzer against the adopted SVC confirmation OOF: 2,699 rows, 150 prompt groups, 2,000 paired bootstrap replicates, seed 42. Qwen8B BA `.554561` vs SVC `.500818`, delta `+.053743`, 95% CI `[+.031481,+.074470]`; confirmation gate=`adopt`. Its existing primary summary is also adopted (BA `.566431`, lower CI `+.041871`). The final-fit runner's standalone primary/confirmation gates now pass.
- Updated `src/gpu_experiment.py` so future preflight/final-fit logs record only hash prefixes. New pilot JSON stores prefixes and points to `pilot-SHA256SUMS`; full checksums are written directly to that sidecar. Final bundles will include directly written `SOURCE-SHA256SUMS` and `SHA256SUMS`, verify both with `sha256sum -c`, and log the match, command, and submission hash prefix. The existing pilot refers to the previous runner revision, so the queued watcher will rerun the one-step pilot before the full fit.
- The 2026-11-10 operating amendment makes the adopted baseline Notebook the early priority. The registered Qwen14B watcher remains preserved for resumption after this baseline run; no running GPU job is interrupted.

## 2026-11-10 18:41 JST — queue 状態の補足

candidate09 GPU workerの起動を検知した。phase・GPU/RAMは未照合のため、Qwen8B final fitはHost142のGPU1 chainが解放された確認後に限る。READMEの現状欄と[host continuation log](2026-11-10-host-continuation-poll.md)を更新した。

## 2026-11-10 18:45 JST — queue 状態訂正

18:42のcandidate09 watcher logと現在のprocess listを照合した結果、candidate09はMistral03 watcher待ちで、GPU workerは未起動。18:41の「worker起動検知」はwatcherとworkerの取り違えだったため訂正する。Host142全体の次の30分pollは18:48。

## 2026-11-10 18:52 JST — baseline final-fit queue

30分pollでHost142 Mistral03 (GPU1)とQwen1.7B final fit (GPU0)が稼働し、RAM/VRAM安全床を満たすことを確認。candidate09にGPU workerはなく、優先度改訂に沿ってその待機watcherだけをSIGSTOP。Qwen8B baseline final-fit watcher PID `905369`を登録し、Mistral watcher終了後にpilot gateとfinal fitを行う待ち状態。Qwen14B watcherはbaseline資産が揃うまで再開しない。

## 2026-11-10 18:54 JST — final bundle interface review

Static source-to-Notebook comparison confirms the Qwen final-fit bundle writes `adapter/`, `tokenizer/`, `head.pt`, and `metadata.json`; the benchmark Notebook loads those same paths and classifier/norm keys. The output layout is compatible. This checks file/interface structure only; no model was loaded in Kaggle and no Notebook was pushed.

Further static comparison at 18:55 JST confirms the Notebook and Qwen runner use the same masked mean pooling layers `[2, 4, 6, 8, 12, 16, 20, 24]`, LayerNorm, dropout, and classifier shapes. No inference bundle change is required for architecture compatibility.

## 2026-11-10 19:00 JST — asset staging helper prepared

Added `scripts/package_private_baseline_assets.py` in the implementation repository. It requires both primary and confirmation OOF gates to be adopted, verifies the staged SVC and each source/destination bundle with `sha256sum -c`, requires Qwen/SVC class order equality, checks the Notebook and asset dataset remain private/offline-linked, stages atomically without overwriting a different bundle, and writes the aggregate checksum manifest directly to a sidecar. It performs no Kaggle upload or model inference. The Qwen bundles do not exist yet, so the helper has only received static review and has not been run.

## 2026-11-10 19:02 JST — asset visibility boundary clarified

The staging helper checks the local Notebook is private/offline and references the expected asset dataset slug. `dataset-metadata.json` does not encode Kaggle visibility; the helper cannot establish remote asset privacy. When uploading, explicitly create/version the dataset as private and verify its Kaggle visibility before using it. No upload has occurred.

## 2026-11-10 19:04 JST — upload-facing provenance included

Added `dataset-assets/PROVENANCE.md` with the Qwen3 model refs/versions, Open Pool v15 source/license, SVC training source, and competition rules link. Updated the Notebook README and made the asset packer refuse to proceed without this file. It will be included in the aggregate asset manifest. No Kaggle upload occurred.

## 2026-11-10 19:05 JST — staging preflight tightened

Extended the asset packer to require the Notebook's local metadata to remain private, Internet-off, GPU-enabled, TPU-disabled, L4, and attached to both intended official Qwen Model versions. This is a local metadata guard only; the Kaggle push must still use private visibility and verify the remote dataset/kernel state immediately before submission.

## 2026-11-10 19:07 JST — benchmark run and scored submission separated

Inspected the installed Kaggle CLI help/source. `datasets create` defaults to private (`public=False`); `--dir-mode tar` includes nested adapter/tokenizer folders. `kernels push` saves/runs a Notebook version, while a separate `competitions submit -k ... -v ... -f submission.parquet` calls the code-submission API. The benchmark-only version has no `submission.parquet`; local CLI source shows scored code submissions use a separate `competitions submit` API path. This supports using the benchmark version for runtime measurement, but Kaggle-side counting behavior must be checked at the required pre-push status review. Only the later final version should be submitted. Added these commands and privacy checks to the Notebook README. Before actual push/submission, refresh official rules/counts per the once-daily/immediately-before-operation policy.

## 2026-11-10 19:12 JST — private assets excluded from Git

The shared Kaggle workspace `.gitignore` had no rule for this upload folder. Added an exact ignore rule for `name-that-llm/notebooks/name-that-llm-private-baseline/dataset-assets/`; `git check-ignore -v` confirmed both the SVC model and upload-facing provenance file are ignored. The Notebook README now records this. The assets remain available locally for the explicit Kaggle private-dataset upload path.

## 2026-11-10 19:13 JST — manifest coverage guard added

Tightened `scripts/package_private_baseline_assets.py`: it now compares the exact file list in each Qwen bundle manifest against the bundle contents, so unlisted extra files and missing manifest entries stop staging. The aggregate asset manifest receives the same exact-file-set check on reruns. Static review only; no final model bundle is available yet, so the packer remains unrun.

## 2026-11-10 19:14 JST — dataset metadata filename confirmed

The Kaggle CLI package constant `DATASET_METADATA_FILE` is `dataset-metadata.json`, matching the upload folder; this was verified from the local installed CLI source. Its `datasets create --help` summary has a pluralized spelling, but the implementation uses the singular filename.

## 2026-11-10 19:15 JST — remote privacy verification path identified

The connected read-only Kaggle MCP exposes `get_dataset_info` and `get_notebook_info`. After private asset creation and Notebook push, use these to inspect the actual remote objects and confirm owner, visibility, and version; local metadata and CLI defaults alone do not prove remote privacy. The tools have not been called because no Kaggle object has been created.

## 2026-11-10 19:22 JST — explicit Kaggle execution timeout

Updated the private-baseline instructions to pass `--timeout 32400` to both benchmark and final `kaggle kernels push` commands. The installed CLI interprets this as session timeout seconds; this caps each run at nine hours per the current spec.

## 2026-11-10 19:24 JST — direct submission-limit query

The installed CLI provides `kaggle competitions submission-limits <competition> --json`, returning `num_today`, `num_total`, `num_allowed_now`, and lifetime-cap status. Added this as the exact pre-push/pre-submit daily allowance check in the Notebook README; verify Final count and current official LB separately at that same operation boundary.

## 2026-11-10 19:32 JST — runtime projection scope checked

Static source review confirms the benchmark-only Notebook times SVC load/probe and both Qwen model loads/inference, projects 4,000 hidden rows, adds a 25% margin and 30-minute fixed overhead, and stops before test inference if the estimate exceeds nine hours. This row count matches the previously recorded official Evaluation estimate of approximately 4,000 hidden passages. The final run still requires the Kaggle benchmark-only runtime result; no source change, push, or submission was made.

## 2026-11-10 19:35 JST — runtime gate follows final execution path

Further static audit found the final Notebook runs the timing probe first, unloads each Qwen model, and loads it again for test inference. Updated the gate to parse only test IDs for the exact row count, include probe plus full-test inference time, and count both Qwen load passes before applying the 25% margin and 30-minute allowance. The benchmark-only branch does not materialize test text or run inference on it. Notebook JSON parsed and all code cells compiled; this is a syntax check only, not a Kaggle runtime result. No model composition change, push, or submission.

The upload README now shows the explicit `kaggle kernels push ... --timeout 32400` command for both the benchmark-only and final versions, with the required daily allowance and official status checks immediately before each push.

It also requires read-only Kaggle MCP verification of the remote dataset's privacy after creation and the remote Notebook's privacy/version after each push. Local metadata and CLI defaults are not treated as proof of remote visibility.

## 2026-11-12 correction — interactive test row count

The earlier claim that reading `test.csv` IDs in an interactive Notebook gives the exact hidden row count was incorrect. Kaggle's official Data Description says interactive sessions contain three sample rows while the hidden scoring rerun has about 4,000. The local runtime projection now uses `max(4,000, visible test-ID rows)`; remote benchmark version 1 was already pushed with the older projection and its boolean gate must not be trusted without recalculating the probe timings at 4,000 rows. See the [2026-11-12 benchmark log](2026-11-12-baseline-benchmark-push.md).
