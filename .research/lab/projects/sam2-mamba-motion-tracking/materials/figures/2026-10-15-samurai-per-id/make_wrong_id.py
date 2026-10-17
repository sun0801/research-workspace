#!/usr/bin/env python3
"""Schematics of an ID error for the 「提案手法1の課題点」 slide (not actual tracking results; made from masks_all.png).

mask_id2_wrong.png: ID 2's color (green) lands on the person of ID 3 (used with the ID 1-4 rows figure).
mask_id1_wrong.png: ID 1's color (purple) lands on the person of ID 2 (used with the stacked figure, where ID 1 is in front).
In both, the wrong person is recolored with the ID's color and boxed; the ID's own person stays gray like the others.
Run with an OpenCV python (e.g. the samurai conda env)."""
from pathlib import Path

import cv2
import numpy as np

from make_per_id import BOXES

HERE = Path(__file__).parent
COLORS = {1: (226, 48, 101), 2: (58, 160, 46)}  # BGR，マスク画像の ID 1（紫）・ID 2（緑）の色
BOX_COLORS = {1: (226, 48, 101), 2: (46, 200, 58)}


def person_mask(img, k):
    """masks_all.png で人 k に塗られたマスク（色の濃い画素の，いちばん大きいかたまり）"""
    x1, y1, x2, y2 = BOXES[k]
    sat = cv2.cvtColor(img[y1:y2, x1:x2], cv2.COLOR_BGR2HSV)[..., 1]
    m = (sat > 90).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((7, 7), np.uint8))
    n, lab, stats, _ = cv2.connectedComponentsWithStats(m)
    m = (lab == 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))).astype(np.uint8)
    return cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))


def make(src_id, dst_id, out_name):
    img = cv2.imread(str(HERE / "masks_all.png"))
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.cvtColor(g, cv2.COLOR_GRAY2BGR)
    out = (gray * 0.55 + 255 * 0.25).astype(np.uint8)
    x1, y1, x2, y2 = BOXES[dst_id]
    mask = person_mask(img, dst_id)
    lum = g[y1:y2, x1:x2].astype(np.float32)[..., None] / 255.0
    tinted = np.clip(np.array(COLORS[src_id], np.float32) * 0.55 + lum * 255 * 0.55, 0, 255)
    out[y1:y2, x1:x2] = np.where(mask[..., None] > 0, tinted, gray[y1:y2, x1:x2] * 0.9).astype(np.uint8)
    cv2.rectangle(out, (x1, y1), (x2, y2), BOX_COLORS[src_id], 4)
    cv2.imwrite(str(HERE / out_name), out)
    print(out_name, "mask pixels", int(mask.sum()))


if __name__ == "__main__":
    make(2, 3, "mask_id2_wrong.png")
    make(1, 2, "mask_id1_wrong.png")
