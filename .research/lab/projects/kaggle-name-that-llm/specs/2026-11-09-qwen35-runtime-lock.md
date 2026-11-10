---
date: 2026-11-09
project: kaggle-name-that-llm
status: clean-environment-preflight-passed-gpu-step-pending
tags: [spec, qwen35, dependencies, cuda, reproducibility]
---

# Qwen3.5 runtime dependency lock

## Scope and status

This is the exact `pip freeze` from the clean Python 3.12 environment `/tmp/qwen35-clean-env` on Host142. It pins CUDA 12.8 / PyTorch 2.9.0, Transformers 5.2.0, PEFT 0.18.1, FLA 0.5.2, bitsandbytes 0.50.2, and the data stack. Imports pass for Qwen3.5 classes, PEFT, FLA's `chunk_gated_delta_rule`/`fused_recurrent_gated_delta_rule`, and `bitsandbytes.optim.AdamW8bit`. This environment has not used a GPU. CUDA LoRA forward/backward, optimizer step, gradient checkpointing, and actual runtime/memory remain gates for the registered GPU pilot.

FLA 0.5.2 is pinned because its official metadata requires only Transformers `>=4.45` and its CUDA extra requires Torch `>=2.7`/Triton `>=3.3`, compatible with this tested Transformers 5.2.0/Torch 2.9.0 pairing. FLA 0.6.0 requires Transformers `>=5.6.2` and upgraded the probe to Transformers 5.22.2, so that combination was reverted. Do not use `causal-conv1d` yet; it is an optional kernel and is not part of the verified lock.

Official references: [Transformers Qwen3.5 implementation](https://github.com/huggingface/transformers/blob/v5.2.0/src/transformers/models/qwen3_5/modeling_qwen3_5.py), [FLA 0.5.2 dependencies](https://github.com/fla-org/flash-linear-attention/blob/v0.5.2/pyproject.toml), [FLA 0.5.2 CUDA install](https://github.com/fla-org/flash-linear-attention/blob/v0.5.2/INSTALL.md), [PEFT 0.18.1 release notes](https://github.com/huggingface/peft/releases/tag/0.18.1).

## Install indexes

Create a clean Python 3.12 virtual environment. Install the CUDA PyTorch wheel from the official PyTorch CUDA 12.8 index with `pypi.nvidia.com` for its CUDA runtime dependencies, then install the Python stack from PyPI. Never install these into the shared Kaggle `.venv`.

```sh
python3.12 -m venv /tmp/qwen35-clean-env
/tmp/qwen35-clean-env/bin/python -m pip install \
  --index-url https://download.pytorch.org/whl/cu128 \
  --extra-index-url https://pypi.nvidia.com \
  --extra-index-url https://pypi.org/simple \
  'torch==2.9.0+cu128'
/tmp/qwen35-clean-env/bin/python -m pip install \
  --index-url https://pypi.org/simple \
  --extra-index-url https://download.pytorch.org/whl/cu128 \
  --extra-index-url https://pypi.nvidia.com \
  -r .research/lab/projects/kaggle-name-that-llm/specs/2026-11-09-qwen35-runtime-lock.txt
```

The [plain requirements lock](2026-11-09-qwen35-runtime-lock.txt) is the resolved full package set.

## Preflight findings

- The pinned model revision has 426 text-backbone tensors. Removing only `model.language_model.` maps every key and tensor shape exactly to `Qwen3_5TextModel`; a CPU BF16 forward returned finite `(1, 4, 4096)` hidden states. The same result was previously checked before adding FLA, with fallback kernels; adding FLA only supplies the CUDA implementation and does not alter checkpoint mapping.
- PEFT 0.18.1 applies all 248 registered target linear layers with 43,278,336 trainable adapter parameters. PEFT 0.17.1 is incompatible with Transformers 5.2.0.
- FLA is discoverable by Transformers 5.2.0 and exports both required Gated DeltaNet functions. These checks are import/CPU metadata checks, not kernel execution.
- The final batched classifier should gather the last non-padding position from `attention_mask`; the pinned tokenizer uses right padding.
- This `/tmp` lock is a verified environment baseline, not approval to bypass the main spec's resource/runtime pilot or the Host142 GPU1 queue.
