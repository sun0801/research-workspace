---
date: 2026-11-12
project: kaggle-name-that-llm
type: source-audit
status: rejected-primary-screen
tags: [public-notebook, punctuation, prompt-grouped, spectral]
---

# Kirill Tymchishin punctuation prior audit

最終結論: **(b) 試さない** — 登録した固定priorはprimaryで予測を1件も変えず、BA差も0。specのゲートに従いconfirmationもparameter tuningも行わない。結果は[screen log](2026-11-12-spectral-punctuation-prior-screen.md)。

## 出典と閲覧範囲

- [Notebook: LoRA + Trained27 | Evidence for Close Calls](https://www.kaggle.com/code/kirilltym/lora-trained27-evidence-for-close-calls), Kirill Tymchishin、current version 19、2026-11-12取得。公式Kaggle MCP metadataとsession-independent Notebookソースを取得し、コードcellを静的読取。
- `get_notebook_info`のlast-runは11/9だが、search resultは11/12の実行時刻を示す。食い違いを保持する。Notebook markdownではV17 public`.684`、V18`.683`を著者報告し、current punctuation versionはPendingと記載する。いずれも現public leader`.768`超えの証拠ではない。
- Notebookは17 datasets、8 upstream kernels、8 model sourcesを束ねた複合ensemble。本screenでは移植せず、その後処理heuristicのみを取り出す。

## 固定候補

- 公式train回答文からfold-localに4 marker（`" — "`, `"—"`, `“`と`”`の組、`’`）を数える。markerはfold train内20件以上、classは80件以上、class内に該当markerが0件の場合に限り、queryを含むclassのlog scoreから`.70`を一度だけ引く。
- 著者は4つのprompt-held-out check（古いprediction cache）でsourceにより2,159件中4–10件正解増を報告する。split詳細と現bestでの再現は未確認。現best Spectral OOFに同じfold-localルールを適用し、primary paired-CI gateを確認する独立screenを[spec](../specs/2026-11-12-spectral-punctuation-prior-screen-spec.md)に登録。
- 公開Notebookの全ensemble scoreやこのheuristicの独立結果は未検証。外部weights/datasetsは取得・利用していない。Kaggle push/submissionもしていない。


## 最終判定（2026-11-12）

- primary BA差`0.000000`、5,000回prompt-paired bootstrap CI`[0, 0]`、prediction change 0。specの棄却条件により(b)試さないで終了。
