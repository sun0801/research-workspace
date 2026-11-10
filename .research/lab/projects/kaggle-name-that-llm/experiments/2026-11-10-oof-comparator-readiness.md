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
