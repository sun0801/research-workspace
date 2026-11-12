---
project: kaggle-name-that-llm
status: active
summary: 現bestはSpectral confirmation BA`.653828`（LB未検証）。DeBERTa固定additionはprimary gate不通過、次はHost142復旧後にMistral独立確認。
created: 2026-11-02
last_updated: 2026-11-12
---

# Kaggle — Name That LLM

## 概要

18種類のLLMの生成文章からモデル名を識別するコンペ。ユーザーは主に方針・制約を伝え、AIが調査・記録・承認済み範囲の実装を担当する。知見と作業履歴をMarkdownで共有して会話をまたいで再開する。

- [公式コンペ](https://www.kaggle.com/competitions/name-that-llm)
- [コードの作業場所](../../../../../kaggle/name-that-llm/README.md)
- [環境・認証・操作ガイド](../../../../../kaggle/README.md)

## 現在の状況

- 現bestはSpectral補正のindependent confirmation BA`.653828`（LB未検証）。公開首位は`.768`（11/12公式確認）。採用中の基準blendはprimary BA`.586408`。
- 基準blend v12 ref`58261829`はPublic`.541`で採点成功。CVとの差は約`-.045`で、CV-LB対応はまだ1点のみ。
- v9 refs`58251076`・`58253257`はhidden rerunで`COMPLETE`だが、Public/Private scoreなし。Kaggleは一般エラーのみ返し、詳細traceは未取得。
- v9失敗の第一仮説は入力path・`train.csv`/template依存。v12のtest-only入力で成功したため支持されるが、根因確定ではない。[診断ログ](experiments/2026-11-12-baseline-benchmark-push.md)
- Mistral＋Spectral primary BA`.689791`はshape screen（uniform m=2/3）も通過、独立confirmation待ち。Host142 GPU1の実行gateは未通過。[screen](experiments/2026-11-12-mistral-spectral-small-prompt-shape-screen.md) · [確認spec](specs/2026-11-12-mistral-spectral-complementarity-confirmation-spec.md)
- 公式MITの未調整DeBERTa-v3-large primary OOFは全5 fold完了。固定addition＋Spectral BA`.654571`でbaseline`.664952`を下回り、prompt bootstrap CIも負のため候補棄却。独立確認・提出には進めない。[spec](specs/2026-11-12-deberta-v3-large-official-prompt-grouped-spec.md) · [実験ログ](experiments/2026-11-12-deberta-v3-large-pilot-primary.md)
- Spectral mean-field単体はprimaryのm=2/3 shapeで不安定だが、固定Mistral追加後はuniform shape flagを通過。[screen](experiments/2026-11-12-spectral-meanfield-small-prompt-shape-screen.md) · [Mistral＋Spectral](experiments/2026-11-12-mistral-spectral-small-prompt-shape-screen.md)
- 次はHost142の厳格host-key確認・queue解消・current-runner pilotを満たしてからconfirmationを再開する。host/deviceの割当ては変えない。
- 21:30 JST: DeBERTa primaryはexit 0。登録済みCPU evaluatorで全2,699行を検証し、固定addition＋Spectralのprimary gate不通過を確認。Host141 GPU1/2は別ユーザーjobが稼働中で未変更。[候補ログ](experiments/2026-11-12-deberta-v3-large-pilot-primary.md)
- 次はHost142固定のMistral＋Spectral独立確認。host-key確認に失敗中のため接続復旧までは状態を推測せず、再試行は次の予定pollのみ。Kaggle提出待ちはなし。
- 現在の候補screen結果・公開監査の結論は各日付ログを参照。詳細な履歴は[README整理アーカイブ](experiments/2026-11-12-readme-status-archive.md)。

## 記録方針

2026-11-12改訂：見送り・保留の公開調査は `experiments/YYYY-MM-DD-source-audit-log.md` に1行ずつ集約する。新しい個別文書は実際に試す候補のspec・結果ログを基本とし、監視・提出診断の変化なしは追記しない。既存記録は保持する。開始・再開時は[承認済みspecの記録運用改訂](specs/2026-11-06-gpu-autonomous-first-place-spec.md#記録運用の改訂2026-11-12ユーザー方針)を読む。

## マイルストーン

- [x] Kaggle共通ディレクトリとName That LLMプロジェクトを作成
- [x] 公式CLI・MCP設定・収集コマンドと共同作業スキルを整備
- [x] 初期のコンペ調査と有力資料の知見を保存
- [x] 公開Notebook 3本の精読と手法・検証条件・計算資源の比較を保存
- [x] 承認済みCPUサイクルのbaseline＋5候補、最良再CV、全件fit、保存モデル再推論、比較報告を完了

## 関連記録

- [2026-11-12 README状況整理・提出失敗診断更新](experiments/2026-11-12-readme-status-archive.md)
- (a) specにして試す — [DeBERTa-v3-large clean-base candidate](experiments/2026-11-12-deberta-v3-large-candidate-selection.md) · [fixed prompt-grouped spec](specs/2026-11-12-deberta-v3-large-official-prompt-grouped-spec.md)
- (b) 試さない — [Qwen3-14B single-model `.657` Discussion audit](experiments/2026-11-12-qwen14b-0657-single-model-discussion-audit.md)（CV/LBの区別と再現根拠なし）
- (b) 試さない — [No-paid-data / top-10 Discussion audit](experiments/2026-11-12-no-paid-data-top10-discussion-audit.md)（手法・OOF・順位の根拠なし）
- (b) 試さない — [`.668 fork + response corpus` Notebook audit](experiments/2026-11-12-whitegg-ntl-fuse33-notebook-audit.md)（全体OOF/score provenance未確認、既存候補と重複）
- (b) 試さない — [RanJeet Nov12 WEMM ensemble Notebook](experiments/2026-11-12-ranjeet-nov12-wemm-notebook-audit.md)（3行FAST_COMMITのみ、full inference/OOF/score未確認）
- (b) 試さない — [Lin Junren Week4 AV Notebook](experiments/2026-11-12-linjunren-week4-av-audit.md)（new 60k/style-score Public未採点、既存Open Pool SVCと重複）
- (b) 試さない — [Toyns Freg ModernBERT v2 validation Notebook](experiments/2026-11-12-toynsfreg-modernbert-v2-audit.md)（単一grouped holdout、v2実行出力なし、主張`.68`は現leader`.768`未満）
- (b) 試さない — [Zhihao Huan NTL 0663 V31 ATLAS20](experiments/2026-11-12-zhihaohuan-0663-v31-atlas20-audit.md)（title`.663`、現leader`.768`とMistral+Spectral primary未満、大規模外部依存）
- (b) 試さない — [OsakanaTeishoku Qwen3-14B-Base score](experiments/2026-11-12-osakanateishoku-qwen14b-base-audit.md)（`.620`/`.622`は本人報告のみ、該当モデルsourceなし）
- (b) 試さない — [Evgen Dvorkin forensic EDA / inference v28](experiments/2026-11-12-evgendvorkin-v28-notebook-audit.md)（既知`.684` ensemble系譜、現leader`.768`未満、multi-source）
- (b) 試さない — [Heliosli Qwen3 embedding ensemble v14](experiments/2026-11-12-heliosli-v14-delta-audit.md)（target mix変更のみ、title`.683`、OOFなし）
- (b) 試さない — [Alex Chilton all-public `.684` Notebook](experiments/2026-11-12-alexchilton-0684-all-public-notebook-audit.md)（複合stackは移植せず、Discussionの小prompt仮説は別screenで評価）
- (b) 試さない — [Kirill fixed punctuation prior](experiments/2026-11-12-kirill-punctuation-prior-audit.md) · [screen result](experiments/2026-11-12-spectral-punctuation-prior-screen.md)（primaryでBA差0・予測変更0、confirmationなし）
- (b) 試さない — [Hidden-rerun late post-processing Discussion](experiments/2026-11-12-hidden-rerun-postprocess-discussion-audit.md)（こちらのbaselineに同じCUDA subprocess方式なし）
- (c) 保留 — [WeMM4 expanded LoRA component](experiments/2026-11-12-wemm4-expanded-lora-component-audit.md)（source dataset/license未確認、公開OOF splitが登録splitと不一致）

- [2026-11-11公式コンペ状況確認](experiments/2026-11-11-official-competition-status.md)
- [2026-11-12公式コンペ状況確認](experiments/2026-11-12-official-competition-status.md)
- [2026-11-12 Host141候補OOF追加screen](experiments/2026-11-12-host141-candidate-addition-screen.md)
- [2026-11-12 DeBERTa-v3-large pilot/primary OOF](experiments/2026-11-12-deberta-v3-large-pilot-primary.md)
- [2026-11-12 Host142継続poll](experiments/2026-11-12-host-continuation-poll.md)
- [2026-11-12 baseline benchmark push](experiments/2026-11-12-baseline-benchmark-push.md)
- [2026-11-12 Qwen3-8B + Spectral complementarity screen](experiments/2026-11-12-qwen8b-spectral-complementarity-screen.md)
- [2026-11-12 Qwen3-1.7B + Spectral complementarity screen](experiments/2026-11-12-qwen17b-spectral-complementarity-screen.md)
- [2026-11-12 4-view SVC + Spectral complementarity screen](experiments/2026-11-12-4view-svc-spectral-complementarity-screen.md)
- [2026-11-12 Prompt-centered Twin SVC + Spectral screen](experiments/2026-11-12-prompt-centered-twin-spectral-complementarity-screen.md)
- (b) 試さない — [top 1% validation Discussion](experiments/2026-11-12-top1-validation-discussion-audit.md)
- (b) 試さない — [hidden rerun post-processing Discussion](experiments/2026-11-12-hidden-rerun-discussion-audit.md)
- (b) 試さない — [Areeb Ali 0.684 public Notebook mirror](experiments/2026-11-12-public-0684-notebook-audit.md)
- (b) 試さない — [The Prompt Is Not the Author v32](experiments/2026-11-12-prompt-is-not-author-audit.md)
- (b) 試さない — 現leader NguyenThanhNhanのNotebook user/title searchと`.768`/team名のDiscussion検索で、再現可能な手法sourceは見つからず。[監査](experiments/2026-11-12-current-leader-public-notebook-search.md)
- (b) 試さない — [Alex Chilton “0.684: All Public + What Failed”](experiments/2026-11-12-alexchilton-0684-all-public-audit.md)は本人報告`.684`で、現leader`.768`を超える根拠なし。
- (b) 試さない — [whitegg “ntl fuse33 (0.668 fork + response corpus)”](https://www.kaggle.com/code/whitegg/ntl-fuse33-0-668-fork-response-corpus)はtitle上の`.668`が現leader`.768`未満で、21 dataset・8 kernel由来の大規模ensembleに独立CV/ablationの比較根拠がない。

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

- (b) 試さない — [xiangqizhang .681 Notebook source audit](experiments/2026-11-10-xiangqizhang-0681-notebook-audit.md)。score/OOF未確認、previewなし再現sourceがない。

- [Hande Akin Qwen3 embedding + LR + Sinkhorn Notebook audit](experiments/2026-11-10-handeakn-embedding-sinkhorn-audit.md) — (b) 試さない。equal-18仮定が不均等test分布と不整合で、独立OOF/score根拠なし。

- (b) 試さない — [Jaime Oliver 0.742+ DeBERTa ensemble Notebook review](experiments/2026-11-10-jaime-oliver-deberta-0742-notebook-review.md)。dependency checkpointはcompetition trainで学習済み、score/OOF差異とprovenance未解消。

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
- 今回は停止指示ではない。実行中benchmarkの再開位置は[11/12 benchmark log](experiments/2026-11-12-baseline-benchmark-push.md)、Host141/142の直近診断は[継続ログ](experiments/2026-11-12-host-continuation-poll.md)、過去の引き継ぎ記録は[archive](experiments/2026-11-10-readme-handoff-history.md)。

## 更新履歴

- 2026-11-12: 記録運用を改訂。見送り・保留は日次一覧、実験はspec・結果ログへ集約し、変化なしの監視追記を省く。詳細は承認済みspecの記録運用改訂を参照。

- 2026-11-12: Discussion 753177由来のm=2/3 prompt-shape meanfield screen完了。primaryはuniform条件で差が負、confirmationは正。primary robustness flagとし、公開複合stackは(b)試さない。[screen](experiments/2026-11-12-spectral-meanfield-small-prompt-shape-screen.md) · [audit](experiments/2026-11-12-alexchilton-0684-all-public-notebook-audit.md)

- 2026-11-12: 公開Mistral OOFと完了したlocal Mistral primary OOFを同一registered foldsで照合。BAは`.586048`/`.587566`、argmax一致68.58%。source provenance・OLMo再現は未解決のため公開OOFは不採用。[result](experiments/2026-11-08-public-mistral-olmo-oof-primary-screen.md)

- 2026-11-12: Heliosli v14をv13とのparameter deltaで監査。title`.683`、target mixのみ変更、session出力にOOF/LB根拠なしのため(b)試さない。[audit](experiments/2026-11-12-heliosli-v14-delta-audit.md)

- 2026-11-12: Evgen Dvorkin Notebook v28のsourceとsessionを確認。既知`.684` Clean LoRA + Qwen Embedding系譜の再構成で新しいOOF/LB根拠がないため(b)試さない。[audit](experiments/2026-11-12-evgendvorkin-v28-notebook-audit.md)

- 2026-11-12: Lin JunrenのWeek4 AV Notebook v1をsource・完了session logまで監査。AV結果は確認できたが、新60k/style-score構成のLBはpendingで、既存Open Pool SVCと重複するため(b)試さない。[audit](experiments/2026-11-12-linjunren-week4-av-audit.md)

- 2026-11-12: 固定fold-local punctuation priorのprimary screenはSpectral BA差0・予測変更0で棄却。specゲートに従いconfirmation・tuningなし、監査を(b)試さないで終了。[result](experiments/2026-11-12-spectral-punctuation-prior-screen.md)

- 2026-11-12: public full-train DeBERTa checkpointは除外し、MITの未調整Microsoft DeBERTa-v3-largeを全foldで再学習する独立候補specを作成。Host141 GPU1 pilot/resource gate通過前は開始しない。[candidate](experiments/2026-11-12-deberta-v3-large-candidate-selection.md) · [spec](specs/2026-11-12-deberta-v3-large-official-prompt-grouped-spec.md)

- 2026-11-12: v12の初CV-LB対応後、保留していたXiangqi Zhang`.681`とJaime Oliver`.742+`を再判定。preview/leakage・score provenance/OOFの問題が残り、両監査とも(b)試さないで終了。[Xiangqi](experiments/2026-11-10-xiangqizhang-0681-notebook-audit.md) · [Jaime](experiments/2026-11-10-jaime-oliver-deberta-0742-notebook-review.md)

- 2026-11-12: Discussion 749447の「paid generationなしでtop 10」自己申告を確認。再現手法や順位根拠がなく(b)試さない。[audit](experiments/2026-11-12-no-paid-data-top10-discussion-audit.md)

- 2026-11-12: Discussion 754860のQwen3-14B単独`.657`投稿を確認。CV/LB・再現根拠不明、著者Notebookなしを追加確認し(b)試さない。[audit](experiments/2026-11-12-qwen14b-0657-single-model-discussion-audit.md)

- 2026-11-12: `ntl-v30-apex-0700`のタイトルscore`.700`はsource冒頭の`.684`再現説明で裏づけられず、巨大stackの独立OOFもないため(b)試さない。[audit](experiments/2026-11-12-apex-0700-notebook-audit.md)
- 2026-11-12: baseline v12 ref`58261829`の採点完了、Public`.541`。初のCV-LB対応点として[benchmark log](experiments/2026-11-12-baseline-benchmark-push.md)に記録。
- 2026-11-12: 改訂specに沿って「現在の状況」を現best・benchmark v7の未解決点・次のpoll・host再開条件に整理。資材検証、旧Notebook失敗、候補数値、公式確認の詳細は日付付きexperimentsログにまとめる。
- 2026-11-12: v7はTesla T4に割り当てられQwen8B SDPA probeでOOM。現行Kaggle CLI docsに`NvidiaL4X1`はなく`NvidiaTeslaT4`はT4×2と記載。v7診断、v6との違い、Host141の空き状況を[benchmark log](experiments/2026-11-12-baseline-benchmark-push.md)へ保存。
- 2026-11-12: specの運用改訂に合わせ、「現在の状況」を現best・基準blend提出gate・認証blocker・host再開先に整理。詳細な候補結果、checksum、時刻・資源情報は既存の日付付きexperimentsログに保持。
- 2026-11-12: 公式Leaderboard首位`.765`・チーム数5,496、提出上限・Code Requirementsを確認。metadataとTimelineでFinal Submission Deadlineが1日ずれている点、CLI未認証で提出残数を取得できない点を[日付ログ](experiments/2026-11-12-official-competition-status.md)に記録。private assetのremote upload・Notebook push・Submissionは未実施。
- 2026-11-12: Host141のcandidate11/12/13 primary OOFをCPU bestと比較し、固定equal-weight additionも2,000回prompt-paired bootstrapでscreen。現行blendを改善せず、追加候補にはしない。結果とHost141 idle状態を[日付ログ](experiments/2026-11-12-host141-candidate-addition-screen.md)へ保存。基準BAの旧記載`.586431`を現行artifact summaryの`.586408`へ訂正。
- 2026-11-12: Host142の静的alias `142`でQwen8B watcher終了とGPU1 idleを確認。Candidate09の停止中watcherが残るため、候補14はspecのterminal条件に従い未投入。[poll記録](experiments/2026-11-12-host-continuation-poll.md)。
- 2026-11-12: Kaggle CLIの`.env`認証が通り、private asset Dataset version 1の`Ready`・privacyを確認。benchmark push前に公式rules/timeline/code requirements/leaderboard、5,508チーム、提出枠5・提出履歴0を再確認。[公式状況ログ](experiments/2026-11-12-official-competition-status.md)。
- 2026-11-12: benchmark-only Notebook v1はL4指定に対し実環境がT4を割り当てたため、GPU名assertで約62秒後に失敗。blend構成と4,000行runtime projectionは維持し、GPU名を記録する修正後のprivate v2をpush。[実験ログ](experiments/2026-11-12-baseline-benchmark-push.md)。
- 2026-11-12: Host142の01:51 JST pollはSSH host key verificationで失敗。alias解決先とknown_hostsを読み取り確認したが一致する登録なし。安全な鍵確認までHost142の現況は未確認として扱う。[継続ログ](experiments/2026-11-12-host-continuation-poll.md)。
- 2026-11-12: benchmark v2は実GPU/T4でCUDA確認後、競技データpathのassertで約43秒後に停止。公式Code Requirementsの`/kaggle/input/competitions/name-that-llm`へ修正しprivate v3をpush。次回pollは02:42 JST。[benchmark log](experiments/2026-11-12-baseline-benchmark-push.md)。
- 2026-11-12: v3は公式競技pathを通過後、private Dataset mount rootの想定違いで約67秒後に停止。remote sourceとhead fileの存在を確認し、標準path variantsからrootを解決するprivate v4をpush。公開首位は`.768`に更新。[benchmark log](experiments/2026-11-12-baseline-benchmark-push.md)。
- 2026-11-12: v4はasset mount解決後、artifact要求scikit-learn 1.9.1に対しKaggle runtime 1.6.1のため約48秒後に停止。local 1.9.1で作った64×18 SVC decision referenceと比較するgateを追加したprivate v5をpush。公開首位`.768`、5,532チーム。[benchmark log](experiments/2026-11-12-baseline-benchmark-push.md)。
- 2026-11-12: v5でSVC cross-version gateはmax abs差0.0で通過。非量子化QwenへのPEFT LoRA loadがKaggleのtorchao 0.10.0で失敗する既知issueを確認し、optional TorchAO dispatchのみ無効化するprivate v6をpush。remote privacy・GPU・offline・inputsを確認。[benchmark log](experiments/2026-11-12-baseline-benchmark-push.md)。
- 2026-11-12: v6でSVC互換性とPEFT LoRA loadは通過したが、実割当てT4の14.56 GiB GPUでQwen8 SDPA inference probeがOOM。9時間runtime gateは未測定。baseline変更前に報告し、構成は維持。[benchmark log](experiments/2026-11-12-baseline-benchmark-push.md)。
- 2026-11-12: Kaggle official CLI docsの`NvidiaL4X1` acceleratorでv7をpush（blend/inference code不変）。remote pullはprivate/L4X1を示した一方`enable_gpu=false`で、CLI metadataと実行設定が不一致の可能性。次回scheduled statusで確認。[benchmark log](experiments/2026-11-12-baseline-benchmark-push.md)。
- 2026-11-12: Kaggle検索でAreeb Aliの0.684 public Notebook mirrorを発見。version/sourceとscore帰属に不一致があり、現leader`.765`も下回るため(c)保留。baseline CV-LB確認後にsource/version・OOF complementarityを照合する。[audit](experiments/2026-11-12-public-0684-notebook-audit.md)。
- 2026-11-12: “The Prompt Is Not the Author” v32は直近weight変更が未採点で、同著者のModernBERT追加もpublic scoreを低下させたとの報告。自前の同系候補screenとも一致するため(b)試さない。[audit](experiments/2026-11-12-prompt-is-not-author-audit.md)。
- 2026-11-12: benchmark Notebookのruntime projectionがinteractiveの3行をhidden全件として扱う問題を修正。公式Data Descriptionの約4,000行を下限にし、v1のprobe値は正しい4,000行へ再計算して使う。[benchmark log](experiments/2026-11-12-baseline-benchmark-push.md)。
- 2026-11-11: README整理時に抜けた完了済みマイルストーン5件を復元し、履歴アーカイブの相対リンクと監査・継続ログの重複を修正。
- 2026-11-11: 当日公式情報を再確認し、leaderboard/top/team count、締切差異、提出条件を[日付ログ](experiments/2026-11-11-official-competition-status.md)に保存。
- 2026-11-11: Qwen3-1.7B final fitのexit 0、採用ゲート通過、GPU0解放とbundle checksum一致、およびMistral03 fold3/4 checkpoint・fold4完了・confirmation error・Qwen8B pilot通過とfinal-fit進捗を[継続ログ](experiments/2026-11-11-host-continuation-poll.md)に記録。「現在の状況」を20行以内に整理し、過去の詳細は日付履歴に保持。
- 2026-11-11: Qwen3-8B final fit完了後、source bundle checksumを確認し、Qwen8/Qwen17/SVCとaggregate asset manifestを`sha256sum -c`で検証してprivate Notebook assetsへstaging。Qwen17 manifestの`./` prefixを相対パスへ正規化。Kaggle upload/submitは未実施。次は同一構成Notebookのruntime gate。
- 2026-11-11: Kaggle CLIにcredentialがなく、Kaggle MCPの`datasets.get`も拒否され、private asset Datasetを作成できないことを確認。認証情報自体は調べず、環境変数・標準credential fileの有無だけを確認。remote upload/push/submissionは未実施。詳細・再開先は[継続ログ](experiments/2026-11-11-host-continuation-poll.md)。
- 2026-11-10: 承認済み運用改訂に合わせ、現在の状況を現best・基準blend提出方針・host状態・blockerに整理。過去の時刻・PID・資源状況は[継続ログ](experiments/2026-11-10-host-continuation-poll.md)と[状況履歴](experiments/2026-11-10-readme-current-situation-history.md)に保持。
- 詳細な更新履歴は[2026-11-10アーカイブ](experiments/2026-11-10-readme-update-history.md)に保存。
- 現在の状況の旧記録は[状況履歴](experiments/2026-11-10-readme-current-situation-history.md)、共同作業の旧引き継ぎは[引き継ぎ履歴](experiments/2026-11-10-readme-handoff-history.md)を参照。
- 2026-11-12: specの改訂節を優先し、「現在の状況」を20行以内の現best・実行中benchmark・次の確認に更新。v8 push前公式確認、remote設定、初回状態を日付付きexperimentsログへ追記し、詳細なhost診断は継続ログへ保持。
- 2026-11-12: 改訂specに従い「現在の状況」を現best・基準blend再提出の採点待ち・次のpollへ整理。旧提出失敗とv10診断の詳細はbenchmark logに保持。
- 2026-11-12: 基準blend v9の2提出がhidden rerunで同じunhandled errorとなり、どちらもscoreなし。Kaggle公開kernel logとartifact取得可否を確認し、stack trace未取得・hidden入力整合を第一仮説として記録。構成は未変更。[benchmark log](experiments/2026-11-12-baseline-benchmark-push.md)
- 2026-11-12: official data descriptionに沿って、hidden testのID/行数を出力の正本にするprivate Notebook v11を作成・synthetic 4,000行で検証してpush。kernelは`RUNNING`、次回statusは30分後。[benchmark log](experiments/2026-11-12-baseline-benchmark-push.md)
- 2026-11-12: 公開Leaderboard首位の公開NotebookをKaggle CLIで検索。コンペfilter付きuser queryは`Not found`で、再現可能sourceがないため(b)試さないと索引化。[監査](experiments/2026-11-12-current-leader-public-notebook-search.md)
- 2026-11-12: private path-only control v2 ref`58259844`はhidden scoring完了、constant-class diagnostic public score`.055`。train/template・path仮説を踏まえてbaseline v12ではモデルとblendを維持し入力依存のみ修正。[benchmark log](experiments/2026-11-12-baseline-benchmark-push.md)
- 2026-11-12: Mistral固定1/4追加＋凍結Spectralのprimary screenがBA`.689791`でCI・class-retention gateを通過。primary-onlyのため独立confirmationを次段階とし、候補化・提出は未実施。[screen log](experiments/2026-11-12-mistral-spectral-complementarity-screen.md)
- 2026-11-12: Mistral＋Spectralのprimary-only small-prompt shape screenを20 seedsで実施。uniform m=2/3とも平均deltaが正で、positive replicate率は`.80`/`1.00`。shape flagを通過し、独立確認候補として優先度を上げたが、Host142 gateとconfirmation前の採用・提出はなし。[screen](experiments/2026-11-12-mistral-spectral-small-prompt-shape-screen.md)
- 2026-11-12: DeBERTa primary OOFの定刻pollでfold4 epoch2完了を確認。GPU2の別compute processはそのまま、次pollは21:24 JST。[run log](experiments/2026-11-12-deberta-v3-large-pilot-primary.md)
- 2026-11-12: DeBERTa独立確認用の登録fold、baseline OOF、Spectral OOFが2,699 IDs/150 promptsで整列し、prompt漏洩なしと読み取り確認。DeBERTa primary通過後の入力待ちを解消。[run log](experiments/2026-11-12-deberta-v3-large-pilot-primary.md)
- 2026-11-12: Toyns Freg ModernBERT v2 validation Notebookを静的監査。単一grouped holdoutと実行出力のないsourceのため(b)試さない。[audit](experiments/2026-11-12-toynsfreg-modernbert-v2-audit.md)
- 2026-11-12: Zhihao HuanのNTL 0663 V31 ATLAS20をmetadata確認。title`.663`と大規模外部依存のため(b)試さない。[audit](experiments/2026-11-12-zhihaohuan-0663-v31-atlas20-audit.md)
- 2026-11-12: Discussion 754860のQwen3-14B-Base `.620` Public / `.622` CV報告を追跡。評価・学習provenance不明でNotebook検索も該当sourceなしのため(b)試さない。[audit](experiments/2026-11-12-osakanateishoku-qwen14b-base-audit.md)
- 2026-11-12: primary-only Mistral+Spectral composition向けに、既存のshuffle GroupKFold confirmation split・固定transform・gateを明記した独立確認specを追加。実行はMistral confirmation OOFとHost142 GPU1 gate通過後。[spec](specs/2026-11-12-mistral-spectral-complementarity-confirmation-spec.md)
- 2026-11-12: Kirill Tymchishin v18 close-pair ruleを固定条件でscreenし、適格pair1組・予測変更なし・BA差0で棄却。公開監査を(b)試さないで完了。[audit](experiments/2026-11-12-kirill-close-pair-audit.md)
- 2026-11-12: “From 0.684 toward top 1%” Discussionを監査し、再現可能な候補手法がないため(b)試さない。監査時点では基準v12のruntime gateと採点提出で確認中だったが、その後15:51 JSTに採点成功（Public`.541`）を確認。[audit](experiments/2026-11-12-top1-validation-discussion-audit.md)
- 2026-11-12: Host141 GPU2 owner process advanced to PID 3148080 (`ogata`, `token_aux/sample_text_only.py`), 6,093 MiB/100%; left untouched. Host142 strict host-key verification still fails.[host log](experiments/2026-11-12-host-continuation-poll.md)
- 2026-11-12: 固定Qwen3-8B 1/4追加＋Spectralをprimary/independent confirmationでscreen。両方deltaは正だがpaired CI下限が0以下で候補を棄却。source checksum一致、CPU出力のみ。[screen](experiments/2026-11-12-qwen8b-spectral-complementarity-screen.md)
- 2026-11-12: 固定Qwen3-1.7B 1/4追加＋Spectralをprimary/independent confirmationでscreen。両splitでdeltaが負、CIも0未満のため棄却。source checksum一致、CPU出力のみ。[screen](experiments/2026-11-12-qwen17b-spectral-complementarity-screen.md)
- 2026-11-12: 固定4-view SVC 1/4追加＋Spectralをprimary/independent confirmationでscreen。両splitで正のdeltaだがpaired CI下限が0以下のため棄却。source checksum一致、CPU出力のみ。[screen](experiments/2026-11-12-4view-svc-spectral-complementarity-screen.md)
- 2026-11-12: 固定Prompt-centered Twin SVC 1/4追加＋Spectralをprimary/independent confirmationでscreen。両splitで正のdeltaだがpaired CI下限が0以下で棄却。source checksum一致、CPU出力のみ。[screen](experiments/2026-11-12-prompt-centered-twin-spectral-complementarity-screen.md)
- 2026-11-12: CHEN HanのWeMM4 fivefold LoRA componentを監査。公開OOF参照はBA`.621`だが現在の登録splitと一致せず、元dataset/licenseと外部pool provenanceも取得できないため(c)保留。再学習・利用は開始しない。[audit](experiments/2026-11-12-wemm4-expanded-lora-component-audit.md)
- 2026-11-12: RanJeetのWEMM ensemble Notebookを静的監査。Kaggle session COMPLETEは3行FAST_COMMITでconstant出力とsmokeのみ。OOF/scoreの根拠がなく、full stackは(b)試さない。[audit](experiments/2026-11-12-ranjeet-nov12-wemm-notebook-audit.md)
- 2026-11-12: DeBERTa primary OOFのHost141定刻pollでfold1への進行を確認。GPU2の別ユーザーjobには触れず、次のpollを19:54 JSTに設定。[run log](experiments/2026-11-12-deberta-v3-large-pilot-primary.md)
- 2026-11-12: DeBERTa primary OOFの定刻pollでfold2 epoch1を確認。GPU2の別ユーザーjobには触れず、次のpollを20:24 JSTに設定。[run log](experiments/2026-11-12-deberta-v3-large-pilot-primary.md)
