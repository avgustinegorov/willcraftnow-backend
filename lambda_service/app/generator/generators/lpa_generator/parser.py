import io
import os

from dateutil.parser import parse
from pdfrw import PageMerge, PdfDict, PdfName, PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from ..base_parser_utils import BaseParserUtils
from ..base_parser import BaseParser


class LPAParser(BaseParser, BaseParserUtils):

    def parse(self):
        data = self.clean_data(self.data, output="VALUE")

        return {
            **self.data,
            'user_details': self.user,
            'available_restrictions': {
                "property_and_affairs_restrictions": len([person for person in data['persons'] if person['donee_powers'] and (
                    person['donee_powers']['powers'] == "PERSONAL_WELFARE"
                    or person['donee_powers']['powers'] == "BOTH"
                )]) != 0,
                "personal_welfare_restrictions": len([person for person in data['persons'] if person['donee_powers'] and (
                    person['donee_powers']['powers'] == "PROPERTY_AND_AFFAIRS"
                    or person['donee_powers']['powers'] == "BOTH"
                )]) != 0,
            },
            "replacement_donees": [
                {**person, "details": self.get_entity_details(person)}
                for person in data["persons"]
                if "REPLACEMENT_DONEE" in person["entity_roles"]
            ],
            "donees": [
                {**person, "details": self.get_entity_details(person)}
                for person in data["persons"]
                if "DONEE" in person["entity_roles"]
            ]
        }
