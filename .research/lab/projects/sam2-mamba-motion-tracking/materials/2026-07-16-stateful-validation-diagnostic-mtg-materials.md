---
date: 2026-07-16
project: sam2-mamba-motion-tracking
type: meeting-materials
topic: stateful-validation-diagnostic
status: draft
target_meeting: null
notion_url: null
notion_export: null
tags: [meeting-materials, research, validation, state-carry, diagnostic]
---

# 2026-07-16 MTG資料: MambaStateful validation退化の診断と次方針

## 0. 今日のMTGで先生に相談したいこと

1. MambaStatefulのfull validation結果を、NaNが発生した不正な推論結果として相関分析から保留する方針でよいか。
2. 次はモデルの学習条件を変えず、`InferenceParams`を使うcached inference経路の実装修正を優先してよいか。
3. 修正後の検証を、1sequence smoke → 少数sequence → full validationの順で進める方針でよいか。
4. MambaTrack / TrackSSMの結果は、MambaStatefulを保留したまま先に相関分析を進めてよいか。

## 1. 現時点の結論

MambaStatefulの`mot_metrics`がepoch間で変化しなかった直接原因は、Cometの記録問題ではなく、stateful inferenceで`NaN`が発生してtrackingがframe 6付近で退化したことだった。

epoch 10とepoch 90は異なるcheckpointだが、両方とも同じNaN → matching失敗 → track再生成の経路に入る。そのため、今回のHOTA / IDF1は「stateful手法の性能がepoch間で同じ」とは解釈できない。

## 2. 前回MTGからの流れ

前回は、1-step予測を測る`val loss`と、tracking全体を測るHOTA等を分けて記録し、両者の関係を確認する方針を決めた。また、tracking validationの計算コストはTrackEvalではなくtracker推論が支配的であることを確認した。

今回、全モデルを100epoch、`val_loss_period=5`、`mot_metrics_period=10`に揃える実験を開始した。その過程でMambaStatefulのtracking結果に退化を発見した。

## 3. 実施したこと

- 3モデルのcanonical YAMLを100epoch条件へ変更。
- `val_loss_period=5`、`mot_metrics_period=10`を設定。
- MambaStatefulについてepoch 10/90の同一sequence比較を実施。
- frame 1〜7のprediction、matching、state transitionをJSONLへ記録する診断モードを追加。
- 通常tracking outputが診断前の結果と一致することを確認。

診断用の外部コード変更は、`track_stateful.py`のCLI引数と`stateful_tracker.py`のログ記録だけで、通常経路のtracker挙動は変更していない。

## 4. Evidence: 確認できたこと

### 4.1 MOT metricsが1点に見えた理由

MambaStatefulのvalidation logでは、epoch 10, 20, ..., 80で`mot_metrics`が複数回実行されていた。しかし値が完全に重なっていたため、Comet上では水平な1本の線に見えていた。

### 4.2 frame 6の診断結果

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

frame 6では、既存trackの予測bboxがNaNになり、IoUが全て0になった。検出は新規trackとしてactivateされるが、frame 1以外でactivateされたtrackは同一frameに出力されないため、frame 6の出力が空になっていた。

### 4.3 epoch 10/90の通常tracking output

`dancetrack0004`の通常tracking outputはepoch 10/90で完全一致した。

```text
SHA256: 73631b0c658520ca332e9926ece7d4399d801fd4266a8d25ca767ae4c27297f7
```

診断JSONLはepochごとにframe 1〜7の7行を生成し、診断JSONL自体もepoch 10/90で完全一致した。

## 5. Interpretation: 現時点の見立て

### 5.1 学習が進んで見えた理由

MambaStatefulの学習では、固定長の重複windowを通常forwardへ入力してlossを計算する。window内ではMambaの内部状態を使うが、window処理後に状態は次のsampleへ持ち越されない。

一方、tracking時は`InferenceParams`のcacheをtrackごとに保持し、frame間でstateを継続する。このcached inference経路が学習時のloss計算では直接検証されていなかった。

したがって、train lossが下がることと、stateful tracking inferenceが正常に動くことは別の条件である。

### 5.2 何が問題か

現時点で確定したのは、「stateful推論経路がNaNを返して成立していない」ことである。これは単なる予測精度の低さではない。

ただし、NaNの発生源がMamba本体、cache初期化、`seqlen_offset`、入力scale、または実装上の更新順序のどこかまでは未確定である。state carryという研究アイデア自体が無効だとは、まだ言えない。

## 6. 今回言えること / まだ言えないこと

### 今回言えること

- MambaStatefulのflatなMOT metricsは、Cometの記録不具合ではない。
- frame 6でNaN predictionが発生し、trackingが同じ退化パターンに入っている。
- 現行stateful結果をepoch間の性能比較やval lossとの相関分析に使うのは不適切である。
- train lossの低下だけではcached stateful inferenceの正常性を保証できない。

### まだ言えないこと

- state carry型Mambaがsliding window型より性能的に劣るか。
- val lossとHOTA / IDF1に本来どの程度の相関があるか。
- NaN修正後のMambaStatefulのbest epochやfull validation性能。
- NaNの根本原因がcache APIの使い方、数値安定性、入力条件のどれか。

## 7. 方針候補・比較

| 方針 | 内容 | 利点 | 懸念 |
|---|---|---|---|
| A: cached inferenceを修正 | `InferenceParams`、cache、offset、入力scaleを切り分ける | 研究対象の本来のstate carryを検証できる | 原因特定に追加時間が必要 |
| B: NaN時fallback | 検出bboxへのfallbackやstate resetを入れる | trackingを動かしやすい | 根本原因を隠す可能性がある |
| C: State carryを保留 | MambaTrack / TrackSSMの相関分析を先に進める | 全体の分析を止めずに済む | state carryの比較が後ろ倒しになる |

現時点の推奨は、Aを主診断として進め、Bはablationとして分離し、Cを並行して検討することである。

## 8. 次に進む候補

1. 実際の5フレーム履歴に対して、通常forwardとcached forwardを同じcheckpoint・同じ入力で比較する。
2. cache初期化、`seqlen_offset`、入力scale、各Mamba layer出力のfinite性を確認する。
3. NaN検出時のfallback/resetは、根本修正とは別の診断用ablationとして比較する。
4. 修正後に1sequence smokeを実施する。
5. finiteなpredictionとtrack continuityを確認してから、少数sequence、full validationへ戻る。
6. MambaStatefulを保留したまま、MambaTrack / TrackSSMの10点相関分析を先に進めるか判断する。

## 9. 図・生成物

今回、新規の実験図は作成していない。frame transitionの説明は次の流れで十分に示せる。

```text
train: fixed window + normal forward → train loss低下
stateful inference: cache継続 → frame 6でNaN
                              → matching失敗
                              → track lost / new track activate
                              → epoch間MOT outputが同一
```

必要なら次回、epoch 10/90のframe 5〜7について、prediction bboxとmatching結果を並べた診断図を作成する。

## 10. 参照ファイル

- [full validation相関分析spec](../specs/2026-07-15-full-validation-correlation-analysis-spec.md)
- [frame transition診断spec](../specs/2026-07-16-statecarry-frame-transition-diagnostic-spec.md)
- [frame transition診断結果](../experiments/2026-07-16-statecarry-frame-transition-diagnostic.md)
- [state carryのMOT metrics診断](../experiments/2026-07-16-statecarry-mot-metrics-diagnostic.md)
- [full validation YAML変更ログ](../experiments/2026-07-15-full-validation-correlation-config-implementation.md)
- [前回MTG議事録](../meetings/2026-07-09-mtg.md)
- 外部診断成果物: `/mnt/HDD10TB-2/aburatani/2025_09_aburatani_Mamba_Trackers/artifacts/profiling/mamba_validation_2026-07-15/full_validation/statecarry_epoch_compare/frame_transition/`
