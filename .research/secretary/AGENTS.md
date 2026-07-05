# Research Workspace - Secretary

このフォルダは、研究活動の日次管理と一時的な相談メモを扱う秘書室です。

## 役割

- TODO管理
- brainstormメモの保存
- 意思決定メモや日次メモの保存
- 研究作業の入口としての軽い整理

## 保存先

```text
.research/secretary/todos/YYYY-MM-DD.md
.research/secretary/notes/brainstorm/YYYY-MM-DD-topic.md
.research/secretary/notes/YYYY-MM-DD-decisions.md
.research/secretary/notes/YYYY-MM-DD-learnings.md
```

## TODOルール

- TODOは、ユーザーが明示したもの、または候補から採用したものだけ追加してください。
- 日次TODOは `.research/secretary/todos/YYYY-MM-DD.md` に保存してください。
- 日付ベースのファイルを作成・更新する前に、必ず今日の日付を確認してください。
- 同じ日付のTODOファイルがある場合は、新しい別ファイルを作らず、追記または更新してください。

TODO形式:

```markdown
- [ ] タスク内容 | 優先度: 高/通常/低
- [ ] タスク内容 | 優先度: 通常 | 期限: YYYY-MM-DD
- [x] 完了タスク | 完了: YYYY-MM-DD
```

## Brainstormルール

- brainstormメモは `.research/secretary/notes/brainstorm/YYYY-MM-DD-topic.md` に保存してください。
- `YYYY-MM-DD.md` のような日次まとめファイルにはしないでください。
- 研究相談の深掘り、仮説整理、spec化前の計画化は `brainstorm` スキルに委ねてください。
- brainstormで出たTODO候補は自動追加せず、ユーザーが採用したものだけTODOに追加してください。

## しないこと

- `inbox/` を前提にしない。
- 部署追加や組織変更を提案しない。
- このテンプレート外の要件定義テンプレートを前提にしない。
- 固まっていない研究相談を、ユーザー承認なしに `specs/` へ保存しない。
