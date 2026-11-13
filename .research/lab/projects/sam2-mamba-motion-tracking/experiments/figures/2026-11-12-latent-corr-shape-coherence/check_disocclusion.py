"""Where do the transported masks leak? (2026-11-13, check after the 11/13 MTG)

For every (object, pair) of compute.py, false-positive cells = transported mask >= 0.5 but not the object at t.
Counts how many of them lie where the object was at t-1 (coverage >= 0.5): with the backward (pull) transport,
a background cell at t whose flow is ~0 copies the t-1 object there (disocclusion), which lowers RAFT's IoU.

  .venv-sam2/bin/python check_disocclusion.py --data data [--fields .../fields.pt] > data/disocclusion.txt
"""
import argparse
import json
from pathlib import Path

import torch
import torch.nn.functional as F

ap = argparse.ArgumentParser()
ap.add_argument("--data", type=Path, default=Path("data"))
ap.add_argument("--fields", type=Path,
                default=Path("/mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2/runs/latent_corr/shape_coherence/20261112/fields.pt"))
args = ap.parse_args()
rows = [json.loads(l) for l in (args.data / "pairs.jsonl").read_text().splitlines()]
rows = [r for r in rows if r["stratum"] is not None]
fields = torch.load(args.fields, weights_only=False)


def near(m):
    return F.max_pool2d(m.float()[None, None], 3, 1, 1)[0, 0] > 0


stats = {m: dict(fp=0, fp_prev=0, fp_near=0, fn=0) for m in ("softmax", "raft", "identity")}
for r in rows:
    f = fields[(r["video"], r["object"], r["t"])]
    tgt, prev = f["tgt"], f["cov"].float() >= 0.5
    for m, s in stats.items():
        mv = f["moved"][m].float() >= 0.5
        fp = mv & ~tgt
        s["fp"] += int(fp.sum()); s["fp_prev"] += int((fp & prev).sum())
        s["fp_near"] += int((fp & near(tgt)).sum()); s["fn"] += int((~mv & tgt).sum())
print(f"rows {len(rows)}")
for m, s in stats.items():
    print(f"{m:9s} fp {s['fp']:7d}  in t-1 object {s['fp_prev'] / s['fp']:.2f}  next to t object {s['fp_near'] / s['fp']:.2f}  fn {s['fn']:7d}")
