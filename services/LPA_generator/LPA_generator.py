import io
import os

import environ
import PyPDF2 as p
from core.serializers import LPAOrderSerializer
from dateutil.parser import parse
from django.conf import settings
from django.core.files.base import ContentFile
from pdfrw import PageMerge, PdfDict, PdfName, PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from ..helpers import clean_data


def clean_unit_number(unit_number):
    return f"{unit_number:04}" if unit_number else None


def clean_floor_number(floor_number):
    return f"{floor_number:02}" if floor_number else None


class LPAGenerator(object):
    def __init__(self, order, *args, data=None, **kwargs):

        if order.order_type != "LPA":
            raise "Order needs to be LPA"
        self.directoryPath = os.path.dirname(os.path.abspath(__file__))
        self.sourcePdf = os.path.join(self.directoryPath, "LPA_Form_1_2020.pdf")
        self.destinationPdf = os.path.join(self.directoryPath, "output.pdf")
        self.encrypteddestinationPdf = os.path.join(
            self.directoryPath, "encryptedOutput.pdf"
        )
        self.read = PdfReader(self.sourcePdf)
        self.stream = ""
        self.order = order

        env = environ.Env(
            # set casting, default value
            DEBUG=(bool, False)
        )
        # reading .env file
        environ.Env.read_env()
        self.stage = settings.STAGE

        data = clean_data(LPAOrderSerializer(order).data, output="VALUE")

        donees = list(
            filter(
                lambda person: "DONEE" in person["entity_roles"], data["people"]
            )
        )

        self.donees = donees

        replacement_donees = list(
            filter(
                lambda person: "REPLACEMENT_DONEE" in person["entity_roles"],
                data["people"],
            )
        )

        self.replacement_donees = replacement_donees

        self.all_field_keys = [
            self.read.Root.AcroForm.Fields[x].T
            for x in range(0, len(self.read.Root.AcroForm.Fields))
        ]

        self.new_schema = {}

        """User Input Functions"""

        user_info_schema = {
            "(Your Full Name as in NRICFINPassport)": data["user_details"].get(
                "name", None
            ),
            "(StreetName)": data["user_details"].get("block_only_address", None),
            "(Your Email Address1)": data["user_details"].get("email", None),
        }

        self.new_schema.update(user_info_schema)

        # user nric input
        user_id_number = data["user_details"].get("id_number", None)
        self.user_id_number = user_id_number
        self.input_sequential_entry(
            "(NRICFINPassport No Delete as appropriate{})", user_id_number, 1, 9
        )

        # date of birth input
        user_date_of_birth = data["user_details"].get("date_of_birth", None)
        if user_date_of_birth:
            parsed_user_date_of_birth = parse(user_date_of_birth).strftime("%d%m%Y")
            self.input_sequential_entry(
                "(Yourdateofbirth{})", parsed_user_date_of_birth, 0, 8
            )

        # user contact number
        user_contact_number = data["user_details"].get("contact_number", None)
        self.input_sequential_entry(
            "(Your Contact No{})", self.parse_contact_number(user_contact_number), 0, 8
        )

        # user contact number
        user_floor_number = clean_floor_number(
            data["user_details"].get("floor_number", None)
        )
        self.input_sequential_entry("(Floor No{})", user_floor_number, 0, 2)

        # user contact number
        if not data["user_details"].get("is_private_housing", None):
            user_unit_number = clean_unit_number(
                data["user_details"].get("unit_number", None)
            )
            self.input_sequential_entry("(Unit No{})", user_unit_number, 0, 4)

        # user postal code
        user_postal_code = data["user_details"].get("postal_code", None)
        self.input_sequential_entry("(Postal Code{})", user_postal_code, 0, 6)

        donee_1 = donees[0]
        donee_2 = donees[1] if len(donees) > 1 else None

        print("""Donee 1 Input Functions""")

        donee_1_personal_details = donee_1["entity_details"]

        donee_1_info_schema = {
            # donee 1 fields
            "(Full Name as in NRICFINPassport1)": donee_1_personal_details.get(
                "name", None
            ),
            "(Relationship to Donor)": donee_1_personal_details.get(
                "relationship", None
            )
            if donee_1_personal_details.get("relationship", None) != "Other"
            else donee_1_personal_details.get("relationship_other", None),
            "(Streetname1)": donee_1_personal_details.get("block_only_address", None),
            "(Email Address2)": donee_1_personal_details.get("email", None),
        }

        self.new_schema.update(donee_1_info_schema)

        # donee 1 nric input
        donee_1_id_number = donee_1_personal_details.get("id_number", None)
        self.input_sequential_entry(
            "(NRICFINPassport No Delete as appropriate_{})", donee_1_id_number, 10, 9
        )

        # date of birth input
        donee_1_date_of_birth = donee_1_personal_details.get("date_of_birth", None)
        if donee_1_date_of_birth:
            parsed_donee_1_date_of_birth = parse(donee_1_date_of_birth).strftime(
                "%d%m%Y"
            )
            self.input_sequential_entry(
                "(Dateofbirth{})", parsed_donee_1_date_of_birth, 8, 8
            )

        # donee 1 contact number
        donee_1_contact_number = donee_1_personal_details.get("contact_number", None)
        self.input_sequential_entry(
            "(Contact No{})", self.parse_contact_number(donee_1_contact_number), 8, 8
        )

        # donee 1 floor number
        donee_1_floor_number = clean_floor_number(
            donee_1_personal_details.get("floor_number", None)
        )
        self.input_sequential_entry("(Floor No_{})", donee_1_floor_number, 2, 2)

        # donee 1 unit number
        if not donee_1_personal_details.get("is_private_housing", None):
            donee_1_unit_number = clean_unit_number(
                donee_1_personal_details.get("unit_number", None)
            )
            self.input_sequential_entry("(Unit No_{})", donee_1_unit_number, 4, 4)

        # donee 1 postal code
        donee_1_postal_code = donee_1_personal_details.get("postal_code", None)
        self.input_sequential_entry("(Postal Code_{})", donee_1_postal_code, 6, 6)

        donee_1_powers = donee_1["donee_powers"].get("powers", None)
        self.input_checkbox_entry(donee_1_powers == "PERSONAL_WELFARE", 1)
        self.input_checkbox_entry(donee_1_powers == "PROPERTY_AND_AFFAIRS", 2)
        self.input_checkbox_entry(donee_1_powers == "BOTH", 3)

        # self.input_checkbox_entry(jointly_severally == "JOINTLY", 15)

        if len(donees) > 1:

            print("""Donee 2 Input Functions""")

            donee_2_personal_details = donee_2["entity_details"]

            donee_2_info_schema = {
                # donee 1 fields
                "(Full Name as in NRICFINPassport_2)": donee_2_personal_details.get(
                    "name", None
                ),
                "(Relationship to Donor_2)": donee_2_personal_details.get(
                    "relationship", None
                )
                if donee_2_personal_details.get("relationship", None) != "Other"
                else donee_2_personal_details.get("relationship_other", None),
                "(Streetname2)": donee_2_personal_details.get(
                    "block_only_address", None
                ),
                "(Email Address_3)": donee_2_personal_details.get("email", None),
            }

            self.new_schema.update(donee_2_info_schema)

            # donee 1 nric input
            donee_2_id_number = donee_2_personal_details.get("id_number", None)
            self.input_sequential_entry(
                "(NRICFINPassport No Delete as appropriate_{})",
                donee_2_id_number,
                19,
                9,
            )

            # date of birth input
            donee_2_date_of_birth = donee_2_personal_details.get("date_of_birth", None)
            if donee_2_date_of_birth:
                parsed_donee_2_date_of_birth = parse(donee_2_date_of_birth).strftime(
                    "%d%m%Y"
                )
                self.input_sequential_entry(
                    "(Dateofbirth{})", parsed_donee_2_date_of_birth, 16, 8
                )

            # donee 1 contact number
            donee_2_contact_number = donee_2_personal_details.get(
                "contact_number", None
            )
            self.input_sequential_entry(
                "(Contact No_{})",
                self.parse_contact_number(donee_2_contact_number),
                16,
                8,
            )

            # donee 1 floor number
            donee_2_floor_number = clean_floor_number(
                donee_2_personal_details.get("floor_number", None)
            )
            self.input_sequential_entry("(Floor No_{})", donee_2_floor_number, 4, 2)

            # donee 1 unit number
            if not donee_2_personal_details.get("is_private_housing", None):
                donee_2_unit_number = clean_unit_number(
                    donee_2_personal_details.get("unit_number", None)
                )
                self.input_sequential_entry("(Unit No_{})", donee_2_unit_number, 8, 4)

            # donee 1 postal code
            donee_2_postal_code = donee_2_personal_details.get("postal_code", None)
            self.input_sequential_entry("(Postal Code_{})", donee_2_postal_code, 12, 6)

            donee_2_powers = donee_2["donee_powers"].get("powers", None)

            self.input_checkbox_entry(donee_2_powers == "PERSONAL_WELFARE", 4)
            self.input_checkbox_entry(donee_2_powers == "PROPERTY_AND_AFFAIRS", 5)
            self.input_checkbox_entry(donee_2_powers == "BOTH", 6)

        if len(replacement_donees) >= 1:

            print("""Replacement Donee Input Functions""")

            replacement_donee = replacement_donees[0]
            replacement_donee_personal_details = replacement_donee["entity_details"]

            replacement_donee_info_schema = {
                # donee 1 fields
                "(Full Name as in NRICFINPassport_3)": replacement_donee_personal_details.get(
                    "name", None
                ),
                "(Relationship to Donor_3)": replacement_donee_personal_details.get(
                    "relationship", None
                )
                if replacement_donee_personal_details.get("relationship", None)
                != "Other"
                else replacement_donee_personal_details.get("relationship_other", None),
                "(Local Mailing Address_4)": replacement_donee_personal_details.get(
                    "block_only_address", None
                ),
                "(Email Address_4)": replacement_donee_personal_details.get(
                    "email", None
                ),
            }

            # replaecement donee fields

            self.new_schema.update(replacement_donee_info_schema)

            # donee 1 nric input
            replacement_donee_id_number = replacement_donee_personal_details.get(
                "id_number", None
            )
            # this could be 28?
            self.input_sequential_entry(
                "(NRICFINPassport No Delete as appropriate_{})",
                replacement_donee_id_number,
                28,
                9,
            )

            # date of birth input
            replacement_donee_date_of_birth = replacement_donee_personal_details.get(
                "date_of_birth", None
            )
            if replacement_donee_date_of_birth:
                parsed_replacement_donee_date_of_birth = parse(
                    replacement_donee_date_of_birth
                ).strftime("%d%m%Y")
                self.input_sequential_entry(
                    "(Dateofbirth{})", parsed_replacement_donee_date_of_birth, 24, 8
                )

            # donee 1 contact number
            replacement_donee_contact_number = replacement_donee_personal_details.get(
                "contact_number", None
            )
            self.input_sequential_entry(
                "(Contact No_{})",
                self.parse_contact_number(replacement_donee_contact_number),
                24,
                8,
            )

            # donee 1 floor number
            replacement_donee_floor_number = clean_floor_number(
                replacement_donee_personal_details.get("floor_number", None)
            )
            self.input_sequential_entry(
                "(Floor No_{})", replacement_donee_floor_number, 6, 2
            )

            # donee 1 unit number
            if not replacement_donee_personal_details.get("is_private_housing", None):
                replacement_donee_unit_number = clean_unit_number(
                    replacement_donee_personal_details.get("unit_number", None)
                )
                self.input_sequential_entry(
                    "(Unit No_{})", replacement_donee_unit_number, 12, 4
                )

            # donee 1 postal code
            replacement_donee_postal_code = replacement_donee_personal_details.get(
                "postal_code", None
            )
            self.input_sequential_entry(
                "(Postal Code_{})", replacement_donee_postal_code, 18, 6
            )

            replacement_donee_powers = replacement_donee["donee_powers"].get(
                "replacement_type", None
            )
            named_main_donee = replacement_donee["donee_powers"].get(
                "named_main_donee", None
            )

            self.input_checkbox_entry(replacement_donee_powers == "ANY", 7)

            self.input_checkbox_entry(replacement_donee_powers == "PERSONAL_WELFARE", 8)

            self.input_checkbox_entry(
                replacement_donee_powers == "PROPERTY_AND_AFFAIRS", 9
            )

            if replacement_donee_powers == "NAMED":
                self.input_checkbox_entry(
                    named_main_donee == donee_1["entity_details"]["id"], 10
                )
                if donee_2:
                    self.input_checkbox_entry(
                        named_main_donee == donee_2["entity_details"]["id"], 11
                    )

        # donee_powers
        if data["available_restrictions"]["personal_welfare_restrictions"]:
            jointly_severally = data["personal_welfare_restrictions"][
                "jointly_severally"
            ]
            self.input_checkbox_entry(jointly_severally == "JOINTLY_AND_SEVERALLY", 14)
            self.input_checkbox_entry(jointly_severally == "JOINTLY", 15)
            power_to_refuse = data["personal_welfare_restrictions"]["power_to_refuse"]
            self.input_checkbox_entry(power_to_refuse == "Yes", 12)
            self.input_checkbox_entry(power_to_refuse == "No", 13)

        if data["available_restrictions"]["property_and_affairs_restrictions"]:
            jointly_severally = data["property_and_affairs_restrictions"][
                "jointly_severally"
            ]
            self.input_checkbox_entry(jointly_severally == "JOINTLY_AND_SEVERALLY", 21)
            self.input_checkbox_entry(jointly_severally == "JOINTLY", 22)

            power_to_give_cash = data["property_and_affairs_restrictions"][
                "power_to_give_cash"
            ]

            self.input_checkbox_entry(power_to_give_cash == "Restricted", 20)
            self.input_checkbox_entry(power_to_give_cash == "Unrestricted", 19)
            self.input_checkbox_entry(power_to_give_cash == "Not_Allowed", 18)

            if power_to_give_cash == "Restricted":
                self.new_schema.update(
                    {
                        # donee 1 fields cash_restriction
                        "(within one calendar year)": data[
                            "property_and_affairs_restrictions"
                        ].get("cash_restriction", None),
                    }
                )

            power_to_sell_property = data["property_and_affairs_restrictions"][
                "power_to_sell_property"
            ]

            self.input_checkbox_entry(power_to_sell_property == "Yes", 16)
            self.input_checkbox_entry(power_to_sell_property == "No", 17)

            restricted_asset_id = data["property_and_affairs_restrictions"].get(
                "restricted_asset", None
            )

            if power_to_sell_property == "No" and restricted_asset_id:
                restricted_asset = next(
                    item for item in data["assets"] if item["id"] == restricted_asset_id
                )

                self.new_schema.update(
                    {
                        # donee 1 fields
                        "(Properadd1)": restricted_asset["asset_details"]["address"],
                        "(Properadd2)": "",
                    }
                )

        """
        Donee 1
        1 - Personal Welfare only (e.g. decide where I should live, handle my letters / mail)
        2 - Property and Affairs only (e.g. buy, sell, rent and mortgage my property, operate bank accounts)
        3 - both Personal Welfare and Property and Affairs
        Donee 2
        4 - Personal Welfare only (e.g. decide where I should live, handle my letters / mail)
        5 - Property and Affairs only (e.g. buy, sell, rent and mortgage my property, operate bank accounts)
        6 - both Personal Welfare and Property and Affairs

        7 - any donee who is unable to act
        8 - any donee with Personal Welfare powers who needs replacing
        9 - any donee with Property and Affairs powers who needs replacing
        10 - Donee 1 only
        11 - Donee 2 only

        Clinical Trials
        12 - Yes
        13 - No

        Personal welfare
        14 - Jointly Severally
        15 - Jointly

        Property and Affairs
        16 - Yes
        17 - No

        Gifts
        18 - No
        19 - Yes
        20 - Yes Limited

        21 - Jointly Severally
        22 - Jointly

        """

    def parse_contact_number(self, contact_number):
        if contact_number:
            return contact_number.split(" ")[1].replace("-", "")

    def input_sequential_entry(
        self, template_key, input_string, start_index, max_index
    ):
        print("---" * 10)
        if input_string != None:
            _input_string = str(input_string)
            real_input = ""
            for i in range(len(_input_string)):
                if i < max_index:
                    index = start_index + i
                    key = self.get_key_from_template(template_key, index, start_index)
                    if i == 0:
                        print(key)
                    self.new_schema[key] = _input_string[i]
                    real_input += _input_string[i]
            print(key)
            print("input_string", _input_string)
            print("real_input", real_input)

    def input_checkbox_entry(self, input, index):
        key = self.get_key_from_template("(Check Box_{})", index, index)
        self.new_schema[key] = input

    def get_key_from_template(self, template_key, index, start_index):
        key = template_key.format(index)
        if key in self.all_field_keys:
            return key

        if start_index == 0 and index == 0:
            if "_{})" in template_key:
                template_key = template_key.replace("_{})", ")")
            elif "{})" in template_key:
                template_key = template_key.replace("{})", ")")
        else:
            if "_{})" in template_key:
                template_key = template_key.replace("_{})", "{})")
            elif "{})" in template_key:
                template_key = template_key.replace("{})", "_{})")

        _key = template_key.format(index)
        if _key not in self.all_field_keys:
            print("---" * 20)
            print(f"SCHEMA KEY ERROR {_key}")
            print("---" * 20)
        else:
            print(f"{_key} ====> {key}")

        return _key

    def get_field_value(self, field_name, index, field_type):

        value = field_name

        if field_type == "checkbox":
            try:
                return self.checkbox_schema[field_name]
            except:
                return False
        if field_type == "textfield":
            try:
                return self.textfield_schema[field_name]
            except:
                return ""
        return True

    # def StrikeSection(self):
    #
    #     doc = fitz.open(self.sourcePdf)
    #     text = "To strike out this"
    #     counter = 0
    #     for page in range(len(self.read.pages)):
    #         doc_page = doc[page]
    #         text_instances = doc_page.searchFor(text)
    #         height = doc[page].getPixmap().height
    #         for inst in text_instances[::-1]:
    #
    #             if counter == 1 and len(self.donees) == 1:
    #                 packet = io.BytesIO()
    #                 can = canvas.Canvas(packet, pagesize=letter)
    #                 can.line(inst.x0 - 40, height - inst.y0 + 40,
    #                          doc[page].getPixmap().width - 30, 100)
    #
    #                 can.save()
    #                 packet.seek(0)
    #                 overlay_pdf = PdfReader(packet)
    #                 overlay_page = overlay_pdf.pages[0]
    #                 PageMerge(self.read.pages[page]).add(overlay_page).render()
    #
    #             if counter == 5 and len(self.donees) == 1:
    #                 packet = io.BytesIO()
    #                 can = canvas.Canvas(packet, pagesize=letter)
    #                 can.line(inst.x0, height - inst.y0 + 30,
    #                          doc[page].getPixmap().width - 30, 540)
    #
    #                 can.save()
    #                 packet.seek(0)
    #                 overlay_pdf = PdfReader(packet)
    #                 overlay_page = overlay_pdf.pages[0]
    #                 PageMerge(self.read.pages[page]).add(overlay_page).render()
    #
    #             if counter == 2 and len(self.replacement_donee) == 0:
    #                 packet = io.BytesIO()
    #                 can = canvas.Canvas(packet, pagesize=letter)
    #                 can.line(inst.x0, height - inst.y0 + 65,
    #                          doc[page].getPixmap().width - 30, 350)
    #
    #                 can.save()
    #                 packet.seek(0)
    #                 overlay_pdf = PdfReader(packet)
    #                 overlay_page = overlay_pdf.pages[0]
    #                 PageMerge(self.read.pages[page]).add(overlay_page).render()
    #
    #             if counter == 4 and len(self.replacement_donee) == 0:
    #                 packet = io.BytesIO()
    #                 can = canvas.Canvas(packet, pagesize=letter)
    #                 can.line(inst.x0, height - inst.y0 + 50,
    #                          doc[page].getPixmap().width - 30, 360)
    #
    #                 can.save()
    #                 packet.seek(0)
    #                 overlay_pdf = PdfReader(packet)
    #                 overlay_page = overlay_pdf.pages[0]
    #                 PageMerge(self.read.pages[page]).add(overlay_page).render()
    #
    #             counter += 1
    #
    # def checkDoneeAndReplacementDonne(self):
    #
    #     doc = fitz.open(self.sourcePdf)
    #     text = "*Only"
    #     counter = 0
    #     for page in range(len(self.read.pages)):
    #         doc_page = doc[page]
    #         text_instances = doc_page.searchFor(text)
    #         height = doc[page].getPixmap().height
    #         for inst in text_instances[::-1]:
    #             y = (inst.y0 + inst.y1) / 2
    #             packet = io.BytesIO()
    #             can = canvas.Canvas(packet, pagesize=letter)
    #             if len(self.donees) == 1:
    #                 can.line(inst.x1 + 10, height - y,
    #                          inst.x1 + 25, height - y)
    #             elif len(self.donees) > 1:
    #                 can.line(inst.x0, height - y, inst.x1, height - y)
    #
    #             can.save()
    #             packet.seek(0)
    #             overlay_pdf = PdfReader(packet)
    #             overlay_page = overlay_pdf.pages[0]
    #             PageMerge(self.read.pages[page]).add(overlay_page).render()
    #
    #             counter += 1

    def get_generated_pdf(self, *args, **kwargs):

        self.encrypt_pdf = kwargs.get("encrypt_pdf", True)

        # doc = fitz.open(self.sourcePdf)
        # text = "Passport"
        # counter = 0
        # for page in range(len(self.read.pages)):
        #     doc_page = doc[page]
        #     text_instances = doc_page.searchFor(text)
        #     height = doc[page].getPixmap().height
        #     for inst in text_instances[::-1]:
        #         id_type = self.id_type_schema['id_type_'+str(counter)]
        #         if id_type!=None:
        #             y = (inst.y0 + inst.y1)/2
        #             packet = io.BytesIO()
        #             can = canvas.Canvas(packet, pagesize=letter)
        #             if id_type == 'Passport':
        #                 can.line(inst.x0-35, height-y, inst.x1-45, height-y)
        #             else:
        #                 can.line(inst.x0, height-y, inst.x1, height-y)
        #             can.save()
        #             packet.seek(0)
        #             overlay_pdf = PdfReader(packet)
        #             overlay_page = overlay_pdf.pages[0]
        #             PageMerge(self.read.pages[page]).add(overlay_page).render()
        #         counter += 1

        # self.checkDoneeAndReplacementDonne()
        # self.StrikeSection()

        # fill form fills
        for x in range(0, len(self.read.Root.AcroForm.Fields)):
            key = self.read.Root.AcroForm.Fields[x].T
            # if '/AS' in self.read.Root.AcroForm.Fields[x]:
            #     value = self.get_field_value(
            #         self.read.Root.AcroForm.Fields[x].T, 0, "checkbox")
            #     self.read.Root.AcroForm.Fields[x].AS = 'Yes' if value else 'off'
            # else:
            if key in self.new_schema:
                value = self.new_schema[key]
                if "/AS" in self.read.Root.AcroForm.Fields[x] and value:
                    self.read.Root.AcroForm.Fields[x].update(PdfDict(AS=PdfName("Yes")))
                else:
                    self.read.Root.AcroForm.Fields[x].V = str(value)
                    self.read.Root.AcroForm.Fields[x].AP = ""
            else:
                print(f"[UNUSED KEYS]: {key}")

            # for debugging
            # if not '/AS' in self.read.Root.AcroForm.Fields[x]:
            #     self.read.Root.AcroForm.Fields[x].V = str(x)
            #     self.read.Root.AcroForm.Fields[x].AP = ""
            #     print(x, key)\

        buf = io.BytesIO()
        pdf = PdfWriter()
        pdf.write(buf, self.read)
        buf.seek(0)
        if self.stage == "LOCAL":
            buf = self.write_to_local(buf)
        buf = self.encrypt(buf)
        return ContentFile(buf.getvalue())

    def encrypt(self, buf):
        newbuf = io.BytesIO()
        output = p.PdfFileWriter()
        input_stream = p.PdfFileReader(buf)

        for i in range(0, input_stream.getNumPages()):
            output.addPage(input_stream.getPage(i))
        if self.encrypt_pdf:
            output.encrypt(self.user_id_number, use_128bit=True)
        output.write(newbuf)
        return newbuf

    def write_to_local(self, buf):
        output = p.PdfFileWriter()
        input_stream = p.PdfFileReader(buf)

        for i in range(0, input_stream.getNumPages()):
            output.addPage(input_stream.getPage(i))

        outputstream = open(self.destinationPdf, "wb")

        output.write(outputstream)
        return open(self.destinationPdf, "rb")
