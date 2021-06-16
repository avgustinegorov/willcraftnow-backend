from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


class Message:
    def __init__(self, server=None, email_main=None, to_email=None, subject=None):
        self.server = server

        self.message = MIMEMultipart('related')
        self.alt_message = MIMEMultipart('alternative')
        self.message.attach(self.alt_message)

        self.message['Subject'] = subject
        self.message['From'] = email_main
        self.message['To'] = to_email if not isinstance(
            to_email, list) else ' ,'.join(to_email)
        self.message['Bcc'] = email_main
        self.from_email = email_main
        self.to_email = to_email if not isinstance(
            to_email, list) else ' ,'.join(to_email)

    def attach_file(self, file_name, stream):
        payload = MIMEBase('application', 'octate-stream', Name=file_name)
        payload.set_payload(stream)

        # add header with pdf name
        payload.add_header('Content-Decomposition',
                           'attachment', filename=file_name)
        self.message.attach(payload)

    def attach_pdf(self, file_name, stream):
        payload = MIMEBase('application', 'octate-stream', Name=file_name)
        payload.set_payload(stream)

        # enconding the binary into base64
        encoders.encode_base64(payload)

        # add header with pdf name
        payload.add_header('Content-Decomposition',
                           'attachment', filename=file_name)
        self.message.attach(payload)

    def set_text_content(self,  text_content):
        self.alt_message.attach(MIMEText(text_content, "plain"))

    def set_html_content(self,  html_content,):
        self.alt_message.attach(MIMEText(html_content, "html"))

    def send_message(self):
        return self.server.sendmail(
            self.from_email, self.to_email, self.message.as_string())
