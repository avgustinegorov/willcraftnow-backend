from django.utils import timezone

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, inch
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

from .pdf_styles import *

from reportlab.lib import pdfencrypt


class BasePdf:
    """A Base Class that all PDF Service object MUST
    inherit from to implement common PDF Requirements
    """

    def __init__(self, *args, **kwargs):
        """ Sets the base reportlab styles as a class attribute """
        # Base Reportlab styles
        self.base_styles = getSampleStyleSheet()
        self.page_size = A4

        this_directory = os.path.dirname(os.path.realpath(__file__))
        self.logo_image = os.path.join(this_directory, "assets", "img", "logo.png")

    def add_spacer(self, width=0, height=0):
        """Adds a spacer to the PDF Elems array of the given
        dimensions
        """
        self.elems.append(Spacer(width=width, height=height))

    def create_generic_text(
        self, text, style, space_below=0.2 * cm, bulletText=None, keepWithNext=False
    ):
        """Adds a paragraph with the given text
        of the given style to the pdf elems array
        """
        p = Paragraph(text, style, bulletText=bulletText)
        if keepWithNext:
            p.keepWithNext = True
        self.elems.append(p)
        self.add_spacer(width=0, height=space_below)

    def build_pdf(self):
        """ Builds the PDF to the outf given in create_invoice - basically just to enable modularization """
        self.doc.build(self.elems)

    def encrypt_pdf(self, encrypt_password=None):
        if encrypt_password != None:
            encrypt = pdfencrypt.StandardEncryption(encrypt_password, "OwnerPass")
            encrypt.setAllPermissions(0)
            encrypt.canPrint = 1
            self.doc.encrypt = encrypt

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
            id="other-pages-frame", frames=other_pages_frame, onPage=self.footer
        )
        self.doc.addPageTemplates([first_page_template, other_pages_template])

        # A container for all PDF elements that need to go on the PDF
        self.elems = []

    def footer(self):
        return
