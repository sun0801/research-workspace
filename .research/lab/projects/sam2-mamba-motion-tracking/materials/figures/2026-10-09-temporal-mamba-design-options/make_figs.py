"""Conceptual figures: temporal Mamba insertion candidates (image side) for 2026-10-09 MTG."""
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
BLUE = "#2563eb"
BLUE_L = "#dbeafe"
ORANGE = "#ea580c"
ORANGE_L = "#ffedd5"
GREEN = "#059669"
GREEN_L = "#d1fae5"
GREY_L = "#f3f4f6"
RED = "#dc2626"
PURPLE = "#7c3aed"


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


# ---------------------------------------------------------------- Fig 1
def fig1():
    fig, ax = new_fig()
    ax.text(0.4, 7.05, "temporal Mambaをどこに入れるか（軸1：位置）", fontsize=20, weight="bold", color=INK)
    ax.text(0.4, 6.65, "前提：promptやtokenと混ざる前の「視覚特徴」に時間情報を入れる（画像側）",
            fontsize=12.5, color=MUTED)
    ax.text(12.95, 6.65, "a・b が設計意図に合う候補（橙）", fontsize=11, color=ORANGE, ha="right", weight="bold")

    y, h = 3.9, 1.0
    cy = y + h / 2
    box(ax, 0.3, y, 1.1, h, "フレーム t\n(1024×1024)", fc="white", fs=10)
    arrow(ax, 1.4, cy, 1.75, cy)
    box(ax, 1.75, y, 1.5, h, "画像エンコーダ\n(Hiera + FPN)", fs=10.5)
    arrow(ax, 3.25, cy, 4.25, cy)
    box(ax, 4.25, y, 1.5, h, "Memory\nAttention", fs=10.5)
    box(ax, 4.0, 5.45, 2.0, 0.75, "対象別メモリ\n(過去7フレーム + obj_ptr)", fc=BLUE_L, ec=BLUE, fs=9.5)
    arrow(ax, 5.0, 5.45, 5.0, y + h, color=BLUE)
    arrow(ax, 5.75, cy, 6.85, cy)

    ax.add_patch(FancyBboxPatch((6.85, 3.55), 3.95, 1.75, boxstyle="round,pad=0.02,rounding_size=0.1",
                                fc="white", ec=INK, lw=1.4))
    ax.text(8.825, 5.08, "マスクデコーダ", ha="center", fontsize=12, weight="bold", color=INK)
    box(ax, 7.0, 3.72, 1.7, 1.05, "Two-Way\nTransformer\n(画像 ⇄ token)", fs=9.5)
    arrow(ax, 8.7, 4.245, 8.95, 4.245)
    box(ax, 8.95, 3.72, 1.7, 1.05, "拡大 64→256\n(高解像度特徴\nを加算)", fs=9.5)
    box(ax, 7.0, 2.65, 1.7, 0.55, "prompt / 出力token", fc=GREY_L, fs=9)
    arrow(ax, 7.85, 3.2, 7.85, 3.72, color=MUTED)
    arrow(ax, 10.8, cy, 11.3, cy)
    box(ax, 11.3, y, 1.0, h, "マスク", fc="white")

    # high-res skip (routed below)
    xs_, xe = 2.5, 9.8
    ax.plot([xs_, xs_, xe], [y, 2.3, 2.3], color=MUTED, lw=1.0, ls=(0, (3, 3)))
    arrow(ax, xe, 2.3, xe, 3.72, color=MUTED, lw=1.0, ls=(0, (3, 3)), ms=10)
    ax.text(6.15, 2.08, "高解像度特徴（128×128, 256×256）", fontsize=9, color=MUTED, ha="center", va="top")
    # memory write back
    ax.add_patch(FancyArrowPatch((11.8, 4.9), (6.0, 5.95), arrowstyle="-|>", mutation_scale=10,
                                 color=BLUE, lw=1.0, ls=(0, (3, 3)), connectionstyle="arc3,rad=0.25"))
    ax.text(9.8, 6.3, "メモリに保存 → 次フレームへ", fontsize=9, color=BLUE, ha="center")

    def marker(x, y0, label, color, fc, filled=True):
        ax.add_patch(Circle((x, y0), 0.26, fc=fc, ec=color, lw=2.0, ls="-" if filled else "--", zorder=5))
        ax.text(x, y0, label, ha="center", va="center", fontsize=13, weight="bold", color=color, zorder=6)

    marker(3.75, cy, "a", ORANGE, ORANGE_L, filled=False)
    ax.text(3.75, 3.75, "共有\nimage embedding\n64×64×256", ha="center", va="top", fontsize=8.8,
            color=ORANGE, linespacing=1.2)
    marker(6.3, cy, "b", ORANGE, ORANGE_L)
    ax.text(6.3, 3.75, "対象別\npix_feat\n64×64×256", ha="center", va="top", fontsize=8.8,
            color=ORANGE, linespacing=1.2)
    marker(7.85, 5.02, "c", MUTED, "white", filled=False)
    marker(9.8, 5.02, "d", MUTED, "white", filled=False)

    yy = 0.2
    cards = [
        ("a", "共有 image embedding\n（Memory Attentionの前）",
         "・全対象で共通の特徴\n・stateは動画に1つ\n・対象の誤対応の影響を受けにくい", ORANGE, ORANGE_L),
        ("b", "対象別 pix_feat（デコーダ入口）\n【現行の位置】",
         "・対象別メモリが混ざった特徴\n・stateは対象ごと\n・誤対応するとstateも汚れうる", ORANGE, ORANGE_L),
        ("c", "Transformer内部の画像特徴\n",
         "・tokenと混ざった後\n・「混ざる前に入れる」という\n  設計意図から外れる", MUTED, "white"),
        ("d", "拡大途中の高解像度特徴\n",
         "・輪郭を作る段階\n・位置数が16〜65倍で重い\n・境界の安定化に用途が限られる", MUTED, "white"),
    ]
    for k, (lab, title, body, col, fc) in enumerate(cards):
        x = 0.3 + k * 3.2
        ax.add_patch(FancyBboxPatch((x, yy), 3.0, 1.5, boxstyle="round,pad=0.02,rounding_size=0.08",
                                    fc=fc, ec=col, lw=1.2))
        ax.text(x + 0.12, yy + 1.38, f"{lab}. {title}", fontsize=9.8, weight="bold", color=INK, va="top",
                linespacing=1.25)
        ax.text(x + 0.12, yy + 0.8, body, fontsize=9.2, color=INK, va="top", linespacing=1.35)
    fig.savefig(OUT / "01-insertion-positions.png", facecolor="white")
    plt.close(fig)


# ---------------------------------------------------------------- Fig 2
def fig2():
    fig, ax = new_fig(13.33, 8.2)
    ax.text(0.35, 7.8, "Mambaへの渡し方（軸2：表現）  ※64×64のマス目を4×4で模式化", fontsize=19,
            weight="bold", color=INK)

    pw = 2.55
    xs = [0.3 + i * 2.6 for i in range(5)]
    titles = ["① 1 token（現行）", "② 全位置・\n位置ごとに時間scan", "③ 時空間scan",
              "④ 縮約グリッド", "⑤ 多スケール（FPN的）"]
    tags = ["9/30：先生が疑問を出した\n「次元を落とした」状態", "9/30「一括で入れる」\nの解釈その1",
            "9/30「一括で入れる」\nの解釈その2", "9/30には未登場の中間案\n「落とすが位置は残す」",
            "9/30「FPNなどの工夫で\nサイズを削らずに」"]
    tagc = [MUTED, BLUE, BLUE, GREEN, PURPLE]
    rows = [
        ("残る空間情報", ["なし（全体の雰囲気のみ）", "すべて（隣とは混ざらない）", "すべて（隣とも混ざる）",
                      "粗い位置（16×16など）", "粗い〜細かいを併用"]),
        ("state / 対象（概算）", ["約8K値（≈32KB）", "約3,400万値（≈134MB）", "小（scan方向数×8K値）",
                            "16×16:≈8MB / 8×8:≈2MB", "使う段の合計"]),
        ("計算", ["ほぼゼロ", "並列に1歩ずつ：中", "1フレーム4096歩：重い", "軽い", "段次第：中〜重"]),
        ("強み", ["動作確認・一致確認に最適", "サイズを削らない素直な案", "表現力が最も高い",
                "ずれを吸収、比較しやすい", "先生の発想に最も近い"]),
        ("弱み", ["マスク形状には効きにくい", "物が動くとメモがずれる", "説明しにくい・実装が重い",
                "細部はMamba側で扱えない", "設計自由度が高く比較条件が増える"]),
    ]

    top = 7.05
    for k in range(5):
        x = xs[k]
        ax.add_patch(FancyBboxPatch((x, 0.25), pw, 6.95, boxstyle="round,pad=0.02,rounding_size=0.08",
                                    fc="white", ec="#d1d5db", lw=1.0))
        ax.text(x + pw / 2, top, titles[k], ha="center", va="top", fontsize=12, weight="bold", color=INK,
                linespacing=1.2)
        ax.text(x + pw / 2, 6.35, tags[k], ha="center", va="top", fontsize=8.6, color=tagc[k],
                linespacing=1.25)

    # ---- diagrams (region y 3.55 - 5.6)
    gs = 0.8   # grid size
    gy = 4.35
    # ① 1 token
    x = xs[0]
    for t, gx in enumerate([x + 0.2, x + 1.5]):
        grid(ax, gx, gy + 0.55, gs, 4)
        ax.text(gx + gs / 2, gy + 1.45, ["t−1", "t"][t], ha="center", fontsize=9, color=MUTED)
        arrow(ax, gx + gs / 2, gy + 0.52, gx + gs / 2, gy + 0.2, color=MUTED, ms=8, lw=1)
        ax.text(gx + gs / 2 + 0.33, gy + 0.33, "平均", fontsize=7.5, color=MUTED, ha="center")
        ax.add_patch(Rectangle((gx + gs / 2 - 0.13, gy - 0.12), 0.26, 0.26, fc=ORANGE_L, ec=ORANGE, lw=1.3))
    arrow(ax, x + 0.2 + gs / 2 + 0.15, gy + 0.01, x + 1.5 + gs / 2 - 0.15, gy + 0.01, color=ORANGE, lw=1.8)
    ax.text(x + 1.25, gy - 0.35, "1本の時系列", fontsize=8.5, color=ORANGE, ha="center")
    ax.text(x + pw / 2, gy - 0.7, "出力は全マスに同じ値を足す", fontsize=8.5, color=MUTED, ha="center")

    # ② per-position
    x = xs[1]
    g0, g1 = x + 0.25, x + 1.5
    for t, gx in enumerate([g0, g1]):
        grid(ax, gx, gy, gs, 4)
        ax.text(gx + gs / 2, gy + gs + 0.1, ["t−1", "t"][t], ha="center", fontsize=9, color=MUTED)
    for (i, j) in [(0, 0), (1, 2), (2, 1), (3, 3), (0, 3), (2, 3), (3, 0), (1, 0)]:
        p0 = cell_center(g0, gy, gs, 4, i, j)
        p1 = cell_center(g1, gy, gs, 4, i, j)
        ax.plot([p0[0], p1[0]], [p0[1], p1[1]], color=BLUE, lw=0.9, alpha=0.8)
        ax.add_patch(Circle(p0, 0.03, color=BLUE))
        ax.add_patch(Circle(p1, 0.03, color=BLUE))
    ax.text(x + pw / 2, gy - 0.35, "各マスが自分専用のstate\n（4096本を並列に）", fontsize=8.5, color=BLUE,
            ha="center", va="top", linespacing=1.2)

    # ③ spatiotemporal scan
    x = xs[2]
    g0, g1 = x + 0.25, x + 1.5
    for t, gx in enumerate([g0, g1]):
        grid(ax, gx, gy, gs, 4)
        ax.text(gx + gs / 2, gy + gs + 0.1, ["t−1", "t"][t], ha="center", fontsize=9, color=MUTED)
        pts = []
        for i in range(4):
            js = range(4) if i % 2 == 0 else range(3, -1, -1)
            for j in js:
                pts.append(cell_center(gx, gy, gs, 4, i, j))
        ax.plot([p[0] for p in pts], [p[1] for p in pts], color=BLUE, lw=1.1)
        ax.add_patch(Circle(pts[0], 0.04, color=BLUE))
        if t == 0:
            last = pts[-1]
        else:
            first = pts[0]
    ax.plot([last[0], last[0], g0 + gs + 0.22, g0 + gs + 0.22, first[0] - 0.12],
            [last[1], gy - 0.15, gy - 0.15, first[1], first[1]], color=ORANGE, lw=1.5)
    arrow(ax, first[0] - 0.13, first[1], first[0] - 0.04, first[1], color=ORANGE, lw=1.5, ms=9)
    ax.text(x + pw / 2, gy - 0.4, "1列に並べて順に読む\n最後のstateを次フレームへ", fontsize=8.5,
            color=BLUE, ha="center", va="top", linespacing=1.2)

    # ④ coarse grid
    x = xs[3]
    g0, g1 = x + 0.25, x + 1.5
    for t, gx in enumerate([g0, g1]):
        grid(ax, gx, gy, gs, 4, ec="#d1d5db")
        grid(ax, gx, gy, gs, 2, ec=GREEN, lw=1.6, fc=(0, 0, 0, 0))
        ax.text(gx + gs / 2, gy + gs + 0.1, ["t−1", "t"][t], ha="center", fontsize=9, color=MUTED)
    for (i, j) in [(0, 0), (0, 1), (1, 0), (1, 1)]:
        p0 = cell_center(g0, gy, gs, 2, i, j)
        p1 = cell_center(g1, gy, gs, 2, i, j)
        ax.plot([p0[0], p1[0]], [p0[1], p1[1]], color=GREEN, lw=1.4)
        ax.add_patch(Circle(p0, 0.045, color=GREEN))
        ax.add_patch(Circle(p1, 0.045, color=GREEN))
    ax.text(x + pw / 2, gy - 0.35, "粗いマスごとにstate\n出力は拡大して足す", fontsize=8.5,
            color=GREEN, ha="center", va="top", linespacing=1.2)

    # ⑤ multi-scale
    x = xs[4]
    g0, g1 = x + 0.25, x + 1.5
    small = 0.55
    for t, gx in enumerate([g0, g1]):
        grid(ax, gx + 0.12, gy + 0.62, small, 2, ec=PURPLE, lw=1.2)
        grid(ax, gx, gy - 0.25, gs, 4, ec=PURPLE, lw=0.6)
        ax.text(gx + gs / 2, gy + 1.27, ["t−1", "t"][t], ha="center", fontsize=9, color=MUTED)
    arrow(ax, g0 + 0.12 + small + 0.05, gy + 0.62 + small / 2, g1 + 0.07, gy + 0.62 + small / 2,
          color=PURPLE, lw=1.4, ms=9)
    arrow(ax, g0 + gs + 0.05, gy - 0.25 + gs / 2, g1 - 0.05, gy - 0.25 + gs / 2, color=PURPLE, lw=1.4, ms=9)
    ax.text(x + pw / 2, gy - 0.4, "上段＝粗：だいたいの位置\n下段＝細：形\n→ 組み合わせて足す", fontsize=8.5,
            color=PURPLE, ha="center", va="top", linespacing=1.2)

    # ---- table rows
    ry = 3.05
    rh = 0.55
    for r, (label, vals) in enumerate(rows):
        yy = ry - r * rh
        for k in range(5):
            x = xs[k]
            ax.text(x + 0.12, yy, label, fontsize=7.8, color=MUTED, va="top")
            ax.text(x + 0.12, yy - 0.2, vals[k], fontsize=8.8, color=INK, va="top")
            if r > 0:
                ax.plot([x + 0.1, x + pw - 0.1], [yy + 0.07, yy + 0.07], color="#e5e7eb", lw=0.8)
    ax.text(13.0, 0.05, "数値は SAM2.1 の次元（256ch, 64×64）と Mamba（d_inner 512, d_state 16）からの概算。未実測。",
            fontsize=8, color=MUTED, ha="right", va="bottom")
    fig.savefig(OUT / "02-representation-options.png", facecolor="white")
    plt.close(fig)


# ---------------------------------------------------------------- Fig 3
def fig3():
    fig, ax = new_fig(13.33, 6.9)
    ax.text(0.4, 6.45, "画像側に入れると必ず出る論点：物が動くと「場所のメモ」がずれる", fontsize=19,
            weight="bold", color=INK)
    ax.text(0.4, 6.05, "フレーム t-1 → t で人物が右へ2マス移動した場合。黒枠＝フレーム t の人物、斜線＝過去に書かれたstateの位置",
            fontsize=11, color=MUTED)
    plt.rcParams["hatch.linewidth"] = 1.0
    n = 8
    gs = 2.8
    gy = 1.75
    c = gs / n
    prev = {(i, j) for i in (4, 5, 6) for j in (0, 1)}
    now = {(i, j + 2) for (i, j) in prev}

    def cells(gx, cs, **kw):
        for (i, j) in cs:
            ax.add_patch(Rectangle((gx + j * c, gy + (n - 1 - i) * c), c, c, **kw))

    def person(gx):
        cells(gx, now, fc="none", ec=INK, lw=2.2, zorder=5)

    def memory(gx, cs, col, rgba):
        cells(gx, cs, fc=rgba, ec="none", zorder=2)
        cells(gx, cs, fc="none", ec=col, lw=0, hatch="////", zorder=3)

    panels = [
        ("② 位置ごとにstate", "ずれる", RED,
         "メモは元の場所（左）に残り、\n人物がいる新しい場所には過去の情報がない"),
        ("④ 粗いグリッドでstate", "緩和", GREEN,
         "1マスが広いので、移動前も後も同じ粗マスに収まる\n→ ずれを吸収（ただしMamba側の位置は粗い）"),
        ("動きでメモをずらす（warp）", "補正", PURPLE,
         "予測した移動量でstateを移動してから使う\n→ ずれを直接補正。本来テーマのmotion predictionと接続"),
    ]
    for k, (title, verdict, col, body) in enumerate(panels):
        gx = 0.85 + k * 4.25
        ax.text(gx + gs / 2, 5.1, title, ha="center", fontsize=13.5, weight="bold", color=INK)
        grid(ax, gx, gy, gs, n, ec="#d1d5db")
        if k == 0:
            plt.rcParams["hatch.color"] = RED
            memory(gx, prev, RED, (0.86, 0.15, 0.15, 0.12))
        elif k == 1:
            cg = gs / 2
            ax.add_patch(Rectangle((gx, gy), cg, cg, fc=(0.02, 0.59, 0.41, 0.16), ec="none", zorder=2))
            grid(ax, gx, gy, gs, 2, ec=GREEN, lw=2.0, fc=(0, 0, 0, 0))
            cells(gx, prev, fc="none", ec=MUTED, lw=1.2, ls=(0, (2, 2)), zorder=4)
            ax.text(gx + cg / 2, gy - 0.12, "この粗マスのstateが\n移動前も後も人物を含む", fontsize=8.5,
                    color=GREEN, ha="center", va="top", linespacing=1.2)
        else:
            plt.rcParams["hatch.color"] = PURPLE
            cells(gx, prev, fc="none", ec=MUTED, lw=1.2, ls=(0, (2, 2)), zorder=4)
            memory(gx, now, PURPLE, (0.49, 0.23, 0.93, 0.12))
            ax.add_patch(FancyArrowPatch((gx + 1.0 * c, gy + 2.5 * c), (gx + 3.0 * c, gy + 2.5 * c),
                                         arrowstyle="-|>", mutation_scale=16, color=PURPLE, lw=2.2, zorder=6))
            ax.text(gx + 2 * c, gy + 4.35 * c, "予測した動き", fontsize=8.5, color=PURPLE, ha="center",
                    zorder=6, bbox=dict(fc="white", ec="none", pad=1))
        person(gx)
        ax.text(gx + gs + 0.15, gy + gs, verdict, fontsize=14, weight="bold", color=col, va="top")
        ax.text(gx + gs / 2, gy - 0.75, body, ha="center", va="top", fontsize=9.6, color=INK, linespacing=1.4)
    ax.text(0.4, 0.2, "灰色の点線枠＝移動前の人物の位置。②・③のように場所ごとにstateを持つ表現ほど影響が大きい。①（1 token）はずれないが、位置情報自体を失う。",
            fontsize=9.5, color=MUTED)
    fig.savefig(OUT / "03-motion-misalignment.png", facecolor="white")
    plt.close(fig)


# ---------------------------------------------------------------- Fig 4
def fig4():
    fig, ax = new_fig(13.33, 6.0)
    ax.text(0.4, 5.55, "まとめ：空間をどれだけ残すか と 重さ のトレードオフ", fontsize=19, weight="bold", color=INK)
    y = 3.6
    ax.add_patch(FancyArrowPatch((0.8, y), (12.6, y), arrowstyle="-|>", mutation_scale=22, color=INK, lw=2.2))
    ax.text(0.8, y - 0.45, "空間情報：少ない／軽い", fontsize=11, color=MUTED)
    ax.text(12.6, y - 0.45, "空間情報：多い／重い", fontsize=11, color=MUTED, ha="right")
    items = [(1.6, "①", "1 token\n（現行）", MUTED), (4.3, "④", "縮約グリッド\n8×8 → 16×16", GREEN),
             (7.2, "⑤", "多スケール\n（FPN的）", PURPLE), (10.2, "②", "全位置\n時間scan", BLUE),
             (11.6, "③", "時空間\nscan", BLUE)]
    for x, num, lab, col in items:
        ax.add_patch(Circle((x, y), 0.3, fc="white", ec=col, lw=2.2, zorder=5))
        ax.text(x, y, num, ha="center", va="center", fontsize=14, weight="bold", color=col, zorder=6)
        ax.text(x, y + 0.5, lab, ha="center", va="bottom", fontsize=10.5, color=INK, linespacing=1.2)
    ax.text(10.9, y + 1.45, "9/30「一括で入れる」", ha="center", fontsize=9.5, color=BLUE)
    ax.text(7.2, y + 1.45, "9/30「FPNなどの工夫」", ha="center", fontsize=9.5, color=PURPLE)

    # channel compression knob
    ax.add_patch(FancyBboxPatch((7.9, 1.75), 4.7, 1.05, boxstyle="round,pad=0.02,rounding_size=0.08",
                                fc=BLUE_L, ec=BLUE, lw=1.0))
    ax.text(8.05, 2.62, "もう1つのつまみ：チャネルを削る", fontsize=10.5, weight="bold", color=BLUE, va="top")
    ax.text(8.05, 2.25, "空間64×64は残し、256ch→64chに圧縮してから入れる\n→ ②のstateを約1/4に（「次元を落とす」の別解）",
            fontsize=9.3, color=INK, va="top", linespacing=1.35)
    arrow(ax, 10.2, 2.8, 10.2, y - 0.32, color=BLUE, lw=1.2, ms=9)

    # proposed order
    ax.add_patch(FancyBboxPatch((0.6, 0.3), 6.9, 2.5, boxstyle="round,pad=0.02,rounding_size=0.08",
                                fc=GREY_L, ec="#d1d5db", lw=1.0))
    ax.text(0.8, 2.62, "進め方の提案（案）", fontsize=11, weight="bold", color=INK, va="top")
    steps = ["1. ②のメモリ・速度を実測し、「一括で入れる」の可否を確認",
             "2. 無理なら：チャネル圧縮した② か ④（8×8 → 16×16）",
             "3. 最終構成の候補として⑤（SAM2既存のFPN段に沿わせる）",
             "4. どの案でも「物が動くとずれる」への対処を併記（図3）"]
    for i, s in enumerate(steps):
        ax.text(0.85, 2.15 - i * 0.43, s, fontsize=10.2, color=INK, va="top")
    fig.savefig(OUT / "04-tradeoff-summary.png", facecolor="white")
    plt.close(fig)


fig1()
fig2()
fig3()
fig4()
print("done")
