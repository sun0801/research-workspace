---
date: 2026-07-28
project: sam2-mamba-motion-tracking
status: completed
tags: [experiment, sam2, samurai, mamba-stateful, kf-score-weight, trackeval, 25-seq]
---

# SAM2最小stateful Mamba統合: `kf_score_weight`比較

## 目的

SAM候補IoUとMamba予測bbox IoUの重み付けが、SAM2側のtracking性能へ与える影響を確認する。checkpointはepoch100に固定し、`kf_score_weight`だけを変更した。

## 条件

- input: DanceTrack val 25系列
- SAM2 model: `tiny`
- checkpoint: `mamba_stateful_dancetrack/epoch100.pth`
- P1/P2: `false`
- TrackEval: HOTA/CLEAR/Identity、`DO_PREPROC=False`、25系列を`SEQ_INFO`で明示
- その他のconfig、lifecycle、state carry、scaleは固定

| 条件 | run_id |
|---|---|
| `kf_score_weight=0.0` | `20260727T_sam2_minimal_25seq_epoch100_kfw0` |
| `kf_score_weight=0.5` | `20260727T_sam2_minimal_25seq_epoch100_kfw05` |

## TrackEval結果

| 指標 | kfw=0.0 | kfw=0.5 | 差分（0.5 - 0.0） |
|---|---:|---:|---:|
| HOTA | 53.911 | **53.915** | +0.004 |
| DetA | 48.256 | **48.353** | +0.097 |
| AssA | **60.572** | 60.454 | -0.118 |
| MOTA | 34.464 | **34.765** | +0.301 |
| IDF1 | **61.734** | 61.727 | -0.007 |
| IDSW | 1,576 | **1,559** | -17 |
| tracker detections | 241,094 | 241,094 | 0 |

HOTA差は`0.004`で、25系列aggregateでは実質的な差は確認できなかった。kfw=0.5はMOTAとIDSWがわずかに改善し、kfw=0.0はAssAとIDF1がわずかに高い。

## state carry診断

両条件とも以下を確認した。

- `motion_model_loaded=True`: 245,291 / 245,291行
- `fallback_mode`: 全行空欄
- `used_window_recompute=False`: 245,291 / 245,291行
- `used_true_state_carry`: kfw=0.0で233,071行、kfw=0.5で233,063行
- `last_update_reliable=False`: kfw=0.0で4,650行、kfw=0.5で4,651行
- `stateful_step`: 0〜1,600
- `miss_count`: 0〜1

state carryの利用状況はほぼ同一であり、今回の差は主にcandidate selectionの重み付けによるものと解釈できる。

## 成果物

- kfw=0.0 manifest: [`manifest.json`](/mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2/results/sam2_stateful_minimal/20260727T_sam2_minimal_25seq_epoch100_kfw0/manifest.json)
- kfw=0.5 manifest: [`manifest.json`](/mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2/results/sam2_stateful_minimal/20260727T_sam2_minimal_25seq_epoch100_kfw05/manifest.json)
- TrackEval output: `/mnt/HDD10TB-2/aburatani/2025_09_aburatani_Mamba_Trackers/artifacts/sam2_minimal_integration/trackeval/sam2_stateful_20260727_epoch100_kfw_compare_25seq/`

## 結論

今回の25系列評価では、`kf_score_weight=0.0`と`0.5`はHOTA上ほぼ同等だった。高HOTAを目的に選ぶなら、HOTA単独ではkfw=0.5を採用できるが、差は測定上ほぼ無視できる範囲である。IDF1/AssAを重視する場合はkfw=0.0にも利点があるため、発表用の主指標をHOTAだけに固定せず、複数指標を併記するのが妥当である。

## 2026-10-18 訂正：kfw=0.0 の実行は 0.0 になっていなかった

中間発表の準備で推論ログ（`*_candidate_debug.csv` の `weighted_scores`）から実際に使われた重みを逆算したところ、`20260727T_sam2_minimal_25seq_epoch100_kfw0` は **1系列目（dancetrack0004）だけが 0.0 で、残り24系列は 0.5** で動いていた。kfw=0.5 の実行（`..._kfw05`）とほぼ同時に始めており（出力の時刻は約3分差）、途中で設定ファイルが 0.5 に書き換わったものと考えられる。実際、24系列の出力は kfw=0.5 の実行とバイト単位で同じだった。

- したがって上の「kfw=0.0 と 0.5 は HOTA 上ほぼ同等（差 0.004）」は、**0.0 の効果を示していない**（ほぼ同じ条件を2回比べただけ）。
- 有効な比較は、kfw=0.25（7/23、HOTA 55.520、25系列とも 0.25 を確認）と kfw=0.5（7/27、HOTA 53.915、25系列とも 0.5 を確認）。系列ごとの差は −4.3〜+10.9 と大きい。
- kfw=0.0（動き予測を候補選択に使わない）の評価はやり直しが必要。

