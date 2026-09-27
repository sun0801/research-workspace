# 2026-09-27 9/25 MTG後の優先順位整理

## 相談の出発点

9/25 MTG後の次方針として、lossプロット修正、SAM2MOT再現、SAM2デコーダーへのtemporal Mamba統合の優先順位を検討した。

## 判断

lossプロットの修正はComet上で短時間に完了できるため、主作業のブロッカーにはしない。SAM2MOT再現とtemporal Mamba統合を進める。

ただし、両者は同じ重みで扱わず、temporal Mamba統合を研究の主線、SAM2MOT再現を期限付きの補助線とする。

## 理由

- temporal Mamba統合は、state carry型MambaをSAM2デコーダーへどう組み込むかという研究の中心課題に直接つながる。
- SAM2MOT再現は、途中検出による補正や複数人物追跡の設計知見を得られるが、8/28以降の主線とは独立した作業である。
- SAM2MOTの再現を広げすぎると、検出器・SAM2構成・論文未記載部分の実装判断に時間を使い、temporal Mambaの検証が遅れる可能性がある。

## 進め方の候補

### 主線: temporal Mamba統合

- SAM2デコーダー周辺の挿入候補を読み取り専用で整理する。
- 既存モジュールを置換せず、temporal Mambaを追加する最小構成に限定する。
- 人物ID routingやID switch対策は初期実験から切り離す。
- 最低限、no-Mamba baseline、Mamba追加、1〜3系列のend-to-end完走、stateのfinite確認、追跡指標比較を行う。

### 補助線: SAM2MOT再現

- 既存の承認済みspecの範囲に限定する。
- まずbaselineと主要componentの成立確認までを短い区切りとする。
- 途中検出による補正への知見を得ることを目的とし、論文の完全再現を主線の前提にしない。

## Implementation Gate

現時点では方針整理であり、外部実装リポジトリは編集しない。実装開始前に、各作業について承認済みspec、変更対象、検証方法、実装開始承認を確認する。特に `2026-09-08-sam2mot-reproduction-spec.md` はdraft表記のため、SAM2MOT実装を開始する前に承認状態を確認する。

