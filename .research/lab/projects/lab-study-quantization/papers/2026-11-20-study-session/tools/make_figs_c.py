"""C案の図を作る．実験由来の図は experiments/figures/（正本，JSONから．既存なら上書きしない），概念図は figures/c/．"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager

HERE = os.path.dirname(os.path.abspath(__file__))
SS = os.path.dirname(HERE)  # papers/2026-11-20-study-session
PROJ = os.path.abspath(os.path.join(SS, "..", ".."))
EXPFIG = os.path.join(PROJ, "experiments", "figures")
CFIG = os.path.join(SS, "figures", "c")
RES = "/mnt/HDD10TB-2/aburatani/quantization_handson/results"
os.makedirs(CFIG, exist_ok=True)
for f in font_manager.findSystemFonts():
    if "NotoSansCJK-Regular" in f :
        font_manager.fontManager.addfont(f)
plt.rcParams["font.family"] = ["Noto Sans CJK JP"]
plt.rcParams.update({"font.size": 16, "axes.titlesize": 17, "axes.labelsize": 16, "legend.fontsize": 15,
                     "xtick.labelsize": 15, "ytick.labelsize": 15, "axes.spines.top": False, "axes.spines.right": False})
C = {"a": "#1f77b4", "b": "#d62728", "c": "#2ca02c", "g": "#7f7f7f"}


def save(fig, path, exp=False):
    if exp and os.path.exists(path):
        print("exists, skip:", path)
        plt.close(fig)
        return
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("saved", path)


ptq = json.load(open(os.path.join(RES, "ptq_table.json")))
sens = json.load(open(os.path.join(RES, "sensitivity.json")))


def runs(model, table):
    return [r for r in ptq["models"][model]["runs"] if r["table"] == table]


# ---- 実験図1: 重みのみ（fake-quant）----
fig, axs = plt.subplots(1, 2, figsize=(12.4, 4.0), sharey=True)
for ax, m, name in zip(axs, ("resnet18", "deit_tiny"), ("ResNet18", "DeiT-Tiny")):
    rs = runs(m, "weight_only")
    for g, lab, col in (("per_tensor", "per-tensor", C["b"]), ("per_channel", "per-channel", C["a"]), ("per_group", "per-group(64)", C["c"])):
        pts = sorted([(r["w_bits"], r["acc"]) for r in rs if r["granularity"] == g], reverse=True)
        ax.plot([p[0] for p in pts], [p[1] for p in pts], "o-", color=col, label=lab, lw=2.5)
    ax.axhline(ptq["models"][m]["fp32"]["eval2000"], color=C["g"], ls="--", lw=1.5)
    ax.set_title(f"{name}（破線: FP32）")
    ax.set_xlabel("重みのビット数")
    ax.set_xticks([8, 6, 4, 3, 2])
    ax.invert_xaxis()
axs[0].set_ylabel("精度 [%]（eval2000）")
axs[0].legend(loc="center left")
fig.tight_layout()
save(fig, os.path.join(EXPFIG, "2026-11-14-weight-only-acc.png"), exp=True)

# ---- 実験図2: 活性ビット × 較正方法（重みは8bit per-channel）----
fig, axs = plt.subplots(1, 2, figsize=(12.4, 4.0), sharey=True)
for ax, m, name in zip(axs, ("resnet18", "deit_tiny"), ("ResNet18", "DeiT-Tiny")):
    rs = [r for r in runs(m, "act_w8")]
    for c, col in (("minmax", C["b"]), ("percentile", C["a"]), ("mse", C["c"])):
        pts = sorted([(r["a_bits"], r["acc"]) for r in rs if r["calib"] == c], reverse=True)
        ax.plot([p[0] for p in pts], [p[1] for p in pts], "o-", color=col, label=c, lw=2.5)
    ax.axhline(ptq["models"][m]["fp32"]["eval2000"], color=C["g"], ls="--", lw=1.5)
    ax.set_title(f"{name}（重み8bit，破線: FP32）")
    ax.set_xlabel("活性のビット数")
    ax.set_xticks([8, 6, 4, 3, 2])
    ax.invert_xaxis()
axs[0].set_ylabel("精度 [%]（eval2000）")
axs[0].legend(loc="lower left")
fig.tight_layout()
save(fig, os.path.join(EXPFIG, "2026-11-14-act-bits-calib.png"), exp=True)

# ---- 実験図3: DeiT-Tiny 1層だけ A4（上位8層）----
L = sorted(sens["deit_tiny"]["layers"], key=lambda r: r["act_acc"])[:8]
fig, ax = plt.subplots(figsize=(12.4, 4.0))
ax.barh([r["layer"] for r in L][::-1], [r["act_acc"] for r in L][::-1], color=C["a"])
ax.axvline(sens["deit_tiny"]["fp32"], color=C["g"], ls="--", lw=1.5)
ax.set_xlim(90, 96)
ax.set_xlabel("1層だけ活性4bit（較正mse，他はFP32）の精度 [%]（破線: FP32 95.00）")
for i, r in enumerate(L[::-1]):
    ax.text(r["act_acc"] - 0.08, i, f'{r["act_acc"]:.2f}', va="center", ha="right", color="white", fontsize=15)
fig.tight_layout()
save(fig, os.path.join(EXPFIG, "2026-11-14-deit-layer-act4-sensitivity.png"), exp=True)

# ---- 概念図1: scale と zero-point（計算例）----
fig, ax = plt.subplots(figsize=(12.4, 3.6))
lo, hi, b = -1.0, 3.0, 4
s = (hi - lo) / (2 ** b - 1)
z = int(round(-lo / s))
qs = np.arange(0, 2 ** b)
xs = s * (qs - z)
ax.hlines(0, -1.2, 3.2, color="k", lw=1)
ax.vlines(xs, -0.1, 0.1, color=C["a"], lw=2)
for q, x in zip(qs, xs):
    ax.text(x, -0.25, str(q), ha="center", va="top", fontsize=16, color=C["a"])
    ax.text(x, -0.75, f"{x:.2f}", ha="center", va="top", fontsize=14, color="k")
ax.text(-1.25, -0.25, "整数 q", ha="right", va="top", fontsize=15, color=C["a"])
ax.text(-1.25, -0.75, "復元値", ha="right", va="top", fontsize=15)
ax.vlines(xs[z], -0.1, 0.5, color=C["b"], lw=3)
ax.text(xs[z] + 0.08, 0.75, f"実数 0 ↔ q={z}（zero-point z）", fontsize=17, color=C["b"], va="center")
ax.annotate("", xy=(xs[9], 0.3), xytext=(xs[8], 0.3), arrowprops=dict(arrowstyle="<->", color=C["c"], lw=2))
ax.text(xs[8] + s / 2, 0.42, f"scale s = {s:.3f}", color=C["c"], fontsize=17, ha="center", va="bottom")
ax.set_xlim(-2.0, 3.25)
ax.set_ylim(-1.3, 1.1)
ax.axis("off")
save(fig, os.path.join(CFIG, "scale-zeropoint.png"))

# ---- 概念図2: 丸め誤差とクリップ誤差（シミュレーションの計算例）----
import torch  # ex1_tensor.py と同じ乱数列（torch seed 0，外れ値20）
torch.manual_seed(0)
x = torch.randn(4096).numpy().astype(np.float64)
x[0] = 20.0
bits = 4
qmax = 2 ** (bits - 1) - 1
cs = np.linspace(1.0, 20.0, 200)
tot, rnd, clp = [], [], []
for c in cs:
    sc = c / qmax
    xc = np.clip(x, -c, c)
    q = np.clip(np.round(x / sc), -qmax - 1, qmax) * sc
    inside = np.abs(x) <= c
    tot.append(np.mean((q - x) ** 2))
    rnd.append(np.sum((q - x)[inside] ** 2) / x.size)
    clp.append(np.sum((q - x)[~inside] ** 2) / x.size)
fig, ax = plt.subplots(figsize=(12.4, 4.2))
ax.plot(cs, tot, color="k", lw=3, label="合計")
ax.plot(cs, rnd, color=C["a"], lw=2.5, label="丸め誤差（範囲内）")
ax.plot(cs, clp, color=C["b"], lw=2.5, label="クリップ誤差（範囲外）")
ib = int(np.argmin(tot))
ax.plot(cs[ib], tot[ib], "o", color="k", ms=10)
ax.annotate(f"最小: 範囲 ±{cs[ib]:.1f}", xy=(cs[ib], tot[ib]), xytext=(cs[ib] + 2.5, 0.45), fontsize=16, arrowprops=dict(arrowstyle="->"))
ax.annotate("minmax（±20）", xy=(20, tot[-1]), xytext=(15.5, 0.3), fontsize=16, arrowprops=dict(arrowstyle="->"))
ax.set_xlabel("量子化する範囲 ±c（対称 4bit）")
ax.set_ylabel("MSE")
ax.set_ylim(0, 1.25)
ax.legend(loc="upper left", ncol=1)
ax.set_title("計算例: 演習①と同じ入力（torch seed 0，外れ値20）を範囲ごとに量子化（実測の表ではなく再計算）", fontsize=15)
fig.tight_layout()
save(fig, os.path.join(CFIG, "round-clip-tradeoff.png"))
print("min c", cs[ib], tot[ib], "minmax", tot[-1])
for c0 in (2.5, 3.0, 3.5):
    k = int(np.argmin(np.abs(cs - c0)))
    print(c0, cs[k], tot[k])

# ---- 概念図3: 粒度 ----
fig, axs = plt.subplots(1, 3, figsize=(12.4, 3.6))
rows, cols = 6, 8
pal = plt.cm.tab10.colors
titles = ["per-tensor\nscale は1つ", "per-channel（出力チャネル）\nscale は行ごと", "per-group（例: 4列ずつ）\nscale は行×グループ"]
for k, ax in enumerate(axs):
    for r in range(rows):
        for c in range(cols):
            idx = 0 if k == 0 else (r if k == 1 else r * 2 + c // 4)
            ax.add_patch(plt.Rectangle((c, rows - 1 - r), 1, 1, fc=pal[idx % 10], ec="w", lw=1.5, alpha=0.85))
    ax.set_xlim(0, cols)
    ax.set_ylim(0, rows)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(titles[k], fontsize=15)
fig.text(0.5, -0.02, "重み行列（行: 出力チャネル，列: 入力側）の模式図．同じ色は同じ scale を共有．演習②の per-group は 64 個ずつ", ha="center", fontsize=14)
fig.tight_layout()
save(fig, os.path.join(CFIG, "granularity.png"))

# ---- 概念図4: 一様と非一様の格子（模式図）----
fig, axs = plt.subplots(2, 1, figsize=(12.4, 2.8), sharex=True)
uni = np.linspace(0, 8, 17)
nonu = np.array([0] + [2.0 ** e * (1 + m / 4) for e in range(-3, 3) for m in range(4)])
nonu = nonu[nonu <= 8]
for ax, g, lab, col in ((axs[0], uni, "一様（INT）: 間隔が同じ", C["a"]), (axs[1], nonu, "非一様（FP や NF4 の考え方）: 0 付近が細かい", C["b"])):
    ax.vlines(g, 0, 1, color=col, lw=2)
    ax.set_ylim(0, 1.4)
    ax.text(8.1, 0.5, lab, fontsize=16, va="center")
    ax.axis("off")
axs[1].set_xlim(-0.2, 15)
fig.text(0.5, 0.0, "説明用の模式図（実際の E4M3・NF4 の値ではない）", ha="center", fontsize=14)
save(fig, os.path.join(CFIG, "nonuniform-grid.png"))

# ---- 概念図5: STE ----
fig, axs = plt.subplots(1, 2, figsize=(12.4, 3.8))
y = np.linspace(-3, 3, 600)
axs[0].plot(y, np.round(y), color=C["a"], lw=3, label="順伝播: round(y)")
axs[0].plot(y, y, color=C["g"], lw=2, ls="--", label="STE が逆伝播で仮定: y")
axs[0].legend(loc="upper left", fontsize=14)
axs[0].set_xlabel("y")
axs[0].set_title("順伝播と逆伝播で別の関数とみなす")
axs[1].plot(y, np.zeros_like(y), color=C["a"], lw=3, label="round の本当の勾配（ほぼ至る所 0）")
axs[1].plot(y, np.ones_like(y), color=C["b"], lw=3, label="STE の勾配（1）")
axs[1].set_ylim(-0.3, 1.5)
axs[1].legend(loc="center right", fontsize=14)
axs[1].set_xlabel("y")
axs[1].set_title("勾配")
fig.tight_layout()
save(fig, os.path.join(CFIG, "ste.png"))
