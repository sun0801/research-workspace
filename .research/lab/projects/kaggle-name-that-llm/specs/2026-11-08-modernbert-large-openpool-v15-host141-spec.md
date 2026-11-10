---
project: kaggle-name-that-llm
status: approved-under-active-goal
execution_status: pilot-passed-primary-running
created: 2026-11-08
last_updated: 2026-11-08
tags: [spec, experiment, gpu, modernbert, kaggle]
---

# ModernBERT-Large + Open Pool v15 Host141 Spec

## 目的と根拠

既存ModernBERT-Base候補と同じOpen Pool v15 / prompt-grouped protocolを使い、公式ModernBERT-Large checkpointへのcapacity scalingがOOF性能やQwen/SVCとの誤り補完性を高めるか測る。Kaggle Discussion 754860 comment 3551013のCV `.616` / public LB `.575` は投稿者の自己申告であり、version・split・pool・leakage handlingが不足している。ModernBERT-Base primaryはまだ未完了のため、この候補は同系列・別容量の並行仮説として事前登録し、報告値を再現済みの証拠に使わない。

公式Kaggle model variation [Answer.AI ModernBERT-Large](https://www.kaggle.com/models/answer-ai/modernbert/PyTorch/large) version 2はfine-tunable、Apache 2.0、listed uncompressed size 1,585,746,891 bytes。download後に`config.json`でarchitecture・hidden size・層数を確定する。想定はModernBERT-largeの28 encoder layersだが、runner/configはpilot前に公式configで照合し、不一致なら本specとconfigを直してからpilotする。

## 固定評価

- 学習データはOpen Pool v15とofficial trainのみ。既存candidate12と同じexact-text removal、fold validation prompt-group removal、uniform 2,500/class capを適用し`match_weight`を使わない。
- Saved `GroupKFold(prompt_id)` primary 5 folds、seed42、max length384、BF16、microbatch1、gradient checkpointing、effective batch rows18。Stage1 filtered pool 1 epoch、stage2 current-fold official train 2 epochs。LoRA rank16/alpha32/dropout `.05`。全encoder layerの`attn.Wqkv`, `attn.Wo`, `mlp.Wi`, `mlp.Wo`へ適用し、pilotで全対象layer/moduleとhidden-state indexを確認する。
- Pooled layersはモデル最終configに対し`[2,4,8,12,16,20,24,28]`を想定。各値が`output_hidden_states`に有効なrange内であることをpilotで確認する。不適合ならprimary前にspec/config更新。
- Primary OOF balanced accuracyとcurrent CPU bestのprompt-paired bootstrap（2,000回以上、seed42）を評価し95% CI lower bound >0を adoption gateとする。既存Qwen blendへのOOF追加価値も同じfoldで測る。採用時のみ独立confirmationへ進む。

## 実装・配置

- Implementation root: `/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/`。
- Add only `src/gpu_modernbert_large_experiment.py` and `configs/gpu13-modernbert-large-openpool-v15.json`; do not alter shared `src/gpu_experiment.py` or active candidate12 runner/config/hash.
- Host `141-X9DAi`, GPU0 UUID `GPU-c542e903-dac3-5541-ea10-2b66b06e5f61`, RTX A4000. Candidate11 remains on Host141 GPU2, candidate12 on GPU1. Do not share a GPU or migrate automatically.
- Cache `artifacts/model-cache/modernbert-large-kaggle-v2/`, run `artifacts/gpu13-modernbert-large-openpool-v15/`; model/cache/run artifacts are Git-excluded.

## 安全・実行ゲート

1. Long-run and pilot each require a fresh `.agents/skills/kaggle-workflow/scripts/codex_rate_limit.py --guard 15`, exact UUID/device check, no external compute PID on GPU0, double snapshot, free VRAM reserve >=4,096 MiB, and host MemAvailable >=16 GiB.
2. Download Kaggle official variation version 2; compare every listed filename and byte size. Confirm actual config architecture, hidden size/layer count, tokenizer, all weights before pilot.
3. Isolated runner performs load/forward/backward/optimizer-step pilot and verifies all expected LoRA projection modules. Start primary only when pilot peak leaves reserve and RAM floor passes. Same-method OOM/retry is prohibited.
4. Resume only from the latest completed epoch checkpoint. SIGTERM requests stop at the next batch boundary; in-progress epoch is not checkpointed. Preserve PID, log, checkpoint, config/hash, and exact resume command.
5. No Notebook creation, Kaggle write, or submission within this candidate spec.

