#!/usr/bin/env python3
"""Main-slide qualitative videos without the frame number (2026-10-17, user's request).

Same drawing as before, only the "frame N" text in the lower left is not written:
- p1a (dancetrack0097, ①; allok25s = the same sequence, frame 676–928, about 25 s) and allfail (dancetrack0026, ②): full frame, GT / SAM2 / SAMURAI / Ours
  (../2026-10-12-qualitative-patterns/render_videos.py, ../2026-10-17-qualitative-patterns-v2/render_videos_v2.py)
- localok (dancetrack0025 GT 3, ③): focal person only, SAM2 / SAMURAI / Ours (../2026-10-17-qualitative-focal-only/render_focal_only.py)
- localfail0007 (dancetrack0007 GT 1, ④): GT (green) and ID 1 (cyan) only, portrait, frame 314–413 (10 s)
  (../2026-10-17-qualitative-focal-only/render_target_only.py; it never wrote frame numbers)
The supplement slides keep the numbered versions.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIG = HERE.parent
for d in ("2026-10-12-qualitative-patterns", "2026-10-17-qualitative-patterns-v2", "2026-10-17-qualitative-focal-only"):
    sys.path.insert(0, str(FIG / d))
import render_videos as rv  # noqa: E402
import render_videos_v2 as rv2  # noqa: E402
import render_focal_only as rf  # noqa: E402
import render_target_only as rt  # noqa: E402

no_label = lambda *a, **k: None  # frame 番号を書かない
for mod in (rv, rv2, rf):
    mod.frame_label = no_label
    mod.OUT_DIR = HERE
rt.OUT_DIR = HERE


def run(name):
    if name == "p1a":
        rv.render(next(c for c in rv.CASES if c[0] == "p1a"))
    elif name == "allfail":
        rv2.render(next(c for c in rv2.CASES if c[0] == "allfail"))
    elif name == "allok25s":  # ① を約25秒に伸ばした版：frame 676–928（3手法とも全員の ID が一度もずれない最長区間）
        rv2.render(("allok25s", "dancetrack0097", 686, 918, None, False))  # 前後10フレームを足して 676–928
    elif name == "localok":
        rf.render(next(c for c in rf.CASES if c[0] == "localok"))
    elif name == "localfail0007":
        sys.argv = ["render_target_only.py", "localfail0007", "dancetrack0007", "324", "403", "1", "390"]  # 314–413
        rt.main()


if __name__ == "__main__":
    for name in (sys.argv[1:] or ["p1a", "allfail", "localok", "localfail0007"]):
        run(name)
