---
date: 2026-09-25
project: sam2-mamba-motion-tracking
status: exploratory
tags: [experiment, sam2, sequence-analysis, failure-analysis, non-shuffle, canonical]
---

# SAM2＋Mamba sequence別失敗分析

## 目的

SAM2＋Mambaの平均性能が十分に出ていない理由を、sequence単位・frame単位の失敗例から確認する。shuffle/non-shuffleの優劣を比較する資料ではない。

## 分析条件

主分析の基準runは、non-shuffle P4a epoch100のSAM2統合結果に固定する。

- SAM2 run: `sam2_p4a_epoch100_25seq_20260904`
- 対象: DanceTrack validation 25系列
- TrackEval aggregate HOTA: `54.391`
- 対応するTrackEval正本: `/mnt/HDD10TB-2/aburatani/TrackEval/data/trackers/dancetrack/val/sam2_p4a_epoch100_25seq_20260904/pedestrian_summary.txt`

shuffle版の結果、loss、candidate debugは、この主分析の条件には混ぜない。shuffleに関する比較は、`2026-09-25-yolo-mamba-shuffle-comparison.md` および既存のshuffle評価ログで扱う。

## 既存情報の扱い

既存の以下のメモと図は、shuffle版SAM2出力とnon-shuffle lossを横断した探索記録である。候補発見には使えるが、正式な原因分類や条件間の性能差の根拠にはしない。

- `2026-09-25-p4a-loss-sequence-comparison.md`
- `2026-09-25-checkpoint-loss-sequence-failure-linkage.md`
- `2026-09-25-sam2-sequence-visualization-candidates.md`
- `2026-09-25-sam2-sequence-candidate-figures-corrected.md`

これらの探索では、Mamba loss上位とSAM2 HOTA下位が一致しない傾向が見えている。ただし、SAM2側がshuffle runであるため、現時点では仮説として扱う。

## 解析項目

| 段階 | 確認内容 | 主な出力 |
|---|---|---|
| 1 | 基準runのsequence別HOTA / AssA / IDF1 / IDSW | 低性能sequenceの一覧 |
| 2 | 低性能sequenceのID switch・missing・matching変更 | 失敗frameと遷移 |
| 3 | 同じ基準checkpointのMamba lossをsequence / track / chunkへ対応付け | Mamba予測誤差の分布 |
| 4 | GT、Mamba予測、SAM2出力、candidate IoUを同一frame軸で可視化 | 代表失敗例の図 |
| 5 | Mamba起因、SAM2 / association起因、検出・欠損起因を切り分け | 原因仮説 |

## 代表候補の選び方

まず基準runのsequence別HOTA下位から代表を選ぶ。その後、同一条件のMamba loss、IDSW、missing、candidate IoUを確認する。lossが高いsequenceだけを先に選ばない。

最低限、以下の3タイプを同一条件で比較する。

1. SAM2 HOTAが低く、Mamba lossも高いsequence
2. Mamba lossは高くないが、SAM2 HOTAが低いsequence
3. Mamba lossは高いが、SAM2 HOTAが維持されるsequence

## 未完了

- 基準runのsequence別TrackEval行を抽出する
- 基準runに対応するcandidate debugの有無とパスを確認する
- 基準runのMamba lossとtrack / frameを対応付ける
- 代表3タイプの同一frame軸の可視化を生成する
- shuffle版候補図を正式分析用の図として再利用しないことを確認する

## 関連

- `meetings/2026-09-18-mtg.md`
- `experiments/2026-09-04-l0-p4a-tracker-sam2-comparison.md`
- `experiments/2026-09-18-p4a-shuffle-sam2-trackeval.md`
- `specs/2026-09-24-yolo-mamba-shuffle-comparison-spec.md`

## 初回sequence比較結果（2026-09-25）

non-shuffle P4a epoch100の基準run
`sam2_p4a_epoch100_25seq_20260904` に対して、TrackEvalのsequence別詳細CSVを抽出した。HOTA下位は次の通りだった。

| sequence | HOTA | DetA AUC | AssA AUC | IDF1 | IDSW | MLR | MTR | PTR |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| dancetrack0026 | 0.3361 | 0.3208 | 0.1822 | 0.3266 | 158 | 0.000 | 0.158 | 0.842 |
| dancetrack0014 | 0.4271 | 0.3274 | 0.2937 | 0.4150 | 115 | 0.000 | 0.083 | 0.917 |
| dancetrack0041 | 0.4955 | 0.3580 | 0.3727 | 0.4721 | 204 | 0.091 | 0.364 | 0.545 |
| dancetrack0019 | 0.5140 | 0.4666 | 0.3999 | 0.4739 | 107 | 0.000 | 0.286 | 0.714 |
| dancetrack0094 | 0.5357 | 0.3359 | 0.5629 | 0.4701 | 138 | 0.320 | 0.360 | 0.320 |
| dancetrack0063 | 0.5360 | 0.3257 | 0.4338 | 0.4911 | 87 | 0.250 | 0.500 | 0.250 |

### 現時点の解釈

- `dancetrack0026`: AssA AUCが0.1822と最も低く、検出側も低い。まず対応付け崩れを確認する代表候補。
- `dancetrack0014`: DetA / AssAがともに低く、長い欠損区間がある。frame 1038–1045付近を確認する。
- `dancetrack0041`: 6系列中でIDSWが204と最大。frame 699–730、862–865、888付近に欠損・ID切替が集中する。
- `dancetrack0019`: HOTAは低いが、長いsequenceの後半 frame 1946–1956付近に欠損・対応崩れが集中する。
- `dancetrack0094`: DetA AUCが低く、MLRが0.320。frame 391–392、433–445付近で欠損が集中する。
- `dancetrack0063`: DetA AUCが低く、frame 588–595、621付近に欠損が集中する。

### 補助的なframe候補抽出

基準runにはcandidate debug CSVが残っていなかったため、MOT出力とGTをIoU 0.5のgreedy matchingで対応付け、miss・ID切替が集中するframeを候補化した。これはTrackEvalのIDSWを再現するものではなく、可視化対象を絞るための補助分析である。

初回の可視化対象は、次の3系列とする。

1. `dancetrack0026`: 低AssAの対応付け失敗代表（frame 60–63、124–150、236–244）
2. `dancetrack0094`: 欠損とID切替が併発する代表（frame 55–65、377–392、433–445）
3. `dancetrack0041`: IDSW最多・長い欠損の代表（frame 699–730、862–865、888–941）

補助抽出の詳細は、各系列のMOT出力・GTから再現できる。次段階では、同じframe範囲にGT bbox、Mamba予測、SAM2出力、ID切替を重ねる。

### 未確認

- non-shuffle基準runにはcandidate debug CSVがないため、SAM2内部のcandidate IoU・stateful step・missing理由は未取得。
- Mamba lossとの対応付けは、同じnon-shuffle checkpointについてsequence・track・chunk単位で継続する。
- 補助matchingによるID切替は、TrackEvalの厳密なIDSWとは区別して扱う。

### 補助contact sheet

non-shuffle基準runのMOT出力とGTから作成した補助図。緑がGT、赤がSAM2＋Mambaの最終track boxで、赤ラベル内の小数値は同frameのGTとのgreedy IoUである。Mamba単体の予測box、candidate IoU、stateful stepは基準runにdebug CSVがないため含めていない。

- [dancetrack0026 補助contact sheet](figures/2026-09-25-sam2-sequence-candidates-nonshuffle/dancetrack0026_nonshuffle_gt_tracker_contact_sheet.jpg)
- [dancetrack0094 補助contact sheet](figures/2026-09-25-sam2-sequence-candidates-nonshuffle/dancetrack0094_nonshuffle_gt_tracker_contact_sheet.jpg)
- [dancetrack0041 補助contact sheet](figures/2026-09-25-sam2-sequence-candidates-nonshuffle/dancetrack0041_nonshuffle_gt_tracker_contact_sheet.jpg)

これは正式なSAM2内部失敗原因の可視化ではなく、sequence比較で抽出したframe候補の確認用図である。

## 同一non-shuffle checkpointのMamba lossとの照合

既に再計算したnon-shuffle P4a epoch100 checkpointのsequence別Smooth L1を、今回の低HOTA系列に対応付けると次のようになる。`dancetrack0019`は今回の表ではloss値未取得のため保留した。

| sequence | SAM2 HOTA | Mamba mean Smooth L1 | 暫定的な読み方 |
|---|---:|---:|---|
| dancetrack0026 | 0.3361 | 0.0341 | lossは突出せず、SAM2 / association側を優先確認 |
| dancetrack0014 | 0.4271 | 0.0304 | lossは突出せず、欠損・対応付けを確認 |
| dancetrack0041 | 0.4955 | 0.0300 | lossは突出せず、IDSWと長い欠損を確認 |
| dancetrack0094 | 0.5357 | 0.0753 | Mamba誤差と下流失敗の併発候補 |
| dancetrack0063 | 0.5360 | 0.0279 | lossは低く、検出・欠損・associationを優先確認 |

この対応では、低HOTA系列の多くでMamba lossが突出していない。一方、`dancetrack0094`だけはlossも高く、Mamba予測誤差がSAM2側の失敗を悪化させている可能性がある。ただし、lossとSAM2失敗の因果関係は、frame単位の同一時刻対応を確認するまで断定しない。
