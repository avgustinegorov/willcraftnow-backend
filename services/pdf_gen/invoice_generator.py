from .pdf_invoice import InvoicePdf

from io import BytesIO
from django.core.files.base import ContentFile
from django.http import HttpResponse


def invoice_generator(order):
    invoice = order.invoice.latest()
    invoice = invoice.update_invoice()
    invoice_items = invoice.get_invoice_items()
    pdf_invoice = InvoicePdf(
        order_number=order.order_number, invoice_items=invoice_items, invoice=invoice
    )

    outf = BytesIO()
    # Generating the invoice
    pdf_invoice.create_invoice(outf)
    pdf_invoice.build_pdf()
    outf.seek(0)

    # Saving the pdf into the database
    invoice.save_invoice(ContentFile(outf.getvalue()))
    outf.seek(0)

    filename = f"Will {order.order_number} Invoice.pdf"
    # Response the Invoice will be built on and sent to the user
    response = HttpResponse(outf, content_type="application/pdf")
    response["Content-Disposition"] = f'filename="{filename}"'

    return response
