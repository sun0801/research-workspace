---
date: 2026-11-12
project: kaggle-name-that-llm
type: candidate-oof-addition-screen
---

# Host141 candidate OOF and baseline-addition screen

確認日時: 2026-11-12 00:08 JST。Host141のGPU compute一覧は空。GPU0は171/16,376 MiB、GPU1/2は各15/16,376 MiB、`MemAvailable=120,798,460 kB`。候補runnerのPIDはなく、長時間bash sessionにもchild jobはなかった。Qwen3-4B、ModernBERT-Base、ModernBERT-Largeの各primaryはfold 0–4のOOFとlogitsが保存され、primary logはfold4完了で終わっている。

## Standalone primary gate

既存analyzerで各候補をCPU best primary OOF（BA `.384504`）と比較。2,699行、150 prompt groups、2,000回prompt-paired bootstrap、seed 42。

| Candidate | Primary BA | CPU bestとの差 | 95% CI | Gate |
|---|---:|---:|---:|---|
| Qwen3-4B | `.542329` | `+.157825` | `[+.137399, +.180455]` | adopt |
| ModernBERT-Base | `.447122` | `+.062617` | `[+.043701, +.081111]` | adopt |
| ModernBERT-Large | `.499734` | `+.115230` | `[+.096659, +.134816]` | adopt |

3候補ともCPU bestに対するprimary adoption gateは通過した。ただし現在採用中のQwen3-8B + Qwen3-1.7B + prompt-centered SVC blendへの追加価値を別に確認した。

## Fixed equal-weight addition screen

保存済みbaseline確率に候補softmax確率を1/4ずつ足し、重み調整なしで5-fold OOFを比較。baseline確率と候補logitsのargmaxは全foldで保存済み予測と一致し、ID・label・prompt・fold整列も確認。現baseline OOF BAは`.586408`。

| Candidate | 追加後BA | baselineとの差 | 95% CI | 判定 |
|---|---:|---:|---:|---|
| Qwen3-4B | `.578998` | `−.007410` | `[−.015931, +.000743]` | reject（増加を確認できず） |
| ModernBERT-Base | `.575285` | `−.011124` | `[−.019269, −.002593]` | reject |
| ModernBERT-Large | `.584188` | `−.002220` | `[−.011513, +.007037]` | reject（増加を確認できず） |

この固定additionでは既存blendを上回る候補がなかったため、3候補を現行blendへ加えず、confirmationやNotebook作成へは進めない。別weight探索を行う場合は、独立したnested prompt-grouped specが必要。

再利用script: [analyze_probability_blend_addition.py](/mnt/HDD10TB-2/aburatani/kaggle/name-that-llm/scripts/analyze_probability_blend_addition.py)。各候補の採用比較summaryと`equal-mean-addition-screen.json`はHost141の各artifact `primary/` に保存。CPU-cycle artifactは読み取りのみで変更していない。

Host141は空いているが、残る登録候補のOLMo2-7BとQwen3.5-9BはHost142 GPU1に固定されている。Host142はSSH aliasの名前解決が失敗し、状態を再確認できなかったため、そこでのjob状態は推測しない。Kaggle CLIも未認証で、private baseline Notebookのremote runtime gateは未実施。

次: Kaggle OAuth復旧後にbaseline private DatasetとNotebook runtime gateを進める。Host142接続復旧後に登録済み候補のqueue状態・GPU/RAMを確認し、継続可能なjobだけを再開する。No GPU job was launched or stopped during this screen.
