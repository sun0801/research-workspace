---
date: 2026-09-08
project: sam2-mamba-motion-tracking
source_todo: null
topic: SAM2MOT-liteを作り直すか改善するかの判断
status: exploratory
tags: [brainstorm, sam2mot, reimplementation, baseline, priority]
---

# SAM2MOT-liteを作り直すか改善するかの判断

## 読み込んだ文脈

- `.research/lab/projects/sam2-mamba-motion-tracking/README.md`
- `.research/lab/projects/sam2-mamba-motion-tracking/experiments/2026-09-08-sam2mot-lite-implementation-status.md`（本日の棚卸し）
- `.research/secretary/notes/brainstorm/2026-09-08-next-priority-after-0904-mtg.md`
- `.research/secretary/todos/2026-09-08.md`
- SAM2MOT論文本体（arXiv 2504.04519 / AAAI 2026）のMethod・Experiments・Ablationを直読

## 相談の出発点

sam2mot_liteは論文をもとに過去Antigravityに作らせたもの。これを論文と同じ構成・同程度の精度まで改善したい。1から作り直すか、既存を改善するか。

## 中心となる問い

論文同等の構成・精度に到達する手段として、自作実装の改修・再実装・公式コード利用のどれが妥当か。そもそも本研究にとってその到達は必要か。

## 決定的な事実

1. **公式コードが存在する。** SAM2MOTはAAAI 2026採択で、`https://github.com/TripleJoy/SAM2MOT` に実装がある。「論文と同じ構成・精度」が目的なら再実装は不要。
2. **精度差の主因は追跡ロジックではなく外側の要素。** 論文のDanceTrack testはHOTA 75.5（Co-DINO-L）／75.8（Grounding-DINO-L）で、従来best MOTIP 73.7に対し+2.1。この数値は強力な検出器とSAM2.1-largeに強く依存する。
3. **論文の最重要コンポーネントは現実装で無効かつ別機構。** Component Ablationは「Cross-object Interactionがassociation精度に最も寄与」と明記。現実装は既定OFFで、機構も出力抑制止まり。

## 論文構成と現実装の差分

| 要素 | 論文 | 現 sam2mot_lite |
|---|---|---|
| 検出器 | Co-DINO-L / Grounding-DINO-L（COCO事前学習・zero-shot・fine-tuningなし） | GTの`gt.txt`をそのまま（オラクル） |
| セグメンタ | SAM2.1-large | SAM2.1-tiny（既定） |
| SAM2の使い方 | オブジェクトごとの並列single-object tracker | 単一のbatched multi-object predictor |
| 状態閾値 | τ_r=8.0 / τ_p=6.0 / τ_s=2.0 | reliable 2.0 / pending 0.0 / lost −2.0 |
| スコア定義 | SAM2のnative mask logit | 正のlogitの平均値（独自の暫定値、実測0.42〜19.44） |
| Cross-object Interaction | mIoU>0.8 → logit差2 → 分散N=10 → 該当フレームのメモリバンク書き込みを除外 | 実装ありだが既定無効、出力抑制+suspicious降格でメモリバンクは不変 |
| Quality Reconstruction | pending状態 かつ 高信頼検出とマッチ → keyframe更新 | 実装あり（構造は一致） |
| Object Addition | 3段フィルタ（conf 0.5 → Hungarian → 未占有領域比 r=0.7） | 実装あり（構造・r値ともに一致） |

一致している値: `lost_tolerance=25`、`free_ratio_thr=0.7`、`det_conf_thr=0.5`、`coi_miou_thr=0.8`、`coi_score_gap_thr=2.0`、`coi_var_window=10`。Trajectory Managerの**構造**は論文どおり拾えている。

### Dynamic Batch Paddingの位置づけ

論文はper-object並列トラッカーなので、途中でオブジェクトが増えてもバッチ次元の不整合が起きない。`inference_state`を遡って書き換えるあの実装は、「単一batched predictor」という論文と異なる設計を選んだ帰結である。

ただし単純な劣化ではない。`OBJECT_ADDITION.md`が並列実行をVRAM OOMで非推奨と判定してbatchedを選んだのはVRAM上は合理的で、論文自身もLimitationに推論速度を挙げている。現実装は「論文より省メモリだが、SAM2内部依存で脆い別アーキテクチャ」と理解するのが正確。

## 収束した方向性

**再実装はしない。** 3つの目的候補（修論の比較ベースライン／途中検出補正の土台／論文主張の検証）のいずれでも、公式コードを動かすほうが短く確実。自作実装で精度を出しても、論文に書く際には「再実装の妥当性証明」という別の負債が生じる。

**ただし今は着手しない。** 9/8 TODOはP4a実装監査（9/9期限）、内部stateログ診断（9/10期限）、View原稿（9/11締切）で埋まっており、SAM2デコーダー統合が10月中旬目標。公式コードの環境構築（mmdet系＋Co-DINO/Grounding-DINO重み、公式は検出結果ファイルを配布していない）は数週間規模の迂回になる。8/28 MTGも「再現ではなく着想として扱う」と決めている。

**二択で答えるなら部分書き直し。** 周辺（`detection.py`/`mask_utils.py`/`matching.py`/`result_writer.py`、約250行）は流用可、追跡コア（SAM2統合層・スコア定義と状態閾値・CoI、約700行）は書き直し。段階的パッチが不利なのは、`sam2_wrapper.py`のpadding機構がbatched設計に強く結合しており、論文構成へ寄せると捨てる前提のコードを保守し続けることになるため。

## 目的別の分岐（未決）

| 目的 | 最短手段 | sam2mot_liteの扱い |
|---|---|---|
| 修論の比較ベースライン | 公式コードを動かし引用可能な数値を得る | 使わない（棚卸し記録のみ残す） |
| 途中検出補正の土台 | 論文同等精度は不要。検出入力をGT→detectorへ戻し最小構成で改造 | M5/M7だけ残して簡素化 |
| 論文主張の検証 | 公式コードをbaselineにCoIのablationを追試 | 使わない |

## 未解決の問い

- 論文同等精度を目指す目的が未確定（本人が保留）。目的により最適解が変わる。
- 公式コードのライセンスと、SAM2.1-large＋Co-DINO-Lを研究室GPUで回せるかのVRAM見積りが未確認。
- 仮に比較ベースラインとして使う場合、DanceTrack **test**（論文値）と本プロジェクトが使う **val 25系列** の差をどう扱うか。論文値75.8はtest、既存の`my_sam2_model` HOTA 51.269はval。直接比較不可。
- 途中検出補正の着想を取り込むだけなら、SAM2MOT実装そのものは不要で、SAM2/SAMURAI側（`2025_03_aburatani_sam2`）へ直接実装する選択肢もある。こちらのほうが本線に近い。

## 次アクション候補

以下は候補であり、TODOへの自動追加はしない。

1. 目的を決める（比較ベースライン／補正の土台／論文検証）。決まるまで着手しない。
2. 公式コードのライセンスとVRAM要件だけ先に確認する（軽量・30分程度）。
3. 途中検出補正を`2025_03_aburatani_sam2`側へ直接実装する案を、SAM2MOT再現とは別に比較検討する。
4. 次回MTGで「SAM2MOT再現に工数を割く価値があるか」を先生に確認する。

## Spec化候補

現時点ではspec化しない。目的が未確定で、成功基準（どの数値にどこまで近づけば成功か）とベースライン（testかvalか）が定義できないため、Spec Gateを満たさない。

## 関連ファイル

- `.research/lab/projects/sam2-mamba-motion-tracking/experiments/2026-09-08-sam2mot-lite-implementation-status.md`
- `.research/lab/projects/sam2-mamba-motion-tracking/README.md`（実装コードの場所 → SAM2MOT-lite節）
- リポジトリ: `/mnt/HDD10TB-2/aburatani/2026_05_aburatani_sam2mot`
- 論文: arXiv 2504.04519 / AAAI 2026、公式実装 `https://github.com/TripleJoy/SAM2MOT`

---

## 追記 21:33（前提の訂正）

### 訂正：公式コードは公開されていない

上記「決定的な事実1」は**誤り**。GitHub API で確認したところ、`TripleJoy/SAM2MOT` のルートには `.gitignore` / `LICENSE` / `README.md` / `assets/` **のみで、コードは1行も存在しない**（repo作成 2025-04-10、最終push 2025-11-18、182 stars、Apache-2.0）。READMEにインストール手順と実行コマンドが書かれているため公開済みに見えるが、実体がない。

open issues 16件はほぼ全てコード公開の催促と再現時の疑問である。

- #1 Code Release（2025-04-12）、#2 Release on Hugging Face、#7 代码开源、#11 Code Release Timeline、#14 When the code be available?（2025-11-12）、#15 开源（2026-02-26）
- 再現時の詰まり: #4 Clarification of occlusion and quality reconstruction logic、#5 关于prompt、#6 Questions about the code reproduction、#9 Question about the implement、#12 Box Reconstruction Details、#13 Question regarding Vram or video length

**したがって「公式コードを動かす」選択肢は存在せず、再現するなら自作するしかない。** ユーザーの意向も再現である。

### 方針：追跡コアは書き直し、周辺は流用

- 流用（約250行）: `detection.py` / `mask_utils.py` / `matching.py` / `result_writer.py`。出力はTrackEval要件を既に満たす
- 書き直し（約700行）: SAM2統合層（batched+padding → per-object並列）、スコア定義、状態閾値、CoI（メモリバンク書き込みレベルへ）

段階的パッチが不利な理由は3点。

1. 論文はper-object並列トラッカー。既存のbatched+padding設計を残すと、捨てる前提のコードを保守し続ける
2. スコア定義が違う（正logit平均 vs native logit）ため、論文の閾値 8.0/6.0/2.0 を移植できない。定義修正は`sam2_wrapper.py`の中
3. CoIはメモリバンク書き込み除外が本質。既存実装は出力抑制で、挿入位置が異なる。パラメータ変更では届かない

### Ablation表が再現の検証チェックポイントになる（最大の収穫）

Table 3（DanceTrack **test**）。各段が公表値との照合点になる。

| Baseline | Add | CoI | Q-R | HOTA | MOTA | IDF1 |
|---|---|---|---|---|---|---|
| ✓ | | | | 62.9 | 55.6 | 69.6 |
| ✓ | ✓ | | | 67.9 | 69.7 | 74.4 |
| ✓ | ✓ | | ✓ | 69.1 | 69.2 | 76.0 |
| ✓ | ✓ | ✓ | | 73.8 | 87.4 | 80.9 |
| ✓ | ✓ | ✓ | ✓ | **75.5** | **89.2** | **83.4** |

（Co-DINO-L。Grounding-DINO-Lは 60.9 → 67.4 → 69.0 → 73.6 → **75.8**）

寄与の内訳: Object Addition +5.0 HOTA、Cross-object Interaction **+5.9 HOTA / +17.7 MOTA**（最大）、Quality Reconstruction +1.7 HOTA。**baselineだけで既にHOTA 62.9** であり、これは検出器とSAM2.1-largeの寄与。同一検出器のByteTrack 56.1 / OC-SORT 56.2（Table 2）を上回る。

### 再現の実務的な壁

- **検出器の導入が最大工数。** Co-DINO-L（mmdet）またはGrounding-DINO-Lをzero-shotでDanceTrackに適用し検出ファイルを生成する必要がある。公式は検出結果を配布していない
- **論文値はtest set。** 本プロジェクトのTrackEval導線はval 25系列。testはevaluation server提出が必要で、val値は75.5と一致しない。照合対象をどう定義するかを先に決める必要がある
- **論文が明示的に未実装と述べている部分がある。** 4状態のうち`suspicious`は「this case is not explicitly handled in this work but remains open for future extensions」。既存実装はここを作り込んでいる可能性があり、論文準拠なら逆に削る判断になる
- **VRAM。** per-object並列 × SAM2.1-large × DanceTrackの多人数は重い。論文自身がLimitationに推論速度を挙げ、issue #13 も同じ懸念。既存のbatched+padding設計はこの点では有利だった
- **論文に書かれていない詳細がある。** issue #4/#5/#12 が示すとおり、box reconstruction、prompt処理、quality reconstructionのロジックは論文だけでは一意に決まらない

### 未解決の問い（更新）

- 照合対象をDanceTrack testにするか、valで自己一貫した相対比較に留めるか
- 検出器はCo-DINO-LとGrounding-DINO-Lのどちらを主にするか（論文はCo-DINO-LがHOTA 75.5、Grounding-DINO-Lが75.8）
- per-object並列がVRAMに収まるか。収まらない場合、batched設計を維持したまま論文構成に寄せる妥協が必要になる
- この再現に割く工数と、View原稿（9/11締切）・SAM2デコーダー統合（10月中旬目標）の両立
