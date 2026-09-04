---
date: 2026-09-04
project: sam2-mamba-motion-tracking
type: meeting-materials
topic: p4a-p4b-sam2-evaluation
status: draft
target_meeting: null
notion_url: null
notion_export: null
tags: [meeting-materials, p4a, p4b, sam2, trackeval, checkpoint]
---

# 2026-09-04 MTG資料: P4a学習とSAM2統合評価

## 0. 今日のMTGで先生に相談したいこと

1. P4aの主結果を「stateful unroll + TBPTTの成立」としてまとめ、tracking性能の改善は未確認という整理でよいか。
2. P4aのepoch100固定比較に加え、Mamba側tracking validationで最良だったepoch40をSAM2上でも補助評価するか。
3. SAM2デコーダーへのMamba統合へ進む前に、P4aの学習条件・checkpoint選択・評価provenanceをどこまで固めるか。
4. View 2ページ原稿では、P4aのnegative resultを含めて「predictor単体の安定性」と「MOT全体の性能」を分けて説明するか。

## 1. 現時点の結論

- P4aの実装・学習・checkpoint保存・GT-only validation・free rolloutは成立した。
- free rolloutはhorizon 32までnonfinite・divergenceなしだったが、これはtracking性能の改善を保証しない。
- P4bのepoch5固定比較では、P4aはL0に対してHOTA、AssA、IDF1で低下した。
- P4aのMamba側tracking validationはepoch40付近が最良で、epoch80以降にHOTAが低下した。
- 正しいP4a epoch100 checkpointを設定したSAM2 25系列推論は現在実行中であり、最終HOTAは未確定である。
- 以前の3系列TrackEval結果と、checkpoint provenanceが不明な25系列結果は主結果として採用しない。

## 2. 背景と今回の位置づけ

現在の研究課題は、SAM2/SAMURAIの動き予測をカルマンフィルタから学習ベースのMambaへ置換し、state carry型Mambaで生じるhidden state contaminationと長期予測誤差を調べることである。

現行L0では、固定長windowで学習したMambaを推論時にstate carryで利用していた。この学習時・推論時の不一致を解消するため、P4aでは同一trackを時系列順にunrollし、chunk境界でstateをdetachするTBPTT学習を導入した。

今回の評価は、次の流れを分離して確認するものである。

```text
P4a学習
  -> GT-only validation / free rollout
  -> checkpoint保存
  -> SAM2/SAMURAIへcheckpoint差し替え
  -> 固定条件TrackEval
```

P4aではP1/P2のassociation・cache規則、P3の入力分布混合、SAM2本体・decoder変更は行わない。

## 3. P4a学習設定と導入理由

### なぜunroll + TBPTTを導入したか

L0では、GT bboxから固定長windowを切り出し、各windowを独立に処理していた。したがって、学習中はwindowの外へstateをcarryしない。一方、推論時のMambaStatefulはtrackごとにhidden state / cacheを保持し、フレームをまたいで更新する。

この差により、L0は「固定windowで学習した予測器を、推論時だけstate carryで使う」構成になっていた。P4aでは、学習時にも同じtrackの時系列を順番に処理してstateをcarryし、推論時の利用形態に近づけることを狙った。

ただし、動画全体を一度に逆伝播するとGPUメモリと計算グラフが過大になる。そのため、時系列をchunkへ分割し、chunk内ではstateをcarryしながら逆伝播し、chunk境界で過去の計算グラフだけを切るTBPTTを用いた。

```text
同一trackの時系列
  -> 48 step unroll
  -> 12 stepごとにTBPTT detach
  -> stateの値は次chunkへcarry、過去のgradient graphは切断
```

### P4aの主要設定

| 項目 | 設定 | 意図 |
|---|---|---|
| 学習単位 | 同一trackの時系列chunk | 推論時のtrack単位state carryに近づける |
| `unroll_length` | 48 | 1 chunk内で時系列stateをcarryする範囲 |
| `tbptt_length` | 12 | 逆伝播する計算グラフの長さを制限 |
| state初期化 | track/video開始時にzero reset | 異なるtrack・動画間のstate混線を防ぐ |
| chunk境界 | state値はcarry、gradient graphはdetach | 長期状態を保持しつつメモリを制御 |
| 入力 | GT-only bbox | association誤りや検出ノイズを混ぜず学習方法を比較 |
| 入力形式 | 4次元 bbox、bbox scale `1` | L0と一致 |
| target | 次時刻のbbox delta、delta scale `50` | L0と一致 |
| loss | Smooth L1、`loss_start_index=4` | warm-up後の予測を学習し、外れ値の影響を抑制 |
| model | `d_m=256`, `d_state=16`, `d_conv=4`, `expand=2`, `L=3` | L0と同じMamba構成 |
| optimizer | Adam、`lr=1e-4` | 現行stateful設定を維持 |
| scheduler | none | 今回は学習方法の差に集中するため変更しない |
| batch size | 64 | 実行時の初期設定 |
| gradient clipping | norm `1.0` | 勾配の急激な発散を抑える |
| epochs | 100 | L0とのepoch100固定比較に合わせる |
| seed | 0 | L0/P4a間の再現条件を固定 |

### 比較から意図的に外したもの

P4aの効果を学習方法の差として切り分けるため、初期比較では以下を導入していない。

- accepted detectionやself predictionを混ぜるP3の入力分布混合
- P1のassociation方式変更
- P2のcache gate、reset、追加の更新制御
- Mamba内部architectureの変更
- SAM2/SAMURAI decoderの変更

したがって、P4aが検証する問いは「入力分布やtracker規則を変えず、学習時のstate carry + TBPTTだけを導入した場合に、predictor単体およびtracking性能が改善するか」である。

## 4. 実施したこと

### P4a学習・validation

- L0互換のtrain loggingを追加。
- trainと分離したGT-only validationを追加。
- stateful unroll + TBPTTで学習。
- free rolloutをhorizon `1, 4, 8, 16, 32`で測定。
- state、gradient、lossのfinite性を記録。
- epoch checkpointとmanifest、checkpoint hashを保存。
- epoch10, 20, ..., 100でtracking validationを実行。

### SAM2統合・provenance

- `samurai_mamba_stateful`へP4a epoch100 checkpointを差し替えて25系列推論を開始。
- 推論開始前にconfigの`motion_model_ckpt`をP4a pathへ置換し、表示で確認。
- SAM2推論スクリプトへ、各シーケンスのComet Experimentにcheckpoint pathとcheckpoint assetを保存する処理を追加。
- 変更後のPython構文確認を完了。
- P4a checkpointでの25系列推論では、ログに以下のロード成功を確認済み。

```text
Loaded exact MambaStateful checkpoint:
.../mamba_stateful_tbptt_p4a_full/p4a_full_100ep_20260903/epoch100.pth
```

## 5. Evidence: P4a predictor単体の結果

### Free rollout

| horizon | IoU | MAE | nonfinite / divergence |
|---:|---:|---:|---:|
| 1 | 0.7845 | 0.0126 | 0 / 0 |
| 4 | 0.5295 | 0.0364 | 0 / 0 |
| 8 | 0.4365 | 0.0443 | 0 / 0 |
| 16 | 0.3324 | 0.0543 | 0 / 0 |
| 32 | 0.2480 | 0.0697 | 0 / 0 |

観測事実として、長期rolloutでも数値発散は発生しなかった。一方、horizonの増加に伴ってIoUは低下するため、長期予測誤差そのものは残っている。

### Mamba側のepoch別tracking validation

| epoch | HOTA | DetA | AssA | MOTA | IDF1 | IDSW |
|---:|---:|---:|---:|---:|---:|---:|
| 10 | 54.216 | 83.1 | 35.9 | 91.0 | 53.2 | 98 |
| 20 | 54.330 | 83.1 | 35.9 | 91.0 | 53.3 | 98 |
| 30 | 55.101 | 83.1 | 36.9 | 91.0 | 53.5 | 97 |
| 40 | **55.317** | 83.1 | 36.9 | 91.0 | 53.5 | 97 |
| 50 | 55.316 | 83.1 | 36.9 | 91.0 | 53.5 | 97 |
| 60 | 55.314 | 83.1 | 36.9 | 91.0 | 53.5 | 97 |
| 70 | 55.314 | 83.1 | 36.9 | 91.0 | 53.5 | 97 |
| 80 | 54.429 | 83.1 | 35.7 | 91.0 | 53.3 | 98 |
| 90 | 54.429 | 83.1 | 35.7 | 91.0 | 53.3 | 98 |
| 100 | 54.430 | 83.1 | 35.7 | 91.0 | 53.3 | 98 |

epoch40〜70でHOTAが最大となり、epoch80以降に低下している。学習lossが低下してもtracking性能が単調に改善するとは限らない。

### epoch5のL0/P4a固定比較

| model | HOTA | DetA | AssA | MOTA | IDF1 | IDSW |
|---|---:|---:|---:|---:|---:|---:|
| L0 | 53.971 | 83.095 | 35.073 | 90.971 | 53.165 | 98 |
| P4a | 53.240 | 82.400 | 34.414 | 90.993 | 52.365 | 100 |
| P4a - L0 | -0.731 | -0.695 | -0.659 | +0.022 | -0.800 | +2 |

## 6. Evidence: SAM2統合評価の進捗

### 既存のSAM2統合reference

旧L0 stateful checkpointをSAM2/SAMURAIへ統合した既存25系列結果は次のとおりである。

| model | HOTA | DetA | AssA | MOTA | IDF1 | IDSW |
|---|---:|---:|---:|---:|---:|---:|
| SAM2 | 51.269 | 45.514 | 58.259 | 30.824 | 58.494 | 1,618 |
| SAMURAI | 54.109 | 47.885 | 61.480 | 33.797 | 62.327 | 1,517 |
| 旧L0 stateful epoch100 | **55.520** | **49.601** | **62.482** | **36.587** | **64.154** | 1,535 |

これらはP4aのSAM2 25系列最終結果と比較するための既存referenceである。

### 今回のP4a epoch100 SAM2 run

- output run: `sam2_p4a_epoch100_25seq_20260904`
- mode: `samurai_mamba_stateful`
- SAM2 model: `tiny`
- split: DanceTrack val 25 sequences
- checkpoint: P4a `epoch100.pth`
- `--save_candidate_debug`: 使用しない
- 2026-09-04資料作成時点で16/25系列の推論結果を確認。
- `dancetrack0058`ではCometに15.86 MBのcheckpoint assetがuploadされ、P4a checkpointのロード成功ログも確認。
- 25系列の最終TrackEval summaryは未確定。

### 採用しない中間結果

- `HOTA 50.304`：TrackEvalのデフォルトseqmapにより3系列のみを評価した結果。25系列結果ではない。
- `HOTA 53.871`：25系列集計ではあるが、実行時checkpoint provenanceが不明で、P4a主結果としては採用しない。

## 7. Interpretation: 現時点の解釈

### 支持される解釈

- P4aは、推論時のstate carryに近い学習経路として実装・再ロード・数値安定性を満たした。
- GT-only free rolloutではhorizon32まで発散しなかったため、P4aのstateful学習経路が直ちに数値不安定になるわけではない。
- しかし、predictor単体のfinite性やfree rolloutの安定性は、MOTのidentity association改善とは別の性質である。
- epoch5の固定比較ではP4aがL0を上回らず、少なくとも初期epochでは「TBPTTによりtracking性能が改善する」という仮説は支持されていない。
- Mamba側tracking validationではepoch40付近が最良であり、epoch100を自動的に最良checkpointとみなす根拠は弱い。

### まだ言えないこと

- SAM2統合上でP4a epoch100が旧L0 statefulを上回るかは、正しい25系列TrackEval結果が出るまで未確定。
- P4aのtracking性能低下が、TBPTTそのもの、checkpoint選択、学習率、SAM2との相互作用のどれに起因するかは未分離。
- free rolloutの改善または非発散が、実際のオクルージョン・誤association下でのhidden state contamination抑制につながるとはまだ言えない。

## 8. 方針候補・比較

| 方針 | 内容 | 利点 | 懸念 |
|---|---|---|---|
| A | P4a epoch100のSAM2 25系列結果を主比較として確定 | specどおりで比較が明快 | P4aがL0を下回る可能性がある |
| B | epoch40 checkpointもSAM2上で補助評価 | Mamba側best epochとSAM2側の対応を確認できる | 評価コストが増え、checkpoint選択の後付けに見える可能性 |
| C | まずP4aの学習条件を再検討 | tracking低下の原因分析を優先できる | decoder統合など次課題の開始が遅れる |
| D | P4aのnegative resultを固定し、decoder統合へ進む | 研究ストーリーを次段階へ進められる | stateful学習の改善余地を残す |

## 9. Ask: 相談したい判断

- P4a epoch100を主比較として報告し、epoch40は補助的なcheckpoint選択分析にとどめるか。
- SAM2上でepoch40も追加評価するか。それとも、まずepoch100の結果だけでP4aの有効性を判断するか。
- P4aがL0を下回った場合、次の優先順位を「学習条件の再検討」「hidden state contaminationの可視化」「SAM2 decoder統合」のどれに置くか。
- View原稿では、P4aを性能改善手法としてではなく、stateful学習の成立性と失敗要因を切り分ける実験として位置づけるか。
- Cometへのcheckpoint asset保存は、今回の簡易方式（シーケンスごとに同一checkpointを保存）を当面採用するか。

## 10. 次に進む候補

1. 正しいP4a epoch100 SAM2 25系列推論の完了を確認する。
2. `SEQ_INFO`で25系列を明示してTrackEvalを実行する。
3. P4a epoch100と旧L0 stateful epoch100を、同じSAM2条件で比較する。
4. 必要ならepoch40 checkpointを同じ条件で補助評価する。
5. P4aの学習条件、checkpoint選択、hidden state contaminationのうち、次に検証する対象を決める。

## 11. 参照ファイル

- [P4a stateful unroll + TBPTT spec](../specs/2026-09-01-p4a-stateful-unroll-tbptt-spec.md)
- [P4a periodic checkpoint tracking validation spec](../specs/2026-09-02-p4a-periodic-checkpoint-tracking-validation-spec.md)
- [P4b checkpoint tracking evaluation spec](../specs/2026-09-02-p4b-checkpoint-tracking-evaluation-spec.md)
- [P4b epoch5 experiment](../experiments/2026-09-02-p4b-checkpoint-tracking-evaluation.md)
- [Project README](../README.md)
- P4a epoch100 artifacts: `/mnt/HDD10TB-2/aburatani/2025_09_aburatani_Mamba_Trackers/ssm_tracker/saved_ckpts/mamba_stateful_tbptt_p4a_full/p4a_full_100ep_20260903/`
- P4a SAM2 output: `/mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2/results/sam2_p4a_epoch100_25seq_20260904/`
- P4a SAM2 TrackEval output: `/mnt/HDD10TB-2/aburatani/TrackEval/data/trackers/dancetrack/val/sam2_p4a_epoch100_25seq_20260904/`
- SAM2 inference entrypoint: `/mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2/scripts/main_inference_mot.py`
