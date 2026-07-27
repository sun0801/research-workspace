---
date: 2026-07-27
project: sam2-mamba-motion-tracking
source_todo: null
topic: MIRUポスターの定性的結果選定
status: exploratory
tags: [brainstorm, research, MIRU, qualitative, tracking]
---

# MIRUポスターの定性的結果選定

## 読み込んだ文脈

- MIRUポスターではSAM2/SAMURAIによる物体追跡の改善を主題とし、定性的結果はオクルージョンを含む複数フレームの時系列で示す方針。
- 直近MTGでは、1フレームの比較ではなく、目安6フレームとID番号を示すこと、動画・sequenceを記録して再生成可能にすることを確認している。
- 対象リポジトリのMOT Viewerは、複数MOT入力の左右比較、フレーム移動、IDフィルタ、PNG保存に対応するが、候補イベントの一括抽出・接触シート生成は持たない。
- `dancetrack0041_candidate_debug.csv` のような候補debug CSVには、選択bbox、KF予測bbox、SAM候補bbox、IoU、weighted score等が含まれる。

## 相談の出発点

全sequence・全フレーム・全手法をViewerで目視比較すると時間がかかりすぎるため、ポスターに載せる少数の定性例を効率的に選びたい。

## 問い

全件を均等に見るのではなく、研究の主張を最も説明できる「代表的なイベント」を、再現可能な基準でどう抽出するか。

## アイデア候補

1. **イベントスコアによる候補抽出（第一候補）**
   - 手法間bbox IoUが急低下する区間
   - trackの一時消失・再出現、ID継続の不安定化
   - bbox中心の急移動、面積・アスペクト比の急変
   - `selected_sam_iou` や予測bboxとの不一致が大きい区間
   - 複数手法の差が大きい区間
   これらをフレーム単位で計算し、近接フレームをまとめてイベント化する。

2. **sequence単位の定量結果を使った層化抽出**
   - 改善例: 提案法のHOTA/AssA/IDF1が相対的に良いsequence
   - 失敗・限界例: IDSWや追跡途切れが目立つsequence
   - 代表例: 指標が中央値付近のsequence
   最終的に「改善1・難例1・代表例1」程度を選び、良い例だけで主張しない。

3. **固定長の接触シート生成**
   - 各イベントについて、発生前2、発生時、回復後3など計6フレームを固定。
   - 行を手法、列をフレームにして、ID・bboxを描画。
   - 数十〜数百候補を1枚のoverviewで確認し、Viewerでの詳細確認を上位10〜20件に限定する。

4. **多様性を考慮した最終選定**
   - 同じsequence・同じID・同じ失敗パターンだけにならないよう、イベント特徴でクラスタリングまたは重複抑制。
   - ポスター掲載は3〜5例に絞り、各例にsequence名・フレーム範囲・比較条件を記録。

## 仮説候補

- ポスターの説得力は、全件を網羅することよりも、主張に対応した異なるイベント型を少数の時系列例で示すことで高まる。
- GUIでの全件比較をやめ、イベント抽出と接触シート確認を先に行えば、目視コストを大幅に下げられる。
- 定性例は「最良例」だけでなく、代表例と限界例を含めた方が、定量結果との対応と再現性を説明しやすい。

## 実験・実装案

### 最小構成

- 既存MOT txt / candidate debug CSVをpandasで読み込む。
- 手法間のbbox IoU、中心距離、面積比、欠損、ID出現・消失を計算する。
- フレームスコアを平滑化し、近接フレームを1イベントにまとめる。
- 上位候補について動画フレームを描画し、6フレーム接触シートと候補一覧CSVを出力する。
- Viewerは候補の最終確認とPNG保存に限定する。

### 候補スコアの例

`event_score = 0.35 * method_disagreement + 0.25 * occlusion_or_gap + 0.20 * motion_jump + 0.20 * association_instability`

係数は固定の真理ではなく、まず均等重みで出してから目視で妥当性を確認する。ポスター掲載可否はスコアだけで決めず、研究ストーリーとの対応を人が確認する。

## 比較・評価軸

- 提案法が従来法より追跡継続・ID保持で改善しているか。
- オクルージョン前後の6フレームで挙動が説明可能か。
- 同じ例が単なる偶然の最良例ではないか。
- sequence、フレーム範囲、checkpoint、比較手法、可視化設定を再現できるか。
- ポスター上でID・bbox・時系列の変化が小さくても読めるか。

## 今回見えた方向性

最初に作るべきものはViewerの高機能化ではなく、Viewerの入力に渡す「候補イベント一覧」と「接触シート」である。候補抽出の初期版は、手法間IoU低下・bbox欠損/再出現・中心の急移動の3種類だけでも十分に価値がある。

## 次アクション候補

1. [ ] 比較対象となるMOT出力のファイル一覧とsequenceごとの定量結果を整理する | 優先度: 高
2. [ ] 上位イベントを抽出する候補スコアと固定6フレームの規則を決める | 優先度: 高
3. [ ] 候補イベントの接触シートを一括生成する読み取り専用スクリプトを作る | 優先度: 高
4. [ ] 改善例・代表例・限界例の各1〜2例をポスター候補として選ぶ | 優先度: 通常

## Spec化候補

候補抽出スクリプトの実装に進む場合は、対象MOTファイル、比較手法、イベント定義、出力画像形式、検証方法を決めたうえでspec化する。現時点では、まだ実装開始の承認やspec保存は行わない。

## 未解決の問い

- ポスターで比較する最終手法の組合せは、SAM2 / SAMURAI / Mamba統合のどれに固定するか。
- GT bboxを重ねるか、予測結果のみで見せるか。
- オクルージョンの正解区間をGTから定義できるか。
- 定性例を何例までポスターに載せるか。

## 関連ファイル

- `/mnt/HDD10TB-2/aburatani/2026_03_aburatani_movies_antigravity/mot_viewer/README.md`
- `/mnt/HDD10TB-2/aburatani/2026_03_aburatani_movies_antigravity/mot_viewer/utils/mot_parser.py`
- `/mnt/HDD10TB-2/aburatani/2026_03_aburatani_movies_antigravity/dancetrack0041_candidate_debug.csv`
- `.research/lab/projects/sam2-mamba-motion-tracking/meetings/2026-07-23-mtg.md`
- `.research/lab/projects/sam2-mamba-motion-tracking/README.md`
