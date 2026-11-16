"""PDF の文字位置（pdftotext -bbox）と pptx の枠の位置を比べ，枠の下端・右端を越えた単語を数える．
使い方: python check_overflow.py deck.pptx deck.pdf  （はみ出し 0 なら "OVERFLOW 0"）"""
import re
import subprocess
import sys

from pptx import Presentation

pptx, pdf = sys.argv[1], sys.argv[2]
prs = Presentation(pptx)
W, H = prs.slide_width, prs.slide_height
html = subprocess.run(["pdftotext", "-bbox", pdf, "-"], capture_output=True, text=True).stdout
pages = html.split("<page ")[1:]
bad = 0
for n, (slide, page) in enumerate(zip(prs.slides, pages), 1):
    pw, ph = (float(x) for x in re.search(r'width="([\d.]+)" height="([\d.]+)"', page).groups())
    kx, ky = W / pw, H / ph
    words = [(float(a) * kx, float(b) * ky, float(c) * kx, float(d) * ky, w)
             for a, b, c, d, w in re.findall(r'xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">([^<]*)<', page)]
    boxes = [(s.left, s.top, s.left + s.width, s.top + s.height) for s in slide.shapes
             if s.left is not None and s.width]
    for x0, y0, x1, y1, w in words:
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        inside = [b for b in boxes if b[0] - 20000 <= cx <= b[2] + 20000 and b[1] - 20000 <= cy <= b[3] + 20000]
        if not inside or y1 > H or x1 > W:
            bad += 1
            print(f"slide {n}: 枠外の文字 '{w}' at y={cy/H:.2f}")
print("OVERFLOW", bad)
