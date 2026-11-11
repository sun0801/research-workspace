---
project: kaggle-name-that-llm
status: active
summary: OOF confirmation bestは固定Spectral補正BA 0.65383（未LB検証）。Host142ではMistral03 primaryがGPU1で継続し、最新ログは32層中24層のLoRA選択を記録。Qwen3-1.7B bundleは検証一致、Qwen8B watcherは待機中。次は両bundle後に基準blend Notebook runtime gate。
created: 2026-11-02
last_updated: 2026-11-11
---

# Kaggle — Name That LLM

## 概要

18種類のLLMの生成文章からモデル名を識別するコンペ。ユーザーは主に方針・制約を伝え、AIが調査・記録・承認済み範囲の実装を担当する。知見と作業履歴をMarkdownで共有して会話をまたいで再開する。

- [公式コンペ](https://www.kaggle.com/competitions/name-that-llm)
- [コードの作業場所](../../../../../kaggle/name-that-llm/README.md)
- [環境・認証・操作ガイド](../../../../../kaggle/README.md)

## 現在の状況

- 現bestは固定Spectral補正の独立confirmation BA`.653828`（public LB未検証）。提出対象の基準blendはprimary BA`.586431`、confirmation BA`.567870`。
- 採用済み基準blendと同一構成のNotebookで9時間以内の実行見積もりを通し、1回提出してOOF BAとpublic LBの対応を確認する。見積もり超過なら構成を変えず、不足を報告する。
- Host141はGPU0/1が他runで稼働中のため新規投入不可。Host142ではMistral03 primaryがGPU1で継続中。fold3 Stage 2 epoch 1の後、08:27 JSTに32層中24層のLoRA選択イベントを記録（fold番号はログにない）。Qwen3-1.7B final fitは00:30 JSTにexit 0で完了し、primary/confirmation採用ゲートを通過。Qwen8B baseline watcherはMistral終了待ち。
- 実行中jobは30分間隔の軽量pollで監視する。Qwen3-1.7B bundleは`sha256sum -c SHA256SUMS`で一致を確認済み。Qwen8B final fit・bundle検証後、両方をstagingして基準blend Notebookのruntime gateへ進む。再開先は[11/11継続ログ](experiments/2026-11-11-host-continuation-poll.md)。
- [Notebook readiness](experiments/2026-11-10-private-baseline-notebook-readiness.md) · [OOF comparison](experiments/2026-11-10-oof-comparator-readiness.md) · [Spectral confirmation](experiments/2026-11-10-spectral-meanfield-confirmation.md)

## マイルストーン

- [x] Kaggle共通ディレクトリとName That LLMプロジェクトを作成
- [x] 公式CLI・MCP設定・収集コマンドと共同作業スキルを整備
- [x] 初期のコンペ調査と有力資料の知見を保存
- [x] 公開Notebook 3本の精読と手法・検証条件・計算資源の比較を保存
- [x] 承認済みCPUサイクルのbaseline＋5候補、最良再CV、全件fit、保存モデル再推論、比較報告を完了

## 関連記録

- [2026-11-11公式コンペ状況確認](experiments/2026-11-11-official-competition-status.md)

- [共同作業と自動化の設計メモ](../../../secretary/notes/brainstorm/2026-11-02-kaggle-collaboration-setup.md)

- [認証トラブルの診断とトークン方式](experiments/2026-11-02-kaggle-auth-troubleshooting.md)

- [認証後のNotebook取得確認](experiments/2026-11-02-authenticated-notebook-discovery.md)

- [公開Notebook 3本の精読比較](experiments/2026-11-02-public-notebook-comparison.md)

- [CPU自動実験サイクルspec](specs/2026-11-05-cpu-autonomous-cycle-spec.md)

- [CPU実装の検証結果・CLIへの引き継ぎ](experiments/2026-11-06-cpu-cycle-handoff.md)

- [CPU実験の最終比較・最良候補・再現確認・再実行コマンド](experiments/2026-11-06-cpu-cycle-results.md)

- [GPU自動実験の開始時確認と候補01](experiments/2026-11-06-gpu-autonomous-initial-check.md)

- [Open Pool v15 階層型SVC候補plan](experiments/2026-11-07-openpool-hierarchical-svc-candidate.md)

- [Open Pool v15 family-mass-preserving rerank spec](specs/2026-11-07-openpool-family-mass-rerank-spec.md)

- [Open Pool SVC complementary fixed probability blend spec](specs/2026-11-07-openpool-svc-complementary-fixed-probability-blend-spec.md)

- [Qwen + Open Pool SVC probability ensemble spec](specs/2026-11-07-qwen-svc-probability-ensemble-spec.md)

- [Qwen + prompt-centered SVC probability ensemble spec](specs/2026-11-07-qwen-prompt-centered-svc-probability-ensemble-spec.md)

- [Prompt-centered SVC low-pool-weight spec](specs/2026-11-07-openpool-prompt-centered-low-pool-weight-spec.md)

- [Public Mistral/OLMo OOF primary screen](experiments/2026-11-08-public-mistral-olmo-oof-primary-screen.md)

- [OLMo 2 1124 7B Open Pool v15 candidate spec](specs/2026-11-08-olmo2-1124-7b-openpool-v15-spec.md)

- [Fold-local typography class guards](specs/2026-11-08-nested-typography-guards-spec.md) — primaryで不採用

- [公開response corpusとNotebookのライセンス・性能主張監査](experiments/2026-11-09-public-response-corpus-and-notebook-audit.md) — (b) 試さない。全体provenance/license不明、性能転移の独立根拠なし。

- [公開ensembleのアブレーションと採点version監査](experiments/2026-11-09-public-ensemble-ablation-audit.md) — (b) 試さない。reported`.663`は`.755`未満で、OOF/採点versionは未検証。

- [Spectral Notebook prompt-cluster recovery spec](specs/2026-11-09-spectral-prompt-cluster-recovery-screen-spec.md)

- [Spectral Notebook prompt-cluster recovery result](experiments/2026-11-09-spectral-prompt-cluster-recovery-screen.md)

- [Spectral cluster mean-field primary spec](specs/2026-11-09-spectral-cluster-meanfield-primary-spec.md)

- [Spectral cluster mean-field primary result](experiments/2026-11-09-spectral-cluster-meanfield-primary.md)

- [Areeb 0.673 Notebook v2 source audit](experiments/2026-11-09-areeb-0-673-notebook-audit.md) — (b) 試さない。score未検証、外部data/provenanceとcluster補正が未確認。

- [xiangqizhang .681 Notebook source audit](experiments/2026-11-10-xiangqizhang-0681-notebook-audit.md) — (c) 保留。基準CV-LB対応後にpreviewなしprompt-grouped OOFと採用blend比較、score source確認が必要。

- [Hande Akin Qwen3 embedding + LR + Sinkhorn Notebook audit](experiments/2026-11-10-handeakn-embedding-sinkhorn-audit.md) — (b) 試さない。equal-18仮定が不均等test分布と不整合で、独立OOF/score根拠なし。

- [Jaime Oliver 0.742+ DeBERTa ensemble Notebook review](experiments/2026-11-10-jaime-oliver-deberta-0742-notebook-review.md) — (c) 保留。基準blendのCV-LB対応、Leakage-free prompt-grouped OOF、依存checkpointの学習分割/provenance照合が必要。

- [Qwen3-Embedding公開blend Notebook review](experiments/2026-11-09-qwen3-embedding-public-notebook-review.md) — (b) 試さない。`.681`/`.595`未検証、candidate08と重複し、首位超えの根拠なし。

- [Candidate11/13 OOF comparator readiness](experiments/2026-11-10-oof-comparator-readiness.md) — 旧CPU/SVC/Qwen+SVC OOFの整合を確認

- [Qwen blend sibling-style residual spec](specs/2026-11-09-qwen-blend-sibling-style-residual-spec.md) — primaryで不採用

- [Qwen blend sibling-style residual result](experiments/2026-11-09-qwen-blend-sibling-style-residual.md)
- [InStyle Qwen3-14B / public extra-pool Notebook audit](experiments/2026-11-09-instyle-qwen14-and-extra-pool-notebook-audit.md) — (b) 試さない。score/version/OOF未検証、prompt overlap・provenance・nested confirmationに未解決点あり。

- [GLM-5.3 OOF corner Discussion and GGUF feasibility audit](experiments/2026-11-09-glm53-oof-corner-discussion-audit.md) — (b) 試さない。追加コメントはGLM/Claude混同を示すが、GLM likelihood実験なし・動作するoffline経路なし。
- (b) 試さない — [Model Parameterizations Discussion](https://www.kaggle.com/competitions/name-that-llm/discussion/757125) reports best mean-pooling/linear-head accuracy`.64–.65` and no better tested alternative; no reproducible gain over current confirmation best`.653828`. — (b) 試さない

- [Omkar Pattanaik v28 Sovereign Titan Apex Notebook triage](experiments/2026-11-10-omkar-v28-apex-notebook-triage.md) — (b) 試さない。記載目標`.690–.711`は確認済み公開首位`.755`未満で、実LB score根拠なし。
- (b) 試さない — [CatBoost-based Discussion](https://www.kaggle.com/competitions/name-that-llm/discussion/757303) reports its CatBoost/LightGBM/XGBoost + TF-IDF stack at`.336`, well below adopted OOF`.653828`; the separate`.673` transformer claim has no reproducible method in the post. — (b) 試さない
- (b) 試さない — [首位提出者James Liebelの公開Notebook検索](https://www.kaggle.com/jamesliebel)ではコンペNotebookが見つからず、公開GLM-5.3 GGUF mirrorだけでは再現手法を特定できない。 — (b) 試さない
- (b) 試さない — [two-base ensemble ablation Discussion](https://www.kaggle.com/competitions/name-that-llm/discussion/756088) reports best public score`.663` (above local OOF`.653828` but below current leader`.755`), with a large multi-model stack and no path toward the goal margin. — (b) 試さない

## 共同作業の引き継ぎ

- Host141/142は実際に空いている場合に利用可。停止指示は指定hostだけに適用する。
- 停止対象の途中結果と正確な再開位置を保存し、そのhostのKaggle jobと自動投入watcherを停止してGPU解放を確認する。もう一方は継続し、停止hostは明示的な再利用指示まで予約する。
- 実行中jobは30分ごとに軽い1コマンドで監視し、変化時だけ記録する。公式情報は1日1回とNotebook push・提出直前に確認する。
- 今回は停止指示ではない。最新の実行状況は[11/11継続ログ](experiments/2026-11-11-host-continuation-poll.md)、過去の引き継ぎ記録は[archive](experiments/2026-11-10-readme-handoff-history.md)。

## 更新履歴

- 2026-11-11: README整理時に抜けた完了済みマイルストーン5件を復元し、履歴アーカイブの相対リンクと監査・継続ログの重複を修正。
- 2026-11-11: 当日公式情報を再確認し、leaderboard/top/team count、締切差異、提出条件を[日付ログ](experiments/2026-11-11-official-competition-status.md)に保存。
- 2026-11-11: Qwen3-1.7B final fitのexit 0、採用ゲート通過、GPU0解放とbundle checksum一致、およびMistral03 fold3 checkpoint・LoRA選択の進捗を[継続ログ](experiments/2026-11-11-host-continuation-poll.md)に記録。「現在の状況」を20行以内に整理し、過去の詳細は日付履歴に保持。
- 2026-11-10: 承認済み運用改訂に合わせ、現在の状況を現best・基準blend提出方針・host状態・blockerに整理。過去の時刻・PID・資源状況は[継続ログ](experiments/2026-11-10-host-continuation-poll.md)と[状況履歴](experiments/2026-11-10-readme-current-situation-history.md)に保持。
- 詳細な更新履歴は[2026-11-10アーカイブ](experiments/2026-11-10-readme-update-history.md)に保存。
- 現在の状況の旧記録は[状況履歴](experiments/2026-11-10-readme-current-situation-history.md)、共同作業の旧引き継ぎは[引き継ぎ履歴](experiments/2026-11-10-readme-handoff-history.md)を参照。
