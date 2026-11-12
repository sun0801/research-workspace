## 16:56–17:01 JST — fixed Prompt-centered Twin SVC + Spectral complementarity screen

- Registered fixed CPU-only screen in [spec](../specs/2026-11-12-prompt-centered-twin-spectral-complementarity-spec.md). Used saved Twin SVC fold scores from primary retry1 and confirmation retry2, adopted baseline probabilities, and frozen fold-local Spectral mean-field. Formula fixed before evaluation: `(3 * baseline_probability + softmax(twin_decision_scores, T=1.0)) / 4`; no refit or weight search.
- Source files matched with `sha256sum -c artifacts/cpu-twin-spectral-complementarity-screen-v1/input-files.sha256`. Log records 8-character prefixes only: train `40a22ce8`; primary/confirmation baseline OOF `3635ad7b` / `c1ff251e`; primary/confirmation Twin OOF `513db151` / `0c549661`.
- Reproduction command: `uv run --project /mnt/HDD10TB-2/aburatani/kaggle python scripts/evaluate_prompt_centered_twin_spectral_complementarity.py`. CPU-only, one thread, 2,699 rows, 150 prompts, 18 classes, five folds per split; runtime 115.749 seconds. Original OOF, baseline probabilities, and Twin scores were preserved.
- Primary: frozen Spectral BA `.664952`, Twin + Spectral BA `.671255`, delta `+.006304`, 5,000 prompt-paired bootstrap 95% CI `[-.000370, +.013383]` (seed 42).
- Independent confirmation: frozen Spectral BA `.653828`, Twin + Spectral BA `.659006`, delta `+.005178`, CI `[-.001487, +.011852]` (seed 42).
- Both deltas are positive, but each CI lower bound is below zero. Reject for Notebook use; no Kaggle asset, Notebook, or submission was created.
