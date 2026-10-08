---
date: 2026-10-08
project: sam2-mamba-motion-tracking
source_todo: null
topic: mose-mtg-logging-strategy
status: exploratory
tags: [brainstorm, research]
---

# 明日のMTG向けMOSE実験ログ提示方針

## 読み込んだ文脈

- 承認済みspecでは、F0/F1をtuningで選択後に評価コード・checkpoint・実装を凍結し、lockboxを一度だけ評価する。
- F1の全2,789 stepは完了。F0はstep2789、F1はstep2000をtuningから選択し、lockbox評価条件は予測前に凍結済み。
- 2026-10-08 12:32 JST時点でP0 lockboxは570対象中310対象まで出力。tmux workerはGPU1で継続中。GPU0は515 MiB/32 GiB使用で追加学習を技術的には並列化できる。
- 現runはstep/object単位JSONLとcheckpointを保存するが、Comet/W&B/MLflow/TensorBoard event writerは接続していない。
- SAM2用venvには`comet_ml`がインストール済みで、`/home/aburatani/.comet.config`も存在する。APIキー値は表示・記録せず、Cometへの実通信は未確認。

## 相談の出発点

明日のMTGでCometなどの途中ログ付き結果を示すため、現在の実行を停止してCometを導入し、再実行するべきか。

## 問い

すでに開始したlockbox比較を止め、logging integrationのために再学習する価値があるか。

## 今回見えた方向性

- 現runを止めずに、凍結済みlockbox評価を完了させる。
- Cometは可視化・記録手段であり、training/evaluation JSONLから図を作れるため、Comet導入だけを目的に学習を再実行しない。
- MTG向け途中経過として、F0/F1 lossとtuning checkpoint選択を示す図を作成した。lockbox出力は未完了なので、この図にはlockbox性能を含めない。
- Comet画面が必須なら、既存JSONLを別の可視化runへ取り込む方法を検討する。現runの凍結済み実装や評価コードは変更しない。
- GPU0で新規学習を並列に始めても、約17時間かかった既存F1 fitを考えると翌日のMTGまでにfit・tuning・評価を揃えるのは難しい。lockbox開封後の追加runは探索的結果として分けて報告する必要があるため、現在は開始せず、凍結済みlockbox評価を優先する。
- P0部分出力315件は凍結indexの期待prefix、unique ID、軌跡長、t0除外後frame数、有限範囲のJ/F/J&Fに一致。Comet SDKと設定ファイルが既にあるので、必要なら既存の学習JSONLをCometへbackfillする方が、再学習より早くMTG用loss曲線を用意できる可能性がある（API疎通は未確認）。
- 現在は1 seedなので、結果は予備結果として説明する。seed間再現性は主張しない。

## 次アクション候補

- 現runを完了し、paired lockbox指標・bootstrap区間・長さ別結果を生成する。
- lockboxが揃ったら、MTG用の最終図と簡潔な結果表へ更新する。
- 今後のrunではCometまたはTensorBoardのloggerを追加し、JSONLと併用する。

---

## 追記 14:28

### 相談の出発点

F0/F1の本学習がすでに終わり、現在は凍結済みlockbox評価が進行中なら、GPUに余裕があるのでCometを付けた学習を並列実行できるのではないか。

### 現在の観測

- F0/F1のfitとtuning checkpoint選択は完了済み。現在の主runはF0 lockbox評価で、`objects.jsonl`は247/570件。条件・checkpoint・評価コードは凍結済み。
- 14:27 JSTの`nvidia-smi`: GPU0は7,272/32,623 MiB・77% util、GPU1は1,538/16,376 MiB・0% util。MOSE評価workerはGPU0に492 MiB、GPU1に1,372 MiBを確保。GPU0では別の評価worker 2件も稼働中。
- Comet SDK/configは存在すると過去に確認済みだが、認証を使った送信疎通は未確認。今回のF0/F1学習JSONLはローカルに残っている。

### 今回見えた方向性

- GPU1に計算余力はあるため、技術的には追加学習の並列実行候補になりうる。ただし現在の推論もGPU1にメモリを確保しており、GPU0も高使用率なので、「空いている」とは言い切れない。並列runは推論の速度・CPU/IOへ影響しうる。
- Comet付きで新規に学習しても、すでに完了したF0/F1や凍結済みlockbox比較のログにはならず、追加runは探索的結果になる。既存のF0/F1学習JSONLをCometへbackfillする方が、MTG向けの学習曲線を早く示せる可能性が高い。
- よって、今は新規学習を始めず、凍結済みlockbox評価を継続する。Comet表示が必要なら、既存JSONLのbackfillを別途短時間で試す。API送信と既存ファイルからのmetric/step対応は未検証。

### 関連ファイル

- `.research/lab/projects/sam2-mamba-motion-tracking/experiments/2026-09-30-mose-temporal-mamba-finetuning.md`

## 関連ファイル

- `.research/lab/projects/sam2-mamba-motion-tracking/specs/2026-09-30-temporal-mamba-mose-finetuning-spec.md`
- `.research/lab/projects/sam2-mamba-motion-tracking/experiments/2026-09-30-mose-temporal-mamba-finetuning.md`
- `.research/lab/projects/sam2-mamba-motion-tracking/experiments/figures/2026-10-08-mose-training-tuning-progress.png`
