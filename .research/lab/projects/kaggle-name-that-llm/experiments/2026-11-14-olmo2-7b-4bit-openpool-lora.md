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
