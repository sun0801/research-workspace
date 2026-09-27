---
date: 2026-09-27
project: sam2-mamba-motion-tracking
source: brainstorm
status: draft
tags: [spec, sam2, temporal-mamba, decoder, single-object, smoke]
---

# SAM2デコーダー直前へのtemporal Mamba最小統合 Spec

## 目的と範囲

SAM2の人物別memory処理後、既存mask decoderへ渡す直前の特徴へtemporal Mambaを残差として加え、**まず単一人物で**組み込みとstate carryの成立性を確認する。今回の成功は、ゼロ出力時の既存SAM2との一致、stateの正しい更新・reset、短区間と1系列の完走で判定する。

このspecは実装と推論smokeの設計であり、学習済みtemporal Mambaの有効性やMOT性能改善を判定する実験設計ではない。複数人物への拡張、学習方法、B2/B3比較は、今回の結果を見て別途spec化する。

## 背景と検証したい問い

2026-09-25 MTGでは、SAM2内部モジュールを置換せず、spatial Mambaと分けてtemporal Mambaを追加する方針が確認された。SAM2の動画推論は既にmemory attentionで過去情報を利用するため、ここで問うのは「SAM2に時間情報があるか」ではなく、**その後段に独立した状態保持経路を接続できるか**である。

現行fork `/mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2` の `sam2/modeling/sam2_base.py` では、`_track_step`が `_prepare_memory_conditioned_features` から得た `pix_feat` を `_forward_sam_heads(backbone_features=pix_feat, ...)` へ渡す。`sam2/sam2_video_predictor.py` の `propagate_in_video` は各フレームで人物ごとに推論する。よって今回は単一人物に限定し、人物間state共有の問題を持ち込まない。

**仮説:** `pix_feat`直後へゼロ初期化残差のtemporal adapterを追加すれば、SAM2 checkpoint・既存decoder・既存memory処理を維持したまま、フレーム間でMamba stateを保持する推論経路を作れる。

## 使用データ・モデル

| 項目 | 固定条件 |
|---|---|
| 実装対象 | `/mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2`、`sam2` mode |
| SAM2 | SAM2.1 Hiera Small、`sam2/configs/sam2.1/sam2.1_hiera_s.yaml`、`checkpoints/sam2.1_hiera_small.pt` |
| データ | `/mnt/HDD10TB-2/aburatani/dataset/DanceTrack/standard_format/val/dancetrack0004` |
| 対象 | 既存`main_inference_mot.py`と同じ規則で「最も早く現れるID、同着ならID昇順」の1人物を選び、選択IDと初出フレームをmanifestへ保存 |
| prompt | 選択人物の初出フレームのGT bboxを1回だけbox promptに使う。その後のGTは入力しない |
| Mamba | 特徴量用に新規初期化する1層。`d_model=self.hidden_dim`、`d_state=16`、`d_conv=4`、`expand=2`。既存bbox用checkpointは流用しない |
| 推論 | 同じframe範囲、checkpoint、autocast dtype、seed、postprocessingで比較 |

最初は初出フレームから16フレームの短区間、その後同じ1系列の末尾まで実行する。完走後、必要な場合だけ`dancetrack0005`と`dancetrack0007`へ同じ単一人物条件を拡張する。系列選定と実際のframe範囲は実行前にmanifestへ固定する。

## 挿入位置と構成

`_track_step`の`pix_feat = self._prepare_memory_conditioned_features(...)`の直後、`_forward_sam_heads(...)`の直前に、無効化可能なadapterを1か所だけ置く。

```text
z_t = mean_spatial(pix_feat_t)              # [1, C]
h_t = TemporalMamba.step(z_t, state_{t-1})  # [1, C]
delta_t = Proj(h_t)[:, :, None, None]        # [1, C, 1, 1]
pix_feat'_t = pix_feat_t + alpha * delta_t   # [1, C, H, W]
mask_t = ExistingSAM2Heads(pix_feat'_t, prompt_t)
```

`alpha=0`を既定値とする。global poolingと空間broadcastは位置情報を直接運ばないため、今回は接続確認の最小構成と位置づける。既存SAM2のimage encoder、memory attention、memory encoder、mask decoder、high-resolution skip features、object ID処理、bbox motion priorは変更しない。Mambaの状態にはSSM stateと短い畳み込みのcacheを含める。

### state更新規則

- 1推論セッションにつき1人物・1 Mamba state。2人物目の入力を検知した場合は共有せず、明示的に停止する。
- 初期promptフレームのデコーダー呼び出しを含め、処理された`(frame_idx, obj_id)`ごとに1 token・1回だけ更新する。`propagate_in_video`が保存済みconditioning outputを再利用した場合は更新しない。
- `init_state`と`reset_state`でcacheと更新履歴を消す。同じpredictorで別セッションを開始しても履歴を持ち越さない。
- 同一フレームの再処理、途中prompt修正、逆方向伝播は今回のsmokeでは行わない。発生した場合は黙ってstateを進めず、診断エラーとして記録する。
- `alpha=0`でもMambaを実行してstateを更新し、finite・更新回数を検証する。Mambaのimport・forward失敗をbaselineへのfallbackで隠さない。

## 比較条件

| 条件 | 用途 |
|---|---|
| B0 | 現行SAM2.1 Small、adapterなし |
| B1 | 同じSAM2 checkpointに新規adapterを追加、`alpha=0`。B0との出力一致を確認 |
| P | 接続診断。B1と同じ未学習adapterで短区間だけ`alpha`を非ゼロにし、`delta_t`と`pix_feat'_t`への経路がfiniteか確認。追跡性能として解釈しない |

学習済みadapterのB2、および同一重みで毎フレームstateをresetするB3は次段階の比較条件とする。DanceTrackの公式GTはbboxとIDであり、mask教師・学習loss・train/val分離を定めるまでは性能実験を始めない。

## 実装変更範囲

実装開始承認後、変更候補を以下に限定する。配置の細部が変わる場合は、同じ責務の範囲で変更点をmanifestへ記す。

| ファイル | 変更内容 |
|---|---|
| `sam2/modeling/temporal_mamba_adapter.py`（新規） | pooling、Mamba 1層、projection、gate、streaming cache、finite/更新診断 |
| `sam2/modeling/sam2_base.py` | `pix_feat`とSAM headsの間に、adapter有効時だけ通るhook |
| `sam2/sam2_video_predictor.py` | `init_state`・`reset_state`とadapter stateの同期、単一人物ガード |
| `scripts/smoke_temporal_mamba_decoder.py`（新規） | B0/B1/P実行、選択ID・frame範囲固定、比較とmanifest保存 |

元のSAM2 checkpointは既存のbuilderでロードしてからadapterを追加し、追加パラメータのために既存checkpointのstrict load条件を緩めない。現行の`main_inference_mot.py`、既存config、checkpoint、既存run出力は変更・上書きしない。結果は新しいrun IDの別ディレクトリに保存する。

## 検証手順と評価指標

1. **read-only確認:** 対象repoのcommit・dirty状態、挿入箇所、実際の`pix_feat` shape/dtype/device、対象IDの初出フレーム、使用checkpointとデータを記録する。
2. **単体smoke:** 1 tokenずつ入力したとき、Mamba cache offsetが1ずつ進むこと、stateが有限であること、reset後に同じ入力列で同じ出力になることを確認する。adapter出力のshape/dtype/deviceが`pix_feat`と一致することも確認する。
3. **16フレーム:** B0/B1を同一prompt・同一frame範囲で実行する。低解像度mask logits、出力mask、bbox、更新イベントをframe単位で保存・比較する。Pでは`delta_t`がゼロに固定されておらず、有限の変化が`pix_feat`へ届くことを確認する。
4. **1系列完走:** B0/B1を同じ設定で末尾まで実行し、出力frame数、state更新回数、系列全体のparity、peak VRAM、初回warm-upを除いた1フレームあたりの時間を記録する。
5. **必要時の拡張:** 0005/0007でも同じ単一人物条件を適用する。結果は系列別に保存し、合算して性能改善を主張しない。

主要指標は、B0/B1のframe別mask logits最大絶対差、二値maskの一致率、bbox一致、state finite率、期待更新回数と実更新回数、reset再現性、完走frame数、追加VRAMと推論時間である。HOTA・DetA・AssA・IDF1・IDSWは今回の合否指標に使わない。

## 成功・失敗の判断基準

**成功:** 16フレームと1系列が終了し、B1のstate・adapter出力にNaN/Infがなく、cache更新が処理済み`(frame_idx, obj_id)`と1対1に対応する。reset後の再実行が再現し、B0/B1の各フレームのmask logits最大絶対差が`1e-3`以下、二値maskとbboxが一致する。Pのadapter出力は有限で、非ゼロの残差が`pix_feat`へ届く。VRAM・速度差と実行条件を記録できる。

**停止して原因を調べる条件:** parity不成立、状態非有限、二重更新、別セッションへのstate漏洩、対象人物が2人以上になったまま処理が進む、Mambaが実行されずfallbackで結果が出る、または短区間を完走できない。閾値未達を許容するための事後的な条件変更はしない。

成功しても「temporal Mambaが追跡性能を改善した」とは結論しない。global tokenに効果が見えない場合も、学習信号と挿入位置を確認する前にtemporal Mamba一般を否定しない。

## 成果物・provenance

外部SAM2 repoの新規runディレクトリへ、実行コマンド、git commitとdirty状態、checkpoint SHA256、SAM2/Mamba/PyTorch/CUDAバージョン、選択sequence・ID・prompt frame・frame範囲、seed、dtype、adapter設定、B0/B1/Pのframe別診断、state更新ログ、parity判定、時間・VRAMを保存する。研究上の解釈は、このspecとは別に`experiments/YYYY-MM-DD-<topic>.md`へ記録する。

## 次段階への条件

このspecの成功後、複数人物の`obj_id`別state、学習可能なforward経路、教師信号・loss、train/val分離、B2（学習済みstate carry）とB3（同一重みで毎フレームreset）の比較を計画する。人物別stateが必要な構成であるため、共有image embeddingへMambaを置く別案とは混同せず、必要なら独立した挿入位置比較として扱う。

## 実装開始ゲート

ユーザーは本specの**作成**を依頼した。外部SAM2 repoの編集・実験開始には、本specの内容、上記変更範囲、検証方法を確認した上で、ユーザーの実装開始承認を別途得る。

## 関連文脈

- [元のbrainstorm](../../../../secretary/notes/brainstorm/2026-09-27-temporal-mamba-decoder-minimal.md)
- [共有特徴への挿入を検討した別案](../../../../secretary/notes/brainstorm/2026-09-27-temporal-mamba-id-dependency-discussion.md)
- [2026-09-25 MTG](../meetings/2026-09-25-mtg.md)
- [既存bbox MambaのSAM2統合spec](2026-07-23-sam2-stateful-mamba-minimal-integration-spec.md)
