# Validation 実装と運用方針の相談

作成日: 2026-07-09
対象プロジェクト: sam2-mamba-motion-tracking
目的: val / tracking-val 実装の現状共有と、今後の運用方針の相談

## 0. 今日のMTGで先生に相談したいこと

1. validation 実装自体は通ったので、今後は `val loss` と `tracking-val(HOTA等)` を分けて運用する方針で良いか。
2. stateful tracker では full official val の tracking-val が重いため、開発中は部分val、節目だけ full val にする運用で良いか。
3. 当面は refactor を入れず、既存 TrackEval 呼び出しをそのまま組み込む実装で進めて良いか。

## 1. 現時点の結論・見立て

- `train` と `val loss` は同時に回る状態まで実装・確認済み。
- `tracking-val` も TrackEval 連携込みで一連の動作確認済み。
- ただし stateful tracker の full official val は 1 回あたりかなり重く、頻繁実行には向かない。
- そのため、日常開発では軽い指標監視と部分的な tracking-val、最終比較では full val という二段構えが実務上よさそう。

## 2. 背景

- もともと「本来の意味の val を実装する」がタスクだった。
- ここでの `val` は、単なる学習ループ内の loss 監視だけでなく、必要に応じて HOTA などの tracking 指標も確認できる状態を指す。
- 既存では HOTA 等を `/mnt/HDD10TB-2/aburatani/TrackEval` を用いた別導線で算出していたため、学習中の validation にどう統合するかを整理した。
- 相談の結果、まずは大きな整理や抽象化は入れず、既存導線をそのまま組み込む方針にした。

## 3. Evidence: 根拠・結果

### 3.1 設計メモと計画

- brainstorm メモを作成:
  - `.research/secretary/notes/brainstorm/2026-07-07-val-implementation-direction.md`
- validation 実装 spec を作成:
  - `.research/lab/projects/sam2-mamba-motion-tracking/specs/2026-07-07-validation-implementation-spec.md`
- 実装 plan を分離して作成:
  - `.research/lab/projects/sam2-mamba-motion-tracking/plans/2026-07-07-validation-implementation-plan.md`

### 3.2 実装内容

外部実装リポジトリ `/mnt/HDD10TB-2/aburatani/2025_09_aburatani_Mamba_Trackers` 側で以下を追加・更新した。

- `tools/gen_traj_data.py`
  - `--split` を追加し、train/val の軌跡アノテーションを分けて生成可能にした。
- config 群
  - `ssm_tracker/cfgs/MambaTrack.yaml`
  - `ssm_tracker/cfgs/TrackSSM.yaml`
  - `ssm_tracker/cfgs/MambaStateful.yaml`
  - `train_anno_path` / `val_anno_path` と `validation` ブロックを追加した。
- validation 用 utility
  - `ssm_tracker/train_utils/validation.py`
  - `ssm_tracker/train_utils/tracking_validation.py`
- 学習・追跡エントリポイント
  - `ssm_tracker/train.py`
  - `ssm_tracker/train_stateful.py`
  - `ssm_tracker/track.py`
  - `ssm_tracker/track_stateful.py`

### 3.3 現在の挙動

- 毎 epoch:
  - val dataloader があれば `val loss` を計算する。
- `tracking_val_period` ごと:
  - checkpoint から tracker 推論を走らせる。
  - 推論結果を TrackEval に流し、HOTA / MOTA / IDF1 などを集計する。
- best checkpoint:
  - `best_val_loss.pth`
  - `best_tracking_hota.pth`
  を別々に保存する。

### 3.4 動作確認

#### train + val loss

- tiny annotation を作成して smoke test を実施した。
- 1 epoch 完走し、`Validation loss at epoch 1: 0.1321131719` を確認した。
- `best_val_loss.pth` も保存された。

言えること:
- 学習と val loss は同時に通る。
- 以前の「train だけ回る」状態から、「毎 epoch の val loss 監視あり」に進んだ。

#### tracking-val

- 1 sequence の tiny validation で end-to-end 動作確認を実施した。
- checkpoint -> `track_stateful.py` -> TrackEval -> summary parse まで通った。
- 取得できた例:
  - HOTA: 4.7207
  - DetA: 66.867
  - AssA: 0.33545
  - MOTA: 54.383
  - IDF1: 0.47542

言えること:
- HOTA 等の tracking 指標は、学習側 validation 導線に組み込めている。
- 既存 TrackEval 導線を大きく崩さず再利用できている。

### 3.5 full official val の計算コスト

- stateful tracker で full official val の timing を途中まで計測した。
- 約 233.67 秒でまだ tracker 推論中で、25 sequence 中 2 sequence 分しか出力されていなかった。
- このペースから単純推定すると、1 回の full tracking-val はおよそ 48-50 分程度かかる見込み。

言えること:
- 実装可能性は確認できた。
- ただし毎回 full val を回す運用はかなり重い。

## 4. Interpretation: 解釈

- `val loss` と `tracking-val` は役割が異なるので、分けて持つ意味がある。
- `val loss` は毎 epoch でも比較的軽く、学習の安定性や過学習傾向の監視に向く。
- `tracking-val` は本当に欲しい評価だが、stateful では計算コストが高く、開発サイクルを遅くしやすい。
- したがって、運用上は
  - 軽い頻度で `val loss`
  - 間引いた頻度で `tracking-val`
  - 最終比較で full val
 という分離が自然。

## 5. 今回言えること / まだ言えないこと

### 今回言えること

- validation 実装は少なくとも smoke test レベルでは成立している。
- TrackEval 連携も成立している。
- `train` と `val` を同時に回す導線はできている。
- `tracking_val_period` を使った periodic な tracking 評価もできる。

### まだ言えないこと

- full official val を毎回回したときの実運用上の負荷が妥当か。
- full val を含む長時間学習を最後まで完走させた際の安定性。
- `val loss` と HOTA の相関がどれくらいあるか。
- TrackSSM / MambaTrack / MambaStateful で同じ validation 設計が十分比較可能か。

## 6. 方針候補・比較

### 案A: 現状のまま進める

- 実装済みの構成をそのまま使う。
- 日常開発では `val loss` を毎 epoch、`tracking-val` は疎に回す。
- 必要時のみ full official val を使う。

メリット:
- すぐ使える。
- 追加リファクタなしで比較実験に進める。

デメリット:
- validation 周りの責務分離はまだ粗い。
- full tracking-val の重さは残る。

### 案B: 部分val運用を正式化する

- full val とは別に、固定 subset の lightweight tracking-val を公式に持つ。
- 開発中は subset、レポート前のみ full val にする。

メリット:
- iteration が速い。
- HOTA 系も早めに傾向確認できる。

デメリット:
- subset と full val のズレを管理する必要がある。

### 案C: validation 周りをさらに整理する

- evaluator / dataset split / metrics collection をより明示的に整理する。

メリット:
- 今後の保守性は上がる。
- 実験追加時の見通しが良くなる。

デメリット:
- 今このタイミングでは実験開始が遅れる。
- まず結果を出す段階としては優先度が低い可能性がある。

## 7. 次に進む候補

1. まずは `CUDA_VISIBLE_DEVICES=1 bash experiments/train_ssm_tracker.sh` で TrackSSM の実運用を流し、学習 + val loss + periodic tracking-val の実挙動を確認する。
2. stateful 系については、開発用の lightweight tracking-val subset を切るかを決める。
3. full official val は、checkpoint 選別の節目だけ回す方針にするか相談する。
4. 必要なら `val loss` を無効化して `train + tracking-val only` に寄せる設定フラグを後から追加する。

## 8. 参照ファイル

- 前回MTG:
  - `.research/lab/projects/sam2-mamba-motion-tracking/meetings/2026-07-02-mtg.md`
- brainstorm:
  - `.research/secretary/notes/brainstorm/2026-07-07-val-implementation-direction.md`
- spec:
  - `.research/lab/projects/sam2-mamba-motion-tracking/specs/2026-07-07-validation-implementation-spec.md`
- plan:
  - `.research/lab/projects/sam2-mamba-motion-tracking/plans/2026-07-07-validation-implementation-plan.md`
