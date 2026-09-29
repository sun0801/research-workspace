---
project: sam2-mamba-motion-tracking
date: 2026-09-28
type: experiment-log
status: completed
---

# Temporal Mamba decoder最小統合：1系列スモーク検証

## 目的

承認済みspec [`2026-09-27-temporal-mamba-decoder-minimal-integration-spec.md`](../specs/2026-09-27-temporal-mamba-decoder-minimal-integration-spec.md) に従い、SAM2内部のマスクデコーダー構造を変更せず、`_prepare_memory_conditioned_features` の出力 `pix_feat` と `_forward_sam_heads` の間に1層のstateful Mambaアダプタを挿入できることを確認する。

今回の実験は、未学習Mambaによる性能改善の主張ではなく、接続位置・時系列state・reset・既存経路との同値性を確認する最小検証である。

## 実装

- 実装リポジトリ: `/mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2`
- 追加: [`sam2/modeling/temporal_mamba_adapter.py`](/mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2/sam2/modeling/temporal_mamba_adapter.py)
- 接続: [`sam2/modeling/sam2_base.py`](/mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2/sam2/modeling/sam2_base.py)
- 検証スクリプト: [`scripts/smoke_temporal_mamba_decoder.py`](/mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2/scripts/smoke_temporal_mamba_decoder.py)

アダプタは、空間平均した `pix_feat` を1トークンとしてMambaへ入力し、射影した残差を空間方向へbroadcastして `pix_feat` に加算する。Mambaは `d_state=16, d_conv=4, expand=2`、stateは `(frame_idx, obj_id)` ごとに1回更新する。現実装ではsingle-objectに限定し、`init_state`/`reset_state` に同期してstateをリセットする。

## 条件

| 条件 | 内容 |
|---|---|
| B0 | 既存SAM2、アダプタなし |
| B1 | アダプタあり、`alpha=0`。state更新のみ行い、SAM2出力は変えない対照 |
| P | アダプタあり、`alpha=1`。Mamba重みは未学習の接続確認用 |

- config: `configs/sam2.1/sam2.1_hiera_s.yaml`
- checkpoint: `checkpoints/sam2.1_hiera_small.pt`
- sequence: DanceTrack val `dancetrack0004`
- 全系列長: 1203フレーム
- prompt: GT bboxを1回だけ使用。最初に出現する `obj_id=1`、0-based frame 0、`xyxy=[956, 434, 1258, 992]`
- 推論: 16フレーム短縮検証 + 全1203フレーム検証
- device: `cuda:0`, torch `2.10.0+cu128`

## 結果

全系列の正本出力は [`runs/temporal_mamba_decoder_full_v1`](/mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2/runs/temporal_mamba_decoder_full_v1) に保存した。

| 条件 | full frames | adapter updates | last frame | reset再現 | peak CUDA MB | script elapsed sec |
|---|---:|---:|---:|---|---:|---:|
| B0 | 1203 | — | — | — | 764.59 | 243.58 |
| B1 | 1203 | 1203 | 1202 | true | 775.20 | 319.40 |
| P | 1203 | 1203 | 1202 | — | 767.23 | 245.49 |

### spec上の検証項目

- B0/B1の16フレーム比較: `max_abs_diff=0.0`、二値マスク完全一致。`B0_vs_B1.parity=true`。
- B1のstate更新: 1203回。各フレームを1回ずつ処理し、`last_frame_idx=1202`。
- B1のreset再現性: `true`。
- Pのstate更新: 1203回。`delta_norm` は `0.6322--0.7018`、残差ノルムは `40.4601--44.9172` で、全フレーム非ゼロ。
- 保存されたB0/B1/Pの短縮マスクと全サマリーの有限値チェック: 成功。NaN/Infなし。

## 解釈

最小構成として、Mambaをマスクデコーダー直前の画像特徴量経路へ接続し、フレーム間stateを維持しながらSAM2の伝播APIを通せることを確認できた。`alpha=0` のB1がB0と完全一致したため、現時点では既存SAM2への非意図的な出力差は確認されていない。

一方、PはMambaが未学習であり、今回の非ゼロ残差は「接続されて実行された」ことの証拠に留まる。マスク精度、HOTA、IDF1などの改善・悪化はこの実験から結論できない。次段階では、学習可能な損失設計と、同一prompt・同一SAM2条件でのB0/P比較を複数系列へ拡張する必要がある。また現実装はsingle-objectなので、複数人物を扱う場合のtrackごとのstate分離と、共有画像特徴へ入れる構成との比較は別実験とする。

## 再現情報

- run manifest: [`manifest.json`](/mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2/runs/temporal_mamba_decoder_full_v1/manifest.json)
- summary: [`summary.json`](/mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2/runs/temporal_mamba_decoder_full_v1/summary.json)
- checkpoint SHA256: `6d1aa6f30de5c92224f8172114de081d104bbd23dd9dc5c58996f0cad5dc4d38`
- 実行時の外部repoには、今回の3ファイルに加えて既存の `sam2/configs/samurai_mamba_stateful/sam2.1_hiera_t.yaml` のユーザー変更が残っていた。既存変更は触れていない。
