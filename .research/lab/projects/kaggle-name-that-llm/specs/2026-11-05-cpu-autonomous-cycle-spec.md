---
date: 2026-11-05
project: kaggle-name-that-llm
source: brainstorm
status: approved
execution_status: not-started
tags: [spec, experiment, goal, cpu]
---

# Name That LLM CPU自動実験サイクル Spec

## 目的と承認

公式Starterを再現可能な比較基準として実装し、共通の評価で改善候補を比較する。ユーザーが2026-11-05に運用案とOOM回避条件へ「OK」と回答したため、合意内容を本specに保存する。実装・実験の開始指示は、このspecを参照するgoalの開始時に受ける。現時点でgoal・実装・実験は未開始。

元の運用案: [自動goalのbrainstorm](../../../../secretary/notes/brainstorm/2026-11-05-kaggle-autonomous-goal.md)。調査根拠: [公開Notebook比較](../experiments/2026-11-02-public-notebook-comparison.md)。

## 問いと仮説

公式Starterに対し、表記・句読点・機能語等を保持する特徴と線形分類器の小規模な変更で、同じprompt分割上の識別性能が改善するか。改善が得られなくても、再現可能な基準と失敗理由の整理を成果とする。

## 変更・実行範囲

- 実装: `/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/{src,configs,notebooks}/`。必要なrunnerと検証用テストの追加、Kaggle環境のpyproject/uv.lockへのML依存追加を含む。
- ローカル成果物: 同プロジェクトのartifacts/、必要な提出形式ファイルはsubmissions/。コンペデータはdata/。いずれもGit対象外。
- 研究記録: このプロジェクトのexperiments/、README。承認済み範囲内の各試行を理由・設定・結果とともに記録する。
- 公式コンペのtrain/test/sample submissionを利用。本人の参加・ルール同意を代行せず、取得権限が足りないときは必要な操作を報告する。秘密値を出力しない。
- 今回はCPUのみ。GPU・外部データ・有料API・Kaggleへの送信は含まない。GPU段階へ自動で拡張しない。

## 比較基準と許可する候補

公式Starter version 4のWord/char TF-IDF + Logistic Regressionを基準にする。

- Word: 1–2 gram、最大25,000特徴、sublinear_tf=True。
- Char: 3–5 gram、最大35,000特徴、sublinear_tf=True。
- 小文字化は公式設定のデフォルト、分類器C=2.0、max_iter=1000。
- 候補は最大5件。小文字化の有無、句読点token、char/word/shape/function view、Logistic Regression/LinearSVC、正則化・特徴数の小規模変更を許可する。
- 原則として一度に主要な変更を1つ選び、前の誤り分析や結果から理由を示す。変更設定を実行前に保存する。
- 公開checkpointやテスト集合のクラス均等化・クラスタ推定はこのCPUサイクルに入れない。

## 検証方法

1. 入力列・欠損・id・model・prompt_idを確認し、データhashを残す。想定と異なる行数を固定値に合わせて加工しない。
2. GroupKFold 5分割を一度作成して保存し、全候補で共有する。promptがtrain/validationに跨らないこと、各行が1回だけvalidationになることを検証する。
3. TF-IDFの語彙・IDF等は各foldの学習側だけでfitする。
4. 主指標は全行OOFのbalanced accuracy。fold別スコアと平均・標準偏差、class recall、文章長別の誤りを保存する。
5. baselineと各候補のOOF・設定・実行環境・コードrevisionまたはhash・時間・メモリ・終了状態を保存する。
6. OOFのid対応、予測ラベル、有限性、指標の再計算、出力ファイルの整合性を検査する。再実行コマンドを残す。
7. 改善はbestに対して主指標が1e-9を超えて増える場合とする。同じCVへの探索的適合を含むため、小差を確実な汎化改善と断定しない。

## OOM回避と資源制限

- CPU試行のGPUはCUDA_VISIBLE_DEVICESを空にして不可視にする。
- CPUは合計8 thread以内、同時CV jobは最大2。2 job時は各jobの数値計算threadを4以内にする。複数候補の同時実行はしない。
- 子プロセスを含む実験のRSS合計は32GiBを上限とし、ホストのMemAvailableが16GiB未満になった場合も、その実験の新規処理を止め、自分の子プロセスだけを終了する。
- runnerの実装時に、委譲されたcgroup等による強制上限の利用可否を確認する。利用できない場合は監視による中断を使い、監視間隔による瞬間超過の可能性を記録する。メモリ不足が疑われるときはCVを1 jobに減らす。
- メモリエラー時は設定とログを残す。同じ失敗設定を繰り返さず、許可範囲の特徴数/並列度縮小で1回だけ再試行する。結果比較への影響を記録する。
- 既存プロセス、GPU設定、他研究のファイル・実行状態は変更しない。

後続のGPU段階では[141/142の診断と選定条件](../experiments/2026-11-05-gpu-availability.md)を計画へ引き継ぐ。観測時の141 GPU 0を固定予約として扱わず、起動直前に再診断する。pilot・VRAM余裕・UUID固定・既存ジョブへの非干渉を含め、対象モデルのspecを具体化してから利用する。

## サイクルと終了条件

実行前の仮説・設定保存 → 同一foldで評価 → baseline/bestと比較 → 採用/棄却と誤り分析を記録 → 次候補選定。

- baseline + 最大5候補を完了、3候補連続で改善なし、または実験プロセスの累積経過時間2時間に到達した時点で探索を終了する。
- 各試行には残り実験時間以内のtimeoutを設ける。2時間は実験プロセスの予算で、資料読み込み・実装・依存構築の時間とは区別して報告する。
- 探索終了後は結果の検証と最終報告を仕上げる。時間上限で未完了の候補を完了扱いにしない。
- 権限・参加同意・環境障害で必要な処理ができない場合は、可能な準備・診断と具体的な不足を残す。goalの状態管理は実際のツール契約に従う。
- token予算はユーザーから指定されていないため、goal作成時に独自のtoken数を設定しない。

## 完了成果物

- 再実行可能なコードと依存、保存済み分割・config。
- baselineと実行した候補のOOF、比較表、class/文章長別の誤り分析。
- 最良候補または改善なしという判断の根拠、失敗・未実行・残る不確実性。
- experiments/の報告とREADMEの到達点・再開先。

## goal起動文

> このspecに従ってCPU自動実験サイクルを実装・実行し、再実行可能な最良候補と比較報告を完成させる。候補は結果から選び、最大試行数・3連続改善なし・実験時間上限・メモリ制限を守る。実装は指定したKaggleディレクトリ、知見はResearch Workspaceへ保存する。
