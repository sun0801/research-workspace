---
date: 2026-09-25
project: sam2-mamba-motion-tracking
status: exploratory
tags: [experiment, mamba, loss, HOTA, sequence-analysis, non-shuffle]
---

# Mamba sequence別lossとHOTAの比較

## 目的

Mambaの学習後checkpointからsequence別の検証lossを再計算し、Mamba単体のHOTA、および下流統合時のHOTAと同じ表で比較する。目的は、Mambaのlossが高いsequenceほどHOTAが低いのか、またSAM2＋Mambaの失敗sequenceと対応するのかを確認することである。

## 結論

- 全25系列のMamba lossを、学習時と同じ設定で再計算できた。global lossは "0.041422" で、既存のepoch100評価値と一致した。
- lossとHOTAの対応は、今回の25系列では「lossが高いほどHOTAが低い」という形ではなかった。むしろ相関係数は弱い正相関になっている。
- Mamba単体HOTAとの相関は Pearson r=+0.308、Spearman rho=+0.245、YOLO＋Mambaでは r=+0.319、SAM2＋Mambaでは r=+0.199 だった。
- したがって、Mamba lossはsequenceの動き・bbox遷移の予測誤差を表すが、HOTAの高低は検出、欠損、association、ID switchなどにも強く依存する。Mamba lossだけで「難しいsequence」やSAM2＋Mambaの失敗を説明することはできない。

## 比較条件

### Mamba loss

- checkpoint: p4a_full_100ep_20260903/epoch100.pth
- config: MambaStatefulTBPTT.yaml
- validation annotation: traj_anno_data/dancetrack_val.json
- unroll length: 48
- TBPTT length: 12
- loss start index: 4
- loss: masked Smooth L1
- padding: 除外
- 対象: 272 tracks、4,817 unroll chunks、valid transitions 205,646
- sequence対応: DanceTrack元GTのsequence順と、軌跡生成時の25フレーム未満filter・再番号付けを用いて対応付け

再計算したglobal lossは 0.0414223355 だった。

### HOTA

表のHOTAはTrackEval詳細CSVの HOTA___AUC を使用した。これはTrackEval summaryのaggregate HOTAと同じ定義であり、HOTA(0)とは異なる。以前のSAM2 sequence表に掲載した 0.3361 などは HOTA(0) の値なので、本表のHOTA AUCと直接比較しない。

- Mamba単体: p4a_full_100ep_20260903/trackeval_epoch100_25seq/mamba_stateful_tbptt/pedestrian_detailed.csv
- YOLO＋Mamba: yolo_mamba_nonshuffle_full_20260925/trackeval_20260925/pedestrian_detailed.csv
- SAM2＋Mamba: sam2_p4a_epoch100_25seq_20260904/pedestrian_detailed.csv

YOLO＋MambaとSAM2＋Mambaの列は、同じMamba checkpoint由来のlossに対する下流統合結果を確認するための参考列である。SAM2＋Mamba側に、SAM2独自のsequence別lossを追加したものではない。

## 全25系列の比較表

Mamba lossはvalid transition単位の平均Smooth L1、HOTAはAUCである。

| sequence | Mamba loss | valid transitions | Mamba HOTA | YOLO＋Mamba HOTA | SAM2＋Mamba HOTA |
|---|---:|---:|---:|---:|---:|
| dancetrack0004 | 0.0480 | 3,558 | 0.4890 | 0.4353 | 0.5419 |
| dancetrack0005 | 0.0477 | 3,400 | 0.7009 | 0.6251 | 0.5041 |
| dancetrack0007 | 0.0521 | 4,818 | 0.4729 | 0.4982 | 0.6238 |
| dancetrack0010 | 0.0456 | 2,913 | 0.6436 | 0.6446 | 0.8644 |
| dancetrack0014 | 0.0304 | 11,571 | 0.3378 | 0.3650 | 0.3092 |
| dancetrack0018 | 0.0814 | 6,894 | 0.8415 | 0.8253 | 0.7200 |
| dancetrack0019 | 0.0260 | 4,532 | 0.3707 | 0.3444 | 0.4313 |
| dancetrack0025 | 0.0137 | 7,145 | 0.6204 | 0.5948 | 0.7529 |
| dancetrack0026 | 0.0341 | 16,013 | 0.4530 | 0.4698 | 0.2379 |
| dancetrack0030 | 0.0357 | 5,323 | 0.5621 | 0.5783 | 0.7665 |
| dancetrack0034 | 0.0414 | 11,898 | 0.4303 | 0.4517 | 0.4617 |
| dancetrack0035 | 0.0192 | 4,647 | 0.4213 | 0.4010 | 0.6166 |
| dancetrack0041 | 0.0300 | 19,635 | 0.2973 | 0.2991 | 0.3639 |
| dancetrack0043 | 0.0608 | 9,149 | 0.5513 | 0.5476 | 0.4756 |
| dancetrack0047 | 0.0373 | 1,069 | 0.3906 | 0.4230 | 0.5088 |
| dancetrack0058 | 0.0294 | 4,679 | 0.5383 | 0.5589 | 0.7912 |
| dancetrack0063 | 0.0279 | 10,057 | 0.2514 | 0.2379 | 0.3750 |
| dancetrack0065 | 0.0302 | 5,116 | 0.3964 | 0.4382 | 0.7829 |
| dancetrack0073 | 0.0634 | 10,445 | 0.3666 | 0.3565 | 0.5097 |
| dancetrack0077 | 0.0413 | 7,574 | 0.6166 | 0.6528 | 0.7675 |
| dancetrack0079 | 0.0227 | 14,940 | 0.6463 | 0.6679 | 0.5696 |
| dancetrack0081 | 0.0359 | 8,230 | 0.4441 | 0.4147 | 0.4617 |
| dancetrack0090 | 0.0231 | 9,290 | 0.4846 | 0.4571 | 0.4604 |
| dancetrack0094 | 0.0753 | 18,554 | 0.4861 | 0.4835 | 0.4307 |
| dancetrack0097 | 0.0894 | 4,196 | 0.4965 | 0.5226 | 0.8669 |

## 高loss 5系列のHOTA(0)統合表

貼付されていた2つの表を、Mamba lossの降順で統合した。ここでのHOTAは HOTA(0) であり、直前の全25系列表に掲載したHOTA AUCとは別指標である。

| sequence | Mamba loss | YOLO＋Mamba HOTA(0) | SAM2＋Mamba HOTA(0) |
|---|---:|---:|---:|
| dancetrack0097 | 0.0894 | 0.5502 | 0.9704 |
| dancetrack0018 | 0.0814 | 0.8580 | 0.8034 |
| dancetrack0094 | 0.0753 | 0.5406 | 0.5357 |
| dancetrack0073 | 0.0634 | 0.4298 | 0.7007 |
| dancetrack0043 | 0.0608 | 0.6926 | 0.7217 |

## lossとHOTAの関係

### 相関

各sequenceを1サンプルとして、lossとHOTA AUCのPearson相関・Spearman順位相関を計算した。統計的有意性の検定は行っていないため、傾向確認として扱う。

| HOTAの対象 | Pearson r | Spearman rho | HOTA平均 |
|---|---:|---:|---:|
| Mamba単体 | +0.308 | +0.245 | 0.4924 |
| YOLO＋Mamba | +0.319 | +0.242 | 0.4917 |
| SAM2＋Mamba | +0.199 | +0.165 | 0.5678 |

期待していた「lossが高いほどHOTAが低い」という負相関は確認できない。相関の絶対値自体も大きくないため、loss単独からHOTAを予測できる状態ではない。

### 代表的な対応・非対応

- dancetrack0018はMamba lossが 0.0814 と高い一方、Mamba単体HOTAは 0.8415、YOLO＋Mambaは 0.8253 だった。bbox遷移の予測誤差が高くても、検出・associationが安定していればHOTAは高くなり得る。
- dancetrack0097はlossが全系列で最大の 0.0894 だが、SAM2＋Mamba HOTAは 0.8669 と高い。Mamba内部の誤差とSAM2統合結果は1対1に対応しない。
- dancetrack0063はloss 0.0279 と低いが、Mamba単体HOTA 0.2514、YOLO＋Mamba 0.2379 と低い。低lossでも検出・欠損・ID association側の問題でHOTAは低下する。
- dancetrack0026はloss 0.0341 と中程度だが、SAM2＋Mamba HOTAは 0.2379 で全系列最低だった。SAM2側で観測欠損やassociationが崩れた代表候補であり、Mamba lossだけでは説明できない。
- dancetrack0094はloss 0.0753 と高く、SAM2＋Mamba HOTAも 0.4307 と低めである。ただし、同じ高lossでも0018や0097のHOTAは高いため、「高lossなら失敗」とは断定できない。

### 解釈

今回のlossはGT bbox列から次のbbox遷移を予測するteacher-forcedな検証lossである。一方、HOTAは実際の検出入力、欠損、track生成、association、ID switchを含む下流評価である。そのため、両者は測っている対象が異なる。

特に、lossが高いsequenceは、bboxの動きや形状変化が大きい可能性がある。しかし、HOTAはそのsequenceで検出が十分でassociationが安定していれば高くなり得る。逆に、MambaがGT遷移を比較的よく予測していても、検出欠損やID切替が多ければHOTAは低くなる。

したがって、MTGで話していた「後半sequenceでlossが高いので難しい」という見方は、少なくともHOTAの低さと同義ではない。lossは「Mambaが動きの予測で苦戦しているsequence」の候補抽出には使えるが、「trackingとして失敗しているsequence」の抽出にはHOTA・DetA・AssA・IDSWとの併用が必要である。

## 今回の分析からの使い分け

| 見たいこと | 主に見る指標 | 今回の結果 |
|---|---|---|
| Mambaのbbox遷移予測が難しいか | sequence別Mamba loss | 0018、0097、0094、0073、0043が高い |
| Mamba単体trackingが失敗しているか | Mamba HOTA / AssA / IDSW | 0063、0041、0014などが低い |
| SAM2＋Mambaの失敗sequenceはどれか | SAM2＋Mamba HOTA / DetA / AssA / IDSW | 0026、0014、0041、0063、0094などを優先確認 |
| Mamba誤差が下流失敗に関係するか | lossとHOTAをframe・track単位で対応 | sequence平均だけでは判断不能 |

## 限界と次の確認

- Mamba lossはsequence平均なので、短い区間の大きな誤差や特定trackの崩れが平均に埋もれる。
- lossとHOTAは同一checkpoint由来だが、lossはGT入力、HOTAは検出器・tracker出力を使うため、因果関係を示さない。
- SAM2＋MambaにはSAM2独自lossを対応付けていない。今回のSAM2列は、Mamba lossと下流HOTAの対応を見るための比較である。
- 次に原因を切り分ける場合は、dancetrack0026、dancetrack0063、dancetrack0094を優先し、track / frame単位でMamba予測誤差、検出欠損、IDSWを同じ時刻軸に並べるのが妥当である。

## 関連

- [SAM2＋Mamba sequence別失敗分析](2026-09-25-sam2-sequence-failure-analysis.md)
- [P4a loss sequence比較](2026-09-25-p4a-loss-sequence-comparison.md)
- [YOLO＋Mamba shuffle比較](2026-09-25-yolo-mamba-shuffle-comparison.md)
