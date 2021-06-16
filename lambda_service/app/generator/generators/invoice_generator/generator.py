
import pytz
from ..base_report_lab import BaseReportLabGenerator
from ..base_report_lab_styles import *
from reportlab.lib.units import cm, inch
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
)
from datetime import datetime
from dateutil import parser


class InvoiceGenerator(BaseReportLabGenerator):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.invoice_items = self.data['line_items']
        self.discounts = self.data['discounts']

    def generate_base(self):
        """ Creates a Base PDF that all of the other methods can work on top of """
        self.doc = BaseDocTemplate(self.stream, pagesize=self.page_size)

        # Setting the margins
        self.doc.topMargin = 4 * cm
        self.doc.bottomMargin = 3 * cm
        self.doc.leftMargin = 1 * cm
        self.doc.rightMargin = 1 * cm

        # Full page dimensions exluding dimensiosns
        width = self.page_size[0] - self.doc.rightMargin - self.doc.leftMargin
        height = self.page_size[1] - self.doc.topMargin - self.doc.bottomMargin

        header_frame = Frame(
            self.doc.leftMargin,
            height + 0.2 * inch,
            width,
            2.3 * inch,
            id="header",
            showBoundary=1,
        )

        body_frame = Frame(
            self.doc.leftMargin + 0.8 * cm,
            height - 3.9 * inch,
            width - 1.8 * cm,
            4.1 * inch,
            id="invoice",
            showBoundary=1,
        )

        full_page_frame = Frame(
            self.doc.leftMargin,
            self.doc.bottomMargin - 2 * cm,
            width,
            self.page_size[1] - self.doc.topMargin + 2 * cm,
            showBoundary=0,
        )
        # frames=[header_frame, body_frame])
        template = PageTemplate(id="base-frame", frames=full_page_frame)
        self.doc.addPageTemplates([template])

        # A container for all PDF elements that need to go on the PDF
        self.elems = []

    def generate_header(self):
        """Generates a header that consists of a Logo and
        the Order number and adds it to the PDF elems
        """
        image = Image(self.logo_image, hAlign="CENTER")
        # Restricting the size to maintain aspect ratio while reducing size
        image._restrictSize(1.8 * inch, 3 * inch)

        # Adding the image to the PDF elements
        self.elems.append(image)
        # Adding a tiny spacer to move the text down
        self.add_spacer(width=0, height=0.1 * cm)

        # Adding the Invoice number text
        self.create_generic_text(
            f"Invoice - {self.order_number}", centered_text_style)

        # Adding bottom margin to the header
        self.add_spacer(width=0, height=1.2 * cm)

    def add_basic_order_details(self):
        """Adds the order details table to the PDF
        Elements
        """
        date_paid = str(datetime.now(pytz.timezone(
            'Asia/Singapore'))) if not self.data['date_paid'] else self.data['date_paid']
        date_paid = parser.parse(date_paid).strftime("%d %B %Y")

        table = [
            [
                Paragraph("Date:", base_text_style),
                Paragraph(self.generated_at.strftime(
                    "%d %B %Y"), base_text_style),
            ],
            [
                Paragraph("Order No:", base_text_style),
                Paragraph(self.order_number, base_text_style),
            ],
            [
                Paragraph("Date Paid:", base_text_style),
                Paragraph(date_paid, base_text_style),
            ]
            if self.data['date_paid']
            else [],
        ]

        table = Table(
            table, colWidths=[1 * inch, 6 * inch], rowHeights=0.4 * cm, hAlign=TA_LEFT
        )

        self.elems.append(table)

        # Adding bottom margin for the details
        self.add_spacer(width=0, height=1 * cm)

    def add_invoice_table(self):
        """ Adds the invoice table to the PDF elements array """
        empty_col = Paragraph("", base_text_style)
        table = []
        full_width = 6.9 * inch  # Actually is 6.2 after taking out padding

        # The Invoice table is actually a table of 4 different flowables

        # The first row is the main invoice items - full width table
        header_row = [
            [Paragraph("Item", base_text_style),
             Paragraph("Price", base_text_style)]
        ]

        line_item_rows = []

        for i in self.invoice_items:
            item_header = [Paragraph(i["name"], base_text_bold_style)]
            item_entry = item_header + [
                [Paragraph(f" - {j['name']}", base_text_style)]
                for j in i["subparagraph"]
            ]
            line_item_rows += [
                [item_entry, Paragraph(f"${i['price']}", base_text_style)]
            ]

        expiry_time_entry = [
            [Paragraph(f"Edit Time", base_text_bold_style)],
            [Paragraph(f" - {self.data['expiry_time']} Days*",
                       base_text_style)],
        ]
        expiry_time_rows = [
            [expiry_time_entry, Paragraph("$0.00", base_text_style)]]

        invoice_table = header_row + line_item_rows + expiry_time_rows  # EditTime Entry
        invoice_table = Table(
            invoice_table, colWidths=[5.2 * inch, 1 * inch], rowHeights=None
        )
        invoice_table.setStyle(invoice_items_style)
        table.append([invoice_table])

        # The second row is the one for the Fees and Totals
        fees_table = [
            [
                empty_col,
                Paragraph("Total", base_text_style),
                Paragraph(f"${self.data['net_price']}", base_text_style),
            ],
            [
                empty_col,
                Paragraph(
                    "Credit Card Transaction Fees (3.4% + $0.50)", base_text_style
                ),
                Paragraph(f"${self.data['card_fees']}", base_text_style),
            ],
            [
                empty_col,
                Paragraph("Total Payable", base_text_style),
                Paragraph(
                    f"${self.data['net_price_after_card_fees']}", base_text_style
                ),
            ],
        ]
        fees_table = Table(
            fees_table,
            colWidths=[2.6 * inch, 2.6 * inch, 1 * inch],
            rowHeights=0.9 * cm,
        )
        fees_table.setStyle(fees_table_style)
        table.append([fees_table])

        expiry_date = str(datetime.now(pytz.timezone(
            'Asia/Singapore'))) if not self.data['expiry_date'] else self.data['expiry_date']
        expiry_date = parser.parse(expiry_date).strftime('%b. %d, %Y, %H:%M')
        # The Third row is basically just a Paragraph stating a comment for the "free"items
        free_comment = Paragraph(
            " ".join(
                f"*We've included {self.data['expiry_time']} days of edits, free! Just"
                " in case you want to change details such as your allocations or      "
                "           assets, or if you realised you made any typos. Your free"
                " edit time ends on"
                f" {expiry_date}".split(
                    " ")
            ),
            free_comment_style,
        )
        table.append([free_comment])

        # And the fourth row is also just a paragraph stating remaining edit time
        # edit_time_comment = Paragraph(
        #     f"Your total edit period is {self.invoice.expiry_time} days, and ends on {self.invoice.expiry_date.strftime('%b. %d, %Y, %H:%M')}",
        #     edit_comment_style
        # )
        # table.append([edit_time_comment])

        table = Table(table, colWidths=[full_width])
        table.setStyle(invoice_frame_style)
        self.elems.append(table)

    def generate(self):
        """A workflow method that combines all of the other class methods to
        generate and return an invoice pdf
        """
        super().generate()

        # Adding on the header to the PDF Elems container
        self.generate_header()

        # Adding the details table into the PDF Elem container
        self.add_basic_order_details()

        # Moving to the Invoice frame
        # self.elems.append(FrameBreak())
        # Adding the actual invoice table
        self.add_invoice_table()
