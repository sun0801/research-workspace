"""Visualise OpenCV flow (Farneback / DIS) on one frame pair per selected MOSE video (2026-11-11).

The pair is the one (within the first --pairs pairs) whose GT centroid step of the first object is closest to the
median step of that object. Flow parameters are the same as flow_cost.py.

Usage:
  python flow_viz.py --selection data/selected_videos.json --stratum fast --out 01-flow-fast.png
  python flow_viz.py --selection data/selected_videos.json --stratum slow --out 02-flow-slow.png
"""
import json
import argparse, os
import numpy as np
import cv2
from PIL import Image
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from flow_cost import R, FARNEBACK


def frames_of(vid):
    return sorted(f for f in os.listdir(f"{R}/JPEGImages/{vid}") if not f.startswith("."))


def flow_rgb(flow, vmax):
    mag, ang = cv2.cartToPolar(flow[..., 0], flow[..., 1])
    hsv = np.zeros(flow.shape[:2] + (3,), np.uint8)
    hsv[..., 0] = (ang * 90 / np.pi).astype(np.uint8)
    hsv[..., 1] = 255
    hsv[..., 2] = np.clip(mag / vmax * 255, 0, 255).astype(np.uint8)
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)


def compute(a, b, method, size):
    H, W = a.shape[:2]
    ga = cv2.cvtColor(cv2.resize(a, size, interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY)
    gb = cv2.cvtColor(cv2.resize(b, size, interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY)
    if method == "farneback":
        f = cv2.calcOpticalFlowFarneback(ga, gb, None, **FARNEBACK)
    else:
        preset = {"ultrafast": cv2.DISOPTICAL_FLOW_PRESET_ULTRAFAST, "fast": cv2.DISOPTICAL_FLOW_PRESET_FAST,
                  "medium": cv2.DISOPTICAL_FLOW_PRESET_MEDIUM}[method]
        f = cv2.DISOpticalFlow_create(preset).calc(ga, gb, None)
    # to cells of the 1024x1024 SAM2 input (64x64 grid)
    return np.dstack([f[..., 0] * 64 / size[0], f[..., 1] * 64 / size[1]])


PANELS = [("farneback", (1024, 1024), "Farneback @1024"), ("ultrafast", (1024, 1024), "DIS ultrafast @1024"),
          ("fast", (1024, 1024), "DIS fast @1024"), ("medium", (1024, 1024), "DIS medium @1024"),
          ("ultrafast", (256, 256), "DIS ultrafast @256")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selection", required=True)
    ap.add_argument("--stratum", choices=["fast", "slow"], required=True)
    ap.add_argument("--pairs", type=int, default=20)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    sel = json.load(open(args.selection))[args.stratum]
    args.videos = [c["video"] for c in sel]
    args.title = f"{args.stratum} videos"
    n = len(args.videos)
    fig, axes = plt.subplots(n, 2 + len(PANELS), figsize=(3.0 * (2 + len(PANELS)), 2.2 * n + 0.6))
    for i, vid in enumerate(args.videos):
        fs = frames_of(vid)[: args.pairs + 1]
        masks = [np.array(Image.open(f"{R}/Annotations/{vid}/{f[:-4]}.png")) for f in fs]
        H, W = masks[0].shape
        ids = sorted(int(x) for x in np.unique(masks[0]) if x != 0)
        oid = ids[0]
        # pair whose GT centroid step (object ids[0]) is closest to the median step
        steps = []
        for t in range(len(fs) - 1):
            m0, m1 = masks[t] == oid, masks[t + 1] == oid
            if m0.sum() < 20 or m1.sum() < 20:
                continue
            y0, x0 = np.nonzero(m0); y1, x1 = np.nonzero(m1)
            steps.append((t, (x1.mean() - x0.mean()) * 64 / W, (y1.mean() - y0.mean()) * 64 / H))
        med = np.median([max(abs(dx), abs(dy)) for _, dx, dy in steps])
        t, gdx, gdy = min(steps, key=lambda s: abs(max(abs(s[1]), abs(s[2])) - med))
        a = cv2.imread(f"{R}/JPEGImages/{vid}/{fs[t]}")
        b = cv2.imread(f"{R}/JPEGImages/{vid}/{fs[t + 1]}")
        vmax = max(1.0, 1.5 * np.hypot(gdx, gdy))
        for j, (im, m, lab) in enumerate([(a, masks[t], f"{vid}  t={t}"), (b, masks[t + 1], f"t+1  GT step ({gdx:+.1f},{gdy:+.1f}) cells")]):
            ax = axes[i, j]
            ax.imshow(cv2.cvtColor(im, cv2.COLOR_BGR2RGB))
            ax.contour(m == oid, levels=[0.5], colors="yellow", linewidths=0.8)
            ax.set_title(lab, fontsize=8)
        m0 = masks[t] == oid
        for k, (meth, size, lab) in enumerate(PANELS):
            f = compute(a, b, meth, size)
            fn = cv2.resize(f, (W, H), interpolation=cv2.INTER_LINEAR)
            dx, dy = np.median(fn[..., 0][m0]), np.median(fn[..., 1][m0])
            ax = axes[i, 2 + k]
            ax.imshow(flow_rgb(fn, vmax))
            ax.contour(m0, levels=[0.5], colors="white", linewidths=0.6)
            ax.set_title(f"{lab}\nmask median ({dx:+.1f},{dy:+.1f})", fontsize=8)
        for ax in axes[i]:
            ax.set_xticks([]); ax.set_yticks([])
    fig.suptitle(f"{args.title}  (hue = direction, brightness = magnitude, saturates at 1.5x GT step; units: cells of 64x64 grid)", fontsize=9)
    fig.tight_layout()
    fig.savefig(args.out, dpi=110)


if __name__ == "__main__":
    main()
