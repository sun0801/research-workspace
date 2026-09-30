---
date: 2026-09-30
project: sam2-mamba-motion-tracking
source_todo: null
topic: temporal-mamba-adapter-training
status: exploratory
tags: [brainstorm, research, temporal-mamba, sam2, training]
---

# Temporal Mamba adapterを学習して影響を確かめる案

## 読み込んだ文脈

- 2026-09-25 MTGでは、SAM2内部を置換せずtemporal Mambaを追加し、まず接続成立性を確認する方針になった。
- 承認済みspec [`2026-09-27-temporal-mamba-decoder-minimal-integration-spec.md`](../../lab/projects/sam2-mamba-motion-tracking/specs/2026-09-27-temporal-mamba-decoder-minimal-integration-spec.md) は、B0/B1/Pの推論smokeを対象にし、学習済みadapterの有効性は対象外として次段階へ分離している。
- 1系列の実験では、B0/B1の16フレーム出力が完全一致し、Pで1203回state更新・非ゼロ残差を確認した。これは接続の確認であり、精度改善の結果ではない。
- 今の挿入位置は、SAM2 memory attention後の人物別`pix_feat`からdecoderへ渡す直前。ここでのtemporal Mambaは既存の人物別memory/ID routingの後段を改善する候補であり、ID routing自体を直す構成ではない。
- SAM2 forkにはmask教師を使う動画学習経路（`training/model/sam2.py`, `training/loss_fns.py`）がある。一方、DanceTrackの`gt.txt`はbbox・IDを含むMOT注釈で、mask annotationではない。
- 現adapterの`step()`は`@torch.no_grad()`かつ`InferenceParams`の推論cacheを使う。現状のままでは学習グラフを作れず、学習用の因果state更新経路を別に設計する必要がある。

## 相談の出発点

未学習のMamba残差を接続した段階から進めて、学習によってdecoder入力に加える時間情報がSAM2の出力へ有効な影響を与えるかを検証したい。

## 問い

1. 学習の目的を、既存SAM2の人物別routing後にマスクを改善することとするか、routing前の共有画像特徴を補強してID誤対応への耐性を狙うこととするか。
2. DanceTrackにpixel mask GTがない条件で、adapterの学習信号をどのデータ・lossから得るか。
3. 学習済みadapterの効果と、Mamba stateを時間方向に持ち越す効果をどう分離するか。

## 仮説候補

- H1: 人物別`pix_feat`を入力する小さなtemporal adapterをmask教師で学習すると、SAM2が既に対象としてroutingした人物のmask品質またはmask由来bboxが改善する。
- H2: 学習済み重みを固定しstate carryだけを切ると効果が落ちるなら、改善に時間履歴が寄与した可能性がある。
- H3: 学習signalがmask品質に限られる場合、ID switchそのものの改善は期待できない。routing前共有特徴へ置く案とは別の研究仮説として比較する必要がある。

## アイデア候補

### A. mask教師のある動画データでadapterを学習（第一候補）

- SAM2既存動画学習pipelineを土台にする。
- base SAM2をfreezeし、Temporal Mamba adapterのみ学習する最小条件から始める。損失が通るか確認後に必要ならdecoder側の学習範囲を再検討する。
- 動画clipの先頭だけにbox/point promptを与え、後続フレームにはGT promptを入れずにlossを計算する。推論時の一度だけの初期prompt条件へ寄せる。
- 全フレームのmask logitsに既存のfocal + dice + IoU lossを適用する。
- まず1 sequence clipでloss・gradient・state carryの学習sanityを確認し、その後train/validation videoを分離して学習する。
- mask annotationがある学習データのvalidationではmask IoU/J&F等、DanceTrackへ転移した試行ではGT box由来のbbox IoU・中心誤差・track coverage等を分けて報告する。

### B. DanceTrackのbox-only弱教師で学習

- predicted maskからsoft bounding boxやbox内外の制約を作る案。
- mask内の形状・境界は教師されず、loss設計次第で矩形化・面積バイアスを起こす。mask教師学習とは別条件として扱い、採用前に学習目的をspecで固定する。

### C. SAM2 baselineのpseudo-maskを使う

- baselineの出力をteacherとしてdistillationする案。
- baseline出力の再現・平滑化は学べるが、GT品質の改善を保証しない。性能改善を示す主学習signalには弱い。

## 学習経路で必要な設計

- 現推論adapterの`@torch.no_grad()`・`InferenceParams` cacheは学習に流用しない。
- 時系列clipをforwardし、フレーム間stateに勾配を保持した因果Mamba unrollを作る。TBPTTを使う場合はdetach境界を固定・記録する。
- SAM2 training loopのconditioning frame処理順はランダム初期条件フレームを先に処理する場合がある。初回は先頭1フレームのみをconditioningにして、以降を時間順に処理する設定に制限する。
- training pathは`obj_id`/単一target routingを明示し、推論smokeの単一人物state resetと意味を揃える。
- 初期alphaを厳密な0にすると、alpha以外のadapter重みへの初期勾配が途切れる可能性がある。alpha初期値、projection初期化、warm-up方針はgradient確認を踏まえて決める。
- SAM2 checkpointの再ロード後にadapter weightsを明示的に保存・復元し、inference adapterとtraining adapterの演算・state parityを確認する。

## 比較・評価軸

| 条件 | 目的 |
|---|---|
| B0: base SAM2 | adapterなしの基準 |
| B1: adapterあり、alpha=0 | 出力parity control |
| B2: 学習済みadapter、state carry | 学習済み提案条件 |
| B3: B2と同じadapter weights、各frameでstate reset | 学習済みfeature変換と時間state持ち越しを分ける診断 |

- 同じSAM2 checkpoint、初期prompt、frame範囲、postprocessing、対象ID、seedで比較する。
- mask GTを持つvalidationではmask品質を主指標にする。
- DanceTrackはbox-onlyなので、box指標とcoverageを使い、mask精度を測ったかのように扱わない。
- ID routing前の特徴を使っていない条件からID switch解消を結論しない。
- まず少数のvalidation sequenceで系列別に確認し、1〜3本の結果は探索的な初期signalと位置づける。

## 今回見えた方向性

現挿入位置の仮説を保つなら、mask教師付き動画データでadapterだけを学習し、B0/B1/B2/B3を比較するのが最も解釈しやすい。現状の推論smoke実装は学習不可なので、adapterの微分可能なcausal training pathとSAM2Trainへの接続が独立した実装課題になる。

この設計で答えられる問いは「既存のobject routing後に、temporal adapterがその対象maskを改善するか」。SAM2のID誤対応を直接改善する問いを優先する場合は、共有image embeddingへの挿入位置を別案として比較し、その学習・評価specを分ける。

## 次アクション候補

1. 利用可能なmask教師付き動画データと、SAM2 training config/weightの使用可否を確認する。
2. 現挿入位置で進めるか、routing前共有image embedding案も学習比較に含めるか決める。
3. training graphの1 clip sanity（loss backward、adapter parameter gradient、state carry/reset parity）を設計する。
4. train/validation sequence分割、初期prompt、学習clip長、loss、checkpoint選択、B0〜B3の評価protocolをspec化する。

## Spec化候補

学習可能な因果adapterの実装と、mask教師付き動画での初期学習・validationを対象にした別specが候補。データの利用可否、主目的（mask品質かrouting耐性か）、validation指標が決まるまでspecには保存しない。

## 未解決の問い

- SAM2用のmask付き動画データをローカルで利用できるか。利用規約とtrain/validation分割はどうなっているか。
- DanceTrack box supervisionだけで学習する場合、bbox評価に対する弱教師lossをどう正当化・検証するか。
- freeze SAM2 + adapter-onlyでgradientと効果が得られるか。
- 人物別`pix_feat`上のstateful MambaでID switch耐性まで研究目的にできるか。共有特徴案との切り分けが必要ではないか。
- train-time stateful forwardと既存推論cache pathの重み共有・数値 parityをどう確保するか。

## 関連ファイル

- `.research/lab/projects/sam2-mamba-motion-tracking/meetings/2026-09-25-mtg.md`
- `.research/secretary/notes/brainstorm/2026-09-27-temporal-mamba-decoder-minimal.md`
- `.research/secretary/notes/brainstorm/2026-09-27-temporal-mamba-id-dependency-discussion.md`
- `.research/lab/projects/sam2-mamba-motion-tracking/specs/2026-09-27-temporal-mamba-decoder-minimal-integration-spec.md`
- `.research/lab/projects/sam2-mamba-motion-tracking/experiments/2026-09-28-temporal-mamba-decoder-minimal-smoke.md`

---

## 追記 08:35 MOSEv1 / MOSEv2の選択

### 問いと判断

現段階の問いは「SAM2の人物別memory処理後に置いたtemporal Mamba adapterを、mask教師で学習するとマスク品質が改善するか」。初期学習とB0/B1/B2/B3の切り分けには **MOSEv1を第一候補**とし、学習経路と効果を確認できた後に **MOSEv2の新規動画で難条件を評価**する。これは研究目的、データ容量、SAM2公式学習例との整合性に基づく提案であり、採用済みの実験specではない。

| 観点 | MOSEv1 | MOSEv2 |
|---|---|---|
| 規模 | 2,149動画、36カテゴリ、431,725 mask | 5,024動画、200カテゴリ、701,976 mask |
| 公式Hugging Faceの配布総容量 | 約26 GB | 約84.8 GB |
| SAM2公式fine-tuning例 | MOSE向けconfigとsample validation splitがある | v2専用の公式例は今回確認できていない |
| 課題 | 遮蔽、混雑、消失・再出現 | v1の課題に加えて悪天候、低照度、複数ショット等 |

MOSEv2はMOSEv1の2,149動画を含む。よってv1 trainで学習後にv2を評価する場合、v2全体を独立な未知データとは呼べない。v2の追加動画から、学習動画と重複しない評価集合を特定する必要がある。版間の発表値やデータセット全体の難度差を、現在のSAM2.1 Smallと単一人物・box prompt条件の期待スコアへ直接転用しない。

両版の公開validationには対象指定用の先頭フレームのmaskしかなく、ローカルで全フレームのJ/Fを計算するには、trainの動画から**動画単位**でmask付きholdoutを確保する。公式validationでの正式評価は評価サーバー経由。MOSEv2の公式サイトはv2での評価を推奨し、v1の評価サーバーをlegacy扱いとしている。

### 次の設計課題

1. v1 trainから学習用とmask付きholdoutを動画単位で固定する。SAM2公式のsample validation listの利用可否を確認する。
2. 単一人物・初回box promptという現smoke条件で、対象IDの選定と未注釈フレームの扱いを固定する。
3. v1で学習が成立したらv2追加動画から難条件別の評価候補を選び、v1との動画重複を除外する。
4. データ取得・学習・評価実行には別の実験specと開始承認を用意する。今回の比較ではデータは取得していない。

### 一次資料

- MOSE公式サイト: https://mose.video/
- MOSE公式リポジトリ: https://github.com/henghuiding/MOSE-api
- MOSEv2論文（v1動画の継承、規模・難度）: https://arxiv.org/html/2508.05630v1
- MOSEv1配布: https://huggingface.co/datasets/FudanCVL/MOSE
- MOSEv2配布: https://huggingface.co/datasets/FudanCVL/MOSEv2
- SAM2公式学習ガイド: https://github.com/facebookresearch/sam2/blob/main/training/README.md

---

## 追記 09:06 MOSEv1取得状態の確認

- 取得先: `/mnt/HDD10TB-2/aburatani/dataset/MOSE-v1-data/MOSE_release.zip`。
- ZIP実体は26,014,033,719バイト。SHA-256は`027b1608c73847f5068112623ce20778cc5067f20c2e81c11f3489447f888585`で、FudanCVL/MOSEのGit LFS参照に記載された値と一致。
- ZIPには`MOSE_release/train.tar.gz`、`valid.tar.gz`、`meta_train.json`、`meta_valid.json`、`SHA256SUMS`が含まれる。`train.tar.gz`内部は`train/JPEGImages/`と`train/Annotations/`を含む。
- 2026-09-30 09:06 JST時点ではZIPのみで、train/validは未展開。取得は完了したが学習入力としては未準備。公開validの正解マスクは先頭フレームのみなので、ローカルの全フレーム評価にはtrainから動画単位のholdoutが必要。

---

## 追記 09:15 MOSEv1 train展開完了と次段階

- `MOSE_release/train/JPEGImages/`と`train/Annotations/`は各1,507系列、画像・マスクは各93,873ファイル。全系列でフレーム名が1対1に対応し、空系列・不一致は0。展開プロセスは終了した。公開`valid/`は未展開。
- SAM2 fork内の`training/assets/MOSE_sample_train_list.txt`は1,246系列、`MOSE_sample_val_list.txt`は200系列。重複0、両リストの全系列が展開済みtrainに存在。残る61系列は両リストに含まれないため、初期比較では使わず、分割を固定する候補とする。
- SAM2公式MOSE fine-tuning configはBase+、1024px・8フレーム・最大3物体で、学習時のpoint/box promptや途中修正フレームをランダムに使う。一方、今回の推論smokeはSAM2.1 Small・単一人物・初回box promptのみ。公式configをそのまま学習条件とせず、データローダーと分割を参照し、モデル・prompt・時間順序・state管理を別specで固定する。
- 2026-09-30 09:15 JST時点のGPUはRTX PRO 4500 Blackwell 32GBとRTX A4000 16GB。まず1 clipのforward/backwardとVRAMを測る設計が必要。GPU状態は時点情報。

### 次の学習specに入れる骨子

1. 問い: SAM2.1 Smallを固定し、学習済みtemporal Mamba adapterのstate carryがmask品質を改善するか。
2. データ: MOSEv1 trainの公式1,246系列を学習候補、200系列を動画単位のローカルholdout候補にする。初期smokeは学習側の1 clip。
3. 条件: B0（SAM2）、B1（adapter alpha=0）、B2（学習済みadapter・state carry）、B3（B2と同じ重み・毎フレームreset）。単一target、初回GT maskから導いたbox prompt、その後GT補正なしを候補とする。
4. 実装前に決めること: 学習時の微分可能なMamba state経路、損失、clip長・detach境界、alpha初期化、SAM2凍結範囲、checkpoint形式、推論経路との一致検証、評価指標と合否基準。
5. 最初の検証: 1 clipでGT読み込み、prompt生成、finite loss、adapter勾配、state carry/reset差、VRAMを確認。その後にholdoutでJ/F等を比較する。

上記は計画候補であり、学習実装・実験開始の承認済みspecではない。

---

## 追記 09:20 学習範囲の方針修正

ユーザーはSAM2公式のMOSE追加学習を土台にモデル全体を更新する想定だった。前節までの「SAM2を固定してadapterのみ学習」は実施可能な診断案だが、主案として固定した記述は早計だった。以後、**SAM2.1 Smallを事前学習checkpointからMOSEで追加学習し、Mambaあり／なしを同条件で比較する案を主案**として検討する。正式な学習範囲は新しいspecで決める。

### 可能な学習範囲と問い

| 条件 | 更新パラメータ | 答えられる問い |
|---|---|---|
| P0 | なし | 事前学習済みSAM2の基準 |
| F0 | SAM2全体 | MOSEへの追加学習だけで得られる改善 |
| F1 | SAM2全体＋temporal Mamba adapter | 同じMOSE追加学習条件でMambaを加えた改善 |
| F1-reset | F1と同一重み、推論時に毎フレームstate reset | 時間stateの寄与 |
| A（任意診断） | adapterのみ、SAM2固定 | 既存SAM2を保持したままadapter単独で効果が出るか |

F0とF1は同一のSAM2.1 Small初期checkpoint、MOSE動画分割、prompt、loss、学習予算、評価条件を使う。P0との比較だけではMOSE追加学習の効果とMambaの効果を分離できない。A条件は低コストな成立性確認として残せるが、主張に必要な比較対象を置き換えない。

SAM2公式MOSE設定はBase+モデル全体を学習する構成で、画像encoderにも学習率が設定されている。今回のSmall・単一人物・初回box prompt条件へは調整が必要。また、現`TemporalMambaAdapter.step()`は`@torch.no_grad()`と推論cacheを使うため、F1でもAでもそのままではadapterへ勾配が流れない。学習時の微分可能なstate更新、videoごとのreset、時間順処理とdetach方針、checkpoint保存を先に設計する。SAM2公式の途中prompt補正が今回の推論条件と異なる点も揃える。

現サーバーの32GB GPUでF0/F1の必要VRAMは未計測。SAM2公式のBase+・8 GPU設定を直接実行せず、Small・1 clipでforward/backwardとpeak VRAMを測る手順をspecへ入れる。全体学習が収まらない場合の縮小条件は、結果の比較可能性を保って事前に決める。

関連一次資料: https://github.com/facebookresearch/sam2/blob/main/training/README.md 、https://docs.pytorch.org/tutorials/beginner/transfer_learning_tutorial.html

---

## 追記 09:23 全体追加学習とadapter単独学習の比較

| 学習範囲 | 利点 | 限界 |
|---|---|---|
| SAM2固定・adapterのみ更新 | 更新パラメータとoptimizer状態が少なく、SAM2の元の重みを保持できる。固定SAM2に追加した経路が単独で機能するかを見やすい。 | 既存decoderが新しい残差を活用するようには更新されない。現adapterは全空間を平均した1 tokenを全位置にbroadcastする小さな経路なので、効果が出ない場合もMamba自体の無効性を意味しない。decoder側の逆伝播と学習可能なMamba state経路は依然必要。 |
| SAM2全体＋adapterを更新 | SAM2のmemory/decoderが新しい時間特徴へ適応でき、マスク品質改善の余地が大きい。SAM2公式の追加学習の枠組みに近い。 | 計算・VRAM・checkpoint管理の負担が大きい。MOSE適応だけでも性能が変わるため、同条件でSAM2のみを全体追加学習した対照が必須。過学習や元checkpointの能力変化にも注意。 |

**推奨:** 研究上の主比較は、同じ事前学習checkpoint・データ分割・prompt・学習予算による`F0: SAM2全体追加学習`対`F1: SAM2全体＋Mamba追加学習`。F1と同じ重みでstateだけresetする評価も入れ、時間stateの寄与を確認する。adapterのみの学習は、必要なら1 clipの学習経路確認や低コスト診断に使う。初期adapter単独で改善が出なくてもF1案を棄却しない。

32GB GPUで全体追加学習が成立するかは未測定。specに1 clipのforward/backwardとpeak VRAM測定を入れ、収まらない場合はSAM2の一部のみを更新する同条件の対照を設計し直す。SAM2公式のBase+・8 GPU設定の結果をSmall・単一人物条件へ直接移さない。

一次資料: https://github.com/facebookresearch/sam2/blob/main/training/README.md 、https://docs.pytorch.org/tutorials/beginner/transfer_learning_tutorial.html

---

## 追記 09:32 学習spec前に固定する条件案

ユーザーは `F0: SAM2.1 Small全体をMOSEで追加学習` と `F1: 同じ条件でSAM2.1 Small＋temporal Mamba adapterを追加学習` を主比較とする方向に同意した。以下はspec化のための**推奨条件案**であり、実装・実験開始の承認ではない。

| 論点 | 推奨する固定条件 |
|---|---|
| 対象とprompt | まずMOSEv1の全カテゴリを対象に、1 clipにつき1物体。対象が見える最初の注釈フレームのGT maskからboxを1回生成し、その後はGT prompt・途中補正なし。人物への転移は別評価として扱う。 |
| データ分割 | 公式SAM2のsample train 1,246動画を学習、sample val 200動画を今回の追加学習からのholdout。リスト外61動画は初期比較に入れない。動画単位で分離する。評価は初回フレームに対象maskがある物体を1物体ずつ独立に走らせ、毎回stateをresetする。 |
| 比較条件 | P0（追加学習前）、F0（SAM2のみ全体追加学習）、F1（SAM2＋adapter全体追加学習）、F1-reset（F1重みのまま推論時だけMamba stateを毎フレームreset）。F0/F1は同checkpoint、split、対象サンプリング、prompt、loss、更新step数、checkpoint選択規則、評価条件を揃える。 |
| 評価と判定 | 主指標は動画・対象ごとのJ&FとF1−F0の差。JとF、失踪・再出現区間、F1−F1-resetも報告する。単一runだけで一般化や時間stateの因果効果を断定しない。holdoutの反復利用と元checkpointのMOSE学習歴を確認し、独立評価の要否をspecへ記す。 |
| 資源制約 | 32GB GPU上でSmall・1 clipのF0/F1 forward/backwardとpeak VRAMを実測してから学習長を確定する。収まらない場合は解像度、clip長、checkpointing、更新範囲を事前規則で調整し、F0/F1に同じ変更を適用する。全体学習を断念する場合は比較名も変更する。 |

spec内で解決する技術項目: 公式`SAM2Train`のランダムなpoint/box・途中補正・複数初期conditioning frame・逆順処理を上記protocolへ揃える。現adapterの`@torch.no_grad()`と推論専用cacheを学習用の微分可能な時間展開へ分ける。`SAM2Train.track_step`からobject IDが現adapterへ渡らない点を解決し、対象・video・clipごとのresetを保証する。学習clip内のBPTT/detach境界と、alpha初期値がadapter勾配を遮断しないことを検証する。初回boxのみで公式lossが成立するかを1 clipで確認する。

外部SAM2実装リポジトリの変更・学習実行は、別途spec承認と開始承認後に行う。
