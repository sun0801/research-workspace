"""Conceptual figures: temporal Mamba integration variants V1-V4 (brainstorm 2026-10-13/14)."""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, FancyArrowPatch, Circle

plt.rcParams["font.family"] = "Noto Sans CJK JP"
OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)

INK = "#1f2937"
MUTED = "#6b7280"
GRID = "#9ca3af"
LINE = "#d1d5db"
BLUE = "#2563eb"
BLUE_L = "#dbeafe"
ORANGE = "#ea580c"
ORANGE_L = "#ffedd5"
GREEN = "#059669"
GREEN_L = "#d1fae5"
GREY_L = "#f3f4f6"
RED = "#dc2626"
RED_L = "#fee2e2"
PURPLE = "#7c3aed"
PURPLE_L = "#ede9fe"
TEAL = "#0e7490"
TEAL_L = "#cffafe"


def new_fig(w=13.33, h=7.5):
    fig = plt.figure(figsize=(w, h), dpi=200)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.axis("off")
    fig.patch.set_facecolor("white")
    return fig, ax


def box(ax, x, y, w, h, text, fc=GREY_L, ec=INK, fs=11, lw=1.2, ls="-", color=INK, weight="normal"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08",
                                fc=fc, ec=ec, lw=lw, ls=ls))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, color=color,
            weight=weight, linespacing=1.3)


def arrow(ax, x0, y0, x1, y1, color=INK, lw=1.4, ls="-", style="-|>", ms=12, rad=0.0):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle=style, mutation_scale=ms,
                                 color=color, lw=lw, ls=ls,
                                 connectionstyle=f"arc3,rad={rad}", shrinkA=0, shrinkB=0))


def grid(ax, x, y, size, n, ec=GRID, lw=0.6, fc="white", fill=None):
    c = size / n
    for i in range(n):
        for j in range(n):
            f = fill(i, j) if fill else fc
            ax.add_patch(Rectangle((x + j * c, y + (n - 1 - i) * c), c, c, fc=f, ec=ec, lw=lw))
    return c


def cell_center(x, y, size, n, i, j):
    c = size / n
    return x + (j + 0.5) * c, y + (n - 1 - i + 0.5) * c


def snake(x, y, size, n):
    pts = []
    for i in range(n):
        js = range(n) if i % 2 == 0 else range(n - 1, -1, -1)
        for j in js:
            pts.append(cell_center(x, y, size, n, i, j))
    return pts


# ---------------------------------------------------------------- Fig 1
def fig1():
    fig, ax = new_fig(13.33, 8.4)
    ax.text(0.35, 8.08, "temporal Mamba 統合方法の候補 V1〜V4（本命：V2・V3・V4／対照：V1）", fontsize=19, weight="bold", color=INK)
    ax.text(0.35, 7.74, "共通：挿入位置は現行の b（対象別 pix_feat。V3は高解像度特徴も含む）。Mambaへの渡し方だけを変える。"
            "出力は pix_feat + α・残差。　※64×64のマス目を4×4で模式化",
            fontsize=10.5, color=MUTED)

    pw = 3.1
    xs = [0.3 + i * 3.2 for i in range(4)]
    PWD = 2.55
    DX = (pw - PWD) / 2
    titles = ["V1  1 token", "V2  縮約グリッド", "V3  FPN的（各段Mamba）", "V4  時空間scan"]
    olds = ["10/9図の①（現行・LR修正版）", "10/9図の④（64×64にすると②）", "10/9図の⑤", "10/9図の③"]
    roles = ["対照", "空間を粗く残す", "9/30の提案（解釈案）", "Vision Mamba標準の型"]
    colors = [ORANGE, GREEN, PURPLE, TEAL]
    rows = [
        ("Mambaに入るもの", ["空間平均した1ベクトル", "縮めた各マス\n（16×16〜64×64で振る）",
                          "64・128・256の各段の全マス\n（サイズを削らない）", "フレーム内の全マスを\n1列に並べたもの"]),
        ("stateの持ち方", ["対象ごとに1本", "マスごとに1本\n（16×16なら256本）", "段ごと・マスごと\n（つなぎ方次第で対象別）",
                        "フレーム末のstateを\n次フレームへ渡す"]),
        ("残る空間情報", ["なし", "粗い位置（64×64なら全位置）", "すべて（粗い〜細かい）", "すべて（隣とも混ざる）"]),
        ("根拠・先行例", ["現行実装", "マスをbatch次元に畳むだけで書ける\n64×64＝全位置案（10/9図の②）も含む",
                       "9/30「FPNなどの工夫で\nサイズを削らずに」", "Vim / VMamba / VideoMamba\n9/30「一括で入れる」の解釈の一つ"]),
        ("未確定・リスク", ["マスク形状に効きにくい", "粗いと細部を扱えない\n細かいと物の移動でstateがずれる",
                         "重い（256段で約6.5万本）\n段のつなぎ方が未確定", "ストリーミングでの\nstate受け渡し・VRAM"]),
    ]

    top = 7.15
    for k in range(4):
        x = xs[k]
        ax.add_patch(FancyBboxPatch((x, 0.35), pw, 6.95, boxstyle="round,pad=0.02,rounding_size=0.08",
                                    fc="white", ec=LINE, lw=1.0))
        ax.add_patch(Rectangle((x + 0.02, 7.24), pw - 0.04, 0.06, fc=colors[k], ec="none"))
        ax.text(x + pw / 2, top - 0.05, titles[k], ha="center", va="top", fontsize=12.5, weight="bold", color=INK)
        ax.text(x + pw / 2, 6.68, olds[k], ha="center", va="top", fontsize=8.3, color=MUTED)
        ax.text(x + pw / 2, 6.42, roles[k], ha="center", va="top", fontsize=9.2, color=colors[k], weight="bold")
        badge, bfc, btc = [("対照", GREY_L, INK), ("本命", colors[1], "white"), ("本命", colors[2], "white"),
                           ("本命", colors[3], "white")][k]
        bw = 0.42 if len(badge) == 2 else 0.8
        ax.add_patch(FancyBboxPatch((x + pw - bw - 0.1, 7.33), bw, 0.22,
                                    boxstyle="round,pad=0.01,rounding_size=0.06", fc=bfc,
                                    ec=colors[k], lw=1.0))
        ax.text(x + pw - bw / 2 - 0.1, 7.44, badge, ha="center", va="center", fontsize=8.6, color=btc,
                weight="bold")

    gs = 0.8
    gy = 4.75
    # V1 1 token
    x = xs[0] + DX
    gy = gy - 0.25
    for t, gx in enumerate([x + 0.2, x + 1.5]):
        grid(ax, gx, gy + 0.55, gs, 4)
        ax.text(gx + gs / 2, gy + 1.45, ["t−1", "t"][t], ha="center", fontsize=9, color=MUTED)
        arrow(ax, gx + gs / 2, gy + 0.52, gx + gs / 2, gy + 0.2, color=MUTED, ms=8, lw=1)
        ax.text(gx + gs / 2 + 0.33, gy + 0.33, "平均", fontsize=7.5, color=MUTED, ha="center")
        ax.add_patch(Rectangle((gx + gs / 2 - 0.13, gy - 0.12), 0.26, 0.26, fc=ORANGE_L, ec=ORANGE, lw=1.3))
    arrow(ax, x + 0.2 + gs / 2 + 0.15, gy + 0.01, x + 1.5 + gs / 2 - 0.15, gy + 0.01, color=ORANGE, lw=1.8)
    ax.text(x + PWD / 2, gy - 0.17, "1本の時系列\n出力は全マスに同じ値", fontsize=8.5, color=ORANGE, ha="center",
            va="top", linespacing=1.2)

    gy = gy + 0.25
    # V2 coarse grid
    x = xs[1] + DX
    g0, g1 = x + 0.25, x + 1.5
    for t, gx in enumerate([g0, g1]):
        grid(ax, gx, gy, gs, 4, ec=LINE)
        grid(ax, gx, gy, gs, 2, ec=GREEN, lw=1.6, fc=(0, 0, 0, 0))
        ax.text(gx + gs / 2, gy + gs + 0.1, ["t−1", "t"][t], ha="center", fontsize=9, color=MUTED)
    for (i, j) in [(0, 0), (0, 1), (1, 0), (1, 1)]:
        p0 = cell_center(g0, gy, gs, 2, i, j)
        p1 = cell_center(g1, gy, gs, 2, i, j)
        ax.plot([p0[0], p1[0]], [p0[1], p1[1]], color=GREEN, lw=1.4)
        ax.add_patch(Circle(p0, 0.045, color=GREEN))
        ax.add_patch(Circle(p1, 0.045, color=GREEN))
    ax.text(x + PWD / 2, gy - 0.42, "粗いマスごとに時系列\n出力は拡大して足す", fontsize=8.5,
            color=GREEN, ha="center", va="top", linespacing=1.2)

    # V3 FPN-like: Mamba at every level, connected top-down
    x = xs[2] + DX
    gy = gy - 0.12
    lv = [(0.34, 2, gy + 0.98, "64"), (0.5, 4, gy + 0.3, "128"), (0.66, 6, gy - 0.5, "256")]
    gx0 = x + 0.55
    for k, (sz, n, yy, lab) in enumerate(lv):
        grid(ax, gx0 + (0.66 - sz) / 2, yy, sz, n, ec=PURPLE, lw=0.6 if n > 2 else 1.0,
             fc=PURPLE_L if n == 2 else "white")
        mx = gx0 + 0.66 + 0.42
        my = yy + sz / 2
        ax.add_patch(Circle((mx, my), 0.15, fc=PURPLE_L, ec=PURPLE, lw=1.2))
        ax.text(mx, my, "M", ha="center", va="center", fontsize=8, color=PURPLE, weight="bold")
        arrow(ax, gx0 + (0.66 + sz) / 2 + 0.03, my, mx - 0.16, my, color=PURPLE, lw=1.0, ms=7)
        arrow(ax, mx + 0.16, my + 0.04, mx + 0.5, my + 0.04, color=ORANGE, lw=1.3, ms=8)
        ax.text(gx0 - 0.08, my, lab, ha="right", va="center", fontsize=7.8, color=PURPLE)
        if k < 2:
            ny = lv[k + 1][2] + lv[k + 1][0] / 2
            arrow(ax, mx, my - 0.16, mx, ny + 0.16, color=PURPLE, lw=1.3, ms=8)
    ax.text(x + PWD - 0.12, gy + 1.4, "→次フレーム", fontsize=7.3, color=ORANGE, ha="right")
    ax.text(x + PWD / 2, gy - 0.64, "各段でMambaを回し、\n粗い段から細かい段へつなぐ", fontsize=8.5, color=PURPLE,
            ha="center", va="top", linespacing=1.2)
    gy = gy + 0.12

    # V4 spatiotemporal scan
    x = xs[3] + DX
    g0, g1 = x + 0.25, x + 1.5
    for t, gx in enumerate([g0, g1]):
        grid(ax, gx, gy, gs, 4)
        ax.text(gx + gs / 2, gy + gs + 0.1, ["t−1", "t"][t], ha="center", fontsize=9, color=MUTED)
        pts = snake(gx, gy, gs, 4)
        ax.plot([p[0] for p in pts], [p[1] for p in pts], color=TEAL, lw=1.1)
        ax.add_patch(Circle(pts[0], 0.04, color=TEAL))
        if t == 0:
            last = pts[-1]
        else:
            first = pts[0]
    ax.plot([last[0], last[0], g0 + gs + 0.22, g0 + gs + 0.22, first[0] - 0.12],
            [last[1], gy - 0.15, gy - 0.15, first[1], first[1]], color=ORANGE, lw=1.5)
    arrow(ax, first[0] - 0.13, first[1], first[0] - 0.04, first[1], color=ORANGE, lw=1.5, ms=9)
    ax.text(x + PWD / 2, gy - 0.42, "フレーム内を順に読み、\n最後のstateを次フレームへ", fontsize=8.5,
            color=TEAL, ha="center", va="top", linespacing=1.2)

    ry = 3.55
    rh = 0.64
    for r, (label, vals) in enumerate(rows):
        yy = ry - r * rh
        for k in range(4):
            x = xs[k]
            if r > 0:
                ax.plot([x + 0.1, x + pw - 0.1], [yy + 0.07, yy + 0.07], color="#e5e7eb", lw=0.8)
            ax.text(x + 0.12, yy, label, fontsize=7.8, color=MUTED, va="top")
            ax.text(x + 0.12, yy - 0.18, vals[k], fontsize=8.6, color=INK, va="top", linespacing=1.15)

    ax.text(6.67, 0.04, "M = temporal Mamba。VRAM・速度はいずれも未実測（段階1で測る）。"
            "V3・V4が32GBに収まらない場合の代替：V3はつなぎ方(c)か128・256段の共有、V4はチャネル圧縮",
            fontsize=8.5, color=MUTED, ha="center", va="bottom")
    fig.savefig(OUT / "01-variants-v1-v4.png", facecolor="white")
    plt.close(fig)


# ---------------------------------------------------------------- Fig 2
def fig2():
    fig, ax = new_fig()
    ax.text(0.4, 7.05, "V3「FPN的」：FPNの各段でMambaを回し、段どうしをつなぐ（解釈案）", fontsize=18.5,
            weight="bold", color=INK)
    ax.text(0.4, 6.65, "9/30「FPNなどを工夫し、サイズを削減せずに入れる」の解釈。各段の全マスをMambaに入れ、"
            "Mamba同士の関係も学習する。10/16 MTGで意図を確認したい",
            fontsize=10.8, color=MUTED)

    rows = [5.85, 4.6, 3.35]
    h = 0.75
    feats = ["pix_feat  64×64・256ch\n対象別", "feat_s1  128×128・64ch\n全対象で共通",
             "feat_s0  256×256・32ch\n全対象で共通"]
    mambas = ["Mamba（64段）\nマスごとに時系列", "Mamba（128段）\nマスごとに時系列", "Mamba（256段）\nマスごとに時系列"]

    box(ax, 0.3, rows[0] - h / 2, 1.85, h, "Memory Attention\n（対象別メモリ）", fc=BLUE_L, ec=BLUE, fs=9.5)
    box(ax, 0.3, rows[2] - h / 2, 1.85, rows[1] - rows[2] + h, "画像エンコーダ\n（Hiera + FPN）\n全対象で共通", fs=9.8)
    fx, fw = 2.65, 2.3
    mx, mw = 5.65, 2.0
    for i, cy in enumerate(rows):
        box(ax, fx, cy - h / 2, fw, h, feats[i], fc="white", fs=9.3)
        box(ax, mx, cy - h / 2, mw, h, mambas[i], fc=PURPLE_L, ec=PURPLE, fs=9.3)
        arrow(ax, fx + fw, cy, mx, cy, color=PURPLE)
        arrow(ax, 2.15 if i else 2.15, cy, fx, cy)
        # recurrence across frames
        ax.text(mx + mw - 0.08, cy - h / 2 + 0.06, "state → t+1", fontsize=7.6, color=ORANGE, ha="right",
                va="bottom", weight="bold")

    # (a) top-down between Mambas
    for i in range(2):
        y0 = rows[i] - h / 2
        y1 = rows[i + 1] + h / 2
        arrow(ax, mx + 0.35, y0, mx + 0.35, y1 + 0.02, color=PURPLE, lw=1.8, ms=11)
        ax.text(mx + 0.5, (y0 + y1) / 2, "(a) 出力を×2に拡大して入力に足す", fontsize=8.2, color=PURPLE,
                va="center")

    # outputs back as residual -> decoder
    dx = 9.35
    box(ax, dx, rows[2] - h / 2, 1.95, rows[0] - rows[2] + h, "マスクデコーダ\n（そのまま）\n\n各段の特徴\n＋ α・Mamba出力\nを入力に使う",
        fc=GREY_L, fs=9.6)
    for cy in rows:
        arrow(ax, mx + mw, cy, dx, cy, color=PURPLE)
        ax.text((mx + mw + dx) / 2, cy + 0.07, "＋α・残差", fontsize=8.3, color=PURPLE, ha="center", va="bottom")
    box(ax, 11.75, rows[1] - 0.35, 1.25, 0.7, "出力マスク", fc="white", fs=9.8)
    arrow(ax, dx + 1.95, rows[1], 11.75, rows[1])

    # connection options
    ax.text(0.4, 2.55, "段のつなぎ方（Mamba同士の関係をどう学習させるか）", fontsize=11.5, weight="bold", color=INK, va="top")
    opts = [
        ("(a) 出力をつなぐ【基本形】", "粗い段のMamba出力を拡大して、細かい段のMamba入力に足す。\nFPNのtop-down経路と同じ形で、一番素直。",
         PURPLE_L, PURPLE),
        ("(b) stateをつなぐ", "粗い段のstateで、細かい段のstateを初期化・補正する。\n時間の記憶そのものを段の間で共有する。",
         "white", PURPLE),
        ("(c) 後で混ぜる", "各段のMambaは独立に回し、出力を最後に合成する。\n関係を学習するのは合成の層だけ（最も弱い）。",
         "white", GRID),
    ]
    cw = 4.1
    for i, (t, d, fc, ec) in enumerate(opts):
        x = 0.4 + i * (cw + 0.12)
        ax.add_patch(FancyBboxPatch((x, 0.8), cw, 1.2, boxstyle="round,pad=0.02,rounding_size=0.08",
                                    fc=fc, ec=ec, lw=1.3))
        ax.text(x + 0.15, 1.88, t, fontsize=10.2, weight="bold", color=INK, va="top")
        ax.text(x + 0.15, 1.5, d, fontsize=8.8, color=INK, va="top", linespacing=1.4)
    ax.text(0.4, 0.1, "注：128・256段の特徴は全対象で共通なので、単独ならその段のMambaは動画に1本で済む。ただし (a)(b) で対象別の64段からつなぐと、\n"
            "128・256段も対象別になる（重さが対象数に比例）。共有したい場合は (c) にするか、64段にも共通特徴を使う。重さは未実測（256段は約6.5万マス）。",
            fontsize=8.4, color=MUTED, va="bottom", linespacing=1.4)
    fig.savefig(OUT / "02-v3-fpn-detail.png", facecolor="white")
    plt.close(fig)


# ---------------------------------------------------------------- Fig 3
def fig3():
    fig, ax = new_fig()
    ax.text(0.4, 7.05, "V4 時空間scan：Vision Mambaの標準形を、ストリーミング追跡に使う", fontsize=19,
            weight="bold", color=INK)
    ax.text(0.4, 6.65, "フレーム内のscanは Vim / VMamba と同じ。違いは「フレーム間でstateを持ち越し続ける」点",
            fontsize=11.5, color=MUTED)

    gs = 1.0
    # panel A: VideoMamba-like
    ax.add_patch(FancyBboxPatch((0.35, 3.55), 6.15, 2.85, boxstyle="round,pad=0.02,rounding_size=0.08",
                                fc="white", ec=LINE))
    ax.text(0.55, 6.2, "先行例（VideoMamba など）", fontsize=11.5, weight="bold", color=INK, va="top")
    ax.text(0.55, 5.85, "短いclipの全tokenをまとめて1本の列として処理（オフライン）", fontsize=9, color=MUTED, va="top")
    xs = [0.75, 2.15, 3.55]
    for k, gx in enumerate(xs):
        grid(ax, gx, 3.95, gs, 4)
        ax.text(gx + gs / 2, 5.05, f"frame {k+1}", ha="center", fontsize=8.5, color=MUTED)
    ax.add_patch(FancyBboxPatch((0.62, 3.82), 4.06, 1.35, boxstyle="round,pad=0.02,rounding_size=0.06",
                                fc="none", ec=GRID, ls="--"))
    ax.text(4.95, 4.55, "clip全体を\n一度に読む\n（双方向も可）", fontsize=8.8, color=INK, va="center", linespacing=1.2)

    # panel B: ours streaming
    ax.add_patch(FancyBboxPatch((6.8, 3.55), 6.15, 2.85, boxstyle="round,pad=0.02,rounding_size=0.08",
                                fc="white", ec=TEAL, lw=1.4))
    ax.text(7.0, 6.2, "今回（V4）", fontsize=11.5, weight="bold", color=TEAL, va="top")
    ax.text(7.0, 5.85, "1フレームずつ処理し、フレーム末のstateを次へ渡す（最長500フレーム）", fontsize=9,
            color=MUTED, va="top")
    xs = [7.2, 8.75, 10.3]
    prev_last = None
    for k, gx in enumerate(xs):
        grid(ax, gx, 3.95, gs, 4)
        ax.text(gx + gs / 2, 5.05, ["t−1", "t", "t+1"][k], ha="center", fontsize=8.5, color=MUTED)
        pts = snake(gx, 3.95, gs, 4)
        ax.plot([p[0] for p in pts], [p[1] for p in pts], color=TEAL, lw=1.0)
        if prev_last is not None:
            mid = gx - 0.27
            ax.plot([prev_last[0], prev_last[0], mid, mid, gx - 0.12],
                    [prev_last[1], 3.82, 3.82, pts[0][1], pts[0][1]], color=ORANGE, lw=1.5)
            arrow(ax, gx - 0.13, pts[0][1], pts[0][0] - 0.03, pts[0][1], color=ORANGE, lw=1.5, ms=9)
        prev_last = pts[-1]
    ax.text(11.5, 4.45, "…", fontsize=16, color=MUTED, va="center")
    ax.text(12.0, 4.45, "state\n持ち越し", fontsize=8.5, color=ORANGE, va="center", linespacing=1.15)

    # bottom: control
    ax.text(0.45, 3.1, "比較のしかた（state carry と reset）", fontsize=12, weight="bold", color=INK, va="top")
    rows = [
        ("V4（carry）", "フレーム内scan ＋ フレーム間のstate持ち越し", TEAL_L, TEAL),
        ("V4-reset", "毎フレームstateを0から開始 ＝ ほぼ VMamba型のフレーム内処理だけ", GREY_L, GRID),
    ]
    for i, (name, desc, fc, ec) in enumerate(rows):
        yy = 2.2 - i * 0.75
        box(ax, 0.5, yy, 1.7, 0.55, name, fc=fc, ec=ec, fs=10, weight="bold")
        ax.text(2.4, yy + 0.27, desc, fontsize=10, color=INK, va="center")
    ax.text(0.5, 0.75, "→ 差が出れば「時間の記憶」が効いている。差がなければ効いているのはフレーム内の空間処理。",
            fontsize=10.2, color=INK, weight="bold")

    ax.text(8.6, 3.1, "要確認", fontsize=12, weight="bold", color=RED, va="top")
    todo = ["・学習時に初期stateを渡せるか：mamba-ssm 2.2.2の\n  Mamba2 chunk scanで可能なはず（未確認）",
            "・VRAM：1区間 = 8フレーム × 4096 token。段階1で実測",
            "・走査方向：1方向から始め、4方向（VMamba型）は後で"]
    for i, s in enumerate(todo):
        ax.text(8.6, [2.65, 2.0, 1.6][i], s, fontsize=9.3, color=INK, va="top", linespacing=1.3)
    fig.savefig(OUT / "03-v4-streaming-scan.png", facecolor="white")
    plt.close(fig)


# ---------------------------------------------------------------- Fig 4
def fig4():
    fig, ax = new_fig()
    ax.text(0.4, 7.05, "進め方：いきなり本学習で並べず、4段階で絞る", fontsize=19, weight="bold", color=INK)
    ax.text(0.4, 6.65, "本学習は1案あたり学習だけで約18時間（前回のF0の速度からの概算）＋ tuning評価1回約71分。GPU 2枚はSAM2MOTと共有",
            fontsize=11, color=MUTED)

    stages = [
        ("0. LR修正の確認", "V1のまま\nadapterのLRを本体と分離\n（例 1e-4前後・warmup）\n初期化の見直し",
         "αと残差が育つか\n育たなければ先へ進まない", ORANGE_L, ORANGE),
        ("1. 共通化＋コスト実測", "V1〜V4を同じ枠に入れ\ntoken化部分だけ差し替え\n最長500フレームで\nVRAM・速度を測る",
         "32GBに収まるか\n（9/30の宿題への答え）", GREEN_L, GREEN),
        ("2. スクリーニング", "SAM2本体はF0で固定\nadapterだけ短く学習\ntuningの固定サブセット\nで比較",
         "F0との差\ncarry と reset の差", PURPLE_L, PURPLE),
        ("3. 本学習", "上位1〜2案だけ\n現行の手順で学習",
         "既存のbootstrap判定\nlockboxは最後だけ", BLUE_L, BLUE),
    ]
    w, gap = 2.95, 0.22
    for i, (title, body, judge, fc, ec) in enumerate(stages):
        x = 0.4 + i * (w + gap)
        ax.add_patch(FancyBboxPatch((x, 2.75), w, 3.5, boxstyle="round,pad=0.02,rounding_size=0.08",
                                    fc="white", ec=ec, lw=1.5))
        ax.add_patch(FancyBboxPatch((x, 5.6), w, 0.65, boxstyle="round,pad=0.02,rounding_size=0.08",
                                    fc=fc, ec=ec, lw=1.5))
        ax.text(x + w / 2, 5.92, title, ha="center", va="center", fontsize=12, weight="bold", color=INK)
        ax.text(x + w / 2, 5.35, body, ha="center", va="top", fontsize=9.8, color=INK, linespacing=1.35)
        ax.plot([x + 0.15, x + w - 0.15], [3.85, 3.85], color="#e5e7eb", lw=0.9)
        ax.text(x + 0.18, 3.75, "判定", fontsize=8.5, color=MUTED, va="top")
        ax.text(x + w / 2, 3.5, judge, ha="center", va="top", fontsize=9.5, color=ec, weight="bold",
                linespacing=1.3)
        if i < 3:
            arrow(ax, x + w + 0.02, 4.5, x + w + gap - 0.02, 4.5, ms=10)

    ax.text(0.45, 2.3, "各案に付ける比較条件", fontsize=12, weight="bold", color=INK, va="top")
    ctrl = [("F0", "adapterなし", GREY_L, GRID), ("V○（carry）", "フレーム間でstateを持ち越す", PURPLE_L, PURPLE),
            ("V○-reset", "同じ重みで毎フレームstateを0に", GREY_L, GRID)]
    for i, (n, d, fc, ec) in enumerate(ctrl):
        yy = 1.6 - i * 0.55
        box(ax, 0.5, yy, 1.55, 0.42, n, fc=fc, ec=ec, fs=9.5, weight="bold")
        ax.text(2.2, yy + 0.21, d, fontsize=9.6, color=INK, va="center")

    ax.text(6.1, 2.3, "読み方", fontsize=12, weight="bold", color=INK, va="top")
    reads = ["・carry > reset > F0：時間の記憶が効いている（研究の主張につながる）",
             "・carry ≈ reset > F0：効いているのは追加パラメータ・空間処理",
             "・どれも ≈ F0：その表現では効果なし（LR不足でないことは段階0で確認済みの前提）"]
    for i, s in enumerate(reads):
        ax.text(6.1, 1.85 - i * 0.42, s, fontsize=9.6, color=INK, va="top")
    ax.text(13.0, 0.15, "注：SAM2固定のスクリーニングは「F0に足した価値」を測るもの。本体と同時に学習したときの順位とは変わりうる。",
            fontsize=8.3, color=MUTED, ha="right", va="bottom")
    fig.savefig(OUT / "04-screening-plan.png", facecolor="white")
    plt.close(fig)


fig1()
fig2()
fig3()
fig4()
print("done")
