# README handoff history (copied 2026-11-10)

過去の「共同作業の引き継ぎ」記録をREADMEから移動して保存。本文は保持し、64桁hashは運用改訂に従い先頭8桁だけに置換した。現CPU-bestの照合は`(cd artifacts/2026-11-06-cpu-cycle/09-05-function-view-candidate && sha256sum -c model.joblib.sha256)`で行う。

## 共同作業の引き継ぎ

運用再確認・実験継続（2026-11-10 17:18 JST）: READMEの引き継ぎ節を再読し、Host141/142が空いている場合の利用可、指定hostだけの停止、停止時の成果・正確な再開位置保存→対象Kaggle job/自動投入watcher停止→GPU解放確認→明示的再利用まで予約、もう一方は継続、を今後の運用に適用する。今回は停止指示ではない。`--guard 15` は17:16:52にpass（5時間97%、週次51%）。Host141 candidate11 PID `2439031` はGPU2で継続（17:18 poll、8,549 MiB使用・40%利用率、RAM floor通過）。Host142ではMistral03 PID `603688` がGPU1で継続、Qwen14B watcher `3748103` はMistral後のGPU1 queue待機。空いているGPU0でQwen1.7B all-train final fitを17:16頃起動（PID `868177`、採用済みprimary/confirmation OOF gate、GPU初期使用183 MiB、MemAvailable約202 GiB）。Notebook/Kaggle write/submissionなし。起動後の詳細確認は[host continuation poll](2026-11-10-host-continuation-poll.md)。

運用・評価更新（2026-11-10 16:57 JST）: 「141/142を止めて」の指定hostのみ停止、成果と再開位置の記録、自動投入停止、GPU解放確認、明示的再利用まで予約、もう一方は継続、という引き継ぎ手順を継続適用する。今回は停止指示ではない。guardは16:54:22にpass（5時間枠99%、週次52%）。両hostを読み取りpollし、Host141 candidate11とHost142 Mistral03を安全域内で継続確認した。Kaggle公式は5,310チーム、LB top`.755`（James Liebel）、次点`.752`。Host141 candidate13は全5 foldを自然終了し、3基準とのOOF比較で現行Qwen+SVC blendを有意に下回ったためconfirmationせず棄却。Qwen blend独立confirmationと固定Spectral補正のconfirmationは承認済み手順で完了し両ゲートpass。candidate08の旧watcherは古いrate recordでpilotをskipして終了しているため、現在のMistral/Qwen14B登録chainに割込み・同一GPU競合を起こさず、再開時期を記録してから再投入する。詳細は当日experiment logsを参照。Notebook/Kaggle object/submissionは未作成。

運用の再確認（2026-11-10 00:12 JST）: ユーザー指示に従い本節を再読。Host141/142は空いていればKaggleに使用可。今後「141を止めて」「142を止めて」は指定ホストだけを対象にし、途中結果・正確な再開位置を保存してから対象Kaggleジョブとその自動投入経路を停止し、再投入watcher不在と対象ジョブのGPU解放まで確認する。もう一方は継続し、停止確認済みホストは明示的な再利用指示までKaggleに使わない。今回は停止指示ではないため、既存実験と登録済みキューを維持して継続する。指定のrate guardは00:12:15 JSTにpass（5時間枠98%、週次54%）。

公式更新（2026-11-10 00:18 JST）: チーム5,242、public LB topは`.752`同率、次点`.747`。締切はTimelineの2027-01-13 23:59 UTCを採用。日次5提出・最終2件、Notebook-only・offline・9時間以内・`submission.parquet`は不変。公開Notebookのscore順トップはタイトル`.681`で、公式top超えの検証可能な根拠なし。[Host continuation poll](2026-11-10-host-continuation-poll.md)。同ページのData DescriptionとEvaluationでinteractive test行数の説明が3行/1行と異なることを確認。実運用ではhidden約4,000行を対象にする。

評価準備（2026-11-10 00:28 JST）: candidate11/13の既定analyzer baselineは旧CPU BA`.384504`。現行採用SVC BA`.501934`とQwen+SVC blend BA`.586408`のOOFも各2,699行・fold0–4で、ID/prompt/fold/labelが3 baseline間で完全一致。全candidate fold完了後に各baselineとのpaired比較を取り、旧CPUのみを超えた結果で採用しない。[詳細](2026-11-10-oof-comparator-readiness.md)。

公式更新（2026-11-10 00:32 JST）: Kaggle MCPでチーム数5,242、public LB`.752`同率、次点`.747`を再確認。Timelineの2027-01-13 23:59 UTC、日次5提出・最終2件、Notebook-only/offline/9時間以内/`submission.parquet`に変更なし。[記録](2026-11-10-host-continuation-poll.md)。

最新の継続poll (2026-11-10 00:36 JST): [Host continuation poll](2026-11-10-host-continuation-poll.md)。Host142 Qwen8B fold4、Host141 candidate11 fold3/candidate13 fold4が継続中。00:26以降OOF/checkpoint更新なしだがPIDとGPU利用は継続。Host142 GPU0とHost141 GPU1が空き、残る3 GPUは登録済みrunに割当中。CPU最良model hashは00:18 pollで一致確認済み。公式LB`.752`同率（00:32更新）。

Notebook search更新（2026-11-10 00:37 JST）: DateRunでNov 9 15:11 UTCより新しい実行なし。ScoreDescending首位は引き続き`.681`タイトルであり、公式`.752`超の検証可能なscore evidenceなし。[検索記録](2026-11-10-host-continuation-poll.md)。

評価更新（2026-11-10 00:45 JST）: Host141上のcandidate11（3/5 fold）とcandidate13（4/5 fold）の部分OOFを、採用SVCおよび現在最良のQwen+SVC blendとprompt単位paired bootstrapで比較。candidate11はSVCを上回る一方blendを下回り、candidate13は両方を下回った。未完了foldの記述統計なので採用判断には使わず、全fold完了後に現行best比較と登録済みgateを適用する。[比較詳細](2026-11-10-oof-comparator-readiness.md)。

最新の継続poll（2026-11-10 00:47 JST）: Host142 Qwen8B confirmation fold4、Host141 candidate11 fold3/candidate13 fold4が継続中。3 GPU割当・2 GPU idle、資源floor通過。新OOF/checkpointなし。停止・再配置・Kaggle書込・提出は行わず、既存runとqueueを維持。[Host continuation poll](2026-11-10-host-continuation-poll.md)。

公式更新（2026-11-10 00:50 JST）: MCPでチーム5,243、public LB`.752`同率、次点`.747`を確認。ルール・締切・Notebook条件は不変。candidate08のGPU1 pilot watcherはQwen8B confirmationと後続blend confirmationを管理する登録watcherの終了を待つ状態で、キューを迂回せず保全する。[Host continuation poll](2026-11-10-host-continuation-poll.md)。

公開手法更新（2026-11-10 00:55 JST）: lightningv08の`.595`題名Notebook（version22）は、5-fold Qwen3-Embedding-8B multi-depth branch 35%とQwen3.8-27B branch 6%を大きな公開親ensembleへ足すsourceを示す。題名scoreはoutput fileから検証できず、21 dataset/8 notebook依存があり、現行candidate08とnative branchが重なるため新規採用・queue変更なし。DateRun/metadata時刻の不一致とexact public fixture preview経路も記録。[source review](2026-11-09-qwen3-embedding-public-notebook-review.md)。

最新の継続poll（2026-11-10 00:57 JST）: Host142 Qwen8B confirmation fold4、Host141 candidate11 fold3/candidate13 fold4の各PIDは生存。3 GPU割当・2 GPU idle、memory/VRAM floor通過。新OOF/checkpointなし。candidate08 pilot watcherは登録済み依存watcherの完了待ち。既存run・queueを保全。[詳細](2026-11-10-host-continuation-poll.md)。

CPU最良成果の保全確認（2026-11-10 01:00 JST）: `09-05-function-view-candidate/model.joblib`は9,971,269 bytesで、SHA-256 `[SHA256省略、prefix ea73912a]`が過去記録と一致。[継続記録](2026-11-10-host-continuation-poll.md)。

公式・Discussion更新（2026-11-10 01:00 JST）: Kaggle公式は5,243チーム、public LB`.752`同率・次点`.747`。CatBoost新規投稿は作者自己申告のtransformer`.673`、CatBoost等`.336`で、再現手段はなく候補追加根拠にしない。GLM threadにも実装可能な新情報なし。提出条件・締切は不変。[記録](2026-11-10-host-continuation-poll.md)。

公開手法更新（2026-11-10 01:11 JST）: Discussion 757125の作者は、Qwen3.8-27B凍結表現の4層mean-pooling＋linear headを`.64–.65`と自己申告し、top-k logits/token-level routingは上回らなかったと報告。OOF/codeなしで再現不可のため、multi-depth embedding candidate08と関連づけて記録するがqueueは変更しない。[source review](2026-11-09-qwen3-embedding-public-notebook-review.md)。

公式/Notebook再確認（2026-11-10 01:13 JST）: 公開LB`.752`同率、5,243チーム、規則・締切に変更なし。DateRun首位は`.681`題名、Discussionの`.673`作者で競技Notebook検索したが公開kernelは見つからず。未知の別account copyまでは排除しない。[記録](2026-11-10-host-continuation-poll.md)。

最新の継続poll（2026-11-10 01:18 JST）: Host142 Qwen8B fold4 stage1、Host141 candidate11 fold3/candidate13 fold4が継続中。各PID生存、3 GPU割当・2 idle、資源floor通過。新checkpoint/OOFなしだが、各foldは過去の実測所要範囲内。candidate08 queueも維持。[詳細](2026-11-10-host-continuation-poll.md)。

運用再確認と継続poll（2026-11-10 01:29 JST）: README「共同作業の引き継ぎ」を再読し、指定hostだけを停止する手順・停止後の再利用制限・空きhostのみ利用可を適用。停止指示ではないため継続。Host141 candidate11/13は稼働中で3 GPUの状態も維持。Host142はSSH host-key検証失敗で再確認できず、迂回せず空き扱いしない（01:18時点ではconfirmationとwatcher稼働）。新規投入・停止・再起動なし。[詳細](2026-11-10-host-continuation-poll.md)。

公式・Notebook再確認（2026-11-10 01:34 JST）: 公式LBは5,243 team、top`.752`同率、締切はTimelineの2027-01-13 23:59 UTC、1日5提出・最終2件。Notebook要件はoffline・9時間以内・`submission.parquet`。公開Notebookの最新DateRunはNov 9 14:55 UTC、タイトル上位`.681`でtop超えの証拠なし。CPU bestのhash維持。現行候補・依存queueを保全。[詳細](2026-11-10-host-continuation-poll.md)。

公式情報の再確認（2026-11-10 01:44 JST）: MCP team_countは5,242へ変化したが、公開topは`.752`同点、次点`.747`で変化なし。Metadata deadline Jan14とTimeline Jan13 23:59 UTCの不一致は継続し、早いJan13を採用。規則・提出条件も不変。[詳細](2026-11-10-host-continuation-poll.md)。

Host142接続調査（2026-11-10 01:45 JST）: `ssh-keyscan`で観測したED25519 fingerprintは過去記録と一致。ただし元記録も未検証のため信頼根拠にはならず、known_hosts登録・Host142上での実行はしていない。host鍵の信頼できる照合経路が必要。[詳細](2026-11-10-host-continuation-poll.md)。

最新host poll（2026-11-10 01:50 JST）: Host141 candidate11/13は稼働中、GPU/RAM安全域内。新しいOOF/checkpointなし。Host142はQwen confirmation/watcherの最終確認が01:18で、SSH鍵は未検証のため空き扱いしない。既存queue維持。[詳細](2026-11-10-host-continuation-poll.md)。

最新host poll（2026-11-10 02:00 JST）: Host141 candidate11/13は継続中、GPU/RAM安全域内。前回からOOF/checkpoint更新なしだが各foldは過去の所要範囲内。Host142は01:18の最終trusted snapshot以降未検証のため空き扱いしない。[詳細](2026-11-10-host-continuation-poll.md)。

次の検証優先順位（2026-11-10 02:04 JST）: 完了primaryでBA`.664952`・差`+.078543`・paired 95% CI下限`+.065968`を示した固定Spectral mean-field correctionを、独立Qwen+SVC blend-confirmation OOFで事前固定のまま検証する。confirmationは未完のため採用/Notebook提出不可。既存queueを保全し、確認用OOFを待つ。[詳細](2026-11-10-host-continuation-poll.md)。

最新host pollと評価準備（2026-11-10 02:10 JST）: Host141 candidate11/13は継続中。Host141にはanalyzer・official train・adopted SVC OOFがあるが、early CPUとcurrent Qwen+SVC OOFは既知パスにない。Host142鍵が未確認のため、trusted sourceのOOFだけを使うHost141 CPU比較をfallbackに準備。[詳細](2026-11-10-oof-comparator-readiness.md)。

最新公式・host確認（2026-11-10 02:21 JST）: チーム数5,244、公開top`.752`同点、締切はTimelineの2027-01-13 23:59 UTC、5提出/日・最終2件。Host141 candidate11/13は継続中で新OOFなし、GPU/RAM安全域内。Host142はtrusted確認できず01:18 snapshotを最終状態として扱う。公開DateRun首位`.742+`DeBERTa notebookは検索時刻とmetadata last_runが不一致で、score/OOF主張も依存datasetと整合未確認。次の固定検証はSpectral independent confirmation。[詳細](2026-11-10-host-continuation-poll.md)。

最新host poll（2026-11-10 01:39 JST）: Host141 candidate11/13は稼働継続、GPU/RAM安全域内、新しいOOF/checkpointなしで既知のfold所要範囲内。Host142はtrusted host keyを照合できず、01:18の確認時点ではQwen confirmation/watchers稼働。安全な鍵確認まで空き扱いしない。新規投入なし。[詳細](2026-11-10-host-continuation-poll.md)。

比較準備（2026-11-10 01:20 JST）: analyzerは実装repoの`data/train.csv`を読むためHost142でCPU実行する。Host141からは完了後のfold OOF parquet 5枚のみを一時転送し、旧CPU・採用SVC・現行blendの6 report filesを比較別に保管する。[手順](2026-11-10-oof-comparator-readiness.md)。

最新の継続poll（2026-11-10 01:08 JST）: Host142 Qwen8B confirmationとHost141 candidate11/13の各PID生存、3 GPU割当・2 idle、資源floor通過。新OOF/checkpointなし。既存runとcandidate08を含む登録queueを維持。[詳細](2026-11-10-host-continuation-poll.md)。

最新の継続poll (2026-11-09 23:56 JST): [Host continuation poll](2026-11-09-host-continuation-poll.md)。対象PID/watcherは継続稼働中で、新OOF/checkpointなし。resource floorは安全域内。5時間枠はリセット後100%、週次54%。

公式更新 (2026-11-09 23:47 JST): [Host continuation poll](2026-11-09-host-continuation-poll.md)の公式差分では5,242チーム、Leaderboardは`.752`同率。candidate11/13の実測fold所要はそれぞれ約9h07m/5h41mで、残foldの時間見積りに使う。

最新の継続poll (2026-11-09 23:44 JST): [Host continuation poll](2026-11-09-host-continuation-poll.md)。candidate11 fold2 OOF完了（fold BA`.544444`）、fold3へ進行。candidate13 fold3 OOF完了（`.524074`）、fold4へ進行。いずれも5fold全体の採否評価は未実施。

最新の継続poll (2026-11-09 23:32 JST): [Host continuation poll](2026-11-09-host-continuation-poll.md)。candidate13 fold3 OOF完了（fold BA`.524074`）、5fold中4foldでfold4準備中。candidate11 fold2はStage2 checkpoint済みでOOF待ち。採否判断は全fold完了後。

最新の継続poll (2026-11-09 23:20 JST): [Host continuation poll](2026-11-09-host-continuation-poll.md)。公式LB`.752`同率、5,241チーム。candidate11 fold2・candidate13 fold3ともStage2 epoch1 checkpointを保存。OOFは未完了で、Qwen8B fold4も継続中。次の評価判断はOOF出力後に行う。

最新の継続poll (2026-11-09 23:08 JST): [Host continuation poll](2026-11-09-host-continuation-poll.md)。candidate11 fold2とcandidate13 fold3のStage1 checkpointを保存済み。両foldのOOFは未完了で、Qwen8B fold4も継続中。停止・再配置せず現行runを継続する。

最新の継続poll (2026-11-09 22:56 JST): [Host continuation poll](2026-11-09-host-continuation-poll.md)。candidate11 fold2 Stage1 epoch1をcheckpoint済み。Qwen8B fold4とcandidate13 fold3は継続中。fold OOFの完了までは採否判断せず、現在のキューを保全する。

最新の継続poll (2026-11-09 22:45 JST): [Host continuation poll](2026-11-09-host-continuation-poll.md)。公式Leaderboard`.752`同率、チーム数5,238。Host142 Qwen8BとHost141候補11/13は稼働中だが、OOF/checkpointの更新なし。資源条件は安全域内のため現行キューを維持する。

最新の継続poll (2026-11-09 22:35 JST): [Host continuation poll](2026-11-09-host-continuation-poll.md)。Host142 Qwen8B confirmationとHost141候補11/13は稼働中だが、新checkpoint/OOFなし。全資源条件は安全域内。停止・再起動・新規割当はせず、登録済み順序で継続する。

最新の継続poll (2026-11-09 22:25 JST): [Host continuation poll](2026-11-09-host-continuation-poll.md)。公式Leaderboardは`.752`同率、Timeline期限は2027-01-13 23:59 UTC。Host142 Qwen8B確認runとHost141候補11/13は稼働中でcheckpoint待ち。停止指示ではないため、既存キューを維持する。

最新の継続poll (2026-11-09 22:15 JST): [Host continuation poll](2026-11-09-host-continuation-poll.md)。今回も停止指示ではないため、Host141/142の既存runと登録済みwatcherを維持した。今後のホスト単位停止は、指定hostだけのcheckpoint・再開位置保存、対象Kaggle job/自動投入停止、watcher再投入なし、対象jobのGPU解放確認まで行い、停止hostは明示的な再利用指示まで使わない。

ユーザーの希望: Kaggleコンペを複数管理したい。今回はNameThatLLM。基本作業はAIへ委ね、各タブの有力資料から知見を蓄積し、情報共有・指示出し・自動化を整える。

GPU配分の最新指示（2026-11-08 21:41 JSTに再確認）: Host141/142は、両方とも空いていて候補spec・安全条件を満たす場合にKaggle実験へ使用してよい。稼働中の実験と登録済みキューは保全し、空きGPUとRAMを確認してから投入する。同一GPUへの同居は別途検証する。今回は停止指示ではなく、全実験を継続する。空き判定は両ホストそれぞれの接続・プロセス・GPU・RAMを確認して行い、接続できないホストを空きとは扱わない。

接続の引き継ぎ（2026-11-08 23:38 JST確認）: 現在の実行シェルはHost142（`hostname`で確認）なのでHost142はローカルで読み取りpollする。Host141はHost142から`ssh 141`で接続できる。ホスト表示名を直接SSH先にした場合や`141-home`/`142-home`は名前解決・鍵検証・banner timeoutになったことがある。`known_hosts`の確認を迂回せず、まず実行シェルのhostnameを確認し、この接続経路で両hostを別々にpollする。

短い停止指示の扱い（2026-11-09 00:44 JSTに再確認）: 「141を止めて」「142を止めて」は指定されたホストだけを止め、もう一方は継続する。「両方／全部止めて」と指定された場合のみ141/142両方を対象にする。指定ホストでは途中結果・再開位置を保存してからKaggleジョブと当該ホスト向け自動投入を止め、子プロセス/watchersによる再投入がないこととGPU解放を確認する。停止を確認したホストは、ユーザーが明示的に再利用を指示するまでKaggleに使わない。他研究プロセスやホストの電源は操作しない。今回は停止指示ではなく、実験を継続する。

運用の再確認（2026-11-09 06:04 JST）: ユーザーがホスト単位の停止・保全・再利用制限を再確認。以後「141を止めて」「142を止めて」は対象ホストだけに適用し、途中結果・正確な再開位置の保存、Kaggleジョブと自動投入経路の停止、子プロセス/watchersの不在、対象KaggleジョブによるGPU解放まで確認する。もう一方は継続し、停止ホストは明示的な再利用指示まで使わない。今回の依頼はREADME運用の再確認であり停止ではないため、両ホストのジョブとキューを継続・保全する。

運用の再確認（2026-11-09 07:49 JST）: Host141/142は両方とも空いている場合にKaggle実験へ使ってよい。停止指示は「141を止めて」「142を止めて」の指定ホストだけに限定し、途中結果・再開位置の保存、Kaggleジョブと指定ホスト向け自動投入の停止、再投入watcherがないこと、対象ジョブによるGPU解放まで確認する。もう一方は継続し、停止確認済みホストは明示的な再利用指示まで使わない。今回の依頼は停止ではなく、両ホストの実験継続である。

運用の再確認（2026-11-09 09:55 JST）: 研究READMEの引き継ぎを読み直し、Host141/142はそれぞれ空いていればKaggleに使用可と確認。今後「141を止めて」「142を止めて」は指定ホストだけを対象にし、途中結果と正確な再開位置を保存し、指定ホスト向けKaggleジョブ・自動投入を止め、子プロセス/watchersから再投入されないことと対象ジョブのGPU解放を確認してから停止完了とする。停止したホストは明示的な再利用指示まで使わない。今回の依頼は停止ではないため、Host141/142両方の実験を継続する。

運用の再確認（2026-11-09 11:09 JST）: ユーザーの明示指示に従い本節を再読。Host141/142は各ホストが空いている場合にKaggle利用可。「141を止めて」「142を止めて」は指定ホストだけに適用し、途中結果・再開位置の保存、対象Kaggleジョブと自動投入経路の停止、再投入watcher不在、対象ジョブによるGPU解放を確認して完了扱いにする。指定外ホストは継続し、停止確認済みホストは明示的な再利用指示までKaggleに使わない。今回は停止指示ではないため既存実験とキューを維持して継続する。指定の `codex_rate_limit.py --guard 15` は11:09 JSTに通過（5時間枠90%、週次60%）。

運用の再確認（2026-11-09 13:20 JST）: ユーザーの再指示に従い本節を再読。Host141/142は空いている場合に利用可だが、今回のpollでは両方とも既存Kaggle実験が稼働し全GPUが割当済みのため新規投入しない。「141を止めて」「142を止めて」は指定ホストだけを対象に、途中結果・正確な再開位置の保存、対象Kaggleジョブと自動投入の停止、再投入watcher不在、対象ジョブによるGPU解放を確認する。停止確認hostは明示的な再利用指示までKaggleに使わず、指定外hostは継続する。今回は停止ではなく継続指示なので全ジョブとキューを維持した。13:18:57 JSTのrate guardは5時間84%、週次60%でpass。

運用の再確認（2026-11-09 16:47 JST）: ユーザー指示に従い本節を再読し、今後の運用条件を再適用する。Host141/142は各ホストが実際に空いている場合にKaggle利用可。今後のホスト単位停止は指定hostだけで途中結果・正確な再開位置を保存し、対象Kaggleジョブとその自動投入経路を止め、再投入watcher不在と対象ジョブによるGPU解放まで確認する。指定外hostは継続し、停止済みhostは明示的な再利用指示まで使わない。今回は停止指示ではないため実験を継続する。16:46:44のrate guardは5時間90%、週次58%でpass。直近のHost141/142確認では全GPUが既存runに割当済みのため、新規投入は空き確認まで行わない。

- まず指定ホストへのKaggle新規投入・自動再起動を止め、待機watcherが別ホスト上にある場合も指定ホストへ投入する経路を止める。指定外ホストの実験・投入は継続する。
- 指定ホスト上のKaggleジョブを特定し、利用可能なcheckpoint・途中結果・ログ・config・正確な再開位置と再開コマンドを保存して、安全に終了する。checkpoint機能がない場合は、保存済み位置と未保存範囲を記録し、保存できたと偽らない。
- 子プロセスやwatcherからの再起動・再投入が残っていないこと、および指定ホスト上の対象KaggleジョブがGPUを解放したことを確認してから停止完了とする。他研究のプロセスが残っている場合はGPU全体が空いたと報告しない。確認不能・未停止があれば明示する。
- 停止を確認した指定ホストは、ユーザーが明示的に再利用を指示するまでKaggleに使わない。他研究の処理やホスト自体の電源は操作しない。

現時点の前提: チャット＋Markdownを入口にし、資料の主張・AIの推測・自分たちの実測を分ける。公開LB先頭超えを目指す承認済み自動実験goalがactive。試行数・累積GPU時間の固定上限はなく、prompt-grouped比較、利用枠15%ガード、GPU/RAM安全条件、提出制限、Kaggle作成物privateのspecを守る。現在までKaggle提出は行っていない。

CPU baseline cycleは完了し、既存成果物を保持する。正本cycleは `name-that-llm/artifacts/2026-11-06-cpu-cycle`、最良configは `configs/05-function-view.json`、最終モデルは `09-05-function-view-candidate/model.joblib`。`src/cpu_finalize.py --cycle ...`で既存成果物を再検査でき、cycle内`reproduce_cycle.sh`には新規cycle向けの全再実行コマンドを保存。追加の自動実験は承認済みGPU goalの範囲で別artifact/configに記録する。

- 2026-11-08 06:09 JST: GPU142のQwen02/04を保全したまま、空きGPU141 host `141-X9DAi` のA4000 UUID `GPU-51b57ca0-53ca-3266-7105-efc692a6c834` にcandidate05 DeBERTa v3 smallの分離環境を配置。CUDA12.8/Torch2.9.0+cu128、Transformers4.57.1等を固定し、pilotは0.772秒/step、peak 2,725 MiB、8,192 MiB reserve通過。primary fold0開始（PID 2324865、wrapper 2324864）、OOFはまだ未完。資源・hash・初回依存不足の復旧は[実験ログ](2026-11-06-gpu-autonomous-initial-check.md)。

- 2026-11-09 21:24 JST 運用継続確認: README「共同作業の引き継ぎ」を再読し、指定ホストのみ停止する条件と、途中結果・再開位置保存→対象ジョブ/自動投入停止→再投入watcher不在/GPU解放確認→停止hostは明示的な再利用指示まで保留、という手順を継続適用する。今回は停止指示ではない。`--guard 15` は21:23:47 JSTにpass（5時間91%、週次56%）。Host142 (`142-X10DAi`) はQwen8B confirmation PID `3871913` がGPU1で継続（15,834 MiB使用/16,266 MiB空き、28%、100% CPU）、GPU0は15/15,960 MiBでidle、MemAvailable `216826104 kB`。登録watcher群は継続。直近の保存結果はfold3 OOF/logits (20:51:44 JST、BA `.571073`); fold4の新checkpoint/OOFなし。Host141 (`141-X9DAi`) は候補11 PID `2439031` と候補13 PID `2448742` がCPU/GPU稼働中。GPU0/1/2使用・空きは`1405/14568`, `15/15960`, `8549/7426 MiB`、MemAvailable `113670080 kB`。候補11の最新OOFはfold1、候補13はfold2で、新checkpoint/OOFなし。現状は3/5 GPU割当、Host142 GPU0とHost141 GPU1が空きだが、待機キューがあるため新規投入せず既存実験・watcherを保全する。公開Notebookの追加レビューは[調査ログ](2026-11-09-qwen3-embedding-public-notebook-review.md)。停止・再起動・Kaggle書込・提出なし。

- 2026-11-09 21:27 JST official refresh: Kaggle MCP metadata now reports 5,231 teams; official public leaderboard remains Le Viet / Meni David Gottesman tied at `.752`, next scores `.747`. Submission limits/deadline unchanged from the 21:14 check. No submission or queue change.

- 2026-11-09 21:37 JST official-page refresh: Rules still allow 5 submissions/day and up to 2 final submissions; Timeline states Jan 13, 2027 at 23:59 UTC, earlier than metadata's Jan 14 date; Code Requirements still require Notebook-only, Internet disabled, <=9 hours and `submission.parquet`. Evaluation confirms unequal test passages per model and different public/private model mixes. These pages were retrieved directly through the official Kaggle MCP; no policy change.

- 2026-11-09 21:48 JST official leaderboard refresh: team count is 5,234; top remains Le Viet and Meni David Gottesman tied at `.752`, next `.747`. Submission settings and deadlines are unchanged; no submission or queue change.

- 2026-11-09 21:48 JST follow-up MCP read: team count refreshed to 5,235; public leaders remain tied at `.752`. Score-sorted search still ranks the parent `.681` Notebook highest; the new Heliosli v5 variant reports no verifiable score/output. See the Qwen embedding source review.

- 2026-11-09 21:54 JST host poll: Qwen8B confirmation `3871913`, candidate11 `2439031`, and candidate13 `2448742` remain alive/active; no new checkpoint/OOF since 21:44. Host142 GPU1 is at 15,834 MiB used, 28% utilization; Host141 GPU0/GPU2 at 1,405/8,549 MiB used with 16%/40% utilization. MemAvailable is 216.8/113.7 GiB. Preserve the current jobs and registered queue.

- 2026-11-09 21:59 JST official rules refresh: Rules remain 5 submissions/day and up to 2 finals; Timeline remains Jan 13, 2027 23:59 UTC (metadata Jan 14), and Code Requirements remain Notebook-only, Internet disabled, <=9 hours, `submission.parquet`. Evaluation still warns that per-model test counts and public/private mix differ. No change.

- 2026-11-09 22:05 JST host poll: Qwen8B confirmation `3871913`, candidate11 `2439031`, candidate13 `2448742`, and registered watchers remain alive. No new checkpoint/OOF since 21:54; GPU/RAM remain within safety floors. Preserve jobs and queue; no stop/restart/new run.

- 2026-11-09 21:44 JST host follow-up: Qwen8B confirmation PID `3871913`, candidate11 PID `2439031`, candidate13 PID `2448742`, and registered watchers remain alive and CPU/GPU active. No checkpoint/OOF advanced since 21:34. Three GPUs remain assigned; Host142 GPU0 and Host141 GPU1 are idle. The registered jobs are tied to their specified host/GPU, so do not reroute or create an unregistered allocation without its candidate/resource gate.

- 2026-11-09 21:34 JST follow-up: `--guard 15` passed at 21:34:10 (5h 91%, weekly 56%). All three runners remain CPU/GPU active with no error or checkpoint/OOF newer than 21:24; their logs show Qwen8B fold4, candidate11 fold2, and candidate13 fold3 as the current/next folds. GPU/RAM remain within the previously recorded safety bounds; preserve runs and watchers, no restart or new allocation.
