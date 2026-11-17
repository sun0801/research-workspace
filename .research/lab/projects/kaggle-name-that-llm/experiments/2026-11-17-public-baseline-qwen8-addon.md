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
- 推論はoffline。公開Qwen3-8B Model v1（Apache-2.0）、既存private baseline assets（CC BY-SA 4.0）、pinned bitsandbytes 0.50.2 wheelを入力に使用。baseはNF4 4-bit、T4 GPU0にロード。model/license metadataの詳細取得はMCP `models.get`権限拒否だったが、base/licenseは保存済みcandidate configと既存asset provenanceで確認。
- Resource gate: load前に空きVRAMがtotal−4096 MiB以上、load後に4,096 MiB以上を要求。公式train textからラベルを読まず長さ層化64行をpilotし、hidden test 4,000行・margin 1.25で予測した総runtimeが8時間未満の場合のみfull inferenceへ進む。9時間超過を避ける内部余裕。
- class orderをmetadataからNotebook `LABELS`へ明示的に並べ替え、finite probability・row sum・submissionのID/label checksを実行する。
- 生成source: `/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/notebooks/name-that-llm-private-two-stage-lora-qwen8-addon-v1/`。Notebook JSON/code cell parse・private/offline/GPU metadata確認済み。

## Pushと状態

- 15:04 JST preflight: official Kaggle competition metadata/Rules/Evaluation/Leaderboardを再確認。Notebook-only、Internet無効、外部data/modelは無料で全参加者に公開される条件、GPU runtime上限9時間、提出上限5件/日・final選択2件、test hidden rerun約4,000行・18 labelsを確認。Leaderboard top `.776`・6,152 teams。
- 同時点の `codex_rate_limit.py --guard 15` は5時間残80%・weekly残71%。ユーザー指定 `kaggle quota` はGPU 29.13h/30h（refresh 2026-11-21 09:00 JST）。既存asset dataset v2はprivate/Ready、wheel dataset v1もprivate/Ready。
- 15:05 JST: private Notebook v1を `kaggle kernels push --path notebooks/name-that-llm-private-two-stage-lora-qwen8-addon-v1 --accelerator NvidiaTeslaT4` でpush。CLIのtitle/metadata ID不一致警告後、Kaggle canonical slug `suntree0801/name-that-llm-private-two-stage-lora-qwen3-8b` version 1として受理。再pushはしていない。
- 15:06 JST: canonical slugでstatus `RUNNING`。remote metadataは `is_private=true`, GPU有効, Internet無効, T4, competition/source/model/dataset inputs一致。CLI pullしたremote Notebookの16 cell sourceはlocal候補と完全一致。runtime完了・hidden scoring・提出は未確認/未実施。
- 同日提出数は15:04直前確認時点で3/5（OLMo ref `58456880`を含む）。このQwen候補は未提出。

## 次

- Kernel v1のstatus/outputを30分間隔でpollし、変化があれば既存のこのログへ追記する。`COMPLETE`後はruntime log、GPU reserve、preview `submission.parquet`のschema/rows/null/ID/label、runtime projectionを回収する。失敗ならremote errorを記録し、source構成を変える前に原因を報告する。
- Runtime gate通過後、当日枠・quota・private/offline metadata・official Rules/Evaluationを提出直前に再確認し、Qwen3-8B + Public `.620` baselineを1件提出する。
- OLMo ref `58456880`は直近14:38 JST pollから30分以上の間隔でstatusを回収する。Host142 GPU1の `mistral-confirm` には触れない。
