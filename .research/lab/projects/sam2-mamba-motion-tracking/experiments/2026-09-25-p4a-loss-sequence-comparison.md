---
date: 2026-09-25
project: sam2-mamba-motion-tracking
source: checkpoint-diagnostic
status: exploratory
tags: [experiment, p4a, loss, sequence-analysis, sam2, failure-analysis, shuffle, cross-condition]
---

# P4a checkpoint lossとSAM2 sequence失敗の探索的比較

## 位置づけ

このメモは、checkpoint lossとSAM2 sequence失敗の関係を探索するための暫定比較である。lossはnon-shuffle / shuffleの両条件、SAM2のsequence評価はshuffle P4a統合runを使っているため、条件が完全には揃っていない。

したがって、以下の表は原因を確定する正式なsequence別失敗分析ではなく、次に同一条件で確認する候補を選ぶための記録として扱う。正式な主分析は、同一checkpoint・同一推論条件で作成する `2026-09-25-sam2-sequence-failure-analysis.md` に分離する。

## 結果

非shuffle / shuffleのepoch100 checkpointを、同じDanceTrack val・同じP4a forward・`loss_start_index=4`・`tbptt_length=12`・Smooth L1で再計算した。

| 条件 | 全体mean Smooth L1 | 高loss上位sequence |
|---|---:|---|
| non-shuffle | 0.04142 | 0097, 0018, 0094, 0073, 0043 |
| shuffle | 0.04110 | 0097, 0018, 0094, 0073, 0043 |

shuffleは全体lossを約0.00032下げたが、高loss sequenceの順位はほぼ変わらなかった。epoch100・単一seedのため、shuffleの一般的な効果とは解釈しない。

## SAM2失敗との対応

既存のshuffle P4a SAM2統合結果でHOTAが低かったsequenceは次の通り。

| sequence | SAM2 HOTA | IDF1 | IDSW | Mamba loss（non-shuffle） |
|---|---:|---:|---:|---:|
| dancetrack0026 | 0.3359 | 0.3190 | 168 | 0.0341 |
| dancetrack0014 | 0.3670 | 0.3564 | 132 | 0.0304 |
| dancetrack0063 | 0.4463 | 0.4267 | 84 | 0.0279 |
| dancetrack0041 | 0.4894 | 0.4598 | 222 | 0.0300 |
| dancetrack0094 | 0.5363 | 0.4806 | 146 | 0.0753 |

Mamba loss上位の`dancetrack0097`（0.0894）と`0018`（0.0814）は、SAM2 HOTAがそれぞれ0.9057、0.8013であり、Mamba誤差がそのままSAM2失敗にはつながっていない。

## 可視化候補

1. 共通失敗: `dancetrack0094`
2. SAM2側要因候補: `dancetrack0026`, `0014`, `0063`
3. Mamba誤差をSAM2が吸収した候補: `dancetrack0097`, `0018`

各候補で、GT bbox、Mamba予測、SAM2出力bbox/mask、ID switch、matching変更、missing区間を同じframe範囲に重ねる。

## 探索的解釈

loss再計算は、SAM2可視化候補の補助情報として利用できる。ただし、現状はSAM2側がshuffle runであるため、「Mamba起因」「SAM2 / association起因」「SAM2が予測誤差を吸収」という分類は仮説であり、同一条件の出力で再確認する必要がある。

この比較から確実に言えるのは、Mamba loss上位とSAM2 HOTA下位が一致しないことである。これは「lossだけではSAM2のsequence失敗を説明できない」という次の分析方針を支持するが、shuffleの影響を評価した結果ではない。

## 関連

- `experiments/2026-09-25-checkpoint-loss-sequence-failure-linkage.md`
- `experiments/2026-09-18-p4a-shuffle-sam2-trackeval.md`
- `meetings/2026-09-18-mtg.md`
- `experiments/2026-09-25-sam2-sequence-failure-analysis.md`
