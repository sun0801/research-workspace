---
date: 2026-09-24
project: sam2-mamba-motion-tracking
source: brainstorm
status: draft
tags: [spec, experiment, yolo, mamba, shuffle, tracking]
---

# YOLO＋Mamba shuffle / non-shuffle再推論比較 Spec

## 目的

前回SAM2統合評価に使用した、shuffle学習・non-shuffle学習のMamba checkpointを再利用し、YOLO＋Mamba trackingにおける性能差を同一条件で比較する。

新規学習を直ちに行わず、SAM2側のメモリ・mask候補選択・統合処理の影響を除いた状態で、shuffle学習の差がYOLO＋Mambaへ伝播するかを確認する。

## 背景

P4aでは`shuffle=False`で固定chunk順序に由来するloss振動が見られ、`shuffle=True`では振動が抑制された。一方、SAM2統合後のDanceTrack val 25系列では、epoch100のshuffle条件がHOTA 53.944、non-shuffle条件がHOTA 54.391となり、shuffle条件の明確な改善は確認されなかった。

SAM2統合では、Mamba以外にSAM2の初期prompt、メモリ、候補選択、associationの影響が混在する。そのため、既存の2つのMamba checkpointをYOLO＋Mambaへ投入し、tracking-by-detection側で比較する。

## 検証したい問い

1. SAM2統合時に使用したshuffle/non-shuffleのMamba checkpointをYOLO＋Mambaへ移しても、tracking性能差が現れるか。
2. shuffleによるMamba予測器の差は、YOLO検出とHungarian matchingを含むtracking性能へ伝播するか。
3. SAM2統合で差が小さかった理由が、Mamba予測器の差の小ささなのか、SAM2側の処理による吸収なのかを切り分けられるか。

## 仮説

- H1: shuffle学習checkpointは、non-shuffle checkpointと比べて学習lossの局所的な振動が少ない。
- H2: shuffle学習checkpointの予測器指標が改善しても、YOLOの全フレーム検出とHungarian matchingにより、最終HOTA差は小さくなる可能性がある。
- H3: 差は平均指標よりも、難しいsequence、matching境界付近のframe、長いmissing区間で現れる可能性がある。

## 実験・実装内容

### Phase 0: checkpointと条件の監査

画像やTrackEval summaryを再利用するのではなく、SAM2統合時に実際にロードされたMamba checkpointを正本として特定する。

確認する項目:

- non-shuffle P4a checkpointの実パス、SHA256、epoch
- shuffle P4a checkpointの実パス、SHA256、epoch
- Mamba architecture、入力形式、出力形式、scale
- checkpointを生成したcommit、config、dataset split、seed
- YOLO detectorのcheckpoint、入力解像度、confidence threshold
- association、matching cost、IoU threshold、track lifecycle
- `missing_mode`、`delta_clip`、cache/state update設定

既知のshuffle checkpoint記録:

```text
/mnt/HDD10TB-2/aburatani/2025_09_aburatani_Mamba_Trackers/ssm_tracker/saved_ckpts/p4a_shuffle_full_100ep_20260911/20260911T061814+0900_3489e78/epoch100.pth
```

non-shuffle checkpointの実パスは、`sam2_p4a_epoch100_25seq_20260904`の実行ログまたはcheckpoint manifestから解決し、推測で補わない。

### Phase 1: single-sequence smoke

同じYOLO検出入力と同じ推論設定で、non-shuffleとshuffleを各1系列ずつ実行する。

両条件で以下を確認する。

- checkpointがstrict loadされ、fallbackが発生しない
- Mambaの入力scaleとbbox形式が一致する
- state/cacheがfiniteである
- 出力MOT形式、frame数、track ID形式が一致する
- `missing_mode`やmatching設定が実行ログ上で一致する

ここでは性能差の結論を出さず、checkpointとYOLO推論経路の互換性を確認する。

### Phase 2: DanceTrack val 25系列比較

Phase 1が通過した場合、同一のYOLO detector・検出結果・tracking設定でDanceTrack val 25系列を推論する。

主比較:

```text
non-shuffle Mamba checkpoint + fixed YOLO detections
shuffle Mamba checkpoint     + fixed YOLO detections
```

推論時のmissing modeは、既存P4a baselineとの連続性を優先して`self_update`に固定する。`freeze`は本specの主比較には含めず、必要になった場合は別の感度分析として扱う。

## 使用データ・モデル

- Dataset: DanceTrack val 25系列
- Mamba: P4a `MambaStateful` epoch100のnon-shuffle / shuffle checkpoint
- Detector: 既存YOLOX detector。両条件で同一checkpoint・同一設定を使用
- Association: 既存YOLO＋MambaのHungarian matching
- 学習済みMambaの入力: GT軌跡で学習されたbbox時系列。推論時はYOLO検出とMamba予測を用いる
- SAM2: 本比較では使用しない

## 比較対象・ベースライン

| 条件 | 学習checkpoint | 推論入力 | 目的 |
|---|---|---|---|
| non-shuffle | SAM2統合non-shuffle P4a checkpoint | 同一YOLO detections | 対照 |
| shuffle | SAM2統合shuffle P4a checkpoint | 同一YOLO detections | shuffle条件 |

学習済みcheckpoint以外の差を作らない。YOLO検出結果を事前生成できる場合は両条件で同じ検出ファイルを使用する。

## 評価指標

### Tracking指標

- 主指標: HOTA
- 副指標: DetA、AssA、IDF1、MOTA、IDSW

### 予測・安定性指標

- bbox予測誤差、IoU
- free rolloutのhorizon別誤差
- state/cacheのnonfiniteイベント
- state norm
- missing時のself-update回数
- 推論時間

### 局所分析

- sequence別の各指標とshuffle−non-shuffle差分
- track別の予測誤差と失敗率
- detector miss、matching変更、self-update発生区間
- 大きな誤差やIDSWの前後におけるstate値

## 成功・失敗の判断基準

### 実験成立条件

- 両checkpointが想定されたMamba構造へstrict loadされる
- 両条件で同一のYOLO検出・matching・missing設定が使われる
- 25系列すべての出力とTrackEval summaryが生成される
- nonfiniteや推論途中停止があれば、系列・frame・trackを記録できる

### 解釈基準

- YOLO＋MambaのHOTA、AssA、IDF1、IDSWを同一25系列で比較する。
- 平均値だけでなくsequence別差分を確認する。
- 差が小さい場合も、shuffle無効の証明とはせず、checkpointが単一seed・epoch100であることを明記する。
- 予測器指標だけ改善してtracking指標が改善しない場合、YOLO検出またはmatchingが差を吸収した可能性として扱う。
- 条件不一致、checkpoint load失敗、出力欠損がある場合は、性能比較を成立扱いにしない。

## 実施手順

1. non-shuffle/shuffle checkpointの実パスとSHA256を記録する。
2. 両条件のconfig、commit、architecture、scale、epochをmanifestに記録する。
3. YOLO detectorのcheckpointと検出設定を固定する。
4. `missing_mode=self_update`、matching、threshold、TrackEval設定を固定する。
5. 1系列のsmokeを両条件で実行する。
6. load、state finite性、出力frame数、MOT形式を確認する。
7. DanceTrack val 25系列を両条件で実行する。
8. TrackEvalでHOTA、DetA、AssA、MOTA、IDF1、IDSWを集計する。
9. sequence別・track別・missing区間別の差分を集計する。
10. 結果を`experiments/2026-09-24-yolo-mamba-shuffle-comparison.md`へ保存する。

## 期待される結果

- 既存SAM2統合結果と同様に差が小さい場合、Mamba checkpoint差がYOLO＋Mambaでも小さい、またはmatchingが差を吸収している可能性がある。
- YOLO＋Mambaで差が拡大する場合、SAM2のメモリ・mask候補選択がshuffle差を吸収していた可能性がある。
- sequence別に差が分かれる場合、平均HOTAではなく、オクルージョンや検出欠損との関係を優先して分析する。

## リスク・懸念

- 既存SAM2統合runとYOLO＋MambaでMamba入力形式やscaleが一致しない可能性がある。
- MambaはGT軌跡で学習されており、YOLO検出ノイズとの入力分布差がある。
- epoch100・単一seedのcheckpoint再利用であり、shuffleの一般的な優位性は主張できない。
- YOLO detectorやmatching条件が過去のtracker評価と異なると、shuffle差以外の要因が混入する。
- `self_update`はmissing時にstate/cacheを進めるため、長い欠損区間でstate contaminationが結果に影響する可能性がある。

## 新規学習へ進む条件

以下の場合のみ、paired再学習を別specまたは本specの後続実験として計画する。

- 既存checkpointを特定できない。
- YOLO＋Mambaの入力形式にcheckpoint互換性がない。
- 既存checkpointのconfig、commit、dataset、seedが確認できず、対照性を保証できない。
- YOLO検出ノイズを含む入力で学習すること自体を新しい研究問いとする。

その場合も、まず同一初期重み・single GPU・1 seedのpaired比較を行い、結果確認後に3 seedへ拡張する。

## 関連brainstorm

- `.research/secretary/notes/brainstorm/2026-09-24-yolo-mamba-shuffle-comparison.md`

## 関連ファイル

- `.research/lab/projects/sam2-mamba-motion-tracking/meetings/2026-09-18-mtg.md`
- `.research/lab/projects/sam2-mamba-motion-tracking/experiments/2026-09-04-l0-p4a-tracker-sam2-comparison.md`
- `.research/lab/projects/sam2-mamba-motion-tracking/experiments/2026-09-18-p4a-shuffle-sam2-trackeval.md`
- `.research/lab/projects/sam2-mamba-motion-tracking/specs/2026-09-01-p4a-stateful-unroll-tbptt-spec.md`
