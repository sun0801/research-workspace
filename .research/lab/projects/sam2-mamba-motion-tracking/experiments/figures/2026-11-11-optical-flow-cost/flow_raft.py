"""RAFT (torchvision raft_small / raft_large, official weights) on GPU: cost and reference error (2026-11-11).

Same videos, pairs and reference error as flow_cost.py. Run with CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=0 (RTX A4000; GPU 1 is used by Kaggle). Without
CUDA_DEVICE_ORDER, CUDA orders the faster GPU first and device 0 becomes the RTX PRO 4500 (nvidia-smi GPU 1).
Main value: model forward only (both frames already on the GPU, normalised to [-1, 1] by the weights' transforms),
timed with torch.cuda.synchronize(). Separately: uint8 BGR -> GPU tensor, resize (bilinear, antialias) and
normalise, per frame pair. Returned flow = last of the iterative updates (num_flow_updates, default 12).
Sizes are square and divisible by 8 (RAFT requirement), so native 1920x1080 is not run.

Usage:
  CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=0 python flow_raft.py --selection data/selected_videos.json \
      --updates 12 6 --out data/timing_raft.json
"""
import argparse, json, os, platform, sys, time
from datetime import datetime
import numpy as np
import cv2
import torch
import torch.nn.functional as F
from PIL import Image
from torchvision.models.optical_flow import raft_small, raft_large, Raft_Small_Weights, Raft_Large_Weights

from flow_cost import R, frames_of

MODELS = {"raft_small": (raft_small, Raft_Small_Weights.DEFAULT), "raft_large": (raft_large, Raft_Large_Weights.DEFAULT)}
SIZES = {"1024sq": 1024, "512sq": 512, "256sq": 256}


def load(name, dev):
    fn, w = MODELS[name]
    return fn(weights=w, progress=False).eval().to(dev), w


def to_input(im_bgr, s, dev):
    """uint8 HxWx3 BGR (numpy) -> 1x3xSxS float in [-1, 1] on dev."""
    x = torch.from_numpy(im_bgr[..., ::-1].copy()).to(dev).permute(2, 0, 1)[None].float() / 255.0
    x = F.interpolate(x, size=(s, s), mode="bilinear", antialias=True, align_corners=False)
    return x * 2 - 1  # same as Raft_*_Weights.transforms() (ConvertImageDtype + Normalize(0.5, 0.5))


@torch.inference_mode()
def raft_flow(model, a, b, updates):
    return model(a, b, num_flow_updates=updates)[-1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selection", required=True)
    ap.add_argument("--pairs", type=int, default=20)
    ap.add_argument("--warmup", type=int, default=3)
    ap.add_argument("--updates", type=int, nargs="+", default=[12])
    ap.add_argument("--sizes", nargs="+", default=list(SIZES))
    ap.add_argument("--models", nargs="+", default=list(MODELS))
    ap.add_argument("--expect-gpu", default="RTX A4000", help="abort unless cuda:0 has this in its name")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    dev = torch.device("cuda")
    if args.expect_gpu not in torch.cuda.get_device_name(0):
        sys.exit(f"cuda:0 is {torch.cuda.get_device_name(0)!r}, expected {args.expect_gpu!r}; "
                 "set CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=0")
    sel = json.load(open(args.selection))
    videos = [(c["video"], c["stratum"]) for c in sel["fast"] + sel["slow"]]
    meta = {"started": datetime.now().isoformat(timespec="seconds"), "host": platform.node(),
            "python": sys.version.split()[0], "torch": torch.__version__,
            "torchvision": __import__("torchvision").__version__, "gpu": torch.cuda.get_device_name(0),
            "CUDA_VISIBLE_DEVICES": os.environ.get("CUDA_VISIBLE_DEVICES"),
            "CUDA_DEVICE_ORDER": os.environ.get("CUDA_DEVICE_ORDER"),
            "cudnn_allow_tf32": torch.backends.cudnn.allow_tf32,
            "matmul_allow_tf32": torch.backends.cuda.matmul.allow_tf32, "cudnn_benchmark": torch.backends.cudnn.benchmark,
            "dtype": "float32", "weights": {k: str(v[1]) for k, v in MODELS.items()}, "argv": sys.argv,
            "pairs": args.pairs, "warmup": args.warmup}
    print(json.dumps(meta), flush=True)
    rows = []
    for mname in args.models:
        model, _ = load(mname, dev)
        for sname in args.sizes:
            s = SIZES[sname]
            for upd in args.updates:
                torch.cuda.reset_peak_memory_stats()
                for vid, stratum in videos:
                    fs = frames_of(vid)[: args.pairs + 1]
                    imgs = [cv2.imread(f"{R}/JPEGImages/{vid}/{f}") for f in fs]
                    masks = [np.array(Image.open(f"{R}/Annotations/{vid}/{f[:-4]}.png")) for f in fs]
                    H, W = masks[0].shape
                    ids = sorted(int(x) for x in np.unique(masks[0]) if x != 0)
                    pt = []
                    xs = []
                    for im in imgs:
                        torch.cuda.synchronize(); t0 = time.perf_counter()
                        xs.append(to_input(im, s, dev))
                        torch.cuda.synchronize(); pt.append((time.perf_counter() - t0) * 1e3)
                    for _ in range(args.warmup):
                        raft_flow(model, xs[0], xs[1], upd)
                    times, errs, zeros = [], [], []
                    for t in range(len(xs) - 1):
                        torch.cuda.synchronize(); t0 = time.perf_counter()
                        flow = raft_flow(model, xs[t], xs[t + 1], upd)
                        torch.cuda.synchronize(); times.append((time.perf_counter() - t0) * 1e3)
                        f = flow[0].permute(1, 2, 0).cpu().numpy()
                        fx, fy = f[..., 0] * 64 / s, f[..., 1] * 64 / s  # -> cells of the 64x64 grid
                        for oid in ids:
                            m0, m1 = masks[t] == oid, masks[t + 1] == oid
                            if m0.sum() < 20 or m1.sum() < 20:
                                continue
                            y0, x0 = np.nonzero(m0); y1, x1 = np.nonzero(m1)
                            gdx = (x1.mean() - x0.mean()) * 64 / W
                            gdy = (y1.mean() - y0.mean()) * 64 / H
                            ms = cv2.resize(m0.astype(np.uint8), (s, s), interpolation=cv2.INTER_NEAREST) > 0
                            if ms.sum() == 0:
                                continue
                            errs.append(float(np.hypot(np.median(fx[ms]) - gdx, np.median(fy[ms]) - gdy)))
                            zeros.append(float(np.hypot(gdx, gdy)))
                    r = {"video": vid, "stratum": stratum, "native": [W, H], "size": sname, "wh": [s, s],
                         "method": mname, "updates": upd, "pairs": len(times),
                         "ms_median": float(np.median(times)), "ms_mean": float(np.mean(times)),
                         "ms_p90": float(np.percentile(times, 90)), "times_ms": times,
                         "prep_ms_median": float(np.median(pt)), "prep_times_ms": pt}
                    if errs:
                        r.update({"obj_steps": len(errs), "err_cells_median": float(np.median(errs)),
                                  "zero_flow_err_median": float(np.median(zeros))})
                    rows.append(r)
                    print(json.dumps({k: v for k, v in r.items() if not k.endswith("times_ms")}), flush=True)
                peak = torch.cuda.max_memory_allocated() / 2**20
                for r in rows:
                    if r["method"] == mname and r["size"] == sname and r["updates"] == upd:
                        r["peak_alloc_mib"] = peak
                print(f"# {mname} {sname} updates={upd} peak_alloc {peak:.0f} MiB", flush=True)
        del model
        torch.cuda.empty_cache()
    meta["finished"] = datetime.now().isoformat(timespec="seconds")
    json.dump({"meta": meta, "rows": rows}, open(args.out, "w"), indent=1)


if __name__ == "__main__":
    main()
