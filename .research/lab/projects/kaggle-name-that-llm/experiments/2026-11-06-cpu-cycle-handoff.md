---
date: 2026-11-06
project: kaggle-name-that-llm
status: superseded-by-completed-cycle
tags: [handoff, cpu, goal, verification]
---

# CPU自動実験のCLI引き継ぎ

2026-11-06 17:09 JST追記: ユーザーの再開指示後、CPUサイクルは完了。baseline＋5候補を比較し、最良の4-view＋LRはOOF BA 0.384504（baseline 0.314479）、再CVのOOF/score完全一致、全件fit・保存モデル再推論・独立検査passを確認した。[最終比較報告](2026-11-06-cpu-cycle-results.md)が最新の入口。既存cycleを再初期化・追加探索しない。

2026-11-06 16:54 JST追記: 本文は実行開始前の引き継ぎ。現在は実データcycle作成・baseline CV完了後、ユーザーの指示で候補1を中断し一時停止している。最新状態と再開位置は[CPU実験の途中比較](2026-11-06-cpu-cycle-results.md)を参照。既存cycleをinitし直さない。

## 到達点

ユーザーは新規会話としてCLIを起動済み。既存の実装と取得済みデータから、[承認済みspec](../specs/2026-11-05-cpu-autonomous-cycle-spec.md)の実験を続ける。specを参照したgoalによる実装・実行の開始承認は受領済み。今回の引き継ぎで設計・承認範囲を拡張しない。

2026-11-06の確認時点では、この会話のgoal取得結果は `goal: null`。`cpu_experiment.py` / `cpu_worker.py` の生きたプロセスと実データ用の `cycle.json` は見つからなかった。実データの学習・CV・提出は未実施で、実験時間予算の消費は0秒。確認時点以後の状態はCLIで再確認する。

## 場所と実装

- 実装ルート: `/mnt/HDD10TB-2/aburatani/kaggle`。Pythonは同ルートの `.venv/bin/python`。
- 研究記録: `/mnt/HDD10TB-2/aburatani/research-workspace/.research/lab/projects/kaggle-name-that-llm`。
- `name-that-llm/src/cpu_pipeline.py`: TF-IDFのviewと線形分類器、固定prompt分割、OOF分析。
- `name-that-llm/src/cpu_worker.py`: データ準備、CV、全データfit、保存モデルの再推論。
- `name-that-llm/src/cpu_audit.py`: OOFと指標・出力整合性の独立検査。
- `name-that-llm/src/cpu_experiment.py`: 排他ロック、時間・CPU・メモリ監視、試行台帳、終了条件。
- `name-that-llm/configs/00-official.json`: 公式Starter v4の基準設定。改善候補の設定はまだ作っていない。
- `pyproject.toml` / `uv.lock`: numpy、scipy、pandas、scikit-learn、pyarrow、psutil、threadpoolctl、joblib等を導入・固定。

runnerは1試行単位で動く。エージェントが実測結果を読み、次の候補の理由とconfigを保存してrunnerを呼ぶことで自律サイクルを回す。常駐スケジューラや、無期限に候補を生成する機能は追加していない。

## データ取得

最初の公式データ取得は403。ユーザーから参加・ルール同意完了の回答を受けた後、公式CLIで取得できた。`name-that-llm/data/` に元zipと下記ファイルを保存。トークンは表示・転載していない。

| ファイル | 確認した内容 | SHA-256 |
|---|---|---|
| train.csv | 2,699行、18クラス、150 prompt。列 id / prompt_id / text / model | 40a22ce8d88c5f46feb4637a099db815bef5f713ffe53e89dbe1b7b21de77707 |
| test.csv | 3行。列 id / text | 4545aa3a3459f4c0724f97ad5bd06c4caa3506bdfea5fab905e8203184fc0c57 |
| sample_submission.parquet | 3行。列 id / model | ccf86796b80fd7f83d8463664603fd1208e17559abcf416f198776b819646188 |

これはダウンロードできたファイルの実測値。公開testが3行であることから、非公開評価データの規模や構造は推定しない。固定分割と正式なデータmanifestは実験の `prepare` で作る。

## 検証結果とメモリ制約

2026-11-06、Kaggleルートで以下を実行し、5件すべて成功（11.640秒）。一時ディレクトリの合成データによる検証であり、コンペ性能の実測ではない。

```bash
.venv/bin/python -m unittest discover -s name-that-llm/tests -v
```

- promptのfold間分離と破損分割の拒否。
- validationだけにある語が学習語彙へ入らないこと。
- timeout / RSS上限で自分の実験だけを終了し、別プロセスが生存すること。
- 再現確認を候補数に含めず、3連続改善なしを判定すること。
- prepare → CV → 独立検査 → fit → 保存モデル再推論が通り、改ざんOOFを拒否すること。

途中で保存ラベル配列のobject dtypeによる検査失敗を修正し、文字列dtypeで保存するようにした。上記は修正後の結果。

CPUはaffinity最大8、同時CVは最大2 job、GPU不可視。実験と子プロセスのRSS合計32GiB、ホストMemAvailable 16GiB、累積実験時間7,200秒を監視する。cgroupの強制上限は委譲されていなかったため、0.25秒間隔の監視で中断する実装。瞬間的な上限超過やOSのOOMを完全には防げない。メモリ起因の再試行はspecとrunnerの制限を守って1 jobで行う。他ジョブは終了しない。

## 再開手順

CLIではResearch WorkspaceとKaggle実装ルートの両方にアクセスできる状態で作業する。まず両方のAGENTS.md、kaggle-workflowスキル、研究README、spec、この記録を読む。実行中workerと既存cycleを確認し、二重起動しない。

実データcycleが未作成のままなら、Kaggleルートで次を順番に実行する。日付は準備開始日に合わせ、cycleパスはこのサイクル中ずっと共用する。

```bash
cd /mnt/HDD10TB-2/aburatani/kaggle
.venv/bin/python name-that-llm/src/cpu_experiment.py init --cycle name-that-llm/artifacts/2026-11-06-cpu-cycle
.venv/bin/python name-that-llm/src/cpu_experiment.py prepare --cycle name-that-llm/artifacts/2026-11-06-cpu-cycle
.venv/bin/python name-that-llm/src/cpu_experiment.py run --cycle name-that-llm/artifacts/2026-11-06-cpu-cycle --config name-that-llm/configs/00-official.json
.venv/bin/python name-that-llm/src/cpu_experiment.py status --cycle name-that-llm/artifacts/2026-11-06-cpu-cycle
```

既存cycleがあればinitし直さず、同じパスでstatusと台帳・ログを確認する。生きたworkerがいれば重複実行を拒否する。初期化時にコード・spec・依存lockが保存され、その後pipeline/workerとlockの変更は拒否される。モデル実装の修正が必要なら、既存の比較条件を壊さず理由と影響を記録する。

baselineのOOF・class recall・文章長別誤りを検査してから、spec内の候補を最大5件、前の結果に基づいて順に選ぶ。実行前に仮説とconfigを保存する。主指標・停止条件・予算を守り、最後の再現確認やfitに必要な時間も残す。例として大文字保持、句読点、shape/function view、LinearSVCは許可候補だが、まだ採用・実行・改善確認はしていない。

最良候補の再CVは同じconfigで `run --purpose reproduction`、全データ学習は `fit --config ...`、保存モデルの再推論は `predict --model .../model.joblib`。いずれも同じ `--cycle` を渡す。提出形式ファイルはローカル確認用で、Kaggleへ送信しない。独立検査、再現性、失敗も含む比較報告と研究READMEを仕上げてからgoal完了とする。予算で未実施となった項目は明記する。

## 新規CLIへ渡すgoal文

```text
.research/lab/projects/kaggle-name-that-llm/specs/2026-11-05-cpu-autonomous-cycle-spec.md に従い、CPU自動実験を続けてください。まず .research/lab/projects/kaggle-name-that-llm/experiments/2026-11-06-cpu-cycle-handoff.md を読み、取得済みデータと既存実装から再開してください。既存cycleと生きたworkerを確認して二重起動を防ぎ、結果から次の候補を選んで、再実行可能な最良候補と比較報告を完成させてください。メモリ・時間・試行数の制限を守り、GPU利用・外部データ・有料API・Kaggle提出へ範囲を広げないでください。
```

CLIの作業ディレクトリがKaggleルートなら、上記の `.research/` パスの前に `/mnt/HDD10TB-2/aburatani/research-workspace/` を付ける。
