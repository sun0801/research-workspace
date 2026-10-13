#!/usr/bin/env python3
"""Small frame images for the TBD / TBA concept diagrams (dancetrack0052, frame 1).

- frame.png: input frame
- detections.png: GT boxes drawn in white without IDs (stand-in for detector output)
- tracks.png: GT boxes with per-ID colors and labels (stand-in for tracking output)
The boxes are GT, used only to illustrate what each stage outputs.
"""

import csv
from pathlib import Path

import cv2

SEQ_DIR = Path("/mnt/HDD10TB-2/aburatani/dataset/DanceTrack/train2/train2/dancetrack0052")
OUT_DIR = Path(__file__).parent
FRAME = 1
CROP = (130, 0, 1566, 1080)  # GT extent in frame 1 is x 150-1676; aspect 1.45 around it
SIZE = (725, 500)
COLORS = {0: (60, 60, 230), 1: (220, 140, 30), 2: (70, 180, 60), 3: (180, 60, 170)}  # BGR


def boxes():
    with open(SEQ_DIR / "gt/gt.txt", newline="") as stream:
        return [(int(r[1]), *map(float, r[2:6])) for r in csv.reader(stream) if int(r[0]) == FRAME]


def save(name, img):
    x, y, w, h = CROP
    cv2.imwrite(str(OUT_DIR / name), cv2.resize(img[y:y + h, x:x + w], SIZE, interpolation=cv2.INTER_AREA))


def main():
    base = cv2.imread(str(SEQ_DIR / "img1" / f"{FRAME:08d}.jpg"))
    save("frame.png", base)
    det, trk = base.copy(), base.copy()
    font = cv2.FONT_HERSHEY_SIMPLEX
    for tid, x, y, w, h in boxes():
        p1, p2 = (round(x), max(4, round(y))), (round(x + w), min(1075, round(y + h)))
        cv2.rectangle(det, p1, p2, (255, 255, 255), 12, cv2.LINE_AA)
        cv2.rectangle(trk, p1, p2, COLORS[tid], 12, cv2.LINE_AA)
        label = str(tid + 1)
        (tw, th), base_ = cv2.getTextSize(label, font, 3.2, 8)
        cv2.rectangle(trk, p1, (p1[0] + tw + 30, p1[1] + th + base_ + 24), COLORS[tid], -1)
        cv2.putText(trk, label, (p1[0] + 15, p1[1] + th + 12), font, 3.2, (255, 255, 255), 8, cv2.LINE_AA)
    save("detections.png", det)
    save("tracks.png", trk)


if __name__ == "__main__":
    main()
