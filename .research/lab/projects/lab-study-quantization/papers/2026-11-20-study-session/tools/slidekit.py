"""量子化勉強会スライド共通ビルダー（3案で共用）。

使い方の例:
    from slidekit import Deck
    d = Deck()                                  # tools/template.pptx（研究室テンプレートのマスター）から開始
    d.title_slide("量子化入門", "2026-11-20 研究室勉強会\n油谷")
    d.section("1. 量子化とは")
    d.bullets("量子化とは", ["連続値を少ない段階の整数に丸める", ("lvl1の項目", 1)], notes="読み上げ原稿…", source="出典…")
    d.two_col("比較", left=[...], right_image="figures/x.png", notes="…")
    d.image("全体図", "figures/x.png", caption="…", notes="…", source="…")
    d.table("結果", [["見出し1", "見出し2"], ["a", "b"]], notes="…", source="…")
    d.save("out.pptx")

規約（見本スライドの照合メモに準拠）:
- 本文は「，」を使い，文末に「。」を付けない．タイトルは1行（40pt）に収める．
- 文字列には言語タグ（日本語 ja-JP）とテーマフォント参照（+mn-ea）を付ける（本ライブラリが自動で付ける）．
- 出典は各スライド下部の小さな文字（12pt）．引用書式は「名前 [第一著者+, 会議名年]」．
- ノートは読み上げ原稿．
"""
import copy
import os
import re

from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Pt

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "template.pptx")
L_TITLE, L_CONTENT, L_SECTION, L_TWO, L_TITLEONLY = 0, 1, 2, 3, 5
SLIDE_W, SLIDE_H = 12192000, 6858000
LEFT, FULL_W = 332507, 11578443
BODY_TOP, BODY_H = 1263316, 5594684
SRC_TOP = 6382512  # 出典の位置（下端）
ACCENT = RGBColor(0xC0, 0x39, 0x2B)


def _tag_runs(txBody, size=None):
    """全ての run に言語タグとテーマフォント参照を付ける．"""
    for r in txBody.iter(qn("a:r")):
        rPr = r.find(qn("a:rPr"))
        if rPr is None:
            rPr = etree.SubElement(r, qn("a:rPr"))
            r.insert(0, rPr)
        text = r.find(qn("a:t")).text or ""
        has_ja = bool(re.search(r"[　-鿿＀-￯]", text))
        rPr.set("lang", "ja-JP" if has_ja else "en-US")
        rPr.set("altLang", "en-US" if has_ja else "ja-JP")
        for tag in ("a:latin", "a:ea"):
            el = rPr.find(qn(tag))
            if el is None:
                el = etree.SubElement(rPr, qn(tag))
            el.set("typeface", "+mn-ea")
        if size:
            rPr.set("sz", str(int(size * 100)))


class Deck:
    def __init__(self, template=TEMPLATE):
        self.prs = Presentation(template)
        ids = self.prs.slides._sldIdLst
        for sldId in list(ids):  # 既存スライドを全削除（マスターとレイアウトは残す）
            self.prs.part.drop_rel(sldId.rId)
            ids.remove(sldId)
        self.main_count = 0

    # ---- 低レベル ----
    def _new(self, layout):
        return self.prs.slides.add_slide(self.prs.slide_layouts[layout])

    def _fill(self, ph, items, size=None):
        """items: 文字列または (文字列, レベル) のリスト．"""
        tf = ph.text_frame
        first = True
        for it in items:
            text, lvl = (it, 0) if isinstance(it, str) else it
            p = tf.paragraphs[0] if first else tf.add_paragraph()
            first = False
            p.level = lvl
            # 先頭が "**" で始まる行は強調（太字）
            bold = text.startswith("**")
            text = text.lstrip("*")
            for k, line in enumerate(text.split("\n")):
                if k:
                    p.add_line_break()
                r = p.add_run()
                r.text = line
                if bold:
                    r.font.bold = True
        _tag_runs(tf._txBody, size)

    def _notes(self, s, notes):
        if notes:
            s.notes_slide.notes_text_frame.text = notes
            _tag_runs(s.notes_slide.notes_text_frame._txBody)

    def textbox(self, s, text, left, top, width, height, size=16, bold=False, color=None, align=None):
        tb = s.shapes.add_textbox(Emu(left), Emu(top), Emu(width), Emu(height))
        tf = tb.text_frame
        tf.word_wrap = True
        for k, line in enumerate(text.split("\n")):
            p = tf.paragraphs[0] if k == 0 else tf.add_paragraph()
            if align:
                p.alignment = align
            r = p.add_run()
            r.text = line
            r.font.size = Pt(size)
            r.font.bold = bold
            if color is not None:
                r.font.color.rgb = color
        _tag_runs(tf._txBody)
        return tb

    def source(self, s, text, left=LEFT, width=FULL_W):
        """出典（12pt）．スライド下端に置く．"""
        if text:
            self.textbox(s, text, left, SRC_TOP, width, 384048, size=12)

    # ---- スライド種別 ----
    def title_slide(self, title, subtitle="", notes=""):
        s = self._new(L_TITLE)
        s.shapes.title.text = title
        _tag_runs(s.shapes.title.text_frame._txBody)
        if subtitle:
            s.placeholders[1].text = subtitle
            _tag_runs(s.placeholders[1].text_frame._txBody)
        self._notes(s, notes)
        return s

    def section(self, title, sub="", notes=""):
        s = self._new(L_SECTION)
        s.shapes.title.text = title
        _tag_runs(s.shapes.title.text_frame._txBody)
        ph = s.placeholders[1]
        if sub:
            ph.text = sub
            _tag_runs(ph.text_frame._txBody)
        else:
            ph._element.getparent().remove(ph._element)
        self._notes(s, notes)
        return s

    def bullets(self, title, items, notes="", source="", size=None):
        s = self._new(L_CONTENT)
        s.shapes.title.text = title
        _tag_runs(s.shapes.title.text_frame._txBody)
        self._fill(s.placeholders[1], items, size)
        self._shrink_body(s, source)
        self.source(s, source)
        self._notes(s, notes)
        self.main_count += 1
        return s

    def _shrink_body(self, s, source):
        if source:  # 出典と重ならないよう本文枠の高さを縮める
            ph = s.placeholders[1]
            ph.left, ph.top, ph.width = Emu(LEFT), Emu(BODY_TOP), Emu(FULL_W)
            ph.height = Emu(SRC_TOP - BODY_TOP - 50000)

    def two_col(self, title, left=None, right=None, left_image=None, right_image=None, notes="", source="", size=None):
        """左右2段．各段は文字列リスト（箇条書き）か画像パス．"""
        s = self._new(L_TWO)
        s.shapes.title.text = title
        _tag_runs(s.shapes.title.text_frame._txBody)
        phs = [p for p in s.placeholders if p.placeholder_format.idx in (1, 2)]
        h = (SRC_TOP - BODY_TOP - 50000) if source else BODY_H
        geo = ((LEFT, 5687293), (6172200, 5738750))
        for (gl, gw), ph, items, img in zip(geo, phs, (left, right), (left_image, right_image)):
            ph.left, ph.top, ph.width, ph.height = Emu(gl), Emu(BODY_TOP), Emu(gw), Emu(h)
            if img:
                self._place_image(s, img, ph.left, ph.top, ph.width, ph.height)
                ph._element.getparent().remove(ph._element)
            else:
                self._fill(ph, items or [], size)
        self.source(s, source)
        self._notes(s, notes)
        self.main_count += 1
        return s

    def _place_image(self, s, path, left, top, width, height):
        from PIL import Image

        w, h = Image.open(path).size
        k = min(width / w, height / h)
        iw, ih = int(w * k), int(h * k)
        return s.shapes.add_picture(path, Emu(int(left + (width - iw) / 2)), Emu(int(top + (height - ih) / 2)), Emu(iw), Emu(ih))

    def image(self, title, path, caption="", notes="", source=""):
        """タイトル＋大きな図．図は本文領域に収まる最大サイズで中央配置．キャプションは図の下（16pt）．"""
        s = self._new(L_TITLEONLY)
        s.shapes.title.text = title
        _tag_runs(s.shapes.title.text_frame._txBody)
        cap_h = 450000 if caption else 0
        bottom = SRC_TOP - 50000
        self._place_image(s, path, LEFT, BODY_TOP, FULL_W, bottom - BODY_TOP - cap_h)
        if caption:
            self.textbox(s, caption, LEFT, bottom - cap_h, FULL_W, cap_h, size=16, align=PP_ALIGN.CENTER)
        self.source(s, source)
        self._notes(s, notes)
        self.main_count += 1
        return s

    def table(self, title, rows, col_widths=None, size=18, notes="", source="", lead=None, highlight=None):
        """rows[0] が見出し行．lead: 表の上に置く1行（24pt）．highlight: 強調するセル (行, 列) の集合．"""
        s = self._new(L_TITLEONLY)
        s.shapes.title.text = title
        _tag_runs(s.shapes.title.text_frame._txBody)
        top = BODY_TOP
        if lead:
            self.textbox(s, lead, LEFT, top, FULL_W, 500000, size=24)
            top += 600000
        nr, nc = len(rows), len(rows[0])
        row_h = 480000
        gf = s.shapes.add_table(nr, nc, Emu(LEFT), Emu(top), Emu(FULL_W), Emu(row_h * nr))
        tbl = gf.table
        if col_widths:
            tot = sum(col_widths)
            for i, w in enumerate(col_widths):
                tbl.columns[i].width = Emu(int(FULL_W * w / tot))
        for i, row in enumerate(rows):
            tbl.rows[i].height = Emu(row_h)
            for j, v in enumerate(row):
                c = tbl.cell(i, j)
                c.text = str(v)
                for p in c.text_frame.paragraphs:
                    for r in p.runs:
                        r.font.size = Pt(size)
                        r.font.bold = i == 0 or bool(highlight and (i, j) in highlight)
                _tag_runs(c.text_frame._txBody)
        self.source(s, source)
        self._notes(s, notes)
        self.main_count += 1
        return s

    def save(self, path):
        self.prs.save(path)
        return path
