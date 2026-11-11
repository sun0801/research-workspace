"""OpenCV optical flow (Farneback / DIS) cost on MOSE tuning videos (2026-11-11, A-a homework of the 11/6 MTG).

Main value: time of the flow call only (grayscale uint8 frames already resized in memory).
Separately: preprocessing time (resize with INTER_AREA + BGR->gray) per frame; JPEG decode is not timed.
Reference only: per object, median flow inside mask_t vs centroid(mask_{t+1}) - centroid(mask_t), both in
stride-16 cells of the 1024x1024 SAM2 input (x * 64 / W, y * 64 / H). The centroid step is not the true motion
when the object deforms or is occluded.

Usage:
  python flow_cost.py --selection data/selected_videos.json --out data/timing.json
  python flow_cost.py --selection data/selected_videos.json --sizes 1024sq --threads 1 --out data/timing_repeat.json
"""
import argparse, json, os, platform, sys, time
from datetime import datetime
import numpy as np
import cv2
from PIL import Image

R = "/mnt/HDD10TB-2/aburatani/dataset/MOSE-v1-data/MOSE_release/train"
SIZES = {"native": None, "1024sq": (1024, 1024), "512sq": (512, 512), "256sq": (256, 256)}
FARNEBACK = dict(pyr_scale=0.5, levels=3, winsize=15, iterations=3, poly_n=5, poly_sigma=1.2, flags=0)
DIS_PRESETS = {"dis_ultrafast": cv2.DISOPTICAL_FLOW_PRESET_ULTRAFAST, "dis_fast": cv2.DISOPTICAL_FLOW_PRESET_FAST,
               "dis_medium": cv2.DISOPTICAL_FLOW_PRESET_MEDIUM}


def frames_of(vid):
    return sorted(f for f in os.listdir(f"{R}/JPEGImages/{vid}") if not f.startswith("."))


def make_methods():
    out = {"farneback": lambda a, b: cv2.calcOpticalFlowFarneback(a, b, None, **FARNEBACK)}
    for name, preset in DIS_PRESETS.items():
        dis = cv2.DISOpticalFlow_create(preset)
        out[name] = (lambda d: (lambda a, b: d.calc(a, b, None)))(dis)
    return out


def preprocess(im, sz):
    return cv2.cvtColor(im if sz is None else cv2.resize(im, sz, interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY)


def env_info():
    cpu = next((l.split(":", 1)[1].strip() for l in open("/proc/cpuinfo") if l.startswith("model name")), None)
    par = [l.strip() for l in cv2.getBuildInformation().splitlines() if "Parallel framework" in l]
    return {"started": datetime.now().isoformat(timespec="seconds"), "host": platform.node(),
            "python": sys.version.split()[0], "numpy": np.__version__, "cv2": cv2.__version__,
            "cv2_parallel": par, "cv2_cuda_devices": cv2.cuda.getCudaEnabledDeviceCount(),
            "cv2_default_threads": cv2.getNumThreads(), "cpu_model": cpu, "cpu_count": os.cpu_count(),
            "loadavg_start": os.getloadavg(), "argv": sys.argv}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selection", required=True)
    ap.add_argument("--pairs", type=int, default=20, help="first N consecutive frame pairs per video")
    ap.add_argument("--warmup", type=int, default=2)
    ap.add_argument("--sizes", nargs="+", default=list(SIZES))
    ap.add_argument("--threads", type=int, nargs="+", default=[-1, 1], help="-1 = OpenCV default")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    sel = json.load(open(args.selection))
    videos = [(c["video"], c["stratum"]) for c in sel["fast"] + sel["slow"]]
    meta = env_info()
    meta.update({"pairs": args.pairs, "warmup": args.warmup, "farneback": FARNEBACK,
                 "dis_presets": list(DIS_PRESETS), "selection": args.selection})
    default_threads = meta["cv2_default_threads"]
    print(json.dumps(meta), flush=True)
    rows, prep = [], []
    for vid, stratum in videos:
        fs = frames_of(vid)[: args.pairs + 1]
        imgs = [cv2.imread(f"{R}/JPEGImages/{vid}/{f}") for f in fs]
        masks = [np.array(Image.open(f"{R}/Annotations/{vid}/{f[:-4]}.png")) for f in fs]
        H, W = imgs[0].shape[:2]
        ids = sorted(int(x) for x in np.unique(masks[0]) if x != 0)
        for sname in args.sizes:
            sz = SIZES[sname]
            for th in args.threads:
                nth = default_threads if th == -1 else th
                cv2.setNumThreads(nth)
                pt = []
                for im in imgs:
                    t0 = time.perf_counter(); preprocess(im, sz); pt.append((time.perf_counter() - t0) * 1e3)
                prep.append({"video": vid, "size": sname, "threads": nth, "ms_median": float(np.median(pt)),
                             "times_ms": pt})
                grays = [preprocess(im, sz) for im in imgs]
                h, w = grays[0].shape
                for mname, fn in make_methods().items():
                    for _ in range(args.warmup):
                        fn(grays[0], grays[1])
                    times, errs, steps, zeros = [], [], [], []
                    for t in range(len(grays) - 1):
                        t0 = time.perf_counter()
                        flow = fn(grays[t], grays[t + 1])
                        times.append((time.perf_counter() - t0) * 1e3)
                        if th != args.threads[0]:
                            continue  # accuracy does not depend on threads; compute once
                        fx = flow[..., 0] * 64 / w  # -> cells of the 64x64 grid
                        fy = flow[..., 1] * 64 / h
                        for oid in ids:
                            m0, m1 = masks[t] == oid, masks[t + 1] == oid
                            if m0.sum() < 20 or m1.sum() < 20:
                                continue
                            y0, x0 = np.nonzero(m0); y1, x1 = np.nonzero(m1)
                            gdx = (x1.mean() - x0.mean()) * 64 / W
                            gdy = (y1.mean() - y0.mean()) * 64 / H
                            ms = cv2.resize(m0.astype(np.uint8), (w, h), interpolation=cv2.INTER_NEAREST) > 0
                            if ms.sum() == 0:
                                continue
                            pdx, pdy = np.median(fx[ms]), np.median(fy[ms])
                            errs.append(float(np.hypot(pdx - gdx, pdy - gdy)))
                            steps.append(float(max(abs(gdx), abs(gdy))))
                            zeros.append(float(np.hypot(gdx, gdy)))
                    r = {"video": vid, "stratum": stratum, "native": [W, H], "size": sname, "wh": [w, h],
                         "threads": nth, "method": mname, "pairs": len(times),
                         "ms_median": float(np.median(times)), "ms_mean": float(np.mean(times)),
                         "ms_p90": float(np.percentile(times, 90)), "times_ms": times}
                    if errs:
                        r.update({"obj_steps": len(errs), "err_cells_median": float(np.median(errs)),
                                  "zero_flow_err_median": float(np.median(zeros)),
                                  "gt_step_cells_median": float(np.median(steps))})
                    rows.append(r)
                    print(json.dumps({k: v for k, v in r.items() if k != "times_ms"}), flush=True)
    meta["loadavg_end"] = os.getloadavg()
    meta["finished"] = datetime.now().isoformat(timespec="seconds")
    json.dump({"meta": meta, "rows": rows, "preprocess": prep}, open(args.out, "w"), indent=1)


if __name__ == "__main__":
    main()
