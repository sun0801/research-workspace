---
date: 2026-07-15
project: sam2-mamba-motion-tracking
source_todo: TrackEval リポジトリ側で、関数化した評価導線が単体で正しく動くか確認する
topic: trackeval-direct-call-direction
status: exploratory
tags: [brainstorm, trackeval, validation, refactor]
---

# TrackEval評価導線の直接関数呼び出し化

## 読み込んだ文脈

- 2026-07-09 MTGで、TrackEvalの関数化と学習ループ統合を分けて確認する方針になった。
- TrackEvalには既存の `Evaluator.evaluate()`、`MotChallenge2DBox`、各metricクラスによるPython APIがある。
- `run_mot_challenge.py` はCLI引数解析と評価オブジェクト構築を `__main__` 内で行っている。
- Mamba側の `mot_metrics.py` は、tracker推論とTrackEval評価を別々の subprocess として起動している。

## 相談の出発点

TrackEval評価を学習ループから呼び出す際、tracker推論まで同時に変更すると原因切り分けが難しくなるため、まずTrackEval評価 subprocessだけを直接関数呼び出しへ置き換える方針を検討した。

## 問い

同じtracker出力を入力したとき、既存CLI導線とPython関数導線でHOTA等の評価結果が一致するか。

## 仮説

- TrackEvalの評価コアはすでに関数化されているため、CLI処理を薄い関数ラッパーへ分離すれば、Mamba側から再利用できる。
- tracker推論 subprocessを維持したまま評価部分だけを置き換えれば、評価導線の問題とtracker推論の問題を分離できる。
- 直接関数呼び出し化はプロセス起動やsummaryファイル経由を減らせるが、TrackEval本体の計算量を自動的に減らすものではない。

## 実験・実装案

### 第1段階: CLIと関数の結果一致

- 固定済みtracker出力を用意する。
- CLIでDanceTrack valを評価する。
- 同じGT・tracker・metric設定で、TrackEvalのPython APIを直接呼ぶ。
- HOTA / DetA / AssA / MOTA / IDF1 とsummary出力を比較する。

### 第2段階: Mamba側の評価subprocessだけ置換

- `mot_metrics.py` のtracker推論 subprocessは維持する。
- TrackEval評価 subprocessのみ、TrackEvalの関数ラッパーまたはAPI呼び出しへ置き換える。
- 初回は既存のsummary出力と `_parse_summary()` を維持し、プロセス境界だけを変更する。

### 第3段階: 結果辞書の直接利用

- 第2段階の一致を確認した後、summaryファイルparseを廃止する。
- `Evaluator.evaluate()` の戻り値から必要なmetricを直接抽出する。

## 比較・評価軸

- CLIと関数呼び出しのmetric値が一致するか
- GT / tracker / metric / split設定が一致しているか
- summary出力先と読み取り先が一致するか
- 既存tracker出力を破壊・混入しないか
- tracker推論とTrackEval評価の実行時間を分離して測れるか

## 今回見えた方向性

最初に変更する対象はTrackEval評価だけとする。tracker推論は従来のsubprocessを残し、評価部分の動作一致を確認した後にのみ、結果辞書の直接利用や追加の最適化を検討する。

## 次アクション候補

1. TrackEvalのCLI導線を `parse/build config` と `run evaluation` に分離する計画を作る。
2. 固定tracker出力を使ったCLI/API一致確認を実施する。
3. Mamba側の評価subprocess置換のspec化を行う。
4. spec承認後、TrackEval側とMamba側の変更範囲を確定する。

## Spec化候補

TrackEval CLI/API parity確認と、Mamba側の評価呼び出し置換を含む小さな実装specにできる。ただし、外部リポジトリ編集は、承認済みspec・変更範囲・検証方法・実装開始承認が揃ってから行う。

## 未解決の問い

- TrackEval側に薄い `run_mot_challenge(config)` を追加するか、Mamba側から既存の `Evaluator` APIを直接呼ぶか。
- 第1段階でsummaryファイルを比較対象に含めるか。
- 1シーケンスのsmokeから始めるか、既存の固定val出力で全valを使うか。

---

## 追記 2026-07-15

### 方針の収束

MambaTrackers側にTrackEvalの評価コードを複製して完全内製化する案を検討したが、現時点では採用しない。

- MambaTrackersから評価を実行できることは維持する。
- 評価ロジックの正本はTrackEval側に置く。
- Mamba側は薄いadapterとしてTrackEval APIを呼び出す。
- TrackEvalのコード複製やmetricの再実装は、コード重複・結果乖離・保守負担が大きいため保留する。
- 将来的に運用上の自立性が必要になった場合は、TrackEvalのcommit/version固定、依存関係の明示、起動時の存在確認を先に検討する。

今回の直接関数呼び出しは、固定tracker出力25 sequenceでCLIとadapterのsummary一致まで確認済みである。このため、短期的には現在の境界を維持し、次はtracker推論時間とTrackEval評価時間のprofilingへ進む。

## 関連ファイル

- `/mnt/HDD10TB-2/aburatani/TrackEval/scripts/run_mot_challenge.py`
- `/mnt/HDD10TB-2/aburatani/TrackEval/trackeval/eval.py`
- `/mnt/HDD10TB-2/aburatani/TrackEval/trackeval/datasets/mot_challenge_2d_box.py`
- `/mnt/HDD10TB-2/aburatani/2025_09_aburatani_Mamba_Trackers/ssm_tracker/train_utils/mot_metrics.py`
- `.research/lab/projects/sam2-mamba-motion-tracking/specs/2026-07-07-validation-implementation-spec.md`
