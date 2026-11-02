> 生成元：Claude のリサーチ機能（2026-11-02）。プロンプトは [11/2 brainstorm](../../../../secretary/notes/brainstorm/2026-11-02-cvpr-timeline-vs-architecture.md) の「追記 13:45」の確定版。以下はレポート本文をそのまま保存したもので、内容は書き換えていない。

# 位置固定stateを捨て、対応を運ぶstateへ：frozen SAM2.1 + Mamba の空間対応サーベイ

先に結論を書く。今の「位置固定・空間混合なしの per-pixel Mamba」が効かない理由は、作業仮説（位置ずれ）と反対仮説 (a)（SAM2 memory との冗長）の両方で説明できる。一次資料がより強く支持するのは (a) である。SAM2 の著者自身が memory に GRU を足す設計を試し、「改善しない」と報告している（[SAM 2, §A.2.3 / Table 11](https://arxiv.org/pdf/2408.00714)）。ただし、その前に潰すべき自明な原因が2つある。1つは「ゼロ初期化射影 × α」で α も 0 から始めると勾配が恒等的に 0 になる点、もう1つは ssm_state だけのリセットでは 4 フレーム分の conv 窓が残る点である。推薦する1週間の計画は、診断（D0〜D2）を先に行い、続いて「flow で state を運ぶ warp-then-step（まず flow oracle 版）」を「位置合わせなし（d≡0）」と同じコードパスで比較することである。修論は、「state carry が SAM2 memory を置き換える・圧縮する」という問いに立てると、state carry の価値を最も示しやすい。

---

## 1. 要約（10行以内）

1. 強い attention memory の上に足した recurrent state の寄与は、一貫して小さい。XMem sensory memory は除去で −1.1〜−1.9 J&F、Cutie の object memory は MOSE で −0.4、SAM2 の GRU memory は改善なし（MOSE dev では 73.1→72.3）。大きく効くのは base が時間対応を持たない場合で、Tokmakov で −6.0 mIoU、BasicVSR で −1.19 dB、DVIS で +5.5 AP。
2. したがって、今回の null result は (a) 冗長の予測と整合する。位置ずれ仮説とは排他でなく、「位置に依らない照合で動きを吸収する memory attention」と「それができない位置固定 state」という同じ現象の表裏である可能性が高い。
3. 診断を最優先にする。α の初期値が 0 なら、全勾配が恒等的に 0 になる（解析的帰結）。ssm_state だけのリセットでは conv 窓（4 フレーム）と D·x スキップが残るので、「リセットしても不変」の解釈が変わる。
4. 1週間で試す案のベスト3は次のとおり。① flow で state を運ぶ warp-then-step（軌跡 gather により既存 scan カーネルのまま実装可能）。② ConvS5 型の空間 read/write カーネル（最安の対照）。③ LiVOS 型の key-addressed 行列 state（位置不変で、state carry を保つ）。
5. 次に実装する1案は ①（flow oracle 版）とする。d≡0 で現行モデルと完全一致するため、「位置合わせなし」と純粋に比較でき、学習 offset の崩壊リスク（BasicVSR++ Table 4）も避けられる。
6. ① の flow 事前計算は、MOSE train 約 9.1 万フレーム（推定）・双方向 18 万ペアで、SEA-RAFT なら約 1〜2 GPU 時間、stride 16・fp16 保存で約 3 GB と見積もる（推定）。
7. ① は SAM2 memory を通常どおり使う条件では利得 ≲1 pt と見込むべきである。memory を絞った条件（D2）と必ず組で評価する。
8. 修論では、stateless な memory 選択（SAMURAI、SAM2Long、DAM4SAM）が SAM2 改善の最強手段であるという事実を踏まえる。そのうえで、state carry の存在意義を「定数メモリでの memory 置換」と「動き・同一性の長期保持」に置くべきである。
9. SAM 3.1 の複数物体機構の正式名は「Object Multiplex」（2026-03-27 公開）である。最大 16 物体を bucket にまとめ、共有パスで処理する。時間モデリングではなく効率化の機構である。
10. SAM2 の memory attention を SSM で置き換えた一次研究も、frozen SAM2 に SSM 時間モジュールを入れた一次研究も、今回の探索範囲では見つからなかった（網羅的な探索ではない）。

---

## 2. 手法の分類表

### 2.1 分類表

凡例：「固定」はバックボーンを固定したまま当該モジュールだけ学習した報告があるかを示す。「E2E」は end-to-end 学習（または backbone の微調整込み）の報告しかないことを示す。アブレーションの差はすべて論文の報告値で、括弧内に根拠の表・節を示す。コード欄の [未] は、URL を本調査で一次確認できなかったことを示す。

| カテゴリ | 代表論文 | 対応の取り方 | 解像度・挿入位置 | 固定バックボーン | コード | 「位置合わせなし」とのアブレーション |
|---|---|---|---|---|---|---|
| 1. flow で特徴／state をワープ | [GRFP/STGRU](https://ar5iv.labs.arxiv.org/html/1612.08871) | 外部 flow（FullFlow/DIS）で **hidden state** を bilinear warp し、光度誤差で reset gate を駆動 | 出力 semantic 解像度、ConvGRU | E2E（static 網も極小 lr で更新） | D-Nilsson/GRFP [未] | Cityscapes val +0.7（Dilation10）/+1.1（LRR）mIoU（Table 1）。flow・GRU 単独除去の行はない |
| 1 | [NetWarp](https://ar5iv.labs.arxiv.org/html/1708.03088) | 中間特徴を flow+FlowCNN でワープし、per-channel 重みで融合（w2=0 初期化） | 任意層（stride に合わせ flow を縮小） | E2E | raghudeep/netwarp_public [未] | CamVid 68.9→70.2。**単純 concat は +0.1、warp は +1.3**（Table 1/3） |
| 1 | [FGFA](https://ar5iv.labs.arxiv.org/html/1703.10025) | 近傍フレーム特徴を flow で warp し、適応重みで平均 | stride 16（flow を 1/2 に縮小） | E2E | msracver/Flow-Guided-Feature-Aggregation [未] | flow なし単純集約は単フレーム比 −1.0 mAP（Table 1） |
| 1 | [BasicVSR](https://ar5iv.labs.arxiv.org/html/2012.02181) / [BasicVSR++](https://arxiv.org/pdf/2104.13371) | SPyNet flow で **再帰 hidden feature** を warp（++ は flow を base offset とする DCN） | LR 特徴、双方向再帰 | E2E（SPyNet も微調整） | open-mmlab/mmagic [未] | alignment 除去で −1.19 dB（本文）。**flow なし DCN は 27.44 dB に崩壊、flow-guided は 32.39 dB**（++ Table 4） |
| 1 | [Tokmakov ConvGRU memory](https://ar5iv.arxiv.org/html/1704.05737) | ワープなし。7×7 ConvGRU の受容野が暗黙に対応を担う | w/8×h/8×64 | **固定**（2-stream を固定し、ConvGRU のみ学習） | なし/不明 | DAVIS memory 除去で −6.0 mIoU、単方向 −2.9（Table 1） |
| 2. 画像 flow／点追跡を latent へ写像 | [FGFA](https://ar5iv.labs.arxiv.org/html/1703.10025), [RAFT](https://ar5iv.arxiv.org/html/2003.12039) | flow を feature 解像度へ縮小し、変位を stride で割る。RAFT は 1/8 内部 flow と convex upsampling | stride 4→16 / 1/8 | — | princeton-vl/SEA-RAFT [未] | 写像そのものの ablation はない |
| 2 | [Softmax splatting](https://arxiv.org/abs/2003.05534) | forward warp の衝突を softmax 重みで解決 | 特徴ピラミッド | — | sniklaus/softmax-splatting [未] | abstract のみ確認 |
| 2 | [SAM-PT](https://arxiv.org/html/2307.01197v1) | 点追跡（PIPS）の軌跡を **SAM の prompt** に使う（latent はワープしない） | 点・全解像度 | 固定（SAM と PIPS は学習なし） | [SysCV/sam-pt](https://github.com/SysCV/sam-pt) | MOSE 38.5（reinit 41.0）。追跡器比較では PIPS 72.3 vs RAFT 63.0（DAVIS17） |
| 2 | [RMNet](https://arxiv.org/pdf/2103.12934) | flow で前マスクを warp して照合領域を限定 | stride 16 相当の照合 | E2E | project page | local-to-local 0.835 vs global 0.818（Table 5）。**flow 精度はほぼ無関係**（Table 7） |
| 3. 潜在空間で対応を推定 | [AOT](https://arxiv.org/pdf/2106.02638) | 前フレームへの λ×λ 局所 attention（short-term） | stride 16 | E2E | yoxu515/aot-benchmark [未] | **λ=0 で −6.0 J&F**（YTVOS18、Table 3）。λ=7 で 78.3、λ=15 で 80.3 |
| 3 | [Understanding DA](https://ar5iv.arxiv.org/html/2009.07265), [TDAN](https://ar5iv.labs.arxiv.org/html/1812.02898) | DCN offset（DCN は「n² 回の warp + 1×1 conv」と等価） | LR 特徴 | E2E | mmagic [未] | offset overflow で整列特徴がゼロ化する。fidelity loss で +1.7 dB |
| 3 | [STSN](https://ar5iv.labs.arxiv.org/html/1803.05549), [MaskProp](https://ar5iv.arxiv.org/html/1912.04573) | 特徴差／concat から offset を予測し、deformable sampling（flow 教師なし） | FPN 第 2 レベル等 | E2E（MaskProp は 64 GPU） | 未公開と記憶 [未] | MaskProp：deformable 46.6 vs FlowNet2 伝播 31.4 mAP（YT-VIS、Table 3） |
| 3 | [TrajGRU](https://arxiv.org/pdf/1706.03458) | [X_t, H_{t−1}] から L 本の flow を予測し、**state を warp** してから更新 | 再帰セル内 | E2E | 公式 MXNet [未] | 同パラメータで ConvGRU 1.310 → TrajGRU 1.138 MSE（Table 1） |
| 3 | [Motionformer](https://arxiv.org/pdf/2106.05392) | 各フレームで空間 softmax により対応点を求め、軌跡上で時間方向に集約 | ViT トークン | E2E | [facebookresearch/Motionformer](https://github.com/facebookresearch/Motionformer) | SSv2 64.0/64.2 → 66.5、FLOPs は約 2 倍（Table 4） |
| 3 | [HMMN](https://ar5iv.labs.arxiv.org/html/2109.11404) | 局所窓 s=7 の追跡から Gaussian kernel を作り、memory 照合の事前分布にする | res4 | E2E | Hongje/HMMN | 有無の数値は未取得 |
| 4. 物体／トークン単位の state | [Cutie](https://ar5iv.labs.arxiv.org/html/2310.12982) | mask pooling による object memory + 双方向 masked cross-attention | object query（N=16） | E2E | [hkchengrex/Cutie](https://github.com/hkchengrex/Cutie) | object memory 除去 **−0.4**（MOSE、Table 5）。masked attn 除去 −3.5（Table 6）。L=0 で −2.2（Table 3） |
| 4 | [SAM2 object pointer](https://arxiv.org/pdf/2408.00714) | mask token を memory に積み、cross-attention で読む（RoPE なし） | 256-d → 64-d×4 | — | facebookresearch/sam2 | **MOSE dev ±0**、SA-V +3.8、LVOSv2 +4.6（Table 11） |
| 4 | [DVIS](https://arxiv.org/pdf/2306.03413) | query 単位の referring cross-attention（identity を残差で保持） | object query | **固定**（MinVIS segmenter を凍結） | [zhang-tao-whu/DVIS](https://github.com/zhang-tao-whu/DVIS) | OVIS +5.5 AP（tracker）、+8.3（+refiner）（Table 5）。標準 CA 2.9 vs RCA 30.5（Table 7） |
| 4 | [MeMOTR](https://arxiv.org/html/2307.15700v3) | track ごとの EMA 長期メモリ（λ=0.01） | track embedding | E2E | [MCG-NJU/MeMOTR](https://github.com/MCG-NJU/MeMOTR) | AssA +4.3（memory+attn、本文/Table 6） |
| 4 | [CamSAM2](https://arxiv.org/html/2503.19730v3) | 予測マスク内の prototype（k-means）を cross-attention で読む | stride 16 + 高解像 | **固定**（SAM2 全凍結、+0.5M） | zhoustan/CamSAM2（"will be available"） | OPG で +8.4 mDice（MoCA-Mask、Table 5） |
| 5. 動画向け SSM | [ConvS5](https://arxiv.org/pdf/2310.19694) | 状態遷移は pointwise・対角のまま、**B/C を 3×3 空間カーネル**にする | H×W×P の state | E2E | [NVlabs/ConvSSM](https://github.com/NVlabs/ConvSSM) | B/C 1×1 → 3×3 で FVD 81→67（DMLab、Table 5） |
| 5 | [VideoMamba](https://www.ecva.net/papers/eccv_2024/papers_ECCV/papers/03773.pdf) | 時空間 flatten の走査順 | ViT トークン | E2E | [OpenGVLab/VideoMamba](https://github.com/OpenGVLab/VideoMamba) | Temporal-First 62.4 vs Spatial-First 65.1（SSv2、Fig. 7a） |
| 5 | [DefMamba](https://arxiv.org/html/2504.05794v1) | 学習 offset で走査点・順序を変形（画像のみ） | トークン | E2E | 未確認 | 変形分岐単独では 76.5 で baseline 76.9 を**下回る**（Table 4） |
| 5 | [MambaLCT](https://arxiv.org/html/2412.13615v1) | 前フレームの最終 state を次フレームの初期 state にし、context token に要約 | 探索トークン全体 | E2E | [GXNU-ZhongLab/MambaLCT](https://github.com/GXNU-ZhongLab/MambaLCT) | LaSOT AUC +1.7（Table 4a） |
| 5 | [LiVOS](https://arxiv.org/html/2411.02818v1) | **key-addressed 行列 state**：S_t = G_t⊙S_{t−1} + φ(K)ᵀV | C_k×C_v = 64×256 | E2E | [uncbiag/LiVOS](https://github.com/uncbiag/LiVOS) | MOSE 64.8。STM 系比で GPU メモリ −53%。gate ablation は未取得 |
| 6. SAM2 派生・VOS メモリ | [SAM2 GRU memory](https://arxiv.org/pdf/2408.00714) | memory に GRU を追加 | stride 16 memory | E2E | facebookresearch/sam2 | **改善なし**（MOSE dev 73.1→72.3 と読める。Table 11、行対応は §6 参照） |
| 6 | [XMem sensory](https://huggingface.co/papers/2207.07115.md) | **位置固定の GRU hidden**（H×W×64） | stride 16 | E2E | hkchengrex/XMem [未] | 除去で D17 −1.1、Y18 −1.3、Long-time −1.9（Table 4） |
| 6 | [SAMURAI](https://arxiv.org/html/2411.11922v2) | box 上の Kalman filter + motion-aware memory 選択 | 物体 box | **学習なし** | [yangchris11/samurai](https://github.com/yangchris11/samurai) | AUC 68.32→74.23（Table 3、LaSOT と推定） |
| 6 | [SAM2Long](https://arxiv.org/abs/2410.16268), [DAM4SAM](https://arxiv.org/html/2411.17576v1) | 木構造 memory 経路／distractor 用 memory | memory 選択 | **学習なし** | Mark12Ding/SAM2Long, jovanavidenovic/DAM4SAM | 平均 +3.7 J&F / DiDi 0.649→0.694（Table 1） |
| 6 | [SAMWISE](https://arxiv.org/html/2411.17646v2) | Hiera 内の時間 adapter（HSA） | encoder の最後 3 層 | **固定** | [ClaudiaCuttano/SAMWISE](https://github.com/ClaudiaCuttano/SAMWISE) | HSA で +3.9 J&F（MeViS、Table 2）。RVOS である点に注意 |
| 6 | [SeC](https://arxiv.org/html/2507.15852v3) | LVLM の concept vector を memory 条件付き特徴に cross-attention で加算 | stride 16 | memory attention のみ学習 → LVLM の LoRA | project page | SeCVOS +11.8 だが **MOSE v1 は +0.8 のみ** |
| 6 | [EdgeTAM](https://arxiv.org/pdf/2501.07256) | 2D 局所 latent による memory 圧縮 | memory | 蒸留込み学習 | [未] | 2D のみ 63.1 vs global のみ 62.0（SA-V val、Table 3b） |
| 7. SAM 3 系 | [SAM 3](https://arxiv.org/html/2511.16719v1) / [SAM 3.1 Object Multiplex](https://github.com/facebookresearch/sam3/blob/main/RELEASE_SAM3p1.md) | 検出器と tracker を分離。3.1 は最大 16 物体を bucket で共有パス処理 | — | tracker は PE 凍結で学習 | facebookresearch/sam3 | MOSEv1 78.4→79.6、MOSEv2 60.3→62.3（release notes） |
| 追加：データの時間依存性 | [Only Time Can Tell](https://arxiv.org/pdf/1907.08340) | frame shuffle による時間依存クラスの同定 | — | — | — | 574 クラス中、時間順序が必要なのは 50 のみ（Table 1） |

### 2.2 カテゴリ別の読み：何が今の構成に移植できるか

**カテゴリ1（flow warp）では、state warp の効果は base が単フレームのときにだけ大きい。** 最も大きな差は video SR で出ている。BasicVSR は alignment を外すと −1.19 dB、BasicVSR++ は flow guidance のない DCN で学習そのものが崩壊する（27.44 dB）（[BasicVSR++, Table 4](https://arxiv.org/pdf/2104.13371)）。これに対し segmentation で state や特徴を warp した場合の上積みは小さく、GRFP で +0.7〜1.1 mIoU、NetWarp で +1.3 IoU 程度であり、しかも backbone を微調整した条件の値である（[GRFP, Table 1](https://ar5iv.labs.arxiv.org/html/1612.08871)、[NetWarp, Table 1](https://ar5iv.labs.arxiv.org/html/1708.03088)）。今の構成に最も近い前例は2つある。NetWarp は融合重みを w2=0 で初期化し、元の網と等価な状態から始めており、user のゼロ初期化残差と同じ思想である。Tokmakov らは固定した 2-stream の上で ConvGRU だけを学習させ、memory を外すと −6.0 mIoU を得た（[Tokmakov et al., Table 1](https://ar5iv.arxiv.org/html/1704.05737)）。ただし Tokmakov の state はワープしておらず、空間方向の混合は 7×7 カーネルが担っている。計算量の目安としては、GRFP の STGRU が 512×512 で 35 ms、NetWarp は 1 層あたり約 2.5 ms・約 16K パラメータと軽い。flow 推定のほうが支配的になる。

**カテゴリ2（画像 flow → latent）の標準手順は「平均プーリングして stride で割る」である。** FGFA は stride 4 の flow を stride 16 の特徴に合わせて半分に縮小している（[FGFA §4](https://ar5iv.labs.arxiv.org/html/1703.10025)）。RAFT は内部で 1/8 解像度の flow を持つので、それを 2×2 平均して 1/2 倍すれば stride 16 の flow が直接得られる（[RAFT](https://ar5iv.arxiv.org/html/2003.12039)）。遮蔽の扱い方は3つある。GRFP 型の光度誤差ゲート、forward-backward 整合マスク、softmax splatting による forward warp である（[Softmax splatting](https://arxiv.org/abs/2003.05534)）。stride 16 では 1 セルが 16×16 px（1024 入力基準）に相当し、物体境界をまたぐセルの平均 flow は前景・背景のどちらの動きとも一致しない。ただし 64 段は SAM2 の memory 自体が stride 16 で、境界の詳細はデコーダの高解像度 skip が担う。そのため、64 段では「物体内部の state を物体と一緒に動かす」ことが主目的となり、境界誤差は許容しやすい（推論）。点追跡は、SAM-PT のように SAM の prompt として使うのが主流である。しかし MOSE で 38.5 にとどまり、SAM2 の memory 方式に大きく劣る（[SAM-PT](https://arxiv.org/html/2307.01197v1)）。**点追跡を SAM2 の prompt に使う方向は、本研究の目的に対しては的外れである。** 使うなら「state をどこへ運ぶか」の軌跡としてのみ使うべきである。RMNet では flow 推定器を TinyFlowNet から RAFT に替えても J&F が変わらなかった（0.835 vs 0.834、[RMNet, Table 7](https://arxiv.org/pdf/2103.12934)）。粗い前景の位置合わせで十分なことを示す証拠として重要である。

**カテゴリ3（潜在空間の対応）では、局所 attention の効果は強く、学習 offset は不安定である。** AOT は前フレームへの 15×15 局所 attention を外すと YouTube-VOS18 で −6.0 J&F となり、窓を 7 にしても −2.0 になる（[AOT, Table 3](https://arxiv.org/pdf/2106.02638)）。SAM2 の memory attention は global cross-attention だけで、明示的な short-term 局所経路を持たないので、ここに余地があるように見える。ただし AOT の値は LSTT ごと学習した条件のものであり、frozen SAM2 に後付けした場合はずっと小さいと見るべきである（推論）。学習 offset については否定的な一次証拠がそろっている。BasicVSR++ は flow guidance なしで崩壊し、Understanding DA は offset overflow によって整列特徴がゼロ化し、単フレーム SR に退化すると報告している（[Understanding DA](https://ar5iv.arxiv.org/html/2009.07265)）。DefMamba も変形分岐を単独で使うと baseline を下回る（[DefMamba, Table 4](https://arxiv.org/html/2504.05794v1)）。MaskProp の deformable 伝播は FlowNet2 より +15.2 mAP 良いが、64 GPU で E2E に学習した結果である（[MaskProp, Table 3](https://ar5iv.arxiv.org/html/1912.04573)）。user の構成では、教師は frozen デコーダを通ったマスク損失だけで、出力はゼロ初期化から始まる。この条件では、**offset 回帰より、frozen 特徴の類似度（相関の argmax／soft-argmax）か外部 flow で対応を決めるほうが崩壊リスクが低い**（推論）。TrajGRU は「state を warp してから更新する」ことが、同パラメータの ConvGRU より良いことを示した（[TrajGRU, Table 1](https://arxiv.org/pdf/1706.03458)）。これは作業仮説を理論的に支える前例になる。ただし user の Mamba は空間カーネルが 1×1 相当であり、比較対象の ConvGRU よりさらに弱い。

**カテゴリ4（物体／トークン state）では、state を持ち越すことより、state で現フレームを読み書きすることが効いている。** Cutie の object memory は MOSE で −0.4 しか寄与しない。これは seed 分散 ±0.26〜0.36 と同じオーダーである。一方、masked attention の除去は −3.5、object transformer の除去（L=0）は −2.2 になる（[Cutie, Tables 3/5/6](https://ar5iv.labs.arxiv.org/html/2310.12982)）。DVIS は凍結した segmenter の上に query 単位の tracker を学習し、OVIS で +5.5 AP を得た（[DVIS, Table 5](https://arxiv.org/pdf/2306.03413)）。ただし MinVIS 型の base は時間メモリを持たず、学習モジュールの query がマスク head に直結する。frozen デコーダの中間特徴に残差を足す user の構成とは、学習信号の届き方が違う。DVIS で標準 cross-attention が 2.9 AP、referring cross-attention が 30.5 AP となった差は、「前状態を identity として残差で保持しないと query state が崩壊する」ことを示している（Table 7）。SAM2 の object pointer は SA-V で +3.8、LVOSv2 で +4.6 と効くが、**MOSE dev では ±0** である（[SAM 2, Table 11](https://arxiv.org/pdf/2408.00714)）。物体単位の時間情報は、MOSE では効果が出にくい可能性が高い。

**カテゴリ5（動画 SSM）には、state を明示的にワープした一次資料が見つからなかった。** 最も近い前例は ConvS5 である。状態遷移 Ā は 1×1・対角のまま保ち、空間の混合を B（書き込み）と C（読み出し）の 3×3 カーネルに担わせる。B/C を 1×1 から 3×3 にすると FVD は 81→67 に改善する（[ConvS5, Table 5](https://arxiv.org/pdf/2310.19694)）。state カーネルを空間的にすると、並列 scan の中でカーネルが膨張するため採用されていない。user の構成はこの B/C カーネルすら持たない、ConvS5 の退化版にあたる。VideoMamba では Temporal-First 走査が最下位（62.4 vs 65.1）だった（[VideoMamba, Fig. 7a](https://www.ecva.net/papers/eccv_2024/papers_ECCV/papers/03773.pdf)）。ただし TF は T×H×W 全体を 1 系列に並べる方式で user の設計とは異なり、非因果の行動認識なので、転用性は弱い。LiVOS は VOS で唯一検証された「線形再帰 state による memory」である。S_t = G_t⊙S_{t−1} + φ(K)ᵀV を現フレームの key で読むので、対応は内容アドレスで解かれる（[LiVOS](https://arxiv.org/html/2411.02818v1)）。**user の per-pixel 設計は、key を位置の one-hot に固定した LiVOS の退化形と見なせる**（推論）。これが、動きに対して原理的に弱い理由の最も簡潔な説明になる。

**カテゴリ6（SAM2 派生）では、学習なしの memory 選択が最大の改善手段である。** SAMURAI（+5.9 AUC）、SAM2Long（平均 +3.7 J&F）、DAM4SAM はいずれも新しい特徴を足さず、どのフレームを memory に入れるかを変えている（[SAMURAI, Table 3](https://arxiv.org/html/2411.11922v2)、[SAM2Long](https://arxiv.org/abs/2410.16268)、[DAM4SAM, Table 1](https://arxiv.org/html/2411.17576v1)）。frozen SAM2 上で学習モジュールが効いた例は、配置に共通点がある。一方は memory attention より前に置くもので、SAMWISE は Hiera 内の時間 adapter で +3.9 を得た（[SAMWISE, Table 2](https://arxiv.org/html/2411.17646v2)）。もう一方は、内容アドレスで読む物体 state を持つもので、CamSAM2 の prototype が +8.4 mDice を得た（[CamSAM2, Table 5](https://arxiv.org/html/2503.19730v3)）。LSVOS 2025 の上位解法は、memory attention だけの微調整、SeC、memory 選択の組み合わせで、Mamba は登場しない（[LSVOS 2025 report](https://arxiv.org/pdf/2510.11063)）。

**カテゴリ7（SAM 3 / 3.1）の Object Multiplex は、時間モジュールの参考には直接ならない。** §4.7 に詳述する。

---

## 3. 1週間で試せる案ベスト3

### 3.0 前提：最初の1〜2日は新手法より診断に使う

どの案を試す前でも、次の3つを潰さないと比較が成立しない。これらは推論・解析によるもので、文献の主張ではない。

**D0：ゼロ初期化 × α の勾配を確認する。** 出力は out = x + α·P(m)、m = Mamba(LN(x))、P(·) はゼロ初期化した 1×1 射影である。g = ∂L/∂out とおくと、勾配は次のようになる。

- ∂L/∂P = α·g mᵀ
- ∂L/∂α = gᵀ P m
- ∂L/∂θ_Mamba = α·(∂m/∂θ)ᵀ Pᵀ g

**α の初期値も 0 なら、3つの勾配はすべて恒等的に 0 になり、学習は永久に始まらない**（weight decay 以外に P と α を動かすものがない）。ControlNet の zero convolution が1ステップで脱出できるのは、ゼロが1か所だけだからである（[ControlNet FAQ](https://huggingface.co/spaces/DmitrMakeev/Rerender/raw/4fcfd85a382db98b9230698aa0b8fd6f527f7beb/ControlNet/docs/faq.md)）。α≠0 でも、P=0 の間は Mamba 本体への勾配が 0 で、2層の積は小さな初期値から遅く立ち上がる。学習ログで α、‖P‖_F、‖αP(m)‖/‖x‖、‖∂L/∂θ_Mamba‖ を確認する。比が 1e-3 程度以下なら、モジュールは事実上恒等写像であり、2つの観測はどちらも自明に説明できる。その場合の修正は、α=1 かつ P ゼロ初期化、または α を小さな非ゼロ値（0.1 程度）にすることである。

**D1：リセットの意味を3条件に分ける。** mamba_ssm の `Mamba` には2つの推論キャッシュがある。1つは depthwise 因果 conv1d 用の **conv_state**（直近 d_conv=4 個の入力の窓）、もう1つは **ssm_state** である（[mamba_simple.py L208-253](https://github.com/state-spaces/mamba/blob/e9594ce1c732d97440f0332fdc43170a2294dbfa/mamba_ssm/modules/mamba_simple.py#L208-L253)）。B・C・Δ も conv 後の x から計算され、出力には D·x のスキップ（初期値 D=1、L113）が足される。したがって条件は次の3つに分ける。

- **R1**：ssm_state だけを毎フレーム 0 にする。受容野は 4 フレーム残る。
- **R2**：conv_state と ssm_state の両方を 0 にする。
- **R3**：L=1 の単独 forward（毎フレーム独立に呼ぶ）。R2 と等価である。

R1 で不変でも R2 で下がるなら、「長期 state は不要だが、短い時間窓は使われている」ことになる。R2 でも不変なら、モジュールは per-frame の MLP adapter として働いているだけである。

**D2：SAM2 memory を絞る。** 推論時に num_maskmem を減らす（直近 1 フレームのみ、または prompt フレームのみ）、あるいは object pointer を切る（設定変更で可能なはずだが、要コード確認）。この状態で「Mamba あり／なし」の差を見る。まず既存のチェックポイントで推論だけ行い、差の兆候があれば、同じ設定で学習もやり直す。これは (a) を最も直接に検定する操作であり、XMem が学習時に working memory を最大 3 フレームに制限して recurrent state に仕事を残した設計と同じ発想である（[XMem §3.6](https://arxiv.org/html/2207.07115v2)）。

### 3.1 案①（推奨）：flow で state を運ぶ warp-then-step（64 段のみ、まず flow oracle）

**直感。** 今の state は「床に固定された付箋」で、物体が動いても付箋は元の場所に残る。warp-then-step は、各フレームで更新する前に、付箋を物体の移動先へ貼り替える。貼り替える先は、外部 flow か frozen 特徴の照合で決める。学習パラメータを使わないので、「offset が育たない」問題を最初から回避できる。

**数式。** 64 段の各セル p について、現行の更新は次のとおりである。

h_t(p) = Ā_t(p)·h_{t−1}(p) + B̄_t(p)·u_t(p)、　y_t(p) = C_t(p)·h_t(p) + D·u_t(p)

warp-then-step では、これを次のように変える。

h_t(p) = Ā_t(p)·h_{t−1}(π_t(p)) + B̄_t(p)·u_t(p)

ここで π_t(p) = round(p + d_t(p)) で、d_t は t→t−1 の backward flow を stride 16 に写像したものである。

d_t = AvgPool₁₆( s ⊙ F_{t→t−1} ) / 16

s = (1024/W, 1024/H) は、SAM2 が入力を 1024×1024 の正方形に resize することに伴う異方スケールである（resize の仕様は要コード確認）。d≡0 のとき、モデルは現行モデルと**完全に一致**する。これが「位置合わせなし」の対照になる。

**実装の要点。** 1週間で組み込める理由は、最近傍対応なら、**入力を軌跡に沿って gather して既存の selective_scan にかける方法が、warp-then-step と厳密に等価**になることである。チェーン p_t=p、p_{s−1}=π_s(p_s) をたどり、系列 (u_1(p_1), …, u_t(p_t)) を作って scan し、最終出力を y_t(p) とする。Ā・B̄・C は各時刻の u から計算されるので、展開した式は warp-then-step と一致する。conv 窓（conv_state）も同じ軌跡に沿うので、「conv バッファもワープしないと不整合になる」という問題も自動的に解消される。

実装上の注意点は次のとおり。

- **系列長ごとのグループ化。** t=1…8 の各長さで HW 本の系列をまとめて forward する。conv1d に bias があるため、左ゼロ詰めは中立にならない。トークン数は Σt = 36 HW で、現行の 4.5 倍程度になる。64 段なら A4000 で問題ない。
- **遮蔽の扱い。** forward-backward 不整合（|F_f(x) + F_b(x+F_f(x))| > τ）を平均プーリングした信頼度が閾値を下回るセルでは、チェーンを切って新しい系列を始める（state のリセットに相当）。これにより、遮蔽後に前景 state が居残る ghosting を防ぐ。GRFP の光度誤差ゲートを離散化した版にあたる。
- **128／256 段。** 物体情報を持たず、ワープの費用と精度要求が最も高い。両群とも Mamba を外すか、現状のまま固定し、64 段だけを比較する。

**flow 源は2種類を用意する。**

- **①-a flow oracle**：SEA-RAFT または RAFT による事前計算。
- **①-b 推論のみの照合**：frozen な Hiera の stride 16 特徴（256ch）で 15×15 窓の cosine 相関をとり、argmax をとる。AOT の λ=15 に倣い、範囲は ±7 セル（≈±112 px）。パラメータは不要で、計算は 4096×225×256 ≈ 2.4 億 MAC/フレームと無視できる。Hiera 特徴の対応品質は未知なので、①-a を上限として先に測る。

**MOSE の flow 事前計算コスト（推定）。** MOSEv1 は全 130,149 フレームである（[MOSEv2, Table 1](https://arxiv.org/pdf/2508.05630v2)）。train 1,507/2,149 本で按分すると約 9.1 万フレーム、双方向で約 18 万ペアになる。

- **計算時間**（A4000 は 1080Ti の 1〜1.5 倍と仮定、480p 程度）
  - RAFT（32 iter）：約 3.5〜5 GPU 時間
  - SEA-RAFT の小型版：約 1〜2 GPU 時間（I/O が律速になる見込み）（[RAFT](https://ar5iv.arxiv.org/html/2003.12039)、[SEA-RAFT](https://arxiv.org/html/2405.14793v1)）
- **保存容量**
  - stride 16・fp16・双方向：約 2.9 GB。遮蔽マスクを含めて約 3.6 GB
  - 全解像度：約 300〜720 GB で非現実的
  - したがって、事前に平均プーリングして保存する
- **augmentation との整合**：flip では x 成分の符号を反転し、resize では変位をスケールする。ここを誤ると静かに性能が落ちる。

**理由。** 3点ある。(1) 作業仮説を直接検定できる唯一の案である。oracle で warp しても利得がなければ、位置ずれ仮説は棄却され、学習 offset を詰める意味がなくなる。(2) d≡0 との比較が同じコードパスで閉じる。(3) 対応を外部 flow と frozen 特徴に委ねるので、BasicVSR++ が示した「flow なし offset の崩壊」（27.44 dB）を構造的に避けられる。公式コードとしては、mamba_ssm（selective_scan_fn をそのまま使う）、SEA-RAFT（[princeton-vl/SEA-RAFT](https://github.com/princeton-vl/SEA-RAFT)、本調査では URL 未確認）、遮蔽処理の参照としての GRFP がある。

**想定リスク。**

- **最大のリスクは (a) である。** SAM2 memory が通常どおり働く条件では、利得は GRFP/NetWarp 程度（≲1 pt）にとどまると見込むべきである（推論）。
- **量子化の影響。** stride 16 で四捨五入するので、8 px 未満の動きは d=0 に丸められ、効果は高速物体に集中する。MOSE の配布フレームは総時間とフレーム数から実効約 5 fps と推定され（推論）、フレーム間変位は大きい。この点は検定にはむしろ有利だが、flow の失敗率も上がる。
- **state の複製。** 多対一のチェーンで state が複製される。
- **境界での混合。** 境界セルでは前景と背景の動きが混ざる。

**最小の検証実験。** 2×2 の4条件を、同じ seed で比べる。

- 軸1：d≡0 か d=flow か
- 軸2：num_maskmem が既定（7）か、制限（例：1）か

これに次の推論時チェックを加える。

- d=flow で学習したモデルを d=0 で推論する（state が使われていれば落ちる）。
- R2 リセットを適用する。

評価は動画単位の paired bootstrap で行い、GT 重心速度で層別する（下位・中位・上位の3分位）。予測は次のとおり。作業仮説が真なら、高速層でだけ差が出る。(a) が真なら、制限条件でだけ差が出る。

### 3.2 案②：ConvS5 型の空間 read/write カーネル（最安の対照）

**直感。** 付箋は床に固定したままにし、書き込むときと読むときに、近所の付箋も見られるようにする。物体が隣のセルへ動いても、読み出し側が隣を覗けば前の情報に届く。

**数式。** 状態遷移は pointwise・対角のまま保つ。

h_t(p) = Ā_t(p)⊙h_{t−1}(p) + Σ_{δ∈N_k} B̄_δ u_t(p+δ)、　y_t(p) = Σ_{δ∈N_k} C_δ h_t(p+δ)

これは ConvS5 の構造である（[ConvS5 §3, Table 5](https://arxiv.org/pdf/2310.19694)）。実装では、各フレームの in_proj 後の x に k×k の depthwise 2D conv（書き込み）をかけ、scan 後の y にも out_proj の前に k×k の depthwise 2D conv（読み出し）をかける。**中心タップを 1、周辺を 0 にした恒等初期化**にすれば、初期値は現行モデルと一致する。周辺タップへの勾配は近傍の活性 × g で、0 にならない。fused scan を壊さないので、メモリ増は conv の分だけで、実装は半日〜1日で済む。対照は k=1（現行）と k=7（7×7 で ±3 セル ≈ ±48 px）である。

**理由。** 3点ある。(1) TrajGRU が「warp > 局所 conv（同パラメータ）」を示した比較軸そのものであり、案①の効果が「局所的な空間混合でも得られるもの」か「対応が必要なもの」かを切り分ける対照になる（[TrajGRU, Table 1](https://arxiv.org/pdf/1706.03458)）。(2) 固定バックボーン上で ConvGRU（7×7）を学習して効いた前例がある（Tokmakov、−6.0）。(3) XMem の sensory memory も位置固定の ConvGRU で、+1〜2 J&F の寄与がある（[XMem, Table 4](https://huggingface.co/papers/2207.07115.md)）。コードは [NVlabs/ConvSSM](https://github.com/NVlabs/ConvSSM) を参照できる（実装言語は未確認）。

**想定リスク。** 理論上の限界がはっきりしている。書き込みで ±r、読み出しで ±r 広がるので、到達範囲は**経過時間に関係なく 2r セル**で止まる。s フレーム前の情報は、物体速度 v（セル/フレーム）について v·s ≤ 2r のときしか読めない。つまり低速物体の短期記憶しか運べない。state カーネル自体を空間化すれば受容野は時間とともに広がるが、それは並列 scan を壊す（ConvS5 が採らなかった理由）。境界の平滑化も起こりうる。

**最小の検証実験。** k=1 と k=7 の2条件を、案①と同じ評価（速度層別・D2 条件込み）で比べる。案①の oracle が案②を高速層で上回れば、「対応そのもの」が必要だったことになる。

### 3.3 案③：LiVOS 型の key-addressed 行列 state（位置不変の state carry）

**直感。** 付箋を床に貼るのをやめ、物体ごとに1冊の「索引つきノート」を持たせる。書くときは「この見た目の場所にはこの内容」と索引（key）付きで書き、読むときは現フレームの各セルが自分の見た目で索引を引く。物体がどこへ動いても、見た目が同じなら同じ内容が引ける。

**数式。** LiVOS の gated linear matching に倣う（[LiVOS Eq. 9](https://arxiv.org/html/2411.02818v1)）。

- key：k_t(p) = φ(W_k f_t(p)) ∈ ℝ^{64}。f_t は frozen Hiera の stride 16 特徴、φ はチャネル方向の softmax。
- value：v_t(p) = W_v[x_t(p); ŷ_t(p)] ∈ ℝ^{256}。x_t は 64 段の物体条件付き特徴、ŷ_t は 64×64 に縮小した予測マスク logit。
- 状態更新：S_t = G_t⊙S_{t−1} + Σ_p k_t(p)ᵀ v_t(p)、Z_t = g_t⊙Z_{t−1} + Σ_p k_t(p)ᵀ
- 読み出し：r_t(p) = k_t(p) S_{t−1} / (k_t(p) Z_{t−1})
- 出力：out = x + α·P(r)

ゲート G_t（または簡略化した per-key ベクトル）は、プールした特徴から σ で作る。Mamba の SSM と対応づけると、B_t が key、x が value、C_t が query に当たり、状態が対角ベクトルから行列に変わった形になる（Mamba-2/GLA 系、推論による対応づけ）。物体あたりの state は 64×256 と小さく、読み出しは 4096×64×256 ≈ 6700 万 MAC/フレームである。T=8 の Python ループで十分動く。

**理由。** 3点ある。(1) state carry の形を保ったまま、位置不変な対応を入れられる唯一の案であり、研究の主題に最も合う。(2) VOS で検証済みの前例があり（MOSE 64.8、STM 系比で GPU メモリ −53%）、公式コード [uncbiag/LiVOS](https://github.com/uncbiag/LiVOS) がある。(3) **「位置合わせなし」との対照を数学的にきれいに作れる。** key を位置の one-hot（4096 次元）に固定すると、S は 4096×256 の位置固定メモリとなり、現行の per-pixel 設計の線形版に退化する。key を内容にするか位置にするかだけを変えれば、対応の効果だけを分離できる。

**想定リスク。** 3点ある。(1) SAM2 の memory attention はすでに内容アドレスの softmax 照合（直近 6 フレーム + prompt + object pointer）なので、memory を通常どおり使う条件では (a) の冗長に最も直接ぶつかる。(2) 線形 attention は C_k=64 のランク制約のため、検索がぼやけやすい。LiVOS がゲートを必要とした理由でもある。(3) frozen デコーダが残差 r をどう解釈するかは保証されない。

**最小の検証実験。** key を位置 one-hot にした版と、内容 key にした版を、D2（memory 制限）条件と既定条件の両方で比べる。memory 制限下で内容 key が位置 key を上回れば、「対応付き state carry が SAM2 memory の代替になる」という修論の中核主張の最初の証拠になる。

### 3.4 次に実装する1案と1週間の配分

**次に実装するのは案①（flow oracle 版から）とする。** 案③のほうが研究主題には合う。しかし、案③の成否は (a) に強く依存し、失敗したときに原因を切り分けられない。案①は作業仮説の真偽を上限（oracle）で先に確定でき、その結果が案②・案③に進むかどうかを決める。

GPU 1 枚で 1 条件 6〜12 時間なので、1週間で回せる学習は約 10〜14 本である。配分は次のとおり。

- **1 日目**：D0 のログ確認、D1（推論のみ）、D2（既存チェックポイントで推論のみ）。並行して、flow の事前計算をバックグラウンドで回す（1〜2 時間）。
- **2〜3 日目**：案①の軌跡 gather を実装する。単体テストとして、d≡0 で現行の出力とビット単位に近く一致することを確認する。
- **3〜6 日目**：案①の 2×2 学習（4 本）。余裕があれば案②の k=7（1〜2 本）。
- **7 日目**：層別評価と判定。

判定基準は次のとおり（推論）。

- D0 で α≈0 → 初期化を直して baseline を取り直す。それ以前の結論はすべて無効になる。
- oracle でも高速層・memory 制限下の両方で利得なし → 密な位置合わせ路線を捨て、案③または物体トークン state（§4.4）へ移る。
- oracle で利得あり → ①-b（frozen 特徴の相関）と、§4.2 の flow-guided 残差 offset へ進む。

---

## 4. 修士論文（2027年2月）までに検討する発展案

本日（2026-11-02）から提出まで約 3 か月で、GPU 1 枚では 60〜80 条件程度が上限と見込む。以下は、優先度の高い順に並べる。

### 4.0 前提：「state を使わない方が筋がよい」証拠を正面から扱う

この証拠は複数ある。SAM2 改善の大きな報告は、SAMURAI（+5.9 AUC）、SAM2Long（+3.7 J&F）、DAM4SAM、SAM2Dual（MOSEv2 +1.32、[SAM2Dual](https://www.alphaxiv.org/abs/2608.18640)）といった**学習なしの memory 選択**に集中している。LSVOS 2025 の上位解法も、memory attention だけの微調整、SeC、memory 選択の組み合わせで構成されている（[LSVOS 2025 report](https://arxiv.org/pdf/2510.11063)）。SAM2 自身の GRU 試行は効かず、SeC の概念 state も MOSE v1 では +0.8 にとどまる（[SeC](https://arxiv.org/html/2507.15852v3)）。「MOSE の J&F を上げる」ことだけが目的なら、state carry は筋の良い手段ではない。これは文献から言えることである。

修論が state carry を主題にするなら、主張は次の2つのいずれかに置くべきである（推論）。

- **(i)** 定数サイズの state が、可変長の memory bank を置き換え・圧縮しても精度を保つ（効率の主張）。
- **(ii)** attention memory が構造的に保持しない情報、すなわち動き・速度、窓を超える長期の同一性を state が運ぶ（能力の主張）。

「memory attention はそのまま残して Mamba を足せば良くなる」という立て付けは、SAM2 Table 11・XMem・Cutie の ablation と逆向きである。**的外れになるリスクが高い。**

### 4.1 「state が memory を置き換える」設計と評価（最優先）

SAM2 の num_maskmem を 1〜2 に絞ると、memory のメモリ使用量と計算量は大きく減る。その不足分を案①または案③の state で補い、精度・メモリ・速度のパレートで評価する。

根拠は3つある。RMem は、memory を少数の必須フレームに制限するとむしろ精度が上がることを示した（VOST で J_tr 37.0→39.8、[RMem, Table 3](https://arxiv.org/html/2406.08476v2)）。EdgeTAM は、memory を 2D 局所 latent に圧縮しても SA-V で精度を保つことを示した（[EdgeTAM, Table 3](https://arxiv.org/pdf/2501.07256)）。LiVOS は、線形 state によって GPU メモリを 53% 削減した。

SAM2 自身の Table 9c では、memory 数 4/6/8 で MOSE dev が 73.5/73.0/73.2 とほぼ動かない（[SAM 2](https://arxiv.org/pdf/2408.00714)）。そのため、MOSE だけでは差が出にくく、**LVOSv2・SA-V val・MOSEv2 を評価に含める必要がある**。object pointer が効いたのも、これらのデータセットである。

### 4.2 flow-guided の残差 offset と、bilinear step モード（案①で利得が出た場合）

BasicVSR++ の形 o = s + C^o(·) を state に適用する。s は flow（または相関 argmax）、残差は tanh で ±2 セル程度に制限し、K=4〜9 点に sigmoid マスクを付ける（[BasicVSR++](https://arxiv.org/pdf/2104.13371)）。安定化策として、Understanding DA の offset-fidelity loss を併用する（[Understanding DA](https://ar5iv.arxiv.org/html/2009.07265)）。

bilinear warp では軌跡 gather との等価性が崩れる。そのため、step モード（PyTorch で h←h⊙exp(ΔA)+ΔB·x を 8 回まわす）で、ssm_state と conv_state の両方を warp する。

- **メモリ（推定）**：64 段で 134 MB/step、8 step で約 1.1 GB。256 段は約 16 倍で 16 GB に収まらない。高解像段は、64 段の offset を ×2・×4 に拡大して使い回す。
- **遮蔽**：GRFP に倣い、光度誤差または特徴誤差を Δ の入力に concat して、忘却ゲートとして使う。

repeated bilinear による state のぼけ（低域通過化）がリスクである。

### 4.3 学習による対応推定（flow なし）

Motionformer の trajectory attention（各フレームで空間 softmax をとり、軌跡上で集約）（[Motionformer, Table 4](https://arxiv.org/pdf/2106.05392)）を、「x_t を query、x_{t−1} を key として 15×15 局所 softmax → soft-argmax offset → state warp」に落とせば、メモリを最小にできる。h を 9×9 局所 attention で素直に unfold すると、約 10.9 GB/フレームになり不可能である（推定）。

これは 4.2 の後継として、flow 事前計算をなくす目的に限るべきである。DefMamba の変形分岐が単独では baseline を下回ったことと、BasicVSR++ の崩壊例から、**flow 事前分布なしの offset 回帰をいきなり主案にするのは避ける**。

### 4.4 物体トークン state を frozen SAM2 の「必ず通る入口」に注入する

64 段特徴の fg/bg masked pooling（Cutie 式）と obj_ptr を concat し、batch=物体・系列=時間の Mamba にかける。注入先は2つある。

- **(a) 追加の sparse prompt token**：mask decoder が必ず attend するので、現フレームに直接効く。
- **(b) obj_ptr へのゼロ初期化残差**：将来のフレームに効く。

空間を畳んでいるので、位置ずれは原理的に生じない。

設計原理は DVIS から取る。前状態を identity 残差として保持する referring CA（2.9→30.5 AP）が鍵である。また、学習モジュールの出力がデコードに直結していることが、frozen 下で効いた条件である（[DVIS, Tables 5/7](https://arxiv.org/pdf/2306.03413)）。更新は遅いほうがよい可能性がある（MeMOTR の EMA は λ=0.01 が最適、[MeMOTR, Table 7](https://arxiv.org/html/2307.15700v3)）。発展形として、SAMURAI の Kalman 状態を学習版に置き換える案がある。TrackSSM のように box 軌跡を SSM にかける（[TrackSSM](https://arxiv.org/html/2409.00487v2)）、あるいは SCOPE の MPM のように位置・速度の事前分布を logit に足す（[SCOPE](https://arxiv.org/pdf/2509.15781)）。

外部で学習した token を frozen デコーダに入れたときの OOD 挙動については、一次報告が見つかっていない。MOSE では obj_ptr 自体の効果が ±0 なので、ここでも評価は LVOSv2・SA-V で行う。

### 4.5 長い時間範囲の学習（(b) への対処）

SAM2 は 8 フレーム学習を「推論時の動画長に比べ短い」と認め、16 フレームで追加学習している（[SAM 2 §D.2.2](https://arxiv.org/pdf/2408.00714)）。XMem は、3 フレームでは sensory memory が学習できず、8 フレームが必要だったと明言している（[XMem §3.6](https://arxiv.org/html/2207.07115v2)）。

具体的には次を行う。

- 連続するクリップ間で、detach した state を持ち越す TBPTT
- 16〜24 フレームのクリップ
- 学習前後の Δ（実効時定数 ln2/(Δn)）の分布を追跡し、DeciMamba が言語で示した「学習長に縛られた受容野」が視覚でも起きるかを見る（[DeciMamba §3](https://arxiv.org/html/2406.14528v3)）

### 4.6 挿入位置の変更：memory attention より前に置く

SAMWISE は、frozen Hiera の最後 3 層に時間 adapter（HSA）を入れて +3.9 J&F を得た（[SAMWISE, Table 2](https://arxiv.org/html/2411.17646v2)）。SAM-I2V の TFI も +4.4 を報告しているが、こちらは凍結していない（[SAM-I2V, Table 4](https://arxiv.org/html/2506.01304v1)）。時間的に豊かになった特徴を frozen な memory attention とデコーダの両方が見る配置のほうが、デコーダ手前の残差より、学習信号の届き方の点で有利である可能性がある（推論）。ただし SAMWISE は referring VOS で、動詞の grounding も担うので、半教師あり MOSE への転用性は未知である。

### 4.7 複数物体と SAM 3.1 Object Multiplex：ID ごとの出力に時間モジュールを入れる場合の注意

**正式名は「Object Multiplex」で、SAM 3.1（2026-03-27）で導入された。** 元の SAM 3 は、検出器と tracker を共有の Perception Encoder の上で分離し、各 masklet を SAM2 式に独立して伝播する。そのためコストは物体数に線形に増える（[SAM 3](https://arxiv.org/html/2511.16719v1)）。Object Multiplex は「objects を固定容量の bucket にまとめて一緒に処理する」機構である（[RELEASE_SAM3p1.md](https://github.com/facebookresearch/sam3/blob/main/RELEASE_SAM3p1.md)）。公開チェックポイントでは multiplex_count=16 で、128 物体なら 8 bucket、memory 経路のパス数は O(N) から ⌈N/16⌉ に減る。同一性は、共有パス内の物体固有 embedding で保たれ、API は永続的な out_obj_ids を返す（[LearnOpenCV](https://learnopencv.com/sam-3-whats-new/)、二次資料）。

コード上は、"Data Space"（B, C, …）と "Multiplex Space"（num_buckets, multiplex_count, C, …）の間で reshape する `MultiplexState`（mux/demux）がある。空きスロットは −1、削除済みの物体には −1116 の sentinel が割り当てられる（[DeepWiki](https://deepwiki.com/facebookresearch/sam3/4.8-sam-3.1-object-multiplex)、自動生成資料）。速度は 128 物体で約 7 倍で、これは同期削減などの最適化を含めた値である。Appendix H の統制比較では 5.2 倍、単一物体で約 7% のオーバーヘッドとされるが、これは二次資料による。精度は MOSEv1 で 78.4→79.6、MOSEv2 で 60.3→62.3 である。

**時間モジュールを ID ごとの出力に入れる参考にするなら、mux/demux の後の Data Space（物体 ID ごと）に、ID をキーとした state 辞書を置くのが素直である**（推論）。Multiplex 自体は効率化の機構であり、時間モデリングの手法ではない。したがって、「Multiplex を真似れば時間対応が良くなる」という期待は的外れである。移植できる発想は、「共有空間マップ上で、スロット embedding によって物体別 state を区別する」ことに限られる。定式化の一次資料（Appendix H.1）は取得できていない。

### 4.8 評価設計（修論全体の共通基盤）

MOSE dev は、SAM2 自身の memory 設計を変えても ±0.5〜0.8 しか動かない（Table 9c/11）。Cutie でも seed 分散は ±0.26〜0.36 ある。したがって「95% 区間が 0 を含む」という結果は、効果量が 1 pt 未満なら当然に起こる（推論）。対策は次のとおり。

- 動画単位の paired bootstrap
- 複数 seed
- 効果量 0.5 J&F を検出するのに必要な動画数の事前見積もり（D12）
- 速度・カメラ運動・遮蔽からの再出現による層別
- LVOSv2・SA-V・MOSEv2・DiDi の併用

---

## 5. 反対仮説 (a)〜(c) に関する証拠と、見分けるための診断実験

### 5.1 (a)「SAM2 memory が時間情報を担っており、recurrent state は冗長」

**支持する証拠は強い。**

- **SAM2 §A.2.3／Table 11**：GRU による recurrent memory は「does not provide an improvement (except slightly on LVOSv2)」で、memory 特徴を memory bank に直接格納すれば十分だと結論している（[SAM 2](https://arxiv.org/pdf/2408.00714)）。数値は MOSE dev が 73.1→72.3、SA-V が 64.5→65.3、LVOSv2 が 67.0→68.9 である（行対応の不確かさは §6）。これは**凍結していない joint 学習でも効かなかった**ことを意味する。frozen SAM2 に後付けする本設定は、さらに不利と見るのが自然である（推論）。
- **XMem**：位置固定の GRU sensory memory の寄与は −1.1〜−1.9 にとどまる。著者自身も「temporal smoothness は与えるが、representation drift により長期予測には失敗する」と位置づけている（[XMem](https://arxiv.org/html/2207.07115v2)）。working memory を除去すると Long-time Video で 89.8→38.7 と壊滅的に落ちる。時間情報の主な担い手は attention memory である（[XMem, Table 4](https://huggingface.co/papers/2207.07115.md)）。
- **Cutie**：object memory の除去は −0.4 にとどまる（[Cutie, Table 5](https://ar5iv.labs.arxiv.org/html/2310.12982)）。
- **静的バイアス**：Sevilla-Lara らは、標準ベンチマークの多くが時間順序を必要としないことを示した（574 クラス中 50 のみ、[Only Time Can Tell, Table 1](https://arxiv.org/pdf/1907.08340)）。

**否定する（あるいは限定する）証拠もある。** SAMURAI は学習なしの運動モデルで +5.9 AUC を得ており、SAM2 memory が時間情報を使い切っているわけではない（[SAMURAI, Table 3](https://arxiv.org/html/2411.11922v2)）。正確に言えば、冗長なのは「学習された位置固定の recurrent state」であり、「動き情報そのもの」ではない（推論）。

また、(a) と作業仮説は排他ではない。memory attention は位置に依らない照合で動きを吸収できるが、per-pixel state はそれができない。両者は同じ現象の表裏である可能性が高い。

### 5.2 (b)「8 フレームでは長期記憶が要らない」

**支持する証拠。**

- XMem は、3 フレームでは sensory memory が初期状態に依存しすぎて学習できないため、8 フレームに伸ばした（§3.6）。
- SAM2 は 8 フレーム学習を短いと認め、16 フレームで追加学習した（§D.2.2）。ただし Table 9b では 4/8/10 フレームで SA-V が 60.0/68.3/68.1 と、8 フレームで飽和している。
- DeciMamba は、Mamba の実効受容野が学習系列長に縛られ、それを超えると文脈の利用が急落することを示した（[DeciMamba Fig. 5, Eq. 9](https://arxiv.org/html/2406.14528v3)）。

mamba_ssm の既定初期化（dt を 0.001〜0.1 の対数一様、A_n=−n、[mamba_simple.py L91-114](https://github.com/state-spaces/mamba/blob/e9594ce1c732d97440f0332fdc43170a2294dbfa/mamba_ssm/modules/mamba_simple.py#L91-L114)）では、1 ステップあたりの保持率 exp(−Δn) から半減期が 0.43〜693 ステップに分布する（解析）。8 フレームの学習では、長い時定数が有用性によって鍛えられる機会がない。学習後の Δ 分布を見れば、(b) を直接検証できる。

**否定する証拠。** MambaLCT は、長さ 2 のクリップ学習でも carried state で +1.7 AUC を得ている。サンプリング長 4 はむしろ悪い（69.8）（[MambaLCT, Table 4b](https://arxiv.org/html/2412.13615v1)）。state がコンパクトな文脈要約であれば、短いクリップでも学習できる。

また、本設定では 8 フレーム内の情報を SAM2 memory がすでに供給しているので、(b) は (a) と交絡する。(b) は、memory を制限した条件で検定するのが筋である（推論）。

### 5.3 (c)「ゼロ初期化／固定デコーダのせいで学びにくい」

**解析で確実に言えること。** §3.0 の D0 のとおり、α の初期値が 0 なら勾配は恒等的に 0 である。ReZero、LayerScale、Fixup といった残差ゲートの初期化手法は、いずれも「ゼロ（または極小）は1か所だけ」にしている。これらの論文本文は本調査では未確認なので、参考にとどめる。

**類推的な証拠。** Wang らは、強いモダリティと弱いモダリティを融合すると、最良の単一モダリティより悪くなることを示した（RGB 単独 72.6 vs Audio+RGB 71.4、[Wang et al. CVPR 2020, Table 1](https://openaccess.thecvf.com/content_CVPR_2020/papers/Wang_What_Makes_Training_Multi-Modal_Classification_Networks_Hard_CVPR_2020_paper.pdf)）。本設定に写像すると、SAM2 memory という強い既存経路が損失をほぼ最小化しているため、新しい経路に流れる勾配は小さい。これは最適化の失敗というより、損失がそれを必要としていないことを意味し、(a) と (c) は学習ダイナミクスの上でつながる（推論）。

固定デコーダは勾配を通すので、学習が不可能になるわけではない。ただしデコーダは、学習時に見たことのない特徴方向を解釈する保証がない。frozen 下で効いた例（DVIS、CamSAM2 の decamouflaged token）は、出力が head に直結するか、デコーダの token として入る形をとっている。

### 5.4 見分けるための診断実験（予測つき）

| # | 実験 | 作業仮説（位置ずれ）が真 | (a) 冗長が真 | (b) 短クリップが真 | (c) 学習不全が真 |
|---|---|---|---|---|---|
| D0 | α、‖P‖、‖αP(m)‖/‖x‖、Mamba 勾配ノルムをログ | 比は非ゼロ | 小〜中 | 非ゼロ | **α≈0 または比≈0** |
| D1 | リセットを R1（ssm のみ）／R2（ssm+conv）／R3（L=1）に分ける | R1 では不変でも R2 で低下しうる | 全条件で不変 | — | 全条件で不変 |
| D2 | SAM2 memory を制限（num_maskmem=1、OP off など） | 制限下でも利得は小 | **制限下で利得が出る** | 制限下で利得あり | 制限下でも利得なし |
| D3 | 静止画に速度 v=0/2/4/8/16 px の合成平行移動を与える | **v=0 で利得があり、v≥16 px（1 セル）で消える** | v=0 でも利得なし | — | v=0 でも利得なし |
| D4 | oracle warp（案①、ssm と conv の両方） | **warp で利得** | warp しても利得なし | — | 利得なし |
| D5 | 学習クリップ長 8 vs 16/24、推論のリセット周期 1/8/16/∞ | — | 差なし | **長クリップで利得、周期に敏感** | 差なし |
| D6 | 推論時に frame shuffle／reverse（SAM2 memory は通常順） | — | 差なし | — | 差なし |
| D7 | ssm_state から t−k の GT マスクを線形プローブで復元 | 同位置では低く、ワープ位置では高い | 情報はあるが使われない | k>8 で低下 | 無情報 |
| D8 | 物体速度・カメラ運動・遮蔽で層別した ΔJ&F | 低速・静止カメラでだけ利得 | 全層で ≈0 | 長い遮蔽で差 | 全層で ≈0 |
| D9 | デコーダの部分開放（LoRA）を対照に置く | — | 差なし | — | **開放で利得** |
| D10 | 初期化の対照（α=1 & P 小乱数／α=0.1 & P=0／ReZero 型） | — | 差なし | — | **初期化で結果が変わる** |
| D11 | 学習前後の Δ 分布（半減期） | — | — | **8 フレーム以下に短期化** | 初期値から不動 |
| D12 | 動画単位 paired bootstrap による検出力の見積もり | 共通 | 共通 | 共通 | 共通 |

優先順位は D0 → D1 → D2 → D4（=案①）/D3 → D8 → 残り、とする。D0 で α≈0 なら、他の実験は意味を持たない。D2 で利得が出て、かつ D3 で利得が v に対して単調に減るなら、(a) と作業仮説の両方が真である。その場合、設計は位置不変の state（案③、§4.4）か、ワープした state へ移すべきである。D2 で memory を絞っても効かず、D0 が健全なら、原因は D9 の固定デコーダ側か、「空間混合のない per-pixel 1D Mamba」という帰納バイアスそのものにある。D3 は静的カメラの動画でも代用できる。stride 16 の 64 段では閾値が 16 px、128/256 段では 8/4 px になるので、段ごとの除去と組み合わせると、作業仮説に対する特異性が上がる（推論）。

---

## 6. 不確かな点・論文間で矛盾する証拠

**SAM2 Table 11 の中間行（72.3/65.3/68.9）が「GRU のみ」か「GRU + object pointer」かは、抽出テキストではチェックマーク列が崩れていて確定できない。** 2つのノートで解釈が分かれた。ただ、「LVOSv2 でわずかに改善」という本文と整合するのは「GRU のみ（OP なし）」の読みである。この読みでは、なし（67.0）に対して +1.9 となる。もう一方の読みでは、OP のみ（71.6）に対して LVOSv2 が低下し、本文と合わない。したがって前者が妥当と判断する（推論）。どちらの読みでも、MOSE dev で改善がないことは変わらない。原典 PDF で要確認である。

**SAMURAI Table 3 の行対応もノート間で食い違う。** 一方は「motion のみ 70.81／memory 選択のみ 72.67」、他方は逆とした。Table 4 で α_kf=0（KF のスコアを使わない）が 72.67 になることと整合するのは、前者（memory 選択のみ = 72.67）である。Table 3 のデータセット名も本文に明記されておらず、LaSOT と推定している。

**DVIS の計算資源の記述は論文内で矛盾する。** abstract では「11 GB の単一 GPU で学習・推論可能」とあるが、付録では「8 GPU で学習」と書かれている（[DVIS](https://arxiv.org/pdf/2306.03413)）。A4000 で再現できるかは不確実である。

**MOSE のフレームレートと train のフレーム数は推定値である。** 130,149 フレーム ÷ 443.62 分から約 4.9 fps と推定したが、本文中に 433.62 分という食い違いもある（[MOSE](https://arxiv.org/pdf/2302.01872)）。train 約 9.1 万フレームは動画数による比例按分で、実数はデータ実体で数えて確定すべきである。flow のコストも、A4000 の実測ではなく外挿である。

**「位置固定 state は原理的に効かない」とは言えない。** 同じく位置固定の XMem sensory memory は、E2E 学習で +1〜2 効いている。これは作業仮説の強い形と矛盾する。stride 16 で隣接フレーム間の移動が 1 セル以内に収まる場面が多いことや、ConvGRU の空間カーネル（XMem のカーネルサイズは未検証）が効いている可能性がある。

**学習 offset について、MaskProp と BasicVSR++ は逆の結論を示す。** MaskProp では flow なしの deformable 伝播が flow を +15.2 mAP 上回るが、BasicVSR++ では flow なしの DCN が崩壊する。差は学習規模、マスクで絞った特徴、タスクの違いから来ると考えられ、frozen・弱教師の本設定は BasicVSR++ 側に近い（推論）。

**flow の品質の効き方も論文で異なる。** GRFP では FlowNet1 に替えると利得が減るが、RMNet では TinyFlowNet と RAFT で差がない。用途の違い（state の運搬か、照合領域の限定か）で説明できるが、本設定でどちらに近いかは実験で決める必要がある。

**memory 量の効き方も一様ではない。** RMem では memory を絞るほうが良いが、SAM2 Table 9c では 8 フレームのとき SA-V で最良（69.0）である。データセットとモデルによって最適な memory 量が異なる。

**その他、表番号や行対応に不確かさが残るもの。**

- BasicVSR の −1.19 dB は、評価セットが抜粋で特定できない（REDS4 と推定）。
- BasicVSR++ Table 3 の列と構成要素の対応は推定である。
- Cutie の表番号は ar5iv 版によるもので、CVF 版とずれる可能性がある。Table 5 は抽出時に S と X の記号が入れ替わっている疑いがある。
- SAM2 の GRU の挿入位置、SAM2.1 チェックポイントが 16 フレーム FT を含むか、obj_ptr の保持本数（16 本程度と記憶）は未確認である。

**SAM 3.1 の Appendix H（定式化と統制比較）は一次資料を取得できていない。** 5.2 倍・7% という数値は二次資料による。MoSAM の数値は第三者レビューによるもので、凍結の有無は未確認である。ViperSAM の評価は非公開の 4 動画のみで、根拠として弱い。

**網羅性の限界。** 「frozen SAM2 + memory attention 後の学習時間モジュール」を MOSE でアブレーションした一次研究、SSM の state を明示的にワープした一次研究、SAM2 の memory を SSM で置き換えた一次研究は、いずれも見つからなかった。未開拓である可能性もあるし、試されたが報告されていない可能性もある。また、**被引用数は一次的に取得できていない**。§7 に示す数値は記憶に基づく未検証の概数である。

---

## 7. 参考文献

被引用数は、すべて**未検証の概数**（記憶に基づくもので、Google Scholar 等では未確認）である。ノートに概数がない文献は「—」とした。

**SAM2 系・VOS メモリ**

| 文献 | ID / URL | 根拠の箇所 | 被引用（未検証） |
|---|---|---|---|
| SAM 2 (Ravi et al., 2024) | arXiv 2408.00714, https://arxiv.org/pdf/2408.00714 ; github.com/facebookresearch/sam2 | §A.2.3 Table 11（GRU, OP）、§A.2.1 Table 9b/9c、§4、§D.2.2 | 2000+ |
| XMem (Cheng & Schwing, ECCV 2022) | arXiv 2207.07115, https://huggingface.co/papers/2207.07115.md ; https://arxiv.org/html/2207.07115v2 | §3.1/§3.5/§3.6、Table 4、Table 8 | 700+ |
| Cutie (Cheng et al., CVPR 2024) | arXiv 2310.12982, https://ar5iv.labs.arxiv.org/html/2310.12982 ; https://github.com/hkchengrex/Cutie | Tables 3–7（ar5iv 番号） | 200+ |
| DVIS (Zhang et al., ICCV 2023) | arXiv 2306.03413, https://arxiv.org/pdf/2306.03413 ; https://github.com/zhang-tao-whu/DVIS | Tables 5–8 | 100+ |
| MeMOTR (ICCV 2023) | arXiv 2307.15700, https://arxiv.org/html/2307.15700v3 ; https://github.com/MCG-NJU/MeMOTR | Tables 5–7 | 100+ |
| RMem (CVPR 2024) | arXiv 2406.08476, https://arxiv.org/html/2406.08476v2 | Fig. 4、Tables 2/3/5/6 | — |
| LiVOS (Liu et al., CVPR 2025) | arXiv 2411.02818, https://arxiv.org/html/2411.02818v1 ; https://github.com/uncbiag/LiVOS | Eq. 9（gated linear matching） | — |
| AOT (Yang et al., NeurIPS 2021) | arXiv 2106.02638, https://arxiv.org/pdf/2106.02638 | Sec. 5、Table 3 | 400–500 |
| RMNet (Xie et al., CVPR 2021) | arXiv 2103.12934, https://arxiv.org/pdf/2103.12934 | Tables 5/7 | ~150 |
| HMMN (Seong et al., ICCV 2021) | arXiv 2109.11404, https://ar5iv.labs.arxiv.org/html/2109.11404 ; https://github.com/Hongje/HMMN | kernel-guided matching の節 | — |
| Tokmakov et al. (ICCV 2017) | arXiv 1704.05737, https://ar5iv.arxiv.org/html/1704.05737 | Table 1 | 数百 |
| SAMURAI | arXiv 2411.11922, https://arxiv.org/html/2411.11922v2 ; https://github.com/yangchris11/samurai | Tables 1–4 | — |
| SAM2Long (ICCV 2025) | arXiv 2410.16268, https://arxiv.org/abs/2410.16268 ; https://github.com/Mark12Ding/SAM2Long | abstract | — |
| DAM4SAM (CVPR 2025) | arXiv 2411.17576, https://arxiv.org/html/2411.17576v1 ; https://github.com/jovanavidenovic/DAM4SAM | Table 1 | — |
| SAMWISE (CVPR 2025) | arXiv 2411.17646, https://arxiv.org/html/2411.17646v2 ; https://github.com/ClaudiaCuttano/SAMWISE | Tables 1/2 | — |
| CamSAM2 | arXiv 2503.19730, https://arxiv.org/html/2503.19730v3 | Tables 1/4/5 | — |
| SeC (ICLR 2026) | arXiv 2507.15852, https://arxiv.org/html/2507.15852v3 | 主結果、Table 6 | — |
| EdgeTAM (CVPR 2025) | arXiv 2501.07256, https://arxiv.org/pdf/2501.07256 | Table 3/3b | — |
| SAM-I2V (CVPR 2025) | arXiv 2506.01304, https://arxiv.org/html/2506.01304v1 ; https://github.com/showlab/SAM-I2V | Tables 1/4/7 | — |
| SCOPE（LSVOS 2025 MOSEv2 3 位） | arXiv 2509.15781, https://arxiv.org/pdf/2509.15781 | MPM の節（Eq. 5） | — |
| LSVOS 2025 overview | arXiv 2510.11063, https://arxiv.org/pdf/2510.11063 | MOSEv2 / VOS トラックの上位解法 | — |
| SAM2Dual | arXiv 2608.18640, https://www.alphaxiv.org/abs/2608.18640 | MOSEv2 の結果 | — |
| Efficient-SAM2 | arXiv 2602.08224, https://arxiv.org/pdf/2602.08224 | 速度と精度 | — |
| SAM 3 (ICLR 2026) | arXiv 2511.16719, https://arxiv.org/html/2511.16719v1 | §3、§C.3、§C.4.1、Appendix H（未取得） | — |
| SAM 3.1 release notes | https://github.com/facebookresearch/sam3/blob/main/RELEASE_SAM3p1.md | VOS 表、速度 | — |
| SAM 3.1 二次資料 | https://learnopencv.com/sam-3-whats-new/ ; https://deepwiki.com/facebookresearch/sam3/4.8-sam-3.1-object-multiplex | multiplex_count、コード構造 | — |
| MOSE / MOSEv2 | arXiv 2302.01872, https://arxiv.org/pdf/2302.01872 ; arXiv 2508.05630, https://arxiv.org/pdf/2508.05630v2 | 統計、Table 1 | — |

**flow／ワープ／整列**

| 文献 | ID / URL | 根拠の箇所 | 被引用（未検証） |
|---|---|---|---|
| GRFP (Nilsson & Sminchisescu, CVPR 2018) | arXiv 1612.08871, https://ar5iv.labs.arxiv.org/html/1612.08871 | §3.1–3.2（Eqs. 1, 6–10）、Table 1、Table 8 | 数百 |
| NetWarp (Gadde et al., ICCV 2017) | arXiv 1708.03088, https://ar5iv.labs.arxiv.org/html/1708.03088 | Tables 1/3 | 数百 |
| FGFA (Zhu et al., ICCV 2017) | arXiv 1703.10025, https://ar5iv.labs.arxiv.org/html/1703.10025 | 解像度の対応、Table 1 | ~1000 |
| BasicVSR (CVPR 2021) | arXiv 2012.02181, https://ar5iv.labs.arxiv.org/html/2012.02181 | 本文の ablation、Tables 2–4 | ~1000 |
| BasicVSR++ (CVPR 2022) | arXiv 2104.13371, https://arxiv.org/pdf/2104.13371 | Tables 2–4、Fig. 8、Appendix A | 数百〜1000 |
| Understanding Deformable Alignment (AAAI 2021) | arXiv 2009.07265, https://ar5iv.arxiv.org/html/2009.07265 | 分解の解析、offset-fidelity loss | ~200 |
| TDAN (CVPR 2020) | arXiv 1812.02898, https://ar5iv.labs.arxiv.org/html/1812.02898 | Fig. 4、Tables 1/2 | ~700 |
| STSN (ECCV 2018) | arXiv 1803.05549, https://ar5iv.labs.arxiv.org/html/1803.05549 | 主結果（stride ablation） | ~300 |
| MaskProp (CVPR 2020) | arXiv 1912.04573, https://ar5iv.arxiv.org/html/1912.04573 | Table 3 | ~200 |
| TrajGRU (NeurIPS 2017) | arXiv 1706.03458, https://arxiv.org/pdf/1706.03458 | Eqs. 4–5、Tables 1/3 | 1000+ |
| Motionformer (NeurIPS 2021) | arXiv 2106.05392, https://arxiv.org/pdf/2106.05392 ; https://github.com/facebookresearch/Motionformer | Eqs. 4–6、Tables 3/4 | ~300 |
| RAFT (ECCV 2020) | arXiv 2003.12039, https://ar5iv.arxiv.org/html/2003.12039 | convex upsampling、warm start、速度 | 数千 |
| SEA-RAFT | arXiv 2405.14793, https://arxiv.org/html/2405.14793v1 | 速度（3090、1080p） | — |
| Softmax splatting (CVPR 2020) | arXiv 2003.05534, https://arxiv.org/abs/2003.05534 | abstract | — |
| SAM-PT (WACV 2025) | arXiv 2307.01197, https://arxiv.org/html/2307.01197v1 ; https://github.com/SysCV/sam-pt | 追跡器比較、MOSE の結果 | 100–200 |

**SSM／Mamba**

| 文献 | ID / URL | 根拠の箇所 | 被引用（未検証） |
|---|---|---|---|
| Mamba | arXiv 2312.00752, https://arxiv.org/pdf/2312.00752 | — | — |
| mamba_ssm 実装（commit e9594ce） | https://github.com/state-spaces/mamba/blob/e9594ce1c732d97440f0332fdc43170a2294dbfa/mamba_ssm/modules/mamba_simple.py | L35-40、L64-72、L91-116、L119-206、L208-253、L268-294 | — |
| ConvS5 (NeurIPS 2023) | arXiv 2310.19694, https://arxiv.org/pdf/2310.19694 ; https://github.com/NVlabs/ConvSSM | §3、Tables 5/6/8 | — |
| VideoMamba (Li et al., ECCV 2024) | https://www.ecva.net/papers/eccv_2024/papers_ECCV/papers/03773.pdf ; https://github.com/OpenGVLab/VideoMamba | Fig. 7(a) | — |
| DefMamba (CVPR 2025) | arXiv 2504.05794, https://arxiv.org/html/2504.05794v1 | Tables 4/5 | — |
| MambaLCT (AAAI 2025) | arXiv 2412.13615, https://arxiv.org/html/2412.13615v1 ; https://github.com/GXNU-ZhongLab/MambaLCT | Eqs. 8/9、Table 4 | — |
| TrackSSM | arXiv 2409.00487, https://arxiv.org/html/2409.00487v2 | S²L、ablation | — |
| DeciMamba (ICLR 2025) | arXiv 2406.14528, https://arxiv.org/html/2406.14528v3 | §1、§3、Eq. 9、Figs. 3/5 | — |

**学習ダイナミクス・時間依存性**

| 文献 | ID / URL | 根拠の箇所 |
|---|---|---|
| ControlNet FAQ（zero convolution） | https://huggingface.co/spaces/DmitrMakeev/Rerender/raw/4fcfd85a382db98b9230698aa0b8fd6f527f7beb/ControlNet/docs/faq.md | FAQ の勾配の議論 |
| What Makes Training Multi-Modal Classification Networks Hard? (Wang et al., CVPR 2020) | https://openaccess.thecvf.com/content_CVPR_2020/papers/Wang_What_Makes_Training_Multi-Modal_Classification_Networks_Hard_CVPR_2020_paper.pdf | Table 1、Gradient-Blending |
| Only Time Can Tell (Sevilla-Lara et al., WACV 2021) | arXiv 1907.08340, https://arxiv.org/pdf/1907.08340 | §3.2、Tables 1/2、Fig. 5 |

---

## 8. 付記：Mamba/SSM の挿入位置の変更、SAM2 内部の Mamba/SSM 置き換えの文献一覧（名前と URL のみ）

SAM2 の memory attention や memory encoder を SSM で置き換えた一次研究は、本調査では見つからなかった。候補名として検索した「TAMBA」「SAM2Mamba」「MambaVOS」も、一次資料では確認できなかった。

- Towards Efficient and Robust Long-Video Object Segmentation via VMamba-based Encoder and Intelligent Memory Management（NTU 修士論文、SAM2 の Hiera を VMamba に置換）— https://tdr.lib.ntu.edu.tw/handle/123456789/99154
- SAMba-UNet — https://arxiv.org/pdf/2505.16304
- SAM-Mamba (Mamba-guided SAM for zero-shot polyp segmentation) — https://arxiv.org/html/2412.08482v1
- A Hybrid Mamba-SAM Architecture for Efficient 3D Medical Image Segmentation — https://arxiv.org/html/2602.00650v1
- LiVOS（SAM ではない。線形再帰 memory）— https://arxiv.org/html/2411.02818v1 ; https://github.com/uncbiag/LiVOS
- MambaLCT（tracker 内の層 3/6/9 への挿入位置 ablation あり、SAM ではない）— https://arxiv.org/html/2412.13615v1
- MambaVLT — https://arxiv.org/html/2411.15459v1
- STTrack (Exploiting Multimodal Spatial-temporal Patterns for Video Object Tracking) — https://arxiv.org/html/2412.15691v1
- MambaTrack3D — https://arxiv.org/pdf/2511.15077
- TrackSSM — https://arxiv.org/html/2409.00487v2
- 内容未確認の検索ヒット（"SAM2 Mamba medical video"）— https://arxiv.org/html/2507.03698v1 ; https://arxiv.org/html/2408.04212v1
- 参考：Mamba ではないことを確認したもの — DD-SAM2 https://arxiv.org/pdf/2507.14613 ; Evaluating SAM2 for Video Semantic Segmentation https://arxiv.org/html/2512.01774v1
