# 実装リポジトリの実行入口と成果物保存方法

作成日: 2026-09-10

対象:

- Mamba tracker: `/mnt/HDD10TB-2/aburatani/2025_09_aburatani_Mamba_Trackers`
- SAM2/SAMURAI: `/mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2`

## 1. 全体像

基本的なデータフローは次のとおり。

```text
データセット
  -> detector結果 / 軌跡アノテーション
  -> Mamba tracker学習
  -> Mamba checkpoint
  -> Mamba tracker単体推論 または SAM2/SAMURAIへのmotion prior統合
  -> tracking txt / 可視化 / debug / 評価結果
```

役割分担は以下のとおり。

| リポジトリ | 主な役割 | 主な入口 |
|---|---|---|
| `2025_09_aburatani_Mamba_Trackers` | 軌跡ベースのmotion model学習・単体追跡 | `ssm_tracker/train*.py`, `ssm_tracker/track*.py` |
| `2025_03_aburatani_sam2` | SAM2/SAMURAIによるmask追跡とMamba motion prior統合 | `scripts/main_inference_mot.py` |

実行時は、相対パスの基準が混乱しないよう、それぞれのリポジトリ直下から起動する。

## 2. Mamba Trackers

### 2.1 環境

現在のstateful/TBPTT系スクリプトは、原則として次を使う。

```bash
cd /mnt/HDD10TB-2/aburatani/2025_09_aburatani_Mamba_Trackers
PYTHON_BIN=./.mamba_trackenv/bin/python
```

旧来のスクリプトには `python` を直接呼ぶものもあるため、再現実験では `PYTHON_BIN` を明示するか、スクリプトを確認してから実行する。

### 2.2 入力生成

軌跡アノテーションは `tools/gen_traj_data.py` で作り、`ssm_tracker/traj_anno_data/` に保存する。

```bash
./.mamba_trackenv/bin/python tools/gen_traj_data.py \
  --dancetrack --save_name dancetrack
```

detector結果を作る場合は `tools/gen_det_results.py` を使い、出力は `det_results/<dataset>/<split>/` に置く。

```bash
./.mamba_trackenv/bin/python tools/gen_det_results.py \
  --dataset_name dancetrack \
  --data_root /path/to/DanceTrack/images \
  --split val \
  --exp_file yolox_exps/custom/yolox_x.py \
  --model_path /path/to/yolox_checkpoint.pth.tar \
  --generate_meta_data
```

入力として最低限、detector結果ディレクトリ内に以下を揃える。

```text
det_results/dancetrack/val/
├── dancetrack0004.txt
├── ...
└── meta_data.txt
```

### 2.3 学習入口とconfig

| 目的 | 実行スクリプト | config |
|---|---|---|
| MambaTrack | `experiments/train_mambatrack_tracker.sh` | `ssm_tracker/cfgs/MambaTrack.yaml` |
| TrackSSM | `experiments/train_trackssm_tracker.sh` | `ssm_tracker/cfgs/TrackSSM.yaml` |
| MambaStateful | `experiments/train_stateful_tracker.sh` | `ssm_tracker/cfgs/MambaStateful.yaml` |
| Stateful TBPTT | `ssm_tracker/train_mamba_stateful.py` または smoke script | `ssm_tracker/cfgs/MambaStatefulTBPTT.yaml` |
| Stateful window smoke | `experiments/train_mamba_window_smoke.sh` | `ssm_tracker/cfgs/MambaStateful.smoke.yaml` |

通常の学習例:

```bash
CUDA_VISIBLE_DEVICES=0 \
PYTHON_BIN=./.mamba_trackenv/bin/python \
bash experiments/train_mambatrack_tracker.sh

CUDA_VISIBLE_DEVICES=0 \
PYTHON_BIN=./.mamba_trackenv/bin/python \
bash experiments/train_stateful_tracker.sh
```

TBPTTのsmoke test:

```bash
CUDA_VISIBLE_DEVICES=0 \
PYTHON_BIN=./.mamba_trackenv/bin/python \
bash experiments/train_mamba_stateful_smoke.sh
```

configの主な責務は次のとおり。

- `dataset`: アノテーション、window/unroll長、座標のスケール
- `train`: model構造、batch size、optimizer、epoch、保存周期
- `inference`: track初期化・履歴・欠損時のmotion設定
- `validation`: validation loss、TrackEval、MOT指標の設定

### 2.4 checkpointの保存

標準の保存先は次の形式。

```text
ssm_tracker/saved_ckpts/<exp_name>/<run_id>/
├── <config basename>.yaml
├── manifest.json
├── git.diff
├── epoch<N>.pth
├── best_val_loss.pth
├── best_tracking_hota.pth
└── final.pth
```

`run_id` を省略すると、時刻とgit commit短縮 hashから自動生成される。既存runを上書きする場合だけ `--overwrite` を使う。再現性のため、checkpoint単体ではなく、同じrunディレクトリのconfig・manifest・git diffを一緒に保存する。

既存の古い実験には `saved_ckpts/<exp_name>/epoch<N>.pth` のようなflat配置もある。新規実験ではrun-id付き配置を正本とし、flat配置は旧実験として扱う。

### 2.5 推論入口と保存先

通常のwindow型:

```bash
CUDA_VISIBLE_DEVICES=0 ./.mamba_trackenv/bin/python ssm_tracker/track.py \
  --det_path det_results/dancetrack/val \
  --motion_model_path ssm_tracker/saved_ckpts/<exp>/<run_id>/epoch25.pth \
  --config_file ssm_tracker/cfgs/MambaTrack.yaml \
  --data_root /mnt/HDD10TB-2/aburatani/dataset/DanceTrack/images/{split}/{seq}/{frame_id:08d}.jpg \
  --device 0 \
  --run_id <inference-run-id>
```

stateful型:

```bash
CUDA_VISIBLE_DEVICES=0 ./.mamba_trackenv/bin/python ssm_tracker/track_stateful.py \
  --det_path det_results/dancetrack/val \
  --motion_model_path ssm_tracker/saved_ckpts/<exp>/<run_id>/epoch100.pth \
  --config_file ssm_tracker/cfgs/MambaStateful.yaml \
  --data_root /mnt/HDD10TB-2/aburatani/dataset/DanceTrack/images/{split}/{seq}/{frame_id:08d}.jpg \
  --device 0 \
  --run_id <inference-run-id>
```

推論結果の標準保存先は次の形式。

```text
track_results/{dataset_name}/{tracker_name}/{split}/{run_id}/
├── <sequence>.txt
├── manifest.json
├── git.diff
├── diagnostics.json       # stateful系
└── vis_results/            # --vis指定時
```

stateful推論では、使用したtraining runとの対応を `--parent_training_run_id` またはcheckpoint metadataで記録できる。P1/P2の比較では、`experiments/inference_p1_association_separation.sh` と `experiments/inference_p2_cache_update_control.sh` を使い、`--run_id`を条件ごとに変える。

### 2.6 Mamba側で保存する単位

実験1件につき、少なくとも以下を同じrun名で対応付ける。

1. 学習checkpoint run: `ssm_tracker/saved_ckpts/<exp>/<run_id>/`
2. 推論run: `track_results/<dataset>/<tracker>/<split>/<run_id>/`
3. 評価結果: `artifacts/` または評価ツール側の出力
4. 研究メモ: `.research/lab/projects/sam2-mamba-motion-tracking/experiments/`

研究メモには巨大なtxtやmp4をコピーせず、runディレクトリの絶対パス、checkpoint名、config名、主要指標、再実行コマンドを記録する。

## 3. SAM2 / SAMURAI

### 3.1 環境と入力

```bash
cd /mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2
PYTHON_BIN=./.venv-sam2/bin/python
```

MOT推論は動画ファイルではなく、次のフレーム列＋GT形式を前提とする。

```text
data/DanceTrack/val/val/<sequence>/
├── img1/*.jpg
└── gt/gt.txt
```

リポジトリの `data` は外部データセットへのsymlinkで、現在はDanceTrackの外部配置を参照している。データ本体はリポジトリ成果物として保存せず、symlink先をmanifestに記録する。

### 3.2 メイン推論入口

入口は `scripts/main_inference_mot.py`。`--mode` によりconfigディレクトリを自動選択する。

| `--mode` | configディレクトリ | motion |
|---|---|---|
| `sam2` | `sam2/configs/sam2.1/` | なし |
| `samurai` | `sam2/configs/samurai/` | Kalman |
| `samurai_mamba_window` | `sam2/configs/samurai_mamba_window/` | window型Mamba |
| `samurai_mamba_stateful` | `sam2/configs/samurai_mamba_stateful/` | stateful Mamba |

`--model_name` は `tiny`, `small`, `base`, `base_plus`, `large`。例えば `tiny`なら、SAM2本体のconfigとcheckpointは自動的に次になる。

```text
config:     sam2/configs/<mode>/sam2.1_hiera_t.yaml
checkpoint: checkpoints/sam2.1_hiera_tiny.pt
```

基本実行:

```bash
./.venv-sam2/bin/python scripts/main_inference_mot.py \
  --testing_set data/DanceTrack/testing_set.txt \
  --video_folder data/DanceTrack/val/val \
  --sequence dancetrack0004 \
  --model_name tiny \
  --mode samurai_mamba_stateful \
  --exp_name p4a_epoch100_dancetrack0004 \
  --save_candidate_debug
```

複数sequenceの場合は `--sequence` を省略し、`--testing_set`に列挙されたsequenceを処理する。

### 3.3 SAM2 checkpointとMamba checkpoint

SAM2本体のcheckpointは `checkpoints/`、Mamba motion checkpointは `checkpoints/motion/` またはMambaリポジトリの `ssm_tracker/saved_ckpts/` に置く。

```text
checkpoints/
├── sam2.1_hiera_tiny.pt
├── sam2.1_hiera_small.pt
├── sam2.1_hiera_base_plus.pt
├── sam2.1_hiera_large.pt
└── motion/
    ├── MambaTrack_epoch25.pth
    └── TrackSSM_epoch100.pth
```

現在の `samurai_mamba_stateful` configは、Mambaリポジトリ内の次のcheckpointを絶対パスで参照している。

```text
/mnt/HDD10TB-2/aburatani/2025_09_aburatani_Mamba_Trackers/ssm_tracker/saved_ckpts/mamba_stateful_tbptt_p4a_full/p4a_full_100ep_20260903/epoch100.pth
```

別マシンへ移す場合は、config内の絶対パスを移行先のパスに更新するか、実行時に同等のconfigを別名で保存する。checkpointを変更した場合は、Mamba checkpointのsha256もrun manifestに記録する。

### 3.4 SAM2側の保存先

`main_inference_mot.py`の標準出力は次のとおり。

```text
results/{exp_name}/{mode}_{model_name}/
├── <sequence>.txt
└── <sequence>_candidate_debug.csv   # --save_candidate_debug時

visualization/{mode}/{model_name}/
└── <sequence>.mp4
```

tracking txtはMOTChallenge形式、candidate debug CSVはSAM候補・motion候補・score・fallback/state情報を含む。Cometログは `comet_logs/` に保存され、実行時にscripts/resultsやmotion checkpointがCometへ記録される。

`--exp_name`は結果txtの衝突回避には有効だが、現行コードの可視化先は `visualization/{mode}/{model_name}/`でrun名を含まない。そのため、同じmode/modelで再実行するとmp4が上書きされ得る。重要な比較では、実行後にmp4をrun固有ディレクトリへ退避するか、可視化保存処理をrun固有化する。

### 3.5 minimal integration script

`experiments/inference_samurai_mamba_stateful_minimal.sh`は、リポジトリ直下へ移動し、run rootを作り、以下を保存してから推論する。

```text
results/sam2_stateful_minimal/<RUN_ID>/
├── manifest.json
├── git_commit.txt
├── git_status.txt
├── git.diff
└── samurai_mamba_stateful_tiny/
    ├── <sequence>.txt
    └── <sequence>_candidate_debug.csv
```

この方式を標準に寄せるのが望ましい。なお、現行scriptのmanifestに書かれたcheckpointと、`samurai_mamba_stateful` configが実際に参照するcheckpointが一致しているかは、実行前に必ず確認する。現在はscript側metadataが旧来の `mamba_stateful_dancetrack/epoch100.pth`、config側がP4a full runの `epoch100.pth`を指しており、記録上の不一致がある。

## 4. 推奨保存ルール

### リポジトリに置くもの

- ソースコード、config、実行shell
- 軽量な入力メタデータ
- checkpoint（容量とバックアップ方針が許す場合）
- 実行結果の正本txt、manifest、git diff、diagnostics

### Research Workspaceに置くもの

- 実験の目的と条件
- 使用したrepo commit
- config/checkpoint/inputのパス
- 再実行コマンド
- HOTA/MOTA/IDF1などの要約値
- 結果の解釈と次の判断

巨大なframe画像、mp4、全sequenceのtxtはResearch Workspaceへ複製せず、実装リポジトリのrunディレクトリを参照する。

### 各runのmanifestに残す項目

```json
{
  "run_id": "...",
  "repo": "...",
  "git_commit": "...",
  "git_dirty": false,
  "command": "...",
  "config": "...",
  "checkpoint": "...",
  "checkpoint_sha256": "...",
  "dataset_root": "...",
  "sequence_list": ["..."],
  "output_dir": "..."
}
```

## 5. 現時点での注意点

- Mamba READMEには存在しない `experiments/train_ssm_tracker.sh` の記載が残っている。実際の入口は `train_mambatrack_tracker.sh` または `train_trackssm_tracker.sh`。
- Mambaの古いshellは相対パスと `python`直接呼び出しを含む。必ずrepo直下から実行し、環境を明示する。
- `saved_ckpts`にはflat配置とrun-id付き配置が混在する。新規runはrun-id付き配置に統一する。
- SAM2のstateful configはMamba repoの絶対パスcheckpointに依存する。
- SAM2 minimal scriptのmanifestとstateful configでcheckpoint記録が不一致のため、実験結果を採用する前に実checkpointを確認する。
- SAM2の可視化mp4はrun固有ディレクトリに入らず、同じmode/modelで上書きの可能性がある。
