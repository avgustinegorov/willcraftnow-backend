import json
import random
import string
from io import BytesIO

from django.core.files.base import ContentFile

from core.serializers import *
from persons.serializers import PersonSerializer
from services.pdf_gen.draft_js_mixin import DraftJSMixin
from services.will_generator.will_generator_utils import *

from ..helpers import clean_data
from .schedule import PremiumWillSchedule


class ScheduleObjectGenerator(DraftJSMixin):
    """A Base Class used to generate will PDFs"""

    def __init__(self, order, *args, **kwargs):

        self.order = order

        self.main_counter = 0

        self.user = PersonSerializer(order.user.personal_details,).data

        self.orderDetails = clean_data(
            AssetScheduleOrderSerializer(order, labels=False).data
        )

        self.assetTypes = {}

        self.assetTypes["real_estates"] = [
            self.parse_asset_details(asset)
            for asset in self.orderDetails["assets"]
            if asset["asset_type"] == "RealEstate"
        ]

        self.assetTypes["bank_accounts"] = [
            self.parse_asset_details(asset)
            for asset in self.orderDetails["assets"]
            if asset["asset_type"] == "BankAccount"
        ]

        self.assetTypes["investments"] = [
            self.parse_asset_details(asset)
            for asset in self.orderDetails["assets"]
            if asset["asset_type"] == "Investment"
        ]

        self.assetTypes["insurances"] = [
            self.parse_asset_details(asset)
            for asset in self.orderDetails["assets"]
            if asset["asset_type"] == "Insurance"
        ]

        self.assetTypes["companies"] = [
            self.parse_asset_details(asset)
            for asset in self.orderDetails["assets"]
            if asset["asset_type"] == "Company"
        ]

        self.ScheduleObject = []

    def parse_asset_details(self, asset):
        asset_details = asset.pop("asset_details")
        asset_details.update(asset)
        return asset_details

    def object_wrapper(self, text, depth=0, type="ordered-list-item", underline=False):
        key = "".join(
            random.choice(string.ascii_uppercase + string.digits) for _ in range(5)
        )
        block_object = {
            "data": {},
            "depth": depth,
            "entityRanges": [],
            "inlineStyleRanges": [],
            "key": key,
            "text": text,
            "type": type,
        }

        self.ScheduleObject.append(block_object)

        return block_object

    def AssetHeader(self, assetName):

        if assetName == "real_estates":
            assetHeader = "REAL ESTATE(s)"
        elif assetName == "bank_accounts":
            assetHeader = "BANK ACCOUNT(s)"
        elif assetName == "insurances":
            assetHeader = "INSURANCE POLICIES(s)"
        elif assetName == "investments":
            assetHeader = "INVESTMENT ACCOUNTS(s)"
        elif assetName == "companies":
            assetHeader = "COMPANY ORDINARY SHARES(s)"
        elif assetName == "residual":
            assetHeader = "RESIDUAL"
        else:
            assetHeader = ""

        self.object_wrapper(assetHeader, type="header-four", underline=True)

    def AssetsParagraphs(self):
        for key, value in self.assetTypes.items():
            assetName = key
            assets = value
            self.AssetHeader(assetName)
            for asset in assets:
                if assetName != "residual":
                    self.object_wrapper(
                        AssetDetails(asset, assetName, isPartSentence=True), depth=0
                    )

    def generate_will_schedule(self, string=False, blocksOnly=True):

        self.AssetsParagraphs()

        self.ScheduleObject = self.generate_draftjs_blocks(self.ScheduleObject)

        if blocksOnly:
            ScheduleObject = self.ScheduleObject
        else:
            ScheduleObject = {"blocks": self.ScheduleObject, "entityMap": {}}

        if string:
            return json.dumps(ScheduleObject)
        else:
            return ScheduleObject

    def generate_pdf(self, schedule_object=None, encrypt_pdf=True):
        if not schedule_object:
            schedule_object = self.generate_will_schedule()

        schedule_object = self.generate_html_blocks(schedule_object)

        order_data = {"user": self.user, "order": self.order}
        outf = BytesIO()
        will_schedule = PremiumWillSchedule(**order_data)
        will_schedule.create_will_from_object(schedule_object, outf)
        if encrypt_pdf:
            self.encrypt_pdf(will_schedule)
        will_schedule.build_pdf()
        outf.seek(0)
        return ContentFile(outf.getvalue())

    def encrypt_pdf(self, will_schedule):
        password = self.user["id_number"]
        will_schedule.encrypt_pdf(password)
