---
date: 2026-11-09
project: kaggle-name-that-llm
type: source-review
status: reviewed-not-queued
tags: [glm-5-3, likelihood, discussion, feasibility]
---

# GLM-5.3 OOF corner discussion audit

開始結論: (b) 試さない

## Source and scope

- Kaggle discussion: [Running GLM-5.3 / GLM-5.3-Flash inside the 9h limit](https://www.kaggle.com/competitions/name-that-llm/discussion/757199), author vishu phalswal, posted 2026-11-09 16:38 JST. Read the original post and its one reply through the official Kaggle MCP at about 21:36 JST.
- Kaggle dataset metadata and file listings: `jamesliebel/glm53-flash-iq3xxs-segs-mirror`, `jamesliebel/glm53-iq3xxs-segs-a-mirror`, and `jamesliebel/glm53-iq3xxs-segs-b-mirror`.

## Claims and limits

The author reports an existing Qwen ensemble with public score around `.68` and own OOF classwise accuracy `.32` for `glm-5.3`, `.44` for `glm-5.3-flash`, and `.48` for `claude-fable-5`, with many confusions among those classes. These are self-reported and the post does not include code, fold predictions, score definition beyond “OOF accuracy,” or a reproducible recipe. The author says their GLM-4-9B/Qwen3-8B log-likelihood feature stack was `−.002` in prompt-grouped CV, about 33k additional public rows reduced OOF, and pseudo-labeling was negative in simulation. Treat all as leads, not verified results.

The suggested IQ3_XXS GGUF layer-segment datasets are very large: Kaggle metadata reports 117.6 GB for GLM-5.3-Flash, and 145.1 GB + 133.0 GB for the two GLM-5.3 parts (278.1 GB total). The mirror descriptions say the upstream weights are Z.AI open weights, describe the GLM-5.3 license as MIT-style, and say a LICENSE file is included; Kaggle categorizes the mirrors as “Other (specified in description).” I did not inspect the LICENSE payload or verify model-file hashes. The post asks about architecture support, streaming, and nine-hour runtime and provides no working inference implementation. With these scale and reproducibility gaps, the datasets do not yet establish a feasible offline Kaggle candidate under the approved runtime conditions.

## 2026-11-10 22:39 JST refresh

The newest reply reports a simple TF-IDF + logistic GroupKFold confusion count: GLM/Claude class errors run both directions across 125 GLM and 119 Claude rows. The author explicitly has not run GLM-5.3 likelihood features; no new working GGUF inference path or score above the existing Qwen ensemble was supplied. This reinforces the difficult class corner but does not change the experiment queue.

## Decision

Do not download these 117–278 GB weight sets, start a pilot, or change the existing queue based on this post. It does identify a potentially hard class corner, but the author’s existing likelihood trial was slightly negative and the proposed larger model has no validated Kaggle inference path. Keep the current registered experiments and confirmation chain in order. Revisit only if public code demonstrates a feasible, offline, <=9-hour inference path with compatible license/provenance and a prompt-grouped OOF comparison that shows complementary improvement.

No model, data, environment, job, watcher, Kaggle object, or submission was changed.

最終結論: (b) 試さない
