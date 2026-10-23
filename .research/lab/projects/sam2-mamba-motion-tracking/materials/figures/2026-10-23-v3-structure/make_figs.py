"""V3（PyramidAdapter）の構造説明図。

実装（SAM2 repo `feat/temporal-mamba-v3` の ff78b57、`sam2/modeling/temporal_adapters.py`・
`sam2/modeling/sam2_base.py`）を読んで描いた概念図。数値はコードから数えた値。
使い方: python3 make_figs.py（このファイルと同じフォルダに出力）
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle, Ellipse

plt.rcParams["font.family"] = "Noto Sans CJK JP"
OUT = Path(__file__).parent

INK = "#1f2937"
MUTED = "#6b7280"
GRID = "#9ca3af"
GREY_L = "#f3f4f6"
BLUE = "#2563eb"
BLUE_L = "#dbeafe"
ORANGE = "#ea580c"
ORANGE_L = "#ffedd5"
PURPLE = "#7c3aed"
PURPLE_L = "#ede9fe"
GREEN = "#059669"


def new_fig(w=13.33, h=7.5):
    fig = plt.figure(figsize=(w, h), dpi=200)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.axis("off")
    fig.patch.set_facecolor("white")
    return fig, ax


def box(ax, x, y, w, h, text, fc=GREY_L, ec=INK, fs=10.5, lw=1.2, ls="-", color=INK, weight="normal"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08",
                                fc=fc, ec=ec, lw=lw, ls=ls))
    if text:
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, color=color,
                weight=weight, linespacing=1.35)


def arrow(ax, x0, y0, x1, y1, color=INK, lw=1.4, ls="-", rad=0.0, ms=12):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=ms,
                                 color=color, lw=lw, ls=ls, connectionstyle=f"arc3,rad={rad}",
                                 shrinkA=0, shrinkB=0))


def plus(ax, x, y, r=0.16, color=INK):
    ax.add_patch(Ellipse((x, y), 2 * r, 2 * r, fc="white", ec=color, lw=1.3))
    ax.text(x, y, "+", ha="center", va="center", fontsize=12, color=color, weight="bold")


def title(ax, t, sub=None, w=13.33, h=7.5):
    ax.text(0.35, h - 0.45, t, fontsize=17, weight="bold", color=INK, va="center")
    if sub:
        ax.text(0.35, h - 0.9, sub, fontsize=10.5, color=MUTED, va="center")


# ---------------------------------------------------------------- 図1: SAM2の中での位置
def fig_position():
    fig, ax = new_fig()
    title(ax, "V3はSAM2のどこに入るか：Memory Attentionの後・マスクデコーダの前",
          "灰色はF0の重みで固定。橙のV3だけを学習する。1フレーム・1対象あたりの流れ")

    # 入力・画像エンコーダ
    box(ax, 0.35, 2.8, 1.25, 1.0, "フレーム t\n（1024×1024）")
    box(ax, 2.0, 1.3, 1.55, 4.0, "画像エンコーダ\n（Hiera＋FPN）\n\n全対象で共通", fs=10.5)
    arrow(ax, 1.6, 3.3, 2.0, 3.3)

    ys = {"64": 4.75, "128": 3.25, "256": 1.75}
    labels = {"64": "64×64・256ch", "128": "128×128・64ch\n（conv_s1で射影）", "256": "256×256・32ch\n（conv_s0で射影）"}
    # 64段: Memory Attention を通る
    box(ax, 4.05, ys["64"] - 0.45, 1.75, 0.9, "Memory Attention\n（過去のメモリを参照）", fc=BLUE_L, ec=BLUE, fs=9.5)
    arrow(ax, 3.55, ys["64"], 4.05, ys["64"])
    box(ax, 6.2, ys["64"] - 0.45, 1.55, 0.9, "pix_feat 64×64・256ch\n対象別の特徴", fs=9.5)
    arrow(ax, 5.8, ys["64"], 6.2, ys["64"])
    for k in ("128", "256"):
        box(ax, 6.2, ys[k] - 0.45, 1.55, 0.9, "高解像度特徴\n" + labels[k].split("\n")[0], fs=9.5)
        arrow(ax, 3.55, ys[k], 6.2, ys[k])
        ax.text(4.0, ys[k] + 0.12, labels[k].replace("\n", " "), fontsize=8.5, color=MUTED)
        ax.text(4.0, ys[k] - 0.3, "対象の情報は持たない", fontsize=8.5, color=MUTED)

    # V3
    box(ax, 8.15, 1.15, 1.9, 4.45, "", fc=ORANGE_L, ec=ORANGE, lw=2.0)
    ax.text(9.1, 5.33, "V3 adapter", ha="center", fontsize=12, weight="bold", color=ORANGE)
    for k in ("64", "128", "256"):
        box(ax, 8.35, ys[k] - 0.38, 1.5, 0.76, f"{k}段の\nMamba", fc="white", ec=ORANGE, fs=9.5)
        arrow(ax, 7.75, ys[k], 8.35, ys[k])
    arrow(ax, 9.1, ys["64"] - 0.38, 9.1, ys["128"] + 0.38, color=ORANGE)
    arrow(ax, 9.1, ys["128"] - 0.38, 9.1, ys["256"] + 0.38, color=ORANGE)
    ax.text(9.17, (ys["64"] + ys["128"]) / 2, "top-down", fontsize=8, color=ORANGE, va="center")
    ax.text(9.17, (ys["128"] + ys["256"]) / 2, "top-down", fontsize=8, color=ORANGE, va="center")
    # state
    ax.text(9.1, 0.72, "学習するのはV3だけ。各段のstateを\nフレーム t−1 → t → t+1 と持ち越す", ha="center", fontsize=9, color=ORANGE)

    # mask decoder
    box(ax, 10.5, 1.3, 1.25, 4.0, "マスク\nデコーダ\n\n（SAM2の\nまま）", fs=10.5)
    for k in ("64", "128", "256"):
        arrow(ax, 9.85, ys[k], 10.5, ys[k])
    box(ax, 12.05, 2.8, 1.05, 1.0, "マスク t", fs=10.5)
    arrow(ax, 11.75, 3.3, 12.05, 3.3)

    # memory encoder path
    box(ax, 4.05, 5.65, 3.7, 0.5, "メモリエンコーダ → メモリバンク（次のフレームで参照）", fc=BLUE_L, ec=BLUE, fs=9.5)
    arrow(ax, 12.55, 3.8, 12.55, 5.9, color=BLUE, ls="--")
    arrow(ax, 12.55, 5.9, 7.75, 5.9, color=BLUE, ls="--")
    ax.text(10.15, 5.98, "予測したマスク", fontsize=8.5, color=BLUE, ha="center")
    arrow(ax, 2.78, 5.3, 4.05, 5.85, color=BLUE, ls="--")
    ax.text(1.0, 5.75, "画像特徴（V3を通らない）", fontsize=8.5, color=BLUE)
    arrow(ax, 4.92, 5.65, 4.92, ys["64"] + 0.45, color=BLUE, ls="--")

    ax.text(0.35, 0.45,
            "・V3が変えるのはマスクデコーダに入る3段の特徴だけ（各段に残差を足す）。メモリエンコーダは元の画像特徴と予測マスクを使うので、V3がメモリに効くのはマスクを通してだけ。\n"
            "・初期化（α＝1、W_out＝0）では残差が0で、出力はF0と完全に一致する（確認済み）。",
            fontsize=9, color=INK, va="center", linespacing=1.5)
    fig.savefig(OUT / "01-v3-position-in-sam2.png")
    plt.close(fig)


# ---------------------------------------------------------------- 図2: 1フレームの中の計算
def fig_inside():
    fig, ax = new_fig()
    title(ax, "V3の中の計算（1フレーム）：段ごとにMambaを回し、粗い段から細かい段へ出力を渡す",
          "各段とも「特徴 ＋ α・W_out（Mambaの出力）」を返す。段の間は、W_outの前のMamba出力を×2に拡大して1×1 convで渡す（つなぎ方(a)）")

    lanes = [("64", 5.55, "pix_feat 64×64・256ch\n（対象別）", "4,096マス", "d_inner 512", "約50万"),
             ("128", 3.55, "feat_s1 128×128・64ch", "16,384マス", "d_inner 128", "約5万"),
             ("256", 1.6, "feat_s0 256×256・32ch", "65,536マス", "d_inner 64", "約1万")]
    xs = dict(feat=0.35, tok=2.55, ln=4.25, add=5.55, mamba=6.25, wout=8.4, alpha=9.6, res=10.45, out=11.0)
    for name, y, flabel, cells, dinner, params in lanes:
        box(ax, xs["feat"], y - 0.45, 1.85, 0.9, flabel, fs=8.8)
        arrow(ax, xs["feat"] + 1.85, y, xs["tok"], y)
        box(ax, xs["tok"], y - 0.45, 1.35, 0.9, f"マスごとに\n1本の系列\n（{cells}）", fs=8.5, fc="white")
        arrow(ax, xs["tok"] + 1.35, y, xs["ln"], y)
        box(ax, xs["ln"], y - 0.3, 0.95, 0.6, "LayerNorm", fs=8.5, fc="white")
        arrow(ax, xs["ln"] + 0.95, y, xs["add"] - 0.16, y)
        plus(ax, xs["add"], y)
        arrow(ax, xs["add"] + 0.16, y, xs["mamba"], y)
        box(ax, xs["mamba"], y - 0.5, 1.75, 1.0, f"MambaCell（1歩進める）\n{dinner}\nstate(t−1) → state(t)", fc=ORANGE_L, ec=ORANGE, fs=8.8)
        # state in/out
        arrow(ax, xs["mamba"] + 1.75, y, xs["wout"], y)
        ax.text((xs["mamba"] + 1.75 + xs["wout"]) / 2 + 0.1, y + 0.1, "h", fontsize=9, color=INK, ha="center")
        box(ax, xs["wout"], y - 0.3, 1.0, 0.6, "W_out\n（0で初期化）", fs=8, fc="white")
        arrow(ax, xs["wout"] + 1.0, y, xs["alpha"], y)
        box(ax, xs["alpha"], y - 0.25, 0.5, 0.5, "×α", fs=9, fc="white")
        arrow(ax, xs["alpha"] + 0.5, y, xs["res"] - 0.16, y)
        plus(ax, xs["res"], y)
        # skip connection from feature
        ax.plot([xs["feat"] + 0.9, xs["feat"] + 0.9, xs["res"]], [y - 0.45, y - 0.68, y - 0.68],
                color=MUTED, lw=1.0, ls=":")
        arrow(ax, xs["res"], y - 0.68, xs["res"], y - 0.16, color=MUTED, lw=1.0, ls=":")
        ax.text(xs["ln"], y - 0.62, "元の特徴（残差の足し先）", fontsize=7.5, color=MUTED)
        arrow(ax, xs["res"] + 0.16, y, xs["out"], y)
        box(ax, xs["out"], y - 0.45, 1.95, 0.9, f"{name}段の出力\n→ マスクデコーダ\n（パラメータ{params}）", fs=8.5)

    # top-down connections (from h, before W_out)
    for (n1, y1, *_), (n2, y2, *_) in zip(lanes[:-1], lanes[1:]):
        xh = (xs["mamba"] + 1.75 + xs["wout"]) / 2
        ax.plot([xh, xh], [y1, y1 - 0.85], color=PURPLE, lw=1.6)
        box(ax, xh - 0.95, y1 - 1.35, 1.9, 0.5, "×2 bilinear拡大 → 1×1 conv", fc=PURPLE_L, ec=PURPLE, fs=8)
        ax.plot([xh, xh], [y1 - 1.35, y2 + 0.55], color=PURPLE, lw=1.6)
        ax.plot([xh, xs["add"]], [y2 + 0.55, y2 + 0.55], color=PURPLE, lw=1.6)
        arrow(ax, xs["add"], y2 + 0.55, xs["add"], y2 + 0.16, color=PURPLE, lw=1.6)

    ax.text(0.35, 0.45,
            "・Mambaの中ではマス同士は混ざらない（各マスが独立した系列）。横方向の情報は、SAM2の特徴そのものと、上の段からのtop-downで入る。\n"
            "・64段だけがMemory Attentionを通った対象別の特徴。top-downで128・256段にも対象の情報が入るので、3段ともstateは対象ごとに持つ。"
            "　合計 約57万パラメータ（V1は約50万）。",
            fontsize=9, color=INK, va="center", linespacing=1.5)
    fig.savefig(OUT / "02-v3-inside-one-frame.png")
    plt.close(fig)


# ---------------------------------------------------------------- 図3: 時間方向とstateの位置
def fig_time():
    fig, ax = new_fig()
    title(ax, "時間方向：マスごとのstateを次のフレームへ持ち越す（stateは画面上の位置に固定）",
          "例として64段の8×8に縮めて描いた。実際は64×64・128×128・256×256の全マスが、それぞれ自分のstateを持つ")

    n, size = 8, 2.6
    c = size / n
    frames = [(0.6, "t−1", 2), (4.1, "t", 3), (7.6, "t+1", 4)]
    ci, cj = 3, 4  # 注目するマス（列, 行）
    for x0, lab, ox in frames:
        y0 = 3.3
        for i in range(n):
            for j in range(n):
                ax.add_patch(Rectangle((x0 + i * c, y0 + j * c), c, c, fc="white", ec=GRID, lw=0.5))
        # 物体（右へ動く）
        ax.add_patch(Ellipse((x0 + (ox + 0.5) * c, y0 + 4.2 * c), 2.2 * c, 3.6 * c, fc=BLUE_L, ec=BLUE, lw=1.2, alpha=0.9))
        ax.add_patch(Rectangle((x0 + ci * c, y0 + cj * c), c, c, fc="none", ec=ORANGE, lw=2.2))
        ax.text(x0 + size / 2, y0 + size + 0.25, f"フレーム {lab}", ha="center", fontsize=11, color=INK)
    # state chain
    for (x0, *_), (x1, *_) in zip(frames[:-1], frames[1:]):
        arrow(ax, x0 + (ci + 1) * c + 0.05, 3.3 + (cj + 0.5) * c, x1 + ci * c - 0.05, 3.3 + (cj + 0.5) * c,
              color=ORANGE, lw=1.8, rad=-0.35)
    ax.text(0.6, 2.95, "同じ位置（i, j）のマスのstateだけが、次のフレームの同じマスへ渡る（橙の矢印）",
            fontsize=10, color=ORANGE)
    ax.text(0.6, 2.6, "青：対象の物体（右へ動いている）　橙の枠：注目するマス（i, j）", fontsize=9, color=MUTED)

    # 右側: 説明
    box(ax, 10.75, 3.0, 2.3, 3.2, "", fc="white", ec=INK)
    ax.text(10.9, 6.0, "このマスのstateが見てきたもの", fontsize=9.5, weight="bold", color=INK, va="top")
    ax.text(10.9, 5.55, "t−1：物体の右端\n t ：物体の中央\nt+1：物体の左側",
            fontsize=9.5, color=INK, va="top", linespacing=1.6)
    ax.text(10.9, 4.2, "→ 同じstateに、物体の\n　別の部分の情報が混ざる", fontsize=9.5, color=ORANGE, va="top", linespacing=1.5)

    ax.text(0.6, 2.05, "読み方", fontsize=11, weight="bold", color=INK)
    ax.text(0.6, 1.25,
            "・state carry：各マスが「その位置で過去に見た特徴」を覚え、今の特徴に残差として足す。stateは軌跡の最初で0、学習ではTBPTT 8フレームごとに勾配を切る（値は持ち越す）。\n"
            "・物体が止まっている・ゆっくり動く間は、同じマスが同じ部位を見続けるので、過去の見え方を使える。\n"
            "・物体が大きく動くと、マスとstateの対応がずれる。粗い64段（1マス＝16 px）は受容野が広く、ずれの影響が小さい見込み。細かい256段（1マス＝4 px）ほどずれやすい（未検証）。\n"
            "・V3-reset（推論時だけ毎フレームstateを0にする）とV3を比べると、学習済みV3がstateの持ち越しにどれだけ頼っているかが分かる。",
            fontsize=9, color=INK, va="center", linespacing=1.6)
    fig.savefig(OUT / "03-v3-state-over-time.png")
    plt.close(fig)


if __name__ == "__main__":
    fig_position()
    fig_inside()
    fig_time()
