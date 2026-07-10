---
project: research-workspace-governance
status: active
summary: brainstormから研究実装へ進む前に、承認済みspecを必須とするImplementation Gateを導入し、想定シナリオで確認済み。
created: 2026-07-10
last_updated: 2026-07-10
---

# Research Workspace 運用ガバナンス

## 概要

Research Workspaceにおいて、brainstormの内容やMTG後TODOから、spec・実施手順・明示承認を経ずに外部実装リポジトリの編集へ進むことを防ぐ運用を設計する。

## 現在の状況

Plan mode未使用は実装直行を促す一因だが、主な課題はmodeに依存しないImplementation Gateがないことだと整理した。第1段階として、`brainstorm` スキルとルートAGENTS.mdに、承認済みspec・変更範囲・検証方法・実装開始承認を確認するゲートを導入した。

## マイルストーン

- [x] 実装直行の原因候補と対策を整理する
- [x] 第1段階のImplementation Gateをspec化する
- [x] brainstormスキルとルートAGENTS.mdへImplementation Gateを導入する
- [x] 想定シナリオでゲートの動作を確認する
- [ ] meeting-minutesとTODOのspec参照導線を第2段階として検討する

## 更新履歴

| 日付 | 内容 |
|---|---|
| 2026-07-10 | プロジェクト作成。Implementation Gate導入の第1段階specを追加。 |
| 2026-07-10 | brainstormスキルとルートAGENTS.mdへImplementation Gateを導入。 |
| 2026-07-10 | 4つの想定シナリオで開始条件・例外・mode非依存性を静的確認。 |
