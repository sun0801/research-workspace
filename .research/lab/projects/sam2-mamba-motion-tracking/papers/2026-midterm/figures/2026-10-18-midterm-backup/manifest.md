# 中間発表の補足スライド（2026-10-18）

[発表原稿](../../2026-10-18-midterm-presentation-script.md)の想定質問に答えるための補足スライド。ユーザーの手元の版（`20261018_中間発表_油谷.pptx`）のデザイン（テーマ・レイアウト）を使い、図はすべて PowerPoint の図形・グラフ・表なので編集できる。`make_backup_slides.py`（python-pptx）で作り直せる。

| # | スライド | 答える質問 | 数字の出どころ |
|---|---|---|---|
| 1 | 系列ごとのHOTAの差 | 改善は意味があるか／どの系列で効くか | TrackEval の系列別 HOTA（SAMURAI：`TrackEval/data/trackers/dancetrack/val/my_samurai_model/pedestrian_detailed.csv`、Ours（state）：7/23 評価の `pedestrian_detailed.csv`）。グラフは PowerPoint のネイティブのグラフ |
| 2 | 評価の条件 | 一般的な MOT と比べられるか | 実験設定（全対象を正解 bbox で初期化、SAMURAI の並列化、SAM2 tiny、val 25系列） |
| 3 | マスク候補選択のスコアと重み | Mamba の予測をどれくらい使っているか | [kf_score_weight の比較](../../../../experiments/2026-07-28-sam2-kf-score-weight-epoch100-25seq.md)（w＝0.5）と表の値（w＝0.25）。w＝0.0 の実行は設定の取り違えで24系列が 0.5 になっていたため使わない（2026-10-18 に判明、同記録に訂正を追記）。表の Ours が w＝0.25 であることは推論ログ（candidate_debug の weighted_scores）から逆算して確認 |
| 4 | 等速の仮定による予測のずれ | なぜ学習ベースにするのか | [dancetrack0052 の図](../2026-10-14-kf-constant-velocity-example/manifest.md) |
| 5 | 動き予測器のMambaブロック | Mamba の構成 | 再構成版スライドの同名スライドを複写。d_model 256、d_state 16 は [7/23 の記録](../../../../experiments/2026-07-23-sam2-minimal-integration-25seq.md) |
| 5d | 動き予測器の各部分のテンソルの形 | どの部分がどんな形のテンソルを扱うか | 5 の Mamba ブロックの図をもとに描き直した図。形は学習コード `models/MambaStateful.py` と、学習済みの重み `epoch100.pth` の各パラメータの形（in_proj 1024×256，conv1d 512×1×4，x_proj 48×512，dt_proj 512×16，A_log 512×16，out_proj 256×512，head 256→256→4。合計約138万）で確認。B は系列の数（学習 64，推論 1），T は系列の長さ（学習 11，推論 1） |
| 5e | Selective SSMとA・B・C・D | 状態方程式・出力方程式の A, B, C, D が今回のモデルのどれにあたるか | `MambaStateful._step_layer`（Ā＝exp(Δ·A)，B̄＝Δ·B，h_t＝Ā h_{t−1}＋B̄ x_t，y＝C h_t＋D x_t）と重みの形（A_log 512×16，D 512，x_proj 48×512＝Δ16＋B16＋C16，dt_proj 512×16） |
| 5b | 手法1のMambaの学習方法 | Mamba をどう学習したか | 学習時に保存された `2025_09_aburatani_Mamba_Trackers/ssm_tracker/saved_ckpts/mamba_stateful_dancetrack/MambaStateful.yaml`、学習コード `dataset/stateful_dataset.py`・`models/MambaStateful.py`、学習データ `traj_anno_data/dancetrack_train.json`（417軌跡・348,910フレーム。`dancetrack.json` と同じ中身で、val とは別）。12フレームの窓ごとに状態を初期化して学習し、推論では状態を引き継ぐ（[P4a の spec](../../../../specs/2026-09-01-p4a-stateful-unroll-tbptt-spec.md) の L0 と同じ） |
| 5c | 手法1のMambaの入出力（1つの物体） | 推論時に Mamba が何を受け取り，何を出し，どう候補選択に使われるか | 表の Ours（state）を実行したときのコード（commit a6253e7 ＋ 実行時の差分 `results/sam2_stateful_minimal/20260723T_sam2_minimal_25seq/git.diff`）の `sam2_base.py`（mamba_stateful の分岐）と `mamba_stateful_motion_filter.py`、設定 `samurai_mamba_stateful/sam2.1_hiera_t.yaml`（重み 0.25、しきい値 0.3、最初の5観測は Mamba なし、直近12個、出力 1/50・±0.1）。今のリポジトリの設定ファイルは重み 0.5 になっているが、表の結果は 0.25 で実行したもの |
| 6 | 手法2の予備実験（MOSE） | 手法2の見込み | [MOSE の実験記録](../../../../experiments/2026-09-30-mose-temporal-mamba-finetuning.md)・README（lockbox 200動画、paired bootstrap 95% CI） |
| 7 | checkpoint の比較 | モデルの選び方 | 7/30 MTG の議事録（100 epoch と best-HOTA＝20 epoch） |

- 1 の「16系列で上回る」は小数まで比べたもの（差が 0.1 未満の系列が4つ）。以前の原稿メモの「14系列」は、小数第1位に丸めた表から数えた値で誤りだったので直した。
- 定性的評価のほかの例は、[抜き出したファイル](../2026-10-17-midterm-qualitative/2026-10-17-midterm-qualitative.pptx)の補足を使う。
