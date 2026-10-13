#!/usr/bin/env python3
"""DanceTrack 0052 clips for the midterm slides (20 fps, H.264).

- mot-task-gt: GT boxes with IDs for the MOT task slide (frames 125-205).
  GT IDs 0-3 are shown as ID 1-4.
- dataset-raw: frames without boxes for the dataset slide (frames 700-860).
- whole-gt / whole-raw: all 1203 frames, full frame, for comparison with the clips.
"""

import csv
import subprocess
from collections import defaultdict
from pathlib import Path

import cv2

SEQ_DIR = Path("/mnt/HDD10TB-2/aburatani/dataset/DanceTrack/train2/train2/dancetrack0052")
OUT_DIR = Path(__file__).parent
FPS = 20  # seqinfo.ini frameRate

COLORS = {0: (60, 60, 230), 1: (220, 140, 30), 2: (70, 180, 60), 3: (180, 60, 170)}  # BGR


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


def draw(img, rows):
    font = cv2.FONT_HERSHEY_SIMPLEX
    for tid, x, y, w, h in rows:
        c = COLORS[tid]
        p1, p2 = (round(x), round(y)), (round(x + w), round(y + h))
        cv2.rectangle(img, p1, p2, c, 7, cv2.LINE_AA)
        label = f"ID {tid + 1}"
        (tw, th), base = cv2.getTextSize(label, font, 1.6, 4)
        top = max(0, p1[1])  # 枠の内側上端に置く（画面上端で切れないように）
        cv2.rectangle(img, (p1[0], top), (p1[0] + tw + 16, top + th + base + 14), c, -1)
        cv2.putText(img, label, (p1[0] + 8, top + th + 7), font, 1.6, (255, 255, 255), 4, cv2.LINE_AA)


def render(name, first, last, crop, size, with_gt):
    gt = read_gt()
    x0, y0, cw, ch = crop
    proc = writer(OUT_DIR / f"2026-10-13-dancetrack0052-{name}.mp4", *size)
    poster = None
    for f in range(first, last + 1):
        img = cv2.imread(str(SEQ_DIR / "img1" / f"{f:08d}.jpg"))
        if with_gt:
            draw(img, gt.get(f, []))
        view = cv2.resize(img[y0:y0 + ch, x0:x0 + cw], size, interpolation=cv2.INTER_AREA)
        proc.stdin.write(view.tobytes())
        if f == first:
            poster = view
    proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError("ffmpeg failed")
    cv2.imwrite(str(OUT_DIR / f"2026-10-13-dancetrack0052-{name}-poster.jpg"), poster,
                [cv2.IMWRITE_JPEG_QUALITY, 90])
    print(name, first, last, crop, size)


if __name__ == "__main__":
    # GT extent in frames 125-205 is x 287-1741, so crop 1566x1080 (aspect 1.45) around it.
    render("mot-task-gt", 125, 205, (231, 0, 1566, 1080), (1160, 800), True)
    render("dataset-raw", 700, 860, (0, 0, 1920, 1080), (1280, 720), False)
    render("whole-gt", 1, 1203, (0, 0, 1920, 1080), (1280, 720), True)
    render("whole-raw", 1, 1203, (0, 0, 1920, 1080), (1280, 720), False)
