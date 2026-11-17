"""CPU-only: how far do DanceTrack objects move per frame on SAM2's 64x64 grid (from the GT boxes)?

Box centre displacement between frames t-gap and t, in cells of the 64x64 map of the 1024x1024 resized input
(x * 64 / W, y * 64 / H), per track: median over the track's frames (the same summary as the MOSE strata file,
which uses mask centroids). Also box size in cells, per-frame size change, objects per frame and an occlusion
proxy (share of the box covered by another GT box).
"""
import argparse, configparser, json
from pathlib import Path
import numpy as np

CUTS = (0.6201862142364104, 1.2327169820960704)  # MOSE tuning tertile cuts (cells / frame)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    rows, seqs = [], sorted(p for p in args.root.iterdir() if (p / "gt/gt.txt").exists())
    cover_all, nobj = [], []
    for seq in seqs:
        ini = configparser.ConfigParser(); ini.read(seq / "seqinfo.ini")
        w, h, fps = int(ini["Sequence"]["imWidth"]), int(ini["Sequence"]["imHeight"]), int(ini["Sequence"]["frameRate"])
        gt = np.loadtxt(seq / "gt/gt.txt", delimiter=",")
        frames = {}
        for f in np.unique(gt[:, 0]):
            b = gt[gt[:, 0] == f]
            nobj.append(len(b))
            x1, y1, x2, y2 = b[:, 2], b[:, 3], b[:, 2] + b[:, 4], b[:, 3] + b[:, 5]
            iw = np.clip(np.minimum(x2[:, None], x2[None]) - np.maximum(x1[:, None], x1[None]), 0, None)
            ih = np.clip(np.minimum(y2[:, None], y2[None]) - np.maximum(y1[:, None], y1[None]), 0, None)
            inter = iw * ih
            np.fill_diagonal(inter, 0)
            cov = inter.max(1) / (b[:, 4] * b[:, 5]) if len(b) > 1 else np.zeros(len(b))
            for i, tid in enumerate(b[:, 1]):
                frames[(int(tid), int(f))] = cov[i]
            cover_all.extend(cov.tolist())
        for tid in np.unique(gt[:, 1]):
            t = gt[gt[:, 1] == tid]
            t = t[np.argsort(t[:, 0])]
            f = t[:, 0]
            cx, cy = (t[:, 2] + t[:, 4] / 2) * 64 / w, (t[:, 3] + t[:, 5] / 2) * 64 / h
            bw, bh = t[:, 4] * 64 / w, t[:, 5] * 64 / h
            row = {"seq": seq.name, "track": int(tid), "frames": len(t), "fps": fps, "w_cells": float(np.median(bw)),
                   "h_cells": float(np.median(bh)), "cells": float(np.median(bw * bh))}
            for gap in (1, 2, 4, 8):
                idx = {int(a): i for i, a in enumerate(f)}
                pairs = [(idx[int(a) - gap], i) for i, a in enumerate(f) if int(a) - gap in idx]
                if not pairs:
                    continue
                a, b = np.array(pairs).T
                d = np.hypot(cx[b] - cx[a], cy[b] - cy[a])
                row[f"med_gap{gap}"] = float(np.median(d))
                row[f"p90_gap{gap}"] = float(np.quantile(d, 0.9))
                row[f"gt7_gap{gap}"] = float((d > 7).mean())
                s = np.sqrt((bw[b] * bh[b]) / (bw[a] * bh[a]))
                row[f"scale_gap{gap}"] = float(np.median(np.abs(s - 1)))
            rows.append(row)
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "box_motion.jsonl").write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    out = [f"sequences {len(seqs)}, tracks {len(rows)}, objects per frame: median {np.median(nobj):.0f}, mean {np.mean(nobj):.1f}",
           f"box size (cells, median over tracks): width {np.median([r['w_cells'] for r in rows]):.1f}, height {np.median([r['h_cells'] for r in rows]):.1f}, area {np.median([r['cells'] for r in rows]):.0f}",
           f"occlusion proxy (share of the box covered by another GT box): > 0.3 in {np.mean(np.array(cover_all) > 0.3):.3f} of object-frames, > 0.5 in {np.mean(np.array(cover_all) > 0.5):.3f}",
           "", "| gap (frames) | median of track medians (cells) | p25 | p75 | tracks slow / mid / fast by the MOSE cuts | median p90 within a track | pairs beyond 7 cells | median size change |",
           "|---|---|---|---|---|---|---|---|"]
    for gap in (1, 2, 4, 8):
        m = np.array([r[f"med_gap{gap}"] for r in rows if f"med_gap{gap}" in r])
        strata = [(m < CUTS[0]).mean(), ((m >= CUTS[0]) & (m < CUTS[1])).mean(), (m >= CUTS[1]).mean()]
        out.append(f"| {gap} | {np.median(m):.3f} | {np.quantile(m, .25):.3f} | {np.quantile(m, .75):.3f} | "
                   f"{strata[0]:.2f} / {strata[1]:.2f} / {strata[2]:.2f} | {np.median([r[f'p90_gap{gap}'] for r in rows if f'p90_gap{gap}' in r]):.3f} | "
                   f"{np.mean([r[f'gt7_gap{gap}'] for r in rows if f'gt7_gap{gap}' in r]):.4f} | {np.median([r[f'scale_gap{gap}'] for r in rows if f'scale_gap{gap}' in r]):.3f} |")
    (args.out / "box_motion_summary.md").write_text("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
