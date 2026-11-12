---
date: 2026-11-08
project: kaggle-name-that-llm
source: autonomous-goal
status: approved
approval_basis: active-goal-2026-11-06-gpu-autonomous-first-place-spec
execution_status: primary-gates-passed; fixed-addition-screen-positive; confirmation-awaits-current-runner-pilot-and-host142-access
tags: [spec, experiment, gpu, mistral, prompt-grouped]
---

# Mistral-7B-v0.1 Open Pool v15 prompt-grouped候補 Spec

## 目的・根拠

固定した公開Mistral-7B-v0.1 base checkpointを、既存Qwenと同じfoldwise Open Pool v15＋official-train LoRA手順で学習する。公開Discussion 756294の作者はMistral/OLMo two-stage LoRAで5-fold prompt-grouped OOF BA 0.60、Public LB 0.663を自己申告したが、データ・実装・予測は共有されず独立検証もない。この値を再現結果として扱わず、第三者adapter/data/predictionを使わない独立Mistral-only候補を測定する。

本候補は2026-11-06公開LB首位超えgoalの自動候補選択・実装・検証範囲に含む。Kaggle Notebook化・push・提出はOOF採否ゲート通過後の別条件を満たす場合に限る。

## 固定実験

- 実装: `/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/src/gpu_experiment.py`
- 固定config: `configs/gpu03-mistral-7b-v0-1-openpool-v15.json`（SHA-256 `c04ff48178e363dc30c54c6e11c02083c32bc7ccc6cd63ce176cc258ccca494f`）。既存config、Qwen run、CPU baselineは変更しない。
- Model: Kaggle公式 `mistral-ai/mistral/PyTorch/7b-v0.1-hf` version 1（Apache-2.0、15,010,167,643 bytes）。ローカル基準revision `mistralai/Mistral-7B-v0.1@27d67f1b5f57dc0953326b2601d68371d40ea8da`。9ファイル・2 safetensors shardは取得とhash照合済み。Kaggle mirror側hashがないため両者のbyte identityは主張しない。
- Open Pool v15はconfigの均等抽出2,500行/class、sample seed 42、external prompt match threshold 0.40を使用する。foldごとにvalidation prompt群・exact normalized train textを除去し、publisher全train情報を含む`match_weight`は使わない。community adapter・追加生成データ・OOF予測・test labelは使わない。
- Model: Mistral-7B-v0.1 base、32層/hidden 4096、BF16、384 tokens、gradient checkpointing。LoRA rank 16/alpha 32/dropout .05で24層に適用、stage1はfiltered pool 1 epoch、stage2は各fold official trainだけで2 epochs、microbatch 1/effective batch 18、seed 42。configの固定値を変更しない。
- Primaryは保存済みofficial `GroupKFold(prompt_id, 5)`をそのまま使う。Confirmationはconfigで定義済みの独立`GroupKFold(n_splits=5, shuffle=True, random_state=42)`を使用する。
- 採否の主比較対象は現在採用済みlow-pool-weight prompt-centered SVCの同一split OOF: `artifacts/cpu-openpool-prompt-centered-low-pool-weight-v15/primary/oof-all.parquet` と `.../confirmation/oof-all.parquet`。直近保存値はprimary BA `.501934`、confirmation BA `.500818`（2026-11-07）。実行時にID・prompt・fold・labelを再整列確認し、prompt単位paired bootstrap 2,000回以上、seed 42でBA差95% CIを求める。primary CI下限が0以下ならconfirmationを実行しない。両splitでCI下限>0の場合のみOOF採用候補とする。config内の旧baseline注記（4-view LR BA `.384504`）は現行baselineとして使わない。

## 資源・実行ゲート

1. 実行先はhost142のGPU1、UUID `GPU-8a059266-7ede-0427-ff30-08ba7a9b5224`（32,623 MiB RTX PRO 4500 Blackwell）のみ。GPU1を使うQwen02、候補06、候補08等の登録済み処理が終わり、GPU1 lockが空くまでは待つ。host141の16,376 MiB A4000では実行しない。Qwen04/WeMMがGPU0で継続中の場合も、GPU1の複数snapshot preflightで自分以外のcompute PID不在、UUID一致、ホストMemAvailable 16 GiB以上を確認する。
2. 起動直前に`.agents/skills/kaggle-workflow/scripts/codex_rate_limit.py --guard 15`を通す。既存Qwen・他研究processを停止・変更しない。GPUをUUID限定し、候補lockで自分のrun間競合を防ぐ。
3. configのpilotを同一runner/config/model/GPUで実行し、model load、forward、backward、optimizer step、finite lossを確認する。free VRAMの残量は`max(4 GiB, 全容量の25%)`以上（config reserve 8,156 MiB）を保つ。pilotで失敗・OOM・16 GiB host RAM floor割れの場合はfull runへ進まない。
4. 成功pilotのstep時間から同じ固定条件の全fold所要時間を見積もり、安全条件と利用枠を各長時間run開始前に再確認する。各fold checkpoint・OOF・resume位置を保持し、OOM時はこの候補の子processだけを停止する。
5. full primary後はcurrent adopted baselineとpaired analysisを完了してからconfirmation可否を決める。Notebook実行は両ゲート通過後のみ検討し、その時点のoffline・9時間以内・license/provenance・private object・提出枠・top score条件を再確認する。

## 現在の状態

- Fixed Mistral v0.1 revision/model/config and all 5 primary prompt-grouped OOF folds are saved under `artifacts/gpu03-mistral-7b-v0-1-openpool-v15/primary/`. The primary comparison versus adopted prompt-centered SVC (2,699 rows, 150 prompts, 5,000 paired prompt-bootstrap replicates, seed 42) gives Mistral BA `.587566` vs SVC `.501934`, delta CI `[+.062961, +.107777]`; the Mistral primary adoption gate passed.
- A fixed Mistral 1/4 addition followed by the frozen Spectral transform passed a primary-only complementarity screen: BA `.689791` vs existing Spectral `.664952`, delta `+.024840`, 5,000 prompt-paired bootstrap CI `[+.013063, +.036412]`; mild/moderate retention simulations were positive in 20/20 seeds each. This remains primary-only and does not replace independent confirmation. See [screen log](../experiments/2026-11-12-mistral-spectral-complementarity-screen.md).
- Confirmation has no OOF result. The 2026-11-11 preflight passed resource checks but the runner stopped before training because the saved pilot evidence does not match the current runner. The pilot was recorded with runner prefix `3bd614d9`; current worktree runner prefix is `7723b086`, while the fixed config prefix remains `c04ff481`. The inspected uncommitted runner diff changes checksum manifests/pilot integrity logging and final-fit metadata; it does not alter the training loop. Preserve the existing primary folds and pilot evidence.
- Next: once Host142's host key can be verified and the registered GPU1 queue is safely clear, preserve the legacy `pilot.json`, rerun the unchanged fixed-configuration pilot with the current runner on its specified GPU1, and only after it passes launch the independent confirmation folds under this approved spec. Do not reassign the run to Host141 or overlap another user's work.

## 関連資料

- [公開LB首位超えgoal spec](2026-11-06-gpu-autonomous-first-place-spec.md)
- 固定config: `/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/configs/gpu03-mistral-7b-v0-1-openpool-v15.json`
- [実験ログ](../experiments/2026-11-06-gpu-autonomous-initial-check.md)
