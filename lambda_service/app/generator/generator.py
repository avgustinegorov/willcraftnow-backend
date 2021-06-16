from smtplib import SMTP
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from .generators.will_generator.generator import WillGenerator
from .generators.lpa_generator.generator import LPAGenerator
from .generators.schedule_generator.generator import ScheduleGenerator
from .generators.invoice_generator.generator import InvoiceGenerator
from .generators.will_generator.parser import WillParser
from .generators.lpa_generator.parser import LPAParser
from .generators.schedule_generator.parser import ScheduleParser
import requests
import json
from .email.email_helper import EmailHelper


class Generator(object):
    def __init__(self, request_body=None, upload=None):

        self.upload_docs = upload if upload is not None else request_body['upload_docs']
        if not self.upload_docs:
            print("Not uploading documents.")

        self.assets = request_body['assets']
        self.entities = request_body['entities']

        if not request_body['upload_url']:
            raise Exception('upload_url kwarg is required')

        self.upload_url = request_body['upload_url']

        if not request_body['invoice_upload_url']:
            raise Exception('invoice_upload_url kwarg is required')

        self.invoice_upload_url = request_body['invoice_upload_url']

        if not request_body['data']:
            raise Exception('data arg is required')

        self.data = request_body['data']

        if not request_body['invoice_data']:
            raise Exception('invoice_data arg is required')

        self.invoice_data = request_body['invoice_data']

        if not request_body['user']:
            raise Exception('user arg is required')

        self.user = request_body['user']

        if not self.data['order_number']:
            raise Exception('order_number arg is required')

        self.order_number = self.data['order_number']

        self.parser = None
        self.doc_type = request_body['doc_type']

        if request_body['doc_type'] == "WILL":
            self.generator = WillGenerator
            self.parser = WillParser
        elif request_body['doc_type'] == "LPA":
            self.generator = LPAGenerator
            self.parser = LPAParser
        elif request_body['doc_type'] == "SCHEDULE_OF_ASSETS":
            self.generator = ScheduleGenerator
            self.parser = ScheduleParser
        else:
            raise Exception('doc_type arg is required')

        self.legal_service = self.data['legal_services'][0] if self.data['legal_services'] and len(
            self.data['legal_services']) != 0 else None
        self.firm = self.legal_service['firm_details'] if self.legal_service else None

        self.invoice_generator = InvoiceGenerator(data=self.invoice_data, user=self.user,
                                                  order_number=self.order_number)

        self.doc_generator = self.generator(data=self.data, user=self.user, parser=self.parser,
                                            order_number=self.order_number, assets=self.assets, entities=self.entities)

    def generate_documents(self, encrypt=True):
        self.doc_generator.clean()
        self.doc_generator.generate()
        self.doc_generator.build(encrypt_pdf=encrypt)
        return self.doc_generator.get_stream()

    def doc_stream(self):
        return self.doc_generator.get_stream()

    def doc_content(self):
        return self.doc_generator.get_content()

    def generate_invoice(self):
        self.invoice_generator.clean()
        self.invoice_generator.generate()
        self.invoice_generator.build(encrypt_pdf=False)
        return self.invoice_generator.get_stream()

    def invoice_stream(self):
        return self.invoice_generator.get_stream()

    def run(self):
        self.generate_invoice()
        invoice_stream = self.invoice_stream()

        if self.upload_docs:
            self.upload(invoice_stream)

        self.generate_documents()

        document_stream = self.doc_stream()

        if self.upload_docs:
            self.upload(document_stream)

        EmailHelper(order_type=self.doc_type,
                    order_number=self.order_number,
                    user_email=self.user['email'],
                    document_stream=self.generate_documents(),
                    invoice_stream=self.generate_invoice(),
                    send_lawyer_email=True if self.legal_service else False,
                    firm=self.firm).send_emails()

        return self

    def upload(self, stream):
        # files = {'file': (self.upload_filename, stream)}
        files = {'filename': stream}
        http_response = requests.put(
            self.upload_url, files=files)
        print(http_response.status)
