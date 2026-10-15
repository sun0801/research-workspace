#!/usr/bin/env python3
"""Split the SAM2 mask image of the SAMURAI figure (masks_all.png, 4 people) into per-ID images.
Each mask_id{k}.png keeps the colors inside ID k's box and turns everything else into dim gray."""
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).parent
BOXES = {1: (165, 120, 452, 936), 2: (570, 118, 814, 924), 3: (891, 120, 1122, 924), 4: (1203, 132, 1445, 908)}  # x1, y1, x2, y2


def main():
    img = cv2.imread(str(HERE / "masks_all.png"))
    gray = cv2.cvtColor(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), cv2.COLOR_GRAY2BGR)
    dim = (gray * 0.55 + 255 * 0.25).astype(np.uint8)
    for k, (x1, y1, x2, y2) in BOXES.items():
        out = dim.copy()
        out[y1:y2, x1:x2] = img[y1:y2, x1:x2]
        cv2.imwrite(str(HERE / f"mask_id{k}.png"), out)
        print(k)


if __name__ == "__main__":
    main()
