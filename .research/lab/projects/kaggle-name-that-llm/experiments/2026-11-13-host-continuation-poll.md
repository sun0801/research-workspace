---
date: 2026-11-13
project: kaggle-name-that-llm
type: host-continuation-poll
---

# Host continuation poll — 2026-11-13

## 15:51 JST — 担当をCodex CLIからClaude Code CLIへ切り替え

- ユーザーの許可により、担当をClaude Code CLI（tmux `claude-kaggle`、`claude --model sonnet --advisor fable`）へ切り替える。根拠はspecの「担当エージェントの切り替え（2026-11-13、ユーザー承認）」。
- Codexのgoalは11/12 21:38から`blocked`のまま。再開しない。止まった原因は利用枠ではなく、Host142の状態を`ssh 142`で確認しようとして、strict host-key確認に失敗し続けたこと。CodexもClaude CodeもHost142の上で動いているので、今後Host142はSSHを使わずローカルのコマンドで確認する。
- 引き継ぎ時点の状態（Claude Code、読み取りのみで確認）
  - Host142：GPU0は15 MiB・0%、GPU1は172 MiB・0%。`gpu_experiment.py`・`gpu_qwen*`のworkerは無い。停止中（`T`）のCandidate09 watcher（PID `3748103`、`/tmp/qwen14b-candidate09-eval-watcher.sh`）が残っている。
  - Host141：GPU0は171 MiB・0%、GPU1/2は15 MiB・0%で、compute processは無い。
  - Kaggle：実行中のkernelは無い（READMEの記録による）。
- 再開位置：READMEの「現在の状況」にあるとおり、次はHost142 GPU1でのMistral＋Spectral独立確認（[確認spec](../specs/2026-11-12-mistral-spectral-complementarity-confirmation-spec.md)）。queue・current-runner pilot・資源gateを確認してから始める。

## 15:55 JST — Mistral current-runner pilot通過、confirmation起動（Claude Code）

- gate：Host142はローカル確認でGPU0/1とも空き、登録queueのPIDは全て終了、`.gpu1-run.lock`は空、MemAvailable約205 GiB、`--guard 15`は5h残84%。停止中のCandidate09 watcher（PID `3748103`）は再開していない（Mistralより先に走るため）。
- 旧pilotは `pilot-legacy-runner-3bd614d9.json`（原本）と `pilot-superseded.json` に保存。現行runner（prefix `7723b086`）で同一config・GPU1（UUID `GPU-8a059266-...`）のpilotを実行し、`pilot_complete`（loss 2.453、step 1.30秒、peak 14,502 MiB、free 17,104 MiB、`pass_reserve` true）。
- 起動：tmux `mistral-confirm`（PID `2872240`、Host142 GPU1、flock `artifacts/.gpu1-run.lock`）、`--split confirmation --resume`、ログ `artifacts/gpu03-mistral-7b-v0-1-openpool-v15/confirmation-run.log`。落ちた場合は同じコマンドで `--resume` 再開。
- 次：全5 foldのconfirmation OOF完了後、[確認spec](../specs/2026-11-12-mistral-spectral-complementarity-confirmation-spec.md)のCPU評価（`artifacts/cpu-mistral-spectral-complementarity-confirmation-v1/`）。

## 23:01 JST — Mistral confirmation fold 0完了

- `mistral-confirm`（Host142 GPU1、PID `2872240`）のconfirmation fold 0が22:48 JSTに完了（BA `.561111`、VRAM peak 14,368 MiB、MemAvailable 209 GiB）。開始15:55から約6.9時間。残り4 foldは約28時間の見込みで、全5 fold完了は11/15 03時ごろ。完了後に[確認spec](../specs/2026-11-12-mistral-spectral-complementarity-confirmation-spec.md)のCPU評価へ進む。
- 同日の他の状況: v13 Spectral付きNotebookはPublic `.560`（[ログ](2026-11-13-baseline-spectral-notebook-lb-check.md)）。Qwen3-14B QLoRAのA4000 pilotは資源gate不通過で棄却（[ログ](2026-11-13-qwen3-14b-qlora-a4000-pilot.md)）。

## 11/14 05:44 JST — Mistral confirmation fold 1完了

- fold 1が05:38 JSTに完了（BA `.583333`、VRAM peak 14,368 MiB、MemAvailable 209 GiB）。fold 0は`.561111`。所要は約6.8時間。残り3 foldは約20時間で、全5 fold完了は11/15 02〜03時ごろの見込み。

## 11/14 12:42 JST — Mistral confirmation fold 2完了

- fold 2が12:27 JSTに完了（BA `.566667`、VRAM peak 14,368 MiB、MemAvailable 209 GiB）。fold 0〜2は `.561` / `.583` / `.567`。所要は約6.8時間。残り2 foldは約13.6時間で、全5 fold完了は11/15 02時ごろの見込み。

## 11/14 13:20 JST — 担当をClaude CodeからCodexへ戻す（引き継ぎ）

- ユーザーの指示により、担当をCodexへ戻す（Codexの週間枠リセットのため）。Claude Codeの`/loop`の次回予約は解除済み。新しい実験・提出・実装は始めていない。
- **実行中job**: tmux `mistral-confirm`（Host142 GPU1 `GPU-8a059266-...`、PID`2872240`、flock`artifacts/.gpu1-run.lock`）。`--split confirmation --resume`、ログ`artifacts/gpu03-mistral-7b-v0-1-openpool-v15/confirmation-run.log`。fold 0〜2完了（BA`.561`/`.583`/`.567`）、fold 3は11/14 19:15ごろ、fold 4を含む全5 fold完了は11/15 02時ごろ（1 fold約6.8h）。再開が要る場合は同じコマンドに`--resume`（コマンドは15:55の節）。**止めない・二重起動しない。** 停止中のCandidate09 watcher（PID`3748103`）は再開しない（GPU1のqueue判断はMistral完了後）。
- **次に確認すること**: (1) fold 3・4の完了を確認し、各fold完了を1回だけ追記。(2) 全5 fold完了後、[確認spec](../specs/2026-11-12-mistral-spectral-complementarity-confirmation-spec.md)のCPU評価（1スレッド。評価runnerはconfirmation OOF完成後に新規作成、出力は`artifacts/cpu-mistral-spectral-complementarity-confirmation-v1/`）。(3) 通過した場合のみ、`.769`（11/13）とCV-LB対応（v12 `.541`・v13 `.560`、約1/4しか転移しない点）を踏まえてprivate Notebook runtime検証の要否を判断。通過しなければ棄却。
- **承認待ち**: 16GB GPU（Host141 GPU0〜2、Host142 GPU0）で回せる未実施候補は、4-bit＋Open Pool二段階LoRA runnerの新規実装（OLMo2-7B等）のみ。runner新規実装・数日規模の学習を伴うため、ユーザーの実装開始承認が要る。official-only QLoRAは候補10（BA`.254`）で棄却済み、Qwen3-14B QLoRAはA4000でpilot不通過のため、同じ領域は繰り返さない。
- **Claude Codeセッションで作ったもの**: spec — [`2026-11-13-baseline-spectral-notebook-lb-check-spec.md`](../specs/2026-11-13-baseline-spectral-notebook-lb-check-spec.md)、[`2026-11-13-qwen3-14b-qlora-a4000-spec.md`](../specs/2026-11-13-qwen3-14b-qlora-a4000-spec.md)。ログ — [`2026-11-13-baseline-spectral-notebook-lb-check.md`](2026-11-13-baseline-spectral-notebook-lb-check.md)、[`2026-11-13-qwen3-14b-qlora-a4000-pilot.md`](2026-11-13-qwen3-14b-qlora-a4000-pilot.md)。実装（`/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/`）— `notebooks/spectral-port/spectral_cell.py`（凍結Spectralの移植）、`notebooks/name-that-llm-private-baseline-v13-spectral-source/`（v13 Notebook、kernel`suntree0801/name-that-llm-private-baseline-blend-v13-spectral`）、`scripts/verify_spectral_port.py`・`scripts/check_spectral_pooled.py`、`configs/gpu17-qwen3-14b-qlora-a4000-prompt-grouped.json`。
- **利用枠の確認**: Claude側は`claude_rate_limit.py --guard 15`（11/14 13:18時点 5h残43%・週間100%）。Codex側は`codex_rate_limit.py --guard 15`。

## 11/14 13:20 JST — Mistral confirmation fold 3 in progress

- Host142 was checked locally (hostname `142-X10DAi`; no SSH). tmux `mistral-confirm` and PID `2872240` are alive with the registered `--split confirmation --resume` command. The log records fold 2 completion at 12:27 JST and fold 3 data preparation immediately afterward; the latest output is checkpoint-shard loading, with no fold 3 completion event yet.
- GPU1 is the pinned UUID (`GPU-8a059266-...`), using 15,008 MiB with 17,092 MiB free at 35% utilization. `MemAvailable` is 218,022,716 kB. The candidate lock file exists. No process or job was changed.
- `.agents/skills/kaggle-workflow/scripts/codex_rate_limit.py --guard 15` passed at 13:19:45 JST: 5-hour and weekly windows both 100% remaining.
- Next light poll: 13:50 JST. Based on the prior ~6.8 h/fold, fold 3 is estimated around 19:15 and all five folds around Nov 15 02:00; these are estimates, not completion evidence.

## 11/14 19:01 JST — Mistral confirmation fold 3 stage progress

- Host142 was checked locally. `mistral-confirm`/PID `2872240` remains alive on GPU1; no state change was made. Fold 3 stage 1 completed at 18:37 JST (mean loss 1.5854, peak allocated 14,368 MiB), and stage 2 epoch 1 completed at 18:55 JST (mean loss 1.2721). Fold 3 has not completed; stage 2 is configured for two epochs.
- GPU1 remains on the registered UUID, using 15,008 MiB with 17,092 MiB free. Host `MemAvailable` is about 203 GiB. Fold completion near 19:15 and all five folds near Nov 15 02:00 remain estimates.
- OLMo primary concurrently remains active on GPU0; its 19:01 checkpoint is recorded in [the OLMo experiment log](2026-11-14-olmo2-7b-4bit-openpool-lora.md). Rate guard passed: 5-hour 99%, weekly 98%. Next light poll: 19:31 JST.

## 11/14 19:31 JST — Mistral confirmation fold 3 complete

- Host142 local poll confirmed `mistral-confirm`/PID `2872240` remains alive on the registered GPU1 UUID. Fold 3 completed at 19:14 JST with balanced accuracy `.586079` and peak allocated VRAM 14,368 MiB. Fold 4 data preparation began immediately afterward; no fold 4 completion yet.
- GPU1 uses 15,008 MiB with 17,092 MiB free; host `MemAvailable` is about 203 GiB. No job or GPU state was changed. All-fold completion near Nov 15 02:00 remains an estimate.
- OLMo primary remains active on GPU0 at step 1350; details are in [the OLMo experiment log](2026-11-14-olmo2-7b-4bit-openpool-lora.md). Rate guard passed: 5-hour 99%, weekly 98%. Next light poll: 20:01 JST.

## 11/15 01:30 JST — Mistral confirmation fold 4 stage 1 complete

- Host142 local poll confirmed `mistral-confirm`/PID `2872240` remains alive on GPU1. Fold 4 stage 1 completed at 01:20 JST (mean loss 1.5856, peak allocated VRAM 14,368 MiB); fold 4 itself has not completed yet. No process or GPU state was changed.
- GPU1 remains on the registered UUID, using 15,008 MiB with 17,092 MiB free. Host `MemAvailable` is about 203 GiB.
- OLMo primary concurrently remains active on GPU0 at fold 1 stage 1 step 275; details are in [the OLMo experiment log](2026-11-14-olmo2-7b-4bit-openpool-lora.md). Rate guard passed: 5-hour 95%, weekly 96%. Next light poll: 02:00 JST.

## 11/15 02:10 JST — Mistral confirmation完了・固定CPU評価通過

- Host142をローカル確認。Mistral confirmationはfold 4まで完了し、tmux `mistral-confirm` とPID`2872240`は終了。GPU1は172 MiB・0%、空き31,929 MiB。GPU1のjob停止や再起動は行っていない。
- fold 4は01:56 JST完了（stage 2 epoch losses 1.27327 / 0.445238、BA`.588889`、peak allocated VRAM 14,368 MiB）。5 fold BAは`.561111` / `.583333` / `.566667` / `.586079` / `.588889`。
- 承認済み[確認spec](../specs/2026-11-12-mistral-spectral-complementarity-confirmation-spec.md)どおり、CPU・1 threadで確認評価を実行。2,699行・150 prompts・18 classes、baselineと凍結Spectralの再現はexact。固定candidate `(3*baseline_probability + softmax(Mistral_logits))/4` の後にSpectralを適用した。
- confirmation BAは基準`.653828`から`.676823`へ`+.022995`。paired prompt bootstrap（5,000回、seed 42）の95% CIは`[+.011596, +.034074]`。fold別の基準→candidate BAは`.624074→.637037`、`.679630→.690741`、`.648148→.679630`、`.674713→.687995`、`.642593→.688889`。
- 18クラスのfold平均recallでは14クラスが改善、4クラスが低下（平均差`+.023027`）。最大低下はgemini-3.8-flash（`-.040`）、claude-opus-5（`-.033`）、glm-5.3（`-.020`）。全クラス×foldの詳細は同summary JSONの`metrics.per_fold[].class_recalls`。
- mild retention simulationは平均delta`+.020751`・20/20 positive、moderateは`+.017810`・20/20 positive。specの確認gateを通過し独立confirmation上の候補として採用。ただしNotebook push・提出は未承認で未実施。評価出力は`/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/artifacts/cpu-mistral-spectral-complementarity-confirmation-v1/`。
- OLMo primaryはHost142 GPU0で継続（PID`3469081`、02:10時点で稼働）。同時点のGPU0は7,517 MiB使用・8,458 MiB空き、MemAvailable約208 GiB。最後に読めたcheckpointはfold 1 stage 1 step 425（02:01 JST）。次の軽量pollは02:30 JST。
- rate guardは5h残93%・週間残96%で通過。runner SHA-256 prefixは`0c70e361`（評価summary記録）。
