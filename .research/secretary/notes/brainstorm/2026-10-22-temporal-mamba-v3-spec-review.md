---
date: 2026-10-22
project: sam2-mamba-motion-tracking
source_todo: null
topic: V3 MOSE adapter specの再レビュー（A4000・checkpointing・val）
status: exploratory
tags: [brainstorm, research, spec-review, temporal-mamba, mose]
---

# V3 MOSE adapter specの再レビュー

## 結論

**F0に対する追加価値と、学習済みadapterのstate carryへの依存を調べる探索実験として妥当。ただし、本学習の前に、メモリ確認の順序・checkpointingの検証・数値一致の合格条件を具体化したい。**

10/18のレビューで指摘された共通forward、凍結とevalの区別、非ゼロ残差での検証、resetの解釈、比較条件の整合性は、今回読んだspecに反映されている。同じ問題を未修正として再指摘する必要はない。

今回の追加懸念の中心は、10/22に追加されたA4000（16GB）への移行とactivation checkpointingである。V3という構造を棄却する根拠ではない。

本メモはレビューであり、spec改訂や実装開始承認ではない。対象spec・README・TODO・外部実装は変更していない。GPU実行は行っておらず、数値は既存の実験ログに記載された結果である。

## 読み込んだ文脈

- [対象spec](../../../lab/projects/sam2-mamba-motion-tracking/specs/2026-10-18-temporal-mamba-v3-mose-adapter-spec.md)：10/22の追加を含む作業中のファイル。git上で既存の変更があることを確認した。
- [プロジェクトREADME](../../../lab/projects/sam2-mamba-motion-tracking/README.md)。
- [直近MTG（10/14）](../../../lab/projects/sam2-mamba-motion-tracking/meetings/2026-10-14-mtg.md)：V3から始め、難しければ他案へ移る方針。
- [前回のレビュー（10/18）](2026-10-18-temporal-mamba-v3-spec-review.md)。
- [実験ログ](../../../lab/projects/sam2-mamba-motion-tracking/experiments/2026-10-18-temporal-mamba-v3-mose-adapter.md)：段階0a、V1 pilot、V3のメモリ実測、GPU環境変化。
- SAM2 repoの `sam2/modeling/temporal_adapters.py`、`training/mose_adapter_train.py` を必要箇所だけ読み取り。checkpointingの仕様確認には、実験ログに記載されたtorch 2.10系の公式資料を使用した。
- 日付はclockで2026-10-22（日本時間）と確認。日次TODOの一覧には10/22のファイルがなく、本文の追加確認は実行環境のエラーで完了しなかった。TODOを根拠とする判断はしていない。

## 妥当な点

1. **問いと比較対象が対応する。** H1はV3−F0、H2はV3−V3-reset、H3は共通レシピでのV3−V1として分かれている。
2. **初期化と学習経路の対策がある。** α=1・W_out=0でF0を再現し、その後にMamba内部へ勾配が届くことを確認する。非ゼロ残差での学習・推論一致も確認する。
3. **凍結の定義が適切。** SAM2の重みを固定しevalを保ちながら、adapterからdecoder等を通る勾配経路を残す。画像encoderだけのno_gradと区別している。
4. **比較の条件が概ね揃っている。** 同じF0、更新数N、軌跡順、augmentation、学習GPU、評価GPUを使う。pilotの重みを引き継がず、段削減時には別条件名にする。
5. **主張の限界が明記されている。** tuningの再利用、単一seed、reset時の分布変化、V1/V3間の複数の構造差を認識している。動画単位のpaired bootstrapも、動画内の対象を独立標本として数えることを避ける設計になっている。
6. **学習中valの用途を限定している。** 最終stepを評価対象とし、valからcheckpoint選択や早期終了を行わない。探索中の経過確認として妥当。ただし、valを見て設計やLRを変えて再実行する場合も探索であり、独立評価にはならない。

## 修正候補1：メモリ確認をV3のLR pilotより先に置く

対象：実施手順の段階0b、段階1。

現在は「0bでV1/V3のLR pilot → 1でメモリ実測と段削減」の順である。一方、実験ログには、checkpointingなしの3段V3が最短9フレームでも学習ピーク20.9GiBとある。A4000へ移行した現在、checkpointingを付けても収まらない場合は、0bで止まり、段階1の退避規則に到達できない。

**提案する順序：checkpointingの正しさ確認 → メモリ予備計測と段構成決定 → 決定した構成でLR pilot → 採用LRで速度を確認してN固定 → 本学習。**

- 予備計測でもforward・backward・optimizer更新を含める。
- 14.5GiB超過に加え、実際のOOMも段削減の条件とする。
- 短・典型・最長の軌跡で確認する。更新後の状態でも確認すると、初回更新だけの見積りを避けられる。
- 3段から2段・1段へ変更した場合は、変更後の構成でLR pilotを行う。別構成のpilot合格を流用しない。

checkpointingで16GBに収まるかは未実測であり、本レビューでは断定しない。

## 修正候補2：checkpointingでstateと時間方向の勾配が保たれることを明記する

対象：実験・実装内容6のactivation checkpointing。

loss・勾配・更新後の重みをオン/オフで照合する方針はよい。ただし、初期のW_out=0ではMamba内部へのloss勾配がゼロになるため、その条件だけでは時間方向の勾配が壊れていても検出しにくい。

具体化したい条件：

- `use_reentrant=False` を明示する。現行の `CellState` はNamedTupleでconv/SSMのtensorを保持するため、入れ子のtensorを扱う方式が適している。
- checkpointの範囲は、入力と入力stateから出力と次stateを返す `MambaCell` の計算とする。推論cacheや可変の外部stateを参照・更新する処理を巻き込まない。
- 非ゼロのW_out、複数フレーム、TBPTT境界を含め、出力、conv/SSM state、各部のloss勾配、更新後の重みを照合する。
- 単体確認では入力stateにも勾配を持たせ、区間内の過去stateへの勾配がオン/オフで一致し、detach境界では切れることを確認する。
- A4000で3段・TBPTT=8のオフ側がOOMになる場合、MambaCell単体の小さいbatchで時間方向の比較を行い、統合側の確認と組み合わせる。オン/オフの比較が可能な検証条件を先に用意する。

PyTorch公式は、再計算時の関数動作がforwardと異なる場合に勾配が誤る可能性を説明しており、non-reentrant方式を推奨している。reentrant方式は入れ子構造内のtensorをautograd参加として扱わない。[PyTorch 2.10 checkpoint公式資料](https://docs.pytorch.org/docs/2.10/checkpoint.html)

なお、1歩ごとのcheckpointingでも、次の時刻の計算に必要な入力state等は残る。SSM state自体の保持まで消えるわけではないため、削減量は実測で判断する。

## 修正候補3：「FP32で一致」の意味と合格基準を具体化する

対象：段階0a'とcheckpointingの正しさ確認。

specの段階0a'は「FP32・deterministicで照合」「FP32で一致」とする。一方、実験ログには以下が記録されている。

- FP32・高速化なし同士でも勾配の最大相対差は1.2e-4。
- encoderのまとめ計算を含めると、1軌跡目のlogit差5.0e-5、loss差3.0e-8、勾配の最大相対差4.0e-2。
- bf16では高速化なし同士でも勾配の最大相対差8.6。

これだけで実装の誤りとは言えない。バッチ計算と個別計算は、FP32でもbit単位の一致が保証されない。[PyTorch 2.10 Numerical accuracy](https://docs.pytorch.org/docs/2.10/notes/numerical_accuracy.html#batched-computations-or-slice-computations)

ただし、**仕様上の合格と実測の判定を一致させる必要がある。**

- tensorごとの絶対誤差と相対誤差、層ごとのnorm比、更新後の重み差を記録する。
- ほぼゼロの勾配に対する最大相対差だけで判定しない。
- 小さい単体計算では決定的な条件を使い、統合計算では非決定性を含む同条件の反復との差も確認する。
- まとめ計算による丸め誤差と、同条件でも生じる非決定性は別の要因として扱う。
- 合格の許容範囲は比較を受け入れる前に固定する。既存ログの最大相対差だけから、新たな合格閾値を捏造しない。

## 追加で明記するとよい点

### 共通LRの採用規則

V1 pilotは1e-4と3e-4で学習が進み、1e-3は不安定だったと記録されている。V3は未実施である。今回の共通レシピ比較に必要なのは、両構造で内部学習が進み、安定する共通LRを選ぶことである。

「V1/V3とも合格する候補の中からどの規則で選ぶか」「共通の合格LRがなければどう扱うか」、pilotの更新数、本学習のwarmup更新数を、実行前に固定したい。共通LRが得られなければ、不安定なままH3を比較せず、LRまたは比較設計を見直す判断候補とする。

### 位置固定のstateの解釈

各マスのstateは物体の移動に自動追従しない。この懸念はspecに既に記載されており、修正漏れではない。V3が不改善でも「Mamba全般が無効」とはせず、固定座標のstate、学習量、SAM2凍結条件を候補要因として残す。

### 今回は必須にしなくてよい追加実験

- 学習時から毎フレームresetする同構造の対照：時間記憶の追加価値を強く主張する段階で有用。現specのH2は依存の診断に限定されているため、今回の探索の必須条件にはしない。
- 独立holdoutと複数seed：本格的な優越性・再現性の主張に必要となるが、今回の探索目的を満たすために直ちに追加する必要はない。

## 次アクション候補・Specへの反映候補

1. メモリ確認と段構成決定をV3のLR pilotより前へ移す。
2. checkpointingの非ゼロ残差・state・時間方向勾配の比較条件を追記する。
3. 数値一致の判定と既存実測の関係を明文化する。
4. 最終構成、共通LR、N、warmup、使用軌跡リストを本学習前に固定する。

これらは提案であり、TODOには追加していない。既存specへはまだ反映していない。

## 未解決の問い

- checkpointing付き3段V3は、A4000で最長軌跡まで14.5GiB以内に収まるか。
- 最終的に採用する段構成で、V1と共通の安定したLRが得られるか。
- A4000の速度で8時間に収まるNは、学習の進行を確認するのに十分か。
- 新たなcheckpointing検証の合格範囲をどう固定するか。
