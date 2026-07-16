# MambaStateful frame transition 診断結果

## 実行条件

- checkpoint: epoch 10、epoch 90
- sequence: dancetrack0004
- 観測範囲: frame 1〜7
- 診断出力: artifacts/profiling/mamba_validation_2026-07-15/full_validation/statecarry_epoch_compare/frame_transition/
- 診断実装: ssm_tracker/track_stateful.py、ssm_tracker/track_utils/stateful_tracker.py

## 結論

原因はCometの記録ではなく、state carry predictionで発生するNaNだった。epoch 10/90ともframe 6で、既存3 trackすべてのpending_deltaとpredicted_last_bboxがNaNになった。その結果、matching IoUが全て0となり、3 trackがすべてlostになった。未matchの検出は新規activateされるが、frame 1以外でactivateされたtrackは同一frameに出力されないため、frame 6のoutputは0件になった。

この同じ遷移がepoch 10/90で発生するため、model checkpointの差が最終tracking outputへ反映されず、MOT metricsがepoch間で完全一致していた。

## Evidence

### frame 6の比較

| 指標 | epoch 10 | epoch 90 |
|---|---:|---:|
| prediction対象track数 | 3 | 3 |
| NaN pending_delta | 3 | 3 |
| NaN predicted_last_bbox | 3 | 3 |
| stage 1 matches | 0 | 0 |
| frame 6 output track数 | 0 | 0 |
| update_missing | 3 | 3 |
| mark_lost | 3 | 3 |
| activate | 3 | 3 |

### 通常tracking output

epoch 10/90のdancetrack0004.txtは完全一致した。
SHA256: 73631b0c658520ca332e9926ece7d4399d801fd4266a8d25ca767ae4c27297f7

診断JSONLはいずれもframe 1〜7の7行を生成し、epoch 10/90の診断JSONL自体も完全一致した。

## 研究上の扱い

このrunは「epoch間でstate carryのtracking性能が同じ」とは解釈しない。stateful inferenceがframe 6でNaNへ退化しているため、HOTA / IDF1の相関分析からは保留する。NaN発生を修正・検証した後に、必要ならfull validationを再実行する。

## 次の修正検討

次の候補を別specまたは修正計画として切り分ける。

1. InferenceParamsを使うstateful inference pathでNaNが発生する箇所の特定。
2. cached inferenceと通常forwardの数値差、およびcache初期化・seqlen_offsetの扱いを確認する。
3. NaNを検出した場合の安全なfallback/resetを診断用ablationとして比較する。

原因未確定のまま、通常出力bboxの採用処理だけは変更しない。

## 実装差分

診断用CLI引数とJSONL記録を追加した。通常経路ではdiagnostic_path未指定のため、既存のtracking処理・config・Comet記録は変更されない。学習用YAMLの既存変更は今回の診断実装とは別に、ユーザーが先に行っていた変更として保持している。
