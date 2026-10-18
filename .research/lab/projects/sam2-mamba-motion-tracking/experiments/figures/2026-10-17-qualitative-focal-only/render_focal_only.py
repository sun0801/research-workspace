#!/usr/bin/env python3
"""Qualitative videos for the local patterns, drawing only the focal person (2026-10-17).

For each method (SAM2 / SAMURAI / Ours), only the boxes related to the focal person are drawn:
- the focal GT person (white dashed box),
- the "target track": the track that matched the focal GT person most often (IoU >= 0.5)
  in the first 10 frames of the window, wherever it goes (if it drifts or breaks, that is visible), and
- any other track that overlaps the focal GT person in that frame (IoU >= 0.5), so that several IDs
  taking turns on one person are visible. Other people's boxes are not drawn.
Same tracker outputs, colors and crop as ../2026-10-12-qualitative-patterns/render_videos.py
(10 fps = half speed). No new inference.

usage: render_focal_only.py [case ids]
"""

import sys
from collections import Counter
from pathlib import Path

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "2026-10-12-qualitative-patterns"))
from render_videos import (GT_DIR, IMG_DIR, METHODS, Writer, crop_region, draw_boxes,  # noqa: E402
                           draw_focal, frame_label, read_mot)

OUT_DIR = Path(__file__).parent
MARGIN = 10
# (case id, seq, first, last, focal GT ID) — 窓は 1回目の p3a と 2回目の oursfail と同じ
CASES = [
    ("localok", "dancetrack0025", 81, 140, 3),
    ("localfail", "dancetrack0079", 822, 881, 8),
]


def iou(a, b):
    ax, ay, aw, ah = a; bx, by, bw, bh = b
    ix = max(0.0, min(ax + aw, bx + bw) - max(ax, bx)); iy = max(0.0, min(ay + ah, by + bh) - max(ay, by))
    inter = ix * iy
    return inter / (aw * ah + bw * bh - inter + 1e-9)


def target_track(gt, pred, focal, first):
    votes = Counter()
    for f in range(first, first + 10):
        g = next((r[1:] for r in gt.get(f, []) if r[0] == focal), None)
        if g is None:
            continue
        best = max(((iou(g, r[1:]), r[0]) for r in pred.get(f, [])), default=(0, None))
        if best[0] >= 0.5:
            votes[best[1]] += 1
    return votes.most_common(1)[0][0]


def render(case):
    cid, seq, first, last, focal = case
    gt = read_mot(GT_DIR / seq / "gt/gt.txt")
    preds = {m: read_mot(p / f"{seq}.txt") for m, p in METHODS.items()}
    f0, f1 = max(1, first - MARGIN), min(max(gt), last + MARGIN)
    H, W = cv2.imread(str(IMG_DIR / seq / "img1" / f"{f0:08d}.jpg")).shape[:2]
    x, y, w, h = crop_region(gt, focal, first, last, W, H)
    stem = f"2026-10-17-{cid}-{seq}-{f0}-{f1}-gt{focal}"
    tracks = {m: target_track(gt, pred, focal, first) for m, pred in preds.items()}
    writers = {m: Writer(OUT_DIR / f"{stem}-{m.lower()}-focal.mp4", 960, 540) for m in preds}
    posters = {}
    for f in range(f0, f1 + 1):
        img = cv2.imread(str(IMG_DIR / seq / "img1" / f"{f:08d}.jpg"))
        focal_box = next((r[1:] for r in gt.get(f, []) if r[0] == focal), None)
        for m, pred in preds.items():
            canvas = img.copy()
            if focal_box is not None:
                draw_focal(canvas, focal_box)
            rows = [r for r in pred.get(f, []) if r[0] == tracks[m]
                    or (focal_box is not None and iou(focal_box, r[1:]) >= 0.5)]
            draw_boxes(canvas, rows, 1.1, 4)
            view = cv2.resize(canvas[y:y + h, x:x + w], (960, 540), interpolation=cv2.INTER_AREA)
            frame_label(view, f)
            writers[m].write(view)
            if f == (first + last) // 2:
                posters[m] = view.copy()
    for m, wr in writers.items():
        wr.close()
        cv2.imwrite(str(OUT_DIR / f"{stem}-{m.lower()}-focal-poster.jpg"), posters[m], [cv2.IMWRITE_JPEG_QUALITY, 88])
    print(cid, seq, f0, f1, "crop", (x, y, w, h), "target tracks", tracks)


if __name__ == "__main__":
    wanted = set(sys.argv[1:])
    for case in CASES:
        if not wanted or case[0] in wanted:
            render(case)
