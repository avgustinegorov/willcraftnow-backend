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


class WillGenerator(BaseReportLabGenerator, Utils):
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
            inch, f"Last Will and Testament of {self.user['name']}"
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
            [Paragraph("Last Will and Testament",
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

    def generate_execution_block(self):
        """Creates the execution block elements and adds them
        to the PDF-Elems array with the keepWithNext
        attribute set to True
        """

        if self.user["gender"] == "Male":
            gender = "his"
        else:
            gender = "her"

        english_execution_block_table = [
            [
                Paragraph(
                    "<b>SIGNED</b> by the abovenamed Testator", will_base_text_style
                ),
                Paragraph(")", will_base_text_style),
            ]
        ]

        translation_execution_block_table = [
            [
                Paragraph(
                    "This Will having first been read over to", will_base_text_style
                ),
                Paragraph(")", will_base_text_style),
            ],
            [
                Paragraph(
                    "the abovenamed Testator and interpreted", will_base_text_style
                ),
                Paragraph(")", will_base_text_style),
            ],
            [
                Paragraph(
                    f"in Mandarin to {gender} who understands", will_base_text_style
                ),
                Paragraph(")", will_base_text_style),
            ],
            [
                Paragraph("Mandarin but has no knowledge of and",
                          will_base_text_style),
                Paragraph(")", will_base_text_style),
            ],
            [
                Paragraph(
                    "cannot read the English language by me", will_base_text_style
                ),
                Paragraph(")", will_base_text_style),
            ],
            [
                Paragraph(
                    "______________________ who understands", will_base_text_style
                ),
                Paragraph(")", will_base_text_style),
            ],
            [
                Paragraph(
                    "both the English language and Mandarin", will_base_text_style
                ),
                Paragraph(")", will_base_text_style),
            ],
            [
                Paragraph("which interpretation was done in our",
                          will_base_text_style),
                Paragraph(")", will_base_text_style),
            ],
            [
                Paragraph(
                    "presence when the said Testator appeared", will_base_text_style
                ),
                Paragraph(")", will_base_text_style),
            ],
            [
                Paragraph("thoroughly to understand the Will",
                          will_base_text_style),
                Paragraph(")", will_base_text_style),
            ],
            [
                Paragraph("and to approve the contents thereof",
                          will_base_text_style),
                Paragraph(")", will_base_text_style),
            ],
            [
                Paragraph(
                    "was signed by the abovenamed Testator", will_base_text_style
                ),
                Paragraph(")", will_base_text_style),
            ],
        ]

        common_execution_block_table = [
            [Paragraph(self.user["name"], will_base_text_style), ")"],
            [
                Paragraph(f"as {gender} last Will and Testament",
                          will_base_text_style),
                Paragraph(")", will_base_text_style),
            ],
            [
                Paragraph("in the presence of us being present",
                          will_base_text_style),
                Paragraph(")", will_base_text_style),
            ],
            [
                Paragraph(
                    f"at the same time and who at {gender} request",
                    will_base_text_style,
                ),
                Paragraph(")", will_base_text_style),
            ],
            [
                Paragraph(
                    f"in {gender} presence and in the presence of each other",
                    will_base_text_style,
                ),
                Paragraph(")", will_base_text_style),
            ],
            [
                Paragraph(
                    "have hereunto subscribed our names as witnesses",
                    will_base_text_style,
                ),
                Paragraph(")", will_base_text_style),
            ],
            ["", ""],
        ]

        if self.services and self.services["review_type"] != "EN":
            execution_block_table = (
                translation_execution_block_table + common_execution_block_table
            )
        else:
            execution_block_table = (
                english_execution_block_table + common_execution_block_table
            )

        execution_block_table = Table(
            execution_block_table, colWidths=[4 * inch, 2.3 * inch]
        )
        execution_block_table.keepWithNext = True

        return execution_block_table

    def generate_witness_label_table(self, witness):
        """Generates and returns a Witness Table flowable
        from the given witness
        """
        witness_block_table = [
            [
                Paragraph("Name:", will_base_text_style),
                Paragraph(witness["name"], will_base_text_style),
            ],
            [
                Paragraph(f"{witness['id_document']} No.:",
                          will_base_text_style),
                Paragraph(witness["id_number"], will_base_text_style),
            ],
            [
                Paragraph("Address:", will_base_text_style),
                Paragraph(witness["address"], will_base_text_style),
            ],
        ]

        witness_block_table = Table(
            witness_block_table, colWidths=[1.2 * inch, 1.8 * inch]
        )
        witness_block_table.setStyle(
            TableStyle(
                [
                    ("ALIGNMENT", (0, 0), (-1, -1), "LEFT"),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("FONTSIZE", (0, 0), (-1, -1), 12),
                ]
            )
        )
        return witness_block_table

    def generate_witnesses_execution_block(self):
        """ Adds the witnesses section under the execution block """

        # Adding the witness signatures table
        table = []

        # The witnesses table has three columns and 4 rows - sign1 | spacer | sign2
        rowOne = [Paragraph("WITNESSED BY:", will_base_text_style), "", ""]
        table.append(rowOne)
        rowTwo = [
            Spacer(width=0, height=3 * cm),
            Spacer(width=0, height=3 * cm),
            Spacer(width=0, height=3 * cm),
        ]
        table.append(rowTwo)
        hr_row = [
            HRFlowable(width=3 * inch),
            Paragraph("", will_base_text_style),
            HRFlowable(width=3 * inch),
        ]
        table.append(hr_row)

        # The Second row is basically a table of Witness Labels
        if not self.services:
            witnesses = self.clean_data['witnesses']
        else:
            witnesses = [
                {
                    "name": "",
                    "id_number": "",
                    "id_document": "",
                    "address": "",
                },
                {
                    "name": "",
                    "id_number": "",
                    "id_document": "",
                    "address": "",
                },
            ]

        label_row = [
            self.generate_witness_label_table(witness)
            for witness in witnesses
        ]
        label_row.insert(1, Paragraph("", will_base_text_style))
        table.append(label_row)

        table = Table(table, colWidths=[3 * inch, 0.2 * inch, 3 * inch])
        table.keepWithNext = True
        return table

    def add_execution_block(self):

        witness_execution_block = self.generate_witnesses_execution_block()
        execution_block_table = self.generate_execution_block()

        self.elems.append(
            KeepTogether([execution_block_table, witness_execution_block])
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
        self.content = will_object = self.clean_data['blocks']
        sub_paragraph_counter = 0
        for count, object in enumerate(will_object):
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

        # TODO: Add the actual execution block text here WITH THE KEEPWITHNEXT ATTRIBUTE
        self.add_execution_block()
