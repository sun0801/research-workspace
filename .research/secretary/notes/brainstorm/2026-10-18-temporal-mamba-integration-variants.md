---
date: 2026-10-18
project: sam2-mamba-motion-tracking
source_todo: temporal MambaのV3（FPN的な統合）を試して形にする（10/14 MTG）／統合方法の候補（FPN的な階層的統合など）を並行して試す（10/9 MTG）
topic: temporal Mamba統合方法の候補整理とV3から始める進め方
status: exploratory
tags: [brainstorm, research, temporal-mamba, sam2, architecture]
---

# temporal Mamba統合方法の候補整理とV3から始める進め方

2026-10-13〜18の壁打ちをまとめたもの。

## 読み込んだ文脈

- プロジェクトREADME：10/9 MTGでtemporal Mambaは探索フェーズとし、LR設定を直したうえで複数の統合方法を並行して試す方針になった。
- [10/9 MTG議事録](../../../lab/projects/sam2-mamba-motion-tracking/meetings/2026-10-09-mtg.md)：MOSEのF1はadapterのLR（5e-6）が小さすぎて実質学習されていなかった。
- [10/14 MTG議事録](../../../lab/projects/sam2-mamba-motion-tracking/meetings/2026-10-14-mtg.md)：V3（FPN的な統合）から始め、難しければ他の案に移る。来週までにある程度形にする。4段階の進め方とGPUの優先順位は議論していない。
- [9/30 MTG議事録](../../../lab/projects/sam2-mamba-motion-tracking/meetings/2026-09-30-mtg.md)：「FPNなどを工夫し、サイズを削減せずに入れる可能性」（当日メモ）。
- [10/9の画像側設計候補](2026-10-09-temporal-mamba-image-side-design-options.md)（挿入位置a〜d、表現①〜⑤）
- [MOSE追加学習の実験ログ](../../../lab/projects/sam2-mamba-motion-tracking/experiments/2026-09-30-mose-temporal-mamba-finetuning.md)、SAM2 repo `dev`の `sam2/modeling/temporal_mamba_adapter.py`、`sam2_base.py`、`training/mose_fulltrack.py`、公式の `sam2.1_hiera_b+_MOSE_finetune.yaml`（読み取りのみ）
- [SAM 3.1 multiplexの論文メモ](../../../lab/projects/sam2-mamba-motion-tracking/papers/2026-10-14-sam3-multiplex-object-sharing.md)

## 相談の出発点

「統合方法の候補（FPNのような階層的統合など）を並行して試す」が未着手。どう進めるかを決めたい。

## 対象TODO

- [ ] FPNのような階層的統合など、temporal Mambaの統合方法の候補を並行して試す（10/9 MTG）
- [ ] temporal MambaのV3（FPN的な統合）を試し、来週までにある程度形にする（10/14 MTG）

## 問い

- 空間情報をどう保ってMambaに渡すか。どの案から試すか。
- 1回の本学習に約17時間かかるなか、複数案をどう比べるか。
- 「時間方向の記憶が効いた」と言うには、何と比べればよいか。

## アイデア候補

候補をV1〜V4に整理した（図：[2026-10-14-temporal-mamba-variants](../../../lab/projects/sam2-mamba-motion-tracking/materials/figures/2026-10-14-temporal-mamba-variants/manifest.md)）。挿入位置はすべて現行のb（対象別の `pix_feat`。V3は高解像度特徴も含む）。

| 案 | 内容 | 位置づけ |
|---|---|---|
| V1 1 token | 空間平均した1ベクトルをMambaに入れ、全マスに同じ値を足す（現行） | 対照 |
| V2 縮約グリッド | 16×16〜64×64に縮めた各マスを独立した時系列にする。64×64にすると10/9の図の②（全位置）にあたるので、②はV2の設定として扱う | 本命 |
| V3 FPN的 | 64・128・256の各段でMambaを回し、段どうしをつなぐ。つなぎ方は(a)出力をつなぐ・(b)stateをつなぐ・(c)後で合成 | 本命（10/14 MTGで最初に試すと決定） |
| V4 時空間scan | フレーム内の全マスを1列に並べて読み、フレーム末のstateを次へ渡す（Vim/VMamba/VideoMamba系） | 本命 |

経緯：
- 最初はV3を「粗い段だけでMambaを回し、細かい段には拡大して足す」と解釈した。しかし9/30の「サイズを削減せずに」と合わないため、ユーザーの記憶（各段でMambaを回し、Mamba同士の関係も学習する）に合わせて差し替えた。
- 時空間scanは当初「重い・実装が大変・解釈しにくい」として外した。しかし、Vision Mambaでは標準的な作りであり、学習時のscanは並列計算され、stateリセット版がVMamba型の対照になる、という指摘を受けて本命に戻した。
- 位置a（Memory Attentionの前の、全対象で共通の特徴）は、余裕があれば試す。

## 仮説候補

- 空間情報を保つ表現（V2〜V4）のほうが、1 token（V1）より時間情報がマスク品質に効く（未検証）。
- V3で時間方向の記憶が効くなら、stateを持ち越した版が毎フレームリセットした版を上回る（未検証）。
- 場所ごとにstateを持つ表現は、物体が動くとstateがずれる。粗い段（V2の粗いグリッド、V3の上の段）やフレーム内での混合（V4）がそれを和らげる（未検証）。

## 実験・実装案

- 共通の枠 `TemporalAdapterBase`（`init_state` / `step` / `reset`、出力は `特徴 + α・残差`）を作り、token化の部分だけ差し替える。
  - `MambaCell`：今の `_mamba_training_step` を切り出す。マスをbatch次元に畳めば空間版にも使える。
  - V1 `GlobalPoolAdapter`、V2 `GridAdapter(g)`、V3 `PyramidAdapter`、V4 `SpatioTemporalScanAdapter`。
  - V3は `high_res_features` も受け取って書き換えるので、`sam2_base.py` の呼び出し部分を広げる必要がある。
  - V4は並列scanに初期stateを渡す必要がある（Mamba2のchunk scanが候補。`mamba-ssm 2.2.2` で使えるかは未確認）。
- 段階的に絞る：段階0（LR修正の確認）→ 段階1（共通化とVRAM・速度の実測）→ 段階2（SAM2本体を固定してadapterだけを短く学習し、比べる）→ 段階3（上位案だけ本学習）。
- 学習の高速化（今の学習は0.30秒/フレーム、F1は1周で16.8時間）：
  - 測定：CPUのデータ読み込みだけで約0.14秒/フレーム。メインスレッドで同期的に読んでいるので、その間GPUが待っている（1動画60フレームで測定）。
  - SAM2公式はDataLoaderのworker 10個、clip単位でのまとめ計算、`freeze_image_encoder` を持つ。今のスクリプトは軌跡全体のTBPTT用に書き直した際にこれらが抜けている。
  - 取り入れる候補：①先読み、②SAM2本体を固定し、画像エンコーダは `no_grad` でTBPTTの区間ごとにまとめて計算、③フレームごとの同期の削減。

## 比較・評価軸

- F0（adapterなし）との差：adapterを足した価値
- stateを持ち越した版と毎フレームリセットした版の差：時間方向の記憶が効いたか
- V1との差：空間情報を保った効果
- VRAMと速度（32GBに収まるか）

## 今回見えた方向性

- 10/14 MTGの決定に合わせて、V3から始める。最初のspecで扱うのはV3と比較相手（F0、V3のリセット版、V1）だけ。V2とV4は後で別specにする。
- スクリーニングでは、SAM2本体をF0で固定し、adapterだけを学習する。学習の高速化も同じspecに入れる。
- 評価はtuningの313対象でJ&Fを測る。成功の目安は「V3 > F0」かつ「V3 > V3のリセット版」（動画単位のpaired bootstrapの95%信頼区間に0を含まない）。lockboxは使用済みなので、使う場合は探索的な扱い。
- SAM 3.1のmultiplexは、物体ごとに特徴を持つ重さを解消する。ただし、trackごとのstateという研究の軸が成り立たなくなり、ベースの乗り換えも必要になる。当面はSAM2ベースで考える。

## 次アクション候補

1. V3のspecをPlan mode相当で計画し、承認を得て `specs/` に保存する。
2. 承認後、Implementation Gateを確認して実装と段階0〜1に入る。
3. 10/9の図の位置aとの比較は、V3の結果を見てから検討する。

TODOには自動追加していない。

## Spec化候補

- V3（FPN的な統合）のMOSE adapter学習：SAM2本体をF0で固定、V1とV3のリセット版を対照にする、学習の高速化①〜③も含める、段階0〜1の判定ルールを入れる。

## 未解決の問い

- 先生の「FPN的」の意図が、各段でMambaを回してつなぐ形で合っているか（10/14 MTGでは詳細を確認していない）。
- V3の256段がVRAMに収まるか（未実測）。
- adapterのLR、warmup、初期化の具体値（段階0で決める）。
- V4に使う並列scanに、初期stateを渡せるか。
- 位置a（共有特徴）を研究の主張の中でどう位置づけるか。

## 関連ファイル

- [V1〜V4の図とmanifest](../../../lab/projects/sam2-mamba-motion-tracking/materials/figures/2026-10-14-temporal-mamba-variants/manifest.md)
- [10/9の画像側設計候補](2026-10-09-temporal-mamba-image-side-design-options.md)
- [10/14 MTG議事録](../../../lab/projects/sam2-mamba-motion-tracking/meetings/2026-10-14-mtg.md)
- [MOSE追加学習の実験ログ](../../../lab/projects/sam2-mamba-motion-tracking/experiments/2026-09-30-mose-temporal-mamba-finetuning.md)
- [SAM 3.1 multiplexの論文メモ](../../../lab/projects/sam2-mamba-motion-tracking/papers/2026-10-14-sam3-multiplex-object-sharing.md)
- [V3のspec（2026-10-18承認）](../../../lab/projects/sam2-mamba-motion-tracking/specs/2026-10-18-temporal-mamba-v3-mose-adapter-spec.md)
