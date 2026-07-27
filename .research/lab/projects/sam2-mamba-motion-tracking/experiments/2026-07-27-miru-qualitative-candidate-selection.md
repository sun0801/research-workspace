# MIRU定性結果候補 抽出結果

- 抽出日: 2026-07-27
- 比較: SAM2 / SAMURAI / Mamba stateful epoch100
- GT: /mnt/HDD10TB-2/aburatani/TrackEval/data/gt/dancetrack/val
- 共通sequence数: 25
- 抽出候補数: 30
- スコア: 6フレーム窓のstateful対SAM2 IoU差、coverage@0.5差、SAM2低IoUを組み合わせた予備ランキング
- 注意: これは自動抽出の候補であり、ポスター掲載可否はMOT Viewerで目視確認する。

## Viewer確認候補

|順位|sequence|GT ID|フレーム範囲|種別|SAM2 IoU|stateful IoU|coverage gain|state利用率|理由|
|---:|---|---:|---:|---|---:|---:|---:|---:|---|
|1|dancetrack0007|6|673–678|strong_stateful_improvement|0.000|0.994|1.000|1.00|stateful mean IoU 0.994 vs SAM2 0.000; coverage@0.5 1.000 vs 0.000; SAMURAI mean IoU 0.000|
|2|dancetrack0007|6|543–548|strong_stateful_improvement|0.000|0.992|1.000|1.00|stateful mean IoU 0.992 vs SAM2 0.000; coverage@0.5 1.000 vs 0.000; SAMURAI mean IoU 0.000|
|3|dancetrack0034|7|891–896|strong_stateful_improvement|0.000|0.989|1.000|0.75|stateful mean IoU 0.989 vs SAM2 0.000; coverage@0.5 1.000 vs 0.000; SAMURAI mean IoU 0.098|
|4|dancetrack0004|1|1090–1095|strong_stateful_improvement|0.000|0.985|1.000|1.00|stateful mean IoU 0.985 vs SAM2 0.000; coverage@0.5 1.000 vs 0.000; SAMURAI mean IoU 0.000|
|5|dancetrack0019|1|571–576|strong_stateful_improvement|0.000|0.983|1.000|1.00|stateful mean IoU 0.983 vs SAM2 0.000; coverage@0.5 1.000 vs 0.000; SAMURAI mean IoU 0.000|
|6|dancetrack0019|1|461–466|strong_stateful_improvement|0.000|0.982|1.000|0.93|stateful mean IoU 0.982 vs SAM2 0.000; coverage@0.5 1.000 vs 0.000; SAMURAI mean IoU 0.000|
|7|dancetrack0019|1|672–677|strong_stateful_improvement|0.000|0.982|1.000|1.00|stateful mean IoU 0.982 vs SAM2 0.000; coverage@0.5 1.000 vs 0.000; SAMURAI mean IoU 0.000|
|8|dancetrack0007|6|560–565|strong_stateful_improvement|0.000|0.982|1.000|1.00|stateful mean IoU 0.982 vs SAM2 0.000; coverage@0.5 1.000 vs 0.000; SAMURAI mean IoU 0.000|
|9|dancetrack0034|11|581–586|strong_stateful_improvement|0.000|0.982|1.000|0.93|stateful mean IoU 0.982 vs SAM2 0.000; coverage@0.5 1.000 vs 0.000; SAMURAI mean IoU 0.000|
|10|dancetrack0034|7|814–819|strong_stateful_improvement|0.000|0.982|1.000|1.00|stateful mean IoU 0.982 vs SAM2 0.000; coverage@0.5 1.000 vs 0.000; SAMURAI mean IoU 0.497|
|11|dancetrack0004|1|1075–1080|strong_stateful_improvement|0.000|0.982|1.000|1.00|stateful mean IoU 0.982 vs SAM2 0.000; coverage@0.5 1.000 vs 0.000; SAMURAI mean IoU 0.000|
|12|dancetrack0019|1|649–654|strong_stateful_improvement|0.000|0.982|1.000|1.00|stateful mean IoU 0.982 vs SAM2 0.000; coverage@0.5 1.000 vs 0.000; SAMURAI mean IoU 0.000|
|13|dancetrack0004|1|948–953|strong_stateful_improvement|0.000|0.981|1.000|1.00|stateful mean IoU 0.981 vs SAM2 0.000; coverage@0.5 1.000 vs 0.000; SAMURAI mean IoU 0.000|
|14|dancetrack0019|1|440–445|strong_stateful_improvement|0.000|0.981|1.000|1.00|stateful mean IoU 0.981 vs SAM2 0.000; coverage@0.5 1.000 vs 0.000; SAMURAI mean IoU 0.000|
|15|dancetrack0019|1|695–700|strong_stateful_improvement|0.000|0.981|1.000|1.00|stateful mean IoU 0.981 vs SAM2 0.000; coverage@0.5 1.000 vs 0.000; SAMURAI mean IoU 0.000|
|16|dancetrack0007|6|703–708|strong_stateful_improvement|0.000|0.981|1.000|1.00|stateful mean IoU 0.981 vs SAM2 0.000; coverage@0.5 1.000 vs 0.000; SAMURAI mean IoU 0.000|
|17|dancetrack0019|1|619–624|strong_stateful_improvement|0.000|0.980|1.000|1.00|stateful mean IoU 0.980 vs SAM2 0.000; coverage@0.5 1.000 vs 0.000; SAMURAI mean IoU 0.000|
|18|dancetrack0034|0|499–504|strong_stateful_improvement|0.000|0.980|1.000|0.93|stateful mean IoU 0.980 vs SAM2 0.000; coverage@0.5 1.000 vs 0.000; SAMURAI mean IoU 0.000|
|19|dancetrack0019|1|505–510|strong_stateful_improvement|0.000|0.980|1.000|1.00|stateful mean IoU 0.980 vs SAM2 0.000; coverage@0.5 1.000 vs 0.000; SAMURAI mean IoU 0.000|
|20|dancetrack0034|13|593–598|strong_stateful_improvement|0.000|0.980|1.000|0.93|stateful mean IoU 0.980 vs SAM2 0.000; coverage@0.5 1.000 vs 0.000; SAMURAI mean IoU 0.000|
|21|dancetrack0004|1|906–911|strong_stateful_improvement|0.000|0.979|1.000|1.00|stateful mean IoU 0.979 vs SAM2 0.000; coverage@0.5 1.000 vs 0.000; SAMURAI mean IoU 0.000|
|22|dancetrack0034|7|861–866|strong_stateful_improvement|0.000|0.979|1.000|0.93|stateful mean IoU 0.979 vs SAM2 0.000; coverage@0.5 1.000 vs 0.000; SAMURAI mean IoU 0.469|
|23|dancetrack0007|6|585–590|strong_stateful_improvement|0.000|0.979|1.000|1.00|stateful mean IoU 0.979 vs SAM2 0.000; coverage@0.5 1.000 vs 0.000; SAMURAI mean IoU 0.000|
|24|dancetrack0019|0|1480–1485|strong_stateful_improvement|0.004|0.983|1.000|1.00|stateful mean IoU 0.983 vs SAM2 0.004; coverage@0.5 1.000 vs 0.000; SAMURAI mean IoU 0.004|
|25|dancetrack0034|13|797–802|strong_stateful_improvement|0.000|0.979|1.000|1.00|stateful mean IoU 0.979 vs SAM2 0.000; coverage@0.5 1.000 vs 0.000; SAMURAI mean IoU 0.980|
|26|dancetrack0004|1|965–970|strong_stateful_improvement|0.000|0.978|1.000|1.00|stateful mean IoU 0.978 vs SAM2 0.000; coverage@0.5 1.000 vs 0.000; SAMURAI mean IoU 0.000|
|27|dancetrack0034|7|877–882|strong_stateful_improvement|0.000|0.977|1.000|0.87|stateful mean IoU 0.977 vs SAM2 0.000; coverage@0.5 1.000 vs 0.000; SAMURAI mean IoU 0.133|
|28|dancetrack0047|4|1190–1195|strong_stateful_improvement|0.007|0.985|1.000|1.00|stateful mean IoU 0.985 vs SAM2 0.007; coverage@0.5 1.000 vs 0.000; SAMURAI mean IoU 0.003|
|29|dancetrack0034|9|348–353|strong_stateful_improvement|0.002|0.980|1.000|1.00|stateful mean IoU 0.980 vs SAM2 0.002; coverage@0.5 1.000 vs 0.000; SAMURAI mean IoU 0.607|
|30|dancetrack0019|1|414–419|strong_stateful_improvement|0.000|0.977|1.000|1.00|stateful mean IoU 0.977 vs SAM2 0.000; coverage@0.5 1.000 vs 0.000; SAMURAI mean IoU 0.000|

## 上位sequence（stateful epoch100のsequence別評価）

|sequence|stateful HOTA(0)|stateful AssA AUC|stateful IDF1|stateful IDSW|SAM2平均IoU|stateful平均IoU|差分|
|---|---:|---:|---:|---:|---:|---:|---:|
|dancetrack0034|0.620|0.494|0.566|59.000|0.578|0.698|0.120|
|dancetrack0041|0.486|0.371|0.469|215.000|0.495|0.584|0.089|
|dancetrack0004|0.741|0.558|0.695|29.000|0.648|0.732|0.084|
|dancetrack0030|0.957|0.767|0.921|6.000|0.758|0.831|0.073|
|dancetrack0025|0.942|0.801|0.916|3.000|0.777|0.848|0.071|
|dancetrack0035|0.832|0.643|0.798|33.000|0.739|0.782|0.043|
|dancetrack0058|0.948|0.878|0.951|6.000|0.861|0.904|0.043|
|dancetrack0073|0.688|0.649|0.557|56.000|0.600|0.632|0.032|
|dancetrack0010|0.974|0.867|0.955|2.000|0.886|0.912|0.026|
|dancetrack0081|0.585|0.510|0.504|163.000|0.550|0.566|0.016|

## 参照ファイル

- 候補CSV: `/mnt/HDD10TB-2/aburatani/research-workspace/.research/lab/projects/sam2-mamba-motion-tracking/experiments/2026-07-27-miru-qualitative-candidate-selection.csv`
- sequence集計CSV: `/mnt/HDD10TB-2/aburatani/research-workspace/.research/lab/projects/sam2-mamba-motion-tracking/experiments/2026-07-27-miru-sequence-summary.csv`
- TrackEval detailed: `/mnt/HDD10TB-2/aburatani/2025_09_aburatani_Mamba_Trackers/artifacts/sam2_minimal_integration/trackeval/sam2_stateful_minimal_20260723T_sam2_minimal_25seq_epoch100_seqinfo/sam2_stateful_minimal_20260723T_sam2_minimal_25seq_epoch100/pedestrian_detailed.csv`
- Viewer: `/mnt/HDD10TB-2/aburatani/2026_03_aburatani_movies_antigravity/mot_viewer`
