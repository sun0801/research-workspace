(a) specにして試す — full-training由来の公開checkpointは採用せず、MITの公式未調整DeBERTa-v3-largeをfold-localで訓練する独立検証に限って候補化する。

---

date: 2026-11-12
project: kaggle-name-that-llm
type: candidate-selection
conclusion: a-spec-to-test
---

# DeBERTa-v3-large clean-base candidate selection

確認日: 2026-11-12。

- Public evidence reviewed earlier in [Jaime Oliver `.742+` audit](2026-11-10-jaime-oliver-deberta-0742-notebook-review.md) is not a valid performance claim for adoption: the supplied checkpoint saw the competition training set, the claimed `.747` OOF does not align with the dataset's `.546` standalone description, and source/version score verification is absent. That Notebook remains `(b) 試さない`.
- A different, clean experiment is possible: Kaggle's `illuminatep/deberta-v3-plain/Transformers/large` version 1 identifies itself as unmodified Microsoft base weights, MIT, 434M params/24 layers/1024 hidden. The exact version file list includes model, tokenizer, and config files; no fine-tuned competition checkpoint.
- Local DeBERTa-v3-small full fine-tuning failed its primary gate, which makes this a high-risk scale hypothesis. However, prompt-grouped fold-local training of the large official base provides a direct, inexpensive-to-screen way to determine whether this architecture has useful complementarity; it uses no questionable checkpoint or external labels.
- Decision: `(a) specにして試す`, with a fixed prompt-grouped primary/confirmation protocol and strict Host141 GPU1 pilot/resource gates. Do not use the public `.747` claim in metrics or decisions.

See [approved-under-active-goal spec](../specs/2026-11-12-deberta-v3-large-official-prompt-grouped-spec.md).
