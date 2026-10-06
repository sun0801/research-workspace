---
date: 2026-10-06
project: sam2-mamba-motion-tracking
source_todo: temporal Mambaの特徴表現・挿入位置の調査 / HOTA 70以上のMOT手法とSAM2MOT条件の比較
topic: literature-research-workflow
status: exploratory
tags: [brainstorm, research, literature-review, zotero]
---

# 論文調査と議論を残す運用

## 読み込んだ文脈

- 2026-09-30 MTGでは、temporal Mambaの空間表現・挿入位置と、HOTA 70以上の追跡手法の評価条件比較が次の調査対象になった。
- temporal MambaはSAM2 decoder直前の`pix_feat`へ入れる最小構成を接続済みだが、1-token poolingが位置情報を失う点を含め、最終設計は未決定。
- SAM2MOT再現はS4のQ-RがDanceTrack valで逆効果。公開結果と比較する際は、split・検出・学習・評価条件の差を分けて調べる必要がある。
- ユーザーはDeep Researchの広い調査能力を使いつつ、論文内容とこの場の議論をローカルに保存したい。既読文献はZoteroにある。

## 相談の出発点

Deep Researchへ依頼するプロンプトを作る従来の方法は、Deep Researchレポートを保存できても、個別論文の読み込みと対話で得た解釈・判断をResearch Workspaceに残す導線が弱い。通常のChatGPTで同じ調査を行う場合の精度とDeep Research利用枠も懸念されている。

## 暫定的な運用案

1. Deep Researchは、広い文献探索と候補の比較が必要な問いに絞る。出力レポートはMarkdownで保存し、候補文献のDOI・主張・根拠箇所をZotero登録と照合する。
2. Zoteroは書誌情報・PDF・ユーザーの注釈の正本にする。個別論文を読む段階では、Zotero内のPDF本文・注釈を参照し、必要な論文だけ1〜2本ずつ根拠箇所とページ番号を確認する。
3. 論文ごとの要点と限界は `papers/` に日付付きの短い読解メモとして保存する。比較表は、設計調査なら特徴表現・挿入位置・空間情報・計算量、SAM2MOTならsplit・detector・学習データ・評価protocolを軸にする。
4. 議論の仮説、反例、未決事項、採用理由は、secretaryのbrainstormメモに論文メモへのリンクとともに残す。設計が固まったら、別途spec化ゲートを通す。
5. Zotero連携は、まずローカルのread-only検索・PDF/注釈取得に限定する。AIから文献の編集、タグ付け、コレクション移動を行う書き込み権限は初期運用では付けない。

## 精度と利用枠についての見立て

- Deep Researchは複数情報源を組み合わせる広い調査向けとして温存し、個別論文の精読や既知文献に基づく比較は、元論文を参照できる通常の対話で行う。
- Zotero MCPは文献へのアクセスと引用根拠の追跡を改善しうるが、推論精度を自動的に保証したり、Deep Researchの利用枠を増やしたりはしない。PDF抽出が崩れた表・数式・図はページ画像または原文で確認する。
- Deep Researchの出力だけで論文の主張を確定せず、重要な記述は一次論文の該当ページ・表・式へ戻って照合する。

## 2つの調査への適用候補

- temporal Mamba設計: Deep Researchで関連アーキテクチャの候補群を探索し、重要論文をZoteroから選んで、空間token/圧縮表現・挿入位置・計算量・時系列stateの設計根拠を読む。
- HOTA 70以上の手法: 候補論文を見つけた後、Zoteroで本文を確認し、DanceTrack split、detector、追加学習データ、TrackEval protocol、報告値を行ごとに記録する。再現値との差は条件差と実装差を分けて議論する。

## 未解決の問い

- Zotero MCPをCodexが使える実行環境へ接続するか、まずはZoteroから選択PDFと注釈を手動exportして扱うか。
- Deep ResearchのMarkdownレポートと個別論文メモを、`papers/`でどう対応づけるか。
- 初回の文献調査で読む論文数と、読解メモに必要な詳細度。

## 関連ファイル・一次資料

- `.research/lab/projects/sam2-mamba-motion-tracking/meetings/2026-09-30-mtg.md`
- `.research/lab/projects/sam2-mamba-motion-tracking/specs/2026-09-27-temporal-mamba-decoder-minimal-integration-spec.md`
- `.research/secretary/notes/brainstorm/2026-09-30-temporal-mamba-adapter-training.md`
- [OpenAI: Deep research in ChatGPT](https://help.openai.com/en/articles/10500283-deep-research-in-chatgpt)
- [Zotero: Local API](https://www.zotero.org/support/dev/web_api/v3/local_api)
- [Zotero MCP candidate project](https://github.com/54yyyu/zotero-mcp)

---

## 追記 18:11 JST

ユーザー提案を受け、運用スキル名は一般的な `deep-research` とする。最初に調査対象を確認し、プロンプトを提示した後、この場で何度でも修正できるようにする。ユーザーが完成と判断するまで最終版として扱わない。

利用枠を抑えるため、レポートの保存と短い全体整理を通常動作にする。レポートから候補文献を列挙しても、Zotero本文・注釈の取得や論文ごとの詳細メモ作成へ自動で進まない。根拠確認が重要な候補だけをユーザーが選び、選んだ論文に限って本文を確認する。Zotero MCPは任意の読み取り経路とし、未設定なら手動でPDF等を渡す。

公式のChatGPT利用案内では、モデル・タスク規模・コンテキスト・ツール使用・検索取得などが利用量に影響し、似たタスクでも使用量は固定でない。したがって「1論文につきいくら」とは見積もらず、複数論文の一括取得・精読を避け、必要な根拠だけを読む方針とする。[ChatGPT Learn: Pricing](https://learn.chatgpt.com/docs/pricing)

関連するスキル案: `.agents/skills/deep-research/SKILL.md`
