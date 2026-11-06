---
date: 2026-11-06
project: sam2-mamba-motion-tracking
type: meeting-materials
topic: weekly-progress
status: draft
target_meeting: 2026-11-06
notion_url: null
notion_export: null
tags: [meeting-materials, research, weekly-progress, temporal-mamba, spatial-mixing, latent-correspondence]
---

# 2026-11-06 MTG資料: state に空間方向の対応を持たせる（10/30〜11/6の進捗）

## 0. 今日相談したいこと

**一言でいうと**：10/30 の方針どおり、V3 の state に空間方向の対応を持たせる方法を考えた。方法は 4 パターンに整理でき、そのうち **A（対応先から運ぶ：①-b）と B（近傍と混ぜる：②・②'）の 2 パターンを実装した**。B では state は使われるようにならなかった。A は、state への依存・寄与・性能の点推定がそろって正（+0.6 前後）になったが、95% 区間はどれもわずかに 0 を含む。

1. **4 パターンの整理**（3章、図6）：抜けや、別の分け方はないか。A を主案、B を対照、C・D を後回しにする判断でよいか。
2. **①-b の結果の読み方と次の一手**（5.3節、8章）：事前に決めた基準では、「①-b は運んだ state を使っている」とも「A' より良い」とも言えない。ただし、これまでの方式（A・②・②'）では点推定がほぼ 0 だったのに対し、①-b はそろって正で、区間の下限も 0 に近い。seed を足して再現するか確かめるべきか。SAM2 の memory と冗長という反対仮説 (a) は、まだ支持も否定もできていない。
3. **開発用の学習の長さ**（2章）：10 epoch では V3 の効果がまだ見えなかった（A − F0 が 0 を含む）ので、今週も 22 epoch（約 12 時間）で回した。この設定でよいか。
4. **判定の解像度**：今の val（MOSE 125 動画、単一 seed）は 95% 区間の幅が 2〜3 pp あり、1 pp 未満の差は見分けられない。この先どう判定するか。
5. **英論文紹介の 3 本**（9.1節）：MambaOut → TV3S → TS-Mamba（案1）でよいか。
6. **近い先行研究**（9.2節）：Memory as Dynamics（ICML 2026）は、SAM2 に SSM の予測 memory を足し、予測による汚染を信頼度で抑える。修論の問いとかなり重なる。精読して差分を整理する予定だが、修論・論文で比較対象にすべきか。

## 1. 実験条件の定義

| 記号 | 意味 |
|---|---|
| F0 | 前回までの全軌跡の学習で作ったモデル。比較の基準 |
| A | F0 から、V3 だけを 8 フレームの短い区間で 22 epoch 学習（SAM2 本体は固定）。前回までの V3 |
| A' | A と同じ設定を、①-b と同じ GPU（RTX A4000）で学習し直したもの。①-b の比較相手 |
| ②・②'・①-b | A に各部品を足し、A と同じ設定で学習したもの（4章） |
| reset1 | 推論時に state を毎フレーム 0 に戻す。state を使っているかを見るための比較 |
| M0 / M1 | 評価時に SAM2 の memory をそのまま使う / 直前 1 枚に絞る |

- **state の寄与 R** = （state を持ち越す）−（reset1）。**寄与の増加 I** = R(新しい条件) − R(A)。
- 評価はすべて MOSE val（125 動画・313 対象）の J&F。区間は動画単位の paired bootstrap による 95% 区間、単位は pp。

## 2. 前回（10/30）からの流れ

| 10/30 の TODO | 状況 |
|---|---|
| 空間方向の入れ込み方を考える（挿入位置は今のまま） | 4 パターンに整理し、A・B を実装（3〜5章） |
| 潜在空間での対応の先行研究を探す | サーベイを実施（11/2）。Mamba の state を凍結特徴の対応で運ぶ前例は、調べた範囲では見つからなかった |
| 画像空間のフローを潜在空間にマッピングする案（杉本さんの取り組み） | ①-a（外部 flow で運ぶ。①-b の上限）として計画に入れた。①-b が ②' を上回らなかったときだけ回す。杉本さんへの確認はまだ |
| ID ごとの出力に入れる案（multiplex など） | 4 パターンの D（物体単位の state）に位置づけた。未着手 |
| 開発用の設定を「Mambaだけ・10 epoch程度」にする | Mambaだけは採用。10 epoch は確認した結果、22 epoch のままにした（下） |
| 「Mambaだけ学習」の研究上のメリットを整理する | 未着手 |
| 修論を書き進める | 今週は進められていない |
| 資料の冒頭で条件を定義する | 1章 |

10 epoch の確認（A・B・C の 10 epoch 時点を val 全体で評価、11/2）：

- A − F0 は 10 epoch で +0.37 [−0.91, +1.65] と 0 を含み、22 epoch で +1.51 [+0.38, +2.79] になった。A は 10 → 22 epoch の間に有意に伸びた（+1.14 [+0.22, +2.29]）。
- V3 だけを学習する条件では、10 epoch で打ち切ると効果がまだ見えない。そのため、今週の比較はすべて 22 epoch で行った。

## 3. 空間方向の対応を持たせる 4 パターン

![図6：state に空間方向の対応を持たせる 4 パターン](figures/2026-11-06-state-spatial-correspondence/fig6-four-families-simple.svg)

| パターン | やること | 近い前例 | 本研究 |
|---|---|---|---|
| **A. 運ぶ** | 対応先から state を持ってきてから更新 | GRFP、TrajGRU | **①-b（実装・評価済み）** |
| **B. 混ぜる** | 対応は取らず、近傍と混ぜて届く範囲を広げる | ConvLSTM、ConvS5 | **②・②'（実装・評価済み）** |
| C. 内容で引く | key で state を引く。位置に依らない | LiVOS、XMem | 未着手 |
| D. 物体単位 | 物体ごとに 1 本の state を持つ | Cutie、SAMURAI | 未着手 |

- **A**：先生の 10/30 の「潜在空間の中で対応を取る」に直接対応する。
- **B**：A の対照。A が B を上回って初めて、「混ぜる」のではなく「運ぶ」ことに意味があると言える。
- **C**：SAM2 の memory attention がすでに内容で引いているので、冗長になりやすい。
- **D**：別の軸。SAMURAI の Kalman filter を置き換えるという本研究の出発点に近い。

## 4. 実装した 2 パターン

どちらも V3 の 64 段（memory attention 後の対象別特徴、64×64）だけを変え、128・256 段は V3 のままにした。追加部分を恒等にすると、どちらも V3 と完全に一致する。

### A：①-b 潜在特徴の対応で state を運ぶ

![図7：①-b の組み込み](figures/2026-11-06-state-spatial-correspondence/fig7-1b-in-model.png)

- 凍結した画像エンコーダ特徴（stride 16）で、各マスの周り 15×15 の cos 類似度を取り、softmax（τ=0.02）で重みにする。この重みで前フレームの state を運んでから、Mamba を 1 歩進める。
- 追加の学習パラメータは 0。
- 対応の取り方は、学習前の計測（5.3節）の条件を満たした唯一の設定として決めた。

### B：② 読み書きカーネル / ②' state 空間混合

![図8：②・②' の組み込み](figures/2026-11-06-state-spatial-correspondence/fig8-2-2p-in-model.png)

- **②**：Mamba の前後に 7×7 の depthwise conv を入れる。届く範囲は ±6 マスで頭打ちになる。
- **②'**：毎フレーム、更新前の state そのものを 7×7 で近傍と混ぜる。
- カーネルの大きさは、MOSE の 1 フレームあたりの動きの 90% 点（2.80 マス）から決めた。
- 制約なしの ②' は、学習 300 更新の時点で長い系列に流すと発散した（state が 1 フレームごとに約 2 倍になり、20 フレーム目あたりで非有限）。8 フレームの学習の loss には現れなかった。カーネルを L1 正規化（‖K‖₁=1）して安定させた。

## 5. Evidence: 結果

### 5.1 B（②・②'）：state の寄与は増えなかった

val の J&F（動画平均）：

| 条件 | M0 持ち越し | M0 毎フレーム reset | M1 持ち越し | M1 毎フレーム reset |
|---|---:|---:|---:|---:|
| F0 | 0.7701 | — | 0.7438 | — |
| A（V3） | **0.7852** | 0.7833 | **0.7635** | 0.7560 |
| ② | 0.7836 | 0.7816 | 0.7598 | 0.7592 |
| ②' | 0.7766 | 0.7740 | 0.7576 | 0.7545 |

**この図で見る点**：学習の効果（F0 との差）は A だけ区間が 0 を含まない。② と ②' は state の寄与（R・I）がすべて 0 をまたぎ、②' は A との差が 0 をわずかに下回る。

![②・②' と D2 の val J&F の差](../experiments/figures/2026-11-06-spatial-mixing-val-paired/01-val-jf-paired-diff.png)

| 仮説 | 比較（M0） | J&F の差 [95% 区間] | 判定 |
|---|---|---|---|
| 混ぜると state が使われるようになる | I(②) / I(②') | +0.01 [−1.00, +1.08] / +0.07 [−0.45, +0.62] | 支持されない |
| ②・②' で state の持ち越しが効く | R(②) / R(②') | +0.20 [−0.94, +1.43] / +0.26 [−0.40, +1.11] | 支持されない |
| 総合性能が A より上がる | ② − A / ②' − A | −0.16 [−1.45, +1.42] / **−0.86 [−1.87, −0.04]** | 支持されない（②' は下がる） |

- M1（memory を直前 1 枚に絞る）でも、I・R はすべて 0 を含む。
- 物体の速さで 3 層に分けた結果（区切りは結果を見る前に決めた）：

| I（M0） | 遅い（104 対象） | 中くらい（103 対象） | 速い（104 対象） |
|---|---|---|---|
| ② | +0.10 [−1.61, +1.83] | −1.12 [−3.06, +0.48] | −0.14 [−2.48, +1.84] |
| ②' | +0.45 [−0.41, +1.44] | −1.37 [−3.09, +0.12] | +0.27 [−0.34, +0.92] |

- 位置ずれ仮説なら差が出るはずの「速い」層でも、I は 0 を含む。

### 5.2 D2：SAM2 の memory を絞っても、A の state の寄与は見えない（図の最下段）

| | M0（そのまま） | M1（直前 1 枚） |
|---|---|---|
| R(A) | +0.19 [−0.44, +1.00] | +0.75 [−0.14, +1.91] |
| memory を絞ったときの低下（A） | — | −2.17 [−3.98, −0.48] |

- memory を絞ると性能は約 2 pp 下がるが、state の寄与は区間が 0 を含んだまま。
- 「memory を絞れば state が使われる」とは言えず、反対仮説 (a) を支持する材料にも否定する材料にもならなかった。

### 5.3 A（①-b）：点推定はそろって正だが、区間はわずかに 0 を含む

**学習前の計測**（MOSE train 100 動画）。指標は保持質量 M（運んだ重みのうち、前フレームで同じ物体の前景から来た割合）：

| 物体の速さ | 対応なし（V3 と同じ） | ①-b（softmax） |
|---|---|---|
| 遅い | 0.830 | 0.888 |
| 中くらい | 0.717 | 0.847 |
| 速い | 0.545 | 0.811 |

- 速い物体ほど、対応を取る効果が大きい。
- 一方、1 マス（16 px）未満の動きでは、運ぶとかえって位置がぼやける（既知の量だけ平行移動した画像で確認）。MOSE の動きの中央値は 0.63 マス/フレームである。

**val の結果**（11/6 朝に学習・評価を完了。比較相手は同じ GPU で学習した A'）

val の J&F（動画平均、M0）：

| 条件 | J&F |
|---|---:|
| F0 | 0.7701 |
| A'（V3） | 0.7789 |
| A'-reset1（毎フレーム reset） | 0.7792 |
| **①-b** | **0.7853** |
| ①-b-reset1（毎フレーム reset） | 0.7794 |
| ①-b、推論だけ対応を恒等に戻す（運ばない） | 0.7797 |
| ①-b、推論だけ類似度を窓の中でシャッフル | 0.7826 |

**この図で見る点**：A' の state の寄与は 0 付近（−0.03）だが、①-b は R・I・推論だけ対応を壊したときの低下・A' との差がそろって +0.3〜+0.6 の正。ただし、どれも区間の下限がわずかに 0 を下回る。

![①-b の val J&F の差](../experiments/figures/2026-11-06-latent-corr-val-paired/01-val-jf-paired-diff.png)

| 仮説（事前に決めた基準） | 比較 | J&F の差 [95% 区間] | 判定 |
|---|---|---|---|
| 運んだ state に依存している | ①-b − 対応を恒等に戻す | +0.56 [−0.07, +1.40] | 言えない（下限がわずかに負） |
| 対応の中身が効いている | ①-b − 類似度をシャッフル | +0.27 [−0.21, +0.79] | 言えない |
| state の寄与が増える | I = R(①-b) − R(A') | +0.61 [−0.75, +2.02] | 言えない |
| state が性能に寄与している | R(①-b) | +0.58 [−0.05, +1.32] | 言えない（下限がわずかに負） |
| 性能が A' より上がる | ①-b − A' | +0.64 [−0.41, +1.80] | 言えない |

物体の速さでの層別（探索的）：

| 比較 | 遅い（104 対象） | 中くらい（103 対象） | 速い（104 対象） |
|---|---|---|---|
| ①-b − 対応を恒等に戻す | +0.43 [+0.02, +0.94] | **+1.01 [+0.04, +2.57]** | +0.20 [−0.63, +1.34] |
| I | −0.15 [−2.08, +1.48] | **+2.79 [+0.18, +5.84]** | +1.38 [−0.76, +4.48] |
| ①-b − A' | +0.38 [−0.35, +1.37] | +1.34 [−0.47, +3.89] | +0.38 [−1.20, +1.92] |

- 中くらいの速さの層では、依存と I の区間が 0 を含まない。ただし層別は探索的で、多数の比較の 1 つ、単一 seed である。
- 速い層では差が小さく、「速い物体ほど効く」という事前の予想とは合わない。
- 64 段の state だけを毎フレーム reset したときの低下（+0.57）は、全段を reset したとき（+0.58）とほぼ同じ。①-b で state を消したときの低下は、ほぼ輸送を入れた 64 段の state で説明できる。
- 「運ぶ量は同じまま、移動だけをなくす」対照も回したが、softmax では重みの行の和が必ず 1 なので、この対照は「対応を恒等に戻す」と同じになっていた。spec の設計時の見落としで、移動の効果は分けて判定できなかった。
- 経過：①-b の本学習は、実装の不具合（学習前の val を推論モードで回したときに作った索引表が、学習の backward で使えない）で一度止まった。修正して 11/5 12:33 に再開し、11/6 6:56 に終わった。

### 5.4 学習の loss：どの方式も A と同じように下がり、差はほぼ 0

学習に使っていない train の 8 フレームの区間 200 個を固定し、2 epoch ごとの checkpoint の loss を F0 との差で比べた（10/30 の資料の 3.3 節と同じ方法）。

![固定した 200 区間の loss](../experiments/figures/2026-11-06-latent-corr-fixed-clip-loss/01-fixed-clip-loss.png)

| 22 epoch での差（mix、区間 200 個の bootstrap） | 値 |
|---|---|
| ② − A | +0.000 [−0.006, +0.003] |
| ②' − A | −0.001 [−0.003, +0.002] |
| ①-b − A' | −0.000 [−0.005, +0.003] |
| （参考）A' − A：同じ設定で GPU だけ違う | +0.002 [−0.000, +0.008] |

- どの方式も、loss は A と同じように epoch ごとに下がった。A との差は、同じ設定を別の GPU で学習したときのばらつき（A' − A）と同じ程度。
- この loss は、state を使っているかを示さない。state の寄与は val の R・I で見る。
- loss の差がなくても、val の差がないとは言えない。②' はこの loss で A と差がなかったが、val の J&F は A より低かった（−0.86）。

## 6. Interpretation: 現時点の見立て

- **近傍と混ぜるだけ（B）では、V3 は state を使うようにならない。** ②' は空間方向の混合を実際に使っていた（学習後、カーネルの中心の重みが平均 0.56 まで下がった）が、state の寄与は増えず、性能はやや下がった。state が平滑化されてぼやけた可能性がある（推論）。
- **明示的に対応を取って運ぶ（A、①-b）と、初めて state を使っている兆しが出た。** A・A'・②・②' では R・I の点推定がほぼ 0 だったのに対し、①-b では依存・寄与・性能がそろって +0.6 前後の正で、区間の下限も 0 に近い。ただし単一 seed で、事前の基準は満たしていない。
- 差の大きさは、事前の予想（memory をそのまま使う条件では 1 pp 未満）と合う。文献でも、強い attention memory の上に足した recurrent state の寄与は小さいという報告が多い。例えば XMem は sensory memory を除くと J&F が −1.1〜−1.9 下がるだけで、SAM2 の著者も memory に GRU を足して改善しなかったと報告している。
- 「速い物体ほど効く」という予想とは合わず、効いているのが位置ずれの補正なのかは、まだ分からない。

## 7. 今回言えること / まだ言えないこと

言えること：

- 空間方向の局所的な混合（②・②'）では、state の寄与を確認できなかった。速さで分けても同じ。
- memory を直前 1 枚に絞っても、A の state の寄与は確認できなかった。
- 学習前の計測では、①-b の対応は、対応なしより同じ物体の state を多く運ぶ。特に速い物体で差が大きい。
- state を再帰的に混ぜる操作は、制約がないと 8 フレームの学習では見えない形で発散する。
- ①-b は、これまでの方式と違い、state への依存・寄与・性能の点推定がそろって正になった。

まだ言えないこと：

- ①-b が運んだ state を使っているか、性能を上げるか（区間がわずかに 0 を含む。単一 seed）。
- 効いているのが位置ずれの補正なのか（速い層で差が大きくならなかった）。
- 反対仮説 (a)（SAM2 の memory と冗長）が正しいか。
- 1 pp 未満の差があるかないか（区間の幅が 2〜3 pp）。

## 8. 次に進む順番

①-b は、事前に決めた読み方の「どの仮説も成り立たない」に当たる。spec では、この場合「この対応の方式と学習条件では効果を確認できなかった」と読み、位置ずれ仮説の否定にはしない。次の候補を比べて決めたい（相談事項 2）。

1. **①-b の seed を足す**：点推定の正が再現するかを確かめる。今回の実績では、1 本あたり学習約 18 時間（学習中の val を含む）・評価約 2 時間（RTX A4000）。中くらいの層の結果も、ここで確かめる項目にする。
2. **①-a（外部 flow で運ぶ）**：対応の質の上限を確かめる。①-b の効果が小さいのが対応の質のせいかを切り分ける。
3. **16 フレームの学習などの診断**：8 フレームの区間では state を持ち越す意味が出にくい可能性（b）と、SAM2 の memory との冗長（a）を確かめる。
4. 移動の効果を見る対照（今回は恒等と同じになった）を作り直す。

## 9. 補足：英論文紹介の候補と、近い先行研究

### 9.1 英論文紹介の候補（3 本）

条件は 2025〜26 年のトップ会議。SambaMOTR は前回紹介したので除いた。

| 案 | 3 本 | 流れ |
|---|---|---|
| **1（推し）** | MambaOut (CVPR'25) → TV3S (CVPR'25) → TS-Mamba (ICLR'26) | Mamba はいつ必要か → 位置固定の時間 state に空間 shift を足す → 軌跡に沿ってトークンを集めてから Mamba に通す |
| 2 | Memory as Dynamics (ICML'26) → TV3S → TS-Mamba | SAM2 ＋ SSM の予測 memory と汚染 → 位置固定 state の限界 → 軌跡で対応 |
| 3 | Memory as Dynamics → SENTRY (ECCV'26) → HyperSSM (CVPR'26) | 3 本とも Tracking。汚染 → memory に書く前の検証 → 物体間の関係を state に入れて Kalman filter を置き換える |

- 案1は 3章の 4 パターンに対応する。TV3S は B（混ぜる）、TS-Mamba は A（運ぶ）に近い。発表の準備が、①-b の次の設計の調査も兼ねる。
- 案1の 3 本は Tracking の論文ではない（画像認識・動画セグメンテーション・動画超解像）。V3 の state は pixel 単位なので、構造はこちらの方が近い。発表の冒頭でそう説明する。
- 採録は 6 本とも公式ページで確認した。数値は ChatGPT Deep Research のレポートの値で、原典ではまだ確認していない。
  - 例：TV3S は shift なし 38.9 → shift あり 39.5 mIoU（Table 3）。本研究の B（②・②'）では state の寄与を確認できなかったので、何が違うかは原典を読んで確かめる。

### 9.2 近い先行研究：Memory as Dynamics（ICML 2026）

Evidence（公式ページの要旨で確認）：

- SAM2 ベースのモデルに、状態空間の dynamics を持つ latent world model を足し、予測 memory を作る。
- 予測 memory は遮蔽や速い動きのときにかえって drift を悪化させる（reliability mismatch）と指摘し、信頼度が低いときは予測の寄与を抑える fusion を入れている。
- SOT で評価し、VOS にも効くと報告している。コードは公開されている。

未確認（Deep Research のレポートによる）：SAM2.1 を固定し、Mamba を使い、予測 memory の prompt だけを学習している。

Interpretation：

- 「frozen SAM2 ＋ SSM の state」「予測による汚染と、信頼度での抑制」という点で、修論の問い（hidden state contamination）とかなり重なる。
- 違いになりうる点（仮説）は、本研究が ①state の空間対応（運ぶ・混ぜる）を扱うこと、②MOT（SAM2MOT・DanceTrack）に入れること、③手法1で Kalman filter を置き換えること。原典を読んで確かめる。

## 10. 参照ファイル

- 実験ログ：[空間混合（②・②'）と D2](../experiments/2026-11-04-temporal-mamba-spatial-mixing.md)、[潜在空間の対応（①-b）](../experiments/2026-11-04-temporal-mamba-latent-correspondence.md)、[10 epoch の評価（補足）](../experiments/2026-10-27-temporal-mamba-short-clip-official-trainer.md)
- spec：[空間混合](../specs/2026-11-04-temporal-mamba-spatial-mixing-spec.md)、[潜在空間の対応](../specs/2026-11-04-temporal-mamba-latent-correspondence-spec.md)
- 文献調査：[空間対応のサーベイ（11/2）](../papers/2026-11-02-deep-research-spatial-correspondence-mamba-state.md)
- 英論文紹介の候補調査：[SSM と state の空間対応（11/4）](../papers/2026-11-04-deep-research-paper-intro-ssm-state-candidates.md)、[既知候補込み（11/6）](../papers/2026-11-06-deep-research-paper-intro-candidates-incl-known.md)、[Tracking に絞った版（11/6）](../papers/2026-11-06-deep-research-paper-intro-tracking-state-memory.md)
- 提案手法の詳細版（式・リスク・関連研究）：[Claude Docs](https://claude.ai/artifact/Gfboj2uoaWB3ktmNbjciEn)。①-b の対応の取り方は argmax 案のまま古い
- 前回 MTG：[議事録](../meetings/2026-10-30-mtg.md)、[資料](2026-10-30-weekly-progress-mtg-materials.md)
- 図：[figures/2026-11-06-state-spatial-correspondence/](figures/2026-11-06-state-spatial-correspondence/manifest.md)

## 11. 付録：これまでに調べた主要論文

- 対象は 2025〜26 年の論文（11/4〜11/6 の調査）。3章の 4 パターン（A 運ぶ・B 混ぜる・C 内容で引く・D 物体単位）に寄せて分けた。
- ★は英論文紹介の候補（9.1節）。
- 会議は公式ページで確認した。手法の説明は要旨にもとづく。
- 3章の表にある 2024 年以前の論文（GRFP、TrajGRU、ConvS5、XMem、Cutie など）は、[11/2 のサーベイ](../papers/2026-11-02-deep-research-spatial-correspondence-mamba-state.md)にまとめてある。

### 11.1 SSM はいつ必要か

| 論文 | 会議 | 手法 |
|---|---|---|
| ★[MambaOut](https://cvpr.thecvf.com/virtual/2025/poster/33055) | CVPR'25 | Mamba ブロックから SSM を外した Gated CNN を作る。ImageNet 分類では visual Mamba を上回り、検出・セグメンテーションでは届かない。「SSM が向くのは長い系列で、因果的に処理するタスク」と主張する |

### 11.2 A. 運ぶ：軌跡や flow で対応を取る

| 論文 | 会議 | 手法 |
|---|---|---|
| ★[TS-Mamba](https://proceedings.iclr.cc/paper_files/paper/2026/hash/30079f848e3abbc9a0877bda33d5c612-Abstract-Conference.html)（Trajectory-aware Shifted SSM） | ICLR'26 | オンライン動画超解像。過去フレームから似たトークンを選んで軌跡を作り、軌跡に沿って Mamba で集約する。Hilbert 走査と shift で空間の連続性を補う |
| [Tracktention](https://openaccess.thecvf.com/content/CVPR2025/html/Lai_Tracktention_Leveraging_Point_Tracking_to_Attend_Videos_Faster_and_Better_CVPR_2025_paper.html) | CVPR'25 | 点追跡の軌跡に沿って特徴を集め、時間方向に attention をかける層。既存の画像モデルに差し込んで、動画の深度推定・カラー化の時間一貫性を上げる（SSM ではない） |
| [MVSSM](https://openaccess.thecvf.com/content/CVPR2026F/supplemental/Zhou_MVSSM_Motion-aware_Visual_CVPRF_2026_supplemental.pdf) | CVPR'26 Findings | 動画のぼけ除去。flow で隣のフレームの特徴を位置合わせし、動きの向きに合わせて SSM の走査方向を選ぶ。リンクは補足資料で、本文は未確認 |

### 11.3 B. 混ぜる：空間方向の混合・走査の順番

| 論文 | 会議 | 手法 |
|---|---|---|
| ★[TV3S](https://openaccess.thecvf.com/content/CVPR2025/html/Hesham_Exploiting_Temporal_State_Space_Sharing_for_Video_Semantic_Segmentation_CVPR_2025_paper.html) | CVPR'25 | 動画 semantic segmentation。空間パッチごとに時間方向の Mamba の state を持ち越し、shift で近傍パッチと混ぜる。V3 に最も近い構造 |
| [RS-SSM](https://arxiv.org/abs/2603.24295) | CVPR'26 | 動画 semantic segmentation。固定サイズの state が圧縮で細部を忘れる問題に対し、forget gate を反転・補正して細部を補う。TV3S と比較している |
| [Long-Context State-Space Video World Models](https://openaccess.thecvf.com/content/ICCV2025/html/Po_Long-Context_State-Space_Video_World_Models_ICCV_2025_paper.html) | ICCV'25 | 動画の world model。ブロック単位の SSM 走査で長期の記憶を持ち、隣のフレームとの整合は局所 attention で取る |

### 11.4 C. 内容で引く・state の更新則

| 論文 | 会議 | 手法 |
|---|---|---|
| [LiVOS](https://openaccess.thecvf.com/content/CVPR2025/html/Liu_LiVOS_Light_Video_Object_Segmentation_with_Gated_Linear_Matching_CVPR_2025_paper.html) | CVPR'25 | VOS の memory の照合を線形 attention に置き換え、固定サイズの行列 state として再帰的に更新する。データに応じた gate で、何を残すかを決める（Mamba の近縁） |
| [Gated DeltaNet](https://proceedings.iclr.cc/paper_files/paper/2025/hash/4904fad153f6434a7bcf04465d4be2cc-Abstract-Conference.html) | ICLR'25 | 言語モデル。gate（一気に忘れる）と delta rule（狙って上書きする）を組み合わせた Mamba2 の改良 |

### 11.5 D. 物体単位の state・Tracking × SSM

| 論文 | 会議 | 手法 |
|---|---|---|
| ★[HyperSSM](https://cvpr.thecvf.com/virtual/2026/poster/39868)（Hypergraph-State Collaborative Reasoning） | CVPR'26 | MOT の動き予測。動きの似た物体どうしを hypergraph で結び、SSM で時間方向を推論する。Kalman filter の置き換えにあたる |
| [MambaVLT](https://cvpr.thecvf.com/virtual/2025/poster/33167) | CVPR'25 | 言語付きの単一物体追跡。Mamba の state をフレーム間で持ち越し、参照特徴を更新する |
| [SambaMOTR](https://proceedings.iclr.cc/paper_files/paper/2025/hash/4a32a646254d2e37fc74a38d65796552-Abstract-Conference.html) | ICLR'25 | MOT。tracklet ごとの SSM の state を物体間で同期させる。不確かな観測を state の更新から外す（MaskObs）。前回紹介済み |
| [SMTrack](https://arxiv.org/abs/2602.01677) | TIP（ジャーナル） | 単一物体追跡。hidden state ごとに別の時間スケールを持たせた Mamba |
| [SUMO](https://arxiv.org/abs/2606.29861) | プレプリント | SAM 系のセグメンテーションに、非線形の状態空間フィルタ（Unscented filter）を組み合わせる。学習なし |

### 11.6 state・memory の汚染と、書き込みの制御

| 論文 | 会議 | 手法 |
|---|---|---|
| ★[Memory as Dynamics](https://icml.cc/virtual/2026/poster/65434) | ICML'26 | SAM2 ベースに、状態空間の latent world model による予測 memory を足す。遮蔽時などは信頼度で予測の寄与を抑える。修論に最も近い（9.2節） |
| ★[SENTRY](https://eccv.ecva.net/virtual/2026/poster/4693) | ECCV'26 | SAM2 系の追跡器。memory に書く前に、候補マスクを短い tracklet にして時間的な整合を検証する。学習なしで後付けできる |
| [Dual-Path Temporal Decoder](https://neurips.cc/virtual/2025/poster/117877) | NeurIPS'25 | end-to-end の MOT。query を更新する経路と、更新せずに過去を保つ経路を分け、信頼度が低いときは更新を止める |
| [DAM4SAM](https://openaccess.thecvf.com/content/CVPR2025/papers/Videnovic_A_Distractor-Aware_Memory_for_Visual_Object_Tracking_with_SAM2_CVPR_2025_paper.pdf) | CVPR'25 | SAM2 の memory を、直近の見た目用と、似た物体（distractor）を見分ける用に分ける。学習なし |
| [SAM2Long](https://openaccess.thecvf.com/content/ICCV2025/papers/Ding_SAM2Long_Enhancing_SAM_2_for_Long_Video_Segmentation_with_a_ICCV_2025_paper.pdf) | ICCV'25 | SAM2 の memory を複数の経路で持ち、木構造で良い経路を残す。1 回の誤りを memory に確定させない。学習なし |

### 11.7 SAM2 の拡張（その他）

| 論文 | 会議 | 手法 |
|---|---|---|
| [SAMURAI++](https://openaccess.thecvf.com/content/CVPR2026F/papers/Yang_Extending_Segment_Anything_Model_2_to_Multi-Object_Tracking_by_Optimizing_CVPRF_2026_paper.pdf) | CVPR'26 Findings | SAM2 を MOT に拡張する。短期の動きの memory と長期の物体の memory を分ける。DanceTrack・MOT17 で評価。学習なし |
| [EdgeTAM](https://openaccess.thecvf.com/content/CVPR2025/html/Zhou_EdgeTAM_On-Device_Track_Anything_Model_CVPR_2025_paper.html) | CVPR'25 | SAM2 の memory attention を、学習した少数の query で圧縮して軽くする。iPhone で 16 FPS |
| [SAMWISE](https://openaccess.thecvf.com/content/CVPR2025/html/Cuttano_SAMWISE_Infusing_Wisdom_in_SAM2_for_Text-Driven_Video_Segmentation_CVPR_2025_paper.html) | CVPR'25 | SAM2 を固定したまま、時間方向と言語の情報を入れる adapter を足す（約 4.9M パラメータ） |
| [SAM 3](https://proceedings.iclr.cc/paper_files/paper/2026/hash/e0982cbc81401df3430ee1ff780dc7a2-Abstract-Conference.html) | ICLR'26 | 名詞句などの概念で対象を指定できる。画像の検出器と、memory を使う動画の追跡器を組み合わせる |
