"""Transported-mask IoU without the disoccluded cells (2026-11-13, after the 11/13 MTG).

check_disocclusion.py showed that most of RAFT's leaks lie where the object was at t-1: with the backward (pull)
transport, a background cell that the object has just left copies the t-1 object. Those cells have no true
source in t-1, so no transport can be right there. This script removes them for every method alike.

Disocclusion test (forward-backward consistency, Sundaram et al. 2010 / UnFlow): with RAFT large at 1024,
backward flow b (t -> t-1) and forward flow f (t-1 -> t), a pixel x of frame t is consistent when
  |b(x) + f(x + b(x))|^2 < 0.01 (|b(x)|^2 + |f(x + b(x))|^2) + 0.5   (pixels).
A cell is valid when >= 50% of its 16x16 pixels are consistent. The IoU of compute.py (transported >= 0.5 vs the
object at t) is recomputed on the valid cells only, for A-b (softmax), argmax is not stored, RAFT and identity.
The backward flow is recomputed exactly as in compute.py; its cell average is checked against the stored one.

Run from the SAM2 repo root:
  CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=0 PYTHONPATH=$PWD .venv-sam2/bin/python \
      <this dir>/fair_iou.py --data <this dir>/data
"""
import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from torchvision.models.optical_flow import Raft_Large_Weights, raft_large

sys.path.insert(0, str(Path(__file__).resolve().parent))
from compute import raft_input  # noqa: E402
from training.measure_correspondence import CELL, CELLS, RES, video_frames  # noqa: E402

METHODS = ("softmax", "raft", "identity")
STRATA = ("slow", "mid", "fast", "all")


def consistent(b, f):
    """b, f [2, H, W] (dx, dy) px -> bool [H, W] for the pixels of frame t."""
    ys, xs = torch.meshgrid(torch.arange(RES, device=b.device), torch.arange(RES, device=b.device), indexing="ij")
    gx = (xs + 0.5 + b[0]) / RES * 2 - 1
    gy = (ys + 0.5 + b[1]) / RES * 2 - 1
    fw = F.grid_sample(f[None], torch.stack([gx, gy], -1)[None], mode="bilinear", padding_mode="border",
                       align_corners=False)[0]
    inside = (gx.abs() <= 1) & (gy.abs() <= 1)
    lhs = ((b + fw) ** 2).sum(0)
    rhs = 0.01 * ((b ** 2).sum(0) + (fw ** 2).sum(0)) + 0.5
    return (lhs < rhs) & inside


def iou(a, b):
    u = (a | b).sum()
    return float((a & b).sum() / u) if u > 0 else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", type=Path, required=True)
    ap.add_argument("--fields", type=Path,
                    default=Path("runs/latent_corr/shape_coherence/20261112/fields.pt"))
    args = ap.parse_args()
    if "RTX A4000" not in torch.cuda.get_device_name(0):
        sys.exit("set CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=0")
    dev = torch.device("cuda")
    rows = [json.loads(l) for l in (args.data / "pairs.jsonl").read_text().splitlines()]
    rows = [r for r in rows if r["stratum"] is not None]
    fields = torch.load(args.fields, weights_only=False)
    raft = raft_large(weights=Raft_Large_Weights.DEFAULT, progress=False).eval().to(dev)

    by_pair = defaultdict(list)
    for r in rows:
        by_pair[(r["video"], r["t"])].append(r)
    out, check = [], []
    for i, ((video, t), rs) in enumerate(sorted(by_pair.items())):
        _, ipaths, _ = video_frames(video)
        a, b = raft_input(ipaths[t], dev), raft_input(ipaths[t - 1], dev)
        with torch.inference_mode():
            bw = raft(a, b, num_flow_updates=12)[-1][0].float()  # t -> t-1
            fw = raft(b, a, num_flow_updates=12)[-1][0].float()  # t-1 -> t
        valid = F.avg_pool2d(consistent(bw, fw).float()[None, None], CELL)[0, 0].cpu() >= 0.5
        uv = F.avg_pool2d(bw[None], CELL)[0].cpu() / CELL
        for r in rs:
            f = fields[(video, r["object"], t)]
            check.append(float((torch.stack([uv[1], uv[0]]) - f["u"]["raft"].float()).abs().max()))
            tgt = f["tgt"]
            row = {"video": video, "object": r["object"], "t": t, "stratum": r["stratum"],
                   "valid_frac_map": float(valid.float().mean()),
                   "invalid_in_tgt_or_prev": float((~valid & (tgt | (f["cov"].float() >= 0.5))).sum())}
            for m in METHODS:
                mv = f["moved"][m].float() >= 0.5
                row[m] = {"iou_all": iou(mv, tgt), "iou_valid": iou(mv & valid, tgt & valid)}
            out.append(row)
        if i % 100 == 0:
            print(json.dumps({"i": i, "pairs": len(by_pair), "max_u_diff": max(check)}), flush=True)
    with (args.data / "fair_iou.jsonl").open("w") as fo:
        for r in out:
            fo.write(json.dumps(r) + "\n")

    # aggregate as fig.py: per object mean over pairs, per stratum mean over objects, bootstrap over objects
    by_obj = defaultdict(list)
    for r in out:
        by_obj[(r["video"], r["object"])].append(r)
    rng = np.random.default_rng(123)
    lines = [f"rows {len(out)}, objects {len(by_obj)}; max |u_raft recomputed - stored| = {max(check):.3f} cells",
             f"valid cells (whole map), mean over rows: {np.mean([r['valid_frac_map'] for r in out]):.3f}", "",
             "| method | key | " + " | ".join(STRATA) + " |", "|---|---|" + "---|" * len(STRATA)]
    for m in METHODS:
        for key in ("iou_all", "iou_valid"):
            cells = []
            for st in STRATA:
                vals = np.array([np.mean([r[m][key] for r in v if r[m][key] is not None])
                                 for v in by_obj.values() if st == "all" or v[0]["stratum"] == st])
                boot = rng.choice(vals, (10000, len(vals))).mean(1)
                lo, hi = np.percentile(boot, [2.5, 97.5])
                cells.append(f"{vals.mean():.3f} [{lo:.3f}, {hi:.3f}]")
            lines.append(f"| {m} | {key} | " + " | ".join(cells) + " |")
    # paired difference A-b - RAFT on valid cells
    for st in STRATA:
        d = np.array([np.mean([r["softmax"]["iou_valid"] - r["raft"]["iou_valid"] for r in v
                               if r["softmax"]["iou_valid"] is not None and r["raft"]["iou_valid"] is not None])
                      for v in by_obj.values() if st == "all" or v[0]["stratum"] == st])
        boot = rng.choice(d, (10000, len(d))).mean(1)
        lo, hi = np.percentile(boot, [2.5, 97.5])
        lines.append(f"A-b - RAFT (iou_valid), {st}: {d.mean():+.3f} [{lo:+.3f}, {hi:+.3f}]")
    (args.data / "fair_iou_summary.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
