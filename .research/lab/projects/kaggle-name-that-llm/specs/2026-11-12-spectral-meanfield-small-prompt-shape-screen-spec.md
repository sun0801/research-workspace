---
date: 2026-11-12
project: kaggle-name-that-llm
source: active-goal / Kaggle Discussion 753177
status: approved-under-active-goal
approval_basis: 2026-11-06-gpu-autonomous-first-place-spec
execution_status: completed-primary-shape-robustness-flagged
implementation_scope: standalone-CPU-evaluator-and-new-artifacts-only
verification: exact-ID/fold alignment; baseline argmax parity; deterministic prompt subsampling; held-out-text-only clustering; primary-and-confirmation paired deltas
tags: [spec, prompt-clustering, mean-field, test-shape, cpu]
---

# Spectral mean-field small-prompt-shape robustness screen

## Rationale

Kaggle Discussion [753177](https://www.kaggle.com/competitions/name-that-llm/discussion/753177) reports that, for one prompt-dependent blend family, OOF simulations with only `m=2` answers per prompt correlated better with public LB than full 18-answer prompts. The author emphasizes that this is a weak sanity check from 15 related submissions, affected by one outlier and selection among 162 configurations; `m=2` did not rank the five later selected configs. Treat the test group size claim as uncertain, not as an observed competition fact.

The adopted Spectral mean-field transform has passed full-prompt primary and independent confirmation, but its postprocessing uses text-derived groups and batch-wide score normalization. Its existing sensitivity tests independently retain 30–100% or 65–100% of rows by class; they do not reproduce only two or three answers per true prompt. This fixed robustness screen measures how much its existing gain survives that shape change. It is not a new CV split, parameter search, or LB estimate.

## Fixed comparison

- Candidate: the already adopted, unchanged version-10 Spectral `normalised_content_groups` + local mean-field transform (`gamma=.55`, cluster temperature `.65`, four iterations, final temperature `.72`) applied to the saved Qwen8B + Qwen1.7B + prompt-centered SVC OOF probabilities.
- Comparator: argmax of those same saved probability arrays before mean-field correction.
- Splits: the registered primary and independent confirmation OOFs, each processed within its saved outer fold. Use all 150 held-out prompt groups across the folds for final balanced accuracy per replicate.
- The official train has 150 prompts: 149 have 18 distinct model rows and one has 17 (one model answer is absent); there are no duplicate models within a prompt. For each prompt in a split and replicate, choose `m=2` or `m=3` from its available rows without replacement. Pair `m=2` and `m=3` by drawing a deterministic ordering of three available rows and taking its first two or all three.
- Fixed sampling conditions: (1) uniform class selection, mirroring the Discussion's random-answer procedure; (2) mild class skew, weighted without replacement with 18 class weights evenly spaced from `.65` to `1.0`; (3) moderate class skew, weights evenly spaced from `.30` to `1.0`. For the skew conditions, permute the fixed weight vector by the replicate seed and share the mapping across prompts, folds, and both splits. Use weighted Gumbel top-k for sampling without replacement. No weight range is tuned.
- Use 20 deterministic replicate seeds `42–61`. Use the same prompt-level sample choices for primary and confirmation. True prompt IDs are used only to select `m` rows and later compute diagnostics; true labels are used only to describe class counts and score. The clusterer and mean-field function receive only sampled texts and probabilities, never prompt IDs or labels.

## Metrics and interpretation

- For each split, `m`, condition, and seed, report baseline/candidate all-row balanced accuracy on selected rows, delta, selected row/prompt/class counts, fold deltas, and inferred cluster-size diagnostics.
- Summarize mean/median/standard deviation, 10th/90th percentiles, and fraction of positive replicate deltas for all six fixed conditions. This is a simulation distribution, not a confidence interval or test-set estimate. Do not choose a setting or hyperparameter from the best replicate.
- Interpret uniform `m=2` and `m=3` first as primary conditions; class-skew conditions show sensitivity. A consistently negative mean or less than 60% positive replicates in both uniform conditions on either registered split flags that the full-prompt mean-field gain is not robust to smaller groups and lowers its priority for hidden-test use. This screen cannot revoke the already measured full-prompt confirmation result or establish a hidden-test score.

## Execution boundaries

- CPU-only; set OpenMP/BLAS/NumExpr threads to 1. Do not inspect or occupy GPU for this run. Preserve all existing OOF arrays, predictions, and models.
- Add one standalone runner under `scripts/` in the Kaggle implementation repository. Write only beneath `artifacts/cpu-spectral-cluster-meanfield-small-prompt-screen-v1/`; fail if the output path already exists. Do not modify existing evaluators or artifacts.
- Preflight exact 2,699-ID alignment, official labels/prompts, saved fold membership, 18 unique labels per source prompt, and baseline argmax reproduction for every fold in both splits. Abort before writing results if any mismatch occurs.
- No Kaggle push, Notebook, submission, coefficient tuning, or follow-on transform is part of this diagnostic. Record exact command, sampling definition, per-split results, and limits in a dated experiment log; hashes, if recorded, must obey the project hash rule (verify by command; never copy full digests into prose).


## Execution result (2026-11-12)

The fixed 20-replicate screen completed on both registered splits. Primary uniform m=2/m=3 means were `-0.012948`/`-0.001217` with positive fractions `.25`/`.45`, so primary shape robustness is flagged. Confirmation uniform means were `+.006320`/`+.010591` with positive fractions `.70`/`.75`. See the [result log](../experiments/2026-11-12-spectral-meanfield-small-prompt-shape-screen.md). No tuning or submission followed.
