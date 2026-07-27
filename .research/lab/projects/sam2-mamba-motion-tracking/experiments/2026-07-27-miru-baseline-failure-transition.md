# MIRU定性結果候補：直前まで成功していた対象の失敗遷移

## 結論

条件に合う候補が1件見つかりました。

`dancetrack0034 / GT ID 9`

- 直前: frames `327–334`
- 失敗開始後: frames `335–340`

|区間|SAM2|SAMURAI|Mamba stateful|
|---|---:|---:|---:|
|直前 327–334|0.758|0.746|0.811|
|失敗開始後 335–340|0.259|0.225|0.941|

## 目視確認で期待できる挙動

- SAM2/SAMURAIは334フレームまでは対象を追跡できる。
- 335フレーム以降、両ベースラインのboxが対象に対して小さくなり、位置がずれる。
- SAM2はtrack IDが9から7へ切り替わり、342フレームでは対象boxが消える。
- SAMURAIもIDが複数切り替わり、対象へのIoUが低下する。
- Mamba statefulはtrack ID 9を維持し、対象boxを追跡する。
- statefulのdebugでは frames 327–340でtrue state carry使用率100%、fallbackなし、最大miss count 0。

このため、ポスターでは次の流れを示せる可能性があります。

> 直前まで追跡できていた対象が、SAM2/SAMURAIでは外観・動きの変化を境に見失われる一方、Mamba state carryを導入したSAM2では追跡が継続する。

## 確認範囲

Viewerでは、`310, 315, 320, 325, 330, 335, 340, 342` の8フレームを5フレーム刻みで表示するのがよいです。310付近のずれ始め、335付近の崩れ、340–342のベースライン破綻を同じ図で追えます。

330ではベースラインのIoUが一時的に戻るため、単調な悪化ではなく「不安定化した後に破綻する」挙動として説明するのが正確です。候補CSVのevent区間は定量比較用に `335–340` としています。

GT IDは対象を特定するための参照番号であり、各手法のtrack IDと一致するとは限りません。

## 注意

IoUはGT boxに対する各フレームの最大予測IoUです。ID維持やassociationの説明はMOT出力とcandidate debugから補助的に確認したもので、最終的なポスター掲載可否はViewerで目視確認します。

## 参照

- 候補CSV: `2026-07-27-miru-baseline-failure-transition.csv`
- SAM2: `/mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2/results/sam2/sam2_tiny/dancetrack0034.txt`
- SAMURAI: `/mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2/results/samurai/samurai_tiny/dancetrack0034.txt`
- Mamba stateful: `/mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2/results/sam2_stateful_minimal/20260723T_sam2_minimal_25seq/samurai_mamba_stateful_tiny/dancetrack0034.txt`
- candidate debug: `/mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2/results/sam2_stateful_minimal/20260723T_sam2_minimal_25seq/samurai_mamba_stateful_tiny/dancetrack0034_candidate_debug.csv`
