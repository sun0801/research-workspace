#!/usr/bin/env python3
"""Extract the qualitative-result slides of the restructured midterm deck into a separate pptx.

Keeps the visible slides whose title starts with 「定性的評価：」 or is a supplement example (「補足：…例…」),
and removes animation entries that point to shapes that no longer exist (left over in some supplement slides).
usage: make_qualitative_pptx.py [src.pptx] [out.pptx]   (python-pptx required)
"""
import sys
from pathlib import Path

from pptx import Presentation
from pptx.oxml.ns import qn

HERE = Path(__file__).resolve().parent
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE.parents[1] / "2026-10-12-midterm-slides-restructured.pptx"
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else HERE / "2026-10-17-midterm-qualitative.pptx"


def main():
    p = Presentation(str(SRC))
    lst = p.slides._sldIdLst
    for s, el in zip(list(p.slides), list(lst)):
        t = s.shapes.title.text_frame.text if s.shapes.title is not None else ""
        keep = s._element.get("show") != "0" and (t.startswith("定性的評価：") or (t.startswith("補足：") and "例" in t))
        if not keep:
            lst.remove(el); p.part.drop_rel(el.get(qn("r:id")))
    removed = 0
    for s in p.slides:
        ids = {c.get("id") for c in s.shapes._spTree.iter(qn("p:cNvPr"))}
        tim = s._element.find(qn("p:timing"))
        if tim is None:
            continue
        for t in list(tim.iter(qn("p:spTgt"))):
            if t.get("spid") in ids:
                continue
            n = t
            while n is not None and n.tag != qn("p:video") and not (
                    n.tag == qn("p:par") and n.find(qn("p:cTn")) is not None
                    and n.find(qn("p:cTn")).get("presetClass") == "mediacall"):
                n = n.getparent()
            if n is not None:
                n.getparent().remove(n); removed += 1
    p.save(str(OUT))
    for i, s in enumerate(Presentation(str(OUT)).slides, 1):
        print(i, s.shapes.title.text_frame.text)
    print("stale animation entries removed:", removed)


if __name__ == "__main__":
    main()
