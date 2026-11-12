(b) 試さない — 単独投稿の`.657`はCV/LBの別と再現手順がなく、現bestおよび公開首位を超える根拠にならない。

---

date: 2026-11-12
project: kaggle-name-that-llm
type: public-discussion-audit
conclusion: b-no-test
---

# Qwen3-14B single-model `.657` Discussion audit

確認日時: 2026-11-12 18:03 JST。

## Source and inspected range

- Kaggle Discussion: [What score your best single model can achieve?](https://www.kaggle.com/competitions/name-that-llm/discussion/754860)
- Official Kaggle MCP `list_competition_topics`でRecent一覧を取得し、`list_topic_messages`でtopic 754860のメッセージを新着順に確認。最新の親投稿は2026-11-12 03:52:50 UTCで「0.657 single qwen 14b」。返信では5-fold CVか単独提出かを質問しているが、確認時点で回答なし。
- 追跡確認（2026-11-12 19:02 JST）で新しい返信を確認。「single qwen14b pretraining on external data and full finetune on host data」と説明された。学習方式は少し明らかになったが、評価値がCVかPublic LBか、split/OOF、Notebook/model versionは依然不明。
- 記載にはNotebook/model/dataの識別子、学習・validation条件、LB/CVの区別、再現コードがない。scoreのKaggle version表示も確認できない。

## Decision

(b) 試さない。追加返信からfull fine-tuneは分かったが、報告`.657`のCV/LB・OOF・split・versionは不明で、現行independent confirmation BA`.653828`との比較にも使えない。公開leaderboardの`.768`を超える根拠がないため候補化しない。

## Scope

これは公開Discussionの主張監査のみ。公式Rules/Timeline/Leaderboardは再取得していない（本日の確認頻度制限内）。Kaggle asset、Notebook、submission、local implementationは変更していない。
