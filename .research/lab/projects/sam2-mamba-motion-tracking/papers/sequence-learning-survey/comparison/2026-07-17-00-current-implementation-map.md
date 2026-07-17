---
date: 2026-07-17
project: sam2-mamba-motion-tracking
status: completed
tags: [paper-note, sequence-learning-survey, comparison, state-carry, batch-0]
---

# 00 現行実装マップ: MambaStateful

## 実装の分類

| 観点 | 判定 |
| --- | --- |
| 学習時のモデル | causal Mambaによるfixed-window many-to-many delta prediction |
| 学習時のstate carry | window内のみ。track / video / batch間のcarryなし |
| 推論時のstate carry | あり。trackletごとの`InferenceParams` cache |
| 学習入力 | Ground Truth bboxのみ |
| 推論入力 | accepted detection、またはmatching失敗時のself prediction |
| loss | index 4–10のSmooth L1 mean（11 token中7時刻） |
| matching | 予測bboxを主位置にしたIoU 2-stage assignment |
| low-confidence guard | なし（detection scoreはfilter/new track用） |
| lost時 | 既定ではself predictionを再入力、`max_time_lost`後に削除 |
| normal/cached parity | epoch100 GT checkpointでは既存診断でmax diff `2.1e-6` |

## 外部比較で使う判定軸

| 軸 | 現行値 | 比較の狙い |
| --- | --- | --- |
| supervised timestep | warm-up後の全時刻 | many-to-many / many-to-oneとの比較 |
| state reset | every shuffled window | TBPTT・sequence carryとの比較 |
| training observation | GT only | noisy observation / scheduled samplingとの差 |
| deployment observation | accepted detection + self prediction | input sourceを明示する |
| prediction role | hard IoU matching position | observation-first / confidence gateとの差 |
| missing policy | self-update or freeze | skip/reset/fallbackとの差 |

## 現行モデルへの含意

現行の主問題は「最終時刻だけにlossがない」ことではない。lossは7時刻に与えられている。優先すべき比較は、次の順である。

1. fixed shuffled window学習とstateful / TBPTT学習の差
2. GT teacher forcingとaccepted detection入力の差
3. self predictionを連続入力する欠測時のrollout劣化
4. predictionをhard matchingの主位置へ置くことの妥当性

## 関連成果物

- [現行MambaStatefulの学習・推論経路分析](../../../experiments/2026-07-17-current-state-carry-analysis.md)
- [コード根拠一覧](../evidence/2026-07-17-current-implementation-evidence.md)
- [GT入力HOTA低下の根本原因診断](../../../experiments/2026-07-17-statecarry-root-cause-diagnosis.md)
