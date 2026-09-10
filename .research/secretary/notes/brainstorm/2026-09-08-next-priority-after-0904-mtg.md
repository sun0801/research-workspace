---
date: 2026-09-08
project: sam2-mamba-motion-tracking
source_todo: "前回MTGの内容などを参照して、何から進めるべきか考えて"
topic: 9/4 MTG後の優先順位整理
status: exploratory
tags: [brainstorm, priority, p4a, tbptt, sam2]
---

# 9/4 MTG後の優先順位整理

## 読み込んだ文脈

- `meetings/2026-09-04-mtg.md`
- `README.md`
- `experiments/2026-09-04-l0-p4a-tracker-sam2-comparison.md`
- `experiments/2026-09-02-p4b-checkpoint-tracking-evaluation.md`
- `specs/2026-09-02-p4b-checkpoint-tracking-evaluation-spec.md`
- `specs/2026-09-03-boxmot-mot-demo-video-generation-spec.md`
- `todos/2026-09-08.md`

## 相談の出発点

9/4 MTGでは、stateful unroll + TBPTTの実装と学習が動作したことを確認した。しかし、`detach`・state carry・resetの実際の挙動、内部stateログ終盤のスパイク、Mamba tracker単体とSAM2統合後の性能差が未整理である。これらを確認してから、SAM2 decoderへのMamba統合へ進む方針になった。

## 現在の事実

- L0 tracker単体: HOTA 47.293
- P4a tracker単体: HOTA 48.121（L0比 +0.828）、AssA +1.171、IDF1 +1.912、IDSW -179
- L0 SAM2統合: HOTA 55.520
- P4a SAM2統合: HOTA 54.391（L0比 -1.129）
- したがって、P4aの単体改善をそのままSAM2統合の改善とは解釈できない。
- 9/8 TODOでは、まず`detach`の対応付けとchunk境界のstate carry/reset確認、その後にstateログ解釈と4条件のsequence比較を行う順序になっている。
- View原稿には2026-09-11の既存締切があるため、研究の切り分けと並行して軽量に進める必要がある。

## 中心となる問い

P4aのtracker単体改善とSAM2統合後の低下は、stateful unroll + TBPTTの効果、state管理の実装、SAM2側の相互作用、評価条件の差のどれによって説明できるか。

## 仮説候補

1. P4aはtracker単体の時系列予測には効いているが、SAM2統合では予測bboxの使われ方やassociation・cache更新との相互作用により改善が吸収または反転している。
2. `detach`はgradient graphだけを切り、`h`・`ss`の数値stateはcarryされる想定だが、chunk境界やbatch内系列の切り替えで意図しないreset・混線がある可能性がある。
3. 内部state終盤のスパイクは、stateそのものの不安定化とは限らず、記録値の定義・正規化・ログ横軸・chunk境界のいずれかによる見かけの変化である可能性がある。

## 発散した候補

### A. P4a実装監査（最優先）

- `detach`の呼び出し箇所と頻度を確認する。
- `tbptt_length=12`がepoch、optimizer step、unroll frameのどの単位かを確認する。
- `h`・`ss`がchunk境界でcarryされることを追跡する。
- track/video開始時のzero reset、batch内系列切り替え、終端処理を確認する。
- コード上の期待と実ログ上のloss/state変化を対応付ける。

### B. 内部stateログ診断

- 記録している値がstate norm、max absolute value、要約値のどれかを確定する。
- 横軸がframe、chunk、step、epochのどれかを確定する。
- スパイク位置がdetach境界、sequence境界、reset、target切り替えと一致するか確認する。
- finite性だけでなく、スパイク後に予測誤差・tracking結果が悪化するかを見る。

### C. 4条件のsequence単位比較

実装監査で直接原因が見つからない場合に限定する。

- L0 tracker単体
- P4a tracker単体
- L0 SAM2統合
- P4a SAM2統合

同じsequenceについてHOTA、AssA、IDF1、IDSWと、必要なら予測bbox・accepted observation・cache更新の挙動を並べ、単体改善が統合後に反転するsequenceを抽出する。

### D. View原稿・研究室見学資料

研究の因果切り分けを待たず、説明資料として独立に進められる。Viewでは、Mambaを使う理由、training windowと推論時state carryの違い、評価スコアの意味を2ページに収める。研究室見学資料では、BoxMOT/OC-SORTの定性的デモを研究性能の主張と混同しない形で整える。

### E. SAM2 decoder統合

P4aの挙動と4条件の性能差が整理されるまで保留する。今始めると、学習・state管理・SAM2統合位置の複数要因が同時に変わり、原因帰属が難しくなる。

## 収束した優先順位

1. **P4a実装監査**: `detach`、chunk単位、`h`・`ss` carry、resetをコードとログで確定する。
2. **内部stateログ診断**: スパイクの意味と発生条件を監査結果に照らして確定する。
3. **原因未特定なら4条件のsequence比較**: tracker単体とSAM2統合の反転条件を抽出する。
4. **View原稿と研究室見学資料を並行して進める**: 9/11締切のある文章作業を後回しにしない。
5. **SAM2 decoder統合**: 上記の切り分け後に、統合位置・token数の検証計画を作ってから開始する。

## 次アクション候補

以下は候補であり、TODOへの自動追加はしない。

1. `detach`・carry・resetのコード追跡表を作る（対象関数、呼び出し頻度、stateの入力/出力、reset条件）。
2. 代表1系列または短いstubで、chunk境界ごとのframe index・state finite性・lossを同時に出力してログ単位を確認する。
3. 内部stateログの定義・横軸・スパイク位置を1枚の診断表にまとめる。
4. 実装監査で問題が見つからない場合、4条件のsequence別比較表を作る。
5. View原稿では、現時点の性能値を「tracker単体」と「SAM2統合」に分けて記載する。

## Spec化候補

- `detach`・carry・resetの監査は、現時点では既存P4a実装の検証作業であり、新規研究specより先に診断ログ・確認表として扱うのが適切。
- 4条件のsequence比較は、監査後も原因が曖昧な場合に、既存P4b固定条件specの補助実験として具体化できる。
- decoder統合は、統合位置、入力token、学習対象、baseline、成功基準を定義してから別spec化する。

## 未解決の問い

- `tbptt_length=12`は実際に12フレームのgradient truncationになっているか。
- `detach`後のstate数値は同一track内でcarryされ、別trackへ混入していないか。
- stateログの終盤スパイクは、内部stateの不安定化か、ログ定義・境界の問題か。
- P4a単体改善がSAM2統合で反転する主因は、予測bbox、association/cache、SAM2 mask更新、または評価条件のどれか。

## 関連ファイル

- `.research/lab/projects/sam2-mamba-motion-tracking/meetings/2026-09-04-mtg.md`
- `.research/lab/projects/sam2-mamba-motion-tracking/experiments/2026-09-04-l0-p4a-tracker-sam2-comparison.md`
- `.research/lab/projects/sam2-mamba-motion-tracking/experiments/2026-09-02-p4b-checkpoint-tracking-evaluation.md`
- `.research/secretary/todos/2026-09-08.md`

---

## 追記 09:11（loss振動診断のspec化前整理）

### 相談の出発点

Cometの`train/current_loss`がepochごとに振動して見える理由を、学習アルゴリズムを変更せずに切り分ける。既存ログは各epochのlocal step 0, 50, 100だけであり、DataLoaderは`shuffle=False`である。

### 中心となる問い

lossの周期性は、固定batch順序による特定trajectory群の難しさなのか、Cometの疎なloggingによる見かけなのか、それともstate/TBPTTの挙動なのか。

### 仮説

1. 固定順序により、難しいbatchが毎epoch同じ位置に現れる。
2. 全batchのlossを見れば、Comet上の周期性は消える。
3. lossとstate normが同じbatchで跳ねる場合は、state/TBPTT側の追加調査が必要である。

### 採用する診断案

- P4aのconfig、seed、batch size、`shuffle=False`、model、optimizerは維持する。
- `step % 50`のlogging条件だけを一時的に全batch記録へ変更する。
- 3 epochを実行し、117 batch/epoch、合計351 batchのlossを確認する。
- まずはshuffleやbatch size変更を同時に入れず、logging不足とbatch位置の影響だけを確認する。
- association modeとmissing modeは今回のloss診断対象に含めない。`prediction + self_update`は別のtracker評価条件として扱う。

### Spec化方針

brainstormでは今回の問い・仮説・候補を保存する。specには、全batch loggingだけを行う3epoch診断実験、変更対象、実行条件、成功/失敗基準、実行後の一時patch復元方法を確定して記載する。

### 次アクション候補

1. `2026-09-11-p4a-loss-oscillation-diagnostic-spec.md`を保存する。
2. spec承認後、`train_mamba_stateful.py`のlogging条件だけを一時変更する。
3. 3 epochを実行し、Cometの全batch lossを確認する。

---

## 追記 04:36（spec改善）

指摘内容とコード確認を踏まえ、specに次を反映した。

- frame gapを既知の交絡候補として扱い、loss/stateの同時ピークからTBPTT原因と直ちに断定しない。
- 現在の`train/state_max_abs`はepoch内最大値なので、`train/current_state_max_abs`をlossと同じglobal stepでbatch単位に記録する。
- `epoch`、`local_batch`、Cometのglobal `step`を対応づけ、epoch間Spearman相関とtop-10 peak overlapで再現性を数値化する。
- 実行開始時に`len(dataloader) == 117`を確認し、351点という期待値を実測値と分けて扱う。
- 再現ピークのbatchをtrajectory構成・frame gap確認へつなげ、説明できない場合だけsegment-levelのstate/TBPTT診断へ進む。

この3epoch runは旧P4aの病理解剖用であり、frame gap修正後の正式モデル性能とは扱わない。
