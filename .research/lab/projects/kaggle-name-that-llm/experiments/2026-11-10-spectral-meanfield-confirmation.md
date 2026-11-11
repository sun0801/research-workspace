---
date: 2026-11-10
project: kaggle-name-that-llm
spec: ../specs/2026-11-09-spectral-cluster-meanfield-primary-spec.md
status: primary-and-independent-confirmation-gates-passed
tags: [experiment, prompt-clustering, mean-field, confirmation]
---

# Fixed Spectral cluster mean-field confirmation

## Procedure

After the five independent Qwen8B, Qwen1.7B, and adopted SVC confirmation OOFs completed, the pre-registered fixed ensemble was evaluated with the existing `src/gpu_probability_ensemble.py` command (`--split confirmation --bootstrap 2000 --seed 42`). The result was written under the private/ignored implementation artifact `artifacts/cpu-qwen-prompt-centered-svc-probability-ensemble-v1/confirmation/`.

The existing frozen evaluator `scripts/evaluate_spectral_cluster_meanfield_confirmation.py` then applied the unchanged primary transform to that independent blend OOF. The evaluator used one CPU thread and its 0.25-second resource monitor; no GPU job, model, or Kaggle object was changed. The user-requested `--guard 15` passed at 2026-11-10 16:54:22 JST (five-hour remaining 99%, weekly 52%) before this confirmation step. The Qwen blend confirmation's previous auto-watcher had exited at 04:42 JST because its recorded rate-limit event was stale; with a current passing guard, the fixed CPU confirmation command was resumed directly.

## Qwen + SVC blend confirmation

The complete 2,699-row, 150-prompt confirmation blend achieved balanced accuracy `.567870`, versus `.500818` for the same-split adopted SVC. Delta was `+.067052`; 2,000 prompt-paired bootstrap replicates (seed 42) gave 95% CI `[+.045917,+.087461]`. The lower bound is positive, so the registered blend confirmation gate passes. The blend also exceeded each component on confirmation: versus Qwen8B delta `+.013308`, CI `[+.002222,+.022578]`; versus Qwen1.7B delta `+.036679`, CI `[+.024444,+.048551]`.

## Frozen mean-field confirmation

The fixed text-only clustering and mean-field transform from the primary screen achieved BA `.653828` versus the unchanged blend argmax `.567870`, delta `+.085958`. The 5,000 prompt-cluster paired bootstrap replicates (seed 42) gave 95% CI `[+.072993,+.098889]`. The frozen sensitivity checks also passed:

| Retention scenario | Range | Replicates | Mean BA delta | Positive replicates |
|---|---:|---:|---:|---:|
| Mild | 0.65–1.00 | 20 | `+.072351` | 20/20 |
| Moderate | 0.30–1.00 | 20 | `+.058307` | 20/20 |

Both preregistered primary and confirmation gates pass. This supports retaining the fixed correction as an OOF candidate; it does not establish public/private leaderboard performance. Public LB was `.755` at the refresh on 2026-11-10, while the confirmation BA was `.653828`. No Notebook, Kaggle object, or submission was created.

Artifacts remain in the implementation checkout, not this workspace: `artifacts/cpu-qwen-prompt-centered-svc-probability-ensemble-v1/confirmation/` and `artifacts/cpu-spectral-cluster-meanfield-confirmation-v1/`. Spectral confirmation summary SHA-256: `99fb73f3cbc6bbd6f273f8b552bd39d48a973277d1030d7f29b3dc33c4796b1c`; processed OOF SHA-256: `7d8540b4dcfeb2bf168cf2c35379cd80519ac2a1d8d4bab35e1eb881030763e0`; evaluator SHA-256: `a0a371a11a7cd79fd3d9da46006e93eece4b2310c4449ad474e4b49954ae404c`. Peak RSS was 260,603,904 bytes; minimum available RAM was 221,720,854,528 bytes, both within the registered limits.

## Competition and host checkpoint — 2026-11-10 16:57 JST

Official Kaggle MCP reported 5,310 teams. Public leaderboard leader James Liebel scored `.755` at 00:34 UTC; the next scores were `.752`. Rules remain five submissions/day and at most two final submissions. Timeline gives Jan 13, 2027 23:59 UTC; Notebook-only, Internet-disabled, <=9-hour and `submission.parquet` requirements are unchanged.

Host141 candidate11 PID `2439031` remained active on GPU2; fold3 OOF was newly complete and fold4 remained in progress. Candidate13 exited naturally after its five folds. Host142 Mistral03 PID `603688` remained active on GPU1, with its registered watcher PID `3743539`; Qwen14B watcher PID `3748103` waited behind it. Host142 GPU0 and Host141 GPU1 were idle, but registered jobs remained active. Resource floors passed on both hosts. No host was stopped or reallocated.
