---
date: 2026-11-13
project: lab-study-quantization
type: survey
---

# 量子化勉強会: 既存の公開資料の調査と採用判断の材料

最終判断は依頼主が行う。本書の「採用の形」「意見」はすべて提案である。

## 1. 調査の概要

- 調査日時: 2026-11-13 19:10頃から。所要は約15分（上限の15〜20分以内）。
- 確認方法: WebFetch（ページ本文を小型モデルが要約して返す形式）とWebSearch。CUHKのPDFだけは本体を取得し、`pdftotext` で目次・見出し語を確認した。
- 重要な限界:
  - WebFetchの結果は要約であり、原文の逐語確認ではない。ライセンス欄は「ページ上に記載が見当たらない」という意味で、「許諾がない」と断定するものではない。
  - MITのスライド（Dropbox）、Lab（Colab）、Pozdnyakovの各Notebook本体、DeepLearning.AIの講義内容は **開いていない**。各資料のページ上の記述だけを根拠にしている。
  - 403等で取れなかったもの:
    - MIT efficientml.ai のGitHub（`mit-han-lab/efficientml.ai`）: 404。
    - torchao の `quick_start.html`: 404（`index.html` は取得できた）。
  - 取得できず未確認のもの: torchaoのライセンス（取得ページに記載なし。ここでは推測で埋めない）、PyTorch公式の量子化チュートリアル（torchao以外）は未調査。
- 再利用条件の方針: 明記が見つからない資料は、依頼どおり「参考・紹介にとどめる」を既定とした。

## 2. 資料ごとの表

| # | 資料 | 対象 | 深さ | 演習・環境 | ライセンス・再利用 | 最終更新（確認できた範囲） |
|---|---|---|---|---|---|---|
| 1a | MIT 6.5940 (2024 Fall) Lec5-6 量子化 Part I/II、Lab 2 | 記載なし（ページ上は題名のみ。CNN/LLMの別は未確認） | PhD向けの講義2回分。ページ上の細目は未確認 | Lab 2: Quantization（2024-09-26公開）。環境はGoogle Colab（リンクあり、Notebook本体は未確認） | 記載なし。「Copyright © MIT Han Lab, MIT」のみ | ページに更新日なし。最新のお知らせは2024-10-24 |
| 1b | MIT 6.5940 (2026 Fall) Lec5-6、Lab 4 | 同上 | 同上 | Lab 4: Quantization（2026-10-27公開、締切11-05）、Colabリンクあり（本体は未確認） | 同上（連絡先 hanlab@mit.edu） | 日付なし。講義スライドとビデオのリンクは掲載済み。最終版かは不明 |
| 2a | DeepLearning.AI × HF「Quantization in Depth」 | 特定モデルの記載なし。「オープンソースのPyTorchモデルのdense層」 | 中級。2時間20分、動画18本、コード13本 | コード例あり。環境の記載なし。Learn-by-doingの完走が前提 | 資料のライセンス記載なし。利用規約へのリンクのみ。「期間限定で無料（ベータ）」 | 2025-10-07 |
| 2b | 同「Quantization Fundamentals with Hugging Face」 | LLM寄り（Transformers/Quanto） | 入門。1時間14分、動画7本、コード3本 | コード例あり。環境の記載なし | 同上 | 2025-10-07 |
| 3 | Arik Poznanski「Neural Network Quantization in PyTorch」（ブログ＋GitHub） | CNN（CIFAR向けに改造したResNet-18、CIFAR-10） | 実践。PyTorch 2 Export量子化によるstatic PTQ/QAT（int8、weight＋activation） | Notebook 4本（PTQ/QAT × X86/XNNPACK）。Colab記載なし。PyTorch 2.4〜2.8で確認と記載 | リポジトリは **MIT license**（GitHubページの表示）。ブログ自体の条件は記載なし | 2025-04-16公開（GitHubの最終コミット日は取得できず） |
| 4 | CUHK CMSC5743 Mo03 Quantization（Bei Yu） | 汎用（DNN全般。ViT/LLMの記述は検索語で見当たらず） | 講義スライド64ページ（フッター表記は /42）。浮動小数点・固定小数点、PTQ（KLによる較正）、QAT（STE、学習可能なクリップ）を含む | なし | 明記なし。冒頭に「UCB EE290 Shao Spring 2020、TensorRT 8-bit、Gholami et al. 2021 から素材を転用」と記載。転用元由来の図が多い可能性 | 2024-09-02（PDFメタデータと表紙） |
| 5a | joisino（佐藤竜馬）「深層モデルの高速化」 | CNN中心＋Attention近似。ViT・LLMは明示なし | 85枚の高速化サーベイ。量子化は5〜35枚付近が最も詳しい（QAT/PTQ、STE、weightのみ/weight＋activation、FP16/INT8/二値化） | なし | Speaker Deck上に「All slide content and descriptions are owned by their creators」のみ。オープンライセンスの表示なし | 2023-07-12 |
| 5b | GO 木村「コンピュータビジョンモデルの量子化による精度低下の原因特定とその緩和」 | CNN（物体検出YOLOv3、EfficientNet-Lite0） | 15枚。層ごとの感度分析、検出ヘッド分割、depthwise畳み込みの影響 | なし | 「無断転載・複製を禁ずる」旨の記載あり | 2023-07-14公開（発表は07-11） |
| 5c | PFN「LLMと低精度数値表現」 | LLM | 52枚。数値フォーマットとcast（量子化）手法、LLMの学習・推論での利用事例と課題 | なし | 記載なし（「All slide content ... owned by their creators」のみ） | 2024-05-13公開（発表は05-08） |
| 6 | torchao公式ドキュメント（quick start / tutorials） | LLM例（Llama-3-8B） | int4 weight-only（`Int4WeightOnlyConfig`、`quantize_`、group_size=32）の例を確認 | pip install torchao、CUDA/XPU/CPU。取得できたのはindexのみ（quick_startは404） | **ページ上では確認できず**。GitHubのライセンスは別途確認が必要 | 2026-03-25 |

補足: 5bのGO資料は、検索では「公開ページ」と「Player」の2か所が見つかった。要約はSpeaker Deckの公開ページから得た。

## 3. 資料ごとの採用の形の提案と理由

| # | 提案する形 | 理由 |
|---|---|---|
| 1a/1b MIT | 構成を参考。必要なら図を出典付きで引用。さらに学ぶ資料としても紹介 | 量子化を2回の講義で体系的に扱うという構成が、本勉強会の講義部分に近い。図の引用は、研究室内の勉強会での引用の範囲で、MITスライドの該当ページを直接確認してから決める（ライセンス記載なし）。Lab（Colab）は、中身を確認していないため下敷きにはしない。ViT・fake-quantの評価条件が合うかも未確認 |
| 2a Quantization in Depth | 構成を参考（特にper-tensor/channel/groupの導入順）＋さらに学ぶ資料 | トピック（対称・非対称、3つの粒度、誤差の測定）が演習①②と重なる。一方、コードの再利用条件が不明で、環境も不明。コードを下敷きにはしない。ログイン・期間限定無料である点は、参加者に紹介する際の注意点 |
| 2b Fundamentals | さらに学ぶ資料 | 入門で、LLM・Quantoが中心。本勉強会のCV向けの演習とは合わない |
| 3 Poznanski | 演習④の参考 ＋ さらに学ぶ資料。ResNet18のコードは、MITライセンス下で一部を下敷きにできる可能性がある（要確認） | ResNet-18×CIFAR-10の実際のint8実行（サイズ44.77MB→11.26MB、精度80.53%→約79.5%、GPU遅延約16%減、CPU遅延はほぼ変化なし、とブログ上に記載）が、演習④と近い。ただし、(a) fake-quantではなく実際の変換、(b) per-channelを明示設定せず既定config、(c) ViTなし、(d) 較正は先頭256枚（specは固定seedの512枚）。演習②③の下敷きにはならない。ブログの数値は引用元として扱い、本勉強会の測定値と混ぜない |
| 4 CUHK | 構成を参考（PTQ→QATの流れ、KL較正、STE）＋さらに学ぶ資料 | 内容は網羅的だが、浮動小数点の導入が長く、90分の入門にはそのまま使えない。冒頭に他講義からの転用元が明記されており、図の再利用条件は転用元にも依存しうる。図の引用は避け、原典（Gholami et al. 2021など）側から出典を取るのが安全 |
| 5a joisino | 構成を参考＋さらに学ぶ資料（日本語） | 日本語で、QAT/PTQ、STE、weightのみとweight＋activationの違いを図解している。メンバーが読みやすい。再利用条件の記載がないため、図の引用は避け、紹介にとどめる |
| 5b GO 木村 | さらに学ぶ資料。講義の「実際に使うときの判断基準」の話題として、層ごとの感度分析を紹介 | 「無断転載・複製を禁ずる」の記載があるため、図は引用せず、概念の紹介にとどめる。数値（YOLOv3 32.3→27.2→31.0 mAPなど）は自分のスライドに転記せず、資料へのリンクを示す |
| 5c PFN | さらに学ぶ資料（FP8・NF4・LLMの話題） | 「一様でない数値形式」の別枠で触れる箇所の参考。LLM寄りで、本勉強会の演習とは重ならない。再利用条件の記載がないため紹介にとどめる |
| 6 torchao | 演習④の実装の拠り所（公式ドキュメントとして参照）＋さらに学ぶ資料 | specの演習④は実際の低精度実行を示す。ドキュメントのquick startはint4 weight-only（`Int4WeightOnlyConfig`）の例を持つ。ただしCNN・ViTでの動作、CPU実行、バージョンの固定は **未確認**で、先行検証が必要。ライセンスもここでは確認していない |

## 4. 演習の下敷きを既存資料に替えるべきか（意見）

意見: 演習①〜③は、既存資料に替えず、自作のままが妥当と考える。理由は次のとおり。

1. specの評価条件（fake-quantの対象を全Conv2d/Linearの重みと入力活性に限定、重みは対称・符号付きで per-tensor/channel/group64、活性は非対称・per-tensor・静的、較正 minmax/percentile/MSE、固定seedの評価2,000枚・較正512枚、ResNet18のBN folding、ViTのQKV/proj/MLP）を、今回確認できた範囲の資料はどれも満たさない。
   - Poznanski: 実際のint8変換でfake-quantではなく、ViTなし、per-channel/group64の明示なし、較正方法の切り替えなし。
   - Quantization in Depth: 重みの線形量子化の導入は近いが、活性の較正（percentile/MSE）、CIFAR10、ViTは確認できていない（トピック一覧にない）。
   - MIT Lab: 中身を確認していないため判断できない。確認には、Colab Notebookを実際に開く必要がある（今回は未実施）。
2. 再利用条件が明記されたコードは、確認できた範囲ではPoznanskiのリポジトリ（MIT license）だけ。その他は紹介にとどめるのが妥当。
3. したがって、既存資料を「下敷き」に使える可能性が最も高いのは、演習④（実際の低精度実行）とその周辺（PyTorch 2 Export量子化のX86/XNNPACKの流れ）だけである。ただし、演習④はtorchaoを予定している。Poznanskiのコードはtorchao（`quantize_`）ではなくPyTorch 2 Export量子化を使うため、そのままは使えず、「別のAPIでの同種の実演」としての位置づけになる。
4. 要確認事項（採用判断の前に、必要なら追加調査）:
   - MIT Lab 2/Lab 4のNotebookの中身（対象モデル、fake-quantの有無、ライセンス表記）。
   - Quantization in Depthのコード（Colab/ローカルの別、ライセンス）。
   - torchaoのCPU・ViT・ResNet18での動作と、torchao自体のライセンス。

本specの「満たせない場合は止めて確認する」の規定に照らすと、今回は替えない方針なので、止める必要は生じない。

## 5. スライドの構成・図のアイデア

資料中の位置は、ページ上の記述と本書で確認した範囲に限る。確認していないものは「未確認」と明記した。

| 講義区間（spec） | 図・構成のアイデア | 参考にする資料と位置 |
|---|---|---|
| 0–10分 なぜ量子化するか | メモリ・帯域・エッジ実行の動機。「FP16で約1.5倍、INT8で2〜4倍」といった目安は、出典付きで1枚に | joisino 5〜35枚付近（速くなる理由: メモリ、SIMD、Tensor core、キャッシュ。ページ上の説明）。具体的な数値は原典スライドで再確認してから引用する |
| 10–28分 数値表現と一様量子化 | scale・zero-pointの数直線図、丸め誤差とクリップ誤差のトレードオフを自作図で。FP8/NF4は別枠で1枚 | CUHK Mo03の冒頭〜Quantization First Example（浮動小数点・固定小数点から入る構成。ページ位置は未確認）。PFN（数値フォーマット）。MITのLec5（位置は未確認） |
| 28–45分 粒度と外れ値 | per-tensor/channel/groupの重み行列の塗り分け図。ViT活性の外れ値のヒストグラム（自作の実測値） | Quantization in Depth（3つの粒度のレッスン。位置未確認）。CUHKには Groupwise の記述あり（検索語で確認、ページ未確認） |
| 45–62分 活性の量子化と較正 | minmax・percentile・MSE（KLとの対比）の比較図。BN foldingの計算グラフ | CUHK（KL divergenceによる較正、「2048 groups」の記述を検索語で確認。ページ位置は未確認） |
| 62–80分 PTQ/QAT・SmoothQuant | STEの図と簡単な数値例。PTQ/QATの流れ図 | joisino（STEの例とQAT/PTQの比較、5〜35枚付近）。CUHK（STE、学習可能なクリップのページ。位置未確認）。Poznanski（PTQ/QATの実コードの流れ。ブログ） |
| 62–80分 実演④ | サイズ・速度・メモリの表を自分の測定値で作る | Poznanskiの数値は「別環境の参考値」として引用に限る |
| 80–90分 実際に使う判断基準 | 層ごとの感度分析（1層ずつ量子化して精度低下を測る）、最初・最後の層、depthwiseの注意 | GO 木村（15枚全体）。ただし図は転載せず、リンクで紹介する |
| 分類表（AdaRound、GPTQ、AWQなど） | specの分類表のまま | 本調査では原論文の確認はしていない（別途、原典で確認する） |

図は、再利用条件が不明な資料のものは使わず、概念図は自作（python-pptx）が原則と考える。数値や図を引用する場合は、出典（資料名・日付・ページまたは枚数）を各スライドに明記し、勉強会の範囲内での引用とする。

## 6. 「さらに学ぶ」候補リスト（参加者向け）

URLは本調査で取得できたもの。内容は、ページ上の記述に基づく概要である。

| 区分 | 資料 | URL | 一言 |
|---|---|---|---|
| 講義（英語） | MIT 6.5940 EfficientML.ai Lec5-6 | https://hanlab.mit.edu/courses/2024-fall-65940 / https://hanlab.mit.edu/courses/2026-fall-65940 | 量子化を2回の講義と、Colabの演習（Lab）で学べる。内容は未確認のため、勉強会の前に1回は目を通して推薦するか決めたい |
| 講義（英語） | CUHK CMSC5743 Mo03 | https://www.cse.cuhk.edu.hk/~byu/CMSC5743/2024Fall/slides/Mo3-quant.pdf | 浮動小数点から、PTQ・QAT・STEまで64ページ |
| コース（英語） | DeepLearning.AI × HF Quantization in Depth / Fundamentals | https://www.deeplearning.ai/short-courses/quantization-in-depth/ / https://www.deeplearning.ai/courses/quantization-fundamentals-with-hugging-face | コードで線形量子化を自作して学ぶ（無料期間は限定的との表示） |
| Notebook（英語） | Poznanski ResNet18×CIFAR-10 PTQ/QAT | https://arikpoz.github.io/posts/2025-04-16-neural-network-quantization-in-pytorch | 実際のint8変換の実例。リポジトリ: https://github.com/arikpoz/neural-network-optimization |
| スライド（日本語） | joisino「深層モデルの高速化」 | https://speakerdeck.com/joisino/shen-ceng-moderunogao-su-hua | 量子化を含む高速化の全体像。日本語 |
| スライド（日本語） | GO 木村「CVモデルの量子化による精度低下の原因特定とその緩和」 | https://speakerdeck.com/mot_techtalk/konpiyutabiziyonmoderunoliang-zi-hua-niyorujing-du-di-xia-noyuan-yin-te-ding-tosonohuan-he | 層ごとの感度分析の実例。CV（検出）向け |
| スライド（日本語） | PFN「LLMと低精度数値表現」 | https://speakerdeck.com/pfn/20240508-hpckenkyukai-pfn-llm | FP8などの数値形式とLLMでの利用 |
| ドキュメント | torchao | https://docs.pytorch.org/ao/stable/index.html | int4 weight-onlyなどのAPI。ライセンスと対応環境は未確認 |

## 7. 未確認事項・次の一手（提案）

- MIT Lab 2/4のColabとスライドの該当ページを開く（15分程度）。演習②③の設計との差と、図の引用候補のページ番号を確定できる。
- PyTorch公式の量子化チュートリアル（torchao以外、`torch.ao.quantization` 系）は今回未調査。
- ライセンス・再利用条件は、すべてページ上の記載ベース。図を引用する場合は、各資料の原本で最終確認する。
- 演習④: torchaoがResNet18/ViTのCPU実行・サイズ測定に使えるかは、specの先行検証で確認する。
