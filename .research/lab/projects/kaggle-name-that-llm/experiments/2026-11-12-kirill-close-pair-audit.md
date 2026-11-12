---
date: 2026-11-12
project: kaggle-name-that-llm
type: public-notebook-audit
decision: (b) 試さない
tags: [audit, public-notebook, pair-correction]
---

# Kirill Tymchishin “LoRA + Trained27 | Evidence for Close Calls”

**最終判定: (b) 試さない。** close-pair補正のみを固定条件でスクリーニングしたが、適格pairは1組で予測変更はなく、BA差は0だった。

- Notebook: [current version](https://www.kaggle.com/code/kirilltym/lora-trained27-evidence-for-close-calls) (version 18 at retrieval); author says version 17 scored Public `.684` ([version 17](https://www.kaggle.com/code/kirilltym/lora-trained27-evidence-for-close-calls?scriptVersionId=368560160)). Current version's adjustment score is listed as pending in its Markdown, so `.684` is not attributed to version 18. Kaggle search returned last-run time Nov 12 02:11 UTC, while `get_notebook_info` returned Nov 9 06:41 UTC; timestamp metadata is inconsistent.
- Retrieved with `uv run --env-file ../.env kaggle kernels pull kirilltym/lora-trained27-evidence-for-close-calls -p /tmp/name-that-llm-kirill-audit --metadata`; examined source and `uv run --env-file ../.env kaggle kernels logs kirilltym/lora-trained27-evidence-for-close-calls`. Kernel status is `COMPLETE`. The newest log is an exact three-row public-format preview: it emits hard-coded preview labels for matching ID/text fingerprints, skips model-weight loading, and completes in about one second. This does not test or score the full inference path.
- The notebook describes a pair correction on semantic groups of size exactly two that also pass TF-IDF overlap `>=0.10` (English stop words, sublinear TF, unigram/bigram), mixing each member's probabilities 50/50 with its conditional marginal under distinct labels. Source code implements this by multiplying each row's probabilities by `(1 - other_row_probabilities)` and renormalizing.
- The full ensemble is an assembly of many public adapters, trained predictions, models and kernels. The pair rule is described as screened using older cached predictions, with no numerical result for the current classifiers. Reproducing the entire stack would not isolate the rule.
- The narrow fixed-rule screen used our frozen Spectral text clusters instead of the source notebook's Qwen embedding groups. It found one eligible pair and zero prediction changes, so the adaptation was rejected. It was not a full reproduction. No Kaggle object or submission was made.

## Source record

- Current Notebook URL above; version 18 source retrieved on 2026-11-12. Metadata lists GPU enabled, internet disabled, T4, and 17 dataset sources, 8 training-kernel sources, and 8 model sources. Its embedded notebook metadata says GPU disabled, an unresolved source/metadata mismatch.
- The claimed `.684` is the notebook author's table entry for v17, not independently remeasured here. The competition's top public score was `.768` at today's official check.
- Outcome: the [fixed primary screen](2026-11-12-kirill-close-pair-screen.md) failed its gain gate; close this audit as (b), with no independent confirmation or submission.
