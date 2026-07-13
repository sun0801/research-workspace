---
date: 2026-07-10
project: sam2-mamba-motion-tracking
source_todo: tracking validation の命名を見直し、`val loss` との差が分かる表現に整理する
topic: tracking-validation-naming
status: exploratory
tags: [brainstorm, validation, naming, trackeval]
---

# tracking validationの命名整理

## 読み込んだ文脈

- 2026-07-09 MTG議事録
- 2026-07-07 validation implementation spec / brainstorm
- `Mamba_Trackers` の `tracking_val` 実装
- 現在のCometログ、設定キー、関数名、説明資料

## 相談の出発点

TODO「tracking validation の命名を見直し、`val loss` との差が分かる表現に整理する」を、概念名・ログ名・設定名・関数名に分けて整理する。

## 対象TODO

- tracking validation の命名を見直し、`val loss` との差が分かる表現に整理する

## 問い

1-step予測誤差と、trackerを実際に動かしてHOTA等を測る評価を、第三者が名前だけで区別できる命名は何か。

## アイデア候補

### A. `tracking_eval`（推奨）

- 概念: tracking evaluation（validation split上のend-to-end tracking評価）
- ログ: `tracking_eval/HOTA`, `tracking_eval/DetA`, `tracking_eval/AssA`, `tracking_eval/MOTA`, `tracking_eval/IDF1`
- 設定: `tracking_eval_period`
- 関数: `run_tracking_evaluation`, `should_run_tracking_evaluation`
- モジュール: `tracking_evaluation.py`

### B. `tracking_metric_eval`

- 指標評価であることは明確
- `tracking_eval` より長く、自然な概念名としてはやや重い

### C. `trackeval_val`

- TrackEvalを使うことは明確
- 実装ツールに依存し、TrackEval以外の評価実装へ広げにくい
- `val` が残るため、`val loss`との混同も完全には解消しない

### D. `tracking_val` 継続

- 変更コストは最小
- ただし、今回のMTGで指摘された曖昧さを解消できない

## 仮説候補

- `val_loss` と `tracking_eval` を並べると、loss監視とend-to-end評価の役割差が最も伝わりやすい。
- TrackEvalは評価手段であり、研究上の概念名に含めない方が将来の実装変更に強い。

## 実験・実装案

1. コード側で `tracking_val` 系のログnamespace、設定キー、関数名、必要ならモジュール名を `tracking_eval` 系へ統一する。
2. 既存設定との互換性のため、旧キー `tracking_val_period` は一時的なaliasとして読むか、変更対象を全configに限定して一括更新する。
3. `best_tracking_hota.pth` は、選択基準がHOTAで明確なので当面維持する。
4. README、spec、materials、meeting本文では初出を「validation split上のend-to-end tracking evaluation」と書き、以後は「tracking evaluation」と略す。
5. smoke runで、`val_loss/epoch_mean` と `tracking_eval/HOTA` 等が同時に記録されることを確認する。

## 比較・評価軸

- `val_loss` との差が名前だけで分かるか
- HOTA等の複数tracking指標を自然に含められるか
- TrackEval以外の評価実装へ拡張できるか
- config・関数・ログnamespaceの一貫性を保てるか
- 既存実験結果・checkpoint名への変更影響を抑えられるか

## 今回見えた方向性

第一候補は `tracking_eval`。概念上は「validation split上のend-to-end tracking evaluation」と定義し、`val_loss` と対になる名前として使う。`TrackEval` は内部の評価ツール名として残す。

## 次アクション候補

1. `tracking_eval` を正式採用するか決める。
2. 変更範囲をログ・config・関数・モジュール・文書のどこまでにするか決める。
3. 旧 `tracking_val_period` の互換aliasを残すか決める。
4. 採用後、既存validation implementation specに命名変更を追記してから実装する。

## Spec化候補

既存の `2026-07-07-validation-implementation-spec.md` への追記、または命名変更だけを扱う小さなspecにできる。コード変更を伴うため、採用名・変更範囲・互換方針・smoke run成功条件を先に確定する。

## 未解決の問い

- `tracking_eval` を採用するか。
- `tracking_evaluation.py` へのモジュール名変更まで行うか。
- 過去Cometログのnamespaceを移行する必要があるか。
- 既存checkpoint名を維持するか。

## 関連ファイル

- `/mnt/HDD10TB-2/aburatani/2025_09_aburatani_Mamba_Trackers/ssm_tracker/train_utils/tracking_validation.py`
- `/mnt/HDD10TB-2/aburatani/2025_09_aburatani_Mamba_Trackers/ssm_tracker/train.py`
- `/mnt/HDD10TB-2/aburatani/2025_09_aburatani_Mamba_Trackers/ssm_tracker/train_stateful.py`
- `.research/lab/projects/sam2-mamba-motion-tracking/meetings/2026-07-09-mtg.md`
- `.research/lab/projects/sam2-mamba-motion-tracking/specs/2026-07-07-validation-implementation-spec.md`


---

## 追記 — MTG意図に基づく候補の見直し

前回の`tracking_eval`推奨は、評価処理の名前に寄りすぎており、2026-07-09 MTGの「HOTA等の物体追跡を総合的に測る指標だと第三者に分かる名前」という要件を満たさない。

### 再評価

- 第一候補: `object_tracking_metrics`
  - 物体追跡の指標であることが直接伝わる。
  - ログ例: `object_tracking_metrics/HOTA`, `object_tracking_metrics/DetA`, `object_tracking_metrics/AssA`, `object_tracking_metrics/MOTA`, `object_tracking_metrics/IDF1`
- 短い内部コード名の候補: `mot_metrics`
  - MOT研究者には簡潔で明確だが、MOTに馴染みのない読者には説明が必要。
- `tracking_eval` は、指標の意味が名前から分かりにくいため候補から外す。

### 決定

正式名称は `mot_metrics` とする。HOTA / DetA / AssA / MOTA / IDF1 など、物体追跡を総合的に測る指標群を表すnamespace・config・関数名に使用する。`tracking_eval` と `object_tracking_metrics` は採用しない。

実装時には、既存の `tracking_val`、`tracking_val_period`、`tracking validation` 表記を対象に、`mot_metrics` 系の命名へ整理する。ただし `TrackEval` は評価ツール名、`best_tracking_hota.pth` はチェックポイント基準を表すため、別途必要性を確認する。
