---
date: 2026-11-13
project: kaggle-name-that-llm
type: experiment-log
spec: ../specs/2026-11-13-baseline-spectral-notebook-lb-check-spec.md
---

# 基準blend + Spectral Notebook（v13）のLB確認

## 15:58–16:05 JST — 移植と検証（push前）

- 事前の優先度確認: 他のcomplementarity screen（Qwen8B・Qwen1.7B・4-view SVC・Twin SVC）は全てconfirmationへ進めず棄却済みで、CPUで進める独立確認は無い。Host141の候補は登録済み追加screenで全てreject。よって優先度3（提出の検証）としてSpectral補正付きNotebookを作る。
- 移植: `notebooks/spectral-port/spectral_cell.py`（`meanfield_probabilities`と`normalised_content_groups`を定数ごと変更なしで移植）。`scripts/verify_spectral_port.py`で、保存済みprimary/confirmationのfold確率に通した予測が保存済みSpectral予測と全2,699行ずつ一致（不一致0）。1・2・3・5・18・19・50行の入力で例外なし、約4,000行（train由来、prompt_idなし）で1.3秒。
- Notebook source: `notebooks/name-that-llm-private-baseline-v13-spectral-source/`。v12のセル1（入力発見・モデル読み込み）は同一。変更は、blend確率の後にSpectralセルを加え、予測を`spectral_postprocess(probs, texts)`のargmaxにしたことと、元予測との差分率・クラスタ数の表示のみ。kernel id `suntree0801/name-that-llm-private-baseline-blend-v13-spectral`、private、Internet無効、T4。
- 公式確認（11/13の1回目、push直前を兼ねる）: 公開LB首位 NguyenThanhNhan `.769`（11/12の`.768`から微増）、2位 `.765`。`submission-limits`: `numAllowedNow=5`。Kaggle GPU枠: 残28.28h/30h（次の更新 11/14 00:00 UTC）。v12のruntime見積は2.51h（9h内）で、Spectral段は数秒の増分。
- 注意: OOFのSpectralは約540行（30 prompt）のfold単位で適用した結果。隠しtestは約4,000行で、クラスタの閾値（median正規化）とz-normの母集団が変わる。この差は結果の解釈に含める。

## 16:08 JST — push前の追加確認とpush

- advisor（Fable）相談後の確認: (1) Kaggleから`kernels pull`したv12-test-only sourceと、ローカルv12 sourceの全5セルが一致（差分なし）。v13とv12の差はSpectralセルと予測行の差し替えのみ。(2) fold単位ではなく全2,699行を1母集団として`spectral_postprocess`を適用したCV（実確率・実text）: primary raw `.586408` → pooled Spectral `.661616`（fold-wise `.664952`）、confirmation raw `.567870` → pooled `.650502`。母集団が大きくなっても効果は大きく崩れない（`scripts/check_spectral_pooled.py`、CVでありLB調整ではない）。
- 提出方法はv9と同じ形（`kaggle competitions submit name-that-llm --file submission.parquet --kernel <slug> --version <N> --message ...`）。
- private kernel `suntree0801/name-that-llm-private-baseline-blend-v13-spectral` をpush。次はinteractive runのCOMPLETE待ち→`runtime_estimate.json`・Spectral print・`submission.parquet`を確認してから提出。
