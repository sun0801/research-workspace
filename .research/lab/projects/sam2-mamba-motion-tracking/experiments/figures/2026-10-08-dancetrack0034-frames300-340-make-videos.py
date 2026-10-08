#!/usr/bin/env python3
"""Render one header-free DanceTrack qualitative video per tracking method."""

import csv
from pathlib import Path

import cv2


ROOT = Path("/mnt/HDD10TB-2/aburatani")
SEQ = "dancetrack0034"
FIRST_FRAME = 300
LAST_FRAME = 340
FPS = 10
PRED_COLOR = (255, 180, 0)  # cyan in RGB; shared by all methods
GT_PATH = ROOT / "TrackEval/data/gt/dancetrack/val" / SEQ / "gt/gt.txt"
IMAGE_DIR = ROOT / "dataset/DanceTrack/val/val" / SEQ / "img1"
OUT_DIR = Path(__file__).parent

METHODS = {
    "sam2": {
        "label": "SAM2",
        "path": ROOT / "2025_03_aburatani_sam2/results/sam2/sam2_tiny" / f"{SEQ}.txt",
    },
    "samurai": {
        "label": "SAMURAI",
        "path": ROOT / "2025_03_aburatani_sam2/results/samurai/samurai_tiny" / f"{SEQ}.txt",
    },
    "mamba-state": {
        "label": "Mamba-state",
        "path": ROOT
        / "2025_03_aburatani_sam2/results/sam2_stateful_minimal/20260723T_sam2_minimal_25seq/samurai_mamba_stateful_tiny"
        / f"{SEQ}.txt",
    },
}


def read_mot(path: Path):
    rows = {}
    with path.open(newline="") as stream:
        for row in csv.reader(stream):
            if not row:
                continue
            frame, track_id = int(float(row[0])), int(float(row[1]))
            x, y, width, height = map(float, row[2:6])
            rows.setdefault(frame, []).append((track_id, x, y, width, height))
    return rows


def iou(a, b):
    ax1, ay1, aw, ah = a
    bx1, by1, bw, bh = b
    left, top = max(ax1, bx1), max(ay1, by1)
    right, bottom = min(ax1 + aw, bx1 + bw), min(ay1 + ah, by1 + bh)
    intersection = max(0.0, right - left) * max(0.0, bottom - top)
    union = aw * ah + bw * bh - intersection
    return intersection / union if union > 0 else 0.0


def draw_box(frame, box, color, label=None):
    x, y, width, height = box
    p1 = (round(x), round(y))
    p2 = (round(x + width), round(y + height))
    cv2.rectangle(frame, p1, p2, color, 3, cv2.LINE_AA)
    if label is not None:
        font = cv2.FONT_HERSHEY_SIMPLEX
        scale, thickness = 0.75, 2
        (text_w, text_h), baseline = cv2.getTextSize(label, font, scale, thickness)
        top = max(0, p1[1] - text_h - baseline - 7)
        cv2.rectangle(frame, (p1[0], top), (p1[0] + text_w + 8, top + text_h + baseline + 6), color, -1)
        cv2.putText(frame, label, (p1[0] + 4, top + text_h + 1), font, scale, (0, 0, 0), thickness, cv2.LINE_AA)


def main():
    gt_rows = read_mot(GT_PATH)
    method_rows = {name: read_mot(spec["path"]) for name, spec in METHODS.items()}

    gt_by_frame = {}
    for frame_id, rows in gt_rows.items():
        for track_id, x, y, width, height in rows:
            if track_id == 9:
                gt_by_frame[frame_id] = (x, y, width, height)

    expected = set(range(FIRST_FRAME, LAST_FRAME + 1))
    if not expected.issubset(gt_by_frame):
        missing = sorted(expected - set(gt_by_frame))
        raise RuntimeError(f"GT ID 9 is missing frames: {missing}")

    first_image = cv2.imread(str(IMAGE_DIR / f"{FIRST_FRAME:08d}.jpg"))
    if first_image is None:
        raise FileNotFoundError(IMAGE_DIR / f"{FIRST_FRAME:08d}.jpg")
    height, width = first_image.shape[:2]

    for method, spec in METHODS.items():
        output = OUT_DIR / f"2026-10-08-{SEQ}-frames{FIRST_FRAME}-{LAST_FRAME}-{method}.mp4"
        writer = cv2.VideoWriter(
            str(output), cv2.VideoWriter_fourcc(*"mp4v"), FPS, (width, height)
        )
        if not writer.isOpened():
            raise RuntimeError(f"Could not open video writer: {output}")

        for frame_id in range(FIRST_FRAME, LAST_FRAME + 1):
            image_path = IMAGE_DIR / f"{frame_id:08d}.jpg"
            frame = cv2.imread(str(image_path))
            if frame is None:
                writer.release()
                raise FileNotFoundError(image_path)

            gt_box = gt_by_frame[frame_id]
            candidates = method_rows[method].get(frame_id, [])
            if candidates:
                _, x, y, box_w, box_h = max(
                    candidates, key=lambda row: iou(gt_box, row[1:])
                )
                draw_box(frame, (x, y, box_w, box_h), PRED_COLOR, "ID 9")
            draw_box(frame, gt_box, (0, 255, 0))
            writer.write(frame)

        writer.release()
        print(f"{spec['label']}: {output}")


if __name__ == "__main__":
    main()
