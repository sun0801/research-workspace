---
date: 2026-11-09
project: kaggle-name-that-llm
type: source-review
status: reviewed
tags: [public-notebook, ensemble, ablation, version-provenance]
---

# 公開ensembleのアブレーション主張とversion provenance

## 出典と取得範囲

- URL: https://www.kaggle.com/competitions/name-that-llm/discussion/756088
- 著者: HALX2158 (`mizuno0522`)
- 取得日時: 2026-11-09 04:45 JST、Kaggle MCPのtopic本文を取得
- 読んだ範囲: Discussion本文。コードと提出versionは独立確認していない。
- 自分たちの再現: 未実施

## 確認した内容

投稿者は公開LB `.638` のBase Aと`.659`のBase Bでensemble部品の除去ablationを比較したと報告する。Qwen3-14B memberを除いた差はそれぞれ`−.020`と`−.010`、centred twinsは`−.017`と`−.006`、補完的frozen stackは`−.008`と`−.004`。一方、n-gram SVC除去は`−.011`と`−.001`、ATLAS除去は`−.009`と`+.001`だった。Base BのQwen/twins比較はGaussian head等も同時に切っており、完全な単一要因比較ではない。

同投稿は、ModernBERT-largeを別Baseへ追加した場合は重み1.5で`.638`、0.5で`.641`、0.3で`.642`となり、元の`.642`を超えなかったと報告する。いずれも投稿者が申告したPublic LBで、CV値や独立再現ではない。

version上の注意として、投稿者は元の`.664` Notebookの採点version 2ではSinkhorn 0.30・typography 1.5だったが、pullした最新ソースは0.60・1.2で、後者を使うと`.659`、採点時の設定では`.663`だったと述べる。これは投稿者の報告であり、当該kernel version/sourceを今回独立照合していない。

## 解釈・限界・反証

- componentの寄与はensemble baseと同時に変更した設定に依存する。別baseのablation deltaをそのまま移植しない。
- 追加時の変化と除去時の変化は対称とは限らない。単独OOFが弱い候補をblendへ追加すれば改善する、とは推論できない。
- Public LBだけの報告で、prompt-grouped OOF、seed、private LBでの転移、Notebook実行出力は未確認。公開値を採用根拠にしない。
- 公開Notebookを参照する場合は取得日時だけでなく、採点済みkernel versionと設定を個別に固定・照合する。

## 今回への候補と未決事項

現在の候補順位や稼働中の実験キューは変更しない。既存specのprompt-grouped primary/confirmation gateを維持し、将来blend構成を比べる場合も同一OOF・同一splitで差分を評価する。この投稿のスコア再現・Notebook取得・Kaggle提出は行っていない。

## 関連ファイル

- [プロジェクトREADME](../README.md)
