---
date: 2026-07-16
project: sam2-mamba-motion-tracking
type: meeting-materials
topic: validation-implementation-and-stateful-diagnostic
status: draft
target_meeting: null
notion_url: null
notion_export: null
tags: [meeting-materials, research, validation, trackeval, profiling, state-carry]
---

# 2026-07-16 MTG資料: validation実装・profiling・MambaStateful診断

## 0. 今日のMTGで先生に相談したいこと

1. 7/9以降に実装したvalidation導線を、現時点の実験基盤として採用してよいか。
2. `val loss`と物体追跡全体を評価する`mot_metrics`を分け、`val_loss_period=5`、`mot_metrics_period=10`で運用する方針でよいか。
3. MambaStatefulはcached inferenceでNaNが発生しているため、現行full validation結果を相関分析から保留し、実装修正を優先してよいか。
4. MambaTrack / TrackSSMは、MambaStatefulの修正と並行してval loss–MOT metrics相関分析を進めてよいか。
5. state carryの修正は、まずcache経路の正常化を行い、fallback/resetは別ablationとして扱う方針でよいか。

## 1. 現時点の全体結論

7/9 MTGで決めた「`val loss`とtracking全体評価を分離して観察する」ための実装・運用基盤は、smokeとparity確認の範囲で成立した。

一方、MambaStatefulのfull validationでは、epoch 10/90のcheckpointが異なるにもかかわらずtracking outputが完全一致した。局所診断の結果、frame 6でstateful predictionの`pending_delta`がNaNになり、matchingが全失敗していた。

したがって、現在の主な論点は「val lossとHOTA / IDF1の相関」へ進む前に、MambaStatefulのcached inference経路を正常化すべきかどうかである。

## 2. 7/9 MTGからの流れ

### 7/9 MTGで決まったこと

- `val loss`とtracking全体評価を区別して運用する。
- tracking評価の名称を、第三者にも意味が伝わる形へ整理する。
- TrackEvalの関数化導線を、既存CLI導線と比較して単体検証する。
- tracking validationの計算時間を、学習・val loss・tracker推論・TrackEvalに分解する。
- MIRUポスターではSAM2 / SAMURAIの改善を主題とし、Mambaは方法として説明する。

### 7/10〜7/15の実装・検証

- tracking指標群の正式namespaceを`mot_metrics`へ整理。
- TrackEvalのCLI/API parityを1sequence・3sequenceで確認。
- Mamba側のTrackEval評価を、tracker推論subprocessを維持したまま直接関数呼び出しへ置換。
- `val_loss_period`、`mot_metrics_period`、`timing_enabled`と区間別wall-clock計測をMamba側へ追加。
- 100epoch実験用に3モデルのcanonical YAMLを更新。

### 7/16の診断

- MambaStatefulのepoch間MOT metrics不変を、Comet表示ではなくtracking pipelineの問題として調査。
- epoch 10/90、`dancetrack0004`、frame 1〜7のprediction・matching・state transitionを記録。
- frame 6のNaN predictionを確認。

## 3. 実装成果

### 3.1 validation指標の命名整理

1-step予測誤差と物体追跡全体の評価を分離するため、次の名称へ整理した。

| 役割 | 名称 | 記録例 |
|---|---|---|
| 1-step予測誤差 | `val_loss` | `val_loss/epoch_mean` |
| tracking全体評価 | `mot_metrics` | `mot_metrics/HOTA`, `mot_metrics/IDF1` |

`mot_metrics`ではHOTA、DetA、AssA、MOTA、IDF1を記録する。`best_tracking_hota`はcheckpoint選択の意味があるため、既存名を維持した。

### 3.2 TrackEval CLI/API parity

TrackEval側で評価本体を関数化し、既存CLIと同じ結果を返すか確認した。

- `dancetrack0004`の1sequence: CLIと関数のsummary完全一致
- `dancetrack0004/0005/0007`の3sequence: CLIと関数のsummary完全一致
- `output_msg=Success`
- `py_compile`、`--help`、`git diff --check`: PASS

この段階ではMamba側のtracker推論導線は変更していない。

### 3.3 Mamba側TrackEval直接呼び出し

Mamba側ではtracker推論subprocessを維持し、TrackEval評価だけを直接関数呼び出しへ置き換えた。

確認内容:

- mockでTrackEval subprocessが0回、関数呼び出しが1回
- 実TrackEval adapterでsummary生成に成功
- 既存25sequence tracker outputでCLI経由とadapter経由のsummary完全一致
- combined HOTA / IDF1も一致

未変更:

- `track.py` / `track_stateful.py`の通常tracker推論
- `train.py` / `train_stateful.py`の学習導線
- summary parseの既存処理

### 3.4 周期制御と時間profiling

Mamba側に次の計測・制御を追加した。

- `val_loss_period`
- `mot_metrics_period`
- `timing_enabled`
- 学習区間、val loss区間、epoch全体のwall-clock
- tracker推論subprocess、TrackEval、summary parseの区間時間

`timing_enabled=false`では追加のtiming処理を行わず、metric結果も一致することを確認した。

### 3.5 100epoch実験設定

3モデルのcanonical YAMLを次の設定へ更新した。

| 設定 | 値 |
|---|---:|
| epochs | 100 |
| val loss周期 | 5epoch |
| mot_metrics周期 | 10epoch |
| MambaStateful LR scheduler | `none`のまま |

optimizer、モデル構造、trackerアルゴリズム、TrackEval metricは変更していない。

## 4. Evidence: 計算時間profiling

MambaStatefulの3sequence部分計測では、次の時間だった。

| 区間 | 時間 |
|---|---:|
| 学習 | 146.172秒 |
| val loss | 24.573秒 |
| tracker推論subprocess | 316.973秒 |
| TrackEval直接呼び出し | 3.490秒 |
| summary parse | 0.000081秒 |

主なボトルネックはTrackEvalではなくtracker推論subprocessだった。

3sequence時間からの単純概算では、100epochのvalidation部分は次の方向になる。

- 現行周期: val毎epoch、MOT 5epochごと
- 候補周期: val 5epochごと、MOT 10epochごと
- 候補周期では評価回数が減り、総時間を大幅に削減できる見込み

ただし、full official valの絶対時間は部分valから保証できないため、実測が必要である。

## 5. Evidence: MambaStatefulのfull validation診断

### 5.1 Cometで1本の線に見えた理由

epoch 10, 20, ..., 80で`mot_metrics`は複数回実行されていた。各回のHOTA / IDF1等が完全に重なったため、Comet上では1点または水平な1本の線に見えていた。

### 5.2 frame 6の診断結果

| 指標 | epoch 10 | epoch 90 |
|---|---:|---:|
| prediction対象track数 | 3 | 3 |
| NaN `pending_delta` | 3 | 3 |
| NaN `predicted_last_bbox` | 3 | 3 |
| matching stage 1のmatch数 | 0 | 0 |
| frame 6の出力track数 | 0 | 0 |
| `update_missing` | 3 | 3 |
| `mark_lost` | 3 | 3 |
| `activate` | 3 | 3 |

epoch 10/90の通常tracking outputは完全一致した。

```text
SHA256: 73631b0c658520ca332e9926ece7d4399d801fd4266a8d25ca767ae4c27297f7
```

## 6. Interpretation: 学習が進んで見えた理由

MambaStatefulの学習datasetは、軌跡から固定長の重複windowを作る。各windowの`condition`を通常forwardへ入力し、window内の出力とlabelでlossを計算する。

```text
training: [x1...x12] → normal forward → loss
          [x2...x13] → normal forward → loss

stateful inference: [x1...x5] → cache保存 → x6 → cache更新 → x7
```

学習時もwindow内ではMambaの内部状態を使うが、window終了後にその状態を次のsampleへ持ち越さない。一方、stateful推論では`InferenceParams`のcacheをtrackごとに継続利用する。

したがって、train lossが低下していても、cached inference経路が正常とは限らない。今回の問題は、学習そのものよりも、学習時に直接検証していなかったstateful inference経路で発生している。

## 7. 今回言えること / まだ言えないこと

### 今回言えること

- validationの指標分離、周期制御、timing計測、TrackEval adapterはsmoke/parity範囲で成立した。
- tracking validationの主要コストはtracker推論である。
- MambaStatefulのflatなMOT metricsは、Cometの記録不具合ではない。
- frame 6でNaN predictionが発生し、trackingが同じ退化パターンへ入っている。
- 現行MambaStateful結果は、epoch間性能比較やval lossとの相関分析に使うべきではない。

### まだ言えないこと

- state carry型Mambaがsliding window型より性能的に劣るか。
- NaN修正後のMambaStatefulのHOTA / IDF1推移。
- val lossとHOTA / IDF1の本来の相関。
- NaNの根本原因がcache API、`seqlen_offset`、入力scale、数値安定性のどれか。
- 100epoch・10観測点の相関から、汎用的なcheckpoint選択基準を導けるか。

## 8. 方針候補・比較

| 方針 | 内容 | 利点 | 懸念 |
|---|---|---|---|
| A: cached inference修正 | cache初期化、offset、入力scale、layer出力を切り分ける | state carry本来の性能を検証できる | 追加の実装・診断時間が必要 |
| B: NaN fallback/reset | NaN時に検出bboxへfallback、またはstate reset | trackingを早く動かせる | 根本原因を隠す可能性がある |
| C: 他モデルを先行 | MambaTrack / TrackSSMの相関分析を先に進める | 研究全体を止めない | state carry比較は後回しになる |

推奨は、Aを主修正、Bを別ablation、Cを並行検討とする構成である。

## 9. 次に進む候補

1. epoch 10/90の同一5フレーム履歴で、normal forwardとcached forwardを比較する。
2. `InferenceParams`のcache初期化、`seqlen_offset`、入力scale、各Mamba layer出力のfinite性を確認する。
3. NaN検出時fallback/resetは、根本修正とは別のablationとして評価する。
4. 修正後に1sequence smokeを実施する。
5. finiteなpredictionとtrack continuityを確認してから、少数sequence、full validationへ戻る。
6. MambaStatefulを保留したまま、MambaTrack / TrackSSMのval loss–MOT metrics対応表と相関を先に集計する。
7. 相関分析は10点の探索的結果として扱い、best epochや有意性を過大解釈しない。

## 10. 図・生成物

今回は新規の実験図は作成していない。説明用には次の流れで十分である。

```text
validation実装・TrackEval parity
        ↓
周期制御・timing計測
        ↓
100epoch full validation
        ↓
MambaStatefulのcached inferenceでNaN
        ↓
stateful結果を保留、cache経路修正へ
```

次回、必要であればepoch 10/90のframe 5〜7について、prediction bbox・IoU・track stateを並べた診断図を追加する。

## 11. 参照ファイル

- [前回MTG議事録](../meetings/2026-07-09-mtg.md)
- [前回validation実装資料](2026-07-09-validation-implementation-mtg-materials.md)
- [validation timing実装smoke](../experiments/2026-07-15-validation-timing-implementation-smoke.md)
- [TrackEval CLI/API parity](../experiments/2026-07-15-trackeval-cli-api-parity.md)
- [Mamba側TrackEval直接呼び出し](../experiments/2026-07-15-mamba-trackeval-direct-call.md)
- [full validation相関分析spec](../specs/2026-07-15-full-validation-correlation-analysis-spec.md)
- [full validation YAML変更ログ](../experiments/2026-07-15-full-validation-correlation-config-implementation.md)
- [frame transition診断spec](../specs/2026-07-16-statecarry-frame-transition-diagnostic-spec.md)
- [frame transition診断結果](../experiments/2026-07-16-statecarry-frame-transition-diagnostic.md)
- [state carry MOT metrics診断](../experiments/2026-07-16-statecarry-mot-metrics-diagnostic.md)
