---
date: 2026-07-30
project: sam2-mamba-motion-tracking
type: meeting-materials
topic: sam2-integration-and-miru-progress
status: draft
target_meeting: null
notion_url: null
notion_export: null
tags: [meeting-materials, research, sam2, state-carry, miru]
---

# 2026-07-30 MTG資料: SAM2統合・MIRU定性結果の進捗

## 0. 今日のMTGで先生に相談したいこと

1. SAM2最小統合では、epoch100を現時点の暫定基準として扱い、`best_tracking_hota.pth` を最良checkpointとは主張しない整理でよいか。
2. `kf_score_weight=0.0/0.5` は25系列のHOTA差が0.004とほぼ無視できるため、重み調整を打ち切り、SAM2上の対照条件・quality-aware updateの検証へ進んでよいか。
3. MIRUポスターでは、まず `dancetrack0034` などの定性候補をViewerで人手確認し、state carryの優位性ではなく「SAM2/SAMURAIの局所的な追跡失敗をMamba統合で継続できる例」として提示してよいか。
4. 次の実験では、同一SAM2条件でMambaなし／stateful Mamba／可能ならsliding-window Mambaを揃え、checkpoint・association・scale・lifecycleを固定して比較する方針でよいか。

## 1. 現時点の結論

- 7/23に、scale修正後のMamba単体でP1/P2の25系列診断と、元のMambaStatefulのSAM2/SAMURAI最小統合を完了した。
- 7/27のSAM2統合checkpoint比較では、epoch100がHOTA 55.520、元repoの`best_tracking_hota.pth`（metadata上epoch20）がHOTA 54.606だった。SAM2上ではepoch100が高かったが、2 checkpointの比較だけでは最適epochや一般的なcheckpoint選択則は決められない。
- 7/28の`kf_score_weight`比較では、0.0と0.5のHOTA差は0.004で、今回の25系列条件では実質的な差を確認できなかった。重み調整は主要な改善要因ではなさそうである。
- MIRU向けには、SAM2/SAMURAIの局所的な失敗とstateful統合の改善を対応付けた候補CSV・短い候補表を作成した。ただし、候補は自動抽出結果であり、ポスター掲載可否はViewerでの目視確認が未完了である。
- 現時点で確認できたのは「元のstateful MambaをSAM2へstrict loadし、fallbackなしで25系列推論・評価できること」と「局所的な定性改善候補があること」であり、state carry全体の優位性やP1/P2のSAM2上の改善量まではまだ主張できない。

## 2. 前回MTGからの1週間の進捗（7/23–7/30）

| 日付 | 実施内容 | 現時点の判断 |
|---|---|---|
| 7/23 | P1 association separationを25系列へ拡張。P2のB0〜B3を25系列で比較。元MambaStatefulをSAM2/SAMURAIへ最小統合し、epoch100で評価。 | P1 A2をreferenceとして固定。P2 B1は診断結果、B2/B3は採用しない。SAM2統合導線は成立。 |
| 7/24–7/26 | 新規の日付付き実験ログは確認できず。 | 7/23の統合結果とMIRU向け追加分析を基準に整理。 |
| 7/27 | SAM2上で元repoの`best_tracking_hota.pth`を比較。MIRU向けに失敗遷移・定性候補・Viewer確認候補を抽出。 | SAM2上のcheckpoint最適性は未確定。定性候補はViewer確認へ進める。 |
| 7/28 | `kf_score_weight=0.0/0.5`をepoch100・25系列で比較。MIRU向けの条件を緩めた失敗遷移候補を追加。 | score重みの影響は小さい。候補は主張候補と補助候補を分けて扱う。 |
| 7/29–7/30 | 追加の実験ログは確認できず。 | 次の判断論点を、SAM2上の対照条件と定性候補の人手確認へ絞る。 |

## 3. Evidence: 7/23 P1/P2診断（Mamba単体）

SAM2統合結果と混同しないため、P1/P2はMambaTrackers側の独立診断として扱う。

### P1: association主位置の分離

| 条件 | HOTA | AssA | IDF1 | IDSW |
|---|---:|---:|---:|---:|
| A1 prediction-primary | 47.233 | 29.907 | 45.886 | 2,578 |
| A2 last accepted observation-primary | **47.910** | **30.843** | **47.315** | **2,386** |
| A2 - A1 | +0.677 | +0.936 | +1.429 | -192 |

- HOTAは17/25系列、AssAは19/25系列、IDF1は17/25系列でA2が改善。
- 効果は一様ではなく、`dancetrack0097`ではA2のHOTAがA1より0.103低下。
- したがって、A2はP2を検討するreferenceとしては支持されるが、最終方式の性能保証ではない。

### P2: missing/cache update control

| 条件 | missing | cache update | HOTA | AssA | IDF1 | IDSW | nonfinite events |
|---|---|---|---:|---:|---:|---:|---:|
| B0 | self-update | all | 47.910 | 30.843 | 47.315 | 2,386 | 4,515 |
| B1 | freeze | all | **48.035** | **31.077** | **47.661** | 2,392 | **115** |
| B2 | freeze | trustedのみ | 46.962 | 29.510 | 44.179 | 3,836 | 0 |
| B3 | freeze | trustedのみ + reset | 46.855 | 29.380 | 44.177 | 3,833 | 0 |

- B1はmissing時のself-updateを止めることで、state非有限イベントを大幅に減らし、指標を小さく改善した。
- B2/B3はstate非有限イベントを0にしたが、古いobservationが残る副作用によりassociationとID指標が悪化した。
- 現状の単純trusted gate/resetは採用せず、観測bboxの保持とMamba state/cache更新を分離するquality-aware設計を別途検討する。

## 4. Evidence: SAM2/SAMURAI最小統合

### 4.1 epoch100と元repo best-HOTA checkpoint

同じSAM2 tiny、DanceTrack val 25系列、scale、lifecycle、state carry、P1/P2無効の条件で比較した。

| 指標 | epoch100 | best-HOTA checkpoint（metadata上epoch20） | 差分（best - epoch100） |
|---|---:|---:|---:|
| HOTA | **55.520** | 54.606 | -0.914 |
| DetA | **49.601** | 48.609 | -0.992 |
| AssA | **62.482** | 61.691 | -0.791 |
| MOTA | **36.587** | 34.595 | -1.992 |
| IDF1 | **64.154** | 62.813 | -1.341 |
| IDSW | 1,535 | **1,525** | -10 |

両runともcheckpointロード済み、fallbackなし、`used_window_recompute=False`を確認した。epoch100の方がHOTA等は高いが、IDSWだけはbest-HOTA checkpointが10少ない。元repoのvalidation HOTAで選択したcheckpointが、SAM2上の最良checkpointになるとは限らない。

### 4.2 `kf_score_weight`比較

epoch100 checkpoint固定で、SAM候補IoUとMamba予測bbox IoUの重みだけを変更した。

| 指標 | kfw=0.0 | kfw=0.5 | 差分（0.5 - 0.0） |
|---|---:|---:|---:|
| HOTA | 53.911 | **53.915** | +0.004 |
| DetA | 48.256 | **48.353** | +0.097 |
| AssA | **60.572** | 60.454 | -0.118 |
| MOTA | 34.464 | **34.765** | +0.301 |
| IDF1 | **61.734** | 61.727 | -0.007 |
| IDSW | 1,576 | **1,559** | -17 |

HOTA差は0.004であり、25系列aggregateでは実質的な差を確認できなかった。kfw=0.5はMOTA/IDSW、kfw=0.0はAssA/IDF1でわずかな利点があるため、単一指標だけで採用値を決める根拠は弱い。

## 5. Evidence: MIRU定性候補

7/27にSAM2 / SAMURAI / Mamba stateful epoch100の共通25系列を対象に、GT IoU・coverage差・SAM2低IoUなどから30候補を自動抽出した。これは自動ランキングであり、ポスター掲載前にViewerで目視確認する。

### 候補を絞った手順

今回の候補抽出は、statefulの結果を先に見て都合のよい例を選ぶのではなく、ベースライン側の失敗・不安定化を起点に、同じsequence・同じ対象・同じフレーム区間を対応付ける方針にした。

| 段階 | 対象・処理 | 絞り込みの目的 |
|---|---|---|
| 1. 比較runの固定 | 共通して結果が存在するDanceTrack val 25系列を対象に、SAM2、SAMURAI、SAM2 + Mamba stateful epoch100を比較。 | sequence・checkpoint・出力の対応が取れない例を混ぜない。 |
| 2. sequence単位の層化 | TrackEvalのHOTA/AssA/IDF1/IDSWとsequence集計を参照し、ベースラインが難しいsequence、statefulとの差が大きいsequence、代表的なsequenceを候補母集団にする。 | 改善例だけでなく、難例・代表例・限界例を残す。sequence全体の指標だけでは掲載候補を確定しない。 |
| 3. フレームイベント抽出 | GT IDを参照軸にして、各手法のGT boxに対するフレームごとの最大IoU、coverage、trackの出現・消失、bboxの漂流や急変を確認。 | 「見失い」「位置ずれ」「再追跡」など、時系列で説明できるイベントを見つける。 |
| 4. 固定長window化 | イベント前後を含むおおむね6フレームの区間にまとめ、同一フレーム範囲で3手法を比較。 | 1フレームだけの偶然の差ではなく、追跡継続の変化として説明できるようにする。 |
| 5. 予備ランキング | 6フレーム窓でのstateful対SAM2の平均IoU差、coverage@0.5の差、SAM2の低IoUを組み合わせてランキング。candidate debugのstate carry利用率・fallbackも確認。 | Viewerで確認する候補数を減らし、statefulの改善が時系列で明確な候補を上位に置く。 |
| 6. 失敗パターンの多様化 | 両ベースラインが崩れる例、SAMURAIが部分的に改善した後にstatefulがさらに改善する例、statefulの限界・対照例を分ける。 | 「最良例だけ」の選択バイアスを避け、ポスターの主張範囲を明確にする。 |
| 7. Viewerで人手確認 | 同じ動画・sequence・フレームをSAM2/SAMURAI/statefulで並べ、対象の消失、ID切替、box位置ずれ、遮蔽や対象交差の有無を確認。 | 自動指標だけでは確定できない「本当に同じ対象を追えているか」とポスター上の見やすさを確認する。 |

自動ランキングで重視したのは、statefulの平均IoUが高いことだけではない。ベースラインが低下していること、6フレームにわたって差が続くこと、stateful側でfallbackがなくstate carryが利用されていることを合わせて確認した。なお、候補スコアは予備的な順位付けであり、固定した真理値や最終採用基準ではない。

### 候補の生成物と現在の位置づけ

- **自動抽出候補**: 共通25系列から30件。stateful対SAM2の局所差を中心にランキングした。
- **厳密な失敗遷移候補**: `dancetrack0034 / GT ID 9`の1件。直前まで両ベースラインが追跡できていた対象が、その後に崩れ、statefulが維持する条件を厳しく設定した。
- **条件を緩めた追加候補**: 5件。直前のベースラインIoUや失敗後のIoU条件を少し緩和し、別sequence・別パターンの候補を追加した。
- **Viewer確認用shortlist**: 主候補4件に加えて、SAMURAIも成功する対照例など2件を用意した。候補間の重複があるため、上記件数を足し合わせて候補総数とは扱わない。

### ポスター候補としての層化

現時点では、以下の役割で確認する順序を考えている。

1. **主ストーリー**: `dancetrack0034 / GT ID 9` — 両ベースラインの失敗遷移とstatefulの追跡継続。
2. **SAMURAI改善後の上乗せ候補**: `dancetrack0034 / GT ID 7` — SAMURAIが一部改善してもstatefulとの差が残る局所例。
3. **別sequenceでの再現候補**: `dancetrack0007 / GT ID 6` — SAM2/SAMURAIが見失い、statefulが継続する例。
4. **条件緩和後の追加候補**: `dancetrack0081 / GT ID 12` — 厳密条件外でも同じ傾向が見えるかの確認。
5. **対照・限界例**: SAMURAIも成功する区間やstatefulが改善しない区間 — 改善が常に起こるように見せないための確認。

このため、現在の4件は「ポスター掲載決定」ではなく、最初にViewerで見る優先候補である。最終採用は、同じGT IDを直接手法別track IDと同一視せず、GTとの対応、対象の見た目、ID切替、boxの位置を確認した後に決める。

### まず確認する主候補

| sequence / GT ID | フレーム | SAM2 IoU | SAMURAI IoU | stateful IoU | 目的 |
|---|---:|---:|---:|---:|---|
| `dancetrack0034 / 9` | 335–340 | 0.259 | 0.225 | **0.941** | 両ベースラインの失敗遷移に対する継続例 |
| `dancetrack0034 / 7` | 878–883 | 0.000 | 0.111 | **0.976** | SAMURAI改善後もstatefulが改善する局所例 |
| `dancetrack0007 / 6` | 673–678 | 0.000 | 0.000 | **0.994** | 両ベースラインが見失い、statefulのみ継続する例 |
| `dancetrack0081 / 12` | 236–241 | 0.082 | 0.096 | **0.953** | 条件を緩めた失敗遷移の追加候補 |

`dancetrack0034 / GT ID 9`では、直前327–334フレームの平均IoUがSAM2 0.758、SAMURAI 0.746、stateful 0.811で、335–340フレームではSAM2 0.259、SAMURAI 0.225、stateful 0.941となった。statefulは該当区間でtrue state carry使用率100%、fallbackなしだった。

ただし、IoUはGT boxに対する局所的な最大IoUであり、候補抽出だけでID維持や原因を確定するものではない。Viewerで「消失」「ID切替」「box位置ずれ」を区別して記録する必要がある。

## 6. Interpretation: 現時点の見立て

- 研究実装としては、元repoのstateful checkpointをSAM2へ移植し、strict load・state carry・25系列TrackEvalまでの再現可能な導線を確保できた。
- 元repoでのcheckpoint選択とSAM2統合上のcheckpoint選択は一致しない可能性がある。現時点ではepoch100を暫定基準にするのが自然だが、最適checkpointの結論ではない。
- `kf_score_weight` は今回の範囲では主要な性能ボトルネックではなさそうであり、ここを細かく調整するよりも、Mambaなし対照・association・state/cache更新の因果を揃える方が情報量が大きい。
- MIRUの定性候補は、statefulの有効性を示す可能性がある。一方、良い局所例の選択だけで系列全体の改善やstate carry一般の優位性を主張してはいけない。
- 7/23 MTGで決めた通り、P1/P2のMamba単体診断とSAM2統合の結果は分けて解釈する必要がある。SAM2上でP1/P2がどの程度効くかは未検証である。

## 7. Ask: 今回確認したい方針

### A. SAM2の基準条件

- epoch100を暫定canonical checkpointとして保持する。
- `best_tracking_hota.pth` は「元repoで選択された別checkpoint」として比較対象に留め、SAM2上のbestとは表現しない。
- `kf_score_weight` は0.0または0.5のどちらかを、HOTA単独ではなく主指標の優先順位と合わせて固定する。追加の細かい探索は優先しない。

### B. 次の定量実験

優先順位案は以下。

1. 同一SAM2条件でMambaなしの対照runを揃える。
2. epoch100 stateful Mambaとの比較を行う。
3. 同一条件のsliding-window出力が揃った場合のみ、state carryとの比較を追加する。
4. その後、SAM2側のassociationおよびquality-aware state/cache updateを、変更を混ぜずに段階検証する。

必要な固定項目は、checkpoint、detector、scale、association、track lifecycle、sequence list、TrackEval設定、fallback禁止、manifest/provenanceである。

### C. MIRU定性結果

- まず `dancetrack0034 / 9`、`dancetrack0034 / 7`、`dancetrack0007 / 6` の順にViewer確認する。
- 掲載候補は「改善例」だけでなく、SAMURAIでも追跡できる対照例やstatefulが失敗する限界例を含める。
- 6〜8フレーム程度の時系列、sequence名、フレーム範囲、比較条件、GT IDと手法別track IDの対応を記録する。
- Viewer確認後、採用例が決まれば`materials/figures/`にポスター用再構成図を作る。

## 8. 今回言えること / まだ言えないこと

### 今回言えること

- P1 A2は、Mamba単体の25系列診断でprediction-primaryよりassociation関連指標を改善した。
- P2 B1は、missing self-updateをfreezeすることでstate非有限イベントを大きく減らしたが、改善は限定的だった。
- 元のMambaStatefulは、SAM2/SAMURAIへfallbackなしで統合され、25系列でHOTA 55.520を得た（epoch100条件）。
- SAM2上では、元repoのbest-HOTA checkpointよりepoch100のHOTAが高かった。
- `kf_score_weight=0.0/0.5`の差は、今回の25系列ではHOTA上ほぼ無視できる。
- MIRU向けに、複数フレームでstatefulの局所改善を確認する候補を抽出できた。

### まだ言えないこと

- state carry型Mambaがsliding window型より優れている、または劣っているという結論。
- SAM2上でP1/P2の改善が再現するという結論。
- epoch100がSAM2上の最適checkpointであるという結論。
- `kf_score_weight` の最適値。
- 自動抽出した定性候補が、ポスターに適した代表例であるという最終判断。

## 9. 次に進む候補

- [ ] SAM2 baseline（Mambaなし）を同一25系列・同一TrackEval条件で整理する | 優先度: 高
- [ ] epoch100 stateful Mambaとbaselineのprovenance・結果表を統合する | 優先度: 高
- [ ] MIRU定性主候補をViewerで確認し、消失・ID切替・位置ずれを記録する | 優先度: 高
- [ ] 必要ならSAM2側のassociationまたはquality-aware updateを別specで計画する | 優先度: 通常
- [ ] 同一条件のsliding-window 25系列出力が揃うか確認する | 優先度: 通常

## 10. 図・生成物

今回、新規の図は作成していない。

- 定性候補CSV: `../experiments/2026-07-27-miru-qualitative-candidate-selection.csv`
- 失敗遷移候補CSV: `../experiments/2026-07-27-miru-baseline-failure-transition.csv`
- 条件緩和後の候補CSV: `../experiments/2026-07-28-miru-relaxed-failure-transitions.csv`
- Viewer確認候補: `../experiments/2026-07-27-miru-viewer-shortlist.md`

Viewer確認後に、採用する時系列を`materials/figures/`へ再構成する。

## 11. 参照ファイル

- [プロジェクトREADME](../README.md)
- [前回MTG議事録](../meetings/2026-07-23-mtg.md)
- [P1 25系列結果](../experiments/2026-07-23-p1-association-separation-25seq.md)
- [P2 cache update control結果](../experiments/2026-07-23-p2-cache-update-control.md)
- [SAM2最小stateful統合結果](../experiments/2026-07-23-sam2-minimal-integration-25seq.md)
- [SAM2 best-HOTA checkpoint比較](../experiments/2026-07-27-sam2-minimal-integration-best-hota-25seq.md)
- [`kf_score_weight`比較](../experiments/2026-07-28-sam2-kf-score-weight-epoch100-25seq.md)
- [MIRU定性候補抽出](../experiments/2026-07-27-miru-qualitative-candidate-selection.md)
- [MIRU失敗遷移候補](../experiments/2026-07-27-miru-baseline-failure-transition.md)
- [MIRU条件緩和後の候補](../experiments/2026-07-28-miru-relaxed-failure-transitions.md)
- [MIRU候補抽出spec](../specs/2026-07-27-miru-qualitative-candidate-selection-spec.md)
- [SAM2最小統合spec](../specs/2026-07-23-sam2-stateful-mamba-minimal-integration-spec.md)
- [P2 cache update control spec](../specs/2026-07-23-p2-cache-update-control-spec.md)
