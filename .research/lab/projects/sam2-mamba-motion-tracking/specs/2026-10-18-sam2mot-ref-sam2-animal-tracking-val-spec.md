---
date: 2026-10-18
project: sam2-mamba-motion-tracking
source: chat
status: approved
approved: 2026-10-18
tags: [spec, experiment, sam2mot, reproduction, reference-implementation, dancetrack, val]
---

# SAM2MOT再現 第三者の再実装（SAM2-Animal-Tracking）を DanceTrack val で動かす Spec

## 目的

SAM2MOT の公式コードは未公開（2026-10-18 に再確認、`TripleJoy/SAM2MOT` は README と画像のみ）。代わりに、SAM2MOT を独自に再実装して動物向けに改変した第三者のリポジトリ（`ecker-lab/SAM2-Animal-Tracking`、arXiv 2511.02591）を、本再現と同じ検出で DanceTrack val 25系列に回し、本再現の S4 と並べる。

これは**参考比較**であり、本再現の性能値でも SAM2MOT の再現値でもない。

## 背景

- 本再現の S4（val、o365tococo）は HOTA 69.29。test では論文より HOTA 約4、MOTA 約9 低い見込み（`experiments/2026-10-09-sam2mot-test-runs.md`）
- val の診断では、CoI 後に残る差の主因は box の位置ずれだった（`experiments/2026-10-15-sam2mot-add-fp-diagnosis.md`）
- 第三者の論文は「SAM2MOT は系列ごとに手で選んだ検出閾値に頼っている」と述べ、系列ごとに自動で閾値を決める方法（Otsu 法 + 0.1）を提案している。公式 README の系列別閾値 CSV（未公開）とも整合する。test で Add の寄与が論文の半分しかないことの候補
- 第三者の実装は本再現と次の点が違う: 自動閾値、Add の判定（新しいマスクと既存マスクの重なりで判定）、マスク NMS（論文にない）、CoI Stage 2 の std 差の閾値 0.2、Q-R はトラックを作り直す、全トラックを1つの SAM2 状態で処理、bfloat16 の autocast、lost のフレームも出力。出力 box はマスクの外接矩形で本再現と同じ

## 検証したい問い

1. 第三者の再実装は、同じ検出で、本再現の S4 より DanceTrack val で高いか
2. 系列ごとの自動閾値は、固定閾値 0.5 に比べて DanceTrack val で効くか

## 実験内容

### 環境（実装リポジトリ・`.venv-sam2mot` は変更しない）

- 場所: `/mnt/HDD10TB-2/aburatani/SAM2-Animal-Tracking`（ユーザーが clone 済み、HEAD `b02af23`）
- `git submodule update --init` で `sam2/` を取得（固定 commit `2b90b9f`）
- 新しい venv をこのリポジトリ内に作る（`.venv`）。torch は本再現と同じ `2.12.0+cu130` を入れる（本再現の `.venv-sam2mot` と同じ版で、RTX A4000 でも動作実績がある）。ほかは `setup.py` のとおり。インストール内容は `requirements-local.txt` に固定する
- SAM2.1 large のチェックポイントは実装リポジトリの `sam2/checkpoints/sam2.1_hiera_large.pt` をリンクする
- 第三者のコードは、次の1か所を除いて改変しない。設定は `run.py` の引数で変える
  - `tracker/sam2tracker.py` の `init_state(video_path=video_dir)` に `offload_video_to_cpu=True, offload_state_to_cpu=True` を足す。既定では全フレーム（1024×1024、float32）を GPU に載せるため、val の系列長（183〜2,402 フレーム、中央値 1,003）では1系列で最大約 30 GB になり、16 GB の A4000 では動かない。offload は保存先を変えるだけで、本再現では出力が md5 一致することを確認済み。差分は出力ディレクトリに `git.diff` として残す
  - これ以外の改変が必要になった場合は、内容を記録してユーザーに確認する

### 入力

- データ: `data/dancetrack/val` に DanceTrack val 25系列をリンク、`val_seqmap.txt` を置く
- 検出: 本再現の o365tococo 検出（`results/detections/co_dino_l_o365tococo_val25/`）を、第三者の形式（系列ごとの `.pt`、フレームごとに `boxes`（xywh）・`scores`・`labels`）に変換する。変換時に score ≥ 0.1 で切る（第三者の検出生成の既定 `DETECTOR.TH_DET = 0.1` に合わせる。自動閾値はこの分布から計算される）
- 変換スクリプトは実装リポジトリ `sam2mot_repro/scripts/ref_animal_convert_dets.py`（新規、読み取りと書き出しのみ）

### run

| run | 設定 | 目的 |
|---|---|---|
| R1 | 既定値（`USE_OTSU True`、δ = 0.1、マスク NMS あり、他も `run.py` の既定）、`--SAM2.COMPILE_ENCODER False`、`--DETECTION False --DETECTOR.LOAD_DETS True` | 問い1 |
| R2 | R1 から `--SAM2MOT.USE_OTSU False`（高信頼の閾値は既定の 0.5 に固定、本再現と同じ） | 問い2（R1 − R2 が自動閾値の効果） |

- GPU: RTX A4000（`CUDA_VISIBLE_DEVICES=1`）。Blackwell は他の作業で使うため使わない。R1 → R2 の順に回す
- `COMPILE_ENCODER` を切るのは、torch.compile が新しい torch・GPU で不安定になるのを避けるため（記録する）
- 出力先: 実装リポジトリ `results/tracks/ref_sam2animal_{r1,r2}/`（`--OUTPUT_DIR` で指定）

### 評価

- 本再現と同じ TrackEval のラッパ（`sam2mot_repro/scripts/eval_trackeval.py`）で評価する
- FP の内訳を `diag_add_fp.py` で数え、本再現 S4 の内訳と並べる（読み取りのみ）

## 比較対象

- 本再現 val（o365tococo）: S2 HOTA 65.76、S3 68.98、S4 69.29（`experiments/2026-10-13-sam2mot-o365tococo-val.md`）
- ノイズの目安: 同じ設定で GPU を替えたときの val COMBINED の差は HOTA 0.15（`experiments/2026-10-14-sam2mot-coi-stage2-skip.md`）。実装が異なる比較なので、±0.5 以内は差なしとみなす

## 評価指標

HOTA、DetA、AssA、MOTA、IDF1、IDSW、FP、FN（COMBINED と系列別）。FP の内訳（重複・位置ずれ・部分重なり・背景）。

## 判断の基準（次に何をするか）

| 結果 | 次の行動 |
|---|---|
| R1 が本再現 S4 より HOTA +0.5 以上高い | どの違いが効いているかを切り分ける候補を挙げる（新しい spec。本再現に取り込むかはユーザーが判断） |
| R1 − R2 が HOTA +0.5 以上 | 自動閾値を本再現の比較設定として試す候補にする（論文からの変更として扱う。新しい spec） |
| R1 が本再現 S4 と ±0.5 以内か低い | 第三者の設計変更は DanceTrack val では効かないと記録し、SAM2MOT の深追いを区切る材料にする |

いずれの場合も、本再現の主設定（SPEC A1〜A9）は変えない。

## 実施手順

1. 環境を作る（submodule、venv、チェックポイントのリンク、データのリンク、seqmap）
2. 検出を変換し、1系列で件数が元ファイル（score ≥ 0.1）と一致することを確認する
3. smoke: 1系列（`dancetrack0004`）の全フレームで R1 を回し、出力が MOT 形式検証（`validate_tracks.py`）を通ることを確認する
4. R1 を val 25系列、続けて R2 を回す（`setsid nohup`）
5. TrackEval と FP の内訳を取る
6. 実行の事実を実装リポジトリ `sam2mot_repro/logs/ref_sam2animal_val25.md`、結果と解釈を `experiments/2026-10-18-sam2mot-ref-sam2-animal-tracking-val.md` に記録する

## リスク・懸念

- VRAM: offload を入れても、人数の多い系列で 16 GB を超えるおそれがある。超えた系列は記録して止め、ユーザーに確認する
- 時間: A4000 で offload ありのため遅い。本再現の A4000・offload ありの val 25系列（S3）は 5.4 時間だった。R1・R2 で合わせて半日〜1日程度を見込む
- GPU: 本再現 S4 は Blackwell で回している。同じ設定で GPU だけを替えたときの差は HOTA 0.15 程度で、判断の基準（±0.5）より小さい
- torch の版が第三者の指定と違う（2.12 と 2.6）。数値の細かい差はありうる
- bfloat16 の autocast（第三者の既定）を使うので、本再現（float32）との差には数値精度の違いも含まれる
- ライセンスの表記がないので、コードは手元の比較に使うだけにし、本再現の実装に取り込まない
- 第三者の実装は、作者自身が「論文の性能には届かなかった」と書いている

## 関連

- 第三者の論文: arXiv 2511.02591（Meier & Lüddecke、Zero-Shot Multi-Animal Tracking in the Wild）
- リポジトリ: <https://github.com/ecker-lab/SAM2-Animal-Tracking>、公式 SAM2MOT の issue #11 で紹介
- 本再現の spec: `specs/2026-09-08-sam2mot-reproduction-spec.md`

## 改訂履歴

- 2026-10-18: 初版（draft）。ユーザーが /goal で実施を指示し approved。同日、Blackwell を他の作業で使うため GPU を RTX A4000 に変更し、VRAM 対策として offload の1か所の改変を追加
