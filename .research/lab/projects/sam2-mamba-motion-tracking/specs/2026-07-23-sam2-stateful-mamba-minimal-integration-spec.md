---
date: 2026-07-23
project: sam2-mamba-motion-tracking
source: P1/P2 results and SAM2 integration audit
status: draft
tags: [spec, sam2, samurai, state-carry, inference-only, minimal-integration]
---

# SAM2/SAMURAI stateful Mamba 最小統合 Spec

## 方針

最初の目的は、P1/P2を同時に移植することではなく、Mamba_Trackersで学習済みの元のMambaStateful state carry方式をSAM2/SAMURAI上で動かし、実験結果を得ることである。

初期実装ではSAM2の既存mask候補選択・object ID処理を維持する。P1 association、P2 freeze、trusted gate、reset、quality-aware updateは初期実装に含めない。

外部repo・SAM2 repoの変更は、spec承認と実装開始承認後に行う。

## 目的

再学習なしで、既存epoch100 checkpointをSAM2/SAMURAIのstateful motion priorとして読み込み、以下を最短経路で確認する。

- checkpoint-compatibleなMambaStatefulが実際にロードされる
- object IDごとにstate/cacheを持続できる
- SAM2の既存候補選択に対してone-token state carry予測が機能する
- constant-velocity fallbackではないstateful Mamba結果を保存・評価できる

## 背景と既知の制約

Mamba_Trackers側のP1/P2は、まず独立した推論診断として完了している。P1はassociation改善、P2aはmissing freezeによるstate非有限イベント削減を示したが、P2の単純trusted gate/resetはassociationを悪化させた。そのため、SAM2統合の初期段階ではP1/P2を混ぜず、元方式の移植成功を先に確認する。

SAM2側には`samurai_mamba_stateful`の入口があるが、現在の`MambaStatefulMotionFilter`は暫定architectureとconstant-velocity fallbackを含む。fallbackで動いた状態を「MambaStateful移植成功」と扱ってはならない。

## 固定するcheckpointとarchitecture

- external repo: `/mnt/HDD10TB-2/aburatani/2025_09_aburatani_Mamba_Trackers`
- SAM2 repo: `/mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2`
- checkpoint: `ssm_tracker/saved_ckpts/mamba_stateful_dancetrack/epoch100.pth`
- model: `MambaStateful`
- `d_m=256`
- `d_state=16`
- `d_conv=4`
- `L=3`
- `expand=2`
- head: `LayerNorm -> Linear -> LeakyReLU -> Linear`
- input token: 4次元 bbox
- bbox scale: `1`
- delta scale: `50`
- `max_inference_seqlen=2048`
- cache: object IDごとの`InferenceParams`、one-token state carry

SAM2既存configの`d_model=512`や`scale_factor=50`を流用しない。checkpointと一致する専用設定を作成する。strict loadでmissing/unexpected keyが出た場合は実験を停止し、fallbackへ silently fallbackしない。

## 初期実装の挙動

### State管理

- `obj_id -> state`の対応を維持する。
- stateにはlast bbox、pending delta、InferenceParams、cache offset、model load statusを保存する。
- object IDが新規になった場合はstateを初期化する。
- object IDが終了した場合はstateを破棄する。
- object ID間でcacheを共有しない。

### 推論

- SAM2が現在選択しているmask candidateをbboxへ変換する。
- candidateがacceptedされたフレームでは、そのbboxをMambaStatefulへ1 token入力する。
- Mambaの出力deltaから次bboxを予測する。
- 初期実装では、P1のlast accepted observation associationを行わず、SAM2既存のcandidate選択を使う。
- 初期実装では、P2のmissing freezeやtrusted gateを行わず、従来のstate update規則を使う。
- prediction処理自体はstate/cacheを追加更新しない。

### Fallback

- `mamba_ssm`未導入、checkpoint不一致、model load failureの場合は実験結果を生成してよいが、MambaStateful結果とは分類しない。
- fallback使用数をdiagnosticsとmanifestへ記録する。
- 本specの成功条件はfallback使用数0である。

## 変更範囲

### SAM2 repoで変更候補

- `sam2/utils/mamba_stateful_motion_filter.py`
  - Mamba_Trackersと同じmodel architecture、checkpoint load、one-token inference cacheを実装
  - object stateの保存・復元・diagnosticsを実装
- `sam2/modeling/sam2_base.py`
  - 既存SAMURAI候補選択からstateful filterを呼ぶ最小接続
  - P1/P2のcandidate selection変更は行わない
- `sam2/configs/samurai_mamba_stateful/*.yaml`
  - checkpoint path、d_m、scale、stateful runtime設定を追加
- `scripts/main_inference_mot.py`
  - 必要最小限のrun_id、manifest、diagnostics保存
- 新規のSAM2用実験スクリプトまたはrun wrapper

### 変更しないもの

- Mamba_Trackers側の学習コードとcheckpoint
- MambaTrack、TrackSSM
- SAM2 image encoder、mask decoder、SAM2 memoryの基本構造
- P1 observation-primary association
- P2 missing freeze、trusted gate、reset、quality-aware update
- P3 input distribution mixing
- P4 teacher forcing、free-running、TBPTT、training forward
- 既存SAM2 baseline mode

## 比較条件

| 条件 | 内容 |
|---|---|
| S0 | 既存SAM2/SAMURAI baseline |
| S1 | 既存SAM2候補選択 + checkpoint-compatible MambaStateful state carry |

S1が動作した後に、別specでP1/P2を段階的に追加する。初期結果ではP1/P2の効果を主張しない。

## 検証手順

1. checkpointのhash、外部repo commit、SAM2 commit、dirty diffをmanifestへ保存する。
2. unit testで以下を確認する。
   - strict checkpoint load
   - bbox xyxy/xywh変換
   - scale bbox=1 / delta=50
   - 1 tokenごとのcache offset増加
   - prediction時にcache offsetが二重に進まない
   - object IDごとのcache分離
   - state finite
3. replay testで固定bbox列を外部repo版とSAM2版へ入力し、prediction deltaを許容誤差内で比較する。
4. `dancetrack0004, dancetrack0005, dancetrack0007`でS0/S1を比較する。
5. 3系列でcheckpoint load、fallback=0、output、diagnostics、TrackEval導線を確認する。
6. 問題がなければP1/P2と同じ25系列を`--SEQ_INFO`で明示して評価する。

## 評価指標

- HOTA、DetA、AssA
- IDF1、IDSW、IDs、MOTA
- per-sequence metrics
- checkpoint load success
- fallback count
- accepted observation count
- object ID数
- state finite rate
- object IDごとのcache offset continuity
- 推論時間

SAM2 mask出力を主対象とするため、可能な場合はmask IoU、object score、candidate selection rateも保存する。TrackEvalを使う場合、共有seqmapを変更せず`--SEQ_INFO`で系列を指定する。

## 成功・失敗基準

### 必須成功

- epoch100 checkpointをstrict loadできる
- fallback使用数が0である
- replay testで外部repo版とSAM2版のdeltaが許容誤差内で一致する
- object ID間のcache混線がない
- 3系列で最後まで推論でき、outputとdiagnosticsが保存される

### 研究上の初期成功

- S1がSAM2上で再現可能なstate carry型Mambaとして動作する
- S0/S1の比較を25系列まで同一条件で実施できる
- P1/P2を入れていない初期state carry baselineとして結果を解釈できる

### 失敗

- checkpoint不一致をfallbackで隠す
- SAM2側だけ異なるarchitecture、scale、headを使う
- predictionとstate updateのタイミングが外部repo版と一致しない
- object ID間でcacheが共有される
- 既存checkpoint、track output、TrackEval outputを削除・上書きする

## 再学習の扱い

初期実装では再学習しない。Mamba_Trackersのepoch100 checkpointをそのまま推論に使う。

再学習が必要になるのは、次の段階である。

- SAM2向けbbox/mask候補分布へ再適応する
- quality情報を入力特徴へ追加する
- teacher forcing、TBPTT、loss、training data distributionを変更する

## 成果物とprovenance

各runはSAM2側の新規run_idディレクトリに保存する。

- exact command
- SAM2 commitとdirty diff
- Mamba_Trackers commit、checkpoint path、checkpoint hash
- config copy
- S0/S1 mode
- sequence list
- checkpoint load log
- fallback count
- state diagnostics JSON
- tracking output
- TrackEval summary/detailed output

既存成果物を削除・上書きしない。SAM2 repoに既存の未commit変更がある場合は、実装開始前に差分を保存し、無関係な変更を上書きしない。

## 後続拡張

S1の再現後に、以下を別段階で追加する。

- P1: last accepted observation association
- P2a: missing freeze
- quality-aware state update: accepted observationの保持とMamba state更新の分離

P2 B2/B3の単純trusted gate/resetは、Mamba_Trackers側でassociationを悪化させたため、初期SAM2統合へ直接入れない。

## Implementation Gate

- [x] P1/P2結果を確認した
- [x] SAM2側の現状実装を読み取り専用で確認した
- [x] 最短経路の変更範囲を限定した
- [x] 再学習なしの初期検証方法を定義した
- [ ] ユーザーによる本specの確認・承認
- [ ] SAM2 repoの変更対象と範囲の最終確認
- [ ] SAM2側実装開始承認

## 関連ファイル

- `specs/2026-07-23-p2-cache-update-control-spec.md`
- `experiments/2026-07-23-p2-cache-update-control.md`
- `experiments/2026-07-23-p1-association-separation-25seq.md`
- SAM2: `/mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2`
- Mamba_Trackers: `/mnt/HDD10TB-2/aburatani/2025_09_aburatani_Mamba_Trackers`
