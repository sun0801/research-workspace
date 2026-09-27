---
date: 2026-09-25
project: sam2-mamba-motion-tracking
status: exploratory
tags: [experiment, train, mamba, loss, HOTA, sequence-analysis, oracle-detection]
---

# DanceTrack train sequence別 loss・HOTA分析

## 目的

validation splitで行ったsequence別lossとHOTAの対応分析を、DanceTrack train splitでも確認する。特に、lossの高いsequenceがtrackingでも失敗しているのか、またMTGで話していた「後半のsequenceが難しい」という見方がtrain splitで成り立つのかを調べる。

## 結論

- train全40系列、417 tracks、7,471 chunksについて、epoch100 checkpointのMamba lossをsequence別に再計算できた。
- valid transition単位のtrain lossは `0.055742` だった。train1の重み付き平均は `0.049310`、train2は `0.063484` で、train2の方が高い。
- loss上位5系列はすべてtrain2（`dancetrack0052`、`0055`、`0072`、`0074`、`0075`）だった。ただし、これは「sequence番号の後半ほど難しい」という単純な意味ではなく、train1/train2のsplit分布差として解釈する。
- GT検出を入力したMamba追跡の診断HOTAでは、lossとHOTA AUCの相関は弱い負相関に留まった（Pearson `r=-0.235`、Spearman `rho=-0.182`）。lossが高いsequenceほどHOTAが必ず低いわけではない。
- したがって、train lossは「Mambaの動き予測が難しいsequence」の候補抽出には使えるが、「trackingとして失敗するsequence」の判定にはHOTA、検出欠損、association、ID switchを併用する必要がある。

## 評価条件

### Mamba loss

- checkpoint: `mamba_stateful_tbptt_p4a_full/p4a_full_100ep_20260903/epoch100.pth`
- config: 同checkpointディレクトリの `MambaStatefulTBPTT.yaml`
- annotation: `ssm_tracker/traj_anno_data/dancetrack_train.json`
- 対象: 417 tracks、7,471 chunks、valid transitions 318,714
- unroll length: 48
- TBPTT length: 12
- loss start index: 4
- loss: paddingを除外したmasked Smooth L1
- sequence対応: train JSONの軌跡をDanceTrack元GTのbbox列と照合して復元

train JSONには元のsequence名が直接保存されていないため、元GTとのbbox signature照合で40系列へ対応付けた。40/40系列、417/417 tracksを対応付けできた。

### HOTA

train splitには、validation時に使ったYOLO＋MambaおよびSAM2＋MambaのTrackEval結果が存在しなかった。そのため、以下のHOTAはraw DanceTrack GT bboxを検出入力としてMamba trackerを実行した診断値である。

- 検出入力: DanceTrack trainのGT bbox
- tracker: 同じepoch100 Mamba checkpoint
- association: `prediction`、missing mode `freeze`
- TrackEval: 40系列、HOTA/CLEAR/Identity、preprocessingなし
- 全体のTrackEval HOTA AUC: `0.84588`
- 全体のTrackEval HOTA(0): `0.85407`

このHOTAは実検出器を含むYOLO＋Mamba／SAM2＋Mambaの性能ではない。特にDetAはほぼ1に近いため、主にMambaのtrack association側を診断する値として扱う。YOLO＋Mamba／SAM2＋Mambaのtrain全系列HOTAを得るには、train splitで各推論を追加実行する必要がある。

## 全40系列の比較表

HOTA列は、同じGT検出入力によるMamba診断評価で、HOTA(0)とHOTA AUCを併記する。lossはvalid transition単位の平均である。

| sequence | tracks | valid transitions | Mamba loss | Mamba HOTA(0), GT det. | Mamba HOTA AUC, GT det. |
|---|---:|---:|---:|---:|---:|
| dancetrack0001 | 7 | 4,485 | 0.039926 | 1.000000 | 1.000000 |
| dancetrack0002 | 8 | 8,469 | 0.030477 | 0.613667 | 0.607782 |
| dancetrack0006 | 9 | 9,658 | 0.027062 | 0.861018 | 0.791358 |
| dancetrack0008 | 8 | 6,255 | 0.062110 | 0.577678 | 0.570013 |
| dancetrack0012 | 12 | 11,907 | 0.032670 | 0.572622 | 0.569791 |
| dancetrack0015 | 9 | 9,809 | 0.045499 | 0.976083 | 0.976083 |
| dancetrack0016 | 6 | 11,545 | 0.031711 | 0.629393 | 0.628937 |
| dancetrack0020 | 40 | 18,381 | 0.027394 | 0.799493 | 0.795304 |
| dancetrack0023 | 9 | 11,919 | 0.032026 | 0.852859 | 0.852685 |
| dancetrack0024 | 6 | 4,122 | 0.060236 | 0.980038 | 0.980038 |
| dancetrack0027 | 11 | 3,102 | 0.053130 | 0.959228 | 0.941240 |
| dancetrack0029 | 7 | 7,203 | 0.052995 | 0.999873 | 0.999873 |
| dancetrack0032 | 6 | 3,062 | 0.021033 | 0.686912 | 0.683613 |
| dancetrack0033 | 8 | 5,697 | 0.089242 | 0.838024 | 0.818110 |
| dancetrack0037 | 7 | 7,602 | 0.067030 | 0.808680 | 0.807873 |
| dancetrack0039 | 5 | 5,571 | 0.108240 | 0.770233 | 0.731523 |
| dancetrack0044 | 13 | 12,240 | 0.066782 | 0.543256 | 0.532377 |
| dancetrack0045 | 14 | 14,477 | 0.042791 | 0.802085 | 0.771668 |
| dancetrack0049 | 8 | 8,691 | 0.094866 | 0.883207 | 0.879259 |
| dancetrack0051 | 9 | 9,884 | 0.067641 | 1.000000 | 1.000000 |
| dancetrack0052 | 4 | 4,078 | 0.154653 | 0.824043 | 0.824043 |
| dancetrack0053 | 5 | 5,449 | 0.117602 | 0.836775 | 0.823327 |
| dancetrack0055 | 5 | 5,323 | 0.150748 | 0.644991 | 0.637751 |
| dancetrack0057 | 6 | 2,739 | 0.097807 | 0.976182 | 0.976182 |
| dancetrack0061 | 5 | 5,500 | 0.057593 | 1.000000 | 1.000000 |
| dancetrack0062 | 6 | 5,691 | 0.042679 | 0.999840 | 0.999840 |
| dancetrack0066 | 5 | 5,500 | 0.046207 | 0.900841 | 0.889752 |
| dancetrack0068 | 5 | 5,494 | 0.103926 | 0.904306 | 0.900375 |
| dancetrack0069 | 6 | 7,553 | 0.054537 | 0.830756 | 0.830413 |
| dancetrack0072 | 5 | 5,402 | 0.144655 | 0.758426 | 0.703338 |
| dancetrack0074 | 5 | 4,847 | 0.126767 | 0.702979 | 0.691151 |
| dancetrack0075 | 7 | 4,971 | 0.124385 | 0.810092 | 0.807839 |
| dancetrack0080 | 16 | 10,995 | 0.030654 | 0.999419 | 0.999419 |
| dancetrack0082 | 24 | 11,264 | 0.018011 | 0.929622 | 0.929269 |
| dancetrack0083 | 25 | 13,669 | 0.032963 | 0.991428 | 0.991428 |
| dancetrack0086 | 16 | 8,656 | 0.040767 | 0.989923 | 0.989923 |
| dancetrack0087 | 11 | 9,780 | 0.032168 | 0.976534 | 0.976534 |
| dancetrack0096 | 40 | 14,364 | 0.020170 | 1.000000 | 1.000000 |
| dancetrack0098 | 8 | 7,701 | 0.081545 | 0.748584 | 0.720744 |
| dancetrack0099 | 11 | 5,659 | 0.080164 | 0.816149 | 0.816149 |

## loss上位5系列の評価

| sequence | split | Mamba loss | Mamba HOTA(0), GT det. | Mamba HOTA AUC, GT det. |
|---|---|---:|---:|---:|
| dancetrack0052 | train2 | 0.154653 | 0.824043 | 0.824043 |
| dancetrack0055 | train2 | 0.150748 | 0.644991 | 0.637751 |
| dancetrack0072 | train2 | 0.144655 | 0.758426 | 0.703338 |
| dancetrack0074 | train2 | 0.126767 | 0.702979 | 0.691151 |
| dancetrack0075 | train2 | 0.124385 | 0.810092 | 0.807839 |

高loss上位5系列のうち、HOTA AUCが特に低いのは0055と0074である。一方、0052と0075はlossが高いにもかかわらずHOTA AUCが0.80以上であり、高lossだけではtracking失敗を説明できない。

## lossとHOTAの関係

全40系列を1サンプルとして計算した相関は次の通りである。統計的有意性の検定は行っていないため、傾向確認として扱う。

| HOTA指標 | Pearson r | Spearman rho |
|---|---:|---:|
| HOTA(0) | -0.219 | -0.213 |
| HOTA AUC | -0.235 | -0.182 |

validation時のMamba lossとHOTA AUCには弱い正相関が見えていたが、train splitのGT検出入力では弱い負相関になった。ただし、いずれも絶対値は小さく、sequence単位のlossだけからHOTAを予測できるほどの関係ではない。

### 対応している例

- `dancetrack0055`: loss `0.150748`、HOTA AUC `0.637751`。高lossかつ診断HOTAも低めで、Mambaの動き予測誤差がassociationに影響している候補である。
- `dancetrack0074`: loss `0.126767`、HOTA AUC `0.691151`。高loss側でHOTAも相対的に低い。
- `dancetrack0039`: loss `0.108240`、HOTA AUC `0.731523`。高lossだが、上位5系列ほどではないもののHOTAも低めである。

### 対応していない例

- `dancetrack0052`: lossが全40系列で最大の `0.154653` だが、HOTA AUCは `0.824043`。
- `dancetrack0075`: loss `0.124385` に対してHOTA AUC `0.807839`。
- `dancetrack0096`: loss `0.020170` と低い一方、HOTA AUCは `1.000000`。低lossが高HOTAと対応する例ではあるが、これはGT検出入力の結果であり、実検出器を含む比較ではない。
- `dancetrack0044`: loss `0.066782`、HOTA AUC `0.532377`。lossは中程度でも診断HOTAは最も低い系列の一つである。

## MTGでの「後半sequenceが難しい」仮説との関係

train1とtrain2を分けると、lossの重み付き平均は次の通りだった。

| split | sequences | valid transitions | weighted mean loss |
|---|---:|---:|---:|
| train1 | 20 | 174,079 | 0.049310 |
| train2 | 20 | 144,635 | 0.063484 |

train2の方が平均lossは高く、loss上位5系列もすべてtrain2だった。この意味では、前回MTGの「後半側に難しいデータが多い」という観察には、train1/train2レベルでは一定の対応がある。

ただし、sequence番号の後半ほど単調に難しくなるわけではない。train2内でも、`0052`は高lossだがHOTAが比較的高く、`0055`や`0074`はHOTAも低い。またtrain1にも`0039`や`0049`のようにlossが高い系列がある。したがって、結論は「後半sequenceは一律に難しい」ではなく、「train2には動き予測lossが高い系列が多いが、tracking失敗との対応は系列ごとに異なる」とするのが妥当である。

## 解釈上の注意

1. train lossは学習に使ったデータに対するin-sample lossであり、validation lossよりも低く出ることが期待される。汎化性能の指標ではない。
2. lossはGT bbox列からの遷移予測誤差、HOTAはGT検出入力でのMamba tracking結果であり、測定対象が異なる。
3. GT検出入力のため、YOLO＋MambaやSAM2＋Mambaの実運用時に発生する検出欠損・誤検出は評価していない。
4. YOLO＋Mamba／SAM2＋Mambaのtrain全40系列HOTAは、対応するtrain推論結果を新たに生成しない限り比較できない。今回の表にそれらの値を代入してはいけない。

## 次に見るべき系列

診断用の優先候補は次の通りである。

- 高lossかつHOTAも低め: `dancetrack0055`、`dancetrack0074`、`dancetrack0039`
- 高lossだがHOTAが維持: `dancetrack0052`、`dancetrack0075`
- lossは中程度だがHOTAが低い: `dancetrack0044`、`dancetrack0012`、`dancetrack0008`

次の原因分析では、これらについてtrack/frame単位でMamba予測誤差、予測boxの欠落、ID switchを同じ時刻軸に並べるのが妥当である。YOLO＋Mamba／SAM2＋Mambaの実検出ベース比較を必要とする場合は、train推論を別実験として実行する。

## 関連

- [Mamba sequence別lossとvalidation HOTAの比較](2026-09-25-mamba-loss-hota-sequence-comparison.md)
- [SAM2＋Mamba sequence別失敗分析](2026-09-25-sam2-sequence-failure-analysis.md)
- [P4a loss sequence比較](2026-09-25-p4a-loss-sequence-comparison.md)
