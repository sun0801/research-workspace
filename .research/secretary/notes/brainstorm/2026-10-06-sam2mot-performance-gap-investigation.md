---
date: 2026-10-06
project: sam2-mamba-motion-tracking
source_todo: HOTA 70以上のMOT手法とSAM2MOT再現条件の比較
topic: sam2mot-performance-gap-investigation
status: exploratory
tags: [brainstorm, research, sam2mot, dancetrack]
---

# SAM2MOT再現と論文値の性能差を調べる方向

## 読み込んだ文脈

- 2026-09-30 MTGでは、A6のみのDanceTrack val HOTA 68.22と論文値約75との差について、HOTA 70以上の手法の学習条件・評価条件・実装上の選択を照合し、差の要因を調べるとした。特定の「トリック」があるとは仮定しない。
- 今回保存したDeep Researchレポートは、DanceTrack testでの高HOTA手法と提出構成の選定が中心になり、性能差の原因、とくにSAM2MOTおよび比較手法の学習・追加データ条件を主題として深掘りできていない。
- レポートには、SAM2MOTがCOCO/Objects365等で事前学習した検出器とSAM2.1-largeを使い、DanceTrackで追加fine-tuningしないという記述、またMOTIP/ColTrack/MOTRv2の追加データ・challenge条件に関する手がかりがある。

## 相談の出発点

HOTA約75の論文値に対し、似た構成の再現がvalで68.22にとどまる理由を探りたい。特に、SAM2MOT本体や同程度のHOTAを報告するDanceTrack手法が、特別な学習方法、追加学習、追加データ、強い事前学習済みモデルを使っていないか確認する。

## 問い

SAM2MOTの論文値と今回の再現値の差を説明しうる学習・データ・モデル条件は、一次資料でどこまで確認できるか。またDanceTrackでHOTAがおよそ70以上の比較手法にも、どのような追加学習・追加データ・事前学習条件があるか。

## アイデア候補

- SAM2MOTの検出器とsegmenterについて、初期checkpoint、事前学習データ、DanceTrack上のfine-tuning有無、論文のablation条件を一次資料で確認する。
- DanceTrackでHOTAがおよそ70以上の手法を少数選び、学習データ、追加データ、学習方式、pretraining、ensemble/challenge条件、公開checkpointとの差を比較する。
- その条件と今回の再現の差を対応づけ、性能差の説明候補を「確認済み」「可能性」「未確認」に分ける。
- split、検出器、閾値、評価器、実装差は、学習条件とは別の説明軸として整理する。

## 今回見えた方向性

追調査は有用。ただし、前回レポート全体をやり直さず、そこにある候補手法とSAM2MOTの出典を起点に、学習・追加データ条件の根拠を掘り下げる。目的はtest提出構成の選定ではなく、再現値と論文値のギャップを説明しうる条件を特定すること。

## 次アクション候補

- Deep Researchへ、SAM2MOTとDanceTrackでHOTAがおよそ70以上の比較手法の学習・事前学習・追加データ条件に絞った追調査を依頼する。
- 結果から、有力な説明要因と未確認事項を切り分ける。追加実験・test提出の要否は、その後に判断する。

## 未解決の問い

- 「SAM2MOT内でHOTAが70程度」の範囲は、SAM2MOT論文内の比較表に載る手法か、DanceTrack benchmark全体の同程度の手法か。追調査では後者を含みつつ、SAM2MOT論文内比較を優先するのが妥当そう。
- 追加データや特別な学習条件が確認できても、それが今回の7ポイント差をどの程度説明するかは、同一split・同一入力条件の比較なしには確定できない。

## 関連ファイル

- `.research/lab/projects/sam2-mamba-motion-tracking/meetings/2026-09-30-mtg.md`
- `.research/lab/projects/sam2-mamba-motion-tracking/papers/2026-10-06-deep-research-dancetrack-test-evaluation-configurations.md`
- `.research/lab/projects/sam2-mamba-motion-tracking/experiments/2026-10-03-sam2mot-s4-qr-results.md`

---

## 追記 19:27 JST

### 追加調査レポートを踏まえた次の方向

ユーザーは、保存した一次資料調査レポートを踏まえ、SAM2MOT再現の差を説明する次の作業を整理する方針を採用した。

レポート上の主要な手がかり:

- 論文本文はCo-DINO-LをCOCO pretrainedと記載する一方、公式READMEはObjects365→COCOのcheckpointを示す。再現で使った3x_cocoとの差は、一次資料同士に不整合があるものの、比較可能な具体的条件差。
- SAM2MOTはDanceTrack-specific fine-tuningをしていないと主張するが、強い事前学習済みdetector/segmenterを使う。高HOTA比較手法の追加データ利用は、SAM2MOTが隠れた追加学習をした証拠にはならない。
- Q-Rのval大幅悪化、Q-Rの最終実装、test threshold CSV、SAM2/SAMURAI code lineageにも未解決点が残る。
- DanceTrack test 35系列の検出生成は実験記録上開始済みだが、追跡run・test提出構成は未決定。

### 次アクション候補と順序

1. 追加学習の有無を主仮説に固定せず、まず Co-DINO checkpoint（現行3x_coco / 公式README記載o365tococo）の影響を、他条件を固定したval比較で切り分ける案を検討する。
2. Q-Rのmatching / reconstruction / re-promptの未解決点は別の切り分けとして扱い、checkpoint比較と混ぜない。既存候補はmatch IoU threshold、発動間隔、A5をconditioning frameでなくrefinementとして行う設定。
3. val上の診断後、どの段をDanceTrack testで評価するかを決め、コード・checkpoint・閾値・評価条件をtest結果を見る前にfreezeする。Q-Rは実装監査ができた場合のみ候補に含める。

これらは次アクション候補であり、今回TODOへの自動追加や実装開始の承認を意味しない。外部実装を変更する場合は承認済みspec・変更範囲・検証方法・実装開始承認を確認する。

### 関連ファイル

- `.research/lab/projects/sam2-mamba-motion-tracking/papers/2026-10-06-deep-research-sam2mot-reproduction-gap.md`
- `.research/lab/projects/sam2-mamba-motion-tracking/experiments/2026-10-03-sam2mot-s4-qr-results.md`
