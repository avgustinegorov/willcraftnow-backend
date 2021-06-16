try:
    pass
except:
    pass

from django.utils import timezone

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
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
    PageBreak,
    NextPageTemplate,
)

from .pdf_styles import *
from .base_pdf import BasePdf

from reportlab.lib import pdfencrypt


class PdfWill(BasePdf):
    """
    A Base Will Object that all of the different will-type specific
    generators must inherit from to implement pdf generation functionality
    """

    def __init__(
        self,
        generated_at=timezone.localtime(timezone.now()),
        user={},
        doc_class=BaseDocTemplate,
    ):
        """Sets the fields required for the WillGeneration as class
        attributes
        """
        self.generated_at = generated_at
        self.user = user
        self.doc_class = doc_class

        # Setting the page size here for convenience
        self.page_size = A4

        this_directory = os.path.dirname(os.path.realpath(__file__))
        self.logo_image = os.path.join(this_directory, "assets", "img", "logo.png")

        super().__init__()

    def generate_base_pdf(self, outf):
        """ Creates a Base PDF that all of the other methods can work on top of """
        self.doc = self.doc_class(outf, pagesize=self.page_size)
        # Setting the margins
        self.doc.topMargin = 8 * cm
        self.doc.bottomMargin = 8 * cm
        self.doc.leftMargin = 2.5 * cm
        self.doc.rightMargin = 2.5 * cm

        # Full page dimensions exluding dimensiosns
        width = self.page_size[0] - self.doc.rightMargin - self.doc.leftMargin
        self.page_size[1] - self.doc.topMargin - self.doc.bottomMargin

        # The firm page frame needs to have a boundary
        first_page_frame = Frame(
            self.doc.leftMargin,
            self.doc.bottomMargin - 4.8 * cm,
            width,
            self.page_size[1] - self.doc.topMargin + 2 * cm,
            showBoundary=1,
        )
        # While the rest don't need a boundary
        other_pages_frame = Frame(
            self.doc.leftMargin,
            self.doc.bottomMargin - 4.8 * cm,
            width,
            self.page_size[1] - self.doc.topMargin + 2 * cm,
            showBoundary=0,
        )

        first_page_template = PageTemplate(
            id="first-page-frame", frames=first_page_frame
        )
        # TODO: On the other pages, add an onPage argument to render the header/footer on all other pages
        other_pages_template = PageTemplate(
            id="other-pages-frame", frames=other_pages_frame
        )

        self.doc.addPageTemplates([first_page_template, other_pages_template])

        # A container for all PDF elements that need to go on the PDF
        self.elems = []

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
        today = dt.today()
        self.create_generic_text(
            f"Dated this {'_'*8} of {'_'*7} {today.year}", will_title_page_header_style
        )

        # Spacer to center the title
        self.add_spacer(height=2.3 * inch)

        # The Table for the Last Will and Testament
        table = [
            [Paragraph("Last Will and Testament", will_title_page_title_style)],
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

    def create_will(self, outf="test.pdf"):
        """A Workflow method that combines all of the other
        class methods to generate a PDF Elements array
        """
        # Generating the base pdf the code will work with
        self.generate_base_pdf(outf)

        # Adding all requirements for the first page onto the PDF Elems array
        self.generate_title_page()

        # Breaking off to the next page and switching page templates
        self.elems.append(NextPageTemplate("other-pages-frame"))
        self.elems.append(PageBreak())

    def build_pdf(self):
        """ Builds the PDF to the outf given in create_will - basically just to enable modularization """
        self.doc.build(self.elems)

    def encrypt_pdf(self, encrypt_password=None):
        if encrypt_password != None:
            encrypt = pdfencrypt.StandardEncryption(encrypt_password, "OwnerPass")
            encrypt.setAllPermissions(0)
            encrypt.canPrint = 1
            self.doc.encrypt = encrypt


if __name__ == "__main__":
    user = {
        "name": "Alvin",
    }
    pdf = PdfWill(user=user)
    pdf.create_will()
    pdf.build_pdf()
