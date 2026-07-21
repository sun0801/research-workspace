---
date: 2026-07-21
project: sam2-mamba-motion-tracking
status: completed
tags: [experiment, p0-5, baseline, mambatrack, trackssm, state-carry]
---

# P0.5 sliding-window baseline比較

## 目的

MambaTrack、TrackSSM、現行MambaStatefulを、同一DanceTrack validation split・同一detector入力・同一TrackEval条件でas-is比較し、Stateful固有の学習設定差と、各手法に共通するprediction-primary associationを切り分ける。

## 実行条件

既存のDanceTrack val推論出力25系列を使用し、GT配置をTrackEvalの一時入力構造へリンクして評価した。評価metricsはHOTA、CLEAR、Identity、前処理なし、単一プロセスで固定した。

| 手法 | checkpoint候補 | window / 入力 | 学習設定 | 推論association |
| --- | --- | --- | --- | --- |
| MambaTrack | `mambatrack_dancetrack2/epoch25.pth` | 12 / diff | SGD、transformer scheduler、25 epoch | prediction-primary |
| TrackSSM | `trackssm_dancetrack_sep_scale_one_dec_layer/epoch100.pth` | 7 / bbox + diff | SGD、transformer scheduler、100 epoch | prediction-primary |
| MambaStateful | `mamba_stateful_dancetrack/epoch100.pth` | 12 / stateful bbox | Adam、scheduler none、100 epoch | prediction-primary、missing_mode=self_update |

既存推論出力の生成時checkpoint provenanceは完全には残っていないため、上表のcheckpointは設定確認用の候補として扱う。上表を明示した再推論も開始したが、全25系列の完走には長時間を要するため、GPU占有を避けて途中停止した。今回の比較値は既存25系列出力に対するTrackEval結果である。

## TrackEval結果（既存25系列出力）

| 手法 | HOTA | DetA | AssA | IDF1 | MOTA | ID switches | IDs |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| MambaTrack | 33.837 | 73.563 | 15.657 | 27.522 | 79.405 | 5,453 | 3,748 |
| TrackSSM | 32.783 | 72.329 | 14.973 | 25.178 | 76.187 | 8,966 | 4,966 |
| MambaStateful | 47.293 | 74.933 | 30.003 | 45.949 | 84.481 | 2,601 | 876 |

全25系列のGT detection数は225,148。今回のas-is出力ではMambaStatefulがHOTA、AssA、IDF1、MOTAで最良だった。これはStateful学習の優位性を意味せず、checkpoint、入力形式、モデル構造、推論associationが未分離であるため、P0.5の目的は因果結論ではなく比較基準の固定である。

## 小規模seqmapとの照合

既存seqmapが指定する3系列（dancetrack0004/0005/0007）でも同じ評価経路を確認した。

| 手法 | HOTA | AssA | IDF1 | MOTA | ID switches |
| --- | ---: | ---: | ---: | ---: | ---: |
| MambaTrack | 35.481 | 15.530 | 28.104 | 87.391 | 264 |
| TrackSSM | 36.399 | 16.342 | 28.309 | 87.758 | 254 |
| MambaStateful | 52.037 | 32.695 | 49.741 | 90.940 | 102 |

## 解釈と次の判断

- MambaTrack / TrackSSMがStatefulを上回るという当初の仮説は、今回のas-is結果では支持されなかった。
- ただし3手法ともpredictionをmatching位置へ使うため、association導線の影響は残っている。
- 次にP1を進める場合は、Statefulだけを変更し、checkpoint・detector・split・track lifecycle・TrackEvalを固定した診断比較にする。
- P1の結果を記録するまでは、P2以降のcache更新やP4a TBPTTへ進まない。

## 再現用出力

TrackEval一時出力: `/tmp/p0_5_state_carry_20260721/output_full/`

推論再実行の一時出力（途中停止）: `/tmp/p0_5_state_carry_20260721/inference/`

