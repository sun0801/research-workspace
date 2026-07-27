---
date: 2026-07-27
project: sam2-mamba-motion-tracking
source: brainstorm
status: draft
tags: [spec, MIRU, qualitative, tracking, candidate-selection]
---

# MIRUポスター定性結果候補抽出 Spec

## 目的

MIRUポスターに掲載する定性的トラッキング結果を、全sequence・全フレームの目視比較なしに候補化する。

既存のMOT推論結果、TrackEvalのsequence別評価、MambaTrackers側artifact、Mamba-aware candidate debugを読み取り、SAM2/SAMURAIの失敗場面と、Mamba統合SAM2の改善場面を対応付けた候補CSVを作成する。最終的な掲載可否はMOT Viewerで人手確認する。

## 背景

- MIRUポスターでは、SAM2/SAMURAIによる追跡をMambaの動き予測で改善する流れを、オクルージョン前後の複数フレームで示したい。
- 現在のMOT Viewerはフレーム単位の左右比較には対応するが、候補イベントの一括抽出には対応していない。
- 25系列のMOT txt、run別manifest、TrackEval artifactが複数箇所に保存されている。
- stateful統合runのcandidate debugには、`motion_model_type`、`used_true_state_carry`、`stateful_step`、`miss_count`、`fallback_mode`等が含まれる。
- `samurai_mamba_window`は現時点で同一条件の25系列出力が確認できず、sliding window比較は追加検証扱いとする。

## 検証したい問い

SAM2/SAMURAIで追跡が不安定になる場面を、Mamba統合SAM2は追跡継続・bbox位置・オクルージョン後の回復の点で改善しているか。

追加の問いとして、同一条件のsliding window出力が揃った場合に、state carryがsliding windowより明確に良い定性的挙動を示す場面があるかを確認する。

## 仮説

- ベースラインでtrack消失、bbox漂流、ID継続の不安定化が起きるイベントの一部では、Mamba統合により追跡継続または回復が改善する。
- state carryは、過去の動きを継続的に利用できる場面ではsliding windowより滑らかな追跡や回復を示す可能性がある。
- ただしstate carryにはfallback、miss、state不安定化があり得るため、state carryの優位性は主張せず、対応する候補が得られた場合のみ補助的に示す。

## 実験・実装内容

### 1. 入力runの棚卸し

以下のファイルを読み取り、run registryを作成する。

- `/mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2/results/sam2/sam2_tiny`
- `/mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2/results/samurai/samurai_tiny`
- `/mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2/results/samurai_mamba/samurai_mamba_tiny`
- `/mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2/results/sam2_stateful_minimal/20260723T_sam2_minimal_25seq`
- `/mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2/results/sam2_stateful_minimal/20260727T_sam2_minimal_25seq_best_hota_epoch20`
- `/mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2/results/sam2_stateful_minimal/20260727T_sam2_minimal_25seq_epoch100_kfw0`
- `/mnt/HDD10TB-2/aburatani/2025_09_aburatani_Mamba_Trackers/artifacts`

各runについて、次を記録する。

- run名、mode、model名
- sequence一覧とMOT txtの存在数
- checkpointパス
- testing set
- git commit/status
- candidate debugの列構成
- 対応するTrackEval artifactのパス
- provenanceの確実性（verified / partial / unknown）

### 2. sequence単位の候補絞り込み

TrackEvalの`pedestrian_detailed.csv`を利用できるrunでは、sequence別の以下の指標を比較する。

- HOTA
- AssA
- IDF1
- IDSW
- MOTAまたはMOTP

主候補は、SAM2またはSAMURAIの指標が相対的に低く、Mamba統合runとの差が大きいsequenceとする。ただし、集計結果だけで掲載候補を確定しない。

TrackEval artifactが存在しない、またはprovenanceが不明な場合は、MOT txtを正本として扱い、候補抽出から除外せず、評価値の信頼性だけを`unknown`として記録する。

### 3. フレームイベント抽出

MOT txtとcandidate debugから、以下のイベントを抽出する。

- trackの一時消失と再出現
- bboxの急移動または漂流
- bbox面積・アスペクト比の急変
- 手法間のbbox位置の不一致
- オクルージョン前後の追跡継続性の差
- statefulの`used_true_state_carry`、`stateful_step`、`miss_count`、`fallback_mode`の変化
- candidate debugに記録されたSAM候補IoU、予測bboxとのIoU、更新信頼性の低下

近接する異常フレームは一つのイベント区間にまとめる。候補区間は、原則としてイベント前後を含む6フレーム程度とする。

### 4. ベースライン起点の比較

候補抽出では、まずSAM2/SAMURAI側の失敗イベントを基準にする。Mamba結果を見てから都合のよいイベントだけを選ばない。

同じsequence・同じフレーム区間について、以下を対応付ける。

- SAM2
- SAMURAI
- Mamba統合SAM2 state carry
- 利用可能ならMamba統合SAM2 sliding window

手法間でtrack IDが一致しない場合は、同一フレームのbbox IoU、中心距離、またはGT IDを介して対応付ける。ID番号だけを直接比較しない。

### 5. 候補CSV出力

候補一覧には最低限、次の列を含める。

- `sequence`
- `event_frame`
- `start_frame`
- `end_frame`
- `event_type`
- `candidate_score`
- `baseline_summary`
- `mamba_summary`
- `state_carry_summary`
- `window_summary`
- `reason`
- `video_path`
- `baseline_output_paths`
- `mamba_output_paths`
- `debug_output_paths`
- `trackeval_paths`
- `checkpoint`
- `provenance_status`

候補は、改善例、代表例、限界例が偏らないように層化して上位候補を出す。最終的なポスター掲載数は3〜5例を想定する。

## 使用データ・モデル

- DanceTrack validation sequenceの動画
- SAM2、SAMURAIのMOT txt
- Mamba統合SAM2 statefulのMOT txt
- 利用可能なMamba windowのMOT txt
- 対応するcandidate debug CSV
- MambaTrackers側のTrackEval summary/detailed CSV
- 必要に応じてDanceTrack GT

本specでは再推論やcheckpoint再学習は行わない。既存出力の読み取りと候補分析のみを扱う。

## 比較対象・ベースライン

主比較:

- SAM2 vs Mamba統合SAM2 state carry
- SAMURAIを補助的なベースラインとして表示

追加比較:

- Mamba統合SAM2 sliding window vs state carry

sliding windowは、sequence数・checkpoint・scale・association・lifecycleが揃った場合にのみ正式比較とする。

## 評価指標

### 自動候補抽出

- GT IoUまたはLocA
- track出現・消失区間
- bbox中心移動量
- bbox面積・アスペクト比変化
- 手法間bbox IoUまたは中心距離
- state carry利用、miss、fallbackの発生

### sequence単位

- HOTA
- AssA
- IDF1
- IDSW
- 必要に応じてDetA、MOTA、MOTP

### 人手確認

- 同じ対象を追跡できているか
- オクルージョン前後のIDが維持されているか
- bboxが対象から漂流していないか
- 改善が6フレームの時系列で説明できるか
- ポスター上で判読可能か

## 成功/失敗の判断基準

### 成功

- 入力runとprovenanceをrun registryで識別できる。
- 少なくとも主比較用に、sequence・フレーム範囲・比較runを含む候補CSVを生成できる。
- 各候補について、ユーザーがViewerで同じ動画・同じMOT出力を再表示できる。
- SAM2/SAMURAIの失敗とMamba統合SAM2の改善が、複数フレームの時系列で説明できる候補が得られる。
- TrackEvalの値とMOT txtの対応が確認でき、上書きやprovenance不明の結果を明示できる。

### 失敗または保留

- 比較runのsequence・checkpoint・条件が対応付けられない。
- Mamba outputが同じsequence・フレーム区間に存在しない。
- 候補が単一フレームの偶然の差に留まり、時系列で説明できない。
- sliding windowの条件が揃わず、state carryとの差を公平に判断できない。

## 実施手順

1. results配下のMOT txt、candidate debug、manifestを列挙する。
2. MambaTrackers側artifactのTrackEval summary/detailed CSVをrun別に対応付ける。
3. run registryにprovenanceとsequence coverageを記録する。
4. 主比較のSAM2/SAMURAI対stateful Mambaについて、sequence単位の候補を抽出する。
5. 各sequenceのMOT時系列からイベント区間を抽出する。
6. 候補CSVを生成する。
7. ユーザーがViewerで候補を確認する。
8. 改善例・代表例・限界例からポスター掲載候補を決定する。
9. 必要な場合のみ、sliding window比較を追加する。

## 期待される結果

- 全25系列をViewerで確認する代わりに、優先度付きの少数候補を確認できる。
- SAM2/SAMURAIの失敗場面とMamba統合SAM2の改善場面を、同一sequence・同一フレーム範囲で比較できる。
- state carryの有効例が得られた場合は、追加の比較行としてポスターに利用できる。
- 使えないrunや上書き疑いのあるTrackEval結果を、候補選定時に除外または注記できる。

## リスク・懸念

- `samurai_mamba`のmode・checkpoint provenanceが不明な可能性がある。
- `samurai_mamba_window`の25系列出力が不足している可能性がある。
- candidate debugの列名が同じでも、runによってモーションモデルの意味が異なる可能性があるため、`motion_model_type`等を必ず確認する。
- TrackEvalのsequence別評価が一部runで欠落・上書きされている可能性がある。
- 定性的候補は選択バイアスを持ち得るため、改善例だけでなく代表例・限界例を含める。

## 未決事項

- `samurai_mamba`の正確なmode、checkpoint、scale、association設定。
- sliding windowの25系列runの有無と、state carryとの公平比較条件。
- GT bboxをViewerに重ねるかどうか。
- event scoreの重みと候補数。
- 候補CSVの永続保存先をResearch Workspaceの`experiments/`にするか、分析用出力ディレクトリにするか。

## 関連brainstorm

- `.research/secretary/notes/brainstorm/2026-07-27-miru-qualitative-result-selection.md`

## 関連ファイル・ディレクトリ

- `/mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2/results`
- `/mnt/HDD10TB-2/aburatani/2025_09_aburatani_Mamba_Trackers/artifacts`
- `/mnt/HDD10TB-2/aburatani/2026_03_aburatani_movies_antigravity/mot_viewer`
