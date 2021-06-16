from collections import OrderedDict
from ..base_parser_utils import BaseParserUtils


class ParserUtils(BaseParserUtils):

    def has_other_main_substitutes(self, allocation, parent_allocation, parent_allocations):
        ans = True
        if len(parent_allocations) < 2:
            ans = False
        elif len(parent_allocations) == 2:
            other_beneficiary = next(
                x
                for x in parent_allocations
                if x["entity"]['id'] != parent_allocation["entity"]['id']
            )

            ans = (
                False
                if other_beneficiary["entity"]['id'] == allocation["entity"]['id']
                else True
            )
        else:
            ans = True

        return ans

    def SubjectToExpensesAndClauses(self, subjectTo):

        if subjectTo:
            if len(subjectTo) != 2:
                raise ValueError(  # pragma: no cover
                    "You need to have a start clause and an end clause."
                    " Function(SubjectToExpensesAndClauses)"
                )
            return (
                f"Subject to clauses {subjectTo[0]} to {subjectTo[1]}, and to the payment"
                " of all my Expenses"
            )

        return "Subject to the payment of all my Expenses"

    def renderPlural(self, total_count, base_term, suffix="s"):
        if len(total_count) > 1:
            return base_term + suffix
        return base_term

    def interestOrBenefits(self, allocation):
        asset = allocation['asset']

        if allocation["allocation_percentage"]:
            if asset['asset_type'] == "Insurance":
                interest_benefit = "benefits"
            else:
                interest_benefit = "interest"
        else:
            interest_benefit = "amount"

        if "holding_type" in asset:
            holding_type = asset["holding_type"]
            if holding_type == "JOINT_TENANT" or holding_type == "JOINTLY":
                return (
                    interest_benefit
                    + ", whether obtained through severance or survivorship,"
                )

        return interest_benefit

    def PercentageOrAmountOfInterestOrBenefitIn(self, allocations):

        if len(allocations) == 1:

            allocation = allocations[0]
            asset = allocation['asset']

            if allocation["allocation_percentage"]:
                return (
                    f"{self.PercentageOrAmount(allocation)} of my"
                    f" {self.interestOrBenefits(allocation)} in"
                    f" {self.AssetDetails(asset)} {self.AssetDefinition(asset)}"
                )

            if allocation["allocation_amount"]:
                return (
                    f"{self.PercentageOrAmount(allocation)} from {self.AssetDetails(asset)}"
                    f" {self.AssetDefinition(asset)}"
                )

        if len(allocations) > 1:

            allocation = allocations[0]
            asset = allocation['asset']

            if allocation["allocation_percentage"]:
                return (
                    f"my {self.interestOrBenefits(allocation)} in"
                    f" {self.AssetDetails(asset)} {self.AssetDefinition(asset)}"
                )

            if allocation["allocation_amount"]:
                return (
                    f"the following amounts from {self.AssetDetails(asset)}"
                    f" {self.AssetDefinition(asset)}"
                )

    def PercentageOrAmount(self, allocation):

        if allocation["allocation_percentage"]:
            return f"{allocation['allocation_percentage']}%"
        elif allocation["allocation_amount"]:
            return f"${allocation['allocation_amount']}"

    def EffectivePercentageOrAmount(self, allocation):

        if allocation["effective_allocation_percentage"]:
            return (
                f"(being {allocation['effective_allocation_percentage']}% of my total"
                f" {self.interestOrBenefits(allocation)} in the same)"
            )
        return ""

    def ResidualStatement(self, allocation, distributionType):
        if distributionType == 'Cash':
            return "."

        if float(allocation["allocation_percentage"]) < 100:
            return ", and the remainder shall be distributed as part of my Residual Estate."
        else:
            return "."

    def SemiColon(self, index, alldata, last=False):
        counter = index + 1
        if len(alldata) == 1 or len(alldata) == counter:
            if last:
                return "; and"
            else:
                return "."
        elif not last and (len(alldata) - 1) == counter:
            return "; and"
        else:
            return ";"

    def heOrSheOrThey(self, entities, beneficiary=None):
        if len(entities) == 0:
            return None
        if beneficiary == None or len(entities) != 0:
            if len(entities) > 1:
                pronoun = "they"
            elif len(entities) == 1:
                beneficiary = entities[0]
                if beneficiary["gender"] == "Male":
                    pronoun = "he"
                else:
                    pronoun = "she"
            return pronoun

    def hisOrHerOrTheir(self, entities, beneficiary=None):
        if len(entities) == 0:
            return None
        if beneficiary == None or len(entities) != 0:
            if len(entities) > 1:
                pronoun = "Their"
            elif len(entities) == 1:
                beneficiary = entities[0]

                if beneficiary["gender"] == "Male":
                    pronoun = "his"
                else:
                    pronoun = "her"
            return pronoun

    def heOrShe(self, beneficiary):
        if beneficiary["gender"] == "Male":
            pronoun = "he"
        else:
            pronoun = "she"
        return pronoun

    def hisOrHer(self, beneficiary):
        if beneficiary["gender"] == "Male":
            pronoun = "his"
        else:
            pronoun = "her"
        return pronoun

    def subClause(self, index):
        counter = index + 1
        if counter == 2:
            subClause = "sub-clause " + self.roman(counter - 1)
        elif counter > 2:
            subClause = "sub-clauses " + \
                self.roman(1) + "-" + self.roman(counter - 1)
        else:
            subClause = ""
        return subClause

    def DefineApplicableSubstitute(self, index, sub_entities):
        if index + 1 == len(sub_entities) and len(sub_entities) != 1:
            return (
                " (for the purpose of this clause, together with the named Substitute"
                f" Beneficiaries in {self.subClause(index)} above, the “<b>Applicable"
                " Substitutes</b>”)"
            )
        else:
            return ""

    def DefineMainSubstitute(self, index, allocations, clause):
        start_clause = clause
        end_clause = clause + len(allocations)
        if index + 1 == len(allocations) and len(allocations) != 1:
            return (
                f" (for the purpose of clauses {start_clause} to {end_clause}, together"
                f" with the named Beneficiaries in {self.subClause(index)} above, the “<b>Main"
                " Substitutes</b>”)"
            )
        else:
            return ""

    def AssetLabel(self, asset):

        if asset['asset_type'] == "RealEstate":
            return f"{asset['real_estate_type']} {asset['postal_code']}"
        elif asset['asset_type'] == "BankAccount":
            return f"{asset['bank']} {asset['account_number']}"
        elif asset['asset_type'] == "Insurance":
            return f"{asset['plan']} {asset['policy_number']}"
        elif asset['asset_type'] == "Investment":
            return f"{asset['financial_institution']} {asset['account_number']}"
        elif asset['asset_type'] == "Company":
            return f"{asset['name']} {asset['registration_number']}"
        elif asset['asset_type'] == "Residual":
            return "Residual Assets"
        else:
            return ""  # pragma: no cover

    def AssetDefinition(self, asset):

        assetLabel = self.AssetLabel(asset)
        return f'("<b>{assetLabel}</b>")'

    def AssetDetails(self, asset, isPartSentence=False):

        if isPartSentence:
            beforeAssetDetails = ""
        else:
            beforeAssetDetails = "the "
        if asset['asset_type'] == "RealEstate":
            AssetDetails = (
                f"{beforeAssetDetails}{asset['real_estate_type']} located at"
                f" {asset['address']}"
            )
        elif asset['asset_type'] == "BankAccount":
            AssetDetails = (
                f"{beforeAssetDetails}Bank Account held with {asset['bank']} with account"
                f" number {asset['account_number']}"
            )
        elif asset['asset_type'] == "Insurance":
            AssetDetails = (
                f"{beforeAssetDetails}Insurance Plan taken out with {asset['insurer']}"
                f" titled {asset['plan']} and with policy number {asset['policy_number']}"
            )
        elif asset['asset_type'] == "Investment":
            AssetDetails = (
                f"{beforeAssetDetails}Investment Account held with"
                f" {asset['financial_institution']} with account number"
                f" {asset['account_number']}"
            )
        elif asset['asset_type'] == "Company":
            AssetDetails = (
                f"{beforeAssetDetails}{asset['shares_amount']} Ordinary Share(s) (being"
                f" {asset['percentage']}% of the total issued Ordinary Shares) of"
                f" {asset['name']}, a Company Incorporated in Singapore with registration"
                f" number {asset['registration_number']}"
            )
        elif asset['asset_type'] == "Residual":
            AssetDetails = "All my Assets not distributed in the clauses above"
        else:
            AssetDetails = ""  # pragma: no cover

        return AssetDetails
