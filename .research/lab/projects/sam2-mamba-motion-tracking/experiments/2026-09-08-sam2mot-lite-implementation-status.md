---
date: 2026-09-08
project: sam2-mamba-motion-tracking
status: completed
tags: [inventory, sam2mot, tracking-by-segmentation, dancetrack, trackeval, oracle-detection]
---

# SAM2MOT-lite実装リポジトリの棚卸し

## 目的

2026-06-12以降停止している SAM2MOT-lite 実装リポジトリを research-workspace の管理下に置くため、実装の実態・出力カバレッジ・残作業・再現条件を確定する。`sam2mot_lite/README.md` の記述が古く実態と乖離していたため、コードとgit履歴を根拠に事実を確定した。

## 調査対象

- リポジトリ: `/mnt/HDD10TB-2/aburatani/2026_05_aburatani_sam2mot`（`git@github.com:tamaki-lab/2026_05_aburatani_sam2mot.git`, branch `master`, working tree クリーン）
- ベース: SAMURAI fork の commit `639751d`（`sam2mot_lite/SAM2_COMMIT.txt`）
- 自作分: `639751d..HEAD` の差分は `sam2mot_lite/` 配下17ファイルのみ、約2,400行追加
- 最終コミット: `408ee5c`（2026-06-12）

## マイルストーン実装実態

`sam2mot_lite/README.md` のMilestone表はM4以降を「設計のみ」と記載しているが**古い**。READMEの最終更新コミット `5bdcc9e`（2026-05-26 13:34）は、M4〜M8実装コミット `67708f2`/`df58a81`/`30fd309`/`fadcc8e`/`0111eb9`（同日13:53〜14:31）の**祖先**であり、実装後に一度も更新されていない。

| # | 内容 | 実態 | 実装位置 |
|---|---|---|---|
| M0 | Detection Reader / MOT Writer | 実装済み | `tracker/detection.py`, `tracker/result_writer.py` |
| M1 | Mask Utility / Matching | 実装済み | `tracker/mask_utils.py`, `tracker/matching.py` |
| M2/M3 | SAM2 single / multi object prompt | 実装済み | `tracker/sam2_wrapper.py` |
| M4 | 最小推論パイプライン | 実装済み | `scripts/run_sequence.py`, `tracker/track.py` |
| M5 | Object Addition（動的追加） | 実装済み | `trajectory_manager.py:162` |
| M6 | Object Removal / 状態遷移 | 実装済みだが**フラグが効かない** | `trajectory_manager.py:104` |
| M7 | Quality Reconstruction | 実装済み | `trajectory_manager.py:256` |
| M8 | Cross-object Interaction | 実装済みだが**既定で無効** | `trajectory_manager.py:359-426` |
| M9 | TrackEval評価接続 | **未着手**（出力形式のみ適合） | — |

`README.md` の構成図に記載のある `tracker/cross_object_interaction.py` と `scripts/visualize.py` は**全git履歴を通じて存在しない**。M8は専用モジュールではなく `trajectory_manager.py` に同居し、可視化機能は未実装。

## 重大な注意: 検出入力がGTのオラクル設定

`scripts/run_dancetrack.py:116` は検出入力として **DanceTrackの `gt/gt.txt` をそのまま読んでいる**。

```python
detections_file = os.path.join(args.video_folder, seq, "gt", "gt.txt")
```

`gt.txt` のscore列は常に `1`（例: `12,0,823,617,158,236,1,1,1`）であり、`det_conf_thr: 0.5` のフィルタは実質無効。つまり `results/sam2mot_lite/dancetrack/` の出力は**GT bboxをpromptに与えたオラクル検出条件**の結果であり、detector入力を用いる既存ベースライン（`my_sam2_model` HOTA 51.269 等）とは**原理的に比較できない**。

この設定を是正しない限り、SAM2MOT-liteの数値は本プロジェクトの定量比較には使えない。一方、途中検出による補正という着想の**挙動確認**には支障がない。

## 出力カバレッジ

DanceTrack val 25系列のうち**15系列**に結果ファイルが存在する。

- 欠損10系列: `dancetrack0014` `0019` `0026` `0034` `0041` `0063` `0073` `0081` `0090` `0094`
- 欠損は辞書順の先頭/末尾に固まらず**全体に散在**している
- 存在する15系列は**すべて完走**（`minF=1`、`maxFrame == seqLength`、フレーム欠落なし、`(frame, track_id)` 重複なし）。サンプル確認: `dancetrack0004` 1203/1203、`dancetrack0079` 1202/1202、`dancetrack0097` 1203/1203
- `max_frames` は `configs/default.yaml:21` で `null`、CLI既定も `None` のため打ち切りなし
- ファイルmtimeは辞書順に単調増加（2026-06-11 13:56:41 → 2026-06-12 05:25:00）、最後は辞書順最終系列の `dancetrack0097`

したがって「15系列目で処理が止まった」のではなく、**25系列のループは最後まで到達し、10系列が出力を一切生成しなかった**。`write_trajectories` は0件でも空ファイルを作る実装（`result_writer.py:22`）で0バイトファイルが無いため、欠損系列は `run_sequence.py:207` に到達していない。

### 未解明点

**欠損10系列の失敗原因は不明。** 実行ログ・nohup出力が一切残っていない（`.gitignore:58` が `*.log` を除外）。`run_dancetrack.py:137-138` の例外catch（OOM含む）か `run_sequence.py:106-108` の早期returnかを区別する直接証拠がない。再実行してログを取る以外に切り分け手段がない。

## SAM2内部ステート操作の範囲

**SAM2本体（`sam2/`）は本研究では一行も改変されていない。** `sam2/` を触った最後のコミットは SAMURAI上流作者による `76ba195`（2025-03-18）で、`639751d..HEAD` の差分は `sam2mot_lite/` に閉じている。

したがって「SAM2の改変」ではなく、**非公開の `inference_state` をラッパー側から外科的に書き換える**方式。これにより可能になっているのは3点。

1. `tracking_has_started` / `frames_already_tracked` を一時的に偽装し、追跡開始後の新規 `obj_id` 登録を通す
2. `output_dict` / `output_dict_per_obj` の全過去フレームのテンソルをバッチ次元でゼロ／`NO_OBJ_SCORE` パディングし、既存物体の時間的メモリを保持したまま B→B+1 に拡張する（`sam2_wrapper.py:78`, `:125-135`）
3. CPUオフロード時にテンソルごとの `.device`/`.dtype` を読んでパディングを作り、デバイス／dtype競合を回避する

### プルーニングとOOMの真因

`run_sequence.py:179-186` の `prune_horizon=48` は `non_cond_frame_outputs` のみを削除する。実際にattentionされる窓（maskmem は t-1..t-6、obj_ptr は t-1..t-15）より十分広いため推論結果への影響はほぼない。

一方 `cond_frame_outputs` は一切削除されず、`max_cond_frames_in_attn=-1` のため**物体追加・再プロンプトのたびに条件フレームが永久に増え、毎フレーム全部cross-attentionされる**。これがOOM・低速化の真の主因であり、48プルーニングでは救えない。

### 内部API依存度

依存している非公開要素: `inference_state` の8キー、frame出力dictの5キー、`obj_idx = 挿入順 = バッチ位置` という不変条件、`NO_OBJ_SCORE` のprivate import、generatorのclose/再呼出し挙動。SAM2側がステート構造を変えれば即座に壊れる。**SAM3移行時にこの実装は再利用できない前提で扱うべき。**

なお `OBJECT_ADDITION.md` の「時間的メモリを100%保持」という主張は、後発の `408ee5c` によるプルーニング導入で現状と矛盾している。

## M9（TrackEval評価接続）の残作業

出力形式は**TrackEvalのMOTChallenge要件を既に全て満たしている**（10列、frame_id 1始まりで `seqLength` と一致、track_id 1始まり、xywh、末尾3列 `-1`、重複なし）。score列が1を超える（0.42〜19.44、SAM2 mask logits平均由来）が、`tracker_confidences` はmetrics側で参照されず各metricのTHRESHOLDはIoUに適用されるため、**HOTA/CLEAR/Identity の計算に影響しない**。

`/mnt/HDD10TB-2/aburatani/TrackEval` 側は DanceTrack val 用の gt symlink・`seqinfo.ini`・25系列seqmap・`run_mot_challenge.py` ラッパ・既存手法用シェルスクリプトが完備。技術的な残作業は次の2点だけ。

1. 15系列分の結果を `data/trackers/dancetrack/val/<name>/data/` へ配置
2. `--SEQ_INFO` で15系列を指定して実行

ただし**実質的な残作業は方法論側**にある。

- 検出入力をGTからdetector出力へ差し替える（上記オラクル問題の解消）
- 15系列の `COMBINED_SEQ` は既存25系列ベースラインと比較不可能なため、25系列を揃えるか比較対象を15系列で再計算する

## 再現環境

- venv: `/mnt/HDD10TB-2/aburatani/2026_05_aburatani_sam2mot/.venv-sam2mot`（Python 3.12.3）
- 主要パッケージ: torch 2.12.0+cu130 / numpy 2.4.6 / scipy 1.17.1 / opencv-python 4.13.0.92 / hydra-core 1.3.2 / iopath 0.1.10、SAM-2 1.0 が editable で同梱 `sam2/` を指す
- checkpoint: `sam2/checkpoints/` に tiny/small/base_plus/large 全4サイズ、既定は sam2.1 tiny
- データ: `data/DanceTrack` → `/mnt/HDD10TB-2/aburatani/dataset/DanceTrack/standard_format` の symlink

### 実行時の必須条件と罠

- `cwd` = リポジトリルート、`PYTHONPATH=./sam2mot_lite` が必須
- **`PYTHONPATH` に `.` を入れてはいけない。** 同名ディレクトリ `sam2/` が `sam2` パッケージを遮蔽し、`build_sam.py` が `RuntimeError` を投げる（実測確認済み）

### 再現性のリスク

- `requirements.txt` も lock ファイルも存在せず、venv自体は `.gitignore` 除外。**venvを失うとバージョン再現は不可能**
- 既存 `results/` は `.gitignore` 除外の未コミット生成物。生成時刻（6/11〜6/12）が HEAD の2コミット（メモリプルーニング追加・パディング修正）**より前**のため、HEADで再実行しても同じ数値は再現しない

## 既知の不具合・死んだ設定

| 項目 | 内容 |
|---|---|
| `enable_object_removal` | `.py` 内の参照**0件**。M6は実装されているがこのフラグでは制御できない |
| `save_visualization` | `.py` 内の参照**0件**。可視化機能自体が未実装 |
| `associate_and_update()` | track index のずれによる実バグの指摘あり（`trajectory_manager.py:256`）。未修正 |

参照が生きているフラグ: `enable_object_addition`（3件）、`enable_quality_reconstruction`（2件）、`enable_cross_object_interaction`（6件、既定 `false`）、`save_masks`（3件）。

## 結論と扱い

M0〜M8は実装済み（M6はフラグ不通、M8は既定無効）、M9は未着手。8/28 MTGの方針どおり、このリポジトリは**SAM2MOTの再現を完成させる対象ではなく、途中検出による軌跡補正という着想の実験場**として扱う。

本プロジェクトへ持ち込む際に踏まえるべき点は3つ。

1. 既存の出力はGTオラクル条件であり、定量比較には使えない
2. 動的オブジェクト追加はSAM2の非公開ステート依存が非常に強く、SAM2デコーダー統合やSAM3移行時に再利用できない
3. 着想として有用なのは「追跡途中で検出を再prompt して軌跡を補正する」という構造そのもの（M5 Object Addition と M7 Quality Reconstruction）
