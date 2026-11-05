"""A（①-b）と B（②・②'）を V3 の 64 段にどう組み込んだかの図。

実装を読んで描いた概念図（SAM2 repo `/mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2`）:
- ②・②': ブランチ `feat/spatial-mixing-adapter`、`sam2/modeling/temporal_adapters.py` の `SpatialPyramidAdapter`
- ①-b: ブランチ `feat/latent-correspondence`、同ファイルの `CorrespondencePyramidAdapter`
スタイルは ../2026-10-23-v3-structure/make_figs.py に合わせた。
使い方: python3 make_figs.py（このファイルと同じフォルダに出力）
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Ellipse

plt.rcParams["font.family"] = "Noto Sans CJK JP"
OUT = Path(__file__).parent

INK = "#1f2937"
MUTED = "#6b7280"
GREY_L = "#f3f4f6"
A_C, A_L = "#1F6FD1", "#EAF2FC"      # ①-b（図6と同じ色）
R_C, R_L = "#E07B10", "#FDF1E4"      # ②
S_C, S_L = "#7D4BC2", "#F1EAFA"      # ②'
W, H = 13.33, 7.5


def new_fig():
    fig = plt.figure(figsize=(W, H), dpi=200)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.axis("off")
    fig.patch.set_facecolor("white")
    return fig, ax


def box(ax, x, y, w, h, text, fc="white", ec=INK, fs=10.5, lw=1.2, ls="-", color=INK, weight="normal"):
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


def title(ax, t, sub):
    ax.text(0.35, H - 0.45, t, fontsize=17, weight="bold", color=INK, va="center")
    ax.text(0.35, H - 0.9, sub, fontsize=10.5, color=MUTED, va="center")


def tail(ax, y, x_mamba_r, x_wout, x_wout_r, x_a, x_a_r, x_plus, x_out, x_feat, h=0.8, out_text="64段の出力\n→ マスクデコーダ"):
    """Mamba の後ろ（W_out → ×α → + → 出力）と、元の特徴からの残差の点線。"""
    box(ax, x_wout, y - h / 2, x_wout_r - x_wout, h, "W_out", fs=10)
    box(ax, x_a, y - h / 2, x_a_r - x_a, h, "×α", fs=10.5)
    plus(ax, x_plus, y)
    box(ax, x_out, y - 0.45, W - 0.35 - x_out, 0.9, out_text, fc=GREY_L, fs=10)
    arrow(ax, x_wout_r, y, x_a, y)
    arrow(ax, x_a_r, y, x_plus - 0.16, y)
    arrow(ax, x_plus + 0.16, y, x_out, y)
    yr = y - 0.75
    ax.plot([x_feat, x_feat, x_plus], [y - 0.45, yr, yr], color=MUTED, lw=1.0, ls=(0, (2, 2)))
    arrow(ax, x_plus, yr, x_plus, y - 0.16, color=MUTED, lw=1.0, ls=(0, (2, 2)), ms=9)
    ax.text(x_feat + 0.15, yr + 0.1, "元の特徴（残差の足し先）", fontsize=8.5, color=MUTED, ha="left")


# ---------------------------------------------------------------- 図7: A（①-b）
def fig_1b():
    fig, ax = new_fig()
    title(ax, "A：①-b の組み込み　64段の Mamba に入る前に、state を対応先から運ぶ",
          "青が追加した部分（学習パラメータなし）。白は V3 と同じで学習する部分、灰色は SAM2 の固定部分。128・256段は V3 のまま")
    y = 5.2
    box(ax, 0.35, y - 0.45, 1.9, 0.9, "pix_feat 64×64・256ch\n（対象別）", fc=GREY_L, fs=10)
    box(ax, 2.65, y - 0.4, 1.3, 0.8, "LayerNorm", fs=10.5)
    box(ax, 4.6, y - 0.55, 2.3, 1.1, "MambaCell（1歩進める）\nマスごとに独立", fs=10.5)
    arrow(ax, 2.25, y, 2.65, y)
    arrow(ax, 3.95, y, 4.6, y)
    ax.text(7.05, y + 0.12, "h", fontsize=10, color=INK)
    arrow(ax, 6.9, y, 7.5, y)
    tail(ax, y, 6.9, 7.5, 8.5, 8.85, 9.55, 10.0, 10.5, 1.3)
    ax.text(7.2, y + 0.75, "h は 128段へも渡す（top-down、V3 と同じ）", fontsize=8.5, color=MUTED)

    # state の経路
    ys = 3.15
    box(ax, 0.35, ys - 0.45, 2.3, 0.9, "前フレームの state（t−1）\nssm_state・conv_state\n（64×64 マスそれぞれ）", fs=9.5)
    box(ax, 4.6, ys - 0.5, 2.3, 1.0, "state を運ぶ\nh'(p) = Σ_q W(p, q)·h(q)", fc=A_L, ec=A_C, lw=2.0, fs=10.5, color=A_C, weight="bold")
    arrow(ax, 2.65, ys, 4.6, ys)
    arrow(ax, 5.75, ys + 0.5, 5.75, y - 0.55, color=A_C, lw=2.0)
    ax.text(5.85, (ys + 0.5 + y - 0.55) / 2 - 0.25, "運んだ state", fontsize=9, color=A_C)

    # 重みの計算
    yw = 1.55
    box(ax, 0.35, yw - 0.45, 2.3, 0.9, "画像エンコーダ特徴\nf_t と f_t−1\n（stride 16・凍結）", fc=GREY_L, fs=9.5)
    box(ax, 3.05, yw - 0.45, 2.75, 0.9, "各マスの周り 15×15 の cos 類似度\n→ softmax（τ = 0.02）→ 重み W", fc=A_L, ec=A_C, lw=1.5, fs=9.5, color=A_C)
    arrow(ax, 2.65, yw, 3.05, yw)
    arrow(ax, 5.25, yw + 0.45, 5.25, ys - 0.5, color=A_C, lw=1.6)
    ax.text(5.33, (yw + 0.45 + ys - 0.5) / 2 - 0.08, "W", fontsize=10, color=A_C, weight="bold")

    notes = [
        "・追加の学習パラメータは 0。W は凍結特徴から計算し、勾配を流さない",
        "・W を恒等（自分のマスだけ）にすると V3 と完全に一致する",
        "・運ぶのは 64段の state だけ（ssm_state と conv_state の両方）",
        "・state(t) と f_t は、次のフレームで同じように使う",
    ]
    for i, t in enumerate(notes):
        ax.text(7.5, 3.3 - i * 0.42, t, fontsize=10, color=INK, va="center")
    fig.savefig(OUT / "fig7-1b-in-model.png")
    plt.close(fig)


# ---------------------------------------------------------------- 図8: B（②・②'）
def fig_2():
    fig, ax = new_fig()
    title(ax, "B：②・②' の組み込み　64段に 7×7 の depthwise conv を足し、近傍と混ぜる",
          "色付きが追加した部分（Δ=0 の恒等で初期化し、初期状態は V3 と一致）。白は V3 と同じで学習する部分。128・256段は V3 のまま")

    # ② 読み書きカーネル
    y = 5.15
    ax.text(0.35, 6.2, "② 読み書きカーネル：Mamba の前後で近傍の特徴を見る（state は位置に固定のまま）",
            fontsize=11.5, color=R_C, weight="bold", va="center")
    box(ax, 0.35, y - 0.45, 1.6, 0.9, "pix_feat\n64×64・256ch", fc=GREY_L, fs=9.5)
    box(ax, 2.25, y - 0.4, 1.0, 0.8, "LayerNorm", fs=9.5)
    box(ax, 3.55, y - 0.45, 1.45, 0.9, "書き込み conv\n7×7 depthwise", fc=R_L, ec=R_C, lw=2.0, fs=9.5, color=R_C, weight="bold")
    box(ax, 5.3, y - 0.5, 1.6, 1.0, "MambaCell\nstate(t−1)→(t)", fs=9.5)
    box(ax, 7.2, y - 0.45, 1.45, 0.9, "読み出し conv\n7×7 depthwise", fc=R_L, ec=R_C, lw=2.0, fs=9.5, color=R_C, weight="bold")
    arrow(ax, 1.95, y, 2.25, y)
    arrow(ax, 3.25, y, 3.55, y)
    arrow(ax, 5.0, y, 5.3, y)
    arrow(ax, 6.9, y, 7.2, y)
    arrow(ax, 8.65, y, 8.95, y)
    tail(ax, y, 8.65, 8.95, 9.75, 10.0, 10.5, 10.85, 11.2, 1.15, out_text="64段の出力")
    ax.text(7.25, y + 0.6, "h' は 128段へも渡す（top-down）", fontsize=8.5, color=MUTED)

    ax.plot([0.35, W - 0.35], [3.75, 3.75], color="#d1d5db", lw=1.0)

    # ②' state 空間混合
    y2 = 2.75
    ax.text(0.35, 3.4, "②' state 空間混合：Mamba に入る前に、前フレームの state を近傍と混ぜる",
            fontsize=11.5, color=S_C, weight="bold", va="center")
    box(ax, 0.35, y2 - 0.45, 1.6, 0.9, "pix_feat\n64×64・256ch", fc=GREY_L, fs=9.5)
    box(ax, 2.25, y2 - 0.4, 1.0, 0.8, "LayerNorm", fs=9.5)
    box(ax, 5.3, y2 - 0.5, 1.6, 1.0, "MambaCell\n（1歩進める）", fs=9.5)
    arrow(ax, 1.95, y2, 2.25, y2)
    arrow(ax, 3.25, y2, 5.3, y2)
    ax.text(7.0, y2 + 0.12, "h", fontsize=10, color=INK)
    arrow(ax, 6.9, y2, 8.95, y2)
    tail(ax, y2, 6.9, 8.95, 9.75, 10.0, 10.5, 10.85, 11.2, 1.15, out_text="64段の出力")

    ys = 0.85
    box(ax, 0.35, ys - 0.4, 2.3, 0.8, "前フレームの state（t−1）\nssm_state・conv_state", fs=9.5)
    box(ax, 4.75, ys - 0.45, 2.7, 0.9, "state を 7×7 depthwise conv で混ぜる\n（カーネルを L1 正規化）", fc=S_L, ec=S_C, lw=2.0, fs=9.5, color=S_C, weight="bold")
    arrow(ax, 2.65, ys, 4.75, ys)
    arrow(ax, 6.1, ys + 0.45, 6.1, y2 - 0.5, color=S_C, lw=2.0)
    ax.text(6.2, (ys + 0.45 + y2 - 0.5) / 2 - 0.05, "混ぜた state", fontsize=9, color=S_C)
    ax.text(7.7, ys + 0.12, "毎フレームかかるので、届く範囲は時間とともに広がる\n（1フレームで ±3 マス）。L1 正規化で発散を防ぐ",
            fontsize=9, color=MUTED, va="center")
    fig.savefig(OUT / "fig8-2-2p-in-model.png")
    plt.close(fig)


if __name__ == "__main__":
    fig_1b()
    fig_2()
