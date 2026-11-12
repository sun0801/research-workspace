# README「現在の状況」整理記録 — 2026-11-12

整理時刻: 2026-11-12 17:55 JST

## 整理前の記載（保全）

## 現在の状況

- 現bestは固定Spectral補正のindependent confirmation BA`.653828`（LB未検証）。提出基準blendはprimary BA`.586408`。
- 基準blend v9の提出`58251076`・`58253257`、v11の`58256577`、CPU control v1`58258273`はhidden rerunの一般エラーでscoreなし。path-only control v2`58259844`はPublic`.055`で成功（診断のみ）。
- Kaggleの失敗詳細は一般的なunhandled errorまででtraceなし。原因は未確定だが、入力path・train/template読込の前提を第一候補として検証中。
- baseline v12（test.csvのみ読込、モデル/blend不変）の提出ref `58261829` が15:51確認で採点成功、Public`.541`（primary OOF BA`.586408`との差 約`-.045`）。初のCV-LB対応点。v9/v11の失敗は入力ファイル前提が最有力（traceなしで未確定）。
- 公開sample 3行の推論・Parquet schema/ID順を確認済み。Kaggleの提出枠は1件/5件残り。submission pollは30分間隔。
- Mistral固定1/4追加＋変更なしSpectral補正のprimary BAは`.689791`（既存`.664952`比`+.024840`、5,000 prompt bootstrap CI `[+.013063,+.036412]`）。保持率simulationもmild/moderate各20 seedすべて改善。ただしprimary-only screenで独立confirmation未通過。[screen](experiments/2026-11-12-mistral-spectral-complementarity-screen.md)
- Qwen3-8B固定1/4追加＋Spectralはprimary/confirmationともdeltaが小さくCI下限が0以下のため棄却。primary `+.000746`、confirmation `+.001489`。[screen](experiments/2026-11-12-qwen8b-spectral-complementarity-screen.md)
- Qwen3-1.7B固定1/4追加＋Spectralはprimary・confirmationともBAが低下し、CIも0未満で棄却。deltaは`-.007780`／`-.015183`。[screen](experiments/2026-11-12-qwen17b-spectral-complementarity-screen.md)
- 4-view SVC固定1/4追加＋Spectralは両splitでdeltaが正だがCI下限が0以下のため棄却。deltaは`+.002958`／`+.005556`。[screen](experiments/2026-11-12-4view-svc-spectral-complementarity-screen.md)
- Prompt-centered Twin SVC固定1/4追加＋Spectralも両splitでdeltaは正だがCI下限が0以下で棄却。deltaは`+.006304`／`+.005178`。[screen](experiments/2026-11-12-prompt-centered-twin-spectral-complementarity-screen.md)
- 次は固定Mistral+Spectral compositionの独立confirmation。Mistral confirmation OOFがなく、Host142は厳格host-key確認、queue解消、current-runner pilotの安全ゲート待ち。[spec](specs/2026-11-12-mistral-spectral-complementarity-confirmation-spec.md)
- close-pair補正は固定screenで棄却：2699行中適格pairは1組、予測変更なし、BA差0。公開監査は(b)試さないで完了。[audit](experiments/2026-11-12-kirill-close-pair-audit.md)
- Host142は17:47 JSTもSSH host-key未検証で状態不明。Host141 GPU2は別ユーザー`ogata`の`eval_denoise.py`で5,777 MiB/100%使用中（PID 3160364）。GPU0/1は空き。候補は指定hostを変えず待機。[host poll log](experiments/2026-11-12-host-continuation-poll.md)
- 詳細・再開手順は[baseline benchmark log](experiments/2026-11-12-baseline-benchmark-push.md)。[Spectral confirmation](experiments/2026-11-10-spectral-meanfield-confirmation.md) · [OOF comparison](experiments/2026-11-10-oof-comparator-readiness.md)

## 変更理由

承認済みspec「運用の改訂（2026-11-10、ユーザー承認）」に従い、READMEの「現在の状況」を20行以内の最新要点に圧縮した。詳細な候補結果・旧提出診断・GPU観測は既存の日付付きexperimentsログに残す。
