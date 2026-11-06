---
date: 2026-11-06
project: kaggle-name-that-llm
status: completed
tags: [experiment, cpu, tfidf, grouped-cv]
---

# CPU自動実験サイクルの比較結果

最終結果: 4-view＋Logistic RegressionのOOF BA **0.384504**（baseline **0.314479**、+7.00ポイント）。最良再CV・全件fit・保存モデル再推論・独立検査を完了。以下は実行前判断と中断履歴を保持し、末尾に最終比較報告をまとめる。

## 承認・実行条件

[承認済みspec](../specs/2026-11-05-cpu-autonomous-cycle-spec.md)と[引き継ぎ](2026-11-06-cpu-cycle-handoff.md)に従う。今回のgoal指示で実行開始承認を確認。範囲は取得済み公式データ、CPU、baseline＋最大5候補。主指標は共通のprompt-grouped 5-fold OOF balanced accuracy。bestを1e-9超上回った場合だけ改善とする。3候補連続改善なし、候補数上限、累積実験時間7,200秒のいずれかで探索終了。

実装正本: `/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm`。cycle: `artifacts/2026-11-06-cpu-cycle`。最大8 CPU、2 CV job（各4数値計算thread）、GPU不可視、実験RSS合計32GiB・ホストMemAvailable 16GiBの監視を使用。cgroup強制制限はなく0.25秒監視のため、瞬間超過は防ぎ切れない。最良候補の再CV・全件fit・保存モデル再推論の時間を探索予算から確保する。

2026-11-06 16:38 JSTに既存worker不在、既存cycleなし、MemAvailable約210GiBを確認。排他ロックを使い、既存コード・依存は変更せず再開。5件の合成データテストが11.043秒で成功（実データ性能の測定とは別）。

## 実行前の判断記録

- baseline `00-official`: 公式Starter v4のword 1–2 gram（25,000）＋char 3–5 gram（35,000）、小文字化、sublinear TF、Logistic Regression C=2、max_iter=1000。まず実測OOFのclass recall・混同・長さ別誤りを確認して次候補を決める。
- 候補1 `01-case-preserved`: baseline OOF BA=0.314479、60語以下のaccuracy=0.227194。Gemini 3.8→3.7が52件、GPT sol→lunaが40件。内容語以外の表記差を残す仮説で、word/charの`lowercase=False`だけを変更する。C・特徴数・token設定は同じ。独立検査成功後にbaselineと比較する。
- 候補2 `02-punctuation`: 候補1がBA=0.315963（baseline比+0.001484）で暫定best。ただし小差のため確実な汎化改善とは断定しない。大文字保持を維持し、word viewのtoken_patternだけを`(?u)\b\w\w+\b|[^\w\s]`へ変え、元の2文字以上の語に句読点を追加する。短文や同系列モデルの文体差を捉える仮説。C・特徴数は同じ。
- 候補3 `03-linear-svc`: 候補2のBA=0.342640（候補1比+0.026677、baseline比+0.028161）を受け、同じ2 view・C=2のまま分類器だけをLinearSVCへ変更。marginによる識別で残る重なりを減らせるか検証する。収束用max_iter=5000、random_state=42。候補2の独立検査成功を確認してから起動。
- 候補4 `04-shape-view`: 候補3のBA=0.330773はbest比−0.011867で不採用。候補2のLRへ戻し、shape char 3–5 gram（最大8,000特徴、weight=0.5）だけを追加。単語をX/xへ置換し、prompt内容への依存を抑えた表記・句読点の並びで、短文や同系列の混同を減らせるか検証する。既存word/char・Cは変更しない。
- 候補5 `05-function-view`: 候補4がBA=0.372289（候補2比+0.029650）へ改善。内容語をCONTENTに置換し、機能語・句読点を残すfunction word 1–3 gram（最大8,000特徴、weight=0.5）だけを追加する。語の内容によらない構文・文体の違いがshapeに上乗せできるか確認。これが最後の候補で、結果に関係なく候補数上限で探索終了し、bestの再現確認と全件fitへ進む。

## 16:54 JST時点の途中結果・一時停止履歴

ユーザーの「一旦止めれる？/goal」に従い、2026-11-06 16:53:40 JSTに候補1のsupervisorへSIGINTを送り、自分のworker/子プロセスを終了。16:53:51 JSTに生きた`cpu_experiment.py` / `cpu_worker.py`がないことと排他ロックの取得を確認した。中断した候補を性能比較の完了試行として扱わない。

| 試行 | 状態 | OOF balanced accuracy | fold平均 ± 標準偏差 | 実験時間 |
|---|---|---:|---:|---:|
| データprepare | 成功 | — | — | 1.658秒 |
| baseline `00-official` | 成功・独立検査pass | 0.3144792443450161 | 0.314496 ± 0.015334 | 47.723秒 |
| 候補1 `01-case-preserved` | ユーザー指示により中断 | 未確定 | 未確定 | 19.895秒 |

累積69.276秒、残り約7,130.724秒。中断時間は最終監視sample 19.688秒より長いsupervisor開始～終了のwall-clock区間19.895秒を計上し、終了処理を含めた保守的な消費時間とした。テスト時間11.043秒は合成データでの実装検証として別記。

baselineは5 foldすべて収束。class recallはclaude-fable-5 0.093960、glm-5.3 0.146667、gpt-5.6-sol 0.146667などが低く、gemini-3.1-pro-preview 0.680000、claude-opus-5 0.600000が高い。長さ別accuracyは60語以下0.227194（581件）、61–120語0.299228（1,036件）、121–180語0.350565（619件）、180語超0.410367（463件）。これらは同じ探索用CVの実測で、非公開testの性能を保証する値ではない。

## 保存済み成果物と再開位置

cycle相対パス:

- `data_manifest.json`: 公式ファイルhash、件数、欠損0、重複文章0。train 2,699件・18クラス・150 prompt。claude-fable-5のみ149件、他クラス150件。
- `folds.parquet`: 全foldで30 prompt、行数は540/540/540/540/539。SHA-256 `0569600bdc2aea862b207828218770ba84e2a696faa1d19bf2617a04355f65a4`。
- `source/`: 初期化時のコード・uv.lock・pyproject・承認済みspecスナップショット。
- `01-00-official-candidate/`: `oof.parquet`、`scores.npz`、`metrics.json`、`fold_metrics.json`、`audit.json`（pass）、config、command、環境、worker/resourceログ。最大RSS約1.531GiB。
- `02-01-case-preserved-candidate/`: 中断ログ・config・command・環境・resourceログ。OOF/CVは未完了。
- `cycle.json`: 中断理由、終了状態、時間会計、ユーザー指示による一時停止を記録。

再開時は同じcycleのstatusと生きたworkerを再確認する。initし直さない。候補1の中断はrunnerの候補枠・連続改善なしの計数対象で、同一configの通常再試行は現runnerが拒否する。再開処理の選択時にこの制約を確認し、既存台帳を書き換えて成功扱いにしたり二重起動したりしない。現時点でそのためのコード変更・追加試行はしていない。

最良候補の最終選定、再CV、全件fit、保存モデル再推論、最終比較報告は未完了。現時点で成功済みの比較基準はbaselineのみ。ユーザーが再開を指示するまで追加実験は実行しない。

## 16:57 JSTからの再開

ユーザーの「再開して」を受領。実行中worker/supervisor不在、MemAvailable約208GiBを再確認。既存cycle・分割・データ・pipeline・worker・uv.lockを維持する。

上記の中断再試行制約は、runnerのみに`--resume-interrupted`を追加して解消する。ユーザー指示で中断した同一configだけを明示的に再開でき、元のinterruptedレコード・消費時間は保持する。候補枠は同名で1件、時間は全attemptの合計、OOM再試行は別に1回のまま。モデル実装・指標・探索範囲には変更しない。元コードのsnapshotを残し、修正版runnerのsnapshotとhashも保存する。これはユーザー指示による中断からの再開処理であり、失敗候補の追加探索を許可する変更ではない。

修正後6テストが11.385秒で成功。`source-user-resume/`へrunnerとtestを保存。候補1の再開CVが48.364秒で成功し、独立検査pass、全fold収束、BA=0.31596321153368134。中断attempt 19.895秒は台帳に保持し、同名候補の成功attemptで改善判定を行う。

## 探索終了・最良候補の選定

候補5がBA=0.3845041014168531へ改善（候補4比+0.012215、baseline比+0.070025）。baseline＋5候補が完了したため探索終了。候補5 `05-function-view`を選定する。全候補の独立検査が成功し、全foldが収束。探索終了時の累積実験時間は316.863秒で、再現確認・fitの予算は十分残っている。

最良候補のconfigを変えず、`run --purpose reproduction`で再CVする。再現確認は新規候補数に含めず、同じid順のOOF全列・ラベル・有限scoreとBAの一致を検証する。その後、同じconfigで全trainをfitし、保存したmodel.joblibからtestを再推論して提出形式ファイルとの一致を検証する。


## 最終比較報告（2026-11-06 17:09 JST）

**採用: `05-function-view`、OOF balanced accuracy 0.384504。baseline 0.314479から+0.070025（+7.00ポイント）。同一configの再CV、全件fit、保存モデルの再推論まで完了。**

探索はbaseline＋5候補で終了。候補3のLinearSVCは不採用、他の改善は順に暫定bestへ採用した。新規候補は5件で、中断候補の同一config再開と最良候補の再CVは追加候補に数えていない。実データCVは7完了＋ユーザー指示による1中断。下表の時間・RSSは成功した探索CVの値で、中断・再現・fit等は後段の累積資源にすべて含める。

| 設定 | 主な変更 | OOF BA | baseline差 | fold平均 ± SD（ddof=0） | 秒 | 最大RSS GiB | 成果物 |
|---|---|---|---|---|---|---|---|
| [00-official](/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/configs/00-official.json) | 公式baseline | 0.314479 | +0.000000 | 0.314496 ± 0.015334 | 47.723 | 1.531 | [OOF](/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/artifacts/2026-11-06-cpu-cycle/01-00-official-candidate/oof.parquet) |
| [01-case-preserved](/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/configs/01-case-preserved.json) | 大文字保持 | 0.315963 | +0.001484 | 0.315964 ± 0.009935 | 48.364 | 1.531 | [OOF](/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/artifacts/2026-11-06-cpu-cycle/03-01-case-preserved-candidate/oof.parquet) |
| [02-punctuation](/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/configs/02-punctuation.json) | ＋句読点token | 0.342640 | +0.028161 | 0.342631 ± 0.018633 | 48.946 | 1.527 | [OOF](/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/artifacts/2026-11-06-cpu-cycle/04-02-punctuation-candidate/oof.parquet) |
| [03-linear-svc](/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/configs/03-linear-svc.json) | 分類器をLinearSVC | 0.330773 | +0.016294 | 0.330779 ± 0.010105 | 33.446 | 1.180 | [OOF](/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/artifacts/2026-11-06-cpu-cycle/05-03-linear-svc-candidate/oof.parquet) |
| [04-shape-view](/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/configs/04-shape-view.json) | 候補2＋shape | 0.372289 | +0.057810 | 0.372299 ± 0.019745 | 53.267 | 1.562 | [OOF](/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/artifacts/2026-11-06-cpu-cycle/06-04-shape-view-candidate/oof.parquet) |
| [05-function-view](/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/configs/05-function-view.json) | 候補4＋function（採用） | 0.384504 | +0.070025 | 0.384521 ± 0.021588 | 63.564 | 1.675 | [OOF](/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/artifacts/2026-11-06-cpu-cycle/07-05-function-view-candidate/oof.parquet) |

全完了CVのfoldが収束し、警告は0件。独立検査でid順、prompt分離、1行1回のvalidation、ラベル/score列順、有限性、fold指標、全class recall、長さ別accuracyとBAを再確認した。OOF全行のBAを主指標とし、fold平均と混同しない。

### 最良設定・再現条件

Logistic Regression C=2.0、max_iter=1000、random_state=42。全viewでsublinear TF、各view内L2正規化、word/charの小文字化なし。word 1–2 gram（25,000特徴、元の2文字以上の単語＋句読点）、char 3–5 gram（35,000）、shape char 3–5 gram（上限8,000、weight=0.5）、function word 1–3 gram（8,000、weight=0.5）。word/charのweightは1。shapeは単語を大文字のみならX、それ以外ならxへ置換。functionは機能語・句読点を残し、内容語をCONTENTへ置換する。shapeの実語彙数はfoldごとに3,086–3,689で、上限8,000と区別する。

GroupKFold 5分割はshuffleなし・prompt_idで固定（各fold 30 prompt、540/540/540/540/539行）。分割生成の乱数seedは使用しない。各foldの語彙・IDFは学習側だけでfit。分類器seed=42、PYTHONHASHSEED=0、数値演算はfloat64。文章長bucketは全試行で同じ閾値を使用。

実行環境: host `142-X10DAi`、Python 3.12.3、依存はcycleのuv.lockで固定。実測version: numpy 2.5.4, scipy 1.18.1, pandas 3.1.1, scikit-learn 1.9.1, pyarrow 26.0.1, psutil 7.2.2, joblib 1.6.0, threadpoolctl 3.7.0。実装ディレクトリはGitリポジトリではないため、revisionの代わりにコードhashとsnapshotを保存した。モデル/worker/lockは全比較で不変。runnerのみユーザー中断の明示再開処理を追加した。

- pipeline SHA-256: `20495f7c0e49166bee6dcf7c17cb0d24e8ac78ba34f6f4d8de402baf59d0797d`
- worker SHA-256: `415acba2ef65cf14491ea4befa00fe6bee2d5d294c68c41e48d65bfea2748d01`
- uv.lock SHA-256: `e779b31140df324c7cbef4d000a5cd0aab10187c04d3ee410615a30c02f350a5`
- 現在のrunner・finalizerを含む全コードhash: [final_audit.json](/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/artifacts/2026-11-06-cpu-cycle/final_audit.json)。開始時snapshotは`source/`、再開修正は`source-user-resume/`、最終コードは`source-final/`。

### class recall・文章長・混同

| class | 件数 | baseline recall | best recall | 差 |
|---|---|---|---|---|
| claude-fable-5 | 149 | 0.093960 | 0.161074 | +0.067114 |
| claude-opus-4-6 | 150 | 0.373333 | 0.453333 | +0.080000 |
| claude-opus-4-8 | 150 | 0.266667 | 0.300000 | +0.033333 |
| claude-opus-5 | 150 | 0.600000 | 0.593333 | -0.006667 |
| claude-sonnet-5 | 150 | 0.300000 | 0.446667 | +0.146667 |
| gemini-3.1-pro-preview | 150 | 0.680000 | 0.766667 | +0.086667 |
| gemini-3.6-flash | 150 | 0.433333 | 0.480000 | +0.046667 |
| gemini-3.7-flash | 150 | 0.386667 | 0.433333 | +0.046667 |
| gemini-3.8-flash | 150 | 0.266667 | 0.426667 | +0.160000 |
| glm-5.3 | 150 | 0.146667 | 0.186667 | +0.040000 |
| glm-5.3-flash | 150 | 0.153333 | 0.213333 | +0.060000 |
| gpt-5.5 | 150 | 0.266667 | 0.306667 | +0.040000 |
| gpt-5.6-luna | 150 | 0.286667 | 0.346667 | +0.060000 |
| gpt-5.6-sol | 150 | 0.146667 | 0.180000 | +0.033333 |
| gpt-5.6-terra | 150 | 0.280000 | 0.286667 | +0.006667 |
| gpt-6-astra | 150 | 0.446667 | 0.606667 | +0.160000 |
| kimi-k3 | 150 | 0.266667 | 0.266667 | +0.000000 |
| qwen3.8-max | 150 | 0.266667 | 0.466667 | +0.200000 |

qwen3.8-max（+0.200000）、gpt-6-astra（+0.160000）、gemini-3.8-flash（+0.160000）、claude-sonnet-5（+0.146667）などで改善。claude-opus-5は−0.006667、kimi-k3は変化なしで、全クラス一律の改善ではない。claude-fable-5（0.161074）、gpt-5.6-sol（0.180000）、glm-5.3（0.186667）は依然低い。

| 語数 | 件数 | baseline accuracy | best accuracy | baseline bucket BA | best bucket BA |
|---|---|---|---|---|---|
| <=60 | 581 | 0.227194 | 0.289157 | 0.223870 | 0.277097 |
| 61-120 | 1036 | 0.299228 | 0.369691 | 0.300630 | 0.372861 |
| 121-180 | 619 | 0.350565 | 0.429725 | 0.345712 | 0.431894 |
| >180 | 463 | 0.410367 | 0.477322 | 0.383326 | 0.453115 |

全bucketでaccuracyは上昇したが、60語以下は依然0.289157で最も難しい。bucket BAはそのbucketに存在するクラスのrecall平均で、全OOF主指標の分解ではない。baselineの誤りを361件修正し、正解を172件誤りへ変更（正解件数の純増189）。全体accuracyは0.314561→0.384587。

| true | predicted | baseline件数 | best件数 |
|---|---|---|---|
| gemini-3.8-flash | gemini-3.7-flash | 52 | 43 |
| gemini-3.7-flash | gemini-3.8-flash | 41 | 40 |
| glm-5.3 | glm-5.3-flash | 15 | 33 |
| glm-5.3-flash | glm-5.3 | 28 | 32 |
| gpt-5.6-sol | gpt-5.6-luna | 40 | 31 |
| gemini-3.6-flash | gemini-3.7-flash | 37 | 30 |
| gpt-5.6-sol | gpt-5.6-terra | 25 | 28 |
| gpt-5.6-terra | gpt-5.6-luna | 28 | 27 |

Gemini 3.8→3.7、Gemini 3.7→3.8、GPT sol→lunaなどの混同は残る。GLM同士の一部混同は増加しており、総BAの改善だけで全混同の解消とは扱わない。

| fold | validation件数 | baseline BA | best BA | 差 |
|---|---|---|---|---|
| 0 | 540 | 0.294444 | 0.359259 | +0.064815 |
| 1 | 540 | 0.298148 | 0.359259 | +0.061111 |
| 2 | 540 | 0.320370 | 0.412963 | +0.092593 |
| 3 | 540 | 0.331481 | 0.396296 | +0.064815 |
| 4 | 539 | 0.328033 | 0.394828 | +0.066794 |

### 再現確認・全件学習・出力整合性

- [最良候補の再CV](/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/artifacts/2026-11-06-cpu-cycle/08-05-function-view-reproduction): config hash同一、BA差0、2,699行のOOF全列が完全一致。scoreの最大絶対差は0（判定許容値1e-12）。新しい分割を作らず、同じ保存分割を使用。
- [全件fit](/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/artifacts/2026-11-06-cpu-cycle/09-05-function-view-candidate): train 2,699行で学習した[model.joblib](/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/artifacts/2026-11-06-cpu-cycle/09-05-function-view-candidate/model.joblib)、[top_features.json](/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/artifacts/2026-11-06-cpu-cycle/09-05-function-view-candidate/top_features.json)、test score、[submission.parquet](/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/artifacts/2026-11-06-cpu-cycle/09-05-function-view-candidate/submission.parquet)を保存。これはローカル出力で、Kaggleへ送信していない。
- [保存モデルの再推論](/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/artifacts/2026-11-06-cpu-cycle/10-predict-candidate): model.joblibを別workerで再loadして推論し、全件fit時のid/modelと完全一致。公開test 3件についてid一意性・順序・列・欠損・ラベル集合・sample_submissionとの対応を検証。公開3件から非公開testの規模・精度は推定しない。
- [最終独立検査](/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/artifacts/2026-11-06-cpu-cycle/final_audit.json)はpass。[比較CSV](/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/artifacts/2026-11-06-cpu-cycle/comparison.csv)、[全候補class recall CSV](/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/artifacts/2026-11-06-cpu-cycle/class_recall.csv)、[全候補長さ別CSV](/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/artifacts/2026-11-06-cpu-cycle/length_metrics.csv)、[成果物hash manifest](/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/artifacts/2026-11-06-cpu-cycle/artifact_manifest.json)も保存。

### 時間・メモリ・停止条件

累積実験時間 **403.896秒（6.73分）/ 7,200秒**、残り6796.104秒。prepare、中断19.895秒、全候補CV、最良再CV、全件fit、再推論を含む。資料読み込み・修正・依存構築・合成データテスト・成果物検査/文書集計は実データ学習の予算と分けて扱う。今回の合成テストは変更前5件11.043秒、再開修正後6件11.385秒で成功。

監視された最大実験RSS合計 **1.675GiB / 32GiB**、最小ホストMemAvailable **206.224GiB / 下限16GiB**。CPU affinityは8論理CPU、CV 2 job・各4数値thread。GPUは不可視。OOM・timeoutなし。0.25秒監視で、委譲cgroupの強制上限はなく瞬間超過を完全には防げない。

全実験の開始/終了区間が重ならないこと、最終時点でworker/supervisorと実験process groupの生きた子がないことを検査。途中で実行中にstatusを要求した際は排他ロックで拒否され、追加workerは起動していない。ユーザー中断1件は失敗性能として採否判断せず履歴として保持し、同じconfigで再開済み。最後は候補数上限に到達したため終了し、予算が残っていても追加探索しない。

### 再実行コマンド・残る不確実性

既存cycleの再検査（モデルの再学習なし）:

```bash
cd /mnt/HDD10TB-2/aburatani/kaggle
.venv/bin/python name-that-llm/src/cpu_finalize.py --cycle name-that-llm/artifacts/2026-11-06-cpu-cycle
```

依存復元には保存したuv.lockとPython 3.12環境を使用する。新しいcycleで同じ6設定・best再CV・fit・再推論を順番に再実行するコマンド列は[reproduce_cycle.sh](/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/artifacts/2026-11-06-cpu-cycle/reproduce_cycle.sh)へ保存した。既存cycleの破壊や二重起動を避けるため、新規パスを必須とする。スクリプト自体による追加の全再実行は今回行っていない。各実測の正確なargvは各attemptのcommand.jsonにある。

同じ探索用CV上で5候補を選んだ結果であり、独立した未使用holdoutやPrivate LBでの改善は未確認。再CV一致は実装・数値計算の再現性を示し、独立データでの汎化検証ではない。小文字化・句読点・shape・functionの効果はこの順序と設定での条件付き比較で、完全なfactorial ablationではない。外部データ、GPU、有料API、testクラス均等化・クラスタ推定、Kaggle送信は実施していない。今回選んだ5候補と必須工程に未完了はない。GPU段階などは別specで扱う。
