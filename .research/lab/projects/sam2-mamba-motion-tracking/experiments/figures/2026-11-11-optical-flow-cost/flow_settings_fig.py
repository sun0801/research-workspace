"""Revised explanatory figure (2026-11-13): move the object by the flow with several settings.

Replaces the reading of 05-flow-moved-object.png, which used only the default settings (Farneback with 3 pyramid
levels cannot follow a 150-pixel motion). Same two pairs as flow_arrows.py. Everything is computed on the
1024x1024 input (as flow_sweep.py) and drawn back at the native aspect ratio:
  yellow = object at t, cyan dashed = object at t+1, orange = object at t moved by the flow (every pixel moved,
  pixels leaving the image dropped, 9x9 closing). Panel titles give the method and its setting.

  CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=0 python flow_settings_fig.py --out 06-flow-moved-object-settings.png
"""
import argparse

import cv2
import matplotlib
import numpy as np
import torch
from PIL import Image

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

from flow_cost import R
from flow_raft import load, raft_flow, to_input
from flow_sweep import CPU

rcParams["font.family"] = "Noto Sans CJK JP"
S = 1024
PAIRS = [("24df9789", 3, 1, "速く動く車", False), ("198021ad", 11, 1, "ゆっくり動くバス（拡大）", True)]
PANELS = [("farneback_L3_w15", "Farneback\nピラミッド3段（前回の設定）"), ("farneback_L7_w21", "Farneback\nピラミッド7段"),
          ("dis_ultrafast", "DIS\n最速の設定"), ("dis_medium", "DIS\nmedium"), ("raft_large", "RAFT large\n（GPU）")]


def moved(flow, m0):
    ys, xs = np.nonzero(m0)
    xt = np.round(xs + flow[ys, xs, 0]).astype(int)
    yt = np.round(ys + flow[ys, xs, 1]).astype(int)
    ok = (xt >= 0) & (xt < S) & (yt >= 0) & (yt < S)
    mv = np.zeros((S, S), np.uint8)
    mv[yt[ok], xt[ok]] = 1
    return cv2.morphologyEx(mv, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8)) > 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    assert "RTX A4000" in torch.cuda.get_device_name(0), "set CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=0"
    raft = load("raft_large", torch.device("cuda"))[0]
    fig, axes = plt.subplots(len(PAIRS), 2 + len(PANELS), figsize=(22, 2.7 * len(PAIRS) + 1.0))
    for i, (vid, t, oid, label, crop) in enumerate(PAIRS):
        a = cv2.imread(f"{R}/JPEGImages/{vid}/{t:05d}.jpg")
        b = cv2.imread(f"{R}/JPEGImages/{vid}/{t + 1:05d}.jpg")
        H, W = a.shape[:2]
        lab = lambda k: cv2.resize(np.array(Image.open(f"{R}/Annotations/{vid}/{k:05d}.png")), (S, S),
                                   interpolation=cv2.INTER_NEAREST) == oid
        m0, m1 = lab(t), lab(t + 1)
        ga, gb = (cv2.cvtColor(cv2.resize(x, (S, S), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY) for x in (a, b))
        gx, gy = (np.arange(S) + 0.5) * W / S, (np.arange(S) + 0.5) * H / S  # 1024 grid -> native coords
        ext = [0, W, H, 0]  # draw the 1024x1024 maps back at the native aspect ratio
        if crop:
            ys, xs = np.nonzero(m0 | m1)
            x0, x1 = max(0, xs.min() * W / S - 80), min(W, xs.max() * W / S + 80)
            y0, y1 = max(0, ys.min() * H / S - 60), min(H, ys.max() * H / S + 60)
        else:
            x0, x1, y0, y1 = 0, W, 0, H
        for j, (im, m, col, ttl) in enumerate([(a, m0, "yellow", "フレーム t"), (b, m1, "cyan", "次のフレーム t+1")]):
            ax = axes[i, j]
            ax.imshow(cv2.cvtColor(im, cv2.COLOR_BGR2RGB))
            ax.contour(gx, gy, m, levels=[0.5], colors=col, linewidths=1.5)
            ax.set_xlim(x0, x1); ax.set_ylim(y1, y0)
            ax.set_title(ttl, fontsize=12)
        axes[i, 0].set_ylabel(label, fontsize=12)
        for k, (name, ttl) in enumerate(PANELS):
            if name == "raft_large":
                f = raft_flow(raft, to_input(a, S, "cuda"), to_input(b, S, "cuda"), 12)[0].permute(1, 2, 0).cpu().numpy()
            else:
                f = CPU[name](ga, gb)
            mv = moved(f, m0)
            ax = axes[i, 2 + k]
            ax.imshow(cv2.cvtColor(a, cv2.COLOR_BGR2RGB), alpha=0.4)
            ax.set_facecolor("black")
            over = np.zeros((S, S, 4)); over[mv] = (1.0, 0.35, 0.0, 0.6)
            ax.imshow(over, extent=ext)
            ax.contour(gx, gy, m0, levels=[0.5], colors="yellow", linewidths=1.5)
            ax.contour(gx, gy, m1, levels=[0.5], colors="cyan", linewidths=1.8, linestyles="dashed")
            ax.set_xlim(x0, x1); ax.set_ylim(y1, y0)
            ax.set_title(ttl, fontsize=12)
        for ax in axes[i]:
            ax.set_xticks([]); ax.set_yticks([])
    handles = [Line2D([], [], color="yellow", lw=2, label="フレーム t の物体"),
               Line2D([], [], color="cyan", lw=2, ls="--", label="t+1 の物体（本当の位置）"),
               Patch(facecolor=(1.0, 0.35, 0.0, 0.6), label="t の物体の各画素を flow で動かした結果")]
    fig.legend(handles=handles, loc="lower center", ncol=3, fontsize=12, frameon=True,
               facecolor="dimgray", edgecolor="none", labelcolor="white")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    fig.savefig(args.out, dpi=100)


if __name__ == "__main__":
    main()
