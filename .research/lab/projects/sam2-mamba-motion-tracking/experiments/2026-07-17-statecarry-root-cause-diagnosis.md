# State Carry GT入力HOTA低下の根本原因診断

## 結論

GT bbox入力でもHOTAが低い原因は、Mambaのmotion predictionをIoU対応付けの主位置として直接使う推論設計である。検出器・TrackEval・Mamba cacheの数値不安定性は、今回のepoch100 GT checkpointにおける主因ではない。

## 条件

- sequence: DanceTrack `dancetrack0004`（1203 frames、GT IDs 4）
- checkpoint: GT入力・single-video学習の`epoch100.pth`
- evaluator: 同一GT/TrackEval設定

## 結果

| 対応付けに使う位置 | HOTA | DetA | AssA | IDF1 | IDs |
|---|---:|---:|---:|---:|---:|
| Mamba予測bbox（通常） | 5.27 | 79.90 | 0.35 | 0.46 | 922 |
| Mamba予測bbox、欠損時`freeze` | 5.27 | 79.99 | 0.35 | 0.46 | 917 |
| Mamba予測bbox、lost時のみzero-motion | 5.27 | 79.96 | 0.35 | 0.46 | 920 |
| Mamba予測bbox、deltaを25%へ減衰 | 5.27 | 79.90 | 0.35 | 0.46 | 922 |
| 最終観測bbox（zero-motion） | **83.74** | **94.65** | **74.10** | **85.90** | **4** |

zero-motionでは MOTA 99.80、ID switches 8、4585/4586 detectionsとなった。

## motion predictor単体

教師強制された12フレーム履歴の次フレーム予測では、Mambaはzero-motionより良い。

| 指標 | Mamba | zero-motion |
|---|---:|---:|
| 平均bbox IoU | 0.920 | 0.904 |
| delta MAE (x, y, w, h) | 0.00312, 0.00321, 0.00605, 0.00578 | 0.00372, 0.00452, 0.00756, 0.00852 |

一方、windowed validationのSmooth L1はMamba 0.0652、zero-prediction 0.1118であり、lossは改善しているがhard IoU assignmentを安全にする水準ではない。

## 推奨する次の実装

観測bbox優先matchingを導入する。まずlast-observed bboxでmatchingし、未対応のtrack/detectionだけでMamba予測bboxをfallbackとして使う。GT-inputでzero-motion基線を下回らないことを回帰テストにする。
