---
date: 2026-11-10
project: kaggle-name-that-llm
type: evaluation-readiness
---

# Candidate11/13 OOF comparator readiness

## 確認日時・対象

- 2026-11-10 00:28 JST
- Implementation: `/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/src/gpu_analyze.py`
- Candidate configs: `configs/gpu11-qwen3-4b-base-openpool-v15.json`, `configs/gpu13-modernbert-large-openpool-v15.json`
- Candidate specs: [Qwen3-4B candidate11](../specs/2026-11-08-qwen3-4b-base-openpool-v15-host141-spec.md), [ModernBERT-Large candidate13](../specs/2026-11-08-modernbert-large-openpool-v15-host141-spec.md)

## Evidence

`gpu_analyze.py` refuses to analyze until it finds exactly five fold OOF files and 2,699 unique official train IDs. It then requires the baseline OOF to align on ID, prompt, fold, and true label. Its default baseline is the early 4-view CPU OOF (`artifacts/2026-11-06-cpu-cycle/07-05-function-view-candidate/oof.parquet`, BA `.384504101`). It accepts one alternate baseline at a time with `--baseline-path`.

Read-only inspection of the three complete baseline parquet files found 2,699 unique IDs and folds 0–4 in each. ID, prompt, fold, and true-label fields match exactly across all three:

| Baseline | OOF BA | Artifact |
|---|---:|---|
| Early CPU 4-view model | `.384504101` | `artifacts/2026-11-06-cpu-cycle/07-05-function-view-candidate/oof.parquet` |
| Adopted prompt-centered SVC | `.501933880` | `artifacts/cpu-openpool-prompt-centered-low-pool-weight-v15/primary/oof-all.parquet` |
| Current adopted Qwen + SVC blend | `.586408153` | `artifacts/cpu-qwen-prompt-centered-svc-probability-ensemble-v1/primary/oof-all.parquet` |

Candidate11 config lists only the early CPU model in `compare_to`; candidate13 lists the early CPU model and adopted Qwen blend. The active goal's candidate-selection rule must also protect the current stronger blend. Candidate11/13 partial OOFs remain incomplete (candidate11 through fold2; candidate13 through fold3 at the 00:26 poll), so no full analysis or adoption decision is valid yet.

## Evaluation procedure when OOF completes

Run the existing analyzer only after all five candidate folds exist. Compare each candidate separately to the early CPU model, adopted SVC, and current Qwen+SVC blend as required by its spec and current-best gate. Because each analyzer call writes to the candidate's `<split>/` directory and accepts only one alternate baseline, preserve each per-baseline report under a distinct comparator-named output directory before the next call. Keep all bootstrap replicates at or above the candidate spec minimum and seed 42; require the registered lower-bound gate for any adoption claim. Probability blending or complementarity requires its own nested prompt-grouped evaluation; a stronger single-model result than the CPU baseline alone is insufficient.

No runner/config/run was changed in this audit. It is evaluation planning and baseline metadata inspection only.

## 2026-11-10 00:45 JST partial-fold comparison

Candidate OOFs are stored on Host141 rather than Host142. The completed prediction-only parquet files were read to a temporary directory for this analysis; no candidate run, config, or checkpoint was changed. Candidate IDs were matched one-to-one to each full baseline, and prompt/fold/true-label alignment passed for all comparisons. The current candidate files contain 3/5 folds for candidate11 and 4/5 for candidate13. The following `GroupKFold`-partial OOF values and 2,000 prompt-level paired resamples (seed 42) are descriptive only; these incomplete subsets do not satisfy the full-primary adoption gate.

| Candidate / completed folds | Candidate BA | Comparator | Comparator BA | Delta | Partial 95% prompt-bootstrap CI |
|---|---:|---|---:|---:|---:|
| candidate11 / 0–2 (1,620 rows, 90 prompts) | `.532716` | Adopted SVC | `.490123` | `+.042593` | `[+.014815,+.070370]` |
| candidate11 / 0–2 | `.532716` | Qwen + SVC blend | `.580864` | `−.048148` | `[−.066667,−.029012]` |
| candidate13 / 0–3 (2,160 rows, 120 prompts) | `.492130` | Adopted SVC | `.500000` | `−.007870` | `[−.029167,+.014826]` |
| candidate13 / 0–3 | `.492130` | Qwen + SVC blend | `.581944` | `−.089815` | `[−.112500,−.068519]` |

Candidate11 is above SVC on these three folds but below the stronger current blend; any blend claim needs a separate nested prompt-grouped evaluation. Candidate13 is below both comparators in these four folds. Keep both registered runs intact until their full primary outputs complete, then apply the full-fold gates and the current-best comparator. No adoption/confirmation/Notebook decision is made from these partial intervals.

## 2026-11-10 01:10 JST analyzer write-path check

Read-only inspection of `src/gpu_analyze.py` confirms there is no output-directory option. Every call writes the six report files (`oof-all.parquet`, `class-recall.csv`, both word-length reports, `confusion-matrix.csv`, `summary.json`) to `<run-dir>/<split>/`, so successive `--baseline-path` calls overwrite the preceding comparator report. After all five fold OOFs are present, run one comparator at a time with `--split primary --bootstrap 2000 --seed 42`; after each successful run, archive those six files under a comparator-specific subdirectory such as `<run-dir>/primary/comparators/{early-cpu,adopted-svc,current-qwen-svc-blend}/` before starting the next call. Keep the canonical per-fold OOFs untouched. The full analysis must show 2,699 rows and 150 prompt groups, pass exact ID/prompt/fold/label alignment, and be interpreted using the registered prompt-paired interval against the current blend. Candidate11's restricted config comparison and candidate13's listed comparators do not replace this current-best check.

The analyzer also reads official passage text from its code-defined `ROOT/data/train.csv`. Host142 was initially preferred because all three complete baseline OOF files were confirmed local there. Once a Host141 candidate's primary process exits and all five fold OOFs are final, transfer only those five prediction parquet files into a temporary analyzer run directory on Host142. Do not transfer model weights, checkpoints, or the implementation environment.

## 2026-11-10 02:10 JST Host141 fallback readiness

A read-only Host141 poll confirms `src/gpu_analyze.py` and official `data/train.csv` are already present, as is the adopted SVC OOF at `artifacts/cpu-openpool-prompt-centered-low-pool-weight-v15/primary/oof-all.parquet` (67 KB). The expected paths for the early CPU OOF (`artifacts/2026-11-06-cpu-cycle/07-05-function-view-candidate/oof.parquet`) and current Qwen+SVC blend OOF (`artifacts/cpu-qwen-prompt-centered-svc-probability-ensemble-v1/primary/oof-all.parquet`) are not present on Host141. Candidate11/13 OOFs remain incomplete, so no analyzer was run.

This makes Host141 a viable CPU evaluation host once the missing baseline prediction files are found locally or transferred from a source whose identity is verified. After the five candidate fold files are final, run the required three one-at-a-time comparisons there only if all three baseline OOFs are available and exact ID/prompt/fold/label alignment passes. Keep the candidate run directories untouched and use a temporary analyzer run directory; do not transfer weights, checkpoints, or the training environment. Host142 remains an alternative after its host key is trusted.

## 2026-11-10 02:24 JST local evaluation route

The implementation checkout at `/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm` has `src/gpu_analyze.py`, official `data/train.csv`, its `.venv/bin/python`, and all three complete comparator OOFs listed above (early CPU 4-view, adopted SVC, and current Qwen+SVC blend). The required baseline ID/prompt/fold/label alignment was already verified in this note. Host141's active candidate11/13 runs remain incomplete, so no candidate OOF was transferred and no analysis was run.

When a registered candidate completes all five primary folds on Host141, retrieve only its five prediction OOF parquet files into a fresh temporary run directory under `/tmp` and run the existing local analyzer with one `--baseline-path` per invocation (`--split primary --bootstrap 2000 --seed 42`). Archive each invocation's six outputs under comparator-specific directories before the next call, because the analyzer writes into `<run-dir>/<split>/` and would otherwise overwrite the prior report. Keep model weights, checkpoints, and implementation environment on their current hosts. This local route avoids dependence on the still-untrusted Host142 SSH identity and does not allocate GPU resources.

## 2026-11-10 16:45 JST full-fold candidate13 decision

Host141 candidate13 completed all five primary OOF folds and its runner/wrapper were absent on the 16:45 poll. Only the five prediction parquet files were staged under `/tmp/ntllm-c13-oof-20261110-1645`; no weights or checkpoints moved. The analyzer passed the full 2,699-row / 150-prompt OOF and exact ID, prompt, fold, and label alignment checks. All comparisons used 2,000 prompt-grouped paired bootstrap replicates, seed 42:

| Comparator | Candidate BA | Comparator BA | Delta | 95% paired CI | Gate |
|---|---:|---:|---:|---:|---|
| Early CPU 4-view | `.499734` | `.384504` | `+.115230` | `[+.096659,+.134816]` | Positive, but superseded by current baselines |
| Adopted prompt-centered SVC | `.499734` | `.501934` | `−.002200` | `[−.022593,+.017778]` | Reject |
| Current Qwen+SVC blend | `.499734` | `.586408` | `−.086674` | `[−.105556,−.067407]` | Reject |

Therefore candidate13 is not adopted and no confirmation is run. Its six-file comparator reports are preserved in `/tmp/ntllm-c13-analyze-20261110-1645/primary/comparators/{early-cpu,adopted-svc,current-qwen-svc-blend}` for this session; this Markdown contains the durable decision. Host141 candidate11 remained active on GPU2 with fold3 newly complete and fold4 continuing. CPU-best `model.joblib` rehashed to the recorded SHA-256. No GPU, candidate config, Kaggle object, or submission changed.

## 2026-11-10 17:54 JST candidate11 OOF transfer attempt

Host141's candidate11 runner/wrapper are absent and all five primary fold OOF parquet files are present; the run completed naturally. A transfer attempt for only those five prediction files failed because this environment could not resolve the configured Host141 alias. No candidate files were copied, and no weights, checkpoints, jobs, or host allocations were changed. Full comparator analysis remains pending until Host141 is reachable; then use the existing local analyzer procedure above against early CPU, adopted SVC, and current Qwen+SVC blend with 2,000 prompt-paired bootstrap replicates (seed 42).

## 2026-11-10 18:00 JST route diagnosis

`hostname` identifies the current executor as `142-X10DAi`, and `getent hosts 142-X10DAi` resolves it to local loopback. `141-X9DAi` has no name-service result. The comparator code, official train data, environment, and three complete baseline OOFs are already available in the local implementation checkout, so the only missing input for candidate11 analysis is its five prediction parquet files from Host141. Once retrieved, run the documented analyzer locally; do not transfer weights/checkpoints or modify either host's jobs.

## 2026-11-10 18:05 JST full-fold candidate11 decision

Resolved Host141 via `141-X9DAi.local` / `10.10.40.141` and retrieved only its five completed `primary/fold-{0..4}/oof.parquet` prediction files. `sha256sum -c` against a temporary source manifest returned `OK` for all five; recorded prefixes: `1cac54a9`, `8138a3bc`, `a2d12266`, `b37a6fc7`, `e005899b`. No model weights or checkpoints moved. The local analyzer verified 2,699 rows, 150 prompt groups, and baseline alignment; each comparison used 2,000 prompt-paired bootstrap replicates, seed 42:

| Comparator | Candidate BA | Comparator BA | Delta | 95% paired CI | Decision |
|---|---:|---:|---:|---:|---|
| Early CPU 4-view | `.542329` | `.384504` | `+.157825` | `[+.137399,+.180455]` | Positive, superseded by stronger baselines |
| Adopted prompt-centered SVC | `.542329` | `.501934` | `+.040395` | `[+.018531,+.061588]` | Positive, but below current best |
| Current Qwen+SVC blend | `.542329` | `.586408` | `−.044079` | `[−.057427,−.029681]` | Reject |

Candidate11 is not adopted under the current-best gate and confirmation is skipped. Its six report files for each comparator are preserved in `/tmp/ntllm-c11-oof-20261110-1800/artifacts/gpu11-qwen3-4b-base-openpool-v15/primary/comparators/{early-cpu,adopted-svc,current-qwen-svc-blend}` for this session; this Markdown is the durable decision. No candidate config, job, Kaggle object, or submission changed.
