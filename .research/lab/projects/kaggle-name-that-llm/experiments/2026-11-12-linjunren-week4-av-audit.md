---
date: 2026-11-12
project: kaggle-name-that-llm
type: public-source-audit
status: rejected
tags: [public-notebook, adversarial-validation, open-pool, prompt-grouped]
---

# Lin Junren — NTL Week4 Adversarial Validation audit

## Decision

**(b) 試さない。** The notebook's newest reported Public LB point is still pending; the only previous result it cites is `.398`, far below the current official leader `.768`. Its production plan is another Open Pool 4-view LinearSVC variant, substantially overlapping our existing Open Pool SVC work. The AV diagnostics are informative, but do not establish a path to a competitive score or an OOF gain over our current `.653828` confirmation best / `.689791` Mistral-Spectral primary screen.

## Source and evidence

- [Kaggle Notebook](https://www.kaggle.com/code/linjunren1016/ntl-week4-av), `linjunren1016/ntl-week4-av`, public version 1, CPU-only, Internet disabled; competition data plus `crtproduction/name-that-llm-open-pool`.
- Search listed a Nov 12 run; Notebook metadata's `last_run_time` instead reports Nov 9. The v1 session status is `COMPLETE`, and the available output log was inspected.
- The executed diagnostics report text-level train-vs-pool AV AUC `0.9789 ± 0.0014` on a 30k pool sample; 45-feature typography AV AUC `0.4696`; and Spearman correlation between `style_score` and AV score `-0.534` (`n=30,000`). Filtering `flag_kb_proxy` left 139,155 rows; sorting by `style_score` selected 59,994 rows (3,333/class).
- Notebook markdown describes the preceding random-40k pool submission as Public `.398` and says the new 60k/style-score submission is pending. The inspected v1 output contains no newer Public score and no independent OOF score for this policy.
- The style-feature migration diagnostics are author-run evidence, not an evaluation of this dataset-selection policy against our current OOF. Dataset license is listed as CC BY-SA 4.0; this audit did not download or use the dataset.

## Relevance and limits

The selection rule filters `flag_kb_proxy`, then takes the highest `style_score` per class, with 19 typography features and a 4-view LinearSVC. Our existing Open Pool candidate already evaluates the same named public pool and related SVC features with prompt-grouped folds and foldwise near-prompt/exact-text exclusions. The public notebook's AV result could motivate a new registered selection-policy experiment, but its in-sample or public claims do not show that it improves our registered prompt-grouped OOF or current best. With the only cited Public result at `.398` and the new result pending, no new experiment is registered from this source.

No source code was run locally, no external data/model was fetched, and no Kaggle push or submission was made.
