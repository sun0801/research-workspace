---
date: 2026-10-26
project: sam2-mamba-motion-tracking
source_todo: temporal Mambaの学習を8フレーム程度の短い区間に切り替え、1週間で数値を報告する
topic: temporal-mamba-short-clip-training
status: exploratory
tags: [brainstorm, research, temporal-mamba, sam2, mose, training]
---

# temporal Mambaの短い区間での学習：進め方

相談は2026-10-23に始め、途中でリファクタリング（[spec](../../../lab/projects/sam2-mamba-motion-tracking/specs/2026-10-23-mose-adapter-train-refactoring-spec.md)、R0〜R5完了、SAM2 repo `09a30a7`）を挟んで2026-10-26にまとめた。

## 読み込んだ文脈

- プロジェクトREADME、[10/23 MTG議事録](../../../lab/projects/sam2-mamba-motion-tracking/meetings/2026-10-23-mtg.md)、[10/23 MTG資料](../../../lab/projects/sam2-mamba-motion-tracking/materials/2026-10-23-weekly-progress-mtg-materials.md) 3章
- [V3 spec](../../../lab/projects/sam2-mamba-motion-tracking/specs/2026-10-18-temporal-mamba-v3-mose-adapter-spec.md)、[V3 実験ログ](../../../lab/projects/sam2-mamba-motion-tracking/experiments/2026-10-18-temporal-mamba-v3-mose-adapter.md)、[9/30 MOSE追加学習ログ](../../../lab/projects/sam2-mamba-motion-tracking/experiments/2026-09-30-mose-temporal-mamba-finetuning.md)のデータ分割
- SAM2 repo：`training/mose_adapter_train.py`、`training/model/sam2.py`、`sam2/modeling/sam2_base.py`、`sam2/configs/sam2.1_training/sam2.1_hiera_b+_MOSE_finetune.yaml`、`training/README.md`、`training/assets/MOSE_sample_{train,val}_list.txt`
- SAM 2論文（arXiv 2408.00714）Appendix A・D.2.2

## 相談の出発点

10/23 MTGで、temporal Mambaの学習を軌跡全体のTBPTTから8フレーム程度の短い区間に切り替え、うまくいけば16フレーム以上に延ばす方針になった。どう進めるかを整理する。

## 対象TODO

- temporal Mambaの学習を8フレーム程度の短い区間に切り替え、1週間で数値を報告する（2026-10-23）

## 問い

- 短い区間で何周も学習すれば、V3はvalで伸びるか（全軌跡1周のV1・V3は伸びなかった）。
- SAM2本体のどこまでを学習すれば、Mambaの効果が出るか。

## 確認できた事実

- **8フレームの区間にしても、1フレームあたりの計算は変わらない**（今もTBPTT=8）。速くなるのは、1周のフレームが約1/9になり、同じ時間で更新回数とサンプルの多様性が増えるため。
- **MOSEの分け方はSAM2論文と同じ扱い**。SAM2の2つのリスト（train 1,246・val 200）はどちらもMOSE公式trainから取ったもので、重なりはない。val 200はSAM2論文の「MOSE dev」（trainから選んだ200動画、学習から除外）。MOSE trainの残り61動画はどちらにも入っていない。
- **配布されたSAM 2.1はMOSEで学習していない**（論文 D.2.2「Our released model is trained on SA-V manual + Internal and SA-1B」）。9/30 specの「事前学習にMOSEが含まれるか除外しきれない」は解消。
- MOSE公式validは先頭フレームのマスクしかなく、採点はCodaLab。論文で使う数値はこちらで取る。
- 今の評価条件（1対象ずつ、先頭にbox 1回）は標準の半教師ありVOS（全対象、先頭にGTマスク）と違うので、公表値（README記載のB+ fine-tune後の79.4など）とは比べられない。
- 公式の学習（`SAM2Train`）では、マスクを与えたフレームはデコーダを通らない（`use_mask_input_as_output_without_sam: true`）。V3はデコーダの前に入るので、そのフレームでは使われない（`sam2_base.py` 1116行）。
- 公式のMOSE fine-tuneのプロンプト：条件フレームでGTマスク50%・クリック25%・box 25%。条件フレームは1〜2枚、1〜2フレームに補正クリック7点、補正したフレームも条件フレームにする。
- 公式の設定には `freeze_image_encoder` とプロンプトの設定値がある。Memory Attentionなどの固定、adapter用の学習率、区間の中でのstateの持ち越し、val J&F、Cometは追加が必要。

## 決めたこと

| 項目 | 決定 | 理由 |
|---|---|---|
| 1週間後の報告 | MOSEだけ。DanceTrackは学習が安定してから | 先生の「まずまともに学習できるように」 |
| 名前 | 資料ではtrain / val / test。コードの名前（fit / tuning / lockbox）は変えない | 過去のrunやhashの照合を壊さないため。MOSE公式validは「MOSE公式valid」と書く |
| testの使い方 | 判断はvalとval-25だけで行う。testは候補が固まってから、表に載せる値として使う | testは10/8に一度使用済み。今後のtestの値は探索的な扱い |
| 学習コードの基盤 | SAM2の公式の学習コード（`training/train.py`・`trainer.py`・`SAM2Train`） | 将来の拡張（段階的な学習・複数対象・空間方向）を楽にするため。リファクタリングが終わるまで実験に移れないので、時間をかけてよい |
| 条件 | A: V3・SAM2本体は固定／B: Mambaなし・デコーダだけを学習／C: V3＋デコーダ | Aは学習方法の効果、C−BでMambaの効果。Bは新しい基盤の動作確認も兼ねる |
| V1 | 実験から外す | 今後使わない |
| 1サンプルの対象数 | 1対象 | V3は1対象で12.6 GiB。3対象ではA4000に入らない |
| プロンプト | 種類（マスク・クリック・boxの混ぜ方）は公式のまま。**条件フレームは先頭1枚、途中の補正なし** | 先頭より後の7フレームを純粋な追跡にする。途中でGTが入るとMambaの記憶に頼る動機が弱まる。マスクのフレームでV3が使われない問題を先頭だけにする |
| augmentation | 公式のまま | |

## 比較・評価軸

- 学習できているか：val-25が更新とともに上がり、最終値がstep 0を0.5ポイント以上上回るか
- 効果：valでA−F0、C−Bのpaired bootstrap 95%区間の下限が0より大きいか
- stateの扱い：推論時にcarry／8フレームごとにreset／毎フレームreset

## 実験・実装案

- 学習量：約25,000更新（≒20万フレーム、全軌跡V3の1周と同じ計算量）。V3は約2.7秒/更新で約18時間（公式基盤での実測で見直す）
- 学習率：adapter 3e-4、デコーダ 5e-6（F0と同じ）
- 比べる相手：F0、全軌跡で学習したV3（valでの評価は未実施なので先に回す）
- 16フレームへの延長は、8フレームでval-25が伸びたときだけ。TBPTTは8のまま

## 今回見えた方向性

公式の学習コードに、V3のstateの持ち越しと本体の部分的な固定を足し、8フレーム・1対象・先頭1枚のプロンプトでA・B・Cを学習する。リファクタリングで作った「val J&Fを `evaluate_track` で測る」仕組みを新しい基盤でも使う。

## 次アクション候補

- 移行specを作る（Plan mode相当で提示 → 承認 → 保存）
- 全軌跡V3の最終結果を実験ログに記録し、V3のval（313対象）評価を回す

## Spec化候補

- `specs/2026-10-26-temporal-mamba-short-clip-official-trainer-spec.md`

## 未解決の問い

- 先頭フレームにマスクを与えたとき、V3のstateを先頭で1歩進めるか（評価のboxでは先頭でもV3が動く）
- 公式の学習率スケジュール（cosineで1/10まで、warmupなし）にadapterの3e-4を合わせてよいか。新しい基盤で短いpilotを回すか
- 次回のMTG（10/30ごろ）に出せるのは学習曲線（val-25）までの見込み。ViEWの締切（10/30）とも重なる
- 公式基盤のA（V3固定）と全軌跡のV3の差には、区間の長さのほか、augmentation・プロンプト・サンプルの取り方の違いも入る

## 関連ファイル

- [10/23 MTG議事録](../../../lab/projects/sam2-mamba-motion-tracking/meetings/2026-10-23-mtg.md)
- [V3 spec](../../../lab/projects/sam2-mamba-motion-tracking/specs/2026-10-18-temporal-mamba-v3-mose-adapter-spec.md)
- [リファクタリングspec](../../../lab/projects/sam2-mamba-motion-tracking/specs/2026-10-23-mose-adapter-train-refactoring-spec.md)、[記録](../../../lab/projects/sam2-mamba-motion-tracking/experiments/2026-10-23-mose-adapter-train-refactoring.md)

---

## 追記 2026-10-27

### 決定

- 先頭フレームにGTマスクを与えたときは、公式の動きどおりV3を通さない（stateは次のフレームから0で始まる）。
- 学習率は公式の形（warmupなし、cosineで1/10まで下げる）に合わせる。V3 3e-4 → 3e-5、マスクデコーダ 5e-6 → 5e-7。段階2のpilotで安定を確かめる。

### spec化

- [specs/2026-10-27-temporal-mamba-short-clip-official-trainer-spec.md](../../../lab/projects/sam2-mamba-motion-tracking/specs/2026-10-27-temporal-mamba-short-clip-official-trainer-spec.md) として保存（status: draft）。実装はImplementation Gateの後。
