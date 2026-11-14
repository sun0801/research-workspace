---
date: 2026-11-14
project: kaggle-name-that-llm
type: experiment-log
spec: ../specs/2026-11-14-olmo2-7b-4bit-openpool-lora-spec.md
---

# OLMo 2 1124 7B 4-bit + Open Pool v15 two-stage LoRA

## 14:00 JST — 承認spec作成、実装前

- ユーザーの2026-11-14承認に基づき、NF4 + double quantization + BF16 computeの二段階LoRA実験specを作成。対象はOLMo 2 1124 7B、Open Pool v15 stage 1、各official fold stage 2。変更範囲・16GB GPU gate・pilot・primary/independent confirmation・採用条件・既存runnerとの差を登録した。[spec](../specs/2026-11-14-olmo2-7b-4bit-openpool-lora-spec.md)
- 実装先は新規`src/gpu_openpool_qlora.py`と`configs/gpu18-olmo2-1124-7b-4bit-openpool-v15.json`のみ。既存candidate14 config、generic BF16 runner、Qwen3-14B QLoRA runnerは変更しない。依存環境はbitsandbytes 0.50.2、PEFT 0.17.1、Transformers 4.57.1、Accelerate 1.10.1、PyTorch 2.9.0。OLMo重みの有無・pilot・学習は未確認/未実行。
- rate guardは13:56:21 JSTに通過（5h残97%、週間残100%）。13:56 Host142ローカル確認ではGPU0が空き、GPU1で既存`mistral-confirm` PID`2872240`が継続。GPU1には触れない。pilot起動直前に選択GPUのsnapshot・process・lock・RAM・disk gateを取り直す。
- 次: 新規runner/configを実装して静的確認。pilotの直前に再度rate guardと資源gateを実行し、条件を満たす16GB GPU一つだけでpilotする。Mistralは30分pollで継続監視。

## 14:15 JST — 新規runner/config実装、静的確認完了

- 新規`src/gpu_openpool_qlora.py`とcandidate18 configを実装。既存generic runnerのfoldwise Open Pool除外・二段階学習を保ち、NF4/double quant/BF16 compute、k-bit preparation、quantized checkpoint reload、UUID固定、GPU0 global lock、disk/RAM/VRAM gateを追加。checkpointはoptimizer step 500回ごととepoch終端にatomic保存し、resume時にstage/epoch/batch位置から再開する。final-fit・test推論・submission生成のCLI経路は含めない。
- `.venv`でPython compileとconfig schema検証は通過。train/pool/prompt reconstruction/primary foldsは存在し、model cacheにOLMo重みはまだない。ディスク空きは約7,020 GiB。モデル取得、GPU pilot、学習は未実行。
- 次: rate guardを再確認し、Kaggle CLIから登録済みOLMo2 version 1をcandidate18専用cacheへ取得する。取得後にpilot直前のrate/GPU/RAM/disk/lock gateを取り直す。Host142 GPU1のMistral jobは継続・非接触。
