"""Exporta la fuente Markdown de la explicación a PDF, manteniendo una fuente editable."""
from html import escape
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Image, KeepTogether, Paragraph, SimpleDocTemplate, Spacer

from data_prep import ROOT
from style import INK, MUTED, NAVY, TEAL


def main():
    source = ROOT / "docs/Explicacion_Diseno_Lab9.md"
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle("Body", fontName="Helvetica", fontSize=10.5, leading=14,
                              textColor=colors.HexColor(INK), spaceAfter=7, alignment=TA_LEFT,
                              allowWidows=0, allowOrphans=0))
    for key, size, color in [("Title", 22, NAVY), ("Heading2", 15, NAVY), ("Heading3", 12, TEAL)]:
        styles[key].fontSize = size
        styles[key].leading = size * 1.2
        styles[key].textColor = colors.HexColor(color)
        styles[key].spaceBefore = 8
        styles[key].spaceAfter = 6
        styles[key].keepWithNext = True
    story = []
    for block in source.read_text(encoding="utf-8").split("\n\n"):
        block = block.strip()
        if not block:
            continue
        image = re.fullmatch(r"!\[(.*?)\]\((.*?)\)", block)
        if image:
            figure = Image(str(source.parent / image[2]))
            ratio = 480 / figure.imageWidth
            figure.drawWidth = 480
            figure.drawHeight = figure.imageHeight * ratio
            story.append(KeepTogether([figure, Paragraph(escape(image[1]), styles["Body"]), Spacer(1, 8)]))
        else:
            level = len(block) - len(block.lstrip("#"))
            style = styles[{1: "Title", 2: "Heading2", 3: "Heading3"}.get(level, "Body")]
            story.append(Paragraph(escape(block[level:].strip()).replace("\n", " "), style))

    def footer(canvas, doc):
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor(MUTED))
        canvas.drawString(48, 28, "CC3084 · Laboratorio 9 · Nicolás Concuá y Felipe Aguilar")
        canvas.drawRightString(A4[0] - 48, 28, str(doc.page))

    document = SimpleDocTemplate(str(source.with_suffix(".pdf")), pagesize=A4,
                                 leftMargin=48, rightMargin=48, topMargin=44, bottomMargin=46,
                                 title="Laboratorio 9 — Decisiones de diseño",
                                 author="Nicolás Concuá y Felipe Aguilar")
    document.build(story, onFirstPage=footer, onLaterPages=footer)
    print("Documento actualizado:", source.with_suffix(".pdf"))


if __name__ == "__main__":
    main()
