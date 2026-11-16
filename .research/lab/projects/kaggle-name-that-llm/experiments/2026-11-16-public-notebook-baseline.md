---
date: 2026-11-16
project: kaggle-name-that-llm
type: experiment-log
status: preflight
---

# Public Notebook baseline — Two-stage LoRA part two

## 採用候補

- 出典: [Nishant Dahal, Two-stage LoRA, part two v2](https://www.kaggle.com/code/nishantdahal/two-stage-lora-part-two)。2026-11-16にKaggle MCPでmetadata/sourceを確認。public、GPU有効、Internet無効、T4、version 2、session status `COMPLETE`。
- Public LB`.620`はKaggle search metadataの`best_public_score`で確認。現手元bestはv13の`.560`。Notebook説明の作者報告CV`.642`（prompt-grouped 5-fold）とT4×2約15分は未独立再現。CV値は足切り用の参考にとどめる。
- 構成: 4-view n-gram SVC、Qwen3-14B LoRA、Qwen2.5-14B LoRA、DeBERTa-v3-large。推論のみ。入力は公式competition data、`nishantdahal/ntl-handwriting-blend` v1、Qwen3-14B-Base v1、Qwen2.5-14B v1。
- License: dataset v1はCC BY-SA 4.0で、説明にpoolの由来と各元データのlicenseを記載。Qwen3-14B-Base/Qwen2.5-14BはApache 2.0、dataset内DeBERTa-v3-largeはMIT。Kaggleの公開Notebook codeはApache 2.0。private forkでも帰属情報を保持する。
- 判定: **(a) 試す**。`.701`/`.694`/`.684`候補はQ14 LoRA等のlicense根拠がないため保留。現時点で確認した候補中、licenseとoffline/T4条件を確認でき、手元Public`.560`を超える最高スコア系統として本候補を選ぶ。

## 実行・提出ゲート

- private fork、push、Kaggle実行、competition submissionは未実施。CLI pullしたNotebook sourceは保持し、`/tmp/ntl-public-baseline-pull/kernel-metadata.json`のみ自分のslugに変更して`is_private=true`、`enable_internet=false`に設定済み。上流の内部IDは除去済み。
- 2026-11-16 17:28 JST preflight: Kaggle MCPでcompetition/rules/evaluation/leaderboardを再確認。deadlineはmetadata `2027-01-14 23:59 UTC` とTimeline `2027-01-13 23:59 UTC`で不一致のため早いTimeline日を採用。Public leaderboardは`.774`、team count 6,046、daily submissionsは最大5。
- 認証付きCLIのsubmission一覧は11/16の提出0件（0/5）。v14 Mistral kernelは`KernelWorkerStatus.ERROR`。提出用候補のpublic metadataはPublic LB`.620`、session COMPLETE、offline/T4。Rulesの9時間・Internet無効・`submission.parquet`条件を満たす設計で、runtimeはKaggleで検証する。
- **停止中のgate**: Kaggle GPU weekly quotaの残量は公式CLI/MCPから読めず、Kaggle公式案内はAccount/Notebook UIの表示を参照するよう記載。quota残量の確認後にprivate pushを実行する。現時点でpush・GPU run・提出は行っていない。
- Runtime gate: Kaggleで全処理成功、Internet無効、出力`submission.parquet`の形式・件数・ID順を検証し、9時間以内。失敗した場合はログと原因を残し、構成を変えず報告する。
- Runtime gate通過後にquotaと日次残数を再確認して1件提出し、score・順位・version・時刻・残枠を追記する。public LBの`.620`との差は参考として記録し、以後のLB比較は手元Public`.560`を基準とする。

