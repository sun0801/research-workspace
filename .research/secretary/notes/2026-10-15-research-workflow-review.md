---
date: 2026-10-15
project: sam2-mamba-motion-tracking
type: research-workflow-review
source: user-request
tags: [research, retrospective, workflow]
---

# 最近の研究の進め方の質と量の評価

## 対象と評価の限界

- ユーザー依頼: 「最近の研究の進め方の質と量を評価して」。
- 2026-09-15〜2026-10-15を対象とし、直近の10/9〜10/15を重点確認した。
- 対象はREADMEから特定した主研究 `sam2-mamba-motion-tracking`。もう1件の運用ガバナンスプロジェクトは直近の更新がなく、本評価の対象外とした。
- ローカルのREADME、MTG議事録5件、主要実験ログ、TODO、ファイル一覧を使用。外部実装コード・生の実験出力を今回再監査したものではない。
- 評価は記録に基づく定性的判断。他の学生との比較、実働時間、GPU稼働時間、本人とAIの作業分担、本人の理解度は判断できない。

## 総合評価

活動量は多く、再現条件の確認・機構の切り分け・不都合な結果の扱いは良い。一方、中心となるtemporal Mambaの仮説を有効に検証するまでの効率と、複数作業の優先順位には大きな改善余地がある。現状は、実験基盤と原因理解が進んだ一方、新規手法の有効性を確定する成果はまだ不足している。

「結果が有意でなかったこと」自体を低評価の理由にはしない。評価上の問題は、追加部分が実質未学習のまま大きな評価へ進み、検証したかった問いに十分答えられなかったことである。

## 量の評価

ファイル名の日付が対象期間に入る直下のMarkdownを集計した。図のmanifest・外部参考資料・README・TODOを除く。既存ファイルへの追記は新規件数に含まれない。

| 記録の種類 | 9/15〜10/15 | 10/9〜10/15 |
|---|---:|---:|
| 実験・分析ログ | 22 | 6 |
| MTG議事録 | 5 | 2 |
| MTG・発表関連資料 | 7 | 5 |
| spec | 7 | 2 |
| 論文・調査メモ | 3 | 1 |
| brainstorm | 13 | 3 |

記録件数は独立実験数や本人の作業量ではない。9/25の関連分析には同じ出力を複数の観点で扱った記録もあるため、総件数をそのまま成果数にはしない。

実質的な実施内容としても、P4aの複数条件・seedでの100 epoch学習、YOLO/SAM2側の比較、decoder最小接続、MOSEのF0/F1各2,789更新と4条件の200動画評価、SAM2MOTのS1〜S4再現と各種切り分け、成功・失敗双方の定性動画作成がある。複数の比較・診断を完了しており、活動不足とは評価しない。

## 質の評価

| 観点 | 評価 | 根拠 |
|---|---|---|
| 比較・評価の厳密さ | 強み | 条件固定、checkpoint来歴、tuningとlockboxの区別、paired CI、seedの制約を記録している |
| 原因の切り分け | 強み | SAM2MOTを段階分解し、A7、Q-Rの入れ方、CoIの損失構造、GPUによる変動を調べている |
| 結果解釈・修正 | 強み | 非改善案を維持しない、Mambaの無効と実質未学習を区別する、成功例と失敗例を両方示す |
| 本評価前の成立確認 | 改善優先度が高い | finite・勾配到達・hashの確認に対して、adapterが十分更新され出力へ寄与するかの確認が遅れた |
| 優先順位と完結 | 改善余地が大きい | 10/9のLR問題発見後、10/14にも修正未着手。再現診断・発表準備・設計候補整理が並行している |
| 論文の中心主張への接続 | まだ弱い | 新しいtemporal Mambaの有効性は未検証。SAM2MOT再現の前進だけでは提案法の有効性を証明できない |

### 強みを示す具体例

1. SAM2MOTのQ-Rは、当初S4 HOTA 61.85まで悪化した後、conditioning frame追加と補正を切り分け、補正方式で69.25になった。単なる閾値探索から原因理解へ進んでいる。
2. CoI Stage 2を除外に使わない案は、AssAが改善してもDetAが悪化し、HOTA差がGPU 0で−0.02、GPU 1で+0.15にとどまった。事前の判定に従って現行維持とし、部分指標だけで採用しなかった。
3. 定性評価は3手法×4パターン、各2例を選び、提案法だけ失敗する例も含めた。定量表と異なる出力を使った旧動画も区別している。
4. MOSEではF1−F0のJ&F差+0.00282と95% CI [−0.00669, +0.01157]を報告し、単一seedの制約も明記した。その後、adapterの実質未学習を受けて解釈を訂正した。

### 最も大きい改善点

MOSEの新規adapterはalphaが約2e-4以下、出力層もほぼ不変だった。10/7のstep100以降にも小さいalphaが記録されていたが、finite/nonzeroであることと、意図した追加処理が十分に学習されていることは別である。長い学習とlockbox評価の前に、パラメータ更新量・残差の寄与・小規模な学習成立を確認する判断が必要だった。これは事後診断自体の丁寧さとは別に評価する。

10/9〜10/14に実装と学習が進まなかった点は、中心課題への投入が遅れた証拠になる。ただし、その間に中間発表資料と定性動画を作成しており、研究活動全体が止まっていたとは言えない。10/14 MTGではV3から始める方針が了承されているため、その後も停滞したと断定しない。

## 進め方の改善候補

以下は助言であり、承認済みの実験計画・TODOではない。

1. 本学習・本評価へ広げる条件に「追加モジュールが十分に更新され、出力へ影響している」を含める。小規模確認で答えられる不確実性を先に減らす。
2. 期限のある発表・原稿準備と、中心仮説の検証を優先して時間を確保する。SAM2MOT再現の追加調査には一区切りの条件を置く。
3. 毎週、実験数より「答えが出た問い」「棄却・保留できた案」「次に答える最重要の問い」を短くまとめる。分単位の稼働監査の記録量と、研究上の進歩を区別する。
4. TODOは完了済み・未完了・保留を実験ログと照合する。9/24のYOLO比較など、実施記録があるのに日次TODOが未完了のままの例があり、チェックボックスから完了率を計算しない。

今後の実験設計や外部コード変更をこの評価だけで承認済みとは扱わない。

## 根拠ファイル

- [プロジェクトREADME](../../lab/projects/sam2-mamba-motion-tracking/README.md)
- [9/17 P4a探索](../../lab/projects/sam2-mamba-motion-tracking/experiments/2026-09-17-p4a-unroll-tbptt-hyperparameter-search.md)
- [9/18 MTG](../../lab/projects/sam2-mamba-motion-tracking/meetings/2026-09-18-mtg.md)
- [9/25 MTG](../../lab/projects/sam2-mamba-motion-tracking/meetings/2026-09-25-mtg.md)
- [9/30 MTG](../../lab/projects/sam2-mamba-motion-tracking/meetings/2026-09-30-mtg.md)
- [MOSE実験と10/9事後診断](../../lab/projects/sam2-mamba-motion-tracking/experiments/2026-09-30-mose-temporal-mamba-finetuning.md)
- [Q-R切り分け](../../lab/projects/sam2-mamba-motion-tracking/experiments/2026-10-03-sam2mot-s4-qr-results.md)
- [10/9 MTG](../../lab/projects/sam2-mamba-motion-tracking/meetings/2026-10-09-mtg.md)
- [定性比較動画](../../lab/projects/sam2-mamba-motion-tracking/experiments/2026-10-12-qualitative-pattern-videos.md)
- [CoI除外診断とオラクル介入](../../lab/projects/sam2-mamba-motion-tracking/experiments/2026-10-13-sam2mot-coi-exclusion-diagnosis.md)
- [CoI Stage 2 skip比較](../../lab/projects/sam2-mamba-motion-tracking/experiments/2026-10-14-sam2mot-coi-stage2-skip.md)
- [10/14 MTG](../../lab/projects/sam2-mamba-motion-tracking/meetings/2026-10-14-mtg.md)
