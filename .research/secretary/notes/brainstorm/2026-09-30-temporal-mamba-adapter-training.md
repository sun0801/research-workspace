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
