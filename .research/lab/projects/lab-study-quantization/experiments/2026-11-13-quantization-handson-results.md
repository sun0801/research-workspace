---
date: 2026-11-13
project: lab-study-quantization
type: experiment-log
status: draft
tags: [quantization, study-session, handson, results]
---

# 量子化勉強会ハンズオンの結果ログ（先行検証・事前計算）

コードは `/mnt/HDD10TB-2/aburatani/quantization_handson`（未コミット）。結果のJSONは同リポジトリの `results/`。
すべて fake-quant（誤差の模擬）の精度。演習④だけが実際の低精度実行。

## 1. 条件の記録

| 項目 | 値 |
|---|---|
| 環境 | Python 3.12 / torch 2.15.0+cu132 / torchvision 0.29.2 / torchao 0.18.0 / timm 1.0.31 / bitsandbytes 0.50.2（`requirements.txt` に固定） |
| GPU | nvidia-smi の GPU0（RTX A4000, 16GB）。計算プロセスなしを確認して使用。GPU1（Blackwell）はKaggleのジョブがあるため使っていない |
| CPU | Intel Xeon E5-2699 v3, 72スレッド。時間測定はスレッド数8に固定 |
| ResNet18 | torchvision `IMAGENET1K_V1` → CIFAR10 fine-tune。入力 96×96（32×32 を bilinear resize） |
| ViT | timm `deit_tiny_patch16_224.fb_in1k`（DeiT-Tiny）→ CIFAR10 fine-tune。入力 112×112（パッチ16 → 49トークン）。理由: 224だと計算が約4倍で、CPU演習の時間制約に余裕を持たせたいため |
| fine-tune | 5 epoch、batch 128、seed 0、bf16 autocast。ResNet18: SGD(nesterov) lr 0.02 / wd 5e-4、OneCycle。DeiT-Tiny: AdamW lr 1e-4 / wd 0.05、OneCycle。augment は random crop(pad 4)＋左右反転（crop位置はバッチ単位） |
| 評価データ | CIFAR10 test から seed 0 で固定した 2,000 枚（`data/eval2000.npz` にindex保存、uint8・32×32 のまま約6MB）。batch 100 |
| 較正データ | CIFAR10 train から seed 0 で固定した 512 枚（`data/calib512.npz`）。FP32モデルで1回流す |
| 較正方法（事前固定） | minmax / percentile 99.99（[0.01%, 99.99%] 分位）/ mse（範囲の0.1〜1.0倍を91通り）。testの結果で選び直していない |
| TF32 | 無効（GPUとCPUで結果をそろえるため） |
| 再現性の注意 | GPUとCPUで評価値が±0.1〜0.2 pp ずれることがある（例: DeiT-Tiny W8A8 mse は GPU 95.15 / CPU 95.25）。同一デバイスでは再現する |

## 2. 先行検証（スペックの順）

### 2-1. fine-tune・QATの所要時間の見積もり（本番と同じコマンドで30 step）

| 対象 | 1 step | 1 epoch(390 step) | peak |
|---|---|---|---|
| ResNet18 fine-tune（96px） | 0.043 s（入力64pxの測定。96pxに変えて本番は5 epoch 1.1分） | 約0.3分 | 0.28 GiB |
| DeiT-Tiny fine-tune（112px） | 0.062 s（本番は5 epoch 1.9分） | 約0.4分 | 0.63 GiB |
| ResNet18 QAT（W4A8、STE） | 0.105 s | 約0.7分 | — |
| DeiT-Tiny QAT（W4A8、STE） | 0.132 s | 約0.9分 | — |

15分を超える学習はなかった。QATの事前計算（3 seed）は ResNet18 約3.7分、DeiT-Tiny 約4.0分。

### 2-2. 基準checkpoint

- ResNet18: CIFAR10 test 10,000枚で 94.29%（5 epoch、1.1分）
- DeiT-Tiny: 同 95.23%（5 epoch、1.9分）
- 学習中のpeakメモリは上の表のとおり（1GiB未満）。

### 2-3. FP32の基準精度

| モデル | eval2000（固定2,000枚） | 全10,000枚（参考、1回） |
|---|---|---|
| ResNet18（BN folding後） | 93.45% | 94.29% |
| DeiT-Tiny | 95.00% | 95.23% |

BN folding の検証: folding前後の最大差（eval2000の先頭64枚，CPU，ResNet18，最大|logit|≈25.6）は fp64 で 1.8e-14，fp32 で 1.1e-5（2026-11-14 再測定）。差は丸め誤差で，folding実装の誤りではない。（当初記録の「fp64 で 5.9e-7」は再現できず，撤回した。GPUのfp32で 1.0e-2 とあったのはTF32無効化前の値）

### 2-4. 演習②③の代表条件の精度・実行時間・peakメモリ

「1回」= 1モデル×1条件（モデル読み込み・較正・評価を含む）。環境の有効化は含めない。

新しいシェルで README の手順だけから環境を作り直して測った（`uv venv` → `uv pip install -r requirements.txt` 1秒（キャッシュ有）→ `prepare.py` 15秒（CIFAR10のtar.gzは取得済みのものを置いた）→ fine-tune → 各演習）。時間は「スクリプトを起動してから結果が出るまで」（`python` 起動・import・モデル読み込み・較正・評価を含む、環境の有効化は含まない）。基準checkpointは作り直しても同じ精度（94.29% / 95.23%）で、演習の精度も元の環境と一致した。

| 演習・条件 | ResNet18 | DeiT-Tiny |
|---|---|---|
| ① `ex1_tensor.py --outlier 20`（CPU） | 2 s | — |
| ② 重みのみ4bit per-channel、GPU（A4000） | 7 s | 6 s |
| ② 同、CPU 8スレッド | 13 s | 13 s |
| ③ W8A8 の3較正方法（minmax/percentile/mse）、GPU | 12 s | 16 s |
| ③ 同、CPU 8スレッド | 27 s | 39 s |
| ④ `fx_int8` / `torchao`（CPU） | 20 s | 85 s |
| ④ `nf4`（GPU） | 11 s（ViT-Base） | — |

- 30秒以内（GPU）・3分以内（CPU）の目安を、1条件ずつなら満たす。③を3つの較正方法まとめて回しても CPU で40秒以内。
- GPUの1条件の評価（プロセス内）は 0.2〜4.6 秒、peak は 0.13〜0.29 GiB（`torch.cuda.max_memory_allocated`、測定前にreset）。
- 注意: `--device cpu` の指定で、MSE探索を含む較正もCPUだけで行う（GPUは使わない）。

代表条件の精度は §4 の全比較表に含まれる。

### 2-5. 演習④（実際の低精度実行）が動くか

CPU、スレッド数8、batch 32、入力は評価画像の先頭32枚（resnet18 96px、deit_tiny 112px）。warm-up 30回のあと30回を測り、中央値。サイズは保存した `state_dict` のファイルサイズ。精度は eval2000。`ex4_lowprec.py` を5〜6回流した値（共有マシンで他ユーザーのジョブがあり、load average 約8の状態）。

**測定順の影響**: 最初に測ったFP32は、同じプロセスで最後に測り直したFP32より遅く出る（ResNet18 61〜64 → 53〜55 ms、DeiT-Tiny 48〜75 → 45〜49 ms）。原因は特定していない（初回のみの状態の影響とみられる）。比較の基準には、測り直したFP32（量子化モデルを測ったあと）を使う。

| 経路 | モデル | サイズ | 遅延(ms/batch32) | 精度 |
|---|---|---|---|---|
| FP32（測り直し） | ResNet18 | 44.80 MB | 53〜55 | 93.45% |
| INT8（`torch.ao` FXグラフモード, x86） | ResNet18 | 11.30 MB | 37〜38（FP32の約0.69倍） | 93.55% |
| FP32（測り直し） | DeiT-Tiny | 22.04 MB | 45〜49 | 95.00% |
| INT8 weight-only（torchao） | DeiT-Tiny | 6.24 MB | 50〜54（FP32より約10%遅い） | 95.00% |
| INT8 dynamic（torchao） | DeiT-Tiny | 6.24 MB | 約790（FP32の約16倍） | 94.90% |

- INT8は小さくなる（ResNet18 約1/4、DeiT-Tiny 約1/3.5）。ResNet18 のConvを含むINT8だけが速くなる。DeiT-Tiny は weight-only でわずかに遅く、dynamic は約16倍遅い。
- dynamic INT8 が遅い原因: `torch.profiler` で、実行時間の約88%が `aten::_int_mm`（49回、1回約15.7ms）に使われていた（torch 2.15 / CPU）。つまり遅いのはINT8の行列積の実装で、活性の量子化処理ではない。「CPUでこのkernelが速くない」ことまでが確認できた事実で、他のCPU・他のバージョンでは結果が変わりうる。
- 「量子化すれば速くなるとは限らない」の実例: 同じINT8でも、モデル・演算・kernelによって速くなる/ほぼ同じ/大きく遅くなる。
- 4bit（bitsandbytes NF4）: timm ViT-Base（`Linear` のみ変換、重みは未学習の初期値）のパラメータ保持量 FP16 165 MiB → NF4 43 MiB、forward（batch 8）のpeak 0.20 → 0.07 GiB（`torch.cuda.max_memory_allocated`）。GPU0（A4000）の4GB以内。
- 経路の選択（確認日 2026-11-13）: torchaoのPT2E（`X86InductorQuantizer`）はResNet18の残差パターンで `Input partition has more than one output node` となり動かなかった（torch 2.15 には `torch.export.export_for_training` もない）。`torch.ao.quantization.quantize_fx` は動くが、将来のtorchao移行で使えなくなる可能性がある。torchao の `quantize_` は ResNet18 の Conv には効かず（Linearのみ）、DeiT-Tiny で有効。

## 3. 観察（スライドで使う場合は「発表者の解釈」を明記する）

- 4bit重みはper-tensorだと崩れ（ResNet18 29%, DeiT-Tiny 29%）、per-channel・per-groupで回復する（§4）。
- 活性は、ResNet18 は A4 まで 86〜91%（minmax/percentile/mse）で耐えるが、DeiT-Tiny は A4 で 25〜71%まで落ち、較正方法の差が大きい（minmax 24.9 / mse 47.6 / percentile 71.1）。A8 では全方法で差は±0.3 pp 以内。
- DeiT-Tiny の1層だけ A4 にしても、最大の低下は blocks.0.mlp.fc2（GELU後）の 95.00 → 92.55 で、ほとんどの層は −0.3 pp 以内（`results/sensitivity.json`）。全層をA4にしたときの崩れは層をまたいだ誤差の累積とみられる（未検証の解釈）。
- **LLM型の極端な外れ値は、この fine-tune 済み DeiT-Tiny では観測されなかった**（スライドの語り方に直結するので、発表者の解釈として扱う）。
  - Linear入力のチャネルごとの最大値の比（最大/中央値）は、DeiT-Tiny で最大 4.3（blocks.0.mlp.fc2、GELU後）、ResNet18 layer4.1.conv2 は 1.7。LayerNorm出力（norm1 out）は 1.8〜4.1、残差ストリーム（ブロック出力）は 2.8〜7.0（blocks 0/3/6/9/11 で測定）。図: [experiments/figures/2026-11-13-act-channel-absmax.png](figures/2026-11-13-act-channel-absmax.png)
  - テンソル全体の裾の重さ（最大値/99.99%点）の中央値は DeiT-Tiny 1.46（最大2.26）、ResNet18 1.98（最大3.10）。DeiT-Tiny のほうが裾が重いわけではない。MSEが選ぶクリップ比（A4）の中央値も DeiT 0.42、ResNet18 0.36 で大差ない。
  - したがって、ViT の A4 での崩れ（minmax 24.9% / percentile 71.1% / mse 47.6%）を「外れ値チャネル」だけでは説明できない。1層だけ A4 にした場合の低下は小さい（最大 −2.45 pp）ことから、層をまたいだ誤差の累積（と GELU後の blocks.*.mlp.fc2 の敏感さ）が効いているとみられる。**ただし未検証の解釈**。
  - SmoothQuant・LLM.int8() の外れ値は原典（LLM）の主張。ViT の分布を直接扱う原典は PTQ4ViT（post-softmax・post-GELU）。演習③の観測とは分けて示す。
- 最初と最後の層の感度（W4 / A4 を1層だけ）: ResNet18 conv1 は W4で 92.5%、A4で 92.05%（FP32 93.45%）、fc はほぼ無傷。DeiT-Tiny patch_embed は W4で 93.7%、A4で 93.65%、head はほぼ無傷。入力に近い層は他より敏感。

## 4. 全比較表（fake-quant、eval2000、1回の実行）

重みの量子化は対称・符号付き。活性は非対称・per-tensor・静的。W4/W8の「per-channel」は出力チャネル軸。


#### resnet18（FP32 93.45%、eval2000。括弧内はFP32との差 pp）

**重みのみ（fake-quant）**

| bit | per-tensor | per-channel | per-group(64) |
|---|---|---|---|
| 8 | 93.50 (+0.05) | 93.40 (-0.05) | 93.45 (+0.00) |
| 6 | 93.20 (-0.25) | 93.30 (-0.15) | 93.45 (+0.00) |
| 4 | 29.20 (-64.25) | 90.70 (-2.75) | 92.25 (-1.20) |
| 3 | 10.30 (-83.15) | 48.25 (-45.20) | 79.60 (-13.85) |
| 2 | 9.90 (-83.55) | 8.70 (-84.75) | 13.50 (-79.95) |

**重み8bit per-channel ＋ 活性（非対称・per-tensor・静的）**

| 活性bit | minmax | percentile(99.99) | mse |
|---|---|---|---|
| 8 | 93.35 (-0.10) | 93.25 (-0.20) | 93.40 (-0.05) |
| 6 | 93.35 (-0.10) | 93.55 (+0.10) | 93.60 (+0.15) |
| 4 | 86.70 (-6.75) | 91.30 (-2.15) | 90.85 (-2.60) |
| 3 | 51.45 (-42.00) | 75.85 (-17.60) | 80.20 (-13.25) |
| 2 | 12.90 (-80.55) | 26.00 (-67.45) | 55.40 (-38.05) |

**重み4bit per-channel ＋ 活性（非対称・per-tensor・静的）**

| 活性bit | minmax | percentile(99.99) | mse |
|---|---|---|---|
| 8 | 90.90 (-2.55) | 90.75 (-2.70) | 90.65 (-2.80) |
| 6 | 90.75 (-2.70) | 90.60 (-2.85) | 90.45 (-3.00) |
| 4 | 83.80 (-9.65) | 88.00 (-5.45) | 88.35 (-5.10) |

#### deit_tiny（FP32 95.00%、eval2000。括弧内はFP32との差 pp）

**重みのみ（fake-quant）**

| bit | per-tensor | per-channel | per-group(64) |
|---|---|---|---|
| 8 | 94.85 (-0.15) | 95.00 (+0.00) | 95.05 (+0.05) |
| 6 | 94.75 (-0.25) | 94.65 (-0.35) | 95.05 (+0.05) |
| 4 | 28.55 (-66.45) | 91.90 (-3.10) | 94.05 (-0.95) |
| 3 | 7.45 (-87.55) | 34.00 (-61.00) | 78.00 (-17.00) |
| 2 | 10.45 (-84.55) | 11.70 (-83.30) | 10.20 (-84.80) |

**重み8bit per-channel ＋ 活性（非対称・per-tensor・静的）**

| 活性bit | minmax | percentile(99.99) | mse |
|---|---|---|---|
| 8 | 94.90 (-0.10) | 94.95 (-0.05) | 95.15 (+0.15) |
| 6 | 94.00 (-1.00) | 94.25 (-0.75) | 94.45 (-0.55) |
| 4 | 24.90 (-70.10) | 71.05 (-23.95) | 47.60 (-47.40) |
| 3 | 10.05 (-84.95) | 11.50 (-83.50) | 14.25 (-80.75) |
| 2 | 9.25 (-85.75) | 8.15 (-86.85) | 10.65 (-84.35) |

**重み4bit per-channel ＋ 活性（非対称・per-tensor・静的）**

| 活性bit | minmax | percentile(99.99) | mse |
|---|---|---|---|
| 8 | 91.95 (-3.05) | 91.10 (-3.90) | 91.90 (-3.10) |
| 6 | 90.30 (-4.70) | 90.35 (-4.65) | 89.75 (-5.25) |
| 4 | 19.90 (-75.10) | 53.10 (-41.90) | 28.90 (-66.10) |

## 5. QAT（事前計算、W4 per-channel ＋ A8 mse、fake-quant）

同じ更新回数（390 step ≈ 1 epoch）、同じデータ順で学習。QATはSTEで重みと活性をfake-quantしながら学習（活性のscaleは学習前のFP32で較正して固定、重みのscaleは毎stepminmaxで再計算）。比較対象は「同じ回数だけ通常のfine-tuneをしてからPTQ（再較正）」。3 seed（学習のデータ順・augment）。

| モデル | FP32 | PTQのみ | fine-tune→PTQ（3 seed、平均） | QAT（3 seed、平均） |
|---|---|---|---|---|
| ResNet18 | 93.45 | 90.65 | 91.7 / 90.5 / 91.4（91.2） | 93.25 / 93.2 / 92.9（93.1） |
| DeiT-Tiny | 95.00 | 91.90 | 91.65 / 91.85 / 91.95（91.8） | 93.6 / 93.45 / 94.05（93.7） |

- 同じ更新回数のfine-tune→PTQ と比べても、3 seedすべてでQATが上回った（ResNet18 +1.5〜2.7 pp、DeiT-Tiny +1.7〜2.1 pp）。この条件（W4A8、短いfine-tune、1データセット）での観察で、一般にQATがPTQより優れるという主張ではない。
- 学習率・epoch数は調整していない（1設定のみ）。「PTQのみ」の値は §4 の W4 per-channel＋A8 mse（ResNet18 90.65 / DeiT-Tiny 91.90）と一致する。

## 6. 未確認・注意

- 速度・サイズは単一マシン（Xeon E5-2699 v3）での1回の中央値。ハードウェアが変われば結果は変わる。
- DeiT-Tiny の dynamic INT8 が遅い原因は特定していない。
- 研究室メンバー各自のCPUスレッド数・GPUでの時間は未測定（当日の配布方法が未決）。
- 分類表（GPTQ・AWQなど）の手法は演習では測っていない。

## 7. 追記（2026-11-14，スライド検査を受けて）

### 7-1 演習① `ex1_tensor.py --outlier 20` の出力（CPU・乱数固定，fresh-venv 再現で一致）
x: min -4.09 max 20.00 std 1.04（外れ値1個を20に置いた入力）

| bits | モード | scale | zero | max\|err\| | MSE | SQNR[dB] |
|---|---|---|---|---|---|---|
| 8 | 対称 | 0.1575 | 0 | 0.0787 | 0.00208 | 27.18 |
| 8 | 非対称 | 0.0945 | 43 | 0.0472 | 0.00074 | 31.68 |
| 6 | 対称 | 0.6452 | 0 | 0.3225 | 0.03409 | 15.02 |
| 6 | 非対称 | 0.3824 | 11 | 0.1912 | 0.01220 | 19.49 |
| 4 | 対称 | 2.8571 | 0 | 1.4282 | 0.59652 | 2.59 |
| 4 | 非対称 | 1.6062 | 3 | 0.8030 | 0.21475 | 7.03 |
| 3 | 対称 | 6.6667 | 0 | 3.2834 | 0.97732 | 0.45 |
| 3 | 非対称 | 3.4420 | 1 | 1.7191 | 0.74210 | 1.65 |
| 2 | 対称 | 20.0000 | 0 | 4.1015 | 0.98635 | 0.41 |
| 2 | 非対称 | 8.0312 | 1 | 3.9375 | 0.98949 | 0.40 |

### 7-2 GPU と CPU の差（検査①②で CPU 実行して確認）
- DeiT-Tiny W8A4 per-channel を CPU で回すと minmax 25.45（GPU 24.90），percentile 70.70（71.05），mse 47.60（同じ）。最大 0.55 pp ずれる。順位は同じ。
- 「±0.1〜0.2 pp」は W8A8 など大半の条件の話で，A4 のように脆い条件では当てはまらない。
- 混雑時の所要: torchao 約 128 秒（空いているとき約 85 秒），fx_int8 約 26.5 秒（約 20 秒）。

### 7-3 演習① `ex1_tensor.py --outlier 0` の出力（外れ値なし，CPU・乱数固定）
x: min -4.09 max 4.10 std 0.99

| bits | モード | scale | zero | max\|err\| | MSE | SQNR[dB] |
|---|---|---|---|---|---|---|
| 8 | 対称 | 0.0323 | 0 | 0.0161 | 0.00009 | 40.50 |
| 8 | 非対称 | 0.0321 | 127 | 0.0161 | 0.00009 | 40.56 |
| 6 | 対称 | 0.1323 | 0 | 0.0661 | 0.00148 | 28.23 |
| 6 | 非対称 | 0.1301 | 31 | 0.0650 | 0.00142 | 28.41 |
| 4 | 対称 | 0.5859 | 0 | 0.2928 | 0.02799 | 15.47 |
| 4 | 非対称 | 0.5463 | 7 | 0.2731 | 0.02468 | 16.02 |
| 3 | 対称 | 1.3672 | 0 | 0.6830 | 0.15442 | 8.05 |
| 3 | 非対称 | 1.1707 | 3 | 0.5854 | 0.11305 | 9.41 |
| 2 | 対称 | 4.1015 | 0 | 2.0485 | 0.85437 | 0.63 |
| 2 | 非対称 | 2.7317 | 1 | 1.3654 | 0.56180 | 2.45 |

### 7-4 演習④ nf4 の再実行（2026-11-14，GPU0のみ）
vit_base FP16: params 165 MiB，forward peak 0.20 GiB／NF4（Linearのみ）: params 43 MiB，peak 0.07 GiB。先行検証と一致。
