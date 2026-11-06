# Open Pool v15 family-mass-preserving rerank spec

## Goal

Test whether a provider-family classifier can improve the adopted flat 4-view SVC by refining only the ranking of sibling labels within a family, while keeping the flat SVC's provider-family probability mass unchanged. The prior hierarchical candidate replaced family mass and scored below the flat SVC (primary BA 0.406358 vs 0.433776; prompt-paired 95% CI for the difference [-0.039630, -0.015195]). This candidate tests the narrower intervention suggested by the error analysis.

## Fixed method

- Use the same 18 official labels, six provider families, Open Pool v15, primary and confirmation outer GroupKFold splits, four feature views, LinearSVC settings, official/pool weights, exact-text exclusion, prompt-overlap filtering, per-class pool cap, and model-label order as the adopted flat Open Pool v15 SVC.
- For each outer fold, generate inner out-of-fold predictions from the outer-training prompts using `GroupKFold(n_splits=4, shuffle=True, random_state=42)`. Inner validation prompts must be excluded from official fitting and from the Open Pool using the same foldwise prompt-overlap and exact-text filters. The outer-validation prompts are excluded from all fitting and pool selection for that outer fold.
- Fit the flat 18-label SVC and the family-specific conditional SVCs on the same fold feature matrix. For each row, convert flat class margins to a softmax distribution `p_flat(y)`. Its family mass is `m(f)=sum_{y in f} p_flat(y)` and its within-family conditional is `q_flat(y|f)=p_flat(y)/m(f)`. Convert each family gate's margins to a softmax conditional `q_gate(y|f)`; singleton-family conditionals are 1.
- Select a single mixing coefficient per outer fold from inner OOF balanced accuracy over the fixed grid `{0, 0.25, 0.50, 0.75, 1.0}`. Ties select the smallest coefficient. No outer-validation labels, public leaderboard scores, third-party fitted weights, API-generated text, or external passages may influence this choice.
- Outer prediction is `p(y)=m(f) * ((1-alpha)*q_flat(y|f) + alpha*q_gate(y|f))`. This preserves the flat SVC family mass exactly. Temperature is fixed to 1.0 for both softmax conversions.

## Evaluation and decision

- Produce one OOF prediction for every official row in each split, using the existing primary and confirmation outer GroupKFold assignments. Verify 2,699 unique rows, 150 prompt groups, prompt separation, class coverage, finite scores, and matching labels/IDs against the adopted flat OOF.
- Report concatenated OOF balanced accuracy, fold scores, selected alpha per outer fold, family mass conservation, class recall, and prompt-level paired bootstrap against the flat SVC (2,000 replicates, seed 42).
- Run confirmation only if primary's paired 95% CI lower bound for rerank minus flat SVC is greater than zero. Adopt only if the confirmation CI lower bound is also greater than zero. Otherwise reject and retain the flat SVC.
- Do not submit a Notebook based on this candidate unless the existing goal's final-fit, reproducibility, Notebook-only, privacy, runtime, and submission-selection gates pass.

## Resources and scope

- CPU-only; maximum two CPU threads; process-tree RSS limit 32 GiB; minimum `MemAvailable` 16 GiB. Check both active GPU jobs and host load/memory before starting. Do not change or stop either GPU run.
- Use a separate runner, config, and artifact directory. Preserve all existing baseline, flat SVC, hierarchical SVC, and GPU candidate files. Do not run a test suite; syntax compilation and the runner's built-in data/convergence assertions are allowed.
- This experiment is authorized under the active autonomous first-place goal and its parent spec. It does not authorize publishing or making any Kaggle object public.
