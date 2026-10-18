---
date: 2026-10-12
project: sam2-mamba-motion-tracking
status: completed
tags: [experiment, qualitative, video, midterm, DanceTrack]
---

# 中間発表用 定性比較動画（3手法×4パターン）

10/9 MTGの方針（成功例・失敗例の両方を示す。3手法×4パターン。GT付きの大きな動画は補足へ）に沿って、DanceTrack valの既存推論結果から動画を作った。新しい推論は行っていない。

## 入力

定量表（中間発表スライド「定量的評価」）と同じ出力を使った。TrackEvalで再評価し、表の値と一致することを確認した。

| 手法 | 推論結果 | 再評価 HOTA / IDSW |
|---|---|---|
| SAM2 | `TrackEval/data/trackers/dancetrack/val/my_sam2_model/data` | 51.269 / 1618 |
| SAMURAI | `TrackEval/data/trackers/dancetrack/val/my_samurai_model/data` | 54.109 / 1517 |
| Ours（Mamba-state epoch100） | `2025_03_aburatani_sam2/results/sam2_stateful_minimal/20260723T_sam2_minimal_25seq/samurai_mamba_stateful_tiny` | 55.520 / 1535 |

### 注意: 10/8の定性動画は別の推論結果を使っている

`2025_03_aburatani_sam2/results/sam2/sam2_tiny` と `results/samurai/samurai_tiny` は、定量表の出力と中身が異なる。TrackEvalで再評価すると次の値になり、表の値と一致しない。

| 出力 | HOTA | IDSW |
|---|---:|---:|
| `results/sam2/sam2_tiny`（2026-07-23更新） | 52.708 | 1509 |
| `results/samurai/samurai_tiny`（2026-05-20更新） | 48.746 | 1928 |

[10/8の dancetrack0034 定性動画](figures/2026-10-08-dancetrack0034-frames300-340-qualitative.md)は、SAM2とSAMURAIでこの `results/` 側を使っている。定量表と同じ条件の動画として示す場合は、今回の動画を使う。どちらの出力がどの実行条件に当たるかは、今回は調べていない。

## 選び方

スクリプト: [select_candidates.py](figures/2026-10-12-qualitative-patterns/select_candidates.py)

- 各フレームで、GTと予測をIoU 0.5以上のHungarian matchingで対応付けた。
- 60フレームの窓（stride 10）ごとに、窓の全フレームにいるGT IDについて次を計算した。
  - `cov`: 対応が取れたフレームの割合
  - `keep`: 窓の最初の10フレームで最も多く対応したtrack IDが、窓内で対応し続けたフレームの割合
  - `transfer`: 最後の10フレームで最も多く対応したtrack IDが、最初と異なれば1
- 出力: [系列ごと](figures/2026-10-12-qualitative-patterns/candidates-sequences.csv)、[窓ごと](figures/2026-10-12-qualitative-patterns/candidates-windows.csv)、[窓×GT IDごと](figures/2026-10-12-qualitative-patterns/candidates-gt-windows.csv)
- 系列ごとのHOTAは、[8/4の比較表](2026-08-04-sequence-level-standard-hota-comparison.md)と一致した。

選定条件:

- ①少人数・成功: 窓内の人数5人以下、3手法とも `keep ≥ 0.98` かつ `transfer = 0`。そのうえで、GTの横移動量が大きい窓を選んだ。
- ②多人数・失敗: 窓内の人数8人以上。3手法の `keep` の最大値が小さい窓を選んだ。
- ③局所・成功: 注目するGT IDについて、Oursが `keep ≥ 0.95`、SAM2とSAMURAIは窓の途中で失敗（`0.25 ≤ keep ≤ 0.75` かつ `transfer = 1`）。
- ④局所・失敗: 注目するGT IDについて、Oursが窓の途中で失敗し、SAM2とSAMURAIは `keep ≥ 0.95`。
- 機械的な候補から、各パターン2例を目視で確認して選んだ。④の2例目は、最初に選んだ dancetrack0081（GT ID 9）が人数が多すぎて注目人物を見分けにくかったため、dancetrack0034（GT ID 10）に差し替えた。

## 選んだ例

窓は60フレーム。動画は前後10フレームを足した80フレームを10fpsで再生する（約8秒）。代表例のみ100フレーム＋前後10フレーム。

| ID | パターン | 系列・窓 | 人数 | SAM2 | SAMURAI | Ours |
|---|---|---|---:|---|---|---|
| p0 | 代表例 | 0004 / 141–240 | 4 | keep 0.49, transfer 2 | keep 0.43, transfer 2 | keep 0.43, transfer 2 |
| p1a | ①少人数・成功 | 0097 / 761–820 | 4 | keep 1.00 | keep 1.00 | keep 1.00 |
| p1b | ①少人数・成功 | 0010 / 781–840 | 5 | keep 1.00 | keep 1.00 | keep 1.00 |
| p2a | ②多人数・失敗 | 0081 / 871–930 | 16 | keep 0.29, transfer 12 | keep 0.33, transfer 12 | keep 0.34, transfer 10 |
| p2b | ②多人数・失敗 | 0079 / 531–590 | 15 | keep 0.24, transfer 12 | keep 0.38, transfer 9 | keep 0.34, transfer 9 |
| p3a | ③局所・成功 | 0025 / 81–140、GT 3 | — | keep 0.52 | keep 0.50 | keep 1.00 |
| p3b | ③局所・成功 | 0034 / 621–680、GT 7 | — | keep 0.53 | keep 0.47 | keep 1.00 |
| p4a | ④局所・失敗 | 0090 / 241–300、GT 8 | — | keep 1.00 | keep 1.00 | keep 0.52 |
| p4b | ④局所・失敗 | 0034 / 41–100、GT 10 | — | cov 0.98, keep 0.98 | cov 0.98, keep 0.98 | cov 0.48, keep 0.45 |

代表例・①・②の人数とkeepは、窓の全フレームにいるGT IDの平均。

### 局所パターンで起きていること（対応したtrack IDの推移）

- **p3a（0025, GT 3）**: SAM2はtrack 2・3・5、SAMURAIはtrack 2・3が、同じ人物に交互に対応する。別の人物を追っていたtrackが、この人物に重なって移ってきている。Oursはframe 75以降、track 3だけが対応する。ただし動画では、Oursでもtrack 2の枠がこの人物の近くに出るフレームがある。
- **p3b（0034, GT 7）**: SAM2はtrack 7と9、SAMURAIはtrack 7と12が交互に対応する。Oursはtrack 7だけが対応する。
- **p4a（0090, GT 8）**: SAM2はtrack 13、SAMURAIはtrack 12が、窓の間ずっと対応する（窓より前に、IDがGTとずれている）。Oursはtrack 7・12・13が交互に対応し、複数のtrackが1人に重なる。
- **p4b（0034, GT 10）**: SAM2とSAMURAIはtrack 10を維持する。Oursはframe 71以降この人物を見失い、一部のフレームでtrack 12が対応する。

いずれも動き予測の有無が原因かどうかは、この可視化からは判断していない。

## 動画の作り方

スクリプト: [render_videos.py](figures/2026-10-12-qualitative-patterns/render_videos.py)。H.264（libx264, yuv420p）、10fps。

スライド上で個別に動かせるよう、手法ごとに別の動画にした（2026-10-13、ユーザーの依頼で連結動画から変更）。手法名は動画に焼き込まず、スライドのテキストで付ける。

- **本編用（`*-{sam2,samurai,ours}-crop.mp4`、960×540）**: 局所パターンは注目する人物の範囲を、それ以外は全GTの範囲を、16:9で切り出す。
- **補足用（`*-{gt,sam2,samurai,ours}-full.mp4`、1280×720）**: フレーム全体を表示する。
- 枠の色と番号はtrack IDを表す。全対象をGT bbox promptで初期化しているので、初期のtrack IDはGT IDと同じ。追跡が他の人物へずれると、同じ人物に付く番号が手法ごとに異なる。
- 注目する人物（GT）は白い破線枠で示す。
- 各動画の中央フレームを、スライドのポスター画像（`*-poster.jpg`）にした。
- 全フレームの動画は同じフレーム範囲・同じ10fpsなので、スライドで同時に再生すれば揃う。

## スライドへの反映

[中間発表スライド（再構成版）](../materials/2026-10-12-midterm-slides-restructured.pptx)に入れた。

- 定性的評価：代表例 → p0（3手法×crop）
- 定性的評価：4パターンの比較 → p1a・p2a・p3a・p4a（各3手法×crop）
- 補足：各パターン2例ずつ → p1a〜p4b（各GT＋3手法×full、8枚）

## 未確認

- 手法別の動画がPowerPointで再生できることは、ユーザーが確認した（2026-10-13）。
- 各パターン2例目のcrop動画（`p*b-*-crop.mp4`）はスライドに入れていない。

## 2026-10-17 追加: 全部うまくいかない例・提案手法だけうまくいかない例の選び直し

10/14 MTGの指摘（動画全体、半分の速さ）に合わせて、②と④の素材を作り直した。詳細は[2回目の素材](figures/2026-10-17-qualitative-patterns-v2/manifest.md)。

- 全部うまくいかない: dancetrack0026 の全302フレーム（GT / SAM2 / SAMURAI / Ours、10fpsで約30秒）。
- 提案手法だけうまくいかない: dancetrack0079 GT 8、frame 812–891（注目人物の周辺を切り出し、GT / SAM2 / SAMURAI / Ours）。Oursだけがframe 842–864で見失う。
- 再構成版スライドの16・17枚目に入れた（2026-10-17）。

## 2026-10-17 再構成版スライドへの反映（4パターン×1系列）

ユーザーの依頼で、手元の版（`20261018_中間発表_油谷.pptx`）に一度入れた変更は取り消して元に戻し、[再構成版](../materials/2026-10-12-midterm-slides-restructured.pptx)に入れた。③④は、注目する人物と、その人物に関わる track だけを描いた3手法の動画にした（[作り方](figures/2026-10-17-qualitative-focal-only/manifest.md)）。

| スライド | 系列 | 動画 |
|---|---|---|
| 16 全手法でうまくいっている例 | dancetrack0058, frame 1–200（20秒、人の重なりあり） | occok20s full（GT＋3手法、frame 番号なし。[オクルージョンがあっても3手法とも全員の ID を保つ区間](figures/2026-10-17-qualitative-occlusion/manifest.md)。0097 の25秒版から差し替え） |
| 17 全手法でうまくいかない例 | dancetrack0026, 全302フレーム | 2回目 allfail full（GT＋3手法、変更なし） |
| 18 局所的にうまくいっている例 | dancetrack0025 GT 3, frame 71–150 | localok focal（3手法） |
| 19 局所的にうまくいっていない例 | dancetrack0007 GT 1, frame 314–413（10秒） | localfail0007 target（3手法、縦長。GT は緑、ID 1 だけ水色。Ours だけ ID 1 が隣の人に移る。0079 GT 8 から差し替え） |

- 「定性的評価：代表例」「4パターンの比較」と、本編と重なる「補足：① 少人数でうまくいく例（1）」は非表示にした。
- 前の「提案手法だけうまくいかない例」（GT＋3手法、全 track）は、補足「④ 局所的に見てうまくいかない例（dancetrack0079，全 track）」として残した。
- PowerPoint での再生確認はユーザーに依頼。
- 本編4枚の動画は、左下の frame 番号を消した版に差し替えた（[作り方](figures/2026-10-17-qualitative-main-nolabel/manifest.md)）。補足は番号ありのまま。
- （上の手元の版への反映は、ユーザーの依頼で取り消し、作業前のファイルに戻した。）
