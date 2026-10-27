---
date: 2026-10-27
project: sam2-mamba-motion-tracking
spec: ../specs/2026-10-27-temporal-mamba-short-clip-official-trainer-spec.md
status: in-progress
tags: [experiment, temporal-mamba, sam2, mose, short-clip, official-trainer]
---

# SAM2公式の学習コードによるV3の短い区間での学習 実験ログ

承認済みspec：[2026-10-27-temporal-mamba-short-clip-official-trainer-spec.md](../specs/2026-10-27-temporal-mamba-short-clip-official-trainer-spec.md)

## 段階0 実装（2026-10-27）

SAM2 repo `/mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2`、ブランチ `feat/official-trainer-short-clip`（`1002_seminar` の `09a30a7` から作成。作業中に並行セッションが `187fe1b`（`AGENT_RESEARCH.md`）を同じブランチにコミットした）。2026-10-27に7つに分けてコミット：`4c6a092`（隠しファイルの無視）、`3b0b08c`（補正クリックの経路とIoUの修正）、`72255f7`（SAM2Trainのadapterと一部の学習）、`e24890b`（dataloaderのseed・`--experiment-log-dir`）、`290228a`（trainer・設定・動画リスト・実行スクリプト）、`8a92a56`（評価）、`1895c45`（段階1の確認・手順書）。push・mergeは未実施。手順書は `training/README_short_clip.md`。

### 変更したファイル

| ファイル | 内容 |
|---|---|
| `training/model/sam2.py`（`SAM2Train`） | `temporal_adapter`・`adapter_checkpointing`・`trainable_modules` の引数。`forward_tracking` で区間ごとに0のstateを明示的に作って1フレームずつ渡す（先頭にマスクを与えたフレームはV3を通らず、stateをそのまま次へ）。`train()` で固定したmoduleをevalのままにする。補正クリックの経路の修正（戻り値8要素、全候補のIoU）。マスクを出力にしたフレームのIoUの予測は定数1（公式と同じ）にする。記録用に各クリップのプロンプトを保持 |
| `training/short_clip_trainer.py`（新規） | 公式 `Trainer` のサブクラス。更新ごとのプロンプトの乱数の初期化、val-25（学習前と2 epochごと）、`manifest.json`（実際に学習したパラメータ、weight decayの除外、学習率のグループ、モード）、`samples.jsonl`、Comet、固定したパラメータの不変の確認、pilot用の `stop_after_steps` と診断用loss |
| `training/dataset/sam2_datasets.py` | `seed` 引数：dataloaderのworkerを `seed + epoch` から初期化（既定は従来どおり） |
| `training/dataset/vos_segment_loader.py` | マスクのフォルダの隠しファイルを無視（下記） |
| `training/train.py` | `--experiment-log-dir`（run directoryの指定。既存のものを指定すると再開） |
| `training/mose_adapter_eval.py` | `--trainer-checkpoint`（公式の形式のcheckpointから全重みを `strict=True` で復元）、`--reset-interval` |
| `sam2/modeling/temporal_adapters.py` | 推論用の `reset_interval`（Nフレームごとにstateを初期化） |
| `sam2/configs/sam2.1_training/short_clip/*.yaml`（新規） | `base.yaml`（公式のMOSE configとの違いを冒頭に列挙）、`A_v3`・`A_v3_nockpt`・`B_decoder`・`C_v3_decoder`、pilot用 |
| `training/assets/MOSE_short_clip_train_list.txt`（新規） | trainの1,121動画 |
| `training/check_short_clip.py`（新規） | 段階1の確認C1〜C11 |
| `experiments/short_clip/{train,eval}.sh`（新規） | 実行用の薄いラッパー |

- 旧自作trainer（`mose_adapter_train.py`）が通る経路（boxのみ、補正なし、`track_step` を直接呼ぶ）は、`SAM2Train` の変更の影響を受けない（IoUの値は従来と同じ `_last_multimask_ious`、`trainable_modules` は未指定）。旧trainerの照合（refactor_golden）は回していない。
- run directoryは `runs/short_clip/`（`.git/info/exclude` でgit管理外）。

### 実装中に見つけたこと

- **MOSEのフォルダにmacOSの隠しファイルがある**：`train/JPEGImages` と `train/Annotations` の下に `._*` が各95,381個（1,508フォルダ）ある。公式の `PalettisedPNGSegmentLoader` は `os.listdir` の全ファイル名を整数に変換するので、そのままでは全動画の読み込みに失敗した。データは消さず、読み込み側で `.` で始まるファイルを無視するようにした。画像側は `glob("*.jpg")` が隠しファイルを拾わないので影響なし。旧自作trainerは `stem.isdigit()` で除外していた。
- **このrepoの `_forward_sam_heads` は3番目の戻り値が「選ばれた候補のIoU」になっている**（SAMURAIの改変）。公式の学習コードは全候補のIoUを前提にしているので、補正クリックの経路とマスクを出力にするフレームで、lossに渡すIoUを直した（specのレビュー1の指摘どおり）。
- 公式のtrainerはepochの区切りでしかcheckpointを保存しないので、val-25の間隔は「2,500更新ごと」ではなく「2 epoch（2,242更新）ごと」にした（spec改訂済み）。再開は中断したepochの最初からやり直す（公式の挙動）。

## 段階1 正しさの確認（2026-10-27、完了：11/11合格）

コード：コミット前の状態（`187fe1b` + 差分。内容は上の7コミットと同じ）。結果：SAM2 repo `runs/short_clip/stage1/20261027_187fe1b-dirty/c*.json`。C11以外はRTX PRO 4500、FP32・決定的な設定（cuDNNの決定論、TF32なし、math attention）、1区間4フレーム。C11はRTX A4000、bf16・既定のkernel（保存済みのF0の評価と同じ条件）。

| 確認 | 結果 |
|---|---|
| C1 初期化直後のA・Cの出力が、V3なしと一致（マスク・クリック・boxそれぞれ） | 6通りとも差0 |
| C2 学習データがtrainだけ、A・B・Cで同じサンプル列 | 3更新分の動画・対象・フレーム・プロンプト・画像の合計値がA・B・Cで完全一致。1更新目のlossも3条件で同じ（2.9147） |
| C3 3更新の後、固定したパラメータはF0と同じ、学習するものだけが動く、manifestが正しい | A・B・Cとも固定したパラメータの変化0。B・Cのマスクデコーダは全パラメータが変化。モードも想定どおり。V3のweight decayの除外は26個で、旧trainerと同じ集合 |
| C4 各プロンプトでforward・backwardが通り、IoUの予測が候補と対応 | マスク：予測1回・候補1、クリック：予測8回（初回3候補、補正後1候補）、box：予測8回。IoUの形はすべて候補と一致。lossと勾配は有限で、V3とデコーダの両方に勾配が届く |
| C5 先頭がマスクならV3を通らず、次のフレームに0のstate | マスク：V3の呼び出し3回（4フレーム中）、クリック・box：4回。最初に渡るstateはすべて0 |
| C6 最後のフレームのlossが前のフレームのconv state・SSM stateに届く | フレーム1〜3の3段×2種の計18個すべてに勾配（ノルム0.0032〜0.046） |
| C7 区間の間でstateが初期化され、計算グラフが漏れない | 2区間目の最初のstateは0で、計算グラフなし（全プロンプト） |
| C8 2回の更新で、V3の全部品に勾配が届く | 1回目は46個中40個が勾配0（出力層が0で始まるため、想定どおり）、2回目は0のものなし |
| C9 学習の経路と推論の経路の一致 | 補正なし・同じ入力・同じbox・evalモードで、全フレームのマスクのlogitとV3のstateの差0 |
| C10 保存→評価用loaderで復元→一致 | B（デコーダを変更）・C（デコーダとV3を変更）とも全パラメータ一致、tuningの1対象の評価結果も一致 |
| C11 学習前のval-25が保存済みのF0と一致 | 64対象すべてでJ・F・J&Fが完全一致（RTX A4000） |

再開の確認：Aの3更新後のcheckpointを `checkpoint.pt` にして同じrun directoryで起動し直すと、step 3から続き（`manifest-*.json` の `resumed_at_step` = 3）、固定したパラメータの確認も通った。

### 速さとメモリの目安（smoke、正式な計測は段階2）

| 条件・GPU | 1更新の時間 | VRAMのピーク |
|---|---|---|
| A・RTX PRO 4500・checkpointingなし | 0.7〜1.0秒（12更新） | 約22 GB |
| A・RTX A4000・checkpointingあり | 1.8〜2.1秒（3更新） | 約9 GB |
| B・RTX A4000 | 未計測（3更新のみ） | 約4 GB |
| C・RTX A4000・checkpointingあり | 未計測（3更新のみ） | 約10 GB |

24,662更新では、Aは約6時間（RTX PRO 4500）、A4000のV3の条件は約13時間の見込み（val-25を除く）。val-25は1回約14分。

## 段階2 実測・pilot

未実施。
