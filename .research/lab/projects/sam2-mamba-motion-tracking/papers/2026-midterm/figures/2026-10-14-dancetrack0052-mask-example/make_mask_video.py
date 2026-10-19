#!/usr/bin/env python3
"""DanceTrack 0052 mask example for the midterm background slide (20 fps, H.264).

DanceTrack has no mask annotation, so each frame's GT boxes are given to the SAM2.1
image predictor (hiera_large) as box prompts, frame by frame. The masks are therefore
SAM2 pseudo masks, not GT. Colors match ../2026-10-13-dancetrack0052-mot-example; ID labels
are drawn only with --labels (the slide version has none).

Run with the SAM2 repo venv:
  /mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2/.venv-sam2/bin/python make_mask_video.py [--frames N]
"""

import argparse
import csv
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

import cv2
import numpy as np
import torch

SAM2_REPO = Path("/mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2")
sys.path.insert(0, str(SAM2_REPO))
from sam2.build_sam import build_sam2  # noqa: E402
from sam2.sam2_image_predictor import SAM2ImagePredictor  # noqa: E402

SEQ_DIR = Path("/mnt/HDD10TB-2/aburatani/dataset/DanceTrack/train2/train2/dancetrack0052")
OUT_DIR = Path(__file__).parent
FPS = 20  # seqinfo.ini frameRate
SIZE = (1280, 720)
ALPHA = 0.55
MIN_LABEL_AREA = 15000  # px at 1920x1080
MIN_PART_AREA = 3000  # px at 1920x1080

COLORS = {0: (60, 60, 230), 1: (220, 140, 30), 2: (70, 180, 60), 3: (180, 60, 170)}  # BGR, same as GT video


def read_gt():
    rows = defaultdict(list)
    with open(SEQ_DIR / "gt/gt.txt", newline="") as stream:
        for row in csv.reader(stream):
            rows[int(row[0])].append((int(row[1]), *map(float, row[2:6])))
    return rows


def writer(path, w, h):
    return subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{w}x{h}",
         "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
         "-preset", "medium", "-movflags", "+faststart", str(path)],
        stdin=subprocess.PIPE)


def box_fit(mask, box):
    """IoU between the mask's bounding box and its prompt box."""
    ys, xs = np.nonzero(mask)
    if len(xs) == 0:
        return 0.0
    mx1, my1, mx2, my2 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
    bx1, by1, bx2, by2 = box
    iw = max(0.0, min(mx2, bx2) - max(mx1, bx1))
    ih = max(0.0, min(my2, by2) - max(my1, by1))
    inter = iw * ih
    return inter / ((mx2 - mx1) * (my2 - my1) + (bx2 - bx1) * (by2 - by1) - inter)


def resolve_overlaps(masks, boxes):
    """Give overlapping pixels to the mask that fits its own box better.

    A box prompt for a person hidden behind another often returns the front person's mask
    (e.g. frame 778, ID 3 behind ID 2). The front person's mask fits its own box better,
    so it keeps the pixels and the hidden person keeps only what is left.
    """
    order = sorted(range(len(masks)), key=lambda i: box_fit(masks[i], boxes[i]), reverse=True)
    taken = np.zeros_like(masks[0])
    out = [None] * len(masks)
    for i in order:
        out[i] = drop_small_parts(masks[i] & ~taken)
        taken |= out[i]
    return out


def drop_small_parts(mask):
    """Remove leftover fragments (edge slivers of a hidden person's mask)."""
    n, labels, stats, _ = cv2.connectedComponentsWithStats(mask.astype(np.uint8), connectivity=8)
    keep = [k for k in range(1, n) if stats[k, cv2.CC_STAT_AREA] >= MIN_PART_AREA]
    return np.isin(labels, keep)


def draw(img, rows, masks, labels):
    overlay = img.copy()
    for (tid, *_), m in zip(rows, masks):
        overlay[m] = COLORS[tid]
    out = cv2.addWeighted(overlay, ALPHA, img, 1 - ALPHA, 0)
    font = cv2.FONT_HERSHEY_SIMPLEX
    for (tid, *_), m in zip(rows, masks):
        c = COLORS[tid]
        contours, _ = cv2.findContours(m.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        cv2.drawContours(out, contours, -1, c, 4, cv2.LINE_AA)
        if not labels:
            continue
        ys, xs = np.nonzero(m)
        if len(xs) < MIN_LABEL_AREA:  # ほぼ隠れている人物にはラベルを付けない
            continue
        label = f"ID {tid + 1}"
        (tw, th), base = cv2.getTextSize(label, font, 1.6, 4)
        x0, y0 = int(xs.min()), int(ys.min())  # マスク上端の左寄りに置く
        cv2.rectangle(out, (x0, y0), (x0 + tw + 16, y0 + th + base + 14), c, -1)
        cv2.putText(out, label, (x0 + 8, y0 + th + 7), font, 1.6, (255, 255, 255), 4, cv2.LINE_AA)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frames", type=int, default=None, help="first N frames only (for checking)")
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--labels", action="store_true", help="draw ID labels on the masks")
    args = ap.parse_args()

    model = build_sam2("configs/sam2.1/sam2.1_hiera_l.yaml",
                       str(SAM2_REPO / "checkpoints/sam2.1_hiera_large.pt"), device=args.device)
    predictor = SAM2ImagePredictor(model)
    gt = read_gt()
    last = args.frames or max(gt)
    name = "whole-mask" if args.frames is None else f"check{last}-mask"
    proc = writer(OUT_DIR / f"2026-10-14-dancetrack0052-{name}.mp4", *SIZE)
    poster = None
    trimmed = []  # (frame, ID, removed fraction) where overlap removal cut >20% of a mask
    with torch.inference_mode(), torch.autocast(args.device, dtype=torch.bfloat16, enabled=args.device == "cuda"):
        for f in range(1, last + 1):
            img = cv2.imread(str(SEQ_DIR / "img1" / f"{f:08d}.jpg"))
            rows = gt.get(f, [])
            masks = []
            if rows:
                predictor.set_image(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
                boxes = np.array([[x, y, x + w, y + h] for _, x, y, w, h in rows], dtype=np.float32)
                m, _, _ = predictor.predict(box=boxes, multimask_output=False)
                raw = list(m.reshape(len(rows), *img.shape[:2]) > 0)
                masks = resolve_overlaps(raw, boxes)
                for (tid, *_), a, b in zip(rows, raw, masks):
                    if a.sum() and b.sum() < 0.8 * a.sum():
                        trimmed.append((f, tid + 1, round(1 - b.sum() / a.sum(), 2)))
            view = cv2.resize(draw(img, rows, masks, args.labels), SIZE, interpolation=cv2.INTER_AREA)
            proc.stdin.write(view.tobytes())
            if f == 1:
                poster = view
            if f % 100 == 0:
                print(f, flush=True)
    proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError("ffmpeg failed")
    cv2.imwrite(str(OUT_DIR / f"2026-10-14-dancetrack0052-{name}-poster.jpg"), poster,
                [cv2.IMWRITE_JPEG_QUALITY, 90])
    print(name, last)
    print(f"masks cut >20% by overlap removal: {len(trimmed)} (frames {len({t[0] for t in trimmed})})")
    for t in trimmed:
        print(*t)


if __name__ == "__main__":
    main()
