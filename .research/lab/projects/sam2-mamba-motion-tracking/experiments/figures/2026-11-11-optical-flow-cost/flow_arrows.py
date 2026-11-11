"""Explanatory figure: move the object at t by each method's flow and compare with the object at t+1 (2026-11-11).

Methods: Farneback / DIS ultrafast (CPU) and RAFT small (GPU), all computed at 1024x1024. Each method panel shows
frame t (dimmed), the GT object outline at t (yellow) and at t+1 (cyan, dashed), and the GT mask at t moved by the
flow (orange; every pixel is moved by the flow at that pixel, then small holes are closed). The arrow goes from the
centroid of the object at t to the centroid of the moved object. If the orange region sits on the cyan outline, the
flow got the motion right. Slow pair is cropped around the object. Panel titles give only the method and CPU/GPU;
the times are in the experiment log and the MTG materials table. A one-line legend sits under the panels.

Usage (RAFT runs on cuda:0):
  CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=0 python flow_arrows.py --out 05-flow-moved-object.png
"""
import argparse
import numpy as np
import cv2
from PIL import Image
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

from flow_cost import R
from flow_viz import compute

rcParams["font.family"] = "Noto Sans CJK JP"
PAIRS = [("24df9789", 3, 1, "速く動く車", False), ("198021ad", 11, 1, "ゆっくり動くバス（拡大）", True)]
METHODS = [("farneback", "Farneback", "CPU"), ("ultrafast", "DIS 最速の設定", "CPU"), ("raft_small", "RAFT small", "GPU")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    fig, axes = plt.subplots(len(PAIRS), 2 + len(METHODS), figsize=(19, 2.55 * len(PAIRS) + 0.7))
    for i, (vid, t, oid, label, crop) in enumerate(PAIRS):
        a = cv2.imread(f"{R}/JPEGImages/{vid}/{t:05d}.jpg")
        b = cv2.imread(f"{R}/JPEGImages/{vid}/{t + 1:05d}.jpg")
        m0 = np.array(Image.open(f"{R}/Annotations/{vid}/{t:05d}.png")) == oid
        m1 = np.array(Image.open(f"{R}/Annotations/{vid}/{t + 1:05d}.png")) == oid
        H, W = m0.shape
        if crop:
            ys, xs = np.nonzero(m0 | m1)
            x0, x1 = max(0, xs.min() - 80), min(W, xs.max() + 80)
            y0, y1 = max(0, ys.min() - 60), min(H, ys.max() + 60)
        else:
            x0, x1, y0, y1 = 0, W, 0, H
        for j, (im, m, col, ttl) in enumerate([(a, m0, "yellow", "フレーム t"), (b, m1, "cyan", "次のフレーム t+1")]):
            ax = axes[i, j]
            ax.imshow(cv2.cvtColor(im, cv2.COLOR_BGR2RGB))
            ax.contour(m, levels=[0.5], colors=col, linewidths=1.5)
            ax.set_xlim(x0, x1); ax.set_ylim(y1, y0)
            ax.set_title(ttl, fontsize=12)
        axes[i, 0].set_ylabel(f"{label}", fontsize=12)
        ys, xs = np.nonzero(m0)
        for k, (meth, name, dev) in enumerate(METHODS):
            f = compute(a, b, meth, (1024, 1024))  # HxWx2 at 1024, in cells
            fn = cv2.resize(f, (W, H), interpolation=cv2.INTER_LINEAR)
            u, v = fn[..., 0] * W / 64, fn[..., 1] * H / 64  # cells -> native px
            xt = np.clip(np.round(xs + u[ys, xs]).astype(int), 0, W - 1)
            yt = np.clip(np.round(ys + v[ys, xs]).astype(int), 0, H - 1)
            moved = np.zeros((H, W), np.uint8)
            moved[yt, xt] = 1
            moved = cv2.morphologyEx(moved, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8)) > 0
            ax = axes[i, 2 + k]
            ax.imshow(cv2.cvtColor(a, cv2.COLOR_BGR2RGB), alpha=0.4)
            ax.set_facecolor("black")
            over = np.zeros((H, W, 4)); over[moved] = (1.0, 0.35, 0.0, 0.6)
            ax.imshow(over)
            ax.contour(m0, levels=[0.5], colors="yellow", linewidths=1.5)
            ax.contour(m1, levels=[0.5], colors="cyan", linewidths=1.8, linestyles="dashed")
            ax.annotate("", xy=(xt.mean(), yt.mean()), xytext=(xs.mean(), ys.mean()),
                        arrowprops=dict(arrowstyle="-|>", color="white", lw=2.2, mutation_scale=18))
            ax.set_xlim(x0, x1); ax.set_ylim(y1, y0)
            ax.set_title(f"{name}（{dev}）", fontsize=12)
        for ax in axes[i]:
            ax.set_xticks([]); ax.set_yticks([])
    handles = [Line2D([], [], color="yellow", lw=2, label="フレーム t の物体"),
               Line2D([], [], color="cyan", lw=2, ls="--", label="t+1 の物体（本当の位置）"),
               Patch(facecolor=(1.0, 0.35, 0.0, 0.6), label="flow で動かした結果"),
               Line2D([], [], color="white", lw=2, marker=">", markersize=7, label="重心の移動")]
    leg = fig.legend(handles=handles, loc="lower center", ncol=4, fontsize=12, frameon=True,
                     facecolor="dimgray", edgecolor="none", labelcolor="white")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    fig.savefig(args.out, dpi=100)


if __name__ == "__main__":
    main()
