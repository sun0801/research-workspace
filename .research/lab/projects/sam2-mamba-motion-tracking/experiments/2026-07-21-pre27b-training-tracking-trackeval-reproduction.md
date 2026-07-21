# TrackEval組み込み前コミットの再現実験

## 目的

`27b74b2 feat(training): 検証損失とTrackEvalによる定期評価を追加` が、StatefulのHOTAを47付近から4.7付近へ変化させた可能性を検証する。

## 実験条件

- source commit: `27b74b2^` = `c4ff22d`
- 学習: 親コミットの`MambaStateful.yaml`、元設定の25epoch、追加validationなし
- checkpoint: 親コミットで新規学習した`epoch25.pth`
- 追跡: 親コミットの`ssm_tracker/track_stateful.py`
- sequence: `dancetrack0004`, `dancetrack0005`, `dancetrack0007`
- TrackEval: 現行TrackEval repository、HOTA/CLEAR/Identity、`DO_PREPROC=False`
- 実行場所: `/tmp/mamba_stateful_pre27b_20260721/`
- 現行実装repoのcheckpoint・ソースコード・追跡出力は変更していない

## 結果

| 指標 | 親コミット25epoch |
|---|---:|
| HOTA | **4.7552** |
| DetA | 68.551 |
| AssA | 0.33101 |
| IDF1 | 0.44802 |
| MOTA | 54.203 |
| ID switches | 3,526 |

## 比較

- 親コミット25epochの新規学習・追跡: HOTA `4.7552`
- 現行コードepoch1・3sequence: HOTA `4.7552`
- 現行コードepoch100・3sequence: HOTA `4.7552`
- 過去の既存出力: HOTA `47.293`（25sequence）、`52.037`（同じ3sequence）

## 結論

`27b74b2`のTrackEval組み込み前に戻して25epoch学習しても、HOTAは4.7552だった。したがって、少なくともこのcommitのvalidation追加だけが47付近から4.7へ落としたとは説明できない。

47.293/52.037は、今回の親コミット再現出力とは別の既存追跡出力である。既存出力の生成時checkpointや当時の未保存作業ツリーのprovenanceが残っていないため、47付近を生んだ差分は、`27b74b2`以外の過去のcheckpoint・未コミット実装・推論条件のいずれかを追加照合する必要がある。
