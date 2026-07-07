# 2026年3月〜7月2日 MTGサマリー（4ヶ月分）

> 複数のMTG議事録をもとに2026-07-07に整理。個別のMTG記録はNotionを参照。

---

## もともとの研究の方向性

初期の大きな方向性：

> **SAM2 / SAMURAI 系の物体追跡において，カルマンフィルタなどの単純な動き予測を，Mambaを用いた学習ベースの時系列モデルに置き換えることで，追跡性能を改善する**

最初の関心は，SAM2 / SAMURAIの追跡における弱点，特に

- 物体追跡中に対象がずれる
- 一度ドリフトすると補正が効きにくい
- SAM2 / SAMURAIの動き予測がカルマンフィルタベースであり，非線形運動や遮蔽に弱い可能性がある
- SAM3 / SAM2MOT / SAMURAIなど，SAM系の追跡モデルの改良可能性を調べる

というあたりにあった。

初期目標の一文まとめ：

> **SAM2/SAMURAIベースの物体追跡に，Mambaによる動き予測を導入して性能を上げる**

---

## 3月〜4月：SAM2 / SAMURAI系の追跡問題の把握

SAM2 / SAMURAI系の追跡をどう扱うか，特にMOTとして使う場合の実装上の問題を調査。

4月の**SAMURAIの途中入力**分析で判明したこと：

- 途中から出現するIDを追加する場合，既存IDのマスクが `NO_OBJ_SCORE` によって上書きされる
- 途中入力フレームで先行IDのマスクが消失する
- メモリアテンションに「物体なし」の情報が入る

この段階で確認されたこと：

- SAM2 / SAMURAIをそのままMOT的に使うと，途中出現IDや複数ID管理で問題が出る
- SAMURAIはSAM2の追跡に動き予測を追加しているが，MOTにそのまま適用するには実装上の注意が多い
- 物体追跡としてのSAM2/SAMURAIには，途中補正・再検出・ドリフト回復の弱さがある

→ この時点の研究の主眼は **「SAM2/SAMURAIをどうMOTに使うか」** に近かった。

---

## 5月前半：MambaTrackを使ったカルマンフィルタ代替の検討

5/14時点での整理：

- カルマンフィルタ：mean + covariance を明示的に持つ
- MambaTrack：過去6〜10フレーム程度のbbox / bbox差分系列を入力し，次フレームのbbox差分を予測する
- **MambaTrackは「Mambaが内部状態を永続的に持ち続ける」というより，ユーザー側が保持した過去windowを毎回入力している**

重要な気づき：

> **MambaTrackは本来期待していた"状態を持ち続けるMamba"ではなく，履歴windowを毎回入れる方式に近い**

→ MambaTrackと同様の設定でSAMURAIの動き予測を置き換え，ベースラインとして比較する方針へ。

---

## 5月後半：SAMURAI + Mambaの初期実験と限界

5/21の比較実験（HOTA）：

| モデル | HOTA |
|--------|------|
| SAM2 | 0.46 |
| SAMURAI | 0.54 |
| SAMURAI + Mamba | 0.53 |

→ **SAMURAI単体の方がSAMURAI+Mambaよりわずかに良い**という結果。

判明したこと：

1. Mambaを入れれば単純に性能が上がるわけではない
2. 現状のSAMURAI+MambaはMambaTrack論文の性能水準と比べて不十分
3. SAM2/SAMURAI系はID維持は比較的得意だが，一度ドリフトしたりすると補正が弱い
4. SAMURAIの初期フレーム処理や，カルマンフィルタをいつから動かすかも性能に影響

**研究の焦点が変化**：「カルマンをMambaに置き換える」では弱く，

> **Mambaの内部状態をどう扱うべきか**

が問題になり始めた。

---

## 5月末：Mamba×Tracking研究の調査とsliding window型 / state carry型の分類

5/28の調査で整理された内容：

### MOTではMambaは主にmotion predictorとして使われる

- Kalman filterの代替・補強
- bbox / trajectory historyから次フレームbboxを予測
- Tracking-by-Detectionパイプラインのmotion prediction部分
- 対応手法：MambaTrack, TrackSSM, MambaMOT, SportMamba など

### SOT / VOTではMambaはmemory moduleとして使われやすい

- Mamba hidden stateを文脈保持・伝搬に使う傾向
- 対応手法：MCITrack, SMTrack など

### 本研究での整理軸（2分類）

この調査から，Mamba tracking手法を以下の2つに分けて整理する方向へ：

1. **sliding window型**：過去数フレームのbbox系列・特徴系列を毎回入力し，window内で処理する
2. **state carry型**：hidden state / memoryをフレーム間で継続更新する

> この分類は本研究での見方・整理軸として導入されたもの。論文内では「本論ではこの2つに分ける」と明示する方針（6/18確認）。

---

## 6月前半：state carry型を自作する方向へ

6/4から，state carry型Mambaのテスト実装開始。

重要な整理：

- MOTでstate carry型Mambaを使う例は少ない
- SAM2/SAMURAIとend-to-endで学習するのは重い
- まずMamba部分だけをbbox予測器としてpretrainし，SAM2/SAMURAI側に組み込むのが現実的
- SAM2/SAMURAIの詳細構造より，「box予測部分をKalmanからMambaに置き換える」を主眼にする

**研究の核心が移動**：

- **以前**：SAM2内部を大きく改造する研究
- **現在**：SAM/SAMURAIに外付けできるMamba motion priorを作る研究

---

## 6月中旬：state carry型の実装整理・MIRU原稿の方針

6/18時点でできたこと：

- `samurai_mamba_window`（sliding window型）を整理
- state carry型Mamba用の外側interfaceを追加
- constant-velocity fallbackで `samurai_mamba_stateful` mode が通る状態を作成
- true state carry Mambaはまだ未完成，学習済みcheckpointなし
- MambaStateful, stateful_dataset, train_stateful, track_stateful, stateful_tracklet, stateful_tracker など，state carry型の学習・推論・track単位state管理のためのファイル群を追加

論文方針（MIRU原稿）：

- Mambaのバージョン整理
- Tracking-by-Detection / Tracking-by-Attentionの分類を整理
- sliding window型 / state carry型の分類を明示する
- SAM2/SAMURAIの詳細は書きすぎず，Mamba trackingの話を中心にする

---

## 6月後半：state carry型の学習不安定性と入力スケーリング問題

6/25時点で，入力スケーリングが問題と判明：

- normalized bbox と bbox delta に同じ `scale_factor` を使っていた → bboxが過大に拡大 → Mamba内部でNaN
- bboxは1倍，bbox deltaは50倍で改善
- TrackSSMでは `scale_factor=20`, `scale_factor_diff=50` になっていることを確認

議論内容：

- 入力直前の分布を確認すべき
- 平均0・分散1に近い方が望ましい可能性がある
- LayerNorm等が入力近くにあるなら吸収される可能性もある
- ヒストグラムを取り，1倍 / 20倍 / 50倍の根拠を明確にする
- **state carryでは内部状態が蓄積されるため，スケーリングの影響がsliding windowより深刻になる可能性がある**

---

## 7月2日時点：state carry型は動き始め，次の焦点は汚染解析

比較実験（7/2）の観察：

- MambaTrack / TrackSSMは25エポックでは学習不足の可能性
- TrackSSMはMambaTrackと入出力が違っていたため，単純比較に誤解があった
- MambaTrack / TrackSSMはいずれも現状かなり精度が低い
- **State carry型は100エポックでそこそこの性能が出ており，収束しかけている**
- ただし，学習率スケジューラやvalidation設計はまだ不十分

MOTのvalidationについて：

- 通常のtrain lossは「次bboxを当てる」タスク
- 本来見たい評価はHOTAなどのtracking全体の性能
- train中に5エポックごとなどでHOTA評価を入れられるとよい
- ただし，計算コストやmulti-GPU対応が課題

**最重要：Mambaの内部状態汚染（hidden state contamination）が次の研究課題に浮上**

- MOTでstate carry型が少ない理由として，オクルージョンや誤associationによるhidden state contaminationがあるのではないか
- PCAなどで内部状態を可視化できないか
- 通常トラッキングと，オクルージョンを強制発生させたトラッキングを比較する
- 汚染が検出されたタイミングでstateをリセットする，あるいは信頼度を見てstate更新を止める

---

## 元の目標からの変化まとめ

### 離れていない部分

> **物体追跡にMambaを導入し，動き予測・時間文脈保持を改善する**

という研究の中心は一貫している。

### 変化した部分

1. **SAM2/SAMURAIそのものの改造 → motion priorの研究へ**：SAM2/SAMURAIは実験基盤となり，研究の中心はMambaによるmotion prediction / state carry / hidden state managementに移動
2. **「Mambaを入れる」→「Mambaの使い方を問う」へ**：単純置換では「Mambaにしただけ」になる認識。新規性候補はhidden state contaminationの可視化・定量化・抑制

この変化は良い方向。単なる「Mambaを入れた」研究から，**なぜMOTでstate carry型Mambaが難しいのか，どうすれば使えるのか**という研究課題に進化している。
