---
project: sam2-mamba-motion-tracking
status: active
summary: MOSE temporal Mambaのspec実装・4条件lockbox評価を完了。F1−F0のJ&F差は+0.00282だが95% CIが0を含み、主仮説は支持されなかった。SAM2MOT S4の寄与切り分けは継続中。
created: 2026-07-07
last_updated: 2026-10-08
---

# Mambaによる動き予測を用いたSAM2ベースの物体追跡

## 概要

SAM2 / SAMURAIベースの物体追跡において，カルマンフィルタによる動き予測をMambaを用いた学習ベースの時系列モデルに置き換えることで追跡性能を改善する研究。

研究の中心は，Mamba tracking手法を **sliding window型**（過去数フレームを毎回入力）と **state carry型**（hidden stateをフレーム間で継続更新）に分類し，MOTにおいてstate carry型が抱える **hidden state contamination**（オクルージョン・誤associationによる内部状態の汚染）の問題を定義・可視化・抑制することにある。

SAM2/SAMURAIは研究の実験基盤として使い，Mamba motion priorを外付けする形で統合する。

## 実装コードの場所

### Mambaトラッカー学習リポジトリ
`/mnt/HDD10TB-2/aburatani/2025_09_aburatani_Mamba_Trackers`

| モデル | 種別 | 学習エントリ | 推論エントリ | チェックポイント |
|---|---|---|---|---|
| `MambaTrack` | sliding window型 | `ssm_tracker/train.py` | `ssm_tracker/track.py` | `saved_ckpts/mambatrack_dancetrack2/` (epoch1〜25) |
| `TrackSSM` | sliding window型 | `ssm_tracker/train.py` | `ssm_tracker/track.py` | `saved_ckpts/trackssm_dancetrack_sep_scale_one_dec_layer/` (epoch10〜100) |
| `MambaStateful` | **state carry型（独自実装）** | `ssm_tracker/train_stateful.py` | `ssm_tracker/track_stateful.py` | `saved_ckpts/mamba_stateful_dancetrack/` (epoch1〜100) |

**現在の制約**（2026-07-09時点）：
- `val loss` と tracking 指標ベース validation は実装済みだが，運用頻度と命名は未整理
- `best_val_loss.pth` と `best_tracking_hota.pth` は保存されるが，full val を含む長時間運用は未検証
- `MambaStateful`のLRスケジューラが`none`（固定）→ 要修正
- データセットはDanceTrack前提

**学習設定のキーパラメータ**：

| モデル | optimizer | LR scheduler | epochs | データ形式 | scale_factor |
|---|---|---|---|---|---|
| MambaTrack | SGD | transformer | 25 | bbox差分→bbox差分 | 50 |
| TrackSSM | SGD | transformer | 25 | bbox+差分→bbox | bbox:20 / diff:50 |
| MambaStateful | Adam | **none（固定）** | 100 | bbox→bbox差分 | bbox:1 / diff:50 |

---

### SAM2/SAMURAI推論・統合リポジトリ
`/mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2`

現在の実装状況（ブランチ：`mot`）：

| 機能 | 状態 |
|---|---|
| SAMURAI + sliding window型Mamba（`samurai_mamba_window`モード） | ✅ 実装済み |
| SAMURAI + state carry型Mamba（`samurai_mamba_stateful`モード） | ✅ 最小版統合・25系列推論・TrackEval評価済み |
| `MambaStatefulMotionFilter`の状態管理 | ✅ 元repo checkpointのstrict load・track別cache・state carryを実装済み |
| MOT推論エントリ | `scripts/main_inference_mot.py` |

---

### SAM2MOT-lite実装リポジトリ（停止中・着想元）
`/mnt/HDD10TB-2/aburatani/2026_05_aburatani_sam2mot`

SAMURAI forkをベースにSAM2部分のみを残し、`sam2mot_lite/`を自作追加（`639751d..HEAD`で17ファイル・約2,400行）。[SAM2MOT](https://github.com/TripleJoy/SAM2MOT)論文設計の再実装で、detectorのbboxをSAM2へのbox promptとして与え、SAM2のmaskから生成したbboxをMOT形式で出力するTracking-by-Segmentationベースライン。

**位置づけ**：8/28 MTGの方針により、SAM2MOTの再現完成を目的とせず「途中検出による軌跡補正」の着想元として扱う。**2026-06-12以降停止中。**

| マイルストーン | 状態 | 実装位置 |
|---|---|---|
| M0-M3 Detection/Mask/Matching・SAM2 prompt | ✅ 実装済み | `tracker/detection.py`, `mask_utils.py`, `matching.py`, `sam2_wrapper.py` |
| M4 最小推論パイプライン | ✅ 実装済み | `scripts/run_sequence.py`, `tracker/track.py` |
| M5 Object Addition（動的追加） | ✅ 実装済み | `trajectory_manager.py:162` |
| M6 Object Removal / 状態遷移 | ⚠️ 実装済みだがフラグ不通 | `trajectory_manager.py:104` |
| M7 Quality Reconstruction | ✅ 実装済み | `trajectory_manager.py:256` |
| M8 Cross-object Interaction | ⚠️ 実装済みだが既定で無効 | `trajectory_manager.py:359-426` |
| M9 TrackEval評価接続 | ❌ 未着手（出力形式のみ適合） | — |

⚠️ **`sam2mot_lite/README.md`のMilestone表は古い**（M4以降を「設計のみ」と記載）。README最終更新`5bdcc9e`はM4〜M8実装コミットの祖先。構成図にある`cross_object_interaction.py`と`visualize.py`は全git履歴を通じて存在しない。

⚠️ **既存の推論結果はGTオラクル条件**：`scripts/run_dancetrack.py:116`が検出入力に`gt/gt.txt`（score列=1）をそのまま使っているため、detector入力の既存ベースラインとは原理的に比較不可能。DanceTrack val **15/25系列**のみ出力あり（欠損10系列は原因不明、ログ未保存）。存在する15系列は全て最終フレームまで完走。

**SAM2への関与**：`sam2/`本体は一行も未改変。非公開の`inference_state`をラッパー側から書き換えるDynamic Batch Padding方式（`sam2_wrapper.py:78`, `:125-135`）で、時間的メモリを保持したまま追跡途中のオブジェクト追加を実現している。内部API依存度が非常に高く、**SAM2デコーダー統合やSAM3移行時に再利用できない前提**で扱う。OOMの真因は`cond_frame_outputs`の無制限増加であり、`prune_horizon=48`（`non_cond`のみ削除）では救えない。

**実行環境**：`.venv-sam2mot`（Python 3.12.3, torch 2.12.0+cu130）。`cwd`=リポジトリルート・`PYTHONPATH=./sam2mot_lite`が必須（`.`を入れると`sam2/`がパッケージを遮蔽して`RuntimeError`）。`requirements.txt`・lockファイルなし、venvは`.gitignore`除外のため**venvを失うとバージョン再現不可**。

詳細な棚卸しは [`experiments/2026-09-08-sam2mot-lite-implementation-status.md`](experiments/2026-09-08-sam2mot-lite-implementation-status.md) を参照。

**再現実装 `sam2mot_repro/`（2026-09-08〜）**：同リポジトリ内に、承認済みspec [`specs/2026-09-08-sam2mot-reproduction-spec.md`](specs/2026-09-08-sam2mot-reproduction-spec.md) に基づく再現実装を新規に作成した（`sam2mot_lite/` は変更禁止・読み取り専用）。検出器はCo-DINO-L、セグメンタはSAM2.1-large per-instance。S0〜S4完了（2026-10-03）。段階実装のプロトコルは同リポジトリの `CLAUDE.md`、結果は [`experiments/2026-09-27-sam2mot-s0-s2-results.md`](experiments/2026-09-27-sam2mot-s0-s2-results.md)、[`experiments/2026-09-28-sam2mot-s3-coi-results.md`](experiments/2026-09-28-sam2mot-s3-coi-results.md) を参照。

## 現在の状況

**10/8 MOSE実装・評価完了**：承認済みspecに基づきF0/F1を各2,789 step学習し、tuningでF0 step 2789、F1 step 2000を選択。200動画・570対象・36,260評価frameでP0/F0/F1/F1-resetを評価し、各条件のprediction PNG・frame coverage・凍結hash・集計値を独立監査して異常なし。動画平均J&FはP0=0.70084、F0=0.73920、F1=0.74202、F1-reset=0.74265。主比較F1−F0は+0.00282、video-level paired bootstrap 95% CI=[−0.00669,+0.01157]で0を含み、specの基準では主仮説を支持しない。F1−F1-resetは−0.00063 [−0.00156,+0.00004]で、state carryの改善は確認できなかった。系列長別比較もすべて95% CIが0を含む。単一seedの結果として記録し、seedを越えた再現性は主張しない。F0−P0は+0.03837 [0.02159,0.05731]。詳細な比較・監査結果は [`experiments/2026-09-30-mose-temporal-mamba-finetuning.md`](experiments/2026-09-30-mose-temporal-mamba-finetuning.md)。

**7/2 MTG後の状況**：state carry型Mambaは100エポックで収束しかけているが、LRスケジューラがほぼ固定になっており過学習の可能性が高い。TrackSSMは入力形式の違いが発覚し実験設定の見直しが必要。public validationの設計（5エポックごとのHOTA評価）が次の実装課題。

**7/9 MTG後の状況**：`val loss` と tracking 指標ベースの validation を学習導線へ組み込む実装自体は成立した。次の課題は、TrackEval 側の関数化が単体で正しいかを切り分けること、tracking validation の命名整理、そして計算時間増加の原因を profiler で特定すること。MIRU ポスターは「SAM2 / SAMURAI の改善」を主題に据え、定量表に加えてオクルージョン時の定性的可視化も準備する。

**7/15時点**：TrackEvalのCLI/API parityを1および3 sequenceで確認し、Mamba側ではtracker推論 subprocessを維持したままTrackEval評価を直接関数呼び出しへ置換した。既存25 sequence tracker出力でCLIとadapterのsummaryが一致した。計測コードを追加し、MambaStatefulの1epoch smokeと3sequence単独計測を実施した。tracker推論は316.973秒、TrackEvalは3.490秒で、今回の条件ではtracker推論が主要コストだった。候補周期の1epoch smokeも通過したが、100epoch本学習とfull valは未実施。

**7/16 MTG後**：state carryのepoch間MOT Metrics不変について、TrackEvalの計算導線ではなくtracker推論側を切り分ける方針を決定した。小規模データへの過学習と同一データでのtracker推論を先に行い、学習・推論・評価を分離して確認する。state carryの学習では、sliding window型と異なり状態を時系列に引き継ぎながら各時刻の損失を扱う必要があるため、RNN/LSTMのteacher forcing・free runningを含む標準的な方法を調査する。MIRUポスターはSAM2/SAMURAIの改善を主軸に、課題・従来法・提案法の簡略図と大きな文字で再構成する。

**7/21 調査完了**：teacher forcing/free-runningの横断調査をBatch 4まで完了した。最優先の改善候補は、予測bboxをhard IoU matchingの主位置から外すassociation分離（P1）である。その後、confidence/match qualityによるcache freeze・reset（P2）、入力分布混合（P3）、明示的stateful unroll + TBPTT（P4）を独立に比較する。実装は未開始であり、P1だけを対象にした承認待ちとする。

**7/21 P0.5完了**：既存のDanceTrack val 25系列出力を同一TrackEval条件で比較した。HOTAはMambaTrack 33.837、TrackSSM 32.783、MambaStateful 47.293。MambaStatefulが高かったが、checkpoint provenance、入力形式、モデル構造、prediction-primary associationが未分離のため、学習方式の優位性とは解釈しない。次はP1を診断用baselineとして個別に検証する。

**10/6 MOSE学習再開**：F0は最後の復旧checkpoint `step 1400` から再開し、step 2001/2789まで進行。ログ1〜2001は連番・固定sample orderに一致し、lossはfinite。step 1500/2000 tuning候補とstep 1600/1700/1800/1900 recovery checkpointを保存。step 2000 checkpoint SHA-256は`f9c8d9e7…bf580111b`。旧step 1401〜1456は再計算済み。最長500-frame軌跡もfiniteで完走し、高loss系列のannotation確認を実験ログに記録。GPU1の別検出ジョブ終了後に残る候補評価を行う。詳細は [`experiments/2026-09-30-mose-temporal-mamba-finetuning.md`](experiments/2026-09-30-mose-temporal-mamba-finetuning.md)。

**10/7 MOSE学習再開**：F0は復旧checkpoint `step 2500`から再開し、step 2566/2789。step/sample order/lossを再監査し、不一致なし。F0 step 2500 tuning評価は97/313対象でGPU1にて進行中。ターン中断対策としてF0 recovery guardと後続pipelineをtmux detached sessionへ移行した。詳細は [`experiments/2026-09-30-mose-temporal-mamba-finetuning.md`](experiments/2026-09-30-mose-temporal-mamba-finetuning.md)。

**7/23 P1 25系列確認完了**：同一epoch100 checkpoint・detector入力・config・scale・lifecycle・state/cache更新・TrackEval条件で、prediction-primary A1とlast accepted observation A2をDanceTrack val 25系列で比較した。A1はHOTA 47.233、A2はHOTA 47.910、AssA 30.843、IDF1 47.315、IDSW 2386となり、A2はA1に対してHOTA +0.677、AssA +0.936、IDF1 +1.429、IDSW -192を示した。効果は3系列より小さく系列依存もあるが、P1仮説を25系列aggregateでも支持する。P2 cache更新制御のspec化へ進む。

**7/23 P2完了**：P1 A2を固定し、B0 self-update、B1 missing freeze、B2 trusted detector match gate、B3 prolonged-untrusted resetを3系列・25系列で診断した。25系列ではB0 HOTA 47.910に対しB1 48.035で、state非有限イベントは4,515から115へ減少した。一方、B2はHOTA 46.962、B3は46.855で、AssA/IDF1が低下しIDSWが増加した。missing freezeはcontamination抑制の根拠を与えたが、単純なquality gate/resetは採用せず、P3/P4へ自動移行しない。

**7/23 SAM2最小統合完了**：元repoのepoch100 `MambaStateful`をSAM2/SAMURAIへ移植し、DanceTrack val 25系列を推論・評価した。HOTA 55.520、AssA 62.482、IDF1 64.154、IDSW 1,535で、全candidate debug行でcheckpointロード済み、fallbackなしを確認した。これはepoch100固定の統合確認値であり、SAM2上の改善量やbest-HOTA checkpointの結果ではない。

**7/27 checkpoint比較完了**：元repoの`best_tracking_hota.pth`（metadata上epoch20）を同じSAM2条件で評価したところ、HOTA 54.606、AssA 61.691、IDF1 62.813、IDSW 1,525となった。epoch100よりHOTAは0.914低く、元repoのbest-HOTA checkpointがSAM2上でも最良とは限らないことを確認した。

**7/30 MTG後**：SAM2統合ではepoch100を暫定基準として扱い、元repoのbest-HOTA checkpointをSAM2上の最良とは断定しない方針を確認した。`kf_score_weight`の細かな探索は優先せず、MambaTrackの論文水準再現とstate carry型のrecurrent学習・TBPTTを含む学習方法の見直しへ進む。MIRUでは30 FPS動画と追跡結果可視化アプリを使い、定性候補はViewerで人手確認してから採用する。

**8/28 MTG後**：MIRUで受けた意見を踏まえ、state carry型Mambaの学習方法の見直しを最優先し、SAM2デコーダーへのMamba統合を10月中旬頃までの実装目標とした。Mamba・LSTM・Transformerは同程度GFLOPSと速度を揃えて比較する。hidden state contaminationは、まずID switchを人工的に挿入した出力軌跡のシミュレーションで定義・可視化し、SAM2MOTは再現ではなく途中検出による独自補正の着想として扱う。Viewの2ページ原稿作成とtestデータ評価も進める。

**9/18 MTG後**：unroll/TBPTTのtracker性能差は明確な単調傾向がなく、細かな探索はいったん深追いしない。YOLO＋MambaとSAM2＋Mambaの比較条件を整理し、sequence別の失敗分析、0-padding・state伝播・detach境界の実装確認、SAM2デコーダーへのMamba埋め込み調査を優先する。

研究の問い：

> MOTにおいて，state carry型Mambaのhidden stateをtrackごとに持続的に保持することは有効か？不安定な場合，その原因はhidden state contaminationなのか？それをどう検出・抑制すればよいか？

詳細は [`specs/2026-07-07-state-carry-research-direction.md`](specs/2026-07-07-state-carry-research-direction.md) を参照。

**9/2 P4a closeout / P4b初回比較完了**：P4aにL0互換train logging、train/val splitを分離したGT-only validation、horizon 1/4/8/16/32のfree rollout、checkpoint SHA256 manifestを追加した。実データepoch5でvalidation loss 0.048975、state finite rate 1.0、全rollout horizonの発散率0を確認した。P2-B1固定条件のDanceTrack val 25系列ではL0 epoch5 HOTA 53.971、P4a epoch5 HOTA 53.240で、P4aはHOTA -0.731、AssA -0.659、IDF1 -0.800、IDSW +2となった。epoch100本学習の結果とは分けて扱う。

**9/4 MTG後**：stateful unroll + TBPTTの学習コード実装と学習実行を確認した。mean lossとvalidation lossは低下している一方、内部stateログ終盤のスパイク、`detach`・state carry・resetの実際のタイミング、Mamba側とSAM2統合側の性能差は未整理である。まずコード・設定・ログ・sequence別結果を突き合わせて挙動と原因を検証し、その後にdecoder統合へ進む。

**9/1 P4a実装着手**：承認済みspecに従い、L0固定windowの明示entrypoint（`train_mamba_window.py`）を残したまま、GT-only stateful unroll dataset、微分可能state forward、TBPTT学習entrypoint、設定、smoke runnerをMamba_Trackersへ追加した。構文・dataset生成・CPU stubでのstate parity/backwardに加え、実Mamba・CUDA上のP4a/L0 smoke、checkpoint再load、legacy/stateful parityを確認済み。

**9/8 SAM2MOT-lite棚卸し完了**：停止中のSAM2MOT-lite実装リポジトリをresearch-workspace管理下へ入れ、実装実態・出力カバレッジ・残作業を確定した。M0〜M8は実装済み（M6は`enable_object_removal`が全`.py`から未参照でフラグ不通、M8は既定無効）、M9 TrackEval接続は未着手。最重要の発見は、既存のDanceTrack出力が`run_dancetrack.py:116`でGTの`gt/gt.txt`を検出入力に使うオラクル条件であり、detector入力の既存ベースラインと比較不可能な点である。val 15/25系列のみ出力があり、存在する15系列は全て完走しているが、欠損10系列の失敗原因はログ未保存のため不明。SAM2本体は未改変で、動的オブジェクト追加は非公開`inference_state`への依存が強く、SAM2デコーダー統合・SAM3移行時には再利用できない。

**9/18 shuffle条件評価完了**：`shuffle=True`で学習したP4a epoch100 checkpointをSAM2/SAMURAIへ統合し、DanceTrack val 25系列をTrackEvalで評価した。HOTA 53.944、AssA 60.701、IDF1 62.172、IDSW 1,551で、非shuffle P4a統合結果（HOTA 54.391）を下回った。単一seed・epoch100固定のため、shuffleの有効性は未確定とし、次はunroll/TBPTT長・batchサイズ・Mamba内部次元の探索で確認する。


**9/11 MTG後**：P4aの用語とstate carry/TBPTTの実挙動を整理した。loss振動は`shuffle=False`で固定されたchunk順序の影響を強く支持するため、shuffle条件のSAM2評価とハイパラ探索へ進む。padding・maskingと正規化bbox lossのpixel換算も確認する。View原稿は状態保持型MambaによるSAM2ベース物体追跡を軸に整理し、デコーダー統合は物体数変化・マスク特徴量対応・SAM2/SAMURAI/MOTの運用差を図示してから検討する。

**9/27 SAM2MOT再現 S0〜S2完了**：承認済みspecに従い、Co-DINO-L検出（val 25系列、track カバレッジ 272/273）、S1 baseline、S2 Object Addition をDanceTrack val 25系列で推論・TrackEval評価した。S1 HOTA 59.21 / MOTA 46.64 / IDF1 64.41 / IDSW 425 に対し、S2は HOTA 64.32 / MOTA 59.77 / IDF1 71.13 / IDSW 1,162（ΔHOTA +5.11、論文testのAdd寄与は+5.0）。FNが71,380減りDetAが+14.38上がった一方、AssAは−6.39、IDSWは+737となった。CoI・Q-Rは未着手で、spec の順序基準の判定はS3・S4待ち。9/25 MTGと9/27の優先順位整理により、SAM2MOT再現は期限付きの補助線、temporal Mamba統合が主線。

**9/28 SAM2MOT再現 S3完了**：Cross-object Interaction（mask IoU>0.8の衝突検出、logit差・分散による誤追跡同定、誤追跡トラックの現フレームのメモリ除外、A7低信頼フィルタ）を実装し、val 25系列で評価した。S2→S3で HOTA 64.32→67.13（+2.81）、MOTA +17.10（論文test +17.7）、IDF1 +1.60、IDSW −264。一方でAssAは−3.21、DetAは+9.19で、spec の機構署名（AssA増・DetAほぼ不変）と順序基準（CoI寄与 > Add寄与）は不成立。MOTA改善の約97%はFP減少由来で、IDSWが小さい以上、論文のΔMOTA +17.7自体がDetA不変と両立しにくいことも分かった。S4前に、A7分離run・spec機構署名の見直し・test提出のどれを行うか決める。

**9/30 S3のA7切り分け**：A7（低信頼エントリのメモリ除外）を切り、A6（CoIによる誤追跡のメモリ除外）だけでval 25系列を評価した。HOTA 68.22、AssA 64.57、IDF1 75.42、MOTA 76.88、IDSW 839。S2比でHOTA +3.90、AssA −1.16、DetA +9.17、MOTA +17.10。AssA低下−3.21のうち−2.05とIDF1低下の大半はA7由来で、DetA・MOTAの変化はすべてA6由来だった。A6のみでも、AssA増とDetA不変の署名、およびCoI寄与 > Add寄与の順序は不成立。同日、A7の既定を無効に変更し、S4の前段はA6のみrunとした（S4実装後にA7の有効・無効を再確認する）。spec機構署名の見直しはS4前に判断する。詳細は [`experiments/2026-09-30-sam2mot-s3-a7-ablation.md`](experiments/2026-09-30-sam2mot-s3-a7-ablation.md)。

**10/3 SAM2MOT再現 S4完了**：Quality Reconstruction（pendingかつAddition段で高信頼検出とマッチしたトラックに、box promptをconditioning frameとして入れ直す）を実装し、val 25系列で評価した。S3（A6のみ）→S4で HOTA 68.22→61.85（−6.37）、AssA −10.15、IDF1 −10.35、IDSW +710 と、論文の+1.7とは逆に悪化した。全段の判定では、Addは再現、CoIはMOTAのみ再現、Q-Rは逆効果で、論文Table 3の寄与構造は未再現。Q-Rのマッチ基準がIoU>0で隣の人物のboxでkeyframeを上書きしている可能性が高く（0065で衝突0→1,068、HOTA 91→49）、マッチ閾値・発動間隔・A5操作の切り分けを判断する。詳細は [`experiments/2026-10-03-sam2mot-s4-qr-results.md`](experiments/2026-10-03-sam2mot-s4-qr-results.md)。

**9/30 MOSE temporal Mamba追加学習開始**：承認済みspecに従い、SAM2専用worktreeで学習・streaming評価entrypoint、F0/F1 100軌跡pilot、更新済み評価器smokeを完了。fit 1,121動画/2,789軌跡、tuning 125動画/313軌跡、lockbox 200動画/570軌跡を固定。短・中央値・最長500-frameでTBPTT=8のfiniteを確認し、TBPTT=16はOOMで不採用。pilot checkpointの全tuningではF0 J&F=0.734545、F1=0.734542（Δ=−0.000003）。全fitを1 pass（2,789 updates）する条件を固定。10/3にF0学習をstep 800の復旧checkpointから再開し、step 1,456/2,789まで進行。step 900・1,000・1,100・1,200・1,300・1,400 checkpointを保存し、step 1〜1,456 lossは全てfinite（最大419.36、step 1,039）。F0 step 500/1,000 tuningは完了し、J&F=0.75319/0.75406。metadata対象数・除外数とprompt tensorを保存する評価器、全6候補を必須とするtuning checkpoint選択器、code/checkpoint/index hashで固定するone-time lockbox gateを実装・smoke確認した。F0 prompt tensor exporterは異なるweight checkpoint間で座標が一致することを2軌跡で確認した。F1 adapter decay groupをspecどおり限定し、augmentationの公式configとの差は明記した。実験ログは [`experiments/2026-09-30-mose-temporal-mamba-finetuning.md`](experiments/2026-09-30-mose-temporal-mamba-finetuning.md)。

**9/30 MTGでの設計整理**：temporal Mambaの現行global average pooling・1 token・空間broadcast構成は最小接続確認用とし、最終設計は未決定。空間情報を保つ特徴表現、次元削減の必要性、計算量・メモリ、設計根拠を調査する。SAM2MOTはHOTA 70以上の手法と学習・評価条件を照合する。中間発表・研究室見学の資料準備も進めるが、日程は確認中。議事録は [`meetings/2026-09-30-mtg.md`](meetings/2026-09-30-mtg.md)。

## マイルストーン

### フェーズ1：MIRU / ポスター
- [x] SAM2 / SAMURAIのMOT適用時の問題を把握する（4月完了）
- [x] Mamba tracking手法の調査・sliding window型 / state carry型の整理（5月末完了）
- [x] SAMURAI+Mambaの初期実験（HOTA: SAM2=0.46, SAMURAI=0.54, SAMURAI+Mamba=0.53）
- [x] state carry型Mambaの実装・100エポック学習（7/2時点で収束しかけ）
- [x] `val loss` と tracking 指標ベース validation の学習導線への実装・smoke test（7/9確認）
- [x] MambaTrack / TrackSSM / State carry型の公平な比較実験（P0.5 as-is比較、7/21完了）
- [x] prediction-primary associationとlast accepted observation associationの分離診断（P1、3系列、7/22完了）
- [x] missing freeze・trusted cache update・prolonged-untrusted resetの診断（P2、3系列・25系列、7/23完了）
- [x] 元MambaStatefulのSAM2最小統合と25系列TrackEval評価（epoch100、7/23完了）
- [ ] MambaTrackを論文記載値に近い条件・性能まで再現し、検出入力とMOT評価を含めて比較可能性を確認する
- [ ] 入力スケーリング（bbox vs bbox delta）の根拠整理
- [x] TrackEval 側の関数化導線を単体で検証し、統合時の問題を切り分ける
- [x] tracking validation の命名整理（`mot_metrics` への統一）と運用方針の明確化
- [ ] **validation運用の安定化（過学習チェック用 + tracking 指標評価頻度の調整）**
- [ ] **State carryのLRスケジューラ修正（warmup比率・decay形状の見直し）**
- [ ] tracking validation の計算時間増加要因を profiler で特定する
- [x] state carryのepoch間MOT Metrics不変について、frame 6付近のNaN・matching失敗・track再生成を診断する（7/16確認）
- [ ] state carryの小規模過学習と同一データでのtracker推論を確認する
- [ ] state carry型のrecurrent学習を導入・検討し、TBPTTを含む学習設計を整理する
- [x] stateful unroll + TBPTTの学習コードを実装する（9/4確認）
- [ ] stateful unroll + TBPTTのdetach・state carry・resetの挙動と内部stateログを検証する
- [x] P4a loss振動を全batch loggingとshuffle対照で診断し、固定chunk順序の影響を確認する（9/11完了）
- [x] shuffle条件で学習したP4aをSAM2統合側で評価する（9/18完了、HOTA 53.944）
- [ ] P4aのchunk/TBPTT長、batchサイズ、Mamba内部次元を探索する
- [ ] padding・maskingの挙動と正規化bbox lossのpixel換算を確認する
- [ ] オクルージョンを含む定性的トラッキング可視化を用意する
- [ ] MIRU用の30 FPS動画・追跡結果可視化アプリ・定性候補を準備する
- [ ] SAM2デコーダーへのMamba統合を実装し、統合位置とトークン数の影響を確認する
- [x] 承認済みMOSE specに基づくSAM2全体fine tuningとtemporal Mamba比較（F0/F1、tuning checkpoint選択、200系列lockbox評価）を完了する（2026-10-08、単一seedの主仮説は未支持）
- [ ] Mamba・LSTM・Transformerを同程度GFLOPS・速度条件で比較する
- [ ] state carryのID switch / hidden state contaminationを出力軌跡のシミュレーションで可視化する
- [ ] testデータで追跡性能を評価する
- [ ] SAM2MOTから着想を得た途中検出による補正機構を検討する
- [ ] SAM2/SAMURAI/MOTの物体数変化とマスク特徴量対応を図示し、デコーダー／メモリへのMamba統合位置を比較する

### フェーズ2：修論 / CVPR
- [ ] hidden state contaminationの定義・定量化指標の設計
- [ ] 強制occlusionによる汚染実験（PCA・hidden state norm・cosine similarity可視化）
- [ ] confidence gating / state reset / update skipの効果比較
- [ ] SAM2/SAMURAIへの応用実験と最終評価

## 更新履歴

| 日付 | 内容 |
|------|--------|
| 2026-10-08 | SAM2MOT再現 S4のA5切り分け：Q-Rを補正として入れるとHOTA 69.25（S3比+1.03、論文+1.7と同方向）。S4悪化の原因はconditioning frame追加だったと判明。test S1完了、test S2〜S4（S4は補正方式）を並行実行中。 |
| 2026-10-08 | 16:38 JST、F1 lockboxは245/570対象。F0 fit manifestに欠けるoptimizer情報を、最終checkpoint stateと同一hashのmodel/trainer sourceから再構成して実験ログに記録。freeze対象のmanifestは変更せず保持。 |
| 2026-10-08 | 16:31 JST、F1 lockboxは221/570対象。途中出力全件をfrozen index/frame順、t0除外、J/F/J&Fのfinite/rangeとobject平均、P0/F0とのprompt parityで監査し通過。8件のsource hashも一致。 |
| 2026-10-08 | 16:29 JST、F1 lockboxは216/570対象。途中出力をfrozen index順・frame coverage・有限指標・object平均・P0/F0同一promptで監査し通過。8ファイルのfreeze hashも一致。 |
| 2026-10-08 | 16:27 JST、F1 lockboxは205/570対象で進行中。F1 worker PID 1131047とdetached pipeline PID 878216を再確認。F1-reset・paired/系列長別summaryは未完了。 |
| 2026-10-08 | 16:25 JST、F1 lockboxは195/570対象。途中出力をfrozen trajectory/frame順・t0除外・有限範囲J/F/J&Fとobject mean整合で再監査し通過。全8 frozen source hashも一致。 |
| 2026-10-08 | 16:24 JST、F1 lockboxは187/570対象。P0/F0の保存予測PNGは対象別評価frameと全件一致。F1の完了object分に予測PNG欠落なしで、JSONL記録前の処理中objectに属する17 frame分も逐次出力を確認。F1-reset・paired集計は未完了。 |
| 2026-10-08 | 16:22 JST、F1 lockboxは177/570対象で進行。P0/F0全件の集計監査とF0/F1全学習log監査は通過し、P0/F0全570件とF1評価済み177件で保存prompt seed/tensorが一致。F1-reset・paired集計は未完了。 |
| 2026-10-08 | 16:17 JST、P0/F0 lockbox評価を完了。200動画・570対象でP0 J&F=0.70084、F0=0.73920。F1 lockboxは156/570対象で評価中、F1-resetとpaired集計は未完了。 |
| 2026-10-08 | 13:56 JST、F0 lockboxは102/570対象。worker PID 1099129で評価継続中。P0は200動画・570対象で完了、F1・F1-resetとpaired集計は未完了。 |
| 2026-10-08 | 13:34 JST、MOSE lockbox P0を200動画・570対象で完了。除外0、平均J=0.66448、F=0.73719、J&F=0.70084。F0 lockbox評価を開始し、F1・F1-resetとpaired集計は継続中。 |
| 2026-10-08 | 13:04 JST、P0 lockboxは446/570対象。全行を凍結index prefix、対象一意性、first frame/length/t0除外frame数、finite/in-range J/F/J&Fで監査し通過。 |
| 2026-10-08 | 13:02 JST、P0 lockboxは440/570対象。全440行で凍結index prefix、一意性、first frame/length、t0除外、finite/in-range J/F/J&Fを監査し通過。worker PID 1074677は稼働中。 |
| 2026-10-08 | 13:01 JST、P0 lockboxは431/570対象。全出力を凍結index順・unique object・first-frame/length・t0除外・finite/in-range J/F/J&Fで監査し通過。worker PID 1074677は稼働継続。 |
| 2026-10-08 | 13:00 JST、P0 lockboxは424/570対象。全出力が凍結trajectory順・一意性・初出frame/length・t0除外後frame数・finite/in-range J/F/J&Fに適合することを再監査。 |
| 2026-10-08 | 12:59 JST、P0 lockboxは414/570対象。途中出力全件を凍結trajectory順・unique ID・初出frame/length・t0除外後frame数・finite/in-range J/F/J&Fで検査し通過。worker PID 1074677は稼働中。 |
| 2026-10-08 | 12:58 JST、P0 lockboxは411/570対象。411行すべてを凍結trajectory prefix・unique object IDs・first frame/length・t0除外後frame数・finite/in-range指標で監査し通過。worker PID 1074677は稼働中。 |
| 2026-10-08 | 12:57 JST、P0 lockboxは404/570対象。部分出力全件を凍結trajectory prefix、unique IDs、初出frame/length、t0除外frame数、finite/in-range J/F/J&Fで検査し通過。 |
| 2026-10-08 | 12:56 JST、P0 lockboxが400/570対象に到達。部分出力400行をspec条件で監査し通過。worker PID 1074677は稼働中。 |
| 2026-10-08 | 12:55 JST、P0 lockboxは398/570対象。途中JSONL 398行をfrozen indexのexpected prefix・unique ID・first frame/length・t0除外後frame数・finite/in-range J/F/J&Fで監査し通過。worker PID 1074677は継続中。 |
| 2026-10-08 | 12:54 JST、P0 lockboxは395/570対象。全出力を凍結trajectory prefix、unique ID、first frame、trajectory/scored frame数、finite/in-range J/F/J&Fで再監査し通過。 |
| 2026-10-08 | 12:53 JST、P0 lockboxは390/570対象。全390行が凍結indexの期待prefix、一意対象、初出frame・軌跡長・t0除外後frame数、finite/in-range J/F/J&Fを満たすことを監査。worker PID 1074677は継続中。 |
| 2026-10-08 | 12:51 JST、P0 lockboxは380/570対象。全380行がfrozen indexの期待prefixと一致し、重複なし、first-frame・length・t0除外frame数・有限範囲J/F/J&Fを監査して通過。 |
| 2026-10-08 | 12:48 JST、P0 lockboxは374/570対象。最新partial JSONLを凍結index順・対象一意性・first frame・length・t0除外後frame数・finite/in-range指標で監査し通過。worker PID 1074677はGPU1で継続中。 |
| 2026-10-08 | 12:45 JST、P0 lockboxは366/570対象で部分出力監査を通過。別のSAM2MOT S4評価2件（GPU0）が同時稼働中。MOSE P0はGPU1で独立して進行し、worker PID 1074677を確認。 |
| 2026-10-08 | 12:44 JST、P0 lockboxは360/570対象。途中出力全行を凍結index順・unique ID・初出frame・軌跡長・t0除外後frame数・finite/in-range J/F/J&Fで監査し通過。 |
| 2026-10-08 | 12:42 JST時点でP0 lockboxは351/570対象、worker PID 1074677は稼働中。直前の349件までの部分監査は凍結index順・unique ID・初出frame・軌跡長・t0除外frame数・finite/in-range J/F/J&Fを通過。実装worktreeのgit commit/dirty状態も実験ログへ記録した。 |
| 2026-10-08 | 12:40 JST、P0 lockboxは342/570対象。途中出力を凍結trajectory index順・unique ID・初出frame・軌跡長・t0除外後frame数・finite/in-range J/F/J&Fで再監査し通過。評価worker PID 1074677はGPU1で継続中。 |
| 2026-10-08 | 12:37 JST、P0 lockboxは330/570対象。部分出力を凍結index順・unique ID・初出frame・軌跡長・t0除外frame数・有限範囲のJ/F/J&Fで監査し通過。worker PID 1074677は継続稼働し、pipelineはP0後にF0/F1/F1-resetとpaired summaryを実行する設定。 |
| 2026-10-08 | 12:35 JST、P0 lockboxは315/570対象。部分JSONL 315行は凍結indexの期待prefixと一致し、対象ID重複なし、軌跡長・評価frame数（t0除外）・finite/in-range J/F/J&Fを確認。Comet SDKとユーザー設定ファイルは存在するが、このMOSE runにはlogger未接続。 |
| 2026-10-08 | 12:32 JST時点でP0 lockboxは310/570対象。tmux評価worker PID 1074677が稼働し、GPU1で評価中。GPU0は515 MiB/32 GiB使用で空きがあるが、追加学習は既開始lockboxの主比較に含まれない探索runとなるため開始せず、凍結済み評価を継続する。 |
| 2026-10-08 | MOSE F1 full fitを2,789/2,789 step完了。全log・final checkpoint finiteとprompt replayを監査し、F0はstep2789、F1はstep2000をtuningから選択。選択checkpoint・評価plan・実装hashをlockbox前に凍結し、P0 lockboxを242/570対象まで評価中。 |
| 2026-10-07 | SAM2MOT再現 S4のQ-Rマッチ閾値を0.5に絞った切り分けrunを評価。HOTA 61.70でS4本番（61.85）とほぼ同じで、マッチ閾値の問題ではないと判明。test 35系列の検出生成も完了。 |
| 2026-10-07 | F0 full fitをstep 2,789まで完了。全学習logは連番・finite loss、最終checkpointのmodel/optimizer tensorもfinite。tuning候補step 500〜2,500評価済みで最高はstep 2,500（動画平均J&F 0.76933）。step 2,789 tuning評価37/313、F1 fit indexは400/1,121動画・1,002軌跡。selector・lockbox評価は継続中。 |
| 2026-10-06 | F0はstep 2,001/2,789。学習ログ全件のfinite・連番・sample order一致を再監査し、全て通過。step 1500/2000候補と1600/1700/1800/1900 recovery checkpointを確認。旧root直下のF1 step100成果物は9/30のpilotで、本学習は別の`F1_full_fit/`出力先を使うことを起動queueで確認。 |
| 2026-10-06 | 承認済みMOSE学習を再開。F0はstep 1400 recovery checkpointからstep 1403まで再計算。 |
| 2026-09-30 | MTGでtemporal Mambaの空間情報を保つ設計候補、HOTA 70以上の手法調査、中間発表・研究室見学資料の準備を整理。`meetings/2026-09-30-mtg.md`に記録。 |
| 2026-10-06 | S4の設定でA7の有効・無効を再確認。A7有効でHOTA −0.61、AssA −1.51、IDF1 −1.58と改善せず、A7は無効のまま。 |
| 2026-10-03 | SAM2MOT再現 S4（Q-R）をval 25系列で評価。HOTA 68.22→61.85、AssA −10.15、IDF1 −10.35で逆効果。全段の判定で寄与構造は未再現。`experiments/2026-10-03-sam2mot-s4-qr-results.md`に記録。 |
| 2026-09-30 | A7（低信頼フィルタ）の既定を無効に変更し、spec のA7行を更新。S4の前段はA6のみrunとし、S4実装後にA7の有効・無効を再確認する。 |
| 2026-09-30 | S3のA7切り分けrun（A6のみ）をval 25系列で評価。HOTA 68.22、AssA 64.57、IDF1 75.42。本番runのAssA低下の約2/3がA7由来と判明。`experiments/2026-09-30-sam2mot-s3-a7-ablation.md`に記録。 |
| 2026-09-28 | SAM2MOT再現 S3（CoI）をval 25系列で評価。HOTA 64.32→67.13、MOTA +17.10、IDSW −264、AssA −3.21、DetA +9.19。機構署名のAssA増・DetA不変と順序基準が不成立。結果を`experiments/2026-09-28-sam2mot-s3-coi-results.md`に記録。 |
| 2026-09-27 | SAM2MOT再現spec（`specs/2026-09-08-sam2mot-reproduction-spec.md`）を承認。期限 2026-10-16。本文は変更せず、Object Removal を S1 に含めた実装差分と解決済み未決事項を承認時メモとして追記。 |
| 2026-09-27 | SAM2MOT再現 S0〜S2の結果をexperimentsへ記録。S2の TrackEval を実施し、val 25系列で S1 HOTA 59.21 → S2 64.32（ΔHOTA +5.11、AssA −6.39、IDSW +737）。 |
| 2026-09-18 | MTG: unroll/TBPTTの細かな探索は一旦保留し、YOLO＋MambaとSAM2＋Mambaの比較条件整理、sequence別失敗分析、padding・detach境界の実装確認、SAM2デコーダーへのMamba埋め込み調査を優先する。 |
| 2026-09-18 | `shuffle=True`のP4a epoch100 checkpointをSAM2統合・TrackEval評価。25系列でHOTA 53.944、AssA 60.701、IDF1 62.172、IDSW 1,551。非shuffle P4aのHOTA 54.391を下回った。 |
| 2026-09-11 | MTG: P4a loss振動は固定chunk順序の影響を強く支持。shuffle条件のSAM2評価、ハイパラ探索、padding・maskingとbbox誤差の確認へ進む。View原稿は状態保持型MambaによるSAM2ベース物体追跡を軸にし、デコーダー統合は物体数変化と特徴対応を整理してから検討する。 |
| 2026-09-08 | SAM2MOT-lite実装リポジトリをREADME『実装コードの場所』へ登録し、棚卸しをexperimentsへ保存。検出入力がGTのオラクル条件である点、M6のフラグ不通・M8既定無効、M9未着手、val 15/25系列を確定。 |
| 2026-09-04 | MTG: stateful unroll + TBPTTの実装・学習を確認。detach/reset・内部stateログ・SAM2統合時の性能差を先に検証し、View原稿と研究室見学資料を進める方針を整理。 |
| 2026-08-28 | MTG: state carryの正しい学習、SAM2デコーダー統合、Mamba・LSTM・Transformerの同程度GFLOPS比較、ID switchを起点にした汚染可視化、test評価を優先する方針を確認。 |
| 2026-09-01 | P4aの承認済みspecに基づく実装に着手。L0/P4aのentrypoint・dataset・stateful forward・TBPTT smokeを追加し、実Mamba・CUDA smoke、checkpoint再load、legacy/stateful parityまで確認。 |
| 2026-07-30 | MTG: epoch100をSAM2統合の暫定基準とし、細かな`kf_score_weight`探索よりMambaTrack再現・state carry学習見直しを優先。MIRU定性候補はViewer確認後に採用する。 |
| 2026-07-27 | `best_tracking_hota.pth`（metadata上epoch20）をSAM2で25系列評価。HOTA 54.606でepoch100の55.520を下回った。 |
| 2026-07-23 | P2 cache更新制御を完了。B1 freezeはstate非有限イベントを抑制したが、B2/B3の単純trusted gate/resetは25系列でassociationを悪化させた。 |
| 2026-07-23 | P1 association分離を25系列で確認。A1 HOTA 47.233に対しA2 HOTA 47.910、AssA 30.843、IDF1 47.315、IDSW 2386。P2 cache更新制御の計画化へ進む。 |
| 2026-07-23 | 元MambaStatefulをSAM2/SAMURAIへ最小統合し、25系列でHOTA 55.520、IDF1 64.154を確認。epoch100固定の統合確認値として記録した。 |
| 2026-07-23 | MTG: scale・association・state carry学習を分離して切り分ける方針を確認。SAM2統合結果とMambaTrack系baselineの再現性を優先し、その後に入力混合・quality-aware state update・TBPTTをspec化して検証する。MIRUポスターは自前の時系列結果と簡略図へ修正する。 |
| 2026-07-22 | P1 association分離を3系列で完了。A1 HOTA 49.666に対しA2 HOTA 54.870、AssA 36.229、IDF1 53.660、IDSW 94。P2 cache更新制御は別spec・承認待ち。 |
| 2026-07-21 | P0.5としてMambaTrack / TrackSSM / MambaStatefulのDanceTrack val 25系列as-is比較を完了。次はP1 association分離の診断へ進む。 |
| 2026-07-21 | teacher forcing/free-running横断調査をBatch 4まで完了。association分離、cache更新ガード、入力分布混合、stateful TBPTTを段階的に検証するspec候補を作成。 |
| 2026-07-16 | MTG: state carryの推論単体検証を先行し、小規模過学習、teacher forcing/free running調査、validation頻度整理、MIRUポスター再構成を進める方針を決定。 |
| 2026-07-15 | TrackEval CLI/API parityとMamba側評価adapterのfull-val parityを確認。3sequence timingでtracker推論316.973秒、TrackEval3.490秒を計測し、候補周期1epoch smokeを確認。 |
| 2026-07-09 | MTG: validation 実装の成立を確認。TrackEval 側の関数化検証、tracking validation の命名整理、計算時間 profiling、MIRU ポスター構成を次課題として整理 |
| 2026-07-07 | 4ヶ月分の議事録分析をもとにREADME・マイルストーン・概要を更新。meetings/experiments/specsへ研究内容を整理 |
| 2026-07-07 | プロジェクト作成 |
| 2026-07-02 | MTG: TrackSSMの入出力形式の違いを発見、LRスケジューラ問題を確認、val設計の方針を決定、hidden state contamination調査開始 |
