"""Concept figure for the 11/13 MTG: three ways to decide where a cell p takes its state from (explanatory, not data).

The window is drawn as 7x7 for readability (the real one is 15x15); the weights are made-up example values.
  python concept.py   # writes 01a-similarity.png, 01b-constraint.png, 01c-surroundings.png
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Patch, Rectangle

rcParams["font.family"] = "Noto Sans CJK JP"
HERE = Path(__file__).resolve().parent
P_COL, NB_COL, OK_COL, W_COL, GRID = "#c71f7a", "#eda100", "#1baf7a", "#2a78d6", "#9a9a9a"
T_X, T_Y, N_T = 0.0, 1.0, 5      # frame t grid (5x5), p at its centre
W_X, W_Y, N_W = 7.0, 0.0, 7      # frame t-1 window (7x7), centred on p's position


def grid(ax, x0, y0, n, label):
    for i in range(n + 1):
        ax.plot([x0, x0 + n], [y0 + i, y0 + i], color=GRID, lw=0.7)
        ax.plot([x0 + i, x0 + i], [y0, y0 + n], color=GRID, lw=0.7)
    ax.text(x0 + n / 2, y0 + n + 0.35, label, ha="center", va="bottom", fontsize=12)


def cell(ax, x0, y0, c, r, **kw):
    ax.add_patch(Rectangle((x0 + c, y0 + r), 1, 1, **kw))


def centre(x0, y0, c, r):
    return x0 + c + 0.5, y0 + r + 0.5


def link(ax, a, b, color, lw=1.5, alpha=1.0, ls="-"):
    ax.add_patch(FancyArrowPatch(b, a, arrowstyle="-|>", mutation_scale=10, color=color, lw=lw, alpha=alpha, ls=ls,
                                 shrinkA=4, shrinkB=4))


def base(ax, title):
    grid(ax, T_X, T_Y, N_T, "フレーム t")
    grid(ax, W_X, W_Y, N_W, "フレーム t−1（探す窓）")
    ax.set_title(title, fontsize=14, pad=14)
    ax.set_xlim(-0.5, 14.5); ax.set_ylim(-3.4, 8.2); ax.set_aspect("equal"); ax.axis("off")


P = (2, 2)
WEIGHTS = {(1, 5): 0.35, (5, 6): 0.25, (0, 1): 0.2, (6, 2): 0.12, (3, 4): 0.08}
H_P = Patch(fc=P_COL, alpha=0.85, label="state を受け取るマス p")
H_W = Patch(fc=W_COL, alpha=0.6, label="持ってくる元（濃いほど重み大）")


def save(fig, ax, handles, name):
    fig.legend(handles=handles, loc="lower center", ncol=2, fontsize=11.5, frameon=False)
    fig.subplots_adjust(left=0.01, right=0.99, top=0.9, bottom=0.15)
    fig.savefig(HERE / name, dpi=110)
    plt.close(fig)


def similarity():
    """1. similarity, cell to cell (the current A-b)."""
    fig, ax = plt.subplots(figsize=(8.5, 6.4))
    base(ax, "類似度最大（今のA-b）")
    pc = centre(T_X, T_Y, *P)
    cell(ax, T_X, T_Y, *P, fc=P_COL, alpha=0.85)
    for (c, r), w in WEIGHTS.items():
        cell(ax, W_X, W_Y, c, r, fc=W_COL, alpha=0.25 + 1.8 * w)
        link(ax, pc, centre(W_X, W_Y, c, r), W_COL, lw=1 + 5 * w, alpha=0.8)
    save(fig, ax, [H_P, H_W], "01a-similarity.png")


def constraint():
    """2. constraint from the up / down / left / right neighbours."""
    fig, ax = plt.subplots(figsize=(8.5, 6.4))
    base(ax, "制約を入れる案")
    pc = centre(T_X, T_Y, *P)
    cell(ax, T_X, T_Y, *P, fc=P_COL, alpha=0.85)
    for dc, dr in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        cell(ax, T_X, T_Y, P[0] + dc, P[1] + dr, fc=NB_COL, alpha=0.7)
    agree = (4, 2)  # where the neighbours' choices point to (+-1 cell shown as the green block)
    ax.add_patch(Rectangle((W_X + agree[0] - 1, W_Y + agree[1] - 1), 3, 3, fc=OK_COL, alpha=0.18, ec=OK_COL, lw=2))
    for (c, r), w in WEIGHTS.items():
        cell(ax, W_X, W_Y, c, r, fc="#cccccc", alpha=0.6)
    cell(ax, W_X, W_Y, *agree, fc=W_COL, alpha=0.8)
    link(ax, pc, centre(W_X, W_Y, *agree), W_COL, lw=3)
    for dc, dr in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        link(ax, centre(T_X, T_Y, P[0] + dc, P[1] + dr), centre(W_X, W_Y, agree[0] + dc, agree[1] + dr),
             NB_COL, lw=1.2, alpha=0.8, ls="--")
    ax.annotate("", xy=(11.6, -1.9), xytext=(9.4, -1.9),
                arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=-0.6", color="#555555", lw=1.5))
    ax.text(10.5, -2.9, "数回くり返す", ha="center", fontsize=11.5, color="#555555")
    save(fig, ax, [H_P, Patch(fc=NB_COL, alpha=0.7, label="上下左右の隣（破線：隣が選んだ移動）"),
                   Patch(fc=OK_COL, alpha=0.3, ec=OK_COL, label="隣と1マス以内でそろう候補"),
                   Patch(fc="#cccccc", alpha=0.6, label="点数が下がる候補")], "01b-constraint.png")


def surroundings():
    """3. compare the 3x3 surroundings."""
    fig, ax = plt.subplots(figsize=(8.5, 6.4))
    base(ax, "周りごと照合する案（本命）")
    q = (5, 4)
    ax.add_patch(Rectangle((T_X + P[0] - 1, T_Y + P[1] - 1), 3, 3, fc=NB_COL, alpha=0.25, ec=NB_COL, lw=2, ls="--"))
    ax.add_patch(Rectangle((W_X + q[0] - 1, W_Y + q[1] - 1), 3, 3, fc=NB_COL, alpha=0.25, ec=NB_COL, lw=2, ls="--"))
    cell(ax, T_X, T_Y, *P, fc=P_COL, alpha=0.85)
    cell(ax, W_X, W_Y, *q, fc=W_COL, alpha=0.8)
    for dc in (-1, 0, 1):
        for dr in (-1, 0, 1):
            link(ax, centre(T_X, T_Y, P[0] + dc, P[1] + dr), centre(W_X, W_Y, q[0] + dc, q[1] + dr),
                 "#888888", lw=0.8, alpha=0.6)
    ax.add_patch(FancyBboxPatch((3.2, -2.9), 7.6, 1.3, boxstyle="round,pad=0.1", fc="#f2f2f2", ec="#555555"))
    ax.text(7.0, -2.25, "小さなネットワーク → 候補の点数", ha="center", va="center", fontsize=11.5)
    save(fig, ax, [H_P, Patch(fc=W_COL, alpha=0.8, label="候補 q"),
                   Patch(fc=NB_COL, alpha=0.4, ec=NB_COL, label="周り3×3"),
                   Line2D([], [], color="#888888", lw=1, label="3×3どうしの類似度")], "01c-surroundings.png")


def main():
    similarity()
    constraint()
    surroundings()

if __name__ == "__main__":
    main()
