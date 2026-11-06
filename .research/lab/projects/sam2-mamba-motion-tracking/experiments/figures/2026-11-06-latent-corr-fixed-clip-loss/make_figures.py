"""①-b（v3_corr）とA'の固定した200区間のloss。10/30 MTG資料の図04、11/6の②・②'の図と同じ形式。

入力は SAM2 repo `/mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2/runs/short_clip/diag_loss_curve_corr/per_clip.jsonl`
（F0・A・②・②'は `diag_loss_curve_spatial/per_clip.jsonl` のコピー、A'・①-bは `scripts/loss_fixed_clips.py` で追加。RTX PRO 4500）。
出力は図と、同じ区間どうしの差の集計 `paired_diffs.json`（F0との差、A'との差、Aとの差、mix・box、epochごと。
22 epochの①-b − A' の区間、lossが100を超える区間）。

SAM2 repo の `.venv-sam2/bin/python -I make_figures.py` で実行する。
"""
import json
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.family"] = "Noto Sans CJK JP"
OUT = Path(__file__).resolve().parent
SRC = Path("/mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2/runs/short_clip/diag_loss_curve_corr/per_clip.jsonl")

MODELS = ("A", "Ap", "Bcorr", "A_rw", "A_sml1")
MAIN = ("A", "Ap", "Bcorr")
# A・②・②'は11/6の図と同じ色。A'はAと同じモデル（学習のGPUだけ違う）なので同じ色の破線
COLOR = {"A": "#2a78d6", "Ap": "#2a78d6", "Bcorr": "#6f42c1", "A_rw": "#eb6834", "A_sml1": "#1baf7a"}
MARK = {"A": "o", "Ap": "D", "Bcorr": "^", "A_rw": "s", "A_sml1": "v"}
SHORT = {"A": "A", "Ap": "A'", "Bcorr": "①-b", "A_rw": "②", "A_sml1": "②'"}
LABEL = {"A": "A（F0→V3、PRO 4500で学習）", "Ap": "A'（Aと同じ設定、A4000で学習）",
         "Bcorr": "①-b（V3＋stateを対応で運ぶ、A4000で学習）", "A_rw": "②（参考）", "A_sml1": "②'（参考）"}
INK, MUTED, GRID, BG = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"


def style(ax):
    ax.set_facecolor(BG)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelsize=8)
    ax.grid(color=GRID, lw=0.8)
    ax.set_axisbelow(True)


def load():
    rows = [json.loads(l) for l in SRC.read_text().splitlines()]
    return {(r["model"], r["epoch"]): {m: np.array(r[m]) for m in ("mix", "box")} for r in rows}


def diff_stats(d):
    return {"median_diff": float(np.median(d)), "share_lower": float(np.mean(d < 0)),
            "q10_diff": float(np.quantile(d, 0.1)), "q90_diff": float(np.quantile(d, 0.9))}


def boot_median(d, n=10_000, seed=123):
    idx = np.random.default_rng(seed).integers(0, len(d), (n, len(d)))
    lo, hi = np.quantile(np.median(d[idx], axis=1), [0.025, 0.975])
    return {"median_diff": float(np.median(d)), "ci95": [float(lo), float(hi)], "n_boot": n, "seed": seed}


def paired(loss):
    """F0との差、A'との差・Aとの差（同じepoch）の中央値など。mix・box、epochごと。"""
    f0 = loss[("F0", 0)]
    out = {"n_clips": int(len(f0["mix"])), "F0_median": {m: float(np.median(f0[m])) for m in f0},
           "vs_F0": {}, "vs_Ap": {}, "vs_A": {}, "boot_ep22": {}, "loss_gt_100": {}}
    for c in MODELS:
        for e in sorted(e for (m, e) in loss if m == c):
            x = loss[(c, e)]
            for mode in ("mix", "box"):
                d = x[mode] - f0[mode]
                out["vs_F0"].setdefault(c, {}).setdefault(mode, {})[e] = {
                    "median_loss": float(np.median(x[mode])), **diff_stats(d),
                    "p90_diff": float(np.quantile(d, 0.9)), "max_loss": float(x[mode].max()),
                    "n_loss_gt_10": int((x[mode] > 10).sum())}
                big = np.where(x[mode] > 100)[0]
                if len(big):
                    out["loss_gt_100"].setdefault(c, {}).setdefault(mode, {})[e] = {
                        int(i): float(x[mode][i]) for i in big}
                for ref, key in (("Ap", "vs_Ap"), ("A", "vs_A")):
                    if c not in (ref, "A_rw", "A_sml1") and (ref, e) in loss and not (c == "A" and ref == "Ap"):
                        out[key].setdefault(c, {}).setdefault(mode, {})[e] = diff_stats(x[mode] - loss[(ref, e)][mode])
    for c, ref in (("Bcorr", "Ap"), ("Bcorr", "A"), ("Ap", "A")):
        for mode in ("mix", "box"):
            out["boot_ep22"].setdefault(f"{c}-{ref}", {})[mode] = boot_median(loss[(c, 22)][mode] - loss[(ref, 22)][mode])
    return out


def fig_fixed_clip(loss):
    f0 = loss[("F0", 0)]["mix"]
    fig, ax = plt.subplots(figsize=(7.2, 4.2), dpi=200)
    fig.patch.set_facecolor(BG)
    style(ax)
    ax.axhline(0, color=MUTED, lw=1)
    for c in MAIN + ("A_rw", "A_sml1"):
        pts = sorted((e, np.median(loss[(m, e)]["mix"] - f0)) for (m, e) in loss if m == c)
        e = [0] + [p[0] for p in pts]
        y = [0.0] + [p[1] for p in pts]
        main = c in MAIN
        ax.plot(e, y, color=COLOR[c], lw=2 if main else 1, ls="--" if c == "Ap" else "-", marker=MARK[c],
                ms=5 if main else 3, mec=BG, mew=1, alpha=1 if main else 0.35, label=LABEL[c], zorder=3 if main else 2)
        if main:  # 薄い②・②'は凡例だけ（終点のラベルが重なるため）
            ax.annotate(SHORT[c], (e[-1], y[-1]), xytext=(6, 0), textcoords="offset points", fontsize=8,
                        color=INK, va="center")
    ax.set_xlabel("epoch（0は初期値のF0）", fontsize=8.5, color=MUTED)
    ax.set_ylabel("F0との差の中央値（同じ区間どうし）", fontsize=8.5, color=MUTED)
    ax.legend(fontsize=7, frameon=False, loc="upper right")
    ax.set_title(TITLE, fontsize=10, color=INK, loc="left")
    fig.text(0.01, 0.01, "trainの動画のうち学習に使っていない8フレームの区間200個、学習と同じプロンプトの混合（mix）。lossの計算はすべてRTX PRO 4500。\n"
             "source: runs/short_clip/diag_loss_curve_corr/per_clip.jsonl（F0・A・②・②'は diag_loss_curve_spatial と同じ値）", fontsize=6.5, color=MUTED)
    fig.subplots_adjust(left=0.11, right=0.95, top=0.90, bottom=0.18)
    fig.savefig(OUT / "01-fixed-clip-loss.png", facecolor=BG)


TITLE = "固定した200区間のloss：①-bもA'と同じように下がり、A'との差はほぼ0"

if __name__ == "__main__":
    loss = load()
    summary = paired(loss)
    (OUT / "paired_diffs.json").write_text(json.dumps(summary, indent=1, ensure_ascii=False) + "\n")
    fig_fixed_clip(loss)
    for key in ("vs_Ap", "vs_A"):
        for c, modes in summary[key].items():
            for mode, by_e in modes.items():
                print(c, key, mode, " ".join(f"{e}:{v['median_diff']:+.4f}" for e, v in by_e.items()))
    for k, v in summary["boot_ep22"].items():
        for mode, b in v.items():
            print("ep22", k, mode, f"{b['median_diff']:+.4f} [{b['ci95'][0]:+.4f}, {b['ci95'][1]:+.4f}]")
