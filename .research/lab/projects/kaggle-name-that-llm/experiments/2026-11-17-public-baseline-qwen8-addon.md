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

## Combined Qwen3-8B + OLMo2-7B add-on (2026-11-17)

- OOF complementarity screen (fixed 0.25/0.25 weights; same 2,699 rows, 150 prompt groups, 5 folds, label order checked): Qwen `.566431`, OLMo `.582727`, pair `.596428` (`+.013701` vs stronger single). This is pair-only evidence, not a CV estimate for the public `.620` Notebook; use Public LB for the decision.
- OLMo-only public ref `58456880` completed at `.626`, `+.006` over `.620`, exceeding the `.005` noise threshold; adopted `.626` as current baseline. Qwen-only ref `58459599` completed at `.623` at 16:46 JST, `+.003` over `.620` (below the `.005` noise threshold and below current `.626`), so it is not adopted.
- Candidate merges the private `.620` baseline with the existing Qwen3-8B and OLMo2-7B full-fit inference packages at fixed log-prob weights `.25` each. No retraining or weight tuning. Inputs include the baseline/blend assets, pinned bitsandbytes wheel, Qwen3-8B, and OLMo2-7B; Notebook is private, GPU-enabled, Internet-disabled, T4.
- Pre-push official gate (16:20 JST): Notebook-only competition, Internet-disabled execution, up to 5 submissions/day, 9-hour runtime limit, Parquet output / 18 valid labels; public top `.776`, 6,159 teams. CLI showed four submissions for the day, leaving one slot. At 16:19 JST the rate guard passed (5-hour 98%, weekly 70%) and user-specified quota command showed GPU 28.93/30h (refresh 2026-11-21 09:00 JST).
- Static source checks passed: all 18 cell IDs unique, code cells parse, fixed weights/votes present, private/GPU/offline metadata and OLMo asset/model inputs attached, test discovery and `submission.parquet` output path present.
- Push first returned HTTP 400 because Kaggle limits Notebook titles to 50 characters. No model/configuration change; shortened title and matching slug, then version 1 was accepted as `suntree0801/name-that-llm-qwen8-olmo7-addon`. Implementation repo commits: `35575ae`, `97b539d`, `30c5c2d`.
- v1 runtime `COMPLETE` at 16:54 JST. Preview took 805s; Qwen 64-row pilot took 13.9s, 4k+1.25 projection was 1,877.9s, Qwen GPU0 peak reserved 7,236 MiB; OLMo five 3-row fold pilots took 0.8–0.9s each, peak reserved 6,450 MiB. `submission.parquet` passed preview artifact checks (3 rows, `id,model`, no nulls/duplicate IDs, all valid labels).
- Source review found v1 called OLMo with default `projection_rows=n_rows`, so its runtime gate saw only the interactive 3 rows. v1 was not submitted. v2 now sets `projection_rows=4000` and passes `max(time.time()-T0, _q8_projected)` so OLMo's 4k forecast adds to the already projected baseline+Qwen time. Model, weights, and assets are unchanged. All notebook code cells parse; 18 cell IDs are unique. Implementation commit `bb85c71`.
- Pre-submit gate at 16:55 JST: current official page confirms Code Requirements (Notebook-only, Internet off, CPU/GPU ≤9h, output `submission.parquet`), Evaluation (18 labels, hidden rerun ~4,000 rows), 5 submissions/day and up to 2 final entries. Official metadata deadline is 2027-01-14 23:59 UTC, while Timeline page says 2027-01-13; preserve as an official-page discrepancy. Public top `.776`, 6,161 teams. Rate guard passed (5h 95%, weekly 69%); quota command reports 28.71/30 GPU hours (refresh 2026-11-21 09:00 JST). CLI shows 4 submissions today, so 1 slot remains.
- Version 2 pushed privately and initial status was `RUNNING` at 16:57 JST. It reached `COMPLETE` at 17:27 JST; interactive runtime 746s. Qwen 4k+1.25 projected total was 2,030.1s (34m), GPU0 peak reserved 7,236 MiB. OLMo 4k projection including the Qwen cumulative projection was 11,341.6s (3h 9m), below the internal 28,800s/8h gate; OLMo fold pilot peak reserved 6,450 MiB. Preview artifact passed schema/null/ID/label checks and exactly matched v1's three preview predictions.
- Final pre-submit check at 17:28 JST: rate guard pass (5h 90%, weekly 69%), user quota command 28.49/30 GPU hours (refresh 2026-11-21 09:00 JST), official Code Requirements confirm Notebook-only / Internet off / ≤9h / `submission.parquet`; Evaluation confirms hidden rerun ~4,000 rows and 18 labels; Rules confirm 5 submissions/day; Leaderboard top `.776`, 6,164 teams. Official competition metadata gives deadline 2027-01-14 23:59 UTC while Timeline says Jan 13. CLI showed four earlier daily submissions, one slot available.
- Version 2 submitted at 17:29 JST as ref `58462545` using kernel `suntree0801/name-that-llm-qwen8-olmo7-addon`, version 2. Initial submission status is `PENDING`; daily limit now 5/5. Public score is not yet known. Implementation commit: `bb85c71`.

## 次

- Qwen ref `58459599`はPublic`.623`で完了、OLMo ref `58456880`はPublic`.626`で完了。提出ref `58462545`を30分間隔の軽い1コマンドで監視し、Public LB scoreを回収して現best`.626`と比較・記録する。
- Host142 GPU1の `mistral-confirm` には触れない。
