---
date: 2026-08-28
project: sam2-mamba-motion-tracking
source_todo: null
topic: MIRU意見の分析とIDSWの解釈
status: exploratory
tags: [brainstorm, research, miru, state-carry, idsw, gating]
---

# MIRU意見の分析とIDSWの解釈

## 相談内容

MIRUで以下の意見を受けた。

- B-BOXを3Dコンボリューションでまとめる
- 線形から非線形へ、学習モデルにする
- デコーダーに入れこむ
- LSTMとTransformerも比較する
- Mambaとカルマンフィルタをゲーティングする
- IDSWが負けている理由を確認する

## 現在の研究文脈

- 研究対象はSAM2/SAMURAIに外付けしたMamba動き予測であり、state carry型ではtrackごとにhidden stateを持ち越す。
- DanceTrack validation 25系列では、SAM2 HOTA `0.513`、SAMURAI `0.541`、stateful `0.555`。
- 一方、statefulが両baselineを下回る系列も4/25あり、常時適用によるassociation悪化またはhidden state contaminationが疑われている。
- Mamba単体の診断では、prediction-primaryよりlast accepted observation-primaryの方がHOTA `47.233 -> 47.910`、AssA `29.907 -> 30.843`、IDF1 `45.886 -> 47.315`となった。
- missing時のself-update freezeはstate非有限イベントを`4515 -> 115`へ減らし、HOTAを`47.910 -> 48.035`へ改善したが、IDSWは`2386 -> 2392`とわずかに悪化した。
- SAM2統合のepoch100はHOTA `55.520`、IDSW `1535`。元repoのbest-HOTA checkpointはHOTA `54.606`、IDSW `1525`であり、HOTAが高いcheckpointでもIDSWが少ないとは限らない。

## 提案ごとの分析

### 1. B-BOXを3D convolutionでまとめる

意図は、複数フレームのbbox列をまとめて時空間的に処理し、単一フレームのbbox差分より豊かな動き表現を学習することだと解釈できる。

- bboxが`x, y, w, h`の4次元ベクトルだけなら、3D convolutionは過剰で、時間方向の1D convolution、TCN、または小さなMLPの方が構造に合う可能性が高い。
- 画像特徴やROI feature mapを複数フレーム分まとめる場合は、3D convolutionの意味が強くなる。
- 現在の課題は表現力不足だけでなく、誤association後のstate汚染と、予測bboxをassociationへ使うことによる副作用である。3D化だけではこの問題は直接解けない。

位置づけ: 中長期の表現拡張候補。まずは同一入力・同一評価で1D temporal convolutionまたはMLPを比較し、3D化の必要性を確認する。

### 2. 線形から非線形（学習）

カルマンフィルタの線形状態遷移を、学習された非線形な動きモデルへ置き換える提案と考えられる。ただし、現在のMamba自体が既に学習ベースかつ非線形なので、研究上は「線形から非線形へ」は導入理由ではなく、以下の問いに分解する必要がある。

- 非線形な動きモデルは、遮蔽後のbbox予測を改善するか。
- 非線形性による改善はDetAかAssAか、またはIDF1か。
- 非線形予測の誤りがstateに蓄積したとき、カルマンよりIDSWを増やさないか。

位置づけ: 既存研究の説明を明確にするための軸。Mambaだけを比較するのではなく、Kalman、MLP/TCN、LSTM、Mambaを同一条件で比較すると主張が整理しやすい。

### 3. デコーダーに入れこむ

現在のMambaはSAM2/SAMURAIの外部motion filterとして使っている。これをSAM2のdecoder内部へ入れると、動き予測をmask/box生成と共同利用できる可能性がある。

- 長所: SAM2の視覚特徴と動き情報を統合でき、単なるbbox後処理より表現力が高い。
- 短所: 研究の因果切り分けが難しくなり、Mambaの効果、decoder変更の効果、association変更の効果が混ざる。
- 現在はstate carryの学習とassociationの問題が未解決であり、decoder統合を先に行うと問題の所在が見えにくくなる。

位置づけ: 最終的な発展案。ただし、今すぐの主実験ではなく、外付けMambaで効果と失敗条件を固めた後に検討する。

### 4. LSTMとTransformer

これはモデルを増やす提案というより、state carryがMamba固有の効果なのか、時系列学習一般の効果なのかを切り分ける比較実験として重要である。

- LSTM: hidden stateを持つrecurrent modelであり、state carry、teacher forcing、free running、TBPTTの検証に最も自然な比較対象。
- Transformer: attentionで過去の複数フレームを参照するため、sliding window型の比較対象として自然。ただし、state carry型との比較では入力長・計算量・cache方式を揃える必要がある。
- Mamba/LSTM/Transformerの比較だけでは結論が出ず、Kalmanと単純なMLP/TCNも含めて「線形・非線形」「recurrent・window」の軸を分ける必要がある。

位置づけ: 高い。特に最初はLSTMをrecurrent学習の対照、Transformerをwindow型の対照として小規模に比較するのが妥当。

### 5. Mambaとカルマンフィルタのゲーティング

現在のsequence別分析に最も直接対応する提案である。観測が信頼できるときはカルマンまたは観測を使い、欠損・遮蔽・観測との乖離が大きいときだけMamba予測を強く使う。

考えられる入力:

- SAM候補と観測bboxのIoU
- Kalman予測と観測のinnovation/距離
- Mamba予測と観測のIoU
- miss count、track age、直近のassociation confidence
- Mamba state norm、stateの非有限値、予測の急変量

最初から学習ゲートにせず、次の順で検証するのがよい。

1. 観測優先、Kalman優先、Mamba優先の固定ルールを比較する。
2. 1つまたは2つの信頼度特徴量による単純なsoft gateを比較する。
3. その後、gate自体を学習する。

ゲートの目的はHOTA最大化だけではなく、HOTA、DetA、AssA、IDF1、IDSWのトレードオフを確認することにする。

位置づけ: 次の主実験候補。ただし、既存の「外付けMamba + last accepted observation-primary」を基準にし、gate以外の条件を固定する必要がある。

## IDSWが負けるとは何か

IDSWはIdentity Switchesで、追跡対象に割り当てたtrack IDがフレーム間で別IDへ切り替わった回数を表す。基本的には**低い方が良い**。

今回の例では、epoch100 statefulのIDSW `1535`は、best-HOTA checkpointの`1525`より10多い。そのため、「HOTAなどの主要指標はepoch100が高いが、IDの一貫性はbest-HOTAの方が少し良い」という意味になる。

重要なのは、IDSWはHOTAと同じものを測っていない点である。動き予測によってbboxの位置や追跡継続が改善するとHOTAやDetAが上がっても、近接対象への誤associationが増えればIDSWは増える。HOTAが改善してもIDSWが悪化することは矛盾ではない。

研究中の具体例は以下。

- `dancetrack0019`: HOTAは改善したが、AssAは`0.527 -> 0.484`、IDSWは`80 -> 104`。HOTA改善をID保持改善とは解釈できない。
- P2のmissing freeze: 非有限stateは大幅に減ったが、IDSWは`2386 -> 2392`。数値の安定化とIDの改善は別問題。
- `dancetrack0063`: IDSWは`96 -> 91`と減ったが、AssAは`0.394 -> 0.309`へ下がった。IDSWだけ見てもassociation品質全体は分からない。

さらに、IDSWが少ないことが常に「よく追跡できている」ことを意味するわけではない。対象を見失って新しいtrackを作る場合、追跡継続性は悪くても、評価上のIDSWが期待ほど増えない可能性がある。そのため、IDSWはIDF1、AssA、track fragmentation、miss区間と合わせて解釈する。

## 中心仮説

stateful Mambaは、遮蔽や検出不安定時の短期予測によって追跡継続を改善する。一方、信頼できる観測がある場合や誤association後には、予測を強く使うことでassociationを壊し、IDSWまたはAssAを悪化させる。

したがって、現時点の主仮説は次の形が最も明確である。

> Mambaの性能不足ではなく、Mamba予測を使うべき時刻と、観測・Kalmanを優先すべき時刻を区別できていないことが、IDSWとsequence別改悪の一因ではないか。

## 実験候補の優先順位

### 第一候補: Mamba-Kalman/観測ゲーティング

- 既存のepoch100 statefulを固定。
- last accepted observation-primaryを固定。
- gateなし、Kalman/観測のみ、Mambaのみ、固定重み、信頼度ベースgateを比較。
- 共通25系列で全指標を評価し、改善群`0007/0034`と改悪群`0005/0063`のframe-levelログを確認する。

成功基準は、HOTAを維持または改善しつつ、改悪系列のAssA/IDF1低下とIDSW増加を抑えること。単にIDSWだけを下げ、対象を頻繁に見失う方式は採用しない。

### 第二候補: recurrent学習の比較

- Kalman、MLP/TCN、LSTM、Mambaを同じ入力・split・loss・unroll長で比較。
- teacher forcingのみではなく、free runningとTBPTTを含める。
- 推論時state carryとの分布差を評価する。

### 保留: decoder内統合、3D convolution

表現力を広げる案として価値はあるが、現在のボトルネックであるassociation・state更新・評価解釈を先に切り分ける必要がある。外付け方式で因果を確認してから進める。

## 未解決事項

- MIRUでいう「B-BOXを3D convolutionでまとめる」が、bbox座標列を指すのか、画像/ROI featureを指すのか。
- カルマンとのゲート対象が、最終bbox、association score、state更新、またはSAM2 decoder入力のどれか。
- IDSW増加が、誤association、state drift、track再生成、または検出品質変化のどれに由来するか。
- gateの成功基準でHOTAとIDSWのどちらを優先するか。最低限、HOTAだけでなくAssA、IDF1、IDSWを併記する必要がある。

## 現時点の結論

MIRUの意見の中で、直近の研究に最もつながるのは「Mambaとカルマンフィルタのゲーティング」と「LSTM/Transformerを含む比較」である。前者は現在観測されているsequence別改悪とIDSW問題に直接効き、後者はstate carryの学習方法そのものを検証できる。

3D convolutionとdecoder内統合は、次段階の表現拡張として保留する。まず、Mambaを常時適用する構成から、観測信頼度に応じてMamba・Kalman・観測を使い分ける構成へ進み、IDSWの増加が抑えられるかを確認する。

## 参照

- `.research/lab/projects/sam2-mamba-motion-tracking/README.md`
- `.research/secretary/notes/brainstorm/2026-08-04-stateful-sequence-improvement-degradation-analysis.md`
- `.research/lab/projects/sam2-mamba-motion-tracking/meetings/2026-07-30-mtg.md`
