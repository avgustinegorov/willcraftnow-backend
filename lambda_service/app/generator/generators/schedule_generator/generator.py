import sys
import os
import pytz
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import pdfencrypt
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm, inch
from reportlab.platypus.flowables import HRFlowable, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageTemplate,
    Paragraph,
    Table,
    TableStyle,
    Image,
    Spacer,
    FrameBreak,
    PageBreak,
    NextPageTemplate,
)

from ..base_report_lab import BaseReportLabGenerator
from .styles import *
from .utils import Utils


class CustomDocTemplate(BaseDocTemplate):
    """Overwriting the doc class method to add a
    flowable-build hook
    """

    height = 0
    added_execution_block_notif = False

    def handle_flowable(self, flowables):
        """Adds "( Execution Page To Follow )" onto the flowables array
        just after a FrameBreak (which is only added in case of
        the keepWithNext paragraph for execution blocks)
        """
        if (
            isinstance(flowables[0], type(FrameBreak))
            and not self.added_execution_block_notif
        ):
            self.added_execution_block_notif = True
            flowables.insert(
                0,
                Paragraph(
                    "<b>( Execution Page To Follow )</b>", execution_block_notice_style
                ),
            )
        super().handle_flowable(flowables)


class ScheduleGenerator(BaseReportLabGenerator, Utils):
    """ Implements all methods required for premium will generation """

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        """ Sets the premium-will specific properties """

        super().__init__(*args, **kwargs)
        self.doc_class = CustomDocTemplate
        self.services = self.data['legal_services'][0] if self.data['legal_services'] and len(
            self.data['legal_services']) else None

    def footer(self, canvas, doc):
        generated_time = self.generated_at.strftime(
            "%d.%m.%Y %I:%M:%S %p"
        )
        canvas.saveState()
        canvas.setFont("Helvetica", 10)
        canvas.drawString(6.85 * inch, 0.55 * inch, "Page %d" %
                          int(self.doc.page - 1))
        canvas.drawString(1 * inch, 0.75 * inch,
                          f'Generated At:  {generated_time}')
        canvas.drawString(
            1 * inch, 0.55 *
            inch, f"Order:               {self.order_number}"
        )
        canvas.drawString(
            3.15 * inch, 11 *
            inch, f"Schedule of Assets of {self.user['name']}"
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

        # Adding the Generate At Datetime
        self.create_generic_text(
            f"Dated this {'_'*8} of {'_'*7} {datetime.now(pytz.timezone('Asia/Singapore')).year}",
            will_title_page_header_style,
        )

        # Spacer to center the title
        self.add_spacer(height=2.3 * inch)

        # The Table for the Last Will and Testament
        table = [
            [Paragraph("Schedule of Assets",
                       will_title_page_title_style)],
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
        self.create_generic_text(
            "www.willcraftnow.com", will_title_page_header_style)
        self.create_generic_text(
            "enquiries@willcraftnow.com", will_title_page_header_style
        )

    def generate(self):
        """ Creates all PDF Elements required for a PremiumWill """

        super().generate()

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
        will_object = self.clean_data['blocks']
        sub_paragraph_counter = 0
        for count, object in enumerate(will_object, -1):
            if "header" in object["type"]:
                para = self.AssetHeaderWrapper(object["text"], context)
            else:
                if object["depth"] == 0:
                    para = self.ParagraphWrapper(
                        object["text"], context, count)
                elif object["depth"] == 1:
                    para = self.SubParagraphWrapper(
                        object["text"], sub_paragraph_counter, context
                    )
                elif object["depth"] == 2:
                    para = self.ParagraphWrapperNoBullet(
                        object["text"], context)

            if "header" not in will_object and object["depth"] != 1:
                sub_paragraph_counter = 0
            else:
                sub_paragraph_counter += 1

            self.create_generic_text(para, will_base_text_style)

        self.add_spacer(height=0.5 * cm)
