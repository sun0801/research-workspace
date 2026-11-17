---
date: 2026-11-17
project: kaggle-name-that-llm
type: experiment-log
spec: ../specs/2026-11-14-olmo2-7b-4bit-openpool-lora-spec.md
---

# Public `.620` baseline + OLMo 2 add-on

## Official conditions and comparison

- Current comparison baseline is the private fork of Nishant Dahal's Two-stage LoRA part two v2, Public `.620` (submission ref `58452056`); prior local best was `.560`.
- Official rules/evaluation and public leaderboard were checked on 2026-11-17. The competition allows up to five submissions/day and two final submissions; scoring reruns on about 4,000 passages, while interactive `test.csv` contains only three local preview rows. Current public top is `.776` (6,138 teams). See [official status](2026-11-17-official-competition-status.md).
- Spectral v2 submission ref `58453689` remained `PENDING` with blank public score at 12:33 JST; two submissions had been made that day.

## 12:46 JST — Spectral score recovered

- Authenticated submission list reports ref `58453689` as `COMPLETE`, Public`.622`; the `.620` baseline ref `58452056` remains `COMPLETE`, Public`.620`.
- Difference is `+.002`, below the approved `.005` noise threshold. Record the observed score but retain `.620` as the adopted comparison baseline; do not tune or repeat Spectral based on this small change.
- Daily submissions used: 2/5. No submission was made for OLMo.
- The OLMo kernel remained `RUNNING` at 12:46 JST; this was an early observation before the next 30-minute poll window, so no extra status poll is scheduled from this result.

## Local pilot and memory fix

- The first 64-row trial sampled from local `data/test.csv`, which held only three preview rows and therefore repeated them. It was not accepted as a valid runtime pilot. Fold 0 ran, then the old helper's next-fold pre-load gate stopped before loading fold 1: free VRAM was 9,175 MiB against a required 11,878 MiB. A separate cleanup diagnostic showed only 9 MiB allocated but 6,574 MiB reserved by the process; process exit released GPU0 back to 15,960 MiB free. No OOM occurred.
- Updated `src/olmo_addon_inference.py` to load the quantized base once, load the five fold adapters sequentially onto that base, and activate one adapter at a time. This avoids repeatedly constructing/unloading the quantized base. Runtime projection now uses the measured 64-row sample and projects only the remaining rows.
- Corrected pilot used 64 distinct, length-stratified texts from `data/train.csv`, all five saved adapters, fixed batch size 2, and `projection_rows=4000`. It completed on Host142 GPU0 in 56.5 seconds. All five folds returned finite probabilities; output shape was 64×18 and maximum row-sum error was `2.4e-7`. Peak reserved VRAM was 7,322 MiB. No training labels or test labels were used for this inference check.
- Projected total was 3,236.9 seconds (~54 minutes) against the 8-hour helper gate, using the 4,000-row projection and 549-second interactive baseline runtime input. This is a local estimate, not the measured hidden full-run duration. The remote scoring run computes `baseline_elapsed_sec` from its actual elapsed time before the OLMo add-on.
- Asset manifest verified with `sha256sum -c SHA256SUMS`: 一致; manifest hash prefix `064efb66`. The upload package excludes local pilot logs.

## Private Kaggle runtime

- Created private Dataset `suntree0801/name-that-llm-private-olmo-addon-assets`; authenticated CLI later reported `ready`, and it appeared in the account's `datasets list --mine`. It contains the five inference-only adapters/heads and helper; no optimizer or RNG state.
- Pushed kernel version 1, `suntree0801/name-that-llm-private-olmo-add-on`, with `is_private=true`, GPU enabled, Internet disabled, selected baseline sources and the private OLMo Dataset attached. Initial status at 12:41 JST was `KernelWorkerStatus.RUNNING`.
- No competition submission has been made for this add-on. Wait for runtime completion, collect the full-run runtime and `submission.parquet` validation, then report before deciding whether to submit against `.620`.
- At this earlier checkpoint Host142 GPU1 was reserved for `mistral-confirm`; the user released that reservation on 2026-11-17 after all five confirmation folds finished and `tmux mistral-confirm` disappeared. No GPU1 action occurred at this earlier checkpoint. Local GPU0 was released after the pilot.

## Reproduction pointers

- Implementation: `/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/src/olmo_addon_inference.py` and `scripts/build_olmo_addon_notebook.py`.
- Private asset package: `/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/artifacts/public-baseline-olmo-addon-assets-v3/`.
- Pilot result: `/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/artifacts/public-baseline-olmo-addon-staging-v2/local-pilot/inference-64-train-projection4000.json`.
- Kaggle kernel: `suntree0801/name-that-llm-private-olmo-add-on`, version 1.

## Kaggle runtime failure and dependency repair

- 13:17 JST: the first private kernel version changed to `KernelWorkerStatus.ERROR`. Kaggle session output shows the baseline SVC, Qwen3-14B/Qwen2.5-14B LoRA and DeBERTa stages completed (last component at 543.7s); cell `In [6]` then failed when Transformers validated 4-bit quantization: `ImportError: Using bitsandbytes 4-bit quantization requires bitsandbytes>=0.46.1`. The OLMo model was not loaded and no competition submission was made.
- Cause: the offline Kaggle image had no importable bitsandbytes package. The local builder invoked the OLMo helper without installing the dependency, and the private OLMo asset Dataset contained adapters/helper but no wheel. This is an environment packaging failure, not evidence about OLMo inference quality or its VRAM gate.
- Downloaded the official PyPI `bitsandbytes==0.50.2` Linux x86-64 wheel. Its embedded package metadata declares `License-Expression: MIT` and includes `LICENSE` ([PyPI release](https://pypi.org/project/bitsandbytes/0.50.2/), [upstream license](https://github.com/bitsandbytes-foundation/bitsandbytes/blob/main/LICENSE)). Checksum verified with `sha256sum -c SHA256SUMS`: 一致、prefix `55348a9a`.
- Created private Dataset `suntree0801/name-that-llm-private-bnb-wheel` (CLI default private; status `ready`) containing only the wheel, its license and provenance. Updated `scripts/build_olmo_addon_notebook.py` to create a separate v2 source and install the pinned wheel with `pip --no-index --no-deps` before OLMo model loading; Internet remains disabled.
- 13:25 JST: pushed kernel version 2. Remote metadata confirms private, T4 GPU, Internet disabled, expected competition/model/data sources, and the wheel Dataset attached. Pulled remote source to `/tmp/ntl-olmo-kernel-v2-remote`; all cell sources match the local v2 Notebook. Initial remote status: `RUNNING`.
- 13:34 JST: source review found a second ordering risk in v2. Transformers 4.57.1 sets `_bitsandbytes_available` when `transformers.utils.import_utils` is imported and its availability check reads that cached value ([pinned upstream source](https://github.com/huggingface/transformers/blob/v4.57.1/src/transformers/utils/import_utils.py#L124-L125)). Since v2 installs the wheel after the baseline Notebook has imported Transformers, it may still report unavailable. Prepared v3 locally to install bitsandbytes in a new first code cell before baseline imports, while leaving baseline source cells untouched. No v3 push while v2 may still be running; next status check is no earlier than 13:55 JST.
- At the 13:34 JST checkpoint, no OLMo competition submission had been made; the active version was to be monitored at 30-minute intervals and its artifact validated before submission.

## v2 successful preview run and competition submission

- 13:55 JST: kernel v2 status `COMPLETE`. Kaggle log reports `bitsandbytes-0.50.2` installed from the attached private wheel, OLMo model loaded with 8,810 MiB free, and all five fold preview passes complete (per-fold pilot peak reserved 6,450 MiB). Notebook runtime reports `done in 676s`; session log/export ends at 703.6s. No traceback or runtime-gate failure.
- The interactive run has only 3 test rows, so its helper does not run the 4,000-row projection branch. Local 4,000-row pilot projection remains 3,236.9s (~54m); this is not the hidden scoring runtime. The scoring job will run the full hidden test set.
- Downloaded `submission.parquet` to `/tmp/ntl-olmo-v2-output/`. It has exactly columns `id,model`, 3 rows, zero nulls, 3 unique IDs, exact local preview test IDs/order, and only valid labels. Compared with the baseline kernel preview, labels are unchanged on all 3 rows; this preview is not representative of the hidden test distribution.
- 13:58 JST pre-submit gates: rate guard 5h 85% remaining and weekly 72%; Kaggle GPU quota 29.13h/30h (refresh 2026-11-21 09:00 JST); earlier same-day submissions were 2/5. Official competition metadata: max five/day, two final selections, deadline 2027-01-14 23:59 UTC, current public top `.776`; Rules/Evaluation were rechecked. Candidate remained eligible under the approved CV cutoff: OOF did not show clear deterioration.
- First submit request used an absolute `/tmp/.../submission.parquet` path and got `400 Bad Request`; no ref was created and submission list stayed at 2/5. CLI source confirms code-submission `file_name` is passed verbatim as the output filename. Retried from the output directory with basename `submission.parquet`; Kaggle accepted ref `58456880` at 14:01 JST. Initial status `PENDING`, score blank; daily submissions now 3/5 (2 remaining).
- The locally prepared v3 (install wheel before baseline imports) was not pushed; v2 succeeded. Keep the active status check on ref `58456880` at 30-minute intervals, and record only a state change. No OLMo score has been received yet.
