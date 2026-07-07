# 研究方向・問いの整理と次のステップ（2026-07-07）

> 2026年7月2日時点の議事録分析をもとに，現在の研究の問いと今後の方針を整理する。

---

## 研究の問いの変遷

### 初期の問い（3月〜5月）

> SAM2/SAMURAIのKalman filterをMambaに置き換えれば，物体追跡性能は上がるか？

### 現在の問い（7/2時点）

> MOTにおいて，Mambaのhidden stateをtrackごとに持続的に保持するstate carry型trackingは有効か？

> もし有効でない／不安定なら，その原因はhidden state contaminationなのか？

> それをどう検出・抑制すればよいか？

---

## 研究の本質的な位置づけ

### SAM2/SAMURAIの位置づけ

SAM2/SAMURAIはSAMURAIに外付けできるMamba motion priorを作るための**実験基盤**。SAM2内部を大きく改造する研究ではない。

### Mamba手法の整理軸（本研究が導入する分類）

| 分類 | 説明 | 代表例 |
|------|------|--------|
| **sliding window型** | 過去数フレームのbbox系列を毎回入力してwindow内で処理 | MambaTrack, TrackSSM, MambaMOT, SportMamba |
| **state carry型** | hidden state / memoryをフレーム間で継続更新 | MCITrack, SMTrack（SOT/VOT系） |

> この2分類は本研究での見方・整理軸。論文内では「本論ではこの2つに分ける」と明示する。

### 新規性候補

> **MOTにおいてstate carry型Mambaを使うと，hidden stateが汚染されやすい。その汚染を可視化・定量化し，抑制する。**

---

## 研究ロードマップ

### フェーズ1：MIRU / ポスター向け

**目標**：SAM/SAMURAI系物体追跡のmotion priorをMambaに置き換え，sliding window型とstate carry型を比較する初期検討の提示

必要なもの：
- [ ] MambaTrack / TrackSSM / State carry型の公平な比較結果
- [ ] SAMURAI+Mamba の評価
- [ ] sliding window型 vs state carry型の概念図
- [ ] TrackEval結果（HOTA / DetA / AssA / MOTA / IDF1）

---

### フェーズ2：修論 / CVPR向け

**目標**：MOTにおけるstate carry型Mambaのhidden state contaminationを定義・可視化し，信頼度に基づくstate update制御によって安定化する

必要なもの：
- [ ] hidden state contaminationの定義と定量化指標
- [ ] 通常trackingと強制occlusion trackingの比較実験
- [ ] hidden state norm / cosine similarity / PCA可視化
- [ ] state reset / update skip / confidence gatingの効果比較
- [ ] SAM2/SAMURAIへの応用実験

---

## 次の具体的なタスク（優先順）

### 1. 公平な比較実験を作る

現状の問題：

- MambaTrackは25エポック，state carryは100エポックで不公平
- TrackSSMはMambaTrackと入出力が異なる
- 入出力形式，スケーリング，学習率スケジューラを統一できていない

必要な統一条件：

- 同一データ
- 同一epoch数または同等収束条件
- 同一評価指標（HOTA / DetA / AssA / MOTA / IDF1）
- 同一初期フレーム処理
- bbox / bbox delta のスケーリングを明示

### 2. Validationを入れる

- 開発用val loss
- tracking全体のHOTA / DetA / AssA（5エポックごとの軽量評価）
- 最終評価用TrackEval

### 3. 入力スケーリングと正規化を確定する

- bbox, bbox delta のヒストグラムを取る
- 1倍 / 20倍 / 50倍の意味を整理し，根拠を明確化
- 平均0化が必要か確認
- Mamba内部のLayerNorm / RMSNormの位置を確認
- 内部状態ノルムが時間とともに発散・縮小していないか観察

### 4. Hidden state contaminationを可視化・定量化する

> MCITrackでは，classification scoreがthreshold以下の場合はhidden stateを更新しないという設計がある。これはstate carry型MOTでも参考になる。

実験候補：

- 通常trackingと強制occlusion trackingを比較
- 誤associationを人工的に入れる実験
- confidenceが低い観測をstate updateに入れた場合 / 入れない場合の比較
- hidden state norm / cosine similarity / PCA軌跡の可視化
- 汚染前後でのbbox予測誤差の変化を観察
- state reset / update skip / confidence gatingの効果を比較

---

## 参照

- MCITrack：hidden state更新をclassification scoreで制御する設計の参考
- MambaTrack / TrackSSM：sliding window型のベースライン
- TrackSSM：scale_factor=20, scale_factor_diff=50 の設定を参照
