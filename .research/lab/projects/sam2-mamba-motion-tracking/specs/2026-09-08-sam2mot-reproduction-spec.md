---
date: 2026-09-08
project: sam2-mamba-motion-tracking
source: brainstorm
status: draft
tags: [spec, experiment, sam2mot, reproduction, ablation, dancetrack]
---

# SAM2MOT再現（DanceTrack val・ablation差分照合）Spec

## 目的

SAM2MOT（AAAI 2026 / arXiv 2504.04519）を自前実装で再現し、論文 Table 3 の component ablation が示す寄与構造を DanceTrack val 25系列で確認する。絶対値の一致は目標としない。各コンポーネント（Object Addition / Cross-object Interaction / Quality Reconstruction）が論文の記述どおりの向きと機構で効くことを確認する。

## 背景

### 公式コードが存在しない

`https://github.com/TripleJoy/SAM2MOT` のルートには `.gitignore` / `LICENSE` / `README.md` / `assets/` のみで、コードは1行も公開されていない（repo作成 2025-04-10、最終push 2025-11-18、182 stars、Apache-2.0、open issues 16件）。README にインストール手順と実行コマンドが記載されているため公開済みに見えるが実体がない。issues はほぼ全てコード公開の催促（#1, #2, #7, #11, #14, #15）と再現時の疑問（#4, #5, #6, #9, #12, #13）である。したがって再現するには自作しかない。

### 既存実装の位置づけ

`/mnt/HDD10TB-2/aburatani/2026_05_aburatani_sam2mot` の `sam2mot_lite/` は論文をもとにAntigravityで生成したもので、2026-06-12以降停止中。Trajectory Manager の構造は論文どおり拾えているが、以下が論文と異なる（詳細は `experiments/2026-09-08-sam2mot-lite-implementation-status.md`）。

| 要素 | 論文 | 既存 sam2mot_lite |
|---|---|---|
| 検出器 | Co-DINO-L / Grounding-DINO-L（COCO事前学習・zero-shot） | GTの`gt.txt`（オラクル） |
| セグメンタ | SAM2.1-large | SAM2.1-tiny（既定） |
| SAM2の使い方 | オブジェクトごとの並列single-object tracker | 単一のbatched multi-object predictor |
| 状態閾値 | τ_r=8.0 / τ_p=6.0 / τ_s=2.0 | reliable 2.0 / pending 0.0 / lost −2.0 |
| スコア定義 | SAM2のnative mask logit | 正のlogitの平均値（独自の暫定値） |
| Cross-object Interaction | 該当フレームのメモリバンク書き込みを除外 | 出力抑制+suspicious降格（既定無効） |

一致していた値: `lost_tolerance=25`、`free_ratio_thr=0.7`、`det_conf_thr=0.5`、`coi_miou_thr=0.8`、`coi_score_gap_thr=2.0`、`coi_var_window=10`。

### 本プロジェクトとの関係

8/28 MTG では「SAM2MOTは再現ではなく途中検出による独自補正の着想として扱う」と整理されている。本specはその方針に対する例外として、再現自体を目的とする作業を明示的に切り出すものである。本線（state carry型Mambaの学習見直し、SAM2デコーダー統合）とは独立に扱う。

## 検証したい問い

Object Addition（+5.0 HOTA）、Cross-object Interaction（+5.9 HOTA / +17.7 MOTA）、Quality Reconstruction（+1.7 HOTA）という論文 Table 3 の寄与構造は、Co-DINO-L + SAM2.1-large の自前実装で DanceTrack val 上に再現できるか。

## 仮説

1. **CoI が最大寄与になる。** その本質はメモリバンク書き込みの除外による誤り伝播の遮断であり、既存実装のような出力抑制では再現しない。MOTA の大幅改善（論文 +17.7）は、誤ったマスクが記憶に残り続けることを止めた結果として説明できる。
2. **CoI は association 系の指標にのみ効く。** IDSW減・AssA増・MOTA増が現れ、DetA はほぼ不変であるはず。DetA が大きく動く場合は実装位置を誤っている。
3. **baseline だけで既に既存手法を上回る。** 論文の baseline は HOTA 62.9（test）で、同一検出器の ByteTrack 56.1 / OC-SORT 56.2（Table 2）を上回る。この差は検出器と SAM2.1-large の寄与であり、追跡ロジックの精緻化より先に効く。

## 実験・実装内容

### 論文のアルゴリズム仕様（実装対象）

**Object Addition**（3段フィルタ）

1. 検出スコアが閾値（Co-DINO-L では 0.5）未満の検出を破棄する
2. 残った高信頼boxとSAM2の追跡boxをHungarian matchingで対応付け、未マッチの検出を新規候補とする
3. 全追跡マスク `M_i` を統合して反転し `M_non = I − ∪M_i` を作る。各候補について検出boxと `M_non` の重なり面積 `p` を求め、`p / area(box) > r`（r = 0.7）なら新規トラックとして初期化する

**Object Removal**（4状態、logit閾値）

```
reliable    : logits > τ_r          (τ_r = 8.0)
pending     : τ_p < logits ≤ τ_r    (τ_p = 6.0)
suspicious  : τ_s < logits ≤ τ_p    (τ_s = 2.0)
lost        : logits ≤ τ_s
```

`lost` 状態が許容フレーム数（25）を超えて continue したら消失とみなし削除する。**`suspicious` は論文が "not explicitly handled in this work but remains open for future extensions" と明記しているため、本再現でも処理を入れない。** 既存実装がここを作り込んでいる場合は論文準拠のため削る。

**Quality Reconstruction**

次の2条件が同時に成立したときのみ発動する。(1) 対象が `pending` 状態、(2) 現在の追跡boxがObject Addition段の高信頼検出boxとマッチしている。このとき、マッチした高信頼boxで対象の keyframe 情報を更新する。

**Cross-object Interaction**

マスク間 mIoU > 0.8 で衝突と判定する（2つのトラッカーが同一オブジェクトを認識している状態）。

- Stage 1: A と B の logit スコアを比較し、Aが有意に高い（2ポイント超）なら B を誤追跡としてフラグする
- Stage 2: スコアが近い場合、過去 N = 10 フレームの信頼度の分散を計算する（`σ²_logits = (1/N)Σ(logits_i − mean)²`）。Aは記憶劣化で緩やかに低下するため分散が小さく、Bは急な遮蔽で急落するため分散が大きい。これにより B を誤追跡と同定する
- 同定後、**B の現フレームのメモリ情報をメモリバンク更新から除外**して誤り伝播を防ぐ。あわせて低信頼エントリのフィルタリングは相対的に低い閾値で維持する

### コードの扱い

**既存 `sam2mot_lite/` のコードは流用しない。** 新規実装とする。

当初は周辺モジュール（`detection.py` 71行、`mask_utils.py` 91行、`matching.py` 52行、`result_writer.py` 30行＝計244行）の流用を検討したが、次の理由で見送る。

1. いずれも1〜2時間で書ける規模であり、流用による短縮効果が小さい
2. Antigravity生成コードへの信頼度が低い（`associate_and_update()` の track index ずれバグ、未参照の死んだフラグ2つが判明済み）。流用するなら中身を検証する必要があり、検証コストが書き直しコストと同程度になる
3. 同一ディレクトリで作業すると、古いREADME・DESIGN.md・破棄予定のbatched wrapperが視界に残り、継ぎ足し方向へ引っ張られる

**再利用するのは環境と知見であり、コードではない。**

| 再利用するもの | 内容 |
|---|---|
| venv | `.venv-sam2mot`（Python 3.12.3 / torch 2.12.0+cu130、SAM2 editable インストール済み） |
| checkpoint | `sam2/checkpoints/` の4サイズ約1.5GB（`sam2.1_hiera_large.pt` を含む） |
| データ構成 | `data/DanceTrack` → `dataset/DanceTrack/standard_format` の symlink |
| 評価環境 | TrackEval側のDanceTrack val設定（gt・`seqinfo.ini`・seqmap・ラッパ） |
| 知見 | `experiments/2026-09-08-sam2mot-lite-implementation-status.md`（回避すべき設計の記録） |
| 代替設計の知見 | `sam2mot_lite/OBJECT_ADDITION.md`（VRAM制約時のfallback候補） |

### 配置

既存リポジトリ `/mnt/HDD10TB-2/aburatani/2026_05_aburatani_sam2mot` 内に新規トップレベルディレクトリ（例 `sam2mot_repro/`）を作成し、そこにゼロから実装する。`sam2/` と checkpoint を共有できるため、別リポジトリを立てるよりSAM2の再インストールと1.5GBの再取得を避けられる。

`sam2mot_lite/` は削除せず**読み取り専用の参考**として残す。ただし継ぎ足しは行わない。

### 新規実装する内容

- per-object 並列トラッカー層（1トラックにつき1つの推論状態）
- SAM2 native logit スコアの取得（既存の「正logit平均」は使わない）
- 4状態遷移（τ_r=8.0 / τ_p=6.0 / τ_s=2.0、tolerance 25、`suspicious` は無処理）
- Object Addition の3段フィルタ
- CoI をメモリバンク書き込み除外として実装
- Quality Reconstruction の発動2条件
- 検出入力は検出ファイル経由のみとし、`gt.txt` を読む経路は作らない（オラクル混入の防止）

### SAM2インスタンス構成の扱い（第一候補と代替）

既存の Dynamic Batch Padding は**設計判断の誤りではなく、SAM2のAPI制約に対する正当な回避策**である。SAM2は `allow_new_object = not inference_state["tracking_has_started"]`（`sam2/sam2/sam2_video_predictor.py:138`）で追跡開始後の新規オブジェクト追加を禁止しており、batched構成で途中追加を行うにはstate操作が避けられない。

またSAM2はbatchedモードでも `output_dict_per_obj[obj_idx]`（同 `:96, :148`）でオブジェクトごとに独立したメモリを保持する。したがって「per-instance と batched」はメモリ意味論の違いではなく、**CoIのメモリ除外はどちらの構成でも実装可能**である。

本specでは per-instance（オブジェクトごとに独立したSAM2インスタンス）を第一候補とする。根拠は下記A1（推定であり論文に明記なし）。VRAM実測で成立しない場合は batched + state操作へ切り替える。その判断はリスク1の判断点で行う。

### 論文未記載事項と実装判断

論文だけでは実装が一意に決まらない箇所がある。各項目について第一候補・根拠・誤りの検出方法を定める。**実装時はこれらをconfigフラグとして切り替え可能にし、差分が論文と合わない場合に疑う対象を特定できるようにする。**

| # | 未記載事項 | 第一候補 | 根拠 | 誤りの検出方法 |
|---|---|---|---|---|
| A1 | SAM2のインスタンス構成（per-instance か batched か） | per-instance（**VRAM面は実測で成立を確認・2026-09-08**） | Limitationの将来課題に "parallel inference across multiple SAM2 instances" が挙がる＝現状は逐次。Related Worksで「独立single-object trackerへの分解」を批判しCoIで補う構成。速度がmain limitation。途中追加が自然に可能 | **実測済み**: 13体101フレームで per-instance 3.26 GiB / 1.18 fps、batched 4.03 GiB / 6.23 fps。per-instanceの方がVRAMは少なく、速度が5.3倍遅い。論文のLimitation記述と整合。詳細は `sam2mot_repro/logs/s1_vram_instance_mode.md` |
| A2 | logitスコアの定義 | **`object_score_logits`（S0.5で確定済み・2026-09-08）** | 実測で確定。閾値2.0/6.0/8.0が分布のp10.4/p42.4/p66.3に散る（他候補は裾に集中）。遮蔽時にpending→suspiciousへ降格。SAM2がmaskごとに公開する正規の信頼度で、placeholder既定値10.0＝存在。詳細は `sam2mot_repro/logs/s0_5_score_distribution.md` | 確定済み。後続段で差分が合わない場合は `mask_logit_posmean`（次点）へ切替可能にする |
| A3 | mask→boxの変換（issue #12） | 全連結成分の外接矩形（union のtight bbox） | Limitationで「可視領域しか覆わない」と明言しており素朴なtight bbox。分裂時の扱いは未記載 | DetAとFPが想定外に動く。代替は最大成分のみ |
| A4 | 第1フレームの初期化 | Object Additionの3段フィルタを通す | 第1フレームは既存トラックがないため `M_non = I` となり r=0.7 判定は自動的に通過する | 第1フレームのtrack数が高信頼検出数と一致するか |
| A5 | Quality Reconstructionの「keyframe更新」の具体操作（issue #4） | 現フレームにbox promptを再投入し conditioning frame として追加 | 論文は "the matched high-confidence box updates the object's keyframe information" とのみ記載 | cond_frame数の増加、pending→reliableの遷移率、VRAM/速度 |
| A6 | CoIのメモリ除外の範囲 | 衝突が検出されたフレームごとに、誤追跡と同定されたB のみ1フレーム単位で除外 | 論文は "its current-frame memory information is excluded from memory bank updates" と記載。継続期間と対象範囲は未記載 | IDSWの減少幅。除外が狭すぎると効果が出ず、広すぎるとトラック消失 |
| A7 | 低信頼エントリのフィルタリング閾値 | τ_s = 2.0 を仮置き | 論文は "adopt a relatively low threshold" とのみ記載し具体値なし | メモリバンクサイズと性能の関係。感度確認が必要 |
| A8 | 検出器の適用条件 | person単一クラス、NMS・score閾値はS0で決定 | DanceTrackは単一クラス。論文に詳細なし | 検出のみのrecall確認 |
| A9 | SAM2のメモリフレーム選択 | SAM2既定（keyframe + 直近6フレーム）を維持し、CoIの除外のみ追加 | 論文はCoIが "jointly optimizes SAM2's memory frame selection strategy" と述べるが、既定からの変更内容は未記載 | CoI段で効果が出ない場合、選択戦略側の変更が必要な可能性 |

### 差分が合わない場合の切り分け対応表

| 症状 | 疑う項目 |
|---|---|
| S1 baselineのHOTAが極端に低い | A2（スコア定義）、A3（mask→box）、A8（検出器設定） |
| Object Additionの寄与が出ない | A4（第1フレーム）、A8（検出器のrecall） |
| CoIの寄与が出ない | A6（除外範囲）、A9（メモリ選択戦略）、A1（インスタンス構成） |
| CoIでDetAが大きく動く | A3（mask→box）、実装位置がassociationでなく検出側 |
| Quality Reconstructionの寄与が出ない | A5（keyframe更新の操作）、A2（pending判定に使うスコア） |
| 状態遷移が機能しない（全てreliableまたは全てlost） | A2（スコア定義の値域が閾値と噛み合っていない） |

### 段階構成

| 段 | 内容 | 論文値（test, Co-DINO-L） |
|---|---|---|
| S0 | Co-DINO-L導入、DanceTrack valの検出ファイル生成 | — |
| S1 | baseline: per-object並列SAM2.1-large、mask→box、Add/CoI/Q-Rなし | HOTA 62.9 / MOTA 55.6 / IDF1 69.6 |
| S2 | + Object Addition | 67.9 / 69.7 / 74.4 |
| S3 | + Cross-object Interaction | 73.8 / 87.4 / 80.9 |
| S4 | + Quality Reconstruction | 75.5 / 89.2 / 83.4 |

論文 Table 3 の Q-R 単独行（Baseline+Add+Q-R = 69.1 / 69.2 / 76.0）も再現可能なら記録し、CoI と Q-R の分離を確認する。

## 使用データ・モデル

- データ: DanceTrack val 25系列（`/mnt/HDD10TB-2/aburatani/dataset/DanceTrack/standard_format/val`）
- セグメンタ: SAM2.1-large。checkpoint は `2026_05_aburatani_sam2mot/sam2/checkpoints/sam2.1_hiera_large.pt` に既存
- 検出器: Co-DINO-L（COCO事前学習、fine-tuningなし、zero-shot適用）。mmdetection経由で導入
- 評価: `/mnt/HDD10TB-2/aburatani/TrackEval`（DanceTrack val用のgt・seqinfo.ini・seqmap・ラッパが既に整備済み）

## 比較対象・ベースライン

1. **論文 Table 3 の ablation 差分構造**（主）: Add +5.0、CoI +5.9（MOTA +17.7）、Q-R +1.7
2. **論文の機構的主張**（主）: CoI は association 精度への寄与
3. **自作実装の S1 baseline**（内部基準）: S2〜S4 はすべて S1 との差で評価する
4. 参考値として本プロジェクト既存の DanceTrack val 25系列結果を並べる。ただしパイプラインと検出器が異なるため同一条件比較ではない（既存値は要確認）

## 評価指標

TrackEval（MOTChallenge プロトコル）で以下を全段階記録する。

- HOTA、MOTA、IDF1（論文が報告している主指標）
- **AssA、DetA**（機構署名の判定に必須。CoI は AssA に効き DetA は不変であるべき）
- **IDSW**（CoI の誤り伝播抑制が効いているかの直接指標）
- FN、FP（MOTA の内訳確認用）

系列別の値も保存し、COMBINED_SEQ だけで判断しない。

## 成功/失敗の判断基準

### 主基準（split差に強い）

1. **符号と順序**: Add の寄与 > 0、CoI の HOTA 寄与 > Add の寄与、Q-R が最小
2. **機構署名**: CoI で IDSW減・AssA増・MOTA増が現れ、DetA はほぼ不変

### 参考基準（弱い）

3. 差分の桁が論文（+5.0 / +5.9 / +1.7）と同程度に収まる

絶対値の一致は判定に用いない。**論文は DanceTrack について test set の値しか報告しておらず（Table 1・2・3すべて test）、val の比較相手が存在しない。** val と test は系列も難易度も異なるため、正しく再現できていても val の絶対値は 75.5 にならない。

### test 追加の発動条件

以下のいずれかが観測された場合、val だけでは「実装ミス」と「split差」を切り分けられないため、DanceTrack test への提出で確定させる。

| 条件 | 疑う対象 |
|---|---|
| 符号か順序が論文と食い違う（CoIの寄与がAddを下回る、Q-Rが最大になる等） | 実装位置の誤り。特にCoIがメモリバンク書き込み除外になっていない可能性 |
| CoIでDetAが大きく動く、またはIDSWが減らない | CoIがassociationではなく検出側に作用している |
| S1 baseline の val HOTA が 50 を大きく下回る | 検出器の設定（クラス指定・NMS・スコア閾値）またはSAM2設定 |
| 差分の桁が論文と2倍以上ずれる | ハイパーパラメータまたはスコア定義 |

## 実施手順

### S0: 検出器の導入と検出ファイル生成

1. mmdetection環境を**別venvで**構築する。既存 `.venv-sam2mot`（Python 3.12.3 / torch 2.12.0+cu130）とmmcvの版固定は両立しない前提で分離する
2. Co-DINO-L のCOCO事前学習重みを取得する
3. DanceTrack val 25系列に zero-shot 適用し、person クラスの検出を MOT 形式ファイルへ書き出す
4. クラス指定・NMS設定・スコア閾値の決定内容を記録する（論文に詳細記載がないため、再現条件として明示が必要）
5. 検出のみの品質を確認する（可視化と、GTに対する粗いrecall確認）

### S0.5: logitスコア定義の実測（A2の確定）

論文の状態閾値 τ_r=8.0 / τ_p=6.0 / τ_s=2.0 は、SAM2のどのスコアを指すかが確定しないと意味を持たない。**S1の前に必ず実施する。**

1. SAM2.1-largeでDanceTrack val の数系列を素朴に追跡し、候補となるスコアを同時に記録する（`object_score_logits`、mask logitsの最大値・平均値・正値平均）
2. 各候補の分布（分位点、遮蔽時と非遮蔽時の差）を出す
3. 8.0 / 6.0 / 2.0 が「reliable / pending / suspicious / lost」を意味のある比率で切り分ける候補を選ぶ
4. 選択結果と分布を記録する。ここを誤ると以降の全段階が無意味になる

**実施済み（2026-09-08）**: `object_score_logits` を採用。dancetrack0026 / 0043 / 0079 の
3系列・785フレーム・8269レコードで実測（GPU peak 6.00 GiB）。判定基準は「reliable比率が
支配的か」ではなく、閾値配置（C1）・遮蔽応答（C2）・SAM2の意味論（C3）を用いた。
結果は `sam2mot_repro/logs/s0_5_score_distribution.md`、生データは同 `logs/s0_5_score_records.csv`。

### S1: baseline実装

1. per-object 並列 SAM2.1-large トラッカー層を実装する。1トラックにつき1つの推論状態を持つ
2. SAM2 の native mask logit スコアを取得する経路を作る（既存の「正logit平均」は使わない）
3. 第1フレームの検出を box prompt として全トラックを初期化し、mask→box で MOT 形式へ出力する
4. **先に1系列で VRAM 実測を取る**（判断点。下記リスク参照）
5. val 25系列を推論し TrackEval で評価する

### S2: Object Addition追加

1. 3段フィルタ（conf 0.5 → Hungarian → `M_non` 重なり比 r=0.7）を実装する
2. Object Removal の4状態遷移（τ_r=8.0 / τ_p=6.0 / τ_s=2.0、tolerance 25）を実装する。`suspicious` は無処理
3. val 25系列を再評価し、S1との差分を記録する

### S3: Cross-object Interaction追加

1. mIoU>0.8 の衝突検出、Stage 1（logit差2）、Stage 2（分散 N=10）を実装する
2. 同定されたトラックの現フレームメモリを**メモリバンク更新から除外**する
3. val 25系列を再評価し、S2との差分と機構署名（IDSW / AssA / DetA）を記録する

### S4: Quality Reconstruction追加

1. pending状態かつ高信頼検出とマッチした場合の keyframe 更新を実装する
2. val 25系列を再評価し、S3との差分を記録する
3. 全段階の差分表を作り、成功基準に照らして判定する

## 期待される結果

論文の寄与構造が val 上でも保たれ、CoI が最大寄与かつ association 系指標に限定して効くことが確認される。絶対値は論文 test より低く出る見込みだが、S1 の時点で既に既存の detection-association 系手法を上回る水準（論文 test では 62.9）に達すると期待する。

## リスク・懸念

1. **VRAM リスクは実測で解消（2026-09-08）。真のコストは速度。** `dancetrack0026`（13体・101フレーム）で計測した結果、per-instance は peak **3.26 GiB**、batched は **4.03 GiB** で、**per-instance の方がVRAMが少ない**（batchedは全オブジェクトを1回のforwardでまとめるため活性化が大きい）。val最大の19体へ外挿しても約4.8 GiBで、GPU 31.4 GiB に十分収まる。したがって「VRAMに収まらないためbatchedへ妥協する」分岐は不要と判断する。

   代わりに顕在化したのは**速度**で、per-instance は **1.18 fps（batched 6.23 fps の1/5.3）**、forward回数が13倍になる。これは論文がLimitationに推論速度を挙げ、将来課題に "parallel inference across multiple SAM2 instances" を置いていることと整合する。

   **改善余地**: `cached_features`（画像エンコーダ出力）を state 間で共有すれば、最も重い backbone を1回に減らせる。上記計測は共有なしの値。S1実装時にこの共有を入れるかを判断する。

   なお外挿は frame 1 のオブジェクト数に基づく。途中出現を含めると同時追跡数は増えるため、全系列での再確認は S1 で行う
2. **mmdet環境。** mmcv はバージョン固定が厳しい。検出は別venvで事前生成し検出ファイル経由で受け渡す設計にして、SAM2側の環境と分離する
3. **論文に記載のない詳細がある。** issue #4（occlusion / quality reconstruction のロジック）、#5（prompt）、#12（box reconstruction）が示すとおり、論文だけでは一意に決まらない箇所がある。実装判断はすべて記録し、再現差の要因として扱う
4. **工数競合。** 現在の優先順位はP4a実装監査、内部stateログ診断、View原稿（9/11締切）、SAM2デコーダー統合（10月中旬目標）。本specは本線と独立に扱い、着手時期は別途判断する
5. **論文のLimitationが再現にも現れる。** 論文は「mask由来のboxは可視領域しか覆わないため MOTChallenge 系で不利（Holistic Object Modeling の欠如）」と「long-term memory の弱さ」を挙げている。DanceTrackでは影響が小さいが、指標の解釈時に留意する

## 未決事項

- Co-DINO-L の DanceTrack への適用条件（クラス指定、NMS、スコア閾値）は論文に詳細がなく、S0 で決定して記録する必要がある
- per-object 並列がVRAMに収まるかは S1 の実測待ち。収まらない場合の妥協設計を採るかは実測後に判断する
- 本プロジェクト既存の DanceTrack val 参考値を並べるか。並べる場合、検出器とパイプラインが異なる旨の注記が必須
- 着手時期。View原稿（9/11）とSAM2デコーダー統合（10月中旬）との兼ね合いで未定
- Grounding-DINO-L（論文最高値 HOTA 75.8）を後段で追加するか。text promptの設定が再現の追加変数になる（issue #5）

## 関連brainstorm

- `.research/secretary/notes/brainstorm/2026-09-08-sam2mot-reimplementation-vs-official.md`（前提の訂正を含む追記あり）
- `.research/lab/projects/sam2-mamba-motion-tracking/experiments/2026-09-08-sam2mot-lite-implementation-status.md`
