---
date: 2026-10-23
project: sam2-mamba-motion-tracking
type: paper-note
tags: [view, method, implementation-check]
---

# ViEW 8ページ版：手法の記述と実装の突き合わせ

MIRU 原稿（`overleaf/miru/main_text.tex`）の手法の記述を、評価に使った実装と突き合わせた。新しい実験はしていない。

## 根拠にしたコード

- **Ours（Mamba-state）**：`2025_03_aburatani_sam2` の評価run `results/sam2_stateful_minimal/20260723T_sam2_minimal_25seq/`。
  - `git_commit.txt`（a6253e7）に `git.diff` を当てた内容が、Python コードについて commit 11f7185 と一致することを確認した。
  - 設定は `sam2/configs/samurai_mamba_stateful/sam2.1_hiera_t.yaml`、checkpoint は `mamba_stateful_dancetrack/epoch100.pth`。
- **Mamba-window**：`results/samurai_mamba/samurai_mamba_tiny`（5/19〜5/20）と推定した。
  - 表の HOTA 53.3 と TrackEval の `my_samurai_mamba_model` が一致する。
  - このrunには git.diff が残っていないので、コードは直前の commit f1edd2b とみなした。
- **Mamba の学習**：`2025_09_aburatani_Mamba_Trackers` の commit f08cd5f。2026-06-30 のrun（comet ログ `comet-mamba-mot-20260630-165150.log`）。

## 実装の事実（論文に書く値）

| 項目 | Mamba-state（Ours） | Mamba-window |
|---|---|---|
| モデル | 独自の MambaStateful：`Linear(4→256)` → Mamba-1（`mamba_ssm.Mamba`）3層（d_model 256，d_state 16，d_conv 4，expand 2，層間の norm・残差なし） → `LN→Linear→LeakyReLU→Linear(→4)` | MambaTrack：Bi-Mamba block 3層，d_model 512，d_state 16 |
| パラメータ数 | 1,381,892 | 13,332,804 |
| 入力 | 選ばれた box の cx,cy,w,h（画像サイズで正規化した4次元），1フレーム1トークン | 直近最大11個の box の差分（最大10個，正規化して×50） |
| 出力 | 次時刻の Δ(cx,cy,w,h)×50。推論時のみ ±0.1 で clip し，`pred = 最後のbox + Δ` | Δ(cx,cy,w,h)。`pred = 最後のbox + Δ` |
| 予測を始める時点 | 5観測目まで，予測は「前フレームの box」 | box が6個未満のあいだは前フレームの box |
| 信頼度が低いとき | 選択候補の SAM 予測 IoU が 0.3 以下だと stable=0 になり，次フレームで状態と履歴をリセットする | 履歴をリセットせず保持する |
| 学習 | DanceTrack train の GT 軌跡（417本，長さ25未満を除外），12フレームの窓（stride 1），SmoothL1，Adam（lr 1e-4 固定，betas 0.9/0.98），grad clip 1.0，batch 64，100 epoch。窓ごとにゼロ状態から開始 | `MambaTrack_epoch25.pth`。**学習条件は確認できない**（元の保存先が空） |

**共通の設定**
- **SAM2**：SAM2.1 Hiera tiny で，追加学習はしていない。
- **候補選択**：$s = w\,\mathrm{IoU}(\hat b, b^k) + (1-w)\,\hat q^k$。$\hat q^k$ は SAM2 の mask decoder が出す予測 IoU（iou_predictions，sigmoid 済み）で，object score は入らない。
  - 候補数は $K=3$（multimask）。
  - $w=0.25$ で，SAMURAI baseline と同じ値。オリジナル SAMURAI の yaml も 0.25。
- **メモリ選択**：SAMURAI と同じく，選ばれた候補の $\mathrm{IoU}(\hat b, b^{k^*})$ を motion score として使い，`kf_score > 0` を条件に含める。直前フレームは常にメモリに入る。
- **SAMURAI の閾値**：stable_frames_threshold は **1**（オリジナルは15。5/19 に変更し，SAMURAI baseline も同じ1），stable_ious 0.3，memory_bank の iou/obj/kf 閾値は 0.5/0.0/0.0。
- **MOT への拡張**：物体ごとに出力（メモリ）と motion state を持ち，物体ごとに順に推論する。
  - 各 ID は，初めて現れるフレームの GT bbox を box プロンプトにして初期化する（全 ID が対象）。
  - 終了処理はなく，マスクが空のフレームは出力しない。

## MIRU 原稿の記述との食い違い

1. **Mamba に入力する box**：MIRU 3.1 では「各候補マスクから bbox を計算し，それを Mamba に入力」とあるが，実際は選んだ候補の box の履歴を入力している。しかも入力するのは，SAM 予測 IoU が 0.3 を超えた場合だけ。
2. **状態ベクトルの定義**：MIRU 3.3 の8次元 $[c_x,c_y,w,h,\Delta c_x,\ldots]$ は，どちらの構成とも合わない。state 型は4次元の box，window 型は box の差分を入力する。構成ごとに分けて書く。
3. **Mamba の引用**：実装は Mamba-1 なので，「Mamba は…」の説明で Mamba-3（Lahoti）を引くのは不適切。Gu & Dao（COLM2024）を引く。
4. **$s_{\mathrm{mask}}$**：「候補の信頼度」ではなく，SAM2 が出す予測 IoU と明記する。$\lambda=0.25$ は SAMURAI の設定に合わせたと書ける。
5. **「SAM2 のメモリ機構は変更していない」**：mask decoder とメモリエンコーダは変えていない。ただし，メモリ選択には SAMURAI と同じく motion score が入るので，Mamba の予測はメモリ選択にも効いている。「候補選択とメモリ選択に用いる動き予測器を置き換える」と書く。
6. **「過去全体を状態として持てる」**：信頼度の低いフレームの次でリセットするので，実際に持っているのは「最後にリセットしてから後の履歴」。また，学習は12フレームの窓（ゼロ状態から開始）なので，長い状態を持ち越すことは学習していない。
7. **window 型と state 型の比較は統制されていない**：次の点がすべて異なる。
   - モデル（MambaTrack 13.3M と独自モデル 1.38M）
   - 入力の表現（差分か box か）
   - 学習の設定
   - リセットの扱い

   したがって，「state を持ち越すから良い」と原因を特定することはできない。MIRU・ViEW 2ページ版の考察（「hidden state として引き継ぐことが有効」）はこの点で言い過ぎ。
8. **書いていない設定**：stable_frames_threshold=1，予測を始めるまでの観測数（5），推論時の ±0.1 clip，各 ID の初出フレームで GT bbox を与える初期化。

## 実装上の気づき（論文の前に確認したいこと）

- 評価runの debug CSV の 1,997/245,291 行（約0.8%）で，全マスクが NO_OBJ になって候補 box が [0,0,0,0] なのに，SAM 予測 IoU が 0.3 を超えたため観測として Mamba に入っている。
- 現在の tiny yaml の $w$ は 0.5 で，評価runの値（0.25）と異なる。0.5 は別run `20260727T_..._kfw05` の値。

## 執筆方針の決定（2026-10-23）

- 概要図（`images/model.pdf`）と手法の説明の流れは，MIRU・2ページ版のまま使う。
- 食い違い1は，「各候補の bbox を Mamba に入力」と読める一文だけを次の表現に直す：「SAM2が出力する候補マスクからバウンディングボックスを求め，Mambaによる動き予測に基づいて各候補の motion score $s_{\mathrm{mamba}}$ を計算する．」
- 関連研究の章は残す。
