# Open Pool v15 hierarchical family SVC candidate

## 仮説

採用済みOpen Pool v15 flat 4-view SVCはconfirmation BA `0.433403`でCPU bestを上回ったが、誤りの半数が同じ提供元内の兄弟モデル間だった。Confirmation混同行列2,699行では、正解1,170件、同一family内の誤り770件（全誤りの50.36%）、familyを跨ぐ誤り759件だった。まずfamilyを分類し、そのfamily内だけで18ラベルの兄弟識別を行う階層型SVCがflat SVCを改善できるか、OOFで検証する。

Familyは公式のprovider mapで固定する: Anthropic (5), Google (4), ZAI (2), OpenAI (5), Moonshot (1), Qwen (1)。singleton familyも6-family分類器には含め、conditional classifierはfamilyに複数classがある場合のみ必要とする。

## 変更対象と範囲

- 外部実験repoに独立runner `src/cpu_openpool_hierarchical_svc.py` と専用run directoryを追加する。既存CPU・GPU runner/config/artifact、進行中candidate02/04は変更しない。
- 採用済みOpen Pool v15 flat SVCと同じ公式train、prompt-reconstructed data、external pool version、foldwise prompt除外（char/word cosine >=0.40）、exact text除外、uniform 2,500 rows/class cap、pool weight 0.35、official weight 1.0、4-view vectorizer/LinearSVC C・max_iter・seed、model label順を使用する。Publisher `match_weight`、test、community adapter、API生成データは使わない。
- 各foldの同一行feature matrixで、(a) 6-class family SVC と (b) family別のconditional SVC群をfitする。SVC decision valuesを固定温度1.0のsoftmaxで変換し、`log P(family) + log P(class | family)`を18列のscoreとする。温度・blend係数の探索は行わず、nested/outer validationラベルから後処理を調整しない。
- Primaryの既存GroupKFoldとConfirmation `GroupKFold(n_splits=5, shuffle=True, random_state=42)`を同じrunnerで個別に作成する。

## 評価

- 各splitで全OOF行2,699、150 prompt group、fold間prompt非重複を確認。Concatenated OOF balanced accuracyをflat SVC・最良CPU baselineとprompt単位paired bootstrap（2,000回、seed 42）で比較する。
- OOF class recall、family-level confusion、word-length指標、fold別BA/SD、全conditional classifierのconvergenceを保存する。
- Candidate採用はprimaryとconfirmationの両方でflat SVCとの差bootstrap 95% CI下限が0超の場合に限る。片splitだけ、または区間が0を含む場合は未確定として記録し、公開LBだけで採用しない。

## 資源・検証

- CPU-only。実行直前にCPU affinity、CPU load、MemAvailable、RSS、両GPUの使用状況を読み取り確認。CPU thread上限4、process-tree RSS上限32 GiB、MemAvailable下限16 GiB。既存runへ干渉する状態なら開始しない。
- Foldごとにoutputをatomic保存し、完了済みfoldのmanifest/hashを検証後に再利用可能とする。Finite/列順/OOF ID/GroupKFold/prompt separation/class coverage/sampling audit/convergenceをrunner内で検証する。追加test suiteは実行しない。
- 出典の着想: [ozertuu/0-672-dual-svc-better](https://www.kaggle.com/code/ozertuu/0-672-dual-svc-better)はwithin-family gateを含むと本文で説明する。0.672は投稿者のPublic LB報告で、複数のdataset/model sourceを使い、自前の再現値ではない。ここではその構成や重みを移植せず、公式provider family階層だけを固定splitで切り分ける。
