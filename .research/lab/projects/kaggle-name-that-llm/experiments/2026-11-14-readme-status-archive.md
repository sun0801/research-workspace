---
date: 2026-11-14
project: kaggle-name-that-llm
type: readme-status-archive
---

# README「現在の状況」アーカイブ（2026-11-14）

担当をClaude CodeからCodexへ戻すにあたり、READMEの「現在の状況」を更新した。更新前の記録を保存する（削除しない）。

- 現bestはSpectral補正のindependent confirmation BA`.653828`（LB未検証）。公開首位は`.768`（11/12公式確認）。採用中の基準blendはprimary BA`.586408`。
- 基準blend v12 ref`58261829`はPublic`.541`、Spectral付きv13 ref`58300703`はPublic`.560`（11/13）。CVの改善`+.078`がLBでは`+.019`で、CV-LB対応は2点。[ログ](experiments/2026-11-13-baseline-spectral-notebook-lb-check.md)
- v9 refs`58251076`・`58253257`はhidden rerunで`COMPLETE`だが、Public/Private scoreなし。Kaggleは一般エラーのみ返し、詳細traceは未取得。
- v9失敗の第一仮説は入力path・`train.csv`/template依存。v12のtest-only入力で成功したため支持されるが、根因確定ではない。[診断ログ](experiments/2026-11-12-baseline-benchmark-push.md)
- Mistral＋Spectral primary BA`.689791`はshape screen（uniform m=2/3）も通過、独立confirmation待ち。Host142 GPU1の実行gateは未通過。[screen](experiments/2026-11-12-mistral-spectral-small-prompt-shape-screen.md) · [確認spec](specs/2026-11-12-mistral-spectral-complementarity-confirmation-spec.md)
- 公式MITの未調整DeBERTa-v3-large primary OOFは全5 fold完了。固定addition＋Spectral BA`.654571`でbaseline`.664952`を下回り、prompt bootstrap CIも負のため候補棄却。独立確認・提出には進めない。[spec](specs/2026-11-12-deberta-v3-large-official-prompt-grouped-spec.md) · [実験ログ](experiments/2026-11-12-deberta-v3-large-pilot-primary.md)
- Spectral mean-field単体はprimaryのm=2/3 shapeで不安定だが、固定Mistral追加後はuniform shape flagを通過。[screen](experiments/2026-11-12-spectral-meanfield-small-prompt-shape-screen.md) · [Mistral＋Spectral](experiments/2026-11-12-mistral-spectral-small-prompt-shape-screen.md)
- 次はHost142の厳格host-key確認・queue解消・current-runner pilotを満たしてからconfirmationを再開する。host/deviceの割当ては変えない。
- 21:30 JST: DeBERTa primaryはexit 0。登録済みCPU evaluatorで全2,699行を検証し、固定addition＋Spectralのprimary gate不通過を確認。Host141 GPU1/2は別ユーザーjobが稼働中で未変更。[候補ログ](experiments/2026-11-12-deberta-v3-large-pilot-primary.md)
- 次はHost142固定のMistral＋Spectral独立確認。host-key確認に失敗中のため接続復旧までは状態を推測せず、再試行は次の予定pollのみ。Kaggle提出待ちはなし。
- 現在の候補screen結果・公開監査の結論は各日付ログを参照。詳細な履歴は[README整理アーカイブ](experiments/2026-11-12-readme-status-archive.md)。
