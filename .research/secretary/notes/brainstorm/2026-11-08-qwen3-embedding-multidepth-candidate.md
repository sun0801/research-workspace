---
date: 2026-11-08
project: kaggle-name-that-llm
source_todo: null
topic: qwen3-embedding-multidepth-candidate
status: exploratory
tags: [brainstorm, research, kaggle, embeddings]
---

# Qwen3-Embedding-8B multi-depth candidate

## 読み込んだ文脈

- Active goal: `.research/lab/projects/kaggle-name-that-llm/specs/2026-11-06-gpu-autonomous-first-place-spec.md`に従う公開LB首位超え探索。
- 現行bestはprompt-centered Open Pool SVC（primary BA 0.501934 / confirmation BA 0.500818）。Qwen02/04のprimary OOFは進行中。candidate06 Qwen3-30B NF4とcandidate07 WeMM-4BはGPU解放待ち。
- Kaggle公式Notebook検索で公開Notebook `concyclics/0-679`を確認。タイトルの0.679は現在のLB首位0.751を超えず、複合モデルの値なので各部品の寄与は識別できない。

## 相談の出発点

同Notebookの入力metadataにQwen3-Embedding-8Bが含まれている。公開Notebookソースを実行せず展開・AST解析したところ、独立したprompt-grouped five-foldモデルの基盤としてQwen3-Embedding-8Bを使うmulti-depth LoRA構成が見つかった。

## 問い

Qwen3-Embedding-8Bの複数層表現をfold内の公式ラベルと公開Open Poolだけで学習することで、現在のSVCより未見promptの識別精度を上げられるか。

## アイデア候補

1. Frozen Qwen3-Embedding-8Bの4096次元embedding + 固定LinearSVC。推論は単純でcandidate07 WeMMと直接比べやすいが、公開0.679で使われた学習可能multi-depth設計を捨てる。
2. Qwen3-Embedding-8Bの8深度表現を連結するLoRA classifier。公開ソースが示す層は36層モデルの`[3, 6, 9, 12, 18, 24, 30, 36]`、特徴幅32,768。公開ソースの事前学習済みadapterやOOFを転用せず、独自に外側foldごとに学習し直す。
3. Qwen3-Embedding-8BとWeMM-4Bのfoldwise probability blend。候補07のOOFも必要であり、単体比較前に組み合わせると寄与を識別できないため保留。

## 仮説候補

- Qwen3-Embedding-8Bの8深度表現は、最終層だけのQwen3-8B分類headよりもstyleと局所的な語彙選択を分離し、prompt-held-out分類を改善する。
- 反例: 公開0.679は複数の独立専門家・外部checkpoint・校正を組み合わせた値で、Qwen3-Embedding-8B単体が高いOOF精度を持つ証拠ではない。公開コードに含まれるfull-fit専門家は独立OOF基準に使えない。

## 実験・実装案

- Qwen3-Embedding-8B公式Apache-2.0 checkpointを使い、8層のmasked pooled hidden statesを連結するmulti-depth headを実装する。encoderはLoRAだけ学習可能、元embedding projectionは凍結する。
- 公式trainのprompt-grouped outer foldsに従って、各外側foldでのみfitする。Open Pool v15を使う場合は既定のfold別prompt近似除外とtrain text exact-match除外を適用する。
- 固定primary OOFを現best SVCと比較し、prompt-paired bootstrap下限>0のときだけ独立seed-42 confirmationへ進む。
- candidate06のGPU1 pilot/実験が終わるまで新しいGPU処理は起動しない。GPU1 Blackwellの空きが確認できた場合に、batch1・512-token pilotと実測runtime/RAM/VRAMで適合性を判定する。

## 比較・評価軸

- 主指標: 2,699行連結OOF balanced accuracy、fold別BA、全クラスrecall、baseline差のprompt単位paired bootstrap 95% CI。
- prompt分離、外側validation label不使用、同一ID/fold alignment、model/data/license provenance。
- 1回のOOF完了時間、GPU peak、host RSS、T4×2への最終Notebook推定時間。

## 今回見えた方向性

Qwen3-Embedding-8Bの独立multi-depth OOFを次の有力候補として事前登録する。公開Notebookの0.679 scoreは候補動機に限り、手法の有効性・OOF品質として転用しない。WeMM-4Bは並行して登録済み候補として保持し、両候補の独立結果が揃うまでblendしない。

## Spec化候補

Qwen3-Embedding-8B multi-depth LoRA prompt-grouped OOF spec。Active goalが候補の選定・実装・再現を継続承認している範囲で、独立runner/config、primary/confirmation gate、runtime pilotを固定する。

## 関連ファイル

- [公開LBトップ超えgoal spec](../../../lab/projects/kaggle-name-that-llm/specs/2026-11-06-gpu-autonomous-first-place-spec.md)
- [candidate07 WeMM-4B spec](../../../lab/projects/kaggle-name-that-llm/specs/2026-11-08-wemm-embedding-4b-prompt-grouped-spec.md)
- [公開Notebook `concyclics/0-679`](https://www.kaggle.com/code/concyclics/0-679)
- [公式Qwen3-Embedding-8B model card](https://huggingface.co/Qwen/Qwen3-Embedding-8B)
