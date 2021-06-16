from collections import OrderedDict

from django_countries import countries


def has_other_main_substitutes(asset, beneficiary, sub_beneficiary):
    ans = True
    if len(asset["entities"]) < 2:
        ans = False
    elif len(asset["entities"]) == 2:
        other_beneficiary = next(
            x
            for x in asset["entities"]
            if x["entity_id"] != beneficiary["entity_id"]
        )

        ans = (
            False
            if other_beneficiary["entity_id"] == sub_beneficiary["entity_id"]
            else True
        )
    else:
        ans = True

    return ans


def roman(num):
    """ Converts a Number to a roman numeral """
    roman = OrderedDict()
    roman[1000] = "M"
    roman[900] = "CM"
    roman[500] = "D"
    roman[400] = "CD"
    roman[100] = "C"
    roman[90] = "XC"
    roman[50] = "L"
    roman[40] = "XL"
    roman[10] = "X"
    roman[9] = "IX"
    roman[5] = "V"
    roman[4] = "IV"
    roman[1] = "I"

    def roman_num(num):
        for r in roman.keys():
            x, y = divmod(num, r)
            yield roman[r] * x
            num -= r * x
            if num <= 0:
                break

    return "".join([a for a in roman_num(num)]).lower()


def SubjectToExpensesAndClauses(subjectTo):

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


def renderPlural(total_count, base_term, suffix="s"):
    if len(total_count) > 1:
        return base_term + suffix
    return base_term


def interestOrBenefits(asset, assetName, beneficiary):
    if beneficiary and beneficiary["allocation_percentage"]:
        if assetName == "Insurance":
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


def PercentageOrAmountOfInterestOrBenefitIn(asset, assetName, beneficiary=None):
    if not beneficiary:
        beneficiary = asset["entities"][0]

    if len(asset["entities"]) == 1:

        if beneficiary["allocation_percentage"]:
            return (
                f"{PercentageOrAmount(asset)} of my"
                f" {interestOrBenefits(asset, assetName, beneficiary)} in"
                f" {AssetDetails(asset, assetName)} {AssetDefinition(asset, assetName)}"
            )

        if beneficiary["allocation_amount"]:
            return (
                f"{PercentageOrAmount(asset)} from {AssetDetails(asset, assetName)}"
                f" {AssetDefinition(asset, assetName)}"
            )

    if len(asset["entities"]) > 1:

        if beneficiary["allocation_percentage"]:
            return (
                f"my {interestOrBenefits(asset, assetName, beneficiary)} in"
                f" {AssetDetails(asset, assetName)} {AssetDefinition(asset, assetName)}"
            )

        if beneficiary["allocation_amount"]:
            return (
                f"the following amounts from {AssetDetails(asset, assetName)}"
                f" {AssetDefinition(asset, assetName)}"
            )


def PercentageOrAmount(asset, beneficiary=None):
    # to cater for where there is only one beneficiary
    if not beneficiary:
        beneficiary = asset["entities"][0]
    if beneficiary["allocation_percentage"]:
        return f"{beneficiary['allocation_percentage']}%"
    elif beneficiary["allocation_amount"]:
        return f"${beneficiary['allocation_amount']}"


def EffectivePercentageOrAmount(asset, assetName, beneficiary):

    if beneficiary["effective_allocation_percentage"]:
        return (
            f"(being {beneficiary['effective_allocation_percentage']}% of my total"
            f" {interestOrBenefits(asset, assetName, beneficiary)} in the same)"
        )
    return ""


def ResidualStatement(asset, distributionType):
    if distributionType == "Cash":
        return "."

    if int(asset["total_allocation"]) < 100:
        return ", and the remainder shall be distributed as part of my Residual Estate."
    else:
        return "."


def SemiColon(index, alldata, last=False):
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


def heOrSheOrThey(entities, beneficiary=None):
    if len(entities) == 0:
        return None
    if beneficiary == None or len(entities) != 0:
        if len(entities) > 1:
            pronoun = "they"
        elif len(entities) == 1:
            beneficiary = entities[0]
            if beneficiary["entity_details"]["gender"] == "Male":
                pronoun = "he"
            else:
                pronoun = "she"
        return pronoun


def hisOrHerOrTheir(entities, beneficiary=None):
    if len(entities) == 0:
        return None
    if beneficiary == None or len(entities) != 0:
        if len(entities) > 1:
            pronoun = "Their"
        elif len(entities) == 1:
            beneficiary = entities[0]

            if beneficiary["entity_details"]["gender"] == "Male":
                pronoun = "his"
            else:
                pronoun = "her"
        return pronoun


def heOrShe(beneficiary):
    if beneficiary["entity_details"]["gender"] == "Male":
        pronoun = "he"
    else:
        pronoun = "she"
    return pronoun


def hisOrHer(beneficiary):
    if beneficiary["entity_details"]["gender"] == "Male":
        pronoun = "his"
    else:
        pronoun = "her"
    return pronoun


def subClause(index):
    counter = index + 1
    if counter == 2:
        subClause = "sub-clause " + roman(counter - 1)
    elif counter > 2:
        subClause = "sub-clauses " + roman(1) + "-" + roman(counter - 1)
    else:
        subClause = ""
    return subClause


def DefineApplicableSubstitute(index, sub_entities):
    if index + 1 == len(sub_entities) and len(sub_entities) != 1:
        return (
            " (for the purpose of this clause, together with the named Substitute"
            f" Beneficiaries in {subClause(index)} above, the “<b>Applicable"
            " Substitutes</b>”)"
        )
    else:
        return ""


def DefineMainSubstitute(index, entities, clause):
    start_clause = clause
    end_clause = clause + len(entities)
    if index + 1 == len(entities) and len(entities) != 1:
        return (
            f" (for the purpose of clauses {start_clause} to {end_clause}, together"
            f" with the named Beneficiaries in {subClause(index)} above, the “<b>Main"
            " Substitutes</b>”)"
        )
    else:
        return ""


def AssetLabel(asset, assetName):

    if assetName == "real_estates":
        assetLabel = f"{asset['real_estate_type']} {asset['postal_code']}"
    elif assetName == "bank_accounts":
        assetLabel = f"{asset['bank']} {asset['account_number']}"
    elif assetName == "insurances":
        assetLabel = f"{asset['plan']} {asset['policy_number']}"
    elif assetName == "investments":
        assetLabel = f"{asset['financial_institution']} {asset['account_number']}"
    elif assetName == "companies":
        assetLabel = f"{asset['name']} {asset['registration_number']}"
    elif assetName == "residual":
        assetLabel = "Residual Assets"
    else:
        assetLabel = ""  # pragma: no cover

    return assetLabel


def AssetDefinition(asset, assetName):

    assetLabel = AssetLabel(asset, assetName)
    return f'("<b>{assetLabel}</b>")'


def AssetDetails(asset, assetName, isPartSentence=False):

    if isPartSentence:
        beforeAssetDetails = ""
    else:
        beforeAssetDetails = "the "
    if assetName == "real_estates":
        AssetDetails = (
            f"{beforeAssetDetails}{asset['real_estate_type']} located at"
            f" {asset['address']}"
        )
    elif assetName == "bank_accounts":
        AssetDetails = (
            f"{beforeAssetDetails}Bank Account held with {asset['bank']} with account"
            f" number {asset['account_number']}"
        )
    elif assetName == "insurances":
        AssetDetails = (
            f"{beforeAssetDetails}Insurance Plan taken out with {asset['insurer']}"
            f" titled {asset['plan']} and with policy number {asset['policy_number']}"
        )
    elif assetName == "investments":
        AssetDetails = (
            f"{beforeAssetDetails}Investment Account held with"
            f" {asset['financial_institution']} with account number"
            f" {asset['account_number']}"
        )
    elif assetName == "companies":
        AssetDetails = (
            f"{beforeAssetDetails}{asset['shares_amount']} Ordinary Share(s) (being"
            f" {asset['percentage']}% of the total issued Ordinary Shares) of"
            f" {asset['name']}, a Company Incorporated in Singapore with registration"
            f" number {asset['registration_number']}"
        )
    elif assetName == "residual":
        AssetDetails = "All my Assets not distributed in the clauses above"
    else:
        AssetDetails = ""  # pragma: no cover

    return AssetDetails
