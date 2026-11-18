---
date: 2026-11-18
project: kaggle-name-that-llm
type: experiment-log
spec: ../specs/2026-11-06-gpu-autonomous-first-place-spec.md#方針の改訂2026-11-16ユーザー承認
status: private-preview-complete-awaiting-baseline-score-runtime
---

# Fixed OLMo2 + Mistral addition for the `.684` public baseline

## Rationale and fixed screen

The Mistral component has independent five-fold confirmation on the local `.586408` primary baseline (BA `.676823`, delta `+.022995`, paired-bootstrap lower bound `+.011596`). Existing OLMo2 primary logits and the `.586408` baseline probability arrays also support a fixed composition screen. The OOF files align on 2,699 IDs, labels, 150 prompts, and folds; each component's logits reproduce its saved hard-label predictions. No training or GPU work was done for this screen.

Using the repository's `gpu_analyze.paired_prompt_bootstrap` with 5,000 replicates and seed 42, the fixed formulas gave:

- Base: BA `.586408`.
- Mistral: `0.75 * P_base + 0.25 * P_Mistral`; BA `.599769`, delta `+.013361`, 95% paired-prompt CI `[+.001852,+.025215]`.
- OLMo2: `softmax(log(P_base) + 0.25 * log(P_OLMo))`; BA `.595309`, delta `+.008901`, CI rounds to `[−.000000,+.017795]`.
- OLMo2 then Mistral: apply the fixed OLMo2 log-probability addition, then `0.75 * P_after_OLMo + 0.25 * P_Mistral`; BA `.602724`, delta `+.016316`, CI `[+.004815,+.027876]`.

This screen uses the older `.586408` base, not the new `.684` Notebook's OOF predictions. It ranks the composition for an LB check but does not establish its value on the `.684` parent; public LB remains the adoption criterion.

## Prepared candidate and gate

Prepared private/offline Notebook `suntree0801/name-that-llm-ntl684-mistral-olmo-addon`, based on the unchanged `.684` parent code cells 1–54. The OLMo2 fixed log-probability addition executes first; the Mistral NF4 fixed probability blend preserves that updated logit. The 64-row T4 pilot and cumulative runtime projection include all elapsed parent and OLMo2 work and stop before hidden test inference if the 8-hour internal gate fails. Static checks passed for parent-cell identity, added-cell syntax/order, and private/GPU-enabled/Internet-disabled metadata. Implementation commit: `e9bc04e`.

At the initial local-screen checkpoint, no Kaggle push, competition submission, local GPU run, or new training had been performed. The unchanged `.684` baseline was then submitted to establish its public score/hidden runtime. Run add-on candidates only when the measured parent-time-inclusive gate passes; prioritize this fixed OLMo2+Mistral composition based on the screen, with Mistral-only as a useful comparison. Report before any competition submission as required by the approved spec.

## Private preview

At 12:32 JST on 2026-11-18, pushed private kernel v1. Kaggle canonicalized the slug from the title to `suntree0801/name-that-llm-ntl684-olmo2-mistral-nf4-add-on`; remote readback confirms private, GPU enabled, Internet disabled, and T4. Remote cells 1–54 match the unchanged parent and cells 56–57 contain OLMo2 then Mistral. The initial slug warning was resolved locally by aligning `id` and `code_file` to that canonical slug (implementation commit `5cb827a`); the already-running remote version was not restarted.

Preview reached `COMPLETE`. `submission.parquet` has three rows, columns `id,model`, no nulls or duplicate IDs, valid label `claude-fable-5`, and exactly matches the unchanged baseline preview. The session reaches notebook conversion/output in about 22.75 seconds. `submission.mode.json` says `exact_public_format_preview`, `model_weights_loaded=false`, and `hidden_runtime_verified=false`; therefore the T4 pilot, add-on inference, resource gate, and hidden runtime have not run. The candidate remains pending the unchanged `.684` baseline score/runtime before its scoring submission.

## 2026-11-18 13:24 JST — supplementary k=2 OOF screen

Audited [Yuki Kaneko's validation-design Notebook v1](https://www.kaggle.com/code/yukikanek0/name-that-llm-validation-design). It samples two held-out responses per prompt from already prompt-grouped OOF predictions. The Notebook reports leaderboard-correlation `.13` for full-group CV versus `.91` for k=2 across its own 15 submissions; this self-reported correlation was not independently reproduced. We used the k=2 sampler only as a secondary sensitivity screen; it does not replace the existing prompt-grouped OOF gate or Public LB adoption check.

Reconstructed the fixed `.586408` base/Mistral/OLMo probabilities from saved fold artifacts. All 2,699 IDs, five fold assignments, class orders, and component argmax predictions matched; the standard full OOF scores reproduced the existing screen. For 150 prompts (17–18 rows each), 1,000 paired draws sampled two rows per prompt without replacement (seed 123):

| Candidate | Full OOF BA | k=2 mean BA (draw SD) | Paired delta vs base (draw SD) | Positive draws |
|---|---:|---:|---:|---:|
| Base | `.586408` | `.586332` (`.024830`) | — | — |
| Mistral | `.599769` | `.600795` (`.024984`) | `+.014463` (`.017149`) | 800/1000 |
| OLMo2 | `.595309` | `.595754` (`.025322`) | `+.009422` (`.012991`) | 756/1000 |
| OLMo2 + Mistral | `.602724` | `.603425` (`.024489`) | `+.017093` (`.016366`) | 851/1000 |

Draw SD is sampling variability, not a confidence interval. This confirms that the fixed composite remains the strongest of these old-base OOF screens under the k=2 view. It still does not estimate performance on the `.684` parent or establish an LB gain; retain the prepared candidate order pending the baseline's hidden runtime and score.

## 2026-11-18 13:35 JST — TF-IDF sibling-pair postprocess screen

From the same public Notebook v1, tested its batch-only postprocess: build TF-IDF cosine neighbors, greedily pair top-5 links, then zero the lower-confidence class when both rows in a pair share the same top-1. On each of 100 seed-777 k=2 samples, prompt IDs were used only to draw/evaluate the two-row pairs; the pairing algorithm saw only text. Mean pair recovery was precision `.9723`, recall `.9563` over about 147.5 greedy pairs per 150 true pairs.

| Base OOF probabilities | Raw k=2 BA | After pair postprocess | Paired delta (draw SD) | Positive draws |
|---|---:|---:|---:|---:|
| `.586408` base | `.583159` | `.586977` | `+.003818` (`.005998`) | 77/100 |
| Base + Mistral | `.596763` | `.601345` | `+.004582` (`.007335`) | 70/100 |
| Base + OLMo2 + Mistral | `.598969` | `.603591` | `+.004622` (`.006842`) | 73/100 |

The draw SD is sampling variability, not a confidence interval. This is an old-base simulation, and its `.684` interaction/runtime is unknown. Keep it as a separate low-cost LB-check candidate after the unchanged baseline and highest-priority fixed OLMo2+Mistral candidate; Public LB decides adoption.

## 2026-11-18 13:50 JST — `.684` + TF-IDF sibling-pair private candidate

Prepared and pushed private kernel v1 `suntree0801/name-that-llm-ntl684-tf-idf-pair-add-on`, using the already-screened TF-IDF sibling postprocess. The unchanged first 55 source cells match the `.684` + OLMo2/Mistral candidate; the final cell adds only the batch pairing postprocess. Authenticated remote pull confirms `is_private=true`, GPU enabled, Internet disabled, and `NvidiaTeslaT4`; pulled source-cell text matches the local source exactly. Local implementation commits: `9fa3e49` and slug alignment `2ddc493`.

Initial kernel status was `RUNNING`. The remote execution has not yet been polled on its 30-minute cadence; preview completion, hidden runtime, and artifact checks are not established. No competition submission was made for this candidate. The unchanged `.684` baseline remains submission ref `58492917`, accepted at 12:30:59 JST and last observed `PENDING` at 13:34 JST; do not duplicate it. Next status check is due at/after 14:04 JST, then use the baseline score/runtime to choose the next candidate.

The CPU pairing probe took `1.238 s` on 2,699 rows; scaling by row count estimates about `1.83 s` for 4,000 rows (arithmetic corrected on 2026-11-18). This covers only the TF-IDF pair postprocess and does not establish Kaggle T4 runtime for the full Notebook.
