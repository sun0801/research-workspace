---
date: 2026-08-04
project: sam2-mamba-motion-tracking
source_todo: null
topic: stateful提案手法のsequence別改善・改悪分析
status: exploratory
tags: [brainstorm, research, HOTA, state-carry, sequence-analysis]
---

# Stateful提案手法のsequence別改善・改悪分析

## 読み込んだ文脈

- DanceTrack validation共通25系列で、SAM2、SAMURAI、SAM2 + Mamba stateful epoch100を比較。
- 比較値はTrackEval標準HOTA（`HOTA___AUC`、alpha 0.05〜0.95の平均）。
- 全25系列統合HOTAはSAM2 `0.513`、SAMURAI `0.541`、stateful `0.555`。
- 研究上の主要仮説は、Mambaの動き予測による追跡継続・association安定化。ただしhidden state contamination、誤association、学習時と推論時のstate carry不一致が懸念されている。

## 問い

提案手法が改善するsequenceと改悪するsequenceにはどのような違いがあり、state carryをどの条件で使うべきか。

## 観察

### 改善群

statefulがSAM2・SAMURAIの両方を標準HOTAで上回ったのは11/25系列。

- 大きな改善: `dancetrack0025`（SAM2比 +0.268、SAMURAI比 +0.078）、`dancetrack0041`（+0.178、+0.001）、`dancetrack0079`（+0.176、+0.009）、`dancetrack0019`（+0.128、+0.009）、`dancetrack0004`（+0.107、+0.045）、`dancetrack0034`（+0.102、+0.019）。
- `dancetrack0007`はSAM2比 +0.051、SAMURAI比 +0.105で、DetAとAssAの両方が改善しており、動き予測による継続・対応付け改善の代表候補。
- `dancetrack0004`はSAMURAI比でDetAがほぼ同じ一方、AssAが`0.470`から`0.558`へ改善しており、association改善の寄与が大きい。
- `dancetrack0034`はSAMURAI比でDetAが`0.438`から`0.469`、AssAが`0.489`から`0.494`へ改善。前回の局所的な見失い回復候補と整合する。
- `dancetrack0019`はSAMURAI比でHOTAはわずかに改善するが、AssAは`0.527`から`0.484`へ低下し、IDSWは`80`から`104`へ増加。HOTA改善をID保持改善と解釈してはいけない例。

### 改悪群

statefulがSAM2・SAMURAIの両方を下回ったのは4/25系列。

- `dancetrack0005`: HOTA `0.514/0.494 -> 0.471`。DetAはほぼ変わらないが、AssAがSAM2比`0.733 -> 0.606`、SAMURAI比`0.670 -> 0.606`へ大きく低下。誤associationの持続、またはhidden state contaminationの有力候補。
- `dancetrack0018`: SAM2比`0.771 -> 0.721`。DetA `0.656 -> 0.591`、AssA `0.908 -> 0.883`の双方が低下。すでにSAM2が良い系列にstatefulを常時適用する必要がない可能性。
- `dancetrack0063`: HOTA `0.368/0.330 -> 0.318`。SAM2比でAssAが`0.394 -> 0.309`へ低下する一方、IDSWは`96 -> 91`にわずかに減少。IDSWだけでは追跡品質を説明できず、association精度全体の低下が問題。
- `dancetrack0010`: HOTA `0.875/0.867 -> 0.863`。高性能系列で、statefulが既存の良い追跡をわずかに壊している。改善余地より副作用が見えやすい飽和系列。

## 仮説候補

1. **難しいsequenceでの回復仮説**: ベースラインの見失い・検出不安定がある場合、Mambaの短期動き予測が追跡継続とassociationを補助する。
2. **常時適用の副作用仮説**: 観測が十分信頼できる場合にもstateful予測を強制すると、正しい観測から予測へ置き換わり、DetAまたはAssAを悪化させる。
3. **state汚染仮説**: `0005`や`0063`では一度の誤association・誤更新がstateに残り、後続フレームの対応付け品質を下げている可能性がある。
4. **学習・推論不一致仮説**: sliding-window的に学習されたmotion modelをstate carryで推論しているため、長いfree-running区間や難しい遮蔽でstate driftが生じる可能性がある。
5. **HOTA分解仮説**: 改善は全てassociation改善ではなく、`0019`のようにDetA改善だけでHOTAが上がる場合がある。HOTA、DetA、AssA、IDF1、IDSWを併記すべき。

## 手法の改善案

- **条件付きMamba利用**: SAM候補IoU、観測との一致度、miss count、association confidenceが低いときだけMamba予測を強く使い、信頼できる観測があるときは観測を優先する。
- **association分離**: Mamba予測bboxをhard IoU matchingの主位置にせず、last accepted observationを主軸にして、Mambaを候補順位付け・補助予測として使う。
- **quality-aware state更新**: untrusted match、欠損、急激なIoU低下時はstateを更新しない。単純な固定threshold resetではなく、連続不一致・state norm・予測と観測の乖離を組み合わせる。
- **state reset / track単位の保護**: 一対象の誤associationが別対象のstateへ混入しないよう、track identityの再対応付けとstate初期化条件を明示する。
- **recurrent学習**: teacher forcingだけでなくfree-running、遮蔽・欠損・誤associationを含むunrollとTBPTTで学習し、推論時state carryとの分布差を減らす。
- **sequence依存の評価**: HOTA単独でcheckpointを選ばず、DetA、AssA、IDF1、IDSWを含む複数指標で、改善群と改悪群の両方を残して選ぶ。

## 反例・注意点

- `dancetrack0019`のようにHOTAが改善してもAssAやIDSWが悪化する系列があるため、「HOTA改善 = ID追跡改善」とは言えない。
- `dancetrack0041`はSAM2からは大きく改善するが、SAMURAIからはほぼ変化がなく、比較baselineによって印象が変わる。
- `dancetrack0058`、`0030`のようにSAMURAIには改善してもSAM2にはわずかに改悪する系列があり、提案手法の効果はベースライン依存である。
- ここでの原因はsequence-level指標からの仮説であり、実際の遮蔽、対象交差、ID切替、state更新イベントはViewerとcandidate debugで確認が必要。

## 今回見えた方向性

statefulは平均HOTAを`0.513/0.541`から`0.555`へ改善しており、難しいsequenceでの追跡継続には有効な兆候がある。一方、全sequenceへ一律適用すると、既に良いsequenceやassociationが不安定なsequenceで性能を損なう。

現時点の中心的な改善方針は、Mambaを常時置換器として使うことではなく、観測信頼度に応じて予測を使い分けるquality-awareなassociation・state更新にすること。また、`0005`を代表的な改悪例、`0007`または`0034`を代表的な改善例として、時系列Viewer確認を行うのが有効。

## 次アクション候補

1. [ ] `dancetrack0005`、`0063`、`0018`、`0010`のcandidate debugを確認し、AssA低下またはDetA低下のフレーム区間を特定する | 優先度: 高
2. [ ] 改善代表`0007/0034`と改悪代表`0005/0063`について、同一フレームの接触シートを作成する | 優先度: 高
3. [ ] 改善・改悪を分けるconfidence / miss / state update特徴量をsequence単位で集計する | 優先度: 高
4. [ ] quality-aware association・recurrent学習・TBPTTのどれを次の主実験にするか決める | 優先度: 通常

## Spec化候補

次の主実験を決めるには、まず改悪sequenceのframe-level原因確認が必要。現時点では、quality-aware state updateを第一候補としつつ、実装specへの昇格はユーザー承認と評価条件の確定後に行う。

## 関連ファイル

- `.research/lab/projects/sam2-mamba-motion-tracking/experiments/2026-08-04-sequence-level-standard-hota-comparison.md`
- `.research/lab/projects/sam2-mamba-motion-tracking/experiments/2026-07-28-sam2-kf-score-weight-epoch100-25seq.md`
- `.research/lab/projects/sam2-mamba-motion-tracking/meetings/2026-07-30-mtg.md`
- `.research/secretary/notes/brainstorm/2026-07-27-miru-qualitative-result-selection.md`
