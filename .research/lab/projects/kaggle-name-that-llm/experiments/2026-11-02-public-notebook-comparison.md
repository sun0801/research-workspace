---
date: 2026-11-02
last_updated: 2026-11-10
project: kaggle-name-that-llm
type: source-review
status: reviewed-not-executed
---

# 公開Notebook 3本の精読比較

開始結論: (c) 保留 — これはStarter・Two-stage LoRA・nlm-v27を並べた初期surveyで、個別候補の現在の試行判断には使わない。判断に必要な証拠は、特定version/sourceに紐づくprompt-grouped OOF、採用SVCとの同一split比較、依存物のlicense/provenance、提出runtime適合。

2026-11-02 JSTに取得したコードを実行せずに精読。自分たちの学習・推論・スコア再現は未実施。以下のセル番号は0始まり。

## 結論

最初の比較基準には公式Starterが適している。プロンプトを分ける検証がコードにあり、CPUで完結し、外部データや公開チェックポイントに依存しない。Two-stage LoRAは、追加データで学習して公式データへ適応させる次段階の候補。nlm-v27は多数の手法を学ぶ資料として有用だが、初回の実験基準としては構成と依存が大きい。

共通して重要なのは、分類器そのものと、テスト集合の構造を仮定する後処理を分けて評価すること。特に均等なクラス数を前提にした補正と、同一プロンプト内のモデル重複を許さない制約は、公式説明から当然に導けるものではない。

## 出典・バージョンと確認範囲

| 対象 | 取得時version | 確認した範囲 | 実行 |
|---|---|---|---|
| [公式Starter](https://www.kaggle.com/code/martynaplomecka/starter-notebook-for-name-that-llm-competition) | 4 | 4セル全体、メタデータ | 未実施 |
| [Two-stage LoRA](https://www.kaggle.com/code/nishantdahal/two-stage-lora-on-the-public-pool) | 2 | 11セル全体、説明・推論コード・学習レシピ・依存先メタデータ | 未実施 |
| [nlm-v27](https://www.kaggle.com/code/dhruvtibarewal/nlm-v27) | 1 | 6セル全体、生成される3つのPythonファイル、最終実行設定、依存先メタデータ | 未実施 |

公式MCPのget_notebook_infoが返したblob.sourceをCLIでpullしたNotebookと比較し、3本すべてでセル種別とソースが一致した。SHA-256と保存場所は[取得確認](2026-11-02-authenticated-notebook-discovery.md)を参照。get_notebook_infoの結果は各取得フォルダのmcp-info.jsonへ保存。

3本とも取得ファイルに保存済み実行出力はない。記載されたCV/LBは、コードによる計算手順の存在と、作者が説明文に記載した結果を区別する。現在の最高順位や手元での再現値とは扱わない。依存モジュール・重みの内部までは監査していない。

## 比較の全体像

| 項目 | 公式Starter | Two-stage LoRA | nlm-v27 |
|---|---|---|---|
| 中心手法 | Word/char TF-IDF + Logistic Regression | 4-view n-gram SVC + Qwen3 8B/14BのLoRA + centred twin | 多数のLoRA・encoder・SVC・Gaussian group head・補助stack・ATLAS |
| 追加データ | なし | 約35k文章のpoolと公開adapter | 120k poolのadapter群、追加文章、公開モデル出力など |
| このNotebook内のCV | GroupKFold 5分割を実装 | 学習とCVの実装はなく説明文に記載 | simulation機能あり。ただし公開済み学習済みadapterのfold除外は別途確認が必要 |
| 計算資源の根拠 | コードはCPU、GPU無効 | 作者は本番推論を2x T4で約1時間、学習をRTX 5090と記載 | コード説明はT4x2。多数の推論passと時間予算を持つ |
| 初回に使う目的 | 再現可能な比較基準 | 追加データ適応と8Bの効果を検討 | 有力構成の分解、アンサンブル設計の参考 |

## 1. 公式Starter — 分かりやすい比較基準

セル2でPipeline内に2種類のTF-IDFとLogisticRegressionを置く。wordは1–2 gram、最大25,000特徴、charは3–5 gram、最大35,000特徴。sublinear_tf=True、分類器C=2.0、max_iter=1000。lowercaseを指定していないため、TF-IDFのデフォルトの小文字化を利用する。

GroupKFold(n_splits=5)、groups=prompt_id、scoring=balanced_accuracyをcross_val_scoreへ渡す。特徴量のfitもPipeline内なので、各foldの学習側から語彙とIDFを作る。CV後は全trainで再fitし、testの実際の行数に合わせてid/model列のsubmission.parquetを生成する（セル3）。

**取り入れる候補**: プロンプト単位の分割、Pipeline内での前処理fit、公式と同じ評価指標、行数を固定しない提出生成。

**不足**: OOF予測の保存、クラス別・文章長別の誤り分析、分割表・依存versionの記録、明示的な提出整合性チェックは追加候補。n_jobs=-1なので実行時のCPU数とメモリ並列度も決める必要がある。

公式Starterの実測スコアは今回のファイルからは得られない。以前のDiscussionにあるTF-IDFの0.343等は異なる設定の結果であり、このStarterのスコアとして転記しない。

## 2. Two-stage LoRA — 学習済みモデルの推論パイプライン

### 中心となる実装

セル3は文字・単語/句読点・形状・機能語の4-view TF-IDFを結合し、train + poolでLinearSVCをfitする。全viewでlowercase=False。形状viewは単語を大文字だけの単語ならX、それ以外ならxに置換する。機能語viewは機能語と句読点を残し、内容語をCONTENTへ置換する。

セル5はQwen3-8B/14Bの先頭部分だけをロードし、LoRAをbaseへmerge。checkpointのmeta.jsonにあるkeep/layers/max_lenに従い、複数層の平均pool + LayerNormから分類する。最初のtokenを平均から除き、final normをIdentityへ置換する。tokenizer・層・正規化・headのラベル順は訓練時と一致させる必要がある。

セル7はテスト文章の内容語TF-IDFで階層クラスタを推定し、2–18文章の群だけで特徴平均を引いたcentred headを追加。各memberのlog確率を重み付きで足す。セル9では50行以上のtestにSinkhorn補正を適用する。

### 作者が記載した学習と結果

セル10のレシピ: LoRA rank 16 / alpha 32 / dropout 0.05、plainとcentredの2head、同一promptの回答3件を単位に学習。Stage 1は34,940件の公開poolで1 epoch、Stage 2は公式2,699件で2 epochs。学習率はLoRA/headでStage 1が1e-4/1e-3、Stage 2が5e-5/5e-4。学習コードはこのNotebookに含まれない。

セル0の作者記載値は、8BのStage 1のみCV 0.483、Stage 2後CV 0.569。14BもCV 0.569。最終blendはgrouped 5-fold CV 0.593 / Public LB 0.592。分割表・OOF・訓練ログの独立検証は未実施。

作者は、RTX 5090でcheckpointあたり8B約30分・14B約90分、本番推論は2x T4で約1時間と記載。これは作者の報告で、このマシンでの実測や全fold分の総学習時間ではない。

### 注意点

- poolの句読点フィルタは、公式trainで各モデルに一度も現れなかった記号を使っている。CV時にvalidation foldも含む全trainでフィルタを決めていた場合、検証側の情報を利用するため、fold内fitの確認が必要。
- 説明文はtestのモデル数がおおむね等しいと仮定するが、[公式Evaluation](https://www.kaggle.com/competitions/name-that-llm/overview/evaluation)はモデルごとの件数が不均等で、Public/Private間の構成も異なると記載。Sinkhornは各クラスの確率質量を等しくする処理で、argmax後の件数が必ず等しくなるわけではない。Balanced accuracyがクラスを等重みにすることと、testの件数が等しいことを混同しない。効果は別途比較する必要がある。
- test側のクラスタ推定とcenteringは、単一文章だけの分類から集合全体に依存する処理へ変わる。trainの18回答を丸ごと使う検証結果を、回答数が不明のtestへそのまま外挿しない。
- fp16が非有限値になった場合にbf16で再試行するコードがある。旧GPUでの動作時間・数値挙動は未測定。
- train.csvなどを入力全体からglobして先頭一致で読む。複数の同名ファイルを付けると取り違える可能性があるため、再現計画では対象パスを明示する候補。

## 3. nlm-v27 — 大規模な構成を分解して読む

### 実際に有効な最終構成

セル5のMODELSはq14v5、q8v5、ll8v5、n14b、q25_14、DeBERTaの6member。v5の3memberはそれぞれ5fold + full-dataの6adapterを平均する。n14bとq25_14は単一adapter。したがって、名前の数だけで推論負荷を見積もれない。

セル2のinfer.pyは、LoRAのplain/twin、q14v5/q8v5のGaussian group head、4-view SVC、補助stackの予測、ATLASを合成し、Sinkhornと句読点guard、12–18件クラスタのHungarian assignmentを適用する。--perpassage 1でも、最終コマンドでは--adapt_w 1.0と--post 1が有効なので、プロンプト推定・centering・クラスタ後処理は動作する。

Gaussian group headは、特徴をclass効果 + prompt効果 + noiseで表し、prompt内残差に基づく次元削減と共分散推定を行う。2–3件の群はlabelの組合せを明示的に扱い、より大きな群は近似計算する。モデル重複を抑える制約を使うため、誤ったクラスタを作った場合の影響も評価対象になる。

### 補助stackと設定の読み違い

セル3のcomp_stack.pyは、n-gram、stylometry、frozen LM/encoder、LoRA、token attention、UltraBERT等を持つ。コードの最終部分はLOGITを保存し、その予測をメインが15%混ぜる。セル4でNTL_DROP_Q35=1にしているので、Qwen3.5のtoken-attention memberは外れる。

この補助stackのGATE_LAMとBALANCE_ALPHAは宣言だけで、最後の保存までに参照されない。family gateのスコアは計算されるが、LOGITを作る箇所には反映されない。変数名やコメントだけで「gateや50% balancingを適用している」と解釈しない。メイン側の句読点guard/Sinkhornとは別。

gauss.pyとcomp_stack.py内のGaussian関数16個は、AST比較で同一と確認。外部コードを実行した確認ではない。

### 検証・実行時間と再現性

- --simはprompt単位のholdoutと、promptごとに回答数を減らすsimulationを実装。ただし既存adapterをloadする処理は、holdoutに応じた訓練し直しや、該当fold以外のadapter選択を自動で行わない。full-dataでStage 2学習したadapterを含む設定をそのまま--simへ持ち込んでも、独立したOOFにはならない。
- 小さい対話test時には、train先頭40件や真のpromptを使うin-sampleチェックがある。訓練との整合確認であり、汎化性能のCVではない。
- ATLASは不確かな文章を優先し、残りtoken量から時間を予測して、予算を超えそうなら例外を出す。メインはその例外を捕捉してATLASを省略する。セル5の予算は8.3時間 − 補助stack時間 − 600秒。最終スコアの再現では、どの処理が実際に走ったかをログで確認する必要がある。
- 補助stackは別processで実行。メインは出力がなければCOMP SKIPPEDとして先へ進める。Notebookが最後まで走ったことだけでは、同じensembleを再現したことにならない。
- adapterを同じbaseへmerge/unmergeして順に処理する。数値精度やtokenizer/EOS、final norm、ラベル順、checkpoint anchorとの整合確認が重要。
- メインの冒頭セルは、最終MODELSでは使わない古いadapterも先に探索してassertする。入力を減らす場合には、実際の実行設定だけでなく、この初期化依存も確認する必要がある。
- このコードのPublic LBは保存出力にない。以前のDiscussionにあるnlm-v27の0.651は投稿者の比較報告で、今回のコードを手元で再現した値ではない。

## 依存と取得コスト

コードの重み取得は未実施。下記は2026-11-02に公式MCPが返したファイル要約・ライセンス表示。ディスク上のファイルサイズを、実行時VRAMとは扱わない。

| 依存 | 確認できた内容 |
|---|---|
| Qwen3-8B-Base / version 1 | 約16.39 GB、Apache 2.0表示 |
| Qwen3-14B-Base / version 1 | 約29.55 GB、Apache 2.0表示 |
| [Two-stageのcheckpoint + pool](https://www.kaggle.com/datasets/nishantdahal/ntl-two-stage-lora) | 11ファイル、合計317,728,259 bytes、CC-BY-SA-4.0表示 |
| [nlm v5 adapter群](https://www.kaggle.com/datasets/dhruvtibarewal/nlm-l24-adapters-v5) | 54ファイル、合計2,591,835,972 bytes、licenseはother表示 |
| [ATLAS bundle](https://www.kaggle.com/datasets/josephadamski91/ntl-atlas-qwen3-8b-v1) | メタデータ上のlicenseはother表示。内部コード・個別条件は未読 |

nlm-v27はメタデータ上、14 dataset・8 Notebook出力・8 model variationを入力に持つ。kernel_sourcesにGLM/encoder等の重みが含まれるため、model_sourcesだけを見ても依存は揃わない。Two-stageは1 dataset + 2 model variation、Starterはコンペデータのみ。

other表示を自由利用の根拠と解釈しない。実際に再利用する依存のREADME/LICENSEと公開状態を別途確認する。全入力のversionは、再現実験を行う際に固定する必要がある。

メタデータ原本: `/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/.cache/notebook-review/2026-11-02/`。

## このマシンとの対応

読み取り診断でRTX A4000（16,376 MiB）とRTX PRO 4500 Blackwell（32,623 MiB）、論理CPU 72、RAM約220 GiBを確認。現在の占有状況・優先利用可否は確認していない。

StarterのCPU基準はこの環境で検討しやすい。32GB GPUを使う8Bの小規模試行は次の候補だが、baseの一部だけをロードする設定、学習activation、optimizer、ライブラリ対応を含めた実測が必要。作者のRTX 5090の所要時間はこのGPUへ転用しない。2枚のVRAMを単純に合算して単一GPUと同等に扱わない。

## 次の候補と未決事項

1. 公式Starterを基準にする計画を作る。prompt単位の分割を記録し、OOF・class recall・文章長別の結果を残す候補。
2. 表記情報を残すTF-IDFや4-view SVCを段階的に比較する候補。追加データや後処理を同時に変えて改善原因が分からなくなることを避ける。
3. その後8Bの二段階学習または公開checkpointの独立した評価方法を計画化する。全trainを見たcheckpointをOOF評価へ混ぜない。
4. centered twin・Gaussian・Sinkhorn・ATLASは、それぞれ単独の寄与とテスト集合の仮定を調べる候補。

以上は調査からの提案で、承認済み実験specではない。実装開始前に、既存のImplementation Gateでspec・範囲・検証方法・承認を確認する。コンペ参加/ルール同意、GPU利用条件、予算・目標も未確認。

最終結論: (c) 保留 — 各Notebookの手法は独立したsource/versionと上記のOOF・provenance・runtime証拠で個別判断する。後続のsource audit/specを優先し、このsurvey単独ではGPU queueへ追加しない。
