## 16:33–16:37 JST — fixed Qwen3-1.7B + Spectral complementarity screen

- Registered fixed CPU-only screen in [spec](../specs/2026-11-12-qwen17b-spectral-complementarity-spec.md). Used saved Qwen3-1.7B Open Pool v15 fold logits, baseline probabilities, and frozen fold-local Spectral mean-field. The weight was fixed before evaluation: `(3 * baseline_probability + softmax(Qwen_logits, T=1.0)) / 4`.
- All source files matched with `sha256sum -c artifacts/cpu-qwen17b-spectral-complementarity-screen-v1/input-files.sha256`. Log records 8-character prefixes only: train `40a22ce8`; primary/confirmation baseline OOF `3635ad7b` / `c1ff251e`; primary/confirmation Qwen OOF `0d86149a` / `6eaca8fb`.
- Reproduction command: `uv run --project /mnt/HDD10TB-2/aburatani/kaggle python scripts/evaluate_qwen17b_spectral_complementarity.py`. CPU-only, one thread, 2,699 rows, 150 prompts, 18 classes, five folds per split; runtime 116.923 seconds. The source OOF, probabilities, and logits were not modified.
- Primary: frozen Spectral BA `.664952`, Qwen3-1.7B + Spectral BA `.657171`, delta `-.007780`, 5,000 prompt-paired bootstrap 95% CI `[-.014830, -.001080]` (seed 42).
- Independent confirmation: frozen Spectral BA `.653828`, Qwen3-1.7B + Spectral BA `.638645`, delta `-.015183`, CI `[-.022958, -.007763]` (seed 42).
- Both splits show a negative delta and CI below zero. Reject this candidate for Notebook use; no Kaggle asset, Notebook, or submission was created.
