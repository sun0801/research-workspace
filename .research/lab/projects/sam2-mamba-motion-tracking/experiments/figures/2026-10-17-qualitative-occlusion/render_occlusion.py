#!/usr/bin/env python3
"""Render the occlusion candidates (GT / SAM2 / SAMURAI / Ours, full frame, no frame number, 10 fps).
Same drawing as ../2026-10-17-qualitative-patterns-v2/render_videos_v2.py. usage: render_occlusion.py [case ids]"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
for d in ("2026-10-12-qualitative-patterns", "2026-10-17-qualitative-patterns-v2"):
    sys.path.insert(0, str(HERE.parent / d))
import render_videos_v2 as rv2  # noqa: E402

rv2.frame_label = lambda *a, **k: None
rv2.OUT_DIR = HERE
CASES = [  # (case id, seq, first, last, focal, crop) — 窓は search_occlusion_all_ok.py の結果。前後10フレームを足して描く
    ("occok", "dancetrack0065", 61, 160, None, False),
    ("occok", "dancetrack0058", 141, 240, None, False),
    ("occok20s", "dancetrack0058", 11, 190, None, False),   # 20秒：1–200
    ("occok20s", "dancetrack0065", 51, 230, None, False),   # 20秒：41–240
]
if __name__ == "__main__":
    wanted = set(sys.argv[1:])
    for c in CASES:
        if not wanted or c[0] in wanted or c[1] in wanted:
            rv2.render(c)
