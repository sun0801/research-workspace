---
date: 2026-11-09
last_updated: 2026-11-10
project: kaggle-name-that-llm
type: source-review
status: reviewed
tags: [public-notebook, lora, adapter-analysis, ensemble-diversity]
---

# LoRA-24公開adapterの構造分析Notebook確認

開始結論: (b) 試さない — Notebookはweight geometry分析で、prompt-grouped OOFや性能改善の根拠がなく、公開adapter datasetのlicenseも未確認。

## 出典と取得範囲

- URL: https://www.kaggle.com/code/romakulichkin/how-lora-24-style-classifiers-work
- 著者: KulichkinRoma
- 取得日時: 2026-11-09 06:34 JSTごろ、公式Kaggle MCP
- 閲覧範囲: score-descending/recent-run Notebook一覧、metadata version 3、Notebook Markdownと公開source/表示済み内容。GPU実行や学習の再現はしていない。
- metadataの`last_run_time`は2026-11-05 21:34 UTC、Notebook searchの`last_run_time`は2026-11-08 21:33 UTCで不一致。
- 本Notebook自体はGPUを使わず、外部データは`dhruvtibarewal/nlm-l24-adapters-v5` dataset一つ。著者は公開adapter重みの解析と説明する。

## Notebook内の報告

- LoRA-24分類器は、凍結したLLMの先頭約24層、全線形projectionへのrank-16 LoRA、8深度のmean pooling、各深度LayerNorm、18-class linear headを使い、約30–45M parametersを学習する構成と説明する。
- 公開adapterの更新量はMLP（gate/up/down）が約2/3を占め、attention projection全体より大きく、特に早いlayerの更新が目立つと報告。
- 5-foldとfull-dataのadapter更新方向は各backbone内でcosine約`.998`と報告し、two-stage学習では大きい第1段poolが更新の大部分を決めると解釈する。そのため同一backboneのfold平均よりbackbone間の多様性がblendに効きやすい、という著者の見立て。
- backboneごとにheadが読む深度profileが異なり、Qwen3-8B/14B/Llama-3.1-8Bの特徴方向も異なると報告。class weightの近さはClaude+GLM等のstyle familyを作るが、方向は概ね直交に近くhard groupingではないとの説明。

## 今回への判断

本Notebookはweight geometryの観察であり、prompt-grouped OOFやLB scoreの改善を示す候補ではない。adapter datasetのKaggle license fieldはNotebook本文によれば`Other`で説明がないため、specのlicense条件を確認できるまで重みを再利用しない。構造上の示唆は、同一backboneのseed/foldを増やすより異なるbackbone間の補完性を測る方が合理的というもの。これは現在進行中のQwen/ModernBERTおよび次候補のOLMo/Mistral/Qwen3.5をprompt-grouped比較する方針を補強するが、実験キューは変更しない。

## 関連資料

- [元Notebook](https://www.kaggle.com/code/romakulichkin/how-lora-24-style-classifiers-work)
- [adapter dataset](https://www.kaggle.com/datasets/dhruvtibarewal/nlm-l24-adapters-v5)
- [プロジェクトREADME](../README.md)

最終結論: (b) 試さない — OOF/LB改善の根拠がなく、license未確認のadapter weightsを再利用できないため、このNotebookを候補として試さない。
