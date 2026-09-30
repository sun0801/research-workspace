---
date: 2026-09-30
project: sam2-mamba-motion-tracking
type: meeting-materials
topic: weekly-progress
status: draft
target_meeting: null
notion_url: null
notion_export: null
tags: [meeting-materials, weekly-progress, temporal-mamba, sam2mot]
---

# 2026-09-30 MTG資料: temporal Mamba統合とSAM2MOT再現の進捗

対象期間: 2026-09-23〜2026-09-30  
前回MTG: 2026-09-25

## 0. 今日相談したいこと

1. temporal Mambaは、まずMOSEv1でSAM2単独追加学習とSAM2＋adapter追加学習を比較する案で進めてよいか。初回は単一対象VOSのmask品質を見る設計で、ID routingの改善は対象外。
2. SAM2MOT再現は、S3で観測した効果が事前specの想定と異なった。S4へ進む前に、成功基準・機構署名を実測に整合する形へ見直す方針でよいか。

## 1. 全体像

今週は、研究の主線であるtemporal Mambaを「接続できるか」の段階から「学習で役立つか」を比べるpilotへ進めた。同時に、補助線として進めているSAM2MOT再現は、S3の効果をA6とA7に分けて評価し、有害だったA7を既定から外した。

| テーマ | ここまで | 現在 | 次に考えていること |
|---|---|---|---|
| temporal Mamba | 最小adapterをSAM2へ接続し、1系列を完走 | MOSEv1の承認済みspecに沿ってF0/F1の学習pilotを実施。TBPTT=8でpreflightを通過 | pilot checkpointのtuning評価を揃え、全学習の予算と設定を固定する |
| SAM2MOT再現 | S0検出、S1 baseline、S2 Object Addition、S3 CoIまで評価 | A7は有害。A6のみでも事前の機構署名とは不一致 | spec上の判定基準を見直してから、A6のみを前段にS4を検討 |

## 2. temporal Mamba: 接続確認から学習pilotへ

### 段階1 — 何を解きたいかを整理（9/25）

SAM2 decoder自体はフレーム間stateを持たない一方、decoder入力の特徴`pix_feat`はSAM2の過去フレームmemoryを反映している。そこで既存SAM2部品を置き換えず、decoder直前へtemporal Mambaを追加し、時間情報がマスク出力に役立つか調べる方向を選んだ。

初期検証ではID routingや複数人物管理を同時に変えず、単一人物で接続とstate更新だけを確かめる。人物別`pix_feat`の後段に置くため、この位置のMambaは既存の人物別memory/routingに依存し、ID対応そのものを直すものではない。

### 段階2 — 最小実装の範囲を固定（9/27）

decoder直前の`pix_feat`に、空間平均した特徴を1 tokenとして入力するMamba adapterを置くspecを作成した。Mambaの残差をゼロにした条件では、既存SAM2と同じ出力になることを確認する設計とした。

### 段階3 — 推論接続とstate更新を確認（9/28）

DanceTrack `dancetrack0004`の1人物で、1,203フレームを処理した。

- adapterを有効にして残差をゼロにした条件は、16フレームの出力が既存SAM2と完全一致した。
- 全1,203フレームでstateが1回ずつ更新され、reset後の再実行も一致した。
- 未学習Mambaの残差を有効にした条件では、stateと出力が有限で、残差が非ゼロであることを確認した。

ここまでで**推論経路に接続して時系列stateを更新できる**ことは確認できた。未学習重みのため、mask品質や追跡性能が良くなったとはまだ言えない。

### 段階4 — MOSEv1追加学習の条件確定とpilot（9/30）

DanceTrackにはbboxとIDはあるがmask教師がないため、mask教師のあるMOSEv1を使う実験specを作成し、実装開始の承認を得た。単一対象に初回box promptだけを与え、後続のGT補正なしでmaskを予測するVOS条件を固定している。主比較は、同じ初期checkpointと学習条件でのF0（SAM2全体追加学習）対F1（SAM2全体＋temporal Mamba adapter追加学習）。

| 条件 | 何を測るか |
|---|---|
| P0: 追加学習前SAM2 | 元checkpointの基準 |
| F0: SAM2全体をMOSEv1で追加学習 | データ適応だけの効果 |
| F1: SAM2全体＋temporal Mamba adapterを追加学習 | F0に対するadapter追加効果 |
| F1-reset | F1と同じ重みでMamba stateのみ毎フレームreset | 学習済みモデルのstate carryへの依存を診断 |

主比較はlockbox上のF1−F0のJ&F。F1−F1-resetはstate carry依存を調べる補助比較で、これだけでは時間情報の有用性を証明しない。fit 1,121系列、tuning 125系列、lockbox 200系列の動画単位分割を固定し、TBPTT=8で短・中央値・500-frame最長系列のpreflightを完了した。TBPTT=16はOOMのため採用していない。F0/F1各100軌跡のpilot学習は完了し、現在はcheckpoint選択に向けたtuning評価を進めている。F0 step 100のtuning評価は完了したが、F1との対応評価と全学習予算の確定前なので、性能比較やcheckpoint選択の根拠にはしていない。

### 次に進む案と未解決点

- F0/F1の同一条件比較を主実験として、pilot tuning結果を踏まえて全学習の予算・checkpoint間隔・選択規則を確認する。
- TBPTT=8でstate数値をcarryし、計算graphのみdetachする条件を固定済み。学習用state経路とstreaming推論の数値一致、有限gradient、DAVIS境界Fとの一致を確認した。
- 全学習後にtuningでcheckpointを選び、評価コードと設定を凍結してからlockbox 200系列を一度評価する。
- この初回実験が扱うのは単一対象mask品質。MOSEv1で改善しても、DanceTrackの複数人物ID維持に転移するとは限らず、別途評価が必要。

## 3. SAM2MOT再現: 段階的評価とA7の切り分け

### 段階1 — baselineとObject Addition（S0〜S2）

DanceTrack val 25系列で検出を用意し、baseline（S1）とObject Additionを加えたS2を評価した。

| 条件 | HOTA | DetA | AssA | MOTA | IDF1 | IDSW |
|---|---:|---:|---:|---:|---:|---:|
| S1 baseline | 59.21 | 48.71 | 72.11 | 46.64 | 64.41 | 425 |
| S2 + Object Addition | 64.32 | 63.09 | 65.73 | 59.77 | 71.13 | 1,162 |

S2は検出・追跡対象を追加し、HOTAを上げた一方、AssAが下がりIDSWが増えた。次段のCross-object Interaction（CoI）が誤追跡やIDの混線を抑えるかを確かめる段階に進んだ。

### 段階2 — CoIを追加（S3、9/28）

S2にA6（CoIによる誤追跡メモリ除外）とA7（低信頼エントリのメモリ除外）を加え、25系列で評価した。

- S2比でHOTAは64.32から67.13、MOTAは59.77から76.88へ上昇し、IDSWは1,162から898へ減少。
- 一方AssAは65.73から62.52へ低下。事前specが想定した「AssA増・DetAほぼ不変」という機構署名は成立しなかった。
- MOTA改善の大部分はFP減少に対応しており、CoIがID対応を改善したと単純には言えない。

この時点ではA6とA7を同時に有効にしていたので、AssA低下の原因を切り分ける必要があった。

### 段階3 — A7だけを外して寄与を確認（9/30）

S3本番条件からA7だけを外し、A6のみで同じval 25系列を再評価した。

| 条件 | HOTA | DetA | AssA | MOTA | IDF1 | IDSW |
|---|---:|---:|---:|---:|---:|---:|
| S2 | 64.32 | 63.09 | 65.73 | 59.77 | 71.13 | 1,162 |
| S3 A6のみ | 68.22 | 72.26 | 64.57 | 76.88 | 75.42 | 839 |
| S3 A6+A7 | 67.13 | 72.29 | 62.52 | 76.88 | 72.74 | 898 |

A7を加えるとHOTA −1.09、AssA −2.05、IDF1 −2.68、IDSW +59となり、association側が悪化した。A7を無効にする判断はすでに反映済みで、S4前段はA6のみrunとする。

### 現在地と次の判断

A6のみでもS2比でHOTA +3.90、MOTA +17.10だが、AssAは−1.16、DetAは+9.17。MOTA上昇の主因はFP減少で、specが予想した機構とは異なる。したがって、次はS4をすぐ進めるより先に、何を成功とみなすか、論文の数値と機構署名をどう対応させるかを整理する段階。

次段の候補は、specの機構署名を実測可能で論文記述とも矛盾しない形へ修正し、その判定条件を固定したうえでA6のみを基準にS4を検討すること。S4の実装・評価はまだ行っていない。

## 4. 今回の相談事項

1. **temporal Mamba:** 承認済みのF0対F1設計に沿い、pilot tuning結果を踏まえて全学習の予算・checkpoint間隔・選択規則を固定する。
2. **SAM2MOT:** A7は無効、A6のみをS4前段とする判断は済んでいる。S4前にspecの機構署名・成功判定を改め、どの条件を満たしたら先へ進むかを決めたい。
3. **優先順位:** SAM2MOT再現は期限付きの補助線として扱い、主線のtemporal Mamba学習比較を優先する整理を続けてよいか。

## 5. 参照ファイル

- [9/25 MTG議事録](../meetings/2026-09-25-mtg.md)
- [temporal Mamba decoder最小統合spec](../specs/2026-09-27-temporal-mamba-decoder-minimal-integration-spec.md)
- [temporal Mamba 1系列smoke結果](../experiments/2026-09-28-temporal-mamba-decoder-minimal-smoke.md)
- [MOSEv1 temporal Mamba追加学習spec（承認済み）](../specs/2026-09-30-temporal-mamba-mose-finetuning-spec.md)
- [MOSEv1追加学習pilotログ](../experiments/2026-09-30-mose-temporal-mamba-finetuning.md)
- [adapter学習のbrainstorm](../../../../secretary/notes/brainstorm/2026-09-30-temporal-mamba-adapter-training.md)
- [SAM2MOT S0〜S2結果](../experiments/2026-09-27-sam2mot-s0-s2-results.md)
- [SAM2MOT S3 CoI結果](../experiments/2026-09-28-sam2mot-s3-coi-results.md)
- [SAM2MOT A7切り分け](../experiments/2026-09-30-sam2mot-s3-a7-ablation.md)
