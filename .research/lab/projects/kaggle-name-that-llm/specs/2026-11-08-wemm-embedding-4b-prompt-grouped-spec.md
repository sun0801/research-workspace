---
date: 2026-11-08
project: kaggle-name-that-llm
source: brainstorm
status: approved
execution_status: rejected-primary-gate
approval_basis: active-goal-2026-11-06-gpu-autonomous-first-place-spec
tags: [spec, experiment, embeddings, prompt-grouped]
---

# WeMM-Embedding-4B prompt-grouped分類 Spec

## 目的

Tencent WeMM-Embedding-4Bの凍結テキスト埋め込みから学習する固定LinearSVCが、現在採用済みのprompt-centered Open Pool SVCより未見prompt上のbalanced accuracyを改善するかを測る。WeMM単体の寄与を測る候補とし、公開Notebook由来のfull-train head・校正器・OOF不明の派生埋め込みは使わない。

この候補は、2026-11-06開始の公開LB首位超えgoalが認める次候補の選定・実装・検証範囲に含める。Kaggleへのpush・提出は本specの評価ゲートを通過した後に限る。

## 固定データ・モデル

- 分類データ: Name That LLM公式`train.csv`のみ。外部の分類用データ、擬似ラベル、testラベルは使わない。
- 主評価分割: `.research/lab/projects/kaggle-name-that-llm`に保存済みのprompt GroupKFold 5-foldをそのまま使う。
- 独立確認分割: `GroupKFold(n_splits=5, shuffle=True, random_state=42)`。各`prompt_id`は単一foldに属する。
- 同一split baseline: 採用済みlow-pool SVCの`confirmation-folds.parquet`を確認し、2,699行のofficial train順と一致し、scikit-learnのGroupKFold seed 42再生成結果と全割当が一致した。primary foldsは既存saved GroupKFold artifactを使う。
- 埋め込みモデル: Kaggle公式mirror `dangkhoa2016/tencent-wemm-embedding-4b`, Transformers/default version 1、upstream revision `a28b25c5d18cf71ec46b115e06ea79ab00ee4819`。
- モデル公開情報: Apache-2.0、bf16重み、2,560次元L2-normalized embedding。公式Kaggle variationの総展開サイズは10,367,587,280 bytes。モデルカードの使用APIはWeMMのchat templateと`model.embedding(**inputs)`。
- 推論dtypeはFP16。Kaggle Notebook公式案内はT4×2（GPUあたり16GB）を示し、NVIDIA precision matrixではT4がFP16対応・BF16非対応。BF16重みをロード時にFP16へcastし、A4000 OOFとKaggle T4 runtimeで同じdtypeを使う。精度差はこの固定候補のprompt-grouped OOFで測る。[Kaggle notebook hardware](https://www.kaggle.com/docs/notebooks)・[NVIDIA T4 precision matrix](https://docs.nvidia.com/deeplearning/tensorrt/archives/tensorrt-1060/pdf/TensorRT-Support-Matrix-Guide.pdf)
- 固定revision configは`model_type=qwen3_5`、`transformers_version=5.2.0`、`AutoModel`と`AutoModelForCausalLM`を同梱`modeling_wemm_embedding.WeMMEmbedding`へmapする。
- 取得・静的監査済みremote code: `modeling_wemm_embedding.py` SHA-256 `ac255e1fad459cc3e68891d6c3327f4486922aed02fb3c5c13fb53277ba8e94f`; `modeling_st_wemm.py` SHA-256 `521d02c1c60ae727cc9dc6500cdb0b28c53b259e0ce3d37197920a33ba4dd333`。後者はSentence Transformers用vision wrapperで固定text-only経路では使わない。前者はQwen3.5 modelを継承し、`rope_deltas`をclear後にtext forward、attention mask末尾tokenを選択してL2 normalizeする。確認したコード範囲にネットワーク・shell・ファイル書込処理はない。実行時もこのhashを再確認する。
- 固定依存: Transformers 5.2.0、Torch 2.9.0、TorchVision 0.24.0、Qwen-VL-Utils 0.0.14などを`configs/gpu07-wemm-embedding-4b-requirements.lock`で固定。CPU上でAutoProcessorのtext-only template/tokenizer経路が1x13 token入力を返すことを確認した。Torch/TorchVision対応は[PyTorch公式version table](https://pytorch.org/get-started/previous-versions/)に従う。
- Kaggle mirror v1のfile listとpinned HF revisionの17 asset名・sizeを照合。全sizeは一致し、README.mdだけupstream側が354 bytes大きい。`model.safetensors`は両方10,347,541,240 bytes、pinned HF SHA-256 `880c33762729584656223d1235bf13d035b2a842c28eac9ae6ea50bbc3d1ac45`。Kaggle側hashは公開されていないため同一byte列とは断定しない。
- トークン上限: 512、truncation有効。pilot前に公式trainの実トークン長分布と512超過割合を保存する。
- 前処理・埋め込み重み・pooling・分類器をOOF結果に合わせて調整しない。モデルカードの推奨text-only embedding APIを固定し、使用したprocessor/model codeのhashを記録する。
- upstreamは学習データ全体を開示していない。Name That LLM固有の学習・competition text使用の根拠が見つかった場合は、この候補のOOFを採否判断に使わず停止して記録する。完全な事前学習データ独立性は主張しない。

## 固定分類器と比較

- 特徴: WeMMの2,560次元embeddingをそのまま使用。埋め込みの追加標準化やラベルを使う特徴選択はしない。
- 分類器: `LinearSVC(C=2.0, max_iter=5000, random_state=42, class_weight=None)`。Cは採用済みSVC configから引き継いだ固定値であり、探索しない。
- 各splitの各foldで、分類器はそのfoldのofficial train rowsだけでfitする。validation labelsは予測後の評価にだけ使う。分類器の学習結果をfold間で共有しない。
- 採用済みbaseline: `cpu-openpool-prompt-centered-low-pool-weight-v15`の同じsplitに対するOOF予測。primaryとconfirmationの両方で、同じ行ID・prompt IDを揃える。
- 主指標: 連結OOFのbalanced accuracy。fold別BA、class recall、confusion matrix、embedding token長分布も記録する。
- 採否: primaryでprompt単位paired bootstrap 2,000回以上、seed 42のBA差95% CI下限が0を超えた場合だけ独立confirmationを実行する。confirmationでも同じCI下限>0を要求する。primary不通過ならconfirmationを実行しない。
- 主要比較以外のmetric・partial fold・pilot subsetから分類器設定を選ばない。partial結果は進行状態の診断に限る。

## 実行順序・資源ゲート

1. 固定revisionの公式mirrorの全file manifestとhashを記録する。`trust_remote_code`を有効にする前に、`modeling_wemm_embedding.py`および`modeling_st_wemm.py`を静的監査し、コードhashを保存する。依存は既存Qwen環境へ上書きせず、候補専用環境に固定する。
2. 実行先をhost141 GPU0 UUID `GPU-c542e903-dac3-5541-ea10-2b66b06e5f61`（RTX A4000）へ変更する。host142 GPU0でQwen04が長時間稼働中のため、同型・同VRAMのhost141 GPU0が空いている時に候補を前倒しし、Qwen04と同居させない。host141は別ホスト・別ローカルディスクであり、candidate runner/config, fixed folds, adopted primary/confirmation baselines, model, candidate-specific venvを個別に転送してhash照合する。host141 GPU0専用lockを使う。pilot直前に5秒間隔2-snapshot preflightでUUID/process, VRAM, host `MemAvailable`を確認する。
3. Pilotはbatch size 1、最大512 tokens、代表的な長さを含む最低32 train examplesで行い、load/forward時間、peak VRAM/RSS、NaN/shape、token長、推論tokens/sを記録する。model load前にMemAvailableが16 GiB未満、GPUに既存計算processがある、またはreserveを残せない場合は開始しない。
4. A4000は16 GiB。pilotの使用分と推定追加分を合わせて空きVRAMから`max(4 GiB, 全容量の25%)`を残せない場合は不適合として終了する。初期の許容上限は概ね12 GiBだが、実測時の空きから都度算出する。
5. 同じ固定推論設定でtrain 2,699行とhidden test 4,000行、計6,699行を処理する時間を見積もる。A4000 pilotのload/tokenization/inference測定値に固定1.5倍のT4 slowdown係数（測定値ではなく保守的な計画仮定）をかけ、投影値が8時間以内（9時間制限に最低1時間の余裕）ならOOF実行候補とする。pilot不通過ならfull extraction/OOFへ進まない。
6. 埋め込み抽出に入る前に`codex_rate_limit.py --guard 15`を通す。長時間処理はsessionから切り離し、UUID lock、atomic cache、resume、OOM時の自分のprocess限定停止を備える。
7. Primary OOFと採否解析が通ったときだけconfirmation seed 42を実行する。confirmationを通過してから、offline依存wheel・pinned model assetsを使うNotebook runtime確認へ進む。

実装runnerは外部実験repoの`src/gpu_wemm_embedding.py`。host142向け固定config `configs/gpu07-wemm-embedding-4b.json`は保全し、host141 UUIDだけを切り替えた`configs/gpu07-wemm-embedding-4b-host141.json`を追加した。host141の独立repoへrunner, analyzer, config, folds, adopted comparator OOFを転送し、hashがhost142と一致すること、official `train.csv` hashも一致することを確認した。公式WeMM modelをhost141 `/tmp/wemm-candidate07-model`へ転送し、`model.safetensors` SHA-256 `880c33762729584656223d1235bf13d035b2a842c28eac9ae6ea50bbc3d1ac45`を保持。candidate専用venv 7.4GBを転送し、Python 3.12.3 / Torch 2.9.0+cu128 / CUDA 12.8 / Transformers 5.2.0 / sklearn 1.9.1のimport確認を完了。runner preflightでPyTorch/NVIDIA UUID表記差と、自プロセスPIDを別compute扱いする不具合を見つけ、prefix正規化と自PIDだけを除外する修正を適用。他PIDの拒否、5秒2-snapshot、UUID/RAM/VRAM確認は保持した。

2026-11-08 09:35 JST pilot: 32行、最大観測token 383、全2,699行で512 token超過なし。出力shape `[32, 2560]`、全値finite。公式model load 14.01秒、32行forward 36.68秒、A4000 peak 10,056 MiB / pre-load free 15,633 MiB / reserve 4,096 MiB、host MemAvailable 120.95 GiB。6,699行（train+hidden-test）×固定T4 slowdown 1.5のNotebook runtime projectionは3.205時間で、8時間gateを通過。pilot JSONとmanifestに全model file hashesを記録。

最初の2回は上記のrunner preflight不具合でmodel load前に終了し、pilot artifactなし・GPU解放を確認して修正後に再実行した。

### 実行結果

2026-11-08 09:44 JSTにhost141 GPU0でprimary OOFを開始し、10:24 JSTに正常終了。2,699行の埋め込み（2560次元）を作成し、5-foldの全2,699行・150 promptを評価した。候補BAは`.2089187174`、採用済みSVCは`.5019338802`、差は`−.2930151628`。5,000回・seed 42のprompt-paired bootstrapで平均差`−.2929612796`、95% CI `[−.3138390891,−.2719463213]`となり、primary gateは`reject`。watcher PID `3764372`はstatus 0で終了し、confirmationをスキップした。final fit、Notebook作成、Kaggleへのpush/提出は未実施。実験ログ: [2026-11-06-gpu-autonomous-initial-check.md](../experiments/2026-11-06-gpu-autonomous-initial-check.md)。

## Kaggle実行・提出ゲート

- Notebook-only、Internet disabled、実行9時間以内などその時点の公式条件を再確認する。
- Kaggle上で必要なprivate Model/Datasetは新規のprivate versionだけを使う。公開Notebookや公開派生データのfull-train readoutは持ち込まない。
- ローカルOOF・confirmation、license/provenance、offline runtime、submission形式の確認が揃わない間はpush/submitしない。
- 1日5件、最終2件などfirst-place goal specの提出上限と選定ルールを守る。

## 保存物

- 設定、依存lock、監査済みmodel codeのhash、固定revision/file manifest。
- 512 token分布、pilotログ、GPU/RAM/runtime記録。
- primary/confirmation folds、全行OOF予測・decision score、fold metrics、prompt paired bootstrap。
- 実験の成功・不採用・停止理由と再開コマンドを`experiments/`とproject READMEへ記録する。

## 関連資料

- [WeMM候補brainstorm](../../../../secretary/notes/brainstorm/2026-11-08-wemm-embedding-authorship-feature.md)
- [公開LB首位超えgoal spec](2026-11-06-gpu-autonomous-first-place-spec.md)
- [Tencent WeMM-Embedding-4B model card](https://huggingface.co/tencent/WeMM-Embedding-4B)
- [Kaggle WeMM-Embedding-4B mirror](https://www.kaggle.com/models/dangkhoa2016/tencent-wemm-embedding-4b/Transformers/default)
- [WeMM technical report](https://arxiv.org/abs/2608.24053)
