"""Select fast / slow MOSE tuning videos for the optical flow cost check (2026-11-11).

Rule: tuning videos (runs/mose_temporal_mamba_20260930/tuning_trajectories.json, 125 videos from MOSE train)
whose native size is 1920x1080, whose objects are all in the same speed stratum
(motion_summary.json tertile cuts; per-object median step in stride-16 cells of the 1024x1024 input),
and which have at least --min-frames frames. fast = top 3 by the video median of object medians,
slow = bottom 3.

Usage (from anywhere; paths are absolute):
  python select_videos.py --out data/selected_videos.json
"""
import argparse, collections, json, os, statistics as st
from PIL import Image

SAM2 = "/mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2"
MOTION = f"{SAM2}/runs/spatial_mixing/motion/20261104"
R = "/mnt/HDD10TB-2/aburatani/dataset/MOSE-v1-data/MOSE_release/train"


def frames_of(vid):
    return sorted(f for f in os.listdir(f"{R}/JPEGImages/{vid}") if not f.startswith("."))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-frames", type=int, default=21)
    ap.add_argument("--n", type=int, default=3)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    cut1, cut2 = json.load(open(f"{MOTION}/motion_summary.json"))["tuning_speed_strata"]["tertile_cuts_cells"]
    per_video = collections.defaultdict(list)
    for line in open(f"{MOTION}/tuning_object_motion.jsonl"):
        r = json.loads(line)
        if r.get("median") is not None:
            per_video[r["video"]].append((int(r["object_id"]), r["median"]))
    cand = []
    for vid, objs in per_video.items():
        fs = frames_of(vid)
        if Image.open(f"{R}/JPEGImages/{vid}/{fs[0]}").size != (1920, 1080) or len(fs) < args.min_frames:
            continue
        meds = [m for _, m in objs]
        if all(m >= cut2 for m in meds):
            stratum = "fast"
        elif all(m < cut1 for m in meds):
            stratum = "slow"
        else:
            continue
        cand.append({"video": vid, "stratum": stratum, "video_median_cells": st.median(meds),
                     "objects": [o for o, _ in objs], "object_medians_cells": meds, "frames": len(fs)})
    fast = sorted([c for c in cand if c["stratum"] == "fast"], key=lambda c: -c["video_median_cells"])[: args.n]
    slow = sorted([c for c in cand if c["stratum"] == "slow"], key=lambda c: c["video_median_cells"])[: args.n]
    out = {"rule": __doc__.split("Usage")[0].strip(), "cuts_cells": [cut1, cut2], "min_frames": args.min_frames,
           "candidates": len(cand), "fast": fast, "slow": slow}
    json.dump(out, open(args.out, "w"), indent=1)
    for c in fast + slow:
        print(c["stratum"], c["video"], f"{c['video_median_cells']:.2f}", c["frames"])


if __name__ == "__main__":
    main()
