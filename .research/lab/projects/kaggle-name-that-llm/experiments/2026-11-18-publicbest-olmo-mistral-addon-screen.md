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
