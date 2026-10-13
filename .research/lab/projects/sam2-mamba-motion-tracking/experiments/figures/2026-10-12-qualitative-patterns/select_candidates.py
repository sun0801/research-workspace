#!/usr/bin/env python3
"""Rank DanceTrack val windows for the 4-pattern qualitative comparison.

Per frame, GT and predictions are matched by Hungarian matching at IoU >= 0.5.
For each GT ID and window: coverage is the matched-frame ratio, keep is the
ratio of frames matched to the tracker ID that dominated the first 10 frames,
and transfer is 1 when the dominant ID of the last 10 frames differs.
"""

import csv
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.optimize import linear_sum_assignment

ROOT = Path("/mnt/HDD10TB-2/aburatani")
GT_DIR = ROOT / "TrackEval/data/gt/dancetrack/val"
# 定量表（HOTA 51.3 / 54.1 / 55.5）と同じ出力
METHODS = {
    "sam2": ROOT / "TrackEval/data/trackers/dancetrack/val/my_sam2_model/data",
    "samurai": ROOT / "TrackEval/data/trackers/dancetrack/val/my_samurai_model/data",
    "ours": ROOT / "2025_03_aburatani_sam2/results/sam2_stateful_minimal/20260723T_sam2_minimal_25seq/samurai_mamba_stateful_tiny",
}
WINDOW, STRIDE, IOU_THR = 60, 10, 0.5
OUT_DIR = Path(__file__).parent


def read_mot(path):
    rows = defaultdict(list)
    with open(path, newline="") as stream:
        for row in csv.reader(stream):
            if row:
                rows[int(float(row[0]))].append((int(float(row[1])), *map(float, row[2:6])))
    return rows


def iou_matrix(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    ax2, ay2 = a[:, 0] + a[:, 2], a[:, 1] + a[:, 3]
    bx2, by2 = b[:, 0] + b[:, 2], b[:, 1] + b[:, 3]
    iw = np.clip(np.minimum(ax2[:, None], bx2) - np.maximum(a[:, None, 0], b[:, 0]), 0, None)
    ih = np.clip(np.minimum(ay2[:, None], by2) - np.maximum(a[:, None, 1], b[:, 1]), 0, None)
    inter = iw * ih
    union = (a[:, 2] * a[:, 3])[:, None] + b[:, 2] * b[:, 3] - inter
    return np.where(union > 0, inter / union, 0.0)


def match_sequence(gt, pred):
    """Return {(gt_id, frame): pred_id or None}."""
    out = {}
    for frame, g_rows in gt.items():
        p_rows = pred.get(frame, [])
        for g in g_rows:
            out[(g[0], frame)] = None
        if not p_rows:
            continue
        m = iou_matrix([g[1:] for g in g_rows], [p[1:] for p in p_rows])
        r, c = linear_sum_assignment(-m)
        for i, j in zip(r, c):
            if m[i, j] >= IOU_THR:
                out[(g_rows[i][0], frame)] = p_rows[j][0]
    return out


def gt_stats(matches, gid, frames, edge=10):
    """coverage, keep ratio of the start ID, and whether the ID at the end differs."""
    seq = [matches.get((gid, f)) for f in frames]
    coverage = sum(s is not None for s in seq) / len(seq)

    def dominant(part):
        ids = [s for s in part if s is not None]
        return max(set(ids), key=ids.count) if ids else None

    start_id, end_id = dominant(seq[:edge]), dominant(seq[-edge:])
    keep = sum(s == start_id for s in seq) / len(seq) if start_id is not None else 0.0
    transfer = int(start_id is None or end_id != start_id)
    return coverage, keep, transfer


HOTA_CSV = {
    "sam2": ROOT / "TrackEval/data/trackers/dancetrack/val/my_sam2_model/pedestrian_detailed.csv",
    "samurai": ROOT / "TrackEval/data/trackers/dancetrack/val/my_samurai_model/pedestrian_detailed.csv",
    "ours": ROOT / "2025_09_aburatani_Mamba_Trackers/artifacts/sam2_minimal_integration/trackeval"
    "/sam2_stateful_minimal_20260723T_sam2_minimal_25seq_epoch100_seqinfo"
    "/sam2_stateful_minimal_20260723T_sam2_minimal_25seq_epoch100/pedestrian_detailed.csv",
}


def load_hota():
    hota = {}
    for method, path in HOTA_CSV.items():
        with open(path) as f:
            for row in csv.DictReader(f):
                hota[(row["seq"], method)] = float(row["HOTA___AUC"])
    return hota


def main():
    hota = load_hota()
    seq_rows, win_rows, gid_rows = [], [], []
    for seq_dir in sorted(GT_DIR.glob("dancetrack*")):
        seq = seq_dir.name
        gt = read_mot(seq_dir / "gt/gt.txt")
        preds = {m: read_mot(p / f"{seq}.txt") for m, p in METHODS.items()}
        matches = {m: match_sequence(gt, preds[m]) for m in METHODS}
        frames_by_gid = defaultdict(set)
        for f, rows in gt.items():
            for r in rows:
                frames_by_gid[r[0]].add(f)
        n_frames = max(gt)
        seq_rows.append({"seq": seq, "n_ids": len(frames_by_gid), "n_frames": n_frames,
                         **{f"hota_{m}": round(hota[(seq, m)], 3) for m in METHODS}})
        for start in range(1, n_frames - WINDOW + 2, STRIDE):
            frames = range(start, start + WINDOW)
            gids = [g for g, fs in frames_by_gid.items() if all(f in fs for f in frames)]
            if not gids:
                continue
            row = {"seq": seq, "start": start, "end": start + WINDOW - 1, "n_ids_in_window": len(gids)}
            per_gid = {g: {"seq": seq, "start": start, "end": start + WINDOW - 1, "gt_id": g} for g in gids}
            for m in METHODS:
                stats = {g: gt_stats(matches[m], g, frames) for g in gids}
                row[f"cov_{m}"] = round(float(np.mean([s[0] for s in stats.values()])), 3)
                row[f"keep_{m}"] = round(float(np.mean([s[1] for s in stats.values()])), 3)
                row[f"transfer_{m}"] = int(sum(s[2] for s in stats.values()))
                for g, (cov, keep, transfer) in stats.items():
                    per_gid[g][f"cov_{m}"] = round(cov, 3)
                    per_gid[g][f"keep_{m}"] = round(keep, 3)
                    per_gid[g][f"transfer_{m}"] = transfer
            gid_rows.extend(per_gid.values())
            win_rows.append(row)
        print(seq, len(frames_by_gid), "ids")
    for name, rows in [("sequences", seq_rows), ("windows", win_rows), ("gt-windows", gid_rows)]:
        with open(OUT_DIR / f"candidates-{name}.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)


if __name__ == "__main__":
    main()
