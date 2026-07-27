# MIRU定性結果 Viewer確認候補

## まず確認する4件

以下は、ポスターの主ストーリー「SAM2/SAMURAIでの見失いを、Mambaを組み込んだSAM2のstate carryが回復する」に最も直接的な候補です。

|順位|sequence|GT ID|確認フレーム|SAM2 IoU|SAMURAI IoU|Mamba stateful IoU|statefulでのcoverage@0.5|確認意図|
|---:|---|---:|---:|---:|---:|---:|---:|---|
|1|dancetrack0007|6|673–678|0.000|0.000|0.994|1.000|両ベースラインが見失い、statefulのみ回復|
|2|dancetrack0034|7|891–896|0.000|0.098|0.989|1.000|両ベースラインの局所失敗から回復|
|3|dancetrack0004|1|1090–1095|0.000|0.000|0.985|1.000|両ベースラインが見失い、statefulのみ回復|
|4|dancetrack0047|4|1190–1195|0.007|0.003|0.985|1.000|別sequenceで同じ回復パターンを確認|

## 比較・対照として追加確認する2件

|順位|sequence|GT ID|確認フレーム|SAM2 IoU|SAMURAI IoU|Mamba stateful IoU|確認意図|
|---:|---|---:|---:|---:|---:|---:|---|
|5|dancetrack0034|9|348–353|0.002|0.607|0.980|SAMURAIが部分的に成功する場合でもstatefulが安定するか|
|6|dancetrack0034|13|797–802|0.000|0.980|0.979|SAMURAIも成功する対照例。Mambaの上乗せが常にあるわけではないことを確認|

## Viewerでの確認方法

各候補について、同じsequence・同じフレーム範囲をSAM2、SAMURAI、Mamba statefulで並べて確認する。GT IDは評価時に対象を特定するための参照番号であり、Viewer上の各手法のtrack IDと一致するとは限らない。

確認時は、対象が「完全に消えた」のか、「別対象へIDが切り替わった」のか、「boxはあるが位置がずれた」のかを記録する。ポスター掲載候補は、statefulのboxが対象を追跡していることを目視でき、ベースラインとの差が一目で分かるものを採用する。

## 重要な制約

今回、同一sequenceを十分な本数で比較できるsliding-window版の出力は確認できなかった（現在確認できるのはdancetrack0004/0005の2sequence）。したがって、この候補表はstateful版の主張に限定し、sliding window対state carryの優劣はポスターの必須主張には含めない。

## 参照

- 自動抽出30件: `2026-07-27-miru-qualitative-candidate-selection.csv`
- sequence集計: `2026-07-27-miru-sequence-summary.csv`
- stateful版manifest: `/mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2/results/sam2_stateful_minimal/20260723T_sam2_minimal_25seq/manifest.json`
- Viewer: `/mnt/HDD10TB-2/aburatani/2026_03_aburatani_movies_antigravity/mot_viewer`
