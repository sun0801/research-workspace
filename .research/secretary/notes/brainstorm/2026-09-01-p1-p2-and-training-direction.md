---
date: 2026-09-01
project: sam2-mamba-motion-tracking
source_todo: null
topic: P1/P2を凍結してMamba学習改善へ進む方針
status: exploratory
tags: [brainstorm, research, state-carry, training, p1, p2]
---

# P1/P2を凍結してMamba学習改善へ進む方針

## 読み込んだ文脈

- P1では、prediction-primaryよりlast accepted observation-primaryの方が25系列でHOTA、AssA、IDF1が改善し、IDSWも減少した。
- P2では、missing freeze（B1）が非有限stateイベントを大幅に減らし、指標を小さく改善した。一方、単純trusted gate/reset（B2/B3）はassociationを悪化させた。
- SAM2最小統合は、元のMambaStatefulを再学習なしで動かす確認として完了している。P1/P2の改善はSAM2へ移植していない。
- 2026-08-28 MTGでは、state carry型Mambaの学習方法見直し、SAM2 decoder統合、Mamba/LSTM/Transformer比較を優先する方針が確認された。

## 相談の出発点

P1/P2を引き続き掘り下げるのではなく、Mambaの学習方法改善へ主線を移してよいかを判断する。

## 問い

P1/P2の診断結果をどのように固定すれば、association/cache更新の問題を再び混ぜずに、state carryの学習方法を検証できるか。

## 仮説

現在の大きな未解決要因は、sliding windowで学習したモデルを推論時だけstate carryで使っているtrain/inference mismatchである。recurrent unroll、teacher forcing/free running、TBPTTを含む学習へ変更すると、長いstate carry時のdriftや汚染が改善する可能性がある。

## 今回見えた方向性

- P1/P2は放置せず、完了済みの診断として凍結する。
- P1 A2（last accepted observation association）をassociation referenceとして保存する。
- P2 B1（missing freeze）はstate instabilityの診断referenceとして保存する。
- B2/B3の単純trusted gate/resetは現条件で悪化したため、当面再開しない。
- 次の主実験は、association方式・cache update方式・detector・評価条件を固定し、学習方式だけを変える。
- 最初からMamba/LSTM/Transformerやdecoder統合を全て同時に進めず、まずstateful recurrent学習の最小比較を成立させる。

## 次の実験設計候補

1. 現行のsliding-window学習 + state carry推論を再現するbaseline。
2. 同じモデル・入力・評価条件で、sequence unrollと時刻ごとのlossを用いるrecurrent学習。
3. teacher forcingからfree runningまたはscheduled samplingへ段階的に広げる。
4. state carryのdetach単位とTBPTT長を明示して比較する。
5. 最終的に、固定した選抜モデルをLSTM・Transformerと同程度GFLOPS・速度で比較する。

## 評価軸

- HOTAだけでなく、DetA、AssA、IDF1、IDSWを併記する。
- sequence別の改善・改悪を残す。
- state finite率、state/cache offset、missing区間後の再associationを記録する。
- 学習方式以外の差分を混ぜない。

## 未解決の問い

- 学習時の次入力をGT、accepted detection、self predictionのどこから始めるか。
- unroll長、detach単位、TBPTT長をどう設定するか。
- association referenceをB0またはB1のどちらに固定するか。
- 学習改善を先にMamba単体で検証するか、SAM2統合上で検証するか。

## 実装開始前の条件

学習変更は新しいspecとして、問い、比較条件、評価指標、成功基準を固めてから実装する。P1/P2およびSAM2最小統合の未コミット差分は、研究上の完了済み診断・統合確認として先に履歴へ残しておく。

## 関連ファイル

- `.research/lab/projects/sam2-mamba-motion-tracking/README.md`
- `.research/lab/projects/sam2-mamba-motion-tracking/meetings/2026-08-28-mtg.md`
- `.research/lab/projects/sam2-mamba-motion-tracking/specs/2026-07-23-p2-cache-update-control-spec.md`
- `.research/lab/projects/sam2-mamba-motion-tracking/experiments/2026-07-23-p2-cache-update-control.md`
- `.research/lab/projects/sam2-mamba-motion-tracking/experiments/2026-07-23-sam2-minimal-integration-25seq.md`
