"""V1・V3の学習中のval（tuning先頭25動画・64対象）のJ&FをF0との差で描く。

値は各runの V*_val_log.jsonl（V1: 142、V3: 141）から写した。V3は2026-10-23 07:25時点（step 1500まで）。
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.family"] = "Noto Sans CJK JP"

F0 = 0.7811
V1 = {0: 0.7811, 250: 0.7931, 500: 0.7883, 750: 0.7835, 1000: 0.7825, 1250: 0.7767,
      1500: 0.7818, 1750: 0.7809, 2000: 0.7854, 2250: 0.7888, 2500: 0.7867, 2750: 0.7871, 2789: 0.7863}
V3 = {0: 0.7811, 250: 0.7813, 500: 0.7802, 750: 0.7811, 1000: 0.7804, 1250: 0.7787, 1500: 0.7848}

BLUE, ORANGE = "#2a78d6", "#eb6834"
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"

fig, ax = plt.subplots(figsize=(7.2, 3.8), dpi=200)
fig.patch.set_facecolor("#fcfcfb")
ax.set_facecolor("#fcfcfb")

ax.axhline(0, color=MUTED, lw=1, ls="--")
ax.text(3480, 0.06, "F0（adapterなし）", ha="right", va="bottom", fontsize=8.5, color=MUTED)

for d, color, name in [(V1, BLUE, "V1（1 token）"), (V3, ORANGE, "V3（FPN的・3段）")]:
    xs = list(d)
    ys = [(v - F0) * 100 for v in d.values()]
    ax.plot(xs, ys, color=color, lw=2, marker="o", ms=5, mec="#fcfcfb", mew=1.5, label=name)
    ax.text(xs[-1] + 40, ys[-1], name, va="center", fontsize=8.5, color=INK)

ax.axvline(2789, color=GRID, lw=1)
ax.text(2810, -0.72, "1周（2,789）", ha="left", fontsize=7.5, color=MUTED)
ax.set_xlim(-80, 3500)
ax.set_ylim(-0.8, 1.6)
ax.set_xlabel("学習step（1 step＝1軌跡）", fontsize=9, color=INK)
ax.set_ylabel("val J&F − F0（ポイント）", fontsize=9, color=INK)
ax.set_title("学習中のval：V1・V3ともF0から±1.2ポイント以内で、stepとともに伸びる傾向はない",
             fontsize=9.5, color=INK, loc="left")
ax.grid(axis="y", color=GRID, lw=0.8)
for s in ["top", "right"]:
    ax.spines[s].set_visible(False)
for s in ["left", "bottom"]:
    ax.spines[s].set_color(MUTED)
ax.tick_params(colors=MUTED, labelsize=8)
ax.legend(loc="upper right", fontsize=8, frameon=False, bbox_to_anchor=(1.0, 1.0))
fig.text(0.01, 0.01, "MOSE tuningの先頭25動画・64対象（F0＝0.7811）。経過確認用で、checkpoint選択には使わない。V3は10/23 07:25時点でstep 1500まで。",
         fontsize=7, color=MUTED)
fig.tight_layout(rect=(0, 0.04, 1, 1))
out = Path(__file__).with_name("01-train-val-jf-vs-f0.png")
fig.savefig(out, facecolor=fig.get_facecolor())
print(out)
