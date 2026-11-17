"""Pre-check for the translation-only correspondence (brainstorm 2026-11-16). CPU only, no model.

Reads the fields saved by the 2026-11-12 shape-coherence measurement (per pair: target cells of the object at t,
t-1 coverage, per-cell displacement u(p) = "where cell p of frame t takes from in t-1" for A-b softmax / argmax /
RAFT) and asks, without computing any new feature:

  1. model fit: how far is the RAFT reference field inside an object from ONE translation per object, or from one
     translation per local block (masked median in a k x k window)?
  2. estimation by voting: does the median / mode of A-b's own per-cell displacements over the object give the
     RAFT object translation?
  3. outline: IoU of the t-1 mask moved by one translation (several estimators, and the oracle best translation).
  4. block-wise voting (median filter of the argmax field): coherence, RAFT distance and IoU.

The proper estimator of the plan (summing the similarity over the region before choosing) needs the cost volume
and is NOT measured here. Aggregation as on 2026-11-12: mean over pairs per object, then over objects.
"""
import argparse, json
from collections import defaultdict
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

CELLS, R = 64, 7


def coherence(u, tgt):
    discs = []
    for dy, dx in ((0, 1), (1, 0)):
        a = tgt[: CELLS - dy, : CELLS - dx] & tgt[dy:, dx:]
        d = (u[:, : CELLS - dy, : CELLS - dx] - u[:, dy:, dx:]).norm(dim=0)
        discs.append(d[a])
    disc = torch.cat(discs)
    core = tgt[:-1, :-1] & tgt[:-1, 1:] & tgt[1:, :-1]
    det = (1 + u[0, 1:, :-1] - u[0, :-1, :-1]) * (1 + u[1, :-1, 1:] - u[1, :-1, :-1]) \
        - (u[0, :-1, 1:] - u[0, :-1, :-1]) * (u[1, 1:, :-1] - u[1, :-1, :-1])
    return (float((disc > 1).float().mean()) if disc.numel() else None,
            float((det[core] <= 0).float().mean()) if core.any() else None)


def iou(a, b):
    union = (a | b).sum()
    return float((a & b).sum() / union) if union > 0 else None


YS, XS = torch.meshgrid(torch.arange(CELLS), torch.arange(CELLS), indexing="ij")


def warp(cov, u):
    """cov [64,64] sampled at p + u(p); u is [2] (one translation) or [2,64,64] (dy, dx)."""
    if u.dim() == 1:
        u = u.view(2, 1, 1).expand(2, CELLS, CELLS)
    grid = torch.stack([(XS + 0.5 + u[1]) / CELLS * 2 - 1, (YS + 0.5 + u[0]) / CELLS * 2 - 1], dim=-1)[None]
    return F.grid_sample(cov[None, None], grid, mode="bilinear", padding_mode="zeros", align_corners=False)[0, 0]


def warp_many(cov, ds):
    """ds [N,2] translations -> [N,64,64]."""
    n = ds.shape[0]
    gx = (XS[None] + 0.5 + ds[:, 1].view(n, 1, 1)) / CELLS * 2 - 1
    gy = (YS[None] + 0.5 + ds[:, 0].view(n, 1, 1)) / CELLS * 2 - 1
    return F.grid_sample(cov[None, None].expand(n, 1, CELLS, CELLS), torch.stack([gx, gy], -1), mode="bilinear",
                         padding_mode="zeros", align_corners=False)[:, 0]


def med(u, m):
    return torch.stack([u[0][m].median(), u[1][m].median()])


def mode_int(u, m):
    k = ((u[0][m].round().long() + R) * (2 * R + 1) + (u[1][m].round().long() + R)).clamp(0, (2 * R + 1) ** 2 - 1)
    b = torch.bincount(k, minlength=(2 * R + 1) ** 2).argmax().item()
    return torch.tensor([b // (2 * R + 1) - R, b % (2 * R + 1) - R], dtype=torch.float32)


def block_median(u, k, mask=None):
    """Median of u over a k x k window (cells outside the image, or outside `mask`, ignored)."""
    r = k // 2
    x = u.clone()
    if mask is not None:
        x[:, ~mask] = float("nan")
    x = F.pad(x[None], (r, r, r, r), value=float("nan"))
    p = F.unfold(x, k).view(2, k * k, CELLS, CELLS)
    return torch.nanmedian(p, dim=1).values.nan_to_num(0.0)


INT = torch.stack(torch.meshgrid(torch.arange(-R, R + 1.0), torch.arange(-R, R + 1.0), indexing="ij"), -1).reshape(-1, 2)
HALF = torch.stack(torch.meshgrid(torch.arange(-R, R + 0.25, 0.5), torch.arange(-R, R + 0.25, 0.5), indexing="ij"), -1).reshape(-1, 2)


def affine_fit(u, m, iters=3):
    """Robust least-squares affine field u(p) = [y, x, 1] @ M on the cells m; returns the fitted field and M [3,2]."""
    ys, xs = YS[m].float(), XS[m].float()
    a = torch.stack([ys - ys.mean(), xs - xs.mean(), torch.ones_like(ys)], 1)
    b = torch.stack([u[0][m], u[1][m]], 1)
    keep = torch.ones(len(ys), dtype=torch.bool)
    sol = None
    for _ in range(iters):
        if int(keep.sum()) < 6:
            break
        sol = torch.linalg.lstsq(a[keep], b[keep]).solution
        res = (a @ sol - b).norm(dim=1)
        keep = res <= max(1.0, float(res.median()))
    if sol is None:
        return None, None
    return a @ sol, sol


def best_translation(cov, tgt, cands):
    m = warp_many(cov, cands) >= 0.5
    inter = (m & tgt[None]).flatten(1).sum(1).float()
    union = (m | tgt[None]).flatten(1).sum(1).float().clamp(min=1)
    v = inter / union
    return float(v.max()), cands[v.argmax()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fields", type=Path, required=True)
    ap.add_argument("--pairs", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    torch.set_num_threads(8)
    store = torch.load(args.fields, map_location="cpu", weights_only=False)
    strata = {}
    for line in args.pairs.read_text().splitlines():
        r = json.loads(line)
        strata[(r["video"], r["object"], r["t"])] = r["stratum"]

    rows = []
    for key, v in store.items():
        tgt, cov = v["tgt"], v["cov"].float()
        u = {m: x.float() for m, x in v["u"].items()}
        n = int(tgt.sum())
        row = {"video": key[0], "object": key[1], "t": key[2], "stratum": strata[key], "cells": n}
        interior = tgt.clone()
        interior[1:] &= tgt[:-1]; interior[:-1] &= tgt[1:]; interior[:, 1:] &= tgt[:, :-1]; interior[:, :-1] &= tgt[:, 1:]
        interior[0] = interior[-1] = False; interior[:, 0] = interior[:, -1] = False
        row["interior_cells"] = int(interior.sum())

        # sanity: the 11/12 numbers from the stored fields
        row["san_soft_gt1"], row["san_soft_fold"] = coherence(u["softmax"], tgt)
        row["san_soft_iou"] = iou(v["moved"]["softmax"].float() >= 0.5, tgt)
        row["san_id_iou"] = iou(v["moved"]["identity"].float() >= 0.5, tgt)
        row["san_raft_iou"] = iou(v["moved"]["raft"].float() >= 0.5, tgt)

        # 1. model fit of the RAFT reference
        d_raft = med(u["raft"], tgt)
        res = (u["raft"] - d_raft.view(2, 1, 1)).norm(dim=0)
        row["fit_obj_mean"] = float(res[tgt].mean())
        row["fit_obj_gt1"] = float((res[tgt] > 1).float().mean())
        row["fit_obj_gt05"] = float((res[tgt] > 0.5).float().mean())
        if interior.any():
            row["fit_obj_int_gt1"] = float((res[interior] > 1).float().mean())
            row["fit_obj_int_gt05"] = float((res[interior] > 0.5).float().mean())
        for k in (3, 5, 9, 15):
            rb = (u["raft"] - block_median(u["raft"], k, tgt)).norm(dim=0)
            row[f"fit_blk{k}_gt1"] = float((rb[tgt] > 1).float().mean())
            row[f"fit_blk{k}_gt05"] = float((rb[tgt] > 0.5).float().mean())
        row["raft_obj_norm"] = float(d_raft.norm())
        # motion classes of the RAFT reference: (1) translation, (2) affine, (3) the rest
        if n >= 20:
            fit, sol = affine_fit(u["raft"], tgt)
            if fit is not None:
                ra = (fit - torch.stack([u["raft"][0][tgt], u["raft"][1][tgt]], 1)).norm(dim=1)
                rt = res[tgt]
                for thr, tag in ((1.0, "1"), (0.5, "05")):
                    row[f"cls{tag}_trans"] = float((rt <= thr).float().mean())
                    row[f"cls{tag}_affine"] = float(((rt > thr) & (ra <= thr)).float().mean())
                    row[f"cls{tag}_rest"] = float(((rt > thr) & (ra > thr)).float().mean())
                row["fit_aff_gt1"] = float((ra > 1).float().mean())
                row["fit_aff_gt05"] = float((ra > 0.5).float().mean())
                row["fit_aff_mean"] = float(ra.mean())
                row["fit_trans_mean_n20"] = float(rt.mean())
                lin = torch.eye(2) + sol[:2].T  # d(source)/d(target): [[1+duy/dy, duy/dx], [dux/dy, 1+dux/dx]]
                det = float(torch.linalg.det(lin))
                if det > 0:
                    row["aff_scale_abs"] = abs(det ** 0.5 - 1)
                    row["aff_rot_deg"] = abs(float(torch.rad2deg(torch.atan2(lin[1, 0] - lin[0, 1], lin[0, 0] + lin[1, 1]))))
                # largest displacement difference the affine part makes across the object (cells)
                a_c = torch.stack([YS[tgt].float() - YS[tgt].float().mean(), XS[tgt].float() - XS[tgt].float().mean()], 1)
                row["aff_spread"] = float((a_c @ sol[:2]).norm(dim=1).max())

        # 2./3. one translation per object: estimators, error to the RAFT object median, IoU of the moved mask
        prev = v["prev_lab"]
        cen = None
        if prev.any():
            cen = torch.stack([YS[prev].float().mean() - YS[tgt].float().mean(), XS[prev].float().mean() - XS[tgt].float().mean()])
        reg_inf = v["moved"]["softmax"].float() >= 0.5  # cells A-b assigns to the object (no frame-t mask needed)
        est = {"raft_med": d_raft, "arg_med": med(u["argmax"], tgt), "arg_mode": mode_int(u["argmax"], tgt),
               "soft_med": med(u["softmax"], tgt), "zero": torch.zeros(2)}
        if reg_inf.any():
            est["arg_med_inf"] = med(u["argmax"], reg_inf)
            est["arg_mode_inf"] = mode_int(u["argmax"], reg_inf)
            est["soft_med_inf"] = med(u["softmax"], reg_inf)
        if cen is not None:
            est["centroid"] = cen
        for name, d in est.items():
            row[f"iou_{name}"] = iou(warp(cov, d) >= 0.5, tgt)
            row[f"epe_{name}"] = float((d.view(2, 1, 1) - u["raft"]).norm(dim=0)[tgt].mean())
            if name != "raft_med":
                row[f"err_{name}"] = float((d - d_raft).norm())
        row["iou_oracle_int"], d_or = best_translation(cov, tgt, INT)
        row["iou_oracle_half"], _ = best_translation(cov, tgt, HALF)
        row["err_oracle_int"] = float((d_or - d_raft).norm())

        # 4. block-wise voting = median filter of the argmax field (mask-free, and restricted to the object)
        for k in (3, 5, 9, 15):
            for tag, mask in (("", None), ("m", tgt)):
                ub = block_median(u["argmax"], k, mask)
                g1, fold = coherence(ub, tgt)
                row[f"blk{k}{tag}_gt1"], row[f"blk{k}{tag}_fold"] = g1, fold
                row[f"blk{k}{tag}_epe"] = float((ub - u["raft"]).norm(dim=0)[tgt].mean())
                row[f"blk{k}{tag}_iou"] = iou(warp(cov, ub) >= 0.5, tgt)
        row["soft_epe"] = float((u["softmax"] - u["raft"]).norm(dim=0)[tgt].mean())
        row["arg_epe"] = float((u["argmax"] - u["raft"]).norm(dim=0)[tgt].mean())
        row["obj_raft_epe"] = float(res[tgt].mean())
        rows.append(row)

    args.out.mkdir(parents=True, exist_ok=True)
    with (args.out / "precheck.jsonl").open("w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")

    # aggregate: pairs -> object -> stratum
    metrics = [k for k in rows[0] if k not in ("video", "object", "t", "stratum", "cells", "interior_cells")]
    metrics = sorted({k for r in rows for k in r if k not in ("video", "object", "t", "stratum", "cells", "interior_cells")},
                     key=lambda k: (metrics.index(k) if k in metrics else 999, k))
    per_obj = defaultdict(lambda: defaultdict(list))
    obj_str = {}
    for r in rows:
        o = (r["video"], r["object"])
        obj_str[o] = r["stratum"]
        for k in metrics:
            if r.get(k) is not None:
                per_obj[o][k].append(r[k])
    rng = np.random.default_rng(123)
    lines = ["| metric | slow | mid | fast | all [95% CI] | objects |", "|---|---|---|---|---|---|"]
    for k in metrics:
        vals = {o: float(np.mean(x[k])) for o, x in per_obj.items() if k in x and obj_str[o] is not None}
        cells = []
        for s in ("slow", "mid", "fast"):
            a = [v for o, v in vals.items() if obj_str[o] == s]
            cells.append(f"{np.mean(a):.3f}" if a else "-")
        a = np.array(list(vals.values()))
        bs = a[rng.integers(0, len(a), (10000, len(a)))].mean(1)
        lines.append(f"| {k} | {cells[0]} | {cells[1]} | {cells[2]} | {a.mean():.3f} [{np.quantile(bs, .025):.3f}, {np.quantile(bs, .975):.3f}] | {len(a)} |")
    (args.out / "summary.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
