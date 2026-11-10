---
date: 2026-11-09
project: kaggle-name-that-llm
spec: ../specs/2026-11-09-spectral-cluster-meanfield-primary-spec.md
status: primary-pass-confirmation-pending
tags: [experiment, prompt-clustering, mean-field, primary-oof, robustness]
---

# Spectral cluster mean-field primary screen

## Fixed candidate

Applied the version-10 Spectral Gaussian Notebook's fixed local at-most-once mean-field correction to the adopted Qwen3-8B + Qwen3-1.7B + prompt-centered SVC primary OOF probabilities. Text-only clusters use `normalised_content_groups` defaults per saved outer fold. The correction uses source defaults `gamma=0.55`, cluster temperature `0.65`, four iterations, and final temperature `0.72`; it preserves singleton/oversize clusters unchanged. It omits the Notebook's orthographic masks and all global Sinkhorn scaling, so it does not enforce equal global class marginals.

The baseline probability argmax exactly reproduced the saved 2,699-row `prediction` column before candidate scoring. Each fold's clusterer/correction received only held-out text and probabilities; `prompt_id` was used only for the canonical paired bootstrap and diagnostic ARI. No values were tuned.

## Primary result

| Metric | Result |
|---|---:|
| Raw adopted blend BA | 0.586408 |
| Fixed mean-field candidate BA | **0.664952** |
| Delta | **+0.078543** |
| Prompt-cluster paired bootstrap (5,000; seed 42) 95% CI | **[+0.065968, +0.090741]** |

All five fold deltas are positive. Fold BA rises from `.564815/.583333/.594444/.585185/.604406` to `.646296/.668519/.685185/.655556/.669029`. Inferred cluster counts remain 39–52 per 540-row fold, with diagnostic ARI `.9421–.9646`; the known over-splitting limitation remains.

## Unequal-class-count sensitivity

The predeclared simulation randomly assigned class retention rates and independently removed rows, then reclustered only the retained texts. This generated incomplete prompt-like groups and unequal class totals; labels were not passed to clustering or correction.

| Scenario | Class retention range | Replicates | Mean BA delta | Positive replicate fraction | Mean cluster ARI |
|---|---:|---:|---:|---:|---:|
| Mild | 0.65–1.00 | 20 | +0.066498 | 20/20 | 0.950909 |
| Moderate | 0.30–1.00 | 20 | +0.047267 | 20/20 | 0.952384 |

The primary gate passes. These synthetic patterns are a sensitivity check, not an estimate of hidden-test performance. The source algorithm still uses within-cluster diversity pressure, whose fit to hidden prompt completeness is not known.

## Decision and next step

Advance to the registered independent confirmation only. The Qwen confirmation watcher PID `3605360` is alive; at the 07:13 JST artifact check, Qwen04 had saved folds 0–2 (latest fold2 OOF 06:14) and Qwen8B folds 0–1 (latest fold1 OOF 05:15). Their runners were alive and no complete confirmation ensemble existed, so the mean-field confirmation cannot yet be scored. Use the same frozen transform and both predeclared retention schedules after the fixed ensemble confirmation OOF is complete. Do not adopt for submission unless that confirmation passes the registered paired-bootstrap and sensitivity gates; verify full hidden-test behavior and Kaggle runtime separately.

CPU-only, one thread; no GPU process or queue changed and no Kaggle object/submission created. Runner SHA-256: `00a0b6b8db59f09dccde4d504401ede455c078a31933f5c9127780847fd606e2`. Summary SHA-256: `e34d158225cc982c6f664e7e288782fa6efbb2df621bc1caf601a52b88e42252`. OOF predictions SHA-256: `cc97822b351ac64ce262fbdda6f43c3a2fd79cdf6a9bbd56050bb6458884ddd0`. Artifacts are under `artifacts/cpu-spectral-cluster-meanfield-v1/` in the external Kaggle project.

## Confirmation readiness check — 2026-11-09 16:14 JST

The registered Spectral confirmation waiter (Host142 PID `137077`) is alive and unchanged. Its prerequisite fixed-blend confirmation OOF directory is not present yet. The upstream Qwen-blend watcher PID `3605360` is alive; its log through 16:11 reports that it is waiting for the Qwen1.7 GPU lock. Thus the Spectral evaluator has not started and remains queued behind the registered confirmation chain. The Qwen04 confirmation watcher PID `3771620` also remains alive. The 16:12 host poll showed all five authorized training processes alive, all GPUs assigned, and both hosts above the RAM floor. No queue or process was changed.
