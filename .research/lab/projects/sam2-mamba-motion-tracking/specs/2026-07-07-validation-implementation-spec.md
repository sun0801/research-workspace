---
date: 2026-07-07
project: sam2-mamba-motion-tracking
source: brainstorm
status: draft
tags: [spec, experiment, validation, implementation]
---

# Validation Implementation Spec

## 目的

Mamba系 motion predictor の学習において、過学習の有無と tracking 性能の推移を学習中に確認できるようにする。具体的には、`val loss` と `TrackEval による tracking validation` を分離して導入し、checkpoint 選択と実験比較を安定化する。

## 背景

- 現状の学習コードは `epochN.pth` の periodic save のみで、学習中 validation loop を持たない
- State carry 型では LR scheduler 問題と過学習の可能性が議論されており、まず開発用 val loss が必要
- 一方で研究上重要なのは tracking 全体の性能であり、HOTA / DetA / AssA / MOTA / IDF1 の推移も学習中に見たい
- DanceTrack では official `val` split と TrackEval 環境が既に手元にあるため、まずはそれをそのまま利用する

## 検証したい問い

1. `val loss` を導入すると、state carry 型や sliding window 型の過学習タイミングを把握できるか
2. `val loss` の推移と tracking 指標の推移はどの程度一致するか
3. 5 エポックごとの TrackEval を入れることで、best checkpoint 選択と比較実験の品質を上げられるか

## 仮説

- `val loss` は過学習検知には有効だが、最良の `val loss` checkpoint と最良の HOTA checkpoint は一致しない可能性が高い
- そのため、checkpoint 選択基準は `best_val_loss` と `best_tracking_hota` に分ける方が妥当である
- official DanceTrack val split をそのまま使うことで、train leakage を避けつつ、既存比較とも整合的な評価ができる

## 実験・実装内容

### A. 開発用 validation loss の導入

- `dancetrack_train.json` と `dancetrack_val.json` を分離して用意する
- `train.py` と `train_stateful.py` に val dataloader を追加する
- epoch ごとに `model.eval()` / `torch.no_grad()` で val loop を回し、平均 loss を記録する
- Comet には `val_loss/current` ではなく `val_loss/epoch_mean` を主に残す

### B. tracking validation の導入

- 5 エポックごとに現在の checkpoint で tracker 推論を実行する
- 既存の `track.py` / `track_stateful.py` を CLI のまま利用する
- 推論結果を TrackEval の tracker folder に配置し、`run_mot_challenge.py` を呼び出す
- `pedestrian_summary.txt` を parse して、HOTA / DetA / AssA / MOTA / IDF1 を Comet に記録する

### C. checkpoint 保存基準の分離

- `epochN.pth`: 既存どおり periodic save
- `best_val_loss.pth`: 最良の val loss で更新
- `best_tracking_hota.pth`: 最良の HOTA で更新

## 使用データ・モデル

### データ

- trajectory 学習用:
  - `dancetrack_train.json`
  - `dancetrack_val.json`
- tracking validation 用 GT:
  - `/mnt/HDD10TB-2/aburatani/TrackEval/data/gt/dancetrack/val`

### モデル

- `MambaTrack`
- `TrackSSM`
- `MambaStateful`

### 既存評価基盤

- TrackEval repository:
  - `/mnt/HDD10TB-2/aburatani/TrackEval`
- 実行スクリプト:
  - `/mnt/HDD10TB-2/aburatani/TrackEval/scripts/run_mot_challenge.py`

## 比較対象・ベースライン

- validation 導入前の現状学習フロー
  - periodic checkpoint save のみ
  - 学習中 val loss なし
  - 学習中 TrackEval なし
- validation 導入後の新フロー
  - epoch ごとの val loss
  - 5 エポックごとの TrackEval
  - best checkpoint の自動保存

## 評価指標

### 学習健全性

- train epoch mean loss
- val epoch mean loss
- train / val gap

### tracking validation

- HOTA
- DetA
- AssA
- MOTA
- IDF1

## 成功/失敗の判断基準

### 成功

- train と val の loss を epoch ごとに安定して記録できる
- 5 エポックごとに TrackEval が自動で回り、主要指標が Comet に残る
- `best_val_loss.pth` と `best_tracking_hota.pth` が自動で保存される
- 手動で毎回推論・評価を回さなくても checkpoint 比較が可能になる

### 失敗

- train / val split が分離されず leakage が残る
- TrackEval 実行が不安定で、学習中フックとして継続運用できない
- best checkpoint の保存基準が曖昧で、どれを使うべきか判断できない

## 実施方針

- trajectory annotation を train / val に分離する
- 学習コードに `val loss` を追加する
- 5 エポックごとの tracking validation を TrackEval 経由で追加する
- `best_val_loss` と `best_tracking_hota` を分けて保存する

詳細な実装順、対象ファイル、確認手順は plan に分離して管理する。

## 期待される結果

- state carry 型で「loss は下がるが tracking 指標が伸びない」状況を早期に検知できる
- sliding window 型と state carry 型の checkpoint 比較がしやすくなる
- MIRU / ポスター向け比較実験の再現性が上がる

## リスク・懸念

- 5 エポックごとの TrackEval でも学習時間は増える
- tracker result directory に古い出力が残ると誤評価の原因になる
- `subprocess` ベースのため、失敗時の診断は初回実装ではやや粗い
- 将来 DDP 対応するときは `rank0 only` 制御が必要

## 未決事項

- TrackEval 実行時に tracker output を毎回上書きするか、epoch ごとに分けるか
- `tracking_val_period` を全モデルで統一するか、state carry 型だけ細かく見るか
- TrackEval の結果を Comet にどこまで詳細に残すか

## 関連brainstorm

- [2026-07-07-val-implementation-direction.md](../../../../secretary/notes/brainstorm/2026-07-07-val-implementation-direction.md)

## 関連plan

- [2026-07-07-validation-implementation-plan.md](../plans/2026-07-07-validation-implementation-plan.md)
