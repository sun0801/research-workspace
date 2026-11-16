"""B案（問題駆動型）用の図を作る．
概念図 -> figures/b/，実験由来の図 -> experiments/figures/（正本，results/*.json から作る）．CPUのみ．"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle  # noqa: E402

plt.rcParams["font.family"] = ["Noto Sans CJK JP", "sans-serif"]
plt.rcParams["font.size"] = 17
plt.rcParams["axes.unicode_minus"] = False

HERE = os.path.dirname(os.path.abspath(__file__))
SESSION = os.path.dirname(HERE)
PROJ = os.path.dirname(os.path.dirname(SESSION))
FIG = os.path.join(SESSION, "figures", "b")
EXP = os.path.join(PROJ, "experiments", "figures")
RES = "/mnt/HDD10TB-2/aburatani/quantization_handson/results"
os.makedirs(FIG, exist_ok=True)
os.makedirs(EXP, exist_ok=True)
C1, C2, C3, GR, RED = "#1f6fb4", "#e08a1e", "#2a9d5c", "#888888", "#c0392b"


def save(fig, path):
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(path)


# ---------- 概念図 ----------
def fig_memory():
    fig, ax = plt.subplots(figsize=(12.6, 3.6))
    names = ["FP16（2 byte/重み）", "INT8（1 byte）", "4 bit（0.5 byte）"]
    vals = [14 * 2, 14 * 1, 14 * 0.5]
    b = ax.barh(names[::-1], vals[::-1], color=[C3, C2, C1])
    ax.axvline(16, color=RED, ls="--", lw=2)
    ax.set_ylim(-0.6, 3.0)
    ax.text(16.4, 2.75, "GPU 16 GB", color=RED, va="center")
    for r, v in zip(b, vals[::-1]):
        ax.text(v - 0.5, r.get_y() + r.get_height() / 2, f"{v:g} GB", va="center", ha="right", color="white", fontweight="bold")
    ax.set_xlim(0, 33)
    ax.set_xlabel("重みの保存に必要な容量 [GB]（14B パラメータ）")
    ax.spines[["top", "right"]].set_visible(False)
    save(fig, os.path.join(FIG, "memory_14b.png"))


def fig_grid():
    b, lo, hi = 4, -1.0, 1.0
    s = (hi - lo) / (2**b - 1)
    z = round(-lo / s)
    grid = [s * (q - z) for q in range(2**b)]
    fig, ax = plt.subplots(figsize=(12.6, 3.7))
    ax.hlines(0, -1.35, 1.35, color="k", lw=1)
    ax.vlines(grid, -0.12, 0.12, color=C1, lw=2)
    ax.plot(grid, [0] * len(grid), "o", color=C1, ms=6)
    ax.axvspan(-1.35, grid[0], color=RED, alpha=0.08)
    ax.axvspan(grid[-1], 1.35, color=RED, alpha=0.08)
    # 丸め例
    x = 0.37
    xq = grid[min(range(len(grid)), key=lambda i: abs(grid[i] - x))]
    ax.plot([x], [0.0], "D", color=C2, ms=10, zorder=5)
    ax.annotate("", xy=(xq, 0.45), xytext=(x, 0.45), arrowprops=dict(arrowstyle="<->", color=C2, lw=2))
    ax.text((x + xq) / 2, 0.58, "丸め誤差\n（最大 s/2）", ha="center", color=C2)
    ax.text(x, -0.38, "x = 0.37", ha="center", color=C2)
    # クリップ例
    x2 = 1.2
    ax.plot([x2], [0.0], "D", color=RED, ms=10, zorder=5)
    ax.annotate("", xy=(grid[-1], 0.45), xytext=(x2, 0.45), arrowprops=dict(arrowstyle="<->", color=RED, lw=2))
    ax.text((x2 + grid[-1]) / 2 + 0.02, 0.58, "クリップ\n誤差", ha="center", color=RED)
    ax.text(x2, -0.38, "x = 1.2", ha="center", color=RED)
    ax.text(0, -0.72, f"4 bit のグリッド 16点（間隔 s = 2/15 ≈ {s:.3f}）", ha="center")
    ax.text(0, -0.95, f"zero-point z = {z}", ha="center")
    ax.text(grid[-1], 0.2, "q_max", ha="center", color=GR, fontsize=15)
    ax.text(grid[0], 0.2, "q_min", ha="center", color=GR, fontsize=15)
    ax.set_xlim(-1.35, 1.35)
    ax.set_ylim(-1.1, 1.05)
    ax.axis("off")
    save(fig, os.path.join(FIG, "grid_round_clip.png"))
    return s, z


def fig_symasym():
    fig, axs = plt.subplots(1, 2, figsize=(12.6, 3.4))
    # 対称（符号付き 4bit）: -8..7, z=0
    s = 0.1
    q = list(range(-8, 8))
    ax = axs[0]
    ax.plot([s * v for v in q], [0] * 16, "o", color=C1)
    ax.axvline(0, color=GR, ls=":")
    ax.set_title("対称: zero-point = 0（重み向き）")
    ax.set_xlim(-1.0, 1.0)
    ax.set_xlabel("実数値（グリッドは 0 の左右で対称）")
    # 非対称（符号なし 4bit）: 範囲 [-0.2, 1.3]
    s2 = 1.5 / 15
    z = round(0.2 / s2)
    ax = axs[1]
    ax.plot([s2 * (v - z) for v in range(16)], [0] * 16, "o", color=C2)
    ax.axvline(0, color=GR, ls=":")
    ax.set_title("非対称: zero-point ≠ 0（活性向き）")
    ax.set_xlim(-1.0, 1.0 + 0.4)
    ax.set_xlabel("実数値（片側に偏った分布に合わせる）")
    for a in axs:
        a.set_yticks([])
        a.spines[["top", "right", "left"]].set_visible(False)
    save(fig, os.path.join(FIG, "sym_asym.png"))


def fig_granularity():
    import numpy as np
    rng = np.random.default_rng(0)
    rows, cols = 8, 12
    scale = np.array([0.3, 1.0, 0.5, 2.0, 0.4, 0.8, 0.2, 1.5])[:, None]
    W = rng.normal(size=(rows, cols)) * scale
    fig, axs = plt.subplots(1, 3, figsize=(12.6, 4.2))
    titles = ["per-tensor\n（scale 1つ）", "per-channel\n（出力チャネルごと）", "per-group\n（入力側を 64 ごと）"]
    cmap = plt.get_cmap("tab10")
    for k, ax in enumerate(axs):
        for i in range(rows):
            for j in range(cols):
                if k == 0:
                    c = 0
                elif k == 1:
                    c = i
                else:
                    c = i * 3 + j // 4
                ax.add_patch(Rectangle((j, rows - 1 - i), 1, 1, fc=cmap(c % 10), alpha=0.25 + 0.1 * (c // 10 % 3),
                                       ec="white", lw=1))
        ax.set_xlim(0, cols)
        ax.set_ylim(0, rows)
        ax.set_aspect("equal")
        ax.set_title(titles[k])
        ax.set_xlabel("入力側")
        ax.set_xticks([])
        ax.set_yticks([])
        if k == 0:
            ax.set_ylabel("出力チャネル")
    save(fig, os.path.join(FIG, "granularity.png"))


def fig_ste():
    import numpy as np
    fig, axs = plt.subplots(1, 2, figsize=(12.6, 3.9))
    y = np.linspace(-2.5, 2.5, 1000)
    ax = axs[0]
    ax.plot(y, np.round(y), color=C1, lw=2.5)
    ax.set_title("順伝播: round（階段）")
    ax.set_xlabel("y")
    ax.set_ylabel("⌊y⌉")
    ax = axs[1]
    ax.plot(y, 0 * y, color=RED, lw=2.5, label="本当の勾配（ほぼ至る所 0）")
    ax.plot(y, 1 + 0 * y, color=C3, lw=2.5, ls="--", label="STE: 1 とみなす")
    ax.set_ylim(-0.4, 1.6)
    ax.set_title("逆伝播: ∂⌊y⌉/∂y")
    ax.set_xlabel("y")
    ax.legend(loc="center right", fontsize=15, frameon=False)
    for a in axs:
        a.spines[["top", "right"]].set_visible(False)
    save(fig, os.path.join(FIG, "ste.png"))


def _box(ax, x, y, w, h, text, fc):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08", fc=fc, ec="#333", lw=1.5))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=17)


def _arrow(ax, x0, y0, x1, y1, color="#333"):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=22, color=color, lw=2))


def fig_qat():
    fig, ax = plt.subplots(figsize=(12.6, 3.9))
    ax.set_xlim(0, 12.6)
    ax.set_ylim(0, 4)
    ax.axis("off")
    xs = [0.2, 3.3, 6.4, 9.5]
    labels = ["重み W\n（FP32 のまま保持）", "fake-quant\nQ(W)", "層の計算\n（FP32）", "損失 L"]
    fcs = ["#e8f1fa", "#fdeccf", "#e8f1fa", "#e8f1fa"]
    for x, t, fc in zip(xs, labels, fcs):
        _box(ax, x, 2.3, 2.7, 1.3, t, fc)
    for a, b in zip(xs[:-1], xs[1:]):
        _arrow(ax, a + 2.75, 2.95, b - 0.05, 2.95)
    ax.text(0.2, 3.85, "順伝播: 量子化の誤差を含めて計算", fontsize=17, color=C1)
    ax.text(0.2, 1.75, "逆伝播: 勾配は round を 1 とみなして（STE）通し，FP32 の W を更新", fontsize=17, color=C3)
    for a, b in zip(xs[:-1], xs[1:]):
        _arrow(ax, b - 0.05, 1.45, a + 2.75, 1.45, color=C3)
    ax.text(6.3, 0.5, "学習後は W を実際の整数に変換して配る", ha="center", fontsize=17)
    save(fig, os.path.join(FIG, "qat_flow.png"))


# ---------- 実験由来 ----------
def load():
    return json.load(open(os.path.join(RES, "ptq_table.json")))["models"]


def fig_w_only(models):
    fig, axs = plt.subplots(1, 2, figsize=(12.6, 4.4), sharey=True)
    bits = [8, 6, 4, 3, 2]
    for ax, m, name in zip(axs, ["resnet18", "deit_tiny"], ["ResNet18", "DeiT-Tiny"]):
        runs = [r for r in models[m]["runs"] if r["table"] == "weight_only"]
        for g, c, lab in [("per_tensor", RED, "per-tensor"), ("per_channel", C2, "per-channel"), ("per_group", C1, "per-group(64)")]:
            ys = [next(r["acc"] for r in runs if r["w_bits"] == b and r["granularity"] == g) for b in bits]
            ax.plot(range(len(bits)), ys, "o-", color=c, lw=2.5, label=lab)
        ax.axhline(models[m]["fp32"]["eval2000"], color=GR, ls="--", lw=1.5)
        ax.set_xticks(range(len(bits)))
        ax.set_xticklabels([f"W{b}" for b in bits])
        ax.set_title(f"{name}（FP32 {models[m]['fp32']['eval2000']:.2f}%）")
        ax.set_ylim(0, 100)
        ax.spines[["top", "right"]].set_visible(False)
    axs[0].set_ylabel("精度 [%]（eval2000）")
    axs[0].legend(loc="lower left", fontsize=15, frameon=False)
    save(fig, os.path.join(EXP, "2026-11-14-w-only-granularity.png"))


def fig_act(models):
    fig, axs = plt.subplots(1, 2, figsize=(12.6, 4.4), sharey=True)
    bits = [8, 6, 4]
    for ax, m, name in zip(axs, ["resnet18", "deit_tiny"], ["ResNet18", "DeiT-Tiny"]):
        runs = [r for r in models[m]["runs"] if r["table"] == "act_w8"]
        for cal, c, lab in [("minmax", RED, "minmax"), ("percentile", C1, "percentile"), ("mse", C3, "mse")]:
            ys = [next(r["acc"] for r in runs if r["a_bits"] == b and r["calib"] == cal) for b in bits]
            ax.plot(range(len(bits)), ys, "o-", color=c, lw=2.5, label=lab)
        ax.axhline(models[m]["fp32"]["eval2000"], color=GR, ls="--", lw=1.5)
        ax.set_xticks(range(len(bits)))
        ax.set_xticklabels([f"A{b}" for b in bits])
        ax.set_title(f"{name}（重み 8bit per-channel）")
        ax.set_ylim(0, 100)
        ax.spines[["top", "right"]].set_visible(False)
    axs[0].set_ylabel("精度 [%]（eval2000）")
    axs[1].legend(loc="lower left", fontsize=15, frameon=False)
    save(fig, os.path.join(EXP, "2026-11-14-act-calib-a-bits.png"))


def fig_qat_res():
    import numpy as np
    fig, axs = plt.subplots(1, 2, figsize=(12.6, 4.3), sharey=False)
    for ax, m, name in zip(axs, ["resnet18", "deit_tiny"], ["ResNet18", "DeiT-Tiny"]):
        q = json.load(open(os.path.join(RES, f"qat_{m}.json")))["models"][m]
        vals = [q["fp32"], q["ptq"], float(np.mean(q["finetune_then_ptq"])), float(np.mean(q["qat"]))]
        labs = ["FP32", "PTQ", "fine-tune\n→PTQ", "QAT"]
        cols = [GR, C2, C1, C3]
        ax.bar(range(4), vals, color=cols)
        tops = [vals[0], vals[1], max(q["finetune_then_ptq"]), max(q["qat"])]
        for i, v in enumerate(vals):
            ax.text(i, tops[i] + 0.2, f"{v:.2f}", ha="center", fontsize=16)
        for i, arr in [(2, q["finetune_then_ptq"]), (3, q["qat"])]:
            ax.plot([i] * len(arr), arr, "k.", ms=8)
        ax.set_xticks(range(4))
        ax.set_xticklabels(labs)
        ax.set_ylim(88, 97)
        ax.set_title(name)
        ax.spines[["top", "right"]].set_visible(False)
    axs[0].set_ylabel("精度 [%]（W4A8）")
    save(fig, os.path.join(EXP, "2026-11-14-qat-vs-ptq.png"))


if __name__ == "__main__":
    fig_memory()
    print(fig_grid())
    fig_symasym()
    fig_granularity()
    fig_ste()
    fig_qat()
    M = load()
    fig_w_only(M)
    fig_act(M)
    fig_qat_res()
