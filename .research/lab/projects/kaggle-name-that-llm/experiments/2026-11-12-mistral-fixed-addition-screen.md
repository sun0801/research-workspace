---
date: 2026-11-12
project: kaggle-name-that-llm
type: prompt-grouped-oof-addition-screen
---

# Mistral-7B primary OOF: fixed addition to adopted blend

## Source and question

Using the existing approved [Mistral prompt-grouped spec](../specs/2026-11-08-mistral-7b-v0-1-prompt-grouped-spec.md) and its saved five-fold primary OOF, check whether its predictions add value to the adopted Qwen3-8B + Qwen3-1.7B + prompt-centered SVC probability blend. This is a fixed screen, not a tuned ensemble or an independent confirmation.

## Method

- Reused `scripts/analyze_probability_blend_addition.py` and its default baseline `artifacts/cpu-qwen-prompt-centered-svc-probability-ensemble-v1/primary/`.
- Formula: equal mean of the three baseline probability components plus Mistral row-wise softmax probabilities, each component weight 1/4. No weight fitting or public-LB selection.
- Alignment checks covered all 2,699 rows, five primary folds, IDs, labels, prompts, folds, and reproduction of each saved model's argmax. Paired bootstrap over 150 prompt groups: 5,000 replicates, seed 42.
- Command: `.venv/bin/python scripts/analyze_probability_blend_addition.py --candidate-run-dir artifacts/gpu03-mistral-7b-v0-1-openpool-v15 --output artifacts/gpu03-mistral-7b-v0-1-openpool-v15/primary/equal-mean-addition-screen.json --bootstrap 5000 --seed 42`.

## Result

- Existing baseline OOF BA: `.586408`.
- Mistral alone OOF BA: `.587566`.
- Fixed four-component equal-mean OOF BA: `.599769`, delta `+.013361`.
- Prompt-paired 95% CI for delta: `[+.001852, +.025215]`; all five augmented fold BAs were `.592593`, `.601852`, `.594444`, `.596296`, `.613602`.
- The existing Mistral standalone adoption gate versus prompt-centered SVC also passed: `.587566` vs `.501934`, primary paired 95% CI `[+.062961, +.107777]` (5,000 replicates, seed 42).

## Decision and limits

This primary-only evidence makes Mistral a strong confirmation candidate. It is not independent evidence because the model and fixed 1/4 addition were evaluated on the primary OOF. Do not create a Kaggle Notebook or submit this blend until Mistral passes the approved independent confirmation gate and the full submission requirements.

The prior confirmation attempt passed Host142 resource preflight but stopped before training: pilot metadata carries runner prefix `3bd614d9` while the current local runner is `7723b086`; the fixed config prefix remains `c04ff481`. Source inspection shows the uncommitted runner diff changes hash manifest/pilot-integrity and final-fit metadata, not the training loop. Preserve the previous pilot/primary outputs. After strict Host142 host-key verification and queue clearance, re-run the pilot with the current code on the spec's GPU1 and then run confirmation only if it passes. No model training, GPU job, Kaggle push, or submission occurred during this screen.


## Relation to the current best

The best saved Spectral primary OOF is `.664952`, so this Mistral four-component screen `.599769` is lower by `.065183` on the same primary rows. The fixed screen supports complementarity to the previous Qwen/SVC baseline only; it does not beat the current best and is not submission-ready. Any composition of Mistral with the Spectral correction would require its own fixed, prompt-grouped screen because the approved Spectral spec freezes its three-model input.
