"""Shape coherence of the A-b correspondence (2026-11-12, for the 11/13 MTG).

Question (11/6 MTG): with the "most similar cell" correspondence, a small noise sends a cell to a place
completely different from its neighbours, so the object's shape breaks. How often does that happen with the
correspondence A-b actually uses (image-encoder stride-16 features of F0, cosine similarity, 15x15 window,
softmax tau=0.02), compared with identity, argmax and a RAFT optical flow reference?

No training, no change to SAM2 code: imports the stage-0 helpers of the SAM2 repo (training.measure_correspondence,
sam2.modeling.latent_correspondence) read-only.

Data: the 125 MOSE tuning videos (the set A-b was evaluated on), objects of tuning_object_motion.jsonl
(speed strata: tertile cuts 0.620 / 1.233 cells). Per video, up to --pairs evenly spaced consecutive pairs
(t-1 -> t). An (object, pair) is used when the object has >= 1 cell (coverage >= 0.5) at t and is visible at t-1.

Per (object, pair), target cells T = the object's cells at t. Displacement field u(p) = sum_k W[k, p] off_k
(cells, target -> source in t-1, same direction as the state transport out(p) = sum_k W[k, p] h(p + off_k)).
  edge_disc     mean ||u(p) - u(p')|| over 4-neighbour edges inside T (cells)
  edge_gt1      fraction of those edges with ||u(p) - u(p')|| > 1 cell
  fold          fraction of cells (p, right, down in T) where det(d(p + u)/dp) <= 0 (folding)
  iou           IoU of the object's t-1 coverage transported by W (>= 0.5) with T (whole map)
  epe_raft      mean ||u - u_raft|| over T
  dup15         fraction of the object's t-1 cells (coverage >= 0.5) with column sum > 1.5 (softmax only)
RAFT: torchvision raft_large (official weights), 12 updates, on the same 1024x1024 inputs, flow from frame t to
t-1, averaged over each 16x16 cell and divided by 16. Its mask transport is bilinear sampling at p + u_raft(p).

Run from the SAM2 repo root:
  CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=0 PYTHONPATH=$PWD .venv-sam2/bin/python \
      <this dir>/compute.py --out <this dir>/data
"""
import argparse
import json
import platform
import sys
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image
from torchvision.models.optical_flow import Raft_Large_Weights, raft_large

from sam2.modeling.latent_correspondence import column_sums, local_similarity, offsets, transport_reference
from training.measure_correspondence import (
    CELL, CELLS, RES, WINDOW, Tracker, cell_labels, image_feature, image_tensor, label_map, video_frames,
)

MOTION = Path("/mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2/runs/spatial_mixing/motion/20261104")
TAU = 0.02
METHODS = ("identity", "softmax", "argmax", "raft")


def raft_input(path, dev):
    img = Image.open(path).convert("RGB").resize((RES, RES), Image.Resampling.BILINEAR)
    x = torch.from_numpy(np.asarray(img).copy()).to(dev).permute(2, 0, 1)[None].float() / 255.0
    return x * 2 - 1


def displacement(w, off):
    """w [K, H, W] -> u [2, H, W] (dy, dx) in cells."""
    return torch.einsum("khw,kd->dhw", w, off)


def coherence(u, tgt):
    """Edge discrepancy, fraction > 1 cell, fold rate inside the target cells."""
    discs = []
    for dy, dx in ((0, 1), (1, 0)):
        a = tgt[: CELLS - dy, : CELLS - dx] & tgt[dy:, dx:]
        d = (u[:, : CELLS - dy, : CELLS - dx] - u[:, dy:, dx:]).norm(dim=0)
        discs.append(d[a])
    disc = torch.cat(discs)
    core = tgt[:-1, :-1] & tgt[:-1, 1:] & tgt[1:, :-1]
    duy_dy = u[0, 1:, :-1] - u[0, :-1, :-1]
    duy_dx = u[0, :-1, 1:] - u[0, :-1, :-1]
    dux_dy = u[1, 1:, :-1] - u[1, :-1, :-1]
    dux_dx = u[1, :-1, 1:] - u[1, :-1, :-1]
    det = (1 + duy_dy) * (1 + dux_dx) - duy_dx * dux_dy
    return {
        "edges": int(disc.numel()),
        "edge_disc": float(disc.mean()) if disc.numel() else None,
        "edge_gt1": float((disc > 1).float().mean()) if disc.numel() else None,
        "fold_cells": int(core.sum()),
        "fold": float((det[core] <= 0).float().mean()) if core.any() else None,
    }


def iou(a, b):
    union = (a | b).sum()
    return float((a & b).sum() / union) if union > 0 else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--pairs", type=int, default=12)
    ap.add_argument("--limit-videos", type=int, default=None)
    ap.add_argument("--expect-gpu", default="RTX A4000")
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    dev = torch.device("cuda")
    if args.expect_gpu not in torch.cuda.get_device_name(0):
        sys.exit(f"cuda:0 is {torch.cuda.get_device_name(0)!r}; set CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=0")

    motion = defaultdict(dict)
    for line in (MOTION / "tuning_object_motion.jsonl").read_text().splitlines():
        r = json.loads(line)
        motion[r["video"]][int(r["object_id"])] = r["median"]
    cut1, cut2 = json.load(open(MOTION / "motion_summary.json"))["tuning_speed_strata"]["tertile_cuts_cells"]
    videos = sorted(motion)[: args.limit_videos]

    meta = {"started": datetime.now().isoformat(timespec="seconds"), "host": platform.node(),
            "gpu": torch.cuda.get_device_name(0), "torch": torch.__version__, "argv": sys.argv,
            "tau": TAU, "window": WINDOW, "videos": len(videos), "pairs_per_video": args.pairs,
            "cuts": [cut1, cut2]}
    (args.out / "meta.json").write_text(json.dumps(meta, indent=1))

    tracker = Tracker(dev)
    raft = raft_large(weights=Raft_Large_Weights.DEFAULT, progress=False).eval().to(dev)
    off = offsets(WINDOW).to(dev).float()  # [K, 2] (dy, dx)
    ys, xs = torch.meshgrid(torch.arange(CELLS, device=dev), torch.arange(CELLS, device=dev), indexing="ij")

    rows, store = [], {}
    t_start = time.time()
    for vi, video in enumerate(videos):
        fids, ipaths, mpaths = video_frames(video)
        n = len(fids)
        if n < 2:
            continue
        ts = sorted({int(round(x)) for x in np.linspace(1, n - 1, min(args.pairs, n - 1))})
        feats, bigs, labs = {}, {}, {}
        for t in sorted({t for t in ts} | {t - 1 for t in ts}):
            vf, _, _ = tracker.backbone(image_tensor(ipaths[t]))
            feats[t] = image_feature(vf)
            bigs[t] = label_map(mpaths[t])[0]
            labs[t] = cell_labels(bigs[t]).to(dev)
        for t in ts:
            s = local_similarity(feats[t][None], feats[t - 1][None], WINDOW)  # [1, K, 64, 64]
            w_soft = torch.softmax(s / TAU, dim=1)[0]
            w_arg = F.one_hot(s[0].argmax(0), s.shape[1]).permute(2, 0, 1).float()
            w_id = torch.zeros_like(w_soft)
            w_id[WINDOW * WINDOW // 2] = 1
            col = column_sums(w_soft[None], WINDOW)[0]
            with torch.inference_mode():
                flow = raft(raft_input(ipaths[t], dev), raft_input(ipaths[t - 1], dev), num_flow_updates=12)[-1]
            uv = F.avg_pool2d(flow.float(), CELL)[0] / CELL  # (dx, dy)
            u = {"identity": displacement(w_id, off), "softmax": displacement(w_soft, off),
                 "argmax": displacement(w_arg, off), "raft": torch.stack([uv[1], uv[0]])}
            weights = {"identity": w_id, "softmax": w_soft, "argmax": w_arg}
            grid = torch.stack([(xs + 0.5 + u["raft"][1]) / CELLS * 2 - 1,
                                (ys + 0.5 + u["raft"][0]) / CELLS * 2 - 1], dim=-1)[None]
            for oid, med in motion[video].items():
                tgt = labs[t] == oid
                prev_big = (bigs[t - 1] == oid)
                if not tgt.any() or not prev_big.any():
                    continue
                cov = F.avg_pool2d(prev_big.float().to(dev)[None, None], CELL)  # [1, 1, 64, 64]
                stratum = None if med is None else ("slow" if med < cut1 else "mid" if med < cut2 else "fast")
                row = {"video": video, "object": oid, "t": t, "frame": fids[t], "motion": med,
                       "stratum": stratum, "cells": int(tgt.sum()), "prev_cells": int((cov[0, 0] >= 0.5).sum())}
                moved = {}
                for m in METHODS:
                    if m == "raft":
                        moved[m] = F.grid_sample(cov, grid, mode="bilinear", padding_mode="zeros",
                                                 align_corners=False)[0, 0]
                    else:
                        moved[m] = transport_reference(cov, weights[m][None], WINDOW)[0, 0]
                    c = coherence(u[m], tgt)
                    row[m] = {"iou": iou(moved[m] >= 0.5, tgt), **c,
                              "epe_raft": float((u[m] - u["raft"]).norm(dim=0)[tgt].mean())}
                src = cov[0, 0] >= 0.5
                row["softmax"]["dup15"] = float((col[src] > 1.5).float().mean()) if src.any() else None
                rows.append(row)
                store[(video, oid, t)] = {
                    "tgt": tgt.cpu(), "prev_lab": (labs[t - 1] == oid).cpu(), "cov": cov[0, 0].half().cpu(),
                    "u": {m: u[m].half().cpu() for m in METHODS},
                    "moved": {m: moved[m].half().cpu() for m in METHODS}}
        print(json.dumps({"i": vi, "video": video, "frames": n, "rows": len(rows),
                          "elapsed_s": round(time.time() - t_start, 1)}), flush=True)

    with (args.out / "pairs.jsonl").open("w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    torch.save(store, args.out / "fields.pt")
    meta["finished"] = datetime.now().isoformat(timespec="seconds")
    meta["rows"] = len(rows)
    (args.out / "meta.json").write_text(json.dumps(meta, indent=1))


if __name__ == "__main__":
    main()
