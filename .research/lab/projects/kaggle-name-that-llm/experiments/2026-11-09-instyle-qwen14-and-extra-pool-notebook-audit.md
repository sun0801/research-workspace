---
date: 2026-11-09
project: kaggle-name-that-llm
type: public-source-review
status: lead-investigated-not-reproduced
tags: [public-notebook, instyle, qwen3, data-provenance, prompt-grouped]
---

# InStyle Qwen3-14B と追加データ量の公開Notebook監査

開始結論: (b) 試さない

## 取得範囲

- 取得: 2026-11-09 09:23–09:25 JST、公式Kaggle MCPのName That LLM Notebook一覧とNotebook詳細。
- ScoreDescending上位10件ではタイトル申告の最高値は`.681`。現在の公式Public LBトップ`.752`を超えるNotebookは確認できなかった。
- DateRun上位には`bgunshui/ntl-train-instyle-q14-smoke`、`sameershaikh27/name-that-llm-how-much-does-extra-data-buy`、`bgunshui/ntl-v673-a25`などが並んだが、一覧の`DateRun`と個別metadataの`last_run_time`に数日の不一致がある。
- source範囲: Sameer notebookはversion 2の本文・選択コード、InStyle Q14はversion 1のmetadata・source選択部分と前後文脈、NTL-v673 A25はmetadata・主要説明部・一部コード。実行や提出結果を独立再現していない。

## InStyle Qwen3-14B smoke

`bgunshui/ntl-train-instyle-q14-smoke`のmetadataはversion 1、14B-Baseモデル、GPU Notebook、Internet無効、7つの外部datasetを登録し、詳細の`last_run_time`は2026-11-06 00:25 UTC。Recent Run検索はNov 9を示すため、検索上の新着を新しい実行結果とは扱わない。

Sourceは、外部文章を`prompt_id`・labelごとに重複排除し、12以上のlabelが回答したpromptを残し、最大12,000行へ制限するQwen3-14B InStyle LoRAを記載する。Qwen3-14Bを24層に切り詰め、fp16、384 token、選択8層のreadout、1 epochを指定する。ただし`SMOKE=True`で各job 3 update、0.4時間の上限である。通常学習のOOFや完全な比較結果ではない。

検証コードはofficial trainから30 prompt groupを一度だけrandom holdoutするが、同じ`VALID_GROUPS`に当たる外部prompt groupを`EXT`から除く処理は選択範囲で確認できなかった。外部群を`ext_`接頭辞にしてofficial prompt IDとは別group扱いするため、prompt overlapがあればvalidation漏洩する余地がある。5-fold OOF、paired bootstrap、独立confirmationも示されていない。

登録datasetのうち、`crtproduction/name-that-llm-open-pool`はCC BY-SA 4.0を掲示し、コンペtrain promptへの回答を含まないと説明する。一方、他の6 sourceのlicense・provider output terms・provenanceは今回未確認。Notebook全体の外部データ構成は、そのまま使用可能とは判断しない。

## 追加Open Poolのデータ量主張

`sameershaikh27/name-that-llm-how-much-does-extra-data-buy`はversion 2、CPU-only、Open Poolを使ったchar/word LinearSVC、`StratifiedGroupKFold(5, shuffle=True, random_state=42)`を記載する。作者は6,000 passages/classで2-answers-per-prompt score `.440`、official-only `.329`、同様のchar+word版Public LB `.422`を報告する。これらはNotebook内の作者申告で、単純なOOF balanced accuracyとは異なる2-answer scorerも使う。notebookのv1 private runをv2へ記録したとsourceに明記し、metadataの最終実行はNov 6。

この結果は外部データが有力な要因である仮説を補強するが、現行Open Pool v15の2500/class設定を変更する直接根拠や、我々のencoder候補の改善予測にはならない。ラベル別のpool数が不均一で、Gemini 3.7は3,541行と記載される。

## NTL-v673 A25 の位置付け

`bgunshui/ntl-v673-a25`はmetadata version 1で、複数の公開dataset・Notebook出力・モデルを入力に列挙する。本文はprivate依存がなくても再現できる複雑なpublic stackを論じ、複数variantのLB値を記載するが、このNotebookの提出scoreや独立再現は今回検証していない。sourceには小規模interactive commit時にheavy処理をskipする`FAST_COMMIT`経路もあり、submit時のhidden rerunとは区別して読む必要がある。公開タイトルの数値をこのversionの検証済み成績として扱わない。

## 候補への反映

InStyle prompt-panel学習は候補仮説として保留する。試す場合はcleanなversion固定外部sourceだけを用い、foldごとにvalidationと同じ・近似prompt groupを外部文章から除外し、exact-text重複も除く。既存candidateとは同一prompt-grouped splitで比較し、OOF全体とprompt-paired bootstrapのgateを通過した場合のみ独立confirmationへ進む。GPUが全て割当中の現時点ではqueue順を変更せず、実装・GPU投入・Kaggle書込・提出を行わない。

## 出典

- [InStyle Q14 smoke](https://www.kaggle.com/code/bgunshui/ntl-train-instyle-q14-smoke)
- [How Much Does Extra Data Buy?](https://www.kaggle.com/code/sameershaikh27/name-that-llm-how-much-does-extra-data-buy)
- [NTL v673 A25](https://www.kaggle.com/code/bgunshui/ntl-v673-a25)
- [Name That LLM Public Leaderboard](https://www.kaggle.com/competitions/name-that-llm/leaderboard)

最終結論: (b) 試さない — 各sourceはscore/version/OOFが検証できず、InStyle smokeはprompt-overlap・provenance・nested confirmationに未解決点があり、現行bestを超える根拠がない。
