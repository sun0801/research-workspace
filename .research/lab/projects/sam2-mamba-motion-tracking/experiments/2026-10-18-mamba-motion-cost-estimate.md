---
date: 2026-10-18
project: sam2-mamba-motion-tracking
type: experiment-log
status: completed
tags: [cost, speed, mamba-stateful, midterm]
---

# 手法1の動き予測（Mamba）の計算コストの目安

中間発表の想定質問「計算コスト・速度は？」に答えるための簡易な見積もり。SAM2・SAMURAI と同じ条件で FPS を測り直したものではない。

## 測ったもの

| 項目 | 値 | 方法 |
|---|---|---|
| Mamba（動き予測器）のパラメータ数 | 1,381,892（約138万） | `epoch100.pth` を `MambaStateful` に strict load して数えた |
| SAM2.1 tiny のパラメータ数 | 38,962,754（約3,900万） | `checkpoints/sam2.1_hiera_tiny.pt` の重みを数えた |
| Mamba 1ステップ（1物体・1フレーム）の時間 | 約 2.3 ms | RTX PRO 4500 Blackwell、B ＝ 1、推論キャッシュを使った1トークン入力を1,000回平均（Python のオーバーヘッド込み） |
| Mamba の GPU メモリ（ピーク） | 約 15 MB | 上の計測時の `max_memory_allocated`（モデルと推論キャッシュ） |
| 物体1つあたりの状態 | 3層 × (512×4 ＋ 512×16) ＝ 30,720 個の値（fp32 で約 120 KB） | 重みの形から計算 |

## 全体の実行時間（表の Ours（state）の実行，7/23）

- 出力ファイルの時刻から、25系列（25,508フレーム、出力した枠 241,284個）の推論に約3時間38分（07:51 → 11:29）かかった。全体で約 1.9 フレーム/秒（候補の debug CSV の書き出しを含む。使った GPU は記録に残っていない）。
- Mamba の時間（約 2.3 ms × 約24万 物体・フレーム ≈ 約9分）は、全体の約4%と見積もれる。計算の大部分は SAM2 側。
- SAM2・SAMURAI の結果ファイルは別の場所から写したもので、実行時間が分からない。手法どうしの FPS の比較は、同じ GPU・同じ条件で測り直す必要がある。
