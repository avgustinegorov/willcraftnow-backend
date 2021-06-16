import os
import sys

from django.template.loader import get_template
from django.utils import timezone
from reportlab.lib import pdfencrypt
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm, inch
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    FrameBreak,
    Image,
    NextPageTemplate,
    PageBegin,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.flowables import HRFlowable, KeepTogether

from services.pdf_gen.base_pdf import BasePdf
from services.pdf_gen.base_pdf_utils import *
from services.pdf_gen.pdf_styles import *


class PremiumWillSchedule(BasePdf):
    """ Implements all methods required for premium will generation """

    def __init__(
        self,
        witnesses=[],
        generated_at=timezone.localtime(timezone.now()),
        user={},
        order=None,
        encrypt_password=None,
        *args,
        **kwargs,
    ):
        """ Sets the premium-will specific properties """

        self.generated_at = generated_at
        self.user = user
        self.order = order
        self.doc_class = BaseDocTemplate

        super().__init__()

    def footer(self, canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 10)
        canvas.drawString(6.85 * inch, 0.55 * inch, "Page %d" % int(self.doc.page - 1))
        canvas.drawString(1 * inch, 0.75 * inch, f"Generated At:  {self.generated_at}")
        canvas.drawString(
            1 * inch, 0.55 * inch, f"Order:               {self.order.order_number}"
        )
        canvas.drawString(
            3.15 * inch, 11 * inch, f"Schedule of Assets of {self.user['name']}"
        )
        canvas.restoreState()

    def generate_title_page(self):
        """Generates all objects for the Title Page
        and adds them onto the PDF Elems array
        """
        # A tiny spacing for top margin
        self.add_spacer(height=0.1 * cm)

        # Header for the title page
        self.create_generic_text(
            "Private and Confidential", will_title_page_header_style
        )

        # Spacer to center the title
        self.add_spacer(height=2.3 * inch)

        # The Table for the Last Will and Testament
        table = [
            [Paragraph("Schedule of Assets", will_title_page_title_style)],
            [Paragraph("of", will_small_text_style)],
            [Paragraph(self.user["name"], will_title_base_text_style)],
        ]
        table = Table(table, colWidths=[3.4 * inch])
        table.setStyle(will_title_page_table_style)
        self.elems.append(table)

        # Adding spacer to move everything down
        self.add_spacer(height=2.3 * inch)

        # Adding the Logo for the title page
        image = Image(self.logo_image)
        image._restrictSize(3 * inch, 2 * inch)
        self.elems.append(image)

        # Adding the final parts of the title-page footer
        self.create_generic_text("www.willcraftnow.com", will_title_page_header_style)
        self.create_generic_text(
            "enquiries@willcraftnow.com", will_title_page_header_style
        )

    def create_will_from_object(self, will_object, outf="test.pdf"):
        """ Creates all PDF Elements required for a PremiumWill """

        # Generating the base pdf the code will work with
        self.generate_base_pdf(outf)

        # Adding all requirements for the first page onto the PDF Elems array
        self.generate_title_page()

        # Breaking off to the next page and switching page templates
        self.elems.append(NextPageTemplate("other-pages-frame"))
        self.elems.append(PageBreak())

        context = {
            "LeftIndent": 30,
            "spaceBefore": 15,
            "subLeftIndent": 55,
            "subBulletLeftIndent": 30,
        }

        sub_paragraph_counter = 0
        for count, object in enumerate(will_object, -1):
            if "header" in object["type"]:
                para = AssetHeaderWrapper(object["text"], context)
            else:
                if object["depth"] == 0:
                    para = ParagraphWrapper(object["text"], context, count)
                elif object["depth"] == 1:
                    para = SubParagraphWrapper(
                        object["text"], sub_paragraph_counter, context
                    )
                elif object["depth"] == 2:
                    para = ParagraphWrapperNoBullet(object["text"], context)

            if "header" not in will_object and object["depth"] != 1:
                sub_paragraph_counter = 0
            else:
                sub_paragraph_counter += 1

            self.create_generic_text(para, will_base_text_style)

        self.add_spacer(height=0.5 * cm)
