> 生成元：ChatGPT Deep Research（2026-11-06）。英論文紹介（3本）の候補をTracking論文に絞って選び直すため、Claude Codeとの会話で作成したプロンプト（末尾の付録）で実行した。前回までの調査は [11/4版](2026-11-04-deep-research-paper-intro-ssm-state-candidates.md)・[11/6 既知込み版](2026-11-06-deep-research-paper-intro-candidates-incl-known.md)。以下はレポート本文をそのまま保存したもので、内容は書き換えていない。本文中の `citeturn...` はChatGPT内部の引用マーカーで、URLには解決できない。数値や採録状況を使う際は一次資料で再確認すること。

# 英論文紹介候補調査：Trackingにおける時間 state・memory の引き継ぎと汚染対策

## 結論

**第一候補は `Memory as Dynamics`（ICML 2026）＋ `SENTRY`（ECCV 2026）＋ `Hypergraph-State Collaborative Reasoning`（CVPR 2026）**。順に「予測 state は汚染される → 書き込み前に信頼性を検証する → state に空間・物体間対応を与えて motion を改善する」とつながり、現在の研究課題に最も直接的です。citeturn859512view0turn513028academia8turn760026search0  
**第二候補は `MambaVLT`（CVPR 2025）＋ `Memory as Dynamics`＋ `Dual-Path Temporal Decoder`（NeurIPS 2025）**。Mamba state carryそのものから始め、「無条件の carry の危険性」「低信頼時には state/query を更新しない」という流れを作れます。citeturn863911view6turn859512view0turn587904search1  
**第三候補は `DAM4SAM`（CVPR 2025）＋ `SENTRY`＋ `Memory as Dynamics`**。SAM2/SAMURAI系だけで統一し、「何をmemoryに残すか → 書く前に検証する → predictive stateを信頼度でgateする」という極めて研究直結の発表になります。citeturn587904search3turn513028academia8turn859512view0  
3本だけ選ぶなら、**新規性と研究への直結度を優先して第一候補**を推します。特に `Memory as Dynamics` は論文自身が「誤った予測がinternal stateをcontaminateし、不可逆なidentity lossを起こす」と問題設定しており、現在の仮説とほぼ一致します。citeturn859512view0

## 候補の全体像

今回確認した範囲では、2025–2026年のトップ会議Tracking論文で、**Mamba/SSMの内部stateをそのまま長期carryしつつ、遮蔽時の汚染まで正面から扱う論文はまだ多くありません**。その代わり、重要な流れは三つに分かれています。第一は `MambaVLT` や `HyperSSM` のような **SSMによる時間state／motion modeling**、第二は `Dual-Path Temporal Decoder` や `Memory as Dynamics` のような **信頼度に応じたstate更新抑制**、第三は `DAM4SAM`・`SENTRY`・`SAM2Long` のような **SAM2 memoryへの誤書き込みを防ぐ設計**です。citeturn760026search2turn760026search0turn587904search1turn587904search3turn513028academia8

この整理から見ると、現在の「固定pixel位置のtemporal Mambaが効かない」という結果に対する次の仮説は、単純にstate容量を増やすことよりも、**① stateをどの物体・位置に対応させるか、② observationが不確かなときに更新しないか、③ prediction自体の信頼度をどう推定するか**に置くのが自然です。これは私の推論ですが、HyperSSMが物体軌跡単位で空間相関を入れ、Dual-Pathがhistorical sampling offsetを保持し、SENTRYが候補trackletの時間整合性でmemory writeを検証していることと整合します。citeturn167589view0turn587904search1turn513028academia8

### Mamba・SSM・線形再帰をstateとして使う論文

| 論文 | 採録・資料 | タスク / stateの単位 | 更新・対応の要点 | 重要なアブレーション | SAM2との関係 / 発表適性 |
|---|---|---|---|---|---|
| **Memory as Dynamics: Learning Reliability-Guided Predictive Models for Online Video Perception** — Minwoo Kim, Sang Min Yoon | **ICML 2026**, PMLR 306, pp.59194–59210。公式PMLRに論文・コードへのリンクあり。citeturn587904search0turn859512view0 | SOT/VOS。SAM2上の**predictive latent memory**を動的stateとして扱う。latent world modelはstate-space dynamicsで予測priorを生成。citeturn859512view0 | 無条件predictionではなく、**reliability-aware fusion**で遮蔽・弱観測時の予測寄与を抑える。「予測誤りがinternal stateをcontaminateする」という問題を明示。citeturn859512view0 | 公式abstractはstatic memory／unconditional predictive modelに対する優位とocclusion後drift低減を報告するが、今回取得できた公式HTMLからは本文の個別Table数値を信頼できる形で抽出できなかったため、数値はここでは断定しない。citeturn859512view0 | **SAM2.1 backbone frozen**で、公開コードは「predictive-memory promptだけを学習」と明記。Mambaをpredictive-memory dynamicsに使用。今回の研究に最も近く、発表価値は非常に高い。citeturn494455view0 |
| **Hypergraph-State Collaborative Reasoning for Multi-Object Tracking** — Zikai Song et al. | **CVPR 2026 main**, pp.28123–28133、arXiv **2604.12665**。citeturn760026search0turn760026academia9 | MOT。各物体の**位置・motion trajectory segment**を入力し、HyperSSMで時空間推論。訓練入力は5-frame trajectory segment。citeturn863911view2 | SSMの時間状態遷移に、同一時刻の複数物体を結ぶ**dynamic hypergraph**を組み合わせる。つまり「各targetを独立にcarry」せず、似たmotionを持つobject同士でstate推論を補正する。citeturn760026search8 | **Table 5**：同じdetector/associationで DanceTrack HOTA は Kalman 47.0、OC-Kalman 52.5、通常SSM 53.7、HyperSSM **59.7**。IDF1は52.2/54.3/53.5/**60.6**。MOT17では64.5/64.6/63.4/**65.5**。つまり非線形motionで差が大きい。citeturn167589view0 | SAM2非依存。Kalman置換という現在のテーマに非常に直接的。図も「trajectory→hypergraph→SSM」と説明しやすく、3本目として強い。 |
| **MambaVLT: Time-Evolving Multimodal State Space Model for Vision-Language Tracking** — Xinqi Liu et al. | **CVPR 2025 main**, pp.8731–8741。citeturn760026search2 | Vision-language SOT。各TEMF layerについて、前時刻の**Mamba final state space**を保持するmulti-level state-space memory。citeturn863911view6 | `H_t^ini = a H^l + (1-a) H_{t-1}^fin` で前フレームstateを次フレームの初期stateへcarry。α/βのtext-first/template-first scanを持ち、別々のAをstate update gateとして使用する。citeturn863911view6 | **Table 3**：baseline→+THSSで TNL2K AUCが BBOX **60.9→62.1**、NL **55.3→56.8**、NL&BBOX **62.6→64.5**。著者はそれぞれ+1.2/+1.5/+1.9 AUCと報告。citeturn167589view3turn520887view1 | SAM2非依存。**「state carryそのもの」を最も素直に見せられる**一方、pixel spatial correspondenceやcontamination対策は弱い。研究導入用として非常に分かりやすい。 |
| **Exploring Historical Information for RGBE Visual Tracking with Mamba** — Chuanyu Sun et al. | **CVPR 2025 main**, pp.6500–6509。citeturn482676search2 | RGB+Event SOT。Mambaでhistorical query／target appearance changeをautoregressiveに保持。citeturn482676search2 | gate-based cross-modal interactionとhistorical decoderを組み合わせる。citeturn482676search2 | センサ融合の寄与とhistory利用を示すが、今回の中心問題であるSAM2 memory contaminationとの距離は大きい。citeturn482676search2 | 特殊なRGB-event設定なので、英論文紹介3本には優先しない。 |

HyperSSMは特に重要です。通常のSSMを単にKalmanの代わりに置くより、**他物体との空間的motion relationを明示的にstate計算へ入れることで、DanceTrack HOTAが53.7→59.7**まで上がっています。一方MOT17では63.4→65.5なので、論文自身の結果も「長いSSM stateそのもの」より、**非線形motion・occlusion環境でどの空間関係をstateに与えるか**が効いていると読むのが妥当です。これは論文報告値に基づく私の解釈です。citeturn167589view0

### 学習ベースmotionと空間対応

**Dual-Path Temporal Decoder for End-to-End Multi-Object Tracking** は、Mambaではないものの現在の問題にかなり重要です。NeurIPS 2025 Main Conference採録で、appearanceを更新するdecoderと、identityを保つdecoderを分離します。identity-preserving側では**query featureを更新せず、過去フレームのsampling offsetsを再利用**し、さらに低confidence時にはquery updateそのものを止めます。つまりstateの「内容」と「どこを見るか」を同時に固定する設計です。citeturn587904search1

論文のDanceTrack ablationでは、identity-preserving decoderなしが HOTA **66.7** / IDF1 **69.5**、identity pathを入れてoffsetを毎回予測すると **67.5 / 73.2**、過去のsampling offsetsを再利用すると **69.1 / 74.9**でした。またconfidence-guided suppressionは、なし **67.9 HOTA / 59.2 AssA / 72.9 IDF1**に対し、threshold β=0.4で **69.1 / 61.6 / 74.9**でした。したがって「信頼度の低い観測でrepresentationを書き換えない」だけで HOTA +1.2、AssA +2.4、IDF1 +2.0というきれいな実験になっています。これは、あなたのMamba stateについて「遮蔽中は `h_t=f(h_{t-1},x_t)` を実行しない／弱める」という仮説を説明するのに非常に使いやすい比較です。citeturn587904search1

**SAMURAI++: Extending Segment Anything Model 2 to Multi-Object Tracking by Optimizing Hierarchical Trajectory Memory** は **CVPR 2026 Findings** 採録で、training-freeにSAM2をMOT化し、short-term motion-aware memoryとlong-term instance memoryを分けます。tracking-by-detectionのtracklet managementとquery候補を組み合わせ、DanceTrack/MOT17を扱います。citeturn741731search0 これは「object/trajectory単位のstate」に寄せる案として有用ですが、今回見つかったHyperSSMの方が「Kalman→learned state model」という現在の実装との対応は明確です。これは比較上の私の評価です。citeturn760026search0turn741731search0

**Occlusion-Aware SORT** は CVPR 2026 mainで、OAMによるocclusion観測、OAO offset、bias-aware momentumをtraining-freeに追加し、複数trackerへの平均改善を報告しています。SSMではありませんが、「遮蔽を観測したらmotion updateを通常通り行わない」という設計対照として有用です。citeturn741731search1 英論文紹介本命より、関連研究スライドに置く方が収まりがよいです。

## SAM2 memoryの汚染と更新制御

### DAM4SAM

**A Distractor-Aware Memory for Visual Object Tracking with SAM2** は CVPR 2025 main採録です。SAM2.1のパラメータを追加学習せず、memory bankの管理だけを変更するため、現在の「frozen SAM2.1へ後付け」という条件に非常によく合います。citeturn587904search3turn587904search6

memoryを **RAM: Recent Appearance Memory** と **DRM: Distractor Resolving Memory** に分け、recent frameだけでなく「distractorが存在し、かつtrackingが信頼できたanchor」を選択的に保存します。RAMは時間encodingを持ちますが、DRMではむしろtime encodingを入れない設計が良く、memory slotの役割を分離しています。citeturn587904search6

関連アブレーションは特に明快です。DiDiのarchitecture ablationでは、SAM2.1が Q **0.649**、target presenceを見て書き込みを抑えるだけで **0.665**、5-frame間隔updateで **0.667**、full DAM4SAMで **0.694**になります。またDRMへtemporal encodingを入れるvariantは **0.669**まで低下します。したがってこの論文は、「memory量を増やせばよいのではなく、**いつ・なぜ保存したフレームかという機能分離が重要**」というメッセージを出せます。citeturn587904search6

### SENTRY

**SENTRY: SAM2-Enhanced Neighbor-Aware and Temporally Reasoned Memory for Visual Tracking** は ECCV 2026採録で、arXiv **2606.24449**、公式コードも公開されています。ECCV公式サイトにも掲載が確認できます。citeturn513028search5turn513028academia8turn513028search0

この論文の核は非常に単純で、**confidenceの高いmaskをそのままmemoryへwriteするのをやめる**ことです。候補maskを短時間backtrackしてtrackletを作り、近傍objectのtrajectoryとcycle-consistentに照合し、「時間・幾何的に整合するcandidateだけ」をwriteします。学習不要・base architecture untouchedであるため、まさに**refine-before-write**型の汚染防止器です。citeturn513028academia8turn513028search2

著者の公開結果では、SAM2-LのLaSOT success **68.5→70.2**、SAMURAI-L **74.2→75.1**、DAM4SAM-L **75.1→76.3**。DiDi Qでは SAM2-L **0.649→0.660**、SAMURAI-L **0.680→0.693**、DAM4SAM-L **0.694→0.705**で、複数のhost trackerに対して一貫して改善しています。citeturn513028search1

より重要なのは論文のmemory-write diagnosticです。著者はSENTRYにより false memory writeが約**37%減少**、severe false writeが約**半減**すると報告し、最終IoU/Jも改善しています。ここは、あなたが「hidden state contamination」を実験指標として定義する際の非常に良い先例です。なお、SENTRY自身のstateはMamba hidden stateではなくSAM2のmemory entryなので、**直接の同一機構ではなく、"汚染した情報をpersistent stateへcommitしない"という設計原理の転用**として見るべきです。citeturn513028academia8

### SAM2Long と Efficient-SAM2

**SAM2Long** は ICCV 2025で、training-freeなmemory treeにより複数のsegmentation pathwayを保持し、累積scoreで良いpathを残します。単一の誤predictionを即座に一本道memoryへ確定しないことで、長動画のerror accumulationを緩和します。citeturn695695search1 SAM2.1-L上でLVOS v1 **80.2→83.4**、SA-V val **78.6→81.1**などの改善が報告され、SOTでもLaSOT **70.0→73.9**、LaSOText **56.9→60.9**でした。citeturn695695search10

一方でSAM2Longのpath数ablationでは P=1からP=3で性能が上がる一方、4まで増やしても改善し続けるわけではありません。さらにmemory-selectionではIoU単独が最良で、temporal/spatial heuristicsの追加が必ずしも改善しません。したがって「複数仮説をcarryする」は面白いものの、あなたの次の実装案としてはSENTRYやRPMより一段間接的です。citeturn695695search10

**Efficient-SAM2** は ICLR 2026採録で、Sparse Window RoutingとSparse Memory RetrievalによってSAM2の推論を軽量化します。SMRだけならSAM2.1-B+のSA-V test **77.7→77.8**程度と精度をほぼ保ったままmemory retrievalを疎化できます。citeturn316457search0turn316457search8 ただし目的は主に速度・token pruningで、**汚染を防ぐためのupdate gate**ではないため、今回の3本には入れない方が焦点が明確です。

## 研究テーマとの対応と候補順位

現在のper-pixel temporal Mambaが「位置固定」であることを基準に各論文を見ると、最も重要な差はstateの単位です。MambaVLTはMamba layer全体のfinal stateをcarryし、Memory as DynamicsはSAM2内のpredictive latent memoryをcarryし、HyperSSMは**物体trajectory**をstate入力にします。一方SENTRY/DAM4SAMはpersistent state自体を連続hidden vectorにはせず、**mask/frame memoryという明示的なobject-aligned単位**にします。citeturn863911view6turn859512view0turn863911view2turn587904search6turn513028academia8

この比較からは、固定画素 `(x,y)` のhidden stateを `h_t(x,y)=Mamba(x_t(x,y),h_{t-1}(x,y))` とcarryするだけでは、camera/target motion後に同じstateが同じphysical pointを表す保証がない、という問題設定がかなり強くなります。これは論文が直接証明した事実ではなく**今回の論文群から導ける設計上の推論**ですが、Dual-Pathがhistorical sampling offsetsを再利用し、HyperSSMがtrajectory coordinatesを入力し、SENTRYがtracklet geometryをmemory write判定に使うことは、この仮説と整合します。citeturn587904search1turn863911view2turn513028academia8

研究への直結度で並べると、私なら **Memory as Dynamics > SENTRY > HyperSSM > Dual-Path > DAM4SAM > MambaVLT > SAM2Long > SAMURAI++ > Efficient-SAM2 > RGBE Mamba** と評価します。前半3本はそれぞれ「state contamination」「write gate」「spatial/object correspondence＋Kalman replacement」をほぼ一対一で担当できるからです。これは文献の採録順位ではなく、あなたの研究課題への適合度についての評価です。citeturn859512view0turn513028academia8turn760026search0

発表のしやすさという点では、**SENTRYとDAM4SAMが最も説明しやすい**です。誤mask→memory contamination→後続frame driftというfailure modeが視覚的で、対策も「書く前に検証」「distractor用memoryを分離」と一枚絵で説明できます。MambaVLTもstate-space-memoryの図が分かりやすく、Figure 1/3とTable 3で導入からablationまで短時間で説明できます。citeturn587904search6turn513028search2turn863911view6turn520887view1 HyperSSMは数式とhypergraphの説明が増えるため発表準備量はやや大きい一方、Kalman replacementという研究テーマへの接続は最も鮮明です。citeturn760026search8turn167589view0

## 別枠候補

### Workshop・準トップ・期間外に近い論文

**SportMamba: Adaptive Non-Linear Multi-Object Tracking with State Space Models for Team Sports** は **CVPR 2025 Workshop / CVSports** で、Mamba＋self-attentionのmotion predictorを使うためテーマ適合度は高いです。arXiv **2506.03335**。ただしCVPR mainではないため本表からは外しました。citeturn677164search2turn677164academia47 HyperSSMの前段として「Mamba motion prediction」を調べる用途には有用です。citeturn677164search52

**SAMIDARE: Advanced Tracking-by-Segmentation for Dense Scenarios** は **CVPR 2026 Workshop / CVSports**。SAM2MOTにdensity-aware mask regeneration、**selective memory update**、state-aware associationを加え、crowded sportsでtarget feature integrityを保つことを明示しています。今回の「低信頼時に書き込まない」テーマに非常に近いものの、main conferenceではないため別枠が妥当です。citeturn677164search0turn677164academia48

**TrackSSM: A General Motion Predictor by State-Space Model** はarXiv **2409.00487**で、Flow-SSMを使ったgeneral motion predictorです。2024プレプリントなので指定期間外ですが、HyperSSMが比較baselineとして採用している直接の先行研究であり、研究実装上は読む価値があります。citeturn677164academia46turn167589view0 2026年にはScience China Information Sciencesでの掲載も確認できますが、指定トップ会議枠ではありません。citeturn677164search1

**MambaTrack** はarXiv **2408.09178**、**MambaMOT** はarXiv **2403.10826**由来のMamba motion predictor系で、いずれも今回の2025–26トップ会議本表には入れません。HyperSSMのCVPR論文では両者が既存learned-motion baselineとして比較されています。citeturn677164academia49turn863911view2

### 点追跡

**Online Dense Point Tracking with Streaming Memory** は ICCV 2025 mainで、ユーザー指定通りpoint trackingなので別枠ですが、**spatial correspondenceを持つstate**の参考として非常に重要です。短期motionを保持するsensory memoryを持ち、visibility-guided splattingで情報を空間的に伝搬します。citeturn695695search2turn231700search10

あなたの案に翻訳すると、これは「pixelごとのhidden stateを固定座標で次フレームへ渡す」のではなく、**visibilityとmotionに従ってstateを次の位置へtransportする**方向です。その意味で、発表の3本には入れなくても、実装方針を決める際には本表の多くのSOT/MOT論文より直接参考になる可能性があります。これは論文設計からの私の推論です。citeturn231700search10

## 三つの発表構成案

**構成A — 「stateは予測できても、信頼できるとは限らない」**  
`Memory as Dynamics → SENTRY → HyperSSM`。最初にMamba/SSM predictive memoryで**contamination問題そのもの**を定義し、次にSENTRYで「persistent memoryへcommitする前に時間整合性を検証する」という実用的なgateを示し、最後にHyperSSMで「そもそもstateを独立pixel/targetとして扱わず、空間・物体間関係をstate transitionへ入れる」と展開できます。3本が現在の「Mambaを入れただけでは効かなかった→gateとspatial correspondenceが必要では」という研究経緯にほぼ完全に対応します。citeturn859512view0turn513028academia8turn760026search0

**構成B — 「carryするstateをどう設計し、いつ止めるか」**  
`MambaVLT → Memory as Dynamics → Dual-Path Temporal Decoder`。MambaVLTの式 `H_t^ini=aH^l+(1-a)H_{t-1}^fin` を出発点にして、「前stateをcarryする」という最も単純な設計を説明できます。次にMemory as Dynamicsでunconditional predictionの失敗を示し、最後にDual-Pathで低confidence時にはrepresentationを更新しないという具体策を見せられます。Mambaのstate carryを中心に英論文紹介を組みたい場合はこれが最も綺麗です。citeturn863911view6turn859512view0turn587904search1

**構成C — 「SAM2 memoryはどう汚れ、どう守るか」**  
`DAM4SAM → SENTRY → Memory as Dynamics`。DAM4SAMで「どのframeを保存するか」、SENTRYで「保存するmaskをどう検証するか」、Memory as Dynamicsで「memoryを予測stateへ拡張した場合にどうreliabilityをgateするか」と、SAM2 memoryの高度化を一直線に説明できます。frozen SAM2系の後付け設計という共通点も強く、研究室発表としては最も議論しやすい構成です。citeturn587904search3turn513028academia8turn494455view0

## 不確実な点と注意事項

`Memory as Dynamics` はICML 2026公式PMLRで採録・問題設定・コード・SAM2-based実験を確認でき、著者コードからMamba利用とSAM2 backbone freezeも確認できました。一方、PMLRのPDFが今回のweb PDF解析経路では安定して展開できなかったため、**個々のablation Table番号と数値は二次情報で補完せず、意図的に未記載**としました。発表論文として選ぶ場合、この論文だけはPDF本文でTableを最終確認する価値があります。citeturn859512view0turn494455view0

SENTRYについてはECCV公式accepted/video listing、arXiv、著者公式project/codeの三者で採録を確認しています。詳細なbenchmark値は著者公式projectにも掲載されていますが、論文本文とprojectの再評価条件が混ざらないよう、発表では「SENTRYが同一hostへ追加された差」を中心に示すのが安全です。citeturn513028search5turn513028search1

SAMURAI++ は **CVPR 2026 Findings** であり、CVPR main trackと同列には扱わない方が正確です。citeturn741731search0 SportMambaとSAMIDAREもCVPR名を含みますが、いずれも**CVPR Workshops**です。citeturn677164search2turn677164search0

Samba/SambaMOTはユーザー指定通り候補から除外しました。ただしICLR 2025採録で、複数trackletのselective state spacesを同期する設計はHyperSSMとの関連研究として一枚だけ触れる価値があります。citeturn677164search10

最後に、今回の調査で最も重要な研究上の示唆は、**「Mambaのstate carryが効くか」ではなく、「そのstateが今も同じtarget/locationを表していると確認できるか」と「確認できないときにupdateを止められるか」へ問いを変えること**です。これは単一論文の主張ではなく、Memory as Dynamicsのreliability mismatch、SENTRYのrefine-before-write、Dual-Pathのconfidence-guided suppression、HyperSSMのtrajectory/hypergraph stateという独立した設計が同じ方向を指していることから得られる統合的な推論です。citeturn859512view0turn513028academia8turn587904search1turn760026search0

---

## 付録：使用したプロンプト（確定版）

````text
# 調査依頼：英論文紹介（3本）の候補選定 — 物体追跡における時間state・memoryの引き継ぎと汚染対策

## 目的と成果物
研究室の英論文紹介で紹介する論文を3本選びたい。今回は「物体追跡（Tracking）」の論文に絞り、候補表とおすすめの組み合わせを出してほしい。

## 背景
- 私の研究：SAM2/SAMURAIベースの物体追跡で、Kalman filterによる動き予測をMamba（学習ベースの時系列モデル）で置き換える。中心テーマは、hidden stateをフレーム間で引き継ぐ「state carry型」が、オクルージョンや誤対応でstateを汚染される問題（hidden state contamination）。
- 現状：frozen SAM2.1に、位置固定のper-pixel temporal Mambaを足したが、「Mambaあり／なし」「stateのリセットあり／なし」の差が誤差の範囲に収まった。次は、stateに空間対応を持たせる案（flowや軌跡でstateを運ぶ、空間カーネル、内容で読み書きするstate）と、更新をいつ止めるかのgateを検討している。
- 前回の調査で、SSMとstateの空間対応についての主な候補は、動画セグメンテーションや動画超解像の論文だった（TV3S、TS-Mamba、LiVOSなど）。今回はそれを補うため、Trackingの論文に限定する。
- 除外：SambaMOTR（ICLR'25）は前回の論文紹介で発表済みなので、候補から外す（関連研究として触れるのは可）。
- 既知のTracking候補：MambaVLT (CVPR'25)、DAM4SAM (CVPR'25)、SAM2Long (ICCV'25)、SAMURAI++ (CVPR'26 Findings)、Efficient-SAM2 (ICLR'26)。採録はおおむね確認済み。これらと重複しない論文の発見を優先するが、既知の論文も比較表には含めてよい。

## 範囲
- 期間：2025年1月〜2026年11月
- 会議：CVPR, ICCV, ECCV, NeurIPS, ICLR, ICML（Findingsなどの併設トラックは明記）。トップ会議で候補が少ない場合に限り、AAAI・TPAMI・TIP・IJCVを別枠で挙げる。採録が確認できないプレプリントも別枠に。
- タスク：SOT、MOT、VOS（semi-supervised、マスクによる追跡）。点追跡（CoTracker系）は、state・memoryの設計が参考になるものだけ別枠に。
- 手法（優先度順）
  1. Mamba/SSM・線形再帰のstateを追跡に使う研究
  2. 学習ベースの動き予測（Kalman filterの置き換え）
  3. 時間state・memoryの更新制御：遮蔽時や信頼度が低い時に書き込まない、リセット、ゲート、誤りの蓄積を防ぐ仕組み
  4. state・memoryの空間対応：位置合わせ、軌跡、物体単位とpixel単位の比較
- 対象外：医療画像・リモートセンシングなどへの単純な適用、backboneの性能比較だけの論文

## 各論文について抽出してほしいこと
- タイトル、著者、会議・年、採録の根拠URL（CVF Open Access、OpenReview、proceedingsなど）、arXiv ID、コードの有無
- タスクとベンチマーク（DanceTrack、LaSOT、MOSEなど）
- stateやmemoryの単位（box／物体query／pixel・特徴マップ）と、更新式の要点
- 本研究に効くアブレーション：「state・memoryの有無」「更新ゲート・マスクの有無」「動きモデルの種類」の差（表番号付き）
- SAM2・SAMURAIとの関係（frozenか、後付けか）
- 論文紹介向きか：新規性の分かりやすさ、図の多さ、分量の目安

## 出力形式
1. 結論（10行以内）：3本のおすすめの組み合わせを2〜3通り。それぞれで発表の流れが1本につながる理由を書く
2. 候補表（本表）：上記の抽出項目。手法1〜4ごとにまとめる
3. 別枠：準トップ会議・ジャーナル／採録未確認のプレプリント／点追跡
4. 不確実な点・矛盾する証拠

## 引用ルール
- 主張と数値には一次資料（論文本文、公式proceedings）のURLを付け、可能なら表・節・図の番号も付ける。
- 第三者の要約サイトは補助にとどめ、使った場合は明記する。
- 論文の報告値とあなたの推論は区別して書く。
````
