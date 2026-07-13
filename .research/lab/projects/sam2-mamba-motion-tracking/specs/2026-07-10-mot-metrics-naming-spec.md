---
date: 2026-07-10
project: sam2-mamba-motion-tracking
source: brainstorm
status: approved
tags: [spec, naming, validation, mot-metrics]
last_updated: 2026-07-13
---

# `mot_metrics` 命名整理 Spec

## 目的

1-step の `val loss` と、tracker を実際に動かして HOTA 等を測る物体追跡指標群を、第三者が名前だけで区別できるようにする。物体追跡の総合指標を表す正式名称として `mot_metrics` を採用する。

## 背景

2026-07-09 MTGで、`tracking-val` という表現では何を評価しているかが伝わりにくく、`val loss` と tracking 全体評価を明確に区別すべきと確認した。tracking 全体評価では HOTA / DetA / AssA / MOTA / IDF1 を記録している。

2026-07-10 brainstormで候補を比較し、`mot_metrics` を正式名称として決定した。2026-07-13にコード調査を行い、変更箇所の全量を確定した。

## スコープ

### 変更対象

- モジュールファイル名: `tracking_validation.py` → `mot_metrics.py`
- 関数名: `should_run_tracking_validation` → `should_run_mot_metrics` / `run_tracking_validation` → `run_mot_metrics`
- Configキー: `tracking_val_period` → `mot_metrics_period`
- Cometログnamespace: `tracking_val/*` → `mot_metrics/*`
- ローカル変数名: `should_tracking_eval` → `should_mot_metrics`
- logger文言: `tracking validation` → `mot_metrics`
- Research Workspace側の文書更新（コード実装後に実施）

### 維持するもの

- `TrackEval`: 評価ツールの固有名
- `best_tracking_hota.pth`: HOTAをcheckpoint選択基準とすることが明確なため維持
- `best_tracking_hota` 変数名: checkpoint選択ロジックの変数であり、`mot_metrics` とは意味が異なる
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

## 変更箇所の全量マップ

対象リポジトリ: `/mnt/HDD10TB-2/aburatani/2025_09_aburatani_Mamba_Trackers`

### A. ファイルリネーム

| 現在 | 変更後 |
|---|---|
| `ssm_tracker/train_utils/tracking_validation.py` | `ssm_tracker/train_utils/mot_metrics.py` |

### B. mot_metrics.py 内部（リネーム後の名前で記載）

| 箇所 | 現在 | 変更後 | 行 |
|---|---|---|---|
| 関数名 | `should_run_tracking_validation()` | `should_run_mot_metrics()` | L21 |
| configキー参照 | `validation_cfgs.get("tracking_val_period", 0)` | `validation_cfgs.get("mot_metrics_period", 0)` | L25 |
| 関数名 | `run_tracking_validation()` | `run_mot_metrics()` | L61 |
| logger | `"Skip tracking validation for unsupported model: ..."` | `"Skip mot_metrics for unsupported model: ..."` | L64 |
| logger | `"Skip tracking validation because ..."` | `"Skip mot_metrics because ..."` | L84 |
| logger | `"Run tracking validation for epoch ..."` | `"Run mot_metrics for epoch ..."` | L110 |
| logger | `"Tracking validation metrics at epoch ..."` | `"mot_metrics at epoch ..."` | L152 |

### C. train.py

| 箇所 | 現在 | 変更後 | 行 |
|---|---|---|---|
| import | `from train_utils.tracking_validation import run_tracking_validation, should_run_tracking_validation` | `from train_utils.mot_metrics import run_mot_metrics, should_run_mot_metrics` | L12 |
| 変数名+関数呼び出し | `should_tracking_eval = should_run_tracking_validation(...)` | `should_mot_metrics = should_run_mot_metrics(...)` | L226 |
| 変数参照 | `should_save_periodic or should_tracking_eval` | `should_save_periodic or should_mot_metrics` | L230 |
| 変数参照 | `if should_tracking_eval:` | `if should_mot_metrics:` | L240 |
| 関数呼び出し | `tracking_metrics = run_tracking_validation(...)` | `tracking_metrics = run_mot_metrics(...)` | L241 |
| ログnamespace | `f'tracking_val/{key}'` | `f'mot_metrics/{key}'` | L251 |

### D. train_stateful.py

| 箇所 | 現在 | 変更後 | 行 |
|---|---|---|---|
| import | `from train_utils.tracking_validation import run_tracking_validation, should_run_tracking_validation` | `from train_utils.mot_metrics import run_mot_metrics, should_run_mot_metrics` | L33 |
| 変数名+関数呼び出し | `should_tracking_eval = should_run_tracking_validation(...)` | `should_mot_metrics = should_run_mot_metrics(...)` | L212 |
| 変数参照 | `should_save_periodic or should_tracking_eval` | `should_save_periodic or should_mot_metrics` | L216 |
| 変数参照 | `if should_tracking_eval:` | `if should_mot_metrics:` | L226 |
| 関数呼び出し | `tracking_metrics = run_tracking_validation(...)` | `tracking_metrics = run_mot_metrics(...)` | L227 |
| ログnamespace | `f"tracking_val/{key}"` | `f"mot_metrics/{key}"` | L237 |

### E. Config YAML（3ファイル）

| ファイル | 現在 | 変更後 | 行 |
|---|---|---|---|
| `cfgs/MambaTrack.yaml` | `tracking_val_period: 5` | `mot_metrics_period: 5` | L42 |
| `cfgs/TrackSSM.yaml` | `tracking_val_period: 5` | `mot_metrics_period: 5` | L43 |
| `cfgs/MambaStateful.yaml` | `tracking_val_period: 5` | `mot_metrics_period: 5` | L47 |

### F. 変更しないもの（確認済み）

| 対象 | 理由 |
|---|---|
| `best_tracking_hota.pth`（ファイル名） | HOTAベースのcheckpoint選択基準として明確。既存ckptとの互換性維持 |
| `best_tracking_hota`（変数名） | checkpoint選択ロジックの変数。`mot_metrics` とは意味が異なる |
| `TrackEval` | 評価ツールの固有名 |
| 過去Cometログ | namespace移行は不要 |
| `tracking_metrics`（変数名） | `run_mot_metrics()` の戻り値を受ける変数。指標辞書を指しており、関数名変更とは独立 |

### G. Research Workspace 文書（コード実装後に実施）

コード変更完了後に、以下の文書内の `tracking_val` 表記を `mot_metrics` に更新する。

- `README.md`（プロジェクト）
- `materials/2026-07-09-validation-implementation-mtg-materials.md`
- `plans/2026-07-07-validation-implementation-plan.md`
- `specs/2026-07-07-validation-implementation-spec.md`

brainstormメモは当時の思考記録のため更新しない。

## 変更規模

全体で **22箇所**（ファイルリネーム1 + モジュール内部7 + train.py 6 + train_stateful.py 6 + config 3 = 23。ただしファイルリネームはgit mvで1操作）。すべて機械的なリネームであり、ロジック変更はない。

## 検証方法

1. `grep -rn "tracking_val" ssm_tracker/` で旧名が残っていないことを確認する。
2. 既存のvalidation smoke runを実行する（1エポック + `mot_metrics_period: 1`）。
3. `val_loss/epoch_mean` と `mot_metrics/HOTA` 等が別namespaceで記録されることを確認する。
4. `mot_metrics_period` による実行間隔が従来と同じ動作になることを確認する。
5. TrackEvalの出力値と、ログに記録されたHOTA / DetA / AssA / MOTA / IDF1が一致することを確認する。
6. `best_tracking_hota.pth` の保存・更新が従来どおり動くことを確認する。

## 成功基準

- `val loss` と物体追跡指標群がログ上で明確に区別される。
- `mot_metrics` がHOTA等の総合的な物体追跡指標を表す命名として、コード・設定で一貫している。
- 既存のTrackEval評価値とcheckpoint選択動作を壊さない。
- `grep` で旧キー `tracking_val` がコード・config内に残っていない。

## 実装開始ゲート

このspecは命名整理の計画であり、現時点では外部実装リポジトリを変更しない。実装開始前に以下を確認する。

- 承認済みspec: 本ファイルの `status` を `approved` に更新
- 変更対象と範囲: 上記全量マップのとおり
- 検証方法: 上記手順
- ユーザーの実装開始承認

## 関連資料

- [2026-07-09 MTG議事録](../meetings/2026-07-09-mtg.md)
- [2026-07-07 validation implementation spec](2026-07-07-validation-implementation-spec.md)
- [2026-07-10 tracking validation命名 brainstorm](../../../../secretary/notes/brainstorm/2026-07-10-tracking-validation-naming.md)
