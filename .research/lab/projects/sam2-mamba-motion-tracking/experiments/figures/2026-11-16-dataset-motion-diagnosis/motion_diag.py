"""What kinds of motion do the objects of a dataset make on SAM2's 64x64 grid? (data diagnosis, not a method evaluation)

For pairs of frames (t - gap, t) of MOSE (GT masks) or DanceTrack (GT boxes -> SAM2 masks from a box prompt), an
optical-flow reference from frame t back to frame t - gap is fitted, inside each object, with
  (1) one translation, (2) one affine map, (3) one translation per k x k block of cells,
and the residuals say how much of the motion each model explains. No tracker, no adapter, no training.

Against the smoothness bias of RAFT (it may hide part-wise motion):
  * cells / pixels whose forward and backward RAFT flows disagree by more than 4 px (0.25 cell, the finest
    threshold reported) are "unknown", never counted as fitting; the share under the strict 11/13 test is also kept;
  * the fits are also made per pixel inside the mask (residual of the object-median flow, in pixels), and the spread
    of the flow inside each 16x16 cell is reported (a cell with two motions has no single displacement);
  * the cell flow of an object is averaged over the object's own pixels only (no background mixed in at the border);
  * the same numbers are computed with DIS (OpenCV, medium preset), a flow method with a different prior.

Run from the SAM2 repo root:
  CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=0 PYTHONPATH=$PWD .venv-sam2/bin/python <dir>/motion_diag.py \
      --dataset dancetrack --out <dir>/data/dancetrack --gaps 1 2 4 8 --pairs 12
"""
import argparse, configparser, json, platform, sys, time
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image
from torchvision.models.optical_flow import Raft_Large_Weights, raft_large

RES, CELL, CELLS = 1024, 16, 64
MOSE_ROOT = Path("/mnt/HDD10TB-2/aburatani/dataset/MOSE-v1-data/MOSE_release/train")
MOSE_MOTION = Path("/mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2/runs/spatial_mixing/motion/20261104/tuning_object_motion.jsonl")
DT_ROOTS = [Path("/mnt/HDD10TB-2/aburatani/dataset/DanceTrack/train1/train1"),
            Path("/mnt/HDD10TB-2/aburatani/dataset/DanceTrack/train2/train2")]
THRS = ((1.0, "1"), (0.5, "05"), (0.25, "025"))
BLOCKS = (3, 5, 9, 15)
MAG_BINS = ((0.0, 0.25, "<0.25"), (0.25, 0.62, "0.25-0.62"), (0.62, 1.23, "0.62-1.23"), (1.23, 1e9, ">=1.23"))


# ----------------------------------------------------------------------------- data
def mose_sequences(limit):
    objs = defaultdict(list)
    for line in MOSE_MOTION.read_text().splitlines():
        r = json.loads(line)
        objs[r["video"]].append(int(r["object_id"]))
    out = []
    for video in sorted(objs)[:limit]:
        ip = {int(p.stem): p for p in (MOSE_ROOT / "JPEGImages" / video).glob("*.jpg") if p.stem.isdigit()}
        mp = {int(p.stem): p for p in (MOSE_ROOT / "Annotations" / video).glob("*.png") if p.stem.isdigit()}
        fids = sorted(ip)
        out.append({"name": video, "images": [ip[f] for f in fids], "masks": [mp[f] for f in fids], "objects": objs[video]})
    return out


def dancetrack_sequences(limit, roots=None):
    """MOT-format sequences (img1/<frame>.jpg, gt/gt.txt with frame,id,x,y,w,h,...): DanceTrack, SportsMOT, ..."""
    out = []
    for seq in sorted(p for root in (roots or DT_ROOTS) for p in root.iterdir() if (p / "gt/gt.txt").exists())[:limit]:
        images = sorted((seq / "img1").glob("*.jpg"), key=lambda p: int(p.stem))
        index = {int(p.stem): i for i, p in enumerate(images)}
        gt = np.loadtxt(seq / "gt/gt.txt", delimiter=",")
        boxes = defaultdict(dict)  # image index -> track -> xyxy in original pixels
        for r in gt:
            if int(r[0]) in index and (gt.shape[1] < 7 or r[6] != 0):
                boxes[index[int(r[0])]][int(r[1])] = (r[2], r[3], r[2] + r[4], r[3] + r[5])
        out.append({"name": seq.name, "images": images, "boxes": boxes})
    return out


def mose_label(path):
    with Image.open(path) as f:
        big = np.asarray(f.convert("P").resize((RES, RES), Image.Resampling.NEAREST)).astype(np.int64)
    big[big == 255] = 0
    return torch.from_numpy(big)


def cover_by_others(boxes, tid):
    """Largest share of the box of `tid` covered by another GT box."""
    x1, y1, x2, y2 = boxes[tid]
    best = 0.0
    for o, (a1, b1, a2, b2) in boxes.items():
        if o != tid:
            best = max(best, max(0.0, min(x2, a2) - max(x1, a1)) * max(0.0, min(y2, b2) - max(y1, b1)))
    return best / max((x2 - x1) * (y2 - y1), 1e-6)


# ----------------------------------------------------------------------------- flow
def load_rgb(path):
    return np.asarray(Image.open(path).convert("RGB").resize((RES, RES), Image.Resampling.BILINEAR)).copy()


def raft_in(rgb, dev):
    return torch.from_numpy(rgb).to(dev).permute(2, 0, 1)[None].float() / 255.0 * 2 - 1


def consistent(b, f, slack=(0.5, 16.0)):
    """b, f [2, H, W] (dx, dy) px -> bool [H, W] per slack (px^2) for the pixels of frame t. slack 0.5 is the test of
    fair_iou.py (11/13); 16 (= 4 px = 0.25 cell) tolerates flow noise that cannot change a cell-level class."""
    ys, xs = torch.meshgrid(torch.arange(RES, device=b.device), torch.arange(RES, device=b.device), indexing="ij")
    gx, gy = (xs + 0.5 + b[0]) / RES * 2 - 1, (ys + 0.5 + b[1]) / RES * 2 - 1
    fw = F.grid_sample(f[None], torch.stack([gx, gy], -1)[None], mode="bilinear", padding_mode="border", align_corners=False)[0]
    lhs, rel, inside = ((b + fw) ** 2).sum(0), 0.01 * ((b ** 2).sum(0) + (fw ** 2).sum(0)), (gx.abs() <= 1) & (gy.abs() <= 1)
    return [(lhs < rel + a) & inside for a in slack]


# ----------------------------------------------------------------------------- fits
YS, XS = torch.meshgrid(torch.arange(CELLS), torch.arange(CELLS), indexing="ij")


def affine_fit(u, m, iters=3):
    ys, xs = YS[m].float(), XS[m].float()
    a = torch.stack([ys - ys.mean(), xs - xs.mean(), torch.ones_like(ys)], 1)
    b = torch.stack([u[0][m], u[1][m]], 1)
    keep, sol = torch.ones(len(ys), dtype=torch.bool), None
    for _ in range(iters):
        if int(keep.sum()) < 6:
            break
        sol = torch.linalg.lstsq(a[keep], b[keep]).solution
        res = (a @ sol - b).norm(dim=1)
        keep = res <= max(1.0, float(res.median()))
    return (None, None) if sol is None else ((a @ sol - b).norm(dim=1), sol)


def block_median(u, k, mask):
    r = k // 2
    x = u.clone()
    x[:, ~mask] = float("nan")
    p = F.unfold(F.pad(x[None], (r, r, r, r), value=float("nan")), k).view(2, k * k, CELLS, CELLS)
    return torch.nanmedian(p, dim=1).values.nan_to_num(0.0)


def cell_field(flow, w):
    """Mean of the pixel flow [2,H,W] (dx,dy px) over the weighted pixels of each cell -> u [2,64,64] (dy,dx cells),
    the weight sum per cell and the spread of the flow inside the cell (cells)."""
    cnt = F.avg_pool2d(w[None, None], CELL)[0, 0] * CELL * CELL
    mean = F.avg_pool2d((flow * w)[None], CELL)[0] * CELL * CELL / cnt.clamp(min=1)
    sq = F.avg_pool2d(((flow ** 2).sum(0) * w)[None, None], CELL)[0, 0] * CELL * CELL / cnt.clamp(min=1)
    spread = (sq - (mean ** 2).sum(0)).clamp(min=0).sqrt() / CELL
    return torch.stack([mean[1], mean[0]]) / CELL, cnt, spread


def fit_metrics(u, cells, prefix):
    """Translation / affine / block fits of the cell field u on the bool cells; residual shares and energies."""
    out, n = {}, int(cells.sum())
    if n < 3:
        return out
    d = torch.stack([u[0][cells].median(), u[1][cells].median()])
    rt = (u - d.view(2, 1, 1)).norm(dim=0)[cells]
    out[prefix + "mag"] = float(d.norm())
    out[prefix + "e_tot"] = float((u ** 2).sum(0)[cells].mean())
    out[prefix + "e_trans"] = float((rt ** 2).mean())
    for thr, tag in THRS:
        out[f"{prefix}trans_gt{tag}"] = float((rt > thr).float().mean())
    for k in BLOCKS:
        rb = (u - block_median(u, k, cells)).norm(dim=0)[cells]
        for thr, tag in THRS:
            out[f"{prefix}blk{k}_gt{tag}"] = float((rb > thr).float().mean())
    if n >= 20:
        ra, sol = affine_fit(u, cells)
        if ra is not None:
            out[prefix + "e_aff"] = float((ra ** 2).mean())
            for thr, tag in THRS:
                out[f"{prefix}cls{tag}_trans"] = float((rt <= thr).float().mean())
                out[f"{prefix}cls{tag}_affine"] = float(((rt > thr) & (ra <= thr)).float().mean())
                out[f"{prefix}cls{tag}_rest"] = float(((rt > thr) & (ra > thr)).float().mean())
            lin = torch.eye(2) + sol[:2].T
            det = float(torch.linalg.det(lin))
            if det > 0:
                out[prefix + "aff_scale_abs"] = abs(det ** 0.5 - 1)
                out[prefix + "aff_rot_deg"] = abs(float(torch.rad2deg(torch.atan2(lin[1, 0] - lin[0, 1], lin[0, 0] + lin[1, 1]))))
    return out


def object_metrics(mask, b, valid, dis, strict=None):
    """mask bool [H,W] (frame t), b RAFT flow t -> t-gap [2,H,W] px, valid bool [H,W], dis flow or None (all CPU)."""
    row, m = {}, mask.float()
    cov = F.avg_pool2d(m[None, None], CELL)[0, 0]
    tgt = cov >= 0.5
    row["cells"], row["pixels"] = int(tgt.sum()), int(mask.sum())
    if row["cells"] < 3:
        return row, None
    mv = mask & valid
    row["valid_px"] = float(mv.sum() / mask.sum())
    if strict is not None:
        row["valid_px_strict"] = float((mask & strict).sum() / mask.sum())
    # pixels: residual of the object-median flow
    if int(mv.sum()) >= 64:
        fb = b[:, mv]
        medp = fb.median(dim=1).values
        rp = (fb - medp[:, None]).norm(dim=0) / CELL
        row["pix_mag"] = float(medp.norm() / CELL)
        for thr, tag in THRS:
            row[f"pix_gt{tag}"] = float((rp > thr).float().mean())
        row["pix_res_mean"] = float(rp.mean())
    # cells: flow averaged over the object's own consistent pixels
    u, cnt, spread = cell_field(b, mv.float())
    mcnt = F.avg_pool2d(m[None, None], CELL)[0, 0] * CELL * CELL
    known = tgt & (cnt >= 0.5 * mcnt)
    row["unknown_cells"] = float(1 - known.sum() / tgt.sum())
    if int(known.sum()) >= 3:
        row["spread_mean"] = float(spread[known].mean())
        row["spread_gt05"] = float((spread[known] > 0.5).float().mean())
        row["spread_gt025"] = float((spread[known] > 0.25).float().mean())
        row.update(fit_metrics(u, known, ""))
    # 11/12-compatible: plain cell average (background mixed in), all target cells
    up = F.avg_pool2d(b[None], CELL)[0] / CELL
    up = torch.stack([up[1], up[0]])
    d = torch.stack([up[0][tgt].median(), up[1][tgt].median()])
    row["plain_trans_gt1"] = float(((up - d.view(2, 1, 1)).norm(dim=0)[tgt] > 1).float().mean())
    fields = {"tgt": tgt, "known": known, "u": u.half()}
    if dis is not None:
        ud, _, _ = cell_field(dis, m)
        row.update(fit_metrics(ud, tgt, "dis_"))
        if int(known.sum()) >= 3:
            diff = (u - ud).norm(dim=0)[known]
            row["agree05"] = float((diff <= 0.5).float().mean())
            row["agree025"] = float((diff <= 0.25).float().mean())
        fields["u_dis"] = ud.half()
    return row, fields


# ----------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", choices=["mose", "dancetrack"], required=True, help="dancetrack = any MOT-format dataset")
    ap.add_argument("--roots", type=Path, nargs="+", default=None, help="MOT-format split folders (default: DanceTrack train1/train2)")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--gaps", type=int, nargs="+", default=[1])
    ap.add_argument("--pairs", type=int, default=12, help="target frames per sequence (shared by all gaps)")
    ap.add_argument("--limit-seqs", type=int, default=None)
    ap.add_argument("--no-dis", action="store_true")
    ap.add_argument("--save-fields", type=Path, default=None)
    ap.add_argument("--expect-gpu", default="RTX A4000")
    ap.add_argument("--summary-only", action="store_true")
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    if args.summary_only:
        return summarize(args.out)
    dev = torch.device("cuda")
    if args.expect_gpu not in torch.cuda.get_device_name(0):
        sys.exit(f"cuda:0 is {torch.cuda.get_device_name(0)!r}; set CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES")
    seqs = mose_sequences(args.limit_seqs) if args.dataset == "mose" else dancetrack_sequences(args.limit_seqs, args.roots)
    raft = raft_large(weights=Raft_Large_Weights.DEFAULT, progress=False).eval().to(dev)
    dis = None if args.no_dis else cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
    predictor = None
    if args.dataset == "dancetrack":
        from sam2.build_sam import build_sam2
        from sam2.sam2_image_predictor import SAM2ImagePredictor
        predictor = SAM2ImagePredictor(build_sam2("configs/sam2.1/sam2.1_hiera_l.yaml", "checkpoints/sam2.1_hiera_large.pt", device=dev))
    meta = {"started": datetime.now().isoformat(timespec="seconds"), "host": platform.node(), "gpu": torch.cuda.get_device_name(0),
            "torch": torch.__version__, "argv": sys.argv, "dataset": args.dataset, "gaps": args.gaps, "pairs": args.pairs,
            "sequences": len(seqs), "raft": "torchvision raft_large, 12 updates, 1024x1024", "dis": None if dis is None else "medium preset, 1024x1024 gray"}
    (args.out / "meta.json").write_text(json.dumps(meta, indent=1))
    gmax, rows, store, clock = max(args.gaps), [], {}, defaultdict(float)
    t0 = time.time()
    for si, seq in enumerate(seqs):
        n = len(seq["images"])
        if n <= gmax:
            continue
        ts = sorted({int(round(x)) for x in np.linspace(gmax, n - 1, min(args.pairs, n - gmax))})
        for t in ts:
            rgb_t = load_rgb(seq["images"][t])
            # objects of frame t
            masks, tags = {}, {}
            if args.dataset == "mose":
                lab = mose_label(seq["masks"][t])
                for oid in seq["objects"]:
                    if (lab == oid).any():
                        masks[oid] = lab == oid
            else:
                c = time.time()
                boxes = seq["boxes"].get(t, {})
                if boxes:
                    with Image.open(seq["images"][t]) as im:
                        full = np.asarray(im.convert("RGB"))
                    with torch.inference_mode(), torch.autocast("cuda", dtype=torch.bfloat16):
                        predictor.set_image(full)
                        for tid, box in boxes.items():
                            mk, _, _ = predictor.predict(box=np.array(box, dtype=np.float32), multimask_output=False)
                            mk = mk[0] > 0
                            if mk.sum() == 0:
                                continue
                            yy, xx = np.nonzero(mk)
                            ix = max(0.0, min(box[2], xx.max() + 1) - max(box[0], xx.min())) * max(0.0, min(box[3], yy.max() + 1) - max(box[1], yy.min()))
                            un = (box[2] - box[0]) * (box[3] - box[1]) + (xx.max() + 1 - xx.min()) * (yy.max() + 1 - yy.min()) - ix
                            tags[tid] = {"mask_box_iou": float(ix / un), "cover_cur": cover_by_others(boxes, tid)}
                            masks[tid] = torch.from_numpy(cv2.resize(mk.astype(np.uint8), (RES, RES), interpolation=cv2.INTER_NEAREST) > 0)
                clock["sam2"] += time.time() - c
            if not masks:
                continue
            gray_t = cv2.cvtColor(rgb_t, cv2.COLOR_RGB2GRAY)
            for gap in args.gaps:
                s = t - gap
                rgb_s = load_rgb(seq["images"][s])
                if args.dataset == "mose":
                    lab_s = mose_label(seq["masks"][s])
                    present = {oid: int((lab_s == oid).sum()) for oid in masks}
                else:
                    bs = seq["boxes"].get(s, {})
                    present = {tid: 1 if tid in bs else 0 for tid in masks}
                if not any(present.values()):
                    continue
                c = time.time()
                with torch.inference_mode():
                    xt, xs_ = raft_in(rgb_t, dev), raft_in(rgb_s, dev)
                    b = raft(xt, xs_, num_flow_updates=12)[-1][0].float()
                    f = raft(xs_, xt, num_flow_updates=12)[-1][0].float()
                    strict, valid = (x.cpu() for x in consistent(b, f))
                    b = b.cpu()
                torch.cuda.synchronize()
                clock["raft"] += time.time() - c
                c = time.time()
                dflow = None
                if dis is not None:
                    dflow = torch.from_numpy(dis.calc(gray_t, cv2.cvtColor(rgb_s, cv2.COLOR_RGB2GRAY), None)).permute(2, 0, 1).float()
                clock["dis"] += time.time() - c
                clock["pairs"] += 1
                for oid, mask in masks.items():
                    if not present[oid]:
                        continue
                    row, fields = object_metrics(mask, b, valid, dflow, strict)
                    row.update({"seq": seq["name"], "object": int(oid), "t": t, "gap": gap, **tags.get(oid, {})})
                    if args.dataset == "mose":
                        row["area_ratio"] = float(mask.sum()) / present[oid]
                    else:
                        row["cover_prev"] = cover_by_others(bs, oid)
                        bt, bp = seq["boxes"][t][oid], bs[oid]
                        row["area_ratio"] = float((bt[2] - bt[0]) * (bt[3] - bt[1]) / max((bp[2] - bp[0]) * (bp[3] - bp[1]), 1e-6))
                    rows.append(row)
                    if args.save_fields is not None and fields is not None:
                        store[(seq["name"], int(oid), t, gap)] = fields
        print(json.dumps({"i": si, "seq": seq["name"], "frames": n, "rows": len(rows), "elapsed_s": round(time.time() - t0, 1),
                          **{k: round(v, 1) for k, v in clock.items()}}), flush=True)
    with (args.out / "rows.jsonl").open("w") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    if args.save_fields is not None:
        args.save_fields.parent.mkdir(parents=True, exist_ok=True)
        torch.save(store, args.save_fields)
    meta.update({"finished": datetime.now().isoformat(timespec="seconds"), "rows": len(rows), "seconds": {k: round(v, 1) for k, v in clock.items()}})
    (args.out / "meta.json").write_text(json.dumps(meta, indent=1))
    summarize(args.out)


KEYS = ["valid_px", "valid_px_strict", "unknown_cells", "mag", "pix_gt1", "pix_gt05", "pix_gt025", "spread_mean", "spread_gt05", "spread_gt025",
        "trans_gt1", "trans_gt05", "trans_gt025", "cls1_trans", "cls1_affine", "cls1_rest", "cls05_trans", "cls05_affine", "cls05_rest",
        "cls025_trans", "cls025_affine", "cls025_rest", "blk3_gt05", "blk5_gt05", "blk9_gt05", "blk15_gt05", "blk3_gt1", "blk9_gt1", "blk15_gt1",
        "aff_rot_deg", "aff_scale_abs", "agree05", "agree025", "dis_trans_gt1", "dis_trans_gt05", "dis_cls05_trans", "dis_cls05_affine",
        "dis_cls05_rest", "dis_blk9_gt05", "plain_trans_gt1"]


def table(rows, title, rng):
    per = defaultdict(lambda: defaultdict(list))
    for r in rows:
        for k in KEYS + ["e_tot", "e_trans", "e_aff"]:
            if r.get(k) is not None:
                per[(r["seq"], r["object"])][k].append(r[k])
    lines = [f"### {title}（{len(rows)} 行、{len(per)} 物体）", "", "| metric | mean [95% CI] | objects |", "|---|---|---|"]
    for k in KEYS:
        a = np.array([np.mean(v[k]) for v in per.values() if k in v])
        if len(a) == 0:
            continue
        bs = a[rng.integers(0, len(a), (2000, len(a)))].mean(1)
        lines.append(f"| {k} | {a.mean():.3f} [{np.quantile(bs, .025):.3f}, {np.quantile(bs, .975):.3f}] | {len(a)} |")
    for name, key in (("unexplained by one translation", "e_trans"), ("unexplained by one affine map", "e_aff")):
        num = sum(np.sum(v[key]) for v in per.values() if key in v and "e_tot" in v)
        den = sum(np.sum(v["e_tot"][: len(v[key])]) for v in per.values() if key in v and "e_tot" in v)
        if den > 0:
            lines.append(f"| share of squared motion {name} | {num / den:.3f} | |")
    return lines + [""]


def summarize(out):
    rows = [json.loads(x) for x in (out / "rows.jsonl").read_text().splitlines()]
    rows = [r for r in rows if r.get("cells", 0) >= 3 and r.get("mask_box_iou", 1.0) >= 0.5]
    rng, lines = np.random.default_rng(123), []
    for gap in sorted({r["gap"] for r in rows}):
        g = [r for r in rows if r["gap"] == gap]
        lines += [f"## gap {gap}", ""] + table(g, "all", rng)
        for lo, hi, name in MAG_BINS:
            sub = [r for r in g if r.get("mag") is not None and lo <= r["mag"] < hi]
            if len(sub) >= 20:
                lines += table(sub, f"object motion {name} cells", rng)
        if any("cover_cur" in r for r in g):
            for name, cond in (("no overlap (cover < 0.1 in both frames)", lambda r: r["cover_cur"] < 0.1 and r["cover_prev"] < 0.1),
                               ("overlapped now (cover >= 0.3)", lambda r: r["cover_cur"] >= 0.3),
                               ("released (cover fell by >= 0.2)", lambda r: r["cover_prev"] - r["cover_cur"] >= 0.2)):
                sub = [r for r in g if "cover_cur" in r and cond(r)]
                if len(sub) >= 20:
                    lines += table(sub, name, rng)
        else:
            sub = [r for r in g if r.get("area_ratio", 1) >= 1.25]
            if len(sub) >= 20:
                lines += table(sub, "visible area grew by >= 25%", rng)
    (out / "summary.md").write_text("\n".join(lines) + "\n")
    print(f"summary -> {out / 'summary.md'}")


if __name__ == "__main__":
    main()
