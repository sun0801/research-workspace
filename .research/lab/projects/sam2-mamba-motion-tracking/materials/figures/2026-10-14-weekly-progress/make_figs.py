"""10/14 週次MTG資料の図。値は experiments/ の記録値を手入力している。

python3 make_figs.py <出力dir>
"""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.family"] = "Noto Sans CJK JP"

INK = "#0b0b0b"
SUB = "#52514e"
MUTED = "#8a8984"
GRID = "#e4e3df"
SURFACE = "#fcfcfb"
PAPER = "#2a78d6"  # 論文 test
OURS_TEST = "#eb6834"  # 本再現 test
OURS_VAL = "#1baf7a"  # 本再現 val（参考）

STAGES = ["S1\nbaseline", "S2\n+ Add", "S3\n+ CoI", "S4\n+ Q-R"]
# experiments/2026-10-09-sam2mot-test-runs.md（S1 は 2026-10-13 追記）
PAPER_TEST = [62.9, 67.9, 73.8, 75.5]
OURS_TEST_V = [63.3, 65.6, 69.2, 70.6]
# experiments/2026-10-13-sam2mot-o365tococo-val.md（3x_coco の行）
OURS_VAL_V = [59.21, 64.32, 68.22, 69.25]


def fig_test_gap(out: Path):
    fig, ax = plt.subplots(figsize=(8.6, 5.2), dpi=200)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)
    x = list(range(len(STAGES)))

    ax.plot(x, OURS_VAL_V, color=OURS_VAL, lw=2, ls=(0, (4, 3)), marker="o", ms=7,
            mec=SURFACE, mew=2, zorder=2, label="本再現 val（参考、別split）")
    ax.plot(x, PAPER_TEST, color=PAPER, lw=2, marker="o", ms=8, mec=SURFACE, mew=2,
            zorder=3, label="論文 test")
    ax.plot(x, OURS_TEST_V, color=OURS_TEST, lw=2, marker="o", ms=8, mec=SURFACE, mew=2,
            zorder=3, label="本再現 test（CodaBench）")

    for i in x:
        p, o = PAPER_TEST[i], OURS_TEST_V[i]
        ax.plot([i + 0.12] * 2, [min(p, o), max(p, o)], color=MUTED, lw=1, zorder=1)
        d = o - p
        ax.text(i + 0.18, (p + o) / 2, f"{d:+.1f}".replace("-", "−"), va="center", ha="left",
                fontsize=11, color=INK, weight="bold", zorder=4,
                bbox=dict(boxstyle="round,pad=0.15", fc=SURFACE, ec="none"))

    ax.set_xticks(x)
    ax.set_xticklabels(STAGES, fontsize=10, color=INK)
    ax.set_xlim(-0.45, 3.6)
    ax.set_ylim(57, 77.5)
    ax.set_ylabel("HOTA", fontsize=10, color=SUB)
    ax.tick_params(axis="y", labelsize=9, colors=SUB)
    ax.tick_params(axis="x", length=0)
    ax.grid(axis="y", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    for s in ["top", "right", "left"]:
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(MUTED)

    fig.text(0.075, 0.955, "SAM2MOT再現：baselineは論文と一致し、差はAddとCoIで開く",
             fontsize=13.5, weight="bold", color=INK, ha="left", va="top")
    fig.text(0.075, 0.895,
             "DanceTrack test（35系列）の段別HOTA。数字は 本再現 test − 論文 test（HOTA）。検出器は3x_coco、S4はQ-R補正方式",
             fontsize=9, color=SUB, ha="left", va="top")
    h, l = ax.get_legend_handles_labels()
    order = [1, 2, 0]
    ax.legend([h[k] for k in order], [l[k] for k in order], loc="lower right", fontsize=9,
              frameon=False, labelcolor=INK)
    fig.text(0.075, 0.02,
             "source: experiments/2026-10-09-sam2mot-test-runs.md（S1は10/13追記）、"
             "experiments/2026-10-13-sam2mot-o365tococo-val.md。論文値は SAM2MOT Table 3",
             fontsize=7.5, color=MUTED, ha="left", va="bottom")
    fig.subplots_adjust(left=0.075, right=0.97, top=0.84, bottom=0.17)
    fig.savefig(out / "01-sam2mot-test-gap-by-stage.png", facecolor=SURFACE)
    plt.close(fig)


if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent
    out.mkdir(parents=True, exist_ok=True)
    fig_test_gap(out)
