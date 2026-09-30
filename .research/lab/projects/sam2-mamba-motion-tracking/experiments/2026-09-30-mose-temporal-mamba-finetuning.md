---
project: sam2-mamba-motion-tracking
type: experiment-log
status: in_progress
created: 2026-09-30
last_updated: 2026-09-30
---

# MOSEv1 SAM2.1 Small + temporal Mamba追加学習

## 目的

[承認済みspec](../specs/2026-09-30-temporal-mamba-mose-finetuning-spec.md)に沿い、SAM2.1 Small全体fine-tuningへtemporal Mamba adapterを加える効果を、MOSEv1の単一対象・先頭box prompt・後続GT補正なし設定で比較する。

## 実行環境

- 実装repo: `/mnt/HDD10TB-2/aburatani/worktrees/sam2-mose-temporal-mamba`
- branch: `codex/mose-temporal-mamba-training`
- base checkpoint: `sam2.1_hiera_small.pt`, SHA-256 `6d1aa6f30de5c92224f8172114de081d104bbd23dd9dc5c58996f0cad5dc4d38`
- Python環境: SAM2 repoの`.venv-sam2`、Torch 2.10+cu128、Mamba 2.3.1
- GPU: GPU0 RTX PRO 4500 Blackwell 32GB
- run成果物: worktreeの`runs/mose_temporal_mamba_20260930/`（git local exclude）

## データ分割

固定seed 123。SAM2公式MOSE train list 1,246動画をfit 1,121動画・tuning 125動画に動画単位で分割し、val list 200動画はlockboxとする。fitは2,789 object軌跡・200,794伝播frame、tuningは313軌跡・21,919伝播frame、lockboxは570軌跡・36,830伝播frame。今回の軌跡はすべて動画frame 0に初出していることをannotation scanで確認した。

## 実装・予備検証

- F0: SAM2全体fine-tuning。F1: SAM2全体とtemporal Mamba adapterをfine-tuning。
- SAM2動画memoryとMamba stateは各軌跡全体でcarry。TBPTT=8境界では計算graphをdetachし、stateの数値を保つ。1軌跡につき1optimizer update。
- full BPTTは9-frame smokeでfinite、ただし実用VRAM余裕と最長系列への対応からTBPTTを採用。TBPTT=16は55-frame系列でOOM（約31GiB allocated）。TBPTT=8では短・中央値・500-frame最長preflightがfinite、peak約18.2/19.9GiB。
- Mamba adapterの学習用forwardと推論用streaming forwardのFP32 parityは最大絶対差`4.47e-08`。gradient finiteを確認。DAVIS公式boundary-F計算と30 random mask pairで一致を確認。

## 学習パイロット

同じfit順序先頭100軌跡、seed・augmentation系列・設定を揃えてF0/F1を実行。各軌跡後にmodel/optimizer/schedulerを含むcheckpointを保存した。

| Condition | 更新 | 状態 | checkpoint |
|---|---:|---|---|
| F0 | 100/100 | 完了 | `F0_step_000100.pt` |
| F1 | 100/100 | 完了 | `F1_step_000100.pt` |

全更新でlossはfinite。augmentationで初期maskが消えた系列は最大4回の幾何再試行後に処理され、学習を完了した。F1で高い単系列loss（最大観測18.28）が1回あったため、tuning結果と系列別分布を確認する。

### 更新済み評価器のsmoke

元解像度J/Fで、tuning先頭1動画（4対象）をP0/F0/F1/F1-reset各条件で推論・完走。これはパイプラインsmokeであり、checkpoint選択や性能比較の根拠には使わない。

| Condition | J | F | J&F |
|---|---:|---:|---:|
| P0 | 0.8497 | 0.9192 | 0.8844 |
| F0 step 100 | 0.8540 | 0.9283 | 0.8911 |
| F1 step 100 | 0.8540 | 0.9279 | 0.8909 |
| F1-reset step 100 | 0.8538 | 0.9285 | 0.8911 |

## 次の処理

1. F0/F1のpilot checkpointをtuning 125動画で評価し、同一J&F基準で候補checkpointを選ぶ。
2. pilotのtuning挙動と学習予算を記録し、lockboxを見る前にF0/F1共通の全学習step数・checkpoint間隔・選択規則を固定する。
3. 固定設定でfit全軌跡をF0/F1学習し、tuningから各条件のcheckpointを選択する。
4. 評価コード・checkpoint・設定を凍結後、lockbox 200動画をP0/F0/F1/F1-resetで一度評価し、paired差とvideo-bootstrap 95% CI、propagation長別結果を算出する。
5. checkpoint hash、run manifest、loss/VRAM/timing、全比較結果をここへ追記する。

### Pilot tuning result (F0 step 100)

- 125/125動画・313/313対象を評価完了。全対象はframe 0開始。
- equal-weight video mean: J=0.6956, F=0.7735, J&F=0.7345。
- inference elapsed: 3,898.7 s（約65.0分）。
- run: `runs/mose_temporal_mamba_20260930/pilot_tuning/F0_step100/`。予測maskは保存せず、objects.jsonl等metricsのみ保存。
- これは100更新pilotのtuning結果であり、lockbox結果ではない。F1同条件評価および学習予算決定前のため、checkpointは未選択。
