---
date: 2026-11-14
project: kaggle-name-that-llm
status: approved
approval_basis: explicit-user-approval-2026-11-14
execution_status: spec-written-implementation-not-started
tags: [spec, experiment, gpu, olmo, qlora, open-pool, prompt-grouped]
---

# OLMo 2 1124 7B 4-bit + Open Pool v15 two-stage LoRA

> **ユーザー承認（2026-11-14）**: 本specの作成後、この範囲で新規runnerの実装とpilotを開始してよい。

## 目的と仮説

既存のOLMo 2 1124 7B + Open Pool v15候補を、16GB GPUで実行できるNF4 QLoRA二段階学習として独立実装する。公開Mistral/OLMo OOFの補完性は候補選定の動機に限り、採用根拠は登録済みprompt-grouped primaryと独立confirmationで得る。基準は採用中のQwen3-8B + Qwen3-1.7B + prompt-centered SVC blend（primary BA `.586`）。テストラベル・テストprompt IDは一切使わない。

## 固定候補とモデル・データ

- Candidate ID: `gpu18-olmo2-1124-7b-4bit-openpool-v15`。既存候補14のconfig・run directoryは変更しない。
- Base model: Kaggle `allenai/olmo-2/transformers/1124-7b`, version 1 (`version_id=202589`), Apache-2.0、7B、32 transformer layers、hidden size 4096。原本shard合計約29.2 GB。tokenizer・重みは取得後ローカル限定で読む。
- External pool: Kaggle `crtproduction/name-that-llm-open-pool`, version 15、CC-BY-SA-4.0。既存OLMo specの登録済み処理を踏襲し、labelあたり最大2,500行をseed 42で抽出する。foldごとに正規化済みtrain本文との完全一致と、validation prompt groupに対応するpool promptのTF-IDF類似度`>=0.40`を除外し、除外行・group数を保存する。publisherの`match_weight`は使わない。
- Quantization: bitsandbytes NF4、double quantization有効、compute dtype BF16。量子化baseはfreezeし、先頭24層の`q_proj,k_proj,v_proj,o_proj,gate_proj,up_proj,down_proj`だけにLoRA（rank 16、alpha 32、dropout 0.05）を付ける。pooling層`[2,4,6,8,12,16,20,24]`のLayerPoolClassifier headは学習する。max length 384、gradient checkpointing、microbatch 1、effective batch 18。
- Stage 1: foldのvalidation promptを除外したOpen Poolのみ、1 epoch、AdamW、LoRA LR`1e-4`、head LR`1e-3`、cosine scheduler、warmup ratio`0.1`。
- Stage 2: そのfoldのofficial train rowsのみ、2 epochs、AdamW、LoRA LR`5e-5`、head LR`5e-4`、cosine scheduler、warmup ratio`0.1`。seed 42。

## 変更範囲

- Research record: 本spec、対応する`experiments/2026-11-14-olmo2-7b-4bit-openpool-lora.md`、READMEの現在状況・更新履歴。
- 新規実装: `/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/src/gpu_openpool_qlora.py`。4-bit base load、LoRA/head構築、二段階学習、pilot、prompt-grouped fold実行、予測出力、再開可能なadapter/head/optimizer/scheduler/RNG checkpointとGPU/RAM preflightを実装する。
- 新規config: `/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/configs/gpu18-olmo2-1124-7b-4bit-openpool-v15.json`。run artifactは`artifacts/gpu18-olmo2-1124-7b-4bit-openpool-v15/`以下（Git対象外）。
- 既存`src/gpu_experiment.py`、`src/gpu_qwen14b_qlora.py`、既存candidate config/artifact、baseline、Mistral runには変更を加えない。依存lockは変更しない。現在の実行環境はbitsandbytes 0.50.2、PEFT 0.17.1、Transformers 4.57.1、Accelerate 1.10.1、PyTorch 2.9.0を確認済み。

## 16GB GPUの資源gate

- 利用許可GPUはHost141 GPU0〜2とHost142 GPU0のみ。Host142 GPU1（`mistral-confirm`）は対象外で、プロセス停止・変更・二重起動・そのGPU上への配置をしない。Host142はローカルコマンドだけで調べ、Host141は`ssh 141`で調べる。Host141は**各利用の直前**に空きを確認する。
- モデル取得・各pilot/full-runの直前にrate guardを実行しexit 0を必須とする。選択GPUについて5秒以上離した2 snapshotで同じhost/device/UUID、対象GPU上に他compute PIDなし、GPU固有lockなしを確認する。UUID指定で可視化・固定し、別GPUへのfallbackを禁止する。
- 起動時にGPU空きVRAMが総容量から4,096 MiB以上差し引いた値以上、`MemAvailable >=16 GiB`、`/mnt/HDD10TB-2`の空き容量`>=45 GiB`を必須とする。モデル原本約29.2 GBに加えてcheckpoint・一時領域を確保する。条件を満たさない場合は待機し、他jobを止めない。
- pilotは384 token、microbatch 1で、モデルload・forward・backward・optimizer stepを実行する。finite loss/logits/gradient、同一UUID、peak allocated/reserved VRAM、step時間、host RAMを記録する。pilot終了後に**実測peak + 4,096 MiB reserve**が対象GPU容量内に収まり、再確認時のfree VRAMもその値以上、RAM・disk・process/lock gateが継続している場合だけfull OOFを開始する。
- pilotが失敗、非有限値、OOM、資源reserve不通過の場合は同じ設定での実験を棄却し、系列長やbatch、quantization、LoRA範囲を変えて再試行しない。変更案は新しいspecと承認対象に戻す。
- 長時間runはtmux等に切り離し、host、GPU UUID、PID、config識別、log、checkpoint、再開位置を記録する。optimizer step 500回ごととepoch終端にatomic checkpointを保存し、再開時は同じstage/epoch/batchから続ける。30分ごとに軽い1コマンドで監視し、変化があった時だけ記録する。安全条件不成立時はこのcandidateだけを安全に停止し、checkpointを保持する。

## Pilot・prompt-grouped評価・採用判定

1. Pilot前にmodel/pool version、config、runner、dataset/filter、fold IDsを固定して記録する。pilotの合格条件は上記resource gateに加えて全出力と学習可能gradientがfiniteであること。
2. Pilot通過後、primaryは保存済み`GroupKFold(prompt_id, n_splits=5)`を変更せずOOFを作る。各foldのpool filterを独立適用し、baselineと`(id,prompt_id,label,fold)`が完全一致することを確認する。raw argmax balanced accuracy、fold別BA、class recall、confusion matrix、5,000回のprompt単位paired bootstrap（seed 42、95% CI）を報告する。baselineは`artifacts/cpu-qwen-prompt-centered-svc-probability-ensemble-v1/primary/oof-all.parquet`。
3. PrimaryのBA差（OLMo単体−baseline）のprompt-paired 95% CI下限が厳密に0超の場合のみ、登録済み`GroupKFold(prompt_id, n_splits=5, shuffle=True, random_state=42)`による独立confirmationを実行する。comparisonは同一ID/foldのconfirmation baseline artifactとし、primaryと同じ指標・5,000 bootstrap・seed 42を使う。confirmation comparatorが揃うまではcandidate結果を解析しない。
4. standalone OLMoを採用候補と呼べるのはprimary・confirmationの両方でBA差CI下限が0超の場合のみ。いずれかが不通過なら不採用。Mistralとのblendや係数・thresholdの調整はこのspecの採用判定に含めない。合格してもKaggle Notebook化・push・提出は自動承認されず、別途runtime・公式条件・提出枠の確認を行う。

## 既存runnerとの違い

- `gpu_experiment.py`はBF16の全重みを読み込む既存generic runnerで、Open Pool二段階処理・prompt-grouped評価の基準になるが、16GB用の量子化loadとk-bit preparationを持たない。
- `gpu_qwen14b_qlora.py`はbitsandbytes QLoRAとcheckpoint機構を持つ一方、Qwen3-14B sequence-classificationのofficial-only一段学習であり、OLMo2 LayerPoolClassifierとfoldごとのOpen Pool stage 1を扱わない。
- 新runnerは両者の機能を別candidate専用ファイルへ統合し、NF4 OLMo2 + Open Pool stage 1 + official fold stage 2を実行する。既存runnerの共通挙動を暗黙に変えず、4-bit baseから再開できるcheckpoint検証を追加する。

## 検証方法と出力

- まず設定schema、静的fold/data整列、model architectureのLoRA target、4-bit checkpoint save/reload、finite pilotを検証する。pilot後にprimary、条件通過時のみconfirmationを実行し、結果はcandidate専用artifact配下へ保存する。
- hashは`sha256sum -c`等の一致確認を使い、Markdownには「一致」、コマンド、必要なら先頭8桁だけを記録する。64桁を手で転記しない。
- 本specはKaggle object、Notebook push、submissionを作らない。Offline Notebookのruntime見積りはcandidate採用後の別判断とする。
