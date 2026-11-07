# Open Pool SVC complementary fixed probability blend

## Goal and selection history

Test a fixed equal mean of the flat four-view Open Pool SVC and the adopted prompt-centered 0.10-pool-weight SVC. An exploratory error-overlap diagnostic found complementary correct rows on both existing outer splits, but those splits have already informed candidate selection and cannot serve as independent evaluation for this blend. The active autonomous first-place goal authorizes this experiment and its implementation.

## Fixed method

- Refit both SVC candidates out of fold on two new five-fold prompt-group splits. Use `GroupKFold(n_splits=5, shuffle=True)` with seed 314159 for `blend-screen` and seed 271828 for `blend-confirm`. Save and hash each assignment in its separate run directory. Keep all train rows for each fold's official fit except its held-out prompts; apply each candidate's existing pool filtering, sampling, feature, classifier and convergence settings unchanged.
- The existing configs remain unchanged: `cpu-openpool-4view-svc-v15.json` and `cpu-openpool-prompt-centered-low-pool-weight-v15.json`. Run artifacts in dedicated blend-study directories; preserve all previous artifacts and active GPU jobs.
- For each aligned row, convert each SVC decision-score vector independently to a softmax distribution at fixed temperature 1.0, then take their equal arithmetic mean. Predict by argmax. Do not fit a calibration, weight, threshold, class prior correction, or postprocessing rule.
- Validate 2,699 unique IDs, 150 prompt groups, all 18 labels, exact ID/label alignment, one OOF prediction per row, prompt separation, finite values, and convergence for both models. Report each base and blended balanced accuracy, per-class recall, and prompt-level paired bootstrap against the adopted prompt-centered SVC (2,000 replicates, seed 42).

## Decision

- `blend-screen` is screening only. Continue to `blend-confirm` only if the blend's paired 95% CI lower bound versus the same-split prompt-centered SVC is above zero.
- Adopt only if the unchanged blend's `blend-confirm` paired 95% CI lower bound is also above zero. Otherwise reject. The existing primary and confirmation splits are not used for this decision.
- This experiment does not authorize a Kaggle submission. Any future submission must separately meet the parent goal's final-fit, Notebook-only, privacy, runtime, and final-two selection rules.

## Implementation and resource scope

- External files may be changed only in `src/cpu_openpool_svc.py`, `src/cpu_openpool_prompt_centered_twin.py`, and a new fixed-blend evaluator. Add only the two named split IDs and their seed mapping; preserve existing `primary` and `confirmation` behavior. Do not alter candidate configs or unrelated runners.
- CPU-only, two threads per run, process-tree RSS cap 32 GiB, and minimum host `MemAvailable` 16 GiB. Recheck active GPU jobs and memory before each run; do not stop or modify them. Do not submit or publish any Kaggle object.
- Verification consists of syntax compilation, runner preflight and built-in data/convergence assertions, artifact alignment checks, and the preregistered paired bootstrap. Do not run a general test suite.
