---
project: sam2-mamba-motion-tracking
created: 2026-09-03
last_updated: 2026-09-03
tags: [mot, boxmot, ocsort, visualization, lab-tour]
---

# BoxMOTによるMOT紹介動画の生成記録

## 目的

研究室見学用に、MOT17の比較的規則的な歩行者シーンと、DanceTrackの複雑な人物動作・接近を、同じOC-SORTベースの追跡表示で比較できる全編動画として用意した。

## 実行条件

- リポジトリ: `/mnt/HDD10TB-2/aburatani/2026_04_aburatani_boxmot`
- detector: `models/yolov8n.pt`
- ReID model: `models/osnet_x0_25_msmt17.pt`
- tracker: `ocsort`
- 対象クラス: `0`（person）
- 描画: `--show-trajectories --save --save-txt`
- GPU: CUDA device 0
- BoxMOTのソースコードは変更していない

## 成果物

### MOT17（推奨: 比較的追跡しやすい例）

- 動画: `/mnt/HDD10TB-2/aburatani/2026_04_aburatani_boxmot/runs/mot-demo/mot17-02-fcnn-ocsort/img1_tracked.mp4`
- TXT: `/mnt/HDD10TB-2/aburatani/2026_04_aburatani_boxmot/runs/mot-demo/mot17-02-fcnn-ocsort/img1.txt`
- 入力: `MOT17-02-FRCNN/img1`
- 600フレーム、1920x1080、30 fps、20秒
- TXT: 2,581行、28追跡ID、全600フレームに追跡結果あり
- 発表では、人物が継続して同じ色・IDで追跡される例として使用する

### DanceTrack（推奨: 難しい条件の例）

- 動画（20 fps補正版）: `/mnt/HDD10TB-2/aburatani/2026_04_aburatani_boxmot/runs/mot-demo/dancetrack0081-ocsort/img1_tracked_20fps.mp4`
- BoxMOT生成元（30 fps）: `/mnt/HDD10TB-2/aburatani/2026_04_aburatani_boxmot/runs/mot-demo/dancetrack0081-ocsort/img1_tracked.mp4`
- TXT: `/mnt/HDD10TB-2/aburatani/2026_04_aburatani_boxmot/runs/mot-demo/dancetrack0081-ocsort/img1.txt`
- 入力: `dancetrack0081/img1`
- 984フレーム、1280x720、20 fps、49.2秒
- TXT: 6,344行、72追跡ID、979フレームに追跡結果あり、最大17 ID/フレーム
- GTとのIoU 0.5以上の対応を使った確認では、同一追跡IDが別GT人物へ移るイベントを168件確認した
- 特にフレーム172付近（20 fps換算で約8.6秒）から前後は、接近・重なりとID切替を確認する候補区間
- これは特定の社会応用を再現する動画ではなく、複雑な動き・接近時に追跡が難しくなる例として扱う

補助候補として、`dancetrack0063-ocsort/img1_tracked_20fps.mp4`（1000フレーム、1920x1080、20 fps、50秒）も生成済みである。ただし、発表用の第一候補は人物数・接近が多い0081とする。

## 検証

- MOT17動画: 600/600フレーム、30 fps、20秒
- DanceTrack 0081補正版: 984/984フレーム、20 fps、49.2秒
- 元画像と描画動画の同一フレーム差分を確認し、色付きのBBox・ID・軌跡描画が動画に入っていることを確認した
- 生成動画はBoxMOTリポジトリ内の `runs/mot-demo/` に置いており、研究ワークスペースへ大容量動画を複製していない

## 注意

MOT17とDanceTrackは撮影条件・解像度・人物数なども異なるため、発表ではデータセット間の性能比較とは言わず、「比較的規則的な例」と「複雑な条件の例」を同じ表示形式で示す説明に限定する。DanceTrack 0081のID切替イベント数は、発表用区間選定の補助指標であり、正式なMOT評価値ではない。


## 追加推論候補

DanceTrackの追加候補（20 fps補正版）:
- dancetrack0041-ocsort/img1_tracked_20fps.mp4: 1003フレーム、TXT 3007行、66 ID
- dancetrack0079-ocsort/img1_tracked_20fps.mp4: 1202フレーム、TXT 5780行、66 ID
- dancetrack0090-ocsort/img1_tracked_20fps.mp4: 1004フレーム、TXT 5933行、55 ID

ID切替候補イベント（GTとのIoU 0.5以上の補助集計）は、0081が168件、0090が116件、0041が69件、0079が67件、0063が55件。まず0081と0090を目視比較する。MOT17では04・09・13も追加生成済み。
今回の追加推論では、MOT17のFRCNN版全7系列（02, 04, 05, 09, 10, 11, 13）が揃った。DanceTrackは0014・0094・0073・0034・0047を追加し、全10系列の比較候補とした。追加5系列の切替候補イベントは、0014が102件、0034が102件、0047が90件、0094が31件、0073が7件である。


## 軌跡なし版

既存の17系列について、`--show-trajectories` を付けずに再推論したBBox・IDのみの動画を `runs/mot-demo/*-ocsort-bbox-only/` に保存した。MOT17は30 fps、DanceTrackは全フレーム保持の20 fps補正版を生成済みで、17系列すべてMP4/TXTの存在とフレーム数を検証済みである。
