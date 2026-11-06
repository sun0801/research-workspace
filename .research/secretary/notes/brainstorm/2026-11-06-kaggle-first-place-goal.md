---
date: 2026-11-06
project: kaggle-name-that-llm
source_todo: null
topic: 1位を目指すGPU自動実験goal
status: promoted-to-spec
tags: [brainstorm, kaggle, goal, gpu, automation]
---

# 1位を目指すGPU自動実験goal

## 読み込んだ文脈

- Kaggle Name That LLMのCPU実験サイクルは完了。GPU学習・提出は未実施。
- 既存CPU specはGPUを対象外とし、GPU段階の利用条件は診断記録に計画案として保存済み。
- 141/142のGPU状況は2026-11-05時点の観測。実行直前の再診断が必要。稼働中GPUや他研究のプロセスを止めない。
- Kaggle CLI利用量は厳密に制御できない。Kaggle用ルールはLuna/high、statuslineで区切り確認、残量15%以下では長い新規作業を始めず安全にチェックポイントを残す。
- 既存の承認済みCPU specは、今回のGPU実験・外部データ・Kaggle提出の承認にはならない。
- 今日のTODOにKaggle関連タスクはない。KaggleプロジェクトのMTG議事録は見当たらない。

## 相談の出発点

ユーザーは原則として手を動かさず、Codex goalにモデルや手法の候補選びと試行錯誤を任せ、Kaggleで1位の性能を追い越すことを目指したい。利用枠を使い切って手動再実行する事態を避けるため、余力を残す運用には同意済み。

## 問い

GPUを含む自動実験goalを、1位達成を目指しながら、コンペ評価に対する過適合や資源・利用枠の浪費を抑え、ユーザーの介入を最小限にして運用できるか。

## 有力な方向性

- goalは、現在の公式公開LBでトップスコアを特定・記録し、公式評価指標でそれを超えるモデルを追求する。
- 各反復で、公開手法・実験結果・エラー分析を見て次の仮説を選び、まず固定したprompt-grouped検証で比較する。LB向け提出は候補を絞って使う。
- 目標未達を達成扱いにせず、goalを未完了として、最後の結果・次の仮説・再開位置を保存する。
- GPUは141/142に限定し、毎回状態を読み取り診断する。計算プロセスがないGPUを優先し、UUIDを固定した最小pilotを行う。余裕条件を満たさない場合は待つ。既存ジョブの停止・変更はしない。
- CLI残量15%以下では長時間処理を新たに始めず、安全な区切りでログ・checkpoint・再開位置を記録する。これは上限到達を避けるヒューリスティックであり、厳密な消費上限や自動再開の保証ではない。
- コンペ公式ルールとモデル/データのライセンスに適合する候補に限る。有料APIや有料計算資源は許可範囲に含めない前提が妥当。

## 決定した方針

- 目標は現在の公開LBトップ超え。Private LBの最終順位は別途報告する。
- 有望候補のKaggle Notebook自動提出を許可し、公式の1日5提出・最終2件の上限を守る。
- 公開・無償で規則とライセンスに適合する外部データ/事前学習モデルを使える。有料APIは使わない。
- 試行数・総ジョブ数・累積GPU時間に固定上限を置かない。GPU安全条件と他研究の停止依頼に従う。
- 5時間利用枠が15%以下なら長時間処理を新規開始せずcheckpointを残す。

## Spec化

- ユーザー承認を受け、`.research/lab/projects/kaggle-name-that-llm/specs/2026-11-06-gpu-autonomous-first-place-spec.md`へGPU自動実験specを保存。
- spec保存は承認済みだが、実装・GPU実験・Kaggle提出の開始指示はまだ受けていない。

## 関連ファイル

- [KaggleプロジェクトREADME](../../lab/projects/kaggle-name-that-llm/README.md)
- [CPU実験spec](../../lab/projects/kaggle-name-that-llm/specs/2026-11-05-cpu-autonomous-cycle-spec.md)
- [GPU利用診断](../../lab/projects/kaggle-name-that-llm/experiments/2026-11-05-gpu-availability.md)
- [利用枠を含むKaggle CLI運用](../../../../.agents/skills/kaggle-workflow/SKILL.md)

---

## 追記 18:39

ユーザー方針: 試行回数・総ジョブ数・総実行時間の固定上限は置かず、他の研究で必要になった場合はその時点で停止する。したがって、goalは公開LBのトップ超えを追求し、コンペ期限またはユーザーの停止指示まで候補選定と実験を続ける。

引き続き守る条件: 5時間利用枠の残量15%以下では長い処理を新規開始せずcheckpointを残す。GPUの占有確認、OOM回避pilot、他プロセス非干渉、Kaggleの1日5提出・最終2件のプラットフォーム上限は固定探索予算とは別の安全/規則条件として残す。既存プロセスや他研究のジョブは終了しない。

外部データ/事前学習モデルは公式規則・ライセンス適合を確認できる公開かつ無償のものを候補にし、有料APIは使わない。spec保存は承認済みだが、実装・学習開始はまだ行わない。
