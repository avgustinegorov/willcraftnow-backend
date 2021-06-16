import os
from reportlab.lib.styles import *
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import TableStyle


def gen_font_path(font):
    directory_path = os.path.dirname(os.path.abspath(__file__))
    try:
        return os.path.join(
            directory_path, "assets", "font", "dejavu", font
        )
    except:
        return f"../assets/font/dejavu/{font}"


grey = HexColor("#ececee")
black = HexColor("#2c2c2c")

pdfmetrics.registerFont(TTFont("DejaVuSans", gen_font_path("DejaVuSans.ttf")))
pdfmetrics.registerFont(
    TTFont("DejaVuSans-Bold", gen_font_path("DejaVuSans-Bold.ttf")))

base_text_style = ParagraphStyle(
    "base_text", fontSize=8, fontName="DejaVuSans", textColor=black,
)

base_text_bold_style = ParagraphStyle(
    "base_text", fontSize=10, spaceAfter=2, fontName="DejaVuSans-Bold", textColor=black,
)

centered_text_style = ParagraphStyle(
    "centered_text",
    fontSize=8,
    fontName="DejaVuSans",
    textColor=black,
    alignment=TA_CENTER,
)

invoice_frame_style = TableStyle(
    [
        ("BOX", (0, 0), (-1, -1), 0.25, black),
        ("TOPPADDING", (0, 0), (0, 0), 20),
        ("BOTTOMPADDING", (-1, -1), (-1, -1), 20),
        ("LEFTPADDING", (0, 0), (-1, -1), 25),
        ("RIGHTPADDING", (0, 0), (-1, -1), 25),
    ]
)

invoice_items_style = TableStyle(
    [("LINEBELOW", (0, 0), (-1, -1), 1, grey),
     ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ]
)

fees_table_style = TableStyle(
    [("LINEBELOW", (2, 0), (-1, -2), 1, grey),
     ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ]
)

free_comment_style = ParagraphStyle(
    "free_comment",
    fontSize=6,
    fontName="DejaVuSans",
    textColor=black,
    alignment=TA_CENTER,
)

edit_comment_style = ParagraphStyle(
    "free_comment",
    fontSize=10,
    fontName="DejaVuSans-Bold",
    textColor=black,
    alignment=TA_CENTER,
)
