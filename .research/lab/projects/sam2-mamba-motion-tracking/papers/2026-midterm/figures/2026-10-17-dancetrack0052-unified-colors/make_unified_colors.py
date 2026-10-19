#!/usr/bin/env python3
"""Re-render the dancetrack0052 figures of slides 2 and 3 with the ID colors of the later figures.

The SAMURAI / proposed-method figures (../2026-10-15-samurai-per-id/masks_all.png) color the four
people, left to right in frame 1, purple (ID 1), green (ID 2), red (ID 3), yellow (ID 4).
The older figures used red / blue / green / purple keyed by the raw GT ID, so the leftmost person was
"ID 2" in blue. Here the raw GT IDs are mapped to the later figures' IDs and colors:

    raw GT 1 (leftmost) -> ID 1 purple, raw 0 -> ID 2 green, raw 2 -> ID 3 red, raw 3 -> ID 4 yellow

Outputs (this folder):
  2026-10-17-dancetrack0052-whole-gt.mp4 (+poster)   slide 2 upper video (GT boxes with ID labels)
  2026-10-17-dancetrack0052-whole-mask.mp4 (+poster) slide 2 lower video (SAM2 pseudo masks, no labels)
  2026-10-17-trk_{0,1,2}.png                          slide 3 "ID付き" thumbnails (frames 7 / 15 / 23)

Run with the SAM2 repo venv (the mask video needs SAM2 and a GPU, about 8 min on an RTX A4000):
  .venv-sam2/bin/python make_unified_colors.py [gt] [mask] [trk]
"""

import shutil
import sys
from pathlib import Path

import cv2

HERE = Path(__file__).resolve().parent
FIG = HERE.parent
COLORS = {1: (225, 48, 101), 0: (44, 184, 22), 2: (99, 76, 226), 3: (8, 179, 216)}  # BGR, raw GT ID -> later figures' color
LABEL = {1: 1, 0: 2, 2: 3, 3: 4}  # raw GT ID -> displayed ID


def gt_video():
    sys.path.insert(0, str(FIG / "2026-10-13-dancetrack0052-mot-example"))
    import make_videos as mv

    def draw(img, rows):
        font = cv2.FONT_HERSHEY_SIMPLEX
        for tid, x, y, w, h in rows:
            c = COLORS[tid]
            p1, p2 = (round(x), round(y)), (round(x + w), round(y + h))
            cv2.rectangle(img, p1, p2, c, 7, cv2.LINE_AA)
            label = f"ID {LABEL[tid]}"
            (tw, th), base = cv2.getTextSize(label, font, 1.6, 4)
            top = max(0, p1[1])
            cv2.rectangle(img, (p1[0], top), (p1[0] + tw + 16, top + th + base + 14), c, -1)
            cv2.putText(img, label, (p1[0] + 8, top + th + 7), font, 1.6, (255, 255, 255), 4, cv2.LINE_AA)

    mv.draw, mv.OUT_DIR = draw, HERE
    mv.render("whole-gt", 1, 1203, (0, 0, 1920, 1080), (1280, 720), True)
    for suffix in (".mp4", "-poster.jpg"):
        (HERE / f"2026-10-13-dancetrack0052-whole-gt{suffix}").rename(HERE / f"2026-10-17-dancetrack0052-whole-gt{suffix}")


def mask_video():
    sys.path.insert(0, str(FIG / "2026-10-14-dancetrack0052-mask-example"))
    import make_mask_video as mm
    mm.COLORS, mm.OUT_DIR = COLORS, HERE
    sys.argv = [sys.argv[0]]
    mm.main()
    for suffix in (".mp4", "-poster.jpg"):
        (HERE / f"2026-10-14-dancetrack0052-whole-mask{suffix}").rename(HERE / f"2026-10-17-dancetrack0052-whole-mask{suffix}")


def trk_thumbnails():
    sys.path.insert(0, str(FIG / "2026-10-15-mot-paradigm-timeline"))
    import make_thumbnails as mt
    tmp = HERE / "_tmp_timeline"
    tmp.mkdir(exist_ok=True)
    mt.COLORS, mt.OUT = COLORS, tmp
    sys.argv = [sys.argv[0], "1", "7", "15", "23"]
    mt.main()
    for k in range(3):
        (tmp / f"trk_{k}.png").rename(HERE / f"2026-10-17-trk_{k}.png")
    shutil.rmtree(tmp)


if __name__ == "__main__":
    wanted = set(sys.argv[1:]) or {"gt", "mask", "trk"}
    if "trk" in wanted:
        trk_thumbnails()
    if "gt" in wanted:
        gt_video()
    if "mask" in wanted:
        mask_video()
