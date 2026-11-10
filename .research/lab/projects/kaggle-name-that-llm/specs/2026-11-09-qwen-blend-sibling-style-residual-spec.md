---
date: 2026-11-09
project: kaggle-name-that-llm
source: active-goal / Areeb Ali public Notebook v2 component
status: approved-under-active-goal
approval_basis: 2026-11-06-gpu-autonomous-first-place-spec
execution_status: rejected-primary
tags: [spec, postprocessing, sibling-style, cpu, prompt-grouped]
---

# Qwen blend sibling-style residual primary screen

## Rationale and evidence boundary

The current accepted primary blend is Qwen3-8B + Qwen3-1.7B + prompt-centered SVC, BA `0.586408`. Areeb Ali's public Notebook [0.673 | I'M BETTER !](https://www.kaggle.com/code/areebbb/0-673-i-m-better), current version 2, includes a family-local stylometric classifier that conserves each provider family's score mass and gates changes toward uncertain sibling labels. Its title/result provenance is unresolved and its broader pipeline has substantial external dependencies; only this text-only residual mechanism is screened independently. See [source audit](../experiments/2026-11-09-areeb-0-673-notebook-audit.md).

The same general family-local style idea was previously evaluated on an older SVC base and failed its strict positive-CI gate (delta `+0.007405`, 95% CI `[-0.001481,+0.016664]`). A separate fold-local typography mask changed only two rows on the current Qwen base and also failed its gate. This screen tests whether the fixed, soft within-family residual transfers to the stronger current blend; the primary split has already been inspected for other candidates, so any positive result is a screen only and requires the independent confirmation split without tuning.

## Frozen candidate

- Baseline: the saved `primary` probabilities and OOF rows from `artifacts/cpu-qwen-prompt-centered-svc-probability-ensemble-v1/primary/`. Reproduce its `prediction` column exactly before scoring. Align all features, probabilities, labels, and fold IDs by official `id`; class order is the saved 18-label order.
- For each of the five outer prompt-grouped folds, fit style classifiers using only official outer-training rows. `prompt_id` is used only for inner group folds and paired-bootstrap clusters, never as a prediction feature or inference-time routing signal.
- Reimplement the public v2 `sibling_style.py` fixed features: token/character/sentence/line lengths and dispersion, lexical diversity, long-token ratio, uppercase/digit/non-ASCII/whitespace/newline rates, fixed punctuation/format markers, and fixed common-word rates. Do not add, remove, or select features after observing results.
- Provider families and regularization are fixed: `claude` (`C=0.003`), `gemini` (`C=0.003`), `gpt` (`C=0.003`), `glm` (`C=0.03`). Qwen and Kimi singleton classes receive no family residual.
- Within each family, estimate style-head balanced accuracy from 5-fold `GroupKFold(prompt_id)` OOF predictions on the outer-training rows. Set reliability to `clip((inner_BA - 1/K)/0.15, 0, 1)`, where `K` is the number of sibling classes. Fit a final style head on the full outer-training family rows.
- Convert baseline probabilities to log scores. For each validation row and family, compute the top-1 minus top-2 margin of the baseline conditional family probabilities. Use `gate=clip((0.65-margin)/0.65,0,1)` and `alpha=0.10*reliability*gate`. Mix the baseline conditional probabilities with the final style-head probabilities at this fixed alpha, then restore the original family probability mass exactly. Apply every family head to every validation row; no held-out labels may route or trigger a correction.
- Do not use any external passages/weights, A/B annotation data, inferred prompt clusters, one-to-one prompt cardinality, Sinkhorn, global class priors, or test-set statistics.

## Evaluation and decision gate

- Primary: all 2,699 rows / 150 prompt groups, official balanced accuracy against the unchanged baseline on identical rows; report five fold scores, class recall, changed predictions by family, style-head inner OOF BA/reliability, finite-probability checks, and family-mass conservation error.
- Use 5,000 paired prompt-cluster bootstrap replicates, seed 42, through the canonical `gpu_analyze.paired_prompt_bootstrap` implementation. No thresholds, families, or candidate versions may be selected on this screen.
- Advance to the independently assigned `confirmation` split only if the full primary paired-bootstrap 95% CI lower bound is strictly above zero and all 18 labels are represented in each outer fold. Otherwise reject this residual for the current Qwen blend and do not run confirmation.
- A primary pass does not imply adoption, hidden-test performance, or a Kaggle Notebook. Confirmation must use the same frozen method and complete fixed Qwen04 + Qwen8B + SVC confirmation OOF when available. Require the confirmation paired-bootstrap lower bound above zero before further adoption/runtime work.

## Scope and reproducibility

- Implement an independent CPU-only evaluator in `/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/src/evaluate_qwen_blend_sibling_style_residual.py`; write only to the new ignored output directory `artifacts/cpu-qwen-blend-sibling-style-residual-v1/` and refuse to overwrite it.
- Limit the evaluator to two CPU threads; monitor its RSS (must remain <=32 GiB) and host `MemAvailable` (must remain >=16 GiB). No GPU, Kaggle write, notebook creation, submission, external data, or changes to existing OOF/base-model artifacts.
- Record script/input hashes, exact command, runtime, resource peak, aligned OOF predictions, summary, and diagnostics. Preserve all prior candidates and active GPU jobs.
