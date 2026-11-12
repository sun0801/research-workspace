"""Explanatory example for the 11/13 MTG: where one cell takes its state from with the A-b weights (cell-to-cell
similarity). The figure shows A-b only; the simplest form of "compare the 3x3 surroundings" (no training) is
computed for the same cell and written to example_weights.json (box3), not drawn.

Simplest form = assume the 3x3 neighbours of p move like p and average their similarities for the same displacement
d: s3(p, d) = mean_{delta in 3x3} s(p + delta, d), then softmax with the same tau (0.02) as A-b. This is the
"weights fixed by hand" special case of the learned surrounding-comparison candidate, not the candidate itself.

Example (rule, not by eye): the median example of the mid stratum in 2026-11-12 (91b754c5, object 3, frame 24);
the cell p is, among the object's interior cells (all 8 neighbours in the object), the one whose A-b displacement
is farthest from RAFT's (the 11/12 fields.pt).

Run from the SAM2 repo root:
  CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=0 PYTHONPATH=$PWD .venv-sam2/bin/python <this dir>/example_weights.py
"""
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn.functional as F
from matplotlib import rcParams
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle

from sam2.modeling.latent_correspondence import local_similarity, offsets
from training.measure_correspondence import CELL, CELLS, WINDOW, Tracker, image_feature, image_tensor, video_frames

rcParams["font.family"] = "Noto Sans CJK JP"
HERE = Path(__file__).resolve().parent
FIELDS = Path("/mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2/runs/latent_corr/shape_coherence/20261112/fields.pt")
VIDEO, OBJ, T = "91b754c5", 3, 24
TAU = 0.02
R = WINDOW // 2


def main():
    dev = torch.device("cuda")
    f = torch.load(FIELDS, weights_only=False)[(VIDEO, OBJ, T)]
    tgt = f["tgt"]
    interior = tgt.clone()
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            interior &= torch.roll(tgt, (dy, dx), (0, 1))
    interior[[0, -1], :] = False
    interior[:, [0, -1]] = False
    gap = (f["u"]["softmax"].float() - f["u"]["raft"].float()).norm(dim=0)
    gap[~interior] = -1
    py, px = divmod(int(gap.argmax()), CELLS)

    tracker = Tracker(dev)
    fids, ipaths, _ = video_frames(VIDEO)
    feats = [image_feature(tracker.backbone(image_tensor(ipaths[t]))[0]) for t in (T - 1, T)]
    s = local_similarity(feats[1][None], feats[0][None], WINDOW)[0]  # [K, 64, 64]
    s_fin = torch.nan_to_num(s, neginf=-1.0)
    s3 = F.avg_pool2d(s_fin[None], 3, stride=1, padding=1, count_include_pad=False)[0]
    s3 = s3.masked_fill(torch.isinf(s), float("-inf"))
    w1 = torch.softmax(s[:, py, px] / TAU, 0).view(WINDOW, WINDOW).cpu().numpy()
    w3 = torch.softmax(s3[:, py, px] / TAU, 0).view(WINDOW, WINDOW).cpu().numpy()
    raft = f["u"]["raft"].float()[:, py, px].numpy()  # (dy, dx) cells, target -> source

    from PIL import Image
    imgs = [np.asarray(Image.open(ipaths[t]).convert("RGB").resize((1024, 1024))) for t in (T - 1, T)]
    half = 12  # crop: +-12 cells around p
    y0, x0 = max(0, py - half), max(0, px - half)
    y1, x1 = min(CELLS, py + half + 1), min(CELLS, px + half + 1)
    ext = (x0 * CELL, x1 * CELL, y1 * CELL, y0 * CELL)

    fig, axes = plt.subplots(1, 2, figsize=(10.4, 5.8))
    ax = axes[0]
    ax.imshow(imgs[1])
    ax.add_patch(Rectangle((px * CELL, py * CELL), CELL, CELL, fill=False, ec="#c71f7a", lw=2.5))
    ax.set_title("フレーム t", fontsize=14)
    for ax, w, ttl in ((axes[1], w1, "フレーム t−1：A-bの重み"),):
        ax.imshow(imgs[0], alpha=0.55)
        heat = np.zeros((CELLS, CELLS))
        heat[py - R: py + R + 1, px - R: px + R + 1] = w
        heat = np.kron(heat, np.ones((CELL, CELL)))
        im = ax.imshow(np.ma.masked_less(heat, 0.01), cmap="Blues", vmin=0, vmax=w1.max(), alpha=0.85)
        ax.add_patch(Rectangle(((px - R) * CELL, (py - R) * CELL), WINDOW * CELL, WINDOW * CELL, fill=False, ec="#555555", lw=1.2))
        ax.plot((px + 0.5) * CELL, (py + 0.5) * CELL, "+", color="#c71f7a", ms=14, mew=2.5)
        ax.plot((px + 0.5 + raft[1]) * CELL, (py + 0.5 + raft[0]) * CELL, "x", color="#1baf7a", ms=13, mew=3)
        ax.set_title(ttl, fontsize=14)
    for ax in axes:
        ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3]); ax.set_xticks([]); ax.set_yticks([])
    handles = [Line2D([], [], color="#c71f7a", lw=2.5, label="対象のマス p（t−1では同じ位置 +）"),
               Line2D([], [], color="#555555", lw=1.2, label="探す窓（15×15）"),
               Line2D([], [], color="#1baf7a", marker="x", lw=0, ms=10, mew=3, label="RAFTが示す移動先")]
    fig.legend(handles=handles, loc="lower left", ncol=2, fontsize=11.5, frameon=False, bbox_to_anchor=(0.02, 0.0))
    cax = fig.add_axes([0.62, 0.08, 0.3, 0.025])
    cb = fig.colorbar(im, cax=cax, orientation="horizontal")
    cb.set_label("重み（窓の中の合計が1）", fontsize=11)
    fig.subplots_adjust(left=0.01, right=0.99, top=0.92, bottom=0.2, wspace=0.04)
    fig.savefig(HERE / "02-example-weights.png", dpi=110)

    peak = lambda w: np.unravel_index(w.argmax(), w.shape)
    info = {"video": VIDEO, "object": OBJ, "frame": T, "cell": [py, px], "rule": "interior cell with max |u_A-b - u_RAFT|",
            "gap_cells": float(gap.max()), "raft_dydx": raft.tolist(),
            "a_b": {"peak_dydx": [int(v) - R for v in peak(w1)], "peak_weight": float(w1.max()),
                    "u_dydx": f["u"]["softmax"].float()[:, py, px].tolist()},
            "box3": {"peak_dydx": [int(v) - R for v in peak(w3)], "peak_weight": float(w3.max()),
                     "u_dydx": [float((w3 * (np.arange(WINDOW) - R)[:, None]).sum()),
                                float((w3 * (np.arange(WINDOW) - R)[None, :]).sum())]}}
    (HERE / "example_weights.json").write_text(json.dumps(info, indent=1))
    print(json.dumps(info))


if __name__ == "__main__":
    main()
