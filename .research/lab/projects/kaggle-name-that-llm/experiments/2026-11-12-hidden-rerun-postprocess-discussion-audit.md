(b) 試さない — 独自CUDA subprocessによる後処理失敗の報告で、こちらのbaseline Notebookには同機構がない。

---
date: 2026-11-12
project: kaggle-name-that-llm
type: public-discussion-audit
conclusion: b-no-test
---

# Hidden rerun late post-processing Discussion audit

確認日時: 2026-11-12 19:02 JST。

- Source: [Late post-processing cell never seems to affect the score in the hidden rerun](https://www.kaggle.com/competitions/name-that-llm/discussion/758021)。投稿者の`.682` submissionは、保存logitsを読む遅延セルでbundled CUDA binaryをsubprocess実行し、成功時に`submission.parquet`を置換する設計。commitと4,000行synthetic runでは動くが、hidden scoringではfallbackして同scoreに見えると報告。
- Replyは`KAGGLE_IS_COMPETITION_RERUN`による明示判定、同等のsession options、入力速度のばらつきと約30分の余裕を紹介。投稿者の個別経験であり、こちらのfailed hidden rerunの原因を示す根拠ではない。
- Private baseline v9とv12のNotebook code cellsを読み、`KAGGLE_IS_COMPETITION_RERUN`、`subprocess`、遅延後処理、atomic置換のいずれも存在しないことを確認。こちらはscoreなしのhidden rerun failureで、discussionはscore unchangedの別事象。
- Decision: (b) 試さない。baseline構成をこのdiscussionに合わせて変更しない。v9 failureの原因は既存benchmark logの仮説と診断範囲を維持する。
