# Open Pool v15 4-view SVC candidate

## 仮説

公開Notebookでは、Open Poolを学習に含めたn-gram SVCが単体・アンサンブルの一部として使われている。投稿者申告のみで再現値ではないが、現在のCPU best（OOF BA 0.384504）に対して、公開かつ出所を確認したOpen Pool v15をfoldwiseに使うSVCを評価する価値がある。外部で学習済みのadapter、予測、annotationは使わず、Public LBも採否判定に使わない。

## 変更対象と範囲

- 外部実験repoに専用config `configs/cpu-openpool-4view-svc-v15.json` と独立runner `src/cpu_openpool_svc.py` を追加する。
- 実行はCPUのみ。既存のCPU baseline/artifacts、GPU runner/config、candidate02/04の実行中プロセスを変更しない。
- 各foldで保存済みGroupKFoldのtrain側official行と、Open Pool v15から同じラベル数だけ抽出した行を使う。fold validationのpromptに近似一致するpool prompt group（char/word TF-IDF cosine >=0.40）を先に除外し、official train回答との完全正規化text重複も除く。publisherの`match_weight`は参照しない。
- 4-view特徴はraw word 1–3-gram、char 3–5-gram、word-shape 2–6-gram、function-word 1–3-gram。LinearSVCで学習し、OOF decision scoresと予測をfoldごとに保存する。

## 評価・採否

- Primary: 既存保存済み5-fold GroupKFold。2,699行それぞれがvalidationに一度だけ現れ、promptがfoldを跨がないことを確認する。
- OOF BA、fold別BA/平均/標準偏差、class recall、混同行列、文章長bin別指標を保存し、既存CPU best OOFとのprompt単位paired bootstrap（2,000回以上、seed 42）を行う。
- Primaryで改善し、資源・品質監査を通過した場合だけ、既存候補と同じ`GroupKFold(n_splits=5, shuffle=True, random_state=42)`のconfirmation OOFと同split baselineを作成して比較する。
- 予測/feature artifactはOOFの採否を確認するまで提出用fitに使わない。testは利用しない。

## 資源条件と検証方法

- 学習前にCPU affinity、MemAvailable、現行GPUプロセスへの影響、pool/officialデータhashを確認する。CPUスレッドは4以下、監視RSS上限32 GiB、MemAvailable下限16 GiBとする。条件を満たさない場合は開始しない。各foldの完了物を保存し、停止後は完了foldを再利用できるようにする。
- 実験実行そのものを検証に用い、fold coverage、prompt disjointness、pool cap/label counts、finite decision scores、OOF ID整合性をassertする。構文check以外の追加test suiteは依頼なしに実行しない。

## 根拠と注意

- Kaggle Discussion [0.672+ Dual-SVC BETTER](https://www.kaggle.com/code/ozertuu/0-672-dual-svc-better) は現行version 9のdata sourcesに複数のcommunity adapter・generated passage・annotation datasetを含み、metadata最終実行時刻と検索表示の実行時刻も一致しない。Public LB値0.672は投稿者表記であり、データの来歴と再現を確認できない。手法の着想のみ参考にし、これらの入力は使わない。
- Discussion [single-model results](https://www.kaggle.com/competitions/name-that-llm/discussion/754860) のQwen3-8B / Open Pool v10の0.6224 OOF・0.628 LBも投稿者申告であり、本候補の性能根拠とは区別する。
