---
date: 2026-09-08
project: sam2-mamba-motion-tracking
status: completed
tags: [experiment, sam2mot, reproduction, a1, vram, instance-mode]
---

# SAM2MOT再現 A1: インスタンス構成のVRAM・速度実測

## 目的

SPEC の A1（SAM2 を per-instance で使うか batched で使うか）と Risk 1（per-instance がVRAMに収まらない懸念）の判断材料を得る。論文は "multiple parallel single-object trackers" と記すのみで構成が明記されていない。

## 実験条件

- 系列: DanceTrack val `dancetrack0026`（frame 1 で13体）、101フレーム
- SAM2.1-large、`offload_video_to_cpu=True`
- GPU: RTX PRO 4500 Blackwell（31.4 GiB）
- per-instance は `images` テンソルを全 state で共有（共有しないと動画キャッシュが state 数だけ重複しCPU RAMが破綻する）
- プロンプトは frame 1 の GT box。**構成の計測が目的で追跡性能の評価ではない**

## 結果

| 構成 | state数 | peak VRAM | fps | forward回数 |
|---|---|---|---|---|
| batched | 1 | 4.03 GiB | 6.23 | 101 |
| per-instance | 13 | **3.26 GiB** | **1.18** | 1313 |

## 解釈

**予想と逆に、per-instance の方がVRAMが少なかった。** batched は13体を1回の forward にまとめるため活性化テンソルが大きく、per-instance は1体ずつ処理するため瞬間の使用量が小さい。peak は最大の単一 forward に支配される。

val で frame 1 の体数が最大の `dancetrack0081`（19体）へ線形外挿しても約4.8 GiBで、GPU容量に十分収まる。**SPEC の Risk 1 にあった「VRAMに収まらないため batched へ妥協する」分岐は不要と判断する。**

代わりに顕在化したのは速度で、per-instance は batched の 1/5.3（forward回数が13倍）。これは論文が Limitation に推論速度を挙げ、将来の高速化方針に "parallel inference across multiple SAM2 instances" を置いていることと整合する。この整合は、論文が実際に per-instance 構成を採っているという SPEC A1 の推定を間接的に支持する。

**改善余地**: `cached_features`（画像エンコーダ出力）を state 間で共有すれば、最も重い backbone を1回に減らせる。本計測は共有なしの値であり、S1 実装時にこの共有を入れるかを判断する。

## 注意

- 1系列・101フレームのみ
- frame 1 のオブジェクトのみ。途中出現による同時追跡数の増加を含まない
- 外挿は frame 1 の体数基準。実際の同時追跡数はこれを超える
- peak は `torch.cuda.max_memory_allocated()` の値で断片化を含まない

## 成果物

- `/mnt/HDD10TB-2/aburatani/2026_05_aburatani_sam2mot/sam2mot_repro/logs/s1_vram_instance_mode.md`
- 同 `scripts/s1_vram_instance_mode.py`
