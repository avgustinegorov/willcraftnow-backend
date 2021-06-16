import html
import os

from jinja2 import Environment, FileSystemLoader
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from smtplib import SMTP

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from .message_helper import Message
from .template_helper import Template
import requests


class EmailHelper:
    def __init__(self, *args, order_type=None, order_number=None, user_email=None, document_stream=None, invoice_stream=None, send_lawyer_email=False, firm=None, **kwargs):
        self.email_main = os.environ.get('EMAIL_MAIN')
        self.password = os.environ.get('EMAIL_HOST_PASSWORD')

        if not order_type:
            raise Exception('document kwarg required')
        self.order_type = order_type

        if not order_number:
            raise Exception('document kwarg required')
        self.order_number = order_number

        if not user_email:
            raise Exception('user_email kwarg required')

        self.user_email = user_email
        self.userhandle = user_email.split("@")[0]

        if not document_stream:
            raise Exception('document kwarg required')
        self.document_stream = document_stream

        if not invoice_stream:
            raise Exception('invoice_stream kwarg required')
        self.invoice_stream = invoice_stream

        if send_lawyer_email and not firm:
            raise Exception('tncs_file kwarg required')

        self.firm = firm
        self.send_lawyer_email = send_lawyer_email
        self.directory_path = os.path.dirname(os.path.abspath(__file__))

    def start_server(self):
        self.server = SMTP('smtp.gmail.com', 587)
        self.server.starttls()
        self.server.login(self.email_main, self.password)

    def end_server(self):
        self.server.quit()

    def send_emails(self):
        self.start_server()
        try:
            self.send_success_emails()
            if self.send_lawyer_email:
                self.send_lawyer_emails()
        except:
            print("Emails Failed")
        self.end_server()

    def get_execution_letter_path(self):
        schema = {
            "LPA": "lpa_execution_letter",
            "WILL": "will_execution_letter",
        }

        execution_letter_filename = f"{schema[self.order_type]}.pdf"
        execution_letter_filepath = os.path.join(
            self.directory_path, f"templates/{execution_letter_filename}"
        )
        return execution_letter_filepath

    def send_success_emails(self):
        template = Template(order_type=self.order_type,
                            template_type='success',
                            context={
                                "user": self.userhandle,
                                "order": self.order_number,
                            })
        message = Message(server=self.server, email_main=self.email_main,
                          to_email=self.user_email, subject="[WillCraft] Succcess!")
        message.attach_pdf(
            f"Invoice_{self.order_number}.pdf",  self.invoice_stream.getvalue())
        message.attach_pdf(f"{self.userhandle}.pdf",
                           self.document_stream.getvalue())

        with open(self.get_execution_letter_path(), "rb") as f:
            message.attach_pdf(f"Instructions & Next Steps.pdf", f.read())

        message.set_html_content(template.get_html())
        message.set_text_content(template.get_text())
        message.send_message()

    def send_lawyer_emails(self):
        template = Template(order_type=self.order_type,
                            template_type='lawyer',
                            context={
                                "user": self.userhandle,
                                "firm": self.firm["name"],
                                "order": self.order_number,
                            })
        message = Message(server=self.server,
                          email_main=self.email_main,
                          #   to_email=[self.firm['email'], self.user_email],
                          to_email=[self.user_email],
                          subject=f"[WillCraft] Referral to {self.firm['name']}")

        tncs_file = requests.get(self.firm['tncs_file']).content
        message.attach_pdf(f"Terms & Conditions.pdf",  tncs_file)

        message.set_html_content(template.get_html())
        message.set_text_content(template.get_text())
        result = message.send_message()
        print(result)
