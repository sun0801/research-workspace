---
project: sam2-mamba-motion-tracking
date: 2026-07-17
experiment: statecarry-gt-input-mot-metrics
status: completed
---

# State Carry GT入力・毎epoch val・5epochごとMOT Metrics

## 条件

- sequence: `dancetrack0004`（1203 frames）
- 学習: 1動画GT trajectory、MambaStateful、100 epoch
- tracker入力: detector bboxではなくGT bbox
- val loss: 毎epoch
- MOT Metrics: epoch 5, 10, ..., 100（20回）
- Comet logging: 有効
- 外部ソースコード: 変更なし

Comet: [statecarry_dancetrack0004_gt_mot_comet_20260717](https://www.comet.com/sun0801/mamba-mot/6e0a1f00df3143e694ffecaab1c89cda)

## 結果

- validation loss: epoch 1 `0.1116693167` → epoch 100 `0.0651373799`
- HOTA: epoch 5 `12.175`、epoch 10〜100 `5.2655`
- DetA: epoch 10〜100 `79.895`
- AssA: epoch 10〜100 `0.34702`
- IDF1: epoch 10〜100 `0.46061`
- MOTA: epoch 10〜100 `59.703`

GT bbox入力でもDetAは約79.9ある一方、AssAとIDF1が極端に低く、HOTAは改善しなかった。detector bboxの誤差を除外してもtrack associationが成立していないため、State Carryの推論・状態伝播・track identity管理側の問題が主因と考えられる。

なお、lossは低下したが初期値の1/10以下には到達していない。そのため厳密には「完全な1動画過学習」ではなく、「loss低下中にもHOTAが改善しない」ことを示す結果である。
