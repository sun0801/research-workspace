---
date: 2026-09-03
project: sam2-mamba-motion-tracking
source: brainstorm
status: draft
tags: [spec, visualization, mot, boxmot, ocsort]
---

# BoxMOTによるMOT定性的デモ動画生成 Spec

## 目的

研究室見学用に、BoxMOTのOC-SORTを用いたMOT17・DanceTrackの全編追跡動画を生成する。
比較的IDを維持できる例と、交差・遮蔽などでID Switchが起きる例を提示し、MOTの難しさを専門外の参加者にも直感的に説明できる状態にする。

## 背景

研究室見学では、MOTの手法や性能値を詳細に説明するのではなく、人物追跡が社会で利用されていること、しかし複雑な動きや環境では同一人物のID維持が難しくなることを短時間で伝える。

現在作成中の研究用Mambaトラッカーでは、MOT17で明確に安定した例をすぐに用意できないため、既存の標準的な追跡器であるOC-SORTをデモ生成用ベースラインとして利用する。

BoxMOTの結果は研究性能の主張には使わず、MOTの難しさを説明するための定性的な代表例として扱う。

## 検証したい問い

同一のOC-SORT設定でMOT17とDanceTrackを処理したとき、比較的IDを維持しやすい条件と、交差・遮蔽・急な方向転換によってID維持が難しい条件を、動画上で分かりやすく示せるか。

## 仮説

MOT17の比較的規則的な動きを含む系列ではIDが安定して維持される一方、DanceTrackの複雑な動きを含む系列では、人物の検出が継続していても交差・遮蔽後にID Switchが観察できる。

## 実験・実装内容

### 使用リポジトリ

- BoxMOT: `/mnt/HDD10TB-2/aburatani/2026_04_aburatani_boxmot`
- 既存の未コミット変更 `boxmot/trackers/tracker_zoo.py` は変更しない
- BoxMOTのソースコードへの機能追加は行わない

### 使用モデル・追跡器

- 検出器: BoxMOT内の `models/yolov8n.pt`
- ReID: BoxMOT内の `models/osnet_x0_25_msmt17.pt`
- トラッカー: `ocsort`
- 対象クラス: person（YOLOクラスID 0）
- 追跡設定: 初期段階ではデフォルト設定、チューニングなし
- MOT17・DanceTrackで同じ検出器・トラッカー・可視化設定を使用する

### 使用データ

- MOT17: ローカルの `dataset/MOT17/train` にある画像系列
  - 同じ映像の重複を避けるため、初回の候補生成では各系列のFRCNN版を使用する
  - まず `MOT17-02-FRCNN` を動作確認用候補とする
- DanceTrack: ローカルの `dataset/DanceTrack/val/val` にある25系列
  - まず `dancetrack0063` を動作確認用候補とする
- 全編を処理し、発表用の区間切り出しは動画生成後に行う

### BoxMOTの可視化・保存

BoxMOT標準機能を使用する。

- `--show-trajectories`: 過去の軌跡を表示
- `--save`: ID付きBBoxと軌跡を重ねたMP4を保存
- `--save-txt`: MOT形式の追跡結果を保存
- IDごとの色はBoxMOTのIDベースの決定的な色生成を使用する

実行例:

```bash
boxmot track \
  --detector models/yolov8n.pt \
  --reid models/osnet_x0_25_msmt17.pt \
  --tracker ocsort \
  --source <sequence>/img1 \
  --classes 0 \
  --show-trajectories \
  --save \
  --save-txt \
  --project runs/mot-demo \
  --name <sequence-name>
```

### FPSの扱い

BoxMOTの現行動画保存処理は出力FPSを30に固定しているため、MOT17はそのまま使用する。
DanceTrackは元データが20 FPSなので、生成後に全フレームを保持したまま20 FPS相当の再生速度へ補正する。補正後のFPSとフレーム数は `ffprobe` で確認する。

## 比較対象・ベースライン

OC-SORTをMOT17とDanceTrackの両方に適用する。

これは科学的なデータセット間性能比較ではなく、同一のベースラインを用いた説明用の代表例の生成である。MOT17とDanceTrackのデータセット差による影響があるため、「MOT17は簡単でDanceTrackは難しい」と一般化せず、以下のように説明する。

> OC-SORTによる代表例として、比較的IDを維持しやすい条件と、ID Switchが起きやすい条件を示している。

## 評価指標

### 定量的な候補選定

- HOTA
- IDF1
- IDSW
- 検出の継続性

### 目視確認

- MOT17: 一定時間、同じ人物に同じIDが維持されるか
- DanceTrack: 検出漏れだけでなく、交差・遮蔽・急な方向転換後にID Switchが起きているか
- BBox、ID、色、軌跡が動画上で視認できるか
- 追跡失敗の原因を説明できる画面になっているか

## 成功・失敗の判断基準

### 成功

- MOT17に、比較的安定してIDを維持する全編動画が1本以上ある
- DanceTrackに、人物の検出は概ね継続しているが、交差・遮蔽後に明確なID Switchが起きる全編動画が1本以上ある
- 両データセットの動画で、ID別の色・BBox・軌跡を確認できる
- 各動画について、データセット名、系列名、フレームレート、検出器、トラッカー、実行条件を記録できる

### 失敗時の代替

- DanceTrackでOC-SORTの明確なID Switchが見つからない場合、同じ選定基準のまま別のモーションベースライン（SORTまたはByteTrack）を候補に加える
- 実データで説明に適した自然な失敗例が得られない場合、実データの軌跡を用いたID Switch模式動画を別案として検討する
- 模式動画を使う場合は、実際の追跡器の出力ではなく「概念説明用」と明記する

## 実施手順

1. BoxMOT用の独立したPython環境を準備する
2. `MOT17-02-FRCNN` と `dancetrack0063` を全編処理して、入力・検出・保存の動作を確認する
3. MOT17のFRCNN系列とDanceTrack val系列を必要な範囲で全編処理する
4. BoxMOTの追跡動画とMOT形式TXTを `runs/mot-demo/` 以下へ保存する
5. HOTA、IDF1、IDSW、検出継続性から代表候補を絞る
6. 候補動画を目視し、MOT17の安定例とDanceTrackのID Switch例を確定する
7. DanceTrack動画のFPSを補正し、フレーム数・再生時間を確認する
8. 発表用スライドには、データセット名・トラッカー名・代表例であることを明記する

## 成果物

- MOT17の全編追跡動画
- DanceTrackの全編追跡動画
- 各動画に対応するMOT形式追跡結果TXT
- 候補選定用のHOTA・IDF1・IDSW等の記録
- 使用系列、実行条件、FPS補正内容を記したメタデータ
- 研究室見学スライドに使用する区間の候補

生成動画は大容量になるため、当面はBoxMOTリポジトリの `runs/mot-demo/` に保存し、Gitには追加しない。最終的に採用する動画や補足情報の保存先は、容量を確認したうえで `materials/` と調整する。

## リスク・懸念

- YOLOv8nの検出漏れが多いと、ID追跡の難しさではなく検出器の弱さを示す動画になる
- MOT17とDanceTrackは動き以外の条件も異なるため、データセット間の厳密な因果比較には使えない
- BoxMOTの現行実装では `--fps` の指定が動画保存処理に反映されないため、DanceTrackの再生速度補正が必要
- BoxMOTのPython環境が未準備で、PyTorch・OpenCV等の依存関係を追加する必要がある
- 全系列の処理はGPUメモリ・処理時間を要する可能性がある

## 未決事項

- 最終的に発表へ採用するMOT17・DanceTrackの系列名
- DanceTrackで採用するFPS補正方法
- OC-SORTで明確な失敗例が得られない場合に追加するベースライン
- 動画・TXT・メタデータの最終的な研究ワークスペースへの保存方法

## 関連ファイル

- [研究プロジェクトREADME](../README.md)
- [2026-08-28 MTG議事録](../meetings/2026-08-28-mtg.md)
- [研究室見学用PowerPoint](../materials/2_物体追跡.pptx)
- [BoxMOT README](/mnt/HDD10TB-2/aburatani/2026_04_aburatani_boxmot/README.md)
