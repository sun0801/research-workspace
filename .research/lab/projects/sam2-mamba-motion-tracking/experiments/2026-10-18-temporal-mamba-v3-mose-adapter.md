---
date: 2026-10-18
project: sam2-mamba-motion-tracking
spec: ../specs/2026-10-18-temporal-mamba-v3-mose-adapter-spec.md
status: in-progress
tags: [experiment, temporal-mamba, sam2, mose, fpn, adapter]
---

# V3（FPN的なtemporal Mamba）のMOSE adapter学習 実験ログ

承認済みspec：[2026-10-18-temporal-mamba-v3-mose-adapter-spec.md](../specs/2026-10-18-temporal-mamba-v3-mose-adapter-spec.md)

## 実装（2026-10-18〜19）

- SAM2 repo `/mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2`、ブランチ `feat/temporal-mamba-v3`（`dev` の `f52a744` から作成）。2026-10-21に3つに分けてコミット：`c2e928b`（adapter本体・`sam2_base.py`・単体確認）、`50f773b`（学習・評価・集計・Comet・実行記録）、`80610fe`（YAML設定・ラッパー・手順書）。`c2e928b` 単独でも単体確認19/19が通ることを確認。pilot以降のrunはこれらのcommitを記録するので、このブランチの履歴は書き換えない（`dev` へはsquashせず通常のmergeで取り込む）。push・mergeは未実施。手順書は `training/README_temporal_adapters.md`。
- 追加：`sam2/modeling/temporal_adapters.py`（`MambaCell`、共通の枠、V1 `GlobalPoolAdapter`、V3 `PyramidAdapter`）、`training/mose_adapter_train.py`（check / parity / pilot / measure / train）、`training/mose_adapter_eval.py`、`training/mose_adapter_summary.py`、`training/comet_utils.py`、`training/check_temporal_adapters.py`。
- 変更：`sam2/modeling/sam2_base.py`（新しいadapterの呼び出し経路。stateを渡せば学習、渡さなければ推論。既存adapterの経路はそのまま）。
- specとの違い：specでは `mose_fulltrack.py` などにオプションを足す計画だったが、旧F0/F1の学習・評価・lockbox照合が実装ハッシュを使うため、旧スクリプトは変えずに新しいファイルとして追加した。
- 環境：`.venv-sam2`（torch 2.10.0+cu128、`mamba_ssm` 2.3.1。`setup.py` の記載は2.2.2だが、実際に入っているのは2.3.1）。
- Comet：記録先は `.comet.config` の `samurai-mot`、タグ `temporal-mamba`。動作確認で送ったexperimentは削除済み。
- 実行方法（2026-10-19、Mamba_Trackersの型に合わせて作り直し）：条件は `configs/temporal_adapters/*.yaml`（pilot・measure・train。trainの `adapter_lr` と `max_steps` は決めるまで `null` にしてあり、未設定だと起動しない）。実行は `experiments/temporal_adapters/*.sh`（Pythonを呼ぶだけの薄いラッパー、`"$@"` で上書き）。runごとに `runs/temporal_adapters/<name>/<run_id>/` を作り、configのコピー、`manifest.json`、`git.diff`（未コミットの変更と未登録のコードファイルを含む）を保存する。`git.diff` がHEADにきれいに当たることを確認済み。未コミットでも実行は止めない。
- GPUの番号：CUDAの既定の順番ではindex 1がA4000になる。コマンドでは必ず `CUDA_DEVICE_ORDER=PCI_BUS_ID` を付ける（PCI順で0=A4000 16GB、1=RTX PRO 4500 32GB）。

## 段階0a 正しさの確認（2026-10-18〜19、完了）

証拠のファイルは `runs/mose_temporal_mamba_v3_20261018/stage0a/`。

### adapter単体（`check_temporal_adapters`、RTX PRO 4500、FP32）：19/19合格

| 確認 | 結果 |
|---|---|
| `MambaCell` と `mamba_ssm` の `Mamba.step` の一致（7 step） | 最大差 1.5e-8 |
| V1・V3（段：64 / 64,128 / 64,128,256）：初期化（α=1、`W_out`=0）で入力をそのまま返す | 差0 |
| 学習用と推論用の経路の一致（αと `W_out` をゼロでない値にして、12フレーム、TBPTT=8の境界を含む） | 出力・conv state・SSM stateとも差0 |
| `reset_every_frame` で毎フレームstateが初期化される | 新しいstateで計算した出力と差0。持ち越した版とは差がある |
| 1回目の更新ではMamba内部の勾配が0、`W_out` が動いた後の2回目でMamba内部に勾配が届く | 全段で確認。V3では段どうしの1×1 convにも届く |

### SAM2＋F0にV3を付けた状態（`--mode check`）

- 初期化直後のV3と、adapterを無効にしたF0とで、11フレームの軌跡のマスクlogitの差は0。
- SAM2本体の学習可能なパラメータは0個、adapterは570,563個。2回の更新後もSAM2本体の重みのハッシュは不変。
- `model.train()` を呼ぶとSAM2本体のsubmoduleがtrainに戻ることを確認した。学習ループでは毎回evalに戻し、更新ごとにevalのままであることを検査する。

### 高速化の前後比較（`--mode parity`、短い3軌跡、各1回更新）

| 条件 | 1軌跡目のlogit差 | 1軌跡目のloss差 | 勾配の相対差（最大） |
|---|---|---|---|
| FP32：高速化なし同士（再現性の基準） | 0 | 0 | 1.2e-4 |
| FP32：①先読み＋GPUでの正規化＋③待ちの削減 | 0 | 0 | 8.4e-5 |
| FP32：①③＋②まとめ計算 | 5.0e-5 | 3.0e-8 | 4.0e-2 |
| bf16：高速化なし同士 | 0 | 0 | 8.6 |
| bf16：①②③すべて | 0 | 0 | 5.7 |

- 学習のbackwardは、memory-efficient attentionが非決定的なので、同じ条件でも勾配が実行ごとにわずかに変わる（FP32で相対1e-4程度）。2軌跡目以降は更新後の重みが変わるため、forwardもずれていく。
- ①③は、1軌跡目のforwardが完全に一致し、勾配の差も基準と同程度。
- ②（TBPTTの8フレームをまとめて画像エンコーダに通す）は、画像エンコーダの出力が1フレームずつ通した場合と最大9.5e-7（値は最大2.5）異なった。まとめ計算そのものは実行ごとに完全に再現する。原因はバッチの大きさによるGPUの計算方法の違いで、FP32の丸め誤差の範囲と判断した。
- bf16では、高速化ありとなしの差が、高速化なし同士の差と同程度だった。
- 途中で不具合を1つ見つけて直した：GPU上で `div_(255.)` を使うとCUDAが逆数の掛け算に置き換え、CPUの読み込みと1ulpずれていた。tensorで割る形に直し、`mose_fulltrack.load_frame` と全要素一致することを確認した。

### F0の既存結果を再利用できるか（tuningの先頭10動画・26対象）

- 新しい評価スクリプトと旧スクリプトを同じGPU（RTX PRO 4500）で回すと、全対象でJ・F・J&Fが完全に一致した。
- その結果と保存済みのF0（`tuning/F0_step_002789`）を比べると、最大でJ&Fが0.0083ずれた。プロンプトは一致していた。
- 同じ新しいスクリプトをA4000で回すと、途中で止まるまでの6対象で、保存済みのF0と完全に一致した。保存済みのF0はA4000で評価したものと考えられ、ずれの原因はGPU（bf16の計算）の違いである。
- 結論：全条件の評価をA4000で行い、F0は保存済みの結果を再利用する（ユーザーと合意、2026-10-19）。

### 各モードの動作確認（V3、`--no-comet`、ただしpilotはComet送信も確認）

- pilot（2軌跡・3更新）：0回目の診断用lossがF0と一致。2〜3回目の更新でMamba内部・1×1 convに勾配が届き、診断用lossがF0より下がった（0.1428 → 0.1383）。SAM2本体は不変。
- measure（最短9フレーム）：学習時のVRAMのピーク20.9 GiB、0.22秒/フレーム。推論時のピーク2.2 GiB、0.12秒/フレーム。
- V1の学習時のVRAMのピークは4.7 GiB（最短9フレーム）。V1はA4000でも学習できる見込み。
- train（3更新）とresume：checkpoint・manifest・ログが出力され、途中のcheckpointから再開してもログの行数が正しい。SAM2本体は不変。学習時のVRAMのピーク21.9 GiB。
- 評価（A4000、2動画・8対象）：V3とV3-resetが評価でき、集計スクリプトで対象の集合・プロンプト・採点フレーム数の一致を確認したうえで差を出せた（3更新のみの重みなので、数値に意味はない）。
- 2対象を回した時点での速度：V3の学習は約0.12秒/フレーム（pilot）。前回のF1（SAM2全体を学習、高速化なし）は0.30秒/フレーム。

## 段階0b LRの確認

### GPU環境の変化（2026-10-21確認）

- 142のRTX PRO 4500 Blackwell（32GB）が、10/19 19:02の起動以降、`nvidia-smi` にも `lspci` にも出ない。10/19 17:38〜19:02に正常停止と起動を4回繰り返しており、その後A4000の接続位置が `02:00.0` から `82:00.0` に変わっている。最後に正常に使えたのは10/19 17:33ごろ（ラッパーの動作確認）。ユーザーによると、GPUの不調のためしばらく復旧しない。
- 142で使えるGPUはA4000（16GB、今はPCI順で0番）だけ。ラッパーの学習用の既定値（PCI順1番）では起動できないので、`CUDA_VISIBLE_DEVICES=0` を付けて実行する。
- V3の学習はVRAMのピークが約21GiBで、A4000では回らない。V1（約4.7GiB）は回る。
- 10/21に、GPUが見つからずに学習の前に終わったrunのフォルダ（記録ファイルのみ）が計8つでき、すべて削除した。

### V1 pilot（2026-10-21、A4000、SAM2 repo `80610fe`、完了）

条件：`configs/temporal_adapters/pilot_v1.yaml`。F0/F1と同じ並び順の先頭16軌跡を繰り返し200更新、warmup 20更新、その後cosine。診断用lossは同じ16軌跡で、F0（adapterなし）と50更新ごとのadapterを比べた。結果は `runs/temporal_adapters/pilot_v1_lr{1e-4,3e-4,1e-3}/` に保存。

診断用lossのF0との差（F0は0.3982、マイナスほど良い）：

| LR | 50更新 | 100 | 150 | 200（最終） | 残差の比（最大） | 勾配ノルム（最大） | 判定 |
|---|---|---|---|---|---|---|---|
| 1e-4 | +0.0078 | −0.0746 | −0.0760 | −0.0555 | 0.211 | 2.84 | 安定 |
| 3e-4 | −0.0649 | +0.0051 | −0.0572 | −0.0890 | 0.521 | 4.53 | 改善が最大、やや揺れる |
| 1e-3 | +5.8507 | +0.0145 | +0.0329 | −0.0758 | 1.178 | 16.9 | 不安定 |

- 3本とも、初期化直後の診断用lossがF0と完全に一致し、学習後もSAM2本体の重みは変わっていない（`sam2_unchanged: true`）。
- adapterは実際に学習された。前回のF1（αが2e-4以下で残差はほぼ0）と違い、残差が特徴の1〜5割の大きさまで育った。最初の1更新ではMamba内部の勾配は0で（`W_out` のゼロ初期化による想定どおりの挙動）、2更新目から勾配が届き、重みも動いた（200更新後の初期値からの変化は、Mamba部分で1e-4が1.92、3e-4が3.02、1e-3が5.79）。
- 1e-3は50更新目で診断用lossが0.40から6.25に跳ね上がり、残差が特徴より大きくなった（比1.18）。LRが下がった後半で持ち直したが、不安定なので採用しない。
- 1e-4と3e-4は、どちらもspecの条件（lossがF0より下がり、数値が有限で安定）を満たす。3e-4は最終的な改善が最も大きく（−0.089、約22%）、学習lossも最も下がった（最初の50更新の平均0.365 → 最後の50更新の平均0.311。1e-4は0.427 → 0.394）。ただし、100更新目で一時的にF0と同程度に戻っている。
- 速さは約0.116秒/フレーム（1e-4の場合、16,027フレームで約31分）。
- 注意：診断用lossは学習に使った16軌跡そのもので測っている。分かるのは「LRを直せば学習が進む」ことまでで、別の動画への汎化は段階3のtuning評価で見る。

暫定の判断：V1だけなら3e-4。specではV1とV3で同じLRを使うので、V3のpilotの結果を見て確定する（V3で3e-4が不安定なら1e-4）。

### V3 pilot

未実施。A4000（16GB）に収めるために、Mambaの途中計算を逆伝播のときに計算し直す形（activation checkpointing）への対応が必要。

## 段階1 実測

2026-10-22のspec改訂（レビュー反映）で、段階1は「1a V3のメモリの予備計測と段構成の決定」（checkpointingの正しさの確認0cの後）と「1b 速度の実測とNの決定」（共通のLRが決まった後）に分かれた。

### V1の実測（2026-10-22、A4000、SAM2 repo `0edf71b`、完了）

`configs/temporal_adapters/measure_v1.yaml`。fitの軌跡のうち最短・長さが中央・最長について、学習1回分（forward・backward・更新）と推論（評価と同じ経路）を測った。結果は `runs/temporal_adapters/measure_v1/20261022T112529+0900_0edf71b/`。

| 軌跡 | フレーム数 | 学習：VRAMのピーク | 学習：秒/フレーム | 推論：VRAMのピーク | 推論：秒/フレーム |
|---|---|---|---|---|---|
| 最短（`a598602d`/1） | 9 | 4.72 GiB | 0.215 | 0.72 GiB | 0.117 |
| 典型（`c5082b3c`/7） | 55 | 5.79 GiB | 0.126 | 0.91 GiB | 0.126 |
| 最長（`c2e88575`/9） | 500 | 5.79 GiB | 0.116 | 0.91 GiB | 0.139 |

- V1は最長の軌跡でも学習時のピークが5.8 GiBで、A4000（16GB）に余裕で収まる。TBPTTで8フレームごとに区切っているので、軌跡が長くてもピークはほぼ増えない。
- 学習は約0.12秒/フレーム。最短の0.215は、1軌跡ごとの準備（augmentationの決定、先読みの立ち上がりなど）の割合が大きいため。fit全体（200,794フレーム）を1周すると約6.6時間の見込み。
- measureモードの推論は画像の先読みを使っていないので、学習中のvalや評価（先読みあり）より遅めに出ている。
- LRは速度に影響しないので、この結果を段階1bのV1の速度として使う。更新回数Nは、specどおりV3（checkpointingあり）の速度で決める。

### V3

未実施（段階0cの後に1a）。

## 段階2 学習・段階3 評価

未実施。
