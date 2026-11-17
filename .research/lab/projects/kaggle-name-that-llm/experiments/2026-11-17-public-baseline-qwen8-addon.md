---
date: 2026-11-17
project: kaggle-name-that-llm
type: experiment-log
status: in-progress
---

# Public .620 baseline + Qwen3-8B add-on

## 候補と判断

- (a) 試す。ユーザー承認済みspec（2026-11-16改訂）により、既存学習済み部品の追加は個別spec不要。CVは明確な悪化のみを棄却条件とし、最終判定はPublic LBで行う。
- 使用部品は既存 `gpu02-qwen3-8b-posttrained-openpool-v15` final-fit adapter/head。新規学習なし。Qwen3-8B baseは既存candidate configでApache-2.0、Open Pool v15はCC BY-SA 4.0と記録されている。
- 既存OOF: Qwen3-8B単体BA `.566431` vs 同splitの弱いSVC `.501934`（primary、delta `+.064497`）、confirmation `.554561` vs `.500818`（delta `+.053743`）。固定Qwen+Spectral additionはprimary `+.000746`、confirmation `+.001489`で、独立screenのCI下限は正でなかった。旧screenの採用gateは未通過だが、11/16改訂はbootstrap/confirmationをLB提出の前提にせず、CVでは明確な悪化を棄却すると定めたため、LB確認候補として再判定した。比較対象は新baseline `.620`。

## Notebook候補

- Base source: 2026-11-17に提出済みのNishant Dahal “Two-stage LoRA, part two v2”をprivate copy。Qwen3-8B final-fitを固定log-probability weight `0.25`で追加し、元Notebookの既存weights・postprocessは変更しない。weight tuningなし。
- 推論はoffline。公開Qwen3-8B Model v1は公式[Kaggle model page](https://www.kaggle.com/refs/hf-model/Qwen/Qwen3-8B)記載のApache-2.0、Open Pool v15は[Kaggle dataset metadata](https://www.kaggle.com/datasets/crtproduction/name-that-llm-open-pool)記載のCC BY-SA 4.0。既存private baseline assets（CC BY-SA 4.0）とpinned bitsandbytes 0.50.2 wheelを入力に使用。baseはNF4 4-bit、T4 GPU0にロード。
- Resource gate: load前に空きVRAMがtotal−4096 MiB以上、load後に4,096 MiB以上を要求。公式train textからラベルを読まず長さ層化64行をpilotし、hidden test 4,000行・margin 1.25で予測した総runtimeが8時間未満の場合のみfull inferenceへ進む。9時間超過を避ける内部余裕。
- class orderをmetadataからNotebook `LABELS`へ明示的に並べ替え、finite probability・row sum・submissionのID/label checksを実行する。
- 生成source: `/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/notebooks/name-that-llm-private-two-stage-lora-qwen8-addon-v1/`。Notebook JSON/code cell parse・private/offline/GPU metadata確認済み。

## Pushと状態

- 15:04 JST preflight: official Kaggle competition metadata/Rules/Evaluation/Leaderboardを再確認。Notebook-only、Internet無効、外部data/modelは無料で全参加者に公開される条件、GPU runtime上限9時間、提出上限5件/日・final選択2件、test hidden rerun約4,000行・18 labelsを確認。Leaderboard top `.776`・6,152 teams。
- 同時点の `codex_rate_limit.py --guard 15` は5時間残80%・weekly残71%。ユーザー指定 `kaggle quota` はGPU 29.13h/30h（refresh 2026-11-21 09:00 JST）。既存asset dataset v2はprivate/Ready、wheel dataset v1もprivate/Ready。
- 15:05 JST: private Notebook v1を `kaggle kernels push --path notebooks/name-that-llm-private-two-stage-lora-qwen8-addon-v1 --accelerator NvidiaTeslaT4` でpush。CLIのtitle/metadata ID不一致警告後、Kaggle canonical slug `suntree0801/name-that-llm-private-two-stage-lora-qwen3-8b` version 1として受理。再pushはしていない。
- 15:06 JST: canonical slugでstatus `RUNNING`。remote metadataは `is_private=true`, GPU有効, Internet無効, T4, competition/source/model/dataset inputs一致。CLI pullしたremote Notebookの16 cell sourceはlocal候補と完全一致。runtime完了・hidden scoring・提出は未確認/未実施。
- 同日提出数は15:04直前確認時点で3/5（OLMo ref `58456880`を含む）。このQwen候補は未提出。
- 15:16 JST resource checkpoint: `kaggle quota` GPU残量28.97h/30h、Codex rate guardは5時間残79%・weekly残71%。quota変化の内訳は特定せず、このQwen kernelの消費時間とは断定しない。
- 15:37 JST: Kaggle kernel v1 `COMPLETE`。取得したruntime logではQwen3-8Bロード94秒、64-row pilot 13.7秒、4,000-row予測＋1.25 marginのprojection 1,929秒（約32.2分）、GPU0 peak reserved 7,236 MiB。preview runは約714秒。3-row `submission.parquet`は`id,model`、nullなし、ID重複なし、valid labelのみでartifact gateを通過。public baseline previewと3/3予測が一致（hidden full testへの効果を示すものではない）。
- 15:40 JST: `codex_rate_limit.py --guard 15` pass（5時間枠77%、weekly 70%）。ユーザー指定quota commandはGPU 28.93h/30h、refresh 2026-11-21 09:00 JST。CLI提出一覧は当日3件、Rules/Evaluationを提出直前に再確認し、private/GPU/Internet-offのkernel metadataとCOMPLETE statusを確認。
- 15:43 JST: 最初の提出CLI呼び出しはHTTP 400 (`CreateCodeSubmission`)。Kaggle CLI実装を調べ、`--file`値はローカル絶対パスではなくkernel出力artifact名をAPIへ渡す仕様と確認。提出一覧に新規refがなく、Kaggle側提出は作成されていなかった。source/configは変更せず、file nameを`submission.parquet`に直して再実行。
- 15:43 JST: Qwen3-8B add-on v1をPublic `.620`基準として提出成功、ref `58459599`。提出一覧では`PENDING`・score未確定、当日残り枠1件。

## 次

- Qwen提出ref `58459599`とOLMo ref `58456880`を30分間隔の軽い1コマンドで監視し、状態変化時に結果を回収してこの日付ログとREADMEへ記録する。
- Host142 GPU1の `mistral-confirm` には触れない。
