> 生成元：ChatGPT Deep Research（2026-11-04）。英論文紹介（3本）の候補選定のため、Claude Codeとの会話で作成したプロンプト（末尾の付録）で実行した。以下はレポート本文をそのまま保存したもので、内容は書き換えていない。本文中の `citeturn...` はChatGPT内部の引用マーカーで、URLには解決できない。数値や採録状況を使う際は一次資料で再確認すること。

# 英論文紹介候補の深掘り調査：SSM／線形再帰 state を用いた動画追跡と state の空間対応

## 結論

2026年11月4日時点で、指定された主要会議を公式 proceedings／CVF／PMLR／ICLR proceedings を中心に再検索したところ、**既知リストと重複せず、研究テーマに特に近い新規候補は TV3S、RS-SSM、AUSM、MVSSM、MoMa、EVDM の6本**だった。なかでも英論文紹介3本なら、最も研究の次の一手につながる組合せは **TV3S → MVSSM → RS-SSM** だと判断する。TV3Sが「固定位置でstateを持ち回ると何が起こるか」、MVSSMが「motion/flowで空間対応を明示する」、RS-SSMが「SSM内部のforgettingそのものを修正する」という順になり、現在の hidden-state contamination 問題をほぼそのまま研究ストーリーにできる。TV3S は CVPR 2025、RS-SSM は CVPR 2026、MVSSM は CVPR 2026 **Findings** である。 citeturn952439search2turn952439search1turn253239search0

第二候補は **TV3S → Trajectory-aware Shifted SSM → AUSM**。これは「固定pixel state → 軌跡に沿うstate/token → 空間stateそのものを持つstreaming model」という、空間対応の設計空間を比較する発表にしやすい。Trajectory-aware Shifted SSM は ICLR 2026 Poster として採録されており、arXiv:2508.10453 でも公開されている。AUSM は固定サイズの **spatial state** を保持して任意長ストリームを処理する CVPR 2026 Findings 論文である。 citeturn592884search2turn224597academia48turn330562search3

第三候補は、研究室で「SAM2への実装可能性」を強調したい場合の **MoMa → TV3S → AUSM**。MoMa は pretrained image foundation model に Mamba adapter を挿入する parameter-efficient な設計で、既存 backbone を壊さず時空間モジュールを足すという発想が、現在の frozen SAM2.1 + temporal module に最も近い。 citeturn799222view2turn952439academia8

既知候補については、**MambaOut = CVPR 2025、Gated DeltaNet = ICLR 2025、SAM 3 = ICLR 2026、SeC = ICLR 2026、SAMURAI++ = CVPR 2026 Findings** という認識は確認できた。特に SAMURAI++ は main CVPR ではなく Findings と明記すべきである。 citeturn224597search2turn224597search0turn521498search0turn521498search1turn521498search2

## 調査範囲と見取り図

今回の検索では、CVPR/ICCV の CVF Open Access、ICLR proceedings/OpenReview、ICML の PMLR、NeurIPS proceedings を優先し、2025年1月から2026年11月までの採録論文を対象に、`video + state space/Mamba + tracking/segmentation/motion/trajectory/warp/memory` 周辺を再走査した。検索結果上、**「追跡・VOSそのものに再帰SSM stateを用いる」論文はまだそれほど多くなく、動画semantic segmentation、restoration、world model、video recognition に重要な設計アイデアが散在している**。これは、MambaVLT が CVPR 2025 で vision-language tracking に temporal SSM を持ち込み、TV3S が video semantic segmentation で frame-to-frame state sharing を行い、2026年には RS-SSM や AUSM のように state の内容・空間構造そのものへ踏み込む流れになっていることからも読み取れる。 citeturn592884search5turn952439search2turn330562search2turn330562search3

研究テーマとの対応で見ると、三つの方向はかなり明瞭に分かれる。**案(1) flow/trajectory で state を運ぶ**には MVSSM と Trajectory-aware Shifted SSM が最も直接的で、EVDM も motion clue により state-space propagation を制御する近縁例である。**案(2) 空間構造を持つSSM**には TV3S、AUSM、RS-SSM が強く関連する。**案(3) 内容アドレス型state**には既知の LiVOS や Gated DeltaNet 系が依然として理論的に重要で、今回の新規発見群では AUSM が「固定 spatial state に圧縮して再利用する」という最も近い橋渡しになる。Gated DeltaNet は ICLR 2025 採録で、Mamba2のforget gateにDelta rule 型の高速重み更新を組み合わせる線形 attention/state update の代表例である。 citeturn224597search0turn224597academia51

## 本表：主要会議の候補

**テーマ1：動画追跡・VOS・動画segmentationで state を明示的に持ち回るもの**

| 論文 | 採録・資料 | state / 更新と空間対応 | 効くアブレーション | frozen / 研究との関係 | 紹介適性 |
|---|---|---|---|---|---|
| **Exploiting Temporal State Space Sharing for Video Semantic Segmentation (TV3S)** — Syed Ariff Syed Hesham et al. | CVPR 2025, pp.24211–24221。arXiv:**2503.20824**。公式 code は `Ashesham/TV3S`。 citeturn952439search2turn952439academia7 | 空間patchごとに時間方向のSSM stateを共有する設計。各patchを独立処理しつつ、**shifted representation** で隣接空間との情報交換を入れる。明示flowは使わず、位置固定state + shiftという意味で、現在の per-pixel temporal Mamba に非常に近い。 citeturn952439search2turn448093view3 | **Table 3** が特に重要。Direct 出力で `1 TSS(No Shift)=38.0`, `TV3S(No Shift)=38.9`, `TV3S(Shift)=39.5 mIoU`。つまり、再帰層の積み重ねだけで +0.9、**空間shiftを加えるとさらに +0.6**。Table 6では temporal contextを1→32 frameに増やすと mIoU 37.9→39.7、mVC16 79.1→87.8。 citeturn448093view0turn448093view3turn818798view0 | SAM backboneではない。研究上は **案(2)** に最も近い。「同じpixel indexにstateを置きっぱなし」から少しだけ空間mixingしたときに性能が上がることが、現在の結果へのかなり直接的な示唆。 | **最有力。** 図と表が分かりやすく、発表では「あなたの現方式に最も近い既存研究」として導入しやすい。11ページ。 |
| **RS-SSM: Refining Forgotten Specifics in State Space Model for Video Semantic Segmentation** — Kai Zhu et al. | CVPR 2026 main, pp.10741–10752。arXiv:**2603.24295**。公式 code 公開。 citeturn952439search1turn952439academia6 | SSMの固定サイズstateが共通semanticを残す一方、pixel-level specifics を忘れることを問題設定にし、Channel-wise Amplitude Perceptron と **Forgetting Gate Information Refiner (FGIR)** で forget gate を反転・補正する。 citeturn952439search1turn952439academia6 | 論文の主眼自体が「forgettingの修正」で、state contaminationというより **必要なspecific情報がstate compressionで落ちる問題**を扱う。これは contamination の逆側、すなわち「何を忘れるべき／残すべきか」の設計問題として強く関連する。 citeturn592884search0 | SAM系ではない。**案(2) + gate/reset設計**。現在検討している「state reset/gateを学習させる」方向の理論的対照として非常に良い。 | **最有力。** 問題設定の一文が非常に強く、hidden-state contaminationとの対比を作りやすい。12ページ。 |
| **Autoregressive Universal Video Segmentation Model (AUSM)** — Miran Heo et al. | **CVPR 2026 Findings**, pp.7429–7438。arXiv:**2508.19242**。 citeturn952439search0turn952439academia5 | streaming segmentationをautoregressive mask predictionとして定式化し、**fixed-size spatial state** を維持する。明示的FIFO memoryなしで長時間文脈をstate compressorに保持する。 citeturn330562search3turn448093view2 | 主論文の ablation は state/reset そのものより long-context と training方式。16-frameでは iterative training 8.75 sec/iter に対し parallel 3.45 sec/iter、約2.5×高速。長いclipで学習すると長動画への一般化が改善すると報告。 citeturn448093view2 | SAM2のmemory bufferを「固定サイズ spatial recurrent state」に置き換える発想として非常に近い。**案(2) と案(3)の中間**。 | **強い候補。** mask autoregressionという説明軸が明快。ただし Findings であることは明記。 |
| **MambaVLT** — Xinqi Liu et al. | CVPR 2025。既知候補。 citeturn592884search5 | multimodal temporal information を Mamba state evolution で保持し、reference featuresを動的更新。 citeturn592884search5 | temporal/reference更新の有効性を見る比較が中心。 | trackingへの直接性は最高だが、既に把握済み。 | 新規発見ではないので3本選定では優先度を下げる。 |

TV3S は、今回の探索で最も「現在の失敗結果を説明する」論文である。論文は patchを独立に時間処理するだけではなく、**spatial shift を入れたときに No-Shift より明確に良くなる**と報告している。表3の Direct 設定では 38.9→39.5 mIoU であり、差は巨大ではないものの、「時間stateだけでは不十分で、空間的にstate/featureをずらす必要がある」という方向性は研究仮説と一致する。さらに時間文脈を1 frameから16–32 frameへ伸ばすと mIoU の改善は早く飽和する一方、temporal consistency 指標 mVC は伸び続ける。この結果は、「state carryを長くしても平均精度はほぼ変わらない」という現在の観測と両立し得る。これは**私の解釈**であってTV3S論文自身の主張ではない。 citeturn448093view3

**テーマ2：flow・軌跡・motionでSSMの空間対応を作るもの**

| 論文 | 採録・資料 | state / 空間対応 | 重要アブレーション | 本研究への意味 | 紹介適性 |
|---|---|---|---|---|---|
| **MVSSM: Motion-aware Visual State Space Model for Efficient Video Deblurring** — Chen Zhou et al. | **CVPR 2026 Findings**, pp.4855–4865。公式 code は `Frank-Zhou-01/MVSSM`。公式CVFから採録確認。 citeturn253239search0turn224597search4 | optical flowで隣接frame featureを **warp** した後、平均flow angleから水平・垂直・斜め・反斜めのscan方向を選ぶ。つまり「stateそのものをflow warp」ではないが、**flowで空間対応を作り、そのmotion trajectoryに沿ってSSM scanを選択**する。 citeturn181488view1 | **Table 4:** Motion-aware Scanning Blockを外すと PSNRが **2.16 dB**、SSIMが0.0163低下。**Table 9:** FlowNet/SpyNet/PWC-Net/RAFTで PSNR 34.59/34.66/34.71/34.81、flow精度が性能に反映される。 citeturn181488view0turn181488view2 | **案(1)の最重要候補。** 「誤flowがstateを汚染する」というまさに次の問題まで見える。対応を導入すれば終わりではなく、correspondenceの信頼度でgate/resetする必要があることを示唆する。後半は私の推論。 | **極めて紹介向き。** motion矢印とscan pathの図で新規性を説明しやすい。 |
| **Trajectory-aware Shifted State Space Models for Online Video Super-Resolution** — Qiang Zhu et al. | **ICLR 2026 Poster**。arXiv:**2508.10453**。 citeturn592884search2turn224597academia48turn224597search56 | 過去frameから現在tokenに似たtokenを選び、**trajectoryを構成してその軌跡に沿ってtemporal aggregation**。さらに Hilbert scan + shift を用いた shifted SSM blockを採用する。 citeturn592884search9turn224597academia48 | 著者は trajectory supervision を明示的に入れ、trajectory生成の精度を学習する。論文abstractでは既存online VSRに対し多くの設定でSOTA、MACsを22.7%以上削減と報告。 citeturn592884search9 | **案(1)に最も直球。** 「固定pixelでMamba」から「軌跡を作ってtokenをgatherしてMamba」に変えるという構造は、そのまま実装案になり得る。 | **最有力。** タスクがVSRなので追跡との差を説明する必要はあるが、新規性は非常に分かりやすい。 |
| **EVDM: Event-based Real-world Video Deblurring with Mamba** — Zhijing Sun et al. | ICCV 2025, pp.13793–13803。公式 code `ZhijingS/EVDM`。CVFで採録確認。 citeturn972903search0turn972903search6 | Motion Clue Extraction Mamba、Motion-aware Intra-frame Fusion Mamba、Inter-frame Temporal Propagation Mambaを組み合わせ、event由来のmotion clueでstate-space fusion/propagationを制御する。 citeturn972903search0turn972903search7 | Figure 1では attention置換とのGPU memory比較を行い、Mamba版がより長い時間窓・大きな空間解像度まで処理できることを示す。 citeturn972903search6 | flowではないが、**motion cueでstateを書き換える**設計例。案(1)の補助候補。event camera依存なので主3本よりは遠い。 | 図は良いがevent modalityの説明に時間を使う。 |
| **Long-Context State-Space Video World Models** — Ryan Po et al. | ICCV 2025。既知候補。 citeturn330562search22 | block-wise SSM scanningとlocal attentionで、causal world modelの長期stateを維持。 citeturn774816search9 | spatial retrieval/reasoningを通じて長期記憶を評価。 | state carryの「長いほど良いとは限らない」という比較対象。 | 既知のため補助。 |

MVSSM は特に重要である。ただし名称から誤解しやすい点として、**pixelごとのhidden stateをoptical flowで直接warpしているわけではない**。式(1)で隣接frame featureを flow warp して局所的に融合し、その後、flowから得たglobal motion angleに応じてSSMのscan directionを選択する。したがって「state warp」の完全な先行例というより、**correspondence-aware SSM scan** の先行例として扱うのが正確である。 citeturn181488view1

一方、Trajectory-aware Shifted SSM はより直接的に「過去frameからtrajectoryに沿ってtokenを選んで集約する」ので、現在考えている「flowや点軌跡でstateを運ぶ」に近い。その意味で、発表の研究接続性だけを優先するなら、MVSSMよりこちらを上位に置いてもよい。 citeturn224597academia48

**テーマ3：frozen / pretrained backboneへMamba系moduleを後付けするもの**

| 論文 | 採録 | 設計 | frozen性 | 本研究との関係 |
|---|---|---|---|---|
| **MoMa: Modulating Mamba for Adapting Image Foundation Models to Video Recognition** — Yuhuan Yang et al. | ICML 2025, PMLR 267:70914–70926。arXiv:**2506.23283**。 citeturn799222view2turn952439academia8 | pretrained image foundation modelに selective SSM を組み込む **SeqMod** と Divide-and-Modulate adapter を挿入し、spatial-temporal情報を元featureを壊さず注入する。 citeturn799222view2 | 論文は parameter-efficient adaptation を主眼とし、full modelをvideo用にゼロから学習する方式ではない。PMLR本文は IFM のpretrained featureを保持しつつadapter側で時空間modulationする設計として説明している。 citeturn799222view2 | 現在の **frozen SAM2.1 + temporal Mamba** に最も構成が近い主要会議論文。タスクはrecognitionなので、追跡state contaminationの直接検証はない。 |
| **AUSM** | CVPR 2026 Findings。 citeturn330562search3 | SAM2型の外部memory bufferとは異なる固定spatial state。 | frozen SAM adapterではない。 | SAM2 memory置換の概念的な候補。 |

MoMa は「空間対応」の論文ではないため3本の主役にする必要はないが、**実装方針を正当化する引用**として非常に価値が高い。つまり「foundation modelを全面fine-tuneせず、video-specific temporal state moduleだけを追加する」研究設計がICML 2025でも成立しているという根拠になる。 citeturn799222view2

**テーマ4：SSMが視覚で本当に必要か、stateの価値を問い直すもの**

MambaOut は既知候補だが、今回の研究ストーリーには依然として非常に重要である。CVPR 2025採録で、著者らはImageNet画像分類ではMambaを除いたGated CNN型モデルがVisual Mamba群を上回ることから、**sequenceの性質を持たない画像タスクでMambaを使う必然性を疑問視している**。arXivは **2405.07992**。 citeturn224597search2turn224597academia55

これは現在の「per-pixel temporal Mambaを足したが差がほぼ出ない」という結果と非常に相性がよい。ただし MambaOut の結論をそのまま動画trackingへ拡張するのは不適切である。むしろ、「Mambaが効くためには**有意味なsequence orderingが必要**であり、pixel indexを固定した時間列が本当に同一物体点のtrajectoryなのか」という問いに置き換えると、MambaOut → trajectory-aware SSM という自然な発表ストーリーになる。後半は今回の文献群を踏まえた**推論**である。 citeturn224597search2turn224597academia48

## 技術的に最も効く比較と研究への示唆

今回見つけた中で、現在の実験結果を最も直接的に解釈できるのは TV3S の Table 3 と Table 6 である。TV3Sでは、時間情報を扱うだけでも効果はあるが、**shiftで空間的な隣接関係を混ぜることでさらに改善**する。また1 frame→32 frameまでstateに時間情報を増やしても、mIoUは 37.9→39.7 で16 frame付近からほぼ飽和するのに対し、mVC16は79.1→87.8まで増える。つまり、長期stateが「平均segmentation精度」に大きな差を作らなくても「時間的一貫性」には効いている可能性がある。 citeturn448093view3

この結果から現在の実験へ推論すると、まず Mamba on/off の平均metricだけではなく、**occlusion区間、再出現直後、急運動、ID誤対応後**に限定してerror curveを分ける価値が高い。Mambaが全frame平均では無差でも、state carryの利点とstate contaminationの損失が相殺されている可能性がある。この相殺仮説は文献で直接検証されたものではないが、TV3Sの長期context飽和と、RS-SSMが固定stateによるspecific-information forgettingを問題視していることから十分に検証価値がある。 citeturn448093view3turn952439academia6

空間対応を入れる場合は、MVSSMがもう一つ重要な警告を出している。より高性能なflow estimatorほど性能が上がり、SpyNet 34.66 dBに対しRAFT 34.81 dBだった。つまり correspondence を入れると、今度は **correspondence error がstate update errorへ直結する**。したがって「flow warp + state carry」だけでなく、flow confidence・forward/backward consistency・SAM mask confidenceなどを用いて `update / keep / reset` を切り替える設計が自然である。前半の数値は論文報告、後半は本研究への**設計上の推論**である。 citeturn181488view2

RS-SSM はさらに別の軸を与える。ここではstateの問題を「誤情報が入る」ではなく「固定容量のstate圧縮でpixel-specific情報を忘れる」と捉え、forget gateを修正する。したがって hidden-state contamination を、単純な「resetすべきか否か」ではなく、**erase と write を分離して制御すべき問題**と考える余地がある。これは Gated DeltaNet の「forgetting + delta-rule memory update」とも理論的につながる。Gated DeltaNet は ICLR 2025で採録され、arXiv:2412.06464、公式実装も公開されている。 citeturn952439academia6turn224597search0turn224597academia51turn224597search3

この観点から、次の実験は「state resetあり/なし」だけでなく、`h_t = g_t ⊙ update(x_t,h_{t-1}) + (1-g_t)⊙h_{t-1}` のような **confidence-conditioned selective update** を比較する方が文献上の位置づけが強い。さらに空間対応後のgatingなら、`g_t(x,y)` をflow consistencyやSAM confidenceから作れる。これは文献そのものの式ではなく、TV3S・MVSSM・RS-SSM・Gated DeltaNetを組み合わせた**研究提案**である。 citeturn448093view3turn181488view1turn952439academia6turn224597academia51

## 別枠：準トップ・ジャーナル・補助候補

**MambaLCT: Boosting Tracking via Long-term Context State Space Model** は AAAI 2025 採録で、指定の主要6会議外なので別枠に置くべきだが、内容はかなり近い。unidirectional Context Mambaで最初のframeから現在までのtarget variation cueをstateに累積し、tracking attentionへ注入する。AAAI proceedings上で正式採録が確認でき、pp.4986–4994。 citeturn774816search2turn774816search3

**Video Mamba Suite** は IJCV 2025のジャーナル論文で、tracking/VOS特化ではないものの、14種のSSMベースモデルを12のvideo understanding taskで比較し、Mambaを temporal modeling、cross-modal interaction、temporal adapter、spatiotemporal modeling の4役に整理している。研究室発表で「Mambaを動画にどう使うか」のsurvey的背景を1枚にまとめる用途にはよい。 citeturn774816search5

EVDMは ICCV 2025なので本来本表側だが、event cameraという特殊sensorを必要とするため、研究との距離を考えて発表候補としては補助扱いが妥当である。論文そのものは正式ICCV採録であり、プレプリント扱いではない。 citeturn972903search0

ユーザーが挙げた **SUMO、LiAM-SAM、Rethinking Memory Design in SAM-Based VOT** については、この調査で主要6会議の公式 proceedings に採録されたことを確認できる一次資料を得られなかったため、現時点では「採録未確認プレプリント」という扱いを維持するのが安全である。逆に **SMTrack = TIP** という整理は、主要会議本表ではなくジャーナル別枠に置く方針で整合する。

## 採録状況の修正点と不確実性

確認済みリストの大部分は正しい。**MambaOut は CVPR 2025**、**Gated Delta Networks: Improving Mamba2 with Delta Rule は ICLR 2025**、**SAM 3 は ICLR 2026**、**SeC は ICLR 2026**、**Trajectory-aware Shifted State Space Models for Online VSR は ICLR 2026 Poster**、**Extending Segment Anything Model 2 to Multi-Object Tracking by Optimizing Hierarchical Trajectory Memory / SAMURAI++ は CVPR 2026 Findings** である。 citeturn224597search2turn224597search0turn521498search0turn521498search1turn592884search2turn521498search2

注意すべき第一点は **CVPR Findings と main conference を区別すること**。今回の新規候補では AUSM と MVSSM が Findings、RS-SSM は main CVPR 2026である。SAMURAI++も Findings である。 citeturn330562search3turn224597search4turn330562search2turn521498search2

第二点は、Trajectory-aware Shifted SSM の検索結果に古い「Under review as a conference paper at ICLR 2026」PDFも残っていること。ただし現在の OpenReview検索結果は **ICLR 2026 Poster** と明示しており、ICLR camera-ready PDFも存在するため、採録済みとして扱ってよい。arXiv番号は2508.10453である。 citeturn592884search9turn592884search2turn224597search56turn224597academia48

第三点は **MVSSM**。これは非常に関連性が高いが、CVPR mainではなく **CVPR 2026 Findings** である。また一次資料で確認できた時点では明確なarXiv IDを特定できなかったため、arXiv欄は「未確認」とするのが適切である。一方、CVF proceedingsと公式コードへの導線は確認できている。 citeturn253239search0turn253239search3

最終的に、**英論文紹介としての第一推奨は TV3S・Trajectory-aware Shifted SSM・RS-SSM** としたい。TV3Sで「固定座標のtemporal state」、Trajectory-awareで「trajectoryによる空間対応」、RS-SSMで「state内部のforget/write制御」と進めれば、発表の最後をそのまま「次に自分は correspondence-aware + confidence-gated state carry を試す」という研究仮説へ接続できる。MVSSMをTrajectory-awareと入れ替えれば、flowによるwarpと誤対応問題をより強く押し出せる。この最終的な研究接続は論文の主張ではなく、今回の文献比較からの**推論**である。 citeturn952439search2turn224597academia48turn952439academia6turn181488view1

---

## 付録：使用したプロンプト（確定版）

````text
# 調査依頼：英論文紹介（3本）の候補選定 — SSM/線形再帰stateを用いた動画追跡と、stateの空間対応

## 目的と成果物
研究室の英論文紹介で紹介する論文を3本選びたい。その判断材料として、条件に合う論文を網羅的に洗い出し、候補表とおすすめの組み合わせを出してほしい。

## 背景（調査済み・確定していること）
- 私の研究：SAM2/SAMURAIベースの物体追跡で、Kalman filterによる動き予測をMamba（学習ベースの時系列モデル）で置き換える。中心テーマは、hidden stateをフレーム間で引き継ぐ「state carry型」が、オクルージョンや誤対応でstateを汚染される問題（hidden state contamination）。
- 現状：frozen SAM2.1に、位置固定のper-pixel temporal Mambaを足した。しかし「Mambaあり／なし」「stateのリセットあり／なし」の差が誤差の範囲に収まった。次は、stateに空間対応を持たせる3案を検討している：(1) flowや点軌跡でstateを運ぶ、(2) 空間カーネルを持つSSM、(3) 内容で読み書きするstate（LiVOS型）。
- 候補として確認済みの論文（採録も確認済み）：MambaOut (CVPR'25)、SambaMOTR (ICLR'25)、Gated DeltaNet (ICLR'25)、Long-Context State-Space Video World Models (ICCV'25)、MambaVLT (CVPR'25)、LiVOS (CVPR'25)、Tracktention (CVPR'25)、DAM4SAM (CVPR'25)、SAM2Long (ICCV'25)、EdgeTAM (CVPR'25)、SAMWISE (CVPR'25)、SAM 3 (ICLR'26)、SeC (ICLR'26)、Trajectory-aware Shifted SSM for Online VSR (ICLR'26)、Extending SAM2 to MOT / SAMURAI++ (CVPR'26 Findings)。
- 採録未確認のプレプリント：SUMO、LiAM-SAM、Rethinking Memory Design in SAM-Based VOT。SMTrackはTIP採録（ジャーナル）。
→ これらと重複しない論文の発見を優先する。上記の論文は、採録状況や位置づけに誤りがあれば指摘してほしい。

## 範囲
- 期間：2025年1月〜2026年11月に採録・発表された論文
- 会議：CVPR, ICCV, ECCV, NeurIPS, ICLR, ICML（AAAIなどの準トップ会議やジャーナルは「参考」として別枠に）。CVPR Findingsなどの併設トラックは明記する。
- 採録が確認できないarXivプレプリントは、本表に入れず別枠に置く。
- 対象テーマ（優先度順）
  1. Mamba/SSM・線形再帰（gated linear attention、DeltaNet系、xLSTM系を含む）のstateを、動画追跡（SOT/MOT）・VOS・動画セグメンテーションに使う研究
  2. 再帰stateや時間特徴の空間対応：flowや点軌跡によるstateのwarp・gather、軌跡に沿った時間モデル、変形可能な走査など。タスクは問わない（動画超解像・深度・生成なども可）
  3. SAM2/SAM3系のmemoryを改良・置換・圧縮する研究。特に、frozen backboneにモジュールを後付けするもの
  4. 視覚でSSMが本当に必要かを分析・批判する研究（MambaOut系）
- 対象外：画像のみのMamba backboneの性能比較、医療画像やリモートセンシングなどへの単純な適用

## 各論文について抽出してほしいこと
- タイトル、著者、会議・年、採録の根拠URL（CVF Open Access、OpenReview、proceedingsなど）、arXiv ID、コードの有無
- stateの形（ベクトル／行列／空間マップ）、更新式の要点、空間対応の取り方（なし／flow／軌跡／attention／内容アドレス）
- 本研究に効くアブレーション：「state・再帰の有無」「対応付けの有無」「リセット・ゲートの有無」とその差（表番号付き）
- backboneを固定してモジュールだけ学習しているか
- 本研究との関係：上の3案のどれに当たるか、hidden state contaminationへの示唆
- 論文紹介向きか：新規性の分かりやすさ、図の多さ、分量の目安

## 出力形式
1. 結論（10行以内）：3本のおすすめの組み合わせを2〜3通り。それぞれで発表の流れが1本につながる理由を書く
2. 候補表（本表）：上記の抽出項目。テーマ1〜4ごとにまとめる
3. 別枠：採録未確認のプレプリント／準トップ会議・ジャーナル
4. 不確実な点・矛盾する証拠：採録が未確認の論文、数値が版によって違う論文など

## 引用ルール
- 主張と数値には一次資料（論文本文、公式proceedings）のURLを付け、可能なら表・節・図の番号も付ける。
- 第三者の要約サイトは補助にとどめ、使った場合は明記する。
- 論文の報告値とあなたの推論は区別して書く。
````
