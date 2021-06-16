import pytz
from datetime import datetime
from io import BytesIO
from .base_parser import BaseParser


class BasePdfGenerator(object):
    def __init__(self, parser=None, *args, data=None, user=None, assets=[], entities=[],
                 order_number=None, **kwargs):

        self.generated_at = datetime.now(pytz.timezone('Asia/Singapore'))
        self.stream = BytesIO()
        self.parser = parser

        self.assets = assets
        self.entities = entities

        if not data:
            raise Exception("Data kwarg required")
        self.data = data

        if not user:
            raise Exception('user arg is required')
        self.user = user
        self.password = self.user.get("id_number", None)

        if not self.data['order_number']:
            raise Exception('order_number arg is required')
        self.order_number = self.data['order_number']

        self.content = None

    def clean(self):
        if not self.parser:
            self.parser = BaseParser
        self.clean_data = self.parser(
            data=self.data, user=self.user, assets=self.assets, entities=self.entities).parse()

    def generate(self):
        raise Exception("Create not implimented")

    def encrypt(self):
        raise Exception("Encrypt not implimented")

    def get_content(self):
        return self.content

    def build(self, encrypt_pdf=True):
        if (encrypt_pdf):
            self.encrypt()

    def get_content(self):
        return None

    def get_stream(self):
        self.stream.seek(0)
        return self.stream

    def write(self):
        raise Exception("Write not implimented")
