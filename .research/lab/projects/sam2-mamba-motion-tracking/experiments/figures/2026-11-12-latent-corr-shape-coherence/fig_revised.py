"""Revised figures after the 11/13 MTG (2026-11-13). The 01-05 figures are kept as shown at the MTG.

06-arrows-median-cells.png  01 with every target cell filled by its neighbour test (the colour no longer sits
                            on thinned arrows only), arrows in dark grey on top.
07-masks-median-disocclusion.png
                            04 with the correct colour-bar label (each cell at t takes the t-1 object mask from
                            its sources, weighted: backward transport, not a count of arrow ends) and the
                            disoccluded cells (RAFT large forward-backward inconsistent, as fair_iou.py) hatched.
08-iou-valid.png            05 recomputed on the consistent cells only (data/fair_iou.jsonl).

Run from the SAM2 repo root (RAFT for the three example pairs):
  CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=0 PYTHONPATH=$PWD .venv-sam2/bin/python <this dir>/fig_revised.py \
      --data <this dir>/data
"""
import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fig  # noqa: E402
from compute import raft_input  # noqa: E402
from fair_iou import consistent  # noqa: E402
from fig import CELL, CELLS, OK, BAD, SNAME, STRATA, example_setup, framed, local_disc, outline, plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402
from torchvision.models.optical_flow import Raft_Large_Weights, raft_large  # noqa: E402
from training.measure_correspondence import video_frames  # noqa: E402

ARROW = "#333333"


def cell_fill(ax, tgt, disc):
    rgba = np.zeros((CELLS, CELLS, 4))
    t = tgt.numpy()
    bad = disc.numpy() > 1
    for sel, col in ((t & ~bad, OK), (t & bad, BAD)):
        c = np.array([int(col[i:i + 2], 16) / 255 for i in (1, 3, 5)])
        rgba[sel] = (*c, 0.45)
    ax.imshow(np.kron(rgba, np.ones((CELL, CELL, 1))), interpolation="nearest")


def arrows_cells_figure(rows, fields, out):
    fig_, axes = plt.subplots(3, 2, figsize=(8.4, 13.2))
    for i, st in enumerate(STRATA):
        r, f, _, cur, ext, side = example_setup(rows, fields, 50, st)
        step = 1 if side <= 24 else 2 if side <= 44 else 3
        for j, m in enumerate(("softmax", "raft")):
            ax = axes[i, j]
            ax.imshow(cur, alpha=0.45)
            u = f["u"][m]
            cell_fill(ax, f["tgt"], local_disc(u, f["tgt"]))
            ys, xs = np.nonzero(f["tgt"].numpy())
            keep = (ys % step == 0) & (xs % step == 0)
            ys, xs = ys[keep], xs[keep]
            uy, ux = u[0].float().numpy()[ys, xs], u[1].float().numpy()[ys, xs]
            cx, cy = (xs + 0.5) * CELL, (ys + 0.5) * CELL
            ax.quiver(cx + ux * CELL, cy + uy * CELL, -ux * CELL, -uy * CELL, color=ARROW, angles="xy",
                      scale_units="xy", scale=1, width=0.005, headwidth=3.5, headlength=4, minlength=0.1)
            framed(ax, ext)
            if i == 0:
                ax.set_title("A-b" if m == "softmax" else "RAFT", fontsize=14)
        axes[i, 0].set_ylabel(SNAME[st], fontsize=14)
    handles = [Patch(facecolor=OK, alpha=0.45, label="マスの塗り：上下左右の隣との移動の差（最大）≤ 1マス"),
               Patch(facecolor=BAD, alpha=0.45, label="マスの塗り：上下左右の隣との移動の差（最大）> 1マス"),
               Line2D([], [], color=ARROW, lw=2, label="矢印：t−1 の取ってくる位置 → t のマス（A-b は重みの平均の位置。数マスおきに表示）")]
    fig_.legend(handles=handles, loc="lower center", ncol=1, fontsize=10.5, frameon=False)
    fig_.subplots_adjust(left=0.07, right=0.99, top=0.96, bottom=0.09, hspace=0.06, wspace=0.04)
    fig_.savefig(out, dpi=110)
    plt.close(fig_)


def valid_cells(raft, video, t, dev):
    _, ipaths, _ = video_frames(video)
    a, b = raft_input(ipaths[t], dev), raft_input(ipaths[t - 1], dev)
    with torch.inference_mode():
        bw = raft(a, b, num_flow_updates=12)[-1][0].float()
        fw = raft(b, a, num_flow_updates=12)[-1][0].float()
    return F.avg_pool2d(consistent(bw, fw).float()[None, None], CELL)[0, 0].cpu() >= 0.5


def masks_disocclusion_figure(rows, fields, raft, dev, out):
    gt = "#c71f7a"
    fig_, axes = plt.subplots(3, 4, figsize=(15, 12.2))
    for i, st in enumerate(STRATA):
        r, f, prev, cur, ext, _ = example_setup(rows, fields, 50, st)
        invalid = ~valid_cells(raft, r["video"], r["t"], dev)
        panels = [("t−1", prev, f["prev_lab"], None), ("t", cur, f["tgt"], None),
                  ("A-b で運んだマスク", cur, f["tgt"], "softmax"), ("RAFT で運んだマスク", cur, f["tgt"], "raft")]
        for j, (ttl, img, lab, m) in enumerate(panels):
            ax = axes[i, j]
            if m is None:
                ax.imshow(img)
            else:
                ax.imshow(img, alpha=0.45)
                heat = np.kron(f["moved"][m].float().clamp(0, 1).numpy(), np.ones((CELL, CELL)))
                im = ax.imshow(np.ma.masked_less(heat, 0.05), cmap="Blues", vmin=0, vmax=1, alpha=0.8)
                ax.contourf(np.kron(invalid.numpy().astype(float), np.ones((CELL, CELL))), levels=[0.5, 1.5],
                            colors="none", hatches=["////"])
                ax.contour(np.kron(invalid.numpy().astype(float), np.ones((CELL, CELL))), levels=[0.5],
                           colors=["#555555"], linewidths=0.8)
            outline(ax, lab, gt, 1.8)
            framed(ax, ext)
            if i == 0:
                ax.set_title(ttl, fontsize=14)
        axes[i, 0].set_ylabel(SNAME[st], fontsize=14)
    fig_.legend(handles=[Line2D([], [], color=gt, lw=2.5, label="正解のマスク（輪郭）"),
                         Patch(facecolor="white", edgecolor="#555555", hatch="////",
                               label="RAFT の前後の flow が一致しないマス（disocclusion と flow の誤り。IoU の再計算で除いたマス）")],
                loc="lower left", bbox_to_anchor=(0.03, 0.02), fontsize=11.5, frameon=False)
    cax = fig_.add_axes([0.6, 0.065, 0.3, 0.012])
    cb = fig_.colorbar(im, cax=cax, orientation="horizontal")
    cb.set_label("t の各マスが、対応先（t−1）の物体マスクの値を重み付きで取ってきた値（0〜1）", fontsize=10.5)
    fig_.subplots_adjust(left=0.04, right=0.99, top=0.96, bottom=0.13, hspace=0.06, wspace=0.04)
    fig_.savefig(out, dpi=110)
    plt.close(fig_)


def iou_valid_figure(data, out):
    rows = [json.loads(l) for l in (data / "fair_iou.jsonl").read_text().splitlines()]
    by_obj = defaultdict(list)
    for r in rows:
        by_obj[(r["video"], r["object"])].append(r)
    rng = np.random.default_rng(123)
    table = {}
    for st in STRATA + ("all",):
        objs = [v for v in by_obj.values() if st == "all" or v[0]["stratum"] == st]
        for m in ("softmax", "raft", "identity"):
            vals = np.array([np.mean([r[m]["iou_valid"] for r in v if r[m]["iou_valid"] is not None]) for v in objs])
            boot = rng.choice(vals, (10000, len(vals))).mean(1)
            table[(st, m, "iou")] = (vals.mean(), *np.percentile(boot, [2.5, 97.5]), len(vals))
    fig_, ax = plt.subplots(figsize=(8, 4.8))
    fig.bars(ax, table, "iou", ("softmax", "raft", "identity"),
             "運んだマスクと正解の IoU（前後の flow が一致するマスだけ）", "IoU")
    ax.legend(fontsize=10.5, frameon=False, loc="upper center", ncol=3, bbox_to_anchor=(0.5, 1.0))
    ax.set_ylim(0, 1.12)
    ax.set_yticks(np.arange(0, 1.01, 0.2))
    fig_.tight_layout()
    fig_.savefig(out, dpi=110)
    plt.close(fig_)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", type=Path, required=True)
    ap.add_argument("--fields", type=Path, default=Path("runs/latent_corr/shape_coherence/20261112/fields.pt"))
    args = ap.parse_args()
    if "RTX A4000" not in torch.cuda.get_device_name(0):
        sys.exit("set CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=0")
    dev = torch.device("cuda")
    rows = [json.loads(l) for l in (args.data / "pairs.jsonl").read_text().splitlines()]
    rows = [r for r in rows if r["stratum"] is not None]
    fields = torch.load(args.fields, weights_only=False)
    raft = raft_large(weights=Raft_Large_Weights.DEFAULT, progress=False).eval().to(dev)
    arrows_cells_figure(rows, fields, HERE / "06-arrows-median-cells.png")
    masks_disocclusion_figure(rows, fields, raft, dev, HERE / "07-masks-median-disocclusion.png")
    iou_valid_figure(args.data, HERE / "08-iou-valid.png")


if __name__ == "__main__":
    main()
