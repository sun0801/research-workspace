#!/usr/bin/env python3
"""Qualitative videos for the midterm slides, second round (2026-10-17).

Reuses the drawing helpers of ../2026-10-12-qualitative-patterns/render_videos.py
(same tracker outputs as the quantitative table, same colors per ID, 10 fps = half speed).

- all-fail: a whole sequence, full frame, one video each for GT / SAM2 / SAMURAI / Ours.
- ours-only-fail: a cropped window around one GT person (white dashed box),
  one video each for GT / SAM2 / SAMURAI / Ours, plus full-frame versions.
"""

import sys
from pathlib import Path

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "2026-10-12-qualitative-patterns"))
from render_videos import (GT_DIR, IMG_DIR, METHODS, Writer, crop_region, draw_boxes,  # noqa: E402
                           draw_focal, frame_label, read_mot)

OUT_DIR = Path(__file__).parent

# (case id, seq, first, last, focal GT ID or None, crop?)
CASES = [
    ("allfail", "dancetrack0026", 1, 302, None, False),
    ("oursfail", "dancetrack0079", 822, 881, 8, True),
]
MARGIN = 10  # frames before/after a window (not used for whole sequences)


def render(case):
    cid, seq, first, last, focal, with_crop = case
    gt = read_mot(GT_DIR / seq / "gt/gt.txt")
    preds = {m: read_mot(p / f"{seq}.txt") for m, p in METHODS.items()}
    n_frames = max(gt)
    whole = first == 1 and last == n_frames
    f0, f1 = (first, last) if whole else (max(1, first - MARGIN), min(n_frames, last + MARGIN))
    sample = cv2.imread(str(IMG_DIR / seq / "img1" / f"{f0:08d}.jpg"))
    H, W = sample.shape[:2]
    crop = crop_region(gt, focal, first, last, W, H) if with_crop else None
    stem = f"2026-10-17-{cid}-{seq}-{f0}-{f1}"
    sources = [("GT", gt)] + list(preds.items())
    writers, posters = {}, {}
    for name, _ in sources:
        key = name.lower()
        writers[(key, "full")] = Writer(OUT_DIR / f"{stem}-{key}-full.mp4", 1280, 720)
        if crop:
            writers[(key, "crop")] = Writer(OUT_DIR / f"{stem}-{key}-crop.mp4", 960, 540)
    poster_frame = (first + last) // 2
    for f in range(f0, f1 + 1):
        img = cv2.imread(str(IMG_DIR / seq / "img1" / f"{f:08d}.jpg"))
        focal_box = next((r[1:] for r in gt.get(f, []) if r[0] == focal), None)
        for name, rows in sources:
            key = name.lower()
            canvas = img.copy()
            if focal_box is not None:
                draw_focal(canvas, focal_box)
            draw_boxes(canvas, rows.get(f, []), 1.1, 4)
            full = cv2.resize(canvas, (1280, 720), interpolation=cv2.INTER_AREA)
            frame_label(full, f)
            frames = {"full": full}
            if crop:
                x, y, w, h = crop
                view = cv2.resize(canvas[y:y + h, x:x + w], (960, 540), interpolation=cv2.INTER_AREA)
                frame_label(view, f)
                frames["crop"] = view
            for kind, frame in frames.items():
                writers[(key, kind)].write(frame)
                if f == poster_frame:
                    posters[(key, kind)] = frame.copy()
    for (key, kind), writer in writers.items():
        writer.close()
        cv2.imwrite(str(OUT_DIR / f"{stem}-{key}-{kind}-poster.jpg"), posters[(key, kind)],
                    [cv2.IMWRITE_JPEG_QUALITY, 88])
    print(cid, seq, f0, f1, crop)


if __name__ == "__main__":
    wanted = set(sys.argv[1:])
    for case in CASES:
        if not wanted or case[0] in wanted:
            render(case)
