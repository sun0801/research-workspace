---
date: 2026-07-15
project: sam2-mamba-motion-tracking
source: 2026-07-15-full-validation-correlation-analysis-spec
status: config-updated
tags: [experiment, validation, correlation, mot_metrics, configuration]
---

# full validation相関分析用canonical YAML変更

## 実施内容

Implementation Gate通過後、specで指定されたcanonical YAML 3ファイルだけを変更した。

変更対象:

- /mnt/HDD10TB-2/aburatani/2025_09_aburatani_Mamba_Trackers/ssm_tracker/cfgs/MambaTrack.yaml
- /mnt/HDD10TB-2/aburatani/2025_09_aburatani_Mamba_Trackers/ssm_tracker/cfgs/TrackSSM.yaml
- /mnt/HDD10TB-2/aburatani/2025_09_aburatani_Mamba_Trackers/ssm_tracker/cfgs/MambaStateful.yaml

変更値:

- train.epochs: 100
- validation.val_loss_period: 5
- validation.mot_metrics_period: 10

維持した設定:

- MambaStatefulのtrain.lr_scheduler: none
- optimizer、モデル構造、tracker実装、TrackEval metric
- 既存のPython実装変更
- timing_enabledは未設定のまま

## 検証結果

- PyYAMLによる3 YAMLのロード: PASS
- 3モデルの設定値確認: PASS
- 1〜100epochのval loss周期列: 5, 10, ..., 100
- 1〜100epochのmot_metrics周期列: 10, 20, ..., 100
- MambaStatefulのscheduler据え置き確認: PASS
- 外部リポジトリの対象YAML git diff --check: PASS
- YAML差分: 対象3ファイルのみ

外部リポジトリには、今回以前から次の未コミット変更が存在していたため保持した。

- .gitignore
- ssm_tracker/train.py
- ssm_tracker/train_stateful.py
- ssm_tracker/train_utils/mot_metrics.py

## 未実施

- 100epoch学習
- epoch 10, 20, ..., 100のfull val
- val lossとHOTA / IDF1のPearson・Spearman分析
- best epoch一致の確認

## 関連ファイル

- [2026-07-15-full-validation-correlation-analysis-spec.md](../specs/2026-07-15-full-validation-correlation-analysis-spec.md)
- [2026-07-15-validation-timing-implementation-smoke.md](2026-07-15-validation-timing-implementation-smoke.md)
