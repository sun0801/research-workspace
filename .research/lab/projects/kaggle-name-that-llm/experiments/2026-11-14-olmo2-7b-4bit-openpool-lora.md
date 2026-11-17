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
- rate guardは13:56:21 JSTに通過（5h残97%、週間残100%）。13:56 Host142ローカル確認ではGPU0が空き、当時GPU1で既存`mistral-confirm` PID`2872240`が継続していたため触れなかった。この予約はユーザーにより11/17 23:08 JSTに解除済み（[継続ログ](2026-11-13-host-continuation-poll.md#1117-2308-jst-host142-gpu1予約解除候補準備の再開)）。pilot起動直前に選択GPUのsnapshot・process・lock・RAM・disk gateを取り直す。
- 次: 新規runner/configを実装して静的確認。pilotの直前に再度rate guardと資源gateを実行し、条件を満たす16GB GPU一つだけでpilotする。Mistralは30分pollで継続監視。

## 14:15 JST — 新規runner/config実装、静的確認完了

- 新規`src/gpu_openpool_qlora.py`とcandidate18 configを実装。既存generic runnerのfoldwise Open Pool除外・二段階学習を保ち、NF4/double quant/BF16 compute、k-bit preparation、quantized checkpoint reload、UUID固定、GPU0 global lock、disk/RAM/VRAM gateを追加。checkpointはoptimizer step 500回ごととepoch終端にatomic保存し、resume時にstage/epoch/batch位置から再開する。final-fit・test推論・submission生成のCLI経路は含めない。
- `.venv`でPython compileとconfig schema検証は通過。train/pool/prompt reconstruction/primary foldsは存在し、model cacheにOLMo重みはまだない。ディスク空きは約7,020 GiB。モデル取得、GPU pilot、学習は未実行。
- 次: rate guardを再確認し、Kaggle CLIから登録済みOLMo2 version 1をcandidate18専用cacheへ取得する。取得後にpilot直前のrate/GPU/RAM/disk/lock gateを取り直す。Host142 GPU1のMistral jobは継続・非接触。

## 14:34 JST — OLMo2 version 1取得完了

- 取得command: `uv run --env-file .env kaggle models instances versions download allenai/olmo-2/transformers/1124-7b/1 -p /mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/artifacts/model-cache/candidate18-olmo2-1124-7b-hf --untar --quiet`（exit 0）。cache合計は約28 GiB、6 safetensors shardsの合計29,194,510,544 bytes。`config.json`は`model_type=olmo2`、32 layers、hidden size 4096。tokenizer filesも存在する。64桁hashは転記していない。
- 13:56 JSTに記録した5h/weekly rate guardは97%/100%で通過。取得開始前の14:17 JST再確認は96%/99%で通過。次のpilot開始直前にもguardを再確認する。
- OLMo重みは展開済み。GPU pilot・full OOFは未実行。次はHost142 GPU0のUUID・2 snapshot・compute PID・global lock・MemAvailable・diskを取り直し、gate通過時だけ384-token pilotを行う。Host142 GPU1のMistral jobは14:27 pollで継続を確認し、変更なし。

## 14:37 JST — NF4 pilot起動

- rate guardは14:36:56 JSTに通過（5h残95%、週間残99%）。Host142 GPU0の直前2 snapshot（14:37:15/20 JST）は同じUUID・A4000、15 MiB使用・15,960 MiB free、target compute PIDなし。`artifacts/.gpu0-run.lock`取得可能、MemAvailable約208 GiB、disk空き6,993 GiB。許容reserve 4,096 MiB、pilot gateを満たした。
- Host142ローカルでtmux `olmo4-pilot`を起動。PID`3464206`、CUDA_VISIBLE_DEVICESはGPU0 UUID固定、config `gpu18-olmo2-1124-7b-4bit-openpool-v15.json`、model cache `candidate18-olmo2-1124-7b-hf`、log `artifacts/gpu18-olmo2-1124-7b-4bit-openpool-v15/pilot-run.log`。コマンドは新規runnerの`--pilot`。
- 起動直後はPython runnerが生存し、GPU0は18 MiB使用、GPU1はMistral PID`2872240`が15,008 MiB使用。pilotは実行中で、pass/fail・peak・step時間はまだ未確定。GPU1には触れていない。

## 14:38 JST — NF4 pilot pass

- `pilot.json`でfinite outputs/loss、finite trainable gradients、`pass_reserve=true`を確認。Host142 GPU0 A4000、measured peak reserved 7,284 MiB（allocated 5,372 MiB）、pilot開始snapshot free 15,958 MiB、step 1.493秒、終了時free 8,457 MiB、MemAvailable 205.84 GiB。4,096 MiB reserve gateを通過。
- Integrity check: 一致。`sha256sum -c artifacts/gpu18-olmo2-1124-7b-4bit-openpool-v15/pilot-SHA256SUMS`。config prefix `19260ce9`、runner prefix `3acb3724`。
- pilotの1 sample時間はfull-run時間見積りの不確実性が大きいため確定所要時間とは扱わない。full OOFは25 optimizer stepごと（およそ450 training rows相当）とepoch終端にatomic checkpointを残し、中断時は同じstage/epoch/batch位置から再開する。
- 次: pilot後のrate guardを再確認し、Host142 GPU0のUUID・compute process・global lock・RAM・disk・free VRAMを2 snapshotで確認してprimary OOFを開始する。Mistral GPU1は並行継続し、次pollは14:57 JST。

## 14:43 JST — checkpoint頻度固定に伴う再pilot

- 初回pilotはpass済みだが、full OOF停止時の巻き戻りを抑えるためcheckpointを500から25 optimizer stepsごとへ変更。configとrunnerのchecksum identityが変わるため、初回`pilot.json`はfull runの根拠にせず、`pilot-previous-14-38/`へ保全して最終設定で再pilotする。runnerはpilot証拠の上書きを拒否する。
- 変更後の構文/config確認は通過。モデル重み・学習条件・GPU UUID・LoRA範囲は変更していない。次はrate guardとHost142 GPU0資源gateを再実行し、pilotをやり直す。

## 14:45 JST — 最終identityでpilot再実行

- rate guardは14:45:00 JSTに通過（5h残94%、週間残99%）。Host142 GPU0の14:45:13/18 JST 2 snapshotは同じUUID、15 MiB使用・15,960 MiB free、compute PIDなし、global lock free、MemAvailable約208 GiB、disk空き6,993 GiB。
- tmux `olmo4-pilot`、Host142 GPU0、runner PID`3468098`で`--pilot`再実行中。最終configはcheckpoint interval 25、model cache/LoRA/data settingsは初回pilotから不変。初回pilot evidenceは`pilot-previous-14-38/`に残した。

## 14:46 JST — 最終identity pilot pass

- Updated pilot is passing: finite outputs/loss and trainable gradients, `pass_reserve=true`, peak reserved 7,284 MiB, end free 8,457 MiB, MemAvailable 205.80 GiB, step 1.335 s. Integrity check: 一致。`sha256sum -c artifacts/gpu18-olmo2-1124-7b-4bit-openpool-v15/pilot-SHA256SUMS`; config prefix `1b351f9c`, runner prefix `a45e8eeb`.

## 14:47 JST — primary OOF開始

- 起動前rate guardは14:47:35 JSTに通過（5h残93%、weekly残99%）。Host142 GPU0の14:47:48/53 JST 2 snapshotは同一UUID、15 MiB使用・15,960 MiB free、target compute PIDなし、global lock free、MemAvailable約208 GiB、disk空き6,993 GiB。
- tmux `olmo4-primary`、Host142 GPU0、runner PID`3469081`、`--split primary`。CUDA_VISIBLE_DEVICESはGPU0 UUID固定。config/runner identityはpassing pilotに一致。checkpointは25 optimizer stepごととepoch終端に保存。logは`artifacts/gpu18-olmo2-1124-7b-4bit-openpool-v15/primary-run.log`。
- OOFは起動直後のためfold進捗・所要時間は未確定。Host142 GPU1は引き続きMistral PID`2872240`が使用中で、変更していない。次の軽量pollは14:57 JST。
- Evaluation readiness: adopted baseline primary is aligned with the saved primary fold assignment on all 2,699 IDs, prompt IDs, and labels (150 prompts); the independent confirmation baseline also exists with 2,699 rows. No candidate predictions have been analyzed.

## 14:59 JST — primary checkpoint進捗

- Host142ローカルpollで`olmo4-primary`/PID`3469081`の継続を確認。fold 0 stage 1、optimizer step 50/2500、next batch 900、平均loss 2.8911。最新checkpoint `primary/fold-0/stage1/step-000050`へ再開位置を保存。
- GPU0 UUIDは固定、使用7,517 MiB・free 8,458 MiB、MemAvailable約203 GiB。安全reserveを維持し、stop/errorなし。次の軽量pollは15:29 JST。
- Major-checkpoint rate guardは15:01:11 JSTに通過（5h残92%、週間残99%）。

## 15:31 JST — primary checkpoint進捗

- Host142をローカルpoll。`olmo4-primary`/PID`3469081`はfold 0 stage 1、optimizer step 200/2500で継続。平均loss 2.8165、最新checkpoint `primary/fold-0/stage1/step-000200`、next batch 3600。`stop_requested=false`。
- GPU0は固定UUID、使用7,517 MiB・free 8,458 MiB・利用率87%。Host `MemAvailable`は約203 GiB。Mistral confirmationのtmux/PID`2872240`も継続し、GPU1は15,008 MiB使用・17,092 MiB free。fold 3の完了記録はまだない。
- step 200の区切りでrate guardを確認し通過（5h残91%、週間残99%）。次の軽量pollは16:01 JST。

## 16:01 JST — primary checkpoint進捗

- Host142の定刻pollで`olmo4-primary`/PID`3469081`は継続。fold 0 stage 1、optimizer step 325/2500、平均loss 2.8705、最新checkpoint `primary/fold-0/stage1/step-000325`、next batch 5850。`stop_requested=false`。
- GPU0 UUIDは固定、使用7,517 MiB・free 8,458 MiB、MemAvailable約203 GiB。Mistral confirmationもtmux/PID`2872240`とGPU1使用を維持し、fold 3完了イベントはまだない。Host142 GPU1には変更を加えていない。
- step 325時点のrate guardは通過（5h残91%、週間残99%）。次の軽量pollは16:31 JST。

## 16:31 JST — primary checkpoint進捗

- Host142の定刻pollで`olmo4-primary`/PID`3469081`は継続。fold 0 stage 1、optimizer step 475/2500、平均loss 2.7569、最新checkpoint `primary/fold-0/stage1/step-000475`、next batch 8550。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB。Host `MemAvailable`は約203 GiB。Mistral confirmation（tmux `mistral-confirm`、PID`2872240`）も生存し、GPU1を15,008 MiB使用。fold 3完了イベントはまだない。
- step 475時点のrate guardは通過（5h残91%、週間残99%）。次の軽量pollは17:01 JST。

## 17:01 JST — primary checkpoint進捗

- Host142の定刻pollで`olmo4-primary`/PID`3469081`は継続。fold 0 stage 1、optimizer step 625/2500、平均loss 2.6267、最新checkpoint `primary/fold-0/stage1/step-000625`、next batch 11250。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB、MemAvailable約203 GiB。Mistral confirmationも生存しGPU1を15,008 MiB使用中。fold 3完了イベントはまだない。
- step 625時点のrate guardは通過（5h残90%、週間残98%）。次の軽量pollは17:31 JST。

## 17:31 JST — primary checkpoint進捗

- Host142の定刻pollで`olmo4-primary`/PID`3469081`は継続。fold 0 stage 1、optimizer step 775/2500、平均loss 2.5045、最新checkpoint `primary/fold-0/stage1/step-000775`、next batch 13950。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB、MemAvailable約203 GiB。Mistral confirmationも生存しGPU1を15,008 MiB使用中。fold 3完了イベントはまだない。
- step 775時点のrate guardは通過（5h残90%、週間残98%）。次の軽量pollは18:01 JST。

## 18:01 JST — primary checkpoint進捗

- Host142の定刻pollで`olmo4-primary`/PID`3469081`は継続。fold 0 stage 1、optimizer step 925/2500、平均loss 2.4025、最新checkpoint `primary/fold-0/stage1/step-000925`、next batch 16650。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB、MemAvailable約203 GiB。Mistral confirmationも生存しGPU1を15,008 MiB使用中。fold 3完了イベントはまだない。
- step 925時点のrate guardは通過（5h残89%、週間残98%）。次の軽量pollは18:31 JST。

## 18:31 JST — primary checkpoint進捗

- Host142の定刻pollで`olmo4-primary`/PID`3469081`は継続。fold 0 stage 1、optimizer step 1050/2500、平均loss 2.3272、最新checkpoint `primary/fold-0/stage1/step-001050`、next batch 18900。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB、MemAvailable約203 GiB。Mistral confirmationも生存しGPU1を15,008 MiB使用中。fold 3完了イベントはまだない。
- step 1050時点のrate guardは通過（5h残100%、週間残98%）。次の軽量pollは19:01 JST。

## 19:01 JST — primary checkpoint進捗

- Host142の定刻pollで`olmo4-primary`/PID`3469081`は継続。fold 0 stage 1、optimizer step 1200/2500、平均loss 2.2491、最新checkpoint `primary/fold-0/stage1/step-001200`、next batch 21600。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB、MemAvailable約203 GiB。Mistral confirmationも生存しGPU1を15,008 MiB使用中。fold 3 stage 1とstage 2 epoch 1の完了を確認したが、fold 3自体は処理中。[host poll log](2026-11-13-host-continuation-poll.md)
- step 1200時点のrate guardは通過（5h残99%、週間残98%）。次の軽量pollは19:31 JST。

## 19:31 JST — primary checkpoint進捗

- Host142の定刻pollで`olmo4-primary`/PID`3469081`は継続。fold 0 stage 1、optimizer step 1350/2500、平均loss 2.1739、最新checkpoint `primary/fold-0/stage1/step-001350`、next batch 24300。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB、MemAvailable約203 GiB。Mistral confirmation fold 3がBA`.586079`で完了し、fold 4の準備を開始。[host poll log](2026-11-13-host-continuation-poll.md)
- step 1350時点のrate guardは通過（5h残99%、週間残98%）。次の軽量pollは20:01 JST。

## 20:01 JST — primary checkpoint進捗

- Host142の定刻pollで`olmo4-primary`/PID`3469081`は継続。fold 0 stage 1、optimizer step 1475/2500、平均loss 2.1228、最新checkpoint `primary/fold-0/stage1/step-001475`、next batch 26550。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB、MemAvailable約203 GiB。Mistral confirmationも生存しGPU1を15,008 MiB使用中。fold 4の完了イベントはまだない。
- step 1475時点のrate guardは通過（5h残98%、週間残98%）。次の軽量pollは20:31 JST。

## 20:31 JST — primary checkpoint進捗

- Host142の定刻pollで`olmo4-primary`/PID`3469081`は継続。fold 0 stage 1、optimizer step 1625/2500、平均loss 2.0673、最新checkpoint `primary/fold-0/stage1/step-001625`、next batch 29250。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB、MemAvailable約203 GiB。Mistral confirmationも生存しGPU1を15,008 MiB使用中。前回記録のfold 3完了以降、fold 4の完了イベントはまだない。
- step 1625時点のrate guardは通過（5h残97%、週間残98%）。次の軽量pollは21:01 JST。

## 21:00 JST — primary checkpoint進捗

- Host142の定刻pollで`olmo4-primary`/PID`3469081`は継続。fold 0 stage 1、optimizer step 1750/2500、平均loss 2.0211、最新checkpoint `primary/fold-0/stage1/step-001750`、next batch 31500。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB、MemAvailable約203 GiB。Mistral confirmationも生存しGPU1を15,008 MiB使用中。fold 4完了イベントはまだない。
- step 1750時点のrate guardは通過（5h残97%、週間残98%）。次の軽量pollは21:30 JST。

## 21:30 JST — primary checkpoint進捗

- Host142の定刻pollで`olmo4-primary`/PID`3469081`は継続。fold 0 stage 1、optimizer step 1875/2500、平均loss 1.9783、最新checkpoint `primary/fold-0/stage1/step-001875`、next batch 33750。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB、MemAvailable約203 GiB。Mistral confirmationも生存しGPU1を15,008 MiB使用中。fold 4完了イベントはまだない。
- step 1875時点のrate guardは通過（5h残96%、週間残98%）。次の軽量pollは22:00 JST。

## 22:00 JST — primary checkpoint進捗

- Host142の定刻pollで`olmo4-primary`/PID`3469081`は継続。fold 0 stage 1、optimizer step 2025/2500、平均loss 1.9304、最新checkpoint `primary/fold-0/stage1/step-002025`、next batch 36450。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB、MemAvailable約203 GiB。Mistral confirmationも生存しGPU1を15,008 MiB使用中。fold 4完了イベントはまだない。
- step 2025時点のrate guardは通過（5h残95%、週間残97%）。次の軽量pollは22:30 JST。

## 22:30 JST — primary checkpoint進捗

- Host142の定刻pollで`olmo4-primary`/PID`3469081`は継続。fold 0 stage 1、optimizer step 2175/2500、平均loss 1.8858、最新checkpoint `primary/fold-0/stage1/step-002175`、next batch 39150。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB、MemAvailable約203 GiB。Mistral confirmationも生存しGPU1を15,008 MiB使用中。fold 4完了イベントはまだない。
- step 2175時点のrate guardは通過（5h残94%、週間残97%）。次の軽量pollは23:00 JST。

## 23:00 JST — primary checkpoint進捗

- Host142の定刻pollで`olmo4-primary`/PID`3469081`は継続。fold 0 stage 1、optimizer step 2300/2500、平均loss 1.8512、最新checkpoint `primary/fold-0/stage1/step-002300`、next batch 41400。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB、MemAvailable約203 GiB。Mistral confirmationも生存しGPU1を15,008 MiB使用中。fold 4完了イベントはまだない。
- step 2300時点のrate guardは通過（5h残93%、週間残97%）。次の軽量pollは23:30 JST。

## 23:30 JST — primary checkpoint進捗

- Host142の定刻pollで`olmo4-primary`/PID`3469081`は継続。fold 0 stage 1、optimizer step 2450/2500、平均loss 1.8140、最新checkpoint `primary/fold-0/stage1/step-002450`、next batch 44100。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB、MemAvailable約203 GiB。Mistral confirmationも生存しGPU1を15,008 MiB使用中。fold 4完了イベントはまだない。
- step 2450時点のrate guardは通過（5h残100%、週間残97%）。次の軽量pollは00:00 JST（11/15）。

## 11/15 00:00 JST — fold 0 stage 1完了、stage 2進行

- Host142の定刻pollで`olmo4-primary`/PID`3469081`は継続。fold 0 stage 1がepoch 1完了（mean loss 1.8028、peak allocated/reserved 6,568/7,284 MiB）。official-data stage 2はstep 100、next batch 1800のcheckpoint `primary/fold-0/stage2/step-000100`まで進行。`stop_requested=false`。fold 0自体の完了・予測出力は未確認。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB、MemAvailable約203 GiB。Mistral confirmationも生存しGPU1を15,008 MiB使用中。fold 4完了イベントはまだない。
- Major-checkpoint rate guardは通過（5h残99%、週間残97%）。次の軽量pollは00:30 JST。

## 11/15 00:31 JST — primary fold 0完了

- Host142の定刻pollで`olmo4-primary`/PID`3469081`は継続。primary fold 0が完了（balanced accuracy `.574074`、VRAM peak 6,568 MiB）。直後にfold 1のdata準備と6 shardのmodel loadを確認。fold 1の学習進捗・OOF全体評価は未完了。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB、MemAvailable約203 GiB。Mistral confirmationも生存しGPU1を15,008 MiB使用中。fold 4完了イベントはまだない。
- Fold completion後のrate guardは通過（5h残97%、週間残97%）。次の軽量pollは01:00 JST。

## 11/15 01:01 JST — primary fold 1進捗

- Host142の定刻pollで`olmo4-primary`/PID`3469081`は継続。fold 1 stage 1、optimizer step 150/2500、平均loss 2.8963、最新checkpoint `primary/fold-1/stage1/step-000150`、next batch 2700。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB、MemAvailable約203 GiB。Mistral confirmationも生存しGPU1を15,008 MiB使用中。fold 4完了イベントはまだない。
- Rate guardは通過（5h残96%、週間残97%）。次の軽量pollは01:30 JST。

## 11/15 01:30 JST — primary fold 1進捗

- Host142の定刻pollで`olmo4-primary`/PID`3469081`は継続。fold 1 stage 1、optimizer step 275/2500、平均loss 2.9216、最新checkpoint `primary/fold-1/stage1/step-000275`、next batch 4950。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB、MemAvailable約203 GiB。Mistral fold 4 stage 1完了（mean loss 1.5856、peak allocated 14,368 MiB）を確認したが、fold 4自体は未完了。[host poll log](2026-11-13-host-continuation-poll.md)
- Rate guardは通過（5h残95%、週間残96%）。次の軽量pollは02:00 JST。

## 11/15 02:40 JST — primary fold 1進捗

- Host142ローカルで `olmo4-primary` / PID`3469081`の継続を確認。fold 1 stage 1はoptimizer step 625/2500、mean loss 2.6023、next batch 11250、checkpoint `primary/fold-1/stage1/step-000625`。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB、GPU util 100%。Host `MemAvailable`約208 GiB。Mistral confirmationは完了済みでGPU1は172 MiB・0%。jobには変更を加えていない。
- 次の軽量pollは03:10 JST。

## 11/15 03:10 JST — primary fold 1進捗

- Host142ローカルでPID`3469081`の継続を確認。fold 1 stage 1はoptimizer step 750/2500、mean loss 2.4993、next batch 13500、checkpoint `primary/fold-1/stage1/step-000750`。`stop_requested=false`。
- Checkpoint記録のGPU0空き8,457 MiB、MemAvailable約208 GiB。GPU/jobは変更なし。
- Rate guard通過（5h残88%、週間残95%）。次の軽量pollは03:40 JST。

## 11/15 03:40 JST — primary fold 1進捗

- Host142ローカルでPID`3469081`の継続を確認。fold 1 stage 1はoptimizer step 900/2500、mean loss 2.4091、next batch 16200、checkpoint `primary/fold-1/stage1/step-000900`。`stop_requested=false`。
- Checkpoint記録のGPU0空き8,457 MiB、MemAvailable約208 GiB。GPU/jobは変更なし。
- Rate guard通過（5h残86%、週間残95%）。次の軽量pollは04:10 JST。

## 11/15 04:10 JST — primary fold 1進捗

- Host142ローカルの定刻pollでPID`3469081`の継続を確認。fold 1 stage 1はoptimizer step 1050/2500、mean loss 2.3241、next batch 18900、checkpoint `primary/fold-1/stage1/step-001050`。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB・util 100%。Host `MemAvailable`は約208 GiB。Host142 GPU1には触れていない。
- Rate guard通過（5h残85%、週間残95%）。次の軽量pollは04:40 JST。

## 11/15 04:40 JST — primary fold 1進捗

- Host142ローカルの定刻pollでPID`3469081`の継続を確認。fold 1 stage 1はoptimizer step 1200/2500、mean loss 2.2479、next batch 21600、checkpoint `primary/fold-1/stage1/step-001200`。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB・util 100%。Host `MemAvailable`は約208 GiB。Host142 GPU1には触れていない。
- Rate guard通過（5h残99%、週間残95%）。次の軽量pollは05:10 JST。

## 11/15 05:10 JST — primary fold 1進捗

- Host142ローカルの定刻pollでPID`3469081`の継続を確認。fold 1 stage 1はoptimizer step 1325/2500、mean loss 2.1922、next batch 23850、checkpoint `primary/fold-1/stage1/step-001325`。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB・util 95%。Host `MemAvailable`は約208 GiB。Host142 GPU1には触れていない。
- Rate guard通過（5h残98%、週間残94%）。次の軽量pollは05:40 JST。

## 11/15 05:40 JST — primary fold 1進捗

- Host142ローカルの定刻pollでPID`3469081`の継続を確認。fold 1 stage 1はoptimizer step 1450/2500、mean loss 2.1328、next batch 26100、checkpoint `primary/fold-1/stage1/step-001450`。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB・util 100%。Host `MemAvailable`は約208 GiB。Host142 GPU1には触れていない。
- Rate guard通過（5h残97%、週間残94%）。次の軽量pollは06:10 JST。

## 11/15 06:10 JST — primary fold 1進捗

- Host142ローカルの定刻pollでPID`3469081`の継続を確認。fold 1 stage 1はoptimizer step 1600/2500、mean loss 2.0756、next batch 28800、checkpoint `primary/fold-1/stage1/step-001600`。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB・util 74%。Host `MemAvailable`は約208 GiB。Host142 GPU1には触れていない。
- Rate guard通過（5h残95%、週間残94%）。次の軽量pollは06:40 JST。

## 11/15 06:40 JST — primary fold 1進捗

- Host142ローカルの定刻pollでPID`3469081`の継続を確認。fold 1 stage 1はoptimizer step 1750/2500、mean loss 2.0187、next batch 31500、checkpoint `primary/fold-1/stage1/step-001750`。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB・util 94%。Host `MemAvailable`は約208 GiB。Host142 GPU1には触れていない。
- Rate guard通過（5h残94%、週間残94%）。次の軽量pollは07:10 JST。

## 11/15 07:10 JST — primary fold 1進捗

- Host142ローカルの定刻pollでPID`3469081`の継続を確認。fold 1 stage 1はoptimizer step 1875/2500、mean loss 1.9769、next batch 33750、checkpoint `primary/fold-1/stage1/step-001875`。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB・util 91%。Host `MemAvailable`は約208 GiB。Host142 GPU1には触れていない。
- Rate guard通過（5h残92%、週間残93%）。次の軽量pollは07:40 JST。

## 11/15 07:40 JST — primary fold 1進捗

- Host142ローカルの定刻pollでPID`3469081`の継続を確認。fold 1 stage 1はoptimizer step 2025/2500、mean loss 1.9290、next batch 36450、checkpoint `primary/fold-1/stage1/step-002025`。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB・util 95%。Host `MemAvailable`は約208 GiB。Host142 GPU1には触れていない。
- Rate guard通過（5h残91%、週間残93%）。次の軽量pollは08:10 JST。

## 11/15 08:10 JST — primary fold 1進捗

- Host142ローカルの定刻pollでPID`3469081`の継続を確認。fold 1 stage 1はoptimizer step 2175/2500、mean loss 1.8832、next batch 39150、checkpoint `primary/fold-1/stage1/step-002175`。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB・util 100%。Host `MemAvailable`は約208 GiB。Host142 GPU1には触れていない。
- Rate guard通過（5h残89%、週間残93%）。次の軽量pollは08:40 JST。

## 11/15 08:40 JST — primary fold 1進捗

- Host142ローカルの定刻pollでPID`3469081`の継続を確認。fold 1 stage 1はoptimizer step 2325/2500、mean loss 1.8420、next batch 41850、checkpoint `primary/fold-1/stage1/step-002325`。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB・util 89%。Host `MemAvailable`は約208 GiB。Host142 GPU1には触れていない。
- Rate guard通過（5h残88%、週間残93%）。次の軽量pollは09:10 JST。

## 11/15 09:10 JST — primary fold 1進捗

- Host142ローカルの定刻pollでPID`3469081`の継続を確認。fold 1 stage 1はoptimizer step 2475/2500、mean loss 1.8073、next batch 44550、checkpoint `primary/fold-1/stage1/step-002475`。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB・util 95%。Host `MemAvailable`は約208 GiB。Host142 GPU1には触れていない。
- Rate guard通過（5h残86%、週間残92%）。次の軽量pollは09:40 JST。

## 11/15 09:40 JST — primary fold 1完了、fold 2開始

- Host142ローカルの定刻pollでPID`3469081`の継続を確認。fold 1 stage 2 epoch 2完了（mean loss 0.7554、examples 2,159、peak allocated 6,568 MiB、peak reserved 7,284 MiB）、fold 1 BA`.566667`。
- fold 2のdata準備を開始。official train/validation各2,159/540行、validation 30 prompts、pool prompt filterで2 groups・13 rowsを除外、pool rows 45,000。model shard読込とLoRA層選択まで確認。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB。Host `MemAvailable`は約208 GiB。Host142 GPU1には触れていない。
- Rate guard通過（5h残97%、週間残92%）。次の軽量pollは10:10 JST。

## 11/15 10:40 JST — primary fold 2 stage 1進捗

- Host142ローカルの定刻pollでPID`3469081`の継続を確認。fold 2 stage 1はoptimizer step 125/2500、mean loss 2.8055、next batch 2250、checkpoint `primary/fold-2/stage1/step-000125`。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB・util 93%。Host `MemAvailable`は約207.8 GiB。Host142 GPU1には触れていない。
- Rate guard通過（5h残95%、週間残92%）。次の軽量pollは11:10 JST。

## 11/15 11:10 JST — primary fold 2 stage 1進捗

- Host142ローカルの定刻pollでPID`3469081`の継続を確認。fold 2 stage 1はoptimizer step 275/2500、mean loss 2.8476、next batch 4950、checkpoint `primary/fold-2/stage1/step-000275`。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB・util 100%。Host `MemAvailable`は約207.8 GiB。Host142 GPU1には触れていない。
- Rate guard通過（5h残93%、週間残91%）。次の軽量pollは11:40 JST。

## 11/15 11:40 JST — primary fold 2 stage 1進捗

- Host142ローカルの定刻pollでPID`3469081`の継続を確認。fold 2 stage 1はoptimizer step 425/2500、mean loss 2.7532、next batch 7650、checkpoint `primary/fold-2/stage1/step-000425`。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB・util 100%。Host `MemAvailable`は約207.8 GiB。Host142 GPU1には触れていない。
- Rate guard通過（5h残91%、週間残91%）。次の軽量pollは12:10 JST。

## 11/15 12:10 JST — primary fold 2 stage 1進捗

- Host142ローカルの定刻pollでPID`3469081`の継続を確認。fold 2 stage 1はoptimizer step 575/2500、mean loss 2.6375、next batch 10350、checkpoint `primary/fold-2/stage1/step-000575`。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB・util 100%。Host `MemAvailable`は約207.7 GiB。Host142 GPU1には触れていない。
- Rate guard通過（5h残89%、週間残91%）。次の軽量pollは12:40 JST。

## 11/15 12:40 JST — primary fold 2 stage 1進捗

- Host142ローカルの定刻pollでPID`3469081`の継続を確認。fold 2 stage 1はoptimizer step 725/2500、mean loss 2.5303、next batch 13050、checkpoint `primary/fold-2/stage1/step-000725`。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB・util 94%。Host `MemAvailable`は約207.8 GiB。Host142 GPU1には触れていない。
- Rate guard通過（5h残87%、週間残90%）。次の軽量pollは13:10 JST。

## 11/15 13:10 JST — primary fold 2 stage 1進捗

- Host142ローカルの定刻pollでPID`3469081`の継続を確認。fold 2 stage 1はoptimizer step 850/2500、mean loss 2.4559、next batch 15300、checkpoint `primary/fold-2/stage1/step-000850`。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB・util 100%。Host `MemAvailable`は約207.7 GiB。Host142 GPU1には触れていない。
- Rate guard通過（5h残84%、週間残90%）。次の軽量pollは13:40 JST。

## 11/15 13:40 JST — primary fold 2 stage 1進捗

- Host142ローカルの定刻pollでPID`3469081`の継続を確認。fold 2 stage 1はoptimizer step 1000/2500、mean loss 2.3674、next batch 18000、checkpoint `primary/fold-2/stage1/step-001000`。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB・util 97%。Host `MemAvailable`は約207.8 GiB。Host142 GPU1には触れていない。
- Rate guard通過（5h残83%、週間残90%）。次の軽量pollは14:10 JST。

## 11/15 14:10 JST — primary fold 2 stage 1進捗

- Host142ローカルの定刻pollでPID`3469081`の継続を確認。fold 2 stage 1はoptimizer step 1150/2500、mean loss 2.2909、next batch 20700、checkpoint `primary/fold-2/stage1/step-001150`。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB・util 100%。Host `MemAvailable`は約207.8 GiB。Host142 GPU1には触れていない。
- Rate guard通過（5h残83%、週間残90%）。次の軽量pollは14:40 JST。

## 11/15 14:40 JST — primary fold 2 stage 1進捗

- Host142ローカルの定刻pollでPID`3469081`の継続を確認。fold 2 stage 1はoptimizer step 1275/2500、mean loss 2.2328、next batch 22950、checkpoint `primary/fold-2/stage1/step-001275`。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB・util 94%。Host `MemAvailable`は約207.8 GiB。Host142 GPU1には触れていない。
- Rate guard通過（5h残100%、週間残90%）。次の軽量pollは15:10 JST。

## 11/15 15:10 JST — primary fold 2 stage 1進捗

- Host142ローカルの定刻pollでPID`3469081`の継続を確認。fold 2 stage 1はoptimizer step 1425/2500、mean loss 2.1641、next batch 25650、checkpoint `primary/fold-2/stage1/step-001425`。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB・util 75%。Host `MemAvailable`は約207.8 GiB。Host142 GPU1には触れていない。
- Rate guard通過（5h残99%、週間残90%）。次の軽量pollは15:40 JST。

## 11/15 15:40 JST — primary fold 2 stage 1進捗

- Host142ローカルの定刻pollでPID`3469081`の継続を確認。fold 2 stage 1はoptimizer step 1575/2500、mean loss 2.1048、next batch 28350、checkpoint `primary/fold-2/stage1/step-001575`。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB・util 93%。Host `MemAvailable`は約207.8 GiB。Host142 GPU1には触れていない。
- Rate guard通過（5h残99%、週間残89%）。次の軽量pollは16:10 JST。

## 11/15 16:10 JST — primary fold 2 stage 1進捗

- Host142ローカルの定刻pollでPID`3469081`の継続を確認。fold 2 stage 1はoptimizer step 1725/2500、mean loss 2.0466、next batch 31050、checkpoint `primary/fold-2/stage1/step-001725`。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB・util 100%。Host `MemAvailable`は約207.8 GiB。Host142 GPU1には触れていない。
- Rate guard通過（5h残99%、週間残89%）。次の軽量pollは16:40 JST。

## 11/15 16:40 JST — primary fold 2 stage 1進捗

- Host142ローカルの定刻pollでPID`3469081`の継続を確認。fold 2 stage 1はoptimizer step 1850/2500、mean loss 2.0019、next batch 33300、checkpoint `primary/fold-2/stage1/step-001850`。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB・util 100%。Host `MemAvailable`は約207.8 GiB。Host142 GPU1には触れていない。
- Rate guard通過（5h残98%、週間残89%）。次の軽量pollは17:10 JST。

## 11/15 17:10 JST — primary fold 2 stage 1進捗

- Host142ローカルの定刻pollでPID`3469081`の継続を確認。fold 2 stage 1はoptimizer step 2000/2500、mean loss 1.9522、next batch 36000、checkpoint `primary/fold-2/stage1/step-002000`。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB・util 76%。Host `MemAvailable`は約207.6 GiB。Host142 GPU1には触れていない。
- Rate guard通過（5h残98%、週間残89%）。次の軽量pollは17:44 JSTごろ。

## 11/15 17:44 JST — primary fold 2 stage 1進捗

- Host142ローカルの定刻pollでPID`3469081`の継続を確認。fold 2 stage 1はoptimizer step 2150/2500、mean loss 1.9018、next batch 38700、checkpoint `primary/fold-2/stage1/step-002150`。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB・util 100%。Host `MemAvailable`は約207.7 GiB。Host142 GPU1には触れていない。
- Rate guard通過（5h残97%、週間残89%）。次の軽量pollは18:14 JSTごろ。

## 11/15 18:44 JST — primary fold 2 stage 1進捗

- Host142ローカルの定刻pollでPID`3469081`の継続を確認。fold 2 stage 1はoptimizer step 2425/2500、mean loss 1.8266、next batch 43650、checkpoint `primary/fold-2/stage1/step-002425`。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB・util 100%。Host `MemAvailable`は約207.8 GiB。Host142 GPU1には触れていない。
- Rate guard通過（5h残96%、週間残89%）。次の軽量pollは19:14 JSTごろ。

## 11/15 19:14 JST — primary fold 2 stage 2進捗

- Host142ローカルの定刻pollでPID`3469081`の継続を確認。fold 2はstage 1を終えてstage 2 epoch 1 step 75に進行。mean loss 1.4397、next batch 1350、checkpoint `primary/fold-2/stage2/step-000075`。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB・util 95%。Host `MemAvailable`は約208.0 GiB。Host142 GPU1には触れていない。
- Rate guard通過（5h残95%、週間残89%）。次の軽量pollは19:44 JSTごろ。

## 11/15 19:44 JST — primary fold 2 stage 2進捗

- Host142ローカルの定刻pollでPID`3469081`の継続を確認。fold 2 stage 2はepoch 2 step 225、mean loss 0.7648、next batch 1890、checkpoint `primary/fold-2/stage2/step-000225`。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB・util 100%。Host `MemAvailable`は約207.9 GiB。Host142 GPU1には触れていない。
- Rate guard通過（5h残100%、週間残89%）。次の軽量pollは20:14 JSTごろ。

## 11/15 20:14 JST — primary fold 2完了、fold 3開始

- Host142ローカルの定刻pollでPID`3469081`の継続を確認。fold 2 stage 2 epoch 2完了（mean loss 0.7610、examples 2,159、peak allocated 6,568 MiB、peak reserved 7,284 MiB）。fold 2 BA`.585185`、fold 3 stage 1はstep 100/2500（mean loss 2.8293、next batch 1800）。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB・util 75%。Host `MemAvailable`は約207.6 GiB。Host142 GPU1には触れていない。
- Rate guard通過（5h残99%、週間残89%）。次の軽量pollは20:44 JSTごろ。

## 11/15 20:44 JST — primary fold 3 stage 1進捗

- Host142ローカルの定刻pollでPID`3469081`の継続を確認。fold 3 stage 1はstep 250/2500、mean loss 2.8889、next batch 4500、checkpoint `primary/fold-3/stage1/step-000250`。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB・util 100%。Host `MemAvailable`は約207.7 GiB。Host142 GPU1には触れていない。
- Rate guard通過（5h残98%、週間残89%）。次の軽量pollは21:15 JSTごろ。

## 11/15 21:15 JST — primary fold 3 stage 1進捗

- Host142ローカルの定刻pollでPID`3469081`の継続を確認。fold 3 stage 1はstep 400/2500、mean loss 2.8047、next batch 7200、checkpoint `primary/fold-3/stage1/step-000400`。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB・util 89%。Host `MemAvailable`は約207.6 GiB。Host142 GPU1には触れていない。
- Rate guard通過（5h残98%、週間残88%）。次の軽量pollは21:46 JSTごろ。

## 11/15 21:46 JST — primary fold 3 stage 1進捗

- Host142ローカルの定刻pollでPID`3469081`の継続を確認。fold 3 stage 1はstep 550/2500、mean loss 2.6568、next batch 9900、checkpoint `primary/fold-3/stage1/step-000550`。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB・util 73%。Host `MemAvailable`は約207.7 GiB。Host142 GPU1には触れていない。
- Rate guard通過（5h残97%、週間残88%）。次の軽量pollは22:17 JSTごろ。

## 11/15 22:17 JST — primary fold 3 stage 1進捗

- Host142ローカルの定刻pollでPID`3469081`の継続を確認。fold 3 stage 1はstep 675/2500、mean loss 2.5592、next batch 12150、checkpoint `primary/fold-3/stage1/step-000675`。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB・util 100%。Host `MemAvailable`は約207.7 GiB。Host142 GPU1には触れていない。
- Rate guard通過（5h残96%、週間残88%）。次の軽量pollは22:48 JSTごろ。

## 11/15 22:48 JST — primary fold 3 stage 1進捗

- Host142ローカルの定刻pollでPID`3469081`の継続を確認。fold 3 stage 1はstep 825/2500、mean loss 2.4511、next batch 14850、checkpoint `primary/fold-3/stage1/step-000825`。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB・util 92%。Host `MemAvailable`は約207.7 GiB。Host142 GPU1には触れていない。
- Rate guard通過（5h残95%、週間残88%）。次の軽量pollは23:18 JSTごろ。

## 11/15 23:18 JST — primary fold 3 stage 1進捗

- Host142ローカルの定刻pollでPID`3469081`の継続を確認。fold 3 stage 1はstep 950/2500、mean loss 2.3691、next batch 17100、checkpoint `primary/fold-3/stage1/step-000950`。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB・util 94%。Host `MemAvailable`は約207.6 GiB。Host142 GPU1には触れていない。
- Rate guard通過（5h残95%、週間残88%）。次の軽量pollは23:48 JSTごろ。

## 11/15 23:48 JST — primary fold 3 stage 1進捗

- Host142ローカルの定刻pollでPID`3469081`の継続を確認。fold 3 stage 1はstep 1100/2500、mean loss 2.2826、next batch 19800、checkpoint `primary/fold-3/stage1/step-001100`。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB・util 92%。Host `MemAvailable`は約207.7 GiB。Host142 GPU1には触れていない。
- Rate guard通過（5h残94%、週間残88%）。次の軽量pollは00:19 JSTごろ。

## 11/16 00:21 JST — primary fold 3 stage 1進捗

- Host142ローカルの定刻pollでPID`3469081`の継続を確認。fold 3 stage 1はstep 1250/2500、mean loss 2.2062、next batch 22500、checkpoint `primary/fold-3/stage1/step-001250`。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB・util 100%。Host `MemAvailable`は約207.7 GiB。Host142 GPU1には触れていない。
- Rate guard通過（5h残93%、週間残88%）。次の軽量pollは00:52 JSTごろ。

## 11/16 00:52 JST — primary fold 3 stage 1進捗

- Host142ローカルの定刻pollでPID`3469081`の継続を確認。fold 3 stage 1はstep 1400/2500、mean loss 2.1406、next batch 25200、checkpoint `primary/fold-3/stage1/step-001400`。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB・util 92%。Host `MemAvailable`は約207.7 GiB。Host142 GPU1には触れていない。
- Rate guard通過（5h残99%、週間残88%）。次の軽量pollは01:23 JSTごろ。

## 11/16 01:23 JST — primary fold 3 stage 1進捗

- Host142ローカルの定刻pollでPID`3469081`の継続を確認。fold 3 stage 1はstep 1550/2500、mean loss 2.0804、next batch 27900、checkpoint `primary/fold-3/stage1/step-001550`。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB・util 100%。Host `MemAvailable`は約207.7 GiB。Host142 GPU1には触れていない。
- Rate guard通過（5h残98%、週間残88%）。次の軽量pollは01:54 JSTごろ。

## 11/16 01:54 JST — primary fold 3 stage 1進捗

- Host142ローカルの定刻pollでPID`3469081`の継続を確認。fold 3 stage 1はstep 1700/2500、mean loss 2.0228、next batch 30600、checkpoint `primary/fold-3/stage1/step-001700`。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB・util 100%。Host `MemAvailable`は約207.6 GiB。Host142 GPU1には触れていない。
- Rate guard通過（5h残97%、週間残87%）。次の軽量pollは02:25 JSTごろ。

## 11/16 02:25 JST — primary fold 3 stage 1進捗

- Host142ローカルの定刻pollでPID`3469081`の継続を確認。fold 3 stage 1はstep 1850/2500、mean loss 1.9715、next batch 33300、checkpoint `primary/fold-3/stage1/step-001850`。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB・util 100%。Host `MemAvailable`は約207.6 GiB。Host142 GPU1には触れていない。
- Rate guard通過（5h残97%、週間残87%）。次の軽量pollは02:56 JSTごろ。

## 11/16 02:56 JST — primary fold 3 stage 1進捗

- Host142ローカルの定刻pollでPID`3469081`の継続を確認。fold 3 stage 1はstep 2000/2500、mean loss 1.9253、next batch 36000、checkpoint `primary/fold-3/stage1/step-002000`。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB・util 100%。Host `MemAvailable`は約207.6 GiB。Host142 GPU1には触れていない。
- Rate guard通過（5h残96%、週間残87%）。次の軽量pollは03:27 JSTごろ。

## 11/16 03:27 JST — primary fold 3 stage 1進捗

- Host142ローカルの定刻pollでPID`3469081`の継続を確認。fold 3 stage 1はstep 2150/2500、mean loss 1.8797、next batch 38700、checkpoint `primary/fold-3/stage1/step-002150`。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB・util 100%。Host `MemAvailable`は約207.6 GiB。Host142 GPU1には触れていない。
- Rate guard通過（5h残95%、週間残87%）。次の軽量pollは03:58 JSTごろ。

## 11/16 03:59 JST — primary fold 3 stage 1進捗

- Host142ローカルの定刻pollでPID`3469081`の継続を確認。fold 3 stage 1はstep 2300/2500、mean loss 1.8383、next batch 41400、checkpoint `primary/fold-3/stage1/step-002300`。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB・util 89%。Host `MemAvailable`は約207.6 GiB。Host142 GPU1には触れていない。
- Rate guard通過（5h残93%、週間残87%）。次の軽量pollは04:29 JSTごろ。

## 11/16 04:30 JST — primary fold 3 stage 1進捗

- Host142ローカルの定刻pollでPID`3469081`の継続を確認。fold 3 stage 1はstep 2450/2500、mean loss 1.8015、next batch 44100、checkpoint `primary/fold-3/stage1/step-002450`。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB・util 98%。Host `MemAvailable`は約207.6 GiB。Host142 GPU1には触れていない。
- Rate guard通過（5h残92%、週間残87%）。次の軽量pollは05:00 JSTごろ。

## 11/16 05:00 JST — primary fold 3 stage 2進捗

- Host142ローカルの定刻pollでPID`3469081`の継続を確認。fold 3はstage 1を終えてstage 2 epoch 1 step 100、mean loss 1.4449、next batch 1800、checkpoint `primary/fold-3/stage2/step-000100`。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB・util 95%。Host `MemAvailable`は約207.9 GiB。Host142 GPU1には触れていない。
- Rate guard通過（5h残91%、週間残86%）。次の軽量pollは05:30 JSTごろ。

## 11/16 05:30 JST — primary fold 3完了

- Host142ローカルの定刻pollでPID`3469081`の継続を確認。fold 3 stage 2 epoch 2完了（mean loss 0.7725、examples 2,159、peak allocated 6,568 MiB、peak reserved 7,284 MiB）。fold 3 BA`.596296`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB・util 93%。Host `MemAvailable`は約207.8 GiB。Host142 GPU1には触れていない。
- Rate guard通過（5h残100%、週間残86%）。次の軽量pollは06:01 JSTごろにfold 4を確認。

## 11/16 06:02 JST — primary fold 4 stage 1進捗

- Host142ローカルの定刻pollでPID`3469081`の継続を確認。fold 4 stage 1はstep 125/2500、mean loss 2.8156、next batch 2250、checkpoint `primary/fold-4/stage1/step-000125`。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB・util 100%。Host `MemAvailable`は約207.2 GiB。Host142 GPU1には触れていない。
- Rate guard通過（5h残99%、週間残86%）。次の軽量pollは06:32 JSTごろ。

## 11/16 06:32 JST — primary fold 4 stage 1進捗

- Host142ローカルの定刻pollでPID`3469081`の継続を確認。fold 4 stage 1はstep 275/2500、mean loss 2.8520、next batch 4950、checkpoint `primary/fold-4/stage1/step-000275`。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB・util 100%。Host `MemAvailable`は約207.2 GiB。Host142 GPU1には触れていない。
- Rate guard通過（5h残97%、週間残86%）。次の軽量pollは07:03 JSTごろ。

## 11/16 07:03 JST — primary fold 4 stage 1進捗

- Host142ローカルの定刻pollでPID`3469081`の継続を確認。fold 4 stage 1はstep 425/2500、mean loss 2.7804、next batch 7650、checkpoint `primary/fold-4/stage1/step-000425`。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB・util 91%。Host `MemAvailable`は約207.2 GiB。Host142 GPU1には触れていない。
- Rate guard通過（5h残96%、週間残86%）。次の軽量pollは07:34 JSTごろ。

## 11/16 07:34 JST — primary fold 4 stage 1進捗

- Host142ローカルの定刻pollでPID`3469081`の継続を確認。fold 4 stage 1はstep 550/2500、mean loss 2.6745、next batch 9900、checkpoint `primary/fold-4/stage1/step-000550`。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB・util 83%。Host `MemAvailable`は約207.2 GiB。Host142 GPU1には触れていない。
- Rate guard通過（5h残95%、週間残85%）。次の軽量pollは08:05 JSTごろ。

## 11/16 08:05 JST — primary fold 4 stage 1進捗

- Host142ローカルの定刻pollでPID`3469081`の継続を確認。fold 4 stage 1はstep 675/2500、mean loss 2.5757、next batch 12150、checkpoint `primary/fold-4/stage1/step-000675`。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB・util 83%。Host `MemAvailable`は約207.2 GiB。Host142 GPU1には触れていない。
- Rate guard通過（5h残94%、週間残85%）。次の軽量pollは08:36 JSTごろ。

## 11/16 08:37 JST — primary fold 4 stage 1進捗

- Host142ローカルの定刻pollでPID`3469081`の継続を確認。fold 4 stage 1はstep 825/2500、mean loss 2.4671、next batch 14850、checkpoint `primary/fold-4/stage1/step-000825`。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB・util 100%。Host `MemAvailable`は約207.2 GiB。Host142 GPU1には触れていない。
- Rate guard通過（5h残93%、週間残85%）。次の軽量pollは09:07 JSTごろ。

## 11/16 09:07 JST — primary fold 4 stage 1進捗

- Host142ローカルの定刻pollでPID`3469081`の継続を確認。fold 4 stage 1はstep 975/2500、mean loss 2.3661、next batch 17550、checkpoint `primary/fold-4/stage1/step-000975`。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB・util 100%。Host `MemAvailable`は約207.2 GiB。Host142 GPU1には触れていない。
- Rate guard通過（5h残83%、週間残84%）。次の軽量pollは09:38 JSTごろ。

## 11/16 09:38 JST — primary fold 4 stage 1進捗

- Host142ローカルの定刻pollでPID`3469081`の継続を確認。fold 4 stage 1はstep 1125/2500、mean loss 2.2923、next batch 20250、checkpoint `primary/fold-4/stage1/step-001125`。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB・util 98%。Host `MemAvailable`は約207.1 GiB。Host142 GPU1には触れていない。
- Rate guard通過（5h残81%、週間残83%）。次の軽量pollは10:09 JSTごろ。

## 11/16 10:09 JST — primary fold 4 stage 1進捗

- Host142ローカルの定刻pollでPID`3469081`の継続を確認。fold 4 stage 1はstep 1275/2500、mean loss 2.2217、next batch 22950、checkpoint `primary/fold-4/stage1/step-001275`。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB・util 89%。Host `MemAvailable`は約207.2 GiB。Host142 GPU1には触れていない。
- Rate guard通過（5h残80%、週間残83%）。次の軽量pollは10:40 JSTごろ。

## 11/16 10:40 JST — primary fold 4 stage 1進捗

- Host142ローカルの定刻pollでPID`3469081`の継続を確認。fold 4 stage 1はstep 1425/2500、mean loss 2.1540、next batch 25650、checkpoint `primary/fold-4/stage1/step-001425`。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB・util 93%。Host `MemAvailable`は約207.2 GiB。Host142 GPU1には触れていない。
- Rate guard通過（5h残99%、週間残83%）。次の軽量pollは11:11 JSTごろ。

## 11/16 11:12 JST — primary fold 4 stage 1進捗

- Host142ローカルの定刻pollでPID`3469081`の継続を確認。fold 4 stage 1はstep 1575/2500、mean loss 2.0957、next batch 28350、checkpoint `primary/fold-4/stage1/step-001575`。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB・util 94%。Host `MemAvailable`は約207.1 GiB。Host142 GPU1には触れていない。
- Rate guard通過（5h残98%、週間残83%）。次の軽量pollは11:43 JSTごろ。

## 11/16 11:43 JST — primary fold 4 stage 1進捗

- Host142ローカルの定刻pollでPID`3469081`の継続を確認。fold 4 stage 1はstep 1725/2500、mean loss 2.0412、next batch 31050、checkpoint `primary/fold-4/stage1/step-001725`。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB・util 100%。Host `MemAvailable`は約207.2 GiB。Host142 GPU1には触れていない。
- Rate guard通過（5h残96%、週間残82%）。次の軽量pollは12:14 JSTごろ。

## 11/16 12:13 JST — primary fold 4 stage 1進捗

- Host142ローカルの定刻pollでPID`3469081`の継続を確認。fold 4 stage 1はstep 1850/2500、mean loss 1.9951、next batch 33300、checkpoint `primary/fold-4/stage1/step-001850`。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB・util 82%。Host `MemAvailable`は約207.2 GiB。Host142 GPU1には触れていない。
- Rate guard通過（5h残96%、週間残82%）。次の軽量pollは12:43 JSTごろ。

## 11/16 12:45 JST — primary fold 4 stage 1進捗

- Host142ローカルの定刻pollでPID`3469081`の継続を確認。fold 4 stage 1はstep 2000/2500、mean loss 1.9440、next batch 36000、checkpoint `primary/fold-4/stage1/step-002000`。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB・util 99%。Host `MemAvailable`は約207.2 GiB。Host142 GPU1には触れていない。
- Rate guard通過（5h残95%、週間残82%）。次の軽量pollは13:15 JSTごろ。

## 11/16 13:17 JST — primary fold 4 stage 1進捗

- Host142ローカルの定刻pollでPID`3469081`の継続を確認。fold 4 stage 1はstep 2150/2500、mean loss 1.8992、next batch 38700、checkpoint `primary/fold-4/stage1/step-002150`。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB・util 100%。Host `MemAvailable`は約207.2 GiB。Host142 GPU1には触れていない。
- Rate guard通過（5h残95%、週間残82%）。次の軽量pollは13:48 JSTごろ。

## 11/16 13:53 JST — primary fold 4 stage 1進捗

- Host142ローカルの定刻pollでPID`3469081`の継続を確認。fold 4 stage 1はstep 2325/2500、mean loss 1.8486、next batch 41850、checkpoint `primary/fold-4/stage1/step-002325`。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB・util 94%。Host `MemAvailable`は約207.2 GiB。Host142 GPU1には触れていない。
- Rate guard通過（5h残94%、週間残82%）。次の軽量pollは14:24 JSTごろ。

## 11/16 14:26 JST — primary fold 4 stage 1進捗

- Host142ローカルの定刻pollでPID`3469081`の継続を確認。fold 4 stage 1はstep 2475/2500、mean loss 1.8113、next batch 44550、checkpoint `primary/fold-4/stage1/step-002475`。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB・util 80%。Host `MemAvailable`は約203.1 GiB。Host142 GPU1には触れていない。
- Rate guard通過（5h残90%、週間残81%）。次の軽量pollは14:56 JSTごろ。

## 11/16 14:30 JST — primary fold 4 stage 1完了

- Host142ローカルの定刻pollでPID`3469081`の継続を確認。fold 4 stage 1はstep 2500/2500、mean loss 1.8053でepoch complete。examples 45,000、peak allocated 6,568 MiB、peak reserved 7,284 MiB。`stop_requested=false`。fold 4全体はまだ完了していない。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB・util 86%。Host `MemAvailable`は約203.3 GiB。Host142 GPU1には触れていない。
- Rate guard通過（5h残89%、週間残81%）。次の軽量pollは15:01 JSTごろ。

## 11/16 15:00 JST — primary fold 4 stage 2進捗

- Host142ローカルの定刻pollでPID`3469081`の継続を確認。fold 4 stage 1はstep 2500/2500で完了。stage 2 epoch 1は120 stepsで完了、epoch 2はstep 125、next batch 90、mean loss 0.8262、checkpoint `primary/fold-4/stage2/step-000125`。`stop_requested=false`。
- GPU0 UUID固定、使用7,517 MiB・free 8,458 MiB・util 81%。Host `MemAvailable`は約203.5 GiB。Host142 GPU1には触れていない。
- Rate guard通過（5h残88%、週間残81%）。次の軽量pollは15:30 JSTごろ。

## 11/16 15:30 JST — primary OOF完了・prompt-grouped評価

- 30分pollでHost142 PID`3469081`は終了済み、GPU0は15 MiB使用・15,960 MiB free・util 0%。Host `MemAvailable`は約209.1 GiB。Host142 GPU1には触れていない。
- Fold 4 completed with BA`.5912515964`; primary OOF artifacts exist for folds 0–4 (2,699 rows total). Fold BA: `.574074`, `.566667`, `.585185`, `.596296`, `.591252`.
- Evaluator: `src/gpu_analyze.py --run-dir artifacts/gpu18-olmo2-1124-7b-4bit-openpool-v15 --split primary --baseline-path artifacts/cpu-qwen-prompt-centered-svc-probability-ensemble-v1/primary/oof-all.parquet --bootstrap 5000 --seed 42`. It validated unique ID alignment and exact `(id,prompt_id,true_model,fold)` agreement with the adopted baseline before scoring. Result: 2,699 rows, 150 prompt groups; OLMo BA`.5827268208`, baseline BA`.5864081531`, delta`−.0036813323`; prompt-paired bootstrap 5,000/seed 42, 95% CI`[−.0196272061,+.0118518519]`.
- Per-class recall: 7 classes improved, 10 declined, 1 tied; largest gains were `gemini-3.7-flash` +`.1000`, `gpt-5.6-terra` +`.0667`, and `claude-fable-5` +`.0604`; largest declines were `gemini-3.8-flash` −`.1333`, `gpt-5.5` −`.0600`, and `claude-opus-4-6` −`.0400`. The 18×18 confusion matrix and class recalls are in `artifacts/gpu18-olmo2-1124-7b-4bit-openpool-v15/primary/` (`confusion-matrix.csv`, `class-recall.csv`); full summary is `summary.json`.
- Under the 2026-11-16 policy, this is not treated as a clear CV degradation because the paired interval spans zero. It is not an adopted standalone model; hold it as an add-on for a later Public LB check after the public-Notebook baseline is established. Do not run a confirmation gate before LB solely to satisfy the superseded criterion.
- Rate guard passed (5h remaining 88%, weekly 81%). Host142 GPU0 is released. Next: fresh official/privacy/runtime/quota checks, then private Mistral v14 push and Kaggle runtime measurement. Report before competition submission.

## 2026-11-17 — Add-on artifact readiness

- Read-only inventory of `artifacts/gpu18-olmo2-1124-7b-4bit-openpool-v15/` found stage1 and stage2 adapter weights for all five primary folds (10 `adapter_model.safetensors`, 119,973,712 bytes each), plus fold OOF/logits and training checkpoints; the full directory is about 3.68 GB. No separate full-test prediction or submission artifact is present in this run directory.
- Keep OLMo as a post-baseline add-on candidate under the revised policy. A read-only scan found no OLMo-specific inference/packaging entrypoint under `scripts/` or `src/`; only the training runner `src/gpu_openpool_qlora.py` matched. After the public baseline and Spectral comparison, the existing adapters need private asset packaging plus a new inference path before runtime/LB validation. No GPU was used for this inventory.
