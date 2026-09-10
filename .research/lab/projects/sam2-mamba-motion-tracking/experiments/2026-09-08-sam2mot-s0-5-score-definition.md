---
date: 2026-09-08
project: sam2-mamba-motion-tracking
status: completed
tags: [experiment, sam2mot, reproduction, s0-5, score-definition, dancetrack]
---

# SAM2MOT再現 S0.5: logitスコア定義の実測

## 目的

SAM2MOT論文の状態閾値 `τ_r=8.0 / τ_p=6.0 / τ_s=2.0` が SAM2 のどのスコアを指すのかを実測で同定する。論文に記載がなく（SPEC の A2）、ここを誤ると後続の全段階が無意味になるため S1 の前に実施した。

## 実験条件

- 対象: DanceTrack val の dancetrack0026（13体）・dancetrack0043（9体）・dancetrack0079（9体）
- フレーム上限 300/系列、計 785フレーム・8269レコード
- SAM2.1-large（`sam2.1_hiera_large.pt`）、標準の multi-object モード
- プロンプトは各系列 frame 1 の GT box。**スコア分布の実測が目的で、追跡性能の評価ではない**
- GPU: RTX PRO 4500 Blackwell、peak 6.00 GiB
- 候補: `object_score_logits` / `mask_logit_max` / `mask_logit_mean` / `mask_logit_posmean`

## 判定基準

当初「reliable比率が支配的か」で判定するスクリプトを書いたが、これは discriminative ではなく誤った結論（`mask_logit_max` を最良と判定）を出したため棄却した。代わりに3基準を用いた。

- **C1 閾値配置**: 論文の3閾値が分布の意味のある範囲に散るか。3つとも裾に固まる候補は、論文がその設計を選ぶ動機がない
- **C2 遮蔽応答**: 遮蔽時にスコアが低下し、かつ状態境界を跨ぐか。論文の Object Removal はスコア低下による状態降格を前提とするため必須
- **C3 SAM2の意味論**: 論文の "SAM2 outputs a confidence (logit) score for each mask" が指すのは、SAM2が公開する正規の信頼度か派生統計量か

## 結果

| 候補 | τ_s=2.0 | τ_p=6.0 | τ_r=8.0 | C1 | C2（非遮蔽→遮蔽 p50） | C3 | 総合 |
|---|---|---|---|---|---|---|---|
| `object_score_logits` | p10.4 | p42.4 | p66.3 | ○ | ○ 7.59→5.28（pending→suspicious） | ○ ネイティブ | **適合** |
| `mask_logit_posmean` | p1.5 | p24.3 | p43.7 | ○ | ○ 9.62→7.50（reliable→pending） | × 派生量 | 適合（次点） |
| `mask_logit_max` | p0.0 | p1.1 | p3.5 | × 裾に集中 | × 状態不変 | × 派生量 | 棄却 |
| `mask_logit_mean` | p100 | p100 | p100 | × | × 逆方向 | × 派生量 | 棄却 |

遮蔽レコード（他オブジェクトとの mask IoU > 0.8）は 2586/8269（31.27%）。マスク消失（`NO_OBJ_SCORE = -1024.0`）は 106件（1.28%）で分布集計から除外した。

## 解釈

`object_score_logits` を A2 の確定値として採用する。3基準すべてを満たす唯一の候補である。

補強材料として、`sam2/sam2/sam2_video_predictor.py:475-479` は `object_score_logits` の placeholder 既定値を **10.0** とし、コメントに "assuming the object is present as sigmoid(10)=1" と記している。論文の τ_r=8.0 はこのスケール（存在≒10）のすぐ下に位置する。

旧 sam2mot_lite が採用していた `mask_logit_posmean` も C1・C2 は満たすため、後続段で差分が論文と合わない場合の切替先として残す。旧実装が閾値を 2.0/0.0/−2.0 に置き換えていたのは、この定義確定を飛ばしたためと解釈できる。

## 注意

- 3系列・上限300フレームのみ。val 25系列全体ではない
- 4状態の比率（`object_score_logits` で reliable 32.5%）は判定に使っていない。frame 1 のみのプロンプトで Quality Reconstruction による再プロンプトがないため、トラックが回復せず劣化し続ける条件になっている。実際の SAM2MOT では Q-R により reliable 比率は上がる
- 遮蔽判定は mask IoU > 0.8 の代理指標であり真の遮蔽ラベルではない
- SPEC の A1（per-instance か batched か）の検証ではない。本計測は標準の batched モード

## 成果物

- `/mnt/HDD10TB-2/aburatani/2026_05_aburatani_sam2mot/sam2mot_repro/logs/s0_5_score_distribution.md`（レポート）
- 同 `logs/s0_5_score_records.csv`（生データ 8269行）
- 同 `scripts/s0_5_score_distribution.py`（計測）、`scripts/s0_5_analyze.py`（解析・推論不要）

## 次

SPEC の S0（Co-DINO-L 導入と検出ファイル生成）へ。S1 baseline は検出ファイルが揃ってから。
