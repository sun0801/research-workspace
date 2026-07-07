---
project: sam2-mamba-motion-tracking
status: active
summary: MOTにおけるstate carry型Mambaのhidden state contaminationを定義・可視化・抑制することで，SAM2/SAMURAI系追跡の動き予測を改善する研究。
created: 2026-07-07
last_updated: 2026-07-07
---

# Mambaによる動き予測を用いたSAM2ベースの物体追跡

## 概要

SAM2 / SAMURAIベースの物体追跡において，カルマンフィルタによる動き予測をMambaを用いた学習ベースの時系列モデルに置き換えることで追跡性能を改善する研究。

研究の中心は，Mamba tracking手法を **sliding window型**（過去数フレームを毎回入力）と **state carry型**（hidden stateをフレーム間で継続更新）に分類し，MOTにおいてstate carry型が抱える **hidden state contamination**（オクルージョン・誤associationによる内部状態の汚染）の問題を定義・可視化・抑制することにある。

SAM2/SAMURAIは研究の実験基盤として使い，Mamba motion priorを外付けする形で統合する。

## 現在の状況

**7/2 MTG後の状況**：state carry型Mambaは100エポックで収束しかけているが、LRスケジューラがほぼ固定になっており過学習の可能性が高い。TrackSSMは入力形式の違いが発覚し実験設定の見直しが必要。public validationの設計（5エポックごとのHOTA評価）が次の実装課題。

研究の問い：

> MOTにおいて，state carry型Mambaのhidden stateをtrackごとに持続的に保持することは有効か？不安定な場合，その原因はhidden state contaminationなのか？それをどう検出・抑制すればよいか？

詳細は [`specs/2026-07-07-state-carry-research-direction.md`](specs/2026-07-07-state-carry-research-direction.md) を参照。

## マイルストーン

### フェーズ1：MIRU / ポスター
- [x] SAM2 / SAMURAIのMOT適用時の問題を把握する（4月完了）
- [x] Mamba tracking手法の調査・sliding window型 / state carry型の整理（5月末完了）
- [x] SAMURAI+Mambaの初期実験（HOTA: SAM2=0.46, SAMURAI=0.54, SAMURAI+Mamba=0.53）
- [x] state carry型Mambaの実装・100エポック学習（7/2時点で収束しかけ）
- [ ] MambaTrack / TrackSSM / State carry型の公平な比較実験
- [ ] 入力スケーリング（bbox vs bbox delta）の根拠整理
- [ ] **validation設計の実装（過学習チェック用 + 5エポックごとのHOTA評価）**
- [ ] **State carryのLRスケジューラ修正（warmup比率・decay形状の見直し）**
- [ ] MIRU原稿の完成

### フェーズ2：修論 / CVPR
- [ ] hidden state contaminationの定義・定量化指標の設計
- [ ] 強制occlusionによる汚染実験（PCA・hidden state norm・cosine similarity可視化）
- [ ] confidence gating / state reset / update skipの効果比較
- [ ] SAM2/SAMURAIへの応用実験と最終評価

## 更新履歴

| 日付 | 内容 |
|------|--------|
| 2026-07-07 | 4ヶ月分の議事録分析をもとにREADME・マイルストーン・概要を更新。meetings/experiments/specsへ研究内容を整理 |
| 2026-07-02 | MTG: TrackSSMの入出力形式の違いを発見、LRスケジューラ問題を確認、val設計の方針を決定、hidden state contamination調査開始 |
| 2026-07-07 | プロジェクト作成 |
