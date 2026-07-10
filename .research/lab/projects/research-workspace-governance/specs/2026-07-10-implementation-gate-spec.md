---
date: 2026-07-10
project: research-workspace-governance
source: brainstorm
status: approved
tags: [spec, governance, brainstorm, implementation-gate]
---

# Research Workspace Implementation Gate Spec

## 目的

研究相談・MTG後TODOから派生した実装について、承認済みspecと具体的な実施手順を確認せずに外部実装リポジトリを編集することを防ぐ。Plan modeの利用可否にかかわらず、同じ計画・承認プロセスを適用する。

## 背景

- 2026-07-09 MTGで、brainstormがspecやplanを十分に作らないまま実装へ進みやすい点が運用課題として挙がった。
- 現行brainstormスキルには、spec保存の条件を定めるSpec Gateはあるが、コード編集の開始条件を定めるImplementation Gateはない。
- skill内でPlan modeに言及しても、skill自身がセッションのmode切替を保証するわけではない。
- 既存の `plans/` はResearch Workspaceの標準構造に含まれていないため、第1段階では新設・標準化しない。

## 検証したい問い

modeに依存しないImplementation Gateを`brainstorm`スキルとルートAGENTS.mdへ導入すると、研究文脈から発生した実装が、承認済みspecと検証方針を経てから開始されるようになるか。

## 仮説

実装開始前に、承認済みspec、実装対象、検証方法を必須確認事項として明示すれば、Default modeであっても実装直行を抑止できる。Plan modeは計画品質を補助するが、ゲートそのものはmodeに依存させない方が安定する。

## 実験・実装内容

### 対象

- `.agents/skills/brainstorm/SKILL.md`
- `AGENTS.md`

### 対象外（第2段階）

- `meeting-minutes` のNEXT ACTIONS分類とspec参照導線
- TODO形式への`spec`フィールド追加
- `plans/` ディレクトリの新設・標準化
- 既存の研究実装リポジトリのコード変更

### 1. 状態遷移を定義する

```text
brainstorm（探索）
  -> 計画化（Plan modeまたはPlan mode相当）
  -> spec draft
  -> ユーザー明示承認
  -> implementation-ready
  -> 実装・検証
```

`plans/` は作成せず、実装順・対象ファイル・検証方法はspecの`## 実施手順`へ記載する。

### 2. brainstormスキルへImplementation Gateを追加する

以下を明文化する。

- brainstorm中および計画化中は、外部実装リポジトリのファイルを編集しない。
- Plan modeが利用可能なら計画化に使う。利用できない場合も、Plan mode相当として計画提示・不足確認・Spec Gateまでを行い、コード編集は開始しない。
- 実装依頼を受けた際、以下がそろわなければImplementation Gateで停止し、spec化または不足確認へ戻る。
  - 承認済みspecのパス
  - 実装対象と変更範囲
  - 検証方法
  - ユーザーの実装開始承認
- ユーザーがspec省略を明示する場合は、例外として扱う理由と影響を確認してから進める。

### 3. ルートAGENTS.mdへ共通ルールを追加する

研究由来の外部実装変更・実験設計変更について、承認済みspecを確認してから開始する永続ルールを追加する。

対象外として、以下を明示する。

- 読み取り専用の調査・診断
- ダッシュボード、TODO、議事録、brainstormメモなどの研究ワークスペース管理
- 文書表現のみの軽微な修正

## 使用データ・モデル

外部データセットや学習モデルは使用しない。対象はResearch WorkspaceのMarkdown指示・スキル定義・想定会話シナリオである。

## 比較対象・ベースライン

### 現行フロー

- brainstormにはSpec Gateがある。
- spec保存の条件はあるが、実装開始の条件はない。
- Plan modeの利用はskill内の記述に留まり、切替やコード編集停止を保証しない。

### 改善後フロー

- Spec Gateに加えてImplementation Gateを適用する。
- modeにかかわらず、実装前にspec・対象・検証方法・承認を確認する。

## 評価指標

- 未承認specの状態で、外部実装リポジトリへの編集が始まらないこと。
- 実装開始時に、対象spec、変更範囲、検証方法を短く提示できること。
- Plan modeが利用できない場合でも、計画化とゲートが機能すること。
- 読み取り専用の調査やResearch Workspace管理が不要に停止しないこと。

## 成功/失敗の判断基準

### 成功

- 「brainstormした内容を実装して」と依頼した場合、承認済みspecがなければコード編集を開始せず、spec化または不足確認へ進む。
- 承認済みspec・変更範囲・検証方法がある場合、実装開始条件を明示してから作業へ進む。
- Default modeとPlan mode相当の双方で、同じ実装開始条件が適用される。
- 第1段階で`plans/`を標準構造へ追加しない。

### 失敗

- specなし、または未承認のまま外部実装リポジトリを編集する。
- Plan modeが使えないだけで、計画化または実装開始判定ができなくなる。
- ダッシュボードやメモ更新など非実装作業まで過剰に停止する。

## 実施手順

1. `brainstorm/SKILL.md` のPhase 9〜11の前後に、Implementation Gateとmode非依存の行動を追加する。
2. 実装開始条件・例外・対象外を明示する。
3. ルート`AGENTS.md`へ、研究由来の外部実装・実験設計変更に対する共通ルールを追加する。
4. 次の想定シナリオを会話レベルで確認する。
   - specなしで実装を依頼する
   - 承認済みspecを指定して実装を依頼する
   - Plan modeが利用できない状態で計画化を依頼する
   - ダッシュボードやTODO更新を依頼する
5. 想定どおりなら、READMEのマイルストーンを更新する。第2段階のmeeting-minutes/TODO連携は別specで扱う。

## 期待される結果

- brainstormが探索・計画化・実装を明確に分離する。
- ユーザーは、実装開始前にどのspecに基づき、何を変更し、どう検証するか確認できる。
- Plan modeは有用な補助機構として使いつつ、利用可否が運用の単一障害点にならない。

## リスク・懸念

- 小さな変更まで厳格に扱うと、日常作業の摩擦が増える。
- ユーザーの明示的なspec省略依頼を例外化する条件が曖昧だと、ゲートが形骸化する。
- 外部実装リポジトリでの実作業時に、当該リポジトリのAGENTS.mdやローカル規約と二重管理になる可能性がある。

## 未決事項

- 第2段階でTODOに`spec`参照を追加するか。
- `plans/` を将来的に標準構造へ追加する必要があるか。
- spec省略例外を、どの粒度・記録方法で認めるか。

## 関連brainstorm

- [.research/secretary/notes/brainstorm/2026-07-10-plan-mode-spec-implementation-gate.md](../../../../secretary/notes/brainstorm/2026-07-10-plan-mode-spec-implementation-gate.md)
