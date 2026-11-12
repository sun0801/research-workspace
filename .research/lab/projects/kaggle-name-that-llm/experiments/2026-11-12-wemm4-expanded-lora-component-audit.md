---
date: 2026-11-12
project: kaggle-name-that-llm
type: source-audit
status: hold
tags: [public-notebook, wemm4, lora, provenance, prompt-grouped]
---

# WeMM4 expanded LoRA component audit

開始結論: **(c) 保留** — 独自foldのOOF参照は有望だが、現在の評価splitと外部資材の利用条件を確定できず、再学習・採用判断へ進めない。

## 出典と取得範囲

- Kaggle Notebook: [concyclics/0-679](https://www.kaggle.com/code/concyclics/0-679?scriptVersionId=365653660)。ORIGIN metadataはCHEN Han (concyclics)の公開出力・source score`.679`に帰属し、adapterはミラー作成者の再学習ではないと記載する。
- Kaggle Dataset: [lightningv08/ntl-olmo2-native24-final-inference-assets](https://www.kaggle.com/datasets/lightningv08/ntl-olmo2-native24-final-inference-assets)、version 22、取得確認 2026-11-12 19:29 JST。説明はcollection licenseを`Other`とし、構成要素ごとに元のlicense・provenanceを確認するよう指定する。
- 監査範囲: Notebook version 1のソースとmetadataをCLI pullし、圧縮sourceを実行せず静的展開。WeMM componentの`ORIGIN.json`、`manifest.json`、`study.json`、`oof_reference.npz`、`tokens.npz`、全foldの`split.json`・`source_complete.json`を取得・確認。base modelの重みや約104.7GBのcollection全体は取得していない。
- 選択ファイルの照合: `sha256sum -c /tmp/wemm-public-audit-v22/WEMM_SELECTED_SHA256SUMS` は全件「OK」（一致）。`oof_reference.npz`のhash prefixは`ff047117`。これは配布manifestとの一致確認であり、学習履歴やデータ権利の独立証明ではない。

## 候補の中身と検証

- manifest/studyはWeMM-Embedding-4Bの5-fold、`original_prompt_fivefold=true`、公式train 2,699行、outer fit後の公式2 epochs、`full_official_fits=0`、held-out adapterだけを使うfull replayを記録する。fold別のsource-complete receiptもmanifestと一致した。公開tokensのID順は公式`train.csv`と完全一致し、全promptは単一foldに所属する。
- 保存されたcomponent OOF参照の単純argmax BAは`plain=.621253`、`centered=.616811`。これは公開者の参照出力を既存ラベルで評価した値で、こちらの独立再現値ではない。`plain`/`centered`も現bestのSpectral confirmation`.653828`より低い。
- componentのfold assignmentは登録済みprimary/confirmationと一致しない。公式train順のうち同じfold番号に残るのはprimary 540/2,699行、confirmation 575/2,699行のみで、prompt割当ても一対一のfold permutationではない。従ってcomponent OOFと採用baseline OOFを同一splitの対応あり比較として扱えない。
- 元Notebookの静的sourceではWeMM branchを既存のQwen系branchと組み、WeMM share`.2`・Q27 weight`.1`などの複合構成に入れる。source score`.679`はWeMM単体のscoreではなく、現公式leader`.768`超えの根拠でもない。
- studyは`clean_old`と`expanded`条件、外部pool由来のdata manifestを記載し、「既知の公式関連行は上流で除外したが、未知の意味的関係は残りうる」と明記する。配布artifactに元のdata manifest/raw external textsは含まれない。ORIGIN記載の元dataset `concyclics/ntl-wemm4-native-fivefold-20261104`はKaggle MCP `datasets.get`とCLI `datasets files`の双方で403となり、元dataset metadata/licenseと外部pool provenanceを確認できなかった。
- Notebook pullのouter sourceはbase85/zlib payloadを展開後に`exec`する構造だったため、実行せずに静的展開して調査した（展開source hash prefix `784a81d3`）。Kaggleのhidden execution traceやこのcomponent単体のLB値は取得していない。

## 保留を解除する条件

1. 元dataset/weightと外部poolのlicense・出所を、元の公開metadataまたは明示された権利情報で確認できること。外部dataを使う場合は、各validation foldの近似promptおよびtrain回答重複を除く方法・件数を再現可能にできること。
2. source training code/設定または独立実装を用意し、登録済みprimaryとindependent confirmationの各foldだけで再学習したOOFを作ること。別foldの公開OOF値は採否gateに流用しない。
3. 同一splitの現bestとのprompt-paired bootstrap、class recall、追加モデルの補完性を固定条件で評価すること。

条件が揃うまでこのweightをNotebookや提出に使わず、新しいGPU runも開始しない。既存のWeMM凍結embedding + LinearSVC候補（primary gateで棄却）とは学習方法が異なるため、結果は混同しない。
