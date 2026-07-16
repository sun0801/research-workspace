---
project: sam2-mamba-motion-tracking
status: active
summary: state carry評価のframe 6付近でNaN退化を確認。次は小規模過学習でtracker推論を単体検証し、teacher forcing等の学習方法を整理する。
created: 2026-07-07
last_updated: 2026-07-16
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
| SAMURAI + state carry型Mamba（`samurai_mamba_stateful`モード） | 🔧 インターフェース実装済み・constant-velocity fallback動作確認済み |
| `MambaStatefulMotionFilter`の状態管理 | 🔧 実装着手中（ステップ1完了） |
| MOT推論エントリ | `scripts/main_inference_mot.py` |

## 現在の状況

**7/2 MTG後の状況**：state carry型Mambaは100エポックで収束しかけているが、LRスケジューラがほぼ固定になっており過学習の可能性が高い。TrackSSMは入力形式の違いが発覚し実験設定の見直しが必要。public validationの設計（5エポックごとのHOTA評価）が次の実装課題。

**7/9 MTG後の状況**：`val loss` と tracking 指標ベースの validation を学習導線へ組み込む実装自体は成立した。次の課題は、TrackEval 側の関数化が単体で正しいかを切り分けること、tracking validation の命名整理、そして計算時間増加の原因を profiler で特定すること。MIRU ポスターは「SAM2 / SAMURAI の改善」を主題に据え、定量表に加えてオクルージョン時の定性的可視化も準備する。

**7/15時点**：TrackEvalのCLI/API parityを1および3 sequenceで確認し、Mamba側ではtracker推論 subprocessを維持したままTrackEval評価を直接関数呼び出しへ置換した。既存25 sequence tracker出力でCLIとadapterのsummaryが一致した。計測コードを追加し、MambaStatefulの1epoch smokeと3sequence単独計測を実施した。tracker推論は316.973秒、TrackEvalは3.490秒で、今回の条件ではtracker推論が主要コストだった。候補周期の1epoch smokeも通過したが、100epoch本学習とfull valは未実施。

**7/16 MTG後**：state carryのepoch間MOT Metrics不変について、TrackEvalの計算導線ではなくtracker推論側を切り分ける方針を決定した。小規模データへの過学習と同一データでのtracker推論を先に行い、学習・推論・評価を分離して確認する。state carryの学習では、sliding window型と異なり状態を時系列に引き継ぎながら各時刻の損失を扱う必要があるため、RNN/LSTMのteacher forcing・free runningを含む標準的な方法を調査する。MIRUポスターはSAM2/SAMURAIの改善を主軸に、課題・従来法・提案法の簡略図と大きな文字で再構成する。

研究の問い：

> MOTにおいて，state carry型Mambaのhidden stateをtrackごとに持続的に保持することは有効か？不安定な場合，その原因はhidden state contaminationなのか？それをどう検出・抑制すればよいか？

詳細は [`specs/2026-07-07-state-carry-research-direction.md`](specs/2026-07-07-state-carry-research-direction.md) を参照。

## マイルストーン

### フェーズ1：MIRU / ポスター
- [x] SAM2 / SAMURAIのMOT適用時の問題を把握する（4月完了）
- [x] Mamba tracking手法の調査・sliding window型 / state carry型の整理（5月末完了）
- [x] SAMURAI+Mambaの初期実験（HOTA: SAM2=0.46, SAMURAI=0.54, SAMURAI+Mamba=0.53）
- [x] state carry型Mambaの実装・100エポック学習（7/2時点で収束しかけ）
- [x] `val loss` と tracking 指標ベース validation の学習導線への実装・smoke test（7/9確認）
- [ ] MambaTrack / TrackSSM / State carry型の公平な比較実験
- [ ] 入力スケーリング（bbox vs bbox delta）の根拠整理
- [x] TrackEval 側の関数化導線を単体で検証し、統合時の問題を切り分ける
- [x] tracking validation の命名整理（`mot_metrics` への統一）と運用方針の明確化
- [ ] **validation運用の安定化（過学習チェック用 + tracking 指標評価頻度の調整）**
- [ ] **State carryのLRスケジューラ修正（warmup比率・decay形状の見直し）**
- [ ] tracking validation の計算時間増加要因を profiler で特定する
- [x] state carryのepoch間MOT Metrics不変について、frame 6付近のNaN・matching失敗・track再生成を診断する（7/16確認）
- [ ] state carryの小規模過学習と同一データでのtracker推論を確認する
- [ ] state carryの学習方法をRNN/LSTMのteacher forcing・free running等と比較整理する
- [ ] オクルージョンを含む定性的トラッキング可視化を用意する
- [ ] MIRU原稿の完成

### フェーズ2：修論 / CVPR
- [ ] hidden state contaminationの定義・定量化指標の設計
- [ ] 強制occlusionによる汚染実験（PCA・hidden state norm・cosine similarity可視化）
- [ ] confidence gating / state reset / update skipの効果比較
- [ ] SAM2/SAMURAIへの応用実験と最終評価

## 更新履歴

| 日付 | 内容 |
|------|--------|
| 2026-07-15 | TrackEval CLI/API parityとMamba側評価adapterのfull-val parityを確認。3sequence timingでtracker推論316.973秒、TrackEval3.490秒を計測し、候補周期1epoch smokeを確認。 |
| 2026-07-16 | MTG: state carryの推論単体検証を先行し、小規模過学習、teacher forcing/free running調査、validation頻度整理、MIRUポスター再構成を進める方針を決定。 |
| 2026-07-09 | MTG: validation 実装の成立を確認。TrackEval 側の関数化検証、tracking validation の命名整理、計算時間 profiling、MIRU ポスター構成を次課題として整理 |
| 2026-07-07 | 4ヶ月分の議事録分析をもとにREADME・マイルストーン・概要を更新。meetings/experiments/specsへ研究内容を整理 |
| 2026-07-02 | MTG: TrackSSMの入出力形式の違いを発見、LRスケジューラ問題を確認、val設計の方針を決定、hidden state contamination調査開始 |
| 2026-07-07 | プロジェクト作成 |
