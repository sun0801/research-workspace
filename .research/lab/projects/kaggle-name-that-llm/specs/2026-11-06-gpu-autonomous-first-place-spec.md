---
date: 2026-11-06
project: kaggle-name-that-llm
source: brainstorm
status: approved
execution_status: in-progress
tags: [spec, experiment, gpu, goal, kaggle]
---

# Name That LLM GPU自動実験・公開LBトップ追従 Spec

## 目的と承認範囲

Kaggle Name That LLMで、結果に基づいてモデル・特徴量・アンサンブル候補を自動選定し、公式評価指標の改善を繰り返す。運用上の目標は、現在の公開Leaderboardトップスコアを超える有効なNotebook提出を作ること。Private Leaderboardによる最終順位は別の結果として扱う。

ユーザーは2026-11-06に本specの内容を承認。試行回数・総ジョブ数・累積実行時間の固定上限は設けず、他の研究でGPUが必要になった場合はユーザーの停止指示に従う。残るGPU/OOM安全条件、5時間利用枠ガード、Kaggle提出上限、コンペ期限は探索予算ではなく安全・サービス条件として適用する。

この承認はspec作成の承認であり、外部実装リポジトリの編集・実験開始の指示とは分ける。Implementation Gateに必要な開始指示を受けるまでは、コード変更、GPUジョブ起動、Kaggle Notebook提出を行わない。

2026-11-06 18:56 JST追記: spec評価を受け、ユーザー承認のもとで以下を追記・修正した。公開checkpointとアンサンブルの評価規則、外部データのprompt重複除外、採否判定、test集合依存の後処理、確認分割の実装方法、Kaggleへの書き込み範囲、最終2件の選定、141環境の配置、Kaggle側利用枠、長時間jobの運用、達成後の扱い。実装開始前の状態は変わらない。

## 問いと仮説

未見promptに対する18モデルの文章分類で、既存のTF-IDF基準を起点に、公開・無償で利用できる事前学習モデル、特徴量モデル、アンサンブル等を検証することで、prompt単位で分離した評価と公開Leaderboardのbalanced accuracyを改善できるか。

具体的な仮説と次候補は、公開Notebook/Discussionの調査、既存結果、誤り分析からgoalが各試行前に選ぶ。効果を事前に断定しない。

## 変更・実行範囲

- 実装先: `/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/{src,configs,notebooks}/`。必要なrunner、Notebook、依存定義・lockを含む。
- データ、重み、OOF、実行ログ、提出候補などの大容量成果物は同プロジェクトの`data/`, `artifacts/`, `submissions/`等、Git対象外に保存する。認証情報は表示・記録しない。
- 研究記録は`.research/lab/projects/kaggle-name-that-llm/experiments/`とREADMEへ保存する。各候補の理由、出典、version、設定、分割、seed、指標、実行環境、GPU UUID、時間、メモリ、失敗・中断状態を残す。
- コンペ公式データを利用する。外部データ・事前学習モデルは、現行ルールで利用可能であり、公開・無償かつ他参加者も合理的に入手でき、ライセンスが適合するものに限る。有料API、有料クラウド計算資源、規約同意の代行は含めない。
- 既存CPUサイクルや成果物を初期化・上書きしない。CPU最良モデルは比較基準として再利用できる。
- GPU探索は141/142のみ。CPUはデータ準備、評価、GPUが空くまでの調査等に使えるが、GPUが使えないことを理由にCPU限定の探索へ自動で範囲を変更しない。
- 141で実行する場合は、141上にコード・依存・必要データの実行環境を新規に配置する作業を含む（2026-11-05診断時点では未配置）。配置先は他研究のディレクトリと分け、配置内容のhash・versionを記録する。
- 外部データを学習に使う場合、validation foldのpromptと同一または近似するpromptの文章は、そのfoldの学習から除く。trainにはprompt本文がないため、回答文の重複・内容語類似度、外部データ側の（復元）prompt情報等で照合し、方法・閾値・除外件数をfoldごとに記録する。trainの文章と完全一致する外部文章も除く。
- Kaggle上でのNotebook push・実行、学習済み重み・adapter・前処理成果物のDataset/Model作成・更新を含む。作成物はprivateに限り、公開化・チーム外共有はしない。slug・version・サイズ・内容を記録する。

## 既存基準と評価

- 既存基準: CPUサイクルの公式Starter OOF balanced accuracy 0.314479、最良4-view TF-IDF + Logistic Regression OOF balanced accuracy 0.384504。結果は同じprompt-grouped 5-fold上の値で、未使用holdoutやPrivate LBでの性能保証ではない。
- 主指標: 公式と同じbalanced accuracy。開始時に公式ページから現行の評価仕様、公開Leaderboard上位スコア、コンペ期限を取得し、URL・取得日時・Notebook versionを記録する。
- 学習データはprompt単位で分割し、同じpromptをtrain/validationへ跨がせない。既存の保存済みGroupKFold分割（shuffleなし・seedなし）を比較用に保持する。追加候補の探索に伴う分割適合を抑えるため、最終候補にはseedを固定してshuffleしたprompt-grouped確認分割（例: `GroupKFold(shuffle=True)`、`StratifiedGroupKFold`）も適用する。同じtrainの再分割は分割による変動の確認であり、多数の候補から選んだことによる楽観的な偏りは除去できないことを報告に明記する。各分割・seedを保存し、全候補で比較条件を揃える。
- tokenizer、語彙、正規化、学習可能な前処理、モデル重みの更新は各foldのtrain側だけで行う。validationのラベルで前処理・閾値等を調整しない。
- OOF全行のbalanced accuracyを主に報告し、fold別平均・標準偏差、クラス別recall、混同行列、文章長別指標も保存する。基準差だけで確実な汎化改善を主張せず、split間の安定性も確認する。
- testデータは予測出力に使う。隠れtestのラベルや非公開情報を得たかのように扱わず、公開testの少数行から非公開test性能を推定しない。
- 採否判定: 現bestとの比較は、同一分割のOOFについてprompt単位の対応ありbootstrap（promptを復元抽出、2,000回以上、seed固定）でBA差の95%区間を求める。下限が0を超えれば「採用」、点推定は改善だが区間が0を含めば「未確定」、点推定が改善しなければ「棄却」とする。未確定候補は理由を記録して次候補の土台にできるが、確実な改善とは報告しない。
- 公開checkpoint等の扱い: 全train、またはvalidation foldのpromptを含むデータで学習された公開checkpoint・adapter・予測出力を含む候補は、OOF比較・採否判定の対象にしない。「OOF評価不可」と区別し、学習データの範囲を出典とともに記録する。同等構成をfold別に学習し直した場合のみOOFで評価する。OOF評価不可の候補のPublic LBは参考値として扱う。
- アンサンブル: 重み、stacking、温度・事前分布補正、後処理パラメータは、外側foldのvalidationを含まないデータで決めるnested CVで評価する。全OOFで決めた重み等による値は参考値とし、主指標や採否判定に使わない。提出用の重み等は全OOFで決めてよい。
- test集合依存の後処理: test集合全体を使う後処理（Sinkhorn、クラスタ推定、Hungarian割当、事前分布補正等）は、ラベルを使わず現行ルールに反しない範囲で候補にできる。分類器単体と分けて効果を評価し、CVではtestの構造（prompt_idなし、prompt当たり回答数やクラス件数が不均等）を模したsimulationで確認する。真のprompt_idや均等なクラス件数を使った結果を効果の根拠にしない。

## 自動実験サイクル

1. 公式ルール、公開Leaderboard、上位Notebook/Discussion/Modelを必要な範囲で調査し、versionと閲覧範囲を記録する。投稿者の主張、公開LB、自分たちの実測を区別する。
2. 現bestと誤り分析に基づき、次の仮説・候補・比較条件を選び、実行前にconfigと根拠を保存する。
3. 新しいモデルや入力長等はGPU使用量を測るpilotから始め、検証可能な設定で同一のprompt-grouped評価を行う。
4. 現bestと比較し、「既存基準と評価」の採否判定に従って採用・棄却・未確定を理由とともに記録する。改善しない場合も、重複した盲目的再試行ではなく、結果から次の有望候補を選ぶ。
5. 有望候補を再現確認し、全train fit・推論・提出形式を検査したNotebookを用意する。Kaggleの実行条件を満たすNotebookのみ提出する。
6. 提出結果とpublic LB scoreを記録し、次の候補を選ぶ。Public LBを唯一の検証指標として候補を過剰調整しない。

探索対象の候補は固定リストや固定件数に閉じない。goalは既存結果と現行の公開知見から次を考え、公式ルール・ライセンス・資源安全条件の範囲で試す。

## Kaggle提出条件

- このコンペはCode Competitionで、Kaggle Notebookから提出する。ローカルの予測ファイルを直接送信しない。
- Notebook実行はCPU/GPU各9時間以内、Internet access disabled、出力`submission.parquet`等の現行要件を提出前に再確認する。必要な公開モデル/データはオフライン実行で利用できる形で準備する。
- 提出前に、Kaggle上で提出Notebookを全処理通して実行し、実行時間・ピークメモリ・出力形式を確認する。公開testは少数行のため、9時間制限はtrain等の文章で測った1件当たり時間から本番の約4,000行分を見積もって判断する。ローカルと異なる数値精度（例: T4でのfp16、量子化）を使う場合は、同一checkpointでのローカル予測との一致度を確認する。
- Kaggle側のGPU週間利用枠の残量を確認し、Kaggle上の実行計画に含める。エラー終了した提出が日次提出数に含まれるかを公式情報で確認し、不明なら含まれるものとして扱う。
- Kaggleへの書き込み（Notebook push、Dataset/Model作成、提出）に使う手段と認証の可否を開始時に確認する。2026-11-02時点の公式MCP設定は読み取りツールのみ有効のため、書き込みは公式CLI等で行い、不足があれば代行せず記録する。
- 現行ルール上、1日最大5提出、最終審査用に最大2件。提出履歴・日次残数を提出前に確認し、候補が検証を通った場合のみ提出する。上限まで使い切ることを目的にしない。
- 最終2件は、(a) prompt-grouped評価と確認分割で安定した最良候補（OOF評価不可の候補は除く）、(b) Public LB最良候補（(a)と同じなら、(a)との予測相関が低い次点）を原則とする。開始時に再確認した締切（2026-11-02調査では2027-01-13 23:59 UTCと2027-01-14 23:59 UTCが不一致。確定しなければ早い方）の3日前までに、選択案と根拠をユーザーへ提示する。ユーザーの指示があればそれに従い、回答がないまま締切24時間前になった場合は(a)(b)を選択して記録する。Kaggleの自動選択に委ねない。
- 開始時と各提出前に公開Leaderboardのトップ値を確認する。提出時刻・Notebook version・score・順位・残り提出枠を記録する。
- 現行ルール/期限が変更されていないか、実行時点で公式ページを再確認する。本人の規約同意や画面操作が必要になった場合は代行せず、正確な不足を記録する。

## GPU・メモリ安全

- 起動直前に141/142を複数回観測し、GPU UUID・機種・空きVRAM・使用率・計算プロセス・ホストRAM・確認可能な予約状況を記録する。2026-11-05の診断値は現在の空き状況や予約を保証しない。
- 既存の計算プロセスがあるGPUは使わない。空き容量だけを理由に他ジョブと同居させない。scheduler等で予約を確認できない場合もその限界を記録し、読み取り診断と起動直前の再確認を行う。
- 各runはUUIDでGPUを限定し、同一GPUで自分の候補を競合させない。別々に安全確認できたGPUでの並列実験は可能。協調lockは自分たちのrun間の重複防止に使うが、他利用者を排除する予約とは扱わない。
- 新しい設定は最小batchと想定最大sequence長でpilotする。学習モデルならload、forward/backward、optimizer stepまで、推論モデルなら対象の推論範囲まで測る。
- pilotで測った自分の使用量と見積追加分が、空きVRAMから`max(4 GiB, 全VRAMの25%)`を差し引いた範囲に収まる場合だけ本実行へ進む。余裕がなければ待つか別の安全なGPUを確認する。
- ホストRAMも他プロセスを含むMemAvailable/RSSを監視する。MemAvailableが16 GiB未満なら新しい重い処理を開始せず、自分のrunが原因で下回る場合は自分の子プロセスだけを止める。cgroup等の強制上限が利用可能かを実装時に確認し、不可なら監視方式と瞬間超過の限界を記録する。
- OOM・異常終了時は自分のjobだけを終了し、config・ログ・消費時間を残す。同じ失敗設定を無制限に繰り返さず、原因に応じて安全側に縮小した再試行は最大1回とする。
- 他研究のファイル、設定、GPUプロセス、予約を変更・終了しない。ユーザーから別研究でGPUが必要との指示があれば、自分のrunを安全に停止してcheckpointと再開位置を残す。

## 利用枠・継続・停止条件

- Kaggle作業に使うCodex CLIでは、既存のkaggle-workflow方針どおり`gpt-6-luna`・`high`を使い、他プロジェクトのモデル設定は変更しない。Goalにtoken予算を独自設定しない。
- 長い作業の開始時と主要checkpointで5時間利用枠を確認する。確認は`.agents/skills/kaggle-workflow/scripts/codex_rate_limit.py --guard 15`で行う（2026-11-06追記: Codexのagent toolからstatuslineを読めず、残量19%でもガード判定不能としてgoalがblockedになったため）。残量15%以下では新しい長時間作業を開始せず、安全な区切りで結果・コード状態・再開位置を保存する。取得不能の場合は1回だけユーザーへ確認して止まり、待機中に同じ確認を繰り返さない。正確な消費量を予測したり、枠の回復後の無人再開を保証したりしない。
- hash（sha256等）は、64桁を応答の中で書き写さない。一致の確認は`sha256sum -c`等のコマンドに任せ、ログ・READMEには「一致」と確認に使ったコマンド、必要なら先頭8桁だけを書く。全桁を残す必要がある場合は、コマンドの出力をファイルへ直接書き出す（例: `sha256sum <file> >> <log>`）。（2026-11-10追記: 64桁のhashを書き写す途中で同じ断片の繰り返しから抜けられず、出力上限（`max_output_tokens`）でturnが失敗し、goalがblockedになったため）
- GPU学習・推論など長時間のjobは、エージェントのセッションから切り離して実行（tmux、nohup等）し、host・PID・GPU UUID・ログ・checkpoint・再開コマンドを記録する。セッション再開時は実行中jobの有無と状態を確認してから次の操作を行い、二重起動しない。
- GPUの空き待ちや長時間jobの監視は、短間隔の連続ポーリングで利用枠を消費しないよう、原則10分以上の間隔で軽量な確認を行う。pilotなど短時間の確認はこの限りでない。
- ユーザー指定により、総試行数・総ジョブ数・累積GPU時間の固定上限、改善なしの固定連続回数による打ち切りは設けない。
- goalは公開LBトップ超えを目指して継続する。達成が確認できれば、そのSubmissionと当時のトップscoreを根拠に報告し、継続するかはユーザーの指示を受ける。指示があるまで新しい探索候補は開始しない（最終2件の選定手順は続ける）。コンペ期限までに達成しない場合は、最終bestと未達を分けて報告する。Private LBの最終順位は公開LBの達成と同一視しない。
- コンペ期限、ユーザーの停止指示、利用枠ガード、Kaggle側のGPU週間利用枠、GPU/RAM安全条件、規約・権限上のblockerは上記の固定探索予算とは別の停止・待機条件とする。止めた際は完了していない試行を成功扱いにせず、再開可能な記録を残す。

## 完了成果物・検証

- 再現可能なコード、依存lock、設定、Notebook、モデル/データの出典とversion。
- 比較分割とOOF予測、各候補の指標・誤り分析・実行資源・失敗記録。
- 再現確認済みbestモデルと、Kaggle Notebookの出力形式検査。
- 提出を行った場合はNotebook version、Submission履歴、Public LB scoreと順位、残り提出枠、Kaggle上に作成したprivate Dataset/Modelのslug・version、最終2件の選定根拠。
- `.research/lab/projects/kaggle-name-that-llm/experiments/`の最終報告とREADMEの到達点・再開先。
- 目標未達の場合は、上回れなかった事実、最良の測定値、残る不確実性を明記する。

## 関連資料

- [初回CPUサイクルspec](2026-11-05-cpu-autonomous-cycle-spec.md)
- [CPU自動実験の最終結果](../experiments/2026-11-06-cpu-cycle-results.md)
- [141/142 GPU診断](../experiments/2026-11-05-gpu-availability.md)
- [Goal方針brainstorm](../../../../secretary/notes/brainstorm/2026-11-06-kaggle-first-place-goal.md)
- [Kaggle Name That LLM公式ルール](https://www.kaggle.com/competitions/name-that-llm/rules)

## Goal起動文案（開始承認後）

> `.research/lab/projects/kaggle-name-that-llm/specs/2026-11-06-gpu-autonomous-first-place-spec.md`に従い、Name That LLMで現在の公開Leaderboardトップスコアを超えるNotebook提出を目指して自動実験を続けてください。まず現在の公式ルール・締切・上位スコア・GPU状態を確認し、既存CPU成果を保全してください。結果と公開知見から次候補を選び、prompt-grouped評価、GPU/RAM安全条件、利用枠15%ガード、Kaggleの1日5提出・最終2件を守って、候補の検証・再現・有望な場合のNotebook提出を繰り返してください。総試行数・総ジョブ数・累積GPU時間に固定上限は設けません。他研究のGPUが必要との指示があれば自分のrunを止め、checkpointと再開位置を保存してください。Kaggle上の作成物はprivateに限ってください。目標達成を確認したら報告して継続の指示を待ち、未達ならコンペ期限まで進めてください。最終2件はspecの選定ルールに従い、Private LBによる最終順位は別に報告してください。実装開始はこのgoalを開始するときの指示を受けてから行ってください。
