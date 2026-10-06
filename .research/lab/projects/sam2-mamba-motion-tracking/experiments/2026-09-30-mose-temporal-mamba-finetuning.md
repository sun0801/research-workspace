---
project: sam2-mamba-motion-tracking
type: experiment-log
status: in_progress
created: 2026-09-30
last_updated: 2026-10-06
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
- 再開時に学習ログがstep 1400へtrimされたことを確認。再開後はstep 1436/2,789まで進み、step 1〜1,436のlossは全てfinite（最大419.36）、固定sample orderとの不一致0件、step連番に欠落なし。再計算したstep 1421は最長500-frame軌跡でloss 2.5397、finiteで完走。GPU0で学習継続中。
- GPU1は別のSAM2MOTプロセスが使用中のため、F0残り候補のtuning評価はGPU1のcompute process終了を待つキューに維持。F0 selectorも6候補のsummaryが全て揃うまで待機中。lockbox評価は未実施。
- F0復旧以降の実装コードにはfinite検査・prompt tensor記録・manifest/実行時間記録が追加されている。学習更新の主要計算は同一であることを確認済みだが、再開以後に適用した追加コード差分を最終manifestと記録で追跡する。
