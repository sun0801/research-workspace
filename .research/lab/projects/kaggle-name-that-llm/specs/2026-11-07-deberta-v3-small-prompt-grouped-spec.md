---
date: 2026-11-07
project: kaggle-name-that-llm
source: autonomous-goal
status: approved
execution_status: rejected-primary-gate
tags: [spec, experiment, gpu, text-classification]
---

# DeBERTa-v3-small prompt-grouped OOF candidate

## Hypothesis

A compact pretrained discriminative transformer may capture model-writing style cues complementary to the adopted 4-view prompt-centered SVC. Test its foldwise OOF predictions before considering any ensemble or Notebook submission.

The public inspiration is `goutamsharma12/stylodeberta` v1 (Kaggle, run 2026-11-04): DeBERTa-v3-small with a multi-sample-dropout classification head, maximum sequence length 384, three epochs, AdamW at 2e-5, and prompt-grouped five-fold code. That notebook has Internet enabled, contains no saved OOF outputs, and tunes its probability blend on the aggregate OOF; those choices are not evidence of a validated gain and will not be copied. A separate Kaggle model variation `mtnash/deberta-v3-small` is publicly available under MIT, with a 286,059,269-byte PyTorch weight file and SentencePiece tokenizer.

## Scope and inputs

- Add an independent GPU runner/config under `/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/` for official train-only fine-tuning and OOF inference. Do not edit the adopted SVC runner, its artifacts, or the live Qwen jobs.
- Use only official competition passages and the official [Microsoft DeBERTa-v3-small](https://huggingface.co/microsoft/deberta-v3-small) pretrained weights, pinned to revision `a36c739020e01763fe789b4b85e2df55d6180012`. The model card lists MIT licensing and describes a 6-layer, 768-hidden-size encoder. No external generated passages, fitted adapters, predictions, or annotations.
- Reinitialize the 18-class head for each fold. Use a fixed 384-token maximum, three epochs, batch size 8, AdamW learning rate `2e-5`, weight decay `0.01`, and the source recipe's multi-sample dropout rates `[0.1, 0.2, 0.3, 0.4, 0.5]`. Score the fixed final epoch; do not choose checkpoints, epochs, or blend weights from the outer validation labels.
- Keep the model and tokenizer immutable across folds. Training labels, gradients, and any fitted transforms must come only from each fold's training rows. Use one shared, prompt-grouped split per run and save its assignments and checkpoint/resume state.

## Evaluation and gates

- Primary screening uses the established 5-fold prompt-grouped primary split; report full OOF balanced accuracy, fold scores, per-class recall, and the same OOF coverage/alignment checks as other candidates.
- Compare to the adopted prompt-centered SVC on aligned rows using a prompt-level paired bootstrap (at least 2,000 resamples, seed 42). The primary adoption gate is a 95% CI lower bound above zero.
- If primary passes, train/evaluate the candidate and baseline on the already registered but unused `blend-confirm` split (`GroupKFold(shuffle=True, random_state=271828)`) and apply the same paired-bootstrap gate. This assignment was created before this candidate and was not used after the prior blend screen failed. Do not use confirmation results to tune epochs or architecture.
- The primary comparator is the adopted 0.10 prompt-centered SVC OOF. For confirmation, refit that SVC using the existing runner on the exact `blend-confirm` assignments; do not reuse the older seed-42 confirmation OOF.
- Do not blend this candidate before the base model clears both gates. Any future blend must have its own preregistered nested/fresh split evaluation.
- Only after both gates pass, fit on all official training data and verify an Internet-disabled Kaggle Notebook can load the attached public model input, finish within the 9-hour cap, and write exactly one prediction for every hidden test row with the required labels.

## Resource and implementation gates

- Run a small GPU pilot before the full five-fold job; select only GPU 141/142, record GPU UUID, VRAM peak, elapsed time, and host MemAvailable, and preserve each completed fold for resume.
- Do not start while the two Qwen jobs occupy the available GPUs unless a repeated preflight proves the selected device has sufficient free VRAM and the concurrent run will not violate their safety envelope. A busy-GPU condition delays the run; it does not change the model experiment into a CPU-only substitute.
- Keep RSS/VRAM below the approved parent spec thresholds, preserve existing artifacts, and stop safely on any guard breach.

## Expected provenance and limits

- Kaggle model mirror: [mtnash/deberta-v3-small](https://www.kaggle.com/models/mtnash/deberta-v3-small), Transformers/default/1, MIT, with a listed 286,059,269-byte PyTorch file. The local OOF model is pinned directly to the official Microsoft revision above; verify the Kaggle mirror weights before relying on it in a final Notebook.
- Public inspiration: [StyloDeBERTa](https://www.kaggle.com/code/goutamsharma12/stylodeberta), v1. Its code is inspiration only; its notebook enables Internet and supplies no saved OOF results.
- This candidate's CV measures generalization to held-out training prompts, not hidden-test performance or LB rank. The independent confirmation split is still drawn from the same 150 prompts and cannot establish final leaderboard performance by itself.

## 実行結果

- 2026-11-08 primary OOFをhost141 GPU1（RTX A4000、UUID `GPU-51b57ca0-53ca-3266-7105-efc692a6c834`）で5fold完了。pilot peak 2,725 MiB、reserve 8,192 MiB、開始時free 15,958 MiB、MemAvailable約121 GiB。pilot config SHA-256 `f5fd55dbf8ade917c67d2cb1de57dfde641e00969678b1b590e74b04051a97af`、runner SHA-256 `a424e3e63b06f3350795800871c1d64cf2d68d7f38947a8cfd73a7791d472c86`。5fold OOFは2,699行・150 promptで、保存splitは基準primary assignmentsとID/fold単位に一致。
- 採用済みSVCとのbalanced accuracyはDeBERTa `.290050`、SVC `.501934`、差 `−.211884`。prompt-paired bootstrap 5,000回、seed 42、95% CI `[−.234169, −.190373]`、adoption=`reject`。primary gate不通過のため独立confirmationとfinal fitは行わない。
- 正本出力: `artifacts/gpu05-deberta-v3-small-prompt-grouped/primary/primary/summary.json`（外部experiment repo）。pilot/run logとOOFも同じrun directoryに保持。
