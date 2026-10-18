#!/usr/bin/env python3
"""④ 局所的にうまくいっていない例（dancetrack0079 GT 8）を，10/08 の dancetrack0034 動画と同じ描き方で作る（2026-10-17）。

- 縦長に切り出す（注目する人物の周辺）。10fps（半分の速さ）。
- 描くのは，GT の枠（緑，ラベルなし）と，その手法でこの人物を追っている track の枠（水色，全手法で同じ色，
  ラベルは track の番号）だけ。ほかの track は描かない。
- 追っている track は，窓の最初の10フレームでこの人物に最も多く対応した track（IoU 0.5 以上）。
  SAMURAI・Ours は 8，SAM2 は 4（SAM2 は frame 466 以降 track 8 が画面右端の別の人に付いている）。
推論結果は定量表と同じ（../2026-10-12-qualitative-patterns/render_videos.py の METHODS）。新しい推論はしていない。
"""

import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "2026-10-12-qualitative-patterns"))
from render_videos import GT_DIR, IMG_DIR, METHODS, Writer, read_mot  # noqa: E402
from render_focal_only import iou  # noqa: E402

OUT_DIR = Path(__file__).parent
SEQ, FIRST, LAST, FOCAL = "dancetrack0079", 822, 881, 8   # 既定（引数なし）は最初に作った ④
MARGIN = 10
POSTER = 852
CASE = "localfail"
OUT_W, OUT_H = 500, 660           # 10/08 の動画と同じ大きさ
CROP_H = 360                      # 元画像での切り出しの高さ（人物の高さの約1.7倍）
GT_COLOR, PRED_COLOR = (0, 255, 0), (255, 180, 0)  # BGR：緑，水色（10/08 と同じ）


def draw_box(img, box, color, label=None):
    x, y, w, h = box
    p1, p2 = (round(x), round(y)), (round(x + w), round(y + h))
    cv2.rectangle(img, p1, p2, color, 3, cv2.LINE_AA)
    if label:
        font, scale, th = cv2.FONT_HERSHEY_SIMPLEX, 0.75, 2
        (tw, tth), base = cv2.getTextSize(label, font, scale, th)
        top = max(0, p1[1] - tth - base - 7)
        lx = min(max(0, p1[0]), img.shape[1] - tw - 8)
        cv2.rectangle(img, (lx, top), (lx + tw + 8, top + tth + base + 6), color, -1)
        cv2.putText(img, label, (lx + 4, top + tth + 1), font, scale, (0, 0, 0), th, cv2.LINE_AA)


def main():
    global SEQ, FIRST, LAST, FOCAL, POSTER, CASE
    if len(sys.argv) > 1:  # 例: render_target_only.py localfail2 dancetrack0034 60 110 10 90
        CASE, SEQ, FIRST, LAST, FOCAL, POSTER = sys.argv[1], sys.argv[2], *map(int, sys.argv[3:7])
    gt = read_mot(GT_DIR / SEQ / "gt/gt.txt")
    preds = {m: read_mot(p / f"{SEQ}.txt") for m, p in METHODS.items()}
    f0, f1 = FIRST - MARGIN, LAST + MARGIN
    to_crop = lambda b: ((b[0] - x0) * s, (b[1] - y0) * s, b[2] * s, b[3] * s)
    def own_track(pred):  # 窓の最初の10フレーム（だめなら窓の前の30フレーム）でこの人物に最も多く対応した track
        for start, n in ((FIRST, 10), (FIRST - 30, 30)):
            votes = {}
            for f in range(start, start + n):
                g = next((r[1:] for r in gt.get(f, []) if r[0] == FOCAL), None)
                if g is None:
                    continue
                best = max(((iou(g, r[1:]), r[0]) for r in pred.get(f, [])), default=(0, None))
                if best[0] >= 0.5:
                    votes[best[1]] = votes.get(best[1], 0) + 1
            if votes and start == FIRST and len(votes) == 1 or (votes and start != FIRST):
                return max(votes, key=votes.get)
        raise RuntimeError('no track')
    tracks = {m: own_track(pred) for m, pred in preds.items()}
    boxes = [r[1:] for f in range(f0, f1 + 1) for r in gt.get(f, []) if r[0] == FOCAL]
    H, W = cv2.imread(str(IMG_DIR / SEQ / "img1" / f"{f0:08d}.jpg")).shape[:2]
    # 切り出しは，GT と各手法の追っている track の枠が入る範囲（崩れて大きくなった枠は除く）
    allb = boxes + [r[1:] for m, pred in preds.items() for f in range(f0, f1 + 1) for r in pred.get(f, [])
                    if r[0] == tracks[m] and r[3] < W * 0.3 and r[4] < H * 0.95]
    bx1 = min(b[0] for b in allb); by1 = min(b[1] for b in allb)
    bx2 = max(b[0] + b[2] for b in allb); by2 = max(b[1] + b[3] for b in allb)
    cx, cy = (bx1 + bx2) / 2, (by1 + by2) / 2
    crop_h = max(CROP_H, (by2 - by1) * 1.1, (bx2 - bx1) * 1.05 * OUT_H / OUT_W)
    crop_h = min(crop_h, H); cw = crop_h * OUT_W / OUT_H
    x0 = int(np.clip(cx - cw / 2, 0, W - cw)); y0 = int(np.clip(cy - crop_h / 2, 0, H - crop_h))
    s = OUT_H / crop_h
    stem = f"2026-10-17-{CASE}-{SEQ}-{f0}-{f1}-gt{FOCAL}"
    writers = {m: Writer(OUT_DIR / f"{stem}-{m.lower()}-target.mp4", OUT_W, OUT_H) for m in preds}
    posters = {}
    for f in range(f0, f1 + 1):
        img = cv2.imread(str(IMG_DIR / SEQ / "img1" / f"{f:08d}.jpg"))
        view = cv2.resize(img[y0:y0 + int(crop_h), x0:x0 + int(cw)], (OUT_W, OUT_H), interpolation=cv2.INTER_CUBIC)
        g = next((r[1:] for r in gt.get(f, []) if r[0] == FOCAL), None)
        for m, pred in preds.items():
            canvas = view.copy()
            t = next((r[1:] for r in pred.get(f, []) if r[0] == tracks[m]), None)
            if t is not None:
                draw_box(canvas, to_crop(t), PRED_COLOR, f"ID {tracks[m]}")
            if g is not None:
                draw_box(canvas, to_crop(g), GT_COLOR)
            writers[m].write(canvas)
            if f == POSTER:  # Ours が見失っている途中
                posters[m] = canvas.copy()
    for m, w in writers.items():
        w.close()
        cv2.imwrite(str(OUT_DIR / f"{stem}-{m.lower()}-target-poster.jpg"), posters[m], [cv2.IMWRITE_JPEG_QUALITY, 90])
    print("crop", x0, y0, int(cw), int(crop_h), "tracks", tracks)


if __name__ == "__main__":
    main()
