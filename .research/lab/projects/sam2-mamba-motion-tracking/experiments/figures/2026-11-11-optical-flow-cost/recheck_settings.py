"""Re-check of the settings behind 05-flow-moved-object.png (2026-11-13, after the 11/13 MTG).

Same two pairs as flow_arrows.py, all at 1024x1024 (the SAM2 input). For each setting: the mean flow inside the
object at t (px at 1024), and the IoU of the object at t moved by the flow (every pixel moved, 9x9 closing) with
the object at t+1. The ground-truth centroid shift is printed for reference. One pair per speed, so only a check.

  python recheck_settings.py > data/recheck_settings.txt
"""
import time

import cv2
import numpy as np
from PIL import Image

from flow_cost import R

S = 1024
CFGS = {
    "farneback L3 w15 (used)": lambda a, b: cv2.calcOpticalFlowFarneback(a, b, None, 0.5, 3, 15, 3, 5, 1.2, 0),
    "farneback L5 w15": lambda a, b: cv2.calcOpticalFlowFarneback(a, b, None, 0.5, 5, 15, 3, 5, 1.2, 0),
    "DIS ultrafast (used)": lambda a, b: cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_ULTRAFAST).calc(a, b, None),
    "DIS medium": lambda a, b: cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM).calc(a, b, None),
}


def gray(path):
    return cv2.cvtColor(cv2.resize(cv2.imread(path), (S, S), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY)


def mask(path, oid):
    m = (np.array(Image.open(path)) == oid).astype(np.uint8)
    return cv2.resize(m, (S, S), interpolation=cv2.INTER_NEAREST) > 0


cv2.setNumThreads(1)
for vid, t, oid in (("24df9789", 3, 1), ("198021ad", 11, 1)):
    ga, gb = gray(f"{R}/JPEGImages/{vid}/{t:05d}.jpg"), gray(f"{R}/JPEGImages/{vid}/{t + 1:05d}.jpg")
    m0, m1 = mask(f"{R}/Annotations/{vid}/{t:05d}.png", oid), mask(f"{R}/Annotations/{vid}/{t + 1:05d}.png", oid)
    ys, xs = np.nonzero(m0)
    y1, x1 = np.nonzero(m1)
    print(f"{vid} t={t}: GT centroid shift dx={x1.mean() - xs.mean():.1f} dy={y1.mean() - ys.mean():.1f} px @1024")
    for name, fn in CFGS.items():
        t0 = time.time(); f = fn(ga, gb); ms = (time.time() - t0) * 1000
        u = f[ys, xs]
        xt = np.clip(np.round(xs + u[:, 0]).astype(int), 0, S - 1)
        yt = np.clip(np.round(ys + u[:, 1]).astype(int), 0, S - 1)
        mv = np.zeros((S, S), np.uint8); mv[yt, xt] = 1
        mv = cv2.morphologyEx(mv, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8)) > 0
        print(f"  {name:24s} mean flow dx={u[:, 0].mean():7.1f} dy={u[:, 1].mean():5.1f}  "
              f"IoU={(mv & m1).sum() / (mv | m1).sum():.2f}  {ms:.0f} ms")
