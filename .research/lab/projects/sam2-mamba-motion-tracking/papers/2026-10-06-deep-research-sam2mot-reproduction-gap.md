# SAM2MOT DanceTrack 再現差の一次資料調査

## 要点：現時点で言えること／言えないこと

今回の調査で最も重要だったのは、**「SAM2MOT は DanceTrack に fine-tune していない」という論文の主張自体は確認できる一方、使われた detector checkpoint の記述が論文本文と現在の公式リポジトリで一致していない**ことです。SAM2MOT は「pre-trained detector + pre-trained segmentor + tracking logic」で benchmark-specific fine-tuning を不要とする zero-shot MOT と位置づけ、DanceTrack test で Co-DINO-L 75.5 HOTA、Grounding-DINO-L 75.8 HOTA を報告しています。したがって、ここでいう “no fine-tuning” は「モデルが未学習」という意味ではなく、**強力に事前学習済みの detector / SAM2.1 を DanceTrack 用に追加学習しない**という意味です。citeturn2view0turn3search6

ただし、**Co-DINO-L の実体について一次資料間に重大な不整合があります**。論文の Implementation Details は Co-DINO-L を “pretrained on COCO” とだけ記載しています。一方、現在の SAM2MOT 公式 README が想定する checkpoint 名は明示的に

`co_dino_5scale_swin_large_16e_o365tococo.pth`

です。これは Co-DETR 公式 Model Zoo で **Objects365 事前学習 → COCO** の Swin-L Co-DINO として公開され、COCO val box AP 64.1 のモデルです。通常の Swin-L `3x_coco` は別モデルで、COCO AP 60.0 です。fileciteturn2file0L2-L2 fileciteturn13file0L1-L2

これは今回の再現に直接関係します。接続された再現リポジトリの S0 manifest を確認すると、実際に使われたのは

`co_dino_5scale_swin_large_3x_coco-d7a6d8af.pth`

であり、COCO class 0 = person、soft-NMS IoU 0.8、書き出し下限 0.05、追跡側 det confidence 0.5 です。再現側は「論文本文の “pretrained on COCO” に忠実」という判断で 3x_coco を第一候補にしていました。fileciteturn30file0L2-L2 さらに再現側自身が同一系列で代替の O365→COCO checkpoint も測定し、det threshold 0.5 で明確に高い detection recall を得ており、この checkpoint 差が Q-R の再検出・再プロンプトにも影響し得ることを記録しています。fileciteturn31file0L2-L2

したがって、**現時点で最も強い「一次資料で確認できた条件差」は detector checkpoint です**。ただし、「この checkpoint 差が HOTA を何点下げた」とは言えません。COCO AP や一部 val の detection recall から DanceTrack HOTA の因果量を換算することはできないためです。

もう一つ非常に強いシグナルは **Quality Reconstruction 周辺**です。論文の Co-DINO-L test ablation では、baseline 62.9 → +Object Addition 67.9 → +Add+CoI 73.8 → full +Q-R 75.5 と進み、最後の Q-R は **+1.7 HOTA** です。一方、今回の val 内では 59.21 → 64.32 → 68.22 → 61.85 であり、Q-R 導入時は **−6.37 HOTA** です。split が違うため絶対値を比較すべきではありませんが、**各 split 内における Q-R の効果の符号が逆**であることは、split 差では済ませず実装・入力条件を疑う十分な理由になります。citeturn2view0

さらに著者本人は 2025年9月、公式 GitHub issue で「latest optimized version では `box reconstruction` module を削除し、論文より高い metric を得た」と回答しています。これは、現在の再現でいう Q-R 全体と box reconstruction が完全に同義だと証明するものではありませんが、**この部分の最終実装が論文記述だけから一意に再現できる状態ではない**ことを強く示します。fileciteturn8file0L1-L2

一方、「HOTA 70 以上の手法は何か秘密の trick を使っている」という一般化もできません。ただし今回確認した MOTIP、ColTrack、MOTRv2 については、**いずれも SAM2MOT と違って DanceTrack 自身で学習しており、さらに 70 前後～73台の特定 variant では CrowdHuman、DanceTrack val、pseudo-video、外部 detector などを利用する例が多い**ことは一次資料で確認できました。したがって、これらの HOTA と SAM2MOT の zero-shot 数値は、学習条件が同じ方法同士の比較ではありません。citeturn30view0 fileciteturn19file0L1-L2

そして最も重要な注意点として、今回の 68.22 は **DanceTrack val 25系列**、75.5 は **DanceTrack test** です。DanceTrack は train / val / test が別系列であり、test GT は非公開です。したがって **68.22 と 75.5 の 7.28 点を「再現ギャップ」と定量解釈すること自体ができません**。比較可能なのは、まず val 内の S1→S4 の差分構造と、論文 test 内の ablation 差分構造です。citeturn17search5

## SAM2MOT と今回の再現条件の比較

| 項目 | SAM2MOT 論文・公式資料 | 今回の再現 | 判定 |
|---|---|---|---|
| 評価 split | DanceTrack **test**。Co-DINO-L 75.5 HOTA / 89.2 MOTA / 83.4 IDF1、Grounding-DINO-L 75.8 / 88.5 / 83.9。Table 1。citeturn2view0 | DanceTrack **val 25系列**。S1 59.21、S2 64.32、S3(A6のみ) 68.22、S4 61.85（今回提示値）。repo も val 25系列を再現対象として明記。fileciteturn25file0L2-L2 | **確認できた差**。絶対 HOTA は直接比較不可 |
| Co-DINO backbone | Co-DINO-L / Swin-L。citeturn2view0 | Co-DINO-L / Swin-L 5-scale。fileciteturn31file0L2-L2 | 大枠一致 |
| Co-DINO checkpoint | 論文本文は “pretrained on COCO”。しかし公式 README の想定 checkpoint は `co_dino_5scale_swin_large_16e_o365tococo.pth`。citeturn2view0 fileciteturn2file0L2-L2 | `co_dino_5scale_swin_large_3x_coco-d7a6d8af.pth`。fileciteturn30file0L2-L2 | **確認できた差／一次資料同士にも矛盾** |
| Co-DINO の事前学習 | 公式 Co-DETR Model Zoo では `16e_o365tococo` は Objects365 pretrained → COCO、AP 64.1。3x_coco は COCO 36 epoch、AP 60.0。fileciteturn13file0L1-L2 | COCO 3x を使用。O365→COCO は代替候補としてのみテスト。fileciteturn31file0L2-L2 | **性能差を説明し得る確認済み条件差** |
| DanceTrack detector fine-tune | 論文は benchmark dataset で additional fine-tuning せず直接適用すると記載。citeturn2view0 | なし。fileciteturn31file0L2-L2 | 一致 |
| Grounding-DINO-L | 公式 README 想定 checkpoint は `grounding_dino_swin-l_pretrain_all-56d69e78.pth`。fileciteturn2file0L2-L2 | 今回の主要再現では未使用 | 比較対象のみ |
| Grounding-DINO-L の学習データ | SAM2MOT 論文は COCO + Objects365 と簡略記載。一方、**exact checkpoint** の MMDetection公式記録は Swin-L、O365V2 + OpenImagesV6 + “ALL”；ALL は GoldG、V3Det、COCO2017、LVISv1、COCO2014、GRIT、RefCOCO 系を含む。COCO AP 60.3。fileciteturn17file0L1-L2 | — | 論文記述以上に強い汎用事前学習であることを確認 |
| Segmenter | SAM2.1-large。citeturn2view0 | `sam2.1_hiera_large.pt` / `sam2.1_hiera_l.yaml`。fileciteturn32file0L1-L2 | checkpoint 名は一致。**ファイル hash は未確認** |
| SAM2.1 の事前学習 | SAM2 は SA-V を含む大規模 video-segmentation data engine で学習された foundation model。SAM2.1 large は 224.4M parameters の公式 improved checkpoint。fileciteturn14file0L1-L2 | 同名 large checkpoint | 「追加学習なし」でも強い事前学習済み model を使用 |
| SAM2 code provenance | SAM2MOT は公式 Meta SAM2 を基盤としていると repo が明記。ただし SAM2 の正確な commit / predictor variant は未公開。fileciteturn2file0L2-L2 | 接続 repo は `sam2/` を **SAMURAI 上流由来**と記録し、1 track = 1 inference state の per-instance 実装。fileciteturn25file0L2-L2 fileciteturn32file0L1-L2 | **確認済み provenance 差。ただし挙動差の因果は未確認** |
| Object Addition detector threshold | 論文: Co-DINO 0.5、Grounding-DINO 0.4、overlap ratio 0.7。citeturn2view0 | Co-DINO 0.5、detections は 0.05 まで保存し tracking 側で適用。fileciteturn30file0L1-L2 | 一致 |
| test時 detector threshold | 論文は unified configuration / default threshold を記載。citeturn2view0 | val は固定 0.5 | 一見一致 |
| 公式 test inference の追加情報 | 現在の公式 README は DanceTrack test で `config/dancetrack_test/co_dino_detections_thresholds.csv` または Grounding版を渡すコマンドを掲載。CSV 本体は未公開。fileciteturn2file0L2-L2 | この CSV は使用していない | **公開情報では内容・粒度不明。重要な未確認点** |
| ensemble | 論文・README に SAM2MOT ensemble の記載なし。citeturn2view0 fileciteturn2file0L2-L2 | なし | 公開資料上は一致。ただしコード非公開なので独立検証不可 |
| sequence別 tuning | 論文は unified configuration と主張。citeturn2view0 | sequence別 tuning なし | README の threshold CSV と緊張関係。CSV内容未確認 |
| mmdet environment | 著者回答: mmcv 2.1.0 / mmdet 3.3.0 / mmengine 0.10.5。fileciteturn4file0L1-L2 | mmcv 2.1.0 / mmdet 3.3.0 / **mmengine 0.10.4**。fileciteturn31file0L1-L2 | 確認できた小差。重要度は低いと推定 |
| CoI score variance | 著者が旧記述を訂正し、「Aの variance は B より小さい」が code logic と回答。fileciteturn5file0L1-L2 | current S3 は variance の大きい方を誤追跡 B とする。fileciteturn33file0L1-L2 | **現在の実装は著者訂正と整合** |
| CoI low-score memory filtering | 論文記述から一意でない | 今回提示の S3 は A6 のみ。repo 上では A7 を切る切り分け run も実施。fileciteturn33file0L1-L2 | 実装判断差。因果未確認 |
| Q-R / reconstruction | Paper Table 3 では +Add+CoI 73.8 → full 75.5。citeturn2view0 著者は後に optimized code で “box reconstruction” を削除したと回答。fileciteturn8file0L1-L2 | S3 68.22 → S4 61.85（今回提示）。接続 repo の committed logs は現時点で S0〜S3 までで S4 の exact implementation は監査不能。fileciteturn29file0L1-L2 | **最重要未確認点の一つ** |

### ablation の「絶対値」ではなく「差分構造」

この比較は split を跨いだ HOTA 値そのものではなく、**それぞれの split 内の変化**だけを見ています。

| 段階 | 論文 Co-DINO-L / DanceTrack test | test 内差分 | 今回 / DanceTrack val | val 内差分 |
|---|---:|---:|---:|---:|
| baseline | 62.9 | — | 59.21 | — |
| + Object Addition | 67.9 | **+5.0** | 64.32 | **+5.11** |
| + Object Addition + CoI | 73.8 | **+5.9** | 68.22 | **+3.90** |
| full + Q-R | 75.5 | **+1.7** | 61.85 | **−6.37** |

論文値は Table 3。citeturn2view0

この表から言えるのは、「val 59.21 が test 62.9 より 3.69 低い」ということではありません。それは split が違うため意味のある差ではありません。一方、**Object Addition は今回も +5.11 で、論文 test 内の +5.0 と非常によく似た方向・規模で効いています**。これは同一 split の再現ではないので成功証明にはなりませんが、少なくとも Object Addition が完全に壊れているという仮説は弱くなります。

逆に、**Q-R だけは論文では正、今回では大きな負**です。split が異なるとしても、−6.37 という大幅悪化は、まず Q-R の matching、re-prompt、state transition、どの box を再利用するか、検出器 recall、SAM2 memory 操作などを切り分けるべきシグナルです。

## DanceTrack HOTA 約70以上の候補手法と学習・追加データ条件

今回の目的には、SAM2MOT Table 1 と関係が明確な **MOTIP、ColTrack、MOTRv2 の3件で十分**です。上位手法を増やしても、SAM2MOT の再現差の原因特定にはほとんど寄与しません。

| 手法・DanceTrack test variant | HOTA / MOTA / IDF1 | Backbone / detector | DanceTrack学習 | 外部・追加データ | 特殊条件 | SAM2MOTとの比較上の意味 |
|---|---|---|---|---|---|---|
| **MOTIP, DT\* + CH** | **73.7 / 92.7 / 78.4**。公式旧 code branch。SAM2MOT Table 1 は同 HOTA/MOTA に対して IDF1 **79.4** と記載しており、1.0pt 不一致。fileciteturn19file0L1-L2 citeturn2view0 | Deformable DETR, ResNet-50。COCO pretrained weight から開始し、対象 dataset で brief detection pretraining。citeturn29view0 | **あり**。DanceTrack train + **val** を training に使用。 | **CrowdHumanあり**。 | trajectory augmentation を学習時に使用。旧 branch の `DT*` は train+val、`CH` は CrowdHuman。fileciteturn19file0L1-L2 | **73.7 は標準条件ではない**。SAM2MOT zero-shot と同条件とは扱えない |
| **ColTrack standard** | **72.6 / 92.1 / 74.0**。+val variant は 75.3 / 92.2 / 77.3。fileciteturn20file0L1-L2 | DINO-like detector、ResNet-50。baseline detector で CNN/encoder を初期化・freezeし、decoder/queryを学習。 | **あり**。DanceTrack で end-to-end tracker を学習。論文実装条件では DanceTrack 40 epochs。 | **CrowdHumanあり**。DanceTrack と joint dataset。 | multi-scale、Mosaic、Mixup。+val は validation も training に追加。 | 標準72.6の時点で外部データ + task-specific training |
| **MOTRv2 standard** | **69.9 / 91.9 / 71.7**。強化 variant は 73.4 / 92.1 / 76.0。citeturn19view0 | MOTR / ResNet-50 + **YOLOX-X detection proposals**。DanceTrack公式 YOLOX weight を利用。citeturn19view0 | **あり**。DanceTrack training。 | **CrowdHumanあり**。19,370 CrowdHuman train+val images から pseudo-video を作り DanceTrack と joint training。citeturn19view0 | 73.4 variant は **DanceTrack val training + 4-model test ensemble + extra association post-processing**。citeturn19view0 | 69.9 でさえ task-specific detector/tracker + CrowdHuman。73.4 はさらに強化条件 |

### MOTIP は「73.7」という数字だけを引用すると条件を誤認しやすい

MOTIP のケースは特に注意が必要です。現在の公式 main branch の Model Zoo は DanceTrack について、Extra Data = no の MOTIP を **HOTA 69.6** と掲載し、COCO から DanceTrack へ detector pre-training した checkpoint を公開しています。trajectory augmentation を外すと 65.2 まで下がります。fileciteturn10file0L1-L2

一方、SAM2MOT が比較表に置いた **73.7** に一致するのは、公式 MOTIP の `prev-engine` branch に保存されている

**DT\* + CH = DanceTrack train + val + CrowdHuman**

variant です。公式 branch は HOTA 73.7、DetA 82.6、AssA 65.9、MOTA 92.7、IDF1 78.4 と記録しています。fileciteturn19file0L1-L2 MOTIP v1 論文本文でも標準 DT-only は 67.5、DAB-Deformable DETR 版70.0、DT+CrowdHuman は71.4であり、CrowdHuman を用いた追加学習が性能を押し上げることが明示されています。citeturn30view0

したがって、既存レポートで挙げられた **MOTIP 73.7 は比較候補として有用ですが、「普通の MOTIP」として扱うのは不適切**です。むしろ「高HOTAの比較対象には、train+val+external data の強化条件が含まれる」という好例です。

一次資料:
- MOTIP paper: `https://arxiv.org/abs/2403.16848`
- CVPR 2025 DOI: `https://doi.org/10.1109/CVPR52734.2025.02596`
- official repo: `https://github.com/MCG-NJU/MOTIP`
- 73.7 と対応する official `prev-engine` branch: `https://github.com/MCG-NJU/MOTIP/tree/prev-engine`

### ColTrack は外部データなしの72.6ではない

ColTrack の paper / official repository は standard DanceTrack test を 72.6 HOTA と報告し、+val では75.3です。fileciteturn20file0L1-L2 論文の dataset setup では、DanceTrack training の際に **CrowdHuman を joint dataset に加える**ことを明記しています。また detector baseline で初期化した CNN / encoder を凍結し、decoder と query を学習する段階的 training を行います。したがって ColTrack 72.6 は、SAM2MOT の「DanceTrack fine-tuning なし」とは大きく条件が異なります。

一次資料:
- paper: `https://arxiv.org/abs/2308.05911`
- official code: `https://github.com/bytedance/ColTrack`

+val 75.3 は test評価そのものは有効ですが、**validation split を training に取り込んだ variant**なので、今回の「val 25系列で再現を検証している」プロジェクトとの性能比較にはさらに向きません。

### MOTRv2 は強い外部 detector + DanceTrack training + CrowdHuman

MOTRv2 の標準 69.9 HOTA は、YOLOX detection proposals を MOTR に与える設計です。DanceTrack では公式 DanceTrack が提供する YOLOX weight を使用し、さらに CrowdHuman の静止画を pseudo-video 化して DanceTrack train と joint training します。citeturn19view0

さらに有名な 73.4 variant は、論文自身が **extra association + DanceTrack validation set の training への追加 + 4-model ensemble** と明記しています。citeturn19view0 したがって 73.4 を「SAM2MOT 75.5 とほぼ同条件」と解釈するのは不適切です。

一次資料:
- paper: `https://arxiv.org/abs/2211.09791`
- CVPR paper: `https://openaccess.thecvf.com/content/CVPR2023/papers/Zhang_MOTRv2_Bootstrapping_End-to-End_Multi-Object_Tracking_by_Pretrained_Object_Detectors_CVPR_2023_paper.pdf`

ここまでから、**HOTA 70前後以上の比較手法には DanceTrack-specific training / CrowdHuman / val training / ensemble 等を使うものが確かにある**と結論できます。しかしこれは **SAM2MOT の75.5が同じ仕組みに依存している証拠ではありません**。SAM2MOT が公称しているのは逆に zero-shot であり、その代わり Co-DINO / MM-Grounding-DINO / SAM2.1 という非常に強い foundation/pretrained models を使っています。citeturn2view0

## 性能差を説明しうる要因の順位づけ

### 最優先：Co-DINO checkpoint の食い違い

**証拠の強さ：非常に高い。今回への関連性：非常に高い。因果量：未確認。**

これは今回新たに一次資料から確認できた最大の違いです。

再現側は論文の “Co-DINO-L (pretrained on COCO)” を文字通り読み、`3x_coco` を選択しています。これは再現側の S0 記録にも、その判断理由まで明記されています。fileciteturn31file0L1-L2

ところが現在の **SAM2MOT 公式 README 自身**が、想定 directory structure の checkpoint として

`co_dino_5scale_swin_large_16e_o365tococo.pth`

を指定しています。fileciteturn2file0L2-L2

Co-DETR 公式 Model Zoo では、そのモデルは “Objects365 pre-trained Co-DETR” の欄にある Swin-L / Co-DINO / COCO 64.1 AP です。対して 3x_coco Swin-L は60.0 APです。fileciteturn13file0L1-L2

さらに今回のプロジェクト自身が o365tococo も試しており、dancetrack0026 の先頭100 frame、score 0.5 では o365tococo が59.85% recallを得る一方、3x_coco より約10ポイント高かったという診断を残しています。fileciteturn31file0L2-L2

したがって、現在の最も妥当な表現は、

> **「再現実装が論文本文には忠実だが、現在の公式 SAM2MOT repository が示す実 checkpoint とは異なる可能性が高い」**

です。

なお、「著者が論文結果を o365tococo で出した」と断定まではできません。README は論文公開後に更新された可能性があり、実験時 checkpoint hash、config、ログが未公開だからです。この点が確認できれば判断は大きく変わります。

### 最優先：Q-R の実装／仕様の不一致

**証拠の強さ：非常に高い。今回への関連性：S4について非常に高い。**

論文 test 内では Q-R が悪化を起こしていません。Co-DINO の Table 3 は、

- +Add: 67.9
- +Add+Q-R: 69.1、すなわち **+1.2**
- +Add+CoI: 73.8
- full: 75.5、すなわち **+1.7**

です。citeturn2view0

これに対し今回 val 内の S3→S4 は **68.22→61.85、−6.37** です。split差があるため HOTA値そのものを対応付けることはできませんが、「有益な補正モジュールが導入直後に大幅悪化」という mechanism-level の現象は確認すべきです。

ここには detector checkpoint も絡み得ます。再現側 S0 の内部記録は、per-frame high-confidence detection recall が特に **Q-R の re-prompt / detector match の成立頻度**に影響し得ると明示しており、3x_coco と o365tococo の差が Q-R で増幅される可能性を既に疑っています。fileciteturn31file0L2-L2

また、著者自身が後日 “box reconstruction” を optimized implementation から削除したと回答した事実も、この領域を優先調査する根拠になります。fileciteturn8file0L1-L2

ただし、**「著者も Q-R は間違いだった」とまでは言えません**。issue は “box reconstruction” についての回答であり、論文の Q-R が複数処理を含む場合、その全体を削除したとは限らないからです。

### 高優先：未公開の DanceTrack test detector-threshold CSV

**証拠の強さ：存在は高確度、内容は不明。関連性：高い可能性。**

論文には Co-DINO threshold 0.5 / Grounding threshold 0.4 と書かれています。citeturn2view0 一方、現在の公式 README の DanceTrack test 実行コマンドは detector ごとに

`config/dancetrack_test/co_dino_detections_thresholds.csv`

を必須引数として渡します。fileciteturn2file0L2-L2

ところが実 repo にはコード・config・CSV がまだ公開されておらず、README 自身も “We will release our code soon” のままです。fileciteturn2file0L2-L2

したがって、CSV が

- 全 sequence 共通の0.5を列挙しただけなのか、
- sequence ごとに threshold が違うのか、
- detector score以外の threshold も含むのか、

は**公開情報では判断できません**。

ここを推測して「著者は sequence-specific tuning している」とするのは行き過ぎです。しかし、論文の “unified configuration” と README の test-specific CSV の関係は、再現性の観点では必ず解消したい矛盾です。

### 中～高優先：SAM2 predictor / memory 操作の実装差

**証拠の強さ：provenance差は確認済み、性能への因果は未確認。**

今回の private project では `sam2/` が **SAMURAI 上流由来**と明記されており、再現 tracker は一 object 一 inference state の `per_instance` 構成です。fileciteturn25file0L2-L2 fileciteturn32file0L1-L2

Meta の SAM2 repository は 2024年12月に video predictor を更新し、multi-object tracking で independent per-object inference を明示的にサポートするよう変更しています。SAM2MOT 論文はその後の2025年に公開されましたが、**著者がどの SAM2 commit / predictor 実装を使ったかは公開されていません**。fileciteturn14file0L1-L2

checkpoint 名 `sam2.1_hiera_large.pt` は一致しているので、これを detector checkpoint より上位の原因候補とする根拠はありません。しかし CoI/Q-R は SAM2 memory bank を直接扱うため、predictor implementation の微差は baseline より後段で増幅される余地があります。

### 中優先：CoI の未記載仕様、特に A7

**証拠の強さ：差の存在は確認済み。正解がどちらかは不明。**

再現 S3 の実装ログでは、A6 は「誤追跡と判断した現 frame を non-conditioning memory から除外」、A7 は「logit ≤ τ_s の frame を memory から除外」です。元の S3 run では双方を有効化し、その後 A7 を切った A6-only run も実施しています。fileciteturn33file0L1-L2

ユーザー提示の68.22は A6-only 条件です。これは **paper implementation と完全同一だと確認された条件ではありません**。ただし、古い paper text の variance 符号ミスについては、著者回答では「誤追跡 B は大きい variance 側」が正しく、今回の implementation もそのようになっているため、少なくともそこは主要容疑から外せます。fileciteturn5file0L1-L2 fileciteturn33file0L1-L2

### 必ず考慮すべきだが原因量は推定不能：val / test split

**証拠の強さ：確実。原因量：評価不能。**

これが「一番ありそうな実装バグ」という意味ではありませんが、**75.5−68.22をそのまま説明すべき差ではない**という意味で最重要の制約です。DanceTrack test と val は別動画群です。citeturn17search5

従って、

> S3 val 68.22だから、paper full test 75.5まで「あと7.28 HOTA足りない」

とは評価できません。

現在有効なのは、

> 「Object Addition の相対効果は論文の test ablation とよく似ている。CoI は正方向だが増分がやや小さい。Q-R は論文と逆方向に大きく壊れる」

という**構造的診断**です。

### 低優先：library minor-version 差

著者は mmcv 2.1.0 / mmdet 3.3.0 / mmengine 0.10.5 と回答しています。fileciteturn4file0L1-L2 再現側は mmcv 2.1.0 / mmdet 3.3.0 / mmengine 0.10.4 です。fileciteturn31file0L1-L2

これは確認できた差ではありますが、現時点で HOTA 数点規模を疑う一次資料上の根拠はありません。checkpoint、Q-R、threshold/predictor仕様より優先順位はかなり低いです。

### 総合順位

| 順位 | 説明候補 | 分類 | 現時点の確度 |
|---|---|---|---|
| **最重要** | `3x_coco` vs 公式 README が示す `o365tococo` | **一次資料で確認できた条件差**。ただし paper/repo 自体が矛盾 | **高** |
| **最重要** | Q-R matching / reconstruction / re-prompt implementation | **性能差を説明し得る。因果未確認** | **S4について高** |
| **高** | DanceTrack-test threshold CSV の未公開設定 | **公開情報では判断不能** | 中 |
| **中～高** | SAM2/SAMURAI code lineage、per-object predictor、memory操作 | **確認できた実装 provenance 差、因果未確認** | 中 |
| **中** | CoI A7 等の論文未記載判断 | **公開情報では正解不明** | 中 |
| **必須制約** | val vs test | **確実な評価条件差** | 高。ただし何点差かは不明 |
| **低** | mmengine 0.10.4 vs 0.10.5 | **確認済み小差** | 低 |

この順位からは、**「高HOTA手法が CrowdHuman 等を使っているから SAM2MOT の75.5も何か追加学習を隠している」ことを主仮説にする根拠はありません**。むしろ今回の再現に直接効きそうなのは、SAM2MOT 自身の exact checkpoint と未公開 inference / Q-R details です。

## 確認できれば判断が変わる公開 checkpoint・コード・著者情報

最も価値が高いのは、論文をさらに何本も読むことではなく、**SAM2MOT 自身の未公開 artifact を3点確定すること**です。

**第一は、Co-DINO-L の実験時 checkpoint の SHA256 / download URL です。**  
著者に確認すべき質問は「AAAI Table 1/Table 3 の75.5を生成した checkpoint は `co_dino_5scale_swin_large_3x_coco` か `co_dino_5scale_swin_large_16e_o365tococo` か」です。現在は paper text が前者を示唆し、official README が後者を明示しているため、一次資料が衝突しています。citeturn2view0 fileciteturn2file0L2-L2  
これが `o365tococo` と確認されれば、今回の A8 選択は「論文本文準拠ではあるが実験 artifact 非準拠」と整理し直す必要があります。

**第二は、`config/dancetrack_test/co_dino_detections_thresholds.csv` の実体です。**  
現在の README がこのファイルを test inference に使うことだけは確実ですが、ファイルは公開されていません。fileciteturn2file0L2-L2 これが単一 threshold 0.5 なら疑いはほぼ消えます。sequence ごとに異なる値なら、論文の “unified configuration” の意味を再解釈する必要があります。

**第三は、Q-R / box reconstruction の最終 AAAI 実装です。**  
必要なのは少なくとも「detector box と mask box の matching条件」「pending → reliable の再初期化条件」「どの SAM2 frame を conditioning/non-conditioning として更新・削除するか」「著者が issue #12 で削除した box reconstruction と paper Table 3 の Q-R の関係」です。著者が optimized code で box reconstruction を削除したという回答は存在しますが、そのコードは未公開です。fileciteturn8file0L1-L2

なお、2026年10月6日時点で接続した公式 SAM2MOT repository の README は依然として “We will release our code soon” としており、README が記述する `tracker/`、`config/`、checkpoint、threshold CSV は実際の repository root には公開されていません。したがって **現時点では official code による exact reproduction check はできません**。fileciteturn1file0L1-L2 fileciteturn2file0L1-L2

また、接続された今回の private repo の committed logs は S0〜S3 までで、S4 log がまだ repository 上にないため、**今回の61.85を生んだ Q-R の exact code/config はこの調査では直接監査できません**。fileciteturn29file0L1-L2 したがって S4 の原因については、これ以上具体的に「この条件式が間違っている」と断定するのは時期尚早です。

## 次に少数の一次資料で確認すべき箇所

広く文献を増やすより、次の箇所に限定するのが効率的です。

**SAM2MOT 最終 AAAI 版の Sec. Implementation Details、Table 3、Q-R / CoI 本文。**  
ここでは特に arXiv 初期版との差分履歴を確認する価値があります。CoI については既に著者が variance の記述ミスを認めており、Q-R/box reconstruction についても issue 上で実装更新を表明しているためです。fileciteturn5file0L1-L2 fileciteturn8file0L1-L2  
一次資料: `https://doi.org/10.1609/aaai.v40i7.37455`、`https://arxiv.org/abs/2504.04519`

**Co-DETR の `co_dino_5scale_swin_large_16e_o365tococo` config / model card。**  
これは追加の比較手法を調べるより今回の原因判定への情報価値が高いです。公式 Model Zoo は O365-pretrained → COCO 64.1 AP としており、今回使った3x_cocoとは明確に異なります。fileciteturn13file0L1-L2  
一次資料: `https://github.com/Sense-X/Co-DETR`

**SAM2MOT official repo の更新履歴と issue、特に code release / reconstruction 関連。**  
paper text よりも exact checkpoint、threshold CSV、最終 code が公開された場合の優先度が高いためです。現在の README は既に paper 本文にない checkpoint filename と test-threshold interface を示しており、再現条件を確定する最重要資料になっています。fileciteturn2file0L1-L2  
一次資料: `https://github.com/TripleJoy/SAM2MOT`

現時点の総括としては、**「SAM2MOT の75.5は DanceTrackで特別に追加学習したから高い」とする証拠は見つかっていません**。むしろ論文は明示的にその逆を主張しています。一方で、**“fine-tuningなし” と “弱いモデルを使っている” は全く同義ではありません**。SAM2MOT は SAM2.1-large と大型 detector を使い、Grounding-DINO-L variant に至っては exact checkpoint が非常に広範な外部データで事前学習されています。fileciteturn14file0L1-L2 fileciteturn17file0L1-L2

そして Co-DINO 再現については、**論文本文から選んだ `3x_coco` と、現在の公式 SAM2MOT README が名指しする `o365tococo` の不一致が、いま最も具体的で検証可能な条件差**です。加えて、Object Addition が val 内で論文とよく似た +5 前後の改善を示しているのに対し、Q-R だけが −6.37 と逆転していることから、現段階では「全体的に特殊な学習が足りない」という説明よりも、**detector exact checkpoint と Q-R 周辺の再現条件を分離して疑う方が、一次資料と現在の実測の双方に整合的**です。