---
date: 2026-07-22
project: sam2-mamba-motion-tracking
tags: [brainstorm, p1, p2, cache-update, decision]
---

# P2以降へ進む判断

## 問い

P1のassociation separation結果を受けて、P2以降のstate carry改善実験へ進むべきか。

## 現在の根拠

- 3系列でA2（last accepted observation association）がA1（prediction-primary）を改善した。
- A2はHOTA 54.870、AssA 36.229、IDF1 53.660、ID switches 94で、A1比でHOTA +5.204、AssA +6.248、IDF1 +8.648、ID switches -12。
- checkpoint、detector、scale、lifecycle、state/cache更新、TrackEval条件は固定され、association主位置の因果診断として成立している。
- ただしA2もmissing時のself-updateを残しているため、cache contaminationの影響は未分離である。

## 判断

P2へ進む根拠はある。ただし、P1結果だけでP2を実装・実行せず、別specで変更範囲と成功基準を固定する。

## 推奨する次の実験

1. A2を固定したreferenceとして再利用する。
2. trusted match時だけstate/cacheを更新する条件を追加する。
3. missing/self prediction時のfreeze条件を比較する。
4. 連続untrusted frame後のreset条件は、freezeとは別条件として扱う。
5. まず3系列で、update/freeze/reset回数、state norm、long-miss後の再associationを記録する。
6. 小規模結果が整合する場合のみ、25系列または別splitへ拡張する。

## 進まない方がよい範囲

- P2と同時にP3の入力分布混合を入れない。
- P4のteacher forcing/TBPTTや学習方式変更を入れない。
- MambaTrack/TrackSSMのアルゴリズムコードを変更して比較条件を混ぜない。

## 未解決点

- trusted matchの定義（first-stage match、second-stage re-activate、confidence threshold）
- freeze対象がhidden stateだけか、bbox/historyも含むか
- resetの発火条件とreset後のtrack lifecycle
- 3系列結果を25系列へ拡張するタイミング
