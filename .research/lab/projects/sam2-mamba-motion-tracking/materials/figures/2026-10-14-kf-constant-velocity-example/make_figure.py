#!/usr/bin/env python3
"""Constant-velocity extrapolation vs actual motion (dancetrack0052 GT), for the research-goal slide.

Left panel: frame t with the past trajectory and the extrapolation. Right panel: frame t+P with the
actual box (green) and the extrapolated box (red, dashed). The center of one GT box is tracked. Velocity = mean displacement over the last H frames
before t; the prediction extends it linearly for P frames (the same constant-velocity assumption
as the Kalman filter motion model). This is an illustration from GT, not a SAMURAI output.

usage: make_figure.py ID T [out.png]
"""
import csv
import sys
from collections import defaultdict
from pathlib import Path

import cv2
import numpy as np

SEQ = Path("/mnt/HDD10TB-2/aburatani/dataset/DanceTrack/train2/train2/dancetrack0052")
OUT = Path(__file__).parent
H, P = 10, 15  # 過去10フレーム，先15フレーム（20fpsで0.75秒）
WHITE, GREEN, RED = (255, 255, 255), (80, 200, 60), (40, 40, 230)  # BGR


def gt():
    rows = defaultdict(dict)
    with open(SEQ / "gt/gt.txt", newline="") as f:
        for r in csv.reader(f):
            x, y, w, h = map(float, r[2:6])
            rows[int(r[1])][int(r[0])] = (x, y, w, h)
    return rows


def dashed(img, p, q, color, th, dash=22, gap=14):
    p, q = np.array(p, float), np.array(q, float)
    n = np.linalg.norm(q - p)
    if n == 0:
        return
    d = (q - p) / n
    s = 0.0
    while s < n:
        a, b = p + d * s, p + d * min(s + dash, n)
        cv2.line(img, tuple(map(int, a)), tuple(map(int, b)), color, th, cv2.LINE_AA)
        s += dash + gap


def main():
    gid, t = int(sys.argv[1]), int(sys.argv[2])
    out = Path(sys.argv[3]) if len(sys.argv) > 3 else OUT / "kf-constant-velocity.png"
    boxes = gt()[gid]
    pt = lambda f: np.array([boxes[f][0] + boxes[f][2] / 2, boxes[f][1] + boxes[f][3] / 2])  # 枠の中心
    past = np.array([pt(f) for f in range(t - H, t + 1)])
    fut = np.array([pt(f) for f in range(t, t + P + 1)])
    v = (past[-1] - past[0]) / H  # 過去10フレームの平均速度
    pred = past[-1] + np.outer(np.arange(P + 1), v)

    x, y, w, h = boxes[t]
    pbox = (x + v[0] * P, y + v[1] * P, w, h)  # 等速で動かした枠（大きさは時刻 t のまま）
    abox = boxes[t + P]

    def frame(f):
        im = cv2.imread(str(SEQ / "img1" / f"{f:08d}.jpg"))
        return (im * 0.75).astype(np.uint8)  # 線を見やすくするため少し暗く

    def rect(im, b, color, th, dash=False):
        p1, p2 = (b[0], b[1]), (b[0] + b[2], b[1] + b[3])
        if not dash:
            cv2.rectangle(im, tuple(map(int, p1)), tuple(map(int, p2)), color, th, cv2.LINE_AA)
            return
        for a_, b_ in [((p1[0], p1[1]), (p2[0], p1[1])), ((p2[0], p1[1]), (p2[0], p2[1])),
                       ((p2[0], p2[1]), (p1[0], p2[1])), ((p1[0], p2[1]), (p1[0], p1[1]))]:
            dashed(im, a_, b_, color, th)

    # 左: 時刻 t（枠，これまでの軌跡，等速で延ばした予測）
    left = frame(t)
    rect(left, boxes[t], WHITE, 4)
    cv2.polylines(left, [past.astype(np.int32)], False, WHITE, 7, cv2.LINE_AA)
    for q in past[:-1]:
        cv2.circle(left, tuple(map(int, q)), 7, WHITE, -1, cv2.LINE_AA)
    dashed(left, pred[0], pred[-1], RED, 8)
    cv2.circle(left, tuple(map(int, pred[-1])), 13, RED, -1, cv2.LINE_AA)
    cv2.circle(left, tuple(map(int, past[-1])), 11, WHITE, -1, cv2.LINE_AA)
    # 右: 時刻 t+P（実際の枠と軌跡，予測した枠）
    right = frame(t + P)
    rect(right, pbox, RED, 6, dash=True)
    rect(right, abox, GREEN, 6)
    cv2.polylines(right, [fut.astype(np.int32)], False, GREEN, 8, cv2.LINE_AA)
    cv2.circle(right, tuple(map(int, fut[-1])), 13, GREEN, -1, cv2.LINE_AA)
    cv2.circle(right, tuple(map(int, pred[-1])), 13, RED, -1, cv2.LINE_AA)

    pts = np.vstack([past, fut, pred, [[x, y], [x + w, y + h]], [pbox[:2], np.add(pbox[:2], pbox[2:])],
                     [abox[:2], np.add(abox[:2], abox[2:])]])
    x0, y0 = pts.min(0) - 60
    x1, y1 = pts.max(0) + 60
    ch = min(max(y1 - y0, (x1 - x0) * 3 / 4), 1080)
    cw = ch * 4 / 3  # 4:3 で切り出す
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    X0 = int(np.clip(cx - cw / 2, 0, 1920 - cw)); Y0 = int(np.clip(cy - ch / 2, 0, 1080 - ch))
    crop = lambda im: cv2.resize(im[Y0:Y0 + int(ch), X0:X0 + int(cw)], (800, 600), interpolation=cv2.INTER_AREA)
    gap = np.full((600, 24, 3), 255, np.uint8)
    cv2.imwrite(str(out), np.hstack([crop(left), gap, crop(right)]))
    print(out, "error at +%d frames: %.0f px" % (P, np.linalg.norm(pred[-1] - fut[-1])))

if __name__ == "__main__":
    main()
