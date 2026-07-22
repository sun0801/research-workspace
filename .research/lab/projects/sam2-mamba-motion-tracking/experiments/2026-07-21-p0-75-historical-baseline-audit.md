date: 2026-07-21
project: sam2-mamba-motion-tracking
status: completed
tags: [experiment, p0-75, provenance, baseline, comet, reproducibility]
---

# P0.75 historical baseline audit and scale correction

## 目的

2026-07-02時点のMambaStateful HOTA約0.47と、現行導線のHOTA 4.7552の乖離について、checkpoint、commit／作業ツリー、detector入力、association、track lifecycle、TrackEval、出力取り違えを切り分ける。さらに、scale伝播修正で退化を再現・回復できるかを確認し、P1へ進むためのcorrected baselineを定義する。

## Comet provenance

### experiment key

- ユーザー指定の `46defef23fb9c4f4fbba691bac8423e82` はComet APIで取得できなかった。
- MTG議事録に記録された `46dfef23fb9c4f4fbba691bac8423e82` は取得でき、実験名は `mamba_stateful_dancetrack`、stateは `finished` だった。
- Comet URL: https://www.comet.com/sun0801/mamba-mot/46dfef23fb9c4f4fbba691bac8423e82

### 保存されていた条件

- command: `ssm_tracker/train_stateful.py --exp_name mamba_stateful_dancetrack --config_file ssm_tracker/cfgs/MambaStateful.yaml --device 0`
- epoch: 100
- optimizer: Adam、`lr0=1e-4`、scheduler `none`
- model/input: `MambaStateful`、window 12、`stateful_bbox`
- scaling: `scale_factor=50`、`scale_factor_bbox=1`、`scale_factor_delta=50`
- inference: `filter_thresh=0.2`、`new_track_thresh=0.6`、`enable_time_thresh=5`、`max_time_lost=30`、`missing_mode=self_update`、`delta_clip=0.1`
- git metadata: branch `refs/heads/master`、parent `f08cd5f`、origin `tamaki-lab/2025_09_aburatani_Mamba_Trackers`

### Comet artifactの限界

保存assetは `MambaStateful.yaml`、`ssm_tracker/train_stateful.py`、`train_utils/comet_logger.py` の3点だけだった。checkpoint、tracker推論ソース、detector入力、追跡output、TrackEval設定／summaryは保存されていない。git patchにはepochs 25→100、train.pyのimport整理、DanceTrack symlink削除があるが、tracking側のscale伝播変更は含まれない。したがってComet runの完全再現はできない。

## ローカル証跡

### checkpoint

旧checkpointは残っている。

- `/mnt/HDD10TB-2/aburatani/2025_09_aburatani_Mamba_Trackers/ssm_tracker/saved_ckpts/mamba_stateful_dancetrack/epoch100.pth`
  - 16,624,938 bytes
  - mtime: 2026-06-30 20:35:37
- 同じディレクトリにはepoch1〜100、`MambaStateful.yaml`、best checkpointがある。
- 7/15再学習系のcheckpointは別ディレクトリにあり、旧checkpointとは混在していない。

### TrackEval／出力

- 既存25系列出力を現行TrackEvalで評価した結果は HOTA 47.293 / DetA 74.933 / AssA 30.003。
- 同じ既存出力の3系列（0004/0005/0007）は HOTA 52.037 / DetA 82.884 / AssA 32.695。
- これは `/tmp/p0_5_state_carry_20260721/output_full/mamba_stateful/` と `/tmp/mamba_stateful_old_output_verify2_20260721/trackeval/output/mamba_stateful/` のsummaryで確認した。
- したがって47.293/52.037はTrackEval計算だけの差ではなく、少なくとも追跡output自体は現行TrackEvalでその値になる。

### 旧checkpoint＋旧推論条件の隔離再推論

7/2時点の保存merge状態 `ce1db7d` を `/tmp/mamba_stateful_historical_ce1db_20260721/` に展開し、同一detector入力の0004/0005/0007、旧epoch100 checkpoint、保存済みconfig（bbox scale 1 / delta scale 50）で再推論した。外部実装repoのmaster、checkpoint、sourceは変更していない。

現行TrackEval（HOTA/CLEAR/Identity、`DO_PREPROC=False`）の結果:

| 条件 | HOTA | DetA | AssA | IDF1 | ID switches |
| --- | ---: | ---: | ---: | ---: | ---: |
| 旧checkpoint + ce1db7d旧推論 + 0004/0005/0007 | 49.666 | 82.342 | 29.981 | 45.012 | 106 |
| 既存旧outputの同3系列 | 52.037 | 82.884 | 32.695 | 49.741 | 102 |

評価出力は `/tmp/mamba_stateful_historical_eval_20260721/output/historical_ce1db/` に保存した。

## 乖離の原因判定

### 確認済み

1. **TrackEval設定単独ではない。** 47.293/52.037の既存outputを現行TrackEvalで再評価できた。
2. **checkpoint単独ではない。** 同じ旧epoch100 checkpointを現行系と旧ce1db系で通すと、旧推論条件では49.666、現行再現記録では4.7552になった。
3. **実行コード／未保存作業ツリーの差が主因の一つである。** `ce1db7d` の `track_stateful.py` は `scale_factor_bbox=1` と `scale_factor_delta=50` をtrackerへ渡す。一方、`e5a6052`および`c4ff22d`相当ではこの2値が伝播されず、tracker側のfallbackによりbboxも `scale_factor=50` で処理される。ただし、GitHub上の`c4ff22d`自身の差分は出力先変更のみであり、この差を`c4ff22d`の変更とは断定しない。
4. **Comet runの学習条件はbbox scale 1 / delta scale 50だった。** 7/2保存作業ツリー以後の通常推論導線は、この条件の2値をtrackerへ伝播していなかった。`c4ff22d`自身の差分は出力先変更のみである。
5. **epoch不足だけではない。** 現行epoch1・epoch100・pre-27b親commit再学習はいずれも4.7552という既存記録と整合する。

### 推定

- 7/2の約47は、Cometで学習したscale条件に対応する旧tracking側の未保存変更（または同等の作業ツリー）で旧epoch100 checkpointを推論した結果と考えるのが最も整合的である。
- 4.7552は、通常commit系列でscale伝播が欠落し、bbox入力の正規化係数が学習時と推論時で不一致になった退化結果と推定する。

### 不明

- 既存25系列の47.293および3系列の52.037を生成した正確なcheckpoint hash、detectorファイルの版、tracker作業ツリー、実行コマンドは残っていない。
- 旧条件の隔離再推論49.666と既存旧output 52.037の差（HOTA 2.371、IDSW 4）の正確な原因は、旧outputファイル本体／detector版／未保存差分不足のため確定できない。
- Cometにはtracking output・TrackEval設定・HOTA metricがないため、Comet画面の約0.47がこのtraining run直結の評価か、別実行の評価かは確定できない。

## P0.75の判断

- historical baselineの完全再現はできないが、HOTA 4.7552への大幅退化を生んだ主要な実装差（bbox/delta scaleの伝播欠落）は特定・修正・再検証できた。
- 同一旧checkpoint・同一detector入力3系列・同一TrackEval条件で、修正前はHOTA 4.7552、修正後は49.666となり、7/2保存作業ツリーと完全一致した。したがって、4.7552は壊れた推論導線のregression baselineであり、P1のcanonical baselineには使わない。
- 修正後のHOTA 49.666は3系列のcorrected baseline anchorである。過去の25系列output HOTA 47.293／3系列output HOTA 52.037との差は、checkpoint、detector版、または未保存の別条件が残るため、完全再現値とは扱わない。
- P0.75は完了扱いとし、P1へ進む。ただしP1開始時に、scale修正commit `104c6ad`を含む導線で25系列のcorrected A1 baselineを記録する。
- P1ではassociation選択だけを変更し、checkpoint、detector入力、track lifecycle、TrackEval設定を固定する。P1は最終手法ではなく、prediction-primary associationの因果効果を測る診断実験とする。
- P2/P3はP1の結果を記録してから判断する。P1でAssA／IDF1／IDSWの改善が確認できない場合、P2/P3へ自動的には進めない。

## spec正式追記案（未反映）

spec候補へ次のP0.75項目を追記する案を作成したが、`2026-07-21-state-carry-improvement-spec-candidate.md`は変更していない。

> **P0.75: historical baseline audit（短期・変更なし）**
>
> Comet key／local checkpoint／git provenance／detector入力／tracker output／TrackEval設定を照合する。旧outputを現行TrackEvalで再評価し、取得可能な旧checkpointは隔離worktreeで同一3系列再推論する。完全再現できない場合は、旧47系をhistorical reference、scale修正後の現行導線をcorrected baselineとして固定し、P1 association診断へ進む。旧runの成功値をP1の成功基準に使わない。




## 2026-07-22 実装修正検証

`d52bb81`を基準に隔離worktree `/tmp/mamba_stateful_scale_forward_fix_20260722/` を作成し、`ssm_tracker/track_stateful.py`へ `scale_factor_bbox` と `scale_factor_delta` の読み出し・伝播を追加した。元repoのmaster、checkpoint、sourceは変更していない。

同一の旧epoch100 checkpoint・同一detector入力3系列（0004/0005/0007）・同一TrackEval条件（`DO_PREPROC=False`）で比較した。

| 条件 | HOTA | DetA | AssA | IDF1 | ID switches |
| --- | ---: | ---: | ---: | ---: | ---: |
| 修正前 `c4ff22d`相当 | 4.7552 | 68.551 | 0.331 | 44.802 | 3526 |
| scale伝播修正版 | 49.666 | 82.342 | 29.981 | 45.012 | 106 |
| 7/2保存作業ツリー `ce1db7d` | 49.666 | 82.342 | 29.981 | 45.012 | 106 |

修正版が`ce1db7d`と完全一致したため、4.7552への退化はscale伝播欠落で再現・修正できた。過去の既存output 47.293/52.037との差は、checkpoint、detector版、または未保存の別条件が残るため、完全再現とは別に扱う。


## 2026-07-22 P0.8 実験成果物保持の実装

承認済みspec `2026-07-22-experiment-artifact-retention-spec.md`に沿って、元repo `/mnt/HDD10TB-2/aburatani/2025_09_aburatani_Mamba_Trackers`へ実装を反映した。

- checkpoint保存先を `ssm_tracker/saved_ckpts/<exp_name>/<run_id>/`へ分離し、`manifest.json`、configコピー、`git.diff`、`final.pth`を保存する。既存checkpointは削除・上書きしない。
- Track output保存先を `track_results/<dataset>/<tracker>/<split>/<run_id>/`へ分離した。`--run_id`指定と、既存run directoryを明示的に上書きする`--overwrite`を追加した。
- checkpoint payloadへ`format_version`とrun metadata（run_id、epoch、config、command、git情報）を追加した。旧checkpointの`model`／`optimizer`／`epoch`形式は維持する。
- 学習中TrackEvalの中間出力を`<trackeval_root>/<run_id>/epoch<epoch>/`へ分離し、epoch間の削除処理を除去した。
- Cometへrun名、run metadata、config、manifest、`git.diff`、final／best checkpointを記録する導線を追加した。Comet無効時もローカル成果物は保存される。

検証: 元repoで対象7ファイルの`py_compile`、`git diff --check`、provenance smoke、checkpoint metadata smoke、tracking CLIの`--run_id`／`--overwrite`表示を確認した。GPUを使う本学習・全系列trackingは未実施であり、P1の前に1回の保存導線smokeを実データで実施する。
