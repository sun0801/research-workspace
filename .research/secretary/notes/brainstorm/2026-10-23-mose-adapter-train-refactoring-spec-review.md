---
date: 2026-10-23
project: sam2-mamba-motion-tracking
source_todo: null
topic: mose-adapter-train-refactoring-spec-review
status: exploratory
tags: [brainstorm, research, spec-review, refactoring]
---

# mose_adapter_train リファクタリングspecの妥当性検査

検査日時: 2026-10-23 17:30 JST。読み取りによる設計・実装照合。GPU実験は実施していない。

## 結論

方針は妥当。ただし、R5の精度・モデルモード・合格条件が十分に固定されておらず、現状のまま実装開始するには修正が必要。R0〜R4の整理と、val lossの意味が変わるR5は、検証上明確に分ける。

以下の「修正案」はレビュー提案であり、採用・承認済みの設計ではない。対象spec、実装、README、TODOは変更していない。

## 読み込んだ文脈

- [対象spec](../../../lab/projects/sam2-mamba-motion-tracking/specs/2026-10-23-mose-adapter-train-refactoring-spec.md)
- プロジェクトREADME、2026-10-23 TODO、2026-10-23 MTG議事録。
- 2026-10-18 V3学習specと実験ログ。adapter単体の経路一致、正規化の1ulp修正、同GPUでのF0一致、checkpointingの照合実績を確認。
- 実装repo `/mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2` の `1002_seminar`、HEAD `ff78b577f49a60404ed38b911f0293d48738e26b`。trackedな変更なし。未追跡の `AGENT_RESEARCH.md` と `CLAUDE.md` あり。
- `training/mose_adapter_train.py`、`training/eval_mose_fulltrack.py`、`training/mose_fulltrack.py`、`training/model/sam2.py`、`sam2/modeling/sam2_base.py`、`sam2/modeling/temporal_adapters.py`、train用YAML。
- Mamba_Trackersの `train_mamba_stateful.py` 冒頭で、val lossとMOT評価が別関数として取り込まれていることを確認。参照元の数値的な同等性までは今回の判定根拠にしていない。

## 妥当な点

- 短いclipでの学習への変更とDanceTrack評価を別specにする。10/23 MTGの目的と矛盾せず、変更原因を切り分けられる。
- 凍結評価ファイルを編集せず `evaluate_track` を利用する。現在のvalと評価関数は、先頭frameの除外、元解像度への補間、prompt seed、履歴削除の基本規則が一致している。
- 同GPU・同commitを基準に、段階ごとに比較して進める。
- optimizerの実際の除外対象、loss重み、freeze状態を記録する。
- R5では旧val lossと数値が変わりうることを認め、学習重みとJ&Fの保存を別に検証する。

## 実装前に修正したい点

### 1. 高: 「共通fp32」「R5の新旧lossをfp32で比較」が現コードでは成立しない

対象spec: 104、120、127行。

現行の `validate` は `mose_adapter_train.py:421` で無条件にbf16 autocastを使う。`evaluate_track` も `eval_mose_fulltrack.py:134` で無条件にbf16。`stream_inference_timing` も同様。`--no-bf16` は `run_trajectory` の精度を変えるが、これらの精度は変えない。

R5で `run_trajectory` をそのまま使うと、照合実行では「旧lossはbf16、新lossはfp32」という比較になり、経路変更と精度変更の差が混ざる。2回実行で結果が一致したとしても、fp32で比較した根拠にはならない。

修正案: 精度を経路ごとに明記する。凍結J&F経路は従来どおりbf16、学習比較はfp32とする。旧val lossのfp32比較が必要なら、凍結評価ファイルを変更せずR0の検証ハーネスに参照処理を用意する。単なる `--no-bf16` 指定で全経路がfp32になるとは扱わない。

### 2. 高: R5のval lossに、誤実装を検出できる合格基準がない

対象spec: 95、127、148行。

「差を記録」「差が大きいときに調査」には、どの差なら許容するか、正しい新lossとは何かが定義されていない。adapter単体の経路一致だけでは、SAM2全体のモード、encoderのバッチ化、前処理、平均の計算まで正しいとは判断できない。

修正案: R0で旧 `run_trajectory` を検証ハーネスから固定入力・固定拡張・固定modeで呼び、意図する新しいval lossの参照値を取得する。新val lossはこの参照値と比較し、旧推論lossとの差は定義変更の参考値として別に記録する。対象ごとのprompt座標・labels・frame数も合格条件に含める。J&Fは動画平均、lossは従来どおり対象平均を維持することを明記する。

### 3. 中: val lossの「学習経路」がモデルのtrain/evalを指定していない

対象spec: 94〜96行。

`run_trajectory(train=False)` は勾配の有無を切り替えるだけで、`model.training` は設定しない。現行 `validate` は入口で `model.eval()` を呼ぶ。一方、通常学習では `set_frozen_modes` によりSAM2のトップだけtrain、SAM2の子moduleはeval、adapterはtrainになる。

新しいvalでJ&Fの直後にそのままlossを計算すると、トップもadapterもevalのままになる。明示stateを渡すadapter経路と、SAM2自身のtrain/eval分岐は別の条件。SAM2にはmemoryのstrideやmaskの扱いなどmode依存の分岐がある。ただし、現在の設定・前向き単対象追跡で必ず数値差が出るとまでは今回確認していない。

修正案: 「evalモードのまま共通forwardを使う」のか「通常学習と同じトップ/子moduleのmodeで勾配だけ止める」のかを明記する。各経路の前のmode設定、対象間のstate reset、終了時・例外時の復元を決め、検証する。

### 4. 中: 既存の「拡張なしdict」は色変換を完全には無効化しない

対象spec: 81〜83、95行。

`load_frame_uint8` の96〜99行、および凍結 `load_frame` の226〜229行は、dictのbrightness等が1でも、frame seed由来のbrightness/contrast/colorを追加適用する。

従って、既存dictを渡すだけでは文字どおりの無拡張にならない。逆に今回これを除去すると、既存J&FやF0との同一条件を壊す可能性がある。

修正案: 今回は「従来valと同じ前処理（frame別の色変換を含む）」を保つことを明記し、両経路の入力一致を確認する。完全な無拡張への変更は別の挙動変更として扱う。

### 5. 中: 保持・変更するmeasure経路が検証対象にない

対象spec: 48、83、107〜119、142行。

R2はmeasureの保持を掲げ、R3では `stream_inference_timing` の履歴削除を変更する。しかしR0の実行表にはmeasureがない。また「軌跡がchunk_lenより長い」だけでは、古い履歴を実際に削除する分岐を通った保証にならない。

修正案: V1/V3でmeasureのtrain→inferenceを通す条件を追加し、時間・VRAMを除く対象・frame数・OOM状態・mode復元を確認する。少なくとも1対象は履歴保持幅を超え、TBPTT境界・末尾の端数chunk・実際の履歴削除を通す。履歴削除の結果も参照実装と照合する。

### 6. 中: train照合のV3設定と実行手順が再現可能な粒度まで固定されていない

対象spec: 109〜113、117行。

pilotのV3にはchunk_len=2とcheckpointingが明記されているが、trainのV3にはない。CLI既定値および本学習YAMLはchunk_len=8であり、fp32・math attentionでA4000に収まる根拠はこの設定について書かれていない。過去の一致確認はV3 3段をchunk_len=2にしている。

修正案: R0で全コマンドまたは専用YAMLを固定し、trainもV3はchunk_len=2・checkpointingありと明記する。各runのLR、warmup、val_interval_steps=1、grad_log_interval、入力indexとcheckpointのhash、対象ID、出力先を記録する。checkpoint比較にはscheduler・step・sample_orderも含める。

resumeは旧resumeと新resumeを比べる条件と、連続実行との比較を区別する。現行コードはresume時にdelta_normの基準を再作成するので、連続実行とresumeの全ログが一致するとは扱わない。参照runの成果物を壊さない独立したコピーで検証する。

## 未解決の問い・判断が必要な点

- 新val lossで、SAM2トップのmodeをどう定義するか。
- R5の参照値をどの固定条件で取得し、どの数値を合格条件にするか。
- 先にR0〜R4を完了し、R5を別段階で承認するか、同じspec内でR5の契約まで具体化するか。どちらも可能だが、前者は挙動保存の承認範囲を明確にしやすい。

以上が残るため、対象specの「未決事項: なし」は検査結果と整合しない。採用する修正を決めたうえで更新するのがよい。

## 次アクション候補

- 精度表とval lossのmode・参照値・合格基準をspecに補足する。
- R0の実行条件を固定し、measureと履歴削除の確認を追加する。
- 上記の具体化後に実装開始を判断する。

TODOへの追加、specの改訂、実装開始は行っていない。

---

## 追記 17:39 — 改訂specの再レビュー

2026-10-23のレビュー反映版（213行）を再読。実装repoのHEADは引き続き `ff78b57`。以下が最新の判定であり、上の初回レビューの未解決事項はこの改訂で概ね解消された。

**判定: 設計として妥当。R0の基準取得に進める内容になった。** 経路ごとの精度、val lossのevalモード・state管理、参照値との合格基準、既存の色変換の保持、measureと履歴削除の確認、trainのV3設定、resumeの比較条件が明記された。これらを再び設計から検討し直す必要はない。R0で決定論が成立するかは実測で確定する。

R0の実行条件・比較スクリプトを固定するとき、次の2点を明確化する。

1. **フレーム数は同じ意味の値を比べる。** spec 107・174行の「フレーム数が一致」は、lossが先頭を含む `n` フレーム、J&Fが先頭を除く `n-1` フレームであることを踏まえる。現行 `run_trajectory` の `frames` は `n`（358行）、旧valの `frames_scored` は `n-1`（444行）。両者を直接等値比較せず、loss側の処理フレーム数と、J&F側の採点フレーム数を区別して確認する。
2. **val lossの参照値は同じadapter重みで取る。** spec 150行の参照値は、V1/V3それぞれ、step 0・1・2の各重みに対応させる。初期重みだけの参照値を学習後のvalへ流用しない。重みとchunk_lenを含む固定条件を参照値に紐付ける。R5の比較時は旧新の同stepの重みが一致していることも確認する。

軽微な記述修正: spec 135行は「step 0・1・2でval、step 1・2でcheckpoint」が現行処理と一致する。現行step 0は `run_val(0)` のみ（607行）で、checkpointは保存しない。step 0参照値は初期化直後の重みから取得できる。

今回もGPU実験・spec変更・外部実装変更は行っていない。実装開始承認の代わりになる判定ではなく、specの妥当性に対するレビューである。
