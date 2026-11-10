---
date: 2026-11-07
project: kaggle-name-that-llm
source: autonomous-experiment
status: approved
execution_status: completed-gates-passed-not-current-best
tags: [spec, experiment, cpu, prompt-grouping, svc]
---

# Open Pool prompt-centered SVC twin Spec

## 目的・根拠

現在の採用法はOpen Pool v15 4-view LinearSVC（primary OOF BA 0.433776）。公開Notebook `ozertuu/0-672-dual-svc-better` version 9は、prompt-centered stylegram SVCが5-fold prompt-grouped OOFで0.423から0.435へ改善したと報告している（著者自己申告であり、当方の再現値ではない）。同Notebookは複数の大規模encoder/LoRA/ATLASも併用しており、全体LB 0.672をこの部品だけの効果とは扱わない。

この候補では既存Open Pool v15の4-view表現に、学習時のprompt中心化と、validation本文のみから推定したprompt群での予測時中心化を適用する。外部実装・実験の開始はactive GPU goalに含まれる。

## 固定手順

- 既存`cpu-openpool-4view-svc-v15` config、row weights、foldwise prompt filtering、4 view、LinearSVC `C=2.0`を再利用する。
- 各foldで特徴量器はofficial outer-trainと許可されたOpen Pool行だけでfitする。OOF予測には同じfoldのvalidation本文だけを使う。
- official outer-train特徴は`prompt_id`ごと、Open Pool特徴は`prompt_canon`ごとに別々に中心化し、元の4-view表現と同じクラスラベルでLinearSVCを学習する。
- Validationの群はvalidation本文だけから作る。public Notebookのstylegram法に合わせ、英語stop-word付きword TF-IDF (`sublinear_tf=True`) のcosine距離を全validation行内で計算し、距離を上三角要素の中央値で割り、average linkageを距離threshold `0.90`でcutする。`prompt_id`・ラベル・予測scoreは群推定に渡さない。サイズ1の群はそのまま残し、最大群サイズやクラス数による除外・補正をしない。
- 各推定群のvalidation特徴から群内平均を引き、学習時に同じfold内でfitしたLinearSVCへ入力する。学習やOOF生成でouter-validationの正解prompt IDは参照しない。
- 主評価は既存flat SVCとの完全対応OOF比較。primary全5foldを実施し、prompt単位paired bootstrap 2,000回・seed 42のBA差95% CI下限が0を上回った場合のみ、固定手順のまま独立confirmationを実施する。confirmationでも下限>0の場合のみ採用する。
- 候補を選んだ公開NotebookのOOF報告に由来する選択biasを記録し、primaryはscreeningとして扱う。foldごとの群サイズ、群の一貫性指標、件数、予測、score、資源情報を保存する。

## 仮説と制約

Promptごとの題材語彙をtrain/validationで除去すると、モデル由来の文体信号が相対的に強くなり、flat SVCを改善する可能性がある。推定群は誤る可能性があり、効果がない場合は棄却する。

公式testの各クラス件数は不均等で、public/private構成も異なる。validation/test群のサイズを18に固定せず、1対1割当、injective assignment、repel、class-count均等化、真のvalidation prompt_idによる中心化は使わない。

## 出力・資源

- 実装: `/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/src/cpu_openpool_prompt_centered_twin.py`
- artifacts: `artifacts/cpu-openpool-prompt-centered-twin-v15/` 以下にprimary/confirmation folds、OOF、decision scores、metrics、manifestsを作る。既存artifactは上書きしない。
- 2 CPU threads、tree RSS <=32 GiB、MemAvailable >=16 GiBを開始条件とし、fold完了ごとにcheckpointを保持する。GPUは使わず、Qwen GPU runは停止・変更しない。
- KaggleへのNotebook提出なし。採用候補になった場合は、既存Notebook化/runtime/ライセンスゲートを別途満たしてから提出を選定する。

## 実行結果（2026-11-07）

- Primary: candidate BA `0.465993` vs adopted flat SVC `0.433776`, delta `+0.032217`; prompt-level paired bootstrap (150 groups, 2,000 replicates, seed 42) 95% CI `[+0.017037, +0.047413]`.
- Independent confirmation: candidate BA `0.469714` vs same-split flat SVC `0.433403`, delta `+0.036311`; paired bootstrap 95% CI `[+0.020380, +0.053000]`.
- Both preregistered lower-bound gates are above zero. Confirmation fold convergence was true for all five folds (`n_iter` 39/41/41/41/41). The primary parent aggregation initially failed only because its metrics omitted the expected convergence field; all five fold artifacts were intact and the independent analysis completed. The corrected runner successfully aggregated confirmation.
- Adopt this method as a candidate baseline for subsequent OOF comparisons. This does not establish Public/Private LB performance or authorize a Kaggle submission; Notebook packaging, runtime, and license checks remain required.

## Current status clarification (2026-11-08)

The primary/confirmation artifacts are complete and no runner remains active. The reported gates compare against the older flat SVC (`0.433776` primary / `0.433403` confirmation), not the currently adopted prompt-centered low-pool SVC (`0.501934` / `0.500818`). Therefore this method is a completed experimental candidate, not the current best and not independently shown to improve over the current adopted baseline. Any blend using its outputs requires a separately registered evaluation.
