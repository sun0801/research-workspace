#!/usr/bin/env python3
"""Render per-method qualitative videos: cropped views (main slides) and full frames with GT (supplement).

Every target is initialised with its GT bbox prompt, so tracker IDs start equal
to GT IDs and one color per ID is shared by all panels. After a tracker drifts,
the number on a person can differ between methods. An ID switch appears as a
change of box color and label on the same person.

Cropped videos show the region covered by the focal GT ID (local patterns) or by all
GT boxes (other patterns) over the window.
"""

import csv
import subprocess
from collections import defaultdict
from pathlib import Path

import cv2
import numpy as np

ROOT = Path("/mnt/HDD10TB-2/aburatani")
GT_DIR = ROOT / "TrackEval/data/gt/dancetrack/val"
IMG_DIR = ROOT / "dataset/DanceTrack/val/val"
METHODS = {  # 定量表（HOTA 51.3 / 54.1 / 55.5）と同じ出力
    "SAM2": ROOT / "TrackEval/data/trackers/dancetrack/val/my_sam2_model/data",
    "SAMURAI": ROOT / "TrackEval/data/trackers/dancetrack/val/my_samurai_model/data",
    "Ours": ROOT / "2025_03_aburatani_sam2/results/sam2_stateful_minimal/20260723T_sam2_minimal_25seq/samurai_mamba_stateful_tiny",
}
OUT_DIR = Path(__file__).parent
FPS = 10
MARGIN = 10  # frames before/after the selected window

# (case id, pattern, seq, first, last, focal GT ID or None)
CASES = [
    ("p0-representative", "代表例", "dancetrack0004", 141, 240, None),
    ("p1a", "①少人数・成功", "dancetrack0097", 761, 820, None),
    ("p1b", "①少人数・成功", "dancetrack0010", 781, 840, None),
    ("p2a", "②多人数・失敗", "dancetrack0081", 871, 930, None),
    ("p2b", "②多人数・失敗", "dancetrack0079", 531, 590, None),
    ("p3a", "③局所・成功", "dancetrack0025", 81, 140, 3),
    ("p3b", "③局所・成功", "dancetrack0034", 621, 680, 7),
    ("p4a", "④局所・失敗", "dancetrack0090", 241, 300, 8),
    ("p4b", "④局所・失敗", "dancetrack0034", 41, 100, 10),
]

PALETTE = [  # BGR, distinguishable on dark stage backgrounds
    (75, 25, 230), (75, 180, 60), (25, 225, 255), (200, 130, 0), (48, 130, 245),
    (180, 30, 145), (240, 240, 70), (230, 50, 240), (60, 245, 210), (212, 190, 250),
    (128, 128, 0), (255, 190, 220), (40, 110, 170), (200, 250, 255), (0, 0, 128),
    (195, 255, 170), (0, 128, 128), (180, 215, 255), (128, 0, 0), (128, 128, 255),
]


def color(track_id):
    return PALETTE[track_id % len(PALETTE)]


def read_mot(path):
    rows = defaultdict(list)
    with open(path, newline="") as stream:
        for row in csv.reader(stream):
            if row:
                rows[int(float(row[0]))].append((int(float(row[1])), *map(float, row[2:6])))
    return rows


def draw_boxes(img, rows, scale, thickness):
    font = cv2.FONT_HERSHEY_SIMPLEX
    for track_id, x, y, w, h in rows:
        c = color(track_id)
        p1, p2 = (round(x), round(y)), (round(x + w), round(y + h))
        cv2.rectangle(img, p1, p2, c, thickness, cv2.LINE_AA)
        label = str(track_id)
        (tw, th), base = cv2.getTextSize(label, font, scale, 2)
        top = max(0, p1[1] - th - base - 6)
        cv2.rectangle(img, (p1[0], top), (p1[0] + tw + 8, top + th + base + 6), c, -1)
        cv2.putText(img, label, (p1[0] + 4, top + th + 2), font, scale, (0, 0, 0), 2, cv2.LINE_AA)


def draw_focal(img, box):
    """白い破線枠で注目する人物（GT）を示す。"""
    x, y, w, h = box
    x1, y1, x2, y2 = round(x) - 8, round(y) - 8, round(x + w) + 8, round(y + h) + 8
    for (a, b) in [((x1, y1), (x2, y1)), ((x2, y1), (x2, y2)), ((x2, y2), (x1, y2)), ((x1, y2), (x1, y1))]:
        length = int(np.hypot(b[0] - a[0], b[1] - a[1]))
        for s in range(0, length, 28):
            t0, t1 = s / length, min(s + 16, length) / length
            p = (round(a[0] + (b[0] - a[0]) * t0), round(a[1] + (b[1] - a[1]) * t0))
            q = (round(a[0] + (b[0] - a[0]) * t1), round(a[1] + (b[1] - a[1]) * t1))
            cv2.line(img, p, q, (255, 255, 255), 4, cv2.LINE_AA)


def crop_region(gt, focal, first, last, width, height):
    boxes = [r[1:] for f in range(first, last + 1) for r in gt.get(f, []) if focal is None or r[0] == focal]
    xs1 = min(b[0] for b in boxes); ys1 = min(b[1] for b in boxes)
    xs2 = max(b[0] + b[2] for b in boxes); ys2 = max(b[1] + b[3] for b in boxes)
    cx, cy = (xs1 + xs2) / 2, (ys1 + ys2) / 2
    h = max((ys2 - ys1) * 1.25, (xs2 - xs1) * 1.25 * 9 / 16, 540)
    h = min(h, height)
    w = h * 16 / 9
    x0 = int(np.clip(cx - w / 2, 0, width - w)); y0 = int(np.clip(cy - h / 2, 0, height - h))
    return x0, y0, int(w), int(h)


def frame_label(img, frame):
    cv2.putText(img, f"frame {frame}", (12, img.shape[0] - 14), cv2.FONT_HERSHEY_SIMPLEX,
                0.8, (255, 255, 255), 2, cv2.LINE_AA)


class Writer:
    def __init__(self, path, w, h):
        self.proc = subprocess.Popen(
            ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24",
             "-s", f"{w}x{h}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p",
             "-crf", "20", "-preset", "medium", "-movflags", "+faststart", str(path)],
            stdin=subprocess.PIPE)
        self.size = (w, h)

    def write(self, img):
        assert (img.shape[1], img.shape[0]) == self.size, (img.shape, self.size)
        self.proc.stdin.write(img.tobytes())

    def close(self):
        self.proc.stdin.close()
        if self.proc.wait() != 0:
            raise RuntimeError("ffmpeg failed")


def render(case):
    """Write one video per method so each can be placed freely on a slide.

    *-{method}-crop.mp4: cropped view for the main slides (SAM2 / SAMURAI / Ours)
    *-{method}-full.mp4: full frame for the supplement (GT / SAM2 / SAMURAI / Ours)
    """
    cid, _, seq, first, last, focal = case
    gt = read_mot(GT_DIR / seq / "gt/gt.txt")
    preds = {m: read_mot(p / f"{seq}.txt") for m, p in METHODS.items()}
    n_frames = max(gt)
    f0, f1 = max(1, first - MARGIN), min(n_frames, last + MARGIN)
    sample = cv2.imread(str(IMG_DIR / seq / "img1" / f"{f0:08d}.jpg"))
    H, W = sample.shape[:2]
    crop = crop_region(gt, focal, first, last, W, H)
    stem = f"2026-10-12-{cid}-{seq}-{first}-{last}"
    sources = [("GT", gt)] + list(preds.items())
    writers, posters = {}, {}
    for name, _ in sources:
        key = name.lower()
        writers[(key, "full")] = Writer(OUT_DIR / f"{stem}-{key}-full.mp4", 1280, 720)
        if name != "GT":
            writers[(key, "crop")] = Writer(OUT_DIR / f"{stem}-{key}-crop.mp4", 960, 540)
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
            if name != "GT":
                x, y, w, h = crop
                view = cv2.resize(canvas[y:y + h, x:x + w], (960, 540), interpolation=cv2.INTER_AREA)
                frame_label(view, f)
                frames["crop"] = view
            for kind, frame in frames.items():
                writers[(key, kind)].write(frame)
                if f == (first + last) // 2:
                    posters[(key, kind)] = frame.copy()
    for (key, kind), writer in writers.items():
        writer.close()
        cv2.imwrite(str(OUT_DIR / f"{stem}-{key}-{kind}-poster.jpg"), posters[(key, kind)],
                    [cv2.IMWRITE_JPEG_QUALITY, 88])
    print(cid, seq, f0, f1, crop)


if __name__ == "__main__":
    import sys
    wanted = set(sys.argv[1:])
    for case in CASES:
        if not wanted or case[0] in wanted:
            render(case)
