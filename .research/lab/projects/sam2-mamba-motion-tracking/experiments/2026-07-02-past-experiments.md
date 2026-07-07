# 過去実験ログ（2026年5月〜7月2日）

> 2026-07-07にMTG議事録の分析をもとに整理。詳細数値はNotionの各MTG記録を参照。

---

## 実験1：SAMURAI + Mamba 初期比較（5/21）

### 設定

- ベースライン：SAM2, SAMURAI, SAMURAI + Mamba
- 評価指標：HOTA
- Mamba motion predictor：MambaTrackと類似の設定でSAMURAIのカルマンフィルタ部分を置き換え

### 結果

| モデル | HOTA |
|--------|------|
| SAM2 | 0.46 |
| SAMURAI | 0.54 |
| SAMURAI + Mamba | 0.53 |

### 観察・考察

- **SAMURAI単体の方がSAMURAI+Mambaよりわずかに良い**
- MambaTrack論文の性能水準と比べてもまだ十分ではない
- SAM2/SAMURAI系はID維持は比較的得意だが，一度ドリフトすると補正が弱い
- SAMURAIの初期フレーム処理や，カルマンフィルタをいつから動かすかも性能に影響

### 結論

単純なKalman → Mamba置き換えでは性能向上を示せない。Mambaの内部状態の扱いを再検討が必要。

---

## 実験2：入力スケーリングの問題と修正（6/25）

### 問題の発見

- normalized bbox と bbox delta に同じ `scale_factor` を使っていた
- bboxが本来0〜1程度であるところ，過大に拡大されMamba内部でNaNが発生

### 修正

| 入力 | 修正前 | 修正後 | 参考（TrackSSM） |
|------|--------|--------|-----------------|
| bbox | scale_factor（過大） | 1倍 | scale_factor=20 |
| bbox delta | scale_factor（同じ） | 50倍 | scale_factor_diff=50 |

### 残課題

- bbox, bbox delta のヒストグラムを取り，各スケールの根拠を明確にする
- 平均0化が必要か確認
- Mamba内部のLayerNorm / RMSNormの位置を確認
- **state carryでは内部状態が蓄積されるため，スケーリングの影響がsliding windowより深刻になる可能性**

---

## 実験3：MambaTrack / TrackSSM / State carry型の比較（7/2）

### 設定上の問題（比較の注意点）

- MambaTrackは25エポックで学習不足の可能性
- TrackSSMはMambaTrackと入出力形式が異なっていた → 単純比較に誤解があった
- State carryは100エポック実施

→ **現時点では公平な比較になっていない**。同一条件での再実験が必要。

### 観察

- MambaTrack / TrackSSMはいずれも現状かなり精度が低い
- **State carry型は100エポックでそこそこの性能が出ており，収束しかけている**
- ただし，学習率スケジューラやvalidation設計はまだ不十分

### Validationの問題

- 通常のtrain lossは「次bboxを当てる」タスク → tracking全体の性能を反映しない
- HOTAなどの本来指標を5エポックごとなどで周期的に評価する仕組みが必要
- 計算コストやmulti-GPU対応が課題

---

## 公平な比較実験のための要件（今後）

同一条件での比較に必要なもの：

- [ ] 同一データ
- [ ] 同一epoch数または同等収束条件
- [ ] 同一評価指標（HOTA / DetA / AssA / MOTA / IDF1）
- [ ] 同一初期フレーム処理
- [ ] bbox / bbox delta のスケーリングを明示・統一
- [ ] 開発用val loss + 5エポックごとのHOTA評価 + 最終TrackEval
