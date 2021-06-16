try:
    from django.conf import settings
except:
    pass

import os
from reportlab.lib.styles import *
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import TableStyle


def gen_font_path(font):
    try:
        return os.path.join(
            settings.BASE_DIR, "services", "pdf_gen", "assets", "font", "dejavu", font
        )
    except:
        return f"../assets/font/dejavu/{font}"


grey = HexColor("#ececee")
black = HexColor("#2c2c2c")

pdfmetrics.registerFont(TTFont("DejaVuSans", gen_font_path("DejaVuSans.ttf")))
pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", gen_font_path("DejaVuSans-Bold.ttf")))

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
    [("LINEBELOW", (0, 0), (-1, -1), 1, grey), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),]
)

fees_table_style = TableStyle(
    [("LINEBELOW", (2, 0), (-1, -2), 1, grey), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),]
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

will_title_page_header_style = ParagraphStyle(
    "will_title_page_header_style", fontSize=10, textColor=black, alignment=TA_CENTER
)

will_title_page_title_style = ParagraphStyle(
    "will_title_page_title_style", fontSize=18, textColor=black, alignment=TA_CENTER
)

will_title_page_table_style = TableStyle(
    [
        ("TOPPADDING", (0, 0), (0, 0), 45),
        ("TOPPADDING", (0, 1), (0, 1), 10),
        ("BOTTOMPADDING", (-1, -1), (-1, -1), 45),
        ("LEFTPADDING", (0, 0), (-1, -1), 25),
        ("RIGHTPADDING", (0, 0), (-1, -1), 25),
        ("LINEABOVE", (0, 0), (0, 0), 1, black),
        ("LINEBELOW", (-1, -1), (-1, -1), 1, black),
    ]
)

will_small_text_style = ParagraphStyle(
    "will_small_text_style", fontSize=10, textColor=black, alignment=TA_CENTER
)

will_title_base_text_style = ParagraphStyle(
    "will_title_base_text_style", fontSize=14, textColor=black, alignment=TA_CENTER
)

will_base_text_style = ParagraphStyle(
    "will_base_text_style",
    fontSize=12,
    textColor=black,
    alignment=TA_JUSTIFY,
    leading=16,
)

execution_block_notice_style = ParagraphStyle(
    "execution_block_notice_style", fontSize=12, textColor=black, alignment=TA_CENTER
)
