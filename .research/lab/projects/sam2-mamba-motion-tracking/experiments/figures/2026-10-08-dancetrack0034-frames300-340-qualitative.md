# DanceTrack 0034の手法別定性動画

- 対象フレーム: 300〜340（41フレーム）
- 再生速度: 10 fps（元動画は20 fps）
- クロップ: 全41フレームに同じ範囲（x=400〜900、y=330〜990、500×660 px）を適用。
- 入力: DanceTrack validationの元画像と、各手法の既存MOT推論結果
- GT: GT ID 9の矩形を緑枠で表示。IDラベルは表示しない。
- 推論結果: 各フレームでGT ID 9とのIoUが最大の予測矩形を1つ表示する。枠とラベルの色は3手法で統一する。
- IDラベル: `ID 9`は比較対象（GT ID 9）を指す表示用ラベルであり、各推論結果に記録されたtracker IDではない。予測矩形はフレームごとのIoU最大対象なので、tracker IDの継続性を示すものではない。
- 色: GT枠は緑。推論枠と`ID 9`ラベルは全手法で同じ水色。
- それ以外の推論対象、タイトル、ヘッダー、パネルは表示しない。

| 手法 | 動画 |
|---|---|
| SAM2 | [2026-10-08-dancetrack0034-frames300-340-sam2-cropped.mp4](2026-10-08-dancetrack0034-frames300-340-sam2-cropped.mp4) |
| SAMURAI | [2026-10-08-dancetrack0034-frames300-340-samurai-cropped.mp4](2026-10-08-dancetrack0034-frames300-340-samurai-cropped.mp4) |
| Mamba-state | [2026-10-08-dancetrack0034-frames300-340-mamba-state-cropped.mp4](2026-10-08-dancetrack0034-frames300-340-mamba-state-cropped.mp4) |
