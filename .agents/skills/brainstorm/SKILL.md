---
name: brainstorm
description: 研究相談・壁打ちを構造化するスキル。研究アイデア、詰まりポイント、MTG後TODO、仮説、実験案、実装案、論文調査の方向性、spec化前の計画化相談に使う。「壁打ちしたい」「研究相談したい」「このTODOを詰めたい」「実験案を考えたい」「仮説を整理したい」「spec化できるか見て」と言われたときは必ず使う。既存研究文脈を読んでから、明確化、発散、収束、構造化、brainstorm保存、Plan modeでのspec化検討まで支援し、通常返信ではコンパクト表示、節目ではフル表示で進行状況を示す。
---

# Brainstorm（研究壁打ちスキル）

研究相談を、既存文脈に基づく「問い・仮説・実験/実装案」へ整理する。未完成の思考は秘書室のbrainstormメモへ保存し、十分に固まった内容だけを、ユーザーの明示承認後にプロジェクトの `specs/` へ昇格する。

## 参照する考え方

長い理論説明は出力しないが、運用は以下の型に従う。

- Creative Problem Solving: Clarify, Ideate, Develop, Implement
  - https://www.creativeeducationfoundation.org/what-is-cps/
- IDEO / d.schoolの発散ルール: 判断を急がない、量を出す、他案に乗る、焦点を保つ
  - https://www.designkit.org/methods/brainstorm-rules.html
  - https://hci.stanford.edu/courses/cs247/2011/readings/dschool-brainstorming.pdf
- LLM-assisted ideation: AI案への受け身化、意味的収束、既存案寄りを避ける
  - https://arxiv.org/html/2503.00946v3
  - https://www.sciencedirect.com/science/article/pii/S187118712500207X
  - https://link.springer.com/article/10.1007/s12599-025-00974-y
- Hypothesis-driven planning: 仮説、検証方法、成功指標を先に定義する
  - https://www.thoughtworks.com/en-us/insights/articles/how-implement-hypothesis-driven-development
  - https://support.optimizely.com/hc/en-us/articles/4410282998541-Design-an-effective-hypothesis

## 原則

- 発散の前に、関連する研究文脈を読む。
- 相談が曖昧なら聞き役として明確化し、材料が十分なら整理役として構造化する。
- 発散と収束を混ぜない。まず候補を広げ、その後で評価軸を使って絞る。
- 壁打ち中は、ユーザーが現在位置を見失わないように進行状況を日本語で短く表示する。
- AIの提案に寄りかかりすぎないよう、反例、別視点、未解決の問い、ユーザー判断が必要な点を必ず出す。
- brainstormメモは秘書室に保存する。プロジェクト配下に `brainstorm/` は作らない。
- `specs/` には、Plan modeで計画化し、ユーザーが明示承認した場合だけ保存する。
- brainstorm中・計画化中は外部実装リポジトリを編集しない。実装開始は、承認済みspec・変更範囲・検証方法・ユーザー承認を確認するImplementation Gateの後に限る。
- READMEは更新しない。必要なら更新候補の提示に留める。
- TODOは自動追加しない。候補を提示し、ユーザーが採用したものだけ追加する。
- 既存ファイルは丸ごと上書きしない。追記時はタイムスタンプを付ける。
- 日付ベースのファイルを作成・更新する前に、必ず今日の日付を確認する。

## 対象パス

Research Workspace運用の正本パスを使う。

```text
.research/secretary/notes/brainstorm/YYYY-MM-DD-topic.md
.research/secretary/todos/YYYY-MM-DD.md
.research/lab/projects/<project>/README.md
.research/lab/projects/<project>/meetings/*.md
.research/lab/projects/<project>/specs/*.md
.research/lab/projects/<project>/experiments/*.md
.research/lab/projects/<project>/references/*.md
.research/lab/projects/<project>/specs/YYYY-MM-DD-topic-spec.md
```

## Workflow

壁打ちでは、ユーザーが現在位置を見失わないように、通常返信ではコンパクト表示、節目ではフル表示で進行状況を示す。英語名だけにせず、日本語を主に使う。

通常返信では、原則として本文の前に以下の3行を表示する。短いやり取りでも、壁打ちが続いている間は現在地を出す。

```markdown
進行状況: 明確化中
完了: 対象特定 / 文脈読込
次: 発散
```

本文との間には空行を1つ入れる。

フェーズ変更時、保存前、spec化検討前、ユーザーが迷いそうな時は、チェックリスト型のフル表示を使う。

```markdown
進行状況:
- [x] 対象特定
- [x] 文脈読込
- [x] 明確化
- [ ] 発散 ← 現在
- [ ] 収束
- [ ] 構造化
- [ ] 保存
- [ ] spec化検討
```

フル表示を使う主なタイミング:

- 文脈読込から相談に入るとき
- 発散から収束へ移るとき
- 収束から構造化へ移るとき
- brainstormメモへ保存するとき
- spec化検討へ移るとき
- ユーザーが「今どこ」「どの段階」など現在位置を尋ねたとき

フェーズを戻す場合は、後退ではなく精度を上げるための移動として短く理由を添える。

```markdown
進行状況: 明確化中
完了: 対象特定 / 文脈読込 / 発散
次: 収束

一度収束に入りかけましたが、成功基準がまだ曖昧なので、明確化に戻します。
```

表示用フェーズ名:

```text
対象特定
文脈読込
TODO変換
明確化
発散
収束
構造化
保存
spec化検討
spec保存判定
spec保存
```

### Phase 1: 相談対象の特定

ユーザーが「壁打ち」「研究相談」「TODOを詰めたい」「仮説を整理したい」などと言ったら、分かっている情報を使って対象を特定する。

確認するもの:

- プロジェクト名
- 対象TODO
- 相談したい問い
- MTG由来かどうか
- 今日のTODOか、指定日のTODOか
- 最終的に決めたいものが、方針、実験、実装、調査のどれか

すでに会話から分かる項目は再質問しない。曖昧な項目だけ短く確認する。

### Phase 2: Context Loading

対象プロジェクトが分かる場合は、発散に入る前に研究文脈を読む。

必須:

- `.research/lab/projects/<project>/README.md`
- 対象TODO、または今日/指定日の `.research/secretary/todos/YYYY-MM-DD.md`
- `.research/lab/projects/<project>/meetings/*.md` の直近1件

必須ファイルが存在しない場合は、捏造せず「未作成」「該当なし」として前提に含める。プロジェクトREADMEが見つからない場合だけ、対象プロジェクトの確認を優先する。

必要に応じて読む:

- `specs/` の最新または関連ファイル 最大3件
- `experiments/` の最新または関連ファイル 最大3件
- `.research/secretary/notes/brainstorm/` の関連メモ 最大3件
- `references/` はまず一覧のみ。本文は必要時だけ読む。

読み込み後、前提を短く確認する。

```markdown
現在の文脈はこう理解しました。

- プロジェクト: ...
- 今回相談するTODO/問い: ...
- 直近MTGでの背景: ...
- 既に決まっていること: ...
- まだ曖昧なこと: ...

この理解で進めます。
```

### Phase 3: TODO起点Brainstorm

TODO起点の場合、TODOをそのまま扱わず、研究相談用に変換する。

```text
TODO
  -> 問い
  -> 仮説
  -> 実験案 / 実装案
  -> 評価指標
  -> 次アクション
  -> spec化候補
```

例:

```markdown
TODO:
- 動的LoRA分離の評価方法を検討する

問い:
- 何をもって「分離できた」と判断するか？

仮説:
- 時間ステップごとのLoRA寄与を分けることで、概念干渉を低減できるのではないか。

実験案:
- baseline LoRA mergeとの比較
- 固定prompt・複数seedでの比較
- CLIP類似度、画像特徴量、人手評価の併用

不足:
- 評価対象データ
- baseline
- 成功基準
```

### Phase 4: Clarify

文脈を読んでも曖昧な場合だけ質問する。質問は一度に詰め込みすぎず、研究を前に進めるために重要なものを優先する。

確認項目:

- 今回決めたいこと
- 詰まりポイント
- 既に試したこと
- 使えるデータ、モデル、コード、論文
- 制約や次回MTGまでの時間
- 成功したと言える状態

### Phase 5: Diverge

発散では、すぐ否定せず候補を広げる。

出すもの:

- 研究アイデア候補
- 仮説候補
- 実験案
- 実装案
- 比較対象
- 評価指標候補
- 関連論文・調査方向
- 反例・失敗パターン
- 別視点

### Phase 6: Converge

候補を評価して絞る。1つに決めきれなくてもよいが、有力候補、保留、棄却寄りを分ける。

評価軸:

- 新規性
- 実現可能性
- 検証しやすさ
- 論文化への寄与
- 既存研究との差分
- 次回MTGまでに進められるか
- 実験コスト
- 失敗しても学びがあるか

### Phase 7: Structure

収束した内容を、保存やspec化の前に一度まとめる。ここでは未完成の思考を無理に完成扱いせず、何が見えたか、何がまだ不確かか、次に何を決めるべきかを分ける。

まとめるもの:

- 相談の出発点
- 中心となる問い
- 有力な仮説
- 有力な実験・実装案
- 保留または棄却寄りの案
- 判断に使った評価軸
- 次に確認すべきこと
- ユーザー判断が必要な点
- spec化できそうな部分と、まだ足りない部分

必要に応じて、以下のように進行状況を示してからまとめる。

```markdown
進行状況: 構造化中
完了: 対象特定 / 文脈読込 / 明確化 / 発散 / 収束
次: 保存

ここまでの議論を、問い・仮説・実験案・未決事項に分けて整理します。
```

### Phase 8: Save Brainstorm

壁打ちが一段落したら、秘書室のbrainstormメモへ保存する。

保存先:

```text
.research/secretary/notes/brainstorm/YYYY-MM-DD-topic.md
```

同じ日付・同じtopicのファイルが既にある場合は、新規ファイルを作らず、タイムスタンプ付きで追記する。

frontmatter:

```yaml
---
date: YYYY-MM-DD
project: <project-name or null>
source_todo: <todo text or null>
topic: <topic>
status: exploratory
tags: [brainstorm, research]
---
```

本文フォーマット:

```markdown
# <topic>

## 読み込んだ文脈

## 相談の出発点

## 対象TODO

## 問い

## アイデア候補

## 仮説候補

## 実験・実装案

## 比較・評価軸

## 今回見えた方向性

## 次アクション候補

## Spec化候補

## 未解決の問い

## 関連ファイル
```

既存ファイルへ追記する場合:

```markdown
---

## 追記 HH:MM

### 読み込んだ文脈

...
```

### Phase 9: Spec Planning Bridge

実験・実装方針が固まり始めたら、すぐに `specs/` へ保存せず、Plan modeで計画化する。Plan modeが利用できない場合も、Plan mode相当として計画提示・不足確認・Spec Gateまでを行い、外部実装リポジトリの編集は始めない。

Plan modeでは、brainstormで得られた仮説、実験案、実装案、評価指標、未決事項を整理し、specとして成立するかを確認する。この段階ではまだファイルを作成しない。

ユーザーが計画化の続行を望む場合は、要約を提示して終わらず、そのままPlan mode相当の計画化を開始する。計画化では不足確認、実験/実装手順、評価指標、比較対象、成功/失敗基準を具体化し、最後にSpec Gateへ進む。

Plan modeに渡す要約:

```markdown
# Spec Planning Prompt

対象プロジェクト: <project>

元TODO:
- ...

読み込んだ文脈:
- ...

brainstormで見えた方向性:
- ...

仮説:
- ...

実験/実装案:
- ...

評価指標候補:
- ...

比較対象・ベースライン:
- ...

未決事項:
- ...

依頼:
この内容を、研究プロジェクトの `specs/YYYY-MM-DD-topic-spec.md` として保存できるレベルまで具体化してください。
不足している前提・評価指標・比較対象・成功基準があれば質問してください。
まだファイルは作成せず、まず計画を提示してください。
```

### Phase 10: Spec Gate

以下が揃うまで `specs/` には保存しない。

- 検証したい問いが明確
- 仮説がある
- 実験または実装の手順がある
- 評価指標がある
- 比較対象またはベースラインがある
- 成功/失敗の判断基準がある
- 必要なデータ・モデル・成果物がある程度分かる
- ユーザーが「spec化して」「保存して」「この内容でOK」など明示承認している

承認が曖昧な場合は保存しない。明示承認を確認する。

### Phase 11: Implementation Gate

承認済みspecがあるだけでは、外部実装リポジトリを編集しない。実装を開始する新たな依頼を受けたら、次を確認する。

- 承認済みspecのパス
- 変更対象と変更範囲
- 検証方法
- ユーザーの実装開始承認

4項目がそろわない場合は、コード編集や実験設計変更を始めず、Phase 9の計画化または不足確認へ戻る。実装開始時は、次のように短く共有する。

```markdown
Implementation Gate: 通過

- Spec: <path>
- 変更対象: <files or components>
- 検証方法: <tests or checks>
```

ユーザーがspec省略を明示する場合は、例外にする理由と影響を確認してから進める。ダッシュボード、TODO、議事録、brainstormメモの更新や読み取り専用の調査は、このゲートの対象外とする。

### Phase 12: Promote to Spec

Spec Gateを満たした場合だけ、以下に保存する。

```text
.research/lab/projects/<project>/specs/YYYY-MM-DD-topic-spec.md
```

specフォーマット:

```markdown
---
date: YYYY-MM-DD
project: <project-name>
source: brainstorm
status: draft
tags: [spec, experiment]
---

# <topic> Spec

## 目的

## 背景

## 検証したい問い

## 仮説

## 実験・実装内容

## 使用データ・モデル

## 比較対象・ベースライン

## 評価指標

## 成功/失敗の判断基準

## 実施手順

## 期待される結果

## リスク・懸念

## 未決事項

## 関連brainstorm
```

## TODOとの関係

次アクション候補は提示するが、自動追加しない。

```markdown
## 次アクション候補

以下をTODOに追加できます。

1. [ ] ...
2. [ ] ...
3. [ ] ...

追加するものを番号で教えてください。優先度や期限があれば一緒に指定してください。
```

ユーザーが採用したものだけ、`.research/secretary/todos/YYYY-MM-DD.md` に既存形式で追加する。

```markdown
- [ ] タスク内容 | 優先度: 高/通常/低
- [ ] タスク内容 | 優先度: 通常 | 期限: YYYY-MM-DD
```
