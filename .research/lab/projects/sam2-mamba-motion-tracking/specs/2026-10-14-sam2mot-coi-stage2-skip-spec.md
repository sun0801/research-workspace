---
date: 2026-10-14
project: sam2-mamba-motion-tracking
source: brainstorm
status: approved
approved: 2026-10-14
tags: [spec, experiment, sam2mot, reproduction, cross-object-interaction, a6, ablation, dancetrack]
---

# SAM2MOT再現 CoI の Stage 2 を除外に使わない案（val 25系列） Spec

## 目的

CoI（A6 のみ）の Stage 2（logit 差が 2.0 以下のとき、直近10フレームの logit 分散で B を決める判定）をメモリ除外に使わない設定を、DanceTrack val 25系列で現行の S3 と比べる**探索実験**である。CoI の AssA 不足（val −1.16、test −2.0）と HOTA 寄与の不足（val +3.90、test +3.6、論文 +5.9）を、GT を使わない変更で縮められるかを確かめる。

GT を使わないので、結果は性能値として扱える。ただし Stage 2 を外すのは論文の手法の変更なので、報告するときは**「再現実装の変更版（ablation）」**として扱い、論文の CoI の再現値とは区別する。

## 背景

- CoI 診断のステップ2（`experiments/2026-10-13-sam2mot-coi-exclusion-diagnosis.md`）で、Stage 2 の判定は、診断対象の5系列の初回区間で分類できた衝突フレームのうち 37 / 65（56.9%）が誤除外だった。Stage 1（logit 差 > 2.0）は 5 / 222（2.3%）。これは選んだ5系列の、分類できたフレームだけの集計で、独立な65エピソードでも Stage 2 全体でもない。したがって「Stage 2 の判定は五分五分」とは断定できないが、**診断対象では Stage 2 の誤除外が多く、無効化を試す動機がある**
- 同じくステップ2で、乗り移りが続いた衝突エピソードでは、B の判定の入れ替わり（揺れ）が約3倍だった（H1b、基準を満たす）
- ステップ3のオラクル CoI では、判定できた誤除外を GT で取り除いても、3系列の AssA はノイズ幅の2倍以上は戻らなかった。一方、GPU を変えただけで3系列の AssA が 9 ポイント動くことが分かり、系列を絞った比較はノイズに埋もれやすい。そこで本 spec は val 25系列で比べる
- 現行 S3（A6 のみ、`results/tracks/s3_coi_no_lowconf/`、GPU 0）の val 25系列: HOTA 68.22 / DetA 72.26 / AssA 64.57 / MOTA 76.88 / IDF1 75.42。B 判定 9,195 件のうち Stage 1 が 6,936 件、Stage 2 が 2,259 件（25%）、メモリ除外 8,799 件
- 論文（AAAI 刊行版）の Stage 2 は「A は記憶劣化で緩やかに下がり分散が小さく、B は急な遮蔽で急落し分散が大きい」という前提に立ち、本再現の実装はこの記述どおりである。Stage 2 を除外に使わない設定は**論文の記述からの逸脱**（A6 の解釈の変更）であり、採用する場合は spec A6 の行と実装リポジトリの logs に理由を記録する

## 検証したい問い

Stage 2 の判定でメモリ除外をしないと、val 25系列の AssA・HOTA は現行 S3 より上がるか。そのとき MOTA・DetA（重複トラックの除去の効果）はどれだけ失われるか。

## 仮説

- Stage 2 による除外には正しいトラックのメモリを外すものが含まれ、AssA を下げている。除外しなければ AssA と HOTA が上がる
- 対立: Stage 2 で外していたものの一部は重複トラックで、外さないと重複が残って FP が増え、MOTA と DetA が下がる。HOTA は AssA の改善と DetA の低下の差し引きで決まる

## 実験・実装内容

### 実装（実装リポジトリ `sam2mot_repro/`）

- `sam2mot/config.py` に `coi_stage2: str = "variance"`（`variance` | `skip`）を追加する。既定 `variance` は現行どおり
- `sam2mot/tracker.py` の `_coi_identify` で、`skip` のときは logit 差が `coi_logit_margin` 以下のペアを B と同定せず（メモリ除外しない）、件数を `coi_stage2_skipped` に数える。判定記録（`--coi-event-log`）には `stage = 2`、`flagged = None`、`reason = "stage2_skip"` で残す
- `scripts/s4_run_qr.py` に `--coi-stage2 {variance,skip}` を追加し、manifest に `coi_stage2_skipped` を出す
- Stage 1 の判定、メモリ除外の方法（A6）、A7（無効）、その他の段は変更しない

### 実行

主比較は **GPU 0 で条件をそろえた variance 対 skip** とする。GPU 1 では両設定を回し、別環境でも同じ向きの差が出るかを確かめる（再現性の確認）。

| run | GPU | 設定 | 出力 | 所要（目安） |
|---|---|---|---|---|
| A: variance（GPU 0） | 0 | 既存の現行 S3 をそのまま使う | `results/tracks/s3_coi_no_lowconf/` | 実行なし |
| B: skip（GPU 0） | 0 | `s4_run_qr.py --no-qr --coi-stage2 skip --coi-event-log` | `results/tracks/s3_coi_stage2skip/` | 2.6時間 |
| C: variance（GPU 1） | 1 | `s4_run_qr.py --no-qr --offload-state-to-cpu` | `results/tracks/s3_gpu1_val25/` | 3〜4時間 |
| D: skip（GPU 1） | 1 | `s4_run_qr.py --no-qr --coi-stage2 skip --offload-state-to-cpu` | `results/tracks/s3_coi_stage2skip_gpu1/` | 3〜4時間 |

- B・C・D は並行して回す（C と D は GPU 1 上で並行。offload ありで peak VRAM は 2 GiB 未満）
- GPU 1 の offload は、0026 で offload の有無の出力が md5 一致することを確認済み（`results/tracks/gpu1_check/`）なので、offload 自体は結果を変えない
- C（現行コードのまま）は実装の変更より前に起動する
- S2 の val 25系列（`results/tracks/s2_addition/`、GPU 0）を、CoI の寄与（S3 − S2）の計算に使う

### 確認方法（満たさなければ停止して報告する）

1. **既定の動作が変わらない**: 実装後、既定（`variance`）で 0026・0063 の出力が既存 `s3_coi_no_lowconf` と md5 一致する
2. **skip が意図どおりに働く**（B の run の manifest と判定記録で確認）
   - Stage 2 による B 判定が 0 件（`coi_flagged_stage2 == 0`）
   - `coi_stage2_skipped` の件数が、判定記録の `reason = "stage2_skip"` の行数と系列ごとに一致する
   - 判定記録で、フレームごとに実際に除外されたトラックが、すべてそのフレームの Stage 1 の B 判定に含まれる
   - manifest の `coi_flagged_stage1` と `coi_memory_excluded` が、判定記録の件数と系列ごとに一致する
3. **Stage 1 の判定が保たれる**: 各系列で、最初の Stage 2 の衝突が起きたフレームまで、B の出力が既存 `s3_coi_no_lowconf` の出力と行単位で一致する（Stage 2 を外した影響は次のフレームのメモリから現れるので、それまでは同じになるはず）

## 使用データ・モデル

- DanceTrack val 25系列（GT は TrackEval の評価にのみ使う）
- 検出 `results/detections/co_dino_l_coco_val25/`（3x_coco）、SAM2.1 large

## 比較対象・ベースライン

- 主比較: GPU 0 の A（variance）対 B（skip）
- 確認: GPU 1 の C（variance）対 D（skip）
- 参考: A と C の差（同じ設定・別 GPU の差。ノイズの目安だが1回だけなので、判定の閾値には使わない）
- S2: 既存 `s2_addition`（CoI の寄与の計算用）

## 評価指標

val 25系列の COMBINED（TrackEval）で、HOTA / DetA / AssA / MOTA / IDF1 / IDSW / FP / FN。

- Δ0 = B − A（GPU 0）、Δ1 = D − C（GPU 1）。指標ごとに出す
- 参考: A − C（同じ設定での GPU 間の差）
- CoI の寄与 = S3 − S2 を、variance と skip（GPU 0）で出し、論文（test、ΔHOTA +5.9 / ΔMOTA +17.7 / ΔIDF1 +6.5）と並べる
- 参考: 系列別の ΔAssA と ΔHOTA、`coi_stage2_skipped` の件数

## 成功/失敗の判断基準

結果を見る前に固定する。数値は確立した基準ではなく、事後に線を引き直さないための事前登録である。GPU 0 と GPU 1 でそれぞれ1回ずつの比較であることを結果に明記する。

**判定**（上から順に当てはめ、最初に当たったものとする）

| 判定 | 条件 | 次の行動 |
|---|---|---|
| 改善（採用候補） | Δ0 HOTA ≥ +0.5 **かつ** Δ1 HOTA > 0 **かつ** Δ0 AssA > 0 | spec A6 の行に変更候補として記録し、S4（Q-R あり）での確認と test 提出を別途相談する |
| 悪化（不採用） | Δ0 HOTA ≤ −0.5 **かつ** Δ1 HOTA < 0 | 現行の Stage 2 を維持する。この条件では Stage 2 の除外を外すと全体として悪くなると記録する |
| 不一致 | Δ0 HOTA と Δ1 HOTA の符号が逆で、どちらかの絶対値が 0.5 以上 | GPU 間で結果が一致しないので結論を出さない。差が数値誤差で動く範囲にあると記録する |
| HOTA 改善・AssA 低下 | Δ0 HOTA ≥ +0.5 **かつ** Δ1 HOTA > 0 **かつ** Δ0 AssA ≤ 0 | 改善の中身が DetA 側で、仮説（AssA の改善）とは別の経路。採用はせず、結果を記録して相談する |
| 差が小さい | 上のどれにも当たらない（\|Δ0 HOTA\| < 0.5 を含む） | 現行の Stage 2 を維持する。結論は「この条件では Stage 2 の無効化による HOTA の改善を確認できなかった」までにとどめる |

- どの判定でも、AssA・IDF1 の変化と DetA・MOTA の変化を併記する。HOTA が動かなくても AssA の改善と DetA の悪化が相殺している可能性があるので、そのときは相殺していると記録する（「Stage 2 では説明できない」とは書かない）
- 改善（採用候補）でも、Δ0 MOTA が −1.0 より大きく下がる場合は、その引き換えを結果に明記する

## 実施手順

1. 本 spec の承認を得る
2. 実装開始の承認を得る（Implementation Gate: 変更範囲 = `sam2mot/config.py`、`sam2mot/tracker.py` の `_coi_identify`、`scripts/s4_run_qr.py` の引数と manifest、検証方法 = 確認方法1〜3）
3. GPU 1 で C（現行コードのまま）を起動する
4. `--coi-stage2` を実装し、確認方法1（既定での md5 一致）を確認する
5. GPU 0 で B、GPU 1 で D を起動する
6. B について確認方法2・3を確認する
7. 4つの run を TrackEval で評価し、判断基準で判定して `experiments/` に記録する。実装リポジトリの `logs/` には実行の事実を書く

## 期待される結果

- 仮説どおりなら、AssA と IDF1 が上がり、IDSW が下がる。FP は少し増え、MOTA と DetA は少し下がる。GPU 0 と GPU 1 で同じ向きになる
- Stage 2 の除外が重複トラックの除去に大きく効いていた場合は、MOTA と DetA の低下が AssA の改善を上回り、HOTA は下がる

## リスク・懸念

- **論文からの逸脱**: 採用しても「論文の CoI の再現」ではなく「再現実装の変更版（ablation）」になる。結果の報告ではその旨を明記する
- **1回ずつの比較**: GPU 0・GPU 1 とも variance と skip を1回ずつ回すだけで、ばらつきの分布は分からない。2つの GPU で向きがそろうことを最低限の確認とし、境界付近の結果は断定しない
- **S4 への影響**: 本 spec は S3 での比較に限る。Q-R は CoI でフラグされたトラックを対象から外すので、Stage 2 を外すと Q-R の発動も変わる。S4 での確認は別途行う
- **GPU 障害**: 前回 GPU 0 が落ちた。長時間の run なので、`--resume` で再開できるようにし、障害時は記録して停止する

## 未決事項

- 改善（採用候補）になった場合に、S4 と test まで確認するか（結果を見て相談する）

## 関連

- brainstorm: `.research/secretary/notes/brainstorm/2026-10-12-sam2mot-val-improvement-plan.md`、レビューメモ `.research/secretary/notes/brainstorm/2026-10-14-sam2mot-coi-stage2-skip-review.md`
- 診断: `specs/2026-10-13-sam2mot-coi-exclusion-diagnosis-spec.md`、`experiments/2026-10-13-sam2mot-coi-exclusion-diagnosis.md`
- 再現 spec: `specs/2026-09-08-sam2mot-reproduction-spec.md`（A6）

## 改訂履歴

- 2026-10-14: レビューを受けて改訂（実行前）。(1) 判定表を上から順に当てはめる排他的な形にし、「悪化」「不一致」「差が小さい」を分けた。HOTA 改善かつ AssA 低下のケースを別扱いにした。(2) GPU 間の1回の差をノイズ幅とする判定をやめ、主比較を GPU 0 の variance 対 skip にし、GPU 1 でも両設定を回して向きの一致を確認する形に変更。(3) HOTA が動かない場合の結論を「Stage 2 の無効化による改善を確認できなかった」までにとどめ、相殺の可能性を併記するようにした。(4) 背景の「Stage 2 の判定は五分五分」を、診断対象の分類できたフレームの集計であることを明記した表現に修正。(5) skip が意図どおりに働くことの確認（Stage 2 の B 判定 0 件、記録とカウンタと実際の除外の整合、最初の Stage 2 の衝突までの出力の一致）を追加。報告は「再現実装の変更版（ablation）」として扱うと明記
