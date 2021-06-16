import os
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import TableStyle

grey = HexColor("#ececee")
black = HexColor("#2c2c2c")

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
