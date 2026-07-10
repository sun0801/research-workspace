---
date: 2026-07-10
project: sam2-mamba-motion-tracking
source_todo: null
topic: plan-mode-spec-implementation-gate
status: exploratory
tags: [brainstorm, research-workflow, codex, plan-mode, spec]
---

# Plan mode・Spec・実装開始ゲートの関係

## 読み込んだ文脈

- `sam2-mamba-motion-tracking` のREADME
- 2026-07-09 MTG議事録
- 2026-07-07 validation brainstorm
- 2026-07-07 validation implementation spec
- 2026-07-07 validation implementation plan
- 2026-07-07、07-09、07-10のTODO
- 現行 `brainstorm` スキル
- CodexのskillsとAGENTS.mdに関する公式ドキュメント

## 相談の出発点

brainstormスキルを使った際、specやplanを作らないまま実装へ進みやすい。2026-07-09の教授とのMTGでは、Plan modeで実行していないことが原因ではないかという仮説が出た。

## 対象TODO

なし。Research Workspaceの運用設計に関する診断。

## 問い

Plan modeを使っていなかったことは、specやplanを経由せず実装へ進んだ主因といえるか。

## アイデア候補

1. brainstorm開始時点からPlan modeを必須にする。
2. modeに依存せず、brainstormスキルに実装禁止とImplementation Gateを追加する。
3. AGENTS.mdへ、承認済みspecがない研究実装を開始しないという永続ルールを追加する。
4. 実装TODOには対応するspecへの参照を必須にする。
5. meeting-minutesで抽出したNEXT ACTIONSを、調査・計画・実装に分類する。

## 仮説候補

### H1: Plan mode未使用が主因

Default modeではファイル編集や実装へ進めるため、Plan mode未使用は実装直行を起こしやすくする。

### H2: 実装開始ゲートの欠如が主因

現行brainstormスキルのSpec Gateは「specを保存してよい条件」を定義しているが、「コードを編集してよい条件」を定義していない。このため、modeに関係なく実装開始を止める規則が弱い。

### H3: mode切替をskillが保証できないことが主因

スキル内にはPlan modeで計画化すると書かれているが、スキル自体がセッションのmode切替を保証するわけではない。Plan modeへの言及だけでは強制力がない。

### H4: TODO導線がspecを迂回させる

MTG後のNEXT ACTIONSが通常TODOとして保存されると、対応specを参照せず、そのまま実装依頼として解釈できる。

## 実験・実装案

### 推奨する最小変更

1. brainstormスキルに「壁打ち中は実装リポジトリを編集しない」を追加する。
2. Implementation Gateを追加し、承認済みspecと実装計画が揃うまでコード編集を禁止する。
3. Plan modeが利用可能ならspec計画時に切替を要求し、利用できなければPlan mode相当の計画化を行うと明記する。
4. 実装開始前に、対象spec、承認状態、実装対象、検証方法を短く提示する。

### より強い変更

1. ルートAGENTS.mdへ研究実装の共通ゲートを追加する。
2. TODO形式へ `種別: 実装` と `spec: <path>` を追加する。
3. meeting-minutesが実装TODOを抽出した際、対応specがなければ「spec化候補」として提示する。

## 比較・評価軸

| 対策 | 実装直行の抑止力 | mode依存 | 運用コスト |
|---|---:|---:|---:|
| Plan modeを使うだけ | 中 | 高 | 低 |
| brainstormにImplementation Gate追加 | 高 | 低 | 低〜中 |
| AGENTS.mdに共通ゲート追加 | 高 | 低 | 中 |
| TODOへspec参照追加 | 高 | 低 | 中 |

## 今回見えた方向性

- Plan mode未使用は一因として妥当だが、単独の主因とはいいにくい。
- validation事例では、2026-07-07にbrainstorm・spec・planが同一コミットで保存されており、「成果物が存在しなかった」という前提はこの事例には当てはまらない。
- より本質的な問題は、現行brainstormスキルがSpec Gateを持つ一方で、コード編集を止めるImplementation Gateを持たないこと。
- Plan modeは補助的な安全策として使い、modeに依存しない永続ルールをskillまたはAGENTS.mdに置くのが妥当。
- `plans/` は現在の標準ワークスペース構造に含まれておらず、plan成果物の保存先も整理が必要。

## 次アクション候補

1. brainstormスキルへImplementation Gateを追加する。
2. plan成果物を独立した `plans/` に置くか、`specs/` に統合するか決める。
3. AGENTS.mdへ研究実装の承認ルールを追加するか判断する。
4. meeting-minutesとTODOのspec参照導線を設計する。

## Spec化候補

Research Workspaceの「brainstorm → spec → implementation」ゲート改善としてspec化できる。必要項目は、成果物の状態遷移、承認方法、Plan mode利用可否の分岐、TODOとの連携、既存 `plans/` の扱い。

## 未解決の問い

- planを永続ファイルとして保存する必要があるか、それとも承認済みspec内の実施手順で十分か。
- 実装ゲートをbrainstormスキルだけに置くか、ルートAGENTS.mdにも置くか。
- 小さな調査・設定変更までspec必須にするか、例外条件を設けるか。
- 既存のvalidation実装で、spec・planの作成と実装開始の厳密な時系列はどうだったか。

## 関連ファイル

- `.agents/skills/brainstorm/SKILL.md`
- `.research/lab/projects/sam2-mamba-motion-tracking/meetings/2026-07-09-mtg.md`
- `.research/secretary/notes/brainstorm/2026-07-07-val-implementation-direction.md`
- `.research/lab/projects/sam2-mamba-motion-tracking/specs/2026-07-07-validation-implementation-spec.md`
- `.research/lab/projects/sam2-mamba-motion-tracking/plans/2026-07-07-validation-implementation-plan.md`
- `.research/lab/projects/research-workspace-governance/specs/2026-07-10-implementation-gate-spec.md`


---

## 追記 14:54 — Spec Gate判定

### 判定

この内容はspec化可能。保存前に、テンプレート全体の運用改善をどのプロジェクトで管理するかだけ決める。

### Spec Gate

| 条件 | 判定 | 根拠 |
|---|---|---|
| 検証したい問い | 満たす | brainstormから実装へ進むことを、modeに依存せず防げるか |
| 仮説 | 満たす | Implementation Gateと永続ルールが実装直行を抑止する |
| 実装手順 | 満たす | brainstorm・AGENTS.md・必要ならmeeting-minutes/TODO導線を段階的に更新する |
| 評価指標 | 満たす | 計画なしの外部実装編集が止まること、承認済みspecへの参照を確認できること |
| 比較対象 | 満たす | 現行workflow（Spec Gateのみ、実装開始ゲートなし） |
| 成功/失敗基準 | 満たす | 成功: 実装依頼がspec確認または計画化へ進む。失敗: specなしで外部実装リポジトリを編集する |
| 必要な成果物 | 満たす | `.agents/skills/brainstorm/SKILL.md`、`AGENTS.md`、必要に応じて `meeting-minutes` とTODO形式 |
| ユーザーの保存承認 | 未取得 | 今回はspec化可否の確認のみ |

### 推奨スコープ

初回specは、`brainstorm` とルートAGENTS.mdへImplementation Gateを導入する範囲に絞る。meeting-minutesとTODOのspec参照は、運用確認後の第2段階にする。

### 保存先の候補

- テンプレート全体の独立テーマとして、新規プロジェクト `research-workspace-governance` を作る。
- 既存の `sam2-mamba-motion-tracking` は、この改善の発見契機としてリンクするだけにする。

### まだ決めること

- `plans/` を標準構造に加えるか、spec内の実施手順へ統合するか。
- spec必須の対象を、外部実装リポジトリの変更・実験設計変更に限定するか。
