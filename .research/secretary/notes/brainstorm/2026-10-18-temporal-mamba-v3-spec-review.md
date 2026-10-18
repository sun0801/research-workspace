---
date: 2026-10-18
project: sam2-mamba-motion-tracking
source_todo: null
topic: V3 MOSE adapter specの妥当性レビュー
status: exploratory
tags: [brainstorm, research, spec-review, temporal-mamba, mose]
---

# V3 MOSE adapter specの妥当性レビュー

## 結論

**F0を固定してV3の追加価値を調べる探索実験として、方向性は妥当。ただし、現状のまま本学習・結果判定へ進めるには、正しさの検証と結果の解釈に修正が必要。**

特に、既存V1の学習・推論で出力射影が一致していないこと、凍結とeval/no_gradが区別されていないこと、reset比較から時間情報の有効性を断定していることが重要。V3の構造そのものを棄却する根拠はない。

これは分析メモであり、承認済みspecの改訂や実装開始承認ではない。spec、README、TODO、外部repoは変更していない。GPU学習・推論・性能計測は実施しておらず、実装に関する所見は静的読解、メモリ量は算術見積りである。

## 読み込んだ文脈と根拠

- 対象spec: [2026-10-18-temporal-mamba-v3-mose-adapter-spec.md](../../../lab/projects/sam2-mamba-motion-tracking/specs/2026-10-18-temporal-mamba-v3-mose-adapter-spec.md)。レビュー時SHA-256: `17958ecc001a2c1317ae065de34f105d0fb64a60c2d469adfc97e73175cde52f`。
- プロジェクトREADME、10/14 MTG議事録、10/14 TODO。本日10/18のTODOファイルは未作成。
- [統合方法のbrainstorm](2026-10-18-temporal-mamba-integration-variants.md)。固定座標stateの位置ずれは、このメモでも未検証の仮説として認識されている。
- [前回MOSE spec](../../../lab/projects/sam2-mamba-motion-tracking/specs/2026-09-30-temporal-mamba-mose-finetuning-spec.md)、[MOSE実験ログの10/9事後診断](../../../lab/projects/sam2-mamba-motion-tracking/experiments/2026-09-30-mose-temporal-mamba-finetuning.md#2026-10-09-事後診断f1-adapterの学習状況とf0の学習量)。
- SAM2実装repo: `/mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2`。確認時branch `dev`、HEAD `f52a7440314d2db649a3d6b2e44879cb500bc139`、git statusに変更表示なし。
- 既存adapter、`sam2_base.py`、`training/model/sam2.py`、`training/mose_fulltrack.py`、評価・集計コード、MOSE学習configを読み取り。
- 一次資料としてSAM2公式ソース、Mamba公式ソース、PyTorch autograd documentationを確認。詳細は末尾。

## 妥当な点

1. 10/14 MTGの「V3から試す」に沿っている。SAM2全体を再学習する前にF0固定で追加価値を調べる範囲も、短期間の探索として扱いやすい。
2. F0、V1、V3、V3-resetの比較は、追加効果・設計間の差・stateへの依存を調べる基本構成としてよい。
3. 対象ごとのJ&Fを動画内で平均し、動画を単位にpaired bootstrapする考え方は、動画内の対象・frameの依存を無視して独立標本扱いすることを避けられる。
4. 既使用のlockboxを今回使わず、最終stepを固定する方針は、探索範囲を限定するうえでよい。
5. 前回の小さいalpha・adapter LRを踏まえ、初期化とLRを先に検査する意図は適切。
6. 64×64/256ch、128×128/64ch、256×256/32chは、既存SAM2でdecoderへ渡す特徴形状と整合する。ただし128/256段は、FPNの生特徴ではなく`conv_s1/conv_s0`による射影後の特徴である。

## 優先度の高い修正候補

### 1. 学習・推論の一致を非ゼロ残差で検証する

対象: spec 43–48行、106行。

既存`sam2/modeling/temporal_mamba_adapter.py`では、推論`step()`は147–150行でMambaの出力に追加の`self.output_proj`を適用する。一方、学習`training_step()`は270–272行で`_mamba_training_step()`の出力をそのまま残差にしており、`self.output_proj`を通さない。内部の`mamba.out_proj`は253行で適用されているので、これは外側の追加射影の欠落である。

この静的な不一致は、前回ログの「output_projがほぼ更新されない」という観察にも関係する。**少なくとも外側output_projの未更新は、低LRだけでは説明を完結できない。学習forwardで未使用であることも原因候補に加えるべき。** 小さいalphaの原因や過去スコアへの影響量は、この読解だけでは確定しない。

共通経路へまとめるspecの方針はよい。ただしα=0では、どんなadapter出力でもSAM2の出力に影響せず、不一致を検出できない。初期出力射影がゼロの場合も同様である。

追加する検証:

- 同じ重み・入力・初期stateで、αを非ゼロ、残差出力射影も非ゼロにして、勾配あり/なしの共通stepを比較する。
- 初回frameだけでなく、複数frame・TBPTT境界をまたいだ出力とconv/SSM stateを比較する。
- 旧実装との互換試験と、新しい正しいforwardの一致試験を区別する。旧F1のlossをすべて再現することを、新しい共通forwardの合格条件にはしない。
- 既存checkpointを読み込む場合のキー対応とforward変更を記録する。今回V1は再学習するので、旧F1をそのまま新V1として評価する必要はない。

### 2. H2を「stateへの依存」として扱い、不支持を無効果と読まない

対象: spec 30–37行、89–100行。

V3-resetは、carryを前提に学習した同じ重みを、推論時だけ異なる状態分布で動かす介入である。性能低下には、過去情報を失った影響と、学習時と違う状態分布にした影響が含まれる。また、resetするのはMambaのstateであり、SAM2のmemoryは残る。したがって「時間情報のないモデル」との比較ではない。

前回9/30 specは、この比較を「学習済みF1のcarry stateへの依存を調べる診断」「単独では有用な時間情報利用の証拠としない」と明記していた。今回もこの区別を維持するのがよい。

判定の推奨表現:

| 観察 | 言えること |
|---|---|
| H1・H2とも支持 | この評価でV3の追加効果があり、学習済みV3はMamba state carryに依存する。追加の時間記憶の有用性と整合的だが、その機序の分離は未完了 |
| H1のみ支持 | V3の追加効果を確認。Mamba state carryの追加寄与は確認できない |
| H2のみ支持 | V3はcarryに依存するが、F0を上回る実用的な追加価値は確認できない |
| 両方不支持 | 今回の条件・予算・標本では改善を確認できない。学習不足、効果量の小ささ、推定の不確かさも残る |

spec 96行の「効いているのは追加パラメータや空間処理で、時間の記憶ではない」は削るべき。不支持は無効果の証明ではない。

探索の次段階で機序を強く主張するなら、**学習時から毎frame resetする同構造の対照**を追加する。それでもSAM2由来の時間情報は残るので、「Mambaが追加する再帰状態の価値」の比較と呼ぶ。今すぐ追加学習を必須にする代わりに、今回の主張を診断に限定する選択も妥当。

### 3. 凍結・モデルモード・高速化の比較条件を分ける

対象: spec 57–62行、106行、122行。

既存trainerは`model.train()`を使用し、読み込む公式MOSE学習configにはimage encoderの`drop_path_rate: 0.1`、memory attentionの`dropout: 0.1`がある。`requires_grad_(False)`や`no_grad()`だけでは、このランダムな処理は停止しない。画像を1frameずつ計算する場合と8frameまとめる場合では、乱数を使う順序が変わり得るため、同じseedでも差が「bf16誤差だけ」とは限らない。

また、凍結SAM2を通るadapterへの勾配は必要。画像encoderの計算をno_gradにする方針は妥当だが、decoderやadapter依存のmemory経路まで一括してno_gradにすると、必要な勾配を失う。

追記候補:

- 凍結するパラメータ一覧と、train/evalをどのsubmoduleへ適用するかを固定する。固定特徴のまとめ計算を狙うなら、image encoderをevalにする案が扱いやすい。
- `model.train()`を再度呼ぶ箇所でencoderのeval設定が戻らないようにする。
- SAM2上位モジュールの`self.training`はadapter呼び出し分岐にも使われているため、全体evalへの切替だけで学習経路を制御しない。
- 高速化前後の比較は、**同じ新adapter・初期重み・凍結条件・モード・optimizer・乱数条件**で行う。設計変更と高速化を同時に比較してloss不一致の原因を混ぜない。
- deterministicなFP32照合を先に行い、その後bf16の絶対/相対誤差、logit・loss・勾配・更新後重みを確認する。相対1e-3だけの一律判定は、ゼロ近傍の値や再帰誤差を扱いにくい。
- DataLoader化では軌跡index、frame順、augmentationのretry、prompt tensorが維持されることも確認する。

`eval()`と勾配無効化は独立であるという点は[PyTorch公式説明](https://docs.pytorch.org/docs/2.14/notes/autograd.html#evaluation-mode-nn-module-eval)とも一致する。

### 4. LR確認をV1だけで終えず、Mamba内部の学習を確認する

対象: spec 47行、87行、107行。

「出力層ゼロ初期化・α=1」は、初期状態でF0の出力を保つ残差接続として妥当。ただし、どの出力層を指すか、αが固定値か学習可能かを明記する必要がある。

例えば`r = W_out f_theta(x)`、`W_out=0`なら、初回のbackwardでは`theta`へのloss由来勾配がゼロになることは正常。`W_out`の更新後に内部へ勾配が到達することを確認すべきであり、初回のゼロ勾配だけで失敗判定してはいけない。逆に、出力biasなどが動くだけでも残差は育つため、「残差が非ゼロ」だけでMamba内部の学習を保証できない。

追加する合格条件:

- 初期状態の実際のα=1・ゼロ出力射影で、F0と一致する。
- 複数optimizer更新後、各段のMamba、入力正規化、残差射影、段間projectionについて、該当するloss勾配と重み差分を記録する。weight decayだけの変化とは区別する。
- SAM2の凍結パラメータが変化していないことを確認する。
- V3でも短いpilotを通し、V1で採用したLRが有限・安定で内部学習を生むことを確認する。
- 少数の固定軌跡での反復学習と、同一診断入力でのloss比較を使う。異なる軌跡のloss推移だけではLRの良否を判断しない。
- 本比較はpilotの最良重みから継続せず、F0＋新規adapterから再初期化するか、pilotを含む更新数を両条件で明示的にそろえる。

同じLRをV1/V3で使うことは「共通レシピ下の比較」としては妥当だが、両構造の最適性能を公平に比較したことにはならない。H3の解釈もその範囲に限る。

### 5. 学習予算とV3の退避条件を再現可能にする

対象: spec 81行、108–109行、130行。

「同じstep数」と「各run 8時間以内」は、遅い側に合わせて共通step数を事前固定すれば両立する。各runをそれぞれ8時間で止めると学習データ量が変わるため、別の比較になる。

既存trainerでは**1 step = 1 video-object軌跡のoptimizer更新**であり、TBPTTの8frame区間ではない。区間ごとにbackwardして勾配を蓄積し、軌跡の最後に1回だけoptimizer.stepする。LR確認の200 stepも、この定義なら200軌跡分である。

固定すべき項目:

- V3実測から決める共通更新数N、対象軌跡indexの固定リスト、合計frame数、seed。
- 「固定順」は既存のseed付きpermutationを保存した順序とする。未shuffleのファイル順の先頭を使うと部分集合の偏りが増える。
- optimizer、weight decay、Mambaの`A_log`/`D`等の扱い、clip norm、warmup後のschedule、warmupの単位、TBPTT detach対象。
- 速度実測はforwardだけでなく、backward・optimizer state生成を含め、短・典型・長い軌跡を測る。最長1本だけで全体の時間を見積もらない。
- pilot、評価、checkpoint I/Oの時間は8時間の本学習予算と分けて記録する。

256段を外した場合は`V3-64-128`、さらに128段を外した場合は`V3-64-only`のように条件名を分ける。1段では階層間の接続がなくなり、実質的にV2の64×64グリッド案に近い。これを元の3段V3の検証結果として扱わない。

### 6. 集計コードと既存F0結果の再利用条件を変更範囲へ追加する

対象: spec 63行、76行、85–86行、110行。

既存`training/summarize_mose_fulltrack.py:260–267`は、条件名を`P0/F0/F1/F1-reset`、比較を`F1-F0/F1-F1-reset/F0-P0`に固定している。bootstrap関数自体は使えるが、V1/V3/V3-resetを追加するだけではH1〜H3の集計は出ない。**集計entrypointの条件名・比較組・入力パス対応も実装変更範囲に必要。**

また、現在のtuning集計は動画IDの共通部分で比較する。欠落した条件を気づかず小さな集合で比べないよう、125動画・313対象のexpected ID集合、frame coverage、prompt、除外理由の一致を先に検査する。

F0既存結果は、同じcheckpoint、評価対象、prompt、画像前処理、t0除外、J/F実装、動画内平均規則が一致した場合に再利用できる。新コードのadapter無効条件で代表軌跡を再実行し、旧F0との一致を確認することを推奨する。違いがあればF0も同じ評価器で再評価する。

## 設計上の見積り・限界

### stateのメモリはV1と大きく異なる

現行既定の`expand=2, d_state=16, d_conv=4`を継承すると仮定する。SSM stateを現行学習実装と同じFP32にすると、1段のstateサイズは`H × W × (2C) × 16 × 4 bytes`。

| 段 | channels | SSM state FP32 | conv stateをbf16とした場合 |
|---|---:|---:|---:|
| 64×64 | 256 | 128 MiB | 16 MiB |
| 128×128 | 64 | 128 MiB | 16 MiB |
| 256×256 | 32 | 256 MiB | 32 MiB |
| 合計 | — | 512 MiB | 64 MiB |

最新stateだけなら計576 MiB。convがFP32なら合計640 MiB。TBPTT=8で8時刻分のSSM stateだけを数えると4 GiB相当になる。これは総peak VRAMではなく、autogradが保存する中間値、積・指数計算、SAM2、勾配、画像encoderのbatch、allocator等は別である。実際に何を保持するかは実装とcheckpointingにも依存する。

現行`_mamba_training_step()`はFP32のstate積や指数を明示的に作るため、単純な空間batch化で32GBへ必ず収まるとは言えない。逆に、この計算だけでOOMと断定することもできない。段階1の実測は必須で、推論の実測時間も旧V1の「1条件71分」からは保証できない。

### 固定座標のstateは、動く物体に自動追従しない

各マスを独立した時系列にする設計では、frame tの位置(x,y)とframe t+1の同じ位置が同じ物体部位とは限らない。粗い段の広い受容野やmemory-conditioned特徴が助ける可能性はあるが、段間のupscaleだけで位置対応が解決するわけではない。

この懸念はV3を試すことを否定しない。改善しない場合の候補原因として残し、移動量・遮蔽を含む代表動画で、carry/resetの差や残差の位置を確認すると次のV2/V4検討につながる。

### tensor接続の定義を補う

64段の`pix_feat`はMemory Attention後、128/256段は画像由来の射影済み特徴であり、元から同程度に対象条件付けされているわけではない。上位段から対象情報が入る可能性を含めて、設計として説明する。

特に、段間に渡す「Mamba出力」が、Mamba内部出力・ゼロ初期化する最終射影の前後・元特徴との残差和のどれかを明記する。入力正規化の位置、upsample方式、1×1 convのbiasと初期化、各段のstateのdtype、αを固定するか学習するかも指定する。

V3とV1の差には、空間解像度だけでなく、利用する特徴段・パラメータ量・計算量・段間接続も含まれる。H3で勝っても「空間情報を保ったことだけの効果」とは限定できない。

### tuning上の信頼区間の解釈

tuningを探索に使うこと自体は妥当。ただし、F0のcheckpoint選択にも使われ、今後V3等の設計判断にも使う同じ集合である。bootstrapは、固定された重み・条件に対する動画間のばらつきを示し、設計選択や学習seedの不確かさまでは含まない。

spec 100行の「比較はV3に不利な側に偏る」は一般には保証できない。V3もtuningで選ばれたF0を初期値にし、その後の適応で動画ごとの誤差の関係が変わるためである。「同じtuningを使用した探索比較であり、独立評価上の優越性は未確認」とするのが適切。

95% CIの符号に加えて、J&Fの差を0–1スケールか百分率ポイントか明示し、実用的に必要な改善幅と推論時間も併記するとよい。新しいholdoutを今すぐ必須にせず、本格的な研究主張を行う段階で独立評価を計画する。

## 推奨する最小限の修正と進め方

1. 判定表を「追加効果」「carry依存」「未確認」に修正する。今回の結果は探索的と明記する。
2. 共通forwardの非ゼロ残差parity、正確な初期化、凍結範囲とモード、各段の内部学習検査を段階0に追加する。
3. 高速化の比較を同一の新学習条件内で行い、V3の短い学習pilotと実測を通す。
4. 学習開始前にV3の段構成・共通N・sample order・scheduleを実測結果から固定する。V1/V3は新規初期化から同じNで学習する。
5. 集計コードの対応とF0再利用の一致確認を範囲へ加える。resetを学習時から使う対照は、機序を主張したくなった場合の追加候補とする。

**ユーザー判断が必要な論点:** 今回はMTG向けの探索結果を得るところまでにするか、追加のreset学習対照まで含めて時間記憶の効果をより強く切り分けるか。前者なら上の最小修正で十分に有意義な実験になる。

## 一次資料

- [SAM2公式 sam2_base.py](https://github.com/facebookresearch/sam2/blob/main/sam2/modeling/sam2_base.py): image encoderの出力、high-resolution特徴の射影、memory-conditioned特徴とdecoderへの入力を確認。ローカルの変更部分の判断はローカルソースを優先した。
- [Mamba公式 mamba_simple.py](https://github.com/state-spaces/mamba/blob/main/mamba_ssm/modules/mamba_simple.py): conv/SSM stateの形、`d_inner=expand*d_model`、inference cacheのin-place更新、`A_log`/`D`のweight-decay除外指定を確認。
- [PyTorch autograd mechanics](https://docs.pytorch.org/docs/2.14/notes/autograd.html): `requires_grad`、no-grad、evalの違いを確認。参照ページの版は2.14であり、ローカル実行環境の版を示すものではない。
