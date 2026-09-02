---
project: sam2-mamba-motion-tracking
status: active
summary: state carryの正しい学習、SAM2デコーダー統合、Mamba・LSTM・Transformer比較、汚染可視化を優先して次段階の実験へ進む段階。
created: 2026-07-07
last_updated: 2026-09-01
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

## 現在の状況

**7/2 MTG後の状況**：state carry型Mambaは100エポックで収束しかけているが、LRスケジューラがほぼ固定になっており過学習の可能性が高い。TrackSSMは入力形式の違いが発覚し実験設定の見直しが必要。public validationの設計（5エポックごとのHOTA評価）が次の実装課題。

**7/9 MTG後の状況**：`val loss` と tracking 指標ベースの validation を学習導線へ組み込む実装自体は成立した。次の課題は、TrackEval 側の関数化が単体で正しいかを切り分けること、tracking validation の命名整理、そして計算時間増加の原因を profiler で特定すること。MIRU ポスターは「SAM2 / SAMURAI の改善」を主題に据え、定量表に加えてオクルージョン時の定性的可視化も準備する。

**7/15時点**：TrackEvalのCLI/API parityを1および3 sequenceで確認し、Mamba側ではtracker推論 subprocessを維持したままTrackEval評価を直接関数呼び出しへ置換した。既存25 sequence tracker出力でCLIとadapterのsummaryが一致した。計測コードを追加し、MambaStatefulの1epoch smokeと3sequence単独計測を実施した。tracker推論は316.973秒、TrackEvalは3.490秒で、今回の条件ではtracker推論が主要コストだった。候補周期の1epoch smokeも通過したが、100epoch本学習とfull valは未実施。

**7/16 MTG後**：state carryのepoch間MOT Metrics不変について、TrackEvalの計算導線ではなくtracker推論側を切り分ける方針を決定した。小規模データへの過学習と同一データでのtracker推論を先に行い、学習・推論・評価を分離して確認する。state carryの学習では、sliding window型と異なり状態を時系列に引き継ぎながら各時刻の損失を扱う必要があるため、RNN/LSTMのteacher forcing・free runningを含む標準的な方法を調査する。MIRUポスターはSAM2/SAMURAIの改善を主軸に、課題・従来法・提案法の簡略図と大きな文字で再構成する。

**7/21 調査完了**：teacher forcing/free-runningの横断調査をBatch 4まで完了した。最優先の改善候補は、予測bboxをhard IoU matchingの主位置から外すassociation分離（P1）である。その後、confidence/match qualityによるcache freeze・reset（P2）、入力分布混合（P3）、明示的stateful unroll + TBPTT（P4）を独立に比較する。実装は未開始であり、P1だけを対象にした承認待ちとする。

**7/21 P0.5完了**：既存のDanceTrack val 25系列出力を同一TrackEval条件で比較した。HOTAはMambaTrack 33.837、TrackSSM 32.783、MambaStateful 47.293。MambaStatefulが高かったが、checkpoint provenance、入力形式、モデル構造、prediction-primary associationが未分離のため、学習方式の優位性とは解釈しない。次はP1を診断用baselineとして個別に検証する。

**7/23 P1 25系列確認完了**：同一epoch100 checkpoint・detector入力・config・scale・lifecycle・state/cache更新・TrackEval条件で、prediction-primary A1とlast accepted observation A2をDanceTrack val 25系列で比較した。A1はHOTA 47.233、A2はHOTA 47.910、AssA 30.843、IDF1 47.315、IDSW 2386となり、A2はA1に対してHOTA +0.677、AssA +0.936、IDF1 +1.429、IDSW -192を示した。効果は3系列より小さく系列依存もあるが、P1仮説を25系列aggregateでも支持する。P2 cache更新制御のspec化へ進む。

**7/23 P2完了**：P1 A2を固定し、B0 self-update、B1 missing freeze、B2 trusted detector match gate、B3 prolonged-untrusted resetを3系列・25系列で診断した。25系列ではB0 HOTA 47.910に対しB1 48.035で、state非有限イベントは4,515から115へ減少した。一方、B2はHOTA 46.962、B3は46.855で、AssA/IDF1が低下しIDSWが増加した。missing freezeはcontamination抑制の根拠を与えたが、単純なquality gate/resetは採用せず、P3/P4へ自動移行しない。

**7/23 SAM2最小統合完了**：元repoのepoch100 `MambaStateful`をSAM2/SAMURAIへ移植し、DanceTrack val 25系列を推論・評価した。HOTA 55.520、AssA 62.482、IDF1 64.154、IDSW 1,535で、全candidate debug行でcheckpointロード済み、fallbackなしを確認した。これはepoch100固定の統合確認値であり、SAM2上の改善量やbest-HOTA checkpointの結果ではない。

**7/27 checkpoint比較完了**：元repoの`best_tracking_hota.pth`（metadata上epoch20）を同じSAM2条件で評価したところ、HOTA 54.606、AssA 61.691、IDF1 62.813、IDSW 1,525となった。epoch100よりHOTAは0.914低く、元repoのbest-HOTA checkpointがSAM2上でも最良とは限らないことを確認した。

**7/30 MTG後**：SAM2統合ではepoch100を暫定基準として扱い、元repoのbest-HOTA checkpointをSAM2上の最良とは断定しない方針を確認した。`kf_score_weight`の細かな探索は優先せず、MambaTrackの論文水準再現とstate carry型のrecurrent学習・TBPTTを含む学習方法の見直しへ進む。MIRUでは30 FPS動画と追跡結果可視化アプリを使い、定性候補はViewerで人手確認してから採用する。

**8/28 MTG後**：MIRUで受けた意見を踏まえ、state carry型Mambaの学習方法の見直しを最優先し、SAM2デコーダーへのMamba統合を10月中旬頃までの実装目標とした。Mamba・LSTM・Transformerは同程度GFLOPSと速度を揃えて比較する。hidden state contaminationは、まずID switchを人工的に挿入した出力軌跡のシミュレーションで定義・可視化し、SAM2MOTは再現ではなく途中検出による独自補正の着想として扱う。Viewの2ページ原稿作成とtestデータ評価も進める。

研究の問い：

> MOTにおいて，state carry型Mambaのhidden stateをtrackごとに持続的に保持することは有効か？不安定な場合，その原因はhidden state contaminationなのか？それをどう検出・抑制すればよいか？

詳細は [`specs/2026-07-07-state-carry-research-direction.md`](specs/2026-07-07-state-carry-research-direction.md) を参照。

**9/2 P4a closeout / P4b初回比較完了**：P4aにL0互換train logging、train/val splitを分離したGT-only validation、horizon 1/4/8/16/32のfree rollout、checkpoint SHA256 manifestを追加した。実データepoch5でvalidation loss 0.048975、state finite rate 1.0、全rollout horizonの発散率0を確認した。P2-B1固定条件のDanceTrack val 25系列ではL0 epoch5 HOTA 53.971、P4a epoch5 HOTA 53.240で、P4aはHOTA -0.731、AssA -0.659、IDF1 -0.800、IDSW +2となった。epoch100本学習の結果とは分けて扱う。

**9/1 P4a実装着手**：承認済みspecに従い、L0固定windowの明示entrypoint（`train_mamba_window.py`）を残したまま、GT-only stateful unroll dataset、微分可能state forward、TBPTT学習entrypoint、設定、smoke runnerをMamba_Trackersへ追加した。構文・dataset生成・CPU stubでのstate parity/backwardに加え、実Mamba・CUDA上のP4a/L0 smoke、checkpoint再load、legacy/stateful parityを確認済み。

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
- [ ] オクルージョンを含む定性的トラッキング可視化を用意する
- [ ] MIRU用の30 FPS動画・追跡結果可視化アプリ・定性候補を準備する
- [ ] SAM2デコーダーへのMamba統合を実装し、統合位置とトークン数の影響を確認する
- [ ] Mamba・LSTM・Transformerを同程度GFLOPS・速度条件で比較する
- [ ] state carryのID switch / hidden state contaminationを出力軌跡のシミュレーションで可視化する
- [ ] testデータで追跡性能を評価する
- [ ] SAM2MOTから着想を得た途中検出による補正機構を検討する

### フェーズ2：修論 / CVPR
- [ ] hidden state contaminationの定義・定量化指標の設計
- [ ] 強制occlusionによる汚染実験（PCA・hidden state norm・cosine similarity可視化）
- [ ] confidence gating / state reset / update skipの効果比較
- [ ] SAM2/SAMURAIへの応用実験と最終評価

## 更新履歴

| 日付 | 内容 |
|------|--------|
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