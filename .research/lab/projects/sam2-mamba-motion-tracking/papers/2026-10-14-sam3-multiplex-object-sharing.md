---
date: 2026-10-14
project: sam2-mamba-motion-tracking
source: SAM 3論文 Appendix H と公式repoのコード読解
tags: [paper-note, sam3, multiplex, temporal-mamba]
---

# SAM 3.1 Object Multiplex の仕組みと temporal Mamba 設計への影響

## 背景

temporal Mambaの統合方法（V1〜V4）を検討する中で、「物体ごとの特徴が作られ、重さが物体数に比例する」問題が出た。とくにV3（FPN的）では、対象別の64段から128・256段へつなぐと、全段が対象別になる。これがSAM 3のmultiplexで解消するのかを確認した。8/28 MTGのTODO「SAM3のmultiplexおよびデコーダー統合位置、トークン数の変化を確認する」にも対応する。

## 要点

- multiplexでは、memoryの作成・memory attention・マスクデコーダを、物体ごとではなく **bucket（既定16物体）ごとに1回** 実行する。デコーダに入る画像特徴はbucketごとに1枚で、物体ごとの特徴マップは作らない。
- 物体の区別は、**slot番号ごとの学習済みembedding** で行う。物体の見た目から作るembeddingではなく、slotの位置に紐づく。
- そのため、temporal Mambaをデコーダ入力の特徴に置けば、stateはbucketごとになり、重さは物体数の約1/16で済む。
- 代わりに、1本のstateに最大16物体が混ざる。研究の軸である「trackごとのhidden stateが誤対応で汚れる」は、そのままの形では定義できなくなる。
- multiplexは関連モジュールまで含めて学習された仕組みで、SAM2の重みに後付けできない。導入は実質的にSAM 3.1へのベース乗り換えになる。

## 確認した事実

### 論文（arXiv 2511.16719, Appendix H）

- 元のSAM 3の追跡器はmemoryの処理を物体ごとに独立に行うため、計算量とメモリが物体数に比例する。
- multiplexは物体をM slotのbucketにまとめ（既定M=16）、memoryの作成と読み出しをbucketごとに1回行う。bucket単位のforward回数がO(N)からO(⌈N/M⌉)になる。
- 物体の情報を「(i) 共有の空間memory」と「(ii) 物体ごとのembedding」に分けて持つ。共有の空間memoryは、画像特徴とbucket内の（slotごとの）マスクをまとめて符号化して作る。
- 物体ごとのembeddingは、時間方向の対応付けのためにmemory bankに空間特徴と一緒に保存され、マスクデコーダにも渡される。
- Mux：物体の添字で並んだテンソルを、bucketとslotの添字で並んだテンソルに変換する。Demux：その逆変換。
- デコーダは各slotにつき5 token（mask token 3、IoU 1、物体スコア 1）を出し、bucketあたり5M token（M=16で80）。学習時はbucket内のslot番号をランダムに入れ替え、slotの並びに頑健にしている。
- 結果：VOSで7ベンチマーク中6つが改善（MOSEv1 78.4→79.6、MOSEv2 60.3→62.3）。速度は1物体で約7%遅く、2物体以上でSAM 3を上回り、128物体で5.2倍速い（H100）。

### 公式repo（facebookresearch/sam3、2026-10-06のcommit `0570b3a`）

- `sam3/model/multiplex_mask_decoder.py`：`B = image_embeddings.shape[0]` がbucket数。画像特徴は物体ごとに複製されず、mask tokenとIoU tokenがslotごとに用意される（`nn.Embedding(multiplex_count, ...)`）。物体ごとの追加embeddingは `extra_per_object_embeddings`（形状：bucket数 × multiplex_count × C）としてmask tokenに足される。
- `sam3/model/memory.py`：mask encoderの入力チャネル数が `multiplex_count`。16物体のマスクを16チャネルに重ねて入れ、bucketごとに1枚のmemoryを作る。
- `sam3/model/video_tracking_multiplex.py`：物体ごとのembeddingは `obj_cond_embed` などの `nn.Parameter(multiplex_count, hidden_dim)` で、slot番号ごとに用意される。
- `sam3/model/multiplex_utils.py`（`MultiplexState`）：
  - 新しい物体は、既存bucketの空きslot（padding）に先に入る。空きがなければ新しいbucketを作る。
  - 消えた物体のslotは「removed」になり、空きslotとは区別される。追加処理は空きslotしか埋めないので、removedのslotは再利用されない。
  - bucket内の全slotがremovedか空きになると、そのbucketは削除される。
  - つまり、物体のslotは生存中は固定されるが、bucketの顔ぶれは物体の追加によって途中で変わる。

## temporal Mamba設計への影響（推測を含む）

| 観点 | multiplexを使う場合 | 今のSAM2ベース（対象別） |
|---|---|---|
| Mambaのstateの単位 | bucketごと（最大16物体で共有） | 対象ごと |
| 重さ | 物体数の約1/16 | 物体数に比例 |
| V3で段をつなぐ問題 | 全段をbucket単位でそろえられる | 64段が対象別なら全段が対象別 |
| 研究の問い | 共有stateで、1物体の誤対応が同じbucketの他の物体へ波及するか | trackごとのstateが誤対応で汚れるか（現在の軸） |
| 導入コスト | SAM 3.1へのベース乗り換え。MOSEの学習とSAM2MOTの比較を作り直す | 現状のまま |

- 「共通の空間特徴＋物体ごとのembedding」という分け方は、10/9の図の位置a（共有のimage embedding）と同じ発想で、SAM2のまま共有特徴にMambaを置く案の根拠として使える。
- bucketの顔ぶれが途中で変わると、共有stateの意味がずれる可能性がある（未検証）。

## 当面の扱い（提案。未決定）

- 中間発表とViEW（10/30締切）の直前なので、ベースの乗り換えはしない。今のSAM2ベースで対象別のまま進める。
- multiplex（共有state）は「計算量の対策」「将来の拡張」として、10/16 MTGで先生に話題として出す。

## 未確認事項

- 物体ポインタ（obj_ptr）がmultiplexでどう扱われるか（bucket化されるのか、物体ごとに残るのか）。
- memory attention内部で、slotごとのembeddingがどこに足されるかの細部。
- SAM 3.1の推論でbucketの割り当てが動画中にどれくらい変わるか（実測していない）。

## 出典

- [SAM 3: Segment Anything with Concepts（arXiv 2511.16719, Appendix H）](https://arxiv.org/pdf/2511.16719)
- [facebookresearch/sam3](https://github.com/facebookresearch/sam3)（commit `0570b3a5be9c4e694f23d85232fb55f4a6f1f7fc`）
- [RELEASE_SAM3p1.md](https://github.com/facebookresearch/sam3/blob/main/RELEASE_SAM3p1.md)
- 関連：[8/28 MTG議事録](../meetings/2026-08-28-mtg.md)、[temporal Mamba統合候補の図](../materials/figures/2026-10-14-temporal-mamba-variants/manifest.md)
