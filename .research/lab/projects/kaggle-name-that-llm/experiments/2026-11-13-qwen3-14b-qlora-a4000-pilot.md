---
date: 2026-11-13
project: kaggle-name-that-llm
type: experiment-log
spec: ../specs/2026-11-13-qwen3-14b-qlora-a4000-spec.md
---

# Qwen3-14B QLoRA（Host142 GPU0 A4000）pilot — 資源gate不通過

## 17:30 JST — pilot結果: 棄却（full OOFは開始しない）

- 実行: tmux `qwen14-a4000-pilot`、Host142 GPU0 `GPU-135ac6e4-...`（A4000 16,376 MiB）、config `gpu17-...`（sha256先頭 `04885ede`）、`--pilot`。起動前は`--guard 15`（5h残69%）、2回のsnapshotでGPU0は18 MiB・compute processなし、MemAvailable約203 GiB。run dir `artifacts/gpu17-qwen3-14b-qlora-a4000-prompt-grouped/`。
- 結果（`pilot.json`）: peak 11,892 MiB（allocated 11,549）、step 26.5秒、step後の空き3,849 MiB < reserve 4,094 MiB（約245 MiB不足）で `pass_resource_gate=false`。`finite_gradients=false`（fp16 GradScalerの初期scale 65536での最初のstepで、scaler起因の可能性があるが原因は未切り分け）、`finite_logits_loss=true`。見積り: 全5 fold OOF 約4.96h、Kaggle 4,000行推論 約5.51h（9h内）。
- 判定: specの規則どおり、資源gate不通過のためfull OOFへ進まない。系列長・microbatch・量子化設定を縮めて載せる変更は別の比較になるので行わない。この構成（16GB A4000、512 token、microbatch 2）はこのspecでは不採用。32GB機（Host142 GPU1）での候補09は、Mistral confirmation後のGPU1 queueの判断として残る。
- GPU0は解放済み（tmux終了、compute processなし）。

## 17:45 JST — 追記: 勾配flagの読み方と次候補の検討

- `finite_gradients=false`は実際の異常: runner（`src/gpu_qwen14b_qlora.py`）は`scaler.unscale_()`の後で`p.grad`の有限性を検査する。候補10（Mistral QLoRA）でも同じ現象があり、`grad_scaler_init_scale`を1,024に下げて通過した前例がある（[候補10 spec](../specs/2026-11-08-mistral-7b-v0-1-qlora-official-only-spec.md)）。候補09のconfig（既定65,536）をGPU1で走らせる場合も、同様に初期scaleの変更（pilot修正）が必要になる可能性が高い。今回はVRAM gateでも不通過のため、scaleは試していない。
- 候補10（official-only・NF4・Mistral-7B、Host141 A4000）のprimary BAは`.254`で棄却済み。official行だけのQLoRAは、Open Pool二段階LoRA（Qwen3-8B・Mistral）より大きく劣る。Qwen3-14Bのofficial-only QLoRAも同じ領域で、見込みは高くなかった。
- 16GBで載る残りの候補: OLMo2-7BのNF4 QLoRAをofficial-onlyで走らせるのは、候補10と同じ領域の繰り返しになるため選ばない。Open Pool二段階をNF4で行うには、4-bitとpoolを両立するrunnerの新規実装が要る（`gpu_experiment.py`はBF16、`gpu_qwen14b_qlora.py`はofficial-only一段）。実装と数日規模の学習を伴うため、実装開始の承認が要る判断としてユーザーへ報告する。
