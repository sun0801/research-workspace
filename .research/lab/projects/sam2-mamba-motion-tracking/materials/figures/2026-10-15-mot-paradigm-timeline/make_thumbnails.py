#!/usr/bin/env python3
"""Frame images for the TBD / TBA timeline diagrams (dancetrack0052 GT, three frames).

For each frame k: frame_k.png (input), det_k.png (white boxes, no ID: detector output),
trk_k.png (ID-colored boxes: tracking output), tba_k.png (ID-colored boxes + dashed search
region around the previous frame's box of ID 1, as in template matching). Boxes are GT and only
illustrate what each stage outputs.

usage: make_thumbnails.py FPREV F0 F1 F2   (FPREV: the frame before F0, used only for the search region of k=0)
"""
import csv
import sys
from pathlib import Path

import cv2
import numpy as np

SEQ = Path("/mnt/HDD10TB-2/aburatani/dataset/DanceTrack/train2/train2/dancetrack0052")
OUT = Path(__file__).parent
SIZE = (725, 500)
SEARCH_ID = 0  # GT ID 0（表示は ID 1）
COLORS = {0: (60, 60, 230), 1: (220, 140, 30), 2: (70, 180, 60), 3: (180, 60, 170)}  # BGR, ID 1-4


def gt(frames):
    rows = {f: {} for f in frames}
    with open(SEQ / "gt/gt.txt", newline="") as fh:
        for r in csv.reader(fh):
            f = int(r[0])
            if f in rows:
                rows[f][int(r[1])] = tuple(map(float, r[2:6]))
    return rows


def dashed_rect(img, p1, p2, color, th, dash=40, gap=24):
    (x1, y1), (x2, y2) = p1, p2
    for a, b in [((x1, y1), (x2, y1)), ((x2, y1), (x2, y2)), ((x2, y2), (x1, y2)), ((x1, y2), (x1, y1))]:
        a, b = np.array(a, float), np.array(b, float)
        n = np.linalg.norm(b - a); d = (b - a) / n; s = 0.0
        while s < n:
            q1, q2 = a + d * s, a + d * min(s + dash, n)
            cv2.line(img, tuple(map(int, q1)), tuple(map(int, q2)), color, th, cv2.LINE_AA)
            s += dash + gap


def label(img, p1, text, color):
    font = cv2.FONT_HERSHEY_SIMPLEX
    (tw, th), base = cv2.getTextSize(text, font, 3.2, 8)
    cv2.rectangle(img, p1, (p1[0] + tw + 30, p1[1] + th + base + 24), color, -1)
    cv2.putText(img, text, (p1[0] + 15, p1[1] + th + 12), font, 3.2, (255, 255, 255), 8, cv2.LINE_AA)


def main():
    prev = int(sys.argv[1])
    frames = [int(a) for a in sys.argv[2:5]]
    boxes = gt([prev] + frames)
    allb = [b for f in frames for b in boxes[f].values()]  # 切り出し範囲は表示する3フレームで決める
    x0 = min(b[0] for b in allb); x1 = max(b[0] + b[2] for b in allb)
    cx = (x0 + x1) / 2; cw = 1566  # 1080 × 1.45
    X0 = int(np.clip(cx - cw / 2, 0, 1920 - cw))
    crop = lambda im: cv2.resize(im[0:1080, X0:X0 + cw], SIZE, interpolation=cv2.INTER_AREA)
    for k, f in enumerate(frames):
        base = cv2.imread(str(SEQ / "img1" / f"{f:08d}.jpg"))
        det, trk, tba = base.copy(), base.copy(), base.copy()
        for tid, (x, y, w, h) in boxes[f].items():
            p1, p2 = (round(x), max(4, round(y))), (round(x + w), min(1075, round(y + h)))
            cv2.rectangle(det, p1, p2, (255, 255, 255), 12, cv2.LINE_AA)
            for im in (trk, tba):
                cv2.rectangle(im, p1, p2, COLORS[tid], 12, cv2.LINE_AA)
                label(im, p1, str(tid + 1), COLORS[tid])
        if True:  # 前フレームの位置の周辺（探索範囲）。見やすさのため1人（ID 1）だけ描く
            for tid, (x, y, w, h) in boxes[frames[k - 1] if k else prev].items():
                if tid != SEARCH_ID:
                    continue
                mx, my = 0.35 * w, 0.06 * h
                dashed_rect(tba, (round(x - mx), max(6, round(y - my))), (round(x + w + mx), min(1073, round(y + h + my))),
                            (255, 255, 255), 10)
        for name, im in (("frame", base), ("det", det), ("trk", trk), ("tba", tba)):
            cv2.imwrite(str(OUT / f"{name}_{k}.png"), crop(im))
    print("frames", frames, "crop x", X0)


if __name__ == "__main__":
    main()
