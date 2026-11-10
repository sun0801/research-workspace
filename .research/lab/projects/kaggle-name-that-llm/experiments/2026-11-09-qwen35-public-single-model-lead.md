---
date: 2026-11-09
project: kaggle-name-that-llm
status: public-lead-investigated-not-reproduced
tags: [public-source, model, qwen, candidate-screen]
---

# Qwen3.5-9B single-model public lead

## Lead

Kaggle Discussion [“What score your best single model can achieve?”](https://www.kaggle.com/competitions/name-that-llm/discussion/754860) has a Nov 7 comment claiming `0.649 Qwen3.5-9B (No quantization)` in a thread about single-model public scores. The comment does not identify its author in the retrieved message record, and supplies no training data, split, code, model revision, validation score, or inference runtime. Treat `0.649` as an unverified public-score claim, not a reproducible OOF result.

## Model availability and architecture

- Official upstream model: [`Qwen/Qwen3.5-9B`](https://huggingface.co/Qwen/Qwen3.5-9B), public versioned weights, Apache-2.0 according to the Qwen model card. The card describes a 9B-parameter, 32-layer multimodal model with a hybrid Gated DeltaNet/full-attention text backbone.
- Kaggle has [`danbth/qwen3-5-9b`](https://www.kaggle.com/models/danbth/qwen3-5-9b), Transformers version 1; Kaggle metadata lists MIT and 19,329,891,881 uncompressed bytes across four weight shards. The Kaggle license label and upstream license are distinct metadata records; verify the packaged LICENSE and that weights match the official upstream revision before reuse.
- The current local Kaggle environment is Transformers 4.57.1 and does not expose `Qwen3_5ForCausalLM` or `Qwen3_5TextConfig`. The current generic Qwen runner therefore cannot load this architecture as-is. The official [Transformers Qwen3.5 implementation](https://github.com/huggingface/transformers/blob/main/src/transformers/models/qwen3_5/modeling_qwen3_5.py) defines hybrid DeltaNet projections (`in_proj_qkv`, `in_proj_z`, `in_proj_b`, `in_proj_a`, `out_proj`) in addition to full-attention/MLP projections. A dedicated compatible environment and architecture-aware classifier are needed before a pilot.

## Notebook search and decision

A Kaggle `search_notebooks` query for `Qwen3.5-9B` returned recent-indexed competition notebooks, but the inspected `omkarpattanaik123/name-that-llm-v26-sovereign-grandmaster-apex` metadata lists Qwen3/Qwen2.5 model inputs and no Qwen3.5 model; its metadata says last run Nov 5 despite the search index showing Nov 8. It is not a reproduction of the reported single-model result. No exact public Notebook or recipe was found in this search.

The lead is worth a later independent local OOF trial because the reported single-model score is competitive with the Anto Pil Qwen members. A separate candidate spec is now registered under the active goal at [`2026-11-09-qwen35-9b-openpool-v15-spec.md`](../specs/2026-11-09-qwen35-9b-openpool-v15-spec.md), after the already registered Host142 GPU1 queue through candidate14. It does not alter the live queue. Before any run, verify official model file identity/license, pin a Transformers version with Qwen3.5 support, implement and inspect the text-only classification path, and pass the Host142 resource/runtime gates. No model download, environment change, runner edit, GPU run, Kaggle write, or submission was made for this lead.


## 2026-11-09 03:05 JST CLI and provenance follow-up

- Kaggle MCP confirms version 1 of `danbth/qwen3-5-9b/Transformers/default` contains 16 files including `LICENSE` (11,544 bytes), four safetensor shards, and 19,329,891,881 uncompressed bytes. It reports MIT, but does not expose file hashes or file contents. The upstream Hugging Face repository is Apache-2.0 and its current tree is at verified commit `c202236`; that does not prove the Kaggle copy's weights or packaged license match.
- Installed Kaggle CLI is 2.2.5; its actual version download route is `kaggle models instances versions download <owner>/<model>/<framework>/<variation>/<version>`. The package `kagglehub` is absent from the existing `.venv`. Kaggle's current CLI documentation describes variation-version download; see [Kaggle CLI model variation version commands](https://github.com/Kaggle/kaggle-cli/blob/main/docs/model_variations_versions.md) and [Kaggle Models documentation](https://www.kaggle.com/docs/models).
- No model files were downloaded. The exact Kaggle payload and its bundled license remain unverified, so the spec's provenance/license gate is still closed. Once that gate is resolved from trusted provenance, use the immutable version route in an isolated download location, compare each weight file against the pinned upstream revision, and only then prepare the separate runtime.


## 2026-11-09 03:27 JST version-pinned source follow-up

- Reviewed the official Transformers `v5.2.0` tagged source. It contains `Qwen3_5TextModel` and `Qwen3_5ForCausalLM`; the latter wraps a text backbone and applies a vocabulary head in `forward`. This gives a version-pinned implementation baseline and confirms the custom classifier can use hidden states without vocabulary logits.
- The upstream [model config](https://huggingface.co/Qwen/Qwen3.5-9B/blob/main/config.json) declares `Qwen3_5ForConditionalGeneration` with nested `text_config.model_type=qwen3_5_text`. Loading its composite checkpoint into a text-only class therefore needs an explicit CPU state-dict/config mapping check; the model config and v5.2.0 source are compatible in principle, but the checkpoint loader path is not yet verified.
- The exact configuration/state-dict mapping from the composite `Qwen3_5ForConditionalGeneration` checkpoint into a text-only backbone still needs a CPU load check. No package was installed and no runner/model was created. Keep the candidate behind the Host142 GPU1 queue and the unresolved model-source/license gate. The Qwen spec now records these compatibility limits. Source: [Transformers v5.2.0 implementation](https://github.com/huggingface/transformers/blob/v5.2.0/src/transformers/models/qwen3_5/modeling_qwen3_5.py).

## 2026-11-09 03:39 JST official source acquisition and preflight

- Downloaded the official Hugging Face snapshot at immutable commit `c202236235762e1c871ad0ccb60c8ee5ba337b9a` to `/tmp/qwen35-official-c202236235762e1c871ad0ccb60c8ee5ba337b9a`. All 16 files passed expected-size and Git blob/LFS SHA-256 checks; total expected size is `19,329,393,661` bytes. The pinned `LICENSE` is Apache-2.0. Four model shard SHA-256 values and the per-file verification record are summarized in the candidate spec.
- CPU-only inspection of the config, index, and safetensors headers confirms a composite `Qwen3_5ForConditionalGeneration` checkpoint with nested text model `qwen3_5_text` (hidden size 4096, 32 layers). The 775 indexed tensors have prefixes `model`, `mtp`, and `lm_head`; text layers use `model.language_model.*`. The exact compatible text-only load/remap and isolated pinned environment are still open preflight gates. No active environment or external runner was changed and no GPU run was started.

## 2026-11-09 03:49 JST text-only load and LoRA compatibility

- A temporary Transformers 5.2.0 / PEFT 0.18.1 probe verified that stripping the `model.language_model.` prefix yields an exact one-to-one match for all 426 `Qwen3_5TextModel` state tensors, including shapes. Loading the official BF16 weights on CPU and forwarding four tokens produced finite `(1, 4, 4096)` hidden states (4.635 s). No vision, MTP, or LM-head weights enter the text-only classifier.
- The registered 12 suffixes match 248 `nn.Linear` modules: 8 each for full-attention q/k/v/o; 24 each for DeltaNet `in_proj_qkv`, `in_proj_z`, `in_proj_b`, `in_proj_a`, `out_proj`; and 32 each for MLP gate/up/down. PEFT injected all targets and reported 43,278,336 trainable parameters.
- Existing PEFT 0.17.1 is incompatible with Transformers 5.2.0 (`HybridCache` import failure). PEFT 0.18.1 import/injection worked. The probe reused active-environment dependencies read-only through a `.pth` and showed NumPy ABI warnings from inherited optional compiled packages; treat versions as a compatibility baseline, not a clean runtime lock. The required gradient/optimizer pilot and Host142 GPU pilot remain pending, and no active job/environment was changed.
- `AutoTokenizer` also loads the pinned local snapshot offline without remote code; plain text inputs tokenize successfully (sample lengths 7 and 10), with right padding, pad id 248044, EOS id 248046, and tokenizer length 248,077. Batch pooling must gather the last non-padding token.

## 2026-11-09 04:04 JST clean runtime dependency baseline

- Built a clean Python 3.12 virtual environment in `/tmp/qwen35-clean-env` with CUDA 12.8/Torch 2.9.0+cu128; exact full `pip freeze` is saved in [`2026-11-09-qwen35-runtime-lock.txt`](../specs/2026-11-09-qwen35-runtime-lock.txt), with install notes in the paired Markdown spec. Transformers 5.2.0, PEFT 0.18.1, Accelerate 1.10.1, bitsandbytes 0.50.2, and FLA/fla-core 0.5.2 all import; Transformers detects the FLA Gated DeltaNet kernels, and AdamW8bit imports. This fixed the earlier probe's inherited NumPy warnings. No GPU calculation or optimizer step was made.
- FLA 0.6.0 resolves Transformers >=5.6.2 and upgraded the temporary env to 5.22.2; reverted it and pinned FLA 0.5.2, whose official metadata supports Transformers >=4.45 and CUDA Torch >=2.7. The exact GPU path and runtime still require the queued Host142 GPU1 pilot.

## 2026-11-09 10:56 JST candidate15 runner prepared

- Added the candidate-specific implementation and frozen config in the external implementation repository: `src/gpu_qwen35_experiment.py` and `configs/gpu15-qwen35-9b-openpool-v15.json`. Final SHA-256: runner `7f18e76fd04f2fb421a1b38903965867a441606f3de46a4cb606cf64516d444b`; config `c3bf55dec00e893277d6963f104f914365d070a820407a16ae4d511a62661d84`.
- Static validation passed with `/tmp/qwen35-clean-env`: `py_compile`, module import, and the runner's registered-config validator. The text-only loader requires exact checkpoint key coverage; LoRA injection requires the preverified 248 suffix counts and 43,278,336 adapter parameters. The gated pilot will measure a finite forward/backward/AdamW8bit step, one-row inference timing, and VRAM/RAM before any OOF run.
- No GPU/model-load/pilot/OOF execution has started. At the 10:56 JST poll all five existing GPU jobs remain active, so keep candidate15 queued after candidate14 and do not overlap or reorder.

## 2026-11-09 11:03 JST candidate15 loader preflight

- With `/tmp/qwen35-preflight-env` (which has no FLA/Triton dispatch), the new `load_text_backbone` loaded 7,936,684,544 parameters from the pinned official text-only checkpoint mapping and produced finite `[1,4,4096]` hidden states on CPU. MemAvailable remained 201.58 to 201.35 GiB. The inherited preflight environment emitted its already known NumPy ABI warnings, but the load/forward completed with exit 0.
- A separate CPU forward in `/tmp/qwen35-clean-env`, which includes FLA, attempted the FLA/Triton CUDA dispatch with CPU tensors and failed with `Pointer argument ... cannot be accessed from Triton (cpu tensor?)`. This was a CPU-forward incompatibility of the optional kernel path; no GPU training or optimizer step started. The actual queued pilot must validate forward/backward/AdamW8bit on the target GPU.
- Froze the classifier head as final-token `LayerNorm + Dropout(0.1) + Linear`, and config validation now checks this choice and weight decay. Static compile, isolated-runtime import, and config validation passed after the change. Candidate15 remains behind candidate14.
