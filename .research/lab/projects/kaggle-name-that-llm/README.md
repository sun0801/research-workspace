---
project: kaggle-name-that-llm
status: active
summary: pool weight 0.10のprompt-centered SVCをOOF比較baselineとして採用。weight 0.05、family-local residual、family-mass rerank、固定SVC blendはゲート未通過。Qwen02/04はfold1学習中。
created: 2026-11-02
last_updated: 2026-11-07
---

# Kaggle — Name That LLM

## 概要

18種類のLLMの生成文章からモデル名を識別するコンペ。ユーザーは主に方針・制約を伝え、AIが調査・記録・承認済み範囲の実装を担当する。知見と作業履歴をMarkdownで共有して会話をまたいで再開する。

- [公式コンペ](https://www.kaggle.com/competitions/name-that-llm)
- [コードの作業場所](../../../../../kaggle/name-that-llm/README.md)
- [環境・認証・操作ガイド](../../../../../kaggle/README.md)

## 現在の状況

- 実装・データ・環境はResearch Workspaceの外の `/mnt/HDD10TB-2/aburatani/kaggle/`、研究記録はこの `.research/` に置く。2026-11-02のユーザー指摘に合わせて移設済み。

- 公式Kaggle CLI 2.2.5を `/mnt/HDD10TB-2/aburatani/kaggle/.venv/` に導入し、`uv.lock` で依存を固定。
- 公式MCPへ接続。ローカルの収集ツールとCodexのネイティブツールの両方で概要取得に成功。
- トークン認証後、収集9項目すべて成功。Notebook人気/新着とデータファイル一覧も取得できた。一覧は先頭ページ。
- 有力Discussion 4件と公開Notebook 3本を精読。Starter v4 / Two-stage LoRA v2 / nlm-v27 v1と取得コードの一致を確認。コードは未実行。
- 比較では、Starterのprompt-grouped CV、二段階LoRAの再現条件、nlm-v27の有効構成・時間制約・CV上の注意を整理。CPU基準の次に8Bを検討する順を提案。
- APIトークンでローカルMCPクライアントと公式CLIの認証付き取得を確認。この会話のネイティブMCP接続は再接続後の認証確認が必要。
- CPU自動実験はbaseline＋5候補を完了。固定prompt-grouped 5-foldで、baseline OOF BA=0.3144792443450161、最良の大文字保持・句読点・shape・functionの4-view TF-IDF＋Logistic Regressionは0.3845041014168531（+7.00ポイント）。全完了CVのfoldが収束し、独立検査pass。
- 最良configの再CVで2,699行のOOF全列・score配列が完全一致。全trainでfitしたモデルを保存し、別workerでの再load推論と提出形式の整合性も確認した。公開test 3件のローカル出力で、Kaggleへは送信していない。性能改善は探索用CV上の結果で、未使用holdout/Private LBでは未確認。
- 16:53 JSTのユーザー指示による中断は履歴と時間を保持し、16:57 JSTの再開指示後に同一configから再開。runnerの明示再開処理を検証する6テストが成功。累積実験403.896秒 / 7,200秒、最大RSS 1.675GiB / 32GiB、最小MemAvailable 206.224GiB / 下限16GiB。候補数上限で探索を終了し、実験プロセス不在を確認。[最終比較・成果物・再実行コマンド](experiments/2026-11-06-cpu-cycle-results.md)を最新の入口とする。
- GPU段階の141/142選定条件も診断記録へ保存。初回specはCPUのみで、GPU学習・提出は未実施。
- 2026-11-06開始の承認済みGPU goalで、公式Leaderboardを再確認しtop 0.747を確認。142 GPU1は空き31,929 MiB・計算プロセスなし。Open Pool v15の監査と候補01 configに加え、foldwise prompt除外・2,500/class pool audit/assert・primary/confirmation split・checkpoint/resume・直前GPU preflightを備えたGPU runner、prompt-cluster bootstrap採否解析runner、confirmation分割のCPU基準runnerを構文準備し、同一split baseline OOF BA 0.373768を既存cycle外へ保存した。候補専用Python 3.12.3の空venvは作成済みだが、依存・重み・pilot、Qwen OOF、Notebook提出は未実施。Codex 5時間利用枠とKaggle GPU週間枠は未確認のため長時間処理は開始しない。詳細と再開先は[GPU自動実験の開始時確認と候補01](experiments/2026-11-06-gpu-autonomous-initial-check.md)。
- 20:26 JST継続監査で、LoRA層数とschedulerがpreregistered設定を反映していなかった不整合を修正。runnerに24層LoRA、cosine＋0.1 warmup、scheduler checkpoint/resume、およびconfig非対応値のpreflight前拒否を実装し、Open Pool pathをversion/filenameから解決するよう更新。`py_compile`と依存非導入状態でのisolated config validatorが成功。現hash・根拠・制約は上記実験ログを参照。5時間利用枠のgetterはagent toolに見当たらず、依存導入・重み取得・GPU pilotは引き続き未開始。
- 20:32 JSTに、primary/confirmation双方のOOF採用後のみ実行できるall-train final-fitと、adapter/tokenizer/head/metadata/local predictionを一時bundleから確定する経路を追加。全train prompt除外後もOpen Poolが最低3,541件/class残ることを確認。まだOOF・pilot・fitは未実施。詳細は実験ログ参照。
- 21:58 JSTユーザー再開後の監査で、KaggleのQwen3-8B post-trained v1とファイル名/サイズが一致する完全なHF cacheを確認。Base候補とは分離して、同一条件比較用の未実行candidate02 configを事前登録。依存不足と利用枠未確認のため、GPU実行はまだ保留。詳細は実験ログ参照。
- 22:31 JSTに指定ガードは5時間90%、週間81%でpass。候補02 primary OOFのPID 2827674はGPU1上で継続中、A4000は未使用。runnerはepoch完了時のみログ・checkpointを書き、fold0 stage1は45,000例のためpilot時間からは初回checkpointまで約19時間と概算（実測ではない）。途中経過の無出力だけでは異常と判断しない。公式状態・新規公開知見・外部spec差分は[実験ログ](experiments/2026-11-06-gpu-autonomous-initial-check.md)を参照。
- 22:29 JSTの公開知見確認では作者報告Public LB 0.672+の複合SVC/LoRA/ATLAS手法と別stackのnested CV 0.6865対Public LB 0.56を確認。現candidate02実行条件は維持し、次候補はOOF・誤り分析後に選ぶ。Open Pool v15の説明はcompetition dataを含まないと記載。新規Discussionの第三者LLM送信に関する投稿は主催者の回答ではないため、公式判断と扱わない。詳細は実験ログ参照。
- 22:33 JSTにDiscussionの新しい作者報告を確認: Qwen3-8B LoRA + Open Pool v10はOOF 0.6224 / Public LB 0.628、ModernBERTの同thread報告は0.616 / 0.575。公開値・分割・データversion差を踏まえ、進行中candidate02を継続。出典と制約は[実験ログ](experiments/2026-11-06-gpu-autonomous-initial-check.md)。
- 22:35 JSTにprompt-dependent blendのtest-like validationに関する別返信を精読。m=2 OOFは全15件でPublic LBと正相関した作者報告だが、候補選択後5件では予測不能、選択biasや1外れ値に依存する弱いsanity signal。単体分類器のprimary採否条件は変更せず、将来の同一prompt依存postprocess候補のみsimulation時に参照する。詳細は[実験ログ](experiments/2026-11-06-gpu-autonomous-initial-check.md)。
- 22:36 JSTにOOF proxy選択biasとLB noiseの公開simulation discussionを確認。単一OOF cutの相関で候補を選ぶと楽観biasが入り得るため、prompt bootstrapとconfirmation splitを維持し、Public LBでの順位付けを過剰解釈しない。詳細は[実験ログ](experiments/2026-11-06-gpu-autonomous-initial-check.md)。
- 22:38 JSTに公開NotebookのOOF leakage事例を確認。full-train community LoRAをvalidationへ流用した0.913はleakageであり、OOF候補ごとにfold内でfitする要件を再確認。candidate02はfold内でadapter/headをfitし、validation promptsをpool/train双方から除く設計。詳細・作者の近似LB-noise推算の制約は[実験ログ](experiments/2026-11-06-gpu-autonomous-initial-check.md)。
- 22:52 JSTに候補01のQwen3-8B-Base重みを公開HFの固定revisionから取得。5つのshardすべてでSHA-256一致を確認。Kaggle variationとのファイル名・サイズ一致は確認したが、Kaggle側hashがないため同一byte列とは未確認。candidate01 configは`preregistered-not-run`のままで、GPU1のcandidate02 primary OOFと並行する学習は開始しない。詳細は[実験ログ](experiments/2026-11-06-gpu-autonomous-initial-check.md)。
- 23:31 JSTに候補03 Mistral-7B v0.1の固定HF revisionから必要ファイルを取得し、2 safetensors shardのSHA-256を両方照合。configはpreregistered-not-runを維持し、pilot/学習は未実施。候補02と同じGPUで競合させず、141のA4000は安全条件不足のため、後続pilotはGPUが空いてから判断する。詳細は[実験ログ](experiments/2026-11-06-gpu-autonomous-initial-check.md)。
- 2026-11-07 00:03 JST時点で候補02 Qwen3-8B post-trained primaryはGPU1で継続（elapsed約1:40、OOF/checkpointなし）。候補04 Qwen3-1.7B primaryはGPU0で起動し、pilot peak 3,672 MiB / reserve後の上限7,636 MiBでpass。HF固定revision・weight hash一致。両候補は別GPU UUIDを使用し、同じprompt-grouped fold・Open Pool v15条件。結果未確定。[実験ログ](experiments/2026-11-06-gpu-autonomous-initial-check.md)。
- 2026-11-07 00:47 JSTにOpen Pool v15 4-view LinearSVC候補のprimary OOFをCPU-onlyで開始。candidate config hash `a4c66799...`、runner hash `d32013a9...`。保存済みprimary GroupKFold、exact text除外、char/word prompt match閾値0.40、均等2,500件/class pool sample、sample weight 0.35を設定。00:51時点でfold0 BA 0.431481（同じfoldのCPU baseline 0.359259）、fold1実行中。1/5 foldの値なので候補採否は未確定。[候補計画](experiments/2026-11-07-openpool-svc-candidate.md)・[実験ログ](experiments/2026-11-06-gpu-autonomous-initial-check.md)。
- 2026-11-07 01:30 JSTにcandidate SVCが独立confirmation splitでも再現。OOF BA 0.433403、同一split baseline 0.373768、差+0.059635。prompt 150群paired bootstrap（2,000回、seed 42）95% CIは[+0.038510, +0.079283]。primary/confirmationとも採用条件を通過。fold summaryのconverged項目欠落も修正し、両splitの収束状態を記録。[実験ログ](experiments/2026-11-06-gpu-autonomous-initial-check.md)。
- 2026-11-07 05:05 JSTにconfirmation SVC混同行列を分析し、全誤りの50.36%が同じprovider family内と確認。公開family-gating手法を着想源に、第三者adapter/API生成データを使わないhierarchical SVCを同一pool/split条件で事前登録し、2-thread CPU primary OOFを開始。GPU候補02/04は別々のGPU UUIDで継続、両方ともepoch checkpoint未作成。詳細・再開先は[階層型候補plan](experiments/2026-11-07-openpool-hierarchical-svc-candidate.md)と[実験ログ](experiments/2026-11-06-gpu-autonomous-initial-check.md)。
- 2026-11-07 06:00 JST確認でLeaderboard topは0.747。Rules: 日次5提出・最終2件、Notebook CPU/GPU各9時間、Internet無効。GPU02はfold0 stage2 epoch1 checkpoint保存済み、GPU04とnested family-mass rerank primaryは継続中。Timelineの保守期限は2027-01-13 23:59 UTC。[family-mass spec](specs/2026-11-07-openpool-family-mass-rerank-spec.md)・[実験ログ](experiments/2026-11-06-gpu-autonomous-initial-check.md)
- 2026-11-07 06:12 JSTに公開Notebookのscore出所を追加監査。著者は自身の0.669と、一部0.672 forkの非公開SVC依存を説明。付属CC BY 4.0 API生成データは著者の旧stackで成績を下げた報告があり、現候補へ混ぜず独立評価に保留。GPU02/04とfamily-mass primaryは継続。[実験ログ](experiments/2026-11-06-gpu-autonomous-initial-check.md)
- 2026-11-07 06:16 JSTにfamily-mass rerank primary outer fold0完了（BA 0.416667, α=0.75）。同fold flat SVC 0.431481を下回るが、primary全5foldを完了してから採否を判定。workerはfold1へ移行し、安全条件内。[family-mass spec](specs/2026-11-07-openpool-family-mass-rerank-spec.md)
- 2026-11-07 06:22 JST、GPU02 fold0 stage2はepoch2までcheckpoint更新、GPU04もfold0 stage1 epoch1の初回checkpointを保存。family-mass候補はfold1で継続。MemAvailable約200 GiB、利用枠ガードpass。[実験ログ](experiments/2026-11-06-gpu-autonomous-initial-check.md)
- 2026-11-07 06:33 JSTに利用枠ガードを再確認（5時間86%、週75%）。Qwen候補02はfold0 OOF BA 0.544444でfold1へ、候補04はfold0 stage2 epoch1まで進行。family-mass rerankはfold1継続、tree RSS約4.23 GB・MemAvailable約198 GiB。いずれもprimary 5-fold未完了で採否保留、Kaggle提出なし。[実験ログ](experiments/2026-11-06-gpu-autonomous-initial-check.md)
- 06:35 JSTにfamily-mass rerank fold1完了（BA 0.405556, α=0.50）、primary fold2へ。累積2/5 foldのため採否は保留。[family-mass spec](specs/2026-11-07-openpool-family-mass-rerank-spec.md)
- 06:42 JSTの監視で5h/週ガードはreset後100% pass。GPU02/04のprocessとGPU使用を再確認、CPU family-mass fold2も継続しRAM余裕あり。Kaggle提出なし。[実験ログ](experiments/2026-11-06-gpu-autonomous-initial-check.md)
- 06:50 JSTにQwen候補04 fold0がBA 0.518519で完了しfold1へ。候補02 fold0は0.544444。どちらもprimary 1/5のため採否保留。Family-mass rerank fold2はRSS約4.00 GiB、MemAvailable約196 GiBで継続。[実験ログ](experiments/2026-11-06-gpu-autonomous-initial-check.md)
- 06:52 JSTの資源監視でGPU02/04とCPU rerankは継続、CPU MemAvailable約198 GiB。ガードは5h97%・週100%でpass。fold0以降の新checkpointはまだなく、各候補を停止・再起動せず継続。[実験ログ](experiments/2026-11-06-gpu-autonomous-initial-check.md)
- 06:57 JSTにfamily-mass rerank fold2 BA 0.422222（flat同fold 0.416667、差+0.005556）で完了しfold3へ。fold0/1との差は負、3/5 foldのため採否保留。Leaderboard topは0.747のまま。[実験ログ](experiments/2026-11-06-gpu-autonomous-initial-check.md)
- 07:02 JST資源確認でGPU候補02/04・CPU rerankは継続。GPU compute processとPID対応を確認、CPU MemAvailable約197 GiB、利用枠ガード97%/99%でpass。新checkpoint待ち。[実験ログ](experiments/2026-11-06-gpu-autonomous-initial-check.md)
- 07:12 JSTもGPU02/04とfamily-mass fold3が継続。GPU utilization/compute PIDを確認し、MemAvailable約196 GiB、rate guard 96%/99%でpass。新checkpointはまだなし。[実験ログ](experiments/2026-11-06-gpu-autonomous-initial-check.md)
- 07:19 JSTにfamily-mass rerank fold3完了（BA 0.475926, α=0.75）。同fold flat SVC比+0.005556、primary fold4へ。4/5 foldsのpaired CIは未算出。[family-mass spec](specs/2026-11-07-openpool-family-mass-rerank-spec.md)
- 07:22 JSTにGPU02/04・CPU fold4の継続を確認。2候補のGPU fold0はflat SVCを上回るが各1/5。Kaggle 9h上限に向け、採用候補のT4互換エンドツーエンドruntime実測を提出前ゲートとして明記。[実験ログ](experiments/2026-11-06-gpu-autonomous-initial-check.md)
- 07:28 JST公式Leaderboard topは引き続き0.747。CPU rerank fold4継続、MemAvailable約198 GiB、利用枠95%/99% pass。GPU候補はfold1の実行継続中。[実験ログ](experiments/2026-11-06-gpu-autonomous-initial-check.md)
- 07:32 JSTの監視でGPU02/04とCPU fold4が継続、GPU使用率37%/28%、MemAvailable約197 GiB、ガード95%/99% pass。checkpoint待ち。[実験ログ](experiments/2026-11-06-gpu-autonomous-initial-check.md)
- 07:46 JST family-mass rerank primary完了: BA 0.434154 vs flat SVC 0.433776、prompt-paired 95% CI [-0.007778, +0.008534]（2,000 replicates）。下限が0を超えないためspecの規則で不採用、confirmationは実施せず。分析結果は[専用artifact summary](../../../../../kaggle/name-that-llm/artifacts/cpu-openpool-family-mass-rerank-v15-retry1/primary-comparison-flat-svc/summary.json)と[manifest](../../../../../kaggle/name-that-llm/artifacts/cpu-openpool-family-mass-rerank-v15-retry1/primary-comparison-flat-svc/analysis-manifest.json)に保存。Qwen候補02/04は継続中。[実験ログ](experiments/2026-11-06-gpu-autonomous-initial-check.md)
- 公式Evaluation pageはhidden testのモデル別件数が均等でなく、Public/Privateのmixが異なると明記。test prompt群に18モデル1件ずつを課す制約は採用しない。[実験ログ](experiments/2026-11-06-gpu-autonomous-initial-check.md)
- 08:38 JST公式状態確認でLeaderboard topはLe Viet/Hod Carriersの`.747`同点。公式metadata deadline Jan 14、Timeline final deadline Jan 13 23:59 UTCのためJan 13を採用。日次5提出・最終2件、Notebookのみ、9時間以内、Internet off、hidden test各class件数不均等。
- 公開Notebook `ozertuu/0-672-dual-svc-better` v9のprompt-centered stylegram SVCは、著者報告OOF BA`.423`→`.435`。この単独寄与は自己申告として扱い、4-view Open Pool SVCでprompt-ID-freeのtext clusterを使う別候補を事前登録。[候補spec](specs/2026-11-07-openpool-prompt-centered-twin-spec.md)
- 08:49 JSTにprompt-centered twin primaryを2-thread CPU・resource guard付きで開始。初回fold0はSciPy sparse subtractionの非broadcast shape errorで失敗したため、そのfold logと旧runnerを保存。修正版を別`retry1` artifactで再開し、primary fold0 BA`.448148`、同fold flat SVC`.431481`（差`+.016667`）。single-fold探索値のため採否根拠ではない。text-only cluster推定は45群/540行、9 singletonで、validation prompt IDは予測に使っていない。fold1へ継続。
- 08:57 JSTのrate guardは5h`90%`/week`98%`でpass。GPU02/04はfold1でalive、util`27%`/`34%`、VRAM`15,835`/`3,907 MiB`、MemAvailable約`187 GiB`; 新checkpointなし。prompt-centered CPU workerはfold1で継続、前foldの最大RSSは約`13.2 GiB`で32 GiB上限以内。Kaggle提出なし。[実験ログ](experiments/2026-11-06-gpu-autonomous-initial-check.md)
- 09:06-09:07 JST prompt-centered retry1 primary fold1完了、BA`.429630` vs 同fold flat SVC`.416667`（差`+.012963`）。fold0/1がともに改善だが2/5のみで採否保留、fold2へ移行。GPU02/04はfold1で継続しutil`31%`/`26%`、VRAM`15,835`/`3,907 MiB`、MemAvailable約`197.6 GiB`; 新checkpointなし。[実験ログ](experiments/2026-11-06-gpu-autonomous-initial-check.md)
- 09:15 JST prompt-centered retry1 primary fold2完了、BA`.470370` vs flat SVC`.416667`（差`+.053704`）。最初の3/5 foldは差がすべて正。fold3へ移行、採否保留。[実験ログ](experiments/2026-11-06-gpu-autonomous-initial-check.md)
- 09:23 JST prompt-centered retry1 primary fold3完了、BA`.509259` vs flat SVC`.470370`（差`+.038889`）。4/5 foldすべてで差が正。最後のfold4実行中で、採否は全OOFのprompt-paired bootstrap後。[実験ログ](experiments/2026-11-06-gpu-autonomous-initial-check.md)

## マイルストーン

- [x] Kaggle共通ディレクトリとName That LLMプロジェクトを作成
- [x] 公式CLI・MCP設定・収集コマンドと共同作業スキルを整備
- [x] 初期のコンペ調査と有力資料の知見を保存
- [x] 公開Notebook 3本の精読と手法・検証条件・計算資源の比較を保存
- [x] 承認済みCPUサイクルのbaseline＋5候補、最良再CV、全件fit、保存モデル再推論、比較報告を完了

## 調査・判断の索引

- [初期調査と資料台帳](experiments/2026-11-02-competition-intelligence.md)
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

## 共同作業の引き継ぎ

ユーザーの希望: Kaggleコンペを複数管理したい。今回はNameThatLLM。基本作業はAIへ委ね、各タブの有力資料から知見を蓄積し、情報共有・指示出し・自動化を整える。

現時点の前提: チャット＋Markdownを入口にし、資料の主張・AIの推測・自分たちの実測を分ける。公開LB先頭超えを目指す承認済み自動実験goalがactive。試行数・累積GPU時間の固定上限はなく、prompt-grouped比較、利用枠15%ガード、GPU/RAM安全条件、提出制限、Kaggle作成物privateのspecを守る。現在までKaggle提出は行っていない。

CPU baseline cycleは完了し、既存成果物を保持する。正本cycleは `name-that-llm/artifacts/2026-11-06-cpu-cycle`、最良configは `configs/05-function-view.json`、最終モデルは `09-05-function-view-candidate/model.joblib`。`src/cpu_finalize.py --cycle ...`で既存成果物を再検査でき、cycle内`reproduce_cycle.sh`には新規cycle向けの全再実行コマンドを保存。追加の自動実験は承認済みGPU goalの範囲で別artifact/configに記録する。

## 更新履歴

| 日付 | 内容 |
|---|---|
| 2026-11-02 | ユーザー依頼で新規作成。共通環境・公式MCP・調査ツール・スキル・初期調査を追加。 |
| 2026-11-02 | ユーザー指摘を受け、実装・実行環境を隣の `/mnt/HDD10TB-2/aburatani/kaggle/` へ移設。参照・共有スキル・仮想環境を修正。 |
| 2026-11-02 | APIトークン認証と収集9項目・公開コード3本の取得を確認。 |
| 2026-11-02 | 公開Notebook 3本のversionと全セルを照合・精読し、主要依存のメタデータ・計算資源・検証の注意点を比較記録。実験は未実施。 |
| 2026-11-05 | CPU自動実験の合意内容をspecへ保存。goal指示文を用意し、開始前の状態を記録。 |
| 2026-11-06 | 公式データ取得とCPU runner実装を確認。修正後の5テストが成功。実学習未開始の状態で、新規CLI用の引き継ぎとgoal文を保存。 |
| 2026-11-06 | CPU baseline CVと独立検査が成功（OOF BA 0.314479）。候補1実行中にユーザー指示で停止し、プロセス不在・累積69.276秒・再開位置を保存。 |
| 2026-11-06 | ユーザーの再開指示後、baseline＋5候補を完了。最良4-view＋LRのBA 0.384504、再CVのOOF/score完全一致、全件fit・保存モデル再推論・最終検査pass。比較報告と再実行コマンドを保存。 |
| 2026-11-06 | GPU自動実験goalを開始。公式LB top 0.747、期限、日次提出履歴、142のGPU/RAMを確認。Open Pool v15を取得・監査し、Qwen3-8B-Base候補01を保存。継続監査でLoRA層数・cosine schedulerの不整合を修正し、config validator、version駆動pool path、OOF採用ゲート付きall-train final-fit/bundle経路を追加。再開後にcomplete Qwen3-8B post-trained HF cacheを確認し、候補02を事前登録。5時間利用枠が未確認のためGPU pilot待ちとして記録。 |
| 2026-11-07 | 候補02 Qwen3-8B primary OOFをGPU1で継続し、候補04 Qwen3-1.7Bの固定revision取得・pilotを通過後にGPU0でprimary OOF開始。両候補のprompt-grouped評価と資源監視を継続。 |
| 2026-11-07 | Open Pool v15 4-view SVC候補を事前登録し、resource guard付きCPU-only primary OOFを開始。 |
| 2026-11-07 | SVC primary/confirmation OOFでbaseline比+0.049272/+0.059635、両prompt bootstrap 95% CIが正。独立splitで再現。GPU候補02/04を継続。 |
| 2026-11-07 | Confirmation SVC誤分類の半数がprovider family内と判明。事前登録したhierarchical SVC primary OOFをCPU-onlyで開始。 |
| 2026-11-07 | Hierarchical SVC primary BA 0.406358。flat SVCに対するprompt-paired bootstrap差の95% CIが全域で負のため候補不採用、confirmationは省略。family-mass-preserving rerank specを用意し、GPU候補02/04を継続。 |
| 2026-11-07 | nested family-mass-preserving rerankを2-thread CPUで開始。sparse matrixの長さ取得例外を修正し、別retry1 artifact dirでprimaryを再開。GPU候補02/04の稼働とRAM/GPU条件を再確認。 |
| 2026-11-07 | 06:00 JSTに公式Leaderboard/Rules/Timeline/Code Requirements再確認。top 0.747、GPU02 fold0 stage2 epoch1 checkpointを確認。family-mass rerank primaryは継続中、Kaggle提出なし。 |
- 07:54 JST再開後、レートガードpass（5h 93% / week 99%）。公式Leaderboard topは0.747同点、保守期限は2027-01-13 UTC。Qwen候補02/04はGPUでfold1継続、fold0 BAは.544444/.518519。両候補の全fold完了前に採否を決めず、family-mass rerankはCI下限が0未満のため棄却済み。新規提出なし。[実験ログ](experiments/2026-11-06-gpu-autonomous-initial-check.md)
- 08:07 JSTのCPU tokenization診断では、Open Pool各label 500件（計9,000文）の平均token長145.2/384、固定長paddingで有効tokenは37.8%だった。実行時間短縮率は未測定。GPU OOFを保全し、dynamic paddingは採用候補の9時間runtime検証時に別runnerで評価する。[実験ログ](experiments/2026-11-06-gpu-autonomous-initial-check.md)
- 08:12 JST、Qwen候補02/04と採用SVCのfold0 OOFをID/ラベル/プロンプト/fold/class順で整列確認。固定temperature 1の等重みsoftmax融合はQwen8B+Qwen1.7B+SVCでBA .564815（各単体.544444/.518519/.431481）。fold0を見た候補選定なので探索値としてのみ扱い、固定手法のprimary/confirmation採否ゲートをspec化。[融合spec](specs/2026-11-07-qwen-svc-probability-ensemble-spec.md)・[実験ログ](experiments/2026-11-06-gpu-autonomous-initial-check.md)
- 08:25 JST、fold1のGPU02/04は継続し安全条件内。CPU-only等重みsoftmax融合解析器を実装し、canonical prompt-fold/ID/label/class alignmentと各base比較のpaired bootstrapを含めた。構文確認pass、未実行（Qwen primary OOFは未完了）。[解析spec](specs/2026-11-07-qwen-svc-probability-ensemble-spec.md)・[実験ログ](experiments/2026-11-06-gpu-autonomous-initial-check.md)
- 10:20 JST prompt-centered SVCがprimary/confirmationの両bootstrapゲートを通過し、次のOOF比較用候補baselineに採用。等重みQwen融合の別specを登録し、既存analyzerにmanifest candidate IDを指定できる変更を追加。Qwen02/04はprimary OOF fold0のみ完了、fold1の学習を継続中。全foldが揃うまで融合は開始しない。Kaggle提出なし。
- 10:37 JST pool weight 0.10の単一変更候補を事前登録し、2-thread CPU primary OOFを新artifact directoryで開始。Preflight MemAvailableは`210,166,168 kB`、採用済みSVC primary OOFあり。Qwen02/04は停止・変更せず並行継続。採否は採用済みprompt-centered SVCとのpaired bootstrap後に判定、Kaggle提出なし。
- 12:01 JST pool weight 0.10のSVC候補がprimary CI [+0.0248, +0.0467]、independent confirmation CI [+0.0203, +0.0415]を通過し、次のOOF比較用baselineに採用。Qwen fusion specを新baselineに合わせて更新。LB改善は未確認、Kaggle提出なし。
- 12:06 JST 0.10候補をbaselineとし、Open Pool row weightだけを0.05へ変更した固定候補のprimaryを開始。2-thread CPU、tree RSS cap 32 GiB、MemAvailable floor 16 GiB。Qwen02/04は維持、Kaggle提出なし。[spec](specs/2026-11-07-openpool-prompt-centered-very-low-pool-weight-spec.md)
- 12:46 JST 0.05候補primary BA 0.506366。0.10 baseline比+0.004432、prompt-paired 95% CI [−0.004460, +0.012970]でprimary gate不通過のためconfirmationを省略し、不採用。0.10 baselineを維持。
- 12:57 JST family-local style residualの初回OOFにvalidation-label routing漏洩を発見。初回値を無効化し、修正版を再実行。13:08 JSTの正しいprimaryはBA 0.509339、prompt-paired 95% CI [−0.001481, +0.016664]でgate不通過のためconfirmationを省略し、不採用。[spec](specs/2026-11-07-prompt-family-style-residual-spec.md)
