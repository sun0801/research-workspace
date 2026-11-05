"""空間混合（②・②'）と D2 の val（125動画・313対象）での J&F の差を、95%区間付きで描く。

値は SAM2 repo の集計（動画単位の paired bootstrap、10,000回、seed 123）から読む:
- runs/spatial_mixing/summary/compare.json（②・②' と A・F0 の差、R）
- runs/spatial_mixing/summary/did.json（I：state の寄与の増加）
- runs/spatial_mixing/D2/summary/did.json（R(A)：A の state の寄与）
スタイルは ../2026-10-30-short-clip-val-paired/make_figure.py に合わせた。
使い方: python3 make_figure.py（このファイルと同じフォルダに出力）
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.transforms import blended_transform_factory

plt.rcParams["font.family"] = "Noto Sans CJK JP"

ROOT = Path("/mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2/runs/spatial_mixing")
cmp_ = json.loads((ROOT / "summary/compare.json").read_text())["comparisons"]
did = json.loads((ROOT / "summary/did.json").read_text())["diff_of_diffs"]
d2 = json.loads((ROOT / "D2/summary/did.json").read_text())["diff_of_diffs"]


def get(src, key):
    r = (cmp_ if src == "cmp" else did if src == "did" else d2)[key]["J&F"]
    return r["mean_pp"], r["ci95_pp"]


GROUPS = [
    ("学習の効果（F0 との差）", [
        (("d2", "AmF0_M0"), "A（V3）− F0"),
        (("cmp", "A_rw-F0"), "② − F0"),
        (("cmp", "A_sml1-F0"), "②' − F0"),
    ]),
    ("総合性能（A との差）", [
        (("cmp", "A_rw-A"), "② − A"),
        (("cmp", "A_sml1-A"), "②' − A"),
    ]),
    ("state の寄与 R（持ち越し − 毎フレーム reset）", [
        (("d2", "R_A_M0"), "A"),
        (("cmp", "A_rw-A_rw-reset1"), "②"),
        (("cmp", "A_sml1-A_sml1-reset1"), "②'"),
    ]),
    ("state の寄与の増加 I = R(新) − R(A)（主な判定）", [
        (("did", "I_rw_M0"), "②"),
        (("did", "I_sm_M0"), "②'"),
    ]),
    ("memory を直前 1 枚に絞った場合（M1）", [
        (("d2", "R_A_M1"), "R(A)"),
        (("did", "I_rw_M1"), "I(②)"),
        (("did", "I_sm_M1"), "I(②')"),
    ]),
]

BLUE = "#2a78d6"
INK, MUTED, GRID, BG = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"

rows = []
for title, items in GROUPS:
    rows.append(("header", title))
    rows += [("item", key, label) for key, label in items]

fig, ax = plt.subplots(figsize=(8.4, 6.0), dpi=200)
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
    (src, key), label = row[1], row[2]
    m, (lo, hi) = get(src, key)
    excl = lo > 0 or hi < 0
    ax.plot([lo, hi], [y, y], color=BLUE, lw=2, solid_capstyle="round")
    ax.plot(m, y, "o", ms=7, mfc=BLUE if excl else BG, mec=BLUE, mew=2)
    ax.text(1.02, y, f"{m:+.2f} [{lo:+.2f}, {hi:+.2f}]", fontsize=8, color=INK, va="center", ha="left", transform=tr)
    yticks.append(y)
    ylabels.append(label)

ax.set_yticks(yticks, ylabels, fontsize=8.5, color=INK)
ax.set_xlim(-2.0, 3.2)
ax.set_xticks([-2, -1, 0, 1, 2, 3])
ax.set_ylim(-len(rows) + 0.4, 0.6)
ax.set_xlabel("val J&F の差（ポイント、平均と 95% 区間）", fontsize=9, color=INK)
ax.grid(axis="x", color=GRID, lw=0.8)
ax.set_axisbelow(True)
for s in ["top", "right", "left"]:
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color(MUTED)
ax.tick_params(axis="y", length=0)
ax.tick_params(axis="x", colors=MUTED, labelsize=8)
ax.set_title("②・②' とも state の寄与は増えず（I・R は 0 を含む）、②' は A よりやや低い",
             fontsize=10, color=INK, x=-0.56, ha="left")
fig.text(0.01, 0.01, "●: 95%区間が0を含まない　○: 含む。MOSE val 125動画・313対象、動画単位のpaired bootstrap、単一seed。M1 以外は memory そのまま（M0）。"
         "\nsource: SAM2 repo runs/spatial_mixing/summary/{compare,did}.json、runs/spatial_mixing/D2/summary/did.json",
         fontsize=7, color=MUTED, ha="left", va="bottom")
fig.subplots_adjust(left=0.30, right=0.80, top=0.93, bottom=0.15)
fig.savefig(Path(__file__).with_name("01-val-jf-paired-diff.png"), facecolor=BG)
