---
date: 2026-11-16
project: lab-study-quantization
type: presenter-prereading
---

# 発表者の予習用: 日本語の解説記事とA案の対応

発表者自身が量子化を理解するための入口。スライドの根拠ではない（根拠は原典と実測。spec「原典と出典の書き方」）。各記事の内容は2026-11-16にWebで中身を確認した（要約はツールによる確認で、全文の精読ではない）。

## 読む順番

| 順 | 資料 | 読む目的 | A案の対応 | 目安 |
|---|---|---|---|---|
| 1 | 亀澤「[ニューラルネットワークの量子化手法の紹介](https://speakerdeck.com/emakryo/niyurarunetutowakunoliang-zi-hua-shou-fa-noshao-jie)」（Speaker Deck、GO、2023-09） | 全体の地図。何を・何ビットに・どの粒度で・どう較正するか、PTQ/QAT、手法名の一覧がCNNとLLMの両方で並ぶ | 全体（特に節4 S37の分類表） | 20分 |
| 2 | jasagiri「[LLM量子化 Day 3: 量子化の基本原理](https://qiita.com/jasagiri/items/b7addba09e6e4043fb47)」（Qiita、2025-12） | scale・zero-pointの式、数値例、対称/非対称の図、NumPyの短いコード | 節1（S7–14）、演習① | 15分 |
| 3 | うるいざか「[INT8量子化でCNNをエッジ推論向けに最適化する — ONNX Runtime PTQ 実践記](https://zenn.dev/ux_xu/articles/ort-int8-ptq-cnn)」（Zenn、2026-05） | CNN（MobileNetV2）での実例。static/dynamic、較正、per-tensorとper-channelの精度差、速度が上がる条件 | 節2–3（S15–30）、節4の演習④（S38–40） | 20分 |
| 4 | 木村「[コンピュータビジョンモデルの量子化による精度低下の原因特定とその緩和](https://speakerdeck.com/mot_techtalk/konpiyutabiziyonmoderunoliang-zi-hua-niyorujing-du-di-xia-noyuan-yin-te-ding-tosonohuan-he)」（Speaker Deck、GO、2023-07） | CVモデルで、どの層が精度を落とすかを1層ずつ量子化して調べる方法（感度解析）と対処 | 節2 S21（最初の層は敏感）、節5 S42–43（自分のモデルに移す） | 15分 |
| 5 | joisino「[深層モデルの高速化](https://speakerdeck.com/joisino/shen-ceng-moderunogao-su-hua)」（Speaker Deck） | 量子化の部分だけ。QATとSTE | 節4 S32–34 | 10分 |

## 注意

- 2のQiita記事はLLM向けの連載。AWQ・k-quantを「重要な重みを高精度で保持」と説明しているのは簡略化しすぎ（AWQは活性の大きいチャネルをスケーリングで守る手法）。
- SmoothQuantの日本語解説（[Zenn、中野](https://zenn.dev/nakano_teppei51/articles/ad29f585d06abb)）は、考え方とαの式は原典どおりだが、実装コード（biasのスケーリング、重みの軸）に誤りがあり、性能の数値に出典がない。読むなら考え方の部分だけにし、A案S35–36と原典を正とする。
- 3のZenn記事の数値（per-channel 57.44% / per-tensor 51.69% など）は記事の環境での値。勉強会の実測値と混ぜない。
