# State carry の MOT metrics が epoch 間で不変な場合の対処方針

## 相談の問い

MambaStateful の checkpoint は異なる model output を生成しているのに、full validation の MOT output と HOTA / IDF1 が epoch 間で完全に一致する。この結果をどう扱い、どこから修正すべきか。

## 現在の理解

- Comet の記録回数の問題ではない。epoch 10, 20, ..., 80でmot_metricsは複数回実行されている。
- epoch 10/90 の代表的な stateful model output は異なる。
- しかし `dancetrack0004` の tracking output は完全一致した。
- frame 6 の output が空で、frame 7から新しいIDが現れる。各IDの最大継続長は5 records。
- `track.py` と `track_stateful.py` は、通常出力時に最新検出bboxを使う点では同じ。state carry固有の差はprediction生成とcached state更新の経路にある。
- `enable_time_thresh=5` 到達後のprediction/matching失敗、trackのlost化、新規trackの出力遅延が、同じtracking結果へ収束する有力な仮説。ただしIoUとstate遷移の直接ログがなく、根本原因は未確定。

## 対処方針

1. 既存の学習・profiling成果物は保持する。
2. state carryのHOTA / IDF1は、原因が解消するまで主相関分析から保留する。
   - HOTA / IDF1が定数の場合、Pearson / Spearmanは実質的に未定義。
   - best epochも全観測点の同率となるため、checkpoint選択の根拠に使わない。
3. 100epochの再学習をすぐにやり直さず、epoch 10/90の1sequence・数フレームで局所診断する。
4. frame 5--7について、検出bbox、`predicted_last_bbox`、`pending_delta`、matching IoU、match結果、track state、activation状態をepoch 10/90で比較する。
5. 診断で原因を分ける。
   - predictionが検出から大きく外れる: state carryのdelta変換、scale、clip、state更新を確認。
   - predictionは妥当だがmatchしない: matching threshold、座標系、更新順序を確認。
   - match失敗後だけ同じ結果になる: lost/resetと新規trackの同一フレーム出力仕様を確認。
6. 根本原因を特定した後に、最小修正を1つだけ入れ、1sequence smoke → full val数点 → 100epoch再実行の順で検証する。

## 修正候補の優先順位

第一候補は `enable_time_thresh=5` 直後のprediction/matchingの局所挙動を正すこと。最新検出bboxを出力する処理だけを変更しても、matching前の予測が崩れている場合は本質的な解決にならない。

次に、低信頼prediction時の検出bbox fallback、missing時のstate reset / update skip、新規trackの出力タイミングを、研究仮説と分離したアブレーションとして比較する。これらは最終仕様を決める前に、診断用設定として扱う。

## 判断

現時点のstate carry結果は「学習がepoch間で同じ性能だった」とは解釈しない。まず tracking pipeline の退化・故障候補として記録し、原因未確定のまま本実験の相関結論へ含めない。
