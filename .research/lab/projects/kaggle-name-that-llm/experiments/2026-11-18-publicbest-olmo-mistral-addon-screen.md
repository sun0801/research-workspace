---
date: 2026-11-18
project: kaggle-name-that-llm
type: experiment-log
spec: ../specs/2026-11-06-gpu-autonomous-first-place-spec.md#方針の改訂2026-11-16ユーザー承認
status: local-candidate-prepared-awaiting-public-684-runtime
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

No Kaggle push, competition submission, local GPU run, or new training was performed. First submit the unchanged `.684` public baseline and establish its public score/hidden runtime. Then run add-on candidates only when the measured parent-time-inclusive gate passes; prioritize this fixed OLMo2+Mistral composition based on the screen, with Mistral-only as a useful comparison. Report before any competition submission as required by the approved spec.
