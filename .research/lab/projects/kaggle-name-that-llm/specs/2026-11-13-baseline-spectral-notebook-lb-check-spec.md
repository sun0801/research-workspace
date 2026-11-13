---
date: 2026-11-13
project: kaggle-name-that-llm
status: approved-under-active-goal
approval_basis: 2026-11-06-gpu-autonomous-first-place-spec（運用の改訂 2026-11-10: 提出の検証）・ユーザー追加指示 2026-11-13
execution_status: not-started
tags: [spec, submission, notebook, spectral, lb-check]
---

# 基準blend + Spectral のNotebook提出によるCV→LB確認

## 目的

現在の確認済みbestは、基準blendへ凍結Spectral mean-field補正を適用したもの（primary BA `.664952`、独立confirmation BA `.653828`）だが、Public LBは未検証。基準blend単体のv12はPublic `.541`（CV `.586`）で、CV→LBの対応は1点しかない。Spectralはtest集合全体の構造（内容近似のクラスタ）に依存する後処理なので、手元CVが隠しtestへ転移するかは提出でしか分からない。本specは、Spectral補正を載せたNotebookを1回提出し、2点目のCV→LB対応と、test依存後処理の隠しtest上の挙動を得る。LBに合わせた調整には使わない。

## 固定内容

- 基盤はv12 `name-that-llm-private-baseline-v12-test-only-source` をそのまま使う。入力の発見・読み込み（`test.csv`のみ。`train.csv`・sample templateは読まない）、モデル、private asset Dataset、推論処理は変えない。変えるのは、基準blend確率の後ろに凍結Spectral補正を加える段だけ。
- Spectral補正は `scripts/evaluate_spectral_cluster_meanfield.py` の `meanfield_probabilities` と、そこで使う `normalised_content_groups`（定義元はscriptのimportを辿って確認）を、定数（GAMMA 0.55, TEMP_CLUSTER 0.65, CLUSTER_ITERS 4, TEMP_FINAL 0.72）を含めて変更なしで移植する。重み・閾値・クラスタ設定を調整しない。
- 移植の同一性: 保存済みprimary fold確率（`artifacts/cpu-qwen-prompt-centered-svc-probability-ensemble-v1/primary/fold-*/probabilities.npz`）をNotebook側の移植コードに通した予測が、`artifacts/cpu-spectral-cluster-meanfield-v1` の保存済みSpectral予測と全行一致することを、提出前にローカルで確認する。一致しなければ提出しない。
- 小さい入力で壊れないこと: 公開testは3行。クラスタ数が行数に近い・1行のクラスタ・`len(scores) < n_classes`の各経路でエラーにならないことを、3行と少数行の入力で確認する。クラスタ化は行数に依存するので、約4,000行の入力でも実行時間と出力を確認する（train由来の疑似testでよい。prompt_idは使わない）。
- 出力は `submission.parquet`、列・行数・ID一致は既存の検査をそのまま適用する。

## ゲートと手順

1. ローカルで移植同一性・小入力・約4,000行の確認を終える。
2. 実行時間は、v12の測定値に疑似test上のSpectral段の増分を加えて9時間以内かを見積もる。大きく変わらない限り、Spectral段はCPU数秒〜数分の見込み。
3. push直前に、公式情報（Rules・Timeline・Code Requirements・公開LB・チーム数）、`submission-limits`による当日提出枠、privateであること、Kaggle側GPU週間枠を確認し、記録する（当日の公式確認がまだなら、これを当日分とする）。
4. 新しいNotebook sourceを `notebooks/` に作り（v12は変更しない）、private・Internet無効でpushする。Kaggle上で全処理を通して実行し、実行時間・出力形式を確認してから提出する。提出前にadvisor（Fable）へ相談する。
5. 提出は1回。結果（手元BA、Public score、Notebook version、提出時刻、残り枠）を実験ログとREADMEに記録する。hidden rerunで失敗した場合は、v12との差がSpectral段だけである点を使って原因を切り分け、記録する（構成を変えて再提出する前に報告する）。

## 結果の読み方（事前登録）

- Public `.541`より明確に高い: Spectral系が隠しtestへ転移する第一の証拠。ただし1提出・公開testの一部のため、確実な改善とは言わない。次候補（Mistral追加など）の土台とする。
- Public `.541`と同程度または低い: この後処理が隠しtestで効かない、または手元のクラスタ構造がtestと違う可能性。Spectralを含む候補の優先度を下げるが、原因を断定しない。
- どの結果でもspecや閾値をLBに合わせて変えない。Spectral単体はprimaryのm=2/3 shapeで不安定という既知の注意（[screen](../experiments/2026-11-12-spectral-meanfield-small-prompt-shape-screen.md)）を前提に、結果の解釈に含める。

## 範囲外

- Mistralなど新しい成分の追加（Mistral confirmation完了後の別判断）。
- v9の原因の再診断（新しい証拠がない限り行わない）。
- 最終2件の選定（本提出はそれに自動では含めない）。
