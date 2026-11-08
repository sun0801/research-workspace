---
date: 2026-11-08
project: kaggle-name-that-llm
source_todo: null
topic: WeMM embeddingを使うprompt-grouped著者分類候補
status: exploratory
tags: [brainstorm, kaggle, embeddings, prompt-grouped]
---

# WeMM embeddingを使うprompt-grouped著者分類候補

## 読み込んだ文脈

- active goalはName That LLMの公開Leaderboard首位を超えるNotebook提出を目指し、候補は既存結果・公開知見から選ぶ。
- 2026-11-08 03:14 JSTの公式Leaderboard首位は0.751。現在のQwen 8B/1.7B primaryは各fold 0–2が完了し、fold3を実行中。採用済みSVCはprimary BA 0.501934 / confirmation BA 0.500818。
- 今日のTODOファイルは未作成、Kaggleプロジェクトのmeetings/にMTG議事録なし。関連goal brainstormは2026-11-06の1位追従方針。
- 公開Notebook `concyclics/0-679` はQwen3-Embedding-8B、Tencent WeMM-Embedding-4B/9B等を併用するが、0.679は複合系の投稿値でWeMM単体の寄与ではない。付属の全train派生資産はOOF評価に流用しない。

## 相談の出発点

公開Notebookで使われたWeMM-Embedding系が、既存Qwen LoRAと採用済みSVCとは異なる表現を提供する可能性がある。今回の問いは、公開・ライセンス適合したWeMM-Embedding-4Bを固定特徴抽出器として、独立したprompt-grouped OOFで単体評価する価値があるか。

## 問い

Tencent WeMM-Embedding-4Bの凍結2,560次元テキスト埋め込みから学習する固定LinearSVCは、採用済みprompt-centered SVCに対して未見promptのbalanced accuracyを改善するか。

## アイデア候補

1. WeMM-Embedding-4Bの凍結テキスト埋め込み + 事前固定LinearSVC。WeMM単体を評価でき、4B版の公開重みとApache-2.0情報がある。まず優先。
2. WeMM-Embedding-9Bの埋め込み。公開0.679複合系に含まれるがA4000 16GBで余裕が小さく、4B単体評価後に別判断。
3. 0.679 notebookが使うfull-train classifier/head/calibrationの再利用。full-train由来でOOFではなく、出所データのライセンスも混在するため対象外。

## 仮説候補

- H1: WeMM-Embedding-4Bは汎用の意味・文体表現を持つため、公式trainだけで学習するLinearSVCが未見promptにもモデル固有の表現差をとらえ、現best SVCを補完または上回る。
- 反例: 公開0.679は複数の埋め込み・head・校正器の複合結果であり、WeMM-4B単体が有効とは限らない。意味中心のembeddingが細かなtoken/style差を落とす可能性、長文の切り詰め、5B BF16モデルのGPU/9時間制約もある。

## 実験・実装案

- 公式Kaggle model mirror `dangkhoa2016/tencent-wemm-embedding-4b`, Transformers/default v1を固定。Kaggle model metadataはApache 2.0、10,367,587,280 bytes、upstream revision `a28b25c5d18cf71ec46b115e06ea79ab00ee4819`。Tencent model cardは2,560次元L2-normalized embedding、5B BF16、Transformers 5.2.0、text-only embedding APIを記載。Qwen3.5-4B baseもApache-2.0。
- 生データは公式competition trainのみ。validation `prompt_id` を学習へ跨がせないprimary GroupKFoldと、既存のseed-42 shuffle GroupKFold confirmationで固定LinearSVCを評価する。埋め込みはラベルを使わない凍結変換であり、各split内の全行でキャッシュ共有できるが、分類器はfold train側だけでfitする。
- 主評価はOOF balanced accuracy。採用済みprompt-centered SVCと、prompt単位paired bootstrap 2,000回以上・seed42で比較。primary CI下限が0より大きい場合だけindependent confirmationへ進む。
- GPU0 A4000のrun lockが空き、fresh preflightを通るまでmodel loadしない。batch 1 / max 512 tokensでpilotし、VRAM余裕`max(4 GiB, 25%)`、MemAvailable >=16 GiB、bf16保存重みを推論時FP16へcastしてA4000評価とKaggle T4×2 Notebookのdtypeを揃える。A4000計測に固定1.5倍T4 slowdown仮定をかけたhidden test 4,000行込みの推定が8時間以内（1時間余裕）なら続行し、未達ならfull OOFは始めない。
- Kaggle offline実行ではpinned model assetsと依存wheelをprivateに用意し、Notebook push/提出はOOF、確認、runtime、license/provenance gatesをすべて通過した後だけ。

## 比較・評価軸

- Primary/confirmationの全行OOF BA、fold別BA、クラス別recall、prompt-paired 95% CI。
- baseline: 各splitの採用済みprompt-centered SVC OOF。
- 成功基準: Primary paired-bootstrap CI lower > 0、独立confirmationでもCI lower > 0。未達は不採用または未確定。
- 実装可能性: exact pinned weights/model codeがKaggle offlineで使えること、A4000 16GB preflight pass、estimated Notebook inference <=9h。

## 今回見えた方向性

4Bは9Bより実行可能性があり、公開モデル単体をfoldwise特徴抽出器として測れば0.679複合Notebookの寄与を独立に切り分けられる。upstream technical reportはモデルの学習データ全体を公開していないため、これは一般公開pretrained modelとしてのOOFであり、事前学習データの完全な独立性までは証明できない。この不確実性を記録し、Name That LLM task-specific trainingやcompetition textを使った証拠が見つかった場合はOOF採否判定に使用しない。

## 次アクション候補

- active goalの広い実装開始承認に基づき、まずcandidate07として独立Spec/runner/configを作り、既存Qwenジョブを止めずにCPU側の依存・model code・T4 runtime計測計画を準備する。
- GPU pilotは現在のGPU0計算が解放され、15%利用枠guardとfresh GPU/RAM preflightを通過した後だけ行う。
- TODOは追加しない。

## Spec化候補

`.research/lab/projects/kaggle-name-that-llm/specs/2026-11-08-wemm-embedding-4b-prompt-grouped-spec.md` にfixed embedding + LinearSVCのprimary/confirmation計画を記録する。承認根拠は、既に開始されているfirst-place goalが公開知見に基づく次候補選定・実装・検証を明示的に許可していること。

## 未解決の問い

- pinned `trust_remote_code`実装を監査し、Kaggle offline dependency/wheel構成での互換性を確認する必要がある。
- technical reportでは訓練data corpusの詳細が完全公開されていない。competition textやtask-specific tuningの証拠がないことと、data independenceが証明されたことは区別する。
- 512-token truncationで対象trainのどの程度を保持できるか、pilot前に分布を計測する。

## 関連ファイル・出典

- [Kaggle project README](../../lab/projects/kaggle-name-that-llm/README.md)
- [First-place goal spec](../../lab/projects/kaggle-name-that-llm/specs/2026-11-06-gpu-autonomous-first-place-spec.md)
- [Qwen + SVC ensemble spec](../../lab/projects/kaggle-name-that-llm/specs/2026-11-07-qwen-prompt-centered-svc-probability-ensemble-spec.md)
- [Kaggle notebook 0.679](https://www.kaggle.com/code/concyclics/0-679)
- [Kaggle WeMM-Embedding-4B v1 mirror](https://www.kaggle.com/models/dangkhoa2016/tencent-wemm-embedding-4b/Transformers/default)
- [Tencent WeMM-Embedding-4B model card](https://huggingface.co/tencent/WeMM-Embedding-4B)
- [Qwen3.5-4B base model card](https://huggingface.co/Qwen/Qwen3.5-4B)
- [WeMM-Embedding technical report](https://arxiv.org/abs/2608.24053)
