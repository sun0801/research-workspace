"""潜在空間の対応（①-b）の val（125動画・313対象）での J&F の差を、95%区間付きで描く。

値は 141 の SAM2 repo `runs/latent_corr/summary/` の集計（動画単位の paired bootstrap、10,000回、seed 123）を
data/ に複製したものから読む（sha256 は manifest.md）:
- round1_did_all.json（①-b の R・I・U_id・U_shuf・性能・F0 との差）
- Ap_compare.json（A' の R・F0 との差）
round2 の U_diag は、softmax では diag が identity と同じになるので描かない（実験ログ参照）。
スタイルは ../2026-11-06-spatial-mixing-val-paired/make_figure.py に合わせた。
使い方: python3 make_figure.py（このファイルと同じフォルダに出力）
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.transforms import blended_transform_factory

plt.rcParams["font.family"] = "Noto Sans CJK JP"

DATA = Path(__file__).resolve().parent / "data"
r1 = json.loads((DATA / "round1_did_all.json").read_text())["diff_of_diffs"]
ap = json.loads((DATA / "Ap_compare.json").read_text())["comparisons"]


def get(src, key):
    r = (r1 if src == "r1" else ap)[key]["J&F"]
    return r["mean_pp"], r["ci95_pp"]


GROUPS = [
    ("学習の効果（F0 との差）", [
        (("ap", "Ap-F0"), "A'（V3）− F0"),
        (("r1", "Bc_F0"), "①-b − F0"),
    ]),
    ("総合性能（A' との差）", [
        (("r1", "perf"), "①-b − A'"),
    ]),
    ("state の寄与 R（持ち越し − 毎フレーム reset）", [
        (("ap", "Ap-Ap-reset1"), "A'"),
        (("r1", "R_Bc"), "①-b"),
    ]),
    ("state の寄与の増加 I = R(①-b) − R(A')（主な判定）", [
        (("r1", "I"), "I"),
    ]),
    ("運んだ state への依存（推論だけ対応を壊す）", [
        (("r1", "U_id"), "①-b − 対応を恒等に戻す"),
        (("r1", "U_shuf"), "①-b − 類似度をシャッフル"),
    ]),
]

BLUE = "#2a78d6"
INK, MUTED, GRID, BG = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"

rows = []
for title, items in GROUPS:
    rows.append(("header", title))
    rows += [("item", key, label) for key, label in items]

fig, ax = plt.subplots(figsize=(8.4, 5.2), dpi=200)
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
ax.set_xlim(-1.5, 3.2)
ax.set_xticks([-1, 0, 1, 2, 3])
ax.set_ylim(-len(rows) + 0.4, 0.6)
ax.set_xlabel("val J&F の差（ポイント、平均と 95% 区間）", fontsize=9, color=INK)
ax.grid(axis="x", color=GRID, lw=0.8)
ax.set_axisbelow(True)
for s in ["top", "right", "left"]:
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color(MUTED)
ax.tick_params(axis="y", length=0)
ax.tick_params(axis="x", colors=MUTED, labelsize=8)
ax.set_title("①-b は state の依存・寄与の点推定がそろって正（+0.3〜+0.6）だが、区間はどれも 0 を含む",
             fontsize=10, color=INK, x=-0.56, ha="left")
fig.text(0.01, 0.01, "●: 95%区間が0を含まない　○: 含む。MOSE val 125動画・313対象、動画単位のpaired bootstrap、単一seed、memory そのまま（M0）。A'・①-b は RTX A4000 で学習。"
         "\nsource: 141 SAM2 repo runs/latent_corr/summary/{round1_did_all,Ap_compare}.json（data/ に複製）",
         fontsize=7, color=MUTED, ha="left", va="bottom")
fig.subplots_adjust(left=0.30, right=0.80, top=0.93, bottom=0.17)
fig.savefig(Path(__file__).with_name("01-val-jf-paired-diff.png"), facecolor=BG)
