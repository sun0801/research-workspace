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

---

## 追記 2026-10-13 17:20: S1 の提出結果

ユーザーが S1（`results/submissions/test_s1/tracker.zip`）を CodaBench に提出した。詳細画面の値は次のとおり（Submission ID は未記録）。

| 段 | HOTA | DetA | AssA | MOTA | IDF1 |
|---|---|---|---|---|---|
| S1 baseline 本再現 test | 63.3 | 55.4 | 72.3 | 55.1 | 70.3 |
| S1 論文 test | 62.9 | — | — | 55.6 | 69.6 |
| 差 | +0.4 | — | — | −0.5 | +0.7 |

### 段ごとの論文との差（test、HOTA / MOTA / IDF1）

| 段 | 本再現 − 論文 |
|---|---|
| S1 baseline | +0.4 / −0.5 / +0.7 |
| S2 + Add | −2.3 / −8.4 / −2.5 |
| S3 + CoI | −4.6 / −8.2 / −4.7 |
| S4 + Q-R | −4.9 / −9.3 / −5.1 |

### 寄与（test）

| 寄与 | ΔHOTA | ΔDetA | ΔAssA | ΔMOTA | ΔIDF1 |
|---|---|---|---|---|---|
| Add（S2−S1） 本再現 test | +2.3 | +8.6 | −5.0 | +6.2 | +1.6 |
| Add 論文 test | +5.0 | — | — | +14.1 | +4.8 |
| Add 本再現 val（参考） | +5.11 | +14.38 | −6.39 | +13.13 | +6.72 |

### 解釈（暫定）

- **baseline（S1）は test で論文とほぼ一致した**（HOTA +0.4、MOTA −0.5、IDF1 +0.7）。SAM2 predictor の系統、スコア定義（A2）、mask→box（A3）、検出器 3x_coco の S1 への影響は、test の S1 では論文との差として現れていない。
- **論文との差は Add で生じ始める。** S2 の時点の MOTA 差 −8.4 は、ほぼすべて Add の寄与不足（+6.2 と論文 +14.1）による。HOTA の差 −4.9（S4）は、Add の寄与不足 −2.7 と CoI の寄与不足 −2.3 でほぼ説明できる。
- **Add の寄与は val では論文と一致するが、test では半分以下になる**（ΔHOTA val +5.11 / test +2.3、ΔMOTA val +13.13 / test +6.2）。S1 は val 59.21 → test 63.3（+4.1）と split 間の差が大きく、「val と test の差は1ポイント程度」は S1 では成り立たない。val で Add を合わせても test の差は縮まらない可能性がある。
- 候補として、公式 README が DanceTrack test でのみ渡す系列別の検出閾値 CSV（`config/dancetrack_test/co_dino_detections_thresholds.csv`、未公開）がある。det conf は Object Addition の発動を直接決めるため、test でだけ Add の寄与が小さいことと整合する（hypothesis。CSV の内容は不明）。
- **spec の順序基準は test では成立した**: Add +2.3 > 0、CoI +3.6 > Add +2.3、Q-R +1.4 が最小。val では CoI < Add で不成立だった。

---

## 追記 2026-10-15 19:10: CodaBench の採点ログによる FP・FN・IDSW の内訳

ダウンロードできる結果（scores.json）には主要5指標しかない。そこで、ユーザーが CodaBench の採点ログ（scoring の stdout）から S1〜S4 の TrackEval 出力を貼り付けた。COMBINED 行を、実装リポジトリの `results/submissions/test_s{1..4}/codabench_scoring_stdout.txt` に保存した。採点の設定が `PRINT_ONLY_COMBINED: True` のため、test には系列別の値がない。

### 誤りの内訳（GT 検出数に対する割合、%）

test の GT は 289,166、val の GT は 225,148。MOTA = 100 − (FN + FP + IDSW)。val は既存の 3x_coco 主設定（`s1_baseline` / `s2_addition` / `s3_coi_no_lowconf` / `s4_qr_refine`）。

| 段 | test FN | test FP | test IDSW | test 誤り計 | 論文 test 誤り計（100 − MOTA） | val FN | val FP | val 誤り計 |
|---|---|---|---|---|---|---|---|---|
| S1 | 31.82 | 12.85 | 0.19 | 44.85 | 44.4 | 41.99 | 11.18 | 53.36 |
| S2 | 6.74 | 31.49 | 0.47 | 38.71 | 30.3 | 10.29 | 29.42 | 40.23 |
| S3 | 6.26 | 14.23 | 0.34 | 20.82 | 12.6 | 9.93 | 12.82 | 23.12 |
| S4 | 6.12 | 13.71 | 0.31 | 20.14 | 10.8 | 9.54 | 12.88 | 22.80 |

| Add（S2 − S1）の変化 | FN | FP | IDSW | ΔMOTA |
|---|---|---|---|---|
| test | −25.07 | +18.65 | +0.28 | +6.14 |
| val | −31.70 | +18.24 | +0.33 | +13.13 |
| 論文 test | — | — | — | +14.1 |

### その他の指標（test）

| 段 | DetRe | DetPr | AssRe | AssPr | 出力 ID 数（GT 298） | 出力 box 数 / GT |
|---|---|---|---|---|---|---|
| S1 | 63.76 | 78.69 | 80.01 | 79.37 | 223 | 0.81 |
| S2 | 86.37 | 69.24 | 74.65 | 79.25 | 474 | 1.25 |
| S3 | 86.67 | 80.27 | 72.43 | 78.43 | 455 | 1.08 |
| S4 | 86.85 | 80.72 | 74.67 | 79.73 | 441 | 1.08 |

### 解釈（暫定）

- **Add で増える FP は、test と val でほぼ同じ**（GT 比 +18.65 / +18.24）。違うのは FN の減り方で、test は −25.07、val は −31.70。test の S1 は最初から FN が少ない（31.82 / 41.99）ため、Add で取り戻せる FN が少ない。test で Add の寄与が val の半分になるのは、主にこの差による。
- **論文との MOTA の差は、FP の多さでしか説明できない。** S4 では、本再現の FP だけで GT 比 13.71 あり、論文の誤りの合計 10.8（FN・FP・IDSW の合計）を超える。S2 でも、本再現の FN は 6.74 しかないので、論文との差 8.4 の大半は FP によるはずだ。S1 の誤りの合計は論文と同水準（44.85 / 44.4）なので、FP の超過は Add 以降に生じる。
- Add は出力 ID 数を 223 から 474 に増やす（GT は 298）。AssA の低下（−5.0）は AssRe（80.01 → 74.65）から来ており、AssPr はほぼ変わらない（79.37 → 79.25）。つまり、1人の GT が複数の ID に分かれている。Add で同じ人物に新しいトラックを重ねて追加し、FP と ID の分裂が同時に起きている可能性がある（hypothesis。val の S2 も AssRe 79.56 → 72.74、AssPr 80.10 → 79.52 で同じ形）。**→ 2026-10-15 の val 診断で否定**: Add で生まれたトラックのうち、生まれた時点で既存トラックと重なったものは 250 本中 2 本だけだった。重複は、生まれた後に隣の人物へ乗り移って生じる（`2026-10-15-sam2mot-add-fp-diagnosis.md`）。
- CoI は FP を S2 の約半分まで減らす（test 31.49 → 14.23）。それでも論文の水準には届かず、差は S3 以降も残る（MOTA の差 −8.2 / −9.3）。
- val の o365tococo でも、S4 の FP は 3x_coco とほぼ同じ（29,225 / 29,010）。検出器を替えるだけでは、この FP の超過は解消しない見込み。
- 次の切り分け候補: val で S2 の FP の中身を分類する（**2026-10-15 実施** → `2026-10-15-sam2mot-add-fp-diagnosis.md`）。既存トラックと重なる追加（重複）、背景や誤検出への追加、GT と IoU 0.5 未満の位置ずれ、のどれが多いかを見る。分類は GT を使う読み取り専用の診断で行う。
