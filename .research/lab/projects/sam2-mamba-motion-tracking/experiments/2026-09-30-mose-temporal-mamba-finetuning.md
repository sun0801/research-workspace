---
project: sam2-mamba-motion-tracking
type: experiment-log
status: in_progress
created: 2026-09-30
last_updated: 2026-10-08
---

# MOSEv1 SAM2.1 Small + temporal Mamba追加学習

## 目的

[承認済みspec](../specs/2026-09-30-temporal-mamba-mose-finetuning-spec.md)に沿い、SAM2.1 Small全体fine-tuningへtemporal Mamba adapterを加える効果を、MOSEv1の単一対象・先頭box prompt・後続GT補正なし設定で比較する。

## 実行環境

- 実装repo: `/mnt/HDD10TB-2/aburatani/worktrees/sam2-mose-temporal-mamba`
- branch: `codex/mose-temporal-mamba-training`
- base checkpoint: `sam2.1_hiera_small.pt`, SHA-256 `6d1aa6f30de5c92224f8172114de081d104bbd23dd9dc5c58996f0cad5dc4d38`
- Python環境: SAM2 repoの`.venv-sam2`、Torch 2.10+cu128、Mamba 2.3.1
- GPU: GPU0 RTX PRO 4500 Blackwell 32GB
- run成果物: worktreeの`runs/mose_temporal_mamba_20260930/`（git local exclude）

## データ分割

固定seed 123。SAM2公式MOSE train list 1,246動画をfit 1,121動画・tuning 125動画に動画単位で分割し、val list 200動画はlockboxとする。fitは2,789 object軌跡・200,794伝播frame、tuningは313軌跡・21,919伝播frame、lockboxは570軌跡・36,830伝播frame。今回の軌跡はすべて動画frame 0に初出していることをannotation scanで確認した。

## 実装・予備検証

- F0: SAM2全体fine-tuning。F1: SAM2全体とtemporal Mamba adapterをfine-tuning。
- SAM2動画memoryとMamba stateは各軌跡全体でcarry。TBPTT=8境界では計算graphをdetachし、stateの数値を保つ。1軌跡につき1optimizer update。
- full BPTTは9-frame smokeでfinite、ただし実用VRAM余裕と最長系列への対応からTBPTTを採用。TBPTT=16は55-frame系列でOOM（約31GiB allocated）。TBPTT=8では短・中央値・500-frame最長preflightがfinite、peak約18.2/19.9GiB。
- Mamba adapterの学習用forwardと推論用streaming forwardのFP32 parityは最大絶対差`4.47e-08`。gradient finiteを確認。DAVIS公式boundary-F計算と30 random mask pairで一致を確認。

## 学習パイロット

同じfit順序先頭100軌跡、seed・augmentation系列・設定を揃えてF0/F1を実行。各軌跡後にmodel/optimizer/schedulerを含むcheckpointを保存した。

| Condition | 更新 | 状態 | checkpoint |
|---|---:|---|---|
| F0 | 100/100 | 完了 | `F0_step_000100.pt` |
| F1 | 100/100 | 完了 | `F1_step_000100.pt` |

全更新でlossはfinite。augmentationで初期maskが消えた系列は最大4回の幾何再試行後に処理され、学習を完了した。F1で高い単系列loss（最大観測18.28）が1回あったため、tuning結果と系列別分布を確認する。

### 更新済み評価器のsmoke

元解像度J/Fで、tuning先頭1動画（4対象）をP0/F0/F1/F1-reset各条件で推論・完走。これはパイプラインsmokeであり、checkpoint選択や性能比較の根拠には使わない。

| Condition | J | F | J&F |
|---|---:|---:|---:|
| P0 | 0.8497 | 0.9192 | 0.8844 |
| F0 step 100 | 0.8540 | 0.9283 | 0.8911 |
| F1 step 100 | 0.8540 | 0.9279 | 0.8909 |
| F1-reset step 100 | 0.8538 | 0.9285 | 0.8911 |

## 次の処理

1. F0/F1のpilot checkpointをtuning 125動画で評価し、同一J&F基準で候補checkpointを選ぶ。
2. pilotのtuning挙動と学習予算を記録し、lockboxを見る前にF0/F1共通の全学習step数・checkpoint間隔・選択規則を固定する。
3. 固定設定でfit全軌跡をF0/F1学習し、tuningから各条件のcheckpointを選択する。
4. 評価コード・checkpoint・設定を凍結後、lockbox 200動画をP0/F0/F1/F1-resetで一度評価し、paired差とvideo-bootstrap 95% CI、propagation長別結果を算出する。
5. checkpoint hash、run manifest、loss/VRAM/timing、全比較結果をここへ追記する。

### Pilot tuning result (F0 step 100)

- 125/125動画・313/313対象を評価完了。全対象はframe 0開始。
- equal-weight video mean: J=0.6956, F=0.7735, J&F=0.7345。
- inference elapsed: 3,898.7 s（約65.0分）。
- run: `runs/mose_temporal_mamba_20260930/pilot_tuning/F0_step100/`。予測maskは保存せず、objects.jsonl等metricsのみ保存。
- これは100更新pilotのtuning結果であり、lockbox結果ではない。F1同条件評価および学習予算決定前のため、checkpointは未選択。

### Pilot tuning result (F1 step 100)

- 125/125動画・313/313対象を評価完了。全対象はframe 0開始。
- equal-weight video mean: J=0.6964, F=0.7727, J&F=0.7345。
- inference elapsed: 3,839.9 s（約64.0分）。
- run: `runs/mose_temporal_mamba_20260930/pilot_tuning/F1_step100/`。
- F1−F0 pilot mean J&F = −0.0000033。step100時点では両条件に実質差が見られない。これはpilotの所見であり、lockbox評価ではない。

## 固定した本学習条件

pilot結果を踏まえ、lockboxを開く前に以下を固定した。両条件とも全fit 2,789軌跡を1 passし、各軌跡1 optimizer update（合計2,789更新）する。TBPTT=8、学習seed・順序・optimizer・augmentation条件はpilotと同一にする。Cosine schedulerのT_maxも2,789とする。中間checkpointは500更新ごと（500, 1000, 1500, 2000, 2500）と最終step 2789で保存する。F0/F1それぞれのtuning平均J&F最大checkpointを選び、同点なら早いstepとする。これにより全fit軌跡を一度ずつ学習しつつ、過学習前の候補をtuningで選べる。

本学習中は割り込み後の再開性を上げるため、復旧用checkpointを100更新ごとに保存する。tuning比較候補は依然500更新ごと（および終端）のみとし、100刻みの全checkpointを選択候補にはしない。

- F0本学習: 2,789 fit軌跡・1 pass・TBPTT=8。現在step 2/2,789で実行中。
- F1本学習はF0完了後に、同じ固定条件で開始する。

### F0本学習の開始状況

- full fit 2,789軌跡のF0本学習を開始。100更新ごとに復旧checkpointを保存し、tuning候補はstep 500, 1000, 1500, 2000, 2500, 2789に限定する。
- 現在step 15/2,789。実行中run: `runs/mose_temporal_mamba_20260930/`。

### 本学習進捗

- F0全fit学習: step 300/2,789到達。`F0_step_000100.pt`, `F0_step_000200.pt`, `F0_step_000300.pt`を確認。step 300時点のloss logは301行（step 1〜301）、全loss finite。最大lossは18.24。500-frame軌跡を含むfit対象が完走している。
- 現在もF0 training processが稼働中。OOM/NaNは未発生。

### F0途中の高loss対象確認（step 326時点）

- step 1〜326でloss>=10の軌跡は7件。該当annotationを全frame scanすると、5件は空GT mask frameを含む（対象消失・不可視区間）、2件は全frameで非空だった。
- 空mask区間だけでは高lossを説明できない。いずれもlossはfiniteで学習更新を完了している。対象ごとのtuning J/Fとlockbox評価で影響を確認し、学習途中のlossだけから除外・重み変更はしない。
- step 330でloss 189.34の系列（video `2bf49664`, object 1, 36 frames）を追加確認。GT maskは5/36 frameで空、frame 17以後の再出現時に面積が急増（最大224,968 pixels）。大lossはfiniteであるが、失踪後再出現を含む難系列として評価結果を照合する。
- step 395でloss 185.58の系列（video `d48c552d`, object 3, 71 frames）も調査。20 frameが不可視で空mask、frame 31に再出現し最大346,769 pixelsまで占有する。再出現後の大領域segmentationが高lossへ関与する可能性はあるが、単一例から原因とは断定しない。
- F0 step 400 checkpoint保存を確認。step 1〜405の学習logは全loss finite。最大lossはstep330の189.34（再出現・大領域mask例）。
- step 448でloss 46.26の系列（video `5ae23f9f`, object 1, 39 frames）を確認。末尾6 frameが空GT、その後3 frameは小領域で再出現。finite lossで完走し、再出現を含む例として保持する。
- step468のloss 11.53系列（video `a9162e14`, object 1, 36 frames）は空GT frameなしで、mask面積は12,243〜50,811 pixels。F0 step1〜473ではloss>=10が12軌跡、そのうち空GT区間を含むのは9、全frame非空は3。空mask/再出現だけで高loss全てを説明できないことを記録する。

### 2026-09-30 実装承認後の進捗

- ユーザーから保留解除と実装開始承認を受領。既存のF0本学習プロセスを継続し、再起動はしていない。
- 学習ログでstep 501〜760を確認。step 500の候補checkpoint `F0_step_000500.pt`（528 MiB）が保存済み。step 600 checkpoint `F0_step_000600.pt`（528 MiB）とstep 700 checkpoint `F0_step_000700.pt`（528 MiB）も保存を確認。step 1〜760の学習log 760行をJSON parseし、全loss finite、最大213.09（step 678）と確認。step 527はloss 23.44（180 frames）、step 578はloss 11.02（352 frames）だったが、いずれもfiniteで完走。step 614はloss 101.82（21 frames、video `6dc5e55d` object 1）。該当GTは全21 frameで非空、mask面積は690〜29,028 pixelへ増加していた。面積変化との関連は未確定。step 678はloss 213.09（66 frames、video `f6bfc699` object 5）。GTは65/66 frameで非空、可視時のmask面積は1,531〜272,424 pixelで、frame 16のみ空だった。大lossとの因果は未確定。step 759はloss 102.62（188 frames、video `b6520a94` object 4）。GTは166/188 frameで非空、最後の22 frameは空で、可視時の面積範囲は626〜199,580 pixelだった。lossとの因果は未確定。step 587では500-frame軌跡をloss 0.123、step 595でも500-frame軌跡をloss 0.185、step 596でも500-frame軌跡をloss 0.096で完走。
- GPU 0で学習プロセスPID 2726797が稼働し、約21.5 GiBを使用していることを確認。学習セッションは継続中。F0完了後にF0 tuning評価、続いて同一条件でF1を学習する。

### 2026-10-03 F0学習の復旧

- 以前の学習プロセスは終了しており、ログはstep 866まで記録されていたが、最後の復旧checkpointはstep 800だった。step 1〜866のlossは全てfinite（最大213.09）。
- checkpointに保存されていないstep 801〜866のモデル・optimizer状態は採用せず、step 800の復旧checkpointから再開した。seed 123、固定sample order、TBPTT=8、Cosine T_max=2,789、同一optimizer/augmentation設定を維持する。実装はログをcheckpoint step以下に戻してから再開するため、step 801以降を再計算する。
- 再開ログに `resumed at optimizer step 800` を確認。step 801〜901の101更新を再計算し、lossは全てfinite。step 1〜901のログもfinite（最大loss 213.09、step 678）。step 900の復旧checkpoint `F0_step_000900.pt`（528 MiB）を確認し、F0 fit学習は継続中。

### 2026-10-03 評価manifestとlockbox手順の補強

- lockbox対象ID一覧の正本をMOSE `meta_train.json` とし、annotation metadata上の対象数・非空mask対象数・非空maskがないため除外した対象IDをindexと評価summaryへ出力するよう評価器を補強。実データではtuning 313/313、lockbox 570/570が非空mask対象と一致し、どちらも除外0件。
- lockbox評価は、全200系列のtrajectory indexとannotation由来の長さ三分位planが先に固定され、planとindexのSHA-256が一致しない場合は開始しないゲートを追加。plan生成を一時copyでsmokeし、570対象のgroup割当とSHA-256照合が通ることを確認。confirmatory lockbox predictionはまだ実行していない。
- 変更後のP0 evaluator smokeをtuning先頭1動画・4対象で完走（予測mask保存なし）。J=0.8494、F=0.9189、J&F=0.8841。metadata対象313・非空313・除外0、prompt座標/label/seedを各対象のJSONLに保存することを確認。これはpipeline smokeで、checkpoint選択や性能比較には使わない。
- checkpoint selectorを追加し、候補step 500/1000/1500/2000/2500/2789の全6候補とtuning全125動画・313対象、同一trajectory index hashを要求する。最大のequal-weight video mean J&Fを選び、同点は早いstep。合成summaryで候補完全性・hash確認・tie-break smokeを通過。
- lockbox用freeze manifestにはF0/F1選択checkpoint、base checkpoint、code各ファイル、trajectory index、annotation由来length planのhashと評価protocolを保存する。evaluatorは4条件のcheckpoint/code/index/plan hashがfreezeと一致しない場合に停止し、同じcondition出力の上書きも拒否する。summaryは4条件の全200動画とindex記載の全有効対象が揃うまで集計しない。temporary runでfreeze生成、index再保存後hash不変、plan未作成時の評価拒否を検証。
- 公式MOSE augmentationのparameter範囲を使うが、実装pipelineには違いがある。現行実装はsquare resize後にaffine、shearをx/y両軸、affine fill=0、color operation固定順。公式config実装はaffine後resize、shear一軸、mean-color fill、color operation順序をrandomizeする。F0/F1には同一実装・paired seedを適用し、各manifestへ現行pipelineを明記する。したがって結論はこのfull-track pipeline下のpaired比較として解釈する。
- F0 fit学習: step 1,000/2,789。step 900と1,000 recovery checkpoint（各528 MiB）を確認。step 1〜1,000のlossは全件finite、最大213.09（step 678）。step 801〜1,000はstep 800 checkpointからの再計算。
- F0の再開前logにはraw prompt tensorがないため、per-track torch seed、augmentation retry count、初回image encoderのRNG消費を再生してnoisy box-point tensorを復元するexporterを追加。base checkpointとF0 step 900 checkpointを使い、2 trajectoryで再生成座標が一致することをsmoke確認。F0完了後に全2,789 trajectoryをexportし、index/log/checkpoint hashとともに保存する。F1本学習logと全評価logではprompt tensorを直接保存する。
- finiteチェックも追加。F1学習と評価では各frameのSAM2浮動小数tensor/memory出力をfinite検査し、非finiteで停止する。adapterは既存のMamba state/cache finite検査を継続する。変更後のP0 tuning先頭1動画smokeも完走し、checkpoint/base/index/evaluator hashとprompt tensorをsummaryへ記録した。
- F1 optimizer decay groupをspecどおり修正。SAM2は ndim<=1/biasを0、その他0.1。adapterはinput LayerNorm/bias/alphaのみ0、ほかの重み（1D Mamba `D`を含む）は0.1。dummy parameter group検査を通過。F1 manifestにはgroupごとのLR・decay・parameter count、software/GPU/code hash、chunk frame ranges、完了時間とpeak memoryを保存する。
- 10/3に保留解除と実装開始承認を受け、F0学習をstep 800 checkpointから継続。再開後はstep 1,045/2,789まで到達し、step 801〜1,045のlossは全件finite（最大419.36、step 1,039）。該当video `ddb1d0b1` object 2は62 frame中4 frameが空maskで、再出現時にmask面積が最大178,397 pixelへ変化する。難系列として記録し、固定済み学習条件は変更しない。GPU1でF0 step 500 checkpointのtuning評価を開始（確認時点37/313対象）。残る5候補はcheckpoint生成とstep 500評価の完了後、同GPUで順次評価するようキュー済み。lockbox評価は未実施。
- 進捗再確認時、F0はstep 1,400/2,789に到達し、`F0_step_001400.pt`（528 MiB）を確認。step 1〜1,400のlossは全件finiteで最大419.36。ログのvideo/object順もmanifestの固定sample orderとstep 1,344まで一致。最長500-frame軌跡はstep 1,160でloss 0.1879、step 1,342でloss 1.6862とそれぞれfiniteで完走した。step 500 tuning評価は313/313対象で完了し、J&F=0.75319。step 1,000候補のtuningは288/313対象。残る候補・F1評価・prompt再現・selector・lockbox手順は待機ジョブとして登録済み。
- F0 step 500 tuning評価を完了。125/125動画、313/313対象で、video等重み平均J=0.71547、F=0.79090、J&F=0.75319。所要4,271.6秒。これは固定6候補のうち1候補の評価であり、checkpoint選択にはまだ使わない。評価summaryは`runs/mose_temporal_mamba_20260930/tuning/F0_step_000500/summary.json`に保存。
- F0 step 1,000 tuning評価を完了。125/125動画、313/313対象で、video等重み平均J=0.71484、F=0.79329、J&F=0.75406。所要4,255.6秒。現時点のstep 500よりJ&Fは0.00088高いが、checkpoint選択には全6候補が揃うまで使わない。summaryは`runs/mose_temporal_mamba_20260930/tuning/F0_step_001000/summary.json`に保存。
- 10/4再確認時、F0学習はstep 1,456/2,789まで進行。step 1〜1,456のlossは全件finite（最大419.36）で、video/object順は固定sample orderと全件一致。F0 step 500/1,000のtuningはともに313/313対象で完了し、それぞれJ&F=0.75319/0.75406。次の固定候補step 1,500 checkpointを待ち、残る候補評価を進める。

### 2026-10-06 実装再開

- ユーザーが保留を解除し、実装開始を再承認。前回セッション終了後に残っていなかったF0学習プロセスを確認し、最後の復旧checkpoint `F0_step_001400.pt` から再開した。checkpointに含まれないstep 1401〜1456の旧ログ・更新は引き継がず、再計算している。
- 再開時に学習ログがstep 1400へtrimされたことを確認。step 1500 tuning候補checkpoint（SHA-256 `1206e9f8c02a73a9eee70b54633366535fc3cab305f427078a9e3b93b4c2ee7d`）、step 1600 recovery checkpoint（SHA-256 `43796d3295acdb2ae183269feb9fbe5853a335ce564d7c83c5fa3ee6663b76f0`）、step 1700 recovery checkpoint（SHA-256 `2553f1fdd1a2e61fb58b3479a6647f309f6cd922c234134dfec6bf86975b54d6`）、step 1800 recovery checkpoint（SHA-256 `c9d884fdd3e5e5486429281ab186743622e4445a425ef3aaa76b8ddf5b29f27b`）を保存し、学習はstep 1835/2,789まで進行。step 1〜1,835のlossは全てfinite（最大419.36）、固定sample orderとの不一致0件、step連番に欠落なし。再計算したstep 1421は最長500-frame軌跡でloss 2.5397、finiteで完走。
- 高loss系列をannotationのみで確認。step 1550はloss 175.82/200 frame、空GT 15 frame、visible mask面積258〜151,979 pixel。step 1567はloss 14.73/53 frame、空GT 23 frame、visible mask面積678〜22,151 pixel。step 1595はloss 56.07/342 frame、空GT 108 frame、visible mask面積244〜410,063 pixel。これらはfiniteで完走し、空maskだけが高lossの原因とは断定せず、固定条件を変えずに評価結果で確認する。
- step 1676はloss 366.62/114 frameでfinite。GT 114 frameは全て非空で、visible mask面積は1,516〜125,213 pixel。単一系列から原因は判断せず、固定条件のtuning評価を待つ。
- step 1791/1793はそれぞれloss 27.81/229 frame、26.08/46 frameでfinite。step1791はaugmentation retry 5回、空GT 156 frameを含み、step1793はretry 1回、空GTなし。visible mask面積は各754〜167,216、1,035〜48,300 pixel。因果は断定せず、設定は維持する。
- GPU0でF0本学習継続中。step 1500 tuning候補は保存済みで、tuning queueはGPU1の別SAM2MOT検出process終了を待つ。
- GPU1は別のSAM2MOTプロセスが使用中のため、F0残り候補のtuning評価はGPU1のcompute process終了を待つキューに維持。F0 selectorも6候補のsummaryが全て揃うまで待機中。lockbox評価は未実施。
- F0復旧以降の実装コードにはfinite検査・prompt tensor記録・manifest/実行時間記録が追加されている。学習更新の主要計算は同一であることを確認済みだが、再開以後に適用した追加コード差分を最終manifestと記録で追跡する。
- step 1,900復旧checkpointを作成。さらにstep 2,000 tuning候補checkpointを作成し、監査時点でF0はstep 2,001/2,789まで進行。ログ2,001行はstep連番、manifestの固定sample orderと全件一致し、loss非finiteは0件（最大lossはstep 1,039の419.36）。step 1900 checkpointは553,340,909 bytes、SHA-256 `996d6a4cc1cd8e438ae64074e8fff351f1d056d60899145514509e287a34fcbf`。step 2000 checkpointは553,340,909 bytes、SHA-256 `f9c8d9e77a829d4522fd6ac13b98077cda0660ed0c8c71f8e632119bf580111b`。step 1500/1600/1700/1800 recovery checkpointのハッシュは上記の通り。
- step 2003はvideo `4344808d`、object 1の492-frame軌跡をloss 0.3634でfinite完走。その後step 2005まで更新を確認した。長時間の無出力区間は停止ではなく、この長系列処理によるものだった。
- step 2034はloss 113.82/102 frames（video `ccf14ee0`, object 7）、GT空maskは20 frame、非空時の面積は3,429〜37,973 pixel。step 2035はloss 395.10/15 frames（video `74a917f1`, object 1）、全frameでGTが非空、面積は23,105〜89,182 pixel。双方finiteで、空maskだけでは高lossを説明できない。原因は断定せず、学習設定は変更しない。
- F1成果物の混同を確認。run直下の`F1_fit_manifest.json`と`F1_step_000100.pt`は9/30に作成された100-step pilotで、本学習待機queueは`runs/mose_temporal_mamba_20260930/F1_full_fit/`を専用出力先に指定している。よってpilot成果物はfull-fit checkpoint選択に混ざらない。F1本学習はF0 manifestの`completed_unix`を待機中。
- GPU0のF0学習processは稼働継続。GPU1は別のSAM2MOT検出process（PID 597741）が使用中で、10/6の再確認時点で21/35系列まで完了（累計246分）。F0残り候補評価・selector・prompt exporter・F1評価・lockbox queueはそれぞれ指定条件を待機中。lockbox評価は未実施。
- 10/6の保留解除後、F0 step 2000 checkpointからの再開watcher（PID 701043）と後続pipeline（PID 702564）を起動した。再開watcherはGPU0の別SAM2MOT追跡process（PID 692515）が使用中のため待機しており、F0学習の再開はまだ確認できていない。pipelineはF0 manifestの`completed_unix`が設定されるまで待つ。既存のrun直下F1 pilot成果物との混同を避け、本学習は`F1_full_fit/`へ分離する。GPU1も別SAM2MOT検出process（PID 597741）が使用中。別実験は停止せず、空き次第キューが続行する。
- lockboxのannotation由来length planを予測前に作成。200動画・570対象を全件含み、短/中/長は219/163/188対象、境界は40/70 frame。index SHA-256 `ae67e0174e594000ff7059a37cf657aadffb1ec024e16ea7f96b7cfc14d893ab` とplan記録のhash一致を確認。予測artifactは未作成で、lockbox比較は未開始。後続pipelineは同じplanを検証してcheckpoint freeze後に評価へ進む。
- GPU待機中にGPU非依存の実装検証を実施。学習・評価・prompt export・checkpoint selector・lockbox summary各entrypointのCLI import/helpが実運用と同じ`PYTHONPATH`で全て成功し、関連Pythonファイルの`compileall`も成功。lockbox予測評価やmodel forwardの代替検証ではない。

### 2026-10-07 F0学習再開

- 前回のwaiter/pipeline processは存在せず、F0 manifestは未完了、最新checkpointはstep 2,000のままと確認。GPU0/1も空いていたため、F0をstep 2,000から同一設定（seed 123、TBPTT=8、scheduler 2,789 steps）で再開し、resume logに`resumed at optimizer step 2000`とstep 2,001（loss 0.18896、42 frames、finite）を確認。GPU0で約21.4 GiB使用。
- 再確認時にstep 2,002（loss 0.11470、169 frames、finite）へ進行し、trainer process PID 804264がGPU0で稼働していることを確認。
- checkpoint step 2,000から再計算したstep 2,003は492-frame軌跡をloss 0.36528でfinite完走。step 2,004は45 frames、loss 1.79836でfinite。再開後ログの対象順はmanifestの固定sample orderと全件一致（step 2,001〜2,004）。以前の未checkpoint更新に記録されたstep 2,003のloss 0.3634はresume時に破棄されており、最終run履歴には今回の再計算を採用。
- F0はstep 2,006まで進行。manifestとの全2,006行のsample order不一致0、nonfinite loss 0件、最大loss 419.3601（step 1,039）。step 2,006は61 frames、loss 0.14845。100-step保存間隔のため最新checkpointはstep 2,000のまま。
- 次の再確認ではstep 2,014まで進行。全2,014行でstep欠落・nonfinite lossはなく、step 2,001以降のsample order不一致も0。step 2,014は30 frames、loss 0.06496。checkpointは保存間隔によりstep 2,000。
- その後step 2,018まで進行。全2,018行でstep連番、finite loss、manifest sample orderが一致。step 2,018は48 frames、loss 0.06354。checkpointは引き続きstep 2,000。
- 最新監査時点でstep 2,020。全2,020行のstep連番・finite loss・manifest sample orderが一致。step 2,019（99 frames、loss 0.05518）とstep 2,020（114 frames、loss 0.11528）はfinite。checkpointは保存間隔どおりstep 2,000。
- さらにstep 2,022へ進行。全2,022行のstep連番とfinite lossを確認し、最新stepもmanifest sample orderに一致。step 2,022は73 frames、loss 0.12342。checkpointは引き続きstep 2,000。
- F0はstep 2,029まで進行し、全2,029行でstep連番・finite loss・固定sample orderを確認。step 2,029は54 frames、loss 0.05964。
- GPU1が空いていたため、保存済みF0 step 1,500のtuning評価をGPU1で先行開始し、F0 fit（GPU0）と並列化。確認時点で6/313対象を処理し、GPU1使用量は約1.5 GiB。後続pipelineはGPU待機後にもsummary有無を再確認するよう修正し、先行評価との二重起動を防止（`bash -n`成功）。
- 並列処理の再確認時、F0はstep 2,036まで進行。全2,036行でstep欠落・nonfinite loss・sample order不一致0。step 2,034/2,035の高loss軌跡も再計算でfiniteに完走。step 1,500 tuning評価は14/313対象まで進行し、summary完成待ち。
- 次の監査時点でF0はstep 2,039。全2,039行で連番・finite loss・sample order一致。step 1,500 tuningは24/313対象まで進行し、GPU0/1の両processが稼働継続。
- 続けてF0はstep 2,042まで進行。全2,042行で連番・finite loss・sample order一致。step 1,500 tuning評価は26/313対象まで完了。step 1,500評価完了後にstep 2,000評価を始めるGPU1 queueも起動済み。
- 追加確認でstep 2,046へ進行。全2,046行で連番・finite loss・sample order一致。step 1,500 tuningは34/313対象まで進行し、step 2,000評価queueはそのsummaryを待機中。
- 再確認時点でF0はstep 2,048、step 1,500 tuningは36/313対象。全2,048行で連番・finite loss・manifest sample order一致。step 2,000評価queueはstep 1,500 summary完成待ち。
- 次の確認ではF0がstep 2,050まで進行。全2,050行で連番・finite loss・sample order一致。step 2,049は300-frame軌跡、loss 9.5428でfinite完走。step 1,500 tuningは37/313対象まで進み、step 2,000候補queueはsummary待ち。
- 現在F0はstep 2,051。全2,051行で連番・finite loss・sample order一致。step 1,500 tuning評価は38/313対象まで進行し、GPU1で継続中。step 2,000候補queueはsummary完成待ち。
- 再確認時点でstep 2,056。全2,056行で連番・finite loss・sample order一致。step 1,500 tuning評価は43/313対象まで進み、summaryは未完成。step 2,000候補queueは引き続き待機。
- 現在F0はstep 2,058、step 1,500 tuningは45/313対象。F0の全2,058行で連番・finite loss・sample order不一致0を再確認。step 2,000候補queueはstep 1,500評価summaryを待機中。
- F0はstep 2,059へ進行。全2,059行でstep連番・finite loss・sample order一致。step 1,500 tuning評価は47/313対象で継続し、step 2,000 queueはsummaryを待っている。
- 最新確認ではF0 step 2,060、step 1,500 tuning 58/313対象。F0全2,060行で連番・finite loss・固定sample order一致。F0学習（GPU0）とtuning評価（GPU1）が並行稼働。
- F0完了後のF1学習・tuning・selector・lockbox pipelineを再登録。pipelineはF0 manifest完了を待機中。lockbox predictionは未実施。
- 11:21 JSTの再確認では、F0学習process（GPU0）とstep 1,500 tuning評価（GPU1）がともに稼働し、F0はstep 2,063/2,789、tuningは60/313対象。F0学習はstep 2,000から約25分で63 step進み、step 2,001〜2,063に欠落・nonfinite loss・manifest sample order不一致はない。後続pipeline（PID 804527）もF0 manifest完了を待機中。現行の実測速度を全工程へ単純外挿すると、残りは概ね2〜4日規模だが、F1の学習速度とlockbox評価時間により変動する。lockbox予測は未実施。
- 11:23 JSTにも再監査し、F0はstep 2,071/2,789へ進行。全2,071行はstep連番、nonfinite loss 0件、manifest sample order不一致0。step 1,500 tuningは60/313対象で継続中、step 2,000候補のqueueと後続pipelineも稼働している。
- 継続確認でF0はstep 2,075/2,789、step 1,500 tuningは81/313対象。F0全ログを再監査し、step連番・有限loss・manifest sample orderが全件一致。両GPUのjobとF0後続pipelineは稼働中。
- 11:26 JST時点でF0はstep 2,081/2,789、step 1,500 tuningは86/313対象。F0全2,081行を再監査し、step連番・有限loss・manifest sample order不一致0。F0 training/evaluationおよびF0完了後のpipelineは引き続き稼働中。
- 11:29 JSTの確認でF0はstep 2,088/2,789、step 1,500 tuningは100/313対象へ進行。F0全2,088行で連番・finite loss・sample order一致を確認。外部run領域は114 GiB使用、同一volumeに7.2 TiB空きがあり、lockbox予測成果物を保存する余地がある。
- 11:31 JST確認ではF0 step 2,093/2,789、step 1,500 tuning 109/313対象。F0全ログで連番・finite loss・manifest sample order一致。評価済み109 objectはID重複なく、J/F/J&Fが全件finite。学習・評価・後続pipelineは稼働中。
- 11:33 JST確認ではF0 step 2,098/2,789、step 1,500 tuning 122/313対象。F0学習全2,098行でstep連番・nonfinite loss 0・sample order不一致0。評価済み122対象はvideo-object重複なし、全指標finite。評価summary完成待ちで、後続jobは稼働中。
- 11:34 JSTの監査でF0 step 2,100/2,789、step 1,500 tuning 124/313対象。学習全行は連番・finite loss・manifest sample order一致。評価済み124対象も重複なく、J/F/J&Fは全件finite。両GPU jobと後続pipelineは継続稼働。
- その後、step 1,500 tuningは126/313対象・51動画まで進み、対象重複と非finite指標は0。summary未完成のためF0 selectorはまだ実行段階にない。
- 11:36 JSTにF0 step 2,104/2,789、step 1,500 tuning 133/313対象を確認。学習ログは全件連番・finite loss・sample order一致、評価済み対象は全件一意でJ/F/J&F finite。summary完成待ちのためselector未実行。後続pipelineも動作中。
- 11:37 JSTにF0 step 2,108/2,789、step 1,500 tuning 139/313対象を確認。全学習行で連番・finite loss・sample order一致。評価済み139対象は重複なく指標finite。summary未完了のためF0 selectorは待機中。
- 11:37 JST後半の確認でF0はstep 2,109、step 1,500 tuningは140/313対象。学習全履歴と評価途中行の連番・固定順・一意性・有限値チェックを再実施し、異常0件。F0 summaryとselectorは引き続き待機中。
- 11:39 JSTの再確認でF0はstep 2,116/2,789、step 1,500 tuningは144/313対象。学習全履歴で連番・finite loss・sample order一致。評価済み144対象は一意でJ/F/J&Fが全件finite。F0 summary未完成、各待機pipeline processは生存中。
- 11:40 JST時点でF0はstep 2,120/2,789、step 1,500 tuningは148/313対象。学習全行の連番・有限loss・sample order一致、評価済み対象の一意性と全指標finiteを確認。評価processと後続pipelineは継続中。
- 11:41 JST確認でF0はstep 2,121/2,789、step 1,500 tuningは151/313対象。F0全学習行の連番・finite loss・manifest順と評価対象の一意性・finite J/Fを再検証し異常なし。評価summaryは未完成。
- 11:42 JSTの再確認でF0 step 2,125/2,789、step 1,500 tuning 160/313対象。全学習stepと評価済みobjectについて連番・manifest順・重複・finite値の異常0。tuning summaryの完成待ちで後続処理は稼働中。
- 11:42 JST後半にF0 step 2,125/2,789、step 1,500 tuning 163/313対象を再確認。step 2,100 recovery checkpointが存在し、全学習ログおよび評価途中行に順序・重複・有限値の異常はない。
- 11:44 JST時点でF0 step 2,130/2,789、step 1,500 tuning 172/313対象。学習ログ全件でstep連番・finite loss・sample order一致。評価対象重複0、J/F/J&Fの非有限値0。評価processと後続pipelineは稼働中。
- 11:45 JSTの確認でF0 step 2,135/2,789、step 1,500 tuning 179/313対象。全学習履歴と評価行を監査し、連番・sample order・重複・finite値の異常0。tuning summary未完成、後続pipelineは待機中。
- 11:47 JSTにF0 step 2,137/2,789、step 1,500 tuning 184/313対象を確認。全学習ログと評価途中行を再監査し、不正step・順序不一致・重複・非finite値はいずれも0。F0 summary未完成で、学習・評価・後続pipelineは稼働中。
- 11:48 JST時点でF0 step 2,143/2,789、step 1,500 tuning 190/313対象。全学習logで連番・finite loss・manifest sample order不一致0、評価済み対象は一意かつ全指標finite。evaluation/pipeline継続中。
- 11:49 JST確認ではF0 step 2,145/2,789、step 1,500 tuning 194/313対象。全学習ログで連番・finite loss・固定sample order一致、評価済み対象の重複・非finite指標なし。step 2,100 recovery checkpointは存在し、F0 summary未完成。
- 11:50 JST確認でF0はstep 2,147/2,789、step 1,500 tuning 202/313対象。全学習履歴の連番・固定順・finite lossと、評価対象の重複・finite metricを再検査して異常0件。summary未完成、pipelineは稼働中。
- 11:51 JST確認でF0 step 2,149/2,789、step 1,500 tuning 205/313対象。全学習行の連番・sample order・有限lossと評価対象の重複・finite metricを再監査し異常0件。F0 summary未完成、後続pipeline稼働中。
- 11:52 JST時点でF0 step 2,156/2,789、step 1,500 tuning 213/313対象。全学習ログで連番・sample order・finite loss一致。評価済み213対象に重複・非finite metricなし。評価summary完成待ちで各process継続中。
- 12:23 JSTの再確認で前回の学習・evaluation・pipeline processは消失し、F0 logはstep 2,157、tuning step 1,500の逐次出力は216対象で終了していた。exit tracebackは残らず、GPUはidle。最後の復旧checkpointはstep 2,100（SHA-256 `3ad0b585c891b3f64c1f92dfeee8364547d92d2ba916de1a50a2be0882856ca0`）。checkpointはF0/fit/seed123で、期待するpermutation sample orderと一致することを確認。
- 12:26 JST、step 2,100 checkpointからF0を再開。resume logにoptimizer step 2,100、再計算step 2,101（loss 0.30418、140 frames、finite）を確認。F0 step 1,500 tuning評価は途中出力を破棄し全313対象を再実行中。step 2,000評価queueとF0完了後のF1/tuning/lockbox pipelineも再起動し、各processの稼働を確認。lockbox評価は未開始。
- 12:28 JST再確認でF0はstep 2,106、再実行中のstep 1,500 tuning評価は14対象。全F0学習行で連番・manifest sample order・finite lossが一致し、評価済み対象の重複・非finite値は0。trainer/evaluator/queue/pipeline各processが稼働中。
- 12:30 JST再監査でF0はstep 2,114/2,789、step 1,500 tuningは25/313対象。学習ログの連番・manifest sample order・finite loss一致、評価対象の一意性・finite J/Fを確認。F0は継続中、評価summary未完成。
- 12:33 JST確認ではF0 step 2,122/2,789、再実行tuning step 1,500は35/313対象。学習全履歴で連番・manifest順・finite lossを確認し、評価済み対象の重複と非finite指標は0。再開したF0/evaluation/後続pipelineは稼働中。
- 12:34 JSTの再確認で再開後F0はstep 2,125/2,789、再実行中のstep 1,500 tuningは36/313対象。全学習ログの連番・manifest順・finite loss、評価対象の重複・finite J/Fを検証し異常0件。F0 trainer/evaluatorと後続pipelineは稼働中。
- 12:35 JST確認でF0はstep 2,129、step 1,500 tuning再評価は38/313対象。全学習ログと途中評価行にstep/sample order/有限値/一意性の異常0件。manifest未完了、学習・評価・後続pipelineは継続中。
- 12:37 JST確認で再開後F0はstep 2,136/2,789、step 1,500 tuningは43/313対象。学習全行の連番・固定sample order・finite lossと、評価済み対象の重複・finite指標を再検査し異常0件。F0 manifestは未完了、pipeline継続中。
- 12:39 JST再監査で再開後F0はstep 2,140/2,789、step 1,500 tuning再評価は58/313対象。学習全履歴で連番・sample order・finite loss一致、途中評価は対象重複・nonfinite metricとも0。学習・評価・後続pipelineは稼働中。
- 12:41 JST確認でF0はstep 2,146/2,789、step 1,500 tuning再評価は62/313対象。学習全行と途中評価を再監査し、連番/順序不一致・重複・非finite値は0。評価summaryは未完成、後続pipeline稼働中。
- 12:43 JST再確認ではF0 step 2,153/2,789、step 1,500 tuningは72/313対象。全学習ログは連番・sample order・finite loss一致、評価72対象は重複なしで指標finite。summary未完成、F0学習・評価・後続pipeline稼働中。
- 12:48 JSTの監査でF0はstep 2,170/2,789、step 1,500 tuningは94/313対象。全2,170学習行で連番・manifest順・finite lossが一致し、評価94対象に重複・nonfinite指標なし。両GPU jobおよび後続pipelineを確認。
- 12:50 JST、F0 step 2,177/2,789、step 1,500 tuning 105/313対象。全学習ログのstep連番・manifest順・finite loss、評価対象の一意性・finite metricを検証し異常0。trainer/evaluatorおよび後続queue/pipeline processの存続を再確認。
- 12:55 JST監査でF0はstep 2,199/2,789、step 1,500 tuningは131/313対象。全学習行の連番・manifest順・finite loss、評価対象の一意性・finite指標を検証し異常0。trainer/evaluatorと後続queue/pipeline processは稼働中。
- 13:00 JST再監査でF0 step 2,213/2,789、step 1,500 tuning 145/313対象。学習順序・finite lossと評価の重複・finite J/F/J&Fに異常なし。学習・評価と後続pipelineは継続中。
- 13:05 JST、F0 step 2,229/2,789、step 1,500 tuning 172/313対象。学習連番・manifest順・finite loss、評価対象の一意性・finite J/Fを全行監査し異常0。評価summaryは未完成、F0学習・評価・後続pipelineは稼働中。
- 13:09 JST再監査でF0 step 2,240/2,789、step 1,500 tuning 191/313対象。学習行の連番・manifest順・finite loss、評価対象重複・nonfinite metricとも異常0。summary未完成、後続pipeline稼働中。
- 13:13 JST再監査でF0 step 2,251/2,789、step 1,500 tuning 215/313対象。全学習行の連番・manifest順・finite lossと、評価対象の重複・finite J/Fに異常なし。summary未完成、後続pipeline稼働中。
- 13:15 JST再監査でF0 step 2,261/2,789、step 1,500 tuning 229/313対象。学習順序・finite lossと評価対象の一意性・finite J/Fを検証し異常なし。summary未完成、後続pipeline稼働中。
- 13:19 JST再監査でF0 step 2,272/2,789、step 1,500 tuning 257/313対象。学習行の連番・manifest順・finite lossと評価対象の重複・nonfinite metricに異常なし。評価summary待ち、後続pipeline稼働中。
- 13:23 JST再監査でF0 step 2,280/2,789、step 1,500 tuning 267/313対象。学習順序・manifest一致・finite loss、評価対象の一意性・finite J/Fに異常なし。summary未完成、後続pipeline稼働中。
- 13:27 JST監査でF0 step 2,286/2,789、step 1,500 tuning 284/313対象。進行中に見えた長時間stepは500-frame trajectoryで、完了logのframe数もindexと一致。全学習順序・finite loss、評価対象の一意性・finite J/Fに異常なし。
- 13:30 JST再監査でF0 step 2,298/2,789、step 1,500 tuning 289/313対象。学習順序・finite loss、評価対象の一意性・finite J/Fに異常なし。266-frame動画の評価は3対象中2対象まで完了、summary待ち。
- 13:33 JST再監査でF0 step 2,304/2,789、step 1,500 tuning 293/313対象。全学習行の順序・manifest一致・finite loss、評価対象の重複・finite指標なし。長尺266-frame動画の全4対象は完了。
- 13:37 JST監査でF0 step 2,315/2,789、step 1,500 tuning 311/313対象。学習の順序・manifest一致・finite loss、評価対象一意性・finite J/Fに異常なし。直前の確認時点ではF0次sampleは228-frame軌跡だった。その後step 2,315まで進み、tuning残り2対象。
- 13:37 JST、F0 step 1,500 tuning評価が完了。313/313 object・125/125 video、初出frameは全対象video frame 0、除外0。video内でobject平均を取った後にvideo平均をraw評価行から再計算し、summaryのJ=0.7204008801、F=0.7947241432、J&F=0.7575625116と完全一致。object重複・nonfinite metricなし。step 2,000評価queueとF0 fit継続中。
- 13:42 JST監査でF0 step 2,325/2,789、step 2,000 tuning 22/313対象。全学習行の順序・manifest一致・finite loss、評価対象重複・nonfinite指標なし。500-frame F0 trajectoryも完了し、F0 fitとstep 2,000評価は継続中。
- 13:45 JST監査でF0 step 2,332/2,789、step 2,000 tuning 34/313対象。学習step/sample順・finite loss、評価対象一意性・finite J/Fに異常なし。F0 fitとstep 2,000評価が継続中。
- 13:49 JST再監査でF0 step 2,342/2,789、step 2,000 tuning 38/313対象。学習順序・finite loss、評価対象一意性・finite J/Fに異常なし。直近評価軌跡は300 frames、step 2,000評価とF0 fitが継続中。
- 13:51 JST監査でF0 step 2,351/2,789、step 2,000 tuning 54/313対象。学習順序・finite loss、評価対象の一意性・finite J/Fに異常なし。両jobは稼働し出力継続中。
- 13:54 JST再監査でF0 step 2,361/2,789、step 2,000 tuning 63/313対象。全学習行のsample順・finite loss、評価の一意性・finite J/Fを確認し異常なし。両jobは出力継続中。
- 13:58 JST監査でF0 step 2,371/2,789、step 2,000 tuning 85/313対象。学習順序・finite loss、評価対象一意性・finite J/Fに異常なし。summary未完成、両job継続中。
- 14:00 JST再監査でF0 step 2,382/2,789、step 2,000 tuning 97/313対象。学習順序・finite loss、評価一意性・finite J/Fに異常なし。F0 fitと評価jobは稼働中。
- 14:04 JST再監査でF0 step 2,393/2,789、step 2,000 tuning 109/313対象。全学習行でstep連番・manifest sample order・finite lossが一致し、評価対象は重複なしでJ/F/J&Fもfinite。F0 fitとstep 2,000評価は稼働中、summary未完成。
- 14:05 JSTの再確認でF0 step 2,399/2,789、step 2,000 tuning 121/313対象。学習全行の順序・manifest一致・finite loss、評価対象の一意性・有限J/F/J&Fを再検査し異常なし。両jobと後続pipelineは稼働継続。
- 14:07 JSTの再監査ではF0 step 2,407/2,789、step 2,000 tuning 128/313対象。全学習行のstep/sample order/loss、評価行の対象一意性・finite J/F/J&Fに異常なし。各processは継続稼働。
- 14:10 JST確認でF0 step 2,412/2,789、step 2,000 tuning 142/313対象。全学習行のstep連番・manifest順・finite loss、評価対象の一意性・finite指標は正常。直近の学習系列は64 framesで完了し、process出力が進行していることを確認。
- 14:11 JST再確認でF0 step 2,414/2,789、step 2,000 tuning 145/313対象。F0全学習行のstep/sample order/finite loss、評価対象の一意性・J/F/J&F有限性に異常なし。F0 fit/evaluationと後続pipelineは継続中。
- 14:13 JSTの監査でF0 step 2,420/2,789、step 2,000 tuning 151/313対象。学習step・manifest順・有限lossと評価の対象一意性・有限指標に不整合なし。両jobと後続pipelineは稼働継続。
- 14:14 JST再監査でF0 step 2,421/2,789、step 2,000 tuning 161/313対象。学習ログ全行でstep/sample order/loss異常0、評価対象の重複・非finite metric 0。F0学習・評価・後続pipelineは稼働中。
- 14:17 JST監査でF0 step 2,428/2,789、step 2,000 tuning 176/313対象。全学習行でstep順・manifest sample order・finite loss一致、評価対象重複と非finite J/F/J&Fは0。直近では65-frame軌跡を処理、F0学習・評価と後続pipelineは稼働中。
- 14:18 JST再監査でF0 step 2,432/2,789、step 2,000 tuning 182/313対象。F0全学習行のstep順・manifest一致・有限loss、評価対象の一意性・finite metricに異常なし。F0 fit・評価と後続pipelineは稼働中。
- 14:20 JSTの監査ではF0 step 2,434/2,789、step 2,000 tuning 189/313対象。全学習行のstep/sample order/finite loss、評価対象重複・nonfinite指標とも異常なし。90-frameの学習系列が完了し、各jobと後続pipelineは継続中。
- 14:21 JST確認でF0 step 2,437/2,789、step 2,000 tuning 196/313対象。全学習ログの順序・manifest一致・finite loss、評価対象の一意性・finite指標に異常なし。F0学習・評価とpipelineは継続中。
- 14:22 JST再監査でF0 step 2,443/2,789、step 2,000 tuning 204/313対象。全学習行のstep/sample order/lossと評価対象一意性・finite J/F/J&Fに不整合なし。後続artifactは未作成でpipelineはF0完了待ち。
- 14:24 JST確認でF0 step 2,445/2,789、step 2,000 tuning 212/313対象。F0全学習行は連番・manifest sample order・finite lossが一致し、評価行は重複なしでJ/F/J&F finite。後続pipelineはF0完了待ち。
- 14:25 JST再監査でF0 step 2,447/2,789、step 2,000 tuning 217/313対象。全学習行の連番・manifest順・finite loss、評価行の一意性・finite J/F/J&Fに異常なし。step 2,500/2,789候補評価はcheckpoint作成待ち。
- 14:26 JST確認でF0 step 2,452/2,789、step 2,000 tuning 224/313対象。全学習行でstep・sample order・有限loss、評価行で対象一意性・有限J/F/J&Fに異常なし。step 2,500/2,789 checkpointは未作成、学習・評価jobは継続中。
- 14:28 JST再確認でF0 step 2,457/2,789、step 2,000 tuning 234/313対象。全学習行のstep/sample order/lossおよび評価行の重複・有限J/F/J&Fを監査し異常なし。候補checkpointと後続summaryはまだ作成待ち。
- 14:29 JST監査でF0 step 2,462/2,789、step 2,000 tuning 244/313対象。学習step・sample order・有限lossと評価対象の一意性・finite metricに異常なし。両jobは進行し、F0 selector/F1開始前。
- 14:30 JST監査ではF0 step 2,464/2,789、step 2,000 tuning 255/313対象。学習全履歴の連番・manifest順・finite loss、評価対象一意性・finite J/F/J&Fに異常なし。評価summary未完成、F0 fit/evaluation継続中。
- 14:32 JST確認ではF0 step 2,470/2,789、step 2,000 tuning 262/313対象。学習全行のstep/sample order/finite loss、評価対象の一意性とfinite metricに異常なし。summary未完成で両job稼働中。
- 14:33 JST確認でF0 step 2,472/2,789、step 2,000 tuning 265/313対象。全学習行の連番・manifest順・finite loss、評価行の一意性・finite J/F/J&Fに異常なし。step 2,500 checkpoint未作成、各job継続中。
- 14:34 JST再確認ではF0 step 2,474/2,789、step 2,000 tuning 267/313対象。全学習行の順序・manifest一致・finite loss、評価の対象一意性・finite J/F/J&Fに異常なし。121-frame trajectory完了を確認、checkpointとsummaryは引き続き待ち。
- 14:36 JST確認でF0 step 2,478/2,789、step 2,000 tuning 270/313対象。学習全行の連番・sample order・finite lossおよび評価対象一意性・finite metricに異常なし。F0 fit/evaluation継続、step 2,500 checkpoint未作成。
- 14:37 JST確認ではF0 step 2,480/2,789、step 2,000 tuning 274/313対象。全学習行のstep/sample order/finite lossと評価対象の一意性・finite J/F/J&Fに異常なし。step 2,500/2,789候補checkpointは未作成。
- 14:38 JST監査でF0 step 2,483/2,789、step 2,000 tuning 284/313対象。全学習履歴の順序・sample order・有限lossと評価対象の重複・非finite指標は0件。step 2,500 checkpointとevaluation summaryは未作成。
- 14:40 JST確認でF0 step 2,487/2,789、step 2,000 tuning 287/313対象。学習全行の順序・manifest一致・finite loss、評価行の一意性・finite metricに異常なし。step 2,000評価summary未完成、F0 fit継続中。
- 14:41 JST確認でF0 step 2,490/2,789、step 2,000 tuning 288/313対象。学習全行の順序・manifest一致・finite loss、評価行の一意性・finite指標に異常なし。checkpoint 2,500とevaluation summaryは未作成。
- 14:42 JST監査でF0 step 2,495/2,789、step 2,000 tuning 289/313対象。全学習行のstep順・manifest順・finite lossと評価行の一意性・finite指標に異常なし。両処理は稼働中、step 2,500 checkpoint未作成。
- 14:44 JST確認ではF0 step 2,497/2,789、step 2,000 tuning 290/313対象。全学習行のstep/sample order/finite loss、評価対象一意性・finite metricに異常なし。直近は166-frame trajectoryが完了し、step 2,500 checkpointは未作成。
- 14:45 JST確認でF0 step 2,502/2,789まで進み、step 2,500 checkpointを作成。step 2,000 tuningは297/313対象でsummary未完成。全学習行の順序・有限loss、評価対象一意性・finite J/F/J&Fに異常なし。
- 14:47 JST再監査でF0 step 2,510/2,789、step 2,000 tuning 306/313対象。学習全行のstep/sample order/finite lossと評価行一意性・finite指標に異常なし。step 2,000 summary未完成、step 2,500評価は未開始。
- 14:49 JST、F0 step 2,000 tuning評価が313/313 object・125/125 videoで完了。frame 0開始313、後発出現・除外0。video内object平均後のmacro video-meanをraw行から独立再計算しsummaryと一致（J=0.7245675933、F=0.7995903629、J&F=0.7620789781、最大差1.2e-16）。F0学習はstep 2,512/2,789で継続、step 2,500 checkpoint作成済み。後続pipelineはF0完了待ち。
- 14:50 JST確認でF0はstep 2,519/2,789へ進行。全2,519行でstep/sample order/finite loss不一致0。step 2,000 tuning summaryを独立監査済み。後続pipelineはF0 fit manifest完了を待機中。
- 14:52 JST再監査でF0 step 2,523/2,789。全2,523学習行でstep連番・manifest sample order・finite lossが一致。step 2,000 tuning評価は313/313でsummaryも独立照合済み。F0 fit継続、後続pipelineはmanifest完了待ち。
- 14:54 JST確認でF0 step 2,526/2,789。全学習行のstep/sample order/finite loss不一致は0。F0 checkpoint 2,500は作成済み。F0学習継続中で、後続pipelineはmanifest完了を待つ。
- 2026-10-07 15:10 JST、中断後の復旧を確認。未保存stepを引き継がずF0 checkpoint 2,500から再開し、学習ログはstep 2,507/2,789まで進行。step連番・manifest sample order・finite lossの不一致は0件。F0 fit manifestは未完了で、後続pipelineはF0完了を待機中。学習processとpipeline processの稼働を確認。
- 2026-10-07 15:12 JST、停止原因を切り分け。F0 stdoutにTraceback、CUDA OOM、明示的なerrorはなく、step 2,530付近でCodex turn interruption後にprocessが消失し、最後の保存checkpoint 2,500から再開した経緯と一致する。OS側の終了signalまではログに残っておらず、Oct 3のstep 866停止も同じく正確なsignalは未特定。現在の再開processはstep 2,511まで進み、GPU 0で稼働中。GPU 1でstep 2,500 tuning評価を並行開始した。
- 2026-10-07 15:13 JST、外部worktreeの変更済みPython entrypoint/model filesを`py_compile`し、`git diff --check`も通過。F0学習はstep 2,515まで進行し、GPU 0 process稼働中。GPU 1ではF0 step 2,500 tuning評価processがmodel初期化後に稼働している。tuning summaryは未完成。
- 2026-10-07 15:17 JST、長時間jobをCodex turn interruptionから切り離すためtmux常駐構成へ移行。F0 fitとstep 2,500 tuning evaluatorを監視し、消失時は有効checkpointから再開／tuning metricsを再実行するguardをtmuxで起動。後続pipelineも、F0完了待ちだけだった旧processを停止して同じscriptを独立tmux sessionで再起動。tmux serverはPPID 1で稼働し、F0 step 2,527、tuning評価30対象まで進行を確認。
- 2026-10-07 15:18 JST、F0はstep 2,533/2,789。step連番・manifest sample order・finite lossを全2,533行で再監査し不一致0。step 2,500 tuning評価は36/313対象、対象重複とnonfinite metricは0。F0 manifest未完了、tmux pipelineは待機中。
- 2026-10-07 15:22 JST、F0はstep 2,535/2,789、tuning評価38/313対象。次の固定sampleは500-frame軌跡で、30秒poll後もstepは未更新だがGPU 0使用率97%、GPU 1使用率58%で両processは稼働中。停止ではなく長尺系列処理中と判断。
- 2026-10-07 15:23 JST、F0はstep 2,538/2,789まで進行。全学習行でstep連番・manifest sample order・finite lossの不一致0件。F0 step 2,500 tuning評価は41/313対象で重複・nonfinite J/F/J&Fなし。両summary/manifestは未完了。
- 2026-10-07 15:24 JST、再監査でF0 step 2,542/2,789、step連番・sample order・finite loss不一致0。tuning評価45/313対象で重複とnonfinite J/F/J&Fは0。学習・評価processと両tmux sessionは稼働中。
- 2026-10-07 15:24 JST、F0はstep 2,545/2,789。全学習履歴をmanifestの順序と照合して異常0。step 2,500 tuning評価は49/313対象、全対象一意・全J/F/J&F finite。
- 2026-10-07 15:25 JST、F0はstep 2,545/2,789から進行中。次の対象は180-frame系列でGPU 0使用率98%。step 2,500 tuning評価は58/313対象まで進み、一意性とfinite J/F/J&Fを再確認。summaryは未完成。
- 2026-10-07 15:26 JST、F0はstep 2,548/2,789。全学習logとmanifest順の照合で不一致0、loss finite。step 2,500 tuning評価は60/313対象で一意性・finite指標に異常なし。学習・評価のtmux監視は稼働中。
- 2026-10-07 15:26 JST、F0はstep 2,550/2,789まで進行。学習全件でsample order/step/loss異常0、F0 step 2,500 tuning評価は61/313対象で一意・finite。F0 fit manifest未完了。
- 2026-10-07 15:27 JST、F0はstep 2,553/2,789。全学習履歴でstep連番・sample order・finite lossを確認し異常0。step 2,500 tuning評価は62/313対象で一意・finite J/F/J&F。学習・評価・pipelineは継続中。
- 2026-10-07 15:28 JST、F0はstep 2,555/2,789まで進行。学習log全件のstep/sample order/loss異常0。step 2,500 tuning評価は65/313対象、重複とnonfinite metricは0。F0 manifestおよび評価summaryは未完了。
- 2026-10-07 15:28 JST、F0はstep 2,557/2,789。全学習ログで連番・manifest sample order・finite lossを再確認し異常0。F0 step 2,500 tuning評価は69/313対象で重複・nonfinite metricなし。両処理は稼働中。
- 2026-10-07 15:29 JST、F0はstep 2,557/2,789で次のsampleは151-frame軌跡を処理中。step 2,500 tuning評価は72/313対象、次の対象は58-frame。log更新は直前確認以後止まっているが、両Python processはCPU約244%で稼働しており停止ではない。
- 2026-10-07 15:29 JST、F0はstep 2,559/2,789まで進行。全学習logで連番・manifest sample order・finite lossを照合して異常0。step 2,500 tuning評価は75/313対象で重複・非有限metricなし。summaryは未作成。
- 2026-10-07 15:30 JST、F0はstep 2,559/2,789で、固定sample order上の次は500-frame軌跡。trainer processはCPU約244%で稼働。step 2,500 tuning評価は82/313対象、全件uniqueでJ/F/J&F nonfinite 0。fit/tuning indexとrun manifestの件数はspecどおり2,789/313、run seedは123。
- 2026-10-07 15:31 JST、F0はstep 2,559/2,789のまま、次sampleが500-frameでtrainerはCPU約244%を使用。step 2,500 tuning評価は85/313対象、全件unique・J/F/J&F finite。長尺軌跡の処理中で両processは稼働。
- 2026-10-07 15:32 JST、F0はstep 2,562/2,789。全学習logのstep/sample order/finite lossを照合し異常0。step 2,500 tuning評価86/313対象でunique・finite。次のfit sampleは122-frame。F0 complete manifest・tuning summaryは未作成。
- 2026-10-07 15:33 JST、F0はstep 2,564/2,789まで進行。全学習logの連番・sample order・finite loss異常0。step 2,500 tuning評価は89/313対象、unique・finite。trainer/evaluatorはCPU約244%で稼働中。
- 2026-10-07 15:33 JST、F0はstep 2,565/2,789。全学習履歴のstep/sample order/finite loss異常0。F0 step 2,500 tuning評価は93/313対象でunique・finite metric。F0 manifestおよびsummary未完了。
- 2026-10-07 15:34 JST、F0はstep 2,566/2,789。全学習logで連番・固定sample order・finite loss不一致0。step 2,500 tuning評価は97/313対象、全件unique・finite。両processはCPU約244%で稼働中。次の学習対象は188-frame。
- 2026-10-07 15:42 JST、F0はstep 2,588/2,789まで進行し、全学習loss finite。step 2,500 tuning評価は138/313対象で、対象重複・nonfinite指標なし。F0 trainer、tuning evaluator、tmux recovery guard、後続pipelineはいずれも稼働中。F1 root直下の100-step logは既完了pilotであり、本学習はpipeline設定どおり`F1_full_fit/`に別出力する。pilotの先頭100軌跡でF0/F1間のsample order、記録済みflip/retry、box prompt座標・ラベルが100/100一致することを照合した。augmentationの乱数は軌跡indexとretryから決定的に作る実装。
- F1本学習の異常終了で後続pipeline全体が止まる条件を除くため、F1を最新の有効checkpointから最大10回再開する処理を`/tmp/mose_continue_pipeline_after_f0.sh`へ追加した。評価も最大5回再試行し、lockboxで中断したpartial出力は別ディレクトリへ退避してから同一条件でやり直す。F0完了待ち中にセッションを入れ替え、bash構文を再確認した。F0学習processは変更していない。
- lockbox pre-evaluation indexは200動画・570軌跡で、すべてのtrajectoryに`video_start_frame`が含まれることを確認。length-group計画は予測前作成済みで境界は短≤40、中≤70、長>70 frame。
- 2026-10-07 15:43 JST、F0はstep 2,590/2,789、step 2,500 tuning評価は141/313対象。全2,590 loss finite。F0 training/evaluation processと両tmux sessionは稼働中、F0 manifestは未完了。
- 2026-10-07 15:48 JST、F0はstep 2,602/2,789、step 2,500 tuning評価は164/313対象。F0 training lossは全件finite、学習・評価processと復旧guard/pipelineは継続中。既完了F0 tuning候補step 500〜2000は313/313対象・125/125動画を評価し、共通hashを確認済み。
- 2026-10-07 15:51 JST、F0はstep 2,612/2,789、step 2,500 tuning評価は180/313対象。学習・評価processは稼働しログ更新を確認。過去に一度観測されたF0のD状態は持続せず、30秒後は両GPU processがCPU約245%で稼働していた。
- 2026-10-07 15:54 JST、F0はstep 2,616/2,789。444-frame軌跡（video `d37e29a7`, object 3）がloss 55.12でfiniteに完走し、固定順序上の次は40-frame軌跡。step 2,500 tuning評価は193/313対象でunique・finite。F0 trainer/evaluatorとtmux guard/pipelineは稼働中。
- 2026-10-07 15:56 JST、F0はstep 2,622/2,789、step 2,500 tuning評価は206/313対象。F0全学習lossは有限・step連番、評価行はunique・finite。次の固定sampleは35-frame軌跡。F0/F1 manifestは未完了、pipelineはF0 completionを待機中。
- 2026-10-07 15:58 JST、F0はstep 2,627/2,789、step 2,500 tuning評価は215/313対象まで進行。30秒poll中にF0は3更新、評価は4対象増加し、両processとも稼働を確認。
- 2026-10-07 15:59 JST、F0はstep 2,633/2,789、step 2,500 tuning評価は222/313対象。30秒poll中にF0は2更新、評価は4対象増えた。F0 process、tuning evaluator、guard、pipelineはいずれも稼働中。
- 2026-10-07 16:02 JST、F0はstep 2,638/2,789、step 2,500 tuning評価は235/313対象。F0 lossは有限でstep連番、評価行はuniqueかつfinite。checkpoint selection未実施で、lockbox freeze/condition出力がまだなく、事前固定したlockbox plan（200動画・570対象、群境界40/70 frame）は未消費。
- 2026-10-07 16:04 JST、F0はstep 2,646/2,789、step 2,500 tuning評価は257/313対象。30秒poll中にF0は4更新、評価は5対象増加。両processは稼働し、F0 lossと評価metricはfiniteのまま。
- 2026-10-07 16:10 JST、同一のF0 trainer/evaluator PIDとtmux recovery guard/pipelineの稼働を再確認。F0はstep 2,664/2,789、step 2,500 tuning出力は272/313対象へ進行。出力済み272対象を再走査し、video/object重複0・J/F/J&F nonfinite 0を確認した。両GPUで利用率を観測し、F0 training logはstep 2,664まで更新。F0完了・checkpoint selection前なのでlockboxは未消費。
- 2026-10-07 16:12 JST、同一trainer/evaluatorとtmux guard/pipelineが継続稼働。F0はstep 2,668/2,789、step 2,500 tuning評価は283/313対象。F0学習ログ全2,668行を検査し、step 1〜2,668の連番・finite lossを確認。tuning出力283件は対象重複0・J/F/J&F nonfinite 0。F0完了・候補選択前のためlockbox評価は未開始。
- 2026-10-07 16:12 JST（再確認）、F0はstep 2,672/2,789、step 2,500 tuning評価は284/313対象。同一trainer/evaluatorとtmux guard/pipelineが稼働し、学習ログ全2,672行は連番・finite loss、tuning出力284件は対象重複0・J/F/J&F nonfinite 0。F0および候補選択は未完了、lockboxは未開始。
- 2026-10-07 16:14 JST、同じtrainer/evaluatorとtmux guard/pipelineを再確認。F0はstep 2,677/2,789、step 2,500 tuning評価は288/313対象。学習ログ全件が連番・finite loss、評価288件は対象一意・J/F/J&F finite。直近の評価対象は266-frame軌跡で、長尺対象の処理中に評価件数が進んでいることを確認した。F0完了・候補選択前につきlockbox未開始。
- 2026-10-07 16:16 JST、trainer/evaluatorとtmux guard/pipelineの生存を確認。F0はstep 2,679で長尺軌跡の計算が続き学習log未更新だが、GPU使用率とCPU稼働は継続。tuning出力は288から289対象に増え、全289件で対象一意・J/F/J&F finite。F0完了・候補選択前につきlockbox未開始。
- 2026-10-07 16:18 JST、500-frame軌跡（video `85aa3b0e`, object 9）がstep 2,680でfinite loss 0.1938にて完了。F0はstep 2,686/2,789、step 2,500 tuning評価293/313対象。全学習ログ2,686行はstep連番・finite loss、評価293件は対象一意・J/F/J&F finite。trainer/evaluatorとtmux guard/pipeline稼働、候補選択・lockbox評価は未実施。
- 2026-10-07 16:19 JST、F0はstep 2,689/2,789、step 2,500 tuning評価は298/313対象。F0学習ログ2,689行は連番・finite loss、評価298件は一意・J/F/J&F finite。F0 trainer/evaluatorおよびrecovery guard/pipelineは稼働中。F0完了・候補選択前につきlockbox未開始。
- 2026-10-07 16:20 JST、F0はstep 2,691/2,789、step 2,500 tuning評価303/313対象。同一trainer/evaluatorとtmux recovery guard/pipelineが稼働中。F0ログ2691件はstep連番・finite loss、tuning出力303件は対象一意・J/F/J&F finite。2700 checkpoint以降の候補選択とlockbox評価は未開始。
- 2026-10-07 16:22 JST、F0はstep 2,691のままで、固定順序の次対象は500-frame軌跡（video `85aa3b0e`, object 6）。GPU利用率は両GPUで高く、trainerは処理中。F0 step 2,500のtuning評価は309/313対象で、全件一意・J/F/J&F finite。trainer/evaluator・recovery guard・pipeline稼働中、候補選択とlockboxは未開始。
- 2026-10-07 16:23 JST、F0 step 2,500 tuning評価が完了。313/313対象・125/125動画、frame0開始313、空mask除外0、全オブジェクトmetricはfiniteかつ一意。動画平均J=0.73270、F=0.80596、J&F=0.76933。checkpoint SHA256 `b3b20c464d48e5d7c137699d07beaaa7cdfb8f476f3a9c2c780c07245e04612c`。F0学習はstep 2,697/2,789で継続中、ログ全件連番・finite loss。選択対象のstep 2,789 checkpointは未作成、候補選択・lockbox評価は未実施。
- 2026-10-07 16:24 JST、F0はstep 2,702/2,789で継続。step 2,700 checkpointをCPUでloadし、`condition=F0`, `split=fit`, `seed=123`, `sample_order=2,789`, model state keys=519, optimizer groups=4を確認。F0学習ログは少なくともstep 2,701まで連番・finite lossで、最新step 2,702もfinite。step 2,500 tuning summaryは313対象・125動画で完了済み。F0 fit完了manifestと候補選択は未作成、pipeline/guard稼働中。
- 2026-10-07 16:27 JST、F0はstep 2,711/2,789。学習ログ全2,711行は連番・finite loss。loss分布はmedian 0.2788、p95 3.5934、p99 58.4133、max 842.2005、100超22件で複数trajectoryに分散。step 2,700 checkpointのmodel tensorとAdam optimizer state tensor 1,515個を走査し、nonfiniteは双方0。実装のgradient clip norm=0.1を確認。step 2,500 tuning評価は313対象・125動画で完了、F0 fit完了と候補選択は未実施。
- 2026-10-07 16:28 JST、F0学習はstep 2,716/2,789。tuning候補step 500/1000/1500/2000/2500はすべて313対象・125動画、later-first 0、excluded 0。各summaryのcheckpoint SHA256が実体と一致し、selectorが要求する固定trajectory index、evaluator/base checkpoint hashも同一。video-mean J&Fは順に0.753188/0.754065/0.757563/0.762079/0.769332で、現時点ではstep2500が最高。step2789評価後に同じselectorで選定予定。
- 2026-10-07 16:30 JST、F0はstep 2,720/2,789。学習ログ全2,720行は連番・finite loss。F0 trainer、recovery guard、pipelineは稼働中。候補step 500〜2,500のcoverage/hash監査済み、最高J&Fはstep2500=0.769332。step2789候補とselector実行は未完了。
- 2026-10-07 16:33 JST、F0はstep 2,725/2,789。学習ログ全2,725件を再走査し、連番・finite lossを確認。F0 trainerとrecovery guard/pipeline稼働中。step 2,500までの候補評価は完了、step 2,789評価・selector・F1 fitは未開始。
- 2026-10-07 16:35 JST、F0はstep 2,733/2,789。学習ログ全2,733行は連番・finite loss。trainer/recovery guard/pipelineは継続稼働。step 2,500までのF0 tuning候補は全件評価済み、step 2,789候補・selector・F1 fitは未開始。
- 2026-10-07 16:37 JST、F0はstep 2,739/2,789。trainer・recovery guard・pipelineが継続稼働し、学習ログ全2,739件は連番・finite loss。F0 tuning候補500〜2500は監査済みで、最終候補2789・selector・F1 fitは未開始。
- 2026-10-07 16:38 JST、F0はstep 2,742/2,789。学習ログ全2,742行はstep連番・finite loss。step 2,740の192-frame trajectoryはloss 0.8686で完了。trainer/recovery guard/pipeline継続中、最終候補2789・selector・F1 fitは未開始。
- 2026-10-07 16:40 JST、F0はstep 2,749/2,789。全学習ログ2,749件は連番・finite loss。F0 trainerとrecovery guard/pipeline稼働中。step 2,500までのtuning候補評価は全件完了、step 2,789候補・selector・F1 fitは未開始。
- 2026-10-07 16:43 JST、F0はstep 2,755/2,789。学習ログ全2,755件は連番・finite loss。trainer、recovery guard、pipelineは稼働中。F0候補500〜2500は評価済みで、最終checkpoint評価・selector・F1 fitは未開始。
- 2026-10-07 16:45 JST、F0はstep 2,761/2,789。学習ログ全2,761件を走査し、step連番・finite lossを確認。trainer/recovery guard/pipelineは稼働中。候補500〜2500のF0 tuningは完了済み、step2789候補評価・selector・F1 fitは未開始。
- 2026-10-07 16:47 JST、F0はstep 2,771/2,789。学習ログ全2,771件はstep連番・finite loss。F0 trainerとrecovery guard/pipeline稼働中。step 2,789 checkpointとそのtuning評価・selector・F1 fitは未開始。
- 2026-10-07 16:55 JST、F0 full fit完了（2,789/2,789）。学習ログ全件を再走査しstep 1〜2,789が連番、nonfinite loss 0。最終checkpointは`condition=F0`, `split=fit`, seed 123, sample order 2,789。model tensor nonfinite 0、Adam state tensor 1,515個のnonfinite 0。pipelineはGPU0 idle後にF1 fitを開始する段階。F0 step2789 tuning評価・checkpoint selectionは未完了、lockbox未消費。
- 2026-10-07 16:58 JST、F0 step 2,789のtuning評価が開始しobjects出力8/313。F1 full fit processもCUDA0で起動、F0 final evaluatorはCUDA1で稼働中。pipeline detached sessionは継続、F0/F1 selectorおよびlockbox評価は未完了。
- 2026-10-07 17:00 JST、F0 step 2,789 tuning出力24/313対象、部分結果は対象一意・J/F/J&F finite。F1 fitはindex作成中で100/1,121動画・218 object trajectoryまで出力。両processとpipelineが稼働中、候補selection・lockbox未完了。
- 2026-10-07 17:02 JST、F0 step 2,789 tuning評価は31/313対象で、全行対象一意・J/F/J&F finite。F1 fit indexは200/1,121動画・495 object trajectory。F0 final evaluator、F1 trainer、pipelineの同一PID稼働を確認。selector・lockbox未完了。
- 2026-10-07 17:03 JST、F0 step 2,789 tuning評価は35/313対象で、35件すべて一意・J/F/J&F finite。F1 fit indexは300/1,121動画・743 object trajectory。F0 evaluator、F1 fit process、pipeline継続稼働。selector/lockbox未完了。
- 2026-10-07 17:05 JST、F0 step 2,789 tuning評価37/313対象、部分metricはすべてunique・finite。F1 fit indexは400/1,121動画・1,002 object trajectory。F1 processはannotation PNGを継続読込しindex進捗が300から400へ更新。F0 evaluator/F1 trainer/pipeline稼働、selector/lockbox未完了。
- 2026-10-07 17:09 JST、F0 step 2,789 tuning評価は47/313対象まで進み、出力済み行は重複なく指標finite。F1 fit indexは600/1,121動画・1,557 object trajectory。F0 evaluator（PID 897662）、F1 fit process（PID 897885）、detached pipeline（PID 878216）は生存し、直近45秒で評価対象数が43から47、indexが500から600動画へ増加。F1はデータindex作成中で学習log/checkpointはまだ未出力。checkpoint selection・lockbox未完了。
- 2026-10-07 17:14 JST、F0 step 2,789 tuning評価71/313対象。全71行でvideo/object一意、J/F/J&F nonfinite 0。F1 fit indexは800/1,121動画・1,994 object trajectory。直近60秒でF0出力が62から71対象、F1 indexが700から800動画へ増加し、trainer/evaluator/pipelineは同じPIDで稼働。F1 index作成は継続中で学習log/checkpoint未出力、候補選択・lockbox評価は未完了。
- 2026-10-07 17:20 JST、F1 fit indexが1,121/1,121動画・2,789軌跡で完了し、training logがstep 1〜4まで生成。run manifestはcondition=F1、split=fit、seed=123、chunk_len=8、sample_order長2,789。最初の4軌跡はmanifest順と一致し、lossは全件finite。F0 step 2,789 tuning評価は104/313対象でunique・finite。F0 evaluator（PID 897662）、F1 trainer（PID 897885）、detached pipeline（PID 878216）は継続稼働中。F1 checkpoint intervalは100のためまだcheckpointなし。selector・lockbox未完了。
- 2026-10-07 17:22 JST、F1 fitはstep 11/2,789。log step 1〜11は連番、manifest sample orderと一致し、loss nonfinite 0。F0 step 2,789 tuning評価111/313件はvideo/object一意・全metric finite。F0 evaluator/F1 trainer/detached pipelineは稼働中。F1最初の保存checkpointはstep100を予定。候補選択・lockbox評価は未完了。
- 2026-10-07 17:25 JST、F1 fitはstep 15/2,789。学習log全15件は連番・manifest順一致・finite loss。F0 step 2,789 tuning評価127/313対象でunique・finite。F0 evaluator（PID 897662）、F1 trainer（PID 897885）、pipeline（PID 878216）は稼働継続。F1 checkpointはまだ100-step間隔に未到達。lockboxは未開始。
- 2026-10-07 17:27 JST、F1 fitはstep 22/2,789、学習logはstep連番・manifest順一致・finite loss。F0 step 2,789 tuningは139/313対象、出力済みmetricsはfinite。F0 tuning候補500〜2,500のsummaryを実ファイルで再監査し、各313対象/125動画、objects出力313行、checkpoint SHA-256一致、evaluator hash・trajectory index hash共通を確認。現時点の最高動画平均J&Fはstep2500=0.769332。selectorはstep2789評価完了後に実行するため未実行。lockbox freezeなし・lockbox出力なし。
- 2026-10-07 17:29 JST、F0最終候補評価144/313対象、F1 full fit step28/2,789。F1学習logは連番・manifest順一致・finite lossで、最後に完了したstep28（36 frame）のlossは0.1399。両学習/評価processとpipelineが継続稼働。100-step checkpointは未到達。候補選択・lockbox評価は未完了。
- 2026-10-07 17:32 JST、F0最終候補は160/313対象、出力済み指標finite・対象一意。F1 fitはstep39/2,789で、全39 stepが連番・manifest順一致・finite loss。PID 897662（F0 tuning）、897885（F1 fit）、878216（pipeline）は稼働中。F0 final summaryとF1 step100 checkpointは未作成、selection/lockboxは未開始。
- 2026-10-07 17:33 JST、F0最終候補評価167/313件で全件unique・finite。F1 fitはstep43/2,789、全stepが連番・manifest順一致・finite loss。3つの実プロセス（F0 evaluator PID 897662、F1 trainer PID 897885、pipeline PID 878216）は継続稼働。F0 final summary・F1 step100 checkpoint未到達、selectorとlockbox未開始。
- 2026-10-07 17:36 JST、F0最終候補評価181/313、F1学習step49/2,789まで進行。直近60秒でF0は173→181、F1は45→49に増加。現時点の全F0出力は対象uniqueかつfinite、F1 logは連番・manifest順一致・finite loss。両プロセスとdetached pipeline稼働中。F1 checkpoint step100、F0最終summary、selector、lockbox評価は未完了。
- 2026-10-07 17:39 JST、F0 step2789 tuningは192/313、F1 fitはstep57/2,789。直近1分にF0は+7対象、F1は+4 step進行し、両方の出力はfinite。F1 checkpoint interval=100未到達で、selector・lockbox評価は未開始。
- 2026-10-07 17:41 JST、F0 step2789 tuningは208/313対象、F1 fit step59/2,789。F0出力は対象unique・全指標finite。F1 logはstep連番・sample order一致・finite loss。F0 evaluator/F1 trainer/pipelineの各PIDは生存しCPU処理中。F1 checkpoint step100、F0最終summary、selector、lockbox未完了。
- 2026-10-07 17:44 JST、F0最終候補は219/313対象、F1学習はstep65/2,789まで進行。F0全出力対象はunique・finite、F1 lossは全step finiteで連番を維持。F1 step59/60は各300 frameの長尺軌跡を処理完了。F0 evaluator、F1 trainer、tmux pipelineは稼働中。100-step checkpoint未到達、F0 summary/selector/lockbox未完了。
- 2026-10-07 17:49 JST、F0 step2789 tuning評価256/313、F1 fitはstep77/2,789。F0出力は対象一意・metric finite、F1 logは連番・manifest順一致・finite loss。F0 evaluator/F1 trainer/detached pipeline稼働中。F0 summary・F1 step100 checkpoint未作成、selector・lockbox未開始。
- 2026-10-07 17:53 JST、F0 step2789 tuning評価267/313対象、F1 fit step86/2,789。出力済みF0対象は一意・指標finite、F1 logは連番・manifest順・finite lossを維持。F0 evaluator、F1 trainer、detached pipeline稼働中。F1 step100 checkpointとF0最終summaryは未作成、selector/lockbox未開始。
- 2026-10-07 18:01 JST、F1 fitはstep107/2,789、F0 step2789 tuningは289/313対象。step100 checkpointをCPU load監査し、condition=F1/split=fit/seed=123/step=100、sample_order 2,789件、model 533 tensor・optimizer 1,551 tensorともnonfinite 0を確認。checkpoint sample orderとmanifest、step100 logのvideo-objectが一致し、adapter alphaは0以外（8.78e-5）。preflight step後の次backwardではMamba gradient 1.95e-9がfiniteで到達済み。F0残り24件、summary・selector・lockbox未完了。F0/F1/pipeline processは稼働。
- 2026-10-07 18:08 JST、F0 step2789 tuning評価完了（313/313対象・125/125動画、later-first 0、除外0、全metric finite・unique）。selectorが6候補を同じ評価コード/base checkpoint/trajectory indexで検証し、すべてcheckpoint SHA-256一致。動画等重み平均J&Fはstep500 0.753188、1000 0.754065、1500 0.757563、2000 0.762079、2500 0.769332、2789 0.770081で、F0 step2789を選択。F1 fitはstep126/2,789、ログfiniteで継続中。lockbox freezeなし・lockbox出力0件のまま。
- 2026-10-07 18:09 JST、F1 fitはstep129/2,789まで進みloss finite。F0 checkpoint選択後のtraining-prompt exportをGPU1で開始し、2,789対象中200対象を再構成。F1 trainer・prompt exporter・pipelineは同時稼働中。F1 tuning/selectionとlockbox freeze/evaluationは未実施。
- 2026-10-07 18:14 JST、F1 fitはstep147/2,789、training log全件finite。F0-selected checkpointからのtraining-prompt exportは1,700/2,789軌跡まで再構成。F1 trainer/PID 897885、prompt exporter/PID 912439、pipeline/PID 878216は稼働継続。prompt manifest未作成のためF1 tuning開始前、lockbox未消費。
- 2026-10-07 18:18 JST、F0 training-prompt export完了し2,789行/2,789軌跡、video-objectとtrajectory_indexは全件一意。export順はF1 manifestのtrajectory・augmentation seed順に2,789/2,789一致。F0全学習ログ2,789件とはvideo/object/retryが全件一致し、F1学習済み150件とはvideo/object/retry/prompt coordinates/labels/augmentation seedが150/150一致。F1 fitはstep150/2,789でfinite lossを維持。F1 trainingは継続し、tuning候補評価・selector・lockbox freeze/evaluationはまだ未開始。
- 2026-10-07 18:23 JST、F1 fitはstep162/2,789まで進行。全学習logは連番、F1 manifest順一致、finite loss。F1_step_000100.ptは存在し、次checkpointはstep200。現在の次sampleは156 frame。F1学習pipelineは稼働し、F1 tuning/selection・lockbox freeze/evaluationは未開始。
- 2026-10-07 18:26 JST、F1 fitはstep175/2,789。直近logは連番・manifest順一致・finite loss。GPU0を使用して同一trainerが稼働中（GPU0 utilization 27%、21.5 GiBメモリ使用）、GPU1はidle。checkpointはstep100のみ。F1 tuning/selection・lockbox未開始。
- 2026-10-07 18:28 JST、F1 fitはstep182/2,789、logは連番・manifest順一致・finite loss。trainer PID 897885およびpipeline PID 878216は継続稼働。step100 checkpointから継続中で、F1 tuning/selection・lockbox未開始。
- 2026-10-07 18:35 JST、F1 fitはstep200/2,789に到達し、step200 checkpointをCPU監査。condition/split/seed/stepがF1/fit/123/200、checkpoint内sample orderとfit manifestが2,789/2,789一致、学習logの先頭200行も固定trajectoryのvideo/object順と200/200一致。loss finite 200/200、model 533 tensor・optimizer 1,551 tensorともnonfinite 0。checkpoint SHA-256は`847bd8bd574a2b1ee70f0ddfe59f7a1516923734328e7d104f46fcb95c01c191`。tmux pipelineとtrainer PIDは稼働継続。F1 tuning/selectionおよびlockbox freeze/evaluationは未開始。
- 2026-10-07 18:39 JST、F1 fitはstep206/2,789。GPU1が空いていることを確認し、既存pipelineと同じ評価entrypoint・条件でstep500/1000/1500/2000/2500のtuning評価queueを独立tmux sessionで開始。checkpoint書き込み完了をlog stepとファイルサイズ安定で確認してから評価し、失敗時は最大5回再試行する。step2789候補はfull fit完了後に既存pipelineが評価する。lockboxは未消費。
- 2026-10-07 18:42 JST、F1 fit logはstep214で更新待ち。manifest順で次の軌跡はvideo `85aa3b0e`, object 2、500 frame（0〜499）。trainer PID 897885はCPU/GPUを使用して稼働中であり、長尺軌跡処理中のため停止ではないことを確認。tuning queueはstep500 checkpoint待機中、lockbox評価出力は0件。
- 2026-10-07 18:44 JST、500-frame軌跡（video `85aa3b0e`, object 2）がstep215でloss 0.11423にてfinite完走。F1 fitはstep219/2,789まで進み、trainer/pipelineは稼働中。GPU1 tuning queueは引き続きstep500 checkpoint待機、lockbox未消費。
- 2026-10-07 18:53 JST、F1 fitはstep249/2,789。学習log全249行を再監査し、step連番、manifest video/object順、trajectory frame数、finite lossがすべて一致。trainer PID 897885とpipeline PID 878216は稼働中。GPU1 tuning queueはstep500 checkpoint待機、lockbox freeze/outputなし。
- 2026-10-07 19:00 JST、F1 fitは少なくともstep263/2,789。全263学習log行を再走査し、連番・manifest video/object/frame count一致・finite lossを確認。trainer PID 897885とpipeline PID 878216が稼働し、GPU1 queueはstep500 checkpoint待機中。lockboxは未使用。
- 2026-10-07 19:04 JST、F1 fitはstep275/2,789。step272で500-frame軌跡（video `c2e88575`, object 2）がloss 2.85045にてfinite完走し、その後step275までログ更新。trainerとpipelineは稼働中、GPU1 tuning queueはstep500 checkpoint待機、lockboxは未使用。
- 2026-10-07 19:09 JST、F1 fitはstep289/2,789。評価コードをspecと照合し、F1-resetが各frame前にMamba stateのみresetしSAM2 memoryを保持すること、t0除外とempty-mask規則がコード上で成立することを確認。empty/emptyはJ=F=1、片側emptyはJ=F=0の関数確認も通過。GPU1 tuning queueはstep500待機、lockbox未使用。
- 2026-10-07 19:13 JST、F1はstep302/2,789、step300 checkpointを監査。condition/split/seed/stepがF1/fit/123/300、sample orderがmanifestと2,789/2,789一致。model 533 tensor、optimizer 1,551 tensorのnonfiniteは双方0。alpha=1.43324e-4、checkpoint SHA-256 `88e69fcabfbed86112ce01b4719982f795579994900f34760fba2af9e1e54e94`。学習log先頭300件は連番・manifest video/object/trajectory長一致・finite loss。GPU1 tuning queueはstep500待機、lockbox未使用。
- 2026-10-07 19:20 JST、F1はstep325/2,789。学習log全325行をmanifestと再照合し、step連番・video/object/trajectory frame数一致・loss finiteを確認。trainer/PID 897885継続稼働。GPU1 tuning queueはstep500 checkpoint待機、F1 tuning summaryは未作成、lockbox未使用。
- 2026-10-07 19:24 JST、F1はstep334/2,789。全334 log行でstep連番・manifest video/object/frame数一致・finite lossを確認。loss median 0.3064、p95 1.9682、p99 17.2234、max 21.3806、loss>10は6件、>100は0件。trainer稼働、GPU1 queueはstep500待機、lockbox未使用。
- 2026-10-07 19:28 JST、F1はstep350/2,789。全350 log行をmanifestと照合し、step連番・video/object/trajectory frame数一致・finite lossを確認。loss median 0.3071、p95 1.9981、p99 17.1026、max 21.3806。trainer/PID 897885稼働、GPU1 queueはstep500待機、lockbox未使用。
- 2026-10-07 19:39 JST、F1はstep381/2,789。全381 log行のstep連番・manifest sample orderとのvideo/object一致・finite lossを確認。trainer PID 897885、detached pipeline PID 878216、GPU1 tuning queue PID 918594が稼働中。最新checkpointはstep300で、step400保存・step500 tuning候補評価を待機。F1 tuning summary、selector、lockbox freeze/evaluationは未完了。
- 2026-10-07 19:47 JST、F1はstep405/2,789。step400 checkpoint (`e7147d8f…b2539bff3`) を監査し、condition/split/seed/step=F1/fit/123/400、2,789 trajectory indexがmanifestと完全一致。model 533 tensor・optimizer 1,551 tensorともnonfinite 0、adapter alpha=1.54633e-4。学習log先頭400行は連番・manifest video/object/frame数と一致しloss finite。trainer/pipeline稼働中、GPU1 tuning queueはstep500待機。lockbox未使用。
- 2026-10-07 19:49 JST、F1 fit logはstep409/2,789まで進み、409件すべてfinite。loss median 0.3057、p95 2.4234、p99 17.9640、max 185.721（step395）、loss>10は9件・>100は1件。step395はF0でもloss 185.585だった同じvideo `d48c552d` object 3（71 frames、flip=false、再試行なし）。既存annotation scanでは20 frameの空GTとframe31からの再出現を確認済み。両runでfiniteに完了しており、原因は断定せず設定変更なし。F1 trainer/pipeline稼働、GPU1 queueはstep500待機、lockbox未使用。
- 2026-10-07 19:51 JST、F1 fit logはstep419/2,789。step 1〜419すべてで、F0由来training-prompt exportとのstep/video/object、augmentation retry、prompt coordinates/labelsが一致。step416のretry index 5もexportと同じpromptを再現し、finiteな座標を確認。再試行処理の再現性に不整合なし。F1学習/pipeline稼働、GPU1 queueはstep500待機中。
- 2026-10-07 19:52 JST、F1 fit開始時manifestの`implementation_sha256` 8ファイルを現在のworktreeと再照合し、hash mismatch 0。学習中に実装対象ファイルが変わっていないことを確認。lockbox freeze前の実装同一性チェックに使える。F1 fitはstep420/2,789、候補評価queueはstep500待機。
- 2026-10-07 19:53 JST、lockboxをまだ実行していない状態で事前length planを再検証。200動画・570軌跡すべてのgroup割当がannotation由来indexと一致し、全対象t0=0。nearest-method tercile境界は40/70 frame、group数short/medium/long=219/163/188。planのtrajectory index SHA-256一致、全対象を重複・欠落なく割当済み。freeze file・lockbox prediction出力は未作成のまま。F1 fit step424/2,789、候補評価queueはstep500待機。
- 2026-10-07 19:57 JST、F1 fitはstep435/2,789。step 1〜435で連番、manifest上のvideo/objectと軌跡長、finite loss/LRを確認。F0由来prompt exportとのbox coordinates/labelsとaugmentation retryも全435件一致。trainer、detached pipeline、GPU1 tuning queueは稼働し、step500候補評価待ち。lockbox未使用。
- 2026-10-07 20:03 JST、F1 fitはstep445/2,789。log全445行でstep連番、manifest video/object・軌跡frame数、finite loss/LRを確認。F0 prompt exportとのaugmentation retry/box coordinates/labelsも445件すべて一致。step444の108-frame軌跡がfinite lossで完了。trainer/pipelineとGPU1 queue稼働中、step500候補評価待ち。lockbox未使用。
- 2026-10-07 20:06 JST、F1 fitはstep451/2,789。全451行でstep連番、manifest video/object/軌跡長一致、finite loss/LR、F0由来prompt export一致を確認。step447の300-frame軌跡もloss 0.1095で完走。step448はF0でも高lossだったvideo `5ae23f9f` object 1（39 frames）で、F1 loss 46.45 / F0 loss 46.26、augmentationもflip=true/retry=0で一致。既存annotation scanで末尾空maskと小領域再出現を確認済み。設定は変更せず評価で影響を確認する。最大lossはstep395の185.72のまま。GPU1 queueはstep500待機、lockbox未使用。
- 2026-10-07 20:10 JST、F1 fitはstep463/2,789。log全463行のstep連番・manifest video/objectとframe数・finite loss/LRを確認し、F0 prompt exportとのaugmentation retry/coordinates/labelsも全件一致。trainer/pipeline/queueが稼働中。GPU1 queueはstep500 checkpoint待機、F1 candidate evaluationとlockboxは未開始。
- 2026-10-07 20:13 JST、F1 fitはstep469/2,789。log全469行でsample order、trajectory長、finite loss/LR、F0 prompt export replayが一致。step464で最長500-frame軌跡（video `c2e88575`, object 3）をloss 0.14393で完走し、長時間state carryもfinite。F1 trainer/pipeline稼働、GPU1 queueはstep500 checkpoint待ち。lockbox未使用。
- 2026-10-07 20:16 JST、F1 fitはstep478/2,789。全478行でstep連番、manifest video/object・軌跡長、finite loss/LR、F0由来prompt export replayが一致。trainer/pipeline/queueは継続稼働中。step500 checkpointは未作成、GPU1 queueはstep500候補を待機。lockbox未使用。
- 2026-10-07 20:20 JST、F1 fitはstep480/2,789。全480行でstep連番、manifest/sample length、finite loss/LR、prompt replayが一致。step479で別の500-frame軌跡（video `c2e88575`, object 9）をloss 2.4938で完走。500-frame完走例はF1内で4件。GPU1 queueはstep500 checkpoint待機、lockbox未使用。
- 2026-10-07 20:28 JST、F1 fitはstep506/2,789。step500 checkpoint (`d781cc1d…77c8944b`) を監査し、condition/split/seed/step=F1/fit/123/500、manifest trajectory order一致、model 533 tensorとoptimizer 1,551 tensorのnonfinite 0、alpha=1.32078e-4。学習log/prompt replayはstep500までsample order・trajectory length・finite loss/LRを含め一致。GPU1でstep500 tuning評価を開始し、最初の6 object metricsはfinite。F1 fitは続行、lockbox未使用。
- 2026-10-07 20:30 JST、F1 fitはstep509/2,789まで進行。step500 tuning評価objects.jsonlは18/313対象。途中出力を監査し、対象はすべてtuning index内で一意、J/F/J&Fはfiniteかつ[0,1]内。GPU1 evaluatorとGPU0 F1 trainerは並行稼働中。lockboxは未使用。
- 2026-10-07 20:34 JST、F1 fit process 897885とstep500 tuning evaluator 955122を再確認し、両方稼働中。F1 fitはstep519/2,789。step500評価はobjects.jsonl 34/313件で、34件すべてvideo/objectが一意、frame0開始、J/F/J&Fはfiniteかつ[0,1]内。tmuxのpipeline・tuning queueも稼働中。lockbox freezeと評価出力は未作成で未消費。
- 2026-10-07 20:36 JST、同じF1 fit/evaluator PIDが継続稼働し、fit logはstep526、step500 tuning途中出力は37/313件へ進行。前回の34件から追加3件。lockboxは未消費。
- 2026-10-07 20:38 JST、F1 fitはstep529/2,789、step500 tuning途中出力38/313件。F1学習log全529行のstep連番・finite loss/LRを確認し、固定sample orderとF0 prompt replay（retry、coords、labels）の不一致は0。tuning途中38件は一意・frame0開始・J/F/J&Fがfiniteかつ[0,1]内。学習/evaluatorの同一PIDとGPU稼働を確認、lockbox未消費。
- 2026-10-07 20:39 JST、F1 fitはstep533/2,789、step500 tuning出力44/313件。全学習logはstep連番・finite loss/LRで、manifest sample orderとF0 prompt replay（retry、coords、labels）の不一致0。評価44件も一意・frame0開始・J/F/J&Fがfiniteかつ[0,1]内。学習・評価processは継続中、lockbox未消費。
- 2026-10-07 20:40 JST、F1 fitはstep537/2,789、step500 tuning出力47/313件。全537学習log行の連番・finite loss/LR、manifest順、F0 prompt replayを監査し不一致0。評価47件はunique・frame0開始・J/F/J&Fがfiniteかつ[0,1]内。F1 fitと評価processの継続を確認し、lockboxは未消費。
- 2026-10-07 20:42 JST、F1 fitはstep540/2,789、step500 tuning出力58/313件。全学習行は連番・finite loss/LR、評価58件は一意・frame0開始・J/F/J&F valid。学習PID 897885と評価PID 955122が継続稼働。lockbox未消費。
- 2026-10-07 20:43 JST、F1 fitはstep546/2,789、step500 tuning出力62/313件。学習全logの連番・finite loss/LR、manifest sample順とF0 prompt replayが一致。評価62件は一意・frame0開始・J/F/J&F valid。GPU0 trainerとGPU1 evaluatorが稼働中、lockbox未消費。
- 2026-10-07 20:46 JST、F1 fitはstep553/2,789、step500 tuning出力73/313件。全学習logは連番・finite loss/LRでsample order・prompt replay不一致0。評価73件は対象一意・frame0開始・J/F/J&F valid。学習/evaluatorは同一PIDで継続稼働し、lockbox未消費。
- 2026-10-07 20:47 JST、F1 fitはstep557/2,789、step500 tuning出力84/313件。学習logはstep連番・finite loss/LR、評価出力は対象一意・frame0開始・J/F/J&F valid。trainer/evaluatorが稼働し、lockbox未消費。
- 2026-10-07 20:49 JST、F1 fitはstep564/2,789、step500 tuning出力87/313件。学習全行は連番・finite loss/LR、評価行は対象一意・frame0開始・J/F/J&Fが[0,1]内。学習・評価PIDは継続稼働、lockboxは未消費。
- 2026-10-07 20:50 JST、F1 fitはstep569/2,789、step500 tuning出力94/313件。学習log全行は連番・有限loss/LR、評価94件は一意・frame0開始・J/F/J&Fがfiniteかつ[0,1]内。F1 fit/evaluator稼働中。manifest内の実装ファイルhashは全て一致、lockbox未消費。
- 2026-10-07 20:52 JST、F1 fitはstep572/2,789、step500 tuning出力102/313件。学習log全行の連番・finite loss/LRと評価102件の一意性・frame0開始・finite/in-range J/F/J&Fを再確認。両プロセス稼働中、lockbox未消費。
- 2026-10-07 20:54 JST、F1 fitはstep577/2,789、step500 tuning出力108/313件。学習logは全577行連番・finite、評価108件は一意・frame0開始・finite/in-range指標。step573の300-frame軌跡をfinite lossで完了し、学習・評価processは継続稼働。lockbox未消費。
- 2026-10-07 20:56 JST、F1 fitはstep579/2,789、step500 tuning出力119/313件。全学習行のstep連番・finite loss/LRと評価行の一意性・frame0開始・有限範囲指標を確認。352-frame軌跡もfinite lossで完了。trainer/evaluatorは稼働中、lockbox未消費。
- 2026-10-07 20:57 JST、F1 fitはstep583/2,789、step500 tuning出力126/313件。学習全logは連番・finite、sample orderとF0 prompt replay一致。評価126件は一意・frame0開始・J/F/J&F valid。fit開始から約4時間、単純平均ペースで全学習約19時間・残り約15時間、直近ペースでは残り約14時間の概算。系列長で変動するため残り14〜16時間程度を目安とする。これはfitのみで、checkpoint tuningとlockbox評価時間を含まない。
- 2026-10-07 20:59 JST、F1 fitはstep586/2,789、step500 tuning出力135/313件。fit log全行はstep連番・finite loss/LR、候補評価135件は一意・frame0開始・finite/in-range指標。GPU0学習・GPU1評価は稼働中。概算fit残時間14時間前後、tuning/lockbox時間は別途。
- 2026-10-07 21:02 JST、F1 fitはstep587/2,789、step500 tuning出力143/313件。学習ログ全件はstep連番・finite loss/LR、sample orderとF0 prompt replay一致。評価143件は一意・frame0開始・J/F/J&F valid。trainerとevaluatorは継続稼働、lockbox未消費。
- 2026-10-07 21:02 JST（再監査）、F1 fitはstep590/2,789、step500 tuning出力145/313件。学習logは全件連番・finiteでmanifest順とprompt replay完全一致。tuning出力145件はindexの期待対象順のprefixに完全一致し、対象別指標は全てvalid。両process稼働中、lockbox未消費。
- 2026-10-07 21:06 JST、F1 fitはstep595/2,789、step500 tuning出力167/313件。学習全logは連番・finite loss/LRでsample orderとF0 prompt replay完全一致。評価167件はindex期待順のprefixと一致し、J/F/J&Fはvalid。GPU上で学習・評価が継続中、lockbox未消費。
- 2026-10-07 21:08 JST、F1 fitはstep595/2,789、step500 tuning出力172/313件。最新step595は500-frame軌跡をloss finiteで完了。全学習logは連番・finite、manifest order/prompt replay一致。tuning出力172件はindex順prefix一致・metrics valid。次のstep596も500-frame軌跡。学習・評価processは稼働中、lockbox未消費。
- 2026-10-07 21:13 JST、step600 checkpoint (`64c8f580e96577b07c4040f075dd248b4022c276bf58483620c778cc3a6f42c0`) を監査。condition/split/seed/step=F1/fit/123/600、2,789件の固定sample order一致、model 533 tensor・optimizer 1,551 tensorにnonfiniteなし。adapter alpha=6.81582e-5。学習log全604行は連番・finite・prompt replay一致。step500 tuning評価197/313件はindex順prefix・unique・valid。学習/evaluation継続、lockbox未消費。
- 2026-10-07 21:14 JST、F1 fitはstep608/2,789、step500 tuning評価203/313件。全学習logは連番・finite loss/LR、manifest order・F0 prompt replay一致。評価203件はindex順prefixに一致し、指標は全てvalid。trainerとevaluatorが稼働中、lockbox未消費。
- 2026-10-07 21:15 JST、F1 fitはstep609/2,789、step500 tuning評価207/313件。全学習logのstep連番・finite loss/LR、sample orderとprompt replay一致を確認。評価207件は期待index順prefixに一致しunique・valid。両process稼働中、lockbox未消費。
- 2026-10-07 21:15 JST（再監査）、F1 fitはstep611/2,789、step500 tuning評価211/313件。全学習行は連番・finite、prompt/sample alignment一致。評価211件はtuning index順prefixと完全一致し、対象一意・frame0・J/F/J&F valid。学習/evaluation processは継続中、lockbox未消費。
- 2026-10-07 21:16 JST、F1 fitはstep615/2,789、step500 tuning評価213/313件。全学習logは連番・finite loss/LR、manifest順とprompt replay一致。評価出力は期待対象順prefixに一致し、対象一意・frame0開始・指標valid。学習/evaluation process継続中、lockbox未消費。
- 2026-10-07 21:17 JST、F1 fitはstep616/2,789、step500 tuning評価216/313件。全学習logの連番・finite loss/LRとmanifest/prompt一致を確認。評価216件はindex順prefix、unique、frame0、metric valid。両process継続中、lockbox未消費。
- 2026-10-07 21:18 JST、F1 fitはstep621/2,789、step500 tuning評価224/313件。全学習logは連番・finite loss/LRで、manifest順・F0 prompt replayが完全一致。評価224件は期待index順prefixと一致、unique・frame0・metric valid。学習・評価process継続中、lockbox未消費。
- 2026-10-07 21:19 JST、F1 fitはstep626/2,789、step500 tuning評価228/313件。学習logは全件step連番・finite loss/LR、sample orderとprompt replay一致。評価228件は期待index順prefix、unique、frame0、metrics valid。両processは稼働中、lockbox未消費。
- 2026-10-07 21:20 JST、F1 fitはstep628/2,789、step500 tuning評価234/313件。全学習logは連番・finiteでmanifest sample順とprompt replayが一致。評価234件はindex順prefixと一致し、対象一意・frame0・有限範囲指標。学習/evaluation process稼働中、lockbox未消費。
- 2026-10-07 21:21 JST、F1 fitはstep636/2,789、step500 tuning評価245/313件。全学習log連番・finite、sample orderとF0 prompt replay一致。評価245件はtuning index順prefixに一致しunique・frame0・metric valid。processはGPU0/GPU1で稼働中、lockbox未消費。
- 2026-10-07 21:22 JST、F1 fitはstep640/2,789、step500 tuning評価253/313件。学習全logは連番・finite loss/LR、manifest sample順・F0 prompt replay完全一致。評価253件はindex順prefixに一致、unique・frame0・metric valid。両process稼働中、lockbox未消費。
- 2026-10-07 21:25 JST、F1 fitはstep651/2,789、step500 tuning評価264/313件。学習log全行は連番・finite loss/LRで、manifest sample順とF0 prompt replayに不一致なし。評価264件もtuning index順prefix・unique・frame0・有限範囲指標を確認。tmux pipeline、trainer、GPU1 evaluatorは稼働中。step600 checkpointは監査済み、lockbox未消費。fit開始から約4時間29分、単純平均ペースで残り約14時間43分（fit総計約19時間12分）の概算。tuning残り候補とlockbox評価時間は別途。
- 2026-10-07 21:27 JST、同じF1 trainer/evaluator PIDが継続稼働し、F1はstep655/2,789、step500候補は268/313対象。学習全logの連番・finite loss/LR・manifest順・F0 prompt replayが一致し、評価ログはindex順prefix、frame0開始、有限範囲J/F/J&Fを維持。残りfitは単純平均ペースで約14時間40分。lockbox未消費。
- 2026-10-07 21:30 JST、F1 fitはstep661/2,789、step500 tuning候補は280/313対象。全学習logの連番・finite loss/LRとsample/prompt replay一致、評価の期待順・frame0開始・finite metricsを再確認。tmux pipelineと2つの実験processは稼働中。fit残りは直近単純平均で約14時間30分、lockbox未消費。
- 2026-10-07 21:33 JST、F1 fitはstep670/2,789、step500 tuning候補は287/313対象。学習log全件が連番・finite loss/LRでmanifest sample順とF0 prompt replayが一致。評価ログも期待順、frame0開始、finite/in-range J/F/J&F。pipeline、trainer、evaluatorは稼働中。lockbox未消費。
- 2026-10-07 21:37 JST、F1 fitはstep686/2,789、step500 tuning候補は290/313対象。全学習logの連番・finite loss/LR、manifest順・F0 prompt replay一致、評価の期待順・frame0・finite指標を再監査。tmux pipeline、trainer、evaluator稼働中でGPU負荷あり。lockbox未消費。
- 2026-10-07 21:39 JST、F1 fitはstep689/2,789、step500 tuning候補は293/313対象。学習ログ全件が連番・有限loss/LR、manifest/sample orderとF0 prompt replay一致。評価行もindex順prefix・frame0開始・finite/in-range指標を確認。各process継続中、lockbox未消費。
- 2026-10-07 21:42 JST、F1 fitはstep698/2,789、step500 tuning候補は304/313対象。全学習行の連番・finite loss/LR、manifest順・F0 prompt replay一致、評価はindex順・frame0・有限範囲指標を確認。step500 summaryはまだ生成中。pipeline、trainer、evaluator稼働中で、lockbox未消費。
- 2026-10-07 21:45 JST、F1 step500 tuning評価完了。313/313対象、全125動画を含み、遅出現object/空mask除外はいずれも0。video mean J=0.71282、F=0.78768、J&F=0.75025。objects.jsonlの順序・対象・frame0・有限指標とsummary再計算値が一致し、checkpointおよびeval script SHA256もsummaryと一致。F1 step700 checkpointはcondition/split/seed/step・manifest index順・model 533 tensor/optimizer state 517件のfinite性を監査済み（SHA256 `bc9a558744858fbd1b7f8c3ad9306ffd551fa941797d0447687b20fd013507e6`）。F1 fitはstep710/2,789で全log連番・finite、manifest/sample orderとprompt replay一致。tuning queueはstep1000 checkpoint待ち。lockbox未freeze・未評価。
- 2026-10-07 21:48 JST、F1 fitはstep714/2,789。学習log全714行でstep連番・finite loss/LRを確認し、manifest sample orderとF0 prompt replay（augmentation retry、point coordinates、labels）も完全一致。F1 step500 tuning summaryは独立再計算・checkpoint/script hash一致を含め検証済み。tuning queueはstep1000 checkpointをpolling中、lockbox未消費。
- 2026-10-07 21:50 JST、F1 fitはstep719/2,789。学習log全行の連番・finite loss/LR・manifest順・F0 prompt replay一致を再確認。step500 tuningは313/313対象・video mean J&F 0.75025で完了済み。step1000 checkpointは未作成でqueueは待機中、trainerはGPU0で稼働、lockbox未消費。
- 2026-10-07 21:52 JST、F1 fitはstep724/2,789。全724学習行が連番・有限loss/LRで、manifest/sample orderとF0 prompt replayは完全一致。step500 tuning完了、tuning queueはstep1000 checkpoint待ちで稼働中。lockbox未消費。
- 2026-10-07 21:54 JST、F1 fitはstep729/2,789。全729学習行の連番・finite loss/LR・manifest順・F0 prompt replay一致を再確認。trainerはGPU0で稼働し、tuning queueはstep1000 checkpointをpolling中。step500 tuning完了、lockbox未消費。
- 2026-10-07 21:55 JST、F1 fitはstep731/2,789。全731学習行は連番・finite loss/LRで、manifest順とF0 prompt replayが一致。step500 tuning summaryは検証済み、step1000 checkpoint待ち。lockbox未消費。
- 2026-10-07 21:56 JST、F1 fitはstep736/2,789。全学習logの連番・finite loss/LR・manifest/prompt replay一致を再確認。step1000 checkpoint未作成のためtuning queueは待機中。GPU1では別のDanceTrack S4評価process (PID 980795) が稼働し、評価開始後のGPU競合要因になり得るため終了を待つ方針とし、停止操作は行わない。F1 fitはGPU0で継続、lockbox未消費。
- 2026-10-07 21:59 JST、GPU1競合を避けるため、step1000待機中（評価子processなし）のF1 tuning queueにGPU1 idle確認を追加し、tuning queueだけを再起動。F1 trainer PID 897885は継続し、step744/2,789。全744 log行の連番・finite loss/LR、manifest sample order・F0 prompt replay一致を確認。GPU1の別DanceTrack評価processは稼働中のため、次candidate評価はGPU1が空くまで開始しない。lockbox未消費。
- 2026-10-07 22:01 JST、F1 fitはstep749/2,789。全学習logが連番・finiteでmanifest sample順とF0 prompt replay一致。GPU1 idle guard付きqueue (PID 986192) はstep1000 checkpoint待ち。別DanceTrack S4評価がGPU1を利用中であることを再確認。F1 trainerはGPU0で継続、lockbox未消費。
- 2026-10-07 22:02 JST、F1 fitはstep753/2,789。全学習logの連番・finite loss/LRとmanifest順・F0 prompt replay一致を確認。GPU1上の別DanceTrack評価processが継続し、F1 tuning queueはidle guardでstep1000待機中。F1 trainerは継続、lockbox未消費。
- 2026-10-07 22:04 JST、F1 fitはstep758/2,789で、全学習logは連番・finite、manifest/sample order・F0 prompt replay一致。GPU1の別DanceTrack評価processが終了したことを確認。idle guard付きF1 queueはstep1000 checkpoint待ちで稼働中。F1 trainerはGPU0で継続、lockbox未消費。
- 2026-10-07 22:06 JST、F1 fitはstep761/2,789。全761行で連番・finite loss/LRとmanifest/prompt replay一致。loss中央値0.291、p95=2.494、最大202.48（step678、66-frame trajectory）であり、現在までに非finite値やOOMなし。高い単発lossは記述し、学習を止めずtrendを監視する。GPU1 idle guard付きqueueはstep1000待ち、lockbox未消費。
- 2026-10-07 22:07 JST、F1 fitはstep764/2,789。全logの連番・finite loss/LR・sample/prompt replay一致を再確認。大きなloss例のうちstep678（F1 202.48/F0 213.09）、step395（185.72/185.58）、step759（102.87/102.62）はF0でも近い値。一方、step373のvideo `b6520a94` object 3はF1 17.76に対しF0 0.97の差があるため、失敗軌跡として最終分析で要確認。GPU0 fit継続、GPU1 idle guard queueはstep1000待ち、lockbox未消費。
- 2026-10-07 22:11 JST、F1 fitはstep772/2,789。全772 log行の連番・finite loss/LR・manifest順・F0 prompt replayが一致し、loss中央値は0.291、最大202.48で前回から増えていない。trainer・idle guard付きqueueは稼働し、step800/1000 checkpointは未作成。GPU1は空き、lockbox未消費。
- 2026-10-07 22:13 JST、F1 fitはstep778/2,789。全log行が連番・finite loss/LR、manifest順・F0 prompt replay一致。trainerはGPU0で稼働、GPU1 idle guard付きqueueはstep1000 checkpoint待ち。step800 checkpoint未作成、lockbox未消費。
- 2026-10-07 22:16 JST、F1 fitはstep787/2,789。全学習logの連番・有限loss/LR・manifest sample順・F0 prompt replay一致を再確認。loss中央値0.290。step800 checkpointはまだ、step1000 tuning queueは稼働して待機。GPU1空き、lockbox未消費。
- 2026-10-07 22:21 JST、F1 fitはstep803/2,789。step800 checkpoint metadataはF1/fit/seed123/step800、sample_orderはmanifest index列と一致。model 533 tensor・optimizer 517 state・schedulerをfinite確認、SHA256 `da9bfd7d82827b45419d46530fa969fdd43ed3a0430afca48c52c00a9e46bdde`。全803 log行が連番・finite loss/LR、manifest順とF0 prompt replay一致。step500 tuning完了済み、queueはstep1000待ち、lockbox未消費。
- 2026-10-07 22:22 JST、F1 fitはstep805/2,789。全805 log行は連番・finite loss/LRで、manifest順・F0 prompt replay一致。step800 checkpointのadapter alphaは`1.65248e-5`でfinite/nonzero、adapter stateもfinite。GPU0 trainerとGPU1 idle guard queue継続、step1000 checkpoint待ち、lockbox未消費。
- 2026-10-07 22:24 JST、F1 fitはstep810/2,789。全810 log行が連番・finite loss/LRでmanifest sample順とF0 prompt replay一致、loss中央値0.290。step800 checkpoint監査済み。GPU1 idle guard queueはstep1000待ちで継続、lockbox未消費。
- 2026-10-07 22:27 JST、F1 fitはstep820/2,789。全logの連番・finite loss/LRとmanifest/prompt replay一致。loss中央値0.290。augmentation retry回数は0〜7の範囲（実装の最大8試行と一致）、retry記録もF0と一致。step800 checkpoint監査済み、GPU1 idle guard queueはstep1000待ち、lockbox未消費。
- 2026-10-07 22:28 JST、F1 fitはstep823/2,789。全823行は連番・finite、manifest/prompt replay一致、loss中央値0.290。step822のvideo `89dc0432` object 4（27 frames）はF1 loss 135.41、対応するF0 loss 38.57で差が大きい。単一学習sampleの値として記録し、最終失敗分析で対象軌跡を確認する。直後のstep823もfiniteで、学習継続中。step1000 queue待ち、lockbox未消費。
- 2026-10-07 22:30 JST、F1 fitはstep830/2,789。全830 log行の連番・finite loss/LR・manifest sample順・F0 prompt replay一致を確認し、loss中央値0.290。step800 checkpoint監査済み。GPU0 trainer、GPU1 idle guard付きqueueは稼働中でstep1000 checkpoint待ち。lockbox未消費。
- 2026-10-07 22:31 JST、F1 fitはstep833/2,789。全logは連番・finite loss/LR、manifest順とF0 prompt replayに一致し、loss中央値0.290。trainer/queue継続中で、step900/1000 checkpointは未作成。lockbox未消費。

- 2026-10-07 22:33 JST、F1 fitはstep837/2,789。全837 log行でstep連番・finite loss/LRを確認し、manifest順およびF0 prompt replay（retry・座標・label）が一致。直近ログ更新でtrainerとtmux pipelineの稼働も確認。16:56開始からの平均ペースではfit完了まで約13時間（総計約18時間40分）の概算。step1000 tuning queueはcheckpoint待ち、lockbox未消費。

- 2026-10-07 22:36 JST、F1 fitはstep844/2,789。全844 log行を再監査し、step連番・finite loss/LR・manifest sample順・F0 prompt replayがすべて一致、loss中央値0.2885。trainer PID 897885とtmux pipeline/step1000待ちtuning queueは稼働中。lockbox未消費。

- 2026-10-07 22:38 JST、F1 fitはstep852/2,789。全852行を監査し、連番・finite loss/LR・manifest順・F0 prompt replayが一致（loss中央値0.2885）。trainerと両tmux pipelineは稼働中。step1000候補評価待ち、lockbox未使用。

- 2026-10-08 12:17 JST、F1 full fitをstep2789/2,789まで完了。全2789 log行でstep連番・finite loss/LR・manifest sample order・F0 training-prompt replay一致。最終checkpoint metadataはF1/fit/seed123/step2789、model・optimizer・scheduler全値finite、SHA-256 `375e1d8e1a8ae242224b14dbfbbceaf6588b8c67016edd628af0af9202ba700c`。6候補tuningからF0 step2789（video mean J&F 0.770081）、F1 step2000（0.771217）を選択。凍結manifest上で両選択step、lockbox plan hash、実装8ファイルhashを再照合。P0 lockbox評価は570対象中242対象まで進み、出力はplanの期待prefixと一致、重複なし、t0除外、frame数およびfinite/in-range J/Fを確認。P0 worker PID 1074677は稼働中。lockbox全条件・paired統計は未完了。

- 2026-10-08 12:21 JST、P0 lockboxは256/570対象。逐次出力のprefix・対象unique・frame数・finite J/Fを継続確認。現在のrunはstep/object単位JSONLと100-step checkpointを保存し、Comet/W&B/MLflow/TensorBoard event writerは接続していない（共通SAM2 TensorBoard utility自体はrepoに存在）。run配下にevent fileなし。

- 2026-10-08 12:26 JST、P0 lockboxは274/570対象まで進行。逐次JSONLはlockbox planのexpected prefix、対象unique、frame count、finite/in-range J/Fと整合。MTG用の途中経過図 [`figures/2026-10-08-mose-training-tuning-progress.png`](figures/2026-10-08-mose-training-tuning-progress.png) を保存。F0/F1全fit lossとtuning候補のみを示し、lockbox性能の主張には使わない。
- 2026-10-08 12:32 JST、P0 lockboxは310/570対象。worker PID 1074677とtmux session `mose_temporal_mamba_pipeline`が稼働中で、直近6分にJSONLが36件増加。GPU1（RTX A4000）は評価workerが1,536 MiB使用、GPU0（RTX PRO 4500 Blackwell）は515 MiB/32 GiB使用。GPU0で追加fitを並列実行する余力はあるが、すでにlockboxを開封した後の追加runは凍結済み主比較に含まれず、Cometを付けても明日のMTGまでに完了したpaired lockbox結果にはならない。追加runは開始せず、現行の凍結済み評価を継続する。
- 2026-10-08 12:35 JST、P0 lockboxは315/570対象。部分監査で315行が凍結trajectory indexの期待prefixと一致し、対象重複なし、軌跡長・t0除外後の評価frame数・finite/in-range J/F/J&Fを確認。SAM2 venvには`comet_ml`がインストール済みで`/home/aburatani/.comet.config`も存在するが、現runにはlogger未接続。Cometへ新規学習を送るより既存JSONLのbackfillで可視化可能かが残る選択肢。lockbox worker PID 1074677継続中。
- 2026-10-08 12:37 JST、P0 lockboxは330/570対象。最新部分JSONLを凍結index順・unique ID・初出frame・軌跡長・t0除外frame数・finite/in-range J/F/J&Fで再監査し通過。worker PID 1074677はCPU約198%で処理中、GPU1使用率は観測時点で43%。P0後のF0/F1/F1-reset評価とpaired集計はtmux pipelineに設定済み。
- 2026-10-08 12:40 JST、P0 lockboxは342/570対象。342行すべてが凍結trajectory indexの期待prefixと一致し、対象重複なし、初出frame・軌跡長・t0除外frame数・finite/in-range J/F/J&Fを確認。worker PID 1074677はGPU1上で稼働中。ほか3条件のlockbox評価とpaired集計は未完了。
- 2026-10-08 12:41 JST、specのgit provenanceを補助監査。実装worktree HEADは`1448f333c323b829fbf2bc73a14180dd485f1ac7`。tracked変更は`sam2/modeling/sam2_base.py`、`sam2/modeling/temporal_mamba_adapter.py`、`training/model/sam2.py`、dirty diff SHA-256は`61c1cc9e151bb354830527ee5540a25eccba62e2fe76ddf0fac39eef14593bd3`。untrackedは`training/README_mose_fulltrack.md`、`training/eval_mose_fulltrack.py`、`training/export_training_prompts.py`、`training/mose_fulltrack.py`、`training/select_mose_checkpoint.py`、`training/summarize_mose_fulltrack.py`。F0 manifestにはgit provenance fieldがないため、この記録で補完する。lockbox freezeにはF0/F1評価に使う実装8ファイルの個別hashが保存され、現worktreeとの一致を確認済み。F1 manifestにはgit commit/statusとimplementation hashが記録済み。
- 2026-10-08 12:42 JST、P0 lockboxは351/570対象。前回監査済みの349件以降もworker PID 1074677が稼働し、JSONL件数が増加。lockbox全条件の評価とpaired summaryは未完了。
- 2026-10-08 12:44 JST、P0 lockboxは360/570対象。360行を凍結trajectory indexのexpected prefix・一意性・初出frame・軌跡長・t0除外後frame数・finite/in-range J/F/J&Fで監査し通過。selector manifestのtuning基準はequal-weight video mean J&Fで、F0 step2789は0.770080510、F1 step2000は0.771216900（いずれも125 videos/313 objects）。
- 2026-10-08 12:45 JST、P0 lockboxは366/570対象。全366行のexpected-prefix順、unique object ID、first frame/trajectory length/scored frame count（t0除外）、finite/in-range J/F/J&Fを再検証し通過。別のSAM2MOT S4評価2件（PID 1086766・1086767）がGPU0で同時稼働、MOSE P0 worker PID 1074677はGPU1で実行中。GPU UUIDを照合しており、GPUは別だがCPU/IOは共有する。
- 2026-10-08 12:48 JST、P0 lockboxは374/570対象。374行を凍結trajectory indexのexpected prefix・一意性・first frame・軌跡長・t0除外後frame count・finite/in-range J/F/J&Fで監査し通過。P0 worker PID 1074677は継続稼働、ほか3条件のsummaryはまだない。
- 2026-10-08 12:51 JST、P0 lockboxは380/570対象。全380行で凍結trajectory indexのprefix順・object uniqueness・first frame/length/scored frame count（t0除外）・finite/in-range J/F/J&Fを確認し通過。P0 summaryは未生成。
- 2026-10-08 12:53 JST、P0 lockboxは390/570対象。全390行のfrozen trajectory expected prefix・unique ID・first_frame/length・t0除外scored frame数・finite/in-range J/F/J&Fを監査し通過。P0 worker PID 1074677は稼働中。ほか3条件とpaired summaryは未完了。
- 2026-10-08 12:54 JST、P0 lockboxは395/570対象。全395行が凍結trajectory indexのexpected prefix・unique object・first_frame/length/scored frame count（t0除外）・finite/in-range J/F/J&Fを満たすことを再監査。worker PID 1074677は継続稼働中。
- 2026-10-08 12:55 JST、P0 lockboxは398/570対象。398件すべて凍結trajectory expected prefix・unique ID・first_frame/length・t0除外scored frame count・finite/in-range J/F/J&Fを満たすことを再確認。P0 worker PID 1074677は稼働中。
- 2026-10-08 12:56 JST、P0 lockboxは400/570対象に到達。400行を凍結trajectory expected prefix、unique ID、first_frame/length、t0除外scored frame数、finite/in-range J/F/J&Fで監査し通過。P0 worker PID 1074677は継続稼働中。
- 2026-10-08 12:57 JST、P0 lockboxは404/570対象。404行をfrozen index順、unique object ID、first_frame/trajectory length/scored frame count（t0除外）、finite/in-range J/F/J&Fで監査し通過。worker PID 1074677は継続稼働中。
- 2026-10-08 12:58 JST、P0 lockboxは411/570対象。全411行が凍結indexのexpected prefix・unique ID・first frame/trajectory length・t0除外scored frame数・finite/in-range J/F/J&Fを満たすことを監査し通過。worker PID 1074677は稼働中。
- 2026-10-08 12:59 JST、P0 lockboxは414/570対象。全414行でexpected-prefix order・一意性・初出frame・軌跡長・t0除外後frame数・finite/in-range J/F/J&Fを再検証。worker PID 1074677は稼働中。
- 2026-10-08 13:00 JST、P0 lockboxは424/570対象。424行を凍結index prefix、unique IDs、first_frame/length、t0除外scored frames、finite/in-range J/F/J&Fで監査し通過。worker PID 1074677は稼働中。
- 2026-10-08 13:01 JST、P0 lockboxは431/570対象。全431行をfrozen index順、一意object、初出frame/軌跡長/t0除外scored frame数、finite/in-range J/F/J&Fで検査し通過。worker PID 1074677は継続稼働中。
- 2026-10-08 13:02 JST、P0 lockboxは440/570対象。全440行を凍結index prefix・unique object IDs・first_frame/length/scored frame count（t0除外）・finite/in-range J/F/J&Fで監査し通過。P0 worker PID 1074677は稼働継続。
- 2026-10-08 13:04 JST、P0 lockboxは446/570対象。全446行をfrozen index順・unique ID・first_frame/trajectory length/t0除外frame数・finite/in-range J/F/J&Fで監査し通過。worker PID 1074677は稼働中。
- 2026-10-08 13:34 JST、P0 lockboxを完了。`summary.json`はfrozen freeze hash・trajectory index hash・eval script hash・base checkpoint hashを記録し、200/200動画・570/570対象、除外0、動画平均J=0.6644776、F=0.7371931、J&F=0.7008354、elapsed 7,627.38秒。P0のlinewise部分監査は446件までの記録があり、以降を含む全条件の最終監査は後続summarizerで実行する。F0 lockboxは13:33 JSTにworker PID 1099129で開始、初回確認時のobjects.jsonlは0件。F1・F1-reset・paired集計は未完了。
- 2026-10-08 13:56 JST、F0 lockboxは102/570対象まで出力。objects.jsonlは13:56 JSTに更新され、worker PID 1099129はGPU上で稼働中。F0の全件summary、F1・F1-reset、paired summaryは未生成。
- 2026-10-08 14:31 JST、F0 lockboxは260/570対象まで出力。queue logも260到達を記録し、worker PID 1099129はGPU0/1上で稼働中。F0 summaryは未生成で、F1・F1-reset・paired summaryも未完了。
- 2026-10-08 14:38 JST、F0 lockboxは293/570対象まで出力。GPU別プロセス監視でworker PID 1099129がGPU1上で継続して計算中。F0 summaryは未生成で、F1・F1-reset・paired summaryも未完了。
- 2026-10-08 14:48 JST、F0 lockboxは336/570対象まで出力。GPU別プロセス監視でworker PID 1099129がGPU1上で計算を継続中。F0 summaryは未生成で、F1・F1-reset・paired summaryも未完了。
- 2026-10-08 14:51 JST、F0 lockboxは351/570対象まで出力。queue logは340件到達を記録し、GPU別プロセス監視でworker PID 1099129の稼働を確認。F0 summaryと後続条件は未完了。
- 2026-10-08 14:57 JST、F0 lockboxは374/570対象まで出力。queue logは360件到達を記録し、GPU別プロセス監視でworker PID 1099129の継続稼働を確認。F0 summaryと後続条件は未完了。
- 2026-10-08 15:02 JST、F0 lockboxは383/570対象まで出力。queue logは380件到達を記録し、GPU別プロセス監視でworker PID 1099129がGPU1上で稼働中。F0 summaryと後続条件は未完了。
- 2026-10-08 15:05 JST、F0 lockboxは400/570対象に到達。queue logも400件を記録し、worker PID 1099129はGPU1上で継続中。F0 summaryとF1・F1-reset・paired集計は未完了。
- 2026-10-08 15:09 JST、F0 lockboxは424/570対象まで出力。queue logは420件を記録し、worker PID 1099129はGPU上で稼働中。F0 summaryと後続条件は未完了。
- 2026-10-08 15:11 JST、F0 lockboxは439/570対象まで出力。GPU別プロセス監視でworker PID 1099129の継続稼働を確認。F0 summaryと後続条件は未完了。
- 2026-10-08 15:14 JST、F0 lockboxは454/570対象まで出力。worker PID 1099129はGPU1上で稼働中。F0 summaryと後続評価・集計は未完了。
- 2026-10-08 15:17 JST、F0 lockboxは460/570対象まで出力。queue logも460件到達を記録し、worker PID 1099129はGPU1上で継続中。F0 summaryと後続評価・集計は未完了。
- 2026-10-08 15:20 JST、F0 lockboxは469/570対象まで出力。queue logは460件到達を記録し、worker PID 1099129はGPU1上で継続中。F0 summaryと後続評価・集計は未完了。
- 2026-10-08 15:22 JST、F0 lockboxは480/570対象まで出力。queue logも480件到達を記録し、worker PID 1099129はGPU上で継続中。F0 summaryと後続条件は未完了。
- 2026-10-08 15:25 JST、F0 lockboxは500/570対象に到達。queue logも500件を記録し、worker PID 1099129はGPU1上で稼働中。F0 summaryと後続条件は未完了。
- 2026-10-08 15:40 JST、F0 lockboxを完了。200動画・570対象、除外0、動画平均J=0.7026991、F=0.7757021、J&F=0.7392006、elapsed 7,585.79秒。選択checkpoint `F0_step_002789.pt` のSHA-256は`5d4cd955a177d40afddba65082df647a64bf6774a40dd210a9099543c8bc0ae9`で、P0/F0のfreeze・trajectory index・評価script・base checkpoint hashは一致。F1 lockboxを開始し、16:17時点で156/570対象まで逐次出力。worker PID 1131047（親pipeline PID 878216）は稼働中。F1-resetとpaired summaryは未完了。
- 2026-10-08 16:19 JST、P0/F0の全570 object JSONLをfrozen trajectory順・frame coverage（t0除外）・全frameとobjectのfinite/in-range J/F/J&F・object/video/summary平均の再計算で監査し通過。F0/F1の全2,789更新もstep連番、finite loss/LR、fit manifest sample orderとの一致を確認し、両条件の順序は完全一致。F1 lockboxは164/570対象で、途中出力はindex prefix・frame coverage・finite/range指標を通過。freeze対象の実装8ファイルhashもすべて一致。F1評価worker PID 1131047と親pipeline PID 878216は稼働中。F1-reset、paired bootstrap summary、長さ別評価は未完了。
- 2026-10-08 16:22 JST、F1 lockboxは177/570対象で進行。P0/F0全件のobject/video/summary集計監査と、F0/F1全学習log監査は通過。P0/F0全570件とF1評価済み177件で、保存prompt seed・座標・labelが条件間で一致。F1-reset、paired bootstrap summary、長さ別評価は未完了。
- 2026-10-08 16:24 JST、F1 lockboxは187/570対象でworker PID 1131047が継続稼働。P0/F0の予測PNGは全36,260 scored frameに対応し、F1は完了objectの全予測PNGに欠落なし。JSONLへ行が確定する前の処理中trajectory由来PNG 17件も、期待される次objectの時系列prefixと一致。F1-resetとpaired summaryは未完了。
- 2026-10-08 16:25 JST、F1 lockboxは195/570対象。途中出力をfrozen trajectory/frame順、t0除外、全object/frame J/F/J&Fのfinite・[0,1]範囲、object平均との一致で再監査し通過。freeze対象の実装hash8件も一致。worker PID 1131047と親pipeline PID 878216は稼働中。
- 2026-10-08 16:27 JST、F1 lockboxは205/570対象。F1 worker PID 1131047とdetached pipeline PID 878216を再確認。F1-resetおよびpaired bootstrap・系列長別summaryは未完了。
- 2026-10-08 16:29 JST、F1 lockboxは216/570対象。全出力済みtrajectoryのfrozen index順・first-frame/length・t0除外後frame coverage・finite/in-range J/F/J&F・object mean整合・P0/F0との同一promptを再監査し通過。凍結コードhash8件も一致。worker PID 1131047は稼働中。
- 2026-10-08 16:31 JST、F1 lockboxは221/570対象。全途中出力をfrozen index/frame順、t0除外、J/F/J&Fの有限範囲とobject平均、P0/F0とのprompt seed/tensor一致で監査し通過。8件のsource hashも一致。
- 2026-10-08 16:38 JST、spec provenance audit: `F0_fit_manifest.json`にoptimizer/config詳細・training source hashがないことを確認。lockbox freezeに含まれるF0 manifestは改変せず、F0最終checkpoint (`F0_step_002789.pt`) の保存optimizer/scheduler stateと、F1 manifestに記録された同一trainer hash `5ad9246d…` から再構成した。F0 checkpointはF0/fit/seed123/step2789、sample order 2,789、scheduler `CosineAnnealingLR(T_max=2789)`。AdamW groupは (LR 5e-6, WD 0.1, 129 tensors, 11,693,956 params)、(3e-6, 0.1, 74, 34,234,752)、(3e-6, 0, 136, 82,240)、(5e-6, 0, 179, 49,406)。F0 manifestから既に確認できるresolution=1024、TBPTT=8、BF16、2,789 updates、base checkpoint hash、peak VRAMも保持。F0 recovery commandは`--mode train --condition F0 --split fit --chunk-len 8 --limit 0 --checkpoint-interval 100 --scheduler-steps 2789 --resume <verified checkpoint> --run-dir runs/mose_temporal_mamba_20260930 --device cuda:0 --seed 123`。experiment log上、再開後に追加した変更はfinite検査・prompt/manifest記録等の計測・provenanceで、主要計算は不変とレビュー済み。F0最初のprefixに関するsource hashは当時のmanifestに残っていないため、そのprovenance限界は保持し、再生成したmanifestとは扱わない。F1 lockboxは16:38時点245/570対象、worker PID 1131047稼働中。
- 2026-10-08 16:43 JST、F1 lockboxは270/570対象まで出力。親pipeline PID 878216とF1 evaluator PID 1131047を再確認し、両方稼働中。確定済み261行を凍結trajectory順・全frame範囲（t0除外）・P0/F0とのprompt seed/座標/label一致・finiteで[0,1]内のframe/object指標・object平均との一致で監査し、異常0。F1-resetとpaired bootstrap/系列長別summaryは未完了。
- 2026-10-08 16:47 JST、F1 lockboxは282/570対象まで出力し、worker PID 1131047はCPU/GPU上で継続稼働。最新監査では276確定行・17,249 scored frameを凍結trajectory順、P0/F0とのprompt一致、frame coverage、有限・[0,1]範囲、object平均の一致で検査し異常0。F1-resetとpaired bootstrap/系列長別summaryは未完了。
- 2026-10-08 16:51 JST、F1 lockboxは304/570対象を越え、確定済み305行・18,803 scored frameを監査。frozen trajectory順、P0/F0とのprompt seed/座標/label一致、t0を除くframe coverage、有限・[0,1]範囲のframe/object J/F、object平均との一致に異常0。親pipeline PID 878216とevaluator PID 1131047は稼働中。F1-resetおよびpaired bootstrap/系列長別summaryは未完了。
- 2026-10-08 16:53 JST、F1 lockboxは312/570対象・19,254 scored frameを出力。全312行で凍結trajectory順、P0/F0とのprompt一致、t0除外後frame coverage、有限かつ[0,1]内のframe/object J/F、object平均との一致を再監査し異常0。pipeline PID 878216とevaluator PID 1131047は稼働中。F1-reset、paired bootstrap、系列長別summaryは未完了。
- 2026-10-08 16:55 JST、F1 lockboxは315/570対象・19,796/36,260 scored frameに到達。全315行を凍結trajectory順、P0/F0とのprompt seed/座標/label parity、t0除外後のframe coverage、finite/in-range frame/object J/F、object平均との一致で検査し異常0。PID 878216/1131047は稼働中。240-frame長尺系列の処理中にもCPU/GPU利用とJSONL更新を確認。F1-resetとpaired bootstrap/系列長別summaryは未完了。
- 2026-10-08 16:57 JST、F1 lockboxは325/570対象を越え、確定済み326行・20,263 scored frame。全行で凍結trajectory順、P0/F0とのprompt一致、t0除外後frame coverage、finite/in-range frame/object J/F、object平均との一致に異常0。親pipeline PID 878216とevaluator PID 1131047が稼働し、GPU使用を再確認。F1-resetとpaired bootstrap/系列長別summaryは未完了。
- 2026-10-08 16:59 JST、F1 lockboxは332/570対象を越え、確定済み333行・20,844 scored frameを監査。frozen trajectory順、P0/F0とのprompt seed/座標/label parity、t0除外後のframe coverage、finite/in-range frame/object J/F、object mean一致に異常0。親pipeline PID 878216・worker PID 1131047は継続稼働中。F1-resetとpaired bootstrap/系列長別summaryは未完了。
- 2026-10-08 17:02 JST、F1 lockboxは349/570対象・21,870 scored frameに到達。全349行をfrozen trajectory順、P0/F0とのprompt一致、t0除外後frame coverage、finite/in-range frame/object J/F、object平均一致で監査し異常0。親pipeline PID 878216とevaluator PID 1131047が稼働中。F1-resetとpaired bootstrap/系列長別summaryは未完了。
- 2026-10-08 17:05 JST、F1 lockboxは364/570対象・22,692 scored frame。全364行の凍結順序、P0/F0 prompt parity、t0除外後frame coverage、finite/in-range指標とobject平均を監査し異常0。親pipeline/evaluatorは稼働中でJSONL更新を確認。F1-reset・paired bootstrap・系列長別summaryは未開始。
- 2026-10-08 17:07 JST、F1 lockboxは369/570対象・23,232/36,260 scored frame (64.1%)。全369行のtrajectory順、P0/F0 prompt parity、t0除外後frame coverage、finite/in-range J/Fとobject mean一致を監査し異常0。pipeline/evaluatorは稼働中。残りF1・F1-reset・paired summaryが未完了。
- 2026-10-08 17:09 JST、F1 lockboxは374/570対象・23,823/36,260 scored frame (65.7%)。全374行をfrozen order、P0/F0 prompt parity、t0除外後frame coverage、finite/in-range frame/object J/F、object mean一致で監査し異常0。親pipeline・evaluatorは稼働中でF1-resetへの切替前。
- 2026-10-08 17:11 JST、F1 lockboxは378/570対象・24,251/36,260 scored frame (66.9%)。全378行をtrajectory順、P0/F0 prompt parity、t0除外後frame coverage、finite/in-range J/F、object mean一致で監査し異常0。workerとGPU利用を確認。F1-resetとpaired summaryは未完了。
- 2026-10-08 17:13 JST、F1 lockboxは381/570対象・24,572/36,260 scored frame (67.8%)。全381行のfrozen trajectory順、P0/F0 prompt parity、t0除外後frame coverage、finite/in-range metricとobject mean一致に異常0。親pipeline/evaluatorとGPU稼働を確認。F1-reset、paired bootstrap、系列長別summaryは未完了。
- 2026-10-08 17:17 JST、F1 lockboxは401/570対象・25,871/36,260 scored frame (71.3%)。全401行のfrozen order、P0/F0 prompt parity、t0除外frame coverage、有限・[0,1]範囲のJ/Fとobject mean一致を監査し異常0。親pipeline/evaluatorは稼働中。F1-resetとpaired bootstrap/系列長別summaryは未完了。
- 2026-10-08 17:19 JST、F1 lockboxは409/570対象・26,556/36,260 scored frame (73.2%)。全409行のtrajectory順、P0/F0 prompt seed/座標/label一致、t0除外frame coverage、有限・[0,1]範囲のJ/F、object平均一致を監査し異常0。pipeline/evaluatorとGPU稼働を確認。F1-resetと最終paired summaryは未完了。
- 2026-10-08 17:21 JST、F1 lockboxは422/570対象・27,133/36,260 scored frame (74.8%)。全422行でfrozen order、P0/F0 prompt parity、t0除外frame coverage、finite/in-range J/F、object mean一致を監査し異常0。pipeline PID 878216/evaluator PID 1131047とGPU稼働中。F1-resetとpaired summaryは未完了。
- 2026-10-08 17:23 JST、F1 lockboxは439/570対象・27,752/36,260 scored frame (76.5%)。全439行をfrozen trajectory順、P0/F0 prompt parity、t0除外後frame coverage、finite/in-range J/Fとobject平均で監査し異常0。pipeline/evaluatorとGPUは稼働中。F1-resetとpaired summary未開始。
- 2026-10-08 17:26 JST、F1 lockboxは446/570対象・28,263/36,260 scored frame (77.9%)。全446行をfrozen order、P0/F0 prompt parity、t0除外frame coverage、有限・[0,1]範囲のframe/object J/Fとobject平均一致で監査し異常0。pipeline/evaluatorおよびGPUの稼働継続を確認。F1-resetとpaired summaryは未完了。
- 2026-10-08 17:28 JST、F1 lockboxは456/570対象・28,827/36,260 scored frame (79.5%)。全456行をfrozen trajectory順、P0/F0 prompt parity、t0除外後frame coverage、finite/in-range J/F、object平均一致で監査し異常0。pipeline/evaluatorとGPUは稼働中。F1-resetとpaired summaryは未開始。
- 2026-10-08 17:30 JST、F1 lockboxは460/570対象・29,363/36,260 scored frame (81.0%)。全460行をfrozen trajectory順、P0/F0 prompt parity、t0除外後frame coverage、finite/in-range J/F、object平均一致で監査し異常0。親pipeline/evaluatorとGPU稼働中。F1-resetおよびpaired summaryは未完了。
- 2026-10-08 17:32 JST、F1 lockboxは464/570対象・29,899/36,260 scored frame (82.5%)。全464行のfrozen order、P0/F0 prompt parity、t0除外frame coverage、finite/in-range frame/object J/Fとobject mean一致を監査し異常0。pipeline/evaluator/GPU稼働中、F1-resetへの切替待ち。
- 2026-10-08 17:34 JST、F1 lockboxは471/570対象・30,374/36,260 scored frame (83.8%)。全471行のtrajectory順、P0/F0 prompt parity、t0除外frame coverage、finite/in-range frame/object J/Fとobject平均一致を監査し異常0。worker/GPU稼働中。F1-resetとpaired summaryは未完了。
- 2026-10-08 17:36 JST、F1 lockboxは482/570対象・30,951/36,260 scored frame (85.4%)。全482行のtrajectory順、P0/F0 prompt parity、t0除外frame coverage、finite/in-range J/F、object mean一致を監査し異常0。pipeline/evaluator/GPUは稼働中。F1-resetとpaired summaryは未完了。
- 2026-10-08 17:38 JST、F1 lockboxは494/570対象・31,495/36,260 scored frame (86.9%)。全494行をfrozen trajectory順、P0/F0 prompt parity、t0除外後frame coverage、finite/in-range J/F、object平均一致で監査し異常0。pipeline/evaluator/GPU稼働中、F1-resetは未開始。
- 2026-10-08 17:40 JST、F1 lockboxは502/570対象・31,964/36,260 scored frame (88.2%)。全502行をfrozen trajectory順、P0/F0 prompt parity、t0除外frame coverage、finite/in-range J/Fとobject平均で監査し異常0。pipeline/evaluatorはCPU・GPU利用状態で稼働中。F1-resetとpaired summaryは未開始。
- 2026-10-08 17:42 JST、F1 lockboxは508/570対象・32,422/36,260 scored frame (89.4%)。全508行の凍結順序、P0/F0 prompt parity、t0除外frame coverage、finite/in-range J/Fとobject mean一致を監査し異常0。pipeline/evaluator/GPU稼働中。F1-reset・paired集計は未完了。
- 2026-10-08 17:44 JST、F1 lockboxは514/570対象・33,197/36,260 scored frame (91.6%)。全514行のfrozen order、P0/F0 prompt parity、t0除外frame coverage、finite/in-range frame/object J/Fとobject平均一致を監査し異常0。pipeline/evaluatorとGPU稼働中。F1-resetとpaired集計は未完了。
- 2026-10-08 17:46 JST、F1 lockboxは520/570対象・33,646/36,260 scored frame (92.8%)。全520行をfrozen trajectory順、P0/F0 prompt parity、t0除外frame coverage、finite/in-range J/Fとobject平均一致で監査し異常0。pipeline/evaluatorとGPUは稼働中。F1-resetとpaired summary未完了。
- 2026-10-08 17:48 JST、F1 lockboxは527/570対象・34,103/36,260 scored frame (94.1%)。全527行を凍結trajectory順、P0/F0 prompt parity、t0除外後frame coverage、finite/in-range J/F、object平均一致で監査し異常0。pipeline/evaluatorは稼働中。F1-resetとpaired summary未完了。
- 2026-10-08 17:50 JST、F1 lockboxは535/570対象・34,600/36,260 scored frame (95.4%)。全535行をfrozen trajectory順、P0/F0 prompt parity、t0除外frame coverage、finite/in-range frame/object J/Fとobject平均で監査し異常0。pipeline/evaluator/GPUは稼働中。F1-resetと集計未完了。
- 2026-10-08 17:51 JST、F1 lockboxは548/570対象・35,169/36,260 scored frame (97.0%)。全548行のfrozen order、P0/F0 prompt parity、t0除外後frame coverage、finite/in-range J/F、object平均一致を監査し異常0。pipeline/evaluator/GPU稼働中。F1-resetとpaired集計は未完了。
- 2026-10-08 17:53 JST、F1 lockboxは559/570対象・35,603/36,260 scored frame (98.2%)。全559行のtrajectory order、P0/F0 prompt parity、t0除外frame coverage、finite/in-range J/Fとobject mean一致を監査し異常0。evaluator/pipeline/GPU稼働中。F1-resetとsummaryは未完了。
- 2026-10-08 17:56 JST、F1 lockbox完了・全件監査。200/200 video・570/570 object・36,260/36,260 scored frame、除外0。summaryはvideo mean J=0.7063523041、F=0.7776926516、J&F=0.7420224779（elapsed 8,076.26秒）。P0/F0/F1全570対象のprompt seed/coords/labels一致、凍結trajectory順と全scored frame、全frame/object/video/summary平均、J/F有限・[0,1]範囲、評価freeze/checkpoint/evaluator hashを独立再計算し異常0。F1予測PNG 36,260枚でscored frame数と一致。F1-resetは同じstep2000 checkpointで開始、確認時点2/570 object。F1-reset最終評価とpaired bootstrap・系列長別summaryは未完了。
- 2026-10-08 18:00 JST、F1-resetは9/570対象まで出力。9行すべてfrozen trajectory順、F1/F0/P0とprompt seed/座標/label一致、t0除外後frame coverage、finite/in-range J/F、object mean整合を監査し異常0。F1-resetとpaired bootstrap・系列長別summaryは実行中/未完了。
- 2026-10-08 18:09 JST、F1-resetは42/570対象・2,568/36,260 scored frameまで出力。途中42行をfrozen trajectory順、P0/F0/F1 prompt parity、初出frame以降のframe IDと件数、finite/in-range J/F、object平均一致で独立監査し異常0。評価worker PID 1194634は稼働中。処理速度からF1-resetは20:45前後、最終集計・全件監査を含む完了は21:00〜21:30ごろの見込み。paired bootstrap・系列長別summaryは未完了。
- 2026-10-08 18:14 JST、F1-resetは55/570対象・3,918/36,260 scored frameまで出力。全55行をfrozen trajectory順、P0/F0/F1のprompt seed/座標/label一致、初出frame以降のframe IDと件数、finite/in-range J/F、object平均一致で独立監査し異常0。評価worker PID 1194634は稼働中。平均処理速度からF1-resetは20:35〜20:45ごろ、最終集計・全件監査を含む完了は21:00〜21:30ごろの見込み。paired bootstrap・系列長別summaryは未完了。
- 2026-10-08 18:17 JST、F1-resetは69/570対象・4,691/36,260 scored frame。途中69行に順序・初出frame以降のframe ID/件数・finite/in-range J/F・object mean・P0/F0/F1 prompt parityの異常なし。加えてP0/F0/F1全570対象・36,260 frameを凍結trajectory順、prompt、frame coverage、object/video/summary mean、予測PNG数まで独立再計算し異常0。F1-reset worker PID 1194634稼働中。paired bootstrap・系列長別summaryは未完了。
- 2026-10-08 18:20 JST、学習manifestの資源・時間計測を確認。F0 peak allocated/reserved VRAMは20.400/20.564 GiB、F1は20.415/20.676 GiB。F1の`this_process_elapsed_seconds`は60,580秒（16.83時間）でmanifestのstart〜completionと一致。F0は6,404.74秒（1.78時間）が完了manifestを書いた最終trainer process分で、開始〜完了は168.30時間だが間に再開・待機があるため総稼働学習時間には使えない。recovery各回の累積時間は記録されておらず、正確なF0総学習時間は復元不能。F0/F1両条件のpeak VRAMとF1所要時間はmanifestから確認できる。F1-resetは85/570対象・5,596/36,260 frame、worker PID 1194634稼働中。
- 2026-10-08 18:23 JST、F1-resetは104/570対象・6,360/36,260 scored frame、予測PNG 6,364枚。18:22に完了済み101行を凍結trajectory順、P0/F0/F1 prompt seed/座標/label parity、初出frame以降のframe ID/件数、finite/in-range J/F、object平均一致で再監査し異常0。評価worker PID 1194634は稼働中。P0/F0/F1全件の独立監査・checkpoint/code hash確認は通過済み。評価完了とpaired bootstrap/系列長別summaryは未完了。
- 2026-10-08 18:26 JST、F1-resetは122/570対象・7,092/36,260 scored frame。全122行を凍結trajectory順、初出frame以降のframe ID/件数、P0/F0/F1 prompt seed/座標/label parity、finite/in-range J/Fとobject平均一致で再監査し異常0。評価worker PID 1194634は稼働中。全体速度から評価は20:25〜20:40ごろ、summaryと全件監査を含む完了は20:45〜21:15ごろの見込み。paired bootstrap・系列長別summaryは未完了。
- 2026-10-08 18:29 JST、F1-resetは133/570対象・7,813/36,260 scored frame。全133行を凍結trajectory順、frame ID/coverage、P0/F0/F1 prompt seed/座標/label parity、finite/in-range J/F、object平均一致で独立監査し異常0。worker PID 1194634は稼働中。平均速度から評価は20:25ごろ、最終summary・全件監査は20:45〜21:15ごろの見込み。paired bootstrap・系列長別summaryは未完了。
- 2026-10-08 18:30 JST、完了済みF1/F0/P0のvideo-level paired bootstrapを最終summary前に独立再計算（200 video、10,000 resample、seed 123、95% percentile CI）。主比較F1−F0のJ&F差=+0.0028219、CI=[−0.0066854,+0.0115706]で0を含むため、specの事前判定基準では主仮説は支持されない。F1−F0のJ差=+0.0036532 [−0.0064114,+0.0130620]、F差=+0.0019906 [−0.0069648,+0.0103733]。適応効果のF0−P0 J&F差=+0.0383652 [0.0215904,0.0573054]。これは最終summary出力前の独立計算であり、F1-resetとlength groupを含むsummaryは未完了。F1-resetは18:29確認時134/570対象・7,919 frameで稼働継続。
- 2026-10-08 18:30 JST、F0/F1 full-fit logを独立監査。各2,789行がstep 1〜2,789で連番、manifest sample orderとvideo/object IDが完全一致、全loss/LRがfiniteでframe数も正。manifestのpeak allocated/reserved VRAMはF0 20.400/20.564 GiB、F1 20.415/20.676 GiB。F1-resetは18:30時点137/570対象でworker PID 1194634稼働中。
- 2026-10-08 18:34 JST、F1-resetは149/570対象・9,058/36,260 scored frame。149行すべて凍結trajectory順、初出frame以降のframe IDとframe数、P0/F0/F1 prompt parity、finite/in-range J/F、object平均一致を監査し異常0。評価worker PID 1194634稼働中。完了済みF1−F0のpaired J&F 95% CIは0を含むため、主仮説の判定は「支持されない」。F1-resetの全件評価とlength group集計は未完了。
- 2026-10-08 18:37 JST、F1-resetは164/570対象・10,070/36,260 scored frame。全164行を凍結trajectory順、初出frame以降のframe coverage、P0/F0/F1 prompt parity、finite/in-range J/F、object平均一致で独立監査し異常0。worker PID 1194634稼働中。free disk 7.2 TiBで、prediction保存の容量懸念なし。平均frame処理速度から評価完了20:20〜20:40ごろ、paired summary・全件監査まで20:45前後を見込む。F1−F0主比較はpaired video bootstrap CIが0を含み仮説支持なし。
- 2026-10-08 18:42 JST、F1-resetは185/570対象・11,487/36,260 scored frame。全185行をfrozen trajectory順、初出frame以降のframe ID・件数、P0/F0/F1 prompt parity、finite/in-range J/F、object平均一致で独立監査し異常0。評価worker PID 1194634は稼働中。F1−F0主比較のJ&F 95% CI=[−0.0066854,+0.0115706]で0をまたぐため、spec基準では支持されない。F1-reset全件・length groups・final paired summaryは未完了。
- 2026-10-08 18:44 JST、F1-resetは199/570対象・12,134/36,260 scored frame。全199行で凍結trajectory順、初出frame以降のframe ID/件数、P0/F0/F1 prompt parity、finite/in-range J/F、object平均一致を再監査し異常0。評価worker PID 1194634稼働中。平均処理速度から評価完了は20:15〜20:35ごろ、paired summaryと全件監査を含む完了は20:40〜21:00ごろの見込み。
- 2026-10-08 18:45 JST、F1-resetは205/570対象・12,348/36,260 scored frame。全205行を凍結trajectory順、frame coverage、P0/F0/F1 prompt parity、finite/in-range J/F、object平均一致で独立監査し異常0。worker PID 1194634稼働中。主比較F1−F0のJ&F差は+0.0028219、video bootstrap 95% CI [−0.0066854,+0.0115706]で0を含み、事前基準を満たさない。F1-resetとlength-group比較は未完了。
- 2026-10-08 18:48 JST、F1-resetは216/570対象・12,997/36,260 scored frame。全216行を凍結trajectory順、frame coverage、P0/F0/F1 prompt parity、finite/in-range J/F、object平均一致で監査し異常0。worker PID 1194634稼働中。全体処理速度から評価完了20:15〜20:35ごろ、paired bootstrap・length groupの集計と監査は20:40〜21:00ごろを見込む。
- 2026-10-08 18:56 JST、F1-resetは245/570対象・15,090/36,260 scored frame。全245行で凍結trajectory順、frame coverage、P0/F0/F1 prompt parity、finite/in-range J/F、object平均一致を独立監査し異常0。worker PID 1194634稼働中。平均速度から評価完了20:15〜20:35ごろ、最終summaryと全件監査は20:40〜21:00ごろの見込み。F1−F0主比較はCIが0を含み仮説支持なし。
- 2026-10-08 18:59 JST、F1-resetは256/570対象・15,895/36,260 scored frame。全256行を凍結trajectory順、初出frame後のframe ID/件数、P0/F0/F1 prompt parity、finite/in-range J/F、object平均一致で監査し異常0。worker PID 1194634は稼働中。平均処理速度から評価完了20:15〜20:35、paired summaryと全件監査まで20:40〜21:00ごろの見込み。
- 2026-10-08 19:02 JST、F1-resetは270/570対象・16,591/36,260 scored frame。全270行を凍結trajectory順、frame coverage、P0/F0/F1 prompt parity、finite/in-range J/F、object平均一致で独立監査し異常0。worker PID 1194634は稼働中。累積frame throughputから評価完了20:20前後、最終paired summaryと全件監査は20:40〜21:00ごろを見込む。
- 2026-10-08 19:11 JST、F1-resetは307/570対象・18,851/36,260 scored frame。全307行を凍結trajectory順、初出frame後のframe ID/件数、P0/F0/F1 prompt parity、finite/in-range J/F、object平均一致で独立監査し異常0。worker PID 1194634稼働中。累積frame rateから評価完了は20:20前後、paired summaryと全件監査は20:40ごろの見込み。F1−F0 J&F CIは0を含み、主仮説はspec基準を満たさない。
- 2026-10-08 19:16 JST、F1-resetは325/570対象・20,180/36,260 scored frame。全325行をfrozen trajectory順、frame coverage、P0/F0/F1 prompt parity、finite/in-range J/Fとobject平均一致で独立監査し異常0。worker PID 1194634は稼働中。累積速度から評価完了20:20ごろ、最終summary・全件監査20:40ごろの見込み。
- 2026-10-08 19:19 JST、F1-resetは338/570対象・21,080/36,260 scored frame。全338行をfrozen trajectory順、frame coverage、P0/F0/F1 prompt parity、finite/in-range J/F、object平均一致で監査し異常0。worker PID 1194634稼働中。推論速度から評価完了20:20前後、final paired summary・全件監査20:40前後の見込み。
- 2026-10-08 19:22 JST、F1-resetは351/570対象・21,959/36,260 scored frame。完了済み351行をfrozen trajectory順、frame coverage、P0/F0/F1 prompt parity、finite/in-range J/F、object平均一致で独立監査し異常0。worker PID 1194634稼働中。累積throughputから評価は20:18前後、paired summaryと全件監査は20:40前後の見込み。
- 2026-10-08 19:28 JST、F1-resetは372/570対象・23,489/36,260 scored frame。全372行をfrozen trajectory順、frame coverage、P0/F0/F1 prompt parity、finite/in-range J/F、object平均一致で監査し異常0。worker PID 1194634は稼働中。累積速度から評価完了は20:20前後、最終summary・全件監査は20:40前後の見込み。
- 2026-10-08 19:41 JST、F1-resetは413/570対象・26,692/36,260 scored frameで、worker PID 1194634は稼働中。最新413行中407行・26,426 frameを凍結trajectory順、初出frame以降のframe ID/件数、P0/F0/F1 prompt parity、finite/in-range J/F、object平均、prediction PNG件数で独立監査し、異常0。累積処理速度からF1-reset完了は20:20ごろ、paired summaryと全件監査を含む完了は20:40ごろの見込み。
- 2026-10-08 19:46 JST、F1-resetは441/570対象・27,949/36,260 scored frame。全441行を凍結trajectory順、初出frame以降のframe ID/件数、P0/F0/F1 prompt parity、finite/in-range J/F、object平均、prediction PNG件数で独立監査し、異常0。評価worker PID 1194634とdetached pipeline PID 878216は稼働中。累積処理速度から評価完了は20:20前後、paired summaryと全件監査を含む完了は20:40前後の見込み。
- 2026-10-08 20:00 JST、F1-resetは494/570対象・31,495/36,260 scored frame。監査実行中にJSONLが進んだため全494行・31,495 PNGを凍結trajectory順、初出frame以降のframe coverage、P0/F0/F1 prompt parity、finite/in-range J/F、object平均で照合し、異常0。worker PID 1194634とpipeline PID 878216は稼働中。累積速度から評価完了は20:19ごろ、paired summaryと全件監査は20:40ごろの見込み。
- 2026-10-08 20:10 JST、F1-resetは529/570対象・34,257/36,260 scored frame。全529行・34,257 PNGをfrozen trajectory順、frame coverage、P0/F0/F1 prompt parity、finite/in-range J/F、object平均で独立監査し、異常0。評価workerとpipelineは稼働中。累積速度から残り評価は約8分、paired summaryと全件監査を含む完了は20:40前後の見込み。

## 2026-10-08 MOSE temporal Mamba 実装・評価 closeout

承認済みspecに従ってSAM2全体を学習するF0と、SAM2全体＋temporal Mamba adapterを学習するF1を実装し、各条件でfit全2,789 video-object軌跡を1 pass学習した。TBPTT=8で軌跡全体の数値stateをcarryし、系列境界でのみstateを初期化した。tuning 125動画・313対象の候補評価に基づき、F0はstep 2789、F1はstep 2000を選択した。F1-resetは同じF1 checkpointを使い、推論時にMamba stateのみを各frame前にresetする診断条件とした。

### Lockbox結果

MOSEv1の固定lockbox 200動画・570対象を評価した。全対象はvideo frame 0から開始し、除外対象は0。各対象の初期box prompt frameを指標から除外し、後続GT補正なしで動画末尾までpropagateした。各条件570対象・36,260 scored frameを完走し、prediction PNGも条件ごとに36,260枚となった。

| 条件 | 動画平均J | 動画平均F | 動画平均J&F |
|---|---:|---:|---:|
| P0 (追加学習なし) | 0.66448 | 0.73719 | 0.70084 |
| F0 (SAM2全体追加学習) | 0.70270 | 0.77570 | 0.73920 |
| F1 (SAM2全体＋Mamba) | 0.70635 | 0.77769 | 0.74202 |
| F1-reset (Mamba stateを毎frame reset) | 0.70693 | 0.77837 | 0.74265 |

paired video bootstrapは10,000 resample、seed 123、95% percentile CI。

| 比較 (J&F差) | 平均差 | 95% CI | 解釈 |
|---|---:|---:|---|
| F1−F0 | +0.00282 | [−0.00669, +0.01157] | 下限が0を上回らず、事前基準では主仮説を支持しない |
| F1−F1-reset | −0.00063 | [−0.00156, +0.00004] | state carryの改善は観測されず、差は小さい |
| F0−P0 | +0.03837 | [+0.02159, +0.05731] | この条件ではMOSE追加学習による改善を確認 |

系列長三分位の境界は40 frame以下、41〜70 frame、71 frame以上。各群の対象数はshort 219、medium 163、long 188。F1−F0のJ&F差はshort +0.00678 [−0.00212, +0.01644]、medium −0.00186 [−0.02084, +0.01647]、long +0.00177 [−0.02242, +0.02323]。いずれもCIが0を含む。F1−F1-resetも全群でCIが0を含み、系列長ごとのstate carry効果は確認されなかった。これらは凍結済みlength planに従った記述的なsubgroup比較である。

### 監査と制約

- P0/F0/F1/F1-resetの全対象順、frame ID、初期prompt parity、有限・範囲内J/F、object/video/summary平均を独立再計算した。各条件の36,260 prediction PNGは、対象・frameごとの期待集合と一致した。
- frozen trajectory index、length plan、evaluation freeze、選択checkpoint、評価コードと実装hashを照合した。F1-resetのsummaryとpaired summary、および三分位別bootstrapを独立再計算し、全監査で不一致0。
- F0/F1の学習logは各2,789 updateで連番、固定sample orderと一致し、loss/LRはfinite。F0/F1のpeak allocated/reserved VRAMはそれぞれ20.400/20.564 GiB、20.415/20.676 GiB。
- F0は中断後にrecovery checkpointから再開したため、manifestから累積active training時間を復元できない。開始から完了までの168.3時間には待機時間・中断時間が含まれ、実学習時間として解釈しない。
- 本結果は1 seedの実験である。F1−F0のCIは0を含み、temporal Mambaの改善仮説は支持されない。seed間再現性や一般的な優位性は主張せず、追加seedが必要。

成果物は外部worktree `/mnt/HDD10TB-2/aburatani/worktrees/sam2-mose-temporal-mamba` の `runs/mose_temporal_mamba_20260930/` に保存した。主要な集計は `lockbox_paired_summary.json`、F1-resetの全frame出力は `lockbox/F1-reset/objects.jsonl` と `lockbox/F1-reset/predictions/`。
