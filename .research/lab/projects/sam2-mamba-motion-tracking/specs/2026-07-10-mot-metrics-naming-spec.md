---
date: 2026-07-10
project: sam2-mamba-motion-tracking
source: brainstorm
status: draft
tags: [spec, naming, validation, mot-metrics]
---

# `mot_metrics` 命名整理 Spec

## 目的

1-step の `val loss` と、tracker を実際に動かして HOTA 等を測る物体追跡指標群を、第三者が名前だけで区別できるようにする。物体追跡の総合指標を表す正式名称として `mot_metrics` を採用する。

## 背景

2026-07-09 MTGで、`tracking-val` という表現では何を評価しているかが伝わりにくく、`val loss` と tracking 全体評価を明確に区別すべきと確認した。tracking 全体評価では HOTA / DetA / AssA / MOTA / IDF1 を記録している。

## スコープ

### 変更対象

- Comet等のログnamespace: `tracking_val/*` → `mot_metrics/*`
- 実行間隔の設定キー: `tracking_val_period` → `mot_metrics_period`
- 関数名・内部変数名・必要なモジュール名の `mot_metrics` 系への整理
- README、spec、plan、materials等の説明表記

### 維持するもの

- `TrackEval`: 評価ツールの固有名
- `best_tracking_hota.pth`: HOTAをcheckpoint選択基準とすることが明確なため維持
- 過去Cometログのnamespace: 移行・書き換えは行わない

## 互換方針

- 新規設定は `mot_metrics_period` を正式キーとする。
- 既存設定の `tracking_val_period` は互換aliasを残さず、対象configを一括更新して `mot_metrics_period` に置き換える。
- 旧キーが残っていないことを静的検索で確認する。

## 対象指標

```text
mot_metrics/HOTA
mot_metrics/DetA
mot_metrics/AssA
mot_metrics/MOTA
mot_metrics/IDF1
```

## 変更対象候補

- `ssm_tracker/train.py`
- `ssm_tracker/train_stateful.py`
- `ssm_tracker/train_utils/tracking_validation.py`
- `ssm_tracker/cfgs/*.yaml`
- 関連するREADME、materials、spec、plan

## 検証方法

1. 静的検索で、対象範囲に残る旧namespace・設定キー・説明表記を確認する。
2. 既存のvalidation smoke runを実行する。
3. `val_loss/epoch_mean` と `mot_metrics/HOTA` 等が別namespaceで記録されることを確認する。
4. `mot_metrics_period` による実行間隔が従来と同じ動作になることを確認する。
5. TrackEvalの出力値と、ログに記録されたHOTA / DetA / AssA / MOTA / IDF1が一致することを確認する。
6. `best_tracking_hota.pth` の保存・更新が従来どおり動くことを確認する。

## 成功基準

- `val loss` と物体追跡指標群がログ上で明確に区別される。
- `mot_metrics` がHOTA等の総合的な物体追跡指標を表す命名として、コード・設定・資料で一貫している。
- 既存のTrackEval評価値とcheckpoint選択動作を壊さない。
- 旧設定キーの扱いが明文化され、移行時に設定解釈が曖昧にならない。

## 実装開始ゲート

このspecは命名整理の計画であり、現時点では外部実装リポジトリを変更しない。実装開始前に以下を別途確認する。

- 承認済みspec: 本ファイルを承認済みに更新
- 変更対象と範囲: 上記スコープの確定
- 検証方法: 上記手順の実行環境・smoke runを確定
- ユーザーの実装開始承認

## 未決事項

- `tracking_val_period` のaliasは残さず、一括置換する方針で確定
- 関数・モジュール名まで変更するか
- 実装対象の外部リポジトリ内で、過去ログやcheckpoint参照をどこまで追跡するか

## 関連資料

- [2026-07-09 MTG議事録](../meetings/2026-07-09-mtg.md)
- [2026-07-07 validation implementation spec](2026-07-07-validation-implementation-spec.md)
- [2026-07-10 tracking validation命名 brainstorm](../../../../secretary/notes/brainstorm/2026-07-10-tracking-validation-naming.md)
