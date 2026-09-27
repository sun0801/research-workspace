---
date: 2026-09-27
project: sam2-mamba-motion-tracking
source_todo: temporal Mamba統合の最小構成整理・実装・1〜3系列検証
topic: temporal-mamba-decoder-minimal
status: exploratory
tags: [brainstorm, research, temporal-mamba, sam2, decoder]
---

# temporal Mamba統合の最小構成整理・実装・1〜3系列検証

## 読み込んだ文脈

- 直近の主線は、SAM2デコーダー周辺へtemporal Mambaを追加すること。
- 9/25 MTGでは、既存SAM2内部モジュールの置換ではなく単純追加、spatial Mambaとtemporal Mambaの分離、初期段階での人物ID routing・ID switch対策の切り離しを確認した。
- 既存のSAM2/SAMURAI + MambaStatefulは、外付けmotion priorとして25系列評価まで完了している。一方、今回のデコーダー統合は別の問いであり、既存のbbox入力Mamba checkpointをそのまま特徴量Mambaへ流用するものではない。
- 9/18時点で、SAM2は初期フレームのGT promptを使い、その後SAM2が追跡する構成であること、YOLO＋Mambaとは観測条件が異なることを確認している。
- 2026-09-27時点では、SAM2MOT再現は補助線、temporal Mamba統合は主線と整理されている。

## 相談の出発点

temporal MambaをSAM2デコーダーへ最小限追加し、実装上の成立性と、1〜3系列で下流追跡への影響を確認したい。

## 問い

1. SAM2の既存デコーダーを大きく変更せず、フレーム間特徴を保持するtemporal Mambaを追加できるか。
2. 追加したtemporal contextが、SAM2の現在フレームのマスク／bbox出力の安定性や追跡指標を改善するか。
3. 改善または悪化があった場合、それをtemporal contextの効果として切り分けられる最小比較は何か。

## 仮説候補

- 現フレームのデコーダー特徴をtemporal Mambaで要約し、残差としてデコーダー入力へ戻すだけでも、短期的な見失い・出力揺れを抑えられる可能性がある。
- 初期段階ではglobalまたは少数tokenのtemporal contextで十分に実装成立性を確認できる。object ID routingやper-object stateを入れると、temporal Mambaの効果とassociationの効果が分離できなくなる。
- temporal contextを強く注入すると、過去フレームの誤情報を保持して誤マスクを引き延ばす可能性がある。そのため、残差のゲートを設け、ゼロ初期化で既存SAM2と同一出力から始めるのが安全である。
- 既存のbbox予測用MambaStateful checkpointは、入力空間・出力意味・state設計が異なるため、今回のデコーダー特徴用Mambaへ直接流用しない方がよい。

## アイデア候補

### A: global pooled token + residual adapter（第一候補）

1. 現フレームのデコーダー入力特徴 `F_t` を空間方向に平均または軽量poolingする。
2. 1〜数個のtokenをsequence単位のtemporal Mambaへ入力する。
3. Mamba出力をprojectionし、`F_t`へbroadcastして残差加算する。
4. 既存mask decoder、SAM2 memory、object ID処理は変更しない。
5. stateはsequence開始時にresetし、1 sequenceにつき1つだけ保持する。

概念式:

```text
z_t = Pool(F_t)
h_t = TemporalMamba(z_t, h_{t-1})
F'_t = F_t + alpha * Broadcast(Proj(h_t))
mask_t = ExistingSAM2Decoder(F'_t, prompt_t, memory_t)
```

`alpha`または最終projectionをゼロ初期化し、Mamba無効時に既存baselineと同一になるようにする。

### B: low-resolution grid tokens

特徴を低解像度の固定gridへ縮約し、grid tokenごとにtemporal contextを持たせる案。Aより局所性を持たせられるが、state数・flatten順序・カメラ移動への脆弱性が増えるため、Aの成立後に検討する。

### C: object/track ROI token

trackごとのROI特徴をtemporal Mambaへ入力する案。MOTへの整合性は高いが、object ID routing、track生成・終了、state contaminationが同時に入る。初期1〜3系列では採用せず、AまたはBで効果が確認できた場合の後続候補とする。

### D: SAM2 memory内部の置換・再設計

研究的には有力だが、SAM2内部memoryの挙動とMambaの寄与が絡み、最小検証にならない。初期構成からは除外する。

## 実験・実装案

### Phase 0: read-only tracing

- SAM2 repoのデコーダー入口・特徴テンソルのshape・frame loop・sequence reset位置を確認する。
- `F_t`の候補を1か所に限定する。
- 既存のSAM2/SAMURAI baselineのrunを再現し、対象1〜3系列の出力・manifest・指標を固定する。
- この段階では外部repoを編集しない。

### Phase 1: integration smoke

- Aのtemporal adapterを追加する。
- SAM2 image encoder、既存mask decoder、SAM2 memoryは変更しない。
- Mamba出力projectionをゼロ初期化し、adapter有効化直後の出力がbaselineと一致することを確認する。
- 1 sequenceを短いframe数でforwardし、state reset、state finite、stateの二重更新がないことを確認する。
- 出力featureのshape、dtype、device、VRAM、1フレームあたりの時間をmanifestへ記録する。

### Phase 2: 1〜3系列の最小検証

- 比較条件を少なくとも次の3つに固定する。
  - B0: 既存SAM2/SAMURAI baseline
  - B1: temporal adapterあり・Mamba出力をゼロに固定したparity control
  - B2: temporal adapterあり・学習済みtemporal Mamba
- 初期フレームprompt、SAM2 checkpoint、検出入力、frame範囲、TrackEval設定を全条件で固定する。
- まず1系列で完走し、その後に性質の異なる2〜3系列へ拡張する。系列選択は、長さ・人物数・遮蔽の違いを含めるが、選定理由と固定を記録する。
- 既存のbbox用Mamba checkpointではなく、特徴量入力用の新規Mamba／adapterを学習する。学習を行わない場合は、性能比較ではなくforward成立性の検証として扱う。

### Phase 3: 初期結果の切り分け

- HOTA、DetA、AssA、IDF1、IDSWを記録する。
- mask GTが利用できない場合は、maskから得たbboxのGT IoU、出力coverage、bbox面積・中心のframe間変動を補助指標にする。
- 改善があっても、1〜3系列・単一条件では一般化を主張しない。
- 悪化した場合は、temporal stateの汚染、残差ゲートの強さ、reset境界、prompt／memoryとの相互作用を分けて確認する。

## 比較・評価軸

### 成立性の必須条件

- baselineとB1の出力差が許容範囲内で、ゼロ初期化のparityが成立する。
- 1〜3系列を最後まで完走する。
- NaN、Inf、state explosion、意図しないstate二重更新がない。
- sequence境界でstateがresetされ、sequence間の情報漏洩がない。
- Mamba有効時の追加VRAM・速度低下を記録できる。

### 研究上の一次評価

- HOTAを総合指標とするが、DetAとAssAを分けて、デコーダー出力改善が検出側か対応側かを確認する。
- IDF1とIDSWは、temporal contextが追跡の安定性へ与える影響の補助指標とする。
- sequenceごとの差を保存し、aggregateだけで結論を出さない。

### 仮の成功・失敗基準

- 成功（実装）: Phase 1の必須条件をすべて満たす。
- 成功（初期研究信号）: B2がB0/B1に対して少なくとも一部系列で改善し、同時にstate・速度・出力の異常がない。どの指標を主判定にするかは、利用可能な教師信号を確認してspec化時に確定する。
- 失敗: parity不成立、state非有限、sequence reset不成立、またはB2の改善がなく悪化原因を切り分けられない。この場合はgrid tokenやobject routingへ進まず、挿入位置・state更新・学習信号を再確認する。

## 今回見えた方向性

第一候補は、デコーダー入力特徴に対するglobal pooled tokenのsequence-level temporal residual adapterである。研究上の新規性を早期に主張する構成ではなく、temporal MambaをSAM2のマスク生成経路へ接続できるかを最小コストで確認するための足場とする。

初回実装では、次を同時に変更しない。

- SAM2 image encoder
- 既存mask decoderの内部構造
- SAM2 memory選択・更新
- object ID routing、track lifecycle、association
- spatial Mamba
- 既存bbox motion Mambaのcheckpoint・入力形式

## 次アクション候補

1. SAM2 repoのデコーダー入口と特徴tensorをread-onlyでtraceし、Aの挿入点候補を1か所に確定する。
2. 1〜3系列検証に使うbaseline条件、sequence、指標、出力manifestを固定する。
3. temporal adapterの教師信号（マスク教師の有無、bbox supervision、distillation／consistencyの可否）を確認する。
4. Aを対象に、比較条件・成功基準・変更ファイルをspec化する。
5. ユーザー承認後にImplementation Gateを通し、外部SAM2 repoの最小実装へ進む。

## Spec化候補

- `2026-09-27-temporal-mamba-decoder-minimal-integration-spec.md`
- 対象: A（global pooled token + residual adapter）のPhase 0〜2
- spec化前に確定が必要な項目: 挿入する特徴tensor、教師信号、1〜3系列の選定、学習／推論の実行経路、主評価指標、B2の成功基準

## 未解決の問い

- SAM2デコーダー周辺で、temporal contextを加える最も自然な特徴tensorはどれか。
- DanceTrackで利用可能な教師信号はbboxのみか、マスク教師も利用できるか。
- B2を学習する最小データ・loss・checkpoint選択をどうするか。
- global tokenで局所的な遮蔽・人物移動を扱えるか。効果がなければgrid tokenへ進む判断基準は何か。
- 1〜3系列で観測した改善を、既存の外付けMamba結果やSAM2MOT補助線とどう位置づけるか。

## 関連ファイル

- `.research/secretary/notes/brainstorm/2026-09-27-priority-after-0925-mtg.md`
- `.research/lab/projects/sam2-mamba-motion-tracking/README.md`
- `.research/lab/projects/sam2-mamba-motion-tracking/meetings/2026-09-25-mtg.md`
- `.research/lab/projects/sam2-mamba-motion-tracking/meetings/2026-09-18-mtg.md`
- `.research/lab/projects/sam2-mamba-motion-tracking/specs/2026-07-23-sam2-stateful-mamba-minimal-integration-spec.md`
- `.research/lab/projects/sam2-mamba-motion-tracking/experiments/2026-09-25-mamba-loss-hota-sequence-comparison.md`

---

## 追記 23:01 — 最小構成の妥当性レビュー

### 判定

ゼロ初期化残差と少数系列でのparity確認は、実装成立性の検証として妥当。ただし案Aの「デコーダー入力特徴」と「sequenceにつきstateを1つ」は、複数人物の現行SAM2推論経路では同時に成立しない。B0/B1/B2のみでは、時間履歴の寄与を特定できない。

### コード上の根拠と修正点

1. 現行SAM2 forkの`sam2/modeling/sam2_base.py`では、`_track_step`が人物ごとのmemoryを融合した`pix_feat`をデコーダーへ渡す。`sam2/sam2_video_predictor.py`の`propagate_in_video`は同じフレーム内で人物ごとに`_run_single_frame_inference(batch_size=1)`を呼ぶ。この位置で共有stateを更新すると、人物間の履歴混合と1フレーム内の複数回更新が起こる。
2. 最初のsmokeは単一人物の`pix_feat`直後で行う。複数人物で同じ位置を使うなら、既存SAM2の`obj_id`に紐づけたstateが必要。新規associationは不要。ID対応付けも避けるなら、共通image featureで1フレーム1回更新する設計とし、人物別motionの効果とは解釈しない。
3. `propagate_in_video`はconditioning frameの再推論をスキップする場合がある。初期prompt、途中修正、逆方向伝播、再開、人物追加・削除のstate更新規則を明示する。現行の`main_inference_mot.py`は`torch.inference_mode()`で動くため、B2学習には微分可能な別経路が必要。
4. B1はparity controlであり、B2との差は学習済みadapter全体の効果。B2と同一重みで毎フレームstateをresetするB3を加えると、追加した時間履歴の寄与をより直接に確認できる。SAM2は既にmemoryを持つため、評価対象は既存memoryに対する追加効果。
5. DanceTrack公式GTはMOT形式のbboxとIDで、mask GTを前提にできない。学習信号とtrain/val分離を先に決める。baseline maskへのdistillationや単純な時間的一貫性lossだけではGT改善を保証しない。学習なしならforward成立性に結論を限定する。

### spec化前の優先事項

- 単一人物のsmokeに限定するか、複数人物の`obj_id`別stateを初回範囲に含めるか決める。
- 学習データ・教師信号・微分可能なforward経路・checkpoint選択を固定する。
- B3（B2と同一重み、毎フレームstate reset）を加え、parityは系列全体の出力でも確認する。
- global poolingのbroadcastは空間位置を直接運べない。改善なしをtemporal Mamba一般の不成立と判断しない。

---

## 追記 23:16 — 合意した初回検証範囲とspec化

ユーザーとの確認で、**まずSAM2の人物別memory処理後、mask decoder直前の`pix_feat`にtemporal Mambaを追加し、単一人物で接続を試す**方針に絞った。初回は性能改善の判定ではなく、ゼロ出力時のbaselineとの一致、1フレーム1回のstate更新、reset、短区間と1系列の完走を確認する。

この範囲を[デコーダー直前へのtemporal Mamba最小統合Spec](../../../lab/projects/sam2-mamba-motion-tracking/specs/2026-09-27-temporal-mamba-decoder-minimal-integration-spec.md)として保存した。最初はSAM2.1 Small・DanceTrack valの1人物を使い、B0（現行SAM2）、B1（adapterあり・残差ゼロ）、P（未学習adapterの接続診断）を比較する。上の「Phase 0〜2を一つのspecにする」案は、この合意を受けて**成立性確認と後続の学習・性能比較に分けた**。

複数人物での`obj_id`別state、学習信号、B2（学習済みstate carry）とB3（同一重みで毎フレームreset）は次段階で設計する。[共有image embeddingへの挿入案](2026-09-27-temporal-mamba-id-dependency-discussion.md)は、人物別memoryより前に置く別の挿入位置として残し、今回のspecには含めない。今回のspec作成は承認されたが、外部SAM2 repoの実装開始は別途Implementation Gateで確認する。
