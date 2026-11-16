---
date: 2026-11-13
project: lab-study-quantization
type: citation-notes
---

# 量子化勉強会（2026-11-20）引用箇所ノート

スライドで引用する原典15本から、節・式・表・図の番号、PDFページ、英語原文の短い引用、一言要約を抽出する。`pdftotext -layout` で得たテキストに基づく。ページは「PDFの物理ページ番号（1始まり）」で、論文内のページ番号と異なる場合は併記する。数値はテキストで確認できたものだけを書き、確認できないものは「未確認」とする。「一言の要約」は原典の記述に基づく（発表者の解釈は含めない）。

## ファイル一覧

保存先: `references/papers/`。取得日はすべて2026-11-13。取得元は、PDF本文から分かる範囲のみ記載する（公式ページでの照合は未実施）。

| ファイル名 | 正式タイトル | 会議/年（PDF内の表記） | 取得元（PDFから分かる範囲） | 版 | スライド表記 |
|---|---|---|---|---|---|
| 2018-cvpr-jacob-integer-only.pdf | Quantization and Training of Neural Networks for Efficient Integer-Arithmetic-Only Inference | 2018 IEEE Conference on Computer Vision and Pattern Recognition（PDFメタデータのSubject。本文には記載なし） | 未確認（CVF Open Access版のPDFと推定されるが、本文からは確認できない） | 会議版（10ページ） | 整数演算のみの推論 [Jacob+, CVPR2018] |
| 2018-arxiv-krishnamoorthi-whitepaper.pdf | Quantizing deep convolutional networks for efficient inference: A whitepaper | 会議発表ではなくarXiv（June 2018） | arXiv:1806.08342v1 [cs.LG] 21 Jun 2018 | v1（36ページ） | 白書 [Krishnamoorthi, arXiv2018] |
| 2021-arxiv-nagel-whitepaper.pdf | A White Paper on Neural Network Quantization | 会議発表ではなくarXiv（2021） | arXiv:2106.08295v1 [cs.LG] 15 Jun 2021 | v1 | 白書 [Nagel+, arXiv2021] |
| 2013-arxiv-bengio-ste.pdf | Estimating or Propagating Gradients Through Stochastic Neurons for Conditional Computation | 会議発表ではなくarXiv（2013） | arXiv:1308.3432v1 [cs.LG] 15 Aug 2013 | v1（12ページ） | STE [Bengio+, arXiv2013] |
| 2020-iclr-esser-lsq.pdf | Learned Step Size Quantization | Published as a conference paper at ICLR 2020 | arXiv:1902.08153v3 [cs.LG] 7 May 2020 | v3（12ページ） | LSQ [Esser+, ICLR2020] |
| 2020-icml-nagel-adaround.pdf | Up or Down? Adaptive Rounding for Post-Training Quantization | Proceedings of the 37th International Conference on Machine Learning, Online, PMLR 119, 2020 | 未確認（arXiv IDは本文から不明） | 会議版 | AdaRound [Nagel+, ICML2020] |
| 2021-iclr-li-brecq.pdf | BRECQ: Pushing the Limit of Post-Training Quantization by Block Reconstruction（本文で確認済み） | Published as a conference paper at ICLR 2021 | arXiv:2102.05426v2 [cs.LG] 25 Jul 2021 | v2 | BRECQ [Li+, ICLR2021] |
| 2022-eccv-yuan-ptq4vit.pdf | PTQ4ViT: Post-Training Quantization for Vision Transformers with Twin Uniform Quantization | 本文に会議名の記載なし（ファイル名・計画書ではECCV2022。公式ページでは未確認） | 未確認 | 会議版と推定（LNCS形式）。未確認 | PTQ4ViT [Yuan+, ECCV2022] |
| 2022-neurips-dettmers-llm-int8.pdf | LLM.int8(): 8-bit Matrix Multiplication for Transformers at Scale | 36th Conference on Neural Information Processing Systems (NeurIPS 2022) | 未確認（arXiv IDは本文から不明） | 会議版 | LLM.int8() [Dettmers+, NeurIPS2022] |
| 2023-icml-xiao-smoothquant.pdf | SmoothQuant: Accurate and Efficient Post-Training Quantization for Large Language Models | Proceedings of the 40th International Conference on Machine Learning, Honolulu, Hawaii, USA. PMLR 202, 2023 | 未確認（arXiv IDは本文から不明） | 会議版（13ページ） | SmoothQuant [Xiao+, ICML2023] |
| 2023-iclr-frantar-gptq.pdf | GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers（本文で確認済み） | Published as a conference paper at ICLR 2023 | arXiv:2210.17323v2 [cs.LG] 22 Mar 2023 | v2 | GPTQ [Frantar+, ICLR2023] |
| 2024-mlsys-lin-awq.pdf | AWQ: Activation-aware Weight Quantization for On-Device LLM Compression and Acceleration | Proceedings of the 5th MLSys Conference, Santa Clara, CA, USA, 2024 | 未確認（arXiv IDは本文から不明） | 会議版（14ページ） | AWQ [Lin+, MLSys2024] |
| 2023-neurips-dettmers-qlora.pdf | QLoRA: Efficient Finetuning of Quantized LLMs | 37th Conference on Neural Information Processing Systems (NeurIPS 2023) | 未確認（arXiv IDは本文から不明） | 会議版（28ページ、付録を含む） | QLoRA [Dettmers+, NeurIPS2023] |
| 2023-iccv-li-q-diffusion.pdf | Q-Diffusion: Quantizing Diffusion Models | ICCV（"This ICCV paper is the Open Access version, provided by the Computer Vision Foundation."。年は本文に記載なし。PDFメタデータSubject: IEEE International Conference on Computer Vision） | 未確認（CVF Open Access版） | Open Access版（採録版と同一と本文に記載） | Q-Diffusion [Li+, ICCV2023] |
| 2022-arxiv-micikevicius-fp8.pdf | FP8 Formats for Deep Learning | 会議発表ではなくarXiv（2022） | arXiv:2209.05433v2 [cs.LG] 29 Sep 2022 | v2 | FP8 [Micikevicius+, arXiv2022] |

スライド表記の注意:
- 「名前 [第一著者+, 会議名年]」の形式（例: SmoothQuant [Xiao+, ICML2023]）。会議発表でない3本（STE・Krishnamoorthi白書・Nagel白書）とFP8は、会議名の代わりにarXivと年を書く。Krishnamoorthi白書は単著のため「+」を付けない。
- PTQ4ViT（ECCV2022）の会議名・年、Q-Diffusion（ICCV2023）の年は、PDF本文だけでは確認できない（計画書・ファイル名に基づく）。公式ページでの確認を、スライド作成前に別途行う。
- Jacob（CVPR2018）はPDFメタデータのSubjectにのみ会議名があり、本文に記載がない。
- 引用の検証方法: 英語原文の引用は、`pdftotext` の出力に対して、空白・ハイフネーション・記号の正規化後に文字列照合した。数式中の添字・上付き・括弧は、PDFのテキスト抽出で崩れるため、数式の転記は人手で読んだ結果であり、照合の対象外。式の細部をスライドに載せる前に、PDFの該当ページで目視確認すること。

---

## 1. Jacob [Jacob+, CVPR2018]

Quantization and Training of Neural Networks for Efficient Integer-Arithmetic-Only Inference（PDF 10ページ。論文内ページ番号は2704〜2713で、PDF p5が論文内2708に当たる）

### 1-1. アフィン写像 r = S(q − Z)（§2.1 Quantization scheme、式(1)、PDF p3）

- 原文: "This is equivalent to requiring that the quantization scheme be an affine mapping of integers q to real numbers r, i.e. of the form r = S(q − Z) (1) for some constants S and Z."
- 原文: "The constant S (for “scale”) is an arbitrary positive real number."
- 原文: "The constant Z (for “zero-point”) is of the same type as quantized values q, and is in fact the quantized value q corresponding to the real value 0."
- 原文（実数の0を厳密に表せる理由）: "The motivation for this requirement is that efficient implementation of neural network operators often requires zero-padding of arrays around boundaries."
- 原文（粒度）: "Our quantization scheme uses a single set of quantization parameters for all values within each activations array and within each weights array; separate arrays use separate quantization parameters."（つまりこの論文はテンソル単位＝per-tensor）
- 8bitの場合: "For 8-bit quantization, q is quantized as an 8-bit integer"。biasは32bit整数（§2.4）。
- 一言の要約: 実数rと整数qの対応をアフィン写像 r = S(q − Z) とし、実数0がzero-point Zで厳密に表せるようにする。パラメータはテンソルごとに1組。

### 1-2. 学習中の疑似量子化（simulated quantization / fake quantization）（§3、式(12)、Algorithm 1、PDF p5）

- 原文: "We propose an approach that simulates quantization effects in the forward pass of training. Backpropagation still happens as usual, and all weights and biases are stored in floating point so that they can be easily nudged by small amounts."
- 原文: "The forward propagation pass however simulates quantized inference as it will happen in the inference engine, by implementing in floating-point arithmetic the rounding behavior of the quantization scheme that we introduced in section 2"
- 式(12): clamp(r; a, b) := min(max(x, a), b)、s(a, b, n) := (b − a)/(n − 1)、q(r; a, b, n) := ⌊(clamp(r; a, b) − a)/s(a, b, n)⌉ s(a, b, n) + a。nは量子化水準の数（8bitでn = 2^8 = 256）。
- Algorithm 1（PDF p5）の手順: 1 浮動小数点モデルの学習グラフを作る / 2 "Insert fake quantization TensorFlow operations in locations where tensors will be downcasted to fewer bits during inference according to equation 12." / 3 擬似量子化モードで収束まで学習 / 4 低ビット推論エンジン向けの推論グラフを作る / 5 量子化済み推論グラフで推論。
- 量子化範囲（§3.1、PDF p5）: 重みは a := min w, b := max w（int8で[−127, 127]に収める小さな調整あり）。活性は学習中に観測した範囲をEMAで集約する（"exponential moving averages (EMA)"）。範囲は 0.0 が整数として厳密に表せるよう nudge され、"S = s(a, b, n), Z = z(a, b, n) (13)" とアフィン写像のSとZに対応する。
- 一言の要約: 順伝播で丸めを浮動小数点上で模擬し、逆伝播は通常どおり行い、重みはfloatのまま保持する（fake quantization学習）。

### 1-3. 単純なPTQの失敗要因（§3、PDF p5）

- 原文: "Common failure modes for simple post-training quantization include: 1) large differences (more than 100×) in ranges of weights for different output channels (section 2 mandates that all channels of the same layer be quantized to the same resolution, which causes weights in channels with smaller ranges to have much higher relative error) and 2) outlier weight values that make all remaining weights less precise after quantization."
- 一言の要約: 小さなモデルで単純なPTQが精度を落とす要因として、出力チャネル間の重み範囲の大差（100倍超）と、外れ値の重みを挙げている。per-tensorの量子化パラメータが前提の記述。

### 1-4. BN folding（§3.2、式(14)、PDF p6）

- 原文: "the inference graph has batch normalization parameters “folded” into the convolutional or fully connected layer’s weights and biases, for efficiency. To accurately simulate quantization effects, we need to simulate this folding, and quantize weights after they have been scaled by the batch normalization parameters."
- 式(14): w_fold := γ w / sqrt(σ²_B + ε)。γはBNのscale、σ²_Bはバッチ全体での畳み込み結果の分散の推定、εは数値安定のための小さな定数。
- 付録の図: C.5（BN付き畳み込みの学習グラフ）、C.6（推論グラフ）、C.7（BN folding後の学習グラフ）、C.8（foldingと量子化の後の学習グラフ）。
- 一言の要約: BNを畳み込みの重み・biasに畳み込んでから重みを量子化する（学習側でもfoldingを模擬する）。

### 1-5. 結果の1点（Table 4.1、PDF p6）

- ImageNet、ResNet深さ50 / 100 / 150: 浮動小数点 76.4% / 78.0% / 78.8%、整数量子化 74.9% / 76.6% / 76.7%（本文テキストで確認）。
- 一言の要約: 整数量子化したResNetは、深さ50・100・150のいずれでも浮動小数点より1.5ポイント前後（50: 1.5、100: 1.4、150: 2.1）低い。※差は上記の表の値から単純に引いた計算。

---

## 2. 白書 Nagel [Nagel+, arXiv2021]

A White Paper on Neural Network Quantization（arXiv:2106.08295v1。PDFページ＝論文内ページ。「Confidential and Proprietary — Qualcomm」のフッタが各ページにある）

### 2-1. 一様アフィン量子化の定義（§2.2、式(4)〜(7)、PDF p4）

- 原文: "Uniform affine quantization, also known as asymmetric quantization, is defined by three quantization parameters: the scale factor s, the zero-point z and the bit-width b."
- 原文: "The zero-point is an integer that ensures that real zero is quantized without error. This is important to ensure that common operations like zero padding or ReLU do not induce quantization error."
- 式(4): x_int = clamp(⌊x/s⌉ + z; 0, 2^b − 1)（⌊·⌉はround-to-nearest）。式(5): clampの定義。式(6): x ≈ x̂ = s(x_int − z)。式(7): x̂ = q(x; s, z, b) = s[clamp(⌊x/s⌉ + z; 0, 2^b − 1) − z]。
- 量子化グリッドの限界: q_min = −sz、q_max = s(2^b − 1 − z)。
- 一言の要約: 実数をscale・zero-point・ビット幅で整数グリッド{0, …, 2^b − 1}に写し（round→zero-point加算→clamp）、s(x_int − z)で戻す。

### 2-2. 丸め誤差とクリップ誤差のトレードオフ（§2.2、PDF p4）

- 原文: "Any values of x that lie outside this range will be clipped to its limits, incurring a clipping error. If we want to reduce the clipping error we can expand the quantization range by increasing the scale factor. However, increasing the scale factor leads to increased rounding error as the rounding error lies in the range [−s/2, s/2]."（原文は区間を式で表記）
- 一言の要約: 範囲を広げるとクリップ誤差が減るが、scaleが増えて丸め誤差（範囲は±s/2）が増える。最適な折り合いは§3.1で扱う。

### 2-3. 対称量子化と符号（§2.2.1、式(8a)〜(8c)、図3、PDF p4〜p5）

- 原文: "The symmetric quantizer restricts the zero-point to 0. This reduces the computational overhead of dealing with zero-point offset during the accumulation operation in equation (3). But the lack of offset restricts the mapping between integer and floating-point domain."
- 式(8a)〜(8c): x̂ = s·x_int。符号なしは x_int = clamp(⌊x/s⌉; 0, 2^b − 1)、符号付きは clamp(⌊x/s⌉; −2^(b−1), 2^(b−1) − 1)。
- 原文: "Unsigned symmetric quantization is well suited for one-tailed distributions, such as ReLU activations (see figure 3). On the other hand, signed symmetric quantization can be chosen for distributions that are roughly symmetric about zero."
- 図3（PDF p5）: bit幅8の対称（符号付き・符号なし）と非対称のグリッドの図。
- 一言の要約: 対称はzero-pointを0に固定する簡略版。符号付きと符号なしで整数グリッドの範囲が変わる。

### 2-4. 対称 vs 非対称の実用上の違い（§2.4.1、式(13)、PDF p8）

- 原文: "asymmetric quantization is more expressive because there is an extra offset parameter, but on the other hand there is a possible computational overhead."
- 式(13)の展開で、重みと活性がともに非対称のとき、x_intに依存する項（第2項 −s_w z_w s_x x_int）が入力データごとに追加計算になる。
- 原文: "For this reason, it is a common approach to use asymmetric activation quantization and symmetric weight quantization that avoids the additional data-dependent term."
- 一言の要約: 非対称は表現力が高いが追加の計算が要る。重みを対称、活性を非対称にするのが一般的な選択。

### 2-5. 粒度: per-tensor / per-channel / グループ（§2.2.3、§2.4.2、PDF p5・p8）

- 原文（§2.2.3）: "So far, we have defined a single set of quantization parameters (quantizer) per tensor, one for the weights and one for activations, as seen in equation (3). This is called per-tensor quantization."
- 原文（§2.2.3）: "For example, for weight tensors, we can specify a different quantizer per output channel. This is known as per-channel quantization"
- 原文（§2.2.3、グループ）: "Increasing the granularity of the groups generally improves accuracy at the cost of some extra overhead." 本白書は、既存の固定小数点アクセラレータが未対応のためグループ量子化を扱わない、と述べている。
- 原文（§2.4.2）: "per-channel quantization of the weights can improve accuracy, especially when the distribution of weights varies significantly from channel to channel."
- 原文（§2.4.2）: "Per-channel quantization of activations is much harder to implement because we cannot factor the scale factor out of the summation and would, therefore, require rescaling the accumulator for each input channel."
- 一言の要約: 標準はper-tensor。重みはper-channel（出力チャネル軸）にすると精度が上がりうる。活性のper-channelはハードウェア実装が難しい。groupは精度が上がるがオーバーヘッドがあり、本白書の範囲外。

### 2-6. 量子化シミュレーション（fake quantization）とBN folding（§2.3、§2.3.1、図4、式(9)〜(12)、PDF p5〜p7）

- 原文（§2.3）: "we often simulate the quantized behavior on the same general purpose hardware we use for training neural networks."
- 原文（§2.3）: "Both the input and output of the quantizer are in floating-point format but the output lies on the quantization grid."
- 原文（§2.3）: "Quantizer blocks are added in between the weights and the convolution to simulate weight quantization, and after the activation function to simulate activation quantization. The bias is often not quantized because it is stored in higher-precision."
- 原文（§2.3.1）: "For on-device inference, these operations are folded into the previous or next linear layers in a step called batch normalization folding (Krishnamoorthi, 2018; Jacob et al., 2018)."
- 式(9): BatchNorm(x) = γ((x − μ)/sqrt(σ² + ε)) + β。式(10): 書き換えの式。式(11)(12): 重みW̃_k,: = γ_k W_k,: / sqrt(σ²_k + ε)、バイアス b̃_k = β_k − γ_k μ_k / sqrt(σ²_k + ε)。
- 一言の要約: 浮動小数点上に量子化器を挟んで量子化の効果だけを模擬できる（出力はグリッド上の値だがfloat）。BNは前後の線形層に畳み込み、BN単体の演算と出力の量子化をなくす。

### 2-7. PTQの範囲設定（較正）: min-max・MSE・cross entropy・BN based（§3.1、式(14)〜(19)、Table 1・2、PDF p9〜p10）

- 原文: "The key trade-off in range setting is between clipping and rounding error, described in section 2.2"
- 原文（§3.1）: "Weights can usually be quantized without any need for calibration data. However, determining parameters for activation quantization often requires a few batches of calibration data."
- min-max（式(14)(15)）: q_min = min V、q_max = max V。原文: "This leads to no clipping error. However, this approach is sensitive to outliers as strong outliers may cause excessive rounding errors."
- MSE（式(16)）: V̂(q_min, q_max)とVのFrobenius norm²を最小化するq_min, q_maxを探す。原文: "The optimization problem is commonly solved using grid search, golden section method or analytical approximations with closed-form solution (Banner et al., 2019)."
- cross entropy（式(17)）: 最終層のlogitsで、大きな値の順序を保つことが重要なため使う。
- BN based（式(18)(19)）: q_min = min(β − αγ)、q_max = max(β + αγ)。原文: "Nagel et al. (2019) uses α = 6 so that only large outliers are clipped."
- 重みの比較（Table 1、PDF p9、ImageNet検証精度、5回平均、活性はFP32、対称一様）:
  - ResNet18（FP32 69.68）W8 / W6 / W4: Min-Max 69.57 / 63.90 / 0.12、MSE 69.45 / 64.64 / 18.82、Min-Max(Per-channel) 69.60 / 69.08 / 44.49、MSE(Per-channel) 69.66 / 69.24 / 54.67。
  - MobileNetV2（FP32 71.72）W8 / W6 / W4: Min-Max 71.16 / 64.48 / 0.59、MSE 71.15 / 65.43 / 13.77、Min-Max(Per-channel) 71.21 / 68.52 / 18.40、MSE(Per-channel) 71.46 / 68.89 / 27.17。
- 活性の比較（Table 2、PDF p10、重みはFP32、非対称一様）: ResNet18 A8 / A6 / A4は Min-Max 69.60 / 68.19 / 18.82、MSE 69.59 / 67.84 / 31.40、MSE + Xent 69.60 / 68.91 / 59.07、BN(α = 6) 69.54 / 68.73 / 23.83。MobileNetV2 A8 / A6 / A4は Min-Max 70.96 / 64.58 / 0.53、MSE 71.35 / 67.55 / 13.57、MSE + Xent 71.36 / 68.85 / 30.94、BN(α = 6) 71.32 / 65.20 / 0.66。
- 原文（比較、PDF p10）: "For high bit-widths, the MSE and min-max approaches are mostly on par. However, at lower bit-widths the MSE approach clearly outperforms the min-max."
- 注意: percentile較正はこの白書のテキストに見当たらない（"percentile"の検索で未確認。§3.1の手法は min-max / MSE / cross entropy / BN based の4つ）。percentileをスライドで原典由来とするなら別の原典が要る。
- 一言の要約: 範囲設定は丸めとクリップの折り合いを決める作業。min-maxは外れ値に弱く、MSEは低ビットで有利。重みはキャリブレーションデータ不要、活性は数バッチが要る。

### 2-8. 標準のPTQパイプライン（§3.5、図8、PDF p16）と代表結果（Table 6、PDF p17）

- 推奨の選択（原文）: "for common AI accelerators we recommend using symmetric quantizers for the weights and asymmetric quantizers for the activations. If supported by the HW/SW stack then it is favorable to use per-channel quantization for weights."
- 手順（図8）: 学習済みFPモデル → CLE → 量子化器の追加 → 重みの範囲設定（MSE）→ （データがあれば）Bias correctionまたはAdaRound → 活性の範囲設定（MSE）。
- 抜粋（Table 6、5回平均、標準PTQパイプライン、ImageNet精度）: ResNet18（FP32 69.68）W8A8 / W4A8 は per-tensor 69.60 / 68.62、per-channel 69.56 / 68.91。MobileNetV2（FP32 71.72）は per-tensor 70.99 / 69.21、per-channel 71.16 / 69.79。EfficientNet liteは per-tensor W4A8 71.24（FP32 75.42）、per-channel 74.01。
- 原文（Table 6の考察、PDF p17、depth-wise separable畳み込みのモデルでのper-channelの効果）: "in EfficientNet lite per-channel quantization increases the accuracy by 2.8% compared to per-tensor quantization"
- 一言の要約: 標準PTQは重みW8A8でほぼFP32並み。W4A8では、depth-wise separable畳み込みのモデルでper-channelの効果が大きい。

### 2-9. QAT: STE、手順（§4、§4.1、式(36)、§4.4、PDF p19、p23）

- 原文（§4）: "However, they have limitations, especially when aiming for low-bit quantization of activations, such as 4-bit and below."（PTQについての記述）
- 原文（§4）: "QAT models the quantization noise source (see section 2.3) during training. This allows the model to find more optimal solutions than post-training quantization. However, the higher accuracy comes with the usual costs of neural network training, i.e., longer training times, need for labeled data and hyper-parameter search."
- 原文（§4.1）: "the gradient of the round-to-nearest operation in equation (4) is either zero or undefined everywhere, which makes gradient-based training impossible."
- 原文（§4.1）: "A way around this would be to approximate the gradient using the straight-through estimator (STE, Bengio et al. 2013), which approximates the gradient of the rounding operator as 1"。式(36): ∂⌊y⌉/∂y = 1。
- 標準QATパイプライン（§4.4、図12、PDF p23〜p24）: 学習済みFPモデルから始め、CLE → 量子化器の追加（重み対称・活性非対称）→ 範囲推定（層ごとのMSE）→ 量子化パラメータを学習可能にして学習。原文: "As discussed in previous sections, we always start from a pre-trained model and follow some PTQ steps in order to have faster convergence and higher accuracy."
- 一言の要約: round勾配は0または未定義なので、STEで丸めの勾配を1とみなして逆伝播する。QATは低ビット（特に活性4bit以下）で有利だが、学習時間・ラベル付きデータ・ハイパーパラメータ探索のコストがかかる。

### 2-10. 8bit PTQは多くの場合で十分（Abstract、PDF p1）

- 原文: "In most cases, PTQ is sufficient for achieving 8-bit quantization with close to floating-point accuracy. QAT requires fine-tuning and access to labeled training data but enables lower bit quantization with competitive results."
- 一言の要約: 8bitはPTQで足りることが多く、より低ビットではQATが競争力のある結果を出す。

---

## 3. 白書 Krishnamoorthi [Krishnamoorthi, arXiv2018]

Quantizing deep convolutional networks for efficient inference: A whitepaper（arXiv:1806.08342v1。PDFページ＝論文内ページ）

### 3-1. 量子化の動機（§1、PDF p4）

- 原文: "Smaller Model footprint: With 8-bit quantization, one can reduce the model size a factor of 4, with negligible accuracy loss. This can be done without needing any data as only the weights are quantized."
- 原文: "Lower Power: Moving 8-bit data is 4 times more efficient than moving 32-bit floating point data."
- 原文: "All the factors above translate into faster inference, with a typical speedup of 2-3x due to the reduced precision for both memory accesses and computations."
- 一言の要約: 8bit化でモデルサイズが4分の1、データ移動のエネルギーが32bit浮動小数点の4倍効率、典型的に2〜3倍の高速化と述べている（いずれも本論文の記述）。

### 3-2. 一様アフィン量子化器（§2.1、PDF p4）

- 原文: "We derive two parameters: Scale (∆) and Zero-point(z) which map the floating point values to integers"。範囲は (0, N_levels − 1)、8bitでN_levels = 256。
- 原文: "Zero-point is an integer, ensuring that zero is quantized with no error. This is important to ensure that common operations like zero padding do not cause quantization error."
- 原文: "For one sided distributions, therefore, the range (xmin, xmax) is relaxed to include zero."
- 式の番号は未確認（§2.1の式は本ノートでは抽出していない）。
- 一言の要約: scaleはステップ幅、zero-pointは実数0に対応する整数。片側分布では範囲を0を含むように広げる。

### 3-3. 量子化パラメータの決め方（§2.5、PDF p8）

- 原文: "For weights, we use the actual minimum and maximum values to determine the quantizer parameters. For activations, we use the moving average of the minimum and maximum values across batches to determine the quantizer parameters."
- TensorRTは「step sizeを決めるために元の分布と量子化後の分布のKL divergenceを最小化する」と記述（"TensorRT [11] minimizes the KL divergence between the original and quantized distributions to determine the step size"）。
- §3.1.2（PDF p10）: 原文 "Typically, about 100 mini-batches are sufficient for the estimates of the ranges of the activation to converge."
- 一言の要約: 重みはmin-max、活性はバッチごとのmin/maxの移動平均。活性の範囲推定にはキャリブレーションデータ（約100ミニバッチ）が要る。

### 3-4. 粒度: per-layer と per-channel（§2.6、PDF p8）

- 原文: "We can specify a single quantizer (defined by the scale and zero-point) for an entire tensor, referred to as per-layer quantization."
- 原文: "per-channel quantization has a different scale and offset for each convolutional kernel. We do not consider per-channel quantization for activations as this would complicate the inner product computations at the core of conv and matmul operations."
- 一言の要約: 重みは畳み込みカーネル（出力チャネル）ごとにscale・offsetを持つper-channelにでき、活性はper-layerのみ扱う。

### 3-5. per-channelの効果（§3.1.3、Table 2・3、観察1〜5、PDF p10〜p13）

- 原文（§3.1.3、重みのみ、PDF p10〜p11）: "From figure 2, we note that per-channel quantization is required to ensure that the accuracy drop due to quantization is small"（図2への言及は原文のまま。続きは "with asymmetric, per-layer quantization providing the best accuracy." と読めるが、Table 2では Asymmetric, per-layer が Mobilenetv1で0.001であり、この文は表の数値と食い違って見える。引用には使わず、表の数値を使う）。
- Table 2（重みのみ8bit、ImageNet top-1、列: Asymmetric per-layer / Symmetric per-channel / Asymmetric per-channel / Floating Point、PDF p11）:
  - Mobilenetv1 1 224: 0.001 / 0.591 / 0.704 / 0.709
  - Mobilenetv2 1 224: 0.001 / 0.698 / 0.698 / 0.719
  - Resnet v1 50: 0.75 / 0.751 / 0.752 / 0.752
  - Inceptionv3: 0.78 / 0.78 / 0.78 / 0.78
- Table 3（重みと活性とも8bit、活性はper-layer、PDF p11）: Mobilenet-v1 1 224は 0.001 / 0.591 / 0.703 / 活性のみ 0.708 / Floating 0.709。Resnet-v1 50は 0.75 / 0.751 / 0.751 / 0.751 / 0.752。
- 原文（観察、PDF p13）: "Weight quantization at the granularity of a layer causes large accuracy drops primarily due to batch normalization, which causes extreme variation in dynamic range across convolution kernels in a single layer."
- 原文（観察、PDF p13）: "Per-channel quantization side-steps this problem by quantizing at the granularity of a kernel, which makes the accuracy of per-channel quantization independent of the batch-norm scaling."
- 原文（観察5、PDF p13）: "Almost all the accuracy loss due to quantization is due to weight quantization."
- 原文（観察2、PDF p13）: "Activations can be quantized to 8-bits with almost no loss in accuracy."（理由として、BN with no scaling（Inception-V3）とReLU6（Mobilenet-V1）で活性の動的範囲が小さいことを挙げている）
- 原文（Abstract項目1、PDF p3）: "Per-channel quantization of weights and per-layer quantization of activations to 8-bits of precision post-training produces classification accuracies within 2% of floating point networks for a wide variety of CNN architectures"
- 一言の要約: BNで畳み込みカーネル間の重みの範囲が大きく違うと、per-layerの重み量子化は大きく崩れる（Mobilenetで顕著）。per-channelはBNの影響を受けずにFP32近くを保つ。8bit活性は、ここで調べたモデルでは損失がほぼない。

### 3-4b. 注意（原典の読み方）

- §3.1.3の注記: "Note that all results are obtained using simulated quantization of weights and activations."（実測の高速化ではなく、シミュレーション上の精度。PDF p10）

### 3-6. QATの推奨と効果（§3.2、§3.2.3〜3.2.4、§8、Table 4〜6、PDF p13、p20〜p23、p30）

- 原文（§3.2、PDF p13）: "Quantization aware training models quantization during training and can provide higher accuracies than post quantization training schemes."
- 原文（§3.2、PDF p13）: "For the backward pass, we use the straight through estimator (see section 2.4) to model quantization. ... However, we maintain weights in floating point and update them with the gradient updates."
- 原文（§3.2.3、PDF p20）: "Training closes the gap between symmetric and asymmetric quantization." / "Training allows for simpler quantization schemes to provide close to floating point accuracy. Even per-layer quantization shows close to floating point accuracy"
- 原文（§3.2.4、PDF p22）: "At four bits, the benefits of per-channel quantization are apparent, even for post training quantization" / "for most networks, one can obtain accuracies within 5% of 8-bit quantization with fine tuning 4 bit weights" / "The losses due to activation quantization are more severe than that of weight quantization (see Table 6)."
- 原文（§8、PDF p30）: "Use symmetric-per-channel quantization of weights with post training quantization as a starting point. Optionally fine tune if there is an accuracy drop." / "Quantization aware training can narrow the gap to floating point accuracy and in our experiments, reduce the gap to within 5% of 8-bit quantized weights, even when all layers are quantized to 4 bits of precision."
- 原文（Abstract項目4、PDF p3）: "Quantization-aware training can provide further improvements, reducing the gap to floating point to 1% at 8-bit precision. Quantization-aware training also allows for reducing the precision of weights to four bits with accuracy losses ranging from 2% to 10%, with higher accuracy drop for smaller networks (section 3.2)."
- 原文（Abstract項目7、PDF p3）: "We recommend that per-channel quantization of weights and per-layer quantization of activations be the preferred quantization scheme for hardware acceleration and kernel optimization."
- 一言の要約: まず重みper-channelのPTQから始め、精度が落ちるなら微調整・QAT。QATは8bitでFP32との差を1%に縮め、4bit重みでも許容できる精度に近づける。活性の4bit化は重みの4bit化より損失が大きい。

---

## 4. STE [Bengio+, arXiv2013]

Estimating or Propagating Gradients Through Stochastic Neurons for Conditional Computation（arXiv:1308.3432v1。12ページ）

### 4-1. Straight-Through Estimatorの定義（§4、式(13)、PDF p7）

- 原文: "The idea is simply to back-propagate through the hard threshold function (1 if the argument is positive, 0 otherwise) as if it had been the identity function."
- 原文: "It is clearly a biased estimator, but when considering a single layer of neurons, it has the right sign (this is not guaranteed anymore when back-propagating through more hidden layers). We call it the straight-through (ST) estimator."
- 式(13): g_i = ∂L/∂h_i（ストキャスティックなバイナリ出力h_iに対する勾配を、そのままシグモイド引数a_iに対する勾配の推定量として使う）。
- 原文: "Better results were actually obtained without multiplying by the derivative of the sigmoid."（シグモイドの微分を掛ける変種を試し、掛けない方が良かったという記述）
- 一言の要約: 微分できない硬い閾値関数を、逆伝播ではidentity（恒等関数）とみなして勾配をそのまま通す。偏りのある推定量だが、1層なら符号は正しい。
- 注意: この論文の対象は確率的バイナリニューロン（条件付き計算）であり、量子化（round関数）は扱っていない。STEを量子化のroundに当てはめる式（∂⌊y⌉/∂y = 1）は、Nagel白書§4.1（式(36)）がBengio et al. 2013を引いて述べている（本ノート §2-9）。スライドでは「STEの原典はBengio、量子化での使い方は白書・LSQ」と書き分ける（Jacobの本文にSTEの語はない．2026-11-14の検査①で確認）。

### 4-2. Abstractでの位置づけ（PDF p1）

- 原文: "A fourth approach heuristically copies the gradient with respect to the stochastic output directly as an estimator of the gradient with respect to the sigmoid argument (we call this the straight-through estimator)."
- 一言の要約: 4つの推定法の1つで、確率的出力に対する勾配を、シグモイド引数に対する勾配の推定量として「ヒューリスティックに」そのままコピーする方法。

### 4-3. 実験での性能（§6 Conclusion、PDF p9）

- 原文: "Another surprise is the good performance of the straight-through units, which provided the best validation and test error, and are very simple to implement."
- 一言の要約: MNISTの条件付き計算の実験で、ST unitsが最良のvalidation・test誤差を示した（数値は未確認、図2・表は未抽出）。

---

## 5. LLM.int8() [Dettmers+, NeurIPS2022]

LLM.int8(): 8-bit Matrix Multiplication for Transformers at Scale（NeurIPS 2022。PDFページ＝論文内ページ）

### 5-1. 外れ値特徴（emergent outlier features）（§1、§4、Figure 1・3・4、PDF p2、p6〜p8）

- 原文（§1、PDF p2）: "the need to explicitly represent the sparse but systematic large magnitude outlier features that ruin quantization precision once they emerge in all transformer layers starting at scales of 6.7B parameters."
- 原文（§1、PDF p2）: "large features with magnitudes up to 20x larger than in other dimensions first appear in about 25% of all transformer layers and then gradually spread to other layers as we scale transformers to 6B parameters. At around 6.7B parameters, a phase shift occurs, and all transformer layers and 75% of all sequence dimensions are affected by extreme magnitude features."
- 原文（§1、PDF p2）: "These outliers are highly systematic: at the 6.7B scale, 150,000 outliers occur per sequence, but they are concentrated in only 6 feature dimensions across the entire transformer."
- 原文（§1、PDF p2）: "Setting these outlier feature dimensions to zero decreases top-1 attention softmax probability mass by more than 20% and degrades validation perplexity by 600-1000% despite them only making up about 0.1% of all input features. In contrast, removing the same amount of random features decreases the probability by a maximum of 0.3% and degrades perplexity by about 0.1%."
- 外れ値の定義（§4.1、PDF p6）: "the magnitude of the feature is at least 6.0, affects at least 25% of layers, and affects at least 6% of the sequence dimensions."
- 注意: 対象はLLM（OPT・fairseq系のdense autoregressive transformer、125M〜175B）。ViTの外れ値ではない。
- 一言の要約: 約6.7Bパラメータ以降、ごく少数（約0.1%）の特徴次元が大きな値（最大で他の20倍規模）を全層に系統的に持ち、これを消すと性能が壊れるので、通常の8bit量子化は精度を保てなくなる。

### 5-2. 混合精度分解（mixed-precision decomposition）（§3.2、式(8)、Figure 2、PDF p3、p5）

- 原文（§3、PDF p4）: "we develop mixed-precision decomposition, where the small number of large magnitude feature dimensions (≈0.1%) are represented in 16-bit precision while the other 99.9% of values are multiplied in 8-bit."
- 式(8)（PDF p5）: C_f16 ≈ Σ_{h∈O} X^h_f16 W^h_f16 + S_f16 · Σ_{h∉O} X^h_i8 W^h_i8。Oは、閾値αより大きい外れ値を1つ以上含む特徴次元の集合。
- 原文（§3.2、PDF p5）: "In our work, we find that α = 6.0 is sufficient to reduce transformer performance degradation close to zero."
- 原文（§3.2、PDF p5）: "Since the number of outlier feature dimensions is not larger than 7 (|O| ≤ 7) for transformers up to 13B parameters, this decomposition operation only consumes about 0.1% additional memory."
- 原文（§3、PDF p4）: "Since most entries are still represented in low-precision, we retain about 50% memory reduction compared to 16-bit. For example, for BLOOM-176B, we reduce the memory footprint of the model by 1.96x."
- 一言の要約: 外れ値の特徴次元だけ16bitで、残り約99.9%は8bitで行列積し、結果を足し合わせる。メモリは約半分に減る。

### 5-3. vector-wise量子化（§3.1、式(6)、PDF p4）

- 原文（§3、PDF p4）: "The main challenge with quantization methods that use a single scaling constant per tensor is that a single outlier can reduce the quantization precision of all other values."
- 原文（§3.1、PDF p4）: "we can assign a different scaling constant c_x to each row of X_f16 and c_w to each column of W_f16. To dequantize, we denormalize each inner product result by 1/(c_x c_w)."
- 一言の要約: 行列積を内積の列とみなし、入力は行ごと・重みは列ごとにscaleを持つ。per-tensorでは1つの外れ値が全要素の精度を下げる。ただしvector-wiseだけでは6.7B超の外れ値を扱えない（原文 "vector-wise quantization is no longer sufficient"、§3、PDF p4）。

### 5-4. 結果（§3.4、Table 1、Figure 1、PDF p2、p6）

- Table 1（C4 validation perplexity、125M / 1.3B / 2.7B / 6.7B / 13B、PDF p6）: 32-bit Float 25.65 / 15.91 / 14.43 / 13.30 / 12.45。Int8 absmax 87.76 / 16.55 / 15.11 / 14.59 / 19.08。Int8 zeropoint 56.66 / 16.24 / 14.76 / 13.49 / 13.94。Int8 absmax vector-wise 35.84 / 16.82 / 14.98 / 14.13 / 16.48。Absmax LLM.int8()（vector-wise + decomp）25.83 / 15.93 / 14.44 / 13.24 / 12.45。
- 原文（§3.4、PDF p5）: "Our method, LLM.int8(), is the only method that preserves perplexity."
- 原文（§3.4、PDF p6）: "LLM.int8() maintains full 16-bit performance as we scale from 125M to 175B parameters. On the other hand, the baseline, 8-bit absmax vector-wise quantization, scales poorly and degenerates into random performance."
- 速度（§3.4、PDF p6）: 原文 "The quantization overhead can slow inference for models with less than 6.7B parameters, as compared to a FP16 baseline." / "LLM.int8() run times is about two times faster for large matrix multiplications equivalent to those in 175B models."
- 一言の要約: 外れ値が出現する6.7B以降で、通常のInt8量子化は精度が悪化（13Bのperplexity 19.08、FP32は12.45）するが、LLM.int8()は12.45でFP32と同じ。小さいモデルでは量子化のオーバーヘッドで遅くなりうる。

---

## 6. SmoothQuant [Xiao+, ICML2023]

SmoothQuant: Accurate and Efficient Post-Training Quantization for Large Language Models（ICML 2023, PMLR 202。PDFページ＝論文内ページ）

### 6-1. 活性は重みより量子化しにくい・外れ値のチャネル（§3、Table 1、Figure 4、PDF p3〜p4）

- 原文（§3 観察1、PDF p3）: "Activations are harder to quantize than weights. The weight distribution is quite uniform and flat, which is easy to quantize."
- 原文（§3 観察2、PDF p3）: "The scale of outliers in activations is ∼ 100× larger than most of the activation values." 有効な量子化水準は 2^8 · m_i/m（m_iはチャネルiの最大値、mは行列全体の最大値）で、非外れ値チャネルでは "the effective quantization levels would be very small (2-3), leading to large quantization errors."
- 原文（§3 観察3、PDF p3）: "Outliers persist in fixed channels. Outliers appear in a small fraction of the channels. If one channel has an outlier, it persistently appears in all tokens"
- Table 1（OPT 6.7B / 13B / 30B / 66B / 175B、4タスク平均、PDF p3）: FP16 64.9% / 65.6% / 67.9% / 69.5% / 71.6%、INT8 per-tensor 39.9% / 33.0% / 32.8% / 33.1% / 32.3%、INT8 per-token 42.5% / 33.0% / 33.1% / 32.9% / 31.7%、INT8 per-channel 64.8% / 65.6% / 68.0% / 69.4% / 71.4%。per-channelは「INT8 GEMM kernelsと両立しない」（表の注記）。
- 原文（§3、PDF p3）: "However, per-channel activation quantization does not map well to hardware-accelerated GEMM kernels" 。カーネルでスケーリングできるのは行列積の外側の次元（トークン次元T、出力チャネル次元C_o）のみ。式(2): Y = diag(Δ_X) · (X̄_INT8 · W̄_INT8) · diag(Δ_W)。
- 一言の要約: 活性は重みより量子化しにくい。外れ値は固定のチャネルに現れ（全トークンで大きい）、per-channelの活性量子化なら精度が保てるが、INT8 GEMMカーネルでは使えない。

### 6-2. 平滑化係数 s_j と α（§4、式(3)・(4)、Figure 2・5、PDF p3〜p4）

- 原文（§4、PDF p3）: "we propose to “smooth” the input activation by dividing it by a per-channel smoothing factor s ∈ R^Ci. To keep the mathematical equivalence of a linear layer, we scale the weights accordingly in the reversed direction:" 式(3): Y = (X diag(s)^−1) · (diag(s) W) = X̂ Ŵ。
- 原文（§4、PDF p4）: "a straight-forward choice is s_j = max(|X_j|), j = 1, 2, ..., C_i" だが "this formula pushes all the quantization difficulties to the weights." 逆の s_j = 1/max(|W_j|) は活性側に難しさが残る。
- 式(4): **s_j = max(|X_j|)^α / max(|W_j|)^(1−α)**（j は入力チャネル）。原文: "Here we introduce a hyper-parameter, migration strength α, to control how much difficulty we want to migrate from activation to weights"
- 原文（§4、PDF p4）: "α = 0.5 is a well-balanced point to evenly split the quantization difficulty, especially when we are using the same quantizer for weights and activations (e.g., per-tensor, static quantization)." 外れ値が多いGLM-130B（約30%が外れ値）では "we can choose a larger α ... (like 0.75)"。
- 平滑化係数は較正サンプルで求め、変換はオフラインで行う（Figure 5の説明: "The smoothing factor s is obtained on calibration samples and the entire transformation is performed offline. At runtime, the activations are smooth without scaling."）。smoothing factorは前の層のパラメータ（LayerNormなど）に融合できる（§4、PDF p3〜p4）。
- αの感度（§5.5 Ablation、Figure 10、PDF p8〜p9）: 原文 "When α is too small (<0.4), the activations are hard to quantize; when α is too large (>0.6), the weights will be hard to quantize."（OPT-175B・LAMBADAの場合）
- 一言の要約: 活性のチャネルを s_j で割り、重みの対応する入力チャネルに s_j を掛けて、数学的に等価なまま量子化の難しさを活性から重みへ移す。αが移す量を決める（0.5が基本、外れ値の多いモデルは大きく）。

### 6-3. W8A8の代表結果（§5.2、Table 2〜4、Figure 7、PDF p5〜p6）

- 設定（Table 2、PDF p5）: W8A8は重みper-tensor・活性per-tensor dynamic。LLM.int8()は重みper-channel・活性per-token dynamic+FP16。SmoothQuant-O1は重みper-tensor・活性per-token dynamic、O2は活性per-tensor dynamic、O3は活性per-tensor static。
- Table 3（OPT-175B、7ゼロショットタスクの平均 / WikiText perplexity、PDF p6）: FP16 66.9% / 10.99、W8A8 35.5% / 93080、ZeroQuant 35.8% / 84648、LLM.int8() 66.7% / 11.10、Outlier Suppression 36.0% / 96151、SmoothQuant-O1 66.5% / 11.11、O2 66.4% / 11.14、O3 66.8% / 11.17。
- Table 4（OPT-175B / BLOOM-176B / GLM-130B、PDF p6）: FP16 71.6% / 68.2% / 73.8%、W8A8 32.3% / 64.2% / 26.9%、LLM.int8() 71.4% / 68.0% / 73.8%、SmoothQuant-O1 71.2% / 68.3% / 73.7%、O3 71.1% / 67.4% / 72.8%（GLM-130Bは別のタスク構成のため、列間の比較は不可と注記あり）。
- 原文（§5.2、PDF p6）: "The W8A8, ZeroQuant, and Outlier Suppression baselines produce nearly random results, indicating that naively quantizing the activation of LLMs will destroy the performance."
- 一言の要約: OPT-175Bで、素朴なW8A8は平均35.5%・perplexity 93080に崩れるが、SmoothQuantは3つの効率レベル（O1〜O3）すべてでFP16（66.9%）に近い66.4〜66.8%を保つ。

### 6-4. 速度・メモリ（§5.3〜5.4、Figure 9、Table 8・9、Abstract、PDF p1、p8、p9）

- 原文（Abstract、PDF p1）: "We demonstrate up to 1.56× speedup and 2× memory reduction for LLMs with negligible loss in accuracy."
- 原文（Figure 9の説明、PDF p8）: "For smaller models, the latency can be significantly reduced with SmoothQuant-O3 by up to 1.56x compared to FP16. ... Memory footprint is almost halved compared to FP16."
- 原文（§1、PDF p2）: PyTorch実装で "up to 1.51× speed up and 1.96× memory saving"。
- 原文（§1、PDF p2、LLM.int8()への言及）: "However, it is hard to implement the decomposition efficiently on hardware accelerators." とmixed-precision decompositionの実装の難しさを指摘。
- 注意: これらはA100・FasterTransformer等での値で、本環境（CPU）の実測ではない。スライドでは「原典由来」と明記する。
- 一言の要約: INT8の行列積をすべての線形層とattentionのBMMに使い、最大1.56倍の高速化と約半分のメモリ。530Bモデルを1ノード（8×A100 80GB）で動かせる。

---

## 7. GPTQ [Frantar+, ICLR2023]

GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers（ICLR 2023、arXiv:2210.17323v2。PDFページ＝論文内ページ）

### 7-1. 何をする手法か（Abstract、§3、式(1)、PDF p1、p3）

- 原文（Abstract）: "propose GPTQ, a new one-shot weight quantization method based on approximate second-order information, that is both highly-accurate and highly-efficient."
- 原文（Abstract）: "GPTQ can quantize GPT models with 175 billion parameters in approximately four GPU hours, reducing the bitwidth down to 3 or 4 bits per weight, with negligible accuracy degradation relative to the uncompressed baseline."
- 層ごとの再構成問題（§3 Layer-Wise Quantization、式(1)）: 線形層の重みW、入力Xに対し、argmin_Ŵ ||WX − ŴX||²₂ を解く。原文: "the objective is to find a matrix of quantized weights Ŵ which minimizes the squared error, relative to the full precision layer output." 量子化グリッドは事前に固定し、個々の重みは自由に動かせる。
- 一言の要約: 重みだけを対象に、層ごとの出力誤差（式(1)）を2次情報（ヘッセ行列）を使って最小化する、一括（one-shot）の事後量子化。

### 7-2. アルゴリズムの3つの工夫（§4、式(2)〜(5)、Algorithm 1、Figure 2、PDF p4〜p5）

- 前提のOBQ（§3、式(2)(3)）: 重みを1つずつ量子化し、誤差を補うよう残りの重みを更新する。原文: "OBQ's runtime for a d_row × d_col matrix W has cubic input dependency O(d_row · d_col³)"
- Step 1 Arbitrary Order Insight（PDF p4）: 原文 "its improvement over quantizing the weights in arbitrary order is generally small, in particular on large, heavily-parametrized layers." 全行で同じ列順に量子化し、実行時間をO(d_row · d_col³)からO(max{d_row · d_col², d_col³})に下げる。
- Step 2 Lazy Batch-Updates（PDF p4〜p5）: 原文 "we apply the algorithm to B = 128 columns at a time" 。メモリ帯域がボトルネックになるため、ブロック単位で更新をまとめる（式(4)(5)）。
- Step 3 Cholesky Reformulation（PDF p5）: 数値誤差でH⁻¹が不定になる問題への対策。原文: "adding a small constant λ (we always choose 1% of the average diagonal value) to the diagonal elements of H" の dampening と、Cholesky分解の併用。
- Algorithm 1（PDF p5）: "Quantize W given inverse Hessian H⁻¹ = (2XXᵀ + λI)⁻¹ and blocksize B."
- 一言の要約: 重みを列ごとに量子化し、その誤差を未量子化の重みへヘッセ行列の逆行列で配分する（OBQの高速・安定版）。丸めの最適化には勾配降下（SGD）を使わない。

### 7-3. 結果（§5、Table 1・3・5・6、PDF p7〜p8）

- 実行時間（Table 2、PDF p7）: OPT 13B / 30B / 66B / 175B = 20.9分 / 44.9分 / 1.6時間 / 4.2時間。BLOOM-176B = 3.8時間。
- OPT WikiText2 perplexity（Table 3、PDF p7）: OPT-175B は 16bit 8.34、RTN 4bit 10.54、GPTQ 4bit 8.37、RTN 3bit 7.3e3、GPTQ 3bit 8.68。OPT-13B は 16bit 10.13、RTN 4bit 11.32、GPTQ 4bit 10.31。
- 原文（§5、PDF p7）: "GPTQ loses only 0.03 perplexity at 4-bit on the 175B model, while RTN drops 2.2 points, performing worse than the 10× smaller full-precision 13B model. At 3-bit, RTN collapses completely, while GPTQ can still maintain reasonable perplexity"
- グループ化（§5、Table 5、PDF p7〜p8）: 原文 "group-size 1024 (≈ 0.02 extra bits) improves perplexities by about 0.2 on average and group-size 128 (≈ 0.15 extra bits) by another 0.1" 。OPT-175B Wiki2は GPTQ 3bit 8.68、3/g1024 8.45、3/g128 8.45。
- 視覚モデルとの比較（Table 1、PDF p7、ResNet18 FP 69.76% / ResNet50 FP 76.13%）: ResNet18 4bit / 3bit は AdaRound 69.34 / 68.37、BRECQ 69.37 / 68.47、OBQ 69.56 / 68.69、GPTQ 69.37 / 67.88。ResNet50 は AdaRound 75.84 / 75.14、BRECQ 75.88 / 75.32、GPTQ 75.71 / 74.87。
- 速度（Table 6、PDF p8）: 3bit OPT-175B のトークンあたりレイテンシ。A100 80GB: FP16 230ms（5GPU）→ 3bit 71ms（1GPU）、3.24倍。A6000 48GB: 589ms（8GPU）→ 130ms（2GPU）、4.53倍。原文: "developing a quantized-matrix full-precision-vector product kernel which performs a matrix vector product by dynamically dequantizing weights when needed. Most notably, this does not require any activation quantization."
- 一言の要約: 重みのみ3〜4bitに量子化し、4bitでOPT-175BのperplexityをFP16から0.03しか悪化させない（RTNは2.2悪化）。速度向上は重みを都度dequantizeする専用kernelによる（活性は量子化しない）。

### 7-4. 先行手法との関係の記述（§2、PDF p3）

- 原文（§2）: "The AdaRound method (Nagel et al., 2020) computes a data-dependent rounding by annealing a penalty term, which encourages weights to move towards grid points corresponding to quantization levels."（原文のNagel et al., 2020はAdaRound）
- 原文（§2）: "BRECQ (Li et al., 2021) introduces Fisher information into the objective, and optimizes layers within a single residual block jointly."
- 原文（§2、LLM.int8()）: "LLM.int8() observes that activation outliers in a few feature dimensions break the quantization of larger models, and proposes to fix this problem by keeping those dimensions in higher precision."
- 一言の要約: GPTQ論文自身が、AdaRound・BRECQ・LLM.int8()をどう位置づけているかが分かる（分類表の「PTQの丸め・較正の工夫」の記述の根拠に使える）。

---

## 8. AWQ [Lin+, MLSys2024]

AWQ: Activation-aware Weight Quantization for On-Device LLM Compression and Acceleration（Proceedings of the 5th MLSys Conference, 2024。PDFページ＝論文内ページ）

### 8-1. 基本の観察: 重要な重みは約1%、選び方は活性の大きさ（§3.1、Figure 2、Table 1、PDF p1、p3〜p4）

- 原文（Abstract、PDF p1）: "Our method is based on the observation that weights are not equally important: protecting only 1% of salient weights can greatly reduce quantization error. We then propose to search for the optimal per-channel scaling that protects the salient weights by observing the activation, not weights."
- 原文（§3.1、PDF p3）: "selecting weights based on activation magnitude can significantly improve the performance despite keeping only 0.1%-1% of channels in FP16."（重みの大きさで選んでもランダム選択と同程度の改善しかない、とも記述）
- 原文（§3.1、PDF p3）: "such a mixed-precision data type will make the system implementation difficult."（約1%をFP16で残す方法の欠点）
- Table 1（PDF p4、OPT-6.7B、INT3 g128、WikiText perplexity）: FP16 10.86、RTN 23.54、活性に基づく選択で FP16 0.1% 11.58 / 1% 11.39 / 3% 11.36、重みに基づく選択で 23.41 / 22.37 / 22.45。
- Figure 2（PDF p3、OPT-6.7B、INT3-g128のperplexity）: RTN 43.2、1% salient weightsをFP16に保つ 13.0、scaling 13.0。
- 一言の要約: 重みの重要度は重み自身の大きさでなく、対応する入力活性の大きさで決まる。重要な約1%を保護すれば量子化誤差が大きく減る。

### 8-2. 活性を見たper-channelスケーリング（§3.2、式(1)〜(5)、PDF p3〜p5）

- 式(1): Q(w) = Δ · Round(w/Δ)、Δ = max(|w|)/2^(N−1)（Nはビット数、Δは絶対値最大で決まるscale）。
- 式(2)(3): 重みにs > 1を掛け、入力xを1/sで割ると Q(w·s)(x/s) = Δ'·Round(ws/Δ')·x·(1/s)。原文: "The ratio of the new error to the original error is Δ'/Δ · 1/s. Given Δ' ≈ Δ and s > 1, the relative error is smaller for the salient weight w."
- Table 2（PDF p4、OPT-6.7B、salientな1%のチャネルにsを掛ける）: s = 1 / 1.25 / 1.5 / 2 / 4 で Wiki-2 PPL = 23.54 / 12.87 / 12.48 / 11.92 / 12.36。原文: "the best perplexity is achieved at s = 2, since further increasing s will increase the quantization error for non-salient channels."
- 式(4): s* = argmin_s L(s)、L(s) = ||Q(W · diag(s))(diag(s)⁻¹ · X) − WX||。
- 式(5): **s = s_X^α、α* = argmin_α L(s_X^α)**。s_Xは活性の平均の大きさ（チャネルごと）。原文: "we use a single hyper-parameter α to balance between the protection of salient and non-salient channels. We can find the best α by a fast grid search over the interval of [0, 1] (0 means we do not scale; 1 corresponds to the most aggressive scaling in our search space). We further apply weight clipping to minimize the MSE error of quantization."（§5.1でgrid sizeは20）
- 原文（§3.2、PDF p5）: "Since the quantization function is not differentiable, we are not able to directly optimize the problem with vanilla backpropagation. There are some techniques relying on approximated gradients (Bengio et al., 2013; Esser et al., 2019), which we found still suffers from unstable convergence."（STE・LSQへの言及）
- 原文（§3.2 Advantages、PDF p5）: "Our method does not rely on any regression (Frantar et al., 2022) or backpropagation" / "It has minimal reliance on the calibration set since we only measure the average magnitude per channel, thus preventing over-fitting"
- 一言の要約: 活性の平均の大きさ s_X のα乗でチャネルをスケールし（重みに掛け、活性を割る）、αをgrid searchで決める重みのみの量子化。逆伝播・回帰を使わず、較正データへの過適合が起きにくいとしている。

### 8-3. SmoothQuantとの違い（原文の記述、§4、PDF p5）

- 原文: "converting the theoretical memory savings from W4A16 (4-bit weight, 16-bit activation) quantization into measured speedup is non-trivial. Alternative W8A8 quantization methods, such as SmoothQuant (Xiao et al., 2022), maintain the same data precision for both storage and computation."
- 一言の要約: AWQ論文自身が、SmoothQuant（W8A8）と自分（W4A16、重みのみ）の位置づけの違いを記述している。重みのみにする理由として、Figure 3（PDF p5、Llama-2-7B・RTX 4090）の説明 "The generation stage is memory bound ... W4A16 quantization can effectively improve the arithmetic intensity by 4×." と "The amount of weight access is orders of magnitude larger than the amount of activation access. Thus, weight-only quantization is more effective for on-device LLMs." を挙げている。

### 8-4. 結果（§5、Table 3・4、Abstract・Conclusion、PDF p4、p7、p11）

- Table 3（OPT 1.3B / 2.7B / 6.7B / 13B / 30B、3bit g128、WikiText perplexity、PDF p4）: FP16 14.62 / 12.47 / 10.86 / 10.13 / 9.56、RTN 119.47 / 298.00 / 23.54 / 46.04 / 18.80、1% FP16 16.91 / 13.69 / 11.39 / 10.43 / 9.85、AWQ 16.32 / 13.58 / 11.39 / 10.56 / 9.77。
- Table 4（PDF p7、WikiText2 perplexity、g128）: Llama-2 7B はFP16 5.47、INT3 RTN 6.66 / GPTQ 6.43 / AWQ 6.24、INT4 RTN 5.73 / GPTQ 5.69 / AWQ 5.60。LLaMA 7B はFP16 5.68、INT3 RTN 7.01 / GPTQ 8.81 / AWQ 6.35、INT4 RTN 5.96 / GPTQ 6.22 / AWQ 5.78。
- 速度（Abstract、PDF p1）: 原文 "TinyChat, an efficient and flexible inference framework tailored for on-device LLM/VLMs, offering more than 3× speedup over the Huggingface FP16 implementation on both desktop and mobile GPUs."（§1、PDF p2: 平均 3.2-3.3× のspeedup）
- 注意: 速度はGPU（RTX 4090、Jetson Orinなど）とTinyChatの実装での値で、本環境（CPU）の実測ではない。
- 一言の要約: 重みのみ3〜4bit（g128）のperplexityは、Table 4の全列でAWQが最小（RTN・GPTQ・GPTQ-Rより低い）。TinyChatでGPU上3倍超の高速化。

---

## 9. QLoRA [Dettmers+, NeurIPS2023]

QLoRA: Efficient Finetuning of Quantized LLMs（NeurIPS 2023。PDFページ＝論文内ページ。28ページ、付録を含む）

### 9-1. 位置づけ（Abstract、§3、PDF p1、p3）

- 原文（Abstract）: "QLoRA backpropagates gradients through a frozen, 4-bit quantized pretrained language model into Low Rank Adapters (LoRA)."（65Bモデルを単一の48GB GPUでfinetuneできる、とも記述）
- 原文（§3、PDF p3）: "QLORA has one low-precision storage data type, in our case usually 4-bit, and one computation data type that is usually BFloat16. In practice, this means whenever a QLORA weight tensor is used, we dequantize the tensor to BFloat16, and then perform a matrix multiplication in 16-bit."
- 式(3)（§2）: LoRA は Y = XW + sXL₁L₂（L₁ ∈ R^(h×r)、L₂ ∈ R^(r×o)、sはスカラー）。式(5)（§3）: Y_BF16 = X_BF16 · doubleDequant(c₁^FP32, c₂^k-bit, W^NF4) + X_BF16 L₁^BF16 L₂^BF16。
- 原文（§3、PDF p5）: "We dequantize the storage data type to the computation data type to perform the forward and backward pass, but we only compute weight gradients for the LoRA parameters which use 16-bit BrainFloat."
- 一言の要約: 凍結した4bit（NF4）重みを使う時だけBF16へdequantizeして計算し、勾配はLoRAのアダプタ（BF16）だけに流す。「量子化モデルの上でのfine-tuning」であり、推論時の高速化が主眼ではない。

### 9-2. ブロック単位の量子化の背景（§2 Block-wise k-bit Quantization、式(1)(2)、PDF p3）

- 式(1): X_Int8 = round(127/absmax(X_FP32) · X_FP32) = round(c_FP32 · X_FP32)（原文では range [−127, 127] のInt8への量子化の例。cは量子化定数 = scale）。式(2): dequant(c, X_Int8) = X_Int8/c = X_FP32。
- 原文: "if a large magnitude value (i.e., an outlier) occurs in the input tensor, then the quantization bins—certain bit combinations—are not utilized well with few or no numbers quantized in some bins. To prevent the outlier issue, a common approach is to chunk the input tensor into blocks that are independently quantized, each with their own quantization constant c."
- 一言の要約: absmaxでスケールする量子化では、外れ値が1つあるとbinが使われなくなる。テンソルをブロックに分けてブロックごとに量子化定数を持つ（per-groupに相当する考え方）。

### 9-3. 4-bit NormalFloat（NF4）の定義（§3、式(4)、Appendix H、PDF p4）

- 原文: "The NormalFloat (NF) data type builds on Quantile Quantization [15, 46] which is an information-theoretically optimal data type that ensures each quantization bin has an equal number of values assigned from the input tensor."
- 原文: "Since pretrained neural network weights usually have a zero-centered normal distribution with standard deviation σ (see Appendix I), we can transform all weights to a single fixed distribution by scaling σ such that the distribution fits exactly into the range of our data type. For our data type, we set the arbitrary range [−1, 1]."
- 構成手順（原文）: "(1) estimate the 2^k + 1 quantiles of a theoretical N(0, 1) distribution to obtain a k-bit quantile quantization data type for normal distributions, (2) take this data type and normalize its values into the [−1, 1] range, (3) quantize an input weight tensor by normalizing it into the [−1, 1] range through absolute maximum rescaling."
- 式(4): q_i = ½( Q_X(i/(2^k + 1)) + Q_X((i + 1)/(2^k + 1)) )。Q_X(·)は標準正規分布N(0, 1)の分位関数。
- 0の表現（原文）: "To ensure a discrete zeropoint of 0 and to use all 2^k bits for a k-bit datatype, we create an asymmetric data type by estimating the quantiles q_i of two ranges q_i: 2^(k−1) for the negative part and 2^(k−1) + 1 for the positive part and then we unify these sets of q_i and remove one of the two zeros that occurs in both sets."
- NF4の具体的な16個の値はAppendix H（本ノートでは未抽出）。
- 一言の要約: 重みが0中心の正規分布に従うことを前提に、標準正規分布の分位点から作る非一様な4bitの数値形式。各binに入る値の個数が等しくなる。0を厳密に表せる。ブロックごとにabsmaxで[−1, 1]へ正規化して使う。

### 9-4. Double Quantization（§3、PDF p4〜p5）

- 原文: "Double Quantization (DQ), the process of quantizing the quantization constants for additional memory savings. While a small blocksize is required for precise 4-bit quantization [13], it also has a considerable memory overhead. For example, using 32-bit constants and a blocksize of 64 for W, quantization constants add 32/64 = 0.5 bits per parameter on average."
- 原文: "Double Quantization treats quantization constants c₂^FP32 of the first quantization as inputs to a second quantization. ... We use 8-bit Floats with a blocksize of 256 for the second quantization"
- 原文: "On average, for a blocksize of 64, this quantization reduces the memory footprint per parameter from 32/64 = 0.5 bits, to 8/64 + 32/(64 · 256) = 0.127 bits, a reduction of 0.373 bits per parameter."
- 設定（§3、PDF p5）: "We use NF4 for W and FP8 for c₂. We use a blocksize of 64 for W for higher quantization precision and a blocksize of 256 for c₂ to conserve memory."
- 一言の要約: 量子化定数（scale）自体を8bitで再量子化し、1パラメータあたりのscaleのコストを0.5bitから0.127bitに減らす（約0.37bit/パラメータの削減）。

### 9-5. 結果（§4、Table 2・3、PDF p5〜p6）

- Table 2（Pile Common Crawl mean perplexity、125M〜13BのOPT/BLOOM/LLaMA/Pythia、PDF p6）: Int4 34.34、Float4 (E2M1) 31.07、Float4 (E3M0) 29.48、NFloat4 + DQ 27.41。
- Table 3（Mean 5-shot MMLU、LLaMA 7B〜65B、Alpaca / FLAN v2、PDF p6）: 平均はBFloat16 53.0、Float4 52.2、NFloat4 + DQ 53.1。
- 原文（§4、PDF p6）: "NF4 with double quantization fully recovers the 16-bit LoRA MMLU performance. In addition, we also note that QLORA with FP4 lags behind the 16-bit brain float LoRA baseline by about 1 percentage point."
- 原文（§4、PDF p6）: "NF4 improves performance significantly over FP4 and Int4 and that double quantization reduces the memory footprint without degrading performance."
- 一言の要約: 4bitの数値形式の比較でNF4（+DQ）が最良で、Int4・FP4より低perplexity。NF4+DQのQLoRAは16bitのLoRA・full finetuningの性能に追いつく（学術ベンチマーク上）。

---

## 10. AdaRound [Nagel+, ICML2020]

Up or Down? Adaptive Rounding for Post-Training Quantization（ICML 2020, PMLR 119。PDFページ＝論文内ページ）

### 10-1. rounding-to-nearestは最適とは限らない（Abstract、§1、§2、式(1)(8)、Table 1、PDF p1〜p3）

- 原文（Abstract、PDF p1）: "When quantizing neural networks, assigning each floating-point weight to its nearest fixed-point value is the predominant approach. We find that, perhaps surprisingly, this is not the best we can do."
- 式(1)（§1、PDF p2）: ŵ = s · clip(⌊w/s⌉, n, p)（nとpはクリップの負・正の整数しきい値）。
- 原文（§1）: "Perhaps surprisingly, we show that for post-training quantization, rounding-to-nearest is not optimal."
- 二次近似（§2、式(2)〜(8)、PDF p2）: タスク損失の変化を2次のTaylor展開で近似し、収束した学習済みモデルでは勾配項を無視すると ΔwᵀH(w)Δw が残る。例1（H = [[1, 0.5], [0.5, 1]]）では損失の増加が Δw₁² + Δw₂² + Δw₁Δw₂ に比例し、原文は "rounding-to-nearest is optimal when we only consider these diagonal terms" だが非対角項（符号が効く）を無視するため "making it often sub-optimal" と述べる。
- Table 1（PDF p3、ResNet18の第1層のみ4bit、ImageNet検証精度）: Nearest 52.29%、Ceil 0.10%、Floor 0.10%、Stochastic 52.06±5.52%、Stochastic (best) 63.06%。原文（PDF p2〜p3）: 100回の確率的丸めのうち48回がnearestより良かった。
- 一言の要約: 重みを個別にもっとも近い値へ丸めるのは、タスク損失から見ると最適とは限らない（重み同士の相互作用を無視している）。丸めの向き（上げる／下げる）を選び直すと精度が上がる。

### 10-2. 層ごとの局所損失への簡略化（§3.1〜§3.2、式(13)〜(20)、PDF p3〜p4）

- 原文（§3.2、PDF p4）: "In (20), we are simply minimizing the Mean Squared Error (MSE) introduced in the preactivations z^(ℓ) due to quantization."
- 式(20): argmin_{ΔW_{k,:}} E[(ΔW_{k,:} x^(ℓ−1))²]。仮定は、プレ活性に対するタスク損失のヘッセ行列が対角で、さらに定数であること（"∇²_z L_{i,i} = c_i is a constant independent of the input data samples"）。
- 原文（§3.2）: "optimizing the MSE, as specified in (20), is the best we can do when assuming no knowledge of the rest of the network past the layer that we are optimizing."
- 一言の要約: タスク損失を層ごとのプレ活性のMSE（式(20)）に落とし、その層の重みの丸め方（上か下か）を選ぶ問題にする。

### 10-3. AdaRoundの定式化（§3.3、式(21)〜(25)、PDF p4〜p5）

- 式(21): argmin_V ||Wx − W̃x||²_F + λ f_reg(V)。式(22): ソフト量子化重み W̃ = s · clip(⌊W/s⌋ + h(V), n, p)（⌊·⌋はfloor）。
- 式(23): h(V_{i,j}) = clip(σ(V_{i,j})(ζ − γ) + γ, 0, 1)（rectified sigmoid。原文: "ζ and γ are stretch parameters, fixed to 1.1 and −0.1, respectively"）。
- 式(24): f_reg(V) = Σ_{i,j} (1 − |2h(V_{i,j}) − 1|^β)。原文: "where we anneal the parameter β. This allows most of the h(V_{i,j}) to adapt freely in the initial phase (higher β) to improve the MSE and encourages it to converge to 0 or 1 in the later phase of the optimization (lower β)"
- 式(25)（asymmetric reconstruction）: argmin_V ||f_a(Wx) − f_a(W̃x̂)||²_F + λ f_reg(V)。x̂はそれ以前の層をすべて量子化した入力、f_aは活性化関数。原文: "(25) defines our final objective that we can optimize via stochastic gradient descent."
- 一言の要約: 各重みを切り上げるか切り下げるかを連続値h(V)で緩和し、層の出力誤差（式(25)）と、0か1へ寄せる正則化で最適化する（SGD）。重みのみの丸め方を学習する。

### 10-4. 設定と結果（§5、Table 7、PDF p6、p8）

- 設定（§5、PDF p6）: 原文 "To optimize AdaRound we use 1024 unlabeled images from the ImageNet [...] training set, Adam [...] optimizer with default hyper-parameters for 10k iterations and a batch-size of 32"（[...]は引用文献の表記を省略） / "the application of AdaRound to Resnet18 takes only 10 minutes on a single Nvidia GTX 1080 Ti."
- Table 7（PDF p8、ImageNet検証精度。W/Aはビット数）: Full precision 69.68 / 76.07 / 77.40 / 71.72（ResNet18 / ResNet50 / InceptionV3 / MobileNetV2）。Nearest 4/32 は 23.99 / 35.60 / 1.67 / 8.09。AdaRound 4/32 は 68.71±0.06 / 75.23±0.04 / 75.76±0.09 / 69.78±0.05（MobileNetV2はCLE前処理あり）。AdaRound w/ act quant 4/8 は 68.55±0.01 / 75.01±0.05 / 75.72±0.09 / 69.25±0.06。
- 原文（Abstract）: "Without fine-tuning, we can quantize the weights of Resnet18 and Resnet50 to 4 bits while staying within an accuracy loss of 1%."
- 一言の要約: ResNet18でW4（活性FP32）にするとき、roundingをnearestから学習した丸めに替えるだけで23.99%から68.71%に回復する。ラベルなしの1024枚で約10分（GTX 1080 Ti）。
- 注意: 活性の量子化はAdaRoundの対象外（活性は別途、較正）。重みの丸めの手法である。

---

## 11. BRECQ [Li+, ICLR2021]

BRECQ: Pushing the Limit of Post-Training Quantization by Block Reconstruction（ICLR 2021、arXiv:2102.05426v2。PDFページ＝論文内ページ。タイトルは本文で確認済み）

### 11-1. 何をする手法か（Abstract、§3.2、Algorithm 1、PDF p1、p4〜p5）

- 原文（Abstract）: "BRECQ leverages the basic building blocks in neural networks and reconstructs them one-by-one."
- 原文（Abstract）: "we propose a novel PTQ framework, dubbed BRECQ, which pushes the limits of bitwidth in PTQ down to INT2 for the first time."
- 原文（§3.2、PDF p4）: "optimizing the whole networks over 1024 calibration data samples leads to over-fitting easily." / "We find layer-wise reconstruction acts like a regularizer which reduces the generalization error by matching each layer's output distribution." → 中間の粒度として、ブロック（Figure 1: net-wise / stage-wise / block-wise / layer-wise の4種類の再構成粒度）を採用。
- 原文（§3.2、PDF p5）: "We name our algorithm BRECQ, because we choose block as our base reconstruction unit."
- 一言の要約: 層ごと（AdaRound）とネットワーク全体の間の粒度として、ResNetのbottleneckなどの「ブロック」単位で出力を再構成して、重みの丸めを最適化するPTQ。

### 11-2. Fisher情報行列の利用（§3.3、PDF p5）

- 原文: "We use the diagonal Fisher Information Matrix (FIM) to replace the pre-activation Hessian."
- 原文: "The diagonal of the pre-activation FIM is equal to the squared gradients of each elements"（出力の勾配が大きい要素ほど再構成で重視される、と説明: "If the output has higher absolute gradients, it will receive more attention when being reconstructed."）
- 原文（§3.3末、PDF p5）: "Note that BRECQ is compatible with any optimization method, like STE (Hubara et al., 2017). Here we adopt adaptive rounding (Nagel et al., 2020) for weights and learned step size (Esser et al., 2020) for activation step size"
- 原文（PDF p5）: "we only need a small subset (1024 in our experiments) of the" （calibration data。続きは未抽出）
- 一言の要約: ブロック出力の誤差を、勾配の2乗（Fisher情報の対角）で重み付けして最小化する。丸めはAdaRound、活性のstep sizeはLSQを使う。

### 11-3. 再構成粒度のablation（§4.1、Table 1、PDF p6）

- Table 1（2bit重み、最初と最後の層を除く、ImageNet精度、列: Layer / Block / Stage / Net）: ResNet-18 65.19 / 66.39 / 66.01 / 54.15。MobileNetV2 52.13 / 59.67 / 54.23 / 40.76。
- 原文（§4.1）: "It can be seen from Table 1 that Block-wise optimization outperforms other methods."
- 一言の要約: 2bit重みでは、ブロック単位の再構成がlayer・stage・network単位より良い（ResNet-18では差が小さい）。

### 11-4. 結果（§4.2〜§4.3、Table 2〜4、PDF p7）

- Table 2（重みのみ、活性FP、ImageNet精度）: Full Prec. はResNet-18 71.08 / ResNet-50 77.00 / MobileNetV2 72.49。4/32: AdaRound 68.71 / 75.23 / 69.78、BRECQ 70.70±0.07 / 76.29±0.04 / 71.66±0.04。3/32: AdaRound* 68.07 / 73.42 / 64.33、BRECQ 69.81±0.05 / 75.61±0.09 / 69.50±0.12。2/32: AdaRound* 55.96 / 47.95 / 32.54、BRECQ 66.30±0.12 / 72.40±0.12 / 59.67±0.13。（*は著者らの実装。注意: Full Precisionの値は、AdaRound論文のTable 7（ResNet18 69.68）とは異なる。）
- Table 3（活性4bit）: 4/4 で BRECQ 69.60±0.04 / 75.05±0.09 / 66.57±0.67（ResNet-18 / ResNet-50 / MobileNetV2）。2/4 で BRECQ 64.80±0.08 / 70.29±0.23 / 53.34±0.15。
- 原文（§4.2）: "Note that the first and the last layer are kept with 8-bit."
- Table 4（QATとの比較、PDF p7、ResNet-18、FP 71.08、4/4）: BRECQ 69.60（データ1024枚、0.4 GPU時間）、PACT 69.2（データ1.2M、100 GPU時間）、LSQ 71.1（データ1.2M、100 GPU時間）。
- 原文（Abstract）: "PTQ can attain 4-bit ResNet and MobileNetV2 comparable with QAT and enjoy 240× faster production of quantized models."
- 一言の要約: 4bit重みで、AdaRoundより高い精度（ResNet-18で70.70 vs 68.71）。2bit重みでも使える精度を出した。QATに近い精度をPTQ（1024枚、0.4 GPU時間）で得られるが、4/4のResNet-18ではLSQ（71.1）に及ばない。

---

## 12. LSQ [Esser+, ICLR2020]

Learned Step Size Quantization（ICLR 2020、arXiv:1902.08153v3。PDFページ＝論文内ページ）

### 12-1. 量子化器とstep sizeの学習（§2、式(1)〜(3)、PDF p3）

- 式(1): v̄ = ⌊clip(v/s, −Q_N, Q_P)⌉。式(2): v̂ = v̄ × s。sは量子化のstep size、Q_N・Q_Pは負・正の量子化水準の数。原文: "Given an encoding with b bits, for unsigned data (activations) Q_N = 0 and Q_P = 2^b − 1 and for signed data (weights) Q_N = Q_P + 1 = 2^(b−1)"（原文は文の一部が抽出テキストで崩れているため、この引用は要確認）。
- 原文（§2.1）: "LSQ provides a means to learn s based on the training loss by introducing the following gradient through the quantizer to the step size parameter:" 式(3): ∂v̂/∂s = −v/s + ⌊v/s⌉（−Q_N < v/s < Q_P）、−Q_N（v/s ≤ −Q_N）、Q_P（v/s ≥ Q_P）。
- 原文（§2.1）: "This gradient is derived by using the straight through estimator (Bengio et al., 2013) to approximate the gradient through the round function as a pass through operation (though leaving the round itself in place for the purposes of differentiating down stream operations), and differentiating all other operations in Equations 1 and 2 normally."
- 原文（§2.1）: "each layer of weights and each layer of activations has a distinct step size, represented as an fp32 value"（層ごと＝テンソルごと）。初期値は 2⟨|v|⟩/√Q_P（平方根は抽出テキストで欠落しており、式の細部は要確認）。初期値の計算は初期の重み、または最初のバッチの活性に基づく。
- 一言の要約: 量子化のstep sizeを学習可能なパラメータにして、STEで丸めを通過させた勾配（式(3)）で重みと同時に学習する。

### 12-2. step sizeの勾配のスケール（§2.2、式(4)、PDF p4）

- 原文: "we multiply the step size loss by a gradient scale, g, where for weight step size g = 1/√(N_W Q_P) and for activation step size g = 1/√(N_F Q_P)"（√は抽出テキストで欠落、N_Wは層の重みの数、N_Fは層の特徴数。式の細部は要確認）。
- 一言の要約: step sizeの更新量が重みの更新量と釣り合うよう、層の大きさとビット数で勾配をスケールする。

### 12-3. 学習の設定（§2.3、PDF p4〜p5）

- 原文（§2.3）: "full precision weights are stored and updated, quantized weights and activations are used for forward and backward passes, the gradient through the quantizer round function is computed using the straight through estimator (Bengio et al., 2013)"（式(5): 1（−Q_N < v/s < Q_P）、それ以外は0）
- 原文（§2.3）: "We set input activations and weights to either 2-, 3-, 4-, or 8-bit for all matrix multiplication layers except the first and last, which always use 8-bit"
- 原文（§2.3）: "All quantized networks are initialized using weights from a trained full precision model with equivalent architecture before fine-tuning in the quantized space"。2〜4bitは90エポック、8bitは1エポック。
- 一言の要約: 学習済みFPモデルから始め、重みもstep sizeも学習するQAT。最初と最後の層は8bit。

### 12-4. 結果（§3.2、§3.6〜§3.7、Table 1・4、PDF p2、p7〜p8）

- Table 1（ImageNet top-1、LSQ、2 / 3 / 4 / 8bit、PDF p2）: ResNet-18（Full precision 70.5）67.6 / 70.2 / 71.1 / 71.1。ResNet-34（Full precision 74.1）71.6 / 73.4 / 74.1 / 74.1。ResNet-50（Full precision 76.9）73.7 / 75.8 / 76.7 / 76.8。
- Table 4（LSQ+知識蒸留、PDF p8、top-1）: ResNet-18 67.9 / 70.6 / 71.2 / 71.1（2 / 3 / 4 / 8bit）、32bit 70.5。ResNet-50 74.6 / 76.9 / 77.6 / 76.8、32bit 76.9。
- 原文（Abstract）: "can train 3-bit models that reach full precision baseline accuracy."（Table 4の蒸留併用のとき）
- 原文（§3.6、PDF p8）: "This indicates that LSQ learns a solution that does not in fact minimize quantization error." / "simply fitting a quantizer to its corresponding data distribution may not be optimal for task performance."
- 一言の要約: step sizeをタスク損失で学習するQAT。ResNet-18の4bitでFP32（70.5）を上回る71.1。学習されたstep sizeは量子化誤差（MSEなど）を最小化する値とは一致しない。

---

## 13. PTQ4ViT [Yuan+, ECCV2022]

PTQ4ViT: Post-Training Quantization for Vision Transformers with Twin Uniform Quantization（PDF本文に会議名の記載なし。レイアウトはSpringer LNCS形式。会議名・年は公式ページで要確認。PDFページ＝論文内ページ）

### 13-1. post-softmax・post-GELUの活性分布（§3.2、Fig. 2・3、PDF p5〜p6）

- 原文（Abstract、PDF p1）: "We observe the distributions of activation values after softmax and GELU functions are quite different from the Gaussian distribution. We also observe that common quantization metrics, such as MSE and cosine distance, are inaccurate to determine the optimal scaling factor."
- 原文（§3.2、PDF p6）: "(1) The distribution of activations after softmax is very unbalanced, in which most values are very close to zero and only a few values are close to one. (2) The values after the GELU function have a highly asymmetric distribution, in which the unbounded positive values are large while the negative values have a very small distribution range."
- 原文（§3.2、PDF p6）: "The activation values in CNNs are usually considered Gaussian distributed. Therefore, most PTQ quantization methods are based on this assumption to determine the scaling factor."
- softmaxの値の問題（§3.2、PDF p6〜p7）: 原文 "A larger scaling factor can reduce the quantization error of these large values, which causes smaller values to be quantized to zero. While a small scaling factor makes the large values quantized to small values, which significantly decreases the intensity of attention between two patches."
- GELUの値の問題（§3.2、PDF p7）: 原文 "it is difficult to quantify both positive and negative values well with symmetric uniform quantization."（非一様量子化は "most hardware devices cannot efficiently process the non-uniform quantized values" として退けている）
- 一言の要約: ViTのsoftmax後は0付近に偏り少数の大きな値（注意の強さ）を持ち、GELU後は正の値の範囲が大きく負の値の範囲が小さい非対称分布になる。CNNで想定されるガウス分布の仮定では較正しにくい。

### 13-2. Twin Uniform Quantization（§3.2、式(4)(5)、Fig. 4、PDF p7〜p8）

- 原文（§3.2、PDF p7）: "We propose the twin uniform quantization, which can be efficiently processed on existing hardware devices including CPUs and GPUs. ... twin uniform quantization has two quantization ranges, R1 and R2, which are controlled by two scaling factors ΔR1 and ΔR2, respectively."
- 式(4): T_k(x, ΔR1, ΔR2) = Ψ_{k−1}(x, ΔR1)（x ∈ R1）、Ψ_{k−1}(x, ΔR2)（それ以外）。
- softmaxの場合（原文、PDF p7）: R1 = [0, 2^(k−1) Δ^s_R1) は小さいΔ^s_R1で細かく量子化し、Δ^s_R2を 1/2^(k−1) に固定して R2 = [0, 1] で全範囲（大きな値）を覆う。GELUの場合: 負の値を R1 = [−2^(k−1) Δ^g_R1, 0]、正の値を R2 = [0, 2^(k−1) Δ^g_R2] とし、Δ^g_R1を固定して負の値の全範囲を覆う。較正では Δ^s_R1 と Δ^g_R2 を探索する。（数式は抽出テキストで一部崩れており、範囲の細部は要確認）
- データ形式（原文、PDF p7）: "The most significant bit is the range flag to represent which range is used (0 for R1, 1 for R2). The other k−1 bits compose an unsigned number to represent the quantity."
- 式(5)（PDF p8）: ΔR2 = 2^m ΔR1（mは符号なし整数）と制約し、a_q × ΔR1 + b_q × ΔR2 = (a_q + b_q × 2^m) ΔR1。原文: "We left shift b_q by m bits ... The shift operation is very efficient on CPUs or GPUs."
- 一言の要約: 1つのテンソルに2つの量子化範囲（細かい範囲と粗い範囲）を持たせ、最上位ビットで範囲を区別する。2つのscaleを2のべき乗の比に制約し、シフト演算だけで揃えられるのでCPU・GPUで効率よく処理できる（非一様量子化ではなく、一様量子化2つの組み合わせ）。

### 13-3. Hessian guided metricと較正（§3.1、§3.3、式(3)(6)(7)、Algorithm 1、PDF p5〜p10）

- ベースのPTQ（§3.1、PDF p5〜p6）: 行列積 O = AB の入力A・Bを対称一様量子化し、較正でscaling factorを探索する。原文: "The same as [27], we use cosine distance as the metric ... We alternatively search for the optimal scaling factors"（A・Bを交互に最適化）。探索空間は [α·A_max/2^(k−1), β·A_max/2^(k−1)] をn個の候補に等分。原文: "the base PTQ results in more than 1% accuracy drop on quantized vision transformer in our experiments."
- 原文（§3.3、PDF p8〜p9）: "MSE, cosine distance, and Pearson correlation coefficient are inaccurate compared with task loss (cross-entropy) on vision transformers." 例として、ViT-S/224のblocks.6.mlp.fc1の活性でcosine distanceは約0.4 A_max/2^(k−1)、task lossは約0.75 A_max/2^(k−1) を最適とする（Fig. 5）。
- 式(6)(7): 量子化の損失への影響をTaylor展開し、層ごとの再構成として min_Δ E[(Ô^l − O^l)ᵀ diag((∂L/∂O^l_1)², …, (∂L/∂O^l_|O^l|)²) (Ô^l − O^l)]（出力勾配の2乗で重み付けした誤差。BRECQと同系統の定式化: 原文は "Based on the layer-wise reconstruction method in [14]" と引用）。
- 一言の要約: MSE・cosine distanceなどの層出力の距離は、タスク損失での最適なscaleと食い違うため、出力の勾配（タスク損失への影響）で重み付けした距離で較正する。

### 13-4. 設定と結果（§4、Table 1・2、PDF p10〜p12）

- 設定（§4.1、PDF p10）: 原文 "We randomly select 32 images from the training dataset as calibration images." / "We quantize all the weights and inputs for the fully-connect layers including the first projection layer and the last prediction layer. We also quantize the two input matrices for the matrix multiplications in self-attention modules." / "we don't quantize softmax and normalization layers in vision transformers." 探索は α = 0、β = 1.2、n = 100、#Round = 3。
- Table 1（ImageNet top-1、括弧内はFP32からの低下、列: FP32 / Base PTQ W8A8 / W6A6 / PTQ4ViT W8A8 / W6A6、PDF p11）: ViT-S/224 81.39 / 80.46(0.91) / 70.24(11.1) / 81.00(0.38) / 78.63(2.75)。ViT-B/224 84.54 / 83.89(0.64) / 75.66(8.87) / 84.25(0.29) / 81.65(2.89)。DeiT-S/224 79.80 / 77.65(2.14) / 72.26(7.53) / 79.47(0.32) / 76.28(3.51)。DeiT-B/224 81.80 / 80.94(0.85) / 78.78(3.01) / 81.48(0.31) / 80.25(1.55)。
- 原文（§4.2、PDF p11）: "base PTQ results in more than 1% accuracy drop on some vision transformers even at the 8-bit quantization. PTQ4ViT achieves less than 0.5% accuracy drop with 8-bit quantization. For 6-bit quantization, base PTQ results in high accuracy drop (9.8% on average) while PTQ4ViT achieves a much smaller accuracy drop (2.1% on average)."
- Table 2（DeiT-S/224、W8A8 / W6A6、較正画像数、PDF p12）: EasyQuant 76.59 / 73.26（1024枚）、Liu 77.47 / 74.58（1024枚）、PTQ4ViT 79.47 / 76.28（32枚）。DeiT-BのW4A4は Liu (MP) 75.94、PTQ4ViT 60.91、PTQ4ViT+BC 64.39。原文: "At 4-bit quantization, the performance of PTQ4ViT is not good."
- Table 3（ablation、PDF p13）: 原文 "using the Hessian guided metric alone can slightly improve the accuracy at 8-bit quantization, and it significantly improves the accuracy at 6-bit quantization. For instance, on ViT-S/224, the accuracy improvement is 0.46% at 8-bit while it is 6.96% at 6-bit."（表本体は抽出テキストで列が崩れており数値は未確認）
- 一言の要約: ViTのW8A8でFP32からの低下を0.5%未満に抑え（ViT-S/224で0.38）、W6A6でも平均2.1%の低下に抑える。W4A4は精度が足りない。
- 注意: 評価対象はImageNet分類のViT/DeiT/Swin。本講義の演習の小さいViT・CIFAR10とは別条件。

---

## 14. Q-Diffusion [Li+, ICCV2023]

Q-Diffusion: Quantizing Diffusion Models（CVF Open Access版。本文に開催年の記載なし。メタデータSubjectはIEEE International Conference on Computer Vision。年は公式ページで要確認。PDFページ＝論文内ページ）

### 14-1. 課題: timestepごとに活性分布が変わる（§3.1、Figure 3〜5、PDF p1、p4〜p5）

- 原文（Abstract、PDF p1）: "We identify the key difficulty of diffusion model quantization as the changing output distributions of noise estimation networks over multiple time steps and the bimodal activation distribution of the shortcut layers within the noise estimation network. We tackle these challenges with timestep-aware calibration and split shortcut quantization in this work."
- 原文（§3.1 Challenge 1、PDF p4）: "the errors accumulate quickly through iterative denoising."（CIFAR-10・DDIM 100ステップで、INT8・INT5・INT4のMSEを各timestepで比較。4bitで誤差が急増。Figure 3）
- 原文（§3.1 Challenge 2、PDF p4〜p5）: "the activation distributions gradually change, with neighboring time steps being similar and distant ones being distinctive."（Figure 5）
- 原文（§3.1、PDF p5）: "Calibrating the noise estimation model using only a few time steps that do not reflect the full range of activations seen among all time steps ... can cause overfitting to the activation distribution described by those specific time steps, while not generalizing to other time steps"
- Figure 4（PDF p4）: 4bit重み量子化で、較正データ（5120サンプル）を最初のn・中間のn・最後のnのtimestepから取ると性能が落ちる。原文: "the case with samples taken from the middle 50 time steps caused smaller drops compared to cases with samples taken from either the first or the last n time steps"。
- 一言の要約: 拡散モデルは同じ網を全timestepで使うが、timestepごとに活性分布が違うので、一部のtimestepだけで較正すると他で性能が落ちる。

### 14-2. Time step-aware calibration（§3.3.1、Algorithm 1、PDF p5）

- 原文: "we propose to randomly sample intermediate inputs uniformly in a fixed interval across all time steps to generate a small calibration set."
- 原文: "Empirically, we have found that the sampled calibration data can recover most of the INT4 quantized models' performance after the calibration"
- 較正の手順（原文）: "we divide the model into several reconstruction blocks [20], and iteratively reconstruct outputs and tune the clipping range and scaling factors of weight quantizers in each block with adaptive rounding [28] to minimize the mean squared errors between the quantized and full precision outputs." 活性は "we only adjust the step sizes of activation quantizers"（adaptive roundingは使わない）。
- 一言の要約: 全timestepから一定間隔で中間入力をサンプリングして較正データにする。重みはブロックごとの再構成とadaptive rounding（BRECQ・AdaRound系）、活性はstep sizeの調整のみ。

### 14-3. Split shortcut quantization（§3.2、§3.3.2、Figure 6・7、PDF p5〜p6）

- 原文（§3.2、PDF p5）: "the input activations in DDIM's shortcut layers can be up to 200 times larger than other neighboring layers."
- 原文（§3.2、PDF p5）: "the ranges of activations from the deep feature channels (X1) and shallow feature channels (X2) being concatenated together vary significantly, which also resulted in a bimodal weight distribution in the corresponding channels ... Naively quantizing the entire weight and activation distribution with the same quantizer will inevitably lead to large quantization errors."
- 式（§3.3.2、PDF p6）: Q_X(X)Q_W(W) = Q_X1(X1)Q_W1(W1) + Q_X2(X2)Q_W2(W2)（concatenationの前の2つの部分に分けて、それぞれ別の量子化器を使う。式番号は抽出テキストで未確認）。
- 一言の要約: UNetのshortcutで深い特徴と浅い特徴をconcatした入力は範囲が大きく違う（最大約200倍）ため、2つに分けて別々に量子化し、あとで足す。

### 14-4. 結果（§4.2、Table 1〜2、PDF p7）

- 設定（PDF p6〜p7）: CIFAR-10（32×32、DDIM 100ステップ）、LSUN-Bedrooms・LSUN-Churches（256×256、LDM）。ベースラインは「channel-wise round-to-nearest Linear Quantization」とSQuant。
- Table 1（CIFAR-10・DDIM、FID（低いほど良い）、PDF p7）: Full Precision 32/32 4.22。Linear Quant 8/32 4.71、Q-Diffusion 8/32 4.27。Linear Quant 4/32 141.47、SQuant 4/32 160.40、Q-Diffusion 4/32 5.09。Linear Quant 8/8 118.26、Q-Diffusion 8/8 3.75。Linear Quant 4/8 188.11、Q-Diffusion 4/8 4.93。
- Table 2（LSUN-Bedrooms・LDM-4、FID、PDF p7）: Full Precision 2.98。Linear Quant 4/32 82.69、Q-Diffusion 4/32 4.86。Linear Quant 4/8 24.86、Q-Diffusion 4/8 5.32。
- 原文（§4.2、PDF p7）: "Q-Diffusion still preserves most of the perceptual quality with at most 2.34 increase in FID and imperceptible distortions in produced samples."
- 原文（Abstract、PDF p1）: "we can run stable diffusion in 4-bit weights with high generation quality for the first time."
- 一言の要約: 拡散モデルを4bit重みにすると、通常のPTQ（Linear Quant）ではFIDが100超に崩れるが、timestepを考慮した較正とshortcut分割でFIDの悪化を最大2.34に抑える（W4/A32のCIFAR-10は4.22から5.09）。

---

## 15. FP8 [Micikevicius+, arXiv2022]

FP8 Formats for Deep Learning（arXiv:2209.05433v2。PDFページ＝論文内ページ）

### 15-1. E4M3・E5M2の定義（§3、Table 1、Abstract、PDF p1、p3）

- 原文（Abstract、PDF p1）: "an 8-bit floating point (FP8) binary interchange format consisting of two encodings - E4M3 (4-bit exponent and 3-bit mantissa) and E5M2 (5-bit exponent and 2-bit mantissa). While E5M2 follows IEEE 754 conventions for representation of special values, E4M3's dynamic range is extended by not representing infinities and having only one mantissa bit-pattern for NaNs."
- 原文（§3、PDF p3）: "FP8 consists of two encodings - E4M3 and E5M2, where the name explicitly states the number of exponent (E) and mantissa (M) bits."
- 原文（§3、PDF p3、推奨）: "The recommended use of FP8 encodings is E4M3 for weight and activation tensors, and E5M2 for gradient tensors."
- Table 1（PDF p3、「Details of FP8 Binary Formats」）:
  - Exponent bias: E4M3 7、E5M2 15
  - Infinities: E4M3 N/A、E5M2 S.11111.00₂
  - NaN: E4M3 S.1111.111₂、E5M2 S.11111.{01, 10, 11}₂
  - Zeros: E4M3 S.0000.000₂、E5M2 S.00000.00₂
  - **Max normal: E4M3 S.1111.110₂ = 1.75 × 2⁸ = 448、E5M2 S.11110.11₂ = 1.75 × 2¹⁵ = 57,344**
  - Min normal: E4M3 S.0001.000₂ = 2⁻⁶、E5M2 S.00001.00₂ = 2⁻¹⁴
  - Max subnorm: E4M3 S.0000.111₂ = 0.875 × 2⁻⁶、E5M2 S.00000.11₂ = 0.75 × 2⁻¹⁴
  - Min subnorm: E4M3 S.0000.001₂ = 2⁻⁹、E5M2 S.00000.01₂ = 2⁻¹⁶
  - （表中のS.E.M表記: Sは符号ビット、Eは指数部、Mは仮数部。下付き2は2進数）
- 原文（§3、PDF p3）: "the E5M2 format follows the IEEE 754 conventions for exponent and special values and can be viewed as IEEE half precision with fewer mantissa bits" / "the dynamic range of E4M3 is extended by reclaiming most of the bit patterns used for special values"
- 原文（§3.1、PDF p3）: "This modification extents the dynamic range by one extra power of 2, from 17 to 18 binades. We gain the representation of seven more magnitudes (256, 288, 320, 352, 384, 416, 448) ... The maximum representable magnitude without this modification would be 240."
- 原文（§3.1、PDF p3）: "5 bits of exponent provide sufficient per tensor dynamic range (32 binades, including the subnormal values) for DL."
- 一言の要約: E4M3は符号1・指数4・仮数3ビット（最大値448、範囲は狭いが精度が高い。無限大を持たない）、E5M2は符号1・指数5・仮数2ビット（最大値57,344、IEEE 754準拠で範囲が広い）。推奨は重み・活性にE4M3、勾配にE5M2。どちらも値の間隔が一様でない浮動小数点形式（講義の「非一様な数値形式」の根拠）。

### 15-1b. スケールと指数bias（§3.2、PDF p4）

- 原文: "Exponent bias controls the placement of representable range on the real number line. The same effect is achieved when maintaining a scale factor per tensor."
- 原文: "Leaving the per-tensor scaling to software implementation enables more flexibility than is possible with a programmable exponent bias approach - the scaling factor can take on any real value (typically represented in higher precision), while programmable bias is equivalent to allowing only powers of 2 as scaling factors."
- 一言の要約: 表現範囲の位置は指数biasかテンソルごとのscaleで決まる。FP8でも、テンソルごとのscaleをソフトウェア側で持つ。

### 15-2. 推論（PTQ）での比較（§4.2、Table 5、PDF p6）

- 原文（§4.2）: "Both quantizations use per-channel scaling factors for weights, per-tensor scaling factors for activations, as is common for int8 fixed-point." / "Max-calibration (choosing the scaling factor so that the maximum magnitude in a tensor is represented) is used for weights, activation tensors are calibrated using the best calibration chosen from max, percentile, and MSE methods."（percentile較正を明記している箇所）
- Table 5（16-bit FPで学習したモデルのPTQ、列: 16-bit FP / int8 / E4M3）: BERT Base SQuAD v1.1 (F1) 88.19 / 76.89 / 88.09。BERT Large 90.87 / 89.65 / 90.94。GPT3 126M wikitext103 (perplexity) 19.01 / 28.37 / 19.43。GPT3 1.3B 10.19 / 12.74 / 10.29。
- 原文（§4.2）: "BERT language model evaluation on Stanford Question Answering Dataset shows that FP8 PTQ maintains accuracy while int8 PTQ leads to a significant loss of model accuracy."
- 原文（§4.2）: "We also tried casting the tensors to FP8 without applying a scaling factor, which resulted in a significant accuracy loss, increasing the perplexity to 11.0."
- 注意: シミュレーション（"Training experiments were carried out with simulated FP8 - tensor values were clipped to only those that could be represented in FP8"、§4）。ハードウェア上の速度の評価は含まれない。
- 一言の要約: 16bit浮動小数点で学習したBERT・GPTでは、int8のPTQで精度が落ちる一方、E4M3のPTQは16bit FPに近い精度を保つ（本論文のモデル・設定での結果）。

---

## 付録A. 分類表用の一言要約（計画書の分類表の軸に沿う）

各行の根拠は上の該当節。軸を混ぜない。

| 軸 | 手法 | 一言（原典の記述に基づく） | 根拠節 |
|---|---|---|---|
| いつ量子化するか | PTQ | 学習済みモデルを再学習なしで量子化する。8bitは多くの場合PTQで足りる（Nagel白書 Abstract） | 2-10 |
| いつ量子化するか | QAT（STE） | 順伝播で量子化を模擬し、丸めの勾配はSTE（∂⌊y⌉/∂y = 1）で通す。低ビットで有利だが学習コストがかかる（Nagel白書 §4．Jacob §3 は学習中の量子化の模擬を述べるが STE とは書いていない） | 1-2、2-9、4-1 |
| 丸め・較正の工夫（PTQ） | AdaRound | 重みを近い値へ丸めるのは最適とは限らず、層出力の誤差を最小化するよう切り上げ／切り下げを学習する | 10-1〜10-3 |
| 丸め・較正の工夫（PTQ） | BRECQ | ブロック単位で出力を再構成し、勾配の2乗（Fisher）で重み付けする。2bit重みまで到達 | 11-1〜11-4 |
| 丸め・較正の工夫（PTQ） | GPTQ | 重みのみを層ごとの出力誤差（2次情報）を最小化して列順に量子化し、誤差を残りの重みへ配分する。3〜4bitのLLM向け | 7-1〜7-3 |
| 外れ値・スケールの扱い | LLM.int8() | 約0.1%の外れ値特徴次元だけ16bit、残りを8bitで行列積する混合精度分解 | 5-1、5-2 |
| 外れ値・スケールの扱い | SmoothQuant | 活性のチャネルをs_jで割り、重みに掛けて難しさを重みへ移す（s_j = max(\|X_j\|)^α / max(\|W_j\|)^(1−α)）。W8A8 | 6-1〜6-3 |
| 外れ値・スケールの扱い | AWQ | 活性の大きい約1%のチャネルを保護するためのスケーリング（s = s_X^α）。重みのみ（W4A16など） | 8-1、8-2 |
| 数値形式 | INT8/INT4 | 一様な整数グリッド（scale・zero-point） | 1-1、2-1 |
| 数値形式 | FP8（E4M3・E5M2） | 浮動小数点の8bit。E4M3は最大448、E5M2は最大57,344 | 15-1 |
| 数値形式 | NF4 | 正規分布の分位点から作る非一様な4bit形式（QLoRA） | 9-3 |
| 量子化モデルの上でのfine-tuning | QLoRA | NF4で凍結した重み＋LoRA。使う時だけBF16へdequantizeして計算し、勾配はアダプタだけ | 9-1、9-4 |
| 対象ドメインへの適用 | PTQ4ViT | ViTのpost-softmax・post-GELUの分布に合わせたtwin uniform quantizationと、Hessianを使った較正 | 13-1〜13-3 |
| 対象ドメインへの適用 | Q-Diffusion | 拡散モデルのtimestepごとの活性分布の変化に対するtimestep-aware較正と、shortcutの分割量子化 | 14-1〜14-3 |
| （補足）学習するscale | LSQ | step sizeをSTEで学習するQAT。最初と最後の層は8bit | 12-1〜12-4 |

## 付録B. 注意が必要な点・確認できなかった点

- percentile較正: Nagel白書・Krishnamoorthi白書のテキストに "percentile" は出現しない（0件）。FP8論文 §4.2（PDF p6）が「max、percentile、MSEの中から最良の較正を選ぶ」と述べる（FP8の節 15-2）。講義の「minmax・percentile・MSE」のうち、minmaxとMSEは白書（節 2-7）、percentileはFP8論文（節 15-2）が出典。percentile単独の定義・式を原典から引く箇所は、今回の15本では未確認。
- STE: 量子化のroundへの適用（∂⌊y⌉/∂y = 1）は、Bengio論文でなくNagel白書 §4.1・LSQが述べる（Jacob は述べていない）。Bengio論文は確率的バイナリニューロンの文脈（節 4-1の注意）。
- 白書の「Qualcomm」のフッタ: Nagel白書の各ページには "Confidential and Proprietary — Qualcomm Technologies" とある。
- ViTの外れ値: 原典のうち、ViT（画像）の活性の外れ値そのものを扱うのはPTQ4ViT（post-softmax・post-GELUの分布）だけ。LLM.int8()・SmoothQuant・AWQの外れ値はLLMの話で、ViTへの転用は発表者の解釈になる（「発表者の解釈」と明記すること）。
- 数値の比較: BRECQのFP32（ResNet-18 71.08）とAdaRoundのFP32（69.68）は設定が違う。論文間の数値を同じ表に並べない。
- 速度・メモリ（SmoothQuant 1.56倍、GPTQ 3.25倍、AWQ 3倍超など）はGPU上の原典の実測。本環境の実測（演習④）と混ぜない。
- 取得元（arXiv ID・URL）: Jacob、AdaRound、PTQ4ViT、LLM.int8()、SmoothQuant、AWQ、QLoRA、Q-DiffusionはPDF本文から確認できず「未確認」。公式ページでの確認が必要。
- 式番号が未確認のもの: Krishnamoorthi §2.1の式、Q-Diffusion §3.3.2の式、BRECQ・PTQ4ViTの一部の式（本文の抽出テキストで式番号が崩れたため）。
- 表の数値が未確認のもの: PTQ4ViT Table 3（ablation）、STEの実験の数値（図・表を未抽出）、QLoRAのNF4の16個の値（Appendix H）。
- 読んだ範囲: 各論文の本文（主に手法と主要結果の節）。付録は、必要な場合を除き読んでいない。上記以外の節の記述を引用する場合は、再確認が必要。

## 付録C 訂正・確認（2026-11-14，スライド検査①の結果）

- 訂正: 「JacobもSTEを述べる」は誤り。Jacob の PDF に "straight"・"STE" は0件。STEと明記するのは Krishnamoorthi 白書・Nagel 白書・LSQ。上記の該当行を直した。
- 公式ページで確認した会議名・年と arXiv ID: Jacob+ = CVPR 2018（1712.05877），PTQ4ViT [Yuan+] = ECCV 2022（2111.12293），Q-Diffusion [Li+] = ICCV 2023（2302.04304）。
- 未確認のまま: 上記以外の arXiv ID（8本のうち残り）。
- 訂正（2026-11-14，最終検査）: Nagel 白書の BN folding は，重み W̃ が式(11)，バイアス b̃ が式(12)（式(10)は書き換えの式）。上の節 2-6 を直した。
