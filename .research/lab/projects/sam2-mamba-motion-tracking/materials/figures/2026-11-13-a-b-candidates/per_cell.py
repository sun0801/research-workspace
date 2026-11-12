"""Concept figure for the 11/13 MTG: per-cell Mamba (current) vs one sequence of all cells (explanatory, not data).

The 64x64 map is drawn as 4x4.
  python per_cell.py   # writes 00-per-cell-vs-one-sequence.png
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.patches import FancyArrowPatch, Patch, Rectangle

rcParams["font.family"] = "Noto Sans CJK JP"
HERE = Path(__file__).resolve().parent
N = 4
CELL_COL, STATE_COL, GRID = "#cde2fb", "#eb6834", "#7a7a7a"


def fmap(ax, x0, y0, label):
    for r in range(N):
        for c in range(N):
            ax.add_patch(Rectangle((x0 + c, y0 + r), 1, 1, fc=CELL_COL, ec=GRID, lw=0.8))
    ax.text(x0 + N / 2, y0 + N + 0.3, label, ha="center", va="bottom", fontsize=12)


def arrow(ax, a, b, color="#555555", lw=1.2, rad=0.0):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=10, color=color, lw=lw,
                                 connectionstyle=f"arc3,rad={rad}", shrinkA=2, shrinkB=2))


def main():
    fig, axes = plt.subplots(1, 2, figsize=(15, 5.6))

    ax = axes[0]
    ax.set_title("マスごと（今のV3）", fontsize=14, pad=10)
    fmap(ax, 0, 0, "フレーム t−1"); fmap(ax, 7, 0, "フレーム t")
    for r in range(N):
        for c in range(N):
            ax.add_patch(Rectangle((c + 0.3, r + 0.3), 0.4, 0.4, fc=STATE_COL, alpha=0.9))
            ax.add_patch(Rectangle((7 + c + 0.3, r + 0.3), 0.4, 0.4, fc=STATE_COL, alpha=0.9))
    for r in range(N):
        arrow(ax, (N - 0.3, r + 0.5), (7 + 0.3, r + 0.5), color=STATE_COL, lw=1.0)

    ax = axes[1]
    ax.set_title("全マスを1本の系列にする（試していない）", fontsize=14, pad=10)
    fmap(ax, 0, 0, "フレーム t−1"); fmap(ax, 7, 0, "フレーム t")
    order = [(r, c if r % 2 == 0 else N - 1 - c) for r in range(N - 1, -1, -1) for c in range(N)]
    for x0 in (0, 7):
        pts = [(x0 + c + 0.5, r + 0.5) for r, c in order]
        for a, b in zip(pts[:-1], pts[1:]):
            arrow(ax, a, b, color="#2a78d6", lw=1.0)
    ax.add_patch(Rectangle((5.25, 1.6), 0.5, 0.8, fc=STATE_COL, alpha=0.9))
    (lr, lc), (fr, fc) = order[-1], order[0]
    arrow(ax, (lc + 0.5, lr + 0.5), (5.25, 2.0), color=STATE_COL, lw=1.4, rad=0.3)
    arrow(ax, (5.75, 2.0), (7 + fc + 0.5, fr + 0.5), color=STATE_COL, lw=1.4, rad=-0.3)

    for ax in axes:
        ax.set_xlim(-0.5, 11.5); ax.set_ylim(-0.6, 5.2); ax.set_aspect("equal"); ax.axis("off")
    fig.legend(handles=[Patch(fc=CELL_COL, ec=GRID, label="特徴のマス（実際は64×64）"),
                        Patch(fc=STATE_COL, label="Mamba の state（1つあたり10,240個の値）"),
                        Patch(fc="#2a78d6", label="読む順")],
               loc="lower center", ncol=3, fontsize=11.5, frameon=False)
    fig.subplots_adjust(left=0.01, right=0.99, top=0.9, bottom=0.12, wspace=0.08)
    fig.savefig(HERE / "00-per-cell-vs-one-sequence.png", dpi=110)


if __name__ == "__main__":
    main()
