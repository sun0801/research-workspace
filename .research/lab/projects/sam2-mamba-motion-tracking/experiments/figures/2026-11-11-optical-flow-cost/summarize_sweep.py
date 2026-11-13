"""Summary of flow_sweep.py: mean IoU per (stratum, border) over objects-pairs averaged per video, median time.

  python summarize_sweep.py > data/sweep_summary.md
"""
import json
from collections import defaultdict

import numpy as np

rows = [json.loads(l) for l in open("data/sweep.jsonl")]
methods = list(rows[0]["iou"])
groups = {"速い・端に触れない": lambda r: r["stratum"] == "fast" and not r["border"],
          "速い・端に触れる": lambda r: r["stratum"] == "fast" and r["border"],
          "遅い・全部": lambda r: r["stratum"] == "slow"}
print(f"rows {len(rows)}; " + ", ".join(f"{g}: {sum(map(f, rows))}" for g, f in groups.items()))
print()
print("IoU（t の物体を flow で前に動かした領域 vs t+1 の正解。動画ごとに平均し、動画の平均）と時間（1組の中央値、ms）")
print()
print("| 設定 | " + " | ".join(groups) + " | 時間 ms |")
print("|---|" + "---|" * (len(groups) + 1))
for m in methods:
    cells = []
    for g, f in groups.items():
        per_vid = defaultdict(list)
        for r in rows:
            if f(r):
                per_vid[r["video"]].append(r["iou"][m])
        cells.append(f"{np.mean([np.mean(v) for v in per_vid.values()]):.3f}（{len(per_vid)}本）" if per_vid else "—")
    ms = np.median([r["ms"][m] for r in rows])
    print(f"| {m} | " + " | ".join(cells) + f" | {ms:.1f} |")
