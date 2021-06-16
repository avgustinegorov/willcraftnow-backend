from pdfrw import PageMerge, PdfDict, PdfName, PdfReader, PdfWriter
from .base_generator import BasePdfGenerator
import os
import io
import PyPDF2 as p


class BasePDFRWGenerator(BasePdfGenerator):

    def build(self, encrypt_pdf=False):
        pdf = PdfWriter()
        pdf.write(self.stream, self.read)
        self.stream.seek(0)
        super().build(encrypt_pdf=encrypt_pdf)

    def encrypt(self):
        newbuf = io.BytesIO()
        output = p.PdfFileWriter()
        input_stream = p.PdfFileReader(self.stream)

        for i in range(0, input_stream.getNumPages()):
            output.addPage(input_stream.getPage(i))

        output.encrypt(self.password, use_128bit=True)
        output.write(newbuf)
        self.stream = newbuf
