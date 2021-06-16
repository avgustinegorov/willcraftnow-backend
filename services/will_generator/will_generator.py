import json
import random
import string
from copy import deepcopy
from io import BytesIO

from django.core.files.base import ContentFile

from core.serializers import WillOrderSerializer
from services.pdf_gen.draft_js_mixin import DraftJSMixin
from services.will_generator.premium_will import PremiumWill
from services.will_generator.will_generator_utils import *

from ..helpers import clean_data


class WillObjectGenerator(DraftJSMixin):
    """A Base Class used to generate will PDFs"""

    def __init__(self, order, *args, **kwargs):

        self.order = order

        self.main_counter = 0

        self.orderDetails = clean_data(
            WillOrderSerializer(order, labels=False).data)

        self.user = self.orderDetails["user_details"]

        self.people = self.orderDetails["people"]

        self.executors = [
            person
            for person in self.people
            if "EXECUTOR" in person["entity_roles"]
        ]

        self.sub_executor = [
            person
            for person in self.people
            if "SUB_EXECUTOR" in person["entity_roles"]
        ]

        self.guardian = [
            person
            for person in self.people
            if "GUARDIAN" in person["entity_roles"]
        ]

        self.lastrites = self.orderDetails["last_rites"]

        self.instructions = self.orderDetails["instructions"]

        self.witnesses = self.orderDetails["witnesses"]

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

        self.assetTypes["residual"] = [
            self.parse_asset_details(asset)
            for asset in self.orderDetails["assets"]
            if asset["asset_type"] == "Residual"
        ]

        self.onlyResidualAsset = True

        self.WillObject = []

        self.defined_persons = []

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

        self.WillObject.append(block_object)

        return block_object

    def definePersons(self, person, ownership=False):

        entity_type = person["entity_type"]
        details = person["entity_details"]

        if entity_type == "Person":
            if details["id_number"] in self.defined_persons:
                result = f'{details["name"].upper()}'
                if ownership:
                    result += "'s"
            else:
                result = (
                    f'{details["name"]} (holder of {details["id_document"]} No.'
                    f' {details["id_number"].upper()}), residing at'
                    f' {details["address"]} ("{details["name"].upper()}")'
                )
                self.defined_persons = self.defined_persons + [
                    details["id_number"],
                ]
        elif entity_type == "Charity":
            if details["id"] in self.defined_persons:
                result = f'{details["name"].upper()}'
                if ownership:
                    result += "'s"
            else:
                result = f'{details["name"]} (UEN No. {details["UEN"].upper()})'
                self.defined_persons = self.defined_persons + [
                    details["id"],
                ]

        return result

    def ExecutorsHeader(self):
        if len(self.executors) == 1:
            result = "EXECUTOR"
        else:
            result = "EXECUTORS"

        self.object_wrapper(result, type="header-four", underline=True)

    def ExecutorPowersHeader(self):
        if len(self.executors) == 1:
            result = "EXECUTOR'S POWERS"
        else:
            result = "EXECUTORS' POWERS"

        self.object_wrapper(result, type="header-four", underline=True)

    def ExecutorsParagraph(self):

        if len(self.executors) == 1:

            result = (
                f"I appoint {self.definePersons(self.executors[0])} to be the sole"
                ' Executor and Trustee of this Will (<b>"Executor"</b>).'
            )

            self.object_wrapper(result)
            self.main_counter += 1

        else:
            result = (
                f"I appoint the following persons as joint Executors and Trustees of"
                f' this Will (each my <b>"Executor"</b> and collectively, my'
                f' <b>"Executors"</b>):'
            )

            self.object_wrapper(result)
            self.main_counter += 1

            for index, executor in enumerate(self.executors):

                result = (
                    f"{self.definePersons(executor)}{SemiColon(index, self.executors, False)}"
                )

                self.object_wrapper(result, depth=1)

    def SubExecutorsParagraph(self):

        assert (len(self.executors) == 1, "Only one sub-executor is allowed")

        for sub_executor in self.sub_executor:

            if len(self.executors) == 1:

                result = (
                    "If for any reason, my Executor is unable or unwilling to act as"
                    " executor and trustee of this Will, I appoint"
                    f" {self.definePersons(sub_executor)} as the sole Executor and"
                    ' Trustee of this Will (<b>"Executor"</b>).'
                )

                self.object_wrapper(result)
                self.main_counter += 1

            else:

                result = (
                    "If for any reason, any one of my Executors is unable or unwilling"
                    " to act as executor and trustee of this Will, I appoint"
                    f" {self.definePersons(sub_executor)} as alternative Executor to"
                    " act jointly with the remaining Executors appointed above (<b>"
                    ' "Executor" </b> and jointly with the Executors named above, <b>'
                    ' "Executors" </b>).'
                )

                self.object_wrapper(result)
                self.main_counter += 1

    def ExecutorPowersParagraph(self):

        result = (
            f'My {renderPlural(self.executors, "Executor")} shall have full powers to'
            " give, sell for cash or upon such terms as"
            f" {heOrSheOrThey(self.executors)} may deem fit, call in and convert into"
            " money, any of my Assets or such part or parts thereof as shall be of a"
            " saleable or convertible nature, at such time or times and in such manner"
            f' as my {renderPlural(self.executors, "Executor")} shall, in'
            f" {hisOrHerOrTheir(self.executors)} absolute and uncontrolled discretion"
            " think fit, with power to postpone such sale, calling in and conversion"
            " of such property, or of such part or parts thereof for such period or"
            f' periods as my {renderPlural(self.executors, "Executor")} in'
            f" {hisOrHerOrTheir(self.executors)} absolute and uncontrolled discretion"
            " think fit, and to the extent necessary, have full powers to pay all my"
            " liabilities, debts, mortgages, funeral and testamentary expenses, and"
            " any taxes payable by reason of my death from my Estate"
            ' (<b>"Expenses"</b>).'
        )

        self.object_wrapper(result)
        self.main_counter += 1

        result = (
            f"The powers of my {renderPlural(self.executors, 'Executor')} named herein"
            " shall be in addition and in modification of the Executor's powers under"
            " the Trustees Act (Cap. 337) of Singapore, any re-enactment thereof and"
            " general terms of the laws of Singapore. For the avoidance of doubt, part"
            " IVA and IVB of the Trustees Act (Cap. 337) shall apply."
        )

        self.object_wrapper(result)
        self.main_counter += 1

    def StartingParagraph(self):

        result = (
            "<b>THIS IS THE LAST WILL AND TESTAMENT</b> of me,"
            f' {self.definePersons({"entity_details": self.user, "entity_type": "Person"})}'
            " in respect of all my assets situated in the Republic of Singapore at the"
            ' time of my death (<b>"Assets"</b>).'
        )

        self.object_wrapper(result)
        self.main_counter += 1

    def RevocationParagraph(self):

        result = (
            f"I hereby revoke all former wills and testamentary dispositions made by"
            f' me, and declare this to be my last will and testament (<b>"Will"</b>)'
            f" and that this Will and any codicil to it shall be construed and take"
            f" effect in accordance with the laws of the Republic of Singapore."
        )

        self.object_wrapper(result)
        self.main_counter += 1

    def GuardianParagraph(self):

        assert (len(self.guardian) == 1, "Only one guardian is allowed")

        for guardian in self.guardian:

            result = (
                f"It is my wish that {self.definePersons(guardian)} be appointed as"
                " guardian of my child/children"
            )

            if self.user["relationship_status"] == "Married":
                result += (
                    ", as the case may be jointly with my spouse, or solely if my"
                    " spouse is not able to act by reason of death or incapacity."
                )
            else:
                result += "."

            self.object_wrapper(result)
            self.main_counter += 1

    def InstructionsParagraph(self):

        if self.instructions and self.instructions["instructions"]:
            result = ""
            if (
                self.instructions["instructions"] == "Scattered in the Sea"
                or self.instructions["instructions"] == "SCATTERED"
            ):
                result = (
                    "It is my wish to be cremated and my ashes to be scattered at sea."
                )
            elif (
                self.instructions["instructions"] == "Held at a crematorium"
                or self.instructions["instructions"] == "CREMATED"
            ):
                result = (
                    "It is my wish to be cremated and my ashes to be kept at the"
                    f" crematorium at {self.instructions['crematorium_location']}."
                )
            elif (
                self.instructions["instructions"] == "Buried in Singapore"
                or self.instructions["instructions"] == "BURIED"
            ):
                result = "It is my wish to be buried in Singapore."

            if result:
                self.object_wrapper(result)
                self.main_counter += 1

    def LastRitesParagraph(self):

        if self.lastrites and all(self.lastrites[key] for key in self.lastrites):

            duration_unit = "days"

            if int(self.lastrites["funeral_duration"]) == 1:
                duration_unit = "day"

            result = (
                f"It is my wish that a {self.lastrites['funeral_religion'].lower()}"
                f" funeral be held at {self.lastrites['funeral_location']} for"
                f" {self.lastrites['funeral_duration']} {duration_unit}."
            )

            self.object_wrapper(result)
            self.main_counter += 1

    def AssetHeader(self, assetName):

        if assetName == "real_estates":
            assetHeader = "REAL ESTATE ALLOCATIONS"
        elif assetName == "bank_accounts":
            assetHeader = "BANK ACCOUNT ALLOCATIONS"
        elif assetName == "insurances":
            assetHeader = "INSURANCE ALLOCATIONS"
        elif assetName == "investments":
            assetHeader = "INVESTMENT ALLOCATIONS"
        elif assetName == "companies":
            assetHeader = "COMPANY SHARES ALLOCATIONS"
        elif assetName == "residual":
            assetHeader = "RESIDUAL ALLOCATIONS"
        else:  # pragma: no cover
            assetHeader = ""  # pragma: no cover

        self.object_wrapper(assetHeader, type="header-four", underline=True)

    def AssetsParagraphs(self):
        for key, value in self.assetTypes.items():
            assetName = key
            assets = value
            for asset in assets:
                if asset["entities"]:
                    self.AssetHeader(assetName)
                    break
            for asset in assets:
                if len(asset["entities"]) > 0:
                    if assetName == "bank_accounts":
                        _asset = deepcopy(asset)
                        for index, allocation in reversed(
                            list(enumerate(_asset["entities"]))
                        ):
                            if allocation["allocation_amount"] == None:
                                _asset["entities"].pop(index)
                        startRef = self.main_counter
                        self.BeneficiaryParagraph(
                            _asset, assetName, distributionType="Cash"
                        )
                        endRef = self.main_counter
                        _asset = deepcopy(asset)
                        for index, allocation in reversed(
                            list(enumerate(_asset["entities"]))
                        ):
                            if allocation["allocation_percentage"] == None:
                                _asset["entities"].pop(index)
                        self.BeneficiaryParagraph(
                            _asset,
                            assetName,
                            # subjectTo=[startRef + 1,
                            #            endRef] if startRef != endRef else None,
                            subjectTo=[startRef + 1, endRef]
                            if startRef != endRef
                            else None,
                            distributionType="Percentage",
                        )
                    elif assetName != "residual":
                        self.BeneficiaryParagraph(asset, assetName)
                    else:
                        self.ResidualBeneficiaryParagraph(asset, assetName)

                if assetName != "residual" and len(asset["entities"]) > 0:
                    self.onlyResidualAsset = False

    def BeneficiaryParagraph(
        self, asset, assetName, subjectTo=None, distributionType=None
    ):

        if len(asset["entities"]) == 1:

            beneficiary = asset["entities"][0]
            result = (
                f"{SubjectToExpensesAndClauses(subjectTo)}, I give"
                f" {PercentageOrAmountOfInterestOrBenefitIn(asset, assetName)}, to"
                f" {self.definePersons(beneficiary)} absolutely and free from all"
                f" encumbrances{ResidualStatement(asset, distributionType)}"
            )

            self.object_wrapper(result)
            self.main_counter += 1

            if beneficiary["entity_type"] == "Person":
                self.SubBeneficiaryParagraph(asset, beneficiary, assetName)

        elif len(asset["entities"]) > 1:

            result = (
                f"{SubjectToExpensesAndClauses(subjectTo)}, I give"
                f" {PercentageOrAmountOfInterestOrBenefitIn(asset, assetName)}, to the"
                " following persons in the corresponding proportions:"
            )

            self.object_wrapper(result)
            self.main_counter += 1

            hasResidual = (
                int(asset["total_allocation"]) < 100
                if distributionType != "Cash"
                else None
            )

            for index, beneficiary in enumerate(asset["entities"]):

                result = (
                    f"{PercentageOrAmount(asset, beneficiary)} to"
                    f" {self.definePersons(beneficiary)} absolutely and free from all"
                    f" encumbrances{DefineMainSubstitute(index, asset['entities'], self.main_counter)}{SemiColon(index, asset['entities'], hasResidual)}"
                )

                self.object_wrapper(result, depth=1)

            if hasResidual and distributionType != "Cash":
                result = (
                    f"the remainder shall be distributed as part of my Residual Assets."
                )
                self.object_wrapper(result, depth=1)

            for index, beneficiary in enumerate(asset["entities"]):
                if beneficiary["entity_type"] == "Person":
                    self.SubBeneficiaryParagraph(asset, beneficiary, assetName)

    def SubBeneficiaryParagraph(self, asset, beneficiary, assetName):

        hasResidual = (
            int(beneficiary["total_sub_allocations"]) < 100
            if beneficiary["allocation_percentage"]
            else None
        )

        if len(beneficiary["sub_entities"]) == 0:

            result = (
                f"If {self.definePersons(beneficiary)} should die during my lifetime,"
                " or fail to survive me for more than thirty (30) days, then the"
                f" {interestOrBenefits(asset, assetName, beneficiary)} in"
                f" {AssetLabel(asset, assetName)} which"
                f" {self.definePersons(beneficiary)} would otherwise have received"
                " under this Will shall be distributed equally amongst"
                f" {self.definePersons(beneficiary, ownership=True)} surviving issues"
                " absolutely and free from all encumbrances so long as they survive me"
                " for more than thirty (30) days"
            )

            if len(asset["entities"]) != 1:
                result += (
                    f", and if {self.definePersons(beneficiary)} does not have any"
                    " issues who have survived me for more than thirty (30) days, then"
                    " the same shall be distributed equally amongst all the Main"
                    " Substitutes who have survived me for more than thirty (30) days."
                )
            else:
                result += "."

            self.object_wrapper(result)
            self.main_counter += 1

        elif len(beneficiary["sub_entities"]) == 1:

            sub_beneficiary = beneficiary["sub_entities"][0]

            result = (
                f"If {self.definePersons(beneficiary)} should die during my lifetime,"
                " or fail to survive me for more than thirty (30) days, I give"
                f" {PercentageOrAmount(asset, sub_beneficiary)} of the"
                f" {interestOrBenefits(asset, assetName, beneficiary)} in"
                f" {AssetLabel(asset, assetName)} which"
                f" {self.definePersons(beneficiary)} would otherwise have received"
                " under this Will"
                f" {EffectivePercentageOrAmount(asset, assetName, sub_beneficiary)} to"
                f" {self.definePersons(sub_beneficiary)} absolutely and free from all"
                " encumbrances, provided always that if"
                f" {self.definePersons(sub_beneficiary)} should die during my lifetime,"
                " or fail to survive me for more than thirty (30) days, then the same"
                " shall be distributed equally amongst"
                f" {self.definePersons(sub_beneficiary, ownership=True)} surviving"
                " issues absolutely and free from all encumbrances so long as they"
                " survive me for more than thirty (30) days"
            )

            if len(asset["entities"]) != 1 and has_other_main_substitutes(
                asset, beneficiary, sub_beneficiary
            ):
                result += (
                    f", and if {self.definePersons(sub_beneficiary)} does not have any"
                    " issues who have survived me for more than thirty (30) days, then"
                    " the same shall be distributed equally amongst all the Main"
                    " Substitutes who have survived me for more than thirty (30) days"
                )

            if hasResidual:
                result += (
                    f", and the remainder shall be distributed as part of my Residual"
                    f" Assets"
                )

            result += "."

            self.object_wrapper(result)
            self.main_counter += 1

        else:

            result = (
                f"If {self.definePersons(beneficiary)} should die during my lifetime,"
                " or fail to survive me for more than thirty (30) days, I give the"
                f" {interestOrBenefits(asset, assetName, beneficiary)} in"
                f" {AssetLabel(asset, assetName)} which"
                f" {self.definePersons(beneficiary)} would otherwise have received"
                " under this Will, to the following persons in the corresponding"
                " proportions:"
            )

            self.object_wrapper(result)
            self.main_counter += 1

            for index, sub_beneficiary in enumerate(beneficiary["sub_entities"]):

                temp_result = (
                    f"{PercentageOrAmount(asset, sub_beneficiary)}"
                    f" {EffectivePercentageOrAmount(asset, assetName, sub_beneficiary)}"
                    f" to {self.definePersons(sub_beneficiary)} absolutely and free"
                    " from all"
                    f" encumbrances{DefineApplicableSubstitute(index, beneficiary['sub_entities'])}{SemiColon(index, beneficiary['sub_entities'], hasResidual)}"
                )

                self.object_wrapper(temp_result, depth=1)

            if hasResidual:
                temp_result = (
                    f"the remainder shall be distributed as part of my Residual Assets."
                )
                self.object_wrapper(temp_result, depth=1)

            temp_result = (
                "Provided Always that if any of the Applicable Substitutes, should die"
                " during my lifetime, or fail to survive me for more than thirty (30)"
                " days, then any gift devise or bequest of my"
                f" {interestOrBenefits(asset, assetName, beneficiary)} in"
                f" {AssetLabel(asset, assetName)} which that Applicable Substitute"
                " would otherwise have received under this Will shall be distributed"
                " equally amongst the issues of that Applicable Substitute so long as"
                " they survive me for more than thirty (30) days, and if that"
                " Applicable Substitute does not have any issues who have survived me"
                " for more than thirty (30) days, then the same shall be distributed"
                " equally amongst all the Applicable Substitutes who have survived me"
                " for more than thirty (30) days."
            )

            # result += ParagraphWrapperNoBullet(temp_result, context)

            self.object_wrapper(temp_result, depth=2)

    def ResidualBeneficiaryParagraph(self, asset, assetName):

        clausesAbove = (
            " not distributed in the clauses above "
            if not self.onlyResidualAsset
            else " "
        )

        if len(asset["entities"]) == 1:

            beneficiary = asset["entities"][0]
            result = (
                f"I give all my Assets{clausesAbove}{AssetDefinition(asset, assetName)}"
                f" to {self.definePersons(beneficiary)} absolutely and free from all"
                " encumbrances."
            )

            self.object_wrapper(result)
            self.main_counter += 1

            if beneficiary["entity_type"] == "Person":
                self.ResidualSubBeneficiaryParagraph(
                    asset, beneficiary, assetName)

        elif len(asset["entities"]) > 1:
            result = (
                f"I give all my Assets{clausesAbove}{AssetDefinition(asset, assetName)}"
                " to the following persons in the corresponding proportions:"
            )

            self.object_wrapper(result)
            self.main_counter += 1

            for index, beneficiary in enumerate(asset["entities"]):

                result = (
                    f"{PercentageOrAmount(asset, beneficiary)} to"
                    f" {self.definePersons(beneficiary)} absolutely and free from all"
                    f" encumbrances{DefineMainSubstitute(index, asset['entities'], self.main_counter)}{SemiColon(index, asset['entities'], False)}"
                )

                self.object_wrapper(result, depth=1)

            for index, beneficiary in enumerate(asset["entities"]):
                if beneficiary["entity_type"] == "Person":
                    self.ResidualSubBeneficiaryParagraph(
                        asset, beneficiary, assetName)

    def ResidualSubBeneficiaryParagraph(self, asset, beneficiary, assetName):

        if len(beneficiary["sub_entities"]) == 0:

            result = (
                f"If {self.definePersons(beneficiary)} should die during my lifetime,"
                " or fail to survive me for more than thirty (30) days, then the"
                f" proportion of my {AssetLabel(asset, assetName)} which"
                f" {heOrShe(beneficiary)} would otherwise have received under this Will"
                f" shall be distributed equally amongst {hisOrHer(beneficiary)}"
                " surviving issues absolutely and free from all encumbrances so long"
                " as they survive me for more than thirty (30) days"
            )

            if len(asset["entities"]) != 1:
                result += (
                    f", and if {self.definePersons(beneficiary)} does not have any"
                    " issues who have survived me for more than thirty (30) days, then"
                    " the same shall be distributed equally amongst all the Main"
                    " Substitutes who have survived me for more than thirty (30) days."
                )
            else:
                result += "."

            self.object_wrapper(result)
            self.main_counter += 1

        elif len(beneficiary["sub_entities"]) == 1:

            sub_beneficiary = beneficiary["sub_entities"][0]

            result = (
                f"If {self.definePersons(beneficiary)} should die during my lifetime,"
                " or fail to survive me for more than thirty (30) days, I give"
                f" {PercentageOrAmount(asset, sub_beneficiary)}"
                f" {EffectivePercentageOrAmount(asset, assetName, sub_beneficiary)} of"
                f" the {AssetLabel(asset, assetName)} which {heOrShe(beneficiary)}"
                " would otherwise have received under this Will to"
                f" {self.definePersons(sub_beneficiary)} absolutely and free from all"
                " encumbrances, provided always that if"
                f" {self.definePersons(sub_beneficiary)} should die during my lifetime,"
                " or fail to survive me for more than thirty (30) days, then the same"
                f" shall be distributed equally amongst {hisOrHer(beneficiary)}"
                " surviving issues absolutely and free from all encumbrances so long"
                " as they survive me for more than thirty (30) days"
            )

            if len(asset["entities"]) != 1:
                result += (
                    f", and if {self.definePersons(sub_beneficiary)} does not have any"
                    " issues who have survived me for more than thirty (30) days, then"
                    " the same shall be distributed equally amongst all the Main"
                    " Substitutes who have survived me for more than thirty (30) days."
                )
            else:
                result += "."

            self.object_wrapper(result)
            self.main_counter += 1

        else:

            result = (
                f"If {self.definePersons(beneficiary)} should die during my lifetime,"
                " or fail to survive me for more than thirty (30) days, I give the"
                f" {interestOrBenefits(asset, assetName, beneficiary)} in"
                f" {AssetLabel(asset, assetName)} which {heOrShe(beneficiary)} would"
                " otherwise have received under this Will, to the following persons in"
                " the corresponding proportions:"
            )

            self.object_wrapper(result)
            self.main_counter += 1

            for index, sub_beneficiary in enumerate(beneficiary["sub_entities"]):

                hasResidual = int(beneficiary["total_sub_allocations"]) < 100

                temp_result = (
                    f"{PercentageOrAmount(asset, sub_beneficiary)}"
                    f" {EffectivePercentageOrAmount(asset, assetName, sub_beneficiary)}"
                    f" to {self.definePersons(sub_beneficiary)} absolutely and free"
                    " from all"
                    f" encumbrances{DefineApplicableSubstitute(index, beneficiary['sub_entities'])}{SemiColon(index, beneficiary['sub_entities'], hasResidual)}"
                )

                self.object_wrapper(temp_result, depth=1)

            temp_result = (
                "Provided Always that if any of the Applicable Substitutes, should die"
                " during my lifetime, or fail to survive me for more than thirty (30)"
                f" days, the proportion of my {AssetLabel(asset, assetName)} which that"
                " Applicable Substitute would otherwise have received under this Will"
                " shall be distributed equally amongst the issues of that Applicable"
                " Substitute so long as they survive me for more than thirty (30)"
                " days, and if that Applicable Substitute does not have any issues who"
                " have survived me for more than thirty (30) days, then the same shall"
                " be distributed equally amongst all the Applicable Substitutes who"
                " have survived me for more than thirty (30) days."
            )

            # result += ParagraphWrapperNoBullet(temp_result, context)
            self.object_wrapper(temp_result, depth=2)

    def generate_will_object(self, string=False, blocksOnly=True):

        self.StartingParagraph()
        self.RevocationParagraph()
        self.ExecutorsHeader()
        self.ExecutorsParagraph()
        self.SubExecutorsParagraph()
        self.ExecutorPowersHeader()
        self.ExecutorPowersParagraph()
        self.AssetsParagraphs()
        self.GuardianParagraph()
        self.InstructionsParagraph()
        self.LastRitesParagraph()

        self.WillObject = self.generate_draftjs_blocks(self.WillObject)

        if blocksOnly:
            WillObject = self.WillObject
        else:
            WillObject = {"blocks": self.WillObject, "entityMap": {}}

        if string:
            return json.dumps(WillObject)
        else:
            return WillObject

    def generate_pdf(self, will_object=None, encrypt_pdf=True):
        if not will_object:
            will_object = self.generate_will_object()

        will_object = self.generate_html_blocks(will_object)

        order_data = {"user": self.user, "witnesses": self.witnesses}
        outf = BytesIO()
        premium_will = PremiumWill(order=self.order, **order_data)
        premium_will.create_will_from_object(will_object, outf)
        if encrypt_pdf:
            self.encrypt_pdf(premium_will)
        premium_will.build_pdf()
        outf.seek(0)
        content_file = ContentFile(outf.getvalue())
        return content_file

    def encrypt_pdf(self, premium_will):
        password = self.user["id_number"]
        premium_will.encrypt_pdf(password)
