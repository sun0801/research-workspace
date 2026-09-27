---
date: 2026-09-27
project: sam2-mamba-motion-tracking
source_todo: temporal Mamba統合の最小構成整理・実装・1〜3系列検証
topic: temporal-mamba-id-dependency-discussion
status: exploratory
tags: [brainstorm, research, temporal-mamba, sam2, decoder, identity]
---

# temporal Mamba統合に関する議論整理

## 1. 出発点

既存のMambaStatefulは、SAM2/SAMURAIの外側でbboxの動き予測を行う。この構成は、SAM2が出力した物体位置とID対応が正しいことを前提にする。

SAM2が人物Aを人物Bとして扱うと、Mambaにも誤ったbbox系列が入力され、trackごとのstateが汚染される。そのため、動き予測Mambaを改善するだけでは、SAM2側の誤ったmask・ID対応を根本的には解決できない。

## 2. 初期仮説

SAM2のmask decoderはフレーム間stateを持つrecurrent moduleではない。image embeddingとprompt embeddingを受け、Two-way Transformerとmask headによって現在フレームのmaskを生成する。

そこで、SAM2の内部構造を置き換えず、decoderへ渡るimage embedding側へtemporal Mambaを追加すれば、マスク生成そのものに時間情報を持たせられるのではないかと考えた。

## 3. SAM2の時系列処理との関係

SAM2全体が時系列情報を持っていないわけではない。動画推論では、現在フレーム特徴と過去mask memoryを`memory_attention`で融合し、その出力`pix_feat`をmask decoderへ渡している。

```text
image encoder
  -> current feature
  -> SAM2 memory attention（過去フレーム情報を融合）
  -> pix_feat
  -> MaskDecoder / TwoWayTransformer
```

したがって、mask decoder自身はフレーム間stateを持たないが、decoder入力はすでにSAM2の時系列memoryで条件付けされている。

主な対応箇所:

- `sam2/modeling/sam2_base.py:785-1000`: 現在特徴と過去memoryの融合
- `sam2/modeling/sam2_base.py:1087-1107`: `pix_feat`をmask decoderへ接続
- `sam2/modeling/sam/mask_decoder.py:168-245`: image embeddingとpromptからmaskを生成
- `sam2/modeling/sam/transformer.py:19-187`: Two-way Transformer

## 4. decoder直前のMambaに残る問題

`memory_attention`後の`pix_feat`は、SAM2の人物ごとのmemoryで条件付けされた特徴である。また動画推論では、`obj_idx`ごとに`batch_size=1`で処理される。

```text
人物ごとのSAM2 memory
  -> 人物ごとのpix_feat
  -> 人物ごとのMamba state
  -> 人物ごとのMaskDecoder
```

この位置にMambaを追加しても、既存の動き予測Mambaほど直接的ではないが、SAM2のID対応・人物別memoryに依存する。SAM2が誤った人物を参照している場合、Mambaが誤った特徴を時間方向に保持する可能性がある。

したがって、`memory_attention`後の人物別`pix_feat`へのMambaは、マスクの時間安定化には意味があるが、ID誤対応問題を主目的とする構成としては不十分である。

## 5. 修正後の推奨構成

ID誤対応の影響を受けにくいtemporal Mambaを検証するなら、人物別memoryへ入る前の共有image embeddingにMambaを追加する。

```text
image encoder
  -> shared image embedding F_t
  -> sequence-level temporal Mamba
  -> temporally enriched F'_t
  -> object-specific SAM2 memory attention
  -> existing per-object MaskDecoder
```

この構成では、Mamba stateはsequence単位で共有でき、人物IDごとのbboxやSAM2 object memoryをMamba stateへ直接入力しない。既存のID routingを変更せずに、decoderへ渡る視覚特徴を時間的に安定化できる可能性がある。

実装候補は、`forward_image()`で取得・キャッシュされる共有特徴のうち、まず低解像度のtop-level featureへ追加残差を適用すること。`forward_image()`直後のraw featureを変更すると、SAM2 memory encoder / memory attentionにもMamba特徴が流れるが、これは今回の仮説には整合している。

## 6. この構成の限界

共有image embeddingへMambaを入れても、ID switchを直接解決するわけではない。SAM2の人物別memoryやpromptがすでに誤っていれば、その後段で誤った人物を処理する可能性は残る。

したがって、研究上の主張は「ID routingを解決する」ではなく、次のようにする。

> ID routing前の共有視覚特徴を時間方向に補強し、既存の人物別SAM2処理が誤対応へ陥ることへの耐性を高める。

明示的にID誤対応を解決するには、別途re-identificationやcross-object associationが必要になる。

## 7. 検証仮説

### 主仮説

SAM2の人物別memory処理より前に共有image embeddingへsequence-level temporal Mambaを追加すると、既存のSAM2 mask decoderへ渡る特徴が時間的に安定し、maskの揺れ・見失い・ID switchが減少する。

### 反証・リスク

- SAM2のmemory attentionがすでに十分な時系列統合を行っており、Mambaの追加効果が小さい。
- 共有stateは人物固有の情報を持たないため、個別人物の遮蔽や再出現には弱い。
- temporal Mambaが過去フレームの誤特徴を保持し、SAM2 memoryとは別の誤り伝播経路になる。
- raw featureへ入れることで、mask decoderだけでなくmemory encoder・memory attentionにも影響し、効果の切り分けが難しくなる。

## 8. 最小比較

```text
B0: 現行SAM2
B1: 共有image embedding + Mamba、出力ゼロのparity control
B2: 共有image embedding + 学習済みtemporal Mamba
```

診断用に、人物別処理後の構成も比較候補とする。

```text
B3: memory attention後の人物別pix_feat + per-object Mamba
```

B2がB0に対してAssA、IDF1、IDSWを改善すれば、共有特徴の時間補強がID誤対応へ間接的な耐性を持つ可能性がある。maskの揺れだけが改善する場合は、ID問題ではなくdecoder入力特徴の時間安定化として解釈する。

## 9. 初期実装で固定する範囲

- SAM2 image encoderの内部構造は変更しない
- MaskDecoderとTwo-way Transformerは変更しない
- object ID routingとtrack lifecycleは変更しない
- Mamba stateはsequence単位で管理する
- sequence開始時にstateをresetする
- まずは低解像度の共有image embeddingだけを対象にする
- high-resolution skip featuresは初期実験では変更しない
- 既存のbbox用MambaStateful checkpointは流用しない

## 10. 結論

今回の方向性は、「mask decoder内部へMambaを埋め込む」よりも、次のように表現するのが正確である。

> SAM2の人物別memory処理より前に、共有image embeddingへsequence-level temporal Mambaを追加し、既存mask decoderへ入力される視覚特徴を時間方向に補強する。

これは既存の動き予測Mambaが抱える「SAM2のID対応誤りをそのまま受け取る」問題を緩和する方向にはなっている。ただし、ID対応そのものを解く構成ではないため、初期実験では`AssA`、`IDF1`、`IDSW`とmask安定性を分けて評価する必要がある。

## 関連ファイル

- `.research/secretary/notes/brainstorm/2026-09-27-temporal-mamba-decoder-minimal.md`
- `.research/secretary/notes/brainstorm/2026-09-27-priority-after-0925-mtg.md`
- `.research/lab/projects/sam2-mamba-motion-tracking/meetings/2026-09-25-mtg.md`
- `.research/lab/projects/sam2-mamba-motion-tracking/meetings/2026-09-18-mtg.md`
