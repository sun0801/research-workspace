---
date: 2026-11-13
project: sam2-mamba-motion-tracking
type: meeting-materials
status: recording
target_meeting: 2026-11-13
previous_meeting: 2026-11-06
notion_url: null
notion_export: null
tags: [meeting-materials, research]
---

# やったこと

## A-a（旧①-a）の宿題：optical flowの計算時間（11/11）

- 前回の宿題「flowをとりあえず計算して、計算量が高いと言えるか確かめる」の答え
- OpenCVのFarnebackとDIS（CPU）、深層学習のRAFT（GPU）を、MOSEの動画6本（速い3本・遅い3本）で測った

1フレームあたりのflowの計算時間

| 手法 | 1024×1024（SAM2の入力と同じ） | 256×256 |
|---|---|---|
| Farneback（CPU） | 247 ms | 15 ms |
| **DIS（最速の設定、CPU）** | **15 ms** | **0.9 ms** |
| RAFT small（GPU） | 91 ms | 37 ms |
| RAFT large（GPU） | 214 ms | 60 ms |
| 参考：SAM2（GPU、1物体・1フレーム） | 約30 ms | |

- CPUは1スレッド、GPUはRTX A4000。6本・120組の中央値
- **DISなら、計算量はA-aをやらない理由にならない**（SAM2の約30 msより短い）
- **GPUにしても速くはならなかった**：RAFTは精度重視の手法で、GPUでもDISより遅い

![](../experiments/figures/2026-11-11-optical-flow-cost/05-flow-moved-object.png)

- フレーム t の物体（黄）を、各手法のflowで動かした結果がオレンジ。次のフレームの本当の位置（水色の破線）に重なれば正しい
    - 速い車：Farnebackはほとんど動かない。DISは途中まで引き伸ばされる。RAFTはほぼ水色に重なる
    - ゆっくり動くバス：どの手法も重なる
    - 速さならDIS、質ならRAFT、と見ている
- 気になること
    - DISは向きは合うが、物体の後ろの背景にはみ出す
    - 速い物体で、DISが動きを小さく見積もるかどうかは、図の1例でしか見ていない。速い3本はどれも物体が画面の端から出入りする場面があり、正解マスクの重心の移動が実際の動きより小さく出るので、数値ではまだ比べられていない
    - flowと潜在表現のマス（64×64）との対応の取り方は、まだ考えていない（前回、後回しでよいと言われた）
- 詳細: [実験ログ](../experiments/2026-11-11-optical-flow-cost.md)
- **→ 相談：A-aは、A-bの改善が一段落してから入れるか、A-bと並行して比べるか**

# 次やること

-

---

## 記録メモ（仕上げで消す）

- 前回の宿題（11/6議事録の「次やること」）:
    - [ ] A-b（旧①-b）の対応付けを改善する（ノイズで形が崩れないように、空間的な制約などを入れる）
        - [ ] 対応付けのアルゴリズム（類似度最大、ハンガリアンマッチング、それ以外）を差し替えられる形にする
    - [x] optical flowを計算してみて、計算量と見た目を確かめる（A-a）
    - [ ] 英論文紹介の4本（MambaOut、TV3S、TS-Mamba、Memory as Dynamics）を読む
    - [ ] 修論を書く
    - [ ] 環境整備係: ウイルス対策ソフトの配布と案内、導入したマシンの管理、Macの一覧
- 記録したエントリ:
    - 11/11 A-aの宿題：optical flowの計算時間
    - 11/11 同上に追記：GPUのRAFTの時間と見た目、重心の移動との比較の限界
