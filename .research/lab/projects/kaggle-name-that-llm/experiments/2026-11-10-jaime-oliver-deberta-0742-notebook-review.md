---
date: 2026-11-10
project: kaggle-name-that-llm
type: public-notebook-review
tags: [deberta-v3-large, ensemble, public-score, prompt-grouped-validation]
---

# Jaime Oliver 0.742+ DeBERTa ensemble notebook review

開始結論: (b) 試さない — 公開sourceの複合ensembleはscore/OOFの対応が未検証で、供給DeBERTa checkpointはcompetition trainで学習済み。leak-freeに再現できる構成・fold artifactがなく、現top`.768`を超える根拠がない。

## Source and retrieval

- Notebook: [NTL v1 baseline](https://www.kaggle.com/code/muhammadasjad2008/ntl-v1-baseline), author metadata `Jaime Oliver`, current version 32.
- Dataset: [NTL two-stage LoRA part two](https://www.kaggle.com/datasets/nishantdahal/ntl-handwriting-blend), version 1, described as CC BY-SA 4.0.
- Kaggle MCP retrieval: 2026-11-10 02:14–02:18 JST. Competition-filtered DateRun search placed this notebook first at Nov 9 17:12:44 UTC, while `get_notebook_info` reports `last_run_time` Nov 6 17:15 UTC; session-status API returned `CANCEL_REQUESTED`. Treat the search timestamp as discovery metadata, not a verified successful run.
- Notebook is public, GPU-enabled, Internet-disabled. Metadata lists 14 dataset sources, 8 source notebooks, and 8 model sources. `machine_shape` is `NvidiaTeslaT4`; the source claims dual-GPU sharding. The metadata does not by itself verify hardware count, successful runtime, or submission score.

## Claims and method

The title and opening markdown claim a 0.742+ public score and say DeBERTa-v3-Large alone reached about 0.747 OOF balanced accuracy. The main pipeline combines multi-layer DeBERTa pooling, Qwen/Llama LoRA members, 4-view StyleGram LinearSVC, a stylometric tree model, ATLAS likelihood scoring, adaptive prior shrinkage, and typography refinement. It sets a DeBERTa blend weight of 4.2, uses layers 18/20/22/24 in its narrative, and claims about 4.5 hours for the two-GPU inference route.

The Kaggle dependency dataset describes a supplied DeBERTa-v3-Large fine-tuned encoder/head that scores 0.546 alone, and states its checkpoints were first trained on public passages and then on the competition training set. The listed dataset file is one final `deberta_v3_large` encoder/head, not fold-specific checkpoints. The Notebook markdown's approximately 0.747 OOF statement and the dependency dataset's 0.546 standalone score have no aligned split/recipe explanation in the retrieved source; they are not comparable evidence without that reconciliation. The Notebook source is primarily an inference pipeline and does not reproduce the claimed OOF evaluation.

The interactive path sets `FAST_COMMIT` when fewer than five test rows are present and writes a constant `claude-sonnet-5` label; the hidden competition rerun takes the full inference path. This can make the notebook commit quickly, but its public interactive output cannot validate the prediction pipeline. Combined with `CANCEL_REQUESTED` and the metadata/search run-time disagreement, no successful 0.742 scoring run was verified in this review.

The same notebook reports its own nested-CV ensemble at 0.6865 but board scores around 0.56 for that pipeline, says prompt centering/Hungarian tricks looked good on complete 18-answer prompts but lost on the board, and reports up to 0.009 variation across identical-code submissions. These are author-reported observations, but they reinforce the need for prompt-grouped validation that also models incomplete prompt groups and for treating small public-score gains cautiously. The 0.742+ title claim remains below the current official public top of 0.752.

The notebook also cites [Discussion 753177](https://www.kaggle.com/competitions/name-that-llm/discussion/753177) for an `m=2` test-shape OOF proxy. Reading the original GoPain comment (posted Oct 29) shows a narrower and noisier result than the notebook's short `0.91 vs 0.13` summary: across 15 submissions from one blend family, `m=2` correlations were Pearson/Spearman `0.91/0.82` on the first 10 and `−0.22/0.05` on the next five selected by that proxy; across all 15 they were `0.79/0.58`. The author says removing a favorable outlier drops Spearman to `0.49`, and describes it as a weak signal for rejecting clearly worse configurations, not ranking close ones. Treat this as a self-reported, family-specific diagnostic with selection effects, not as a general replacement for the approved full prompt-grouped primary metric. It may motivate a separately frozen incomplete-group robustness report for future candidates.

## Decision

Do not adopt the public checkpoint or copied ensemble OOF as validation evidence. The method is too composite to attribute gains, the provided DeBERTa asset has seen the competition training set, and the OOF score claim is unresolved. Record DeBERTa-v3-Large as a later replication lead only after baseline CV-LB correspondence: rerun fold-by-fold under the approved prompt-grouped protocol, establish the dependency checkpoint's training split/provenance, then compare against the adopted blend. No Kaggle object or submission was created.

最終結論: (b) 試さない — 公開checkpoint/OOFのprovenanceが不明で、現存sourceからfoldwise再現できず、主張score`.742+`も現top`.768`未満。

## 2026-11-12 follow-up after baseline CV-LB check

基準blend v12のprimary OOF BA`.586408` / Public`.541`を確認したため、当初の「CV-LB対応待ち」は解消した。ただしCV-LBの対応点は1件だけで校正は未完了。Notebook source・datasetの既存監査では、`.742+`は該当versionで確認されず、DeBERTa依存checkpointはcompetition trainで学習済み、OOF`.747`とのsplit/recipe差も説明されていない。よってこの公開stackのscore/OOFは独立根拠にならず、同じassetを使う追試はleakage-freeにならない。再現可能な独立DeBERTa候補のspecも存在せず、このNotebook監査は(b)で終了する。既存small DeBERTaはprimary gateで大幅不採用（BA`.290050` vs SVC`.501934`）であり、本監査からLarge architectureへの転移根拠も得られなかった。
