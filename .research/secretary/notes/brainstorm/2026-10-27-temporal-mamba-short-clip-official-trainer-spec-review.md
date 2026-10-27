---
date: 2026-10-27
project: sam2-mamba-motion-tracking
source_todo: null
topic: temporal-mamba-short-clip-official-trainer-spec-review
status: exploratory
tags: [brainstorm, research, spec-review, temporal-mamba, sam2, training]
---

# 公式trainerによるtemporal Mamba短区間学習specのレビュー

記録日時: 2026-10-27 12:15 JST

## 対象・確認範囲

- 対象: [短区間学習spec](../../../lab/projects/sam2-mamba-motion-tracking/specs/2026-10-27-temporal-mamba-short-clip-official-trainer-spec.md)。以下のspec行番号はレビュー時点のもの。
- 研究文脈: プロジェクトREADME、10/23 MTG議事録、10/26 brainstorm、V3 spec・実験ログ、リファクタリング記録。
- 実装: `/mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2`、`1002_seminar`、`09a30a7`。読み取り専用で確認。
- 確認方法: コードの静的確認とPython標準ライブラリによる構文木解析。GPU上のforward・backward、OOM、数値一致は今回実行していない。
- 今日のTODOファイルは未作成。今回の依頼はspecレビューであり、TODO追加や実装開始の依頼ではない。

## 総評

Aで固定したF0への追加効果、C−Bでデコーダ学習時のV3の追加効果を見る設計は、探索的な比較として整理されている。最後のcheckpointを使うこと、val-25でcheckpointを選ばないこと、testを使わないこと、単一seed・再利用valの限界も明記されている。

一方、公式の学習経路で新たに通る補正クリックのAPI互換、学習・推論の一致条件、学習済み重みの復元、V3のメモリ対策には実装前の補足が必要。以下は修正提案であり、新しい決定事項ではない。

## 優先して修正したい点

### 1. [P1] 先頭補正クリックの経路が現コードの戻り値と整合していない

対象spec: 74、131〜132行。

根拠:

- `sam2/modeling/sam2_base.py:726` の `_forward_sam_heads` は8要素を返す。
- `training/model/sam2.py:518` の `_iter_correct_pt_sampling` と同426行の呼び出し元は7要素として展開している。構文木解析でも8対7を確認した。
- 今回は先頭のクリック・boxで補正クリックを行うので、この経路に入る。旧自作trainerは `num_correction_pt_per_frame=0` で、この分岐を使っていなかった。

影響: 補正クリックに入った時点で、戻り値の展開に失敗する。

さらに、展開数だけを直してもIoU lossの契約が揃わない。`sam2_base.py:708,729` の戻り値は選択済みの `best_ious[B]`。通常の学習経路は `training/model/sam2.py:405` で全候補の `_last_multimask_ious` を使うが、補正経路は420行で選択済みの値を渡し、475・531行で記録する。初回の1クリックで3候補を出す場合、`training/loss_fns.py:118` では候補ごとの正解IoUに対して選択済み1個の予測値がbroadcastされ、全候補への適切なIoU監督にならない。

修正案:

- 段階0に、補正経路の戻り値と全候補IoUの受け渡しの互換修正を追加する。
- 段階1で、mask・click・boxをそれぞれ強制し、forward、候補ごとのIoUとlossの対応、backwardの成功を確認する。

### 2. [P1] 学習・推論の出力一致テストは「同じ先頭box」だけでは成立しない

対象spec: 132行の②。

根拠: 学習側は先頭の補正クリックを追加し、その後のマスク・object pointerをmemoryへ保存する（`training/model/sam2.py:410〜450`）。`evaluate_track` は先頭boxのみで、補正クリックを追加しない（`training/eval_mose_fulltrack.py:127〜143`）。同じ画像tensorと先頭boxでも、後続が参照するmemoryが異なる。

修正案:

- 経路の一致確認では補正クリックを無効にし、重み・入力・プロンプト・初期state・系列長・モード・dtypeなど、計算に影響する条件を揃える。
- 実際の学習設定での補正クリックの正しさは、上記1の確認として別途検証する。
- 比較対象をlogitだけでなくconv/SSM stateにも広げ、FP32の決定的な設定とbf16での許容誤差を明記する。既存V3 specの数値一致基準を参照できる。

### 3. [P1] B・Cの学習済みデコーダを評価へ渡すcheckpoint契約が未定義

対象spec: 98、131〜135行。

根拠:

- 公式trainerは全重みを `checkpoint["model"]` に保存する（`training/trainer.py:339〜349`）。
- 現在のV3評価ラッパーはF0を読み、別checkpointの `adapter_type`・`v3_levels`・`adapter` を使ってadapterだけを追加する（`training/mose_adapter_eval.py:56〜63`）。
- `evaluate_track` 関数は渡されたモデルを評価するので継続利用できるが、現ラッパーをそのまま使うだけでは公式checkpoint形式と一致しない。Cを従来のadapter-only形式へ合わせると、更新したデコーダが評価に反映されない。

修正案:

- 凍結した `evaluate_track` の外側に、A/B/Cの学習済みSAM2本体とV3を復元するloaderまたは明示したexport形式を定義する。
- 段階1に「非ゼロV3と更新済みデコーダを保存→別インスタンスに復元→パラメータと出力が一致」を追加する。Bも更新済みデコーダで確認する。
- F0からの初期化では、新規V3以外のmissing/unexpected keyを許さない。公式configの `strict: true` を単に全面解除する形にはしない。

### 4. [P1] 3段V3で必要だったactivation checkpointingの継承が明記されていない

対象spec: 70、131、133行。

根拠: `MambaCell.checkpointing` の既定値はfalse（`sam2/modeling/temporal_adapters.py:67`）。旧trainerは `adapter.set_checkpointing(args.adapter_checkpointing)` を呼ぶ（`training/mose_adapter_train.py:205`）。既存V3 specのリスク欄では、checkpointingなしの学習は約21 GiBと記録されている。新specが引用する12.6 GiBは、機能を明示して移植しない限り新trainerで保証されない。

修正案: A/Cのconfigとmanifestにadapter checkpointingの有効化を明記する。補正クリックの経路も含む新trainerでforward・backward・optimizer更新後のピークVRAMを測る。公式側の補正クリック用checkpointingと、V3のMambaCell用checkpointingを区別して記録する。

## 検証と結果解釈の修正候補

### 5. [P2] forward一致とloss低下だけでは時間方向の勾配を保証できない

対象spec: 86、132〜133行。

stateを毎フレームdetachしてもforward値は一致し、現在フレームだけの経路でlossが下がる可能性がある。Cではデコーダだけが学習していても、現在のpilot合格条件を満たせる。既存V3 specにあった時間方向の勾配と各段の更新確認を、新しい統合でも継承したい。

修正案:

- 非ゼロのV3出力層を使い、後半フレームのlossから前時刻のconv/SSM stateへ勾配が届くことを確認する。
- 区間間ではstateをリセットし、別サンプルへ値・計算グラフが漏れないことも確認する。
- A/Cで、各段のMamba・LayerNorm・出力層・top-down接続に勾配が届き、weight decay以外の理由で重みが変わることを確認する。
- 固定するmoduleの `eval()` と `requires_grad=False` は、adapterの出力からlossまでを `no_grad` にする意味ではないことを明記する。
- 現コードでは `temporal_state=None` がstreaming経路を選ぶ（`sam2_base.py:1139〜1146`）。明示的に初期化したstateを学習経路へ渡し、mask先頭でV3を使わない場合はそのstateを維持する。

### 6. [P2] 比較に使う乱数・共通学習量・pilotの規約を固定したい

対象spec: 78〜81、123、133、158行。

旧V3 specは同じ軌跡列・更新回数・seed・augmentationを明示していた。今回も特にC−Bの比較では、学習サンプルの違いが加わらないようにしたい。

修正案:

- A/B/Cで共通の更新回数Nを使い、本学習前に固定する。Bだけ速いことを理由に更新数を増やさない。
- 学習seedを明示し、動画順、切り出す区間、対象ID、augmentation、初期プロンプトの乱数を条件間で揃える。モデル初期化の乱数消費とデータ側の乱数を分離し、実際のサンプル列を記録する。
- 200更新pilotのcosineが、本学習スケジュールの最初200更新なのか、200更新で終わる短縮スケジュールなのかを明記する。前者なら本学習初期の安定性を直接確認できる。
- 診断用lossは固定した入力・プロンプトでF0と比較する。pilotの重み・optimizerを本学習に持ち込むかも明記する。旧specと同様、F0＋新規adapterからやり直す案が明確。

### 7. [P2] 公式lossへの移行で、フレーム方向の集約規約も変わる

対象spec: 78〜80、86、133行。

旧trainerはframe lossを軌跡長nで割って積算する（`training/mose_adapter_train.py:399`）。公式lossは各フレームのlossを加算し、フレーム数では割らない（`training/loss_fns.py:167〜180`）。補正クリック各反復のlossも加算される（同207〜214行）。旧pilotのLR・clip値を使うので、この差は明記したい。

修正案: 公式の合計lossを使うか、フレーム平均にするかを明示し、pilot・学習ログ・F0診断で揃える。公式lossを採るなら、loss重み20:1:1:1、全候補IoU監督なども設定として記録する。AdamWなので、単純に「実効LRが8倍」とは解釈しない。

### 8. [P2] stateの1歩ずれの影響は、先頭1フレームに限定できない

対象spec: 87〜88行。

Mambaのconv stateとSSM stateは再帰的に更新される（`sam2/modeling/temporal_adapters.py:95,105〜107`）。先頭を処理したかどうかの違いは、後続stateと出力にも伝播し得る。

修正案: 先頭maskでV3を通さないという合意は維持し、「box評価とのstate初期履歴の差が後続へ与える影響は未検証」と記載する。

表現上の補足: GT maskから出力マスクを直接作る場合も、`use_obj_ptrs_in_encoder=true` の設定ではobject pointer生成のため `_forward_sam_heads` を呼ぶ（`sam2_base.py:761〜767`）。「マスク予測はGTをそのまま使い、V3は通らない」と書くと正確。デコーダ全体を一切呼ばないという説明は避けたい。

### 9. [P2] H1未達から「学習方法を変えても伸びない」と結論するのは強すぎる

対象spec: 122〜124、136行。

H1はval-25、H2は125動画全体なので、H1未達かつH2支持は起こり得る。train lossが下がってもval-25が伸びない場合もあり、「学習できている」と「汎化が改善した」は同じではない。実際に旧V1では、val-25の改善がval全体で再現しなかったことが実験ログにある。

修正案:

- H1は「val-25で改善傾向を確認する監視指標」と位置づける。
- H1未達時は「val-25では改善未確認」と述べ、最終valのH2/H3とtrain診断を合わせて次の方針を判断する。
- 「上がる傾向」を判定条件に残すなら、どの区間の平均差などで判断するかを事前に固定する。
- 16フレームへ進む基準をH1だけにするか、H2/H3も含めるかは判断候補として提示する。

## 研究記録との同期

### 10. [P3] 全軌跡V3のval評価は完了済み

対象spec: 18、111、135行。

[V3実験ログ](../../../lab/projects/sam2-mamba-motion-tracking/experiments/2026-10-18-temporal-mamba-v3-mose-adapter.md) の2026-10-27追記（298行以降）に、125動画・313対象での評価完了が記録されている。

| 条件・比較 | 記録値 |
|---|---|
| F0 J&F | 0.7701 |
| 全軌跡V3 J&F | 0.7698 |
| V3−F0 | −0.03ポイント、95% CI [−0.72, +0.59] |
| V3−V3-reset | +0.13ポイント、95% CI [−0.18, +0.42] |

「未評価なので並行して回す」は完了済み結果の参照に直せる。再利用時は既存V3 specと同じく、評価対象・プロンプト・採点フレーム・評価実装の互換を確認する。

## その他の確認済み事項

- `RandomUniformSampler` は連続した区間を選び、先頭で非空の対象から抽選する。後続で対象が消えても同じ対象を使う（`training/dataset/vos_sampler.py:49〜77`）。この挙動は未決ではなくspecに記録できる。
- SAM 2論文D.2.2は、配布モデルの学習データと、8フレームから16フレームへ延長する追加学習を説明している。specの当該背景と整合する。[SAM 2論文 D.2.2](https://arxiv.org/html/2408.00714v2)

## 今回見えた方向性・次アクション候補

1. 補正クリック経路のAPI互換とIoU監督を、段階0の実装範囲へ加える。
2. 出力一致の条件、全重みの保存・復元、activation checkpointing、時間方向の勾配を段階1の確認へ加える。
3. 共通の学習量・乱数・pilot・lossの規約を固定し、H1とstateの影響について解釈を修正する。
4. 全軌跡V3の評価済み結果を参照する。

以上はspecへの反映候補。レビュー対象spec・プロジェクトREADME・TODO・外部実装コードは変更していない。実装開始承認も今回のレビューからは推定しない。

## 関連ファイル

- [短区間学習のbrainstorm](2026-10-26-temporal-mamba-short-clip-training.md)
- [V3 spec](../../../lab/projects/sam2-mamba-motion-tracking/specs/2026-10-18-temporal-mamba-v3-mose-adapter-spec.md)
- [V3実験ログ](../../../lab/projects/sam2-mamba-motion-tracking/experiments/2026-10-18-temporal-mamba-v3-mose-adapter.md)
- [10/23 MTG議事録](../../../lab/projects/sam2-mamba-motion-tracking/meetings/2026-10-23-mtg.md)
