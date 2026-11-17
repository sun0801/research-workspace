---
date: 2026-11-16
project: kaggle-name-that-llm
type: experiment-log
status: in-progress
---

# Public Notebook baseline — Two-stage LoRA part two

## 採用候補

- 出典: [Nishant Dahal, Two-stage LoRA, part two v2](https://www.kaggle.com/code/nishantdahal/two-stage-lora-part-two)。2026-11-16にKaggle MCPでmetadata/sourceを確認。public、GPU有効、Internet無効、T4、version 2、session status `COMPLETE`。
- Public LB`.620`はKaggle search metadataの`best_public_score`で確認。現手元bestはv13の`.560`。Notebook説明の作者報告CV`.642`（prompt-grouped 5-fold）とT4×2約15分は未独立再現。CV値は足切り用の参考にとどめる。
- 構成: 4-view n-gram SVC、Qwen3-14B LoRA、Qwen2.5-14B LoRA、DeBERTa-v3-large。推論のみ。入力は公式competition data、`nishantdahal/ntl-handwriting-blend` v1、Qwen3-14B-Base v1、Qwen2.5-14B v1。
- License: dataset v1はCC BY-SA 4.0で、説明にpoolの由来と各元データのlicenseを記載。Qwen3-14B-Base/Qwen2.5-14BはApache 2.0、dataset内DeBERTa-v3-largeはMIT。Kaggleの公開Notebook codeはApache 2.0。private forkでも帰属情報を保持する。
- 判定: **(a) 試す**。`.701`/`.694`/`.684`候補はQ14 LoRA等のlicense根拠がないため保留。現時点で確認した候補中、licenseとoffline/T4条件を確認でき、手元Public`.560`を超える最高スコア系統として本候補を選ぶ。

## Source review

- 2026-11-16 17:38 JSTに取得済みv2の全14セルを静的確認。外部通信・token/API credential参照・runtime package installはなく、すべての入力は`/kaggle/input`から読む。処理はSVC fit、2 LoRA推論、DeBERTa推論、全test時のみSinkhornを行い、最終出力`submission.parquet`を生成する。DeBERTa weightsの`/tmp`への複製以外に明示的な追加保存先なし。
- Static reviewでKaggle全testの実行は証明されない。実runtime、成功状態、出力の全件/ID/label整合はprivate fork後のKaggle runで確認する。

## 実行・提出ゲート

- private fork、push、Kaggle実行、competition submissionは未実施。CLI pullしたNotebook sourceは保持し、`/tmp/ntl-public-baseline-pull/kernel-metadata.json`のみ自分のslugに変更して`is_private=true`、`enable_internet=false`に設定済み。上流の内部IDは除去済み。
- 2026-11-16 17:28 JST preflight: Kaggle MCPでcompetition/rules/evaluation/leaderboardを再確認。deadlineはmetadata `2027-01-14 23:59 UTC` とTimeline `2027-01-13 23:59 UTC`で不一致のため早いTimeline日を採用。Public leaderboardは`.774`、team count 6,046、daily submissionsは最大5。
- 認証付きCLIのsubmission一覧は11/16の提出0件（0/5）。v14 Mistral kernelは`KernelWorkerStatus.ERROR`。提出用候補のpublic metadataはPublic LB`.620`、session COMPLETE、offline/T4。Rulesの9時間・Internet無効・`submission.parquet`条件を満たす設計で、runtimeはKaggleで検証する。
- **停止中のgate**: Kaggle GPU weekly quotaの残量は公式CLI/MCPから読めず、Kaggle公式案内はAccount/Notebook UIの表示を参照するよう記載。quota残量の確認後にprivate pushを実行する。現時点でpush・GPU run・提出は行っていない。
- Runtime gate: Kaggleで全処理成功、Internet無効、出力`submission.parquet`の形式・件数・ID順を検証し、9時間以内。失敗した場合はログと原因を残し、構成を変えず報告する。
- Runtime gate通過後にquotaと日次残数を再確認して1件提出し、score・順位・version・時刻・残枠を追記する。public LBの`.620`との差は参考として記録し、以後のLB比較は手元Public`.560`を基準とする。

## 2026-11-17 実行

- 00:36 JST: ユーザー指定の`kaggle quota`でGPU残量29.79h/30h、refresh 2026-11-21 09:00 JSTを確認。`codex_rate_limit.py --guard 15`は5h 100%・weekly 74%。
- 00:37 JST: Kaggle MCPで公式Rules/Evaluation/competition metadataを確認。Notebook-only competition、Internet無効・`submission.parquet`、1日5件・最終選択2件、外部data/modelは無料かつ全参加者に公開される条件。現在のleaderは`.775`だが、本実験の候補基準は承認済み改訂に従い手元Public`.560`。
- 00:40 JST: 認証付きCLIで当日提出0/5を確認。既存の準備済みsource/metadataを変更せず、`is_private=true`、GPU有効、`enable_internet=false`、competition `name-that-llm`、dataset `nishantdahal/ntl-handwriting-blend`、Qwen3-14B-Base/Qwen2.5-14B model version 1を再確認。`kaggle kernels push --path /tmp/ntl-public-baseline-pull --accelerator NvidiaTeslaT4`が成功し、private kernel v1を開始。
- push直後の認証付き`kaggle kernels status`は`KernelWorkerStatus.RUNNING`。T4×2を指定。後のpollで`COMPLETE`を確認。ログの最終出力は約549秒、SVC 403秒、Qwen3-14B LoRA 468秒、Qwen2.5-14B LoRA 514秒、DeBERTa 520秒、全component後の`done in 520s`。tracebackや実行失敗はなく、Transformersは一部の層を`UNEXPECTED`と報告した。モデルの層切り詰めを含む元Notebookのsourceは変更していない。
- CLIで取得した対話runの`submission.parquet`は3行、`id`,`model`の2列、null 0、重複ID 0、予測はEvaluationに列挙された有効label。公式Evaluationは対話runがsmall sampleを使い、競技提出で隠し全test（約4,000行）へ再実行すると説明するため、この3行artifactはsmoke検証として扱い、全件整合・full runtimeは採点runで確認する。
- remote metadataを`kaggle kernels pull ... --metadata`で確認し、kernel id一致、`is_private=true`、GPU有効、Internet無効、competition/dataset/model sourcesがprepared metadataと一致。
- 10:57 JSTの提出直前gate: quota GPU 29.64h/30h、Codex rate guard 5h 100%、当日提出0/5、official competition metadataはNotebook-only・5件/日・team count 6,129。leaderは`.776`だが、候補の比較基準は手元Public best`.560`。`kaggle competitions submit name-that-llm --file submission.parquet --kernel suntree0801/name-that-llm-private-two-stage-lora-baseline --version 1 --message "Private public-notebook baseline: Two-stage LoRA part two v2"`が受理され、ref `58452056`。直後のsubmission listは`PENDING`、Public/Private score空欄、当日1/5件。Code Competition hidden scoring/runtime完了後にPublic LBを記録し、手元best`.560`と比較する。
- 11:13 JST: ref `58452056`の採点待ち中に、後段LB比較用のSpectral v2を実装リポジトリ`name-that-llm/notebooks/name-that-llm-private-two-stage-lora-spectral-v2/`へ準備し、実装commit `54c5e20`。既存v13の凍結Spectral postprocessorを、v1 baselineの元Sinkhorn処理の後に追加した。v1本体・metadata・sourceは変更せず、draftのmetadataもprivate/GPU有効/Internet無効・各input sourceを維持。静的比較ではoriginalから1 cell追加、最終出力cellのみ変更。v2はまだpush・run・提出していない。ref `58452056`の結果を確認してからruntime gateへ進む。

- 11:29 JST: v1の採点待ち中、準備済みSpectral v2をT4×2でprivate push。Kaggle CLIは「kernel title does not resolve to specified id」と警告し、元のbaseline slugではstatus/pullが404。タイトル由来slug `suntree0801/name-that-llm-private-two-stage-lora-spectral`でremote metadataを取得し、private、GPU有効、Internet無効、competition/dataset/model sources一致を確認。push応答はversion 2成功、canonical slugのstatusは`RUNNING`。実行中のため再起動・二重pushはしない。v1 submission ref `58452056`は直近確認（11:27 JST）で`PENDING`、採点結果なし。次の軽いpollは両方とも30分以上の間隔を空ける。
- 11:33 JST: `kaggle quota`実測はGPU残量29.57h/30h、refresh 2026-11-21 09:00 JST（ユーザー提示の直前値29.79hから変化）。Codex rate guardは5h 96%・weekly 73%。新たなpush/submitは行わず、Spectral v2 runtimeとbaseline採点の完了待ち。
- 11:38 JST: canonical slugから`kaggle kernels pull ... --metadata`でremote sourceを取得。ローカルv2とremoteの全7 code cell sourceが一致。remote metadataはcanonical id `suntree0801/name-that-llm-private-two-stage-lora-spectral`、private、GPU有効、Internet無効、competition `name-that-llm`、dataset source 1件。slug警告後も意図したコードが載っていることを独立確認した。
- 11:50 JST: OLMo add-onはまだ実装・pushしない。v1の約549秒は対話用3行smoke runtimeで、submission ref `58452056`の隠し全件runtime・採点は未確定。9時間制限はNotebook全体に適用されるため、基準の全件runtimeとSpectral v2の結果を確認してから、追加推論分を含むruntime gateを判断する。
- 11:57 JST: 既存fold checkpointからinference-only asset packageをローカル作成。`uv run --offline --no-project --with torch==2.9.0 -- python scripts/package_olmo_addon_assets.py`。5 foldのstage-2 adapter・classifier/norm head、sorted 18-label metadataを格納し、optimizer/RNG stateを除外（585 MiB）。headsは`weights_only=True`で全5件をロードし、各shape `(18,32768)`/`(32768,)`を確認。checksum一致: `sha256sum -c SHA256SUMS`（先頭file prefix `13335b34`）。private upload、Notebook推論実装、GPU pilot/runは未実施。基準全件runtimeとSpectral v2比較後にruntime gateを判断する。
- 11:59 JST: authenticated `kaggle competitions submissions name-that-llm --format json --page-size 20`でref `58452056`が`COMPLETE`、Public score`.620`、Private score空欄を確認。旧best v13`.560`を`+.060`上回り、公開Notebookの主張scoreをprivate fork提出で再現。これを以降のPublic比較基準に更新する。CLIにはhidden scoringの正確なruntimeは表示されない。Spectral v2は別の30分monitor intervalを維持し、現時点で再poll・提出はしていない。
- 12:00 JST: Spectral v2 canonical kernel `suntree0801/name-that-llm-private-two-stage-lora-spectral`が`COMPLETE`。log runtime `done in 526s`; preview output `submission.parquet`は3行、2列`id,model`、null 0、重複ID 0、有効labelのみ。frozen Spectral postprocessのpreview changed fractionは0.0で、hidden full testの効果は未確認。private/offline/T4 metadataとremote source/local 7 code cells一致は既確認。
- 12:02 JST pre-submit gate: Kaggle MCPでcompetition/rules/evaluationを確認。Notebook-only、balanced accuracy、最大5件/日・最終選択2件、対話previewとhidden full testの違いを確認。`kaggle quota` GPU残量29.48h/30h（refresh 2026-11-21 09:00 JST）、Codex rate guard 5h 94%・weekly 73%、当日提出はref `58452056`の1件（1/5）。
- 12:03 JST: `kaggle competitions submit name-that-llm --file submission.parquet --kernel suntree0801/name-that-llm-private-two-stage-lora-spectral --version 2 --message 'Private .620 public-notebook baseline + frozen Spectral postprocess'`が受理されref `58453689`。CLIは当日残り3件（計2/5）と報告。採点status/scoreはまだpollしていない。次回pollは30分以上空け、Public`.620`を比較基準とする。
- 12:06 JST: OLMo asset packagerに基準Notebook label-order gateを追加し、local packageを再生成。18ラベルの集合は一致するが順序は異なるため、sorted OLMo列からbaseline Notebook列へのindex permutationをmetadataに保存。round-trip整合確認にpass。checksum一致: `sha256sum -c SHA256SUMS`（先頭file prefix `13335b34`）。Kaggle upload、Notebook実装、GPU pilot/runは未実施。

