# State Carry trackerの根本原因診断

## 結論

主因は、Mambaの予測bboxをIoU対応付けの唯一の位置として使うこと。

- GT bbox入力でも通常State Carryは HOTA 5.27 / AssA 0.35 / IDF1 0.46 / 922 IDs。
- 同じGT入力で予測を使わないzero-motion対応付けは HOTA 83.74 / AssA 74.10 / IDF1 85.90 / 4 IDs。
- Mambaはteacher-forcedな1ステップbbox予測ではzero-motionより良い（12履歴の平均IoU 0.920 vs 0.904）だが、hard IoU matchingへそのまま投入するには不確実性が大きい。
- cache付き逐次推論と一括推論は最大誤差 `2.1e-6` で一致し、epoch100 GT checkpointではNaNも出ない。

## 却下した仮説

| 仮説 | 検証 | 判断 |
|---|---|---|
| 検出器誤差 | GT bboxをtracker入力にした | 否定 |
| TrackEval導線の不具合 | zero-motionで高HOTA、同一評価設定 | 否定 |
| cache逐次推論の破綻 | 一括・prefill・token逐次が一致 | 今回は否定 |
| 欠損時self-updateだけが原因 | `freeze` / lost時zero-motionでもHOTA約5.27 | 単独原因ではない |
| 学習・推論履歴長のoff-by-one | 12履歴でも1ステップIoUは改善 | 主因ではない |

## 改善方針

1. **観測bbox優先matching**: 前フレームの観測bboxでまず対応付け、未対応のtrack/detectionだけにMamba予測bboxをfallbackとして使う。
2. **prediction confidence gate**: 予測と観測bboxのIoU、deltaの大きさ、欠損長でMamba fallbackを制限する。
3. **tracker向け学習**: detector欠損を含む入力、scheduled sampling/free-running、予測不確実性を導入し、val lossだけでなくHOTA/AssA/IDF1で選ぶ。

改善1の実装前にはmatching順序とGT-input zero-motion parityをspec化する。
