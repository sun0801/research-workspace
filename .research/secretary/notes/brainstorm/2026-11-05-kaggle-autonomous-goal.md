---
date: 2026-11-05
project: kaggle-name-that-llm
source_todo: null
topic: goalによる自動実験サイクル
status: promoted-to-spec
tags: [brainstorm, kaggle, goal, automation]
---

# goalによる自動実験サイクル — 初回運用案

## 読み込んだ文脈

- プロジェクトREADMEと2026-11-02の公開Notebook比較。
- 最上位AGENTSのImplementation Gate、brainstorm/kaggle-workflowスキル。
- 当日のTODOは未作成、MTG議事録なし、承認済み実験specなし。
- 利用可能なgoal作成・状態取得・完了等の管理ツールを確認。現在のgoalは未設定。
- [OpenAI公式のGoals説明](https://developers.openai.com/cookbook/examples/codex/using_goals_in_codex)、[長時間作業の説明](https://learn.chatgpt.com/docs/long-running-work)を確認。

## 相談の出発点

ユーザーはgoal機能を使い、Kaggleのサイクルを毎回「続けて」と言わずに自動継続させたい。現時点の発言は利用可能性と運用方法の相談で、実験範囲・資源上限・spec保存と実装開始の承認はまだ確定していない。

## 問いと仮説

問い: 検証と知見保存を維持しながら、自動で仮説・変更・評価・次の候補選定を進められるか。

仮説: 固定した分割と指標、許可した探索範囲、計算量の上限、成果物と終了条件を一度合意すれば、範囲内の各試行で再確認せずにサイクルを継続できる。

## 方式の比較

| 方式 | 向く用途 | 条件 |
|---|---|---|
| この会話のgoal | 結果を見て次の作業を選ぶ調査・改善 | セッションと実行環境が利用可能で、達成条件が明確 |
| 定時の収集ジョブ | 毎日の新着一覧取得 | 別途スケジュール・認証・実行環境が必要 |
| 実験runnerとgoalの併用 | 実験の時間制限・ログ・再開と、AIによる次候補選定 | runnerは承認後に実装。goalは同じsandbox/承認制約に従う |

最初はgoal + 小さなCPU実験runnerを候補にする。goal開始は権限の拡大や、電源断・切断後の実行保証を意味しない。IDE等のセッションと作業環境を利用可能にしておく。

## 初回goalの具体案

### 目的と範囲

公式Starterを比較基準として、再現可能なCPU分類実験を行い、許可範囲内で改善案を比較し、根拠付きの採用判断を残す。スコアが必ず上がることは終了条件にしない。

- コード変更先: `/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/{src,configs,notebooks}/`。必要なML依存はKaggle環境のpyproject/lockへ追加する範囲を含める。
- 実験データ: 公式train/test/sample submission。参加・ルール同意と取得権限を確認して取得する。画面上の同意を代行しない。
- 探索範囲: TF-IDFの文字/単語/句読点/shape/function view、Logistic Regression/LinearSVC、正則化と特徴数の小規模な変更。
- 外部データ・GPU・有料API・Kaggleへの提出は初回goalの範囲に含めない。必要なら次の段階を別途具体化する。

### 評価と成果物

- 最初にGroupKFold 5分割を固定・保存し、全候補に共通で使用する。
- 語彙・IDF等は各foldの学習側だけでfitする。
- 主指標: 全行OOFのbalanced accuracy。fold別スコア・class recall・文章長別の誤りも残す。
- 基準の設定は公式Starterに揃える。実行並列度だけは資源上限に合わせる。
- baseline + 最大5つの改善候補。候補はそれまでの誤り分析から選び、変更理由を記録する。
- 各試行にconfig・データhash・fold表・OOF・指標・所要時間・失敗情報を保存。改善だけでなく棄却理由をMarkdownへ残す。
- 同じ分割への適合が起こりうるため、小さなCV差を確実な汎化改善と断定しない。未実施のLB/Private改善を主張しない。
- 最終成果物: baselineと最良候補の再実行可能なコード・比較表・誤り分析・次の仮説。必要なら提出形式のローカル整合性検査まで行い、送信しない。

### 資源上限と終了条件（提案値）

- CPUは最大8 thread、CVは最大2 job。実験プロセスの合計経過時間は2時間を目安上限とし、新規試行を開始する前に残り時間を確認する。実験runnerにも各試行のtimeoutを設ける。
- baseline + 5候補の比較完了、3候補連続で主指標の改善なし、または実験時間上限到達時に、得られた結果で最終報告する。
- 基準実験を再現できない場合は診断・修正を優先する。権限・同意など本人操作が必要な障害は、できた作業と不足を報告する。
- goal機能側のtoken/利用量上限は別管理。ユーザーがtoken数を指定していないため、この案ではtoken予算を設定しない。
- goalのpause/resume/予算制限は実際のツール契約に従う。実験の終了条件とgoal自体の状態変更を混同しない。

### 自動サイクル

仮説を1つ選ぶ → 変更とconfigを記録 → 同じfoldで評価 → baseline/最良候補と比較 → 採用/棄却と理由を保存 → 次の仮説へ。

## goal文案

> 承認済みCPU実験specに従い、Name That LLMの公式Starterを再現して、許可されたTF-IDF/線形分類器の範囲でbaselineと最大5つの改善候補を比較する。共通のprompt-grouped 5-foldでOOF balanced accuracyを評価し、設定・予測・失敗・誤り分析を保存する。試行結果から次の候補を選び、3候補連続で改善なし、実験時間上限、または全候補終了時に、再実行可能な最良候補と根拠付き比較報告を完成させる。GPU・有料API・外部データ・Kaggle提出は使わない。実装と成果物は指定のKaggleディレクトリへ、研究知見はResearch Workspaceへ記録する。

## Spec化候補と開始条件

承認後のspec予定パス: `.research/lab/projects/kaggle-name-that-llm/specs/2026-11-05-cpu-autonomous-cycle-spec.md`。

一度の返信でこの運用案、spec保存、記載範囲の実装開始を明示的に承認してもらえば、その承認を保持して各試行を継続できる。毎回の試行に再承認を要求しない。現時点ではspec未保存、goal未作成、実験未開始。

## 未解決の問い

- この初回CPU範囲と提案上限を採用するか。
- コンペ参加・ルール同意が済んでいるか。未確認でも調査・実装準備の範囲を進め、データアクセスに必要なら本人に確認する。
- 後続のGPU段階の予算・利用条件・到達目標。今回のCPU案から自動でGPU段階へ拡張しない。

## 関連ファイル

- [プロジェクト正本](../../../lab/projects/kaggle-name-that-llm/README.md)
- [Notebook比較](../../../lab/projects/kaggle-name-that-llm/experiments/2026-11-02-public-notebook-comparison.md)


## 追記 — 141/142の選定とOOM回避

ユーザーから運用案への概ねの賛同と、141/142内の未使用または十分余裕のあるGPUを選び、OOMを避けたいとの要望があった。読み取り診断の結果は[GPU診断記録](../../../lab/projects/kaggle-name-that-llm/experiments/2026-11-05-gpu-availability.md)に保存した。

2026-11-05 03:11 JSTでは141 GPU 0が技術的な第一候補。141 GPU 1は稼働中で、他研究の学習先にも指定されているため候補から外す。現在の空き状況を固定の予約や将来の保証にはしない。

初回のCPU goalではGPUを使わず、ホストRAMも監視する。後続のGPU実験では、141/142のみを毎回診断し、既存計算プロセスのないGPUを優先してUUIDで固定する。最小batchかつ想定最大sequence長のpilotを先に行い、測定した使用量にmax(4GiB, 全VRAMの25%)の余裕を残せる場合に進める。該当GPUがなければGPU実験を待機/見送る。既存ジョブの停止・再起動・GPU resetは行わない。OOM時は自分の試行だけを止めて記録し、許可範囲の縮小再試行に回数上限を設ける。

141にはKaggle環境がまだないため、GPU段階で配置・依存の確認が必要。GPU段階のモデル・予算・検証範囲はCPU goalから自動で拡張しない。選定runnerは未実装で、今回の操作は読み取り診断と運用案更新まで。

## 追記 03:16 — specへ保存

ユーザーがOOM対策の説明後に「OK、あとはgoalで指定しとけばいいかな？」と回答。合意した初回CPU範囲と資源制限を[spec](../../../lab/projects/kaggle-name-that-llm/specs/2026-11-05-cpu-autonomous-cycle-spec.md)へ保存した。実装・実験はgoalの開始指示を受けて進める。現時点ではgoal未作成、コード変更・実験開始なし。
