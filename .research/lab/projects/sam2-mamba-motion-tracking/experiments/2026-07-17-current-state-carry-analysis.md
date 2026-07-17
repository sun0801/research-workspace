---
date: 2026-07-17
project: sam2-mamba-motion-tracking
status: completed
tags: [experiment-analysis, state-carry, mamba, training, inference, batch-0]
---

# 現行MambaStatefulの学習・推論経路分析（Batch 0）

## 結論

現行 `MambaStateful` は、名称とは異なり**学習時にはtrack単位・動画単位でstateを持ち越していない**。各サンプルは固定長12 bboxから作る11トークンの重複sliding windowであり、DataLoaderがshuffleした各windowを通常forwardへ入力する。window内では因果Mambaのstateを展開してBPTTするが、windowの境界およびbatch間で明示的なstate carryやdetachはない。

一方trackerは、trackletごとに `InferenceParams` cacheを保持して逐次推論し、5観測以降のMamba予測bboxをIoU matchingの主位置として使う。matching成功時はaccepted detection、失敗時（`self_update`）はself predictionを履歴・cacheへ入力する。このtrain/inference経路の差に加え、predictionをhard matchingに直結する設計が、現在のID崩壊の主な切り分け対象である。

## 対応表

| 段階 | 現行実装 | 入力 | 出力 | state / reset | loss / matching | 根拠 |
| --- | --- | --- | --- | --- | --- | --- |
| Dataset | 重複fixed window | 連続12 bbox | 11 bbox token, 11 delta target | sampleごとに独立 | なし | `stateful_dataset.py:42-48, 75-85` |
| Train forward | 通常Mamba forward | GT bbox token | 時刻別4次元delta | forward内のみ因果state。cacheなし | なし | `MambaStateful.py:61-70`, `train_stateful.py:162-177` |
| Loss | Smooth L1 mean | output index 4–10 | scalar | window境界で次batchへ伝播しない | 7時刻のdelta loss | `MambaStateful.py:83-100`, config `loss_start_index: 4` |
| BPTT | 1 window全体 | shuffled batch | parameter gradient | detachなし、batchをまたぐstateなし | window内のlossから逆伝播 | `train_stateful.py:87-93, 162-177` |
| Validation loss | trainと同じwindow forward | val annotationのGT window | scalar | eval/no_grad、cacheなし | 同一loss slice | `validation.py:62-86` |
| Tracker state | trackletごとのcache | accepted detection / self prediction | 次delta・予測bbox | 新trackで初期化、track削除までcarry。cache容量到達時は最大12履歴から再構築 | なし | `stateful_tracklet.py:53-65, 106-176` |
| Matching | 2段IoU assignment | 予測track bbox と detection bbox | accepted / unmatched | predictionは5観測以降に利用 | threshold 0.7 / 0.9 | `stateful_tracker.py:58-90`, `stateful_tracklet.py:67-74` |
| State update | 観測成功時はdetection、失敗時はprediction | accepted detection / self prediction | memo/cacheの次state | `freeze`以外は未対応時にも更新 | confidence gateなし | `stateful_tracklet.py:200-230` |
| Output | 通常はlast memo bbox | accepted detection またはself prediction | MOT text | debug時だけ予測bboxを直接出力 | TrackEvalへ渡すtracker出力 | `track_stateful.py:168-195` |
| MOT metrics | tracker subprocess後にTrackEval API | tracker text + GT | HOTA/DetA/AssA/MOTA/IDF1 | 各epochで新しいtracker process | 指標計算はtracker推論と分離 | `mot_metrics.py:101-199` |

## データフロー

```text
GT trajectory JSON
  -> 12 bboxの重複window
  -> condition: bbox[t=0..10], label: delta[t=0..10]
  -> normal causal Mamba forward（cacheなし）
  -> loss: index 4..10のSmooth L1 mean
  -> checkpoint
  -> tracker: trackごとのcached Mamba inference
  -> predicted bbox
  -> predicted bbox対detectionのIoU matching
  -> accepted detection または self prediction
  -> track state/cache update
  -> MOT-format tracker output
  -> TrackEval
```

## 確定事項

### Dataset / loss / BPTT

- `window_size=12`で、各trajectoryから開始位置を1ずつずらしたwindowを作る。`condition`はbbox `[0..10]`、`label`は各次時刻へのbbox差分 `[0→1,..,10→11]`。
- 学習DataLoaderは`shuffle=True`である。したがって同一track・同一動画の隣接windowが連続して処理される保証はない。
- configの`loss_start_index=4`により、loss対象は11 token中index 4–10、すなわち7時刻である。最終時刻だけのlossではない。lossはmask・時刻重みなしの`SmoothL1Loss`既定meanである。
- 通常forwardは`inference_params=None`で呼ばれる。window内の因果計算グラフ全体にbackpropagationするが、stateを次windowへ渡す箇所もdetachする箇所もない。実質的なBPTT範囲は11入力tokenのwindow内に限られる。
- validation lossも同じ`StatefulTrajDataset`と同じlossをeval/no_gradで評価する。tracking推論・matchingは含まれない。

### Tracker / matching / state update

- trackerはsequenceごとに新しい`MambaStatefulTracker`を作り、new trackletごとに`memo_bank`、`InferenceParams`、`pending_delta`を初期化する。
- 5観測未満はlast observed bboxによるzero-motion、5観測以降はlast memo bboxにMamba deltaを加えたbboxを`tlwh`として返す。`iou_distance`はこの`tlwh`を読むため、predictionがIoU matchingの主位置となる。
- matching成功時にはaccepted detectionのbboxでhistoryとcacheを更新する。検出scoreは初期filter/new track閾値にのみ使われ、matched observationをstateへ入れるか判断するconfidence gateはない。
- matching失敗時の既定`self_update`ではprediction bboxをhistoryとcacheへ再入力する。`freeze`では再入力しないが、reset・decay・confidence-based fallbackはない。
- MOT出力は通常`get_bbox()`、すなわちlast memo bboxである。associationが成立した場合はaccepted detection、失敗後にself updateした場合はpredictionが書き出される。

## Train/inference mismatch

1. **状態の持越し範囲**: 学習は独立した11-token window、推論はtrackごとの逐次cacheである。
2. **入力分布**: 学習はGT bboxのみ、推論はaccepted detectionまたはself predictionである。
3. **目的関数と下流判断**: 学習はdeltaのSmooth L1のみ、推論ではそのdeltaがhard IoU assignmentを左右する。
4. **欠測処理**: 学習にはmatching失敗・誤association・欠測連鎖がなく、推論では`self_update`が既定である。

## 既存実験との照合

2026-07-17のGT入力実験では、teacher-forced 1-step motion predictionはzero-motionより良い一方、予測bboxをmatchingに使う通常trackerはHOTA 5.27、last-observed bboxを使うzero-motion matchingはHOTA 83.74だった。これは上記の「delta lossの改善」と「hard associationの安全性」が別問題であることと整合する。詳細は [2026-07-17-statecarry-root-cause-diagnosis.md](2026-07-17-statecarry-root-cause-diagnosis.md) を参照。

## 未確認・断定しない事項

- `InferenceParams` / Mamba cacheそのものがautograd対応かは、本Batchでは未検証。現行コードではcache利用がすべて`torch.no_grad()`下のtracker推論に限定されるため、TBPTTへ直接流用できるとは判断しない。
- 固定window全体の状態展開と逐次cache出力の数値parityは、epoch100 GT checkpointで最大差`2.1e-6`が既に確認済み。ただし全checkpoint・長時間cache・学習中のautograd parityを保証するものではない。

## Batch 1で優先して確認する問い

1. next-step many-to-manyで、warm-up後の全時刻lossと最終時刻lossはどの目的で使い分けるか。
2. stateをsequence間で持ち越す学習では、TBPTTとdetachをどこに置くか。
3. Teacher forcing時のGT入力、実運用のaccepted detection入力、欠測時self predictionをどう分離するか。
4. autoregressive rolloutを通常MOTではなく欠測診断としてどう評価するか。

## コード根拠

- repository: `/mnt/HDD10TB-2/aburatani/2025_09_aburatani_Mamba_Trackers`
- commit: `d52bb81553e0d124f428a8f5c5e915d4208def88`
- 詳細な判断単位の根拠は [2026-07-17-current-implementation-evidence.md](../papers/sequence-learning-survey/evidence/2026-07-17-current-implementation-evidence.md) に記録する。
