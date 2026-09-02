---
date: 2026-09-01
project: sam2-mamba-motion-tracking
source: ../secretary/notes/brainstorm/2026-09-01-p1-p2-and-training-direction.md
status: draft
tags: [spec, p4a, state-carry, recurrent-training, tbptt, mamba]
---

# P4a: Stateful Unroll + TBPTTによるMamba予測器学習 Spec

## ステータス

P4のうち、まずMamba予測器単体の学習方法を検証するための個別spec。P4bのtracker/SAM2統合は本specの対象外とする。

本specはユーザー承認済みで、2026-09-01に実装を開始した。外部実装の対象範囲・検証方法・実装開始承認はImplementation Gateに記録する。

## 背景

現行の`MambaStateful`学習は、`StatefulTrajDataset`から固定長のGT bbox windowを取り出し、各batchを独立に`model.forward(x, label)`へ入力している。dataloaderもshuffleされ、window外へstateをcarryしない。

一方、推論時はtrackごとにMambaの`InferenceParams` cacheを持ち、accepted observationやself predictionをフレーム間でstateへ入力する。このため、現状は「sliding-window的な学習」と「state carryによる推論」の間に不一致がある。

P1/P2ではassociationとcache更新の診断を完了している。P1 A2とP2 B1はreferenceとして固定し、P4aではtracker側のassociation・cache規則を変更せず、学習方法だけを検証する。

## 目的

同一モデル・同一入力形式・同一データ条件で、以下を比較する。

1. 現行のfixed-window GT学習（L0）
2. track/video単位でstateをcarryするrecurrent unroll + TBPTT学習（P4a）

これにより、state carry学習そのものが長期rolloutの予測安定性を改善するかを、入力分布混合やassociation変更と分離して確認する。

## 検証したい問い

現行のfixed-window学習を、明示的なstateful unroll + TBPTT学習へ変更すると、推論時のstate carryに近い条件で、Mambaの長期rollout性能とstate安定性は改善するか。

## 仮説

学習時にも同一trackのstateを時系列にcarryし、chunk境界でのみ勾配をdetachすれば、fixed-window学習よりも推論時のstate carryに適した予測器になる。特に、長いfree rolloutでの誤差蓄積、state normの発散、非有限値の発生が抑制される可能性がある。

ただし、P4aの初期比較では入力をGT-onlyに固定する。accepted detectionやself predictionを学習入力へ混ぜる効果はP3として別に検証する。

## 用語と動作定義

### Unroll

同一trackのbbox列を時系列順に1時刻ずつ処理し、各時刻のstateを次の時刻へ渡すこと。異なるtrackやvideoのstateは共有しない。

### Detach

stateの数値は次のchunkへ渡すが、過去chunkの計算グラフとの接続だけを切ること。stateをゼロへ戻すresetとは区別する。

### TBPTT

長い時系列を複数chunkに分け、chunk内ではunrollして逆伝播し、chunk境界でstateをdetachする学習方法。本specでは、stateをcarryしながら勾配の逆伝播範囲を有限長に制限する。

## 対象範囲

### 対象

- MambaStatefulの学習用forward
- 時系列順のdataset samplerまたはbatch構成
- 明示的な学習用stateの入出力
- TBPTTのdetach処理
- loss mask、state/gradient finite性のlogging
- predictor単体のteacher-forced評価とfree-rollout評価

### 対象外

- P1 association変更
- P2 missing freeze、trusted gate、reset
- P3のGT / accepted-detection surrogate / self prediction混合
- SAM2/SAMURAIへの統合（P4b）
- SAM2 decoderへの統合
- LSTM・Transformerとの比較
- Mamba内部architectureの変更
- detector、ReID、track lifecycle、TrackEval実装の変更

## 比較条件

### L0: 現行fixed-window baseline

- `train_mamba_window.py`と`StatefulTrajDataset`を使用
- 既存の`train_stateful.py`は、当面このfixed-window経路への互換entrypointとして残す
- GT bbox入力、教師はGT next bbox delta
- bbox scale `1`、delta scale `50`
- 現行Mamba architectureを維持: `d_m=256`, `d_state=16`, `d_conv=4`, `expand=2`, `L=3`
- optimizer、learning rate、loss、epoch数は現行設定を初期値として維持
- 各windowを独立にforwardし、window外のstate carryは行わない

### P4a: recurrent unroll + TBPTT

- L0と同じMamba architecture、GT入力、target、scale、optimizerを使用
- 同一track・同一videoの時間順chunkからbatchを構成
- sequence / track開始時にstateをzero初期化
- chunk内ではstateを各時刻へcarry
- chunk境界ではstateをdetachして次chunkへ渡す
- 異なるtrack・video間でstateをcarryしない
- 初期比較ではP3の入力分布混合を行わず、GT-only teacher forcingとする
- 初期実験の候補値は`unroll_length=48`、`tbptt_length=12`とする。GPUメモリまたは実装上の制約で変更する場合は、run metadataへ記録する
- 現行設定の`loss_start_index=4`を初期値とし、warm-up後の全有効時刻へlossを置く
- padding・不足時刻はloss maskで除外する

## 学習用stateの要件

推論用の`InferenceParams` cacheを、そのままautogradのstateとして再利用しない。P4aでは、学習用forwardがstateを明示的に受け取り、次のstateを返す形式を検討する。

必須要件:

- stateの初期化、入力、出力が明示されている
- chunk境界でstateをdetachできる
- stateをresetした場合とcarryした場合を区別できる
- state更新がautograd上で追跡可能である
- `torch.no_grad()`前提の推論cacheと学習用stateを混同しない
- state shapeがbatch内のtrackと対応している

Mamba実装のAPI上、既存forwardから安全な微分可能stateを取り出せない場合は、InferenceParamsを無理に流用せず、学習用wrapperまたは学習用state更新経路を別に定義する。その場合も、fixed-window forwardとの数値parityを先に確認する。

## 実装候補ファイル

Mamba_Trackers repo:

- `ssm_tracker/train_mamba_window.py`: L0のfixed-window学習。既存`train_stateful.py`から移行する実体
- `ssm_tracker/train_mamba_stateful.py`: P4aの時系列順batch、unroll、TBPTT、detach、logging
- `ssm_tracker/train_stateful.py`: 既存利用者向けのfixed-window互換entrypoint。P4aの実体にはしない
- `ssm_tracker/models/MambaStateful.py`: 学習用state入出力forwardとloss接続
- `ssm_tracker/dataset/stateful_unroll_dataset.py`: track/video単位の時系列chunk sampler
- `ssm_tracker/cfgs/MambaStatefulTBPTT.yaml`: P4a設定。既存設定を直接上書きせず、P4a用設定を明示する
- `experiments/`: smoke・pilot・再現用runner

SAM2 repoはP4aでは変更しない。

## 段階的な実施内容

### P4a-0: 現行L0の回帰確認

- 現行コード・設定で短いtraining smokeを実行
- loss、checkpoint、validation lossがfiniteであることを確認
- 固定bbox列に対するone-step出力を保存
- commit、config、dataset split、seedをmanifestへ記録

### P4a-1: 学習用state forwardの単体確認

- 1 trackの短いbbox列でstateful forwardを実行
- state reset時とcarry時の出力を区別
- chunkを分割してcarryした出力と、同じ長さを一括処理した出力を比較
- state、output、loss、gradientがfiniteであることを確認
- 異なるtrackを交互に処理してもstateが混線しないことを確認

### P4a-2: forward parityとTBPTT smoke

- carryを無効化したP4a forwardとL0の同一window forwardを比較
- 同一入力・同一初期stateで出力差を記録
- `tbptt_length=12`の短いunrollでbackwardを実行
- chunk境界でstateの値は継続し、gradient graphだけが切れることを確認
- gradient norm、state norm、lossのfinite性を確認

### P4a-3: predictor単体比較

L0とP4aを同じtrain/val split、seed、architecture、optimizer条件で比較する。

評価:

- teacher-forced one-step bbox IoU
- delta MAEまたはSmooth L1
- free rolloutのhorizon別IoU / MAE: `1, 4, 8, 16, 32`
- rollout発散率、NaN/Inf率
- state norm、gradient norm、cacheではなく学習用stateのfinite率
- 学習時間、GPUメモリ使用量

P4aで学習したcheckpointのtracker評価は、P4a-3のpredictor単体検証を通過した後にP4bで行う。

## 固定条件

- dataset annotation: 現行MambaStateful学習と同じもの
- train/val split: 現行設定から変更しない
- bbox入力形式: 現行の4次元xywh
- bbox scale: `1`
- delta scale: `50`
- architecture: 現行epoch100 checkpointと同じ構成
- 初期入力: GT-only teacher forcing
- P1/P2 tracker変更: なし
- detector / association / TrackEval: P4aでは使用しない
- seed: L0とP4aで固定し、manifestへ保存

## 成功・失敗の判断基準

### 必須成功条件

- carry無効時のforward parityを確認できる
- 学習用state、loss、gradientがfiniteである
- chunk境界のdetach後もstate値が意図どおりcarryされる
- track/video境界でstateがresetされる
- 異なるtrack間でstate混線がない
- P4a checkpointを保存・再読み込みできる

### 研究上の成功候補

- L0に対してP4aのfree rollout長期horizon誤差または発散率が改善する
- one-step性能を大きく損なわずにstateful rolloutが安定する
- state normやgradientの異常がL0より増えない

研究上の改善が得られなくても、必須成功条件を満たしていれば、stateful学習自体は成立したというnegative resultとして記録する。

### 中止条件

- parity不一致の原因が未解決
- loss、gradient、stateにNaN/Infが発生
- track/videoをまたいだstate混線が発生
- 学習用forwardが推論用InferenceParamsへ暗黙依存する
- P3の入力混合、P1/P2のtracker変更、architecture変更が同時に混入する

中止した場合はP4bやSAM2統合へ進まず、state表現・detach境界・chunk構成の診断へ戻る。

## 成果物とprovenance

各runは既存成果物と別のrun_idで保存する。

- command line
- configのコピー
- dataset splitとsequence/track sampler条件
- seed
- repo commitとdirty diff
- model architecture
- unroll length、TBPTT length、loss start index
- checkpointとhash
- predictor metrics
- state norm、gradient norm、finite性ログ
- smoke/parity結果

学習ログやcheckpoint本体は必要に応じてartifact directoryへ保存し、Gitにはソースコード・設定・再現用scriptのみをコミットする。

## 次フェーズへの条件

### P3へ進む条件

P4aのGT-only学習が成立し、L0/P4aの差を解釈できること。P3ではaccepted-detection surrogateとself predictionを別々に導入し、P4aの効果と混ぜない。

### P4bへ進む条件

P4a checkpointでforward parity、finite性、free rollout評価が成立していること。P4bではassociation・cache update・detector・TrackEval条件を固定し、学習checkpointだけを差し替える。

## Implementation Gate

- [x] P4aの問い・仮説・対象範囲を定義
- [x] L0との比較条件を定義
- [x] unroll、detach、TBPTTのstate境界を定義
- [x] predictor単体の評価指標と中止条件を定義
- [x] P3、P4b、SAM2統合を対象外として分離
- [x] ユーザーによるP4a spec内容の最終確認（2026-09-01、実装開始指示）
- [x] Mamba_Trackers repoの変更対象ファイルの最終確定（上記の実装候補ファイル）
- [x] 検証runner・smoke方法の最終確定（P4a-2のparity/TBPTT smoke）
- [x] ユーザーによるP4a実装開始承認（2026-09-01）

## 関連ファイル

- `specs/2026-07-21-state-carry-improvement-spec-candidate.md`
- `specs/2026-07-23-p2-cache-update-control-spec.md`
- `experiments/2026-07-23-p2-cache-update-control.md`
- `meetings/2026-08-28-mtg.md`
- `../secretary/notes/brainstorm/2026-09-01-p1-p2-and-training-direction.md`
