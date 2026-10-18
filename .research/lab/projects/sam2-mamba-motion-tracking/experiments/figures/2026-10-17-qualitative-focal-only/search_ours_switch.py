#!/usr/bin/env python3
"""Search DanceTrack val for "only Ours fails, visibly" cases (2026-10-17).

For each GT person g and each method, the "own track" is the track that matched g (IoU >= 0.5) most often
in the previous 30 frames. A frame counts as an Ours switch when Ours' own track now matches ANOTHER GT
person h (IoU >= 0.5) that stands next to g, while the own tracks of SAM2 and SAMURAI still match g.
Runs of >= MIN_RUN such frames are listed (longest first).
"""
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "2026-10-12-qualitative-patterns"))
from render_videos import GT_DIR, METHODS, read_mot  # noqa: E402

MIN_RUN, HIST = 6, 30


def iou(a, b):
    ax, ay, aw, ah = a; bx, by, bw, bh = b
    ix = max(0.0, min(ax + aw, bx + bw) - max(ax, bx)); iy = max(0.0, min(ay + ah, by + bh) - max(ay, by))
    i = ix * iy
    return i / (aw * ah + bw * bh - i + 1e-9)


def best_gt(box, gtrows):
    b = max(((iou(box, r[1:]), r[0]) for r in gtrows), default=(0, None))
    return b[1] if b[0] >= 0.5 else None


def main():
    out = []
    for seqdir in sorted(d for d in GT_DIR.iterdir() if (d / "gt/gt.txt").exists()):
        seq = seqdir.name
        gt = read_mot(seqdir / "gt/gt.txt")
        preds = {m: read_mot(p / f"{seq}.txt") for m, p in METHODS.items()}
        # per method, per frame: track -> matched GT (IoU >= 0.5), and GT -> matched track
        t2g = {m: {f: {r[0]: best_gt(r[1:], gt.get(f, [])) for r in pr.get(f, [])} for f in gt} for m, pr in preds.items()}
        g2t = {m: defaultdict(dict) for m in preds}
        for m in preds:
            for f, d in t2g[m].items():
                for t, g in d.items():
                    if g is not None:
                        g2t[m][f][g] = t
        gids = {r[0] for rows in gt.values() for r in rows}
        frames = sorted(gt)
        for g in gids:
            runs, cur = [], None
            for f in frames:
                own = {}
                for m in preds:
                    hist = Counter(g2t[m][ff].get(g) for ff in range(f - HIST, f) if g2t[m][ff].get(g) is not None)
                    own[m] = hist.most_common(1)[0][0] if hist else None
                ok_others = all(own[m] is not None and g2t[m][f].get(g) == own[m] for m in ("SAM2", "SAMURAI"))
                h = t2g["Ours"][f].get(own["Ours"]) if own["Ours"] is not None else None
                hit = ok_others and h is not None and h != g
                if hit:
                    if cur and cur[1] == f - 1 and cur[2] == h:
                        cur[1] = f
                    else:
                        cur = [f, f, h, own["Ours"]]; runs.append(cur)
            for a, b, h, t in runs:
                if b - a + 1 >= MIN_RUN:
                    out.append((b - a + 1, seq, g, a, b, h, t))
    for r in sorted(out, reverse=True)[:25]:
        n, seq, g, a, b, h, t = r
        print(f"{seq} GT {g}: Ours track {t} on GT {h} for frames {a}-{b} ({n})")


if __name__ == "__main__":
    main()
