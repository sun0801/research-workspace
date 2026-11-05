"""空間混合（②・②'）の固定した200区間のloss。10/30 MTG資料の図04と同じ形式。

入力は SAM2 repo `/mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2/runs/short_clip/diag_loss_curve_spatial/per_clip.jsonl`
（F0・A・B・Cは `diag_loss_curve/per_clip.jsonl` のコピー、②・②'は `scripts/loss_fixed_clips.py` で追加。RTX PRO 4500）。
出力は図と、同じ区間どうしの差の集計 `paired_diffs.json`（F0との差、Aとの差、mix・box、epochごと）。

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
SRC = Path("/mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2/runs/short_clip/diag_loss_curve_spatial/per_clip.jsonl")

# 10/30の図と同じ参照パレットの順番。この図ではA・②・②'の3条件に順に割り当てる
COLOR = {"A": "#2a78d6", "A_rw": "#eb6834", "A_sml1": "#1baf7a"}
MARK = {"A": "o", "A_rw": "s", "A_sml1": "^"}
SHORT = {"A": "A", "A_rw": "②", "A_sml1": "②'"}
LABEL = {"A": "A（F0→V3）", "A_rw": "②（V3＋読み書きの空間conv）", "A_sml1": "②'（V3＋stateの空間混合、L1正規化）"}
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


def paired(loss):
    """F0との差、Aとの差（同じepoch）の中央値など。mix・box、epochごと。"""
    f0 = loss[("F0", 0)]
    out = {"n_clips": int(len(f0["mix"])), "F0_median": {m: float(np.median(f0[m])) for m in f0}, "vs_F0": {}, "vs_A": {}}
    for c in ("A", "A_rw", "A_sml1"):
        for e in sorted(e for (m, e) in loss if m == c):
            x = loss[(c, e)]
            for mode in ("mix", "box"):
                d = x[mode] - f0[mode]
                out["vs_F0"].setdefault(c, {}).setdefault(mode, {})[e] = {
                    "median_loss": float(np.median(x[mode])), "median_diff": float(np.median(d)),
                    "share_lower": float(np.mean(d < 0)), "p90_diff": float(np.quantile(d, 0.9)),
                    "max_loss": float(x[mode].max()), "n_loss_gt_10": int((x[mode] > 10).sum())}
                if c != "A" and ("A", e) in loss:
                    da = x[mode] - loss[("A", e)][mode]
                    out["vs_A"].setdefault(c, {}).setdefault(mode, {})[e] = {
                        "median_diff": float(np.median(da)), "share_lower": float(np.mean(da < 0)),
                        "q10_diff": float(np.quantile(da, 0.1)), "q90_diff": float(np.quantile(da, 0.9))}
    return out


def fig_fixed_clip(loss):
    f0 = loss[("F0", 0)]["mix"]
    fig, ax = plt.subplots(figsize=(7.2, 4.2), dpi=200)
    fig.patch.set_facecolor(BG)
    style(ax)
    ax.axhline(0, color=MUTED, lw=1)
    for c in ("A", "A_rw", "A_sml1"):
        pts = sorted((e, np.median(loss[(m, e)]["mix"] - f0)) for (m, e) in loss if m == c)
        e = [0] + [p[0] for p in pts]
        y = [0.0] + [p[1] for p in pts]
        ax.plot(e, y, color=COLOR[c], lw=2, marker=MARK[c], ms=5, mec=BG, mew=1, label=LABEL[c])
        ax.annotate(SHORT[c], (e[-1], y[-1]), xytext=(6, 0), textcoords="offset points", fontsize=8, color=INK, va="center")
    ax.set_xlabel("epoch（0は初期値のF0）", fontsize=8.5, color=MUTED)
    ax.set_ylabel("F0との差の中央値（同じ区間どうし）", fontsize=8.5, color=MUTED)
    ax.legend(fontsize=7.5, frameon=False, loc="upper right")
    ax.set_title(TITLE, fontsize=10, color=INK, loc="left")
    fig.text(0.01, 0.01, "trainの動画のうち学習に使っていない8フレームの区間200個、学習と同じプロンプトの混合（mix）。RTX PRO 4500。\n"
             "source: runs/short_clip/diag_loss_curve_spatial/per_clip.jsonl（F0・Aは diag_loss_curve と同じ値）", fontsize=6.5, color=MUTED)
    fig.subplots_adjust(left=0.11, right=0.95, top=0.90, bottom=0.18)
    fig.savefig(OUT / "01-fixed-clip-loss.png", facecolor=BG)


TITLE = "固定した200区間のloss：②・②'もAと同じように下がる"

if __name__ == "__main__":
    loss = load()
    summary = paired(loss)
    (OUT / "paired_diffs.json").write_text(json.dumps(summary, indent=1, ensure_ascii=False) + "\n")
    fig_fixed_clip(loss)
    for c, modes in summary["vs_A"].items():
        for mode, by_e in modes.items():
            print(c, "-A", mode, " ".join(f"{e}:{v['median_diff']:+.4f}" for e, v in by_e.items()))
