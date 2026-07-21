# MambaStateful epoch1 HOTA再現確認

## 目的

過去に記録されたMambaStatefulの3シーケンス評価で、HOTAが約5になった結果が再現するかを確認する。P0.5で記録したHOTA 47.293との差が、推論条件ではなくcheckpointの学習段階に由来するかを切り分ける。

## 実験条件

- 対象: DanceTrack val `dancetrack0004`, `dancetrack0005`, `dancetrack0007`
- 学習: 現行`MambaStateful.yaml`と同じモデル・データ設定、`epochs: 1`
- checkpoint: 今回新規に生成した`epoch1.pth`
- 入力: 既存のdetector bbox
- association: Mamba予測bboxを主matching位置に使用する現行実装
- TrackEval: HOTA/CLEAR/Identity、`DO_PREPROC=False`
- 既存checkpoint・外部実装リポジトリのソースコードは変更していない
- 実行時の指定は`CUDA_VISUBLE_DEVICES=2`だったが、これは変数名の typo。スクリプトが参照する`CUDA_VISIBLE_DEVICES`は未指定だったため、実効GPUは0だった。GPU番号は評価値の条件を変えない。

## 結果

| 指標 | 3sequence combined |
|---|---:|
| HOTA | **4.7552** |
| DetA | 68.551 |
| AssA | 0.33101 |
| IDF1 | **0.44802** |
| MOTA | 54.203 |
| ID switches | 3,526 |

TrackEval一時出力: `/tmp/mamba_stateful_verify_20260721/trackeval/output/`

## 比較と解釈

今回の再実験は、過去ログのepoch1・3sequence結果（HOTA 4.7552、IDF1 0.44802）と一致した。したがって、HOTA約5の結果は再現可能である。

一方、P0.5のMambaStateful HOTA 47.293は、既存25sequence出力に対する比較値であり、epoch100相当の最終checkpoint候補と比較していた。今回のepoch1結果とは、主にcheckpointの学習段階と評価範囲が異なる。3sequenceに限定したP0.5の既存出力はHOTA 52.037だが、こちらも今回新規に生成したepoch1出力ではない。

また、別のGT-input単一動画診断でHOTA 5.27になった結果は、今回の4.7552とはcheckpoint・入力条件が異なるため、同一実験の再現値ではない。ただし、いずれも低HOTA時にはAssAが極端に低く、association経路が主要な問題という診断と整合する。

## 結論

`train_stateful_tracker.sh`を現行設定のまま実行した場合、学習途中のepoch1 checkpointを評価すればHOTA約5になることを確認した。HOTA 47.293との差は、単純なGPU指定差ではなく、少なくともcheckpointの学習段階と評価対象sequence数の違いによる。最終checkpoint同士の比較を行うには、同一split・同一sequence list・同一checkpoint epochで揃えた再評価が必要である。
