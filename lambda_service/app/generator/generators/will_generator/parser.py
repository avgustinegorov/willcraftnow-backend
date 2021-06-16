import json
import random
import string
from copy import deepcopy
from io import BytesIO

import string

from html.parser import HTMLParser
import html

from draftjs_exporter.html import HTML
from draftjs_exporter.dom import DOM
from draftjs_exporter.wrapper_state import WrapperState
from .parser_utils import ParserUtils
from ..base_parser import BaseParser
from ..mark_safe import mark_safe


class DraftToHtmlBlocks(HTML):
    def render(self, block):
        """
        Starts the export process on a given piece of content state.
        """

        wrapper_state = WrapperState(self.block_options, [block])
        entity_map = {}

        return self.render_block(block, entity_map, wrapper_state)


class MyHTMLParser(HTMLParser):
    def __init__(self, block, *args, **kwargs):
        self.block = block
        self.parsed_data = []
        self.styles = []
        self.reconstructed_text = ""
        self.current_position = 0
        self.tag_type = {"b": "BOLD", "em": "ITALIC", "u": "UNDERLINE"}
        super().__init__()

    def feed(self, block):

        super().feed(block["text"])
        block["text"] = mark_safe(self.reconstructed_text)
        block["inlineStyleRanges"] = self.styles
        return block

    def handle_starttag(self, tag, attrs):
        self.styles.append(
            {
                "style": self.tag_type[tag],
                "offset": self.current_position,
                "length": None,
            }
        )

    def handle_endtag(self, tag):
        for style in self.styles:
            if style["style"] == self.tag_type[tag] and style["length"] == None:
                style["length"] = self.current_position - style["offset"]

    def handle_data(self, data):
        self.reconstructed_text += data
        self.current_position += len(data)


class DraftJSMixin:
    def generate_draftjs_blocks(self, will_object):
        new_will_object = []
        for block in will_object:
            parser = MyHTMLParser(block)
            updated_block = parser.feed(block)
            new_will_object.append(updated_block)
        return new_will_object

    def generate_html_blocks(self, blocks):
        updated_blocks = []

        for block in blocks:
            rendered_block = DraftToHtmlBlocks().render(block)
            text = html.unescape(DOM.render(rendered_block))
            block["text"] = text
            updated_blocks.append(block)

        return updated_blocks

        return DraftToHtmlBlocks().render(blocks)


class WillParser(BaseParser, DraftJSMixin, ParserUtils):
    """A Base Class used to generate will PDFs"""

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.main_counter = 0

        self.data = self.clean_data(self.data)

        self.people = self.data["persons"]

        self.executors = [
            self.get_entity_details(person)
            for person in self.people
            if "EXECUTOR" in person["entity_roles"]
        ]

        self.sub_executor = [
            self.get_entity_details(person)
            for person in self.people
            if "SUB_EXECUTOR" in person["entity_roles"]
        ]

        self.guardian = [
            self.get_entity_details(person)
            for person in self.people
            if "GUARDIAN" in person["entity_roles"]
        ]

        self.lastrites = self.data["last_rites"]

        self.instructions = self.data["instructions"]

        self.witnesses = [
            self.get_entity_details(person)
            for person in self.people
            if "WITNESS" in person["entity_roles"]
        ]

        self.allocations = self.get_allocation_categories(
            self.reduce_allocations(self.data['allocations']))

        self.onlyResidualAsset = len(self.allocations) == 1 and self.allocations.keys()[
            0] == 'Residual'

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

        if entity_type == "Person":
            if person["id_number"] in self.defined_persons:
                result = f'{person["name"].upper()}'
                if ownership:
                    result += "'s"
            else:
                result = (
                    f'{person["name"]} (holder of {person["id_document"]} No.'
                    f' {person["id_number"].upper()}), residing at'
                    f' {person["address"]} ("{person["name"].upper()}")'
                )
                self.defined_persons = self.defined_persons + [
                    person["id_number"],
                ]
        elif entity_type == "Charity":
            if person["id"] in self.defined_persons:
                result = f'{person["name"].upper()}'
                if ownership:
                    result += "'s"
            else:
                result = f'{person["name"]} (UEN No. {person["UEN"].upper()})'
                self.defined_persons = self.defined_persons + [
                    person["id"],
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
                    f"{self.definePersons(executor)}{self.SemiColon(index, self.executors, False)}"
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
            f'My {self.renderPlural(self.executors, "Executor")} shall have full powers to'
            " give, sell for cash or upon such terms as"
            f" {self.heOrSheOrThey(self.executors)} may deem fit, call in and convert into"
            " money, any of my Assets or such part or parts thereof as shall be of a"
            " saleable or convertible nature, at such time or times and in such manner"
            f' as my {self.renderPlural(self.executors, "Executor")} shall, in'
            f" {self.hisOrHerOrTheir(self.executors)} absolute and uncontrolled discretion"
            " think fit, with power to postpone such sale, calling in and conversion"
            " of such property, or of such part or parts thereof for such period or"
            f' periods as my {self.renderPlural(self.executors, "Executor")} in'
            f" {self.hisOrHerOrTheir(self.executors)} absolute and uncontrolled discretion"
            " think fit, and to the extent necessary, have full powers to pay all my"
            " liabilities, debts, mortgages, funeral and testamentary expenses, and"
            " any taxes payable by reason of my death from my Estate"
            ' (<b>"Expenses"</b>).'
        )

        self.object_wrapper(result)
        self.main_counter += 1

        result = (
            f"The powers of my {self.renderPlural(self.executors, 'Executor')} named herein"
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
            f' {self.definePersons(self.user)}'
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

        if assetName == "RealEstate":
            assetHeader = "REAL ESTATE ALLOCATIONS"
        elif assetName == "BankAccount":
            assetHeader = "BANK ACCOUNT ALLOCATIONS"
        elif assetName == "Insurance":
            assetHeader = "INSURANCE ALLOCATIONS"
        elif assetName == "Investment":
            assetHeader = "INVESTMENT ALLOCATIONS"
        elif assetName == "Company":
            assetHeader = "COMPANY SHARES ALLOCATIONS"
        elif assetName == "Residual":
            assetHeader = "RESIDUAL ALLOCATIONS"
        else:  # pragma: no cover
            assetHeader = ""  # pragma: no cover

        self.object_wrapper(assetHeader, type="header-four", underline=True)

    def AssetsParagraphs(self):
        for assetName, asset_allocations in self.allocations.items():
            self.AssetHeader(assetName)
            if assetName == "BankAccount":
                startRef = self.main_counter
                self.BeneficiaryParagraph(
                    list(filter(
                        lambda allocation: allocation['allocation_amount'] != None, asset_allocations)),
                    distributionType="Cash"
                )
                endRef = self.main_counter
                self.BeneficiaryParagraph(
                    list(filter(
                        lambda allocation: allocation['allocation_percentage'] != None, asset_allocations)),
                    subjectTo=[startRef + 1, endRef]
                    if startRef != endRef
                    else None,
                    distributionType="Percentage",
                )
            elif assetName != "Residual":
                self.BeneficiaryParagraph(asset_allocations)
            else:
                self.ResidualBeneficiaryParagraph(asset_allocations)

    def BeneficiaryParagraph(self, allocations, subjectTo=None, distributionType=None):

        if len(allocations) == 1:

            allocation = allocations[0]
            result = (
                f"{self.SubjectToExpensesAndClauses(subjectTo)}, I give"
                f" {self.PercentageOrAmountOfInterestOrBenefitIn(allocations)}, to"
                f" {self.definePersons(allocation['entity'])} absolutely and free from all"
                f" encumbrances{self.ResidualStatement(allocation, distributionType)}"
            )

            self.object_wrapper(result)
            self.main_counter += 1

            self.SubBeneficiaryParagraph(
                allocation['allocations'], allocation, allocations)

        elif len(allocations) > 1:

            result = (
                f"{self.SubjectToExpensesAndClauses(subjectTo)}, I give"
                f" {self.PercentageOrAmountOfInterestOrBenefitIn(allocations)}, to the"
                " following persons in the corresponding proportions:"
            )

            self.object_wrapper(result)
            self.main_counter += 1

            hasResidual = (
                sum([float(allocation['allocation_percentage'])
                     for allocation in allocations]) < 100
                if distributionType != "Cash"
                else None
            )

            for index, allocation in enumerate(allocations):

                result = (
                    f"{self.PercentageOrAmount(allocation)} to"
                    f" {self.definePersons(allocation['entity'])} absolutely and free from all"
                    f" encumbrances{self.DefineMainSubstitute(index, allocations, self.main_counter)}{self.SemiColon(index, allocations, hasResidual)}"
                )

                self.object_wrapper(result, depth=1)

            if hasResidual and distributionType != "Cash":
                result = (
                    f"the remainder shall be distributed as part of my Residual Assets."
                )
                self.object_wrapper(result, depth=1)

            for index, allocation in enumerate(allocations):
                self.SubBeneficiaryParagraph(
                    allocation['allocations'], allocation, allocations)

    def SubBeneficiaryParagraph(self, allocations, parent_allocation, parent_allocations):

        hasResidual = (
            sum([float(allocation['allocation_percentage'])
                 for allocation in allocations]) < 100
            if parent_allocation["allocation_percentage"]
            else None
        )

        if len(allocations) == 0:

            result = (
                f"If {self.definePersons(parent_allocation['entity'])} should die during my lifetime,"
                " or fail to survive me for more than thirty (30) days, then the"
                f" {self.interestOrBenefits(parent_allocation)} in"
                f" {self.AssetLabel(parent_allocation['asset'])} which"
                f" {self.definePersons(parent_allocation['entity'])} would otherwise have received"
                " under this Will shall be distributed equally amongst"
                f" {self.definePersons(parent_allocation['entity'], ownership=True)} surviving issues"
                " absolutely and free from all encumbrances so long as they survive me"
                " for more than thirty (30) days"
            )

            if len(parent_allocations) != 1:
                result += (
                    f", and if {self.definePersons(parent_allocation['entity'])} does not have any"
                    " issues who have survived me for more than thirty (30) days, then"
                    " the same shall be distributed equally amongst all the Main"
                    " Substitutes who have survived me for more than thirty (30) days."
                )
            else:
                result += "."

            self.object_wrapper(result)
            self.main_counter += 1

        elif len(allocations) == 1:

            allocation = allocations[0]

            result = (
                f"If {self.definePersons(parent_allocation['entity'])} should die during my lifetime,"
                " or fail to survive me for more than thirty (30) days, I give"
                f" {self.PercentageOrAmount(allocation)} of the"
                f" {self.interestOrBenefits(allocation)} in"
                f" {self.AssetLabel(allocation['asset'])} which"
                f" {self.definePersons(parent_allocation['entity'])} would otherwise have received"
                " under this Will"
                f" {self.EffectivePercentageOrAmount(allocation)} to"
                f" {self.definePersons(allocation['entity'])} absolutely and free from all"
                " encumbrances, provided always that if"
                f" {self.definePersons(allocation['entity'])} should die during my lifetime,"
                " or fail to survive me for more than thirty (30) days, then the same"
                " shall be distributed equally amongst"
                f" {self.definePersons(allocation['entity'], ownership=True)} surviving"
                " issues absolutely and free from all encumbrances so long as they"
                " survive me for more than thirty (30) days"
            )

            if len(parent_allocations) != 1 and self.has_other_main_substitutes(
                allocation, parent_allocation, parent_allocations
            ):
                result += (
                    f", and if {self.definePersons(allocation['entity'])} does not have any"
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
                f"If {self.definePersons(parent_allocation['entity'])} should die during my lifetime,"
                " or fail to survive me for more than thirty (30) days, I give the"
                f" {self.interestOrBenefits(parent_allocation)} in"
                f" {self.AssetLabel(parent_allocation['asset'])} which"
                f" {self.definePersons(parent_allocation['entity'])} would otherwise have received"
                " under this Will, to the following persons in the corresponding"
                " proportions:"
            )

            self.object_wrapper(result)
            self.main_counter += 1

            for index, allocation in enumerate(allocations):

                temp_result = (
                    f"{self.PercentageOrAmount(allocation)}"
                    f" {self.EffectivePercentageOrAmount(allocation)}"
                    f" to {self.definePersons(allocation['entity'])} absolutely and free"
                    " from all"
                    f" encumbrances{self.DefineApplicableSubstitute(index, allocations)}{self.SemiColon(index, allocations, hasResidual)}"
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
                f" {self.interestOrBenefits(parent_allocation)} in"
                f" {self.AssetLabel(parent_allocation['asset'])} which that Applicable Substitute"
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

    def ResidualBeneficiaryParagraph(self, allocations):

        clausesAbove = (
            " not distributed in the clauses above "
            if not self.onlyResidualAsset
            else " "
        )

        if len(allocations) == 1:

            allocation = allocations[0]
            result = (
                f"I give all my Assets{clausesAbove}{self.AssetDefinition(allocation['asset'])}"
                f" to {self.definePersons(allocation['entity'])} absolutely and free from all"
                " encumbrances."
            )

            self.object_wrapper(result)
            self.main_counter += 1

            self.ResidualSubBeneficiaryParagraph(
                allocation['allocations'], allocation, allocations)

        elif len(allocations) > 1:
            result = (
                f"I give all my Assets{clausesAbove}{self.AssetDefinition(allocations[0]['asset'])}"
                " to the following persons in the corresponding proportions:"
            )

            self.object_wrapper(result)
            self.main_counter += 1

            for index, allocation in enumerate(allocations):

                result = (
                    f"{self.PercentageOrAmount(allocation)} to"
                    f" {self.definePersons(allocation['entity'])} absolutely and free from all"
                    f" encumbrances{self.DefineMainSubstitute(index, allocations, self.main_counter)}{self.SemiColon(index, allocations, False)}"
                )

                self.object_wrapper(result, depth=1)

            for index, allocation in enumerate(allocations):
                self.ResidualSubBeneficiaryParagraph(
                    allocation['allocations'], allocation, allocations)

    def ResidualSubBeneficiaryParagraph(self, allocations, parent_allocation, parent_allocations):

        if len(allocations) == 0:

            result = (
                f"If {self.definePersons(parent_allocation['entity'])} should die during my lifetime,"
                " or fail to survive me for more than thirty (30) days, then the"
                f" proportion of my {self.AssetLabel(parent_allocation['asset'])} which"
                f" {self.heOrShe(parent_allocation['entity'])} would otherwise have received under this Will"
                f" shall be distributed equally amongst {self.hisOrHer(parent_allocation['entity'])}"
                " surviving issues absolutely and free from all encumbrances so long"
                " as they survive me for more than thirty (30) days"
            )

            if len(parent_allocations) != 1:
                result += (
                    f", and if {self.definePersons(parent_allocation['entity'])} does not have any"
                    " issues who have survived me for more than thirty (30) days, then"
                    " the same shall be distributed equally amongst all the Main"
                    " Substitutes who have survived me for more than thirty (30) days."
                )
            else:
                result += "."

            self.object_wrapper(result)
            self.main_counter += 1

        elif len(allocations) == 1:

            allocation = allocations[0]

            result = (
                f"If {self.definePersons(parent_allocation['entity'])} should die during my lifetime,"
                " or fail to survive me for more than thirty (30) days, I give"
                f" {self.PercentageOrAmount(allocation)}"
                f" {self.EffectivePercentageOrAmount(allocation)} of"
                f" the {self.AssetLabel(allocation['asset'])} which {self.heOrShe(parent_allocation['entity'])}"
                " would otherwise have received under this Will to"
                f" {self.definePersons(allocation['entity'])} absolutely and free from all"
                " encumbrances, provided always that if"
                f" {self.definePersons(allocation['entity'])} should die during my lifetime,"
                " or fail to survive me for more than thirty (30) days, then the same"
                f" shall be distributed equally amongst {self.hisOrHer(allocation['entity'])}"
                " surviving issues absolutely and free from all encumbrances so long"
                " as they survive me for more than thirty (30) days"
            )

            if len(parent_allocations) != 1:
                result += (
                    f", and if {self.definePersons(allocation['entity'])} does not have any"
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
                f"If {self.definePersons(parent_allocation['entity'])} should die during my lifetime,"
                " or fail to survive me for more than thirty (30) days, I give the"
                f" {self.interestOrBenefits(parent_allocation)} in"
                f" {self.AssetLabel(parent_allocation['asset'])} which {self.heOrShe(parent_allocation['entity'])} would"
                " otherwise have received under this Will, to the following persons in"
                " the corresponding proportions:"
            )

            self.object_wrapper(result)
            self.main_counter += 1

            for index, allocation in enumerate(allocations):

                hasResidual = sum([float(allocation['allocation_percentage'])
                                   for allocation in allocations]) < 100

                temp_result = (
                    f"{self.PercentageOrAmount(allocation)}"
                    f" {self.EffectivePercentageOrAmount(allocation)}"
                    f" to {self.definePersons(allocation['entity'])} absolutely and free"
                    " from all"
                    f" encumbrances{self.DefineApplicableSubstitute(index, allocations)}{self.SemiColon(index, allocations, hasResidual)}"
                )

                self.object_wrapper(temp_result, depth=1)

            temp_result = (
                "Provided Always that if any of the Applicable Substitutes, should die"
                " during my lifetime, or fail to survive me for more than thirty (30)"
                f" days, the proportion of my {self.AssetLabel(parent_allocation['asset'])} which that"
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

    def parse(self):
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

        return {
            **self.data,
            'witnesses': self.witnesses,
            "blocks": self.generate_draftjs_blocks(self.WillObject)
        }
