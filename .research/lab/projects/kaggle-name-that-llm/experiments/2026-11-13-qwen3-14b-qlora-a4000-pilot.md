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
