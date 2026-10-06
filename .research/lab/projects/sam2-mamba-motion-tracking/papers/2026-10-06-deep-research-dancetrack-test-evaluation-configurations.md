# SAM2MOT再現実験におけるDanceTrack test評価構成の選定調査

## 結論と候補選定

DanceTrackの公式分割は **train 40系列 / val 25系列 / test 35系列** で、test annotation は非公開です。現在の公式提出先はCodaBenchです。したがって、今回の25系列val結果と論文のtest値は絶対値で直接比較せず、**自分たちのval内の構成差**と、**論文test内の構成差**を別々に扱うのが妥当です。 citeturn3view3turn11search8  
公式データ: `https://github.com/DanceTrack/DanceTrack`  
現行test提出先: `https://www.codabench.org/competitions/14885/`

HOTA 70以上の手法を網羅するのではなく、SAM2MOTとの比較上の役割が異なるものとして、以下の3件に絞るのが有用です。

| 選定手法 | 選定理由 | DanceTrack test HOTAの一次資料上の位置づけ |
|---|---|---|
| **MOTIP** | 「検出 → 学習型ID association」と明示的に分離した方式で、tracking-by-detectionに近い問題分解を保ちながらassociationを学習化している。SAM2MOTの「検出器を利用しつつtracking本体を別機構にする」設計と比較しやすい。 | CVPR 2025 Table 1 の **with extra data: 72.0**。追加データなしは69.6なので、72.0を引用するときは条件差が必須。 citeturn25view0turn27view2 |
| **ColTrack** | 検出ファイルを後段でheuristic matchingする方式ではなく、複数の履歴queryを用いてassociationを強化するend-to-end方式。DanceTrack特有の類似外観・複雑運動に対する「履歴情報の使い方」をSAM2MOTのCross-object Interactionと対比できる。 | ICCV 2023 Table 5 の通常構成で **72.6**。+valの75.3ではなく、通常行を採る。 citeturn20view0 |
| **MOTRv2** | YOLOXの検出proposalを毎フレームMOTRへ与えるため、外部検出器にtrackingをbootstrappingする方式。SAM2MOTの「強いpretrained detectorをtrackingへ利用する」という条件差を見る境界例として有用。 | 原論文・公式実装は **73.4** をchallenge resultとして報告。ただし公開標準checkpointは69.9で、73.4は通常公開モデルと同条件ではない。 citeturn16search16turn26academia20 fileciteturn0file0L2-L2 |

この選び方では、**ColTrackを比較条件が比較的明瞭な70+参照点、MOTIPを「学習型association」参照点、MOTRv2を「検出器依存・追加条件の強い70+値を安易に横比較してはいけない例」**として使えます。逆に、DanceTrackで一般的なByteTrack/OC-SORTは70未満なので選定3件には含めません。ただしSAM2MOT論文自身が同じCo-DINO-L / Grounding-DINO-L入力でByteTrackとOC-SORTを再評価しており、**SAM2MOTのtracker部分を理解するには、70+のcross-paper比較よりこちらの方が制御された比較です**。 citeturn7view1turn9view0

## 対象手法の条件比較

### 選定したHOTA 70以上の関連手法

| 手法・採用variant | HOTA / MOTA / IDF1 | split | 検出器・検出入力 | 学習データ・外部データ | 主要構成 | 公式コード | 数値の一次資料・URL |
|---|---:|---|---|---|---|---|---|
| **MOTIP** `with extra data` | **72.0 / 91.9 / 76.8** | DanceTrack **test** | **Deformable DETR + ResNet-50**。各フレームのdetector出力embeddingをID Decoderへ入れるため、外部の固定detection txtを後段associationする形式ではない。COCO pretrained weightsで初期化。 citeturn25view0turn27view2 | Table 1では qualifying row を単に **“with extra data”** と表記。今回確認した本文では、その72.0行に使った追加データセット名を一意に結び付けられなかったため**未記載扱い**とする。なお論文はCrowdHuman等の追加検出データを別途議論しているが、そこから72.0行のデータを推測しない。 citeturn27view0turn27view2 | detector、ID dictionary、Transformer ID Decoder、trajectory augmentation。associationをin-context ID predictionとして学習。 citeturn25view0 | **有**。ただし現在の公式Model Zooで公開されているDanceTrack checkpointは**extra dataなし69.6**で、Table 1の72.0 artifactは同一覧にない。 fileciteturn1file0L2-L2 fileciteturn2file0L2-L2 | **CVPR 2025, Table 1**。`https://openaccess.thecvf.com/content/CVPR2025/html/Gao_Multiple_Object_Tracking_as_ID_Prediction_CVPR_2025_paper.html` / arXiv DOI `https://doi.org/10.48550/arXiv.2403.16848` |
| **ColTrack** | **72.6 / 92.1 / 74.0** | DanceTrack **test** | DINO系DETR-like detector、**ResNet-50**。current-frame detection queriesとhistorical tracking queriesをモデル内で処理。外部detection fileをassociation器に渡す古典的TbDではない。 citeturn19view0turn20view0 | DanceTrack学習時に、論文Sec. 4.1は**CrowdHumanをjoint datasetとして追加**すると明記。40 epochs。なお+val variantは別に75.3を報告するが、本比較では採らない。 citeturn19view0turn20view0 | Collaborative Tracking Queries、temporal blocking decoder、Information Refinement Module、Tracking Object Consistency Loss。 citeturn19view0 | **有**。公式READMEも72.6 / 92.1 / 74.0を掲載。 fileciteturn3file0L2-L2 | **ICCV 2023/arXiv, Table 5**。`https://arxiv.org/abs/2308.05911` / DOI `https://doi.org/10.48550/arXiv.2308.05911` |
| **MOTRv2 challenge variant** | **HOTA 73.4**。MOTA/IDF1は今回確認したMOTRv2一次資料の73.4 artifactについて**一次確認できず**。ColTrack Table 5は`+val+ens`を **92.1 / 76.0** と転載しているが、これは参考値としてのみ扱う。 citeturn20view0turn26academia20 | DanceTrack **test** | **YOLOX detection proposals**をMOTRのdetect-query anchorとして与える。公式実装は事前生成YOLOX detectionのダウンロードを要求する。 citeturn26search1 fileciteturn0file0L2-L2 | 技術報告は**CrowdHumanからpseudo videoを生成したjoint training**を明記。公式repoもDanceTrackとCrowdHumanを学習データ準備に要求。73.4についてColTrack Table 5は`+val+ens`と記載するため、通常設定より強い条件として扱う。 citeturn26academia19turn20view0 fileciteturn0file0L2-L2 | MOTR + anchor formulation + pretrained YOLOX proposal。 | **有**。ただし公式公開モデルのMain Resultsは **69.9 / 91.9 / 71.7** であり、73.4 challenge resultとは別条件。 fileciteturn0file0L2-L2 | **CVPR 2023**。`https://openaccess.thecvf.com/content/CVPR2023/html/Zhang_MOTRv2_Bootstrapping_End-to-End_Multi-Object_Tracking_by_Pretrained_Object_Detectors_CVPR_2023_paper.html` / official code `https://github.com/megvii-research/MOTRv2` |

MOTRv2は特に注意が必要です。公式repositoryが現在直接配布しているDanceTrack modelは **HOTA 69.9 / MOTA 91.9 / IDF1 71.7** ですが、論文abstractとchallenge technical reportでは73.4を掲げています。つまり、「MOTRv2 = 73.4」と一行だけ書くと、**公開標準モデル69.9と、追加条件を持つchallenge variantを混同する**ことになります。 citeturn16search16turn26academia20 fileciteturn0file0L2-L2

同様にMOTIPも、CVPR論文Table 1では**追加データなし69.6、with extra data 72.0**です。したがって「MOTIPは72以上」という引用は、SAM2MOTのzero-shot/no-finetuning条件と同じ意味ではありません。 citeturn27view2

### SAM2MOT原論文と今回の再現

SAM2MOTの最終DanceTrack値はすべて**test split**です。Co-DINO-L版が **HOTA 75.5 / MOTA 89.2 / IDF1 83.4**、Grounding-DINO-L版が **75.8 / 88.5 / 83.9**。論文はCo-DINO-LをCOCO pretrained、Grounding-DINO-LをCOCO・Objects365でpretrainedされた検出器として使用し、benchmarkごとの追加fine-tuningなしで適用し、segmentation/tracking側にはSAM2.1-largeを用います。 citeturn8view0turn8view1turn6view0  
論文: `https://arxiv.org/abs/2504.04519`  
AAAI 2026 DOI: `https://doi.org/10.1609/aaai.v40i7.37455`

| 構成 | HOTA | MOTA | IDF1 | split | 条件・出典 |
|---|---:|---:|---:|---|---|
| SAM2MOT baseline, Co-DINO-L | 62.9 | 55.6 | 69.6 | test | Table 3。 citeturn7view0turn9view0 |
| + Object Addition | 67.9 | 69.7 | 74.4 | test | Table 3。baseline比HOTA +5.0。 citeturn7view0turn9view0 |
| + OA + Cross-object Interaction | 73.8 | 87.4 | 80.9 | test | Table 3。OA比HOTA +5.9。 citeturn7view0turn9view0 |
| + OA + CoI + Quality Reconstruction | **75.5** | **89.2** | **83.4** | test | Table 3。直前比HOTA **+1.7**。 citeturn7view0turn9view0 |
| SAM2MOT final, Grounding-DINO-L | **75.8** | **88.5** | **83.9** | test | Table 1。 citeturn8view1 |
| **今回 S1 baseline** | **59.21** | 未提示 | 未提示 | **val 25系列** | ユーザー提示。detector・weights・threshold等は本依頼では未提示。 |
| **今回 S2 +OA** | **64.32** | 未提示 | 未提示 | **val 25系列** | ユーザー提示。S1比 +5.11。 |
| **今回 S3 +CoI（A6のみ）** | **68.22** | 未提示 | 未提示 | **val 25系列** | ユーザー提示。S2比 +3.90。原論文のfull CoIと同一構成とは扱わない。 |
| **今回 S4 +Q-R** | **61.85** | 未提示 | 未提示 | **val 25系列** | ユーザー提示。S3比 **−6.37**。 |

Grounding-DINO-L側の原論文Table 3でも、baseline→OAは **60.9→67.4**、OA+CoIは **73.6**、fullは **75.8** で、full CoIにQ-Rを追加した差は **+2.2 HOTA** です。またCoIなしでOAにQ-Rだけを足した比較でも、Co-DINO-Lは67.9→69.1、Grounding-DINO-Lは67.4→69.0と正方向です。したがって、**原論文では2種類のdetector、2種類のQ-R差分のどちらでもQ-Rによる大幅悪化は報告されていません**。 citeturn7view0turn7view3turn9view0

なお、SAM2MOTの公式GitHubはREADME上で詳細なディレクトリ構成・実行コマンドまで掲載していますが、2026年10月6日時点でdefault branchの実体を確認すると、rootには`.gitignore`、`LICENSE`、`README.md`、`assets/`しかなく、README自身にも「code will release soon」という未完了項目が残っています。したがって**公式repositoryは有るが、論文実装を照合できるソースコードは現時点で公開されていない**と判断するのが安全です。 fileciteturn4file0L2-L2 fileciteturn5file0L1-L13  
公式repository: `https://github.com/TripleJoy/SAM2MOT`

## SAM2MOT再現との直接比較

### 直接比較できること

今回の再現で最も信頼できる比較単位は、**同一val 25系列・同一実装・同一検出入力の中でのstage差**です。S1→S2は+5.11、S2→S3は+3.90、S3→S4は−6.37 HOTAなので、少なくとも現在のコードでは「Object AdditionとA6-only CoIは正方向、Q-R追加時のみ大きく崩れる」という内部的な事実があります。

原論文側にも同じく**同一test split・同一detector内のablation差**があり、Co-DINO-Lでは baseline→OA +5.0、OA→OA+CoI +5.9、OA+CoI→full +1.7、Grounding-DINO-Lではそれぞれ+6.5、+6.2、+2.2です。これはsplitをまたいだ絶対値比較ではなく、**「各split内で各componentを有効化したときの方向」**を照合するためには使えます。 citeturn7view0turn9view0

その意味で、S4の−6.37は重要です。これは「testならS4は上がるはず」と予測する根拠ではありませんが、**Q-Rの実装を監査する十分な理由**にはなります。特に論文のQ-Rは、pending状態のobjectについて、**current tracking boxがObject Additionで得られたhigh-confidence detectionに正常にmatchした場合に、そのmatched detectionを使ってkey-frame informationを再構成する**ものです。単に「pending objectの近傍にhigh-confidence detectionがあれば更新する」という処理ではありません。 citeturn6view0turn8view0

### 直接比較できないこと

**59.21、64.32、68.22、61.85という今回のval値を、62.9、67.9、73.8、75.5という原論文test値から引いて「再現差」と呼ぶことはできません。** splitそのものが異なります。DanceTrackの25系列valと35系列testは別集合で、test GTは非公開です。 citeturn3view3

さらに、今回のS3は「Cross-object Interaction（A6のみ）」とのことなので、原論文Table 3の“CoI✓”行と同一componentであることも未確認です。原論文のCross-object Interactionには、重なりobjectの識別、mask IoU、stage-1 logit差、複数frameのtracking-logit varianceなど複数条件が含まれ、論文設定では履歴長 \(N=10\) を使います。 citeturn6view0turn8view2

また、MOTIP・ColTrack・MOTRv2との絶対値横比較には学習条件差があります。MOTIPの72.0はextra-data variant、ColTrackはDanceTrack+CrowdHumanで学習、MOTRv2の73.4はchallenge条件で、少なくとも他論文の整理では+val+ensembleです。一方SAM2MOTはDanceTrackでfine-tuneせず、強いpretrained detectorとSAM2.1を組み合わせます。したがって、**「75.5 > 73.4 > 72.6だからtracking paradigmとしてSAM2MOTが何点優れている」という読み方は成立しません**。 citeturn27view2turn19view0turn20view0turn8view0

tracking-by-detectionとの比較だけを目的にするなら、cross-paperの70+手法より、SAM2MOT論文Table 2の同一detector比較の方が強い証拠です。Co-DINO-L入力ではByteTrackが **HOTA 56.1 / MOTA 87.2 / IDF1 56.6**、OC-SORTが **56.2 / 86.5 / 56.8**、同じ表のSAM2MOTが75.5 / 89.2 / 83.4です。Grounding-DINO-LでもByteTrack 53.3、OC-SORT 53.6に対してSAM2MOT 75.8です。これは少なくとも検出器の種類を揃えた比較になっています。 citeturn7view1turn9view0

したがって、今回のtest提出で主に答えるべき問いは**「外部70+手法に勝つか」ではなく、「自分たちの固定したS2→S3、必要ならS3→S4の効果が、未知の35系列でも維持されるか」**です。

## DanceTrack testで評価する最小構成

現状では、**必須2構成をS2とS3、Q-R監査が完了した場合だけS4を同時追加**する案を推奨します。S1は最小案から外します。

| test提出構成 | 扱い | 答える研究上の問い | 含める根拠 |
|---|---|---|---|
| **S2: baseline + Object Addition** | **必須** | 「現在の実装で、detectorを用いたObject Additionまでの構成をtestに移したとき、S3の比較基準として安定しているか」 | S3との差がCoI（A6-only）の増分を直接表す。現在valでは64.32で、S1から+5.11。原論文にもOA単独行があり、ablationの対応関係を作りやすい。 citeturn7view0turn9view0 |
| **S3: S2 + Cross-object Interaction（A6のみ）** | **必須** | 「A6-only CoIによるval上の+3.90 HOTAが、未知testでも同方向のassociation改善として現れるか」 | 現在のval最良構成68.22であり、かつS2とのpaired comparisonでcomponent効果を切り分けられる。原論文でもCoIが主要なHOTA増加要因。 citeturn7view0turn9view0 |
| **S4: S3 + Quality Reconstruction** | **条件付き** | 「実装正当性を確認したQ-Rが、同じS3基盤に対しtestでも追加価値を持つか」 | 原論文ではCo-DINO-Lで+1.7、Grounding-DINO-Lで+2.2 HOTAだが、現状valは−6.37。**現在のままではtestに出す根拠より、バグを疑う根拠の方が強い。** citeturn7view0turn9view0 |

**最小提出はS2とS3の2本**です。これだけで、今回もっとも重要な「現在のCoI実装がOAに対して未知系列でも寄与するか」を、一度のtest確認で答えられます。

S1を外す理由は、S1→S2のObject Addition効果までtestで完全なablationを取り直すことは再現論文としては有用でも、**「どの現行構成をtestで確認するか」という今回の意思決定にはS2→S3の方が情報量が大きい**ためです。提出数を1本だけに極端に制限する場合はS3になりますが、その場合はtest上でCoIの効果を分離できません。そのため研究上はS2+S3のpaired submissionを最低単位とする方がよいです。

S4は「valでS3を超えたら提出」という性能選択にはしない方がよいです。それではvalに対して原論文の方向を再現するまで調整することになり得ます。**提出条件は性能ではなく実装正当性で決める**べきです。Q-Rのmatch・state transition・keyframe更新が論文記述どおりであることを確認し、その修正をtest scoreを見る前にfreezeできた場合のみS4を同じ提出回に含めます。 citeturn6view0turn8view0

また、S2・S3・条件を満たしたS4は**すべてtest scoreを見る前に生成・freezeし、可能なら同じ提出セッションで全て提出してから結果を見る**運用が最も明快です。最初のS3結果を見てthresholdを変更し、その後S4を作る、といった運用は避けます。

## 評価前に固定する設定と見送り条件

### 固定すべき実験設定

最優先は、**test scoreを見る前に「コード・入力・パラメータ・評価器」を一意に再現可能な状態にすること**です。具体的には、各提出についてGit commit hash、Python/torch/SAM2環境、detector checkpoint hash、SAM2/SAM2.1 checkpoint hash、precomputed detectionを使うならそのfile hashを記録します。

検出条件は特に重要です。現行SAM2MOT論文のimplementation detailsでは、Object Additionのhigh-confidence detector thresholdはデフォルトで **Co-DINO-L 0.5、Grounding-DINO-L 0.4**、untracked-region条件 \(r=0.7\)、object removal tolerance 25 frames、tracking logitsの閾値として \(\tau_r=8.0,\tau_p=6.0,\tau_s=2.0\)、Cross-object Interactionの履歴長 \(N=10\) が記載されています。 citeturn8view0turn6view0

ただし現在のSAM2MOT READMEはDanceTrack test用に`co_dino_detections_thresholds.csv`や`grounding_dino_detections_thresholds.csv`という**sequence別に見えるthreshold file**を参照する実行例を掲載しています。一方、実repositoryにはその`config/`自体が公開されていません。したがって、このファイルの値を推測してtest系列ごとにthresholdを決めるのは避け、**今回の再現でval上ですでに確定した単一ルールをそのままtestに適用する**のが再現実験として最も defensible です。 fileciteturn4file0L2-L2 fileciteturn5file0L1-L13

Q-Rについては、提出前にイベントログで少なくとも次を機械的に検証すべきです。Q-R発火対象がpending stateであること、更新に使うboxが**そのtrackとmatchしたhigh-confidence detectionそのもの**であること、一つのdetectionが複数trackを再構成していないこと、Q-R後もIDが保持されること、keyframeのbox/mask/promptのどれを更新したかが追跡可能であることです。論文の記述ではQ-Rはpending objectの現在boxとhigh-confidence detectionの成功matchをトリガーにします。 citeturn6view0turn8view0

評価器もfreezeします。公式DanceTrackはHOTAを中心にDetA、AssA、MOTA、IDF1等を評価します。今回の**primary endpointはHOTA**のままにし、モジュールの作用を読むためにAssA/IDF1とDetA/MOTAを併記するのが適切です。 citeturn3view3turn11search8

判定は次のように事前定義しておくと、testをvalidation代わりに使わずに済みます。

**S3対S2**では \(\Delta HOTA=HOTA_{S3}-HOTA_{S2}\) を主要なmodule effectとしてそのまま報告し、AssA/IDF1の変化でassociation由来かを診断します。MOTA/DetAの大幅な変動がある場合は、「CoIだけの純粋なassociation改善」とは解釈しません。結果が原論文より低い・高いこと自体を理由にthresholdを変えません。

**S4対S3**も、実装監査を通った場合に限り同様のpaired deltaを最終結果として報告します。負になっても再度test向け調整をせず、「正しく実装した範囲では今回の再現条件/test splitでQ-R benefitを再現できなかった」と結論づけます。

### test提出を見送る条件

**全体のtest提出を見送るべきなのは、val結果自体がfreezeした環境で再現できない場合です。** 同じcommit・同じdetections・同じevaluatorでS2=64.32、S3=68.22という基準結果を再生成できない、sequence/frame indexingやMOT output formatに未解決の問題がある、duplicate IDやNaN/invalid boxが残る、といった状態ではtestへ進める根拠がありません。

また、**test系列を見て個別thresholdを選ぶ必要が生じた場合も見送る**べきです。原論文側の非公開threshold fileが存在する可能性は、今回の再現側でtest-specific tuningを正当化しません。testへはvalで事前固定したルールのみ適用します。SAM2MOT公式repoの実装ファイルが現時点で公開されていないため、非公開設定を完全再現できない点はそのままlimitationとして残します。 fileciteturn5file0L1-L13

S4だけについてはさらに厳しく、**Q-Rのmatch条件が未解決、同じdetectionが誤ったtrackを更新する事例が残る、pending→reconstructed transitionのログを説明できない、またはS4の大幅悪化の原因が既知の実装不整合である**場合はS4のみ提出対象から外します。S4を外すことはS2/S3のtest確認を妨げません。

## 未確認事項

**最も判断に効く未確認事項は三点です。**

**Q-Rの「successfully matches」の完全なmatching仕様。** 論文は「pending objectのcurrent tracking boxがObject Addition由来のhigh-confidence detectionとmatchしたとき」と明記しますが、Q-R専用のcost、IoU threshold、競合解消順序など、実装を一意に復元するための細部までは本文から確定できません。 citeturn6view0turn8view0 さらに公式repositoryには実装コードが現時点で存在しないため、ここがS4の最大の再現不確実性です。 fileciteturn5file0L1-L13 **追加調査の優先度は最上位**で、著者実装公開・supplement更新・著者回答など一次資料が得られた場合のみ再確認価値があります。

**SAM2MOT test用detector thresholdの実値。** READMEは`config/dancetrack_test/*_detections_thresholds.csv`を使う例を示す一方、そのファイルはdefault branchに公開されておらず、論文本文は0.5/0.4というdefault thresholdを記載します。 citeturn8view0 fileciteturn4file0L2-L2 fileciteturn5file0L1-L13 もし論文test値75.5/75.8がsequence-specific detector thresholdsを使っているなら、今回の固定global thresholdとの絶対値比較可能性に大きく影響します。**これは外部手法との順位より重要な条件差**です。

**今回の再現がどのSAM2MOT版・detector条件を基準にしているか。** ユーザー提示情報からは、detector種類・checkpoint、detection confidence rule、SAM2/SAM2.1 checkpoint、Object Additionの\(r\)、CoIのA6以外を無効にした具体的差分、Q-R matching ruleまでは確定できません。一方、現行arXiv版には上記thresholdや\(r=0.7\)等が明記されています。 citeturn6view0turn8view0 したがってtest提出前の研究記録では、**「SAM2MOTを再現した」ではなく、参照したpaper versionと、原論文から意図的・非意図的に異なる設定を明記すること**が必要です。

以上を踏まえると、現時点の最も保守的で情報量の高い判断は、**DanceTrack testにはS2とS3を同時に一度だけ提出する。S4はQ-Rのmatching/update semanticsをtest scoreを見る前に監査・freezeできた場合だけ同じ提出セットに加える。現状の61.85のまま、原因未解決でS4を提出することは見送る**、です。外部のHOTA 70+という数字は到達目標ではなく条件付きの参照点とし、今回のtestでは自分たちのpaired component effectを主対象にするのが、split差とtest leakageの双方を避ける設計です。