---
date: 2026-10-09
project: sam2-mamba-motion-tracking
status: completed
tags: [experiment, sam2mot, reproduction, test, dancetrack, codabench, submission]
---

# SAM2MOT再現 test: DanceTrack test 35系列で S1〜S4 を実行し、提出用ファイルを作成

## 目的

spec「test 追加の発動条件」のうち「符号か順序が論文と食い違う」が S3 の時点で成立したため、DanceTrack test で全段（S1〜S4）を回し、論文 Table 3（test の値）と直接比べられるようにする。test は GT が公開されていないため、評価は CodaBench への提出で行う。

## 実験条件

| 項目 | 値 |
|---|---|
| データ | DanceTrack test 35系列（test1 20 + test2 15） |
| 検出 | Co-DINO-L 3x_coco（val と同一設定）。35/35 系列、2026-10-06 生成 |
| 段の設定 | S1: baseline / S2: + Object Addition / S3: + CoI（A6 のみ、A7 無効） / S4: + Q-R（**補正方式**、`--qr-as-refinement`） |
| GPU | GPU 0（val の S1〜S4 と同じ GPU。GPU 1 では出力が一致しないため揃えた） |
| メモリ | `--offload-state-to-cpu`（val で出力の md5 一致を確認）、VRAM 上限 8〜16 GiB |
| コード | 実装リポジトリ `cb6ad0e`（全段共通、作業ツリー clean） |
| 実行ログ | 実装リポジトリ `sam2mot_repro/logs/test_s1_s4.md` |

S4 の Q-R は、spec A5 の第一候補（conditioning frame として追加）ではなく、val の切り分けで最良だった補正方式を使った（`experiments/2026-10-03-sam2mot-s4-qr-results.md` の 2026-10-08 追記）。

## 結果

| 段 | 成功 | 形式検証 | 所要 | 生成トラック（途中追加） | 出力行 | Q-R 発動 |
|---|---|---|---|---|---|---|
| S1 | 35/35 | PASS | 3.48 h | 223（0） | 234,304 | — |
| S2 | 35/35 | PASS | 5.73 h | 474（251） | 360,734 | — |
| S3 | 35/35 | PASS | 5.23 h | 455（232） | 312,204 | — |
| S4 | 35/35 | PASS | 5.55 h | 441（218） | 311,128 | 32,875 |

S2〜S4 は GPU 0 で並行実行した。並行実行は計算資源の取り合いで所要時間を延ばすが、出力の数値は変えない。

## 提出用ファイル

| 段 | ファイル |
|---|---|
| S1 | `/mnt/HDD10TB-2/aburatani/2026_05_aburatani_sam2mot/results/submissions/test_s1/tracker.zip` |
| S2 | `/mnt/HDD10TB-2/aburatani/2026_05_aburatani_sam2mot/results/submissions/test_s2/tracker.zip` |
| S3 | `/mnt/HDD10TB-2/aburatani/2026_05_aburatani_sam2mot/results/submissions/test_s3/tracker.zip` |
| S4 | `/mnt/HDD10TB-2/aburatani/2026_05_aburatani_sam2mot/results/submissions/test_s4/tracker.zip` |

- 提出先: CodaBench（<https://www.codabench.org/competitions/14885/#/participate-tab>）
- 形式: zip 直下に `tracker/` フォルダがあり、その中に `dancetrack00xx.txt` が 35 ファイル（DanceTrack 公式の指示「tracker フォルダごと zip にする、フォルダ名は tracker」に合わせた）

## 比較の予定（提出後）

| 段 | 論文 test（HOTA / MOTA / IDF1） | 本再現 val（HOTA） |
|---|---|---|
| S1 baseline | 62.9 / 55.6 / 69.6 | 59.21 |
| S2 + Add | 67.9 / 69.7 / 74.4 | 64.32 |
| S3 + CoI | 73.8 / 87.4 / 80.9 | 68.22 |
| S4 + Q-R | 75.5 / 89.2 / 83.4 | 69.25（補正方式） |

提出結果が返ったら、この表に本再現 test の値を加え、spec の成功基準（符号と順序、差分の桁）を test で判定する。val で残っている食い違い（CoI の寄与 +3.90 が Add の +5.11 を下回る）が test でも出るかが主な確認点。

## 次

- S1 の `tracker.zip` を提出する（CodaBench の提出上限が1日3件のため、2026-10-10 以降）

## 提出結果（2026-10-09、ユーザーが CodaBench に提出）

CodaBench の提出上限が1日3件のため、初日は S2〜S4 を提出した。表の Score は CodaBench の一覧の値で、詳細画面で HOTA と確認した。

| 段 | Submission ID | 提出時刻 | Score（本再現 test） | 論文 test HOTA | 差 |
|---|---|---|---|---|---|
| S2 + Add | 970256 | 2026-10-09 06:49 | 65.60 | 67.9 | −2.3 |
| S3 + CoI | 970264 | 2026-10-09 06:54 | 69.20 | 73.8 | −4.6 |
| S4 + Q-R（補正方式） | 970291 | 2026-10-09 07:17 | 70.60 | 75.5 | −4.9 |
| S1 baseline | 未提出 | — | — | 62.9 | — |

| 寄与 | 本再現 test | 本再現 val | 論文 test |
|---|---|---|---|
| CoI（S3−S2） | +3.60 | +3.90 | +5.9 |
| Q-R（S4−S3） | +1.40 | +1.03 | +1.7 |
| Add（S2−S1） | 未確定（S1 未提出） | +5.11 | +5.0 |

### 解釈（暫定）

- CoI と Q-R は、test でも論文と同じ向きに効いた。寄与の大きさは val と test でよくそろっている（CoI +3.60 / +3.90、Q-R +1.40 / +1.03）
- **CoI の寄与が論文より小さいことは、test でも同じだった**（+3.60 と +5.9）。val だけの現象（split の差）ではなく、実装側の差である可能性が高い。候補は A6（除外範囲）と A9（論文が CoI について述べる "memory frame selection strategy" の未実装）
- 絶対値は全段で論文より 2〜5 ポイント低く、段が進むほど差が開く（S2 −2.3 → S4 −4.9）。開き方は CoI の寄与の不足（−2.3）でほぼ説明できる
- Add の寄与と、CoI との大小（spec の順序基準）は、S1 の提出後に判定する

### 詳細指標（CodaBench の詳細画面、2026-10-09 ユーザー確認）

| 段 | HOTA | DetA | AssA | MOTA | IDF1 |
|---|---|---|---|---|---|
| S2 + Add | 65.6 | 64.0 | 67.3 | 61.3 | 71.9 |
| S3 + CoI | 69.2 | 73.6 | 65.3 | 79.2 | 76.2 |
| S4 + Q-R（補正方式） | 70.6 | 74.0 | 67.5 | 79.9 | 78.3 |

論文 test との比較（論文は HOTA / MOTA / IDF1 のみ報告）:

| 段 | HOTA 本再現 / 論文 | MOTA 本再現 / 論文 | IDF1 本再現 / 論文 |
|---|---|---|---|
| S2 + Add | 65.6 / 67.9 | 61.3 / 69.7 | 71.9 / 74.4 |
| S3 + CoI | 69.2 / 73.8 | 79.2 / 87.4 | 76.2 / 80.9 |
| S4 + Q-R | 70.6 / 75.5 | 79.9 / 89.2 | 78.3 / 83.4 |

寄与（test）:

| 寄与 | ΔHOTA | ΔDetA | ΔAssA | ΔMOTA | ΔIDF1 |
|---|---|---|---|---|---|
| CoI（S3−S2） 本再現 | +3.6 | +9.6 | −2.0 | **+17.9** | +4.3 |
| CoI 論文 | +5.9 | — | — | +17.7 | +6.5 |
| CoI 本再現 val（参考） | +3.90 | +9.17 | −1.16 | +17.10 | +4.29 |
| Q-R（S4−S3） 本再現 | +1.4 | +0.4 | +2.2 | +0.7 | +2.1 |
| Q-R 論文 | +1.7 | — | — | +1.8 | +2.5 |
| Q-R 本再現 val（参考） | +1.03 | +0.23 | +1.75 | +0.33 | +1.80 |

### 解釈（暫定、詳細指標を踏まえて）

- **CoI の MOTA の寄与は論文とほぼ一致した**（+17.9 と +17.7）。val（+17.10）とも一致する。CoI がメモリ除外を通じて重複トラックの FP を減らす効果は再現できている
- **CoI の HOTA・IDF1 の不足は、AssA の低下から来ている**。本再現の CoI は test でも val でも AssA を下げる（−2.0 / −1.16）。論文は AssA を報告していないが、IDF1 の寄与（+6.5）から見て、論文の CoI は association も改善していると考えられる。本再現では、メモリ除外が正しいトラックの見失いや ID の付け替わりも引き起こしている可能性がある（候補: A6 の除外範囲、A9 の未実装）
- **Q-R（補正方式）は全指標で論文と同じ向き**で、大きさも近い（HOTA +1.4 / +1.7、IDF1 +2.1 / +2.5）
- **MOTA の絶対値は S2 の時点で論文より 8.4 低く**、その差は S3・S4 でもほぼ一定（−8.2 / −9.3）。差は CoI や Q-R ではなく、S2 以前（検出器の設定、baseline、Object Addition）で生じている。S1 の提出で、baseline と Add のどちらで差が生じているかを切り分けられる
- spec の機構署名（CoI で AssA 増・DetA ほぼ不変）は、test でも不成立（AssA −2.0、DetA +9.6）。ただし、論文の ΔMOTA +17.7 自体が DetA の大きな変化を伴うはずなので、この署名は見直しが必要（`2026-09-28-sam2mot-s3-coi-results.md`）
