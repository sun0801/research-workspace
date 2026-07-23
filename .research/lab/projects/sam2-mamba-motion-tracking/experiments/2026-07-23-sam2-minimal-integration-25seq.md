---
date: 2026-07-23
project: sam2-mamba-motion-tracking
status: completed
tags: [experiment, sam2, samurai, mamba-stateful, integration, trackeval, 25-seq]
---

# SAM2最小stateful Mamba統合: 25系列評価

## 目的

元Mamba repoの`MambaStateful`をSAM2/SAMURAIのMOT推論へ最小構成で移植し、25系列の推論出力が生成され、TrackEvalで評価できることを確認する。P1/P2の変更はSAM2側へ持ち込まず、元のstate carry挙動を固定する。

## 実験条件

- run_id: `20260723T_sam2_minimal_25seq`
- mode: `samurai_mamba_stateful`
- SAM2 model: `tiny`
- input: `data/DanceTrack/val/val`
- sequence split: `data/DanceTrack/testing_set.txt`（25系列）
- Mamba checkpoint: `mamba_stateful_dancetrack/epoch100.pth`
- Mamba architecture: `d_m=256`, `d_state=16`, `d_conv=4`, `expand=2`, `L=3`
- scale: bbox `1`, delta `50`
- P1/P2: `false`
- fallback: 不許可
- TrackEval: HOTA/CLEAR/Identity、`DO_PREPROC=False`、25系列を`SEQ_INFO`で明示

checkpointはepoch100を使用した。`best_tracking_hota.pth`（保存metadata上はepoch20）ではないため、本結果は「最終epoch固定の統合確認値」であり、checkpoint選択の最良値ではない。

## 成果物

- SAM2 manifest: [`manifest.json`](/mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2/results/sam2_stateful_minimal/20260723T_sam2_minimal_25seq/manifest.json)
- Track output: `/mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2/results/sam2_stateful_minimal/20260723T_sam2_minimal_25seq/samurai_mamba_stateful_tiny/`
- TrackEval summary: [`pedestrian_summary.txt`](/mnt/HDD10TB-2/aburatani/2025_09_aburatani_Mamba_Trackers/artifacts/sam2_minimal_integration/trackeval/sam2_stateful_minimal_20260723T_sam2_minimal_25seq_epoch100_seqinfo/sam2_stateful_minimal_20260723T_sam2_minimal_25seq_epoch100/pedestrian_summary.txt)
- TrackEval detailed CSV: [`pedestrian_detailed.csv`](/mnt/HDD10TB-2/aburatani/2025_09_aburatani_Mamba_Trackers/artifacts/sam2_minimal_integration/trackeval/sam2_stateful_minimal_20260723T_sam2_minimal_25seq_epoch100_seqinfo/sam2_stateful_minimal_20260723T_sam2_minimal_25seq_epoch100/pedestrian_detailed.csv)
- candidate debug: 25 files、245,291 rows

## TrackEval結果

| 指標 | combined |
|---|---:|
| HOTA | **55.520** |
| DetA | 49.601 |
| AssA | 62.482 |
| DetRe | 67.227 |
| DetPr | 62.731 |
| AssRe | 72.210 |
| AssPr | 70.377 |
| LocA | 87.260 |
| MOTA | 36.587 |
| IDF1 | 64.154 |
| IDSW | 1,535 |
| tracker detections | 241,284 |
| GT detections | 225,148 |
| track IDs | 273 |

系列別HOTAの範囲は22.922（`dancetrack0026`）〜87.094（`dancetrack0097`）で、系列依存性が大きい。

## state carry診断

- `motion_model_loaded=True`: 245,291 / 245,291行
- `fallback_mode`: 全行空欄
- `used_window_recompute=False`: 245,291 / 245,291行
- `used_true_state_carry=True`: 234,101 / 245,291行（95.44%）
- `last_update_reliable=False`: 4,273 / 245,291行（1.74%）
- `miss_count`: 0〜1
- `stateful_step`: 0〜1,600

したがって、今回の25系列runではcheckpoint未ロードやconstant-velocity fallbackへの退化はなく、SAM2側でMambaStatefulのcacheを持つ推論導線は成立したと判断する。`used_true_state_carry=False`の11,190行は、初期warmupや観測更新を伴わない行を含むdebug上の分類であり、fallback発生を意味しない。

## 解釈と比較上の注意

SAM2側の最小stateful統合は、25系列でHOTA 55.520、IDF1 64.154を得た。これは統合推論と成果物保存・TrackEval評価が成立したことを示す結果である。

ただし、Mamba repo単体のP1 25系列結果（A1 HOTA 47.233、A2 HOTA 47.910）とは、SAM2 detector、SAM2 mask propagation、track lifecycleなどが異なるため、単純な性能差やP1/P2の改善量として比較しない。SAM2上での改善を主張するには、同一SAM2条件でstateful Mambaなし／従来motion filter等の対照runが必要である。

また、epoch100は最良HOTA checkpointではない。checkpoint選択の影響を切り分ける次の候補は、同じSAM2条件を固定した`best_tracking_hota.pth`（epoch20）でのrunである。これは新規run_idで実施し、今回の成果物は保持する。

## 結論

最小版specの実装・25系列推論・TrackEval評価は完了した。現時点で確認できたのは「元のMambaStatefulをSAM2へ移植して安定に実行できる」ことと、そのepoch100条件の評価値であり、SAM2上でのstate carryの有効性やP1/P2の寄与は未確定である。

