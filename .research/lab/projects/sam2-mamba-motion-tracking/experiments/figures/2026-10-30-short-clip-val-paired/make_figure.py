"""短区間学習（F0から始めたA・B・C）のval（125動画・313対象）でのJ&Fの差を、95%区間付きで描く。

値は SAM2 repo `runs/short_clip/stage4/paired_summary.json`（動画単位のpaired bootstrap）から読む。
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.transforms import blended_transform_factory

plt.rcParams["font.family"] = "Noto Sans CJK JP"

SRC = Path("/mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2/runs/short_clip/stage4/paired_summary.json")
comp = json.loads(SRC.read_text())["comparisons"]

GROUPS = [
    ("学習の効果（F0との差）", [
        ("A−F0", "A（V3だけ）− F0"),
        ("B−F0", "B（デコーダだけ）− F0"),
        ("C−F0", "C（V3＋デコーダ）− F0"),
        ("A−V3full", "A − 全軌跡で学習したV3"),
    ]),
    ("Mambaの効果", [
        ("C−B", "C − B（H3）"),
        ("A−B", "A − B"),
    ]),
    ("stateの持ち越し（推論時のreset、診断）", [
        ("A−A-reset1", "A − 毎フレームreset"),
        ("A−A-reset8", "A − 8フレームごとにreset"),
        ("C−C-reset1", "C − 毎フレームreset"),
        ("C−C-reset8", "C − 8フレームごとにreset"),
    ]),
]

BLUE = "#2a78d6"
INK, MUTED, GRID, BG = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"

rows = []
for title, items in GROUPS:
    rows.append(("header", title))
    rows += [("item", key, label) for key, label in items]

fig, ax = plt.subplots(figsize=(8.4, 5.4), dpi=200)
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)
ax.axvline(0, color=MUTED, lw=1, ls="--")
tr = blended_transform_factory(ax.transAxes, ax.transData)

yticks, ylabels = [], []
for i, row in enumerate(rows):
    y = -i
    if row[0] == "header":
        ax.text(-0.56, y, row[1], fontsize=9, fontweight="bold", color=INK, va="center", ha="left", transform=tr)
        continue
    key, label = row[1].replace("−", "-"), row[2]
    r = comp[key]["J&F"]
    lo, hi = r["ci95_pp"]
    m = r["mean_pp"]
    excl = lo > 0 or hi < 0
    ax.plot([lo, hi], [y, y], color=BLUE, lw=2, solid_capstyle="round")
    ax.plot(m, y, "o", ms=7, mfc=BLUE if excl else BG, mec=BLUE, mew=2)
    ax.text(1.02, y, f"{m:+.2f} [{lo:+.2f}, {hi:+.2f}]", fontsize=8, color=INK, va="center", ha="left", transform=tr)
    yticks.append(y)
    ylabels.append(label)

ax.set_yticks(yticks, ylabels, fontsize=8.5, color=INK)
ax.set_xlim(-1.0, 3.2)
ax.set_xticks([-1, 0, 1, 2, 3])
ax.set_ylim(-len(rows) + 0.4, 0.6)
ax.set_xlabel("val J&Fの差（ポイント、平均と95%区間）", fontsize=9, color=INK)
ax.grid(axis="x", color=GRID, lw=0.8)
ax.set_axisbelow(True)
for s in ["top", "right", "left"]:
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color(MUTED)
ax.tick_params(axis="y", length=0)
ax.tick_params(axis="x", colors=MUTED, labelsize=8)
ax.set_title("短区間学習でA・B・CともF0を上回ったが、A−B・C−Bとreset比較は0を含む",
             fontsize=10, color=INK, x=-0.56, ha="left")
fig.text(0.01, 0.01, "●: 95%区間が0を含まない　○: 含む。MOSE val 125動画・313対象、動画単位のpaired bootstrap、単一seed。"
         "\nsource: SAM2 repo runs/short_clip/stage4/paired_summary.json",
         fontsize=7, color=MUTED, ha="left", va="bottom")
fig.subplots_adjust(left=0.30, right=0.80, top=0.92, bottom=0.17)
fig.savefig(Path(__file__).with_name("01-val-jf-paired-diff.png"), facecolor=BG)
