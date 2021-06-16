import io
import os

import PyPDF2 as p
from dateutil.parser import parse
from pdfrw import PageMerge, PdfDict, PdfName, PdfReader, PdfWriter

from ..base_pdfrw import BasePDFRWGenerator
from .utils import Utils


class LPAGenerator(BasePDFRWGenerator, Utils):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.directory_path = os.path.dirname(os.path.abspath(__file__))
        self.source_pdf = os.path.join(
            self.directory_path, "LPA_Form_1_2020.pdf")

        self.read = PdfReader(self.source_pdf)
        self.all_field_keys = [
            self.read.Root.AcroForm.Fields[x].T
            for x in range(0, len(self.read.Root.AcroForm.Fields))
        ]

        self.new_schema = {}

    def clean(self):
        super().clean()
        self.donees = self.clean_data['donees']
        self.replacement_donees = self.clean_data['replacement_donees']
        self.available_restrictions = self.clean_data["available_restrictions"]
        self.personal_welfare_restrictions = self.clean_data["personal_welfare_restrictions"]
        self.property_and_affairs_restrictions = self.clean_data["property_and_affairs_restrictions"]

        print(self.available_restrictions)

    def generate(self, *args, **kwargs):
        """User Input Functions"""

        user_info_schema = {
            "(Your Full Name as in NRICFINPassport)": self.user.get(
                "name", None
            ),
            "(StreetName)": self.user.get("block_only_address", None),
            "(Your Email Address1)": self.user.get("email", None),
        }

        self.new_schema.update(user_info_schema)

        # user nric input
        user_id_number = self.user.get("id_number", None)
        self.user_id_number = user_id_number
        self.input_sequential_entry(
            "(NRICFINPassport No Delete as appropriate{})", user_id_number, 1, 9
        )

        # date of birth input
        user_date_of_birth = self.user.get("date_of_birth", None)
        if user_date_of_birth:
            parsed_user_date_of_birth = parse(
                user_date_of_birth).strftime("%d%m%Y")
            self.input_sequential_entry(
                "(Yourdateofbirth{})", parsed_user_date_of_birth, 0, 8
            )

        # user contact number
        user_contact_number = self.user.get("contact_number", None)
        self.input_sequential_entry(
            "(Your Contact No{})", self.clean_contact_number(
                user_contact_number), 0, 8
        )

        # user contact number
        user_floor_number = self.clean_floor_number(
            self.user.get("floor_number", None)
        )
        self.input_sequential_entry("(Floor No{})", user_floor_number, 0, 2)

        # user contact number
        if not self.user.get("is_private_housing", None):
            user_unit_number = self.clean_unit_number(
                self.user.get("unit_number", None)
            )
            self.input_sequential_entry("(Unit No{})", user_unit_number, 0, 4)

        # user postal code
        user_postal_code = self.user.get("postal_code", None)
        self.input_sequential_entry("(Postal Code{})", user_postal_code, 0, 6)

        donee_1 = self.donees[0]
        donee_2 = self.donees[1] if len(self.donees) > 1 else None

        print("""Donee 1 Input Functions""")

        donee_1_personal_details = donee_1["details"]

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
        donee_1_date_of_birth = donee_1_personal_details.get(
            "date_of_birth", None)
        if donee_1_date_of_birth:
            parsed_donee_1_date_of_birth = parse(donee_1_date_of_birth).strftime(
                "%d%m%Y"
            )
            self.input_sequential_entry(
                "(Dateofbirth{})", parsed_donee_1_date_of_birth, 8, 8
            )

        # donee 1 contact number
        donee_1_contact_number = donee_1_personal_details.get(
            "contact_number", None)
        self.input_sequential_entry(
            "(Contact No{})", self.clean_contact_number(
                donee_1_contact_number), 8, 8
        )

        # donee 1 floor number
        donee_1_floor_number = self.clean_floor_number(
            donee_1_personal_details.get("floor_number", None)
        )
        self.input_sequential_entry(
            "(Floor No_{})", donee_1_floor_number, 2, 2)

        # donee 1 unit number
        if not donee_1_personal_details.get("is_private_housing", None):
            donee_1_unit_number = self.clean_unit_number(
                donee_1_personal_details.get("unit_number", None)
            )
            self.input_sequential_entry(
                "(Unit No_{})", donee_1_unit_number, 4, 4)

        # donee 1 postal code
        donee_1_postal_code = donee_1_personal_details.get("postal_code", None)
        self.input_sequential_entry(
            "(Postal Code_{})", donee_1_postal_code, 6, 6)

        donee_1_powers = donee_1["donee_powers"].get("powers", None)
        self.input_checkbox_entry(donee_1_powers == "PERSONAL_WELFARE", 1)
        self.input_checkbox_entry(donee_1_powers == "PROPERTY_AND_AFFAIRS", 2)
        self.input_checkbox_entry(donee_1_powers == "BOTH", 3)

        # self.input_checkbox_entry(jointly_severally == "JOINTLY", 15)

        if len(self.donees) > 1:

            print("""Donee 2 Input Functions""")

            donee_2_personal_details = donee_2["details"]

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
            donee_2_date_of_birth = donee_2_personal_details.get(
                "date_of_birth", None)
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
                self.clean_contact_number(donee_2_contact_number),
                16,
                8,
            )

            # donee 1 floor number
            donee_2_floor_number = self.clean_floor_number(
                donee_2_personal_details.get("floor_number", None)
            )
            self.input_sequential_entry(
                "(Floor No_{})", donee_2_floor_number, 4, 2)

            # donee 1 unit number
            if not donee_2_personal_details.get("is_private_housing", None):
                donee_2_unit_number = self.clean_unit_number(
                    donee_2_personal_details.get("unit_number", None)
                )
                self.input_sequential_entry(
                    "(Unit No_{})", donee_2_unit_number, 8, 4)

            # donee 1 postal code
            donee_2_postal_code = donee_2_personal_details.get(
                "postal_code", None)
            self.input_sequential_entry(
                "(Postal Code_{})", donee_2_postal_code, 12, 6)

            donee_2_powers = donee_2["donee_powers"].get("powers", None)

            self.input_checkbox_entry(donee_2_powers == "PERSONAL_WELFARE", 4)
            self.input_checkbox_entry(
                donee_2_powers == "PROPERTY_AND_AFFAIRS", 5)
            self.input_checkbox_entry(donee_2_powers == "BOTH", 6)

        if len(self.replacement_donees) >= 1:

            print("""Replacement Donee Input Functions""")

            replacement_donee = self.replacement_donees[0]
            replacement_donee_personal_details = replacement_donee["details"]

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
                self.clean_contact_number(replacement_donee_contact_number),
                24,
                8,
            )

            # donee 1 floor number
            replacement_donee_floor_number = self.clean_floor_number(
                replacement_donee_personal_details.get("floor_number", None)
            )
            self.input_sequential_entry(
                "(Floor No_{})", replacement_donee_floor_number, 6, 2
            )

            # donee 1 unit number
            if not replacement_donee_personal_details.get("is_private_housing", None):
                replacement_donee_unit_number = self.clean_unit_number(
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

            self.input_checkbox_entry(
                replacement_donee_powers == "PERSONAL_WELFARE", 8)

            self.input_checkbox_entry(
                replacement_donee_powers == "PROPERTY_AND_AFFAIRS", 9
            )

            if replacement_donee_powers == "NAMED":
                self.input_checkbox_entry(
                    named_main_donee == donee_1["id"], 10
                )
                if donee_2:
                    self.input_checkbox_entry(
                        named_main_donee == donee_2["id"], 11
                    )

        # donee_powers
        if self.available_restrictions["personal_welfare_restrictions"]:
            jointly_severally = self.personal_welfare_restrictions[
                "jointly_severally"
            ]
            self.input_checkbox_entry(
                jointly_severally == "JOINTLY_AND_SEVERALLY", 14)
            self.input_checkbox_entry(jointly_severally == "JOINTLY", 15)
            power_to_refuse = self.personal_welfare_restrictions["power_to_refuse"]
            self.input_checkbox_entry(power_to_refuse == "Yes", 12)
            self.input_checkbox_entry(power_to_refuse == "No", 13)

        if self.available_restrictions["property_and_affairs_restrictions"]:
            jointly_severally = self.property_and_affairs_restrictions[
                "jointly_severally"
            ]
            self.input_checkbox_entry(
                jointly_severally == "JOINTLY_AND_SEVERALLY", 21)
            self.input_checkbox_entry(jointly_severally == "JOINTLY", 22)

            power_to_give_cash = self.property_and_affairs_restrictions[
                "power_to_give_cash"
            ]

            self.input_checkbox_entry(power_to_give_cash == "Restricted", 20)
            self.input_checkbox_entry(power_to_give_cash == "Unrestricted", 19)
            self.input_checkbox_entry(power_to_give_cash == "Not_Allowed", 18)

            if power_to_give_cash == "Restricted":
                self.new_schema.update(
                    {
                        # donee 1 fields cash_restriction
                        "(within one calendar year)": self.property_and_affairs_restrictions.get("cash_restriction", None),
                    }
                )

            power_to_sell_property = self.property_and_affairs_restrictions[
                "power_to_sell_property"
            ]

            self.input_checkbox_entry(power_to_sell_property == "Yes", 16)
            self.input_checkbox_entry(power_to_sell_property == "No", 17)

            restricted_asset_id = self.property_and_affairs_restrictions.get(
                "restricted_asset", None
            )

            if power_to_sell_property == "No" and restricted_asset_id:
                restricted_asset = next(
                    item for item in self.assets if item["id"] == restricted_asset_id
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
                    self.read.Root.AcroForm.Fields[x].update(
                        PdfDict(AS=PdfName("Yes")))
                else:
                    self.read.Root.AcroForm.Fields[x].V = str(value)
                    self.read.Root.AcroForm.Fields[x].AP = ""
            else:
                print(f"[UNUSED KEYS]: {key}")
