#!/usr/bin/env python3
"""Images for the SAMURAI (single object) figure on the related-work slide.

input_sot.png: dancetrack0052 frame 1 (the frame used for the input video of the original figure),
               resized to the original 629x351, with only GT ID 1's box (the leftmost person) drawn.
mask_sot.png:  mask_id1.png with the faint boxes of the other people painted out (only ID 1 is tracked).
Run with an OpenCV python (e.g. the samurai conda env)."""
from pathlib import Path

import cv2
import numpy as np

from make_per_id import BOXES

HERE = Path(__file__).parent
SEQ = Path("/mnt/HDD10TB-2/aburatani/dataset/DanceTrack/train2/train2/dancetrack0052")
W, H = 629, 351          # 元の図の入力画像の大きさ
PURPLE = (226, 48, 101)  # BGR，マスク画像（masks_all.png）の ID 1 の枠の色


def input_image():
    f = cv2.imread(str(SEQ / "img1/00000001.jpg"))
    s = W / f.shape[1]
    img = cv2.resize(f, (W, round(f.shape[0] * s)), interpolation=cv2.INTER_AREA)
    top = (img.shape[0] - H) // 2
    img = img[top:top + H]
    gt = np.loadtxt(SEQ / "gt/gt.txt", delimiter=",")
    x, y, w, h = gt[(gt[:, 0] == 1) & (gt[:, 1] == 1)][0, 2:6]  # frame 1，左端の人（GT の ID は 1）
    p1 = (round(x * s), round(y * s) - top)
    p2 = (round((x + w) * s), round((y + h) * s) - top)
    cv2.rectangle(img, p1, p2, PURPLE, 3)
    cv2.imwrite(str(HERE / "input_sot.png"), img)


def mask_image():
    img = cv2.imread(str(HERE / "mask_id1.png"))
    lines = np.zeros(img.shape[:2], np.uint8)
    for k in (2, 3, 4):
        x1, y1, x2, y2 = BOXES[k]
        cv2.rectangle(lines, (x1, y1), (x2, y2), 255, 23)  # 線は枠の座標から内側に5 px ほどずれ，幅も6 px ほどある
    cv2.imwrite(str(HERE / "mask_sot.png"), cv2.inpaint(img, lines, 5, cv2.INPAINT_TELEA))


if __name__ == "__main__":
    input_image()
    mask_image()
