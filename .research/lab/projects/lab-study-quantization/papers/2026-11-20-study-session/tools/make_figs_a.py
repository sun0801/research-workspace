"""案Aの図を作る。概念図 -> figures/a/，実験由来の図 -> experiments/figures/（案A用の名前）。CPU・既存JSONのみ。
使い方: pptvenv/bin/python make_figs_a.py a_data.json
"""
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Rectangle  # noqa: E402

plt.rcParams["font.family"] = "Noto Sans CJK JP"
plt.rcParams["font.size"] = 16
plt.rcParams["axes.unicode_minus"] = False
P = "/mnt/HDD10TB-2/aburatani/research-workspace/.research/lab/projects/lab-study-quantization"
FIG = f"{P}/papers/2026-11-20-study-session/figures/a"
EXP = f"{P}/experiments/figures"
RES = "/mnt/HDD10TB-2/aburatani/quantization_handson/results"
os.makedirs(FIG, exist_ok=True)
D = json.load(open(sys.argv[1]))
BLUE, RED, GRAY, GREEN, ORANGE = "#2c6fbb", "#c0392b", "#888888", "#2e8b57", "#e08a1e"


def save(fig, path):
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def box(ax, x, y, w, h, text, fc="#eef3fa", ec=BLUE, fs=16, bold=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08", fc=fc, ec=ec, lw=2))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, fontweight="bold" if bold else None)


# 1. 積み上げ地図
fig, ax = plt.subplots(figsize=(11, 4.6))
ax.axis("off")
ax.set_xlim(0, 10)
ax.set_ylim(0, 5.7)
labs = ["数値表現", "一様量子化", "粒度", "較正", "手法"]
sub = ["INT8/INT4\nFP8/NF4", "scale\nzero-point\n丸めとクリップ", "per-tensor\nper-channel\nper-group", "minmax\npercentile\nMSE",
       "STE\nSmoothQuant\n分類表"]
ex = ["", "演習①", "演習②", "演習③", "演習④"]
for i in range(5):
    h = 0.9 + 0.75 * i
    ax.add_patch(Rectangle((i * 2, 0.2), 1.85, h + 1.2, fc=plt.cm.Blues(0.25 + 0.14 * i), ec=BLUE, lw=2))
    tc = "white" if i >= 2 else "black"
    ax.text(i * 2 + 0.92, 0.2 + h + 0.85, labs[i], ha="center", va="center", fontsize=17, fontweight="bold", color=tc)
    ax.text(i * 2 + 0.92, 0.2 + 0.85, sub[i], ha="center", va="center", fontsize=14, color=tc)
    if ex[i]:
        ax.text(i * 2 + 0.92, 0.2 + h + 1.5, ex[i], ha="center", va="center", fontsize=16, color=RED, fontweight="bold")
save(fig, f"{FIG}/a-stack-map.png")

# 2. fake-quant と 実際の低精度実行
fig, ax = plt.subplots(figsize=(11, 4.4))
ax.axis("off")
ax.set_xlim(0, 11)
ax.set_ylim(0, 4.4)
ax.text(0.1, 4.0, "fake-quant（演習①②③）: 誤差の模擬", fontsize=18, fontweight="bold", color=BLUE)
for i, (t, fc) in enumerate([("FP32 の値 x", "#eef3fa"), ("量子化\nround・clamp", "#fdf1d8"), ("すぐ逆量子化\nx' = s(q−z)", "#fdf1d8"),
                             ("FP32 で計算", "#eef3fa")]):
    box(ax, 0.1 + i * 2.7, 2.7, 2.2, 1.0, t, fc=fc, fs=15)
    if i:
        ax.annotate("", xy=(0.1 + i * 2.7, 3.2), xytext=(0.1 + i * 2.7 - 0.5, 3.2), arrowprops=dict(arrowstyle="->", lw=2))
ax.text(0.1, 2.25, "精度の変化は分かる，速度・メモリは改善しない（むしろ遅くなりうる）", fontsize=16, color=BLUE)
ax.text(0.1, 1.75, "実際の低精度実行（演習④）: 低ビットで保存し，対応する kernel で計算", fontsize=18, fontweight="bold", color=RED)
for i, (t, fc) in enumerate([("INT8 / INT4 で保存", "#fbe4e0"), ("低精度 kernel\nで計算", "#fbe4e0")]):
    box(ax, 0.1 + i * 3.6, 0.45, 3.0, 0.9, t, fc=fc, ec=RED, fs=15)
    if i:
        ax.annotate("", xy=(0.1 + i * 3.6, 0.9), xytext=(0.1 + i * 3.6 - 0.6, 0.9), arrowprops=dict(arrowstyle="->", lw=2))
ax.text(7.5, 0.9, "サイズ・速度・メモリが\n実際に変わるかを見る", fontsize=16, va="center")
save(fig, f"{FIG}/a-fakequant-vs-real.png")

# 3. 一様グリッドと計算例（4bit 非対称，範囲 [-1.0, 3.0]）
lo, hi, b = -1.0, 3.0, 4
s = (hi - lo) / (2 ** b - 1)
z = int(round(-lo / s))
xs = 0.5
q = int(np.clip(round(xs / s) + z, 0, 2 ** b - 1))
xh = s * (q - z)
json.dump(dict(s=s, z=z, q=q, xh=xh, err=xh - xs), open(f"{FIG}/a-affine-example.json", "w"))
fig, ax = plt.subplots(figsize=(11, 3.6))
grid = [s * (k - z) for k in range(2 ** b)]
ax.hlines(0, -1.3, 3.3, color="k", lw=1)
ax.vlines(grid, -0.12, 0.12, color=BLUE, lw=2)
for k, g in enumerate(grid):
    ax.text(g, -0.38, str(k), ha="center", fontsize=13, color=BLUE)
ax.plot([xs], [0], "o", color=RED, ms=11)
ax.plot([xh], [0.0], "|", color=GREEN, ms=34, mew=3)
ax.text(xs, 0.5, "x = 0.5", ha="center", color=RED, fontsize=17)
ax.text(xh, 0.95, f"x' = {xh:.3f}\n(q = {q})", ha="center", color=GREEN, fontsize=17)
ax.plot([0], [0], "v", color="k", ms=10)
ax.text(0, -0.9, f"実数 0 ↔ 整数 z = {z}", ha="center", fontsize=17)
ax.set_xlim(-1.35, 3.35)
ax.set_ylim(-1.2, 2.3)
ax.axis("off")
ax.text(-1.3, 2.05, f"4bit（16個の格子点，青）  s = (3.0−(−1.0))/15 = {s:.3f}，z = round(1.0/{s:.3f}) = {z}", fontsize=16)
save(fig, f"{FIG}/a-affine-grid.png")

# 4. 対称 vs 非対称（ReLU 後の範囲 [0, 6]，4bit）
fig, axs = plt.subplots(2, 1, figsize=(11, 3.6), sharex=True)
for ax, ttl, qs, sc, zz in ((axs[0], "対称・符号付き（z=0，整数 −8〜7）", range(-8, 8), 6 / 7, 0),
                            (axs[1], "非対称・符号なし（整数 0〜15）", range(0, 16), 6 / 15, 0)):
    g = [sc * (k - zz) for k in qs]
    ax.vlines(g, -0.2, 0.2, color=BLUE, lw=2)
    ax.axvspan(0, 6, color="#fdf1d8", alpha=0.7)
    ax.set_title(ttl, fontsize=16, loc="left")
    ax.set_yticks([])
    ax.set_ylim(-0.4, 0.5)
    for sp in ("left", "right", "top"):
        ax.spines[sp].set_visible(False)
axs[1].set_xlabel("値（黄色はデータの範囲 0〜6，ReLU 後を想定）")
axs[0].text(-6.9, 0.3, "負側の格子点は使われない", fontsize=15, color=RED, va="center")
fig.subplots_adjust(hspace=0.7)
save(fig, f"{FIG}/a-sym-asym.png")

# 5. 丸め誤差とクリップ誤差（計算例）
T = D["tradeoff"]
fig, ax = plt.subplots(figsize=(11, 4.6))
ax.plot(T["c"], T["rounding"], color=BLUE, lw=3, label="丸め誤差（範囲内）")
ax.plot(T["c"], T["clipping"], color=RED, lw=3, label="クリップ誤差（範囲外）")
ax.plot(T["c"], T["total"], color="k", lw=3, ls="--", label="合計 MSE")
ax.set_xlabel("クリップ範囲 c（[−c, c]，4bit 対称）")
ax.set_ylabel("MSE")
ax.set_ylim(0, 0.1)
ax.legend(fontsize=15)
ax.grid(alpha=0.3)
save(fig, f"{FIG}/a-round-clip.png")

# 6. 演習①の計算例: ビット数と SQNR
fig, ax = plt.subplots(figsize=(11, 4.4))
for tag, c, lab in (("plain", BLUE, "N(0,1) の 4096 個"), ("outlier20", RED, "同じ 4096 個の1つを 20 にする")):
    rows = [r for r in D[tag] if r["sym"]]
    ax.plot([r["bits"] for r in rows], [r["sqnr"] for r in rows], "o-", color=c, lw=3, ms=9, label=lab)
ax.invert_xaxis()
ax.set_xlabel("ビット数（対称・per-tensor）")
ax.set_ylabel("SQNR [dB]（大きいほど良い）")
ax.legend(fontsize=15)
ax.grid(alpha=0.3)
save(fig, f"{FIG}/a-ex1-sqnr.png")

# 7. 粒度の図
fig, axs = plt.subplots(1, 3, figsize=(11, 3.8))
rng = np.random.default_rng(0)
for ax, ttl, mode in zip(axs, ["per-tensor", "per-channel（出力チャネル）", "per-group（64 要素）"], range(3)):
    ax.set_xlim(0, 8)
    ax.set_ylim(0, 4)
    ax.invert_yaxis()
    cols = plt.cm.tab10.colors
    for r in range(4):
        for cc in range(8):
            idx = 0 if mode == 0 else (r if mode == 1 else r * 2 + cc // 4)
            ax.add_patch(Rectangle((cc, r), 1, 1, fc=cols[idx % 10], alpha=0.55, ec="white", lw=1.5))
    ax.set_title(ttl, fontsize=15)
    ax.set_xticks([])
    ax.set_yticks([])
axs[0].set_ylabel("出力チャネル")
fig.text(0.5, -0.03, "同じ色の要素が 1 組の scale を共有（入力側の軸 →）", ha="center", fontsize=15)
save(fig, f"{FIG}/a-granularity.png")

# 8. 較正3方法（計算例）
C = D["calib"]
xe = np.linspace(-25, 25, 121)
fig, ax = plt.subplots(figsize=(11, 4.6))
ax.bar(xe[:-1] + 25 / 120, np.where(np.array(C["hist"]) > 0, np.array(C["hist"]), np.nan), width=50 / 120, color="#b5c7e0", log=True)
for k, col, lab in (("minmax", RED, "minmax"), ("percentile", ORANGE, "percentile 99.99"), ("mse", GREEN, "MSE")):
    ax.axvline(C[k][0], color=col, lw=3)
    ax.axvline(C[k][1], color=col, lw=3, label=f"{lab}  MSE={C['err'][k]:.3f}")
ax.set_xlabel("活性の値（合成データ）")
ax.set_ylabel("個数（対数）")
ax.legend(fontsize=14, loc="upper right")
save(fig, f"{FIG}/a-calib-ranges.png")

# 9. BN folding
fig, ax = plt.subplots(figsize=(11, 3.6))
ax.axis("off")
ax.set_xlim(0, 11)
ax.set_ylim(0, 3.6)
box(ax, 0.1, 2.0, 2.0, 1.0, "Conv\nW, b", fs=16)
box(ax, 3.0, 2.0, 2.0, 1.0, "BN\nγ, β, μ, σ²", fs=16)
ax.annotate("", xy=(3.0, 2.5), xytext=(2.1, 2.5), arrowprops=dict(arrowstyle="->", lw=2))
ax.annotate("", xy=(6.3, 2.5), xytext=(5.0, 2.5), arrowprops=dict(arrowstyle="->", lw=3, color=RED))
ax.text(5.6, 2.9, "畳み込む", ha="center", fontsize=15, color=RED)
box(ax, 6.3, 2.0, 2.6, 1.0, "Conv\nW_fold, b_fold", fc="#fbe4e0", ec=RED, fs=16)
ax.text(0.1, 1.2, "出力チャネルごとに異なる γ・σ が重みに入る", fontsize=17)
ax.text(0.1, 0.5, "→ 量子化は W_fold に対して行う", fontsize=17, color=RED, fontweight="bold")
save(fig, f"{FIG}/a-bn-folding.png")

# 10. PTQ vs QAT
fig, ax = plt.subplots(figsize=(11, 4.2))
ax.axis("off")
ax.set_xlim(0, 11)
ax.set_ylim(0, 4.2)
ax.text(0.1, 3.8, "PTQ", fontsize=20, fontweight="bold", color=BLUE)
for i, t in enumerate(["学習済み FP32", "較正データを\n1 回流す", "scale・z を固定\nして量子化"]):
    box(ax, 0.1 + i * 3.4, 2.6, 2.7, 1.0, t, fs=15)
    if i:
        ax.annotate("", xy=(0.1 + i * 3.4, 3.1), xytext=(0.1 + i * 3.4 - 0.7, 3.1), arrowprops=dict(arrowstyle="->", lw=2))
ax.text(0.1, 2.0, "QAT", fontsize=20, fontweight="bold", color=RED)
for i, t in enumerate(["学習済み FP32", "fake-quant を挿入", "STE で逆伝播\n重みを更新", "量子化して\n推論"]):
    box(ax, 0.1 + i * 2.7, 0.5, 2.3, 1.2, t, fc="#fbe4e0", ec=RED, fs=15)
    if i:
        ax.annotate("", xy=(0.1 + i * 2.7, 1.1), xytext=(0.1 + i * 2.7 - 0.4, 1.1), arrowprops=dict(arrowstyle="->", lw=2))
save(fig, f"{FIG}/a-ptq-qat.png")

# 11. STE
fig, axs = plt.subplots(1, 2, figsize=(11, 3.8))
y = np.linspace(-3, 3, 600)
axs[0].plot(y, np.round(y), color=BLUE, lw=3)
axs[0].plot(y, y, color=GRAY, lw=1.5, ls=":")
axs[0].set_title("順伝播: round(y)", fontsize=16)
axs[1].plot(y, np.zeros_like(y), color=RED, lw=3, label="真の勾配（ほぼ至る所で 0）")
axs[1].plot(y, np.ones_like(y), color=GREEN, lw=3, ls="--", label="STE: 1 とみなす")
axs[1].set_ylim(-0.3, 1.6)
axs[1].legend(fontsize=13, loc="center right")
axs[1].set_title("逆伝播: ∂round(y)/∂y", fontsize=16)
for a in axs:
    a.grid(alpha=0.3)
save(fig, f"{FIG}/a-ste.png")

# ---- 実験由来の図（正本は experiments/figures/，案A用の名前）----
M = json.load(open(f"{RES}/ptq_table.json"))["models"]


def runs(model, **kw):
    return [r for r in M[model]["runs"] if all(r.get(k) == v for k, v in kw.items())]


fig, axs = plt.subplots(1, 2, figsize=(11, 4.4), sharey=True)
for ax, (m, ttl) in zip(axs, (("resnet18", "ResNet18"), ("deit_tiny", "DeiT-Tiny"))):
    for g, c, lab in (("per_tensor", RED, "per-tensor"), ("per_channel", BLUE, "per-channel"), ("per_group", GREEN, "per-group(64)")):
        rr = sorted(runs(m, table="weight_only", granularity=g), key=lambda r: -r["w_bits"])
        ax.plot([r["w_bits"] for r in rr], [r["acc"] for r in rr], "o-", color=c, lw=3, ms=8, label=lab)
    ax.axhline(M[m]["fp32"]["eval2000"], color=GRAY, ls="--")
    ax.set_title(ttl, fontsize=17)
    ax.set_xlabel("重みのビット数")
    ax.invert_xaxis()
    ax.grid(alpha=0.3)
axs[0].set_ylabel("精度 [%]（eval2000）")
axs[0].legend(fontsize=14, loc="lower left")
save(fig, f"{EXP}/2026-11-14-slides-a-weight-only-granularity.png")

fig, axs = plt.subplots(1, 2, figsize=(11, 4.4), sharey=True)
names = {"minmax": "minmax", "percentile": "percentile", "mse": "MSE"}
for ax, (m, ttl) in zip(axs, (("resnet18", "ResNet18"), ("deit_tiny", "DeiT-Tiny"))):
    xs = np.arange(3)
    for k, (cal, c) in enumerate((("minmax", RED), ("percentile", ORANGE), ("mse", GREEN))):
        vals = []
        for ab in (8, 6, 4):
            rr = [r for r in runs(m, table="w8_act", a_bits=ab) if r["calib"] == cal] or \
                 [r for r in M[m]["runs"] if r.get("w_bits") == 8 and r.get("a_bits") == ab and r.get("calib") == cal
                  and r.get("granularity") == "per_channel"]
            vals.append(rr[0]["acc"])
        ax.bar(xs + (k - 1) * 0.27, vals, 0.25, color=c, label=names[cal])
        for x0, v in zip(xs + (k - 1) * 0.27, vals):
            ax.text(x0, v + 1.5, f"{v:.1f}", ha="center", va="bottom", rotation=90, fontsize=15)
    ax.set_xticks(xs)
    ax.set_xticklabels(["A8", "A6", "A4"])
    ax.set_title(f"{ttl}（W8 per-channel）", fontsize=16)
    ax.set_ylim(0, 125)
    ax.set_yticks([0, 25, 50, 75, 100])
axs[0].set_ylabel("精度 [%]（eval2000）")
h_, l_ = axs[0].get_legend_handles_labels()
fig.legend(h_, l_, fontsize=15, loc="lower center", ncol=3, bbox_to_anchor=(0.5, -0.08))
save(fig, f"{EXP}/2026-11-14-slides-a-act-calibration.png")

Q = {m: json.load(open(f"{RES}/qat_{m}.json"))["models"][m] for m in ("resnet18", "deit_tiny")}
fig, axs = plt.subplots(1, 2, figsize=(11, 4.4))
for ax, (m, ttl) in zip(axs, (("resnet18", "ResNet18"), ("deit_tiny", "DeiT-Tiny"))):
    q = Q[m]
    vals = [q["fp32"], q["ptq"], np.mean(q["finetune_then_ptq"]), np.mean(q["qat"])]
    cols = [GRAY, RED, ORANGE, BLUE]
    ax.bar(range(4), vals, color=cols)
    tops = [vals[0], vals[1], max(q["finetune_then_ptq"]), max(q["qat"])]
    for i, v in enumerate(vals):
        ax.text(i, tops[i] + 0.25, f"{v:.2f}", ha="center", fontsize=15)
    ax.scatter([2] * 3, q["finetune_then_ptq"], color="k", s=14, zorder=3)
    ax.scatter([3] * 3, q["qat"], color="k", s=14, zorder=3)
    ax.set_xticks(range(4))
    ax.set_xticklabels(["FP32", "PTQ", "fine-tune\n→PTQ", "QAT"], fontsize=14)
    ax.set_ylim(88, 97)
    ax.set_title(f"{ttl}（W4 per-ch + A8 mse）", fontsize=15)
axs[0].set_ylabel("精度 [%]")
save(fig, f"{EXP}/2026-11-14-slides-a-qat.png")
print("ok")
