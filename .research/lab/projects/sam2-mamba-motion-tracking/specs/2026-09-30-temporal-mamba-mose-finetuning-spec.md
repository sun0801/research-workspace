---
project: sam2-mamba-motion-tracking
type: experiment-spec
status: approved
created: 2026-09-30
last_updated: 2026-09-30
---

# MOSEv1によるSAM2.1 Small + temporal Mamba追加学習spec

## 目的

SAM2.1 Hiera SmallをMOSEv1で全体追加学習するとき、temporal Mamba adapterを加えることで、同じ学習条件のSAM2単独モデルより動画物体マスク品質が改善するかを検証する。Mamba stateを保持すること自体の寄与は、学習済み重みのまま推論時にstateを毎フレームresetする条件との比較で調べる。

## 問いと仮説

**問い:** 単一対象・先頭box prompt・後続GT補正なしのVOS条件で、SAM2.1 Small全体とtemporal Mamba adapterをMOSEv1追加学習すると、SAM2.1 Small全体のみの追加学習よりJ&Fが向上するか。

**主仮説:** F1はF0よりlockbox上の平均J&Fが高い。F1-resetとの比較は、学習済みF1が推論時にcarry stateへ依存するかを調べる診断とする。それ単独ではMambaが有用な時間情報を利用した証拠とはしない。

## 固定する前提

- **モデル:** 現行推論smokeと同じSAM2.1 Hiera Small。元checkpointのパスとSHA-256を各run manifestに記録する。
- **データ:** MOSEv1 train内のSAM2公式`MOSE_sample_train_list.txt` 1,246系列を、動画単位・固定seed 123でfit 1,121系列とtuning 125系列に分ける。`MOSE_sample_val_list.txt` 200系列は条件確定後のlockbox評価に使う。公式リスト外の61系列は今回の比較から除外する。
- **対象:** 全カテゴリから1 video-object軌跡ずつ学習する。軌跡はその対象のGT maskが最初に非空となるframeから動画末尾までとする。人物だけの効果は本specの評価対象に含めず、別途扱う。
- **prompt:** 対象maskの外接boxを軌跡の初出frameで1回だけ与える。後続frameにGT mask、point、boxによる補正を与えない。評価でも同じ条件を使う。
- **時間順:** 各video-object軌跡を時系列の正方向で最後まで処理する。Mamba stateとSAM2動画memoryは軌跡開始時だけ初期化し、学習用のTBPTT境界では数値stateをresetしない。
- **主要指標:** 先頭prompt frameを除いたframeのJ&F。JとFも個別に記録する。

SAM2.1の事前学習checkpointがMOSE由来データを含むか、配布情報だけでは完全に除外できない。そのため200系列は「今回の追加学習から分離したローカルlockbox」と呼び、事前学習から完全に未見の汎化評価とは主張しない。fit 1,121系列だけで学習する。tuning 125系列は学習設定の調整とcheckpoint選択にのみ使う。200系列は、F0/F1設定、学習予算、checkpoint選択規則、評価コードを固定した後に一度だけ最終比較へ使う。結果を見て方法を変更した場合、その後の同じ200系列での評価は探索的とし、confirmatoryな最終評価とは呼ばない。

## 比較条件

| ID | 条件 | 用途 |
|---|---|---|
| P0 | 追加学習前のSAM2.1 Small | 元checkpointの基準性能 |
| F0 | 同じ初期checkpointからSAM2全体をMOSEで追加学習 | MOSE適応のみの効果 |
| F1 | 同じ初期checkpointからSAM2全体＋temporal Mamba adapterをMOSEで追加学習 | F0に対するMamba追加効果 |
| F1-reset | F1と同じcheckpoint。各frameの処理前にMamba stateだけをresetし、SAM2動画memoryは通常どおりcarryして推論 | 学習済みF1のMamba state carryへの依存を調べる診断 |

F0/F1はfit/tuning分割、video-object軌跡のサンプル順、画像拡張乱数、prompt生成、loss、初期checkpoint、optimizer設定、最大更新回数、checkpoint候補間隔、tuning選択規則を揃える。対応するrunでは同じseedとデータ順を使う。tuning上で各条件のcheckpointを同じJ&F基準で選ぶ。F1-resetは追加学習を行わず、F1の評価条件だけを変える。

## データと学習protocol

### video-object軌跡 sampling

- 公式SAM2 MOSE dataloaderとaugmentationを基礎に、1対象ずつ動画内の全軌跡を処理するdataset/trainerを作る。対象の初出frameから動画末尾までの画像列と、その対象IDのGT mask列を時系列順で返す。
- 1 sampleは1 video-object軌跡、batch sizeは1。SAM2/Mamba stateはsample開始時に初期化し、動画末尾までcarryする。可変長系列は動画間でpaddingして同一batchに混ぜず、別々に処理する。
- 学習対象maskは各frameのMOSE annotationから選択した対象IDだけを二値化する。画像・mask対応、対象の初出位置、消失・再出現を含む系列を検査する。
- 1024×1024の空間解像度と、時間方向に一貫した幾何変換を基準とする。色変換は公式MOSE設定に沿ってよいが、F0/F1では同一video-objectに同じ乱数列を使う。
- 1,246系列を辞書順に並べ、`numpy.random.default_rng(123).shuffle`後の先頭125系列をtuning、それ以外をfitとする。実際のfit/tuning/lockbox一覧をrun manifestに固定する。
- 学習・評価のvideo-object一覧、対象annotation ID、初出frame、総系列長、処理chunk範囲をmanifestに保存する。

### promptとloss

- SAM2Trainのpoint/mask prompt混合を無効にし、各video-object軌跡の初出frameでGT maskから作るbox promptのみを使う。後続のcorrection click、追加conditioning frame、逆順処理を無効にする。
- configでは`prob_to_use_pt_input_for_train=1.0`、`prob_to_use_box_input_for_train=1.0`、`num_init_cond_frames_for_train=1`、`num_frames_to_correct_for_train=1`、`num_correction_pt_per_frame=0`、`rand_init_cond_frames_for_train=false`、`rand_frames_to_correct_for_train=false`、samplerの`reverse_time_prob=0`を指定する。これにより軌跡の初出frameだけbox promptとなり、SAM2Trainのcorrection処理ループは0回になる。
- GT boxの座標規約、画像resize後の変換、矩形端点の扱いを学習と評価で共通化し、prompt tensorを保存して再現可能にする。
- SAM2公式`MultiStepMultiMasksAndIous` lossを使う。初期weightはMOSE config通り`loss_mask=20`、`loss_dice=1`、`loss_iou=1`、`loss_class=1`、`supervise_all_iou=true`、`iou_use_l1_loss=true`、`pred_obj_scores=true`とし、F0/F1で共通にする。評価GTはlossやprompt生成へ渡さない。
- 公式configのresolution、clip length、augmentation、loss weight、optimizer値から変える項目は新configへ明記する。Base+・8 GPU向けの公式値をSmall・単一GPUの性能期待値として扱わない。

### SAM2とadapterの更新

- F0はimage encoder、memory attention/encoder、prompt encoder、mask decoderを含むSAM2全体を更新する。
- F1もSAM2全体を更新し、adapterのMamba、input LayerNorm、output projection、alphaも更新する。
- F1はSAM2 checkpointをstrict loadした後にadapterを追加する。alpha初期値は既存smokeと同じ0とし、alphaが学習可能であることを確認する。adapter各parameter groupのLRとweight decayはF0/F1共通のSAM2 optimizer設定から明記し、個別LRを設ける場合は予備検証後に固定する。
- adapterの学習用forwardは推論用`InferenceParams` cacheと`@torch.no_grad()`から分離し、video-object軌跡の初出frameでstateを初期化し、動画末尾まで微分可能にcarryする。full BPTTでは全軌跡で勾配を保持する。TBPTTへ切り替える場合も、境界でMamba stateの値は次区間へ渡し、計算graphだけをdetachする。state resetはvideo-object軌跡の境界だけで行う。
- SAM2動画memoryとobject pointerを元の動画処理順どおりcarryする。TBPTT境界では数値memoryを保ったまま計算graphをdetachし、backward後に不要な過去frame出力を破棄する。条件frameとSAM2のmemory選択規則は全区間forwardと一致させ、別video-object間でSAM2/Mamba stateを共有しない。
- 学習モードでは`SAM2Train.track_step`から単一対象のIDをadapterへ渡す。video-object軌跡の途中で対象IDを付け替えない。
- 推論adapterと学習adapterの重み・演算の対応を保つ。複数chunkに分けた学習用stateful forwardと動画全体を順次処理するstreaming推論forwardを比較し、同一演算経路ではFP32の最大絶対差`1e-3`以下、BF16で`1e-2`以下を満たす。detachは数値stateを変えないことも確認する。

## VRAMと学習予算の決定

本学習前に、fit集合から対象propagation長の短・中央値・長系列と最長系列を選び、利用可能な32GB GPUでP0相当のmodel loadとF0/F1の全系列forward/backwardを試す。長さ別peak VRAM、系列処理時間、finite loss、parameter gradientを記録する。特にF1でadapter alpha、output projection、Mamba parameterへ勾配が流れることを確認する。最長系列のfull BPTTが実行可能かを判断する。

先行するMambaTrackers P4aでは、unroll長・TBPTT長を最大384 frameまで検証し、U384T384を完走した。一方で、各unroll開始時にstateをresetしており、track全体state carryやchunkごとのbackwardは検証していない。また、そのモデルとSAM2ではactivation/memory構成が異なるため、報告VRAMを本実験の見積りには流用しない。この先行結果は長いunrollを試す根拠にはなるが、SAM2での動画全体BPTT/TBPTT成立を保証しない。[P4a探索spec](2026-09-17-p4a-unroll-tbptt-hyperparameter-search-spec.md)・[P4a探索結果](../experiments/2026-09-17-p4a-unroll-tbptt-hyperparameter-search.md)

長系列full BPTTがOOMまたは安全なmemory marginを満たさない場合、学習中の時間state horizonを縮めず、F0/F1共通で動画全体state carry + TBPTTへ切り替える。TBPTTではchunkごとにlossをbackwardし、gradientを累積しながら、Mamba stateとSAM2 memoryの数値を次chunkへ渡す。optimizer stepはvideo-object軌跡の最後に1回だけ行う。

TBPTT長は短・中央値・長系列で8、16、32 frameをpilotし、最長fit系列でもfiniteかつVRAMに安全余裕がある最大値を採用する。選択したTBPTT長をF0/F1共通で固定し、データsampleをその長さで独立resetしない。SAM2 activation checkpointingは追加で適用してよい。TBPTTでも1系列を処理できない場合に限り、解像度を1024から768へ下げて再計測する。

解像度縮小後も全SAM2 parameterの更新ができなければ、全体追加学習という当初の問いは本環境で未検証として停止する。SAM2部分凍結やstate reset学習へ事後的に置き換えてF0/F1の結果と呼ばない。

本学習の最大optimizer step数は、全系列pilotとtuning結果を使って決める。TBPTTの場合は1 video-object軌跡ごとに1 optimizer stepとし、chunk lossを全有効frame数で正規化して系列間のloss尺度を揃える。lockbox評価前にF0/F1共通の軌跡数・更新回数・設定を固定してmanifestへ記録する。公式MOSE configを参考にする。lockbox結果を見てからstep数を変えない。optimizerはAdamW、公式configの基準LR（SAM2本体 base 5e-6、vision encoder 3e-6）、cosine decay、gradient clip norm 0.1、BF16 AMPを初期候補とする。F1 adapterはSAM2本体base LRを使い、adapter LayerNorm・bias・alphaはweight decay 0、他のadapter weightはweight decay 0.1とする。実装configとSmallの互換性を予備clipで確認し、変更時は両条件へ同じSAM2設定を使い、adapter固有の変更は記録して固定する。

### full BPTTとTBPTTの区別

- **full BPTT:** Mamba stateとSAM2 memoryを全video-object軌跡でcarryし、軌跡末尾で総lossをbackwardする。勾配は初出frameまで戻る。
- **TBPTT:** 同じ数値stateを軌跡末尾までcarryする。選んだTBPTT境界ごとにchunk lossをbackwardして過去の計算graphを解放し、Mamba stateとSAM2 memoryのgraphだけdetachして次chunkへ渡す。勾配は直近chunkまで戻るが、過去chunkで作られたstateの数値は後続予測に残る。
- 両方式とも1 optimizer updateはvideo-object軌跡単位とする。長い軌跡中にparameterを更新してstateを古い重みのまま使う状況を作らない。Pilot後に採用した方式・TBPTT長を全F0/F1 runで固定する。

## 評価protocol

- lockbox 200系列では、各video annotation中の対象IDごとにGT maskが最初に非空となるframe `t0` を特定する。そのframeのboxをpromptとして対象ごとの単一対象推論を行う。
- 各対象は`t0`から動画末尾まで正方向にpropagateし、後続GT補正・teacher forcingを行わない。SAM2 memoryはcarryし、F1ではMambaもcarryする。次の対象へ移る前に両方の推論stateを初期化する。video frame 0開始対象と後発対象の数を分けて報告する。annotation上にIDがあるが有効な非空maskを持たない対象も除外数として記録する。
- P0、F0、F1、F1-resetに同じ画像前処理、box、対象、frame範囲、post-processingを適用する。確率的処理が残る場合はseedを固定する。
- prompt frame `t0` は指標計算から除外する。それ以降の注釈済みframeは、GT maskと予測maskが両方空ならJ=1・F=1、片方だけ空ならJ=0・F=0とする。これはDAVIS評価実装のempty-union規則に合わせる。frameごとにregion Jaccard (J) とboundary Fを求め、対象ごとに全評価frameを平均し、対象を系列内で平均、その後系列を等重みで平均する。J&Fは平均Jと平均Fの算術平均とする。
- 主比較はpaired `F1 − F0` のJ&F差。J、F、`F1 − F1-reset`、P0からF0への差も併記する。`F1 − F1-reset`はstate carryへの依存を診断する副次比較であり、時間情報の利用や性能改善を単独で立証する根拠にはしない。失踪・再出現への影響は、対象ごとの可視/空mask区間を分けて記述的に集計し、事後的に主指標へ置き換えない。
- 対象propagation長の三分位点をlockbox annotationだけから予測結果を見る前に計算し、短・中・長の3群で系列数、対象数、`F1 − F0`、`F1 − F1-reset`を報告する。分位点と群境界はmanifestに保存する。
- 系列単位bootstrapで平均差の95%信頼区間を計算する。1 seedの区間は動画間ばらつきのみを表すため、seed間の安定性を表すと解釈しない。

## 成功・失敗の判断

### 技術的な成立条件

- F0/F1とも学習・評価video-object軌跡でloss、予測mask、SAM2/adapter stateがfinite。各対象は動画末尾までstateを保持して完走し、最長propagation対象でもMamba stateのfinite性・更新回数・cache上限を確認する。
- F1 adapterの学習parameterへ有限gradientが届く。alpha初期値0では最初のstepでMamba勾配が0になり得るため、optimizer step後にalphaが非ゼロとなり、次のbackwardでMamba parameterへ有限gradientが届くことを確認する。学習state carry経路とstreaming推論経路は上記の数値許容範囲内。
- 各video-object軌跡開始時だけstateが初期化され、別sampleへのstate漏れがない。全系列のbackward/optimizer stepと200系列評価を完了でき、peak VRAMと速度を記録できる。

### 研究上の判定

- 主仮説を支持する条件は、paired `F1 − F0` の平均J&F差が正で、系列bootstrap 95%区間の下端も0を上回ること。
- `F1 − F1-reset`は副次診断として差と95%区間を報告する。正の差はこの学習済みcheckpointがstate carryに依存することを示唆するが、Mambaの時間情報利用を単独で立証しない。性能改善の主張は`F1 − F0`に基づく。
- 1 seedしか実行できない場合は予備結果として報告し、seedを越えた再現性を主張しない。研究上の結論を出す場合は、最低3 paired seedsで同じ方向が再現することを確認し、seed別結果も併記する。
- 技術的成立後に主仮説が支持されなくても結果として記録する。prompt・評価・seed・指標を事後的に変更して成功扱いにしない。

## 実装変更範囲

Implementation Gate通過後、外部実装repo `/mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2` の専用branchまたはworktreeで、以下の責務に限って変更する。

- Small用SAM2Train config、単一対象・全軌跡時系列dataset/sampler、初出box prompt条件、動画全体state carryとTBPTT trainer
- `TemporalMambaAdapter`の微分可能なtraining forward、軌跡単位state reset、TBPTT境界のdetach、推論forwardとの重み互換
- `SAM2Train.track_step`への対象ID接続、時系列順処理とloss接続
- 学習entrypoint/設定、F0/F1 paired run、評価とJ&F集計、manifest出力

既存の推論smoke・config・checkpoint・run出力は上書きしない。全run成果物は外部repoの新規runディレクトリに保存する。

## 実行手順と成果物

1. read-onlyでrepo commit/dirty状態、checkpoint hash、MOSEリスト、依存バージョンを記録する。
2. 全系列または代表video-object軌跡preflightでannotation/box/時系列順/state carry、finite loss、各parameter gradient、full BPTT/TBPTT境界の数値state continuity、inference parity、peak VRAMを確認する。
3. 事前固定した資源設定・step数・seedでP0/F0/F1を実行する。F0/F1のsample orderと拡張乱数を対応させる。
4. 中間checkpointを固定間隔で保存する。tuning 125系列の平均J&Fが最大となるcheckpointをF0/F1それぞれ選び、同点なら早いstepを採用する。
5. 設定・選択checkpoint・評価コードを凍結し、lockbox 200系列をP0/F0/F1/F1-resetで一度だけ評価する。対象別予測、初出frame別の対象数、J/F、系列別平均、長さ群別paired差、bootstrap区間を出力する。
6. command、git commit/dirty diff、checkpoint SHA-256、config、seed、splitと対象一覧、loss曲線、OOM/VRAM、学習時間、推論結果、評価スクリプトversionをmanifestと実験ログへ保存する。

## Implementation Gate

このspecは学習・評価の計画と実装範囲を定義する。2026-09-30にユーザーから実装開始承認を受け、以下の条件を満たした専用worktreeで実装・preflightを開始した。

- 承認済みspec: 本ファイル
- 変更範囲: 上記「実装変更範囲」
- 検証: 全動画state carryのF0/F1 preflight、BPTT/TBPTT state continuity・gradient・VRAM、固定lockbox J&F評価
- ユーザーの実装開始承認: 2026-09-30に受領
- 実装branch/worktree: `codex/mose-temporal-mamba-training` / `/mnt/HDD10TB-2/aburatani/worktrees/sam2-mose-temporal-mamba`

## 関連資料

- [最小decoder統合spec](2026-09-27-temporal-mamba-decoder-minimal-integration-spec.md)
- [MOSE・adapter学習brainstorm](../../../../secretary/notes/brainstorm/2026-09-30-temporal-mamba-adapter-training.md)
- [SAM2公式学習ガイド](https://github.com/facebookresearch/sam2/blob/main/training/README.md)
- [SAM2公式MOSE fine-tuning config](https://github.com/facebookresearch/sam2/blob/main/sam2/configs/sam2.1_training/sam2.1_hiera_b%2B_MOSE_finetune.yaml)
- [SAM2 VOS inference（後発対象の処理option）](https://github.com/facebookresearch/sam2/blob/main/tools/vos_inference.py)
- [DAVIS J/F metric implementation](https://github.com/davisvideochallenge/davis2017-evaluation/blob/master/davis2017/metrics.py)
