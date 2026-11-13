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
