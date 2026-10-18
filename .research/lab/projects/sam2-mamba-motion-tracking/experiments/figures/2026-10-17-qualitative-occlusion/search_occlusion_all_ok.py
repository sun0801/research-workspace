#!/usr/bin/env python3
"""Search DanceTrack val for windows with occlusions where all three methods still keep every ID (2026-10-17).

Occlusion event: two GT people overlap (IoU >= OCC_IOU) and their left-right order is different before and after
the overlap (they cross). A window "succeeds" for a method when, for every GT person who appears in the window,
the track matched in the first 10 frames is the one matched in the last 10 frames, and that track matches the person
(IoU >= 0.5) in at least COV of the frames. Windows where all three methods succeed are ranked by crossings.
"""
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "2026-10-12-qualitative-patterns"))
from render_videos import GT_DIR, METHODS, read_mot  # noqa: E402

WIN, STRIDE, OCC_IOU, COV = (int(sys.argv[1]) if len(sys.argv) > 1 else 100), 20, 0.3, 0.9  # 引数で窓の長さ（フレーム）


def iou(a, b):
    ax, ay, aw, ah = a; bx, by, bw, bh = b
    ix = max(0.0, min(ax + aw, bx + bw) - max(ax, bx)); iy = max(0.0, min(ay + ah, by + bh) - max(ay, by))
    i = ix * iy
    return i / (aw * ah + bw * bh - i + 1e-9)


def matched(gtrows, predrows):
    """GT id -> best track id (IoU >= 0.5)"""
    out = {}
    for g, *gb in gtrows:
        b = max(((iou(gb, p[1:]), p[0]) for p in predrows), default=(0, None))
        if b[0] >= 0.5:
            out[g] = b[1]
    return out


def crossings(gt, a, b):
    events = 0
    for f in range(a, b + 1):
        rows = {r[0]: r[1:] for r in gt.get(f, [])}
        prev = {r[0]: r[1:] for r in gt.get(f - 1, [])}
        for g in rows:
            for h in rows:
                if g < h and g in prev and h in prev and iou(rows[g], rows[h]) >= OCC_IOU:
                    cx = lambda bb: bb[0] + bb[2] / 2
                    if (cx(prev[g]) - cx(prev[h])) * (cx(rows[g]) - cx(rows[h])) < 0:
                        events += 1
    return events


def main():
    res = []
    for seqdir in sorted(d for d in GT_DIR.iterdir() if (d / "gt/gt.txt").exists()):
        seq = seqdir.name
        gt = read_mot(seqdir / "gt/gt.txt")
        preds = {m: read_mot(p / f"{seq}.txt") for m, p in METHODS.items()}
        n = max(gt)
        mt = {m: {f: matched(gt.get(f, []), pr.get(f, [])) for f in range(1, n + 1)} for m, pr in preds.items()}
        for a in range(1, n - WIN + 2, STRIDE):
            b = a + WIN - 1
            pres = Counter(r[0] for f in range(a, b + 1) for r in gt.get(f, []))
            people = set(pres)  # 窓の中に一度でも出てくる人はすべて確認する
            if len(people) < 2:
                continue
            ok = True
            for m in preds:
                for g in people:
                    fs = [f for f in range(a, b + 1) if any(r[0] == g for r in gt.get(f, []))]
                    first = Counter(mt[m][f].get(g) for f in fs[:10]).most_common(1)[0][0]
                    last = Counter(mt[m][f].get(g) for f in fs[-10:]).most_common(1)[0][0]
                    cov = sum(mt[m][f].get(g) == first for f in fs) / len(fs)
                    if first is None or first != last or cov < COV:
                        ok = False; break
                if not ok:
                    break
            if ok:
                c = crossings(gt, a, b)
                if c:
                    res.append((c, seq, a, b, len(people)))
    best = {}
    for c, seq, a, b, k in sorted(res, reverse=True):
        if all(not (s == seq and abs(a - a2) < WIN) for (s, a2) in best):
            best[(seq, a)] = (c, b, k)
    for (seq, a), (c, b, k) in list(best.items())[:15]:
        print(f"{seq} frame {a}-{b}: {k} people, crossings {c}")


if __name__ == "__main__":
    main()
