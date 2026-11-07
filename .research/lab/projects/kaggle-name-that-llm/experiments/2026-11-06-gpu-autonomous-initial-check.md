---
date: 2026-11-06
project: kaggle-name-that-llm
status: in-progress
tags: [experiment, gpu, kaggle, qwen, external-data]
---

# GPU自動実験の開始時確認と候補01

2026-11-06 19:20 JST時点の開始記録。承認済み[GPU自動実験spec](../specs/2026-11-06-gpu-autonomous-first-place-spec.md)に従い、公式状態、既存成果、GPU・提出枠を再確認した。まだ学習、Notebook push、Kaggle提出は行っていない。

## 現在の基準・競技条件

- CPUサイクルの基準は4-view TF-IDF＋Logistic Regression、同一prompt-grouped 5-fold OOF balanced accuracy **0.384504**。そのcycleとCPU成果物は変更していない。
- 公式 [Public Leaderboard](https://www.kaggle.com/competitions/name-that-llm/leaderboard) をoverridePublicで取得。2026-11-06 10:20 UTC時点の先頭はLe Vietの **0.747**（submission 00:03 UTC）、次点も0.747（Hod Carriers）。この値を超える有効なNotebook提出が運用上の目標。
- 公式 [Rules](https://www.kaggle.com/competitions/name-that-llm/rules) と [Timeline](https://www.kaggle.com/competitions/name-that-llm/overview/timeline) を確認。Timelineは最終提出期限を**2027-01-13 23:59 UTC**と表示する一方、API metadataは2027-01-14 23:59 UTC。specどおり早い方の1月13日を採用する。
- 公式metadataは1日最大5件・Notebook提出限定。[Evaluation](https://www.kaggle.com/competitions/name-that-llm/overview/evaluation) は18クラスbalanced accuracy、test側のclass数は均等でなくPublic/Privateのmixも異なると明記。[Code Requirements](https://www.kaggle.com/competitions/name-that-llm/code) はCPU/GPU各9時間以内、Internet無効、`submission.parquet`を要求。
- 公式CLIの認証付き提出履歴は `No submissions found`。したがって本日分の上限は現時点で5件全て残っている。提出はまだ行わない。

## GPU・実行環境

142 (`142-X10DAi`) で約5秒間隔の複数観測を実施。3回とも次の値が同じで、計算プロセス一覧は空だった。

| GPU UUID | 機種 | 総VRAM | 使用 / 空き | GPU使用率 |
|---|---|---:|---:|---:|
| `GPU-135ac6e4-8006-058e-ae74-0bb708d0f143` | RTX A4000 | 16,376 MiB | 15 / 15,960 MiB | 0% |
| `GPU-8a059266-7ede-0427-ff30-08ba7a9b5224` | RTX PRO 4500 Blackwell | 32,623 MiB | 172 / 31,929 MiB | 0% |

MemAvailableは219,311,328 kB（約209 GiB）。`squeue`は見つからず、予約状況は確認できない。GPU使用メモリはXorg等の表示用と見られるが、計算アプリは報告されていない。プロセス一覧には他研究のSAM2系LSP等があるため、それらは変更しない。起動直前にも再観測する。

## 公開知見と候補01

- `crtproduction/name-that-llm-open-pool` の現行dataset version 15を確認。Kaggle metadataはCC BY-SA 4.0、更新日11月5日、213k規模と表示し、main parquetは105,708,387 bytes、別にrecovered promptを含む`prompts.parquet`がある。作成者は「99%にrecovered prompt IDがあり、train promptへの回答や近似train本文は含まない」と説明している。説明文の見出しはv13表記のままなので、実データ列・件数・version 15との差分をダウンロード後に確認する。
- version 15のmain/prompt parquetを取得し、実体が212,623行/23列・16,598 prompt rowsであることを確認。18ラベル、各列欠損0、normalized duplicate passage 0、公式trainとのnormalized exact text match 0。最小ラベル件数は3,541で、各ラベル2,500件上限が可能。mainには`prompt_canon`、`max_cos_train`、`max_sim_train_prompt`、`match_weight`、`flag_near_train_prompt`等がある。作成者の説明ではcreator overlap flagsは既に除去済みで常にfalse。`prompt_canon`のunique 34,900件のうち、prompt本文を持つtableとのjoinは16,598件に限られる。
- `match_weight`は作成者が公式trainの全文章から合わせた重みなので、OOFでは使わない。候補01はseed 42の一様・非復元抽出、最大2,500件/labelとし、validation prompt情報が重みに入るのを避ける。
- `pjmathematician/ntl-train-prompts-reconstructed` v1（CC BY-SA 4.0）を取得。150件の推定train promptとOpen Poolの16,598 prompt textを照合した。char 3–5 gram cosineの最大値は0.503、word 1–2 gramでは0.545。cosine≥0.90は0件、0.40ではそれぞれ8件/10件が候補一致となったため、configのfold-wise near-match閾値を両方0.40へ更新した。一致promptの本文は表示せず、対応`prompt_canon`のpool行を該当validation foldの学習から除外する。これは保守的なlexical filterで、意味的に同じpromptの完全な判定ではない。本文を復元できない18,302 canonical groupsは、作成者の既存除外と完全一致検査に依存する。
- `nishantdahal/two-stage-lora-on-the-public-pool` version 2のNotebook本文を読み、2段階学習（public pool事前学習→公式train微調整）の設計を確認。説明値はLB 0.592。現run metadataは11月3日、T4、offline、public poolの依存が記載される。別のDiscussion投稿は、Qwen3-8B単体＋Open Pool v10でOOF 0.6224 / Public LB 0.628と主張しているが、投稿者の自己申告として扱う。
- `weywuy/leak-audit-is-your-holdout-really-held-out` version 3は、全trainで学習済みのcommunity adapterをOOFへ持ち込むと、validation promptを既に見ているため0.913の不正確な値になった事例を説明する。従って既存LoRA adapterは採否用OOFに使わず、fold外promptを除外したpoolから学習し、各foldのofficial trainだけで再微調整する。
- 候補01の実行前configを `/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/configs/gpu01-qwen3-8b-openpool-v15.json` に保存済み。Qwen3-8B-Baseの新規LoRA24 classifierを2段階で学習する。Stage 1はfoldwise prompt filtering後のpublic poolのみ、Stage 2は各GroupKFold foldのtrain側だけで微調整。validation promptとのexact/near overlapと完全一致文章を除外する。元のGroupKFoldを維持し、最終候補には固定seedのshuffled prompt-grouped確認分割も追加する。公開Qwen3-8B-BaseはKaggle model version 1、16.39 GB、Apache 2.0。
- nested CVのprompt-level paired bootstrap（2,000回以上）で採否を判断する。全trainを含む公表adapterは比較に使わない。prompt recovery、外部pool filtering、class balancingの各段階を別ログに残す。

## 利用枠・次の操作

- 実装ディレクトリ `/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/` はGit repositoryではない。候補01 configと公開poolデータだけを新規保存し、既存CPU cycle/コード/認証値は変更していない。
- 共通Kaggle `.venv` はtorch/transformers/peft/bitsandbytes/accelerate未導入。CPU環境を変えず、別GPU環境を用意する必要がある。Kaggle CLIの `kernels push` はkernel-metadataの `is_private` を使うことを公式[metadata docs](https://github.com/Kaggle/kaggle-cli/blob/main/docs/kernels_metadata.md)で確認。公式GPU使用ガイドはweekly quotaが30時間または需要次第で変動し、Notebook Settings/profile/session画面で残量確認できると案内するが、現在値は未確認。
- 本セッションでCodex CLIの5時間rate limit statuslineや利用状況画面を確認するツールは見つからなかった。goalの累積token値から残量を推定しない。長時間GPU学習はstatusline残量を確認できるまで開始しない。
- GPU学習前に別環境、model取得、最小pilotを整える。Kaggle上のNotebook/Dataset/Modelは作成する場合もPrivateに限る。

## 出典

- [Name That LLM Rules](https://www.kaggle.com/competitions/name-that-llm/rules), [Timeline](https://www.kaggle.com/competitions/name-that-llm/overview/timeline), [Evaluation](https://www.kaggle.com/competitions/name-that-llm/overview/evaluation), [Code Requirements](https://www.kaggle.com/competitions/name-that-llm/code) — 2026-11-06 10:20 UTCに公式Kaggle MCPから取得。
- [Name That LLM Open Pool](https://www.kaggle.com/datasets/crtproduction/name-that-llm-open-pool) — dataset metadata/version 15/file listを公式Kaggle MCPから取得。本文の詳細は作成者の説明であり、まだデータ再検査していない。
- [Two-stage LoRA on the public pool](https://www.kaggle.com/code/nishantdahal/two-stage-lora-on-the-public-pool) — Notebook metadataとmarkdown本文を読了、コードは未実行。
- [Leak audit: is your holdout really held out?](https://www.kaggle.com/code/weywuy/leak-audit-is-your-holdout-really-held-out) — version 3本文を読了、記載実験を未再現。
- [Qwen3-8B-Base](https://www.kaggle.com/models/qwen-lm/qwen-3/Transformers/8b-base) — version 1 metadata、Apache 2.0、約16.39 GB。
- [Kaggle Efficient GPU Usage](https://www.kaggle.com/docs/efficient-gpu-usage) — GPU quotaと確認場所を確認。現在の個人残量は未確認。

## 再現用hash

2026-11-06に確認したSHA-256:

- 候補config: `109cc0a01591ed16b11a7ee138b8fca8297a676fd2fb900c1d64a8b207bd41ab`
- Open Pool v15 `ntl_open_pool.parquet`: `1e4200aed80f52d655d4900a301cb427ca1341e06be31a8b7d5fde9ea3ef425f`
- Open Pool v15 `prompts.parquet`: `6c18c6df3aff5e33034062bf3bbb06428986c055608181c22daebb132e3269ae`
- Reconstructed train prompts v1: `41357f850c4309528a59f92ecda5323e2b1c2a925eb69dfc87ea92a4f68d6d6e`

## 2026-11-06 19:44 JST 継続確認・候補runner準備

- 現在状態を再確認。142 (`142-X10DAi`) のGPU1 RTX PRO 4500 Blackwellは空き31,929/32,623 MiB、使用率0%、`nvidia-smi`の計算プロセスなし。MemAvailable 209 GiB。GPU0 RTX A4000も空き15,960 MiB、使用率0%。予約状況は引き続き取得できない。CPU cycleのOOF/モデル成果物には触れていない。
- 公式Kaggle MCPのLeaderboardを再取得。先頭はLe Viet **0.747**（11月6日00:03 UTC）、Hod Carriers **0.747**（11月4日22:38 UTC）、3位Team Aillis 0.743。competition metadata上の上限は5提出/日、Code Notebookのみ。metadata期限は2027-01-14 23:59 UTCで、既存ログどおりTimelineとの不一致が解消していないため早い方の1月13日を維持。
- Kaggle週間GPU枠とCodex CLIの5時間利用枠残量はこのセッションのツールから取得できない。Codexは `get_goal` の累積token数で残量を推測しない。specの15%ガードにより長時間作業を開始せず、短時間のrunner準備のみ継続。
- 外部実装場所 `name-that-llm/src/gpu_experiment.py` に候補01専用runnerを追加。saved primary GroupKFoldと`GroupKFold(shuffle=True, random_state=42)`のconfirmation split、recovered promptとのchar/word TF-IDF near-match（閾値0.40）によるfoldwise canonical group除外、公式train文章のexact-match除外、creator flags除外、ラベル均等上限サンプリング、Qwen3-8B LoRA二段階学習、OOF logits、epoch checkpoint/resume、SIGTERM/SIGINTの完了epoch checkpoint停止を実装した。`match_weight`は参照しない。
- 起動時にGPU UUIDを固定し、5秒間隔の2回の`nvidia-smi`、計算プロセス不在、VRAM reserve 8,156 MiB、MemAvailable 16 GiB、cgroup上限記録を確認する。`--pilot`は1件についてmodel load/forward/backward/optimizer stepを行い、peak VRAM証跡がない限り全学習を拒否する。`--split primary|confirmation`をサポートする。
- runnerの`python3 -m py_compile`は成功。これは構文検査だけで、GPUコード実行・依存整合・pilot・学習・OOF結果は未検証。専用`.venv`、Qwen重み、CUDA pilotはまだ用意・実行していない。共通CPU venvには変更なし。
- `src/gpu_experiment.py` SHA-256: `95afb941ce106c991b39c98ecc66a09c3e242ed0c88a773d16977e33207290f6`。候補config SHA-256は前回記録どおり。
- 再開先: statuslineまたは利用状況画面でCodex 5時間枠が15%超と確認できた後、Kaggle GPU週間残量を調べ、専用venv/モデルの取得へ進む。その後runnerのデータ処理・PEFTとの互換性を短いGPU pilotで検証し、測定peak＋reserveが現空きに収まる場合のみfold CVを開始する。Codex利用枠が見えない限り長時間作業は開始しない。

### OOF採否集計の準備

- `src/gpu_analyze.py` を追加。5 fold全件・ID一意・baselineと候補のrow/prompt/truth一致を要求し、OOF全体BA、fold別BA/平均/SD、class recall、confusion matrixを保存する。
- 採否用にprompt group単位の対応ありbootstrapを2,000回以上、seed 42で行う。promptを復元抽出し同じ行重みをbaselineとcandidate双方へ適用する。95%区間下限が0より大なら採用、観測差が非正なら棄却、改善しても区間が0を含めば未確定とする。
- 構文検査成功。解析はOOF未生成のため未実行。
- `src/gpu_experiment.py` SHA-256: `95afb941ce106c991b39c98ecc66a09c3e242ed0c88a773d16977e33207290f6`
- `src/gpu_analyze.py` SHA-256: `4b18276c8c26c4489bd508e9255e046433d5dfe6d8a6c3866a4f9501a317df2c`

### confirmation splitの比較条件

- confirmation candidate OOFをprimary baselineと直接比較すると分割条件が異なるため、`src/gpu_confirmation_baseline.py` を追加。既存best config `05-function-view.json` をそのまま使い、`GroupKFold(n_splits=5, shuffle=True, random_state=42)`上で各fold trainだけでTF-IDF/LRをfitする。既存CPU cycle成果物は読取専用で保持し、新しいOOFはGPU候補artifactの外側へ別保存する。
- `src/gpu_analyze.py` はprimaryでは既存baseline OOF、confirmationではこの新baseline OOFを必須にし、同一splitの行/prompt/正解を照合してからpaired prompt bootstrapを行う。baseline作成・解析はまだ実行していない。
- 3 scriptsの最終SHA-256: `gpu_experiment.py` `95afb941ce106c991b39c98ecc66a09c3e242ed0c88a773d16977e33207290f6`; `gpu_analyze.py` `a022e759a972f1dd02980aac7dba9c3af0c225162bd7b09a69683b98bf183860`; `gpu_confirmation_baseline.py` `dd4020dc656e6bde57d8a5f71a9590624e91d488b9240bbcc7c2a32035d0ac30`。

### checkpoint信頼性と最終コード版

- checkpointを完了epoch別の不変ディレクトリへ保存し、`latest.json`をatomic更新する方式に変更。中断で未完了epochの途中重みを使わず、直近完了epochへ戻る。optimizerとPython/NumPy/PyTorch/CUDA RNG状態を保存し、再開時に復元する。epochごとのDataLoader shuffle seedも固定した。
- pilotのVRAM判定には最大allocated/reservedの大きい方を使い、full run前に同じ値＋8,156 MiB reserveを再確認する。
- `gpu_experiment.py`最終SHA-256: `88b94335f5518b2fab3dd706b7ab62da3060700ef6474e6f52ede84cd6d65e2b`。前の節のhashは直前版であり、この値が現行版。3 runnerとも構文検査済み。実行検証は依然未実施。
- statusline/rate-limit表示に対応する専用toolは現在の利用可能tool一覧にも見つからない。5時間枠は不明のままなので、依存install・モデルdownload・CPU confirmation OOF・CUDA pilotをまだ起動していない。

### confirmation splitのCPU基準OOF実測（2026-11-06 19:53 JST）

- 既存の最良設定 `configs/05-function-view.json`（SHA-256 `72c845e323bf214f56f3807c2de06cabc0dbdc1fdd6fe1804fb854530d784f25`）を固定し、`GroupKFold(n_splits=5, shuffle=True, random_state=42)`で再fitした。`CUDA_VISIBLE_DEVICES=''`、OMP/OpenBLAS/MKL各4 threadを設定。既存CPU cycleは変更していない。
- confirmation OOF BA **0.3737683321**、fold平均 **0.3737547893**、fold SD **0.0044071482**。fold別BA: 0.368519 / 0.374074 / 0.374074 / 0.370626 / 0.381481。全2,699行・150 prompt・18 class、ID重複/欠損なし。primary split既存基準0.384504との差は−0.010736だが、分割が異なるため候補比較には使わず、後続Qwen候補は各split上の同一split baselineに対応あり比較する。
- 成果物は`artifacts/gpu01-qwen3-8b-openpool-v15/confirmation-baseline/`に隔離。OOF SHA-256 `aa945813a5577c6f0dfa2b44c13fa6163d6db1656f065d3b39761e2b7d37f253`、metrics SHA-256 `0063cac5bd76d3507b7f975d70792fd44e2b573b49a13bcc0299244cdee5a3bb`。再計算runnerは`src/gpu_confirmation_baseline.py`、SHA-256 `dd4020dc656e6bde57d8a5f71a9590624e91d488b9240bbcc7c2a32035d0ac30`。
- 実行後のGPUはRTX A4000空き15,960 MiB、RTX PRO 4500空き31,929 MiB、両方0%、計算プロセスなし。GPU学習は開始していない。

## 2026-11-06 19:55 JST 再開時の状態と安全性修正

- 現行の公式Kaggle metadata/Leaderboardを再取得。team count 4,865、daily submission limit 5、Notebook-only、API deadline 2027-01-14 23:59 UTC。現topはLe Viet 0.747、Hod Carriers 0.747、3位0.743。Timelineはbrowser readerから内容を取得できず、既知の1/13 vs 1/14不一致は未解決なので早い方を維持する。
- GPU host `142-X10DAi`を再確認。A4000は15,960 MiB free、RTX PRO 4500 Blackwellは31,929 MiB free、両方0%。計算プロセスなし、MemAvailable 209 GiB。候補GPU job・confirmation CVプロセスはいずれも不在。専用venvとQwen weightsもまだない。
- runnerを静的に再監査し、実際のGPUモデルload直前にも5秒間隔のpreflightを二度行うよう変更。MemAvailableが両方のsnapshotで16 GiB以上を要求し、pilot passにも実行後の16 GiB条件を含めた。現行hashは`gpu_experiment.py` `5f01094f0b34af58a2ee5c57f4106909c4620b9052206287998dbdac445f2da1`。
- analyzerはcandidate/baselineのid、prompt、真値に加えfold idも一致しない場合に止まるよう強化。現行hashは`gpu_analyze.py` `66343912b03724ec6fa84ddfdec34bc0364d9d9b21c440828f92f78051d4ac60`。全3 runnerは構文検査済み、runtime検証はまだ。
- 認証情報を出さずに使える公式MCPはread-only。Notebook push/submit機能は利用可能ツールにない。提出可能なNotebook/weightもまだないので書き込みはしていない。
- statusline残量の専用toolは現在も存在せず、5時間枠は不明。specの利用枠ガードに従い、依存導入・model download・CUDA pilot/full CVは起動せず、短い静的準備と公式状態の再確認までとした。

## 公開資料の差分調査（2026-11-06 19:57 JST）

- Kaggleのnotebook検索（competition=Name That LLM、score-descending先頭10件。検索APIがLB scoreを返すわけではない）で、`ozertuu/0-670-residual-sibling-gating-apex`のversion 4を選びmetadataとMarkdown構成を確認。run metadataは2026-11-03、Public LB 0.670+は著者表記。現在の首位0.747を下回る。
- 著者の構成説明はQwen3-14B/8BとLlama-3.1-8Bのfold adapter＋full-fit、Qwen-family公開checkpoint、stylometric encoder、Open Pool学習の4-view SVM、TF-IDF/text-distortionを合成し、test prompt cluster由来のtwin/Gaussian head、ATLAS、Sinkhorn、typography、sibling residual/pairwise verifierを重ねるもの。metadata上は多数の公開dataset/model/kernel依存を列挙している。LB説明は著者主張で、構成全体の再現は未実施。計算/依存量が大きく、今の候補に一括導入しない。
- Discussion 756088（2026-11-05投稿）の作者ablation主張では、同一部品でもbase A/Bで寄与が異なる。Qwen3-14B除去で−0.010〜−0.020、centered twins除去−0.006〜−0.017、Sinkhorn温度変更が一方のbaseで+0.003など。ただし複数項目を同時変更した行があり、他者の自己申告LB結果である。採用する場合は係数を流用せず、まずprompt-grouped holdout simulationとnested調整で個別に評価する。
- 候補01はfoldwise Qwen3-8B＋public Open Poolをベースとして維持。候補01の結果後に、誤り分析/クラス間混同がfamily内に残る場合、sibling-family conditional residual gateを別候補にする価値がある。test clustering/Sinkhornは実testの構造（prompt group size/class counts）を前提とせず、公式specのsimulation条件で別評価する。
- 出典: [0.670+ Residual Sibling Gating Apex](https://www.kaggle.com/code/ozertuu/0-670-residual-sibling-gating-apex) — notebook metadataとMarkdown見出し・構成説明を読了。コード全セルの依存・学習データを再現検査したわけではない。 [Same ablations on two bases](https://www.kaggle.com/competitions/name-that-llm/discussion/756088) — discussion本文を取得。表は投稿者のPublic LB ablation主張。

### Codex利用残量の公式確認経路

- `openai-docs`で公式OpenAI資料を確認。OpenAI DevelopersのCodex案内では、実行中セッションの残りrate limitは`/status`で確認できる（https://developers.openai.com/blog/mastering-codex-remote-for-engineering、2026-11-06確認）。利用上限dashboardも案内されている（https://developers.openai.com/ja-JP/docs/pricing の検索結果。ページ本文のopenは404で未取得）。
- 現在のagent tool surfaceには`/status` slash commandまたはrate-limit getterがない。これはユーザー承認待ちではなく、必要な残量情報の取得待ち。残量15%以下なら新しい長時間作業を始めない条件を維持し、残量が得られたら判断を更新する。

### GPU環境の軽量準備（2026-11-06 20:00 JST）

- `name-that-llm/.venv/`をPython 3.12.3で新規作成。これはコンペ内の候補専用で、`/mnt/HDD10TB-2/aburatani/kaggle/.venv`（CPU/Kaggle CLI共通）とは別。まだpip依存・torch・transformersを導入していないため、GPU環境としては未完成。Qwen重みの取得もしていない。
- OpenAI Docsを調べ、Codex CLIの実行中セッションで残量を見る公式コマンドは`/status`と確認した（[OpenAI Developers: Mastering remote engineering work](https://developers.openai.com/blog/mastering-codex-remote-for-engineering)）。このfunctions agent tool surfaceから稼働中セッションへ`/status`を直接送る手段はない。質問は残り率の情報だけで、承認を求めているものではない。回答を待つ間も、短い読み取り調査・安全な準備を継続する。

## 2026-11-06 20:02 JST 継続時の再検証

- Kaggle公式metadata再取得: deadline API `2027-01-14 23:59 UTC`、daily submissions 5、notebook-only。現Public LBはLe Viet/Hod Carriersの**0.747**同率首位、次点0.743。新規の提出/Notebookなし。Timelineの日付不一致は継続。
- 142 GPU1は空き31,929 MiB/32,623 MiB、0%、計算アプリなし。host MemAvailable 209 GiB。候補runner/解析/confirmation-baselineプロセスなし。
- candidate専用`.venv`はPython 3.12.3、pipだけ。CPU共通venvは未変更。confirmation baseline artifact 2ファイルが残り、OOF BA 0.373768。
- runner hashes unchanged since prior audit: experiment `5f01094f0b34af58a2ee5c57f4106909c4620b9052206287998dbdac445f2da1`; analyzer `66343912b03724ec6fa84ddfdec34bc0364d9d9b21c440828f2f78051d4ac60`; confirmation reference `dd4020dc656e6bde57d8a5f71a9590624e91d488b9240bbcc7c2a32035d0ac30`.
- 5-hour remaining percentage has not arrived. OpenAI Docs /status route is documented and asked once. No long install/download/GPU run started; progress this turn is official-state revalidation and current artifact audit.

### confirmation OOF誤り分析（2026-11-06 20:04 JST）

- confirmation CPU基準BA 0.373768、accuracy 0.373842。最弱recallはclaude-fable-5 0.1745、glm-5.3-flash 0.1800、glm-5.3 0.2067、gpt-5.6-terra 0.2267、kimi-k3 0.2533、claude-opus-4-8 0.2667。
- 大きい混同はgemini-3.8→3.7 (49)、3.7→3.8 (42)、gemini-3.6→3.7 (36)、glm-5.3-flash→glm-5.3 (36)、GPT-5.6-sol→luna (30)、Claude opus-4-6→sonnet-5 (29)。family内の近縁モデル混同が多いが、claude-fable-5はglm-5.3-flashにも25件誤分類し、全てがfamily内問題ではない。
- 文章長別BA（bucket内にあるclassのみ）: <=60語 0.2608、61–120 0.3703、121–180 0.4109、>180 0.4364。短文が最も困難。
- OOFだけから求めたdiagnosticsで、holdoutとは別分割への性能保証ではない。出力は`confirmation-baseline/diagnostics.json`, `class-recall.csv`, `confusion-matrix.csv`。この結果はQwen候補01を変える根拠にはせず、その結果のclass recall比較と次候補（family-sibling residual/gatingをnested grouped評価）の設計に使う。

### checkpoint cache確認（2026-11-06 20:05 JST）

- `/home/aburatani/.cache/huggingface/hub/models--qwen-lm--qwen-3`、Kagglehubの同model cache、候補projectのmodels/data/modelsを指定して確認したが、Qwen3-8B-Base重みは既存キャッシュにない。取得には別途大きいdownloadが必要。
- confirmation OOF診断artifact（BA 0.373768、弱recall/近縁family混同/短文弱点）の作成を確認。CUDA/gpu experiment/CPU refitはこのturnで起動していない。

### foldwise Open Pool事前監査（2026-11-06 20:08 JST）

- CPU-only audit runner `src/gpu_data_audit.py`を実装・実行し、config/official train/Open Pool/reconstructed promptsのhash付きでprimaryとconfirmation全foldを集計した。source 212,623行、creator flag除外0、official train文章exact match除外0。threshold 0.40で復元prompt 150件中9件が候補一致、該当canonical pool groups 12件。
- foldごとにnear/exact prompt filterが31/49/13/19/7行（primary）、38/7/0/12/62行（confirmation）を除外。全10 foldsで全18 classそれぞれ2,500件以上が残り、seed42の均等sampleは毎foldちょうど45,000行（2,500/class）。CPU auditはrunnerの近似prompt照合方法を別実装で再現した。各splitは別々に抽出するため、OOF fit側でも同じ固定seed capを適用する。
- audit JSON: `artifacts/gpu01-qwen3-8b-openpool-v15/pool-filter-audit.json`, SHA-256 `76b8f14bc81e35e97f5b0d72d1a751d5b73ec417b5f27a942dbb111faed69d99`; audit source SHA-256 `787d95f622416225dd265ec88939dfcf739b95e3eaf612dcfe19058ba6454534`.
- 監査内容に合わせ、GPU runnerはfold prompt除外後の全label 2,500件未満を拒否し、45,000件/全classのcapをassertするよう更新。row数はnear-prompt filter前後でログ出力する。現行`gpu_experiment.py` SHA-256 `3c5a76ec0e02fc3bc8f1e5e8215d446c1fed66ce79bc346b47dce2eb2a1a9eb1`。構文検査のみ、GPU未実行。

### Goal再開時の公式状態・新規公開Notebook確認（2026-11-06 20:10 JST）

- Kaggle公式MCPでcompetition metadata/rules/leaderboardを再取得。API deadline `2027-01-14 23:59 UTC`、Balanced Accuracy、Notebook-only、1日5提出・最終提出2件を確認。Overview Timeline本文はAPIから空で、過去に記録した1/13 vs 1/14不一致は未解決のまま。公開首位はLe VietとHod Carriersの0.747同率、次点0.743。公式順位は [Leaderboard](https://www.kaggle.com/competitions/name-that-llm/leaderboard)、規則は [Rules](https://www.kaggle.com/competitions/name-that-llm/rules)。
- Notebook検索で `goutamsharma12/stylodeberta` を発見し、詳細APIが返すversion 1 (T4) の全セルを確認。検索APIのlast-run表示は2026-11-06だが、詳細metadataは2026-11-03を返し、実行時刻はAPI間で不一致。Notebookはprompt単位StratifiedGroupKFold 5-foldを使う一方、OOF確率に対して同じOOF正解率を最大化する形でmarginal recentering係数を選択しているため、その報告値は独立な校正評価ではない。またtrain全体でTF-IDFをfitしてからfold分割し、validation文書を語彙選択へ含める。内容は候補の着想には使えても比較用OOFの根拠としては採用しない。取得したセル出力にBAや提出scoreはなく、公開LB順位もMCPからはNotebook別に確認できない。候補01 (foldwise Qwen3-8B + Open Pool) はこのNotebook情報だけでは変更しない。
- GPU1 RTX PRO 4500 Blackwellを再照会: 空き31,929/32,623 MiB、利用率0%。利用可能な別個のcompute-process一覧取得はこの実行面から安定しなかったため、GPU空き状況のみを安全保証とはしない。新たなGPU/重い処理は起動していない。
- `statusline` 5時間利用枠の残量は引き続き未取得。既存ルールどおり依存導入・重みdownload・GPU pilot/full CVは開始しない。今回の実質的な進捗は公式状態の更新と、公開候補のOOF校正に関する独立性監査。次は現行runner/venv/artifactを再確認し、残量情報なしでも可能な短い読み取り調査と安全な準備を続ける。

### 候補01の再開可能性・外部依存再監査（2026-11-06 20:13 JST）

- goalの実装開始指示は受領済み。Kaggle側は再取得時点でも公開首位0.747、API deadline 2027-01-14 23:59 UTC、daily submissions 5、Notebook-only。Rulesでfinal submissionsは2件を確認。APIのOverview Timeline本文が空のため締切は早い方を採用する方針を維持する。
- GPU hostでrunnerを含むjobなし。142-X10DAi GPU1 RTX PRO 4500 Blackwellは31,929/32,623 MiB free・0%、GPU compute-app一覧空。MemAvailable 209 GiB。GPU0 A4000は15,960/16,376 MiB free・0%。他研究のGPUは変更していない。
- 外部projectの専用`.venv`はPython 3.12.3 + pip 24.0のみ。候補重み/pilot/full OOFはなく、保存済みconfirmation baseline OOF・診断とpool-filter auditのみ存在。`gpu_experiment.py` SHA-256 `3c5a76ec0e02fc3bc8f1e5e8215d446c1fed66ce79bc346b47dce2eb2a1a9eb1`、`gpu_analyze.py` `66343912b03724ec6fa84ddfdec34bc0364d9d9b21c440828f2f78051d4ac60`、`gpu_confirmation_baseline.py` `dd4020dc656e6bde57d8a5f71a9590624e91d488b9240bbcc7c2a32035d0ac30`、`gpu_data_audit.py` `787d95f622416225dd265ec88939dfcf739b95e3eaf612dcfe19058ba6454534`。候補runnerはlocal-only weights、二重preflight、2,500/class cap、epoch checkpoint/resumeを現行コードで確認。GPU runtime検証はまだ。
- 公式Kaggle Model APIでQwen3-8B-Base `qwen-lm/qwen-3/transformers/8b-base` version 1、Apache 2.0、16,393,043,378 bytesを確認。Dataset APIのOpen Pool current versionは15、212,623 rows、CC BY-SA 4.0で、configと一致。外部cache/project内にモデルweightsはなく取得が必要。
- 利用枠の15%条件はstatusline残量をこのagent面から取得できず、既に一度ユーザーへ照会して回答は未着。専用venvへの依存install、16.4GB model download、CUDA pilot/full CVは引き続き保留。Kaggle GPU週次枠も未確認。読み取り監査でrunner/source/config/data versionの不一致は見つからず、次工程は利用枠確認後の依存固定環境構築→重み取得→pilot。

### 公開上位手法と単体Qwen比較値の追加確認（2026-11-06 20:15 JST）

- Kaggle公式Notebook APIのscore-descending検索で `aboodps/ntl-672-sinkhorn-050` version 1 (2026-11-03, T4) を読了。著者記載のbest Public LBは0.672で、現在の公式トップ0.747を0.075下回る。Notebook本文ではV1/V2/V3を0.672と記す一方、「下のcode cellsは0.668を出したversion」とも説明しており、完全再現証拠ではなく著者レポートとして扱う。多数の公開data/model/kernel inputs (metadata上合計35)を使う複合stackで、Qwen3-14B/8B・Llama 3.1 8B・Qwen2.5、DeBERTa、4-view SVC、test prompt clustering/twin/Gaussian、soft Sinkhorn、typography、sibling residual、pairwise verifier、ATLASを含む。構成全体を一度に移植せず、各部品をOOFで切り分ける必要がある。
- Discussion [What score your best single model can achieve?](https://www.kaggle.com/competitions/name-that-llm/discussion/754860) の投稿者報告では、単体Qwen3-8B LoRAがOpen Pool v10使用時にOOF BA 0.6224 (fold: 0.589/0.598/0.654/0.626/0.645)、Public LB 0.628。v10より新しいv15・今回のfoldwise leak filtering・stage1 pool plus stage2 official-fold adaptationにより条件が異なるため直接再現値ではないが、Qwen3-8B + clean poolという候補01の優先度を裏付ける実測近似例である。
- 現在公開されている方法の報告値と公式leaderboard首位には少なくとも0.075差がある。候補01は有望な比較用base候補として維持し、その後は同じprompt-grouped splitのOOFを確保してから、残るfamily confusionに対するsibling residual等を独立候補として調べる。0.672等のPublic LB報告だけでは採用判断に使わない。

### preregistered trainable layer設定の不整合修正（2026-11-06 20:18 JST）

- 読み取り監査で、immutable configは`trainable_layers: 24`なのに、`build_model()`のPEFT `LoraConfig`がlayer filterを渡しておらず、対象linear modulesすべて＝Qwen3-8Bの全36層へLoRAを付ける実装だと判明。公式Qwen3-8B metadataは36 decoder layers。設定値を無視するコード不整合なので実験前に修正した。
- `gpu_experiment.py`は`trainable_layers`をmodel configのlayer countと照合し、PEFTに`layers_to_transform=list(range(24))`と`layers_pattern="layers"`を渡す。adapter後に実際のLoRA parameter名から変換対象indexを集め、期待する`0..23`と完全一致しなければ停止し、選択層をJSON logへ記録する。これはconfigに事前登録した24-layer条件を実装する修正で、config/hypothesis/hyperparameter自体は変更していない。`py_compile`成功。runner SHA-256は`f0e04f90012d385319af0b99b1ff9bafd6698b2571e24c1c9ed38a6aa18660fd`。
- 依存未導入・model未取得のためPEFT実runtimeでmodule match確認は未実施。API契約は固定依存版の[PEFT v0.17.1 LoraConfig](https://github.com/huggingface/peft/blob/v0.17.1/src/peft/tuners/lora/config.py)を、Qwen module pathは固定版[Transformers v4.57.1 Qwen3 implementation](https://github.com/huggingface/transformers/blob/v4.57.1/src/transformers/models/qwen3/modeling_qwen3.py)を参照。重いinstall/download/pilotは15%利用枠残量が未確認のため未開始。

### 公式stateと利用枠参照先の再確認（2026-11-06 20:19 JST）

- Kaggle official metadata/leaderboard/datasetを再取得。deadline API `2027-01-14 23:59 UTC`、daily submissions 5、Notebook-only、top score 0.747同率、Open Pool v15・212,623 rowsが継続。公式Rulesのfinal submissionsは2件。141/142で候補job/compute-appなし、GPU1 31,929 MiB free・0%、host MemAvailable 209 GiB。専用venvはPython 3.12.3 + pip 24.0のみ。Qwen weights/pilot/OOFは未作成。
- 修正後runner hash `f0e04f90012d385319af0b99b1ff9bafd6698b2571e24c1c9ed38a6aa18660fd`維持を確認。PEFT/transformers package importを伴う層選択runtime検証は依存未導入のため未実施。
- 利用可能なKaggle MCPにはNotebook実行状態以外の個人GPU quota getterがなく、agent tool listにも5時間statusline getterがない。Kaggle公式の[Efficient GPU Usage](https://www.kaggle.com/docs/efficient-gpu-usage)はGPU利用状況確認先としてNotebook Settings、`kaggle.com/notebooks`、profile page、session managementを案内するが、このAPI/agent面から個人quota値は取得できなかった。状況を推測で補わず、利用枠ガードを維持する。

### preregistered scheduler設定の実装修正（2026-11-06 20:20 JST）

- 候補runnerとimmutable configを再照合したところ、configのstage1/stage2両方に`warmup_ratio: 0.1`・`scheduler: cosine`がある一方、runnerはoptimizerへ固定LRを渡すだけでschedulerを適用していなかった。これは実験条件と実装の不一致。
- runnerへTransformersの`get_cosine_schedule_with_warmup`を追加し、各stageのdataset長・effective batch rows・epoch数からoptimizer総step数とwarmup step数を計算するよう修正済み。各optimizer step後にschedulerを進め、epoch checkpointへscheduler stateを保存し、resume時に復元する。非cosine値・旧checkpointにscheduler stateがない場合は黙って別条件で続行せず停止する。config/hypothesisは変更していない。
- 候補専用`.venv/bin/python -m py_compile src/gpu_experiment.py`成功。config読込でstage1/2双方のcosine・0.1 warmup・epoch数（1/2）と共通effective batch rows 18を確認。runner SHA-256 `37880adb5ad7dc7cc1aec3508502bc87233ad667a496bce11ffa890f0fd642e6`。
- これは静的な構文・設定確認のみで、Transformers/PEFT依存が未導入のためscheduler実runtime確認・GPU pilotは未実施。5時間利用枠15%ガードの残量も未確認のため、依存導入・重みdownload・長時間runは保留。

### scheduler修正後の実行資源再確認（2026-11-06 20:22 JST）

- GPUの読み取り診断ではGPU1 RTX PRO 4500 Blackwellが31,929/32,623 MiB free・0%、GPU0 RTX A4000が15,960/16,376 MiB free・0%。host MemAvailableは209.2 GiB。`nvidia-smi --query-compute-apps`は空で、候補runner/analyzer/confirmation runnerの既存プロセスもない。
- これは空き資源の観測で、予約確認や15%利用枠の確認を代替しない。GPU使用・依存導入・weights取得・Notebook提出は開始していない。次に進む条件は5時間利用枠の残量確認であり、回答が来るまでは短時間の読み取り監査と軽いコード整備を続ける。

### runnerのconfig適用監査と早期拒否（2026-11-06 20:25 JST）

- preregistered configとrunnerの読み取り箇所を照合。現行値は一致するものの、BF16、micro-batch 1、AdamW、pilot sequence length、およびpoolファイルversion/nameの一部がrunner側で固定されていた。`validate_runtime_config()`を追加し、実装が対応しない値ならpreflight前に停止する。Open Poolのversion・main/prompt filenamesはconfigからpath解決するよう変更（pilotとfull load双方）。
- runnerの構文compile成功。依存未導入のため通常importは`numpy`不足で失敗したが、validator関数だけをAST抽出して現行configに適用しPASS。これは限定的な設定検査であり、PEFT/Transformersや実データを含むruntime確認ではない。runner SHA-256 `74df75efc62956b9d831d13baf69f2a08fb8b848bc797cdc5029be890e0e0308`。
- Kaggle公式metadataを再取得: API deadline `2027-01-14 23:59 UTC`、Balanced Accuracy、Notebook-only、daily submissions 5。overridePublic leaderboard先頭は引き続きLe Viet 0.747 / Hod Carriers 0.747、次点0.743。final submissions 2件のRules確認は直近公式参照（20:19 JST）の結果を維持。公開上位は変わらず、候補順位付けに新しい性能証拠はない。
- 有効なagent tool listを再照会したが、5時間rate-limit/statusline getterもKaggle personal GPU-quota getterもない。重い依存導入・model download・GPU runは未開始。

### OOF解析器とCPU比較基準の対応確認（2026-11-06 20:26 JST）

- `gpu_analyze.py`はprimary splitで保存済みCPU best OOFを、confirmation splitでは同じ確認分割のCPU baseline OOFを結合し、ID・prompt_id・fold・正解ラベルの一致を要求する。prompt単位を復元抽出する2,000回以上の対応bootstrap、concatenated OOF BA、fold別BA、クラスrecall、混同行列を出力する実装を読み取り確認。
- primary baseline artifact `07-05-function-view-candidate/oof.parquet`は存在し、隣接metrics.jsonのBAは0.3845041014。これはconfigが指定するCPU best基準と一致。confirmation baselineも既存artifactがあると確認済み（前回記録のBA 0.373768）。解析は未実行でcandidate OOFも未生成。
- workspace `git diff --check`は通過。CPU成果物には書き込みなし。実行条件・公式上位の最新値を踏まえても現時点の有力な次候補はfoldwise Qwen3-8B + clean Open Pool v15のpreregistered候補01を維持。

### 実行再開時の入力hash照合（2026-11-06 20:28 JST）

- 現runner・analyzerの`py_compile`を再確認して成功。runner SHA-256 `74df75efc62956b9d831d13baf69f2a08fb8b848bc797cdc5029be890e0e0308`、analyzer `66343912b03724ec6fa84ddfdec34bc0364d9d9b21c440828f92f78051d4ac60`、config `109cc0a01591ed16b11a7ee138b8fca8297a676fd2fb900c1d64a8b207bd41ab`。
- `pool-filter-audit.json`記録のconfig/train/Open Pool/prompt復元SHA-256は現在の実ファイルと全て一致。既存leakage auditの基礎入力が変更されていないことを確認。
- 最新読み取り診断: GPU1空き31,929/32,623 MiB・0%、GPU compute-processなし、host MemAvailable 211.8 GiB。これらは予約の有無・利用枠残量の確認ではない。利用枠status getterはtool listに見当たらず、重い作業は未開始。

### OOF採用後のfinal fitとローカルbundle経路（2026-11-06 20:32 JST）

- 公式全train promptの類似groupをOpen Pool v15からまとめて除いた場合のclass別件数を読み取り再計算。matched canonical groups 12、最少classでも3,541行残り、固定2,500/class capを満たす。
- runnerに`--fit-final`を追加。primary/confirmation双方のprompt-paired bootstrapが`adopt`でない限り開始を拒否し、全train prompt除外後の均等poolでstage1、official全trainでstage2をfitする。完成後はadapter・tokenizer・classifier head・metadata・公式sample submissionと同じ列/IDで作るローカル`submission.parquet`を一時bundleへ保存し、全て完了してから`final-model/`へatomic renameする。既存bundle/stagingは上書きしない。
- 公式sample schemaは`id, model`、test idは`id`・文章は`text`。全train prompt除外poolはcapを満たした。runnerの`py_compile`成功、現SHA-256 `e6d632de1af6cb60aa802c286df57ea47b229f06eccae87d05d8d52f689c0277`。
- これは経路の実装とCPU側のpool件数監査であり、OOF candidate、pilot、final fit、test predictionはいずれも未実施。GPU運転には引き続き15%利用枠確認とpassing pilotが必要。
- 20:33 JSTの公式MCP再確認でもdeadline APIは`2027-01-14 23:59 UTC`、daily submission上限5、Notebook-only、公開top 0.747同率/次点0.743で変化なし。GPU1は31,929 MiB free・0%、host MemAvailable 211.8 GiB、compute app一覧空。Kaggle GPU週次quotaとCodex 5時間残量はいずれも取得できていない。

### goal再開後のcheckpoint cache発見と候補02事前登録（2026-11-06 21:58 JST）

- ユーザーの再開指示を受けたfresh auditでgoalを継続。候補runner・analyzer・候補01 configのhashは直前記録と一致。candidate/pilotプロセス・GPU compute appなし。GPU1空き31,929/32,623 MiB・0%、host MemAvailable 208.0 GiB。
- HF cacheに完全な`Qwen/Qwen3-8B` snapshot (`b968826d9c46dd6066d109eabc6255188de91218`)を発見。全5 weight shard・config・tokenizerが揃い、各shard名/サイズはKaggle `qwen-lm/qwen-3/transformers/8b` version 1の公式file listと一致。公式variationはQwen3-8B「Pretraining & Post-training」、36層、Apache 2.0、16,397,448,180 bytes。preregistered候補01の`8b-base`とは別のcheckpointなので流用せず、同一pool/分割/学習条件で比較する候補02を作成。
- 候補02 config `configs/gpu02-qwen3-8b-posttrained-openpool-v15.json`を未実行・事前登録状態で保存。候補01との差分はcandidate id/hypothesis/model checkpoint metadataだけ。isolated runtime-config validator PASS。config SHA-256 `23f620d66d6f15b154bf52d1544138d13b74a0d61c6523a1f75f252dc73246b8`。
- cache発見はmodel取得作業を不要にするが、依存は候補専用venvにpipのみでCUDA runtimeなし。5時間利用枠残量とKaggle個人GPU週次quotaは未取得のままなので、install・pilot・学習は開始していない。公式競技metadataはdeadline `2027-01-14 23:59 UTC`、daily 5、Notebook-only、LB top 0.747同率で継続。

### 利用枠ガード通過・候補02 primary OOF起動（2026-11-06 22:24 JST）

- ユーザー指定の`python3 -I .agents/skills/kaggle-workflow/scripts/codex_rate_limit.py --guard 15`を実行。22:24:30 JST時点で5時間枠残量92%（used 8%、reset 2026-11-07 02:57 JST）、週間枠残量82%（reset 2026-11-12 14:41 JST）、status=ok。最初のsandbox実行は`bwrap: loopback: Failed RTM_NEWADDR`で起動できなかったため、同じ読み取り用途のコマンドを承認済み実行面で再試行し、成功。
- 候補02専用`.venv`へlock済み依存を導入済み。Python 3.12.3、torch 2.9.0+cu128、transformers 4.57.1、PEFT 0.17.1等。GPU pilotはpass_reserve=true、1例あたり1.5083秒、peak reserved 15,332 MiB（preflight上限23,510 MiB）。pilotはconfig hash `23f620d66d6f15b154bf52d1544138d13b74a0d61c6523a1f75f252dc73246b8`、runner hash `3bd614d95d8cdda0b521d98f940a5c127ded2981f1399bd64e1f3f3222c63aca`に対応。
- 22:22 JST頃、142-X10DAiのGPU1（RTX PRO 4500 Blackwell、UUID `GPU-8a059266-7ede-0427-ff30-08ba7a9b5224`）でprimary 5-fold OOFを開始。nvidia-smi ordinal 1だがTorch ordinal 0であることをUUID照合し、対象UUIDへ限定して実行。GPU0 RTX A4000は未使用。実行時config/runner hashは上記と一致。
- 起動コマンド: `cd /mnt/HDD10TB-2/aburatani/kaggle/name-that-llm && flock -n artifacts/.gpu1-run.lock .venv/bin/python -u src/gpu_experiment.py --config configs/gpu02-qwen3-8b-posttrained-openpool-v15.json --model-path /home/aburatani/.cache/huggingface/hub/models--Qwen--Qwen3-8B/snapshots/b968826d9c46dd6066d109eabc6255188de91218 --run-dir artifacts/gpu02-qwen3-8b-posttrained-openpool-v15 --split primary --resume`
- wrapper PID `2827673`、Python PID `2827674`、lock `artifacts/.gpu1-run.lock`、log `artifacts/gpu02-qwen3-8b-posttrained-openpool-v15/primary-run-retry1.log`、host `142-X10DAi`。再開時は同じコマンドを同じconfig/run-dirに対して使い、`--resume`を維持する。プロセス確認ではfold0のofficial train 2,159行・validation 540行・30 validation prompts、prompt類似group 2個を除外、external pool 45,000行（18ラベル各2,500件）、LoRA対象層0–23/36を確認。直近GPU確認では対象PIDのみがGPU1を使用（15,648 MiB、29% util）、GPU0は18 MiB使用・0%。まだepoch/fold完了・OOF指標は出ていない。
- 現runはこの記録時点で継続中。固定依存、pilot、実装上のUUID/PEFT/RNG/preflight修正の経緯はこの節より前の作業履歴とcandidate pilot artifactを参照。公式Kaggle GPU週間quotaは引き続きこの実行面から取得できていないため、Kaggle Notebook GPU実行は未開始。

### goal継続時の利用枠・公式状態再確認（2026-11-06 22:26 JST）

- `codex_rate_limit.py --guard 15`を再実行し、5時間枠92%、週間枠82%、status=okを確認。プロセスPID `2827674`は生存し、同PIDだけがGPU1を使用。GPU1 free 16,272 MiB / 29% util、GPU0 free 15,958 MiB / 0%。ログはfold0のLoRA層選択後からまだepoch/fold完了を記録していない。
- Kaggle公式MCPを再取得。競技期限は`2027-01-14 23:59:00.817 UTC`、Balanced Accuracy、Notebook-only、最大5 submissions/day。公式Rules本文でfinal submissionsは最大2件。公開LBはLe VietとHod Carriersが0.747で同率首位、次点Team Aillis 0.743。Overview timeline APIは空応答のまま。公式ページ: [Overview](https://www.kaggle.com/competitions/name-that-llm)、[Rules](https://www.kaggle.com/competitions/name-that-llm/rules)、[Leaderboard](https://www.kaggle.com/competitions/name-that-llm/leaderboard)。Kaggle Notebook GPU実行・提出はまだ行っていない。
- 現在runを重複起動せず継続する。次回run確認はspecの監視間隔に従い、10分以上空けてからPID・ログ・GPUを再確認する。

### OOF待機中の公開知見・外部データ再監査（2026-11-06 22:29 JST）

- KaggleのNotebook検索（実行順・score順）とDiscussionを読み取り確認。新しく確認できた公開上位手法は、作者主張Public LB 0.672+の[Dual-SVC Residual Refinement Apex](https://www.kaggle.com/code/ozertuu/0-672-dual-svc-residual-refinement-apex)と、[v21 Apex Grandmaster](https://www.kaggle.com/code/omkarpattanaik123/name-that-llm-v21-apex-grandmaster-sovereign)。後者は作者レポートとしてnested CV 0.6865とPublic LB 0.56の大差を併記し、同じコードでもPublic LBが揺れると記す。確認したv21 sourceは複数LoRA、Open Pool/SVC、shared-prompt Gaussian、ATLAS、Sinkhorn等を含む大規模stackで、単一手法の改善根拠にはならない。上位codeのscoreは自己申告として扱い、公式LB top 0.747を超える証拠は見つからなかった。
- Dual-SVC Notebookはmetadata上、19 datasets・8 model sourcesを接続し、Qwen/LoRA群、Open Pool SVC、ATLAS、Sinkhorn、sibling residual、pairwise verifierを組み合わせる。本文はA/B Public LB値を示すが、MCP検索の最終実行時刻とNotebook metadata/papermill実行時刻に不一致があるため、score・再現値は作者報告と区別する。候補02 OOFが終わる前にこの複合stackを移植・追加実験する根拠は不足しており、実行中configは変えない。次の候補はprimary/confirmation OOFと誤り分析を見て選ぶ。
- Open Poolの公式Dataset metadata/version 15を再取得。CC BY-SA 4.0、説明上212,623行で、competition dataを含まずtrain copies・train content近似・train promptsへの回答はないと作者が記載。旧版からtrain-prompt answers 284行を除外した記録があり、今回run開始時のcreator flags除去は0行、foldごとのprompt類似除外も別途記録済み。新規Discussion [外部データにcompetition textを送ったAI annotationの確認依頼](https://www.kaggle.com/competitions/name-that-llm/discussion/756466)は参加者から主催者への質問のみで、取得時点で主催者回答は見えない。これはOpen Poolの生成方法を問う投稿ではなく、公式判断として扱わない。今後、competition textを第三者LLMへ送るデータやその派生annotationは候補へ加えず、Open Poolのprompt/train-content filterを維持する。
- Research Workspaceのtracked diffに、承認済みspec frontmatterの`execution_status`が`awaiting-implementation-start`から`in-progress`へ変わったユーザー側変更を確認。こちらではspecを編集しておらず、現行goalの実装開始指示と整合する。外部Kaggle作業ディレクトリはGit repositoryではないため`git status`による差分列挙はできなかったが、候補02 runner/configの現在hashは実run preflight記録と一致し、実行中入力の差し替わりは確認されなかった。

### 単体Qwen3-8Bの追加公開報告（2026-11-06 22:33 JST）

- Competition Discussion「[What score your best single model can achieve?](https://www.kaggle.com/competitions/name-that-llm/discussion/754860)」で11月6日の新しい返信を確認。投稿者はQwen3-8B単体LoRA（Open Pool v10を2,500/label capで使用）についてOOF BA 0.6224、fold 0.589/0.598/0.654/0.626/0.645、Public LB 0.628を報告。さらに同モデルにDeBERTa、SVC群、stylometryを加えたblendは0.635と報告し、差は1ポイント未満。これは投稿者報告で、同一configの再現値ではない。比較時にfold spreadとPublic LBの揺れを考慮する。
- 同じthreadの別返信はModernBERTをOpen Poolでpretrainしてtrain上で5-fold LoRAした結果としてCV 0.616 / LB 0.575を報告。Qwen3-14Bで約0.670との別報告は作者自身の追加データを含むと返信しており、本specの公開・無償・他参加者も合理的に入手可能という条件に沿う候補比較値とは分ける。
- 公開Qwen3-8B実績は現在の候補02（同じmodel family、より新しいOpen Pool v15、foldwise prompt除外、pool→official trainの二段階学習）を継続する判断を補強するが、実験条件が異なるため目標値の保証には使わない。実行中configは変更しない。

### Prompt-dependent validationのtest-like subsampling報告（2026-11-06 22:35 JST）

- [同じDiscussion threadのGoPain返信](https://www.kaggle.com/competitions/name-that-llm/discussion/753177)を精読。著者はblend 15提出（Public LB 0.593–0.621）で、全18回答prompt OOFとPublic LBの相関が低い一方、validation promptごとにm=2行へsubsampleしたOOFは15件全体でPearson 0.79 / Spearman 0.58と報告。ただしm=2で次の5候補を選んだ後は順位予測できず、162設定からの事後選択、単一blend family、小標本、1つの外れ値に依存する弱いsanity signalだと投稿者自身が注意している。
- この候補02単体分類器はprompt-centering/同一prompt相互依存を使わず、primary採否はpreregistered全OOF＋対応ありprompt bootstrapで評価する。将来prompt-dependent postprocessを候補化する場合は、specどおりhidden testのprompt構成を決めつけず、m=2/3等のsimulationを補助評価にする。ただし本報告はPublic LB上の順位づけを保証しないため現run/configは変えない。

### OOF proxy選択とPublic LBの小標本性（2026-11-06 22:36 JST）

- [Discussion「Ten LB points can't tell you which OOF to trust」](https://www.kaggle.com/competitions/name-that-llm/discussion/754084)を確認。作者のGaussian simulation（180,000 seasonsを含む公開code/dataと記載）では、複数OOF proxyからPublic LB相関が最高だったものを選ぶと、その見かけの相関が上方へ選択biasを受け、次の上位候補5件の並びはLB noiseで弱くなる傾向を示す。著者は次候補を選ぶ際、LBで最も相関した単一cutだけではなく、全cutで改善することを要求している。これはsimulation仮定に依存する投稿者分析で、competitionの真のLB noise分布を証明するものではない。
- この知見はspecのprompt-bootstrap採否、primary/confirmation二分割、Public LB単独で過剰調整しない方針を補強する。Public LBの上位値を選び直す目的でtest-like cutを使わず、現candidate02のOOF評価規則を維持する。

### 公開adapter起因のOOF leakage監査知見（2026-11-06 22:38 JST）

- 公開Notebook [Leak audit: is your holdout really held out?](https://www.kaggle.com/code/weywuy/leak-audit-is-your-holdout-really-held-out) version 3を確認（作者記述は中国語、最終run metadataは2026-11-03）。作者は、community 6-member blendの5つのLoRA adapterがfull official trainでfit済みなのにprompt-grouped 1/5 holdoutへ使用され、BA 0.913を出した例を共有。これはOOFと呼んでも学習済みadapterがvalidationを見ているため不正な評価であり、authorは既学習community modelの再利用で高すぎるOOFが出る危険を説明している。
- 候補02ではbase Qwen3-8B post-trained checkpointから各fold内でadapterを初期化し、fold validation prompt groupをstage1外部poolから除外、stage2のofficial trainから除外する設計。community adapterやfull-train learned headをOOFへ流用していないため、このspecific leakage経路は確認されない。今後もOOF候補はfoldごとの自前fitで評価する。
- 同Notebookは公開LB標準誤差を約0.007と推算するが、作者の記述中のtop value 0.683は当日の公式top 0.747と異なり、数値は近似・投稿者仮定（test各class約220件）に基づく。公式topや不確実性の確定値とは扱わない。この留意点も含め、submissionの小差を断定根拠にしない。

### primary OOF稼働確認・利用枠checkpoint（2026-11-06 22:30 JST）

- `codex_rate_limit.py --guard 15`はstatus=ok。5時間残量90%（used 10%、reset 2026-11-07 02:57 JST）、週間残量81%（reset 2026-11-12 14:41 JST）。
- Python PID `2827674`とflock wrapper PID `2827673`は稼働中（elapsed 7:45）。RTX PRO 4500 GPU1上で同PIDの計算プロセスを確認、約15,648 MiB使用・29% util・空き16,272 MiB。RTX A4000は空き15,958 MiB・0% utilで未使用。ログ末尾はfold0 LoRA層選択（36層中0–23）で、epoch/fold checkpoint・OOF指標はまだ出ていない。runner/config hashは起動時と一致。
- runnerのepoch処理を読み取り確認。学習中のbatchごとの進捗イベントはなく、`checkpoint_saved`/`epoch_complete`はepochを終えた後にだけ出力する。fold0のstage1対象は45,000例で、pilotの単例step時間1.508秒をそのまま当てはめる概算では最初のcheckpointまで約18.9時間。したがって開始後9分弱で新規ログやcheckpointがない状態は現時点では異常の証拠ではない。これは時間見積もりであり実測epoch時間ではない。
- 出力先を含む`/mnt/HDD10TB-2`は9.1 TiB中1.6 TiB使用・7.1 TiB空き（18%）、HF cacheのあるroot filesystemは3.6 TiB中805 GiB使用・2.7 TiB空き（24%）。現行runのcheckpoint保存に対するディスク容量の懸念は見えていない。

### 候補01のBase checkpoint取得・照合（2026-11-06 22:52 JST）

- Candidate01 configは変更せず、状態`preregistered-not-run`を維持。Kaggle CLI取得は認証情報不在で使えなかったため、公開公式HF repo `Qwen/Qwen3-8B-Base` の固定revision `a64df03b50f8fdeb56e303ed2dd5228dc149f926`から取得した。ローカルcacheは実装側 `artifacts/model-cache/candidate01-qwen3-8b-base-hf-a64df03/`。競技データや提出物ではなく、公開モデル重み。
- 5つのsafetensors shardのSHA-256を全件検証し、HFの同revisionで事前取得した期待値とすべて一致。Kaggle Model variation `qwen-lm/qwen-3/transformers/8b-base` version 1とはファイル名・サイズが一致するが、Kaggle APIがhashを提供しないためKaggle側ファイルとのbyte-identicalまでは主張しない。取得元はあくまで固定HF revision。
- Baseとcandidate02のpost-trained `config.json`をCPUで比較。どちらも`Qwen3ForCausalLM` / 36層 / hidden size 4096 / vocab 151,936 / bfloat16。`max_position_embeddings`のみBase 32,768・post-trained 40,960で異なるが、事前登録済み`max_length=384`より十分大きい。候補01は同じrunner系統で扱える見込みだが、実学習前のpilotで確認する。
- 候補02のprimary OOFは別GPU上で継続中のためcandidate01学習は開始しない。次に実行する場合は候補01専用のGPU UUID/空き容量確認とmodel-load/forward/backward/optimizer-step pilotを行い、passしてから同じ承認済みspecの範囲で着手する。重み取得完了は学習結果ではない。

### 公式条件・Kaggle CLI認証の再確認（2026-11-06 22:54 JST）

- 公式Kaggle MCPでcompetition metadata・rules/timeline/evaluation/code requirements・Public Leaderboardを再取得。metadataの期限は`2027-01-14 23:59 UTC`だが、Timeline本文は`2027-01-13 23:59 UTC`と表示する不一致が継続しているため、specに従い早い方を期限計画に使う。Balanced Accuracy、Notebook-only、1日5提出、Final Submission最大2件、CPU/GPU各9時間、Internet無効を再確認。公開首位はLe Viet 0.747、同点Hod Carriers 0.747、次点Team Aillis 0.743。変更なし。
- Notebook書き込み前提の認証状態を公式CLIの読み取り専用`competitions list --search name-that-llm`で確認したが、Kaggle APIは`Authentication required`を返した。資格情報の値は表示していない。よってKaggle CLIの書き込み可否は未確認のままで、Notebook push/submissionは行っていない。ローカルOOFと候補選定は継続できる。

### candidate02 primary OOF稼働監視（2026-11-06 23:02 JST）

- `codex_rate_limit.py --guard 15`: 5時間残量82%、週間80%、status=ok。
- wrapper PID `2827673`とPython PID `2827674`は生存（elapsed 40:48）。指定GPU1 UUID `GPU-8a059266-7ede-0427-ff30-08ba7a9b5224`上で同PIDだけを確認し、GPU使用15,648 MiB、nvidia-smi utilization 29%、free 16,272 MiB。GPU0 A4000は18 MiB・0%。host MemAvailableは204 GiBで、16 GiBの新規重処理下限を十分上回る。
- 出力ディレクトリにはpilot、run pid、run logのみでcheckpointはまだない。最新ログはfold0のLoRA層選択（36層中0–23、2026-11-06 22:23 JST）から変化なし。pilotの単microbatch時間約1.508秒に対しfold0 stage1は45,000例なので、epoch完了まで相応の時間を要する想定。ログ更新がないだけでは異常終了と判断せず、同じrunを維持する。

### 141別GPUでのcandidate01並列可否診断（2026-11-06 23:05 JST）

- 承認spec対象の141を読み取り確認。host `141-X9DAi`の3 GPUはいずれもRTX A4000 16,376 MiB。計算プロセスなし、使用量は15–171 MiB、free 15,802–15,960 MiB。MemAvailable 121 GiB。
- 空いてはいるが、candidate01のbase checkpointだけで16,393,043,378 bytes（約15.3 GiB）。各A4000で最低4 GiB（全VRAMの25%より大きい）の予備を残すpilot範囲を満たせない。安全基準によりmodel load/pilotも並列学習も開始しない。141の空き観測はGPU予約を意味しない。candidate01は候補02完了後に、より大きく安全なGPUを起動直前に再診断して実施可否を判断する。

### Mistral/OLMo 2段階LoRAに関する新しい作者報告（2026-11-06 23:07 JST）

- Kaggle Discussion「[Looking to merge: unique Mistral/OLMo LoRAs with full OOF + fresh Gemini data (public 0.663)](https://www.kaggle.com/competitions/name-that-llm/discussion/756294)」を再確認。作者はMistral-7BとOLMo-2-7Bのtwo-stage LoRAについて、expanded poolを使ったfull prompt-grouped 5-fold OOF BA 0.60、Public LB 0.663を報告し、曖昧クラスの誤り表とfresh Gemini生成文も提示可能と記載。取得時点で返信・コード・データ詳細なし。すべて投稿者報告で独立再現ではない。
- 投稿の主目的はteam merge募集で、expanded poolと新規Geminiデータの出典・公開性・競技テキスト生成手順は未検証。merge申請や連絡、当該データ・予測の受領は行わない。将来の独立候補にする場合は、公開base modelと適格な公開データだけでfold内学習し、候補02のprimary/confirmationと同じ評価・prompt filteringを行う。実行中candidate02の変更根拠にはしない。

### candidate02 primary OOF稼働監視（2026-11-06 23:12 JST）

- `codex_rate_limit.py --guard 15`: 5時間残量81%、週間80%、status=ok。
- wrapper PID `2827673`・Python PID `2827674`は生存（elapsed 50:15、Python state `Sl`）。GPU1 UUID `GPU-8a059266-7ede-0427-ff30-08ba7a9b5224`で同PIDだけを確認し、使用15,648 MiB、使用率31%、free 16,272 MiB。GPU0は18 MiB・0%、host MemAvailable 204 GiB。
- run directoryにcheckpointはなく、ログ末尾は引き続きfold0 LoRA層選択。runnerはepoch境界でのみcheckpoint/logを保存する。fold0 stage1は45,000件をbatch size 1で処理し、pilotは1.508秒/microbatchだったため、開始約50分で未完了なのは想定範囲。生存・GPU計算・RAM安全を確認したため同じrunを継続し、次の監視も10分以上空ける。

### 新着NotebookのCV・実行時刻監査（2026-11-06 23:16 JST）

- Kaggle Notebook検索の`DateRun`順で`pawankumargunjan/name-that-llm`が2026-11-06 14:13:58 UTCに実行された表示を確認。ただし`get_notebook_info`のversion 12は`last_run_time=2026-11-03 14:16:23 UTC`で、検索時刻とmetadataが一致しない。version 12のsourceは有効だが、この再実行のsource/出力との対応はAPIから確認できない。
- 取得できたversion 12 sourceでは、competition trainを行単位`train_test_split(test_size=0.2, stratify_by_column="model")`で分割し、`validation`と`test`に同一splitを渡している。`prompt_id` grouped CVではなく、modelは`/kaggle/input/notebooks/.../checkpoint-*`から見つけた`checkpoints[0]`を使い、そのcheckpointの学習範囲も同API結果だけでは確定できない。したがってこのNotebookの検証はspecのOOF比較条件を満たさず、候補や性能根拠へ採用しない。取得時刻の矛盾が解消されるまでは今日の再実行とも扱わない。

### candidate03 Mistral-7B v0.1候補の事前登録と取得（2026-11-06 23:28 JST）

- Discussion 756294の作者がMistral-7B/OLMo-2-7B二段LoRAでOOF BA 0.60・Public LB 0.663を報告しているが、team merge募集に付随する未再現値で、expanded poolと生成文の公開性・出典は未確認。そこから独立した候補として、公開base model Mistral-7B v0.1のみを採用し、community adapter/data/予測は使わない。
- Kaggle Model APIで`mistral-ai/mistral/PyTorch/7b-v0.1-hf/1`を確認（Apache 2.0、公開、15,010,167,643 bytes）。HF公式repo `mistralai/Mistral-7B-v0.1` のcommit `27d67f1b5f57dc0953326b2601d68371d40ea8da`（Apache-2.0、非gated、BF16）をローカル学習元に固定。これはHF repoのrevision固定であり、Kaggle側hashがないためKaggleファイルとbyte-identicalとの主張はしない。
- `configs/gpu03-mistral-7b-v0-1-openpool-v15.json`を`preregistered-not-run`で作成、SHA-256 `c04ff48178e363dc30c54c6e11c02083c32bc7ccc6cd63ce176cc258ccca494f`。Open Pool v15、既存primary/confirmation prompt-grouped folds、foldwise prompt除外、2-stage設定、seed、採否基準を候補02と揃え、base model情報だけをMistral用に定義。primary/confirmationいずれの学習・pilotもまだ開始していない。
- HF pinned revisionから必要なsafetensors/config/tokenizerを`artifacts/model-cache/candidate03-mistral-7b-v0-1-hf-27d67f1b/`へ取得中。取得コマンドは同じパスへの`hf download ... --revision 27d67f1b5f57dc0953326b2601d68371d40ea8da --include '*.safetensors' config.json generation_config.json model.safetensors.index.json tokenizer.json tokenizer.model tokenizer_config.json special_tokens_map.json --max-workers 4`。session 48900 / PID 2867714は23:28 JST時点で生存（elapsed 5:12）。7.0 GiBが揃い、shard 2は完了、shard 1のpartialは2,956,943,740 bytes（最終更新23:24:27）。同一session/PIDを継続確認し、partialが停止しただけで再起動しない。
- 取得済みconfig/indexはMistralForCausalLM、32層、hidden 4096、vocab 32,000、context 32,768、BF16と示す。weight indexの`model.layers.*.self_attn.{q,k}_proj`と`mlp.gate_proj`名は現runnerのLoRA regexと整合し、runnerは`pad_token_id`未設定時にEOSをpadに設定する。これはCPU上のsource/config inspectionのみ。候補03のGPU UUID・load/forward/backward/optimizer-step pilot・VRAM予備量は未測定なので、候補02終了後にGPUを再診断してから実行可否を決める。

### candidate03 pinned checkpoint取得・hash照合（2026-11-06 23:31 JST）

- 固定HF revisionから重み2 shard・config・index・tokenizer等9ファイルを取得完了。保存先`/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/artifacts/model-cache/candidate03-mistral-7b-v0-1-hf-27d67f1b/`、合計約14 GiB。
- 両shardのSHA-256がHF download時に示されたcontent hash/ETagと一致: `model-00001-of-00002.safetensors` 9,942,981,696 bytes `9742cb4764964155b7a5f35eefad651f590006091ddeb536863d6c5865cca1b9`; `model-00002-of-00002.safetensors` 4,540,516,344 bytes `9bcf56354ec0c68b5f8e97b4f3b02d16af899a65b0868d6dba5a51c1b30f01cb`。設定・tokenizerもすべて揃った。これはHF固定revisionの取得整合性でありKaggle variationとのhash照合ではない。
- 取得完了はGPU実行承認・pilot合格・学習結果を意味しない。candidate02 primary OOFの結果とGPU状態を待ち、候補03開始直前に利用枠・GPU UUID・空きVRAM・予約状況・host MemAvailableを再確認してpassing pilotを行う。

### candidate02 primary OOF稼働監視（2026-11-06 23:23 JST）

- `codex_rate_limit.py --guard 15`: 5時間残量80%、週間80%、status=ok。
- wrapper PID `2827673`・Python PID `2827674`は生存（elapsed 1:00:38）。GPU1 UUID `GPU-8a059266-7ede-0427-ff30-08ba7a9b5224`で同PIDだけ、使用15,648 MiB、使用率30%、free 16,272 MiB。GPU0は18 MiB・0%、host MemAvailable 200 GiB。
- fold0 stage1のepoch checkpointはまだない。ログ末尾はLoRA layer selectionのまま。runner/config hashはpreflightと一致し、学習を続行する。次回GPU監視も10分以上空ける。

### candidate02継続時のレート枠・公式競技情報確認（2026-11-06 23:35 JST）

- ユーザー指定の`.agents/skills/kaggle-workflow/scripts/codex_rate_limit.py --guard 15`を実行: 5時間枠79%、週間枠80%、status=ok。
- Kaggle公式MCPを再確認。API deadlineは`2027-01-14 23:59:00.817Z`、評価はBalanced Accuracy、Notebook-only、日次提出上限5、参加チーム4,884。公開LB上位はLe VietとHod Carriersが0.747で同率、Team Aillisが0.743で続く。上位構造に変化なし。
- GPUジョブは前回23:33 JSTの読み取り確認から10分未満のため、次のGPU/PID/log監視は23:43 JST以降に行う。

### 新着ルール相談とOpen Pool出典の照合（2026-11-06 23:37 JST）

- Discussion 756466は、競技train文章を第三者LLMへ送って注釈した公開データを使えるか、主催者へ質問している段階で、取得時点で回答はない。公式Rulesの2.4.bは競技データを非参加者へ提供・送信しない義務、2.6は外部データが公開・同等アクセス可能かつ合理的であることを定める。
- 実行中候補02の外部データは公開dataset `crtproduction/name-that-llm-open-pool` v15。Kaggle dataset説明は全件の品質・ジャンル・ライセンス確認済み、CC BY-SA 4.0、競技trainコピー・近似文・train promptへの回答を含まないと主張し、元の公開prompt poolからの生成も説明する。これはpublisherの説明であり独立証明とは区別する。
- 現候補は当該注釈datasetを使っておらず、競技textを第三者APIに送る処理も行わない。version 15の訓練データにはconfig済みのfoldwise train-text/近似prompt除外を適用する。Discussionの懸念はこの時点でcandidate02停止理由に該当する証拠なし。主催者回答・外部データの扱いに関する新情報が出た場合は再評価する。

### candidate02監視接続の保留（2026-11-06 23:45 JST）

- 23:43 JSTにレートガードは5時間残量78%、週間80%、status=ok。
- GPUの10分監視間隔を満たしてSSHを試したが、設定済みalias `142`でもこの実行環境の`known_hosts`に`10.10.40.142`の検証済み鍵がなく、host key verificationに失敗。鍵確認を回避して接続する操作は行わず、PID/GPU/RAMの新状態は未確認。
- 作業ツリーから見える候補02ログのmtimeは22:23 JSTで、共有ログの現在状態とは判断できない。したがって23:33 JSTの最終確認（PID `2827673/2827674`稼働、GPU1で約15.6 GiB、GPU0未使用）以後の状態を断定しない。host keyを安全に確認できるまでGPU状態依存の新規job起動・再開・停止を行わない。
- 未検証の提示鍵を`ssh-keyscan`で読むとED25519 fingerprintは`SHA256:/eihdJOcW8jNvSL9x9j9QW2Mt5C9TnyhEwLQom2ZCww`。これは信頼済み鍵ではなく、142本体/管理コンソールから確認するまでknown_hostsへ追加しない。

### candidate02 primary OOF稼働監視（2026-11-06 23:49 JST）

- 23:47 JSTのレートガード: 5時間残量78%、週間79%、status=ok。
- host 141の検証済みSSH接続から141上のknown_hostsに以前登録済みの142 ED25519鍵を読み、fingerprintが142の現在提示鍵と一致することを照合。known_hostsファイル自体は変更せず、照合済み鍵だけを使う一時UserKnownHostsFileでstrict host-key checkingを有効にして接続した。
- PID `2827673/2827674`は稼働中（elapsed 1:27:14）。GPU1 UUID `GPU-8a059266-7ede-0427-ff30-08ba7a9b5224`上でPID `2827674`が15,648 MiB、GPU1表示は15,828 MiB used / 16,272 MiB free / 33% util。GPU0 A4000は18 MiB used / 15,958 MiB free / 0%。MemAvailable 216,986,976 kB（約207 GiB）。
- remote log末尾はfold0の45,000行stage1向けfold data直後（13:23:12 UTCの層選択）で、epoch境界以外ログが出ないため新しい段階は読めない。checkpointファイルはまだ見つからない。process state `R`とGPU利用から同じrunが計算継続中と確認。再起動・停止は行わない。

### candidate04 Qwen3-1.7B事前登録・pilot・primary OOF開始（2026-11-07 00:03 JST）

- 指定rate guardは00:01 JSTに5時間枠77%、週間79%、status=ok。公式Kaggle APIを再確認し、deadline `2027-01-14T23:59:00.817Z`、Balanced Accuracy、Notebook-only、日次上限5、top 0.747同率は変化なし。
- 公開Qwen3-1.7Bを並列サイズ比較候補として事前登録。Kaggle Model `qwen-lm/qwen-3/transformers/1.7b` version 1の公開file listingは総4,079,437,039 bytes、28層。実際の取得元はHF `Qwen/Qwen3-1.7B` commit `70d244cc86ccca08cf5af4e1e306ecf908b1ad5e`、Apache-2.0。公式Hub metadataで両weight shard hashを照合: 3,441,185,608-byte shard `169ad53ec313c3a34b06c0809216e4fc072cce444a5d4ff2b59690d064130ed5`; 622,329,984-byte shard `912becff8d60672aa8628ef08c05898d9adf17c2ad4ae3caf99b065622fdeff9`。configはqwen3/28層/hidden 2048/BF16。
- config `configs/gpu04-qwen3-1-7b-openpool-v15.json` hash `3663facc16f379c977dc91025e02bde6117634869bfac951c25f209e8c8bf3ec`。candidate02と同じOpen Pool v15、近似prompt除外、primary/confirmation fold、学習stage、seed、採否ルール。LoRAは28層中20層。単独性能とOOF誤り相補性を比較する仮説。
- GPU0 RTX A4000 (`GPU-135ac6e4-8006-058e-ae74-0bb708d0f143`)でload/forward/backward/optimizer-step pilot成功。事前2 snapshotで15,958 MiB free・他compute PIDなし、MemAvailable 206.44 GiB。測定peak 3,672 MiB、必要reserve 8,156 MiB、許容上限7,636 MiB、`pass_reserve=true`、optimizer step 1.400秒。pilot後MemAvailable 204.42 GiB。
- 同一config/runner hashを保ったままprimary 5-fold OOFを00:02 JSTからnohup + GPU別lockで開始。outer launcher PID `2889691`、flock PID `2889692`、runner PID `2889693`、lock `artifacts/.gpu0-run.lock`、log `artifacts/gpu04-qwen3-1-7b-openpool-v15/primary-run.log`。00:02:58 UTC logでGPU0 UUIDに対するpreflight pass、fold0（official train 2,159行/validation 540行/30 prompts/外部pool45,000行/近似prompt group 2件除外）とLoRA対象層0–19/28を確認。結果・checkpointはまだなし。
- candidate02 primaryはGPU1で継続。00:02:51 JSTにPID `2827673/2827674`生存、GPU1のみが約15.6 GiBを使用し、GPU0 pilot/preflightおよびcandidate04とはGPU UUIDを分離。host MemAvailable約205 GiB。どちらの候補も終了・OOF score未確認。

### candidate02/04 primary OOF稼働監視（2026-11-07 00:13 JST）

- `codex_rate_limit.py --guard 15`: 5時間残量76%、週間79%、status=ok。
- candidate02: wrapper/Python PID `2827673/2827674`生存（elapsed 1:50:29）。GPU1 UUID `GPU-8a059266-7ede-0427-ff30-08ba7a9b5224`上でPython 15,648 MiB、GPU free 16,272 MiB、27% util。GPU0とは分離。
- candidate04: launcher/flock/Python PID `2889691/2889692/2889693`生存（elapsed 10:43）。GPU0 UUID `GPU-135ac6e4-8006-058e-ae74-0bb708d0f143`上でPython 3,884 MiB、GPU free 12,068 MiB、31% util。Pilot peak3,672 MiBと同等範囲。
- host MemAvailable `211,711,896 kB`（約201.9 GiB）。両runner/config SHA-256は起動/事前登録値と一致（candidate02 `23f620d...`、candidate04 `3663fac...`、runner `3bd614d...`）。
- 両logはfold0のLoRA layer selection直後で、epoch境界ログ・checkpoint・OOFはまだない。45,000例stage1を含み、runnerはepoch境界のみ進捗を保存するので、この間隔でcheckpointがないのは異常終了の証拠ではない。process alive・GPU利用・RAM余裕を確認し、同じjobを継続する。

### 公開NotebookのLB分散・test後処理失敗例（2026-11-07 00:06 JST）

- Kaggle Notebook `alexchilton/name-that-llm-0-669-all-public-what-failed` source metadata/version 16を読取。作者は同一codeの再提出で最大0.009差、prompt-grouped nested CV 0.6865の5-backbone blendがLB 0.559–0.560、prompt cluster/center追加で0.567、twin ruleで0.588、Hungarian追加で0.579だったと報告。テストのpromptごとの回答数が訓練18件と異なると後処理の効果が逆転しうる、という作者解釈を掲載。すべて投稿者の経験報告で、API上の最新metadata最終実行は2026-11-03と表示され、11/6検索表示とは一致しない。
- 同Notebookの入力source一覧には`mercurydust/ntllm-chatgpt-a-b`等が含まれ、ChatGPT A/B annotationsについてはDiscussion 756466で主催者回答待ちの規約相談が出ている。この外部annotation・adapter群の取得/使用は行わず、今回のOOF候補にも含めない。
- 次の分析ではsmall public-LB差やtrue-18-group validation上のcentering/Hungarian利得を採用根拠にせず、候補02/04の同一条件OOFと、隠れtestの少数公開サンプルを真似しないsimulationを優先する。
- Kaggle Notebook検索のScoreDescending先頭ページ（30件）では公開Notebookの最高表示は0.672+。公式公開Leaderboard top 0.747に相当する手法・Notebookは今回の検索では見つからない。これは現時点での検索範囲の結果で、未公開コードや別slugの不存在を意味しない。
- 2026-11-07 00:09 JSTの公式Rules再取得でも、2.4.bの競技dataを非参加者へ送信・公開しない要件、2.6の外部データ公開・同等アクセス/Reasonableness要件、1日5提出・final2件は同じ。Discussion 756466は依然として質問者の投稿のみで、主催者回答なし。
- 00:10 JSTの競技metadata/Leaderboard再取得でもdeadline API `2027-01-14T23:59:00.817Z`、metric Balanced Accuracy、日次上限5、top 0.747同率（Le Viet/Hod Carriers）は変化なし。
- 00:16 JSTにDiscussion 756294の新コメントを確認。Anto Pil（自己申告Public 0.666）はMistral/OLMo LoRA作者にOOF CSV交換を提案し、自らはQwen3-14B/8B・Llama-8B LoRAとSVMのstackだと投稿。これはmerge誘いに伴う投稿者申告で、CV/OOFや相補性の独立確認ではない。連絡、OOF/データ交換、team mergeは行わず、candidate03は登録済み独立Mistral再現として扱う。
- 既存CPU bestの保存済みOOF BA `0.3845041`からclass recallを読み直し、弱い順に`claude-fable-5` .161、`gpt-5.6-sol` .180、`glm-5.3` .187、`glm-5.3-flash` .213、`kimi-k3` .267、`gpt-5.6-terra` .287、`claude-opus-4-8` .300、`gpt-5.5` .307を確認。public Discussionの混同ペア投稿とは一部一致するが、採用根拠にはせず候補02/04のOOF誤りと照合してから次仮説を選ぶ。
- 同保存OOFの混同行列では、Gemini 3.7/3.8相互誤り（40/43件）、Gemini 3.6→3.7（30件）、GPT-5.6-sol→luna/terra（31/28件）、GLM-5.3↔flash（33/32件）が大きい。これは現行CPU線形分類器のOOF事実で、改良策は候補02/04比較後に選ぶ。
- 仕様監査でGPU解析runnerが文章長別指標を出力していないと判明（学習OOFにはword_countなし、confirmation baselineにもなし）。学習中の`gpu_experiment.py`は変更せず、`gpu_analyze.py`のみofficial `train.csv`からIDでword_countを結合し、全候補共通のtrain-word-count quartile別BA/accuracyとbin×class recall CSVを出すよう修正。新hash `5d10ab53c7f67c7207416e8b0daf5e1a799ce4fd3dae2fc5a6ee2585bfa261b2`。既存runnerコードを読んでレビューしたが、テスト/再実行はしていない。候補OOF完成後の解析に適用する。
- 00:22 JSTに公式Overview timelineをWeb再確認。ページはFinal Submission Deadlineを2027-01-13 23:59 UTCと表示する一方、競技metadata APIは2027-01-14 23:59:00.817Zを返す不一致が継続。approved specに従い、確定できない場合の計画基準は早い方（2027-01-13）とする。[公式Timeline](https://www.kaggle.com/competitions/name-that-llm/overview/timeline)。

### 公開手法候補の追加確認（2026-11-06 23:47 JST）

- Discussion 756477とlinked Notebook `pinheirodw17/reverse-leakage-why-random-cv-is-pessimistic` version 2を確認。Notebook metadataの最終実行は2026-11-03で、外部data/model不使用のTF-IDF診断を含む。prompt-grouped validationを推奨する議論は現spec/候補02の分割と一致する。
- 作者はLLM embedding特徴のprompt-mean centering、test側では文章類似度による未知prompt group推定、test統計による正規化をPublic LB v8/v9で使ったと自己報告し、v9はgrouped-CV 0.504/Public LB 0.502と掲載。ただしNotebook sourceには該当推論実装がなく、これらの値も同Notebook内の作者記載で独立再現なし。現候補を変える根拠にはせず、次の候補選定時の調査項目に留める。

### candidate02/04 primary OOF稼働監視（2026-11-07 00:24 JST）

- ユーザー指定の`.agents/skills/kaggle-workflow/scripts/codex_rate_limit.py --guard 15`を実行: 5時間枠74%、週間枠79%、status=ok。
- candidate02: wrapper/Python PID `2827673/2827674`生存（elapsed 2:02:07）。GPU1 UUID `GPU-8a059266-7ede-0427-ff30-08ba7a9b5224`上でPython 15,648 MiB、GPU free 16,272 MiB、28% util。candidate04とはGPU UUIDが分離。
- candidate04: launcher/flock/Python PID `2889691/2889692/2889693`生存（elapsed 22:21）。GPU0 UUID `GPU-135ac6e4-8006-058e-ae74-0bb708d0f143`上でPython 3,884 MiB、GPU free 12,068 MiB、36% util。
- host MemAvailable `211,838,524 kB`（約202.0 GiB）。両runner/config SHA-256は登録値と一致（candidate02 `23f620d...`、candidate04 `3663fac...`、runner `3bd614d...`）。
- candidate02のlog更新時刻は22:23 JST、candidate04は00:02 JST。両ログ末尾はfold0のLoRA layer selectionで、epoch境界ログ、checkpoint、OOFはまだなし。processとGPU compute PIDは一致して生存・計算中。既存の45,000例stage1とepoch境界ログ方式を踏まえ、停止・再起動せず同じrunを継続し、次回GPU監視は10分以上空ける。

### 公式競技情報の再確認（2026-11-07 00:27 JST）

- Kaggle公式APIで競技metadata・Rules・公開Leaderboardを再取得。metadata deadlineは`2027-01-14T23:59:00.817Z`、metricはBalanced Accuracy、Notebook-only、日次上限5件。Rulesは最終提出選択2件、競技データを非参加者へ送らない要件（2.4.b）、外部データの公開・同等アクセスまたはReasonableness要件（2.6）を維持。
- 公開Leaderboard先頭はLe VietとHod Carriersが0.747で同率。直近に更新された新しい上位値は確認されず、現行候補の採否基準は変わらない。
- Discussion 756466のコメントを再取得したが、主催者回答なし。Competition topicsにも新しい公式告知は見当たらない。競技テキストを第三者APIへ送るデータ作成や、出所・規約適合性を検証できない外部annotationは引き続き使わない。
- 公式Overview Timelineページは今回の取得でも本文を返さず、直近に確認した同ページとmetadata APIの締切不一致（Overview表示2027-01-13 23:59 UTC、metadata API表示2027-01-14 23:59 UTC）は未解消として扱う。計画上は早い方の2027-01-13を基準にする。

### 公開アンサンブルablation報告の確認（2026-11-07 00:28 JST）

- Discussion「[Same ablations on two bases: what each part is worth on the public LB (0.638 vs 0.659)](https://www.kaggle.com/competitions/name-that-llm/discussion/756088)」を確認。投稿者は2つの公開submission baseでQwen3-14B、centered twins、SVC、ATLAS等を除去したPublic LB差を報告し、同じ要素でもbaseごとに寄与が異なると述べている。投稿値でありOOF評価・独立再現ではない。現候補へ重みや後処理値を流用せず、候補02/04の同一分割OOFとnested CVの結果から組合せを決める。

### candidate03事前登録物の再確認（2026-11-07 00:29 JST）

- 外部実験ディレクトリを読み取り確認。candidate03 config SHA-256は事前登録値`c04ff481...`と一致し、固定HF revisionのsafetensors 2 shard（9.3 GiB、4.3 GiB）が存在する。重みの完全hash照合は23:31 JSTの記録済み確認を参照。GPU実行・pilotは未開始のまま。
- 外部実験ディレクトリには`.git`がなく`git status`で全体の変更状態は取得できない。このためrunner/config等の対象ファイルhashと各runの記録を個別に照合し、今回も実験コード・設定・重みは変更していない。

### 単体モデル性能の新着投稿を確認（2026-11-07 00:31 JST）

- Discussion「[What score your best single model can achieve?](https://www.kaggle.com/competitions/name-that-llm/discussion/754860)」の最新コメントを確認。投稿者報告では、Open Pool v10を使ったQwen3-8B LoRAがPublic LB 0.628、5-fold grouped OOF 0.6224（fold別0.589–0.654）。別投稿はModernBERTをOpen Poolでpretrain後、trainで5-fold LoRAしたCV 0.616/Public LB 0.575を報告。いずれも独立再現値ではないが、現在進行中candidate02のモデル規模とpool pretrainingを比較する参考になる。v10結果・adapterは今回のOOFへ混ぜず、v15の候補を同じ条件で評価する。
- Qwen3-14BでPublic LB約0.670との投稿者申告もあるが、返信で「独自データ」を使ったと明記し、その出典・同等アクセス性を検証できないため候補として採用しない。Leaderboard先頭0.747との差を詰める根拠は、適格データを使う自前OOFと、公開LBだけに依存しない評価から得る。
- Discussion「[Heads-up: submissions failing with Notebook Threw Exception after several hours](https://www.kaggle.com/competitions/name-that-llm/discussion/751754)」には、3–4時間のscoring後に複数submissionが失敗したとの投稿と、同様の問題との返信がある。主催者回答・原因特定はないため、提出失敗の一般則とは扱わず、将来のKaggle実行ではNotebook sessionの状態・出力artifactを個別に確認する。

### candidate02/04とCPU SVC primary OOF稼働監視（2026-11-07 00:49 JST）

- guard: 5時間枠72%、週間79%、status=ok。
- candidate02: wrapper/Python PID `2827673/2827674`生存（elapsed 2:26:40）。GPU1 UUID `GPU-8a059266-7ede-0427-ff30-08ba7a9b5224`上でPython 15,648 MiB、GPU free 16,272 MiB、25% util。
- candidate04: launcher/flock/Python PID `2889691/2889692/2889693`生存（elapsed 46:54）。GPU0 UUID `GPU-135ac6e4-8006-058e-ae74-0bb708d0f143`上でPython 3,884 MiB、GPU free 12,068 MiB、28% util。GPU compute PIDは各自のrunnerと一致し、新CPU候補はGPUを使用していない。
- CPU SVC: supervisor PID `2913154`・fold0 worker PID `2913335`生存（elapsed約2分25秒）。fold0 child tree RSS `4,062,924,800 bytes`（約3.78 GiB）、CPU約100%、GPU非使用。OOF foldファイル未完成で結果はまだなし。
- host MemAvailable `207,634,040 kB`（約198 GiB）。CPU候補開始前の約201.7 GiBから大きく崩れておらず、32 GiB RSS/16 GiB MemAvailable guard内。3候補を分離したまま継続し、CPU fold完了前に再起動しない。

### Open Pool v15 SVC primary fold0完了（2026-11-07 00:51 JST）

- candidate CPU SVCのfold0 artifact（540 validation行、30 prompt group、45,000 pool行、18 class各2,500行）と完了manifestを確認。近似prompt group 2件をpoolから除外し、uniform capとweightを維持。fold0 BA `0.431481`。
- 同じprimary fold0の既存CPU best OOF BAは`0.359259`。対応する540行で観測差は`+0.072222`。これは1/5 foldの記述値にすぎず、全OOF・paired prompt bootstrap前の採否や改善主張には使わない。fold1 workerへ進行中。
- cgroup v2でこのsessionの`memory.max=max`、`cpu.max=max 100000`（memory/CPU quotaのhard capなし）を確認。runnerの2秒ごとのchild-tree RSS / host MemAvailable監視（RSS上限32 GiB、MemAvailable下限16 GiB）で続行する。fold1観測時点のchild RSS約1.9 GiB、host available約200 GiB。

### 公式Leaderboard・期限metadata再確認（2026-11-07 00:53 JST）

- Kaggle公式competition metadata/Leaderboardを再取得。Balanced Accuracy、Notebook-only、日次上限5、metadata deadline `2027-01-14T23:59:00.817Z`に変更なし。Overview Timelineとの1日差は未解消のため、計画上は早い方の2027-01-13 23:59 UTCを維持。
- 公開LB先頭はLe Viet / Hod Carriers同率0.747、3位Team Aillis 0.743で変化なし。目標scoreは0.747超のまま。

### Open Pool v15 SVC primary OOFとconfirmation開始（2026-11-07 01:21 JST）

- Primary 5-fold OOFが完了（2,699行・150 prompt group）。Candidate BA `0.4337757892`、fold BA `[0.431481, 0.416667, 0.416667, 0.470370, 0.433844]`。既存best CPU baselineの同一primary split BA `0.3845041014`に対し差は`+0.0492716878`。
- Prompt groupを単位とした対応bootstrap 2,000回（seed 42）の95% CIは`[+0.0277777, +0.0703804]`、平均差`+0.0491756`で、specのprimary採用条件を通過。モデル長別4分位すべてでBAがbaselineを上回ったが、最終確認は独立splitの結果で判断する。
- Runnerの最終aggregateで`KeyError: 'converged'`が発生したが、fold予測・decision score・manifestは5foldすべて保存済み。独立分析runnerでprimary指標を算出。原因はCPU fold metricsに収束状態が欠けるschema不一致。CPU runnerへ`n_iter < configured max_iter`の収束フラグを追記し、更新runner SHA-256は`b3b896134e61ed3efdead97128e254ff2b0e6d34e36175d746a251e7e363e605`。Python構文コンパイル成功。Primary fold outputsの再実行はせず、confirmation側で修正を適用する。
- Confirmation用同一split CPU baseline 5foldを作成済み（fold BA `[0.368519, 0.374074, 0.374074, 0.370626, 0.381481]`）。Candidate confirmationはfold0 `0.427778`、fold1 `0.446296`を完了し、fold2を実行中。各foldでtrain/validation prompt-grouped、pool 45,000行を均等18 class×2,500、pool weight 0.35。CPUのみ・4 threads・RSS/host memory guard付き。
- 01:21 JST host 142監視: candidate02 Qwen3-8BはGPU1上で継続（Python 15,648 MiB、GPU 31% util）、candidate04 Qwen3-1.7BはGPU0上で継続（Python 3,884 MiB、GPU 34% util）。MemAvailable `207,677,204 kB`（約198 GiB）。両GPU process PIDは各runnerと一致。CPU confirmationは別プロセスでGPU非使用。次のGPU監視は10分間隔を守る。

### Open Pool v15 SVC confirmation再現（2026-11-07 01:30 JST）

- Candidate confirmation 5-fold OOF完了（2,699行・150 prompt group）。BA `0.4334029331`、fold BA `[0.427778, 0.446296, 0.427778, 0.463346, 0.401852]`。同じconfirmation folds上の既存CPU baseline BA `0.3737683321`、差`+0.0596346010`。
- Prompt-group paired bootstrap 2,000回（seed 42）のBA差95% CIは`[+0.0385100, +0.0792830]`、平均差`+0.0595166`。Primaryの正の区間`[+0.0277777, +0.0703804]`と合わせ、両分割でspec採用条件を通過。ただし同一trainの再分割は独立holdoutではなく、候補探索による選択biasも残るため汎化保証ではない。
- Confirmationの4つのword-count quartileすべてでcandidate BAがbaselineを上回った（36–64 tokens: .3276 vs .2775; 65–101: .4395 vs .3678; 102–157: .4342 vs .3939; 158–274: .5292 vs .4319）。比較表・class recall・confusion matrixをrun artifactsに保存。
- CPU runnerの収束schema修正後、confirmation runnerは全5fold完了し`oof_complete`を出力。Candidate SVCはCPU特徴量基準を確実に上げたが、公開LB先頭0.747との差は大きく残るため、次に候補02/04のOOFと誤分類相補性を確認し、同一prompt-grouped評価の範囲内で組合せ候補を選ぶ。

### GPU候補02/04稼働確認（2026-11-07 01:42 JST）

- レートガード: 5時間枠69%、週枠78%、status=ok。
- candidate02 Qwen3-8B post-trained: PID `2827674`がGPU1 UUID `GPU-8a059266-7ede-0427-ff30-08ba7a9b5224`で継続、VRAM 15,648 MiB・GPU util 27%。candidate04 Qwen3-1.7B: PID `2889693`がGPU0 UUID `GPU-135ac6e4-8006-058e-ae74-0bb708d0f143`で継続、VRAM 3,884 MiB・GPU util 34%。各PIDは登録runnerと一致し、Python CPU時間も増加。
- MemAvailable `211,738,384 kB`（約202 GiB）。両方ともrun開始後の新しいepoch/fold/checkpointログはまだなく、candidate02 retry1 logの最終eventは22:23 JSTのfold0 LoRA層選択、candidate04 logの最終eventは00:02:58 JSTのfold0 LoRA層選択。現在もCPU/GPU計算中で、checkpoint境界の記録待ち。停止・再起動は行わず、GPU確認は10分以上の間隔で継続する。

### GPU候補02/04の追加稼働確認（2026-11-07 01:52 JST）

- candidate02 elapsed `3:30:11`（CPU time `3:33:27`）、candidate04 elapsed `1:50:25`（CPU time `1:53:04`）。各Python processはLinux state `Sl`で存続し、GPU compute PIDと一致。GPU utilは27%/36%、VRAMは15,648/3,884 MiB。MemAvailable `211,759,244 kB`（約202 GiB）。
- runnerはepoch完了時にcheckpointを保存する仕様。両方のlogは前回と同じfold0層選択で、`latest.json`/epoch checkpoint/OOFはまだ見当たらない。45,000-example stage1 epoch中の可能性が高く、PIDのCPU時間が増えGPU使用も続いているため停止・再起動せず継続する。GPU pollingは次も10分以上空ける。

### 公開18モデル追加応答コーパスの適格性確認（2026-11-07 02:00 JST）

- Kaggle Discussion「[18-model wide response additional corpus](https://www.kaggle.com/competitions/name-that-llm/discussion/749629)」とDataset v1「[Name That LLM: Response Corpus](https://www.kaggle.com/datasets/olegzholobov/name-that-llm-response-corpus)」を確認。所有者記載では135,171 unique responses/18モデルを含み、prompt・source・model evidence・quality metadata付き。dataset全体のKaggle licenseは`other`、READMEはsource licensesが混在しunderlying contentの再ライセンスなしと明記。
- 小さなREADME/source catalog/manifest/validationだけを`/tmp`へ取得して監査。source catalogには明示的にunknown/no output-specific reuse license, provider output terms apply, mixed upstream license等の行があり、全体を一括利用できない。公開スレッドの返信でも外部コーパスを追加するとformatting/length/domain gapでCVが悪化したという投稿者報告がある。CC BY-SAで既に採用条件を通ったOpen Pool v15を、このデータで置換/拡張しない。
- 併せてDiscussion「[Clarification on self-generated data from model APIs](https://www.kaggle.com/competitions/name-that-llm/discussion/749613)」と新しい外部データ確認スレッド`756466`を照合。質問者の追加投稿のみで主催者回答は確認できず、API生成データの規約解釈は未確定。現runのOpen Pool v15への影響なし。取得したprovenance filesは実験データとして取り込まず、`/tmp`監査用に留める。

### GPU候補02/04長時間stage1稼働（2026-11-07 02:03 JST）

- candidate02 elapsed `3:40:40`（CPU time `3:43:56`）、candidate04 elapsed `2:00:53`（CPU time `2:03:33`）。両Python PIDはLinux `Rl`でrunning、GPU utilization 23%/35%、VRAM 15,648/3,884 MiB。MemAvailable `211,697,400 kB`（約202 GiB）。
- どちらもfold0 stage1のepoch完了ログ・checkpoint・OOFなし。runnerは45,000 pool rowsをbatch size 1で処理しepoch完了時にのみ保存するため、長い無出力区間と整合する。CPU/GPU使用が継続しRAMは安定しているので再起動せず、次のGPU確認は10分以上空ける。

### GPU候補02/04長時間stage1継続（2026-11-07 02:13 JST）

- candidate02 elapsed `3:50:55`、CPU time `3:54:11`。candidate04 elapsed `2:11:09`、CPU time `2:13:49`。PIDは引き続き`Rl`、GPU0/1 usage 34%/26%、VRAM 3,884/15,648 MiB。MemAvailable `211,783,940 kB`（約202 GiB）。
- 新checkpoint/OOF/epoch logなし。現在のstage1が45k例なので想定された長時間処理の範囲。両run継続、次のGPU監視も10分以上間隔。

### GPU候補02/04継続（2026-11-07 02:24 JST）

- candidate02 elapsed `4:01:15` / CPU time `4:04:32`、candidate04 elapsed `2:21:29` / CPU time `2:24:09`。GPU utilization 23%/32%、VRAM 15,648/3,884 MiB、MemAvailable `211,796,024 kB`（約202 GiB）。
- 依然fold0 stage1のcheckpoint・OOFなし。両process Linux `Rl`で実行を続け、GPUも使用しているため異常停止ではない。設定変更や再起動は行わず、次回も最低10分後に確認する。

### GPU候補02/04継続（2026-11-07 02:34 JST）

- candidate02 elapsed `4:11:35` / CPU time `4:14:52`、candidate04 elapsed `2:31:49` / CPU time `2:34:29`。GPU util 23%/27%、VRAM 15,648/3,884 MiB。MemAvailable `211,757,524 kB`（約202 GiB）。
- checkpoint/OOFなし。PIDは`Sl`状態を含みつつCPU時間が実時間相当に増加し、GPU compute PIDは登録runと一致。実行中の長いstage1として継続し、停止・再起動しない。

### GPU候補02/04継続（2026-11-07 02:44 JST）

- candidate02 elapsed `4:22:00` / CPU time `4:25:17`、candidate04 elapsed `2:42:14` / CPU time `2:44:54`。GPU util 26%/34%、VRAM 15,648/3,884 MiB。MemAvailable `211,806,004 kB`（約202 GiB）。
- 依然fold0 stage1のcheckpoint/OOFなし。process state `Rl`、GPU compute PIDがrunと一致し、資源上の異常は見えない。runnerのepoch-boundary保存まで継続する。

### 利用枠リセット前のGPU確認（2026-11-07 02:55 JST）

- rate guard 02:51時点: 5時間枠66%、週枠78%、status=ok。5時間枠は02:57 JSTリセット予定。
- candidate02 elapsed `4:32:19` / CPU time `4:35:36`、candidate04 elapsed `2:52:33` / CPU time `2:55:13`。GPU util 28%/25%、VRAM 15,648/3,884 MiB。MemAvailable `211,775,572 kB`（約202 GiB）。
- 新しいcheckpoint/OOFなし。PIDは継続中でGPU使用とRAMは安定。設定変更・再起動なし。リセット後guardを取り直し、GPU確認は次回10分以上空ける。

### 5時間枠リセット後・GPU候補確認（2026-11-07 03:05 JST）

- guard 02:57: 5時間枠100%、週枠78%、status=ok。
- candidate02 elapsed `4:42:42` / CPU time `4:45:59`、candidate04 elapsed `3:02:56` / CPU time `3:05:36`。GPU util 24%/38%、VRAM 15,648/3,884 MiB、MemAvailable `211,764,656 kB`（約202 GiB）。
- どちらもfold0 stage1の新checkpoint/OOFなし。実行PIDは継続して自身のGPUを使用。引き続き変更せず、次の確認を10分以上空ける。

### GPU候補02/04継続（2026-11-07 03:16 JST）

- rate guard 03:15: 5時間枠99%、週枠77%、status=ok。
- candidate02 elapsed `4:53:24` / CPU time `4:56:41`、candidate04 elapsed `3:13:38` / CPU time `3:16:18`。GPU util 27%/26%、VRAM 15,648/3,884 MiB。MemAvailable `213,459,520 kB`（約203 GiB）。
- 両方ともfold0 stage1のcheckpoint/OOFは未作成。PIDとGPU compute processは一致し、RAM安全域。次回も最低10分間隔で確認する。

### GPU候補02/04継続（2026-11-07 03:26 JST）

- guard 03:25: 5時間枠99%、週枠77%、status=ok。
- candidate02 elapsed `5:03:38` / CPU time `5:06:55`、candidate04 elapsed `3:23:52` / CPU time `3:26:33`。GPU util 25%/37%、VRAM 15,648/3,884 MiB、MemAvailable `213,926,616 kB`（約204 GiB）。
- stage1のcheckpoint/OOF未作成。両processは存続しGPU compute PIDが一致。次回も10分以上空けて確認し、設定変更しない。

### GPU候補02/04継続（2026-11-07 03:36 JST）

- rate guard 03:36: 5時間枠98%、週枠77%、status=ok。
- candidate02 elapsed `5:13:54` / CPU time `5:17:11`、candidate04 elapsed `3:34:07` / CPU time `3:36:49`。GPU util 21%/39%, VRAM 15,648/3,884 MiB。MemAvailable `213,853,976 kB`（約204 GiB）。
- checkpoint/OOFはまだなし。各PIDは継続中でGPU compute processとの対応も正常。次の監視は10分以上空ける。

### GPU候補02/04継続（2026-11-07 03:47 JST）

- guard 03:46: 5時間枠98%、週枠77%、status=ok。
- candidate02 elapsed `5:24:11` / CPU time `5:27:29`、candidate04 elapsed `3:44:25` / CPU time `3:47:06`。GPU util 32%/30%、VRAM 15,648/3,884 MiB。MemAvailable `213,886,320 kB`（約204 GiB）。
- まだfold0 stage1 checkpoint/OOFはない。各runのGPU PIDは一致し、process継続中。次回も10分以上間隔を空けて確認する。

### GPU候補02/04継続（2026-11-07 03:57 JST）

- guard 03:56: 5時間枠97%、週枠77%、status=ok。
- candidate02 elapsed `5:34:26` / CPU time `5:37:44`、candidate04 elapsed `3:54:40` / CPU time `3:57:21`。GPU util 31%/37%、VRAM 15,648/3,884 MiB、MemAvailable `213,916,148 kB`（約204 GiB）。
- stage1 checkpoint/OOF未作成。PID存続・GPU process対応は正常。設定変更せず次回も10分以上空けて監視する。

### GPU候補02/04継続（2026-11-07 04:07 JST）

- guard 04:06: 5時間枠97%、週枠77%、status=ok。
- candidate02 elapsed `5:44:42` / CPU time `5:48:01`、candidate04 elapsed `4:04:56` / CPU time `4:07:38`。GPU util 29%/24%、VRAM 15,648/3,884 MiB。MemAvailable `213,895,056 kB`（約204 GiB）。
- 両方ともfold0 stage1 checkpoint/OOFはなし。GPU compute PIDはrunnerと一致し、CPU時間も進行。次回は10分以上空けて再確認。

### GPU候補02/04継続（2026-11-07 04:18 JST）

- guard 04:17: 5時間枠96%、週枠77%、status=ok。
- candidate02 elapsed `5:54:59` / CPU time `5:58:18`、candidate04 elapsed `4:15:13` / CPU time `4:17:55`。GPU util 24%/36%、VRAM 15,648/3,884 MiB。MemAvailable `213,950,380 kB`（約204 GiB）。
- fold0 stage1 checkpoint/OOF未作成。process・GPU対応は継続正常、RAMは余裕。次の監視も10分以上空ける。

### GPU候補02/04継続（2026-11-07 04:28 JST）

- guard 04:27: 5時間枠96%、週枠77%、status=ok。
- candidate02 elapsed `6:05:17` / CPU time `6:08:36`、candidate04 elapsed `4:25:31` / CPU time `4:28:13`。GPU util 25%/35%、VRAM 15,648/3,884 MiB。MemAvailable `213,885,508 kB`（約204 GiB）。
- fold0 stage1 checkpoint/OOFなし。process/GPUの対応とCPU時間は正常に増加。状態を変えずに継続し、次のGPU確認は10分以上空ける。

### GPU候補02/04継続（2026-11-07 04:38 JST）

- guard 04:37: 5時間枠95%、週枠77%、status=ok。
- candidate02 elapsed `6:15:33` / CPU time `6:18:52`、candidate04 elapsed `4:35:47` / CPU time `4:38:30`。GPU util 29%/31%, VRAM 15,648/3,884 MiB。MemAvailable `213,882,292 kB`（約204 GiB）。
- checkpoint/OOFなし。両runner processは生存し、自分のGPU UUIDと対応。次回もGPU監視を10分以上空けて継続。

### GPU候補02/04継続（2026-11-07 04:51 JST）

- rate guard 04:49: 5時間枠94%、週枠77%、status=ok。
- candidate02 elapsed `6:28:27` / CPU time `6:31:46`、candidate04 elapsed `4:48:41` / CPU time `4:51:23`。GPU util 29%/28%、VRAM 15,828/3,907 MiB。MemAvailable 約204 GiB。
- fold0 stage1 checkpoint/OOFは未作成。両runner processとGPU computeは継続し、RAMは安全域。設定変更なし。次回GPU確認は10分以上空ける。

### goal継続時の公式状態・公開Notebook・GPU確認（2026-11-07 04:52 JST）

- rate guard 04:51: 5時間枠94%、週枠77%、status=ok。
- Kaggle公式MCP `get_competition` / `get_competition_leaderboard` / `list_competition_pages` を再取得。leaderboard上位はLe Viet `0.747`、Hod Carriers `0.747`、次点Team Aillis `0.743`。API metadata: deadline `2027-01-14 23:59 UTC`、entry deadline `2027-01-06 23:59 UTC`、日次最大5件、Notebook-only。Rulesは最終提出選択2件、Code RequirementsはCPU/GPU各Notebook 9時間以内・Internet access disabled・`submission.parquet`。Timeline pageはFinal Submission Deadlineを`2027-01-13 23:59 UTC`と表示するため、計画は早い方を採用する。取得範囲は上位10件のみ。公式URL: [leaderboard](https://www.kaggle.com/competitions/name-that-llm/leaderboard), [rules](https://www.kaggle.com/competitions/name-that-llm/rules), [timeline](https://www.kaggle.com/competitions/name-that-llm/overview/timeline)。
- 公式Notebook APIで`ozertuu/0-672-dual-svc-better` version 9のmetadataと選択セルを確認。API metadataは19 dataset sources・8 model sourcesを列挙し、本文は公開Open Pool SVCに加えてLoRA群、外部passage群、ATLAS、stylometry/family gates、Sinkhorn、pairwise residualを使うと説明。0.672はnotebook本文/著者のPublic LB報告であり、API metadataにscoreはなく、自前再現値ではない。Notebook内にはv13 poolの記述がある一方、API更新versionは新しく、実行日時表示にも差があるため、版と入力を固定した再現性は未確認。Notebook URL: https://www.kaggle.com/code/ozertuu/0-672-dual-svc-better。外部passage、adapter等は今回の候補に導入せず、既存specのfoldwise Open Pool v15候補を完了してからOOF上で次の部品を選ぶ。
- host 142 04:52 JST: candidate02 PID `2827674` elapsed `6:29:40` / CPU `6:32:59`、GPU1 util 25%, VRAM 15,828 MiB。candidate04 PID `2889693` elapsed `4:49:53` / CPU `4:52:36`、GPU0 util 25%, VRAM 3,907 MiB。MemAvailable約204 GiB。両processは登録runと一致し、stage1 checkpoint/OOFはまだなし。現行config・CPU成果・他ユーザーのファイルは変更せず継続。

### 階層型SVC候補の事前登録・primary開始（2026-11-07 05:07 JST）

- Official Open Pool v15 flat SVCのconfirmation confusion matrix（18×18、2,699 OOF rows）をprovider familyへ集約。正解1,170、family内誤り770、family間誤り759で、全誤りの50.36%が同じprovider family内。最大の混同はAnthropic↔ZAIとOpenAI↔Qwen、ならびにGemini兄弟モデル間。外部コード/データは追加せず、provider階層を使うcandidateを事前登録。[候補plan](2026-11-07-openpool-hierarchical-svc-candidate.md)
- 外部runner `src/cpu_openpool_hierarchical_svc.py` と専用config `configs/cpu-openpool-hierarchical-svc-v15.json` を追加。runner SHA-256 `f91cb28297bf3b6fe3c978f62ea8ab0b7744747e50d16295e19cb8e04a6ce3b2`、config SHA-256 `cc1888ab8c9cc361807bb4ea455bfde2ee8da0fa7fe7670710e31b0089ba91a2`。Python構文コンパイル成功。family SVC + family内conditional SVCを同一fold feature matrixでfitし、固定softmax温度1.0でlog-probabilityを合成。pool v15 / foldwise prompt filtering / exact text exclusion / 2,500 per class / 0.35 pool weight / 同じ4 views・C=2 / 保存primary GroupKFoldはflat候補と同一。2 CPU threads、RSS 32 GiB上限、MemAvailable 16 GiB下限。
- 05:04 JST 起動直前: 72 logical CPUs、loadavg `2.12/2.17/2.14`、MemAvailable `219,020,210,176 bytes`（約204 GiB）。GPU0 util 36%, VRAM 3,907 MiB、GPU1 util 23%, VRAM 15,828 MiB。両GPUは進行中Qwen runner専用なので新候補はCPU-only。rate guard 05:05: 5h 93%、週77%、status=ok。
- 05:05 JST primary OOF起動。Orchestrator PID `3030615`、fold0 worker PID `3030765`（host 142）。ログ `artifacts/cpu-openpool-hierarchical-svc-v15/primary-run.log`。preflight_pass: 2,699 rows/150 prompts/folds 0–4、pool 45,000 rows/fold、CPU affinity `[0,1]`、`gpu_visible=false`、MemAvailable `203.68 GiB`。data hashesはrun manifest/ログに保存。既存CPU baseline/SVC artifactsとGPU config・プロセスは変更せず。
- 05:04 JST GPU監視: candidate02 PID `2827674` elapsed `6:42:09` / CPU `6:45:29`、GPU1 util 26%, VRAM 15,828 MiB。candidate04 PID `2889693` elapsed `5:02:23` / CPU `5:05:06`、GPU0 util 38%, VRAM 3,907 MiB。MemAvailable約204 GiB。両fold0 stage1 logにcheckpoint/OOFなし、両PIDは存続。次回GPU監視は10分以上空ける。次のCPU候補確認時にRSS/host memoryも監視し、primary採否をpaired prompt bootstrapで確認後にのみconfirmationへ進む。

### 公式Leaderboard・利用枠の差分確認（2026-11-07 05:10 JST）

- 指定guard 05:09: 5時間枠93%、週次76%、status=ok。
- Kaggle公式MCPのcompetition metadata/leaderboardを再取得。topはLe Viet `0.747`とHod Carriers `0.747`で変化なし。Le Vietの最新同点submissionは`2026-11-06 11:58:58 UTC`。3位Team Aillis `0.743`。API deadline metadata `2027-01-14 23:59 UTC`、daily limit 5、Notebook-only、balanced accuracyで変化なし。前確認済みTimeline pageとの差1日は未解決のため、計画は早い`2027-01-13 23:59 UTC`を維持。

### 公開Notebook新着結果の出所監査（2026-11-07 05:12 JST）

- 公式Notebook検索の実行順先頭10件を確認。`areebbb/0-670-this-actually-works` version 3は表題/本文でPublic LB 0.670・公開入力と主張し、従来0.672/0.673 forkの一部が非公開dataset不在時に別fallback pathを取るという主張を掲載。しかしNotebook metadataは20 dataset sources（Open Pool以外にAPI-generated passages、community adapters/fitted states等）・8 model sourcesを列挙し、metadata `last_run_time`は2026-11-03で検索結果のrun時刻と不一致。本文の一部とmetadataのみを確認、code全体・各source license/availability・score再現は未監査。0.670は著者のPublic LB claimとして扱い、同Notebookやその依存物をcandidateへ流用しない。URL: https://www.kaggle.com/code/areebbb/0-670-this-actually-works
- `lightningv08/0-666-qwen3-8-27b-lora-weighted-ensemble` version 58のtitle/本文はQwen3.8-27B LoRA (119,899 external passages)と複数SVC/adapter/ATLAS/補助stackを組み合わせ、Public LB 0.666と記す。metadataは19 dataset sources・5 model sources、`last_run_time` 2026-11-03で検索結果時刻と不一致。selected notebook sectionsとmetadataのみ確認し、全コード/data provenanceは未監査。著者値であり自前再現ではなく、原データの来歴が今回のspec基準で確認できないため依存しない。URL: https://www.kaggle.com/code/lightningv08/0-666-qwen3-8-27b-lora-weighted-ensemble
- どちらの公開値も現公式top 0.747を超えず、現在のQwen foldwise candidateを差し替える根拠にはしない。次のcandidate selectionは進行中primary/confirmation OOFと、ライセンス/来歴を監査できるデータ・モデルに基づける。

### OOF/GPU候補の継続確認（2026-11-07 05:16 JST）

- Primary hierarchical SVC fold1完了: BA `0.381481`、全family/conditional SVCが収束。Flat SVCの同fold BAは`0.416667`。Fold0/1は両方flat SVCより低いが、残りfoldを含むconcatenated OOF前に打ち切らず、設定を変えずprimary完了まで続行。fold2 worker PID `3033124`、親PID `3030615`。
- Fold2中の監視RSSは約2.54 GiB、MemAvailable約201 GiB。CPU runnerは2 threadsで上限内。
- 05:16 host 142: candidate02 PID `2827674` elapsed `6:53:18` / CPU `6:56:38`、GPU1 util 23%, VRAM 15,828 MiB。candidate04 PID `2889693` elapsed `5:13:32` / CPU `5:16:15`、GPU0 util 38%, VRAM 3,907 MiB。MemAvailable約201 GiB。両runnerとGPU processは存続するが、両logの最終entryはfold0 `lora_layer_selection`のまま。最新fold0 stage1 checkpoint/OOFなし。stage1 epoch境界前であり、予測した時間を超えたことだけでは停止・restartしない。
- 05:12 guardは5時間枠92%、週次76%、status=ok。公式Leaderboardは05:10再確認時点で0.747同点、期限・提出条件の直近確認値に変化なし。

### 階層型SVC途中誤り分解・公式状態更新（2026-11-07 05:19 JST）

- Official Kaggle MCPを再取得: leaderboard topはLe Viet/Hod Carriers `0.747` tie、3位Team Aillis `0.743`、API metadata deadline `2027-01-14 23:59 UTC`・日次上限5・Notebook-only。official TimelineはFinal Submission Deadline `2027-01-13 23:59 UTC`、Rules pageはfinal selections 2件、CPU/GPU各9h、Internet disabled、`submission.parquet`。期限は保守的に早い1/13を採用。URL: [leaderboard](https://www.kaggle.com/competitions/name-that-llm/leaderboard), [rules](https://www.kaggle.com/competitions/name-that-llm/rules), [timeline](https://www.kaggle.com/competitions/name-that-llm/overview/timeline)。
- Hierarchical/flat primary predictionsをfold 0–1のみ読み、全18 class BAとfamily macro-BA、familyが正しい条件下のclass accuracyを比較。Fold0: flat family BA `.585278`, hier `.581389`; conditional exact `.624665` vs `.602899`。Fold1: family BA `.594444` vs `.601111`; conditional exact `.598404` vs `.598837`。差は混在し、階層candidateの2fold全体BAはflatを下回る。途中分析なので採否なし。分解結果は、flat family massを保った兄弟rerankを次の仮説にできる可能性を示すが、nested prompt-grouped評価前に候補採用や事後調整しない。
- Rate guard 05:17: 5h `92%`, weekly `76%`, status=ok。GPU前回監視は05:16、次回は10分間隔を満たした05:26以降。

### Public family-gate source codeの限定精読（2026-11-07 05:21 JST）

- `ozertuu/0-672-dual-svc-better` version 9 Notebook API sourceのcell 14から、`StyleGrams`とfamily-gate箇所のみを確認。`StyleGrams`はchar 3–5, word 1–3, shape char 2–6, function-word 1–3の4 sparse TF-IDF views。Family gateはfamilyごとのLinearSVCで、本文の後段では既存blendのfamily probability massを保ったままfamily内label順位だけをconfidence-awareに混合する設計と説明する。
- 実際の本文ではGPT/Gemini/GLM gateにofficial rows + `EX_T` (sample weight 0.25, balanced=True)、Claude gateには別のAPI-generated passagesを任意使用。GATE_LAMはClaude/generic gate別の投稿者選択値であり、現Notebookのscore再現・OOFでの独立検証はしていない。family massを維持する発想のみ候補とし、投稿者の数値・API data・community fitted weightsは利用しない。
- 現在のhierarchical SVCはfamily probabilityも置換する方式なので、fold0/1でflat比に一貫した改善がない。現runを完了後、必要ならflat family mass preserving + clean foldwise Open Pool family-gateを別candidateとして事前登録し、prompt-grouped nested evaluationを行う。

### 階層型SVC primary途中経過（2026-11-07 05:11 JST）

- Fold 0が完了: validation 540 rows / 30 prompts、45,000 pool rows、全5モデルfamily/conditional SVCが収束、fold BA `0.385185`。同じsplitのflat SVC fold0は`0.431481`だったため途中の劣勢シグナルだが、1/5 foldのみで採否判断はしない。fold0 OOF/decision scores/metrics/manifestを保存。
- Primary parent PID `3030615`継続中、fold1 worker PID `3031859`。監視ログのRSS約1.65–1.81 GiB、MemAvailable約202 GiB。runnerはfoldごとに成果物を保存し、host/RSS上限監視中。実験は設定変更せずprimaryの5foldを完了させる。

### 階層型SVC primary完了・不採用（2026-11-07 05:28 JST）

- 指定rate guard 05:28:41: 5時間枠91%、週枠76%、status=`ok`。公式Kaggle MCPを再確認し、LeaderboardはLe Viet/Hod Carriersが`0.747`同点、Team Aillisが`0.743`。competition metadataはdeadline `2027-01-14 23:59 UTC`、daily submissions 5、Notebook-only、Balanced Accuracy。
- 階層型SVC primary OOFは2,699行・150 prompts・5 folds完了。fold BA: `0.385185`, `0.381481`, `0.383333`, `0.442593`, `0.439272`; overall BA `0.406358` (fold mean `0.406373`, population SD `0.028261`)。全fold収束、runner正常終了。最大観測RSSは約3.45 GiB、MemAvailable約203 GiB。
- flat Open Pool v15 SVC primary OOFとID・正解label・promptを照合し、全行一致を確認。paired prompt bootstrap 2,000回、seed 42で hierarchical − flat BA差は`−0.027448`、95% CI `[−0.039630, −0.015195]`。事前の採用条件（CI下限>0）を満たさないため不採用。確認splitは実行しない。既存flat SVCのprimary/confirmation結果と成果物は保持する。
- 05:26 JSTのGPU監視ではcandidate02 Qwen3-8B post-trained (PID `2827674`, elapsed `7:04:07`) がGPU1を使用（util 26%, VRAM 15,828 MiB）、candidate04 Qwen3-1.7B (PID `2889693`, elapsed `5:24:21`) がGPU0を使用（util 24%, VRAM 3,907 MiB）。両方ともfold0 `lora_layer_selection`中でcheckpoint/OOFなし。CPU時間はelapsedと並行して進み、PID/GPU対応は正常。MemAvailable約203 GiB。停止・再起動・設定変更をしない。次回GPU監視は05:37 JST以降。
- 次候補の仮説は、flat SVCのprovider-family質量を維持し、family内の兄弟label順位だけをclean foldwise Open Pool scoreで補正する方式。別のnested prompt-grouped candidateとして事前登録してから実装可否を判断する。第三者Notebookの重み、API生成データ、外部passageは使用しない。

### 階層型候補の後処理分析準備・GPU継続（2026-11-07 05:37 JST）

- 後続candidateの手順を[spec](../specs/2026-11-07-openpool-family-mass-rerank-spec.md)へ記録。flat SVCのfamily probability massを固定し、family内conditionalのみ補正する。補正率は外側foldごとにinner prompt-grouped OOFで選び、primary→confirmation順にpaired bootstrap採否を判定する。第三者weights/dataは使用しない。
- guard 05:37:38: 5時間枠90%、週76%、status=`ok`。
- host 142 05:37:27 JST: candidate02 PID `2827674`, elapsed `7:14:44` / CPU `7:18:05`, GPU1 util 25%, VRAM 15,828 MiB; candidate04 PID `2889693`, elapsed `5:34:58` / CPU `5:37:42`, GPU0 util 38%, VRAM 3,907 MiB. どちらもPID/GPU対応は継続、ログ末尾はfold0 `lora_layer_selection`。checkpoint/OOFファイルはまだない。MemAvailable約204 GiB。実行中の学習・設定は変更しない。
- 稼働時間が長くなっているがGPU利用とCPU時間の進行は確認できる。fold/epoch境界のcheckpoint前なので、無出力だけを根拠に停止・再起動しない。GPU次回確認は最低10分間隔を空ける。

### family-mass rerank nested primary開始（2026-11-07 05:45 JST）

- 次候補の実装前に指定guard 05:45:10を再実行: 5時間枠90%、週76%、status=`ok`。同時刻のGPU/host preflight: load average `2.06/2.16/2.47`, MemAvailable `214,105,292 kB` (~204 GiB)。candidate02/04両方存続し、GPU1 util 21%, VRAM 15,830 MiB / GPU0 util 36%, VRAM 3,907 MiB。
- 専用runner `src/cpu_openpool_family_mass_rerank.py` とconfig `configs/cpu-openpool-family-mass-rerank-v15.json` を追加。SHA-256 runner `e4b74a28b331d457cf9b8a48f62461fb60d11b9acf1d7a01f42e382b39c52a5b`、config `a40ba0d702975e48e725a99eebeafd6bdd35b3b9f2e48ac4f70e8463450a42d2`。`.venv/bin/python -m py_compile` 成功（suite/testは追加・実行せず）。
- 外側は既存primary GroupKFold 5-fold、各outer-train内のalpha選択はseed42・4-fold prompt-grouped OOF上のBA、alpha grid `{0,.25,.5,.75,1}`、tieは小さいalpha。flat SVCの6-family massを固定し、family別conditional SVCのみを混合。各inner/outer trainで同一Open Pool v15・prompt/exact-text filtering・weights・4 viewsを使う。family mass保存と全出力finiteチェックをrunnerに含めた。
- 05:45 JSTにCPU 2-thread primary開始。Orchestrator PID `3046645`、fold0 worker PID `3046805`。preflight pass: 2,699 rows / 150 prompts / GPU非表示 / MemAvailable `203.84 GiB`;既存primary GroupKFoldとdata hashesをrun manifestへ保存。05:46:29時点でworker RSS約2.48 GiB、tree RSS約2.52 GiB、MemAvailable約201.5 GiB。両GPU runは別GPU UUID上で継続。
- 05:47:43 JST GPU再確認: candidate02 PID `2827674` がfold0 stage1 epoch1を完了し、`epoch-001` checkpointと`latest.json`を05:38 JSTに保存。GPU1 util 31%, VRAM 15,830 MiB。candidate04 PID `2889693` はlora layer selection後のままで初回checkpointなし、GPU0 util 28%, VRAM 3,907 MiB。両PID継続、MemAvailable約200 GiB。CPU rerank fold0 worker PID `3046805`はelapsed `2:06` / CPU `2:07`, RSS約4.19 GiB、tree RSS約4.29 GiB、RSS/host RAM limits内。設定・実行を変更しない。
- CPU rerank最初の試行は05:49 JST、fold0/inner0で停止。`decision_prob`がsparse feature matrixへ`len()`を呼び、scipyが「sparse array length is ambiguous」と例外。学習結果やGPU候補への影響はなく、部分OOF/metricsも作られていない。runnerの該当箇所を`raw.shape[0]`へ修正（新runner SHA-256 `ea92f08c16487e0a2dbb9bd8e33db581038ce03285bd14ec4b476bdfbd73a88b`）、syntax compile成功。失敗run manifest・log・resource historyは変更せず保持。
- 05:51:11 JST rate guard再確認: 5h 89%、週76%、status=`ok`。CPU load average `2.16/2.48/2.55`, MemAvailable `214,097,312 kB` (~204 GiB)。同じconfig/hashでartifactを混在させないため、別の`artifacts/cpu-openpool-family-mass-rerank-v15-retry1`からprimaryを再起動。orchestrator PID `3050424`、fold0 worker PID `3050577`。preflight pass、MemAvailable `203.95 GiB`、2 CPU threads、GPU非表示。両GPU候補を停止・変更せず。
- 05:57:12 JST確認: GPU02 PID `2827674` elapsed `7:34:30` / CPU `7:37:59`, GPU1 util 29%, VRAM 15,830 MiB。fold0 stage1 epoch1 checkpoint (`latest.json=epoch-001`)は維持、後続log/OOFなし。GPU04 PID `2889693` elapsed `5:54:44` / CPU `5:57:28`, GPU0 VRAM 3,907 MiB (util snapshot 0%), 初回checkpointなし、PID/CPU時間は継続。host MemAvailable約201 GiB。
- 修正後CPU rerank PID `3050577` elapsed `5:37` / CPU `5:37`, RSS約2.56 GiB、tree RSS約2.62 GiB、MemAvailable約201 GiB。fold0のnested training継続中、まだfold completion recordなし。資源上限内なので変更せず続行。
- 05:59:05 JST rate guard: 5h 89%、週76%、status=`ok`。同時刻のCPU worker PID `3050577` elapsed/CPU `7:21`, RSS約4.13 GiB、tree RSS約4.23 GiB、host MemAvailable約200 GiB。まだfold0完了前。既存GPU runと同条件を維持。

### goal continuationの公式状態・checkpoint確認（2026-11-07 06:00 JST）

- guard 06:00:24: 5h 89%、週76%、status=`ok`。Kaggle公式MCPでcompetition/Leaderboard/Rules/Timeline/Code Requirementsを再取得。Leaderboard topはLe Viet/Hod Carriers `0.747`同点、Team Aillis `0.743`。metadata deadline `2027-01-14 23:59 UTC`、entry deadline Jan6 UTC、日次上限5、Notebook-only、Balanced Accuracy。RulesはFinal Submissions最大2件。TimelineはFinal Submission Deadline `2027-01-13 23:59 UTC`。Code Requirements: CPU/GPU notebook各9時間以内、Internet disabled、出力`submission.parquet`。保守的期限Jan13を継続。
- 06:00:27 GPU状況: candidate02 PID `2827674` elapsed `7:37:44` / CPU `7:41:14`; fold0 stage2 epoch1 checkpointを05:59 JST (`latest.json=epoch-001`)に保存。GPU1 util 29%, VRAM 15,830 MiB。candidate04 PID `2889693` elapsed `5:57:58` / CPU `6:00:42`; process継続、fold0 checkpoint未作成。GPU0 util 37%, VRAM 3,907 MiB。MemAvailable約202 GiB。
- 修正後nested rerank primary PID `3050424` / fold0 worker `3050577`継続中。worker elapsed `8:51` / CPU `8:52`, RSS約1.85 GiB、MemAvailable約202 GiB。primary OOFは未完成。Kaggleへ提出なし。

### 公開Notebook・追加生成データの出所監査（2026-11-07 06:12 JST）

- Official Notebook検索のscore-descending上位20と`prvsiyan/the-prompt-is-not-the-author`を確認。検索結果の直近実行時刻`2026-11-06T21:03Z`に対し、Notebook metadataの`last_run_time`はNov3で不一致。metadataはcurrent version 24、19 dataset sources・8 model sources、GPU T4、Internet off。本文はversion23の作者自身のPublic LB `0.669`と記し、旧0.672表示のforkは非公開SVC datasetを参照していたと説明する。個々の19 dataset/8 modelのprovenanceとlicenseは全監査していないため、コード・重み・そのLB主張を候補へ流用しない。URL: https://www.kaggle.com/code/prvsiyan/the-prompt-is-not-the-author
- 同Notebookが紹介する`prvsiyan/prvsiyans-extended-name-that-llm-dataset`はKaggle metadata上CC BY 4.0・public。最新descriptionは13,500件/810 prompts/18 labels、`passages_clean.csv` 5,070行、prompt blockで全モデルを揃え、API provenanceを公開、official train passage/promptは含まないと説明。Notebook内コードはvalidation foldの`source_prompt_id`対応行を除く。作者は自身の旧stackで追加データを加えた際Public LBが0.533から0.524–0.529へ下がったと報告。ただし構成・重みが異なるため、現Open Pool SVCでの効果を示すものではない。Dataset URL: https://www.kaggle.com/datasets/prvsiyan/prvsiyans-extended-name-that-llm-dataset
- version 8 descriptionのsplit表ではclean rowsは`new` 4,158、`proxy_v1` 516、`new2` 144、`train_regen` 252。`new2`はcommunity-reconstructed train promptsのregisterに似せた別prompt群（作者のstyle-only audit AUC 0.76）、`train_regen`は150のreconstructed competition train prompts verbatimを使い`source_prompt_id`がcompetition `prompt_id`を示す。将来評価する場合はdataset versionを固定し、split別に監査し、必ずheld promptの`source_prompt_id`行を除外する。`new2`も現候補へ混ぜず別実験で評価する。
- 公開Discussion `756466`はcompetition textを第三者LLMへ送ったannotation dataset等に関する参加者の質問で、今回取得したtopicに主催者回答は見当たらない。これは公式解釈ではない。上記dataset説明は独自prompt由来と主張するため前者とは別だが、使う場合も固定version/CC BY 4.0/プロンプト由来を再監査し、`source_prompt_id`によるfold除外、厳密prompt-grouped評価を要す。追加データは現nested candidateへ混ぜず、結果後の独立candidateに限定。
- Discussion `756477`は同一TF-IDF/LRでrandom KFold BA `.109`, StratifiedKFold `.114`, prompt-grouped BA `.347`とする作者報告を掲載し、topic sibling confoundingを説明。自前の実測ではないが、現行のGroupKFold維持を支持する参考情報。URL: https://www.kaggle.com/competitions/name-that-llm/discussion/756477
- 06:12:37 JST guard: 5h 88%、週76%、status=`ok`。06:12:39 GPU監視: candidate02 PID `2827674` elapsed `7:49:57` / CPU `7:53:27`, GPU1 util 33%, VRAM 15,830 MiB; fold0 stage1/stage2各epoch1 checkpointを保持、以後のログ/OOFなし。candidate04 PID `2889693` elapsed `6:10:11` / CPU `6:12:55`, GPU0 util 33%, VRAM 3,907 MiB, checkpoint未作成。MemAvailable約200 GiB。CPU rerank PID `3050577` elapsed/CPU `21:04`, RSS約3.45 GiB, tree RSS約3.54 GiB, MemAvailable約200 GiB。primary fold0継続、設定変更なし。

### OOF漏洩リスクの追加監査（2026-11-07 06:16 JST）

- Kaggle Notebook `weywuy/leak-audit-is-your-holdout-really-held-out` version 3を精読。metadata `last_run_time`はNov3で、本文はcommunity pretrained LoRAがvalidationを含むfull trainで学習済みなら、grouped OOFも0.913/0.9204などに過大評価されると作者主張。これは公開Notebook作者の説明・実験報告で主催者保証ではないが、OOF provenanceの独立監査を強める有用な警告。Notebook URL: https://www.kaggle.com/code/weywuy/leak-audit-is-your-holdout-really-held
- 本候補のQwenベースは固定revisionの汎用Qwen weightで、コミュニティfine-tuned adapterを読み込まず、各outer fold内でLoRAを新規fitする。Open Pool側もvalidation prompt overlap/exact official textを各foldで除外する設計。OOFはその手順/manifest/hash/IDを確認してから採否判定する。public 0.747は実Leaderboard値として扱う一方、上記Notebookの原因説明・LB noise計算は作者主張で別に記録する。
- 修正版nested primary outer fold0が06:15 JST頃に完了。BA `0.416667`, `alpha=0.75`。inner OOF BAはalpha 0:`0.433870`, .25:`0.438967`, .50:`0.439893`, .75:`0.439904`, 1:`0.438060`。同fold flat SVCは`0.431481`のため候補は低いが、1/5 foldなので採否未確定。全モデル収束。worker `3050577`はfold1 worker PID `3058795`に正常遷移。fold1 resource monitor RSS約4.30 GiB、MemAvailable約200 GiB。
- 06:16:31 JST rate guard: 5h `87%`, weekly `76%`, status=`ok`。
- Test-time row/group constraintの監査: Topic `755733`への参加者replyがOverviewの文言として「modelごとのtest件数は均等でなく、Public/Private LBのmixも異なる」と引用し、公式Evaluation pageも同じ事実を明記。従って各promptを必ず18モデル1件ずつとみなすHungarian/permutation制約は使わない。将来prompt clusteringを試す場合は、群サイズやclass countsを固定せず、held prompt OOF上で群推定を評価する。Discussion topic: https://www.kaggle.com/competitions/name-that-llm/discussion/755733
- `pinheirodw17/reverse-leakage-why-random-cv-is-pessimistic` version 2のコードは近傍train passageがsame-prompt siblingかを直接測り、random KFoldのpessimistic behaviorを説明。作者報告であり、現候補へ新たな数値は転記しない。OOFはGroupKFoldを維持する。URL: https://www.kaggle.com/code/pinheirodw17/reverse-leakage-why-random-cv-is-pessimistic
- 同Notebookの後半は、test rowの類似性からprompt群を推定し、embeddingから群平均を引くtest-time prompt-centeringを作者のv8で試したと説明（CV値はsimulation approximation）。group membershipはhiddenで、公式testは1 promptあたり18件固定でもclass count均等でもない。現候補完了後に試すなら、outer validation textだけから群を推定し、validation `prompt_id`を予測・後処理へ渡さず、train側のみ既知promptでcenteringする別foldwise候補として検討。test label/class count/18-per-prompt制約は利用しない。
- 06:25:49 JST guardは5h `86%`, weekly `75%`, status=`ok`。official Leaderboardを再取得しLe Viet/Hod Carriers `0.747` tie、Team Aillis `0.743`を確認。CPU fold1 PID `3058795` elapsed/CPU `13:01`, RSS約1.81 GiB、tree RSS約1.85 GiB、MemAvailable約202 GiBで継続。GPU PIDs `2827674`/`2889693`も存続（GPU metricsは06:22確認、次の監視間隔まで再照会しない）。
- 06:26:54 JST guard: 5h `86%`, weekly `75%`, status=`ok`。06:26:57ホスト確認でGPU02/04 PIDは継続、MemAvailable約200 GiB。GPU metricsは前回06:22から10分未満のため取得せず。CPU rerank orchestrator `3050424`/fold1 worker `3058795`継続（elapsed/CPU `14:09`, RSS約3.23 GiB、resource log tree RSS約2.88 GiB、MemAvailable約201 GiB）。fold1 output未完成。

### Kaggle GPU precision compatibility audit（2026-11-07 06:28 JST）

- Public Kaggle Notebook metadataの実例はaccelerator `NvidiaTeslaT4`。現GPU02/04 configはbfloat16 weight loading、runnerは`torch.autocast(..., dtype=torch.bfloat16)`を使い、`AutoModel.from_pretrained`へ`device_map`を指定せず単一`device`へ移す。T4はTuring世代で16 GB、NVIDIA資料はTensorRT BF16対応をAmpere以降とし、PyTorch資料もnative BF16はAmpere以降と記載。従って現在のBF16 runnerをT4 Notebookへそのまま載せられるとは扱わない。参照: [NVIDIA TensorRT precision control](https://docs.nvidia.com/deeplearning/tensorrt/10.x.x/inference-library/precision-control.html), [PyTorch BF16 availability](https://docs.pytorch.org/tutorials/intermediate/FSDP_advanced_tutorial.html), [NVIDIA T4 product brief](https://www.nvidia.com/content/dam/en-zz/Solutions/Data-Center/tesla-product-literature/T4%20Product%20Brief.pdf)。
- GPU02はA4000/Blackwell local環境でepoch peak allocated `15,197 MiB`、T4 nominal 16 GBに対し余裕が小さい。GPU04 local A4000 epoch peak `3,619 MiB`。これはT4実行の直接測定ではない。候補は現在のOOF完了まで保全し、採用候補が決まった場合に、FP16 + loss-scaling等のT4互換configで同一prompt-grouped評価またはKaggle private runtime smokeを追加し、精度と9時間制約・VRAMを検証してからNotebook提出へ進む。
- 06:22:26 JST guard: 5h `87%`, weekly `76%`, status=`ok`。GPU check 06:22:29: candidate02 PID `2827674` elapsed `7:59:46` / CPU `8:06:34`, GPU1 util 32%, VRAM 15,834 MiB; fold0 stage2 latest checkpoint advanced to epoch 2. candidate04 PID `2889693` elapsed `6:20:00` / CPU `6:22:53`, GPU0 util 41%, VRAM 3,907 MiB; fold0 stage1 epoch1 checkpoint saved at 06:16 JST, peak allocated 3,619 MiB. Both PIDs live. MemAvailable約200 GiB。
- CPU rerank fold1 PID `3058795` elapsed/CPU `9:40`, RSS約2.75 GiB、tree RSS約2.79 GiB、MemAvailable約201 GiB、継続中。Fold0 artifact remains BA `.416667`, alpha `.75`, converged true。設定・GPU allocationを変更しない。

- 06:30:46 JSTに指定の`codex_rate_limit.py --guard 15`を再実行: 5時間枠`86%`、週枠`75%`、status=`ok`。
- 06:32 JST以降のGPU確認でcandidate02 PID `2827674`はGPU1 (RTX PRO 4500 Blackwell) 上で継続、VRAM `15,834 MiB`, util `28%`。fold0 OOFが完了しBA `.544444`、fold1の学習を開始。candidate04 PID `2889693`はGPU0 (RTX A4000) 上で継続、VRAM `3,907 MiB`, util `37%`。fold0 stage2 epoch1 checkpointを06:32 JST頃に保存し、stage2 epoch2以降は未完了。両候補ともprimary 5-foldの一部のみで、採否は未確定。
- CPU family-mass rerank orchestrator `3050424`とfold1 worker `3058795`も継続。worker elapsed/CPU約`19:37`、tree RSS `4.23 GB`、MemAvailable `212,481,814,528 bytes`（約`198 GiB`）。fold1 metricはまだ出力されていない。既存run設定・checkpointは変更せず、Kaggle提出なし。次は同じ資源条件で完了event/OOFを待ち、5-fold全体が揃うまで候補を採択しない。
- 06:35 JSTにCPU候補のfold1完了を確認: BA `.405556`, `alpha=0.50`, 全inner/outer SVC収束。fold0 `.416667`, alpha `.75`に続く2/5 foldだが、採否はprimary全体のprompt-paired CI後に判断する。orchestrator PID `3050424`は継続しfold2へ移行。直近resource snapshotはtree RSS `2,255,429,632 bytes`、MemAvailable `214,134,321,152 bytes`（約`199 GiB`）。
- 06:35:55 JSTのguardもpass（5h `86%`, weekly `75%`）。公式Leaderboard上位10件を再取得し、先頭Le Viet/Hod Carriersが引き続き`0.747` tie、3位Team Aillis `0.743`。新規Kaggle提出なし。
- 06:37 JSTの軽量監視ではGPU02/04とCPU orchestrator PID `3050424`が継続。GPU候補の新checkpoint/eventは前回確認以降なし（fold2 CPU候補は出力待ちで、停止とは判定しない）。CPU resource monitorはfold2、tree RSS `4,260,847,616 bytes`、MemAvailable `212,243,963,904 bytes`（約`198 GiB`）。GPU telemetryは前回06:32から10分未満のため未取得。
- 同一primary foldの保存済みflat SVC metricsとの直接比較（06:38 JST）: fold0 family-mass `.416667` vs flat `.431481` (差`-.014815`)、fold1 `.405556` vs `.416667` (差`-.011111`)。両方alpha選択・convergence記録と一致。2/5 foldsで候補は両方低いが、specどおりprimary全fold OOFとprompt-paired CIが揃うまで判断を確定しない。
- 06:38 JSTに公式Competition metadata/pagesを再取得。Leaderboard topは直前確認から変わらず`.747`; metadataはdeadline `2027-01-14 23:59 UTC`だがTimeline pageは`2027-01-13 23:59 UTC`と記載するため早い方を計画上の締切として維持。ルールは日次最大5提出・final selection最大2件、Notebook提出のみ、CPU/GPU各9時間以内、Internet off、出力`submission.parquet`。Evaluationは18クラス均等test件数ではないと明記。
- 06:42:46 JST guard: 5時間/週とも`100%`（直前window reset後）、status=`ok`。GPU2件のPID/UUID対応と負荷を再確認: candidate02 PID `2827674`はBlackwell GPU1 util `32%`, VRAM `15,834 MiB`; candidate04 PID `2889693`はA4000 GPU0 util `39%`, VRAM `3,907 MiB`。両方のprocess live、GPU compute processも一致。epoch/checkpoint eventは06:32以降未更新だがGPU utilあり、異常とは判定しない。CPU orchestrator PID `3050424`継続、primary fold2 resource snapshot tree RSS `3,223,998,464 bytes`, MemAvailable `212,961,099,776 bytes`（約`198 GiB`）。
- 06:50:13 JST candidate04 fold0完了を確認: BA `.518519`, stage2 epoch2, peak allocated `3,619 MiB`; fold1のdata setupへ移行。candidate02 fold0 BA `.544444`のあとfold1で処理中。各候補1/5 foldのため採否未確定。06:49 JST公式Leaderboard topは引き続き`.747` tie。06:50:38 JST guardは5h `98%`, weekly `100%`, status=`ok`。CPU rerank fold2継続、tree RSS `4,293,836,800 bytes`, MemAvailable `210,477,207,552 bytes`（約`196 GiB`）。
- 06:52:25 JST monitoring: guard 06:52:35時点で5h `97%`, weekly `100%`, status=`ok`。candidate02 PID `2827674` GPU1 util `25%`, VRAM `15,834 MiB`でfold1 lora-layer selection継続。candidate04 PID `2889693` GPU0 util `36%`, VRAM `3,907 MiB`でfold1 lora-layer selection開始後の実行中。compute PID/GPU UUID対応は正常。新checkpointは前回からなし。CPU orchestrator PID `3050424`もalive、fold2 tree RSS `2,261,245,952 bytes`, MemAvailable `212,936,630,272 bytes`（約`198 GiB`）。
- 06:57:33 JST family-mass primary fold2完了: BA `.422222`, alpha `.75`, converged. 同じfoldのflat SVC BA `.416667`で差`+.005556`。fold0/1はそれぞれ`-.014815`/`-.011111`だったため、3/5 foldsではmixedかつpaired primary CI未算出、候補採否は保留。orchestrator `3050424`はfold3へ移行、最新tree RSS `2,696,269,824 bytes`, MemAvailable `212,610,560,000 bytes`（約`198 GiB`）。06:57:50 JST guardは5h `97%`, weekly `100%`, status=`ok`。Leaderboard topは`.747` tieのまま。
- 07:02:30 JST check: guard `97%`/`99%`, status=`ok`。candidate02 PID `2827674`はGPU1 util `29%`, VRAM `15,834 MiB`でalive、最新eventはfold1 `lora_layer_selection`。candidate04 PID `2889693`はGPU0 util `40%`, VRAM `3,907 MiB`でalive、fold1 `lora_layer_selection`。新checkpoint/eventなし、ただし両GPU compute processとPID対応があり負荷継続。CPU orchestrator `3050424`はfold3継続、tree RSS `4,286,033,920 bytes`, MemAvailable `211,015,262,208 bytes`（約`197 GiB`）。
- 07:03 JST same-fold comparison: GPU02 fold0 `.544444` / GPU04 fold0 `.518519` vs adopted flat SVC fold0 `.431481`, respective deltas `+.112963` / `+.087037`. これらは同じprimary fold0のOOFで、強い単fold signalだが5-foldの一般化・採否を示すものではない。両GPU候補は引き続きprimary foldsを完了させる。
- 07:07:52 JST current-state refresh: official leaderboard top unchanged at`.747` tie. GPU/CPU PIDs `2827674`/`2889693`/`3050424` are still live. Family-mass outer fold3 resource snapshot tree RSS `4,181,127,168 bytes`, MemAvailable `210,923,675,648 bytes` (~`196 GiB`). No Kaggle submission.
- 07:12:21 JST check: guard 5h `96%` / weekly `99%`, status=`ok`. candidate02 PID `2827674` remained on GPU1 (Blackwell), util `28%`, VRAM `15,835 MiB`; candidate04 PID `2889693` remained on GPU0 (A4000), util `33%`, VRAM `3,907 MiB`; UUID/PID compute mapping matched. Both latest events remain fold1 `lora_layer_selection`; no new checkpoint, but active GPU utilization confirms ongoing execution. CPU orchestrator `3050424` remains in fold3; tree RSS `4,286,889,984 bytes`, MemAvailable `210,594,078,720 bytes` (~`196 GiB`).
- 07:18:56 JST family-mass primary fold3 completed: BA `.475926`, alpha `.75`, converged; same-fold flat SVC `.470370`, delta `+.005556`. Folds0-3 now show deltas `-.014815`, `-.011111`, `+.005556`, `+.005556`; primary is 4/5, CI not yet computed and final decision remains pending. Orchestrator `3050424` moved to fold4; current tree RSS `3,192,217,600 bytes`, MemAvailable `211,710,472,192 bytes` (~`197 GiB`). Guard at 07:19:13 JST `96%` / `99%`, status=`ok`.
- 07:22:49 JST check: guard `96%` / `99%`, status=`ok`. GPU02 PID `2827674` remains active on GPU1 at util `28%`, VRAM `15,835 MiB`; GPU04 PID `2889693` remains active on GPU0 at util `32%`, VRAM `3,907 MiB`; compute PID mapping matches. Latest logged event for both is fold1 `lora_layer_selection`; no new checkpoint. CPU rerank PID `3050424` is in fold4, tree RSS `1,908,789,248 bytes`, MemAvailable `213,028,438,016 bytes` (~`198 GiB`).
- Notebook runtime planning note (inference from local logs, not a Kaggle T4 measurement): GPU02's fold0 stage1 ran about `7h16m`, two stage2 epochs about `40m`; fold04 fold0 stage1 about `6h14m`, two stage2 epochs about `34m`. A final fit on all official rows will train more stage2 rows, then process ~4,000 hidden test rows. With Kaggle's per-notebook 9-hour cap and T4 being slower/different precision, each selected candidate still needs an actual T4-compatible end-to-end runtime/memory check before Notebook submission.
- 07:24 JST official pages refresh: metadata still reports deadline Jan 14 UTC, Timeline still Jan 13 23:59 UTC; use Jan 13. Code Requirements unchanged: Notebook-only, <=9h CPU/GPU, Internet disabled, external public/free pretrained models allowed, output `submission.parquet`. Evaluation remains 18-class balanced accuracy with unequal test class counts and different public/private mixes.
- 07:28:28 JST refresh: official leaderboard top remains`.747` tie; guard `95%`/`99%`, status=`ok`. GPU02/04 and CPU rerank processes are all live. CPU fold4 resource snapshot tree RSS `2,748,428,288 bytes`, MemAvailable `212,240,752,640 bytes` (~`198 GiB`); fold4 metrics not yet written. Latest GPU telemetry was 07:22; next sample remains on the 10-minute cadence.
- 07:32:22 JST telemetry: guard `95%` / `99%`, status=`ok`. candidate02 PID `2827674` on GPU1 util `28%`, VRAM `15,835 MiB`; candidate04 PID `2889693` on GPU0 util `37%`, VRAM `3,907 MiB`; PID/UUID mappings intact. Both latest events remain fold1 `lora_layer_selection` with GPU compute activity; no new checkpoint yet. CPU orchestrator `3050424` still in fold4; tree RSS `2,933,174,272 bytes`, MemAvailable `211,937,382,400 bytes` (~`197 GiB`); fold4 metrics not yet written.
- 07:38:54 JST refresh: official Leaderboard top remains`.747` tie; guard `95%`/`99%`, status=`ok`. All three run PIDs remain alive. CPU fold4 metrics still absent, resource snapshot tree RSS `4,359,962,624 bytes`, MemAvailable `210,724,270,080 bytes` (~`196 GiB`). No Kaggle submission; GPU telemetry remains on the 10-minute cadence.


- 07:40 JST terminal audit confirmed family-mass primary run completed successfully: `primary-status.json`=`success`, `oof_complete` event present, 2,699 unique OOF rows / 150 prompts, all 5 folds and all model fits converged. Family-mass conservation was checked inside every fold by the runner: for each provider family, reranked family sums match the flat SVC mass with `np.allclose(rtol=1e-8, atol=1e-10)`; successful completion indicates all assertions passed.
- 07:42-07:46 JST preregistered primary evaluation: candidate BA `.434153617`, flat SVC `.433775789`, observed delta `+.000377827`; prompt-paired bootstrap 2,000 replicates, seed 42, 95% CI `[-.007777778, +.008533743]`, bootstrap mean delta `+.000335750`. IDs, prompt IDs, fold assignments and true labels aligned one-to-one; 2,699 rows / 150 prompt groups. CI lower bound is not above zero, so under the spec do not run confirmation; reject this candidate and retain flat SVC. Analyzer outputs and checksums are preserved separately under `artifacts/cpu-openpool-family-mass-rerank-v15-retry1/primary-comparison-flat-svc/` (analysis manifest, summary, aligned OOF, class/length reports, confusion matrix). No original OOF/baseline artifacts were overwritten.
- Family-mass rerank fold scores vs same-fold flat SVC: fold0 `.416667` vs `.431481` (`-.014815`), fold1 `.405556` vs `.416667` (`-.011111`), fold2 `.422222` vs `.416667` (`+.005556`), fold3 `.475926` vs `.470370` (`+.005556`), fold4 `.450511` vs `.433844` (`+.016667`). Full OOF improvement is negligible and not statistically established.
- 07:46:17 JST GPU recheck: candidate02 PID `2827674` remains active on GPU1 at util `26%`, VRAM `15,835 MiB`. candidate04 PID `2889693` remains active with `3,907 MiB` on GPU0; one utilization sample was `0%`, but PID/compute-memory mapping persists and CPU time advanced along with elapsed time, consistent with its layer-selection preprocessing. Latest logged event is still fold1 `lora_layer_selection` for both. Family-mass CPU process ended after successful completion. Guard at 07:45:44 JST was `94%` / `99%`, status=`ok`.

### 再開後の公式状態・実行確認（2026-11-07 07:54 JST）

- 指定の`codex_rate_limit.py --guard 15`を開始時に実行しpass（5時間枠93%、週枠99%、status=`ok`）。
- 公式Kaggle MCPを再取得。Leaderboard上位はLe Viet/Hod Carriersが`0.747`で同点、Team Aillisが`0.743`。Competition metadataのdeadlineは2027-01-14 23:59 UTCだが、TimelineページのFinal Submission Deadlineは2027-01-13 23:59 UTCのままのため、保守的に1月13日を採用。Notebook提出のみ、CPU/GPU各9時間、Internet無効、日次5件・最終選択2件。Evaluationはモデル別test件数が不均等でPublic/Private構成も異なると再確認。
- GPU02 PID `2827674`（Qwen3-8B post-trained）は生存、elapsed約9時間32分、fold1処理中。fold0 BA `.544444`、VRAM約15,835 MiB。GPU04 PID `2889693`（Qwen3-1.7B）は生存、elapsed約7時間52分、fold1処理中。fold0 BA `.518519`、VRAM約3,907 MiB。どちらもprimary 5-fold未完了で採否未定。再開時点で停止・再起動・設定変更なし。
- Open Pool v15は212,623行、18 labels、50,204 `prompt_group`。群サイズ・label構成に大きな偏りがあり、最大7,521行でも7 labels、row数18以上かつ10 labels以上の群は154件だけ。したがってOpen Poolの`prompt_group`をhidden test prompt群の代用にしたり、18-per-promptを仮定する案は採らない。公開Notebookのprompt-centeringは作者のCV/実装主張で再現値ではなく、未評価の着想として扱う。
- 既存4-view SVCとCPU成果物は保持。次候補は現在進行中Qwen候補のprimary全fold結果を見てから選び、同じprompt-grouped比較とprompt-paired CIゲートを適用する。新規Kaggle提出なし。
- 08:04:43 JST再確認: guard 5h `93%` / week `99%`, status=`ok`。candidate02 PID `2827674` elapsed `9:42:00` / CPU `9:48:50`, GPU1 util `24%`, VRAM `15,835 MiB`; candidate04 PID `2889693` elapsed `8:02:14` / CPU `8:08:11`, GPU0 util `32%`, VRAM `3,907 MiB`。両者はfold1、最後のeventはそれぞれ06:20/06:50 JST頃の`lora_layer_selection`。新checkpoint/OOFは未記録。MemAvailable `210,166,992 kB`（約`200.4 GiB`）。CPU timeはelapsedとともに進行し、GPU負荷とRAMも安全域。停止・再起動・設定変更・提出なし。
- 08:06 JST continuation audit: official MCP still reports `.747` top tie, January 13 Timeline deadline (metadata January 14), five submissions/day, Notebook-only, nine-hour runtime and unequal hidden class counts. Candidate02/04 PIDs remain live; latest events remain fold1 `lora_layer_selection`, with no new OOF/checkpoint. GPU utilization `23%`/`36%`, VRAM `15,835`/`3,907 MiB`, host MemAvailable `210,170,968 kB`; no resource guard breach or Kaggle submission. Next full GPU telemetry is deferred at least 10 minutes from this check.
- 08:07 JST CPU-only tokenization診断（Open Pool v15から各18 label 500件、合計9,000件、Qwen3-8B fast tokenizer、max length 384）: token長 p10/median/p90=`66/130/256`、mean `145.2`、384へ達した行は`0.03%`。現runnerは`padding="max_length"`・batch size 1なので、サンプル上の有効tokenは固定384枠の`37.8%`。dynamic paddingならpad token数を理論上約`62.2%`減らせる可能性がある（実行時間短縮率ではない）。現在のfoldwise OOFの計算条件を変えないため、実行中jobとrunnerは変更せず、候補採択後のT4/9h互換化または別runnerの検証対象として記録。tokenizer計測時間`0.82s`、GPUは未使用。
- 08:10 JST continuation: 指定guardは5h `92%` / week `99%`, status=`ok`。公式Leader/Timeline/Code Requirements/Evaluation再取得は直前値から変化なし（top `.747`, Timeline Jan 13 UTC, 9h Notebook run, Internet off, max 5/day and 2 final, unequal class counts）。GPU02/04のfold1 PIDはそれぞれelapsed `9:47:21`/`8:07:35`でlive、GPU util `33%`/`26%`、VRAM `15,835`/`3,907 MiB`、MemAvailable `210,223,828 kB`。fold0におけるstage1所要時間はcandidate02約7h15、candidate04約6h14であり、fold1開始後それぞれ約1h50/1h20のため、現在は実測済みの1-fold stage1所要時間より早い区間。最後のevent/OOF/checkpointは未更新だが、両PIDのCPU時間とGPU稼働が進むため停止とは判定せず、そのまま継続。

### Qwen/SVC融合の探索的fold0診断（2026-11-07 08:12 JST）

- candidate02、candidate04、採用Open Pool v15 SVCのprimary fold0 OOFを比較。3件すべて540 rows。ID、true label、prompt_id、fold、class orderは整列一致し、重複・欠損なし。Qwen logitsとSVC `decision-scores.npz`も同じ18 sorted labelsに対応。
- BA: Qwen3-8B `.544444`; Qwen3-1.7B `.518519`; SVC `.431481`。各モデルのrow-wise softmax（temperature=1）を等重み平均した探索値はQwen8B+SVC `.550000`、Qwen1.7B+SVC `.524074`、3者平均`.564815`。3者値は最良単体Qwen比+`.020371`、採用SVC比+`.133333`。
- 補完性: Qwen8BとSVCは184行でともに誤り、Qwen8Bだけの誤り62行、SVCだけの誤り123行（error-set Jaccard `.4986`）。Qwen1.7B/SVCも共通誤り187行、Qwen1.7Bだけ73、SVCだけ120（Jaccard `.4921`）。これは各Qwenの独立寄与可能性を示すが、one-fold exploratory resultであり、generalization/adoption claimには使わない。
- 以上を受け、重み・温度・閾値の追加調整なしの固定等重みsoftmax 3者融合を、[ensemble spec](../specs/2026-11-07-qwen-svc-probability-ensemble-spec.md)として記録。fold0を見て候補を選んだ選択バイアスがあるため、primary 5-foldはscreening、CIが通れば独立confirmationの両方を満たさない限り採用しない。全Qwen base OOFが完了するまでfusionは実行しない。GPU base jobs・CPU基準は不変更、提出なし。
- 08:17:50 JST: candidate02/04 PIDs `2827674`/`2889693` still live; elapsed `9:55:07`/`8:15:21`, CPU `10:01:57`/`8:21:18`, RSS `6.34`/`6.18 GB`. No new fold event or checkpoint since fold1 initialization. MemAvailable `210,126,372 kB`. GPU metrics intentionally not repeated since last telemetry was 08:10 (10-minute cadence); no process restart or configuration edit.
- 08:18 JST guard `91%`/`99%`, status=`ok`; official LB still `.747` tie and official Timeline/Code Requirements unchanged from 08:10 verification. Candidate02/04 remain live on fold1 (elapsed `9:55:53`/`8:16:07`, CPU `10:02:43`/`8:22:04`), no new fold/checkpoint; MemAvailable `210,055,716 kB`. GPU telemetry was last taken 08:10; no repeated query within the 10-minute interval. Fusion spec is staged for the complete primary OOFs; no Kaggle objects or submissions created.
- 08:25:43 JST telemetry (10+ min after previous): candidate02 PID `2827674` elapsed `10:03:00` / CPU `10:09:50`, GPU1 util `24%`, VRAM `15,835 MiB`; candidate04 PID `2889693` elapsed `8:23:14` / CPU `8:29:12`, GPU0 util `36%`, VRAM `3,907 MiB`. Both remain in fold1 before first stage1 checkpoint; MemAvailable `210,151,892 kB`, no safety threshold approached. Rate guard last pass 08:19 (`91%` / `99%`).
- Prepared CPU-only fusion evaluator `/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/src/gpu_probability_ensemble.py`, SHA-256 `7e2caa5bcff16b4c97e705917dd14fe7e68ca0ffabb28631cfff1e6b9eeaa9ee`. It checks canonical primary/confirmation prompt folds, complete aligned OOF IDs/labels/folds/class order and score shapes, creates the fixed softmax mean, runs the existing SVC paired-bootstrap report, and additionally reports paired bootstrap against each Qwen base. `py_compile` passed. It has not been run: current Qwen base OOFs only have fold0; no GPU run or existing artifact was changed. After all five primary folds, command is `.venv/bin/python src/gpu_probability_ensemble.py --split primary --run-dir artifacts/cpu-qwen-svc-probability-ensemble-v1` from the external project root.
- 08:33:56 JST rate guard passed (5h `90%`, weekly `98%`, status=`ok`). Kaggle MCP notebook metadata call failed at the transport layer. Browser fallback reconfirmed official timeline (final submission Jan 13 23:59 UTC), Notebook-only submission, <=9h runtime, Internet disabled, and unequal test class counts; this fallback did not refresh the live leaderboard. No submission was made.
- 08:35 JST resource refresh: candidate02 PID `2827674` elapsed `10:13:14`, CPU `10:20:04`, RSS `6.34 GB`; candidate04 PID `2889693` elapsed `8:33:28`, CPU `8:39:26`, RSS `6.18 GB`. Both PIDs remain alive on fold1, with GPU0/1 utilization `30%`/`28%`, VRAM `3,907`/`15,835 MiB`; host MemAvailable `215,272,247,296 bytes` (~`200.5 GiB`). Their last fold1 events remain `lora_layer_selection` (02: 06:20 JST; 04: 06:50 JST), with no new checkpoints yet. Fold0 OOF and fold0 BA remain preserved (`.544444`/`.518519`). Runtime is still within the previously measured fold0 stage1 duration; no stop, restart, or runner change.
- 08:38:33 JST rate guard passed (`90%` 5h, `98%` weekly). Official MCP refreshed competition metadata/pages and leaderboard: top remains Le Viet/Hod Carriers tied at `.747`; metadata deadline Jan 14 UTC conflicts with Timeline Jan 13 23:59 UTC, so use Jan 13. Limits remain five submissions/day, two final selections, Notebook only, <=9h, Internet off. Evaluation states test class counts are unequal and public/private mixes differ.
- Public Notebook `ozertuu/0-672-dual-svc-better` v9 source and metadata were inspected. The author reports an isolated stylegram SVC OOF increase `.423`→`.435` from adding prompt-centred features inside a broader stack; this is author-reported and not reproduced here. Its text-only grouping uses content-word TF-IDF cosine distance, median normalization, average linkage, threshold `.90`; a separate shared-prompt Gaussian head also uses injective/repetition constraints. The new candidate adapts only prompt-centering and text-only grouping; it deliberately omits one-to-one class assignment and count constraints because the official hidden test is unequal by class. No API-generated/ChatGPT annotation data is used.
- Registered [prompt-centered twin spec](../specs/2026-11-07-openpool-prompt-centered-twin-spec.md). Created new external config and runner `configs/cpu-openpool-prompt-centered-twin-v15.json` / `src/cpu_openpool_prompt_centered_twin.py`, leaving prior code, OOF, and GPU jobs untouched. Uses the existing 4-view SVC and pool settings, fits transformers inside each outer fold, centers training by official `prompt_id` and public-pool `prompt_canon`, and infers held-out groups using only held-out response text. No held-out prompt ID, label, score, test class count, or fixed group size enters predictions. GPU disabled; two CPU threads; 32 GiB RSS cap and 16 GiB MemAvailable floor.
- Initial fold0 run failed on SciPy sparse matrix subtraction (the row mean does not broadcast). Preserved its run manifest, failure log, and runner snapshot at `artifacts/cpu-openpool-prompt-centered-twin-v15/runner-failed-attempt1.py`; fixed the shape explicitly and retried under a distinct `...-retry1/` artifact directory. Primary fold0 completed with BA `.448148` vs the adopted flat SVC's same-fold `.431481` (`+.016667`). Inferred clusters: 45 for 540 rows, 9 singleton; true prompt IDs were retained only for scoring/alignment and are not used for cluster inference. This is one-fold exploratory evidence, not an adoption result.
- At 08:57 JST telemetry, Qwen candidate02 PID `2827674` and candidate04 PID `2889693` remain live in primary fold1; GPU1/0 utilization `27%`/`34%`, VRAM `15,835`/`3,907 MiB`. No new fold/checkpoint events since fold1 layer selection at 06:20/06:50 JST. Prompt-centered retry1 moved to fold1; its fold0 peak tree RSS was `14,116,450,304 bytes` (~`13.2 GiB`), below 32 GiB; fold1 started around `1.6 GB`, MemAvailable about `213 GB`. All jobs remain within safety thresholds, no Kaggle submission made. Latest official LB remains `.747` tie.
- 09:00 JST continuation: prompt-centered retry1 worker remains active in fold1. Resource monitor reports tree RSS `14,162,759,680 bytes` (~`13.2 GiB`), host MemAvailable `201,006,088,192 bytes` (~`187.3 GiB`), both within the 32 GiB/16 GiB limits. The primary fold0 artifact remains complete and intact; parent session is live and waiting for fold1 completion. No new GPU checkpoint/OOF event or Kaggle submission.
- 09:01-09:04 JST official refresh: leaderboard remains `.747` tie; official Rules confirm max five submissions/day and at most two final selections, public/equally accessible external-data requirement, and Code Requirements remain Notebook-only <=9h, Internet disabled. Timeline deadline remains Jan 13, metadata Jan 14; use Jan 13 conservatively. Discussion topic 756466 about third-party annotation/API data still has no organizer response; continue excluding competition-text annotations and paid/API-generated data from this candidate.
- Inspected public Notebook `weywuy/leak-audit-is-your-holdout-really-held-out`. Its author reports a 0.913 grouped-fold score from community adapters that had seen the full official training set, and attributes that score to leakage. This is a self-reported audit, not independently reproduced, but reinforces the existing rule: do not use community full-train checkpoints/OOF as validation evidence. Current Qwen adapters are trained independently within each outer fold and the SVC twin is fit only on outer-train data.
- 09:03 JST process/resource check: prompt-centered retry1 parent PID `3140344` is live; fold1 child PID `3145295` is active, no fold-1 artifact yet. Tree RSS `14,163,525,632 bytes` (~`13.2 GiB`), MemAvailable `200,887,164,928 bytes` (~`187.2 GiB`). GPU02/04 remain live; last GPU telemetry is 08:57 JST, so no premature repeated GPU sample. No submission.
- 09:06:44 JST retry1 completed primary fold1 and advanced to fold2. Fold1 BA `.429630` vs flat `.416667` (`+.012963`); inferred text-only clusters: 39/540, max size 18, mean `16.87`, 3 singleton. Together folds0-1 are `2/5`, both point deltas positive; no CI/adoption decision until all primary folds are complete. Fold2 child PID `3149360` is now live.
- 09:07 JST telemetry: GPU0 A4000 util`26%`, VRAM`3,907 MiB`; GPU1 Blackwell util`31%`, VRAM`15,835 MiB`; host MemAvailable `212,176,044,032 bytes` (~`197.6 GiB`). GPU02 PID `2827674` elapsed`10:44:50`, GPU04 PID `2889693` elapsed`9:05:04`; both remain fold1. Latest event remains `lora_layer_selection` from 06:20/06:50 JST, with no new checkpoint. Prompt-centered fold2 starts around`2.6 GB` tree RSS. All safety thresholds remain met; no Kaggle submission.
- 09:09:26 JST rate guard passed (`87%` 5h, `98%` weekly). Current official metadata still says Jan 14 UTC while Timeline says Jan 13 23:59 UTC; leaderboard remains Le Viet/Hod Carriers`.747` tie. Re-fetched Rules/Code Requirements/Evaluation: max five submissions/day, max two final selections, external data must be public/equally accessible or meet the reasonableness standard, notebook only, <=9h, internet off, balanced accuracy over 18 labels with unequal test class counts.
- 09:15:19 JST prompt-centered retry1 primary fold2 completed: BA`.470370` vs adopted flat SVC same-fold`.416667`, delta`+.053704`; fold0/1/2 deltas are`+.016667`/`+.012963`/`+.053704`. Fold2 inferred 42 text-only clusters over 540 rows, max size 18, mean`16.40`, 7 singleton; fit runtime`494.65s`. This is screening-only (3/5), no adoption conclusion. Parent PID`3140344` advanced to fold3 child`3154277`; at 09:15:45 tree RSS`2,431,176,704 bytes` (~`2.3 GiB`), MemAvailable`212,605,259,776 bytes` (~`198 GiB`). Last GPU telemetry remains 09:07 JST; no repeated sample before 09:17. No submission.
- Audited completed folds0-2 against the adopted flat SVC: all 1,620 IDs unique and one-to-one, and `id`/`prompt_id`/`fold`/true label lists match exactly in every fold. All three 540x18 score arrays are finite with 18 classes; each OOF/score/metrics SHA-256 matches its fold manifest. This validates current artifacts for aggregate comparison but does not establish generalization.
- 09:17 JST telemetry: GPU0 A4000 util`26%`, VRAM`3,907 MiB`; GPU1 Blackwell util`26%`, VRAM`15,835 MiB`; host MemAvailable`200,885,104,640 bytes` (~`187.2 GiB`). GPU02 PID`2827674` elapsed`10:55:14` and GPU04 PID`2889693` elapsed`9:15:28`, both live on fold1; latest event remains fold1 `lora_layer_selection` from 06:20/06:50 JST. Prompt-centered fold3 PID`3154277` elapsed`3:14`, RSS`14,165,291,008 bytes` (~`13.2 GiB`), under the 32 GiB cap; host free memory remains well above the 16 GiB floor. No submission.
- 09:23:31 JST prompt-centered retry1 fold3 completed: BA`.509259` vs flat SVC`.470370`, delta`+.038889`, runtime`500.83s`. Four folds now show deltas`.016667`,`.012963`,`.053704`,`.038889`; all point in the same direction, still no adoption decision until fold4 and prompt-level CI. Fold4 child PID`3159045` launched.
- 09:24 JST candidate fold4 elapsed`00:53`, RSS`2,096,112,512 bytes`, host MemAvailable`212,942,921,728 bytes` (~`198.3 GiB`). GPU02/04 remain live in fold1 at elapsed`11:01:21`/`09:21:35`; next GPU telemetry is due after 09:27 (last was 09:17). No Kaggle submission.
- 09:27 JST telemetry: GPU0 A4000 util`26%`, VRAM`3,907 MiB`; GPU1 Blackwell util`29%`, VRAM`15,835 MiB`; host MemAvailable`200,835,014,656 bytes` (~`187.1 GiB`). Qwen02/04 PIDs are live at elapsed`11:04:35`/`09:24:49`; latest events remain fold1 `lora_layer_selection` at 06:20/06:50 JST, with active GPU utilization. Prompt-centered fold4 PID`3159045` elapsed`4:07`, RSS`14,203,019,264 bytes` (~`13.2 GiB`); resource monitor stays below 32 GiB and above 16 GiB MemAvailable floor. No new OOF/checkpoint or submission.
- 09:31 JST prompt-centered retry1 primary fold4 completed (539 rows, BA`.472478`). The five completed folds cover all 2,699 training rows. The first parent aggregation stopped because its fold metrics lacked the `converged` field expected by `analyse_oof`; this was an aggregation/reporting failure after fold outputs had been saved, not a fold-training failure. The independent analyzer then produced the preregistered comparison against adopted flat SVC OOF: candidate BA`.465993`, baseline`.433776`, delta`+.032217`; prompt-level paired bootstrap (150 groups, 2,000 reps, seed 42) 95% CI`[+.017037,+.047413]`, adoption gate passed. Existing retry1 artifacts remain unchanged.
- 09:34 JST Codex rate guard passed (5h`84%`, weekly`98%`). Added `n_iter` and explicit `ConvergenceWarning` capture to the runner's per-fold metrics so the normal aggregate includes convergence state. Started independent, preregistered confirmation in a new `artifacts/cpu-openpool-prompt-centered-twin-v15-retry2/` directory, with the same config and confirmation GroupKFold, 2 CPU threads, 32 GiB tree-RSS cap, and 16 GiB host-memory floor. Ongoing Qwen02/04 jobs were left untouched. No Kaggle submission.
- 09:45 JST prompt-centered retry2 confirmation fold0 completed (540 rows): BA`.459259`, `n_iter=39`, `converged=true`. Text-only groups: 58/540, maximum size 18, mean size 15.67, 18 singleton; no validation prompt IDs entered prediction. Fold1 is running. The fold-0 resource peak was about 13.2 GiB tree RSS, below the 32 GiB cap; MemAvailable stayed above 187 GiB. Qwen02/04 remain alive and unchanged; no Kaggle submission.
- 09:52 JST prompt-centered retry2 confirmation fold1 completed (540 rows): BA`.490741`, `n_iter=41`, `converged=true`. Text-only groups: 40/540, maximum size 18, mean size 16.94, 6 singleton; validation prompt IDs were not used for prediction. Confirmation is 2/5 folds; fold2 has started. Resource limits remain satisfied and Qwen02/04 remain untouched. No Kaggle submission.
- 10:01 JST prompt-centered retry2 confirmation fold2 completed (540 rows): BA`.475926`, `n_iter=41`, `converged=true`. Text-only groups: 48/540, maximum size 18, mean size 16.43, 11 singleton; validation prompt IDs were not used for prediction. Confirmation is 3/5 folds; fold3 has started. Resource limits remain satisfied and Qwen02/04 remain untouched. No Kaggle submission.
- 10:10 JST prompt-centered retry2 confirmation fold3 completed (539 rows): BA`.487484`, `n_iter=41`, `converged=true`. Text-only groups: 40/539, maximum size 18, mean size 16.81, 6 singleton; validation prompt IDs were not used for prediction. Confirmation is 4/5 folds; fold4 has started. Resource limits remain satisfied and Qwen02/04 remain untouched. No Kaggle submission.
- 10:19 JST prompt-centered retry2 confirmation fold4 completed (540 rows): BA`.435185`, `n_iter=41`, `converged=true`. All five confirmation folds now have complete, hash-manifested artifacts, and the corrected runner's normal aggregate succeeded (OOF BA`.469714`).
- 10:20 JST independent confirmation comparison against the adopted flat SVC completed: baseline BA`.433403`, delta`+.036311`; prompt-level paired bootstrap (150 groups, 2,000 reps, seed 42) 95% CI`[+.020380,+.053000]`. Together with primary delta`+.032217` and CI`[+.017037,+.047413]`, both preregistered gates pass. Treat prompt-centered SVC as adopted candidate baseline for subsequent comparisons, not as a verified LB improvement. Confirmation metrics record all folds converged (`n_iter` 39/41/41/41/41). The primary runner's prior aggregate issue was repaired; no fold reruns were needed. No Kaggle submission.
- 10:22 JST reviewed the pre-existing Qwen+SVC ensemble evaluator and prepared a separate spec for the same fixed equal-softmax formula using the adopted prompt-centered SVC as its comparator. Added a `--candidate-id` option to preserve distinct artifact provenance and included the prompt-centered runner/config hashes. Qwen02/04 primary still each have only fold0 OOF; their fold1 jobs remain alive. The new fusion will not run until both primary OOFs are complete. Kaggle submission remains none.
- 10:24:30 JST rate guard passed (5h`82%`, weekly`97%`). Refreshed official Kaggle MCP: leaderboard top remains Le Viet/Hod Carriers`.747` tie; Timeline says Jan 13, 2027 23:59 UTC, so retain that conservative deadline. Limits remain five submissions/day and two final selections; Notebook only, CPU/GPU <=9h, Internet disabled. Qwen02/04 PIDs `2827674`/`2889693` remain alive with only fold0 OOF artifacts; fold1 is still training. 10:24:36 GPU telemetry: A4000 util`37%`, VRAM`3,907 MiB`; Blackwell util`32%`, VRAM`15,835 MiB`; MemAvailable`210,099,300 kB` (~`200.4 GiB`). Both within resource headroom. Evaluator CLI change passes `py_compile`; no fusion run or Kaggle submission.
- 10:26 JST Kaggle notebook search surfaced [areebbb/0-670-this-actually-works](https://www.kaggle.com/code/areebbb/0-670-this-actually-works) (current version 3). The author reports Public LB`.670` and describes a public DeBERTa-v3 classifier, prompt-aware Gaussian head, style residual, and pairwise verifier. Notebook info lists 20 dataset sources, 8 kernel sources, and 8 model sources. The search listing and notebook metadata disagree on `last_run_time` (Nov 6 vs Nov 4). This was a metadata/intro review, not a full code, license, or provenance audit; none of its assets or scores are adopted as independently verified. It may inform later targeted candidate selection after the current Qwen OOF comparison.
- 10:33 JST GPU telemetry: candidate02 PID`2827674` and candidate04 PID`2889693` are still alive on fold1. GPU0 A4000 util`35%`, VRAM`3,907 MiB`; GPU1 Blackwell util`23%`, VRAM`15,835 MiB`; MemAvailable`210,144,596 kB` (~`200.4 GiB`). Only fold0 OOF is present for each; there is no new checkpoint event. Both remain under memory limits, active GPU use is visible, and no stop/restart was issued.
- 10:36:33 JST rate guard passed (`81%` 5h, `97%` weekly). At 10:37 JST, started the preregistered low-pool-weight SVC primary with only Open Pool row weight changed from`.35` to`.10`, using a new config and artifact directory. Preflight MemAvailable was`210,166,168 kB`; adopted prompt-centered primary OOF exists for paired comparison. Qwen02/04 jobs remain untouched.
- 10:43 JST resource check: low-weight fold0 PID`3197190` remains active, tree RSS`14,121,562,112 bytes` (~`13.2 GiB`), host MemAvailable`196,211,732 kB` (~`187.1 GiB`). Qwen02/04 remain alive; GPU0 A4000 util`33%`, VRAM`3,907 MiB`, GPU1 Blackwell util`25%`, VRAM`15,835 MiB`. All processes remain within configured memory/GPU headroom; no checkpoint/OOF completion yet.
- 10:45 JST low-pool-weight primary fold0 completed (540 rows): BA`.485185`, `n_iter=36`, `converged=true`; inferred groups 45/540, maximum 18, mean 16.43, 9 singleton. The same fold's adopted prompt-centered SVC BA is`.448148` (exploratory delta`+.037037`). This is one fold only; no adoption decision until all five folds and prompt bootstrap. Fold1 started.
- 10:54 JST low-pool-weight primary fold1 completed (540 rows): BA`.481481`, `n_iter=35`, `converged=true`; inferred groups 39/540, maximum 18, mean 16.87, 3 singleton. Adopted prompt-centered SVC same-fold BA is`.429630` (exploratory delta`+.051852`). Two of five folds show positive deltas, but primary and CI decision remain pending. Fold2 started. Rate guard last passed 10:47 JST (80%/97%).
- 10:55 JST telemetry: low-weight candidate fold2 PID`3204646` active, tree RSS`2,313,416,704 bytes`, MemAvailable`210,076,904 kB` (~`200.4 GiB`). Qwen02/04 remain alive; GPU0 util`22%`, VRAM`3,907 MiB`; GPU1 util`31%`, VRAM`15,835 MiB`. 10:56:39 rate guard pass (`79%` 5h, `97%` weekly). No thresholds approached, stops/restarts, or Kaggle submissions.
- 11:02 JST low-pool-weight primary fold2 completed (540 rows): BA`.503704`, `n_iter=34`, `converged=true`; inferred groups 42/540, maximum 18, mean 16.40, 7 singleton. Same-fold adopted prompt-centered SVC BA`.470370` (exploratory delta`+.033333`). All first three fold deltas are positive, but the five-fold paired bootstrap gate remains pending. Fold3 started. Rate guard passed 11:02:47 (`79%` 5h, `97%` weekly).
- 11:05 JST telemetry: low-weight fold3 PID`3206817` tree RSS`14,159,585,280 bytes` (~`13.2 GiB`); MemAvailable`198,822,236 kB` (~`189.5 GiB`). Qwen02/04 remain alive; GPU0 util`29%`, VRAM`3,907 MiB`; GPU1 util`30%`, VRAM`15,835 MiB`. Resource limits remain satisfied.
- 11:10 JST low-pool-weight primary fold3 completed (540 rows): BA`.529630`, `n_iter=34`, `converged=true`; inferred groups 52/540, maximum 18, mean 16.19, 14 singleton. Same-fold adopted prompt-centered SVC BA`.509259` (exploratory delta`+.020370`). Four of five fold deltas are positive; no overall decision before fold4 and paired bootstrap. Fold4 started. Rate guard passed at 11:08:13 (`78%` 5h, `97%` weekly).
- 11:13:47 JST rate guard passed (`78%` 5h, `97%` weekly). Fold4 remained within the 32 GiB tree-RSS cap and 16 GiB host-memory floor; both Qwen jobs were left untouched.
- 11:18 JST low-pool-weight primary fold4 completed (539 rows): BA`.509579`, `n_iter=35`, `converged=true`; inferred groups 46/539, maximum 18, mean 16.59, 8 singleton. All five folds converged. Aggregated OOF BA`.501934` over 2,699 rows.
- 11:19 JST prompt-paired bootstrap (2,000 replicates, seed 42) versus adopted prompt-centered SVC primary OOF BA`.465993`: candidate delta`+.035941`, bootstrap mean`+.035778`, 95% CI`[+.024822, +.046694]`. Primary gate passed. Started independent confirmation on the exact config, to compare against the same-split adopted SVC confirmation OOF. No Kaggle submission.
- 11:28 JST confirmation fold0 completed (540 rows): BA`.492593`, `n_iter=35`, `converged=true`; inferred groups 58/540, maximum 18, mean 15.67, 18 singleton. Fold1 started.
- 11:37 JST confirmation fold1 completed (540 rows): BA`.505556`, `n_iter=35`, `converged=true`; inferred groups 40/540, maximum 18, mean 16.94, 6 singleton. Fold2 started. Resource limits remain satisfied; Qwen02/04 remain alive and unchanged.
- 11:44 JST confirmation fold2 completed (540 rows): BA`.505556`, `n_iter=36`, `converged=true`; inferred groups 48/540, maximum 18, mean 16.43, 11 singleton. Fold3 started.
- 11:52 JST confirmation fold3 completed (539 rows): BA`.518838`, `n_iter=35`, `converged=true`; inferred groups 40/539, maximum 18, mean 16.81, 6 singleton. Fold4 started. Rate guard passed at 11:52:28 JST (`100%` 5h, `96%` weekly); no resource threshold approached.
- 12:00 JST confirmation fold4 completed (540 rows): BA`.481481`, `n_iter=35`, `converged=true`; inferred groups 39/540, maximum 18, mean 16.94, 4 singleton. All five confirmation folds converged; overall OOF BA`.500818`.
- 12:01 JST same-split paired bootstrap versus adopted prompt-centered SVC confirmation BA`.469714` passed: candidate delta`+.031104`, bootstrap mean`+.031020`, 95% CI`[+.020325, +.041482]` (2,000 prompt groups replicates, seed 42). Both primary and independent confirmation gates passed, so fixed pool-row weight`.10` is adopted as the next OOF comparison baseline. This is CV-only adoption, not an LB claim or submission authorization. Qwen02/04 remain unchanged.
- 12:04:43 JST rate guard passed (`99%` 5h, `96%` weekly). Load average was 2.49/2.76/3.02 on 72 CPUs, with Qwen02/04 each using one CPU core while retaining GPU utilization.
- 12:06 JST registered a new fixed spec testing only Open Pool row weight`.05` versus the adopted`.10` SVC. Started its primary on 2 CPU threads in a separate artifact directory; initial MemAvailable about`203 GiB`. Qwen02/04 were not stopped or modified. No submission.
- 12:07 JST official Kaggle MCP refreshed competition metadata and leaderboard: top remains Le Viet / Hod Carriers tied at`.747`; max daily submissions remains 5. Metadata deadline reports Jan 14 23:59 UTC, conflicting with previously verified Timeline Jan 13 23:59 UTC; continue using the conservative Jan 13 date. No submission made.
- 12:15 JST 0.05 primary fold0 completed (540 rows): BA`.498148`, `n_iter=34`, `converged=true`; same-fold adopted 0.10 SVC BA`.485185` (exploratory delta`+.012963`). Fold1 started; no gate decision before full OOF and bootstrap.
- 12:22 JST 0.05 primary fold1 completed (540 rows): BA`.492593`, `n_iter=34`, `converged=true`; same-fold adopted 0.10 SVC BA`.481481` (exploratory delta`+.011111`). Both observed fold deltas are positive; fold2 started.
- 12:30 JST 0.05 primary fold2 completed (540 rows): BA`.505556`, `n_iter=35`, `converged=true`; 3/5 folds are positive against the same-fold 0.10 baseline, with overall bootstrap still pending. Fold3 started; resource guard passed 12:27:09 JST (`98%` 5h, `96%` weekly).
- 12:38 JST 0.05 primary fold3 completed (540 rows): BA`.518519`, `n_iter=33`, `converged=true`; this is below the same-fold 0.10 result`.529630`. Three of the first four fold deltas are positive; fold4 started, adoption decision pending.
- 12:46 JST 0.05 primary fold4 completed (539 rows): BA`.516986`, `n_iter=34`, `converged=true`; 5-fold OOF BA`.506366` and all folds converged. Against the adopted 0.10 SVC primary BA`.501934`, delta`+.004432`; paired bootstrap mean`+.004535`, 95% CI`[-.004460, +.012970]` (2,000 replicates, seed 42). The CI lower bound fails the preregistered gate, so the 0.05 candidate is rejected and confirmation is skipped. The 0.10 SVC remains adopted; no Kaggle submission.
- 12:52 JST inspected the newly indexed public `ozertuu/0-673-sibling-stylometry-forensic-apex`. It describes a family-mass-preserving sibling-style residual; however search-index and notebook run metadata disagree on last-run date, and the source explicitly says the displayed 0.664 screenshot belongs to another notebook and its own added variant was not measured. Its 16 external datasets/multiple model checkpoints are not reproduced. Registered a separate, independently implemented, text-only family-local residual OOF test; no prompt-size constraint or cross-family adjustment.
- 12:57 JST family-local style residual retry1 produced BA`.506376` and a CI spanning zero, but the validation-label routing flaw was found afterward. Discard this result and do not treat it as a performance gate. Preserve v1/retry1 artifacts for audit.
- 13:07 JST corrected the runner to apply every family head to every validation row using only text and baseline scores. This removes the held-out `true_model` routing. Restarted the primary in a separate retry2 artifact directory; previous metrics are invalid and ignored. No submission.
- 13:08 JST valid retry2 primary complete (2,699 rows, 150 prompt groups, every outer/inner head converged; max family log-mass error`2.22e-16`). BA`.509339` vs 0.10 SVC`.501934`, delta`+.007405`; paired bootstrap mean`+.007472`, 95% CI`[-.001481, +.016664]` (2,000 replicates, seed 42). Lower bound failed the preregistered gate, so reject and skip confirmation. The 0.10 SVC remains adopted; no submission.
- 13:01 JST rate guard passed (`96%` 5h / `96%` weekly). Official leaderboard remains topped at`.747` by Le Viet and Hod Carriers; recent Notebook listings are unchanged. Qwen02/04 PIDs `2827674`/`2889693` are alive on fold1, with no new event/checkpoint since `2026-11-06T21:20:05Z` / `21:50:14Z`; GPU0/1 util`29%`/`30%`, VRAM`3,907`/`15,835 MiB`, host MemAvailable about`203 GiB`. Both remain within limits and are left untouched. No submission.
- Exploratory OOF error overlap: adopted 0.10 prompt-centered SVC vs flat 4-view SVC are aligned on both existing splits. Primary: 194 rows are fixed only by flat while 378 are fixed only by prompt-centered; confirmation: 202 and 384 respectively. Because both splits were inspected for this diagnostic, do not use either as an independent confirmation for a blend selected from this overlap; a future blend needs a fresh fixed confirmation split. No blend is adopted from this observation.
- 13:14 JST rate guard passed (5h 91%, weekly 95%). Refreshed the correct official competition, `name-that-llm` (the similarly named `llm-classification-finetuning` is a different competition and its leaderboard result was discarded): public top is Le Viet / Hod Carriers tied at 0.747; daily limit is five submissions. Competition metadata says Jan 14, 2027, while the official Timeline page says Jan 13, 2027 23:59 UTC; retain Jan 13 as the conservative deadline. Notebook-only, <=9h, Internet disabled, and final two submissions remain the relevant requirements.
- Audited the completed family-mass rerank primary retry1 artifacts: OOF BA 0.434154 vs flat SVC 0.433776 (delta +0.000378); prompt-paired bootstrap mean +0.000336, 95% CI [-0.007778, +0.008534]. The lower bound did not pass the preregistered gate, so reject and skip confirmation; flat SVC remains the comparator. No submission.
- 13:18 JST resource refresh: Qwen02/04 processes `2827674`/`2889693` remain alive on fold1; no fold1 checkpoint is present yet. GPU0/1 utilization 28%/33%, VRAM 3,907/15,835 MiB, host MemAvailable about 200 GiB. Both jobs remain active and below resource thresholds; no stop/restart or artifact changes. No Kaggle submission.
- Registered and implemented the fixed flat-SVC/prompt-centered-SVC equal-probability blend under [its spec](../specs/2026-11-07-openpool-svc-complementary-fixed-probability-blend-spec.md). Fresh `blend-screen` and `blend-confirm` splits use GroupKFold seeds 314159 and 271828; their assignments are saved, distinct, and shared across models. Updated only the two existing CPU runner split selectors/assignment paths and added a standalone evaluator. Runner syntax/CLI checks and fold assignment validation passed; no test suite run.
- The fresh screen flat SVC completed all five folds (OOF BA`.429697`, fold mean`.429681`; all converged). The adopted prompt-centered SVC also completed all five (BA`.493768`, fold mean`.493780`; all converged). The fixed T=1 equal mean reached BA`.476744`; versus the prompt-centered baseline, delta`-.017025`, paired bootstrap mean`-.017064`, 95% CI`[-.031111, -.002572]` (2,000 prompt-group replicates, seed 42). CI is below zero, so the preregistered screen failed and the independent `blend-confirm` was not run. No blend adopted and no Kaggle submission.
- 14:24 JST guard passed (5h 84%, weekly 94%). Correct official `name-that-llm` leaderboard still shows Le Viet / Hod Carriers tied at`.747`; the other competition slug queried earlier was unrelated and its result was discarded. Qwen02/04 fold1 completed with BA`.561111` /`.542593`; both are training fold2. Latest events show GPU1/0 assignments respectively, utilization`27%`/`35%`, VRAM`15,835`/`3,907 MiB`, host MemAvailable about`196 GiB`. Both jobs remain alive; no restart or artifact change. No submission.
- Reviewed public `qianyuchaoni/ntl-own-v37b-fork-v1` version 4 (run metadata Nov 4; search indexing refreshed Nov 7). The V37-B pipeline combines One Swap, a pairwise verifier, GSQ27, and a `.87/.13` V35/MPNet mixture, with many external inputs (19 datasets, 10 models, 9 upstream kernels; T4). Its own notes say the combined gain is not independently measured and the displayed`.664` belongs to another notebook. The appended V43-B four-view pool SVC and Top34-style structural expert is explicitly disabled by default and lacks full ensemble OOF. Not adopted; no source code or weights copied.
- 14:28 JST continuation refresh: `name-that-llm` metadata still reports deadline Jan 14, 2027, while the official Timeline page says Jan 13, 2027 23:59 UTC; retain Jan 13. Public top remains Le Viet / Hod Carriers`.747`. Limits remain five submissions/day, two final selections, Notebook-only, <=9h, Internet disabled; evaluation still says public/private class mixes differ. Guard passed 5h`83%`, week`94%`. Qwen02/04 PIDs `2827674`/`2889693` remain on fold2 after the `fold_data` / `lora_layer_selection` events at `05:01Z`; no fold2 checkpoint yet. Both are CPU-active and GPUs are active (GPU0/1 util`32%`/`30%`, VRAM`3,907`/`15,835 MiB`, host MemAvailable about`200 GiB`). This is within the observed fold1 Stage1 duration so no stop/restart; no Kaggle submission.
- 14:33 JST rate guard passed (`83%` 5h / `94%` weekly). Rechecked public Notebook `ozertuu/0-672-dual-svc-better` current v9 metadata/source: it is a multi-input, multi-head T4 notebook; the source exposes stylegram's SVC and centered twin as parts of a broader external-data stack, but does not substantiate the logged isolated `.423`→`.435` claim with reproducible comparison evidence. Treat that increment as author-reported and do not start a new run from it. Qwen02/04 remain alive on fold2 (PIDs `2827674`/`2889693`); both logs last record `lora_layer_selection` at `05:01Z`, with no fold2 checkpoint yet. Current GPU0/1 utilization is `37%`/`33%`, VRAM `3,907`/`15,835 MiB`; host MemAvailable about `200 GiB`. Fold2 began about 32 minutes ago, so leave both jobs untouched and continue monitoring. No Kaggle submission.
- 14:55 JST guard passed (`82%` 5h / `94%` weekly). Official Kaggle MCP refreshed the current leaderboard and pages: top remains Le Viet/Hod Carriers tied at`.747`; Timeline says Jan 13, 2027 23:59 UTC; Code Requirements specify Notebook-only, Internet disabled, <=9h; submissions remain limited to 5/day and 2 final selections. Evaluation confirms per-class counts and public/private mix differ. Qwen02/04 PIDs `2827674`/`2889693` remain alive on fold2; latest run-log event is still `lora_layer_selection` at `2026-11-07T05:01Z`, with no fold2 checkpoint by `05:55:50Z`. GPU0/1 util`38%`/`26%`, free VRAM`12,068`/`16,266 MiB`, MemAvailable about`200 GiB`. Do not share either active GPU; no new GPU run started.
- Registered [DeBERTa-v3-small prompt-grouped spec](../specs/2026-11-07-deberta-v3-small-prompt-grouped-spec.md) based on the public `goutamsharma12/stylodeberta` v1 recipe, after checking it has no saved outputs and enables Internet. Added independent `src/deberta_experiment.py`, fixed config, and `gpu05-requirements.in/.lock`. Runner uses the saved primary folds and the previously unused `blend-confirm` fold assignment; scores only the fixed final epoch, checkpoints each epoch for resume, requires a passing GPU pilot, and refuses a device with another compute PID. Syntax/CLI verification passed.
- Downloaded official `microsoft/deberta-v3-small` at revision `a36c739020e01763fe789b4b85e2df55d6180012` (MIT; 6 layers, hidden size 768). The first offline load found the environment lacked SentencePiece/Protobuf; pinned these in the candidate-only dependency lock and verified the tokenizer/model locally with Internet disabled using temporary deps. CPU forward produced finite `[1,16,768]` output. The model assets are prepared, but no Qwen or DeBERTa GPU work was stopped, restarted, or launched; no Kaggle submission.
- Additional DeBERTa setup verification: candidate `load_split` confirms primary fold sizes `540/540/540/540/539` and unused `blend-confirm` sizes `540/539/540/540/540`; each split covers all 2,699 train rows and keeps every prompt in one fold. `py_compile` and `--help` pass. The confirmation comparator will be a fresh 0.10 prompt-centered SVC OOF on the exact same `blend-confirm` assignment; the older seed-42 confirmation is not reused.
