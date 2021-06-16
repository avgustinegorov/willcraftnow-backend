import sys
from itertools import cycle

from assets.tests import factories as asset_factories
from core.serializers import LPAOrderSerializer

from .will_templates_bankaccount import *
from .will_templates_company import *
from .will_templates_insurance import *
from .will_templates_investment import *
from .will_templates_misc import *
from .will_templates_realestate import *
from .will_templates_residual import *


def build_will_template(
    will_template,
    asset_type,
    allocations,
    sub_allocations,
    total_allocation_percentage,
    total_allocation_amount=None,
):
    len_allocations = len(allocations)
    if len_allocations:
        title_added = False
        title = getattr(
            sys.modules[__name__], f"WILL_{asset_type}_ALLOCATIONS_TITLE_BLOCK_TEMPLATE"
        )

        if total_allocation_amount:
            len_amount_allocations = 0
            mentioned_beneficiaries = set()
            amount_allocations = []
            for allocation in allocations:
                if allocation.allocation_amount:
                    len_amount_allocations += 1
                    amount_allocations.append(allocation)
                    mentioned_beneficiaries.add(allocation.entity.id)

            _template_name = f"WILL_{asset_type}_{len_amount_allocations}_AMOUNT_ALLOCATIONS_BLOCK_TEMPLATE"
            print(_template_name)

            will_template.append(
                ("" if title_added else title)
                + getattr(sys.modules[__name__], _template_name),
            )
            title_added = True
            len_sub_allocations = len(sub_allocations[amount_allocations[0].id])
            if len_sub_allocations:
                for i, allocation in enumerate(amount_allocations):
                    mentioned_sub_entity_codes = set()
                    for j, sub_allocation in enumerate(sub_allocations[allocation.id]):
                        if sub_allocation.entity.id in mentioned_beneficiaries:
                            mentioned_sub_entity_codes.add(f"{i+1}_{j+1}")

                    _template_name = f"WILL_{len_sub_allocations}_SUB_BENEFICIARIES_{asset_type}_AMOUNT_BENEFICIARY_{i+1}_DIES_BLOCK_TEMPLATE"
                    print(_template_name)

                    will_template.append(
                        "%(numbering)d."
                        + getattr(sys.modules[__name__], _template_name)(
                            len_amount_allocations, mentioned_sub_entity_codes
                        ).replace("%", "%%")
                    )

                    for sub_allocation in sub_allocations[allocation.id]:
                        mentioned_beneficiaries.add(sub_allocation.entity.id)

            else:
                for i in range(len_amount_allocations):

                    _template_name = f"WILL_{asset_type}_AMOUNT_BENEFICIARY_{i+1}_DIES_BLOCK_TEMPLATE"
                    print(_template_name)

                    will_template.append(
                        "%(numbering)d."
                        + getattr(sys.modules[__name__], _template_name)(
                            len_amount_allocations
                        ).replace("%", "%%"),
                    )

        if total_allocation_percentage is None:
            return

        len_pct_allocations = 0
        pct_allocations = []
        for allocation in allocations:
            if allocation.allocation_percentage:
                len_pct_allocations += 1
                pct_allocations.append(allocation)

        if total_allocation_percentage < 100:
            _template_name = f"WILL_{asset_type}_{len_pct_allocations}_ALLOCATIONS_LT_100_BLOCK_TEMPLATE"
            print(_template_name)

            will_template.append(
                ("" if title_added else title)
                + getattr(sys.modules[__name__], _template_name)(
                    bool(total_allocation_amount)
                ),
            )
        else:
            _template_name = (
                f"WILL_{asset_type}_{len_pct_allocations}_ALLOCATIONS_BLOCK_TEMPLATE"
            )
            print(_template_name)

            will_template.append(
                ("" if title_added else title)
                + getattr(sys.modules[__name__], _template_name)(
                    bool(total_allocation_amount)
                ),
            )

        len_sub_allocations = len(sub_allocations[pct_allocations[0].id])
        if len_sub_allocations:
            for i, allocation in enumerate(pct_allocations):
                if total_allocation_percentage < 100:

                    _template_name = f"WILL_{len_sub_allocations}_SUB_BENEFICIARIES_{asset_type}_BENEFICIARY_{i+1}_DIES_LT_100_BLOCK_TEMPLATE"
                    print(_template_name)

                    will_template.append(
                        "%(numbering)d."
                        + getattr(sys.modules[__name__], _template_name)(
                            len_pct_allocations, bool(total_allocation_amount)
                        ).replace("%", "%%")
                    )
                else:
                    _template_name = f"WILL_{len_sub_allocations}_SUB_BENEFICIARIES_{asset_type}_BENEFICIARY_{i+1}_DIES_BLOCK_TEMPLATE"
                    print(_template_name)

                    will_template.append(
                        "%(numbering)d."
                        + getattr(sys.modules[__name__], _template_name)(
                            len_pct_allocations, bool(total_allocation_amount)
                        ).replace("%", "%%")
                    )
        else:
            for i in range(len_pct_allocations):

                _template_name = (
                    f"WILL_{asset_type}_BENEFICIARY_{i+1}_DIES_BLOCK_TEMPLATE"
                )
                print(_template_name)

                will_template.append(
                    "%(numbering)d."
                    + getattr(sys.modules[__name__], _template_name)(
                        len_pct_allocations, bool(total_allocation_amount)
                    ).replace("%", "%%"),
                )


def get_will_template(
    relationship_status,
    total_allocation_percentage,
    total_allocation_amount,
    num_executors,
    num_sub_executors,
    num_guardians,
    instructions,
    has_lastrites,
    AssetFactory,
    allocations,
    sub_allocations,
    residual_allocations,
    residual_sub_allocations,
):
    will_template = []
    if num_executors == 1:
        will_template = [
            WILL_1_EXECUTOR_BLOCK_TEMPLATE,
            "EXECUTOR'S POWERS\n%(numbering)d." + WILL_1_EXECUTOR_POWERS_BLOCK_TEMPLATE,
            "%(numbering)d." + WILL_1_EXECUTOR_CAP_337_BLOCK_TEMPLATE,
        ]

    elif num_executors == 2:
        will_template = [
            WILL_2_EXECUTORS_BLOCK_TEMPLATE,
            "EXECUTORS' POWERS\n%(numbering)d."
            + WILL_2_EXECUTORS_POWERS_BLOCK_TEMPLATE,
            "%(numbering)d." + WILL_2_EXECUTORS_CAP_337_BLOCK_TEMPLATE,
        ]

    elif num_executors == 3:
        will_template = [
            WILL_3_EXECUTORS_BLOCK_TEMPLATE,
            "EXECUTORS' POWERS\n%(numbering)d."
            + WILL_2_EXECUTORS_POWERS_BLOCK_TEMPLATE,
            "%(numbering)d." + WILL_2_EXECUTORS_CAP_337_BLOCK_TEMPLATE,
        ]

    elif num_executors == 4:
        will_template = [
            WILL_4_EXECUTORS_BLOCK_TEMPLATE,
            "EXECUTORS' POWERS\n%(numbering)d."
            + WILL_2_EXECUTORS_POWERS_BLOCK_TEMPLATE,
            "%(numbering)d." + WILL_2_EXECUTORS_CAP_337_BLOCK_TEMPLATE,
        ]

    # Each will can only have one sub_executor
    if num_sub_executors == 1:
        if num_executors == 1:
            will_template.insert(1, WILL_1_SUB_EXECUTOR_BLOCK_TEMPLATE)
        elif num_executors > 1:
            will_template.insert(1, WILL_1_SUB_EXECUTOR_JOINT_BLOCK_TEMPLATE)

    if AssetFactory == asset_factories.RealEstateFactory:
        build_will_template(
            will_template,
            "REAL_ESTATE",
            allocations,
            sub_allocations,
            total_allocation_percentage,
        )
    elif AssetFactory == asset_factories.BankAccountFactory:
        build_will_template(
            will_template,
            "BANK_ACCOUNT",
            allocations,
            sub_allocations,
            total_allocation_percentage,
            total_allocation_amount,
        )
    elif AssetFactory == asset_factories.InsuranceFactory:
        build_will_template(
            will_template,
            "INSURANCE",
            allocations,
            sub_allocations,
            total_allocation_percentage,
        )
    elif AssetFactory == asset_factories.InvestmentFactory:
        build_will_template(
            will_template,
            "INVESTMENT",
            allocations,
            sub_allocations,
            total_allocation_percentage,
        )
    elif AssetFactory == asset_factories.CompanyFactory:
        build_will_template(
            will_template,
            "COMPANY",
            allocations,
            sub_allocations,
            total_allocation_percentage,
        )

    # Handle Residuals
    build_will_template(
        will_template,
        "RESIDUAL",
        residual_allocations,
        residual_sub_allocations,
        total_allocation_percentage or 100,
    )

    # Each will can only have one guardian
    if num_guardians == 1:
        will_template.append("%(numbering)d." + WILL_GUARDIAN_JOINT_BLOCK_TEMPLATE),
        if relationship_status == "Single":
            will_template[-1] = "%(numbering)d." + WILL_GUARDIAN_BLOCK_TEMPLATE

    if instructions:
        if instructions == "BURIED":
            will_template.append(
                "%(numbering)d." + WILL_INSTRUCTIONS_BURIED_BLOCK_TEMPLATE
            )
        elif instructions == "SCATTERED":
            will_template.append(
                "%(numbering)d." + WILL_INSTRUCTIONS_SCATTERED_BLOCK_TEMPLATE
            )
        elif instructions == "CREMATED":
            will_template.append(
                "%(numbering)d." + WILL_INSTRUCTIONS_CREMATED_BLOCK_TEMPLATE
            )

    if has_lastrites:
        will_template.append("%(numbering)d." + WILL_LASTRITES_FUNERAL_BLOCK_TEMPLATE)

    return (
        WILL_OPENING_BLOCK_TEMPLATE
        + "\n".join(
            numbered_text[1]
            % dict(
                numbering=numbered_text[0],
                numbering_plus_2=numbered_text[0] + 2,
                numbering_plus_3=numbered_text[0] + 3,
                numbering_minus_1=numbered_text[0] - 1,
                numbering_minus_beneficiaries=numbered_text[0]
                - len(residual_allocations)
                - 1,
            )
            for numbered_text in enumerate(will_template, 3)
        )
        + WILL_SIGN_BLOCK_TEMPLATE
    )


def get_will_pdf_test_input_permutations():
    params = []
    relationship_statuses = cycle(["Married", "Single"])
    instructions_list = cycle([None, "BURIED", "SCATTERED", "CREMATED"])
    has_lastrites_list = cycle([False, True])
    num_guardians_list = cycle([0, 1])
    num_executors_list = cycle(range(1, 5))
    num_sub_executors_list = cycle([0, 0, 1])
    num_beneficiaries_list = [1, 2, 3]
    num_sub_beneficiaries_list = [0, 1, 2, 3]
    AssetFactories = [
        asset_factories.RealEstateFactory,
        asset_factories.BankAccountFactory,
        asset_factories.InsuranceFactory,
        asset_factories.InvestmentFactory,
        asset_factories.CompanyFactory,
    ]
    allocations = [
        dict(total_allocation_percentage=100, total_allocation_amount=None),
        dict(total_allocation_percentage=60, total_allocation_amount=None),
        dict(total_allocation_percentage=None, total_allocation_amount=100000),
        dict(total_allocation_percentage=100, total_allocation_amount=200000),
        dict(total_allocation_percentage=70, total_allocation_amount=300000),
    ]

    for AssetFactory in AssetFactories:
        for allocation in allocations:
            if (
                allocation["total_allocation_amount"] is not None
                and AssetFactory != asset_factories.BankAccountFactory
            ):
                continue
            for num_beneficiaries in num_beneficiaries_list:
                for num_sub_beneficiaries in num_sub_beneficiaries_list:
                    instructions = next(instructions_list)
                    while True:
                        has_lastrites = next(has_lastrites_list)
                        if instructions is not None:
                            break
                        if not has_lastrites:
                            break

                    param = allocation.copy()
                    param.update(
                        dict(
                            order_type="WILL",
                            num_executors=next(num_executors_list),
                            num_sub_executors=next(num_sub_executors_list),
                            relationship_status=next(relationship_statuses),
                            instructions=instructions,
                            has_lastrites=has_lastrites,
                            num_guardians=next(num_guardians_list),
                            num_beneficiaries=num_beneficiaries,
                            num_sub_beneficiaries=num_sub_beneficiaries,
                            AssetFactory=AssetFactory,
                        )
                    )
                    params.append(param)

    return params


def get_lpa_pdf_test_input_permutations():
    params = []
    relationship_statuses = cycle(["Married", "Single"])
    instructions_list = cycle([None, "BURIED", "SCATTERED", "CREMATED"])
    has_lastrites_list = cycle([False, True])
    num_guardians_list = cycle([0, 1])
    num_executors_list = cycle(range(1, 5))
    num_sub_executors_list = [0, 1]
    num_beneficiaries_list = [(1, 0), (1, 1), (1, 2), (2, 0)]
    AssetFactories = [
        asset_factories.RealEstateFactory,
        asset_factories.BankAccountFactory,
        asset_factories.InsuranceFactory,
        asset_factories.InvestmentFactory,
        asset_factories.CompanyFactory,
    ]

    basic_params = [
        dict(total_allocation_percentage=100, total_allocation_amount=None,),
        dict(total_allocation_percentage=60, total_allocation_amount=None,),
    ]

    for basic_param in basic_params:
        for num_sub_executors in num_sub_executors_list:
            for num_beneficiaries_pair in num_beneficiaries_list:
                num_beneficiaries = num_beneficiaries_pair[0]
                num_sub_beneficiaries = num_beneficiaries_pair[1]
                for AssetFactory in AssetFactories:
                    if (
                        num_beneficiaries > 1 or num_sub_beneficiaries > 0
                    ) and AssetFactory not in [
                        asset_factories.BankAccountFactory,
                        asset_factories.RealEstateFactory,
                    ]:
                        continue

                    instructions = next(instructions_list)
                    while True:
                        has_lastrites = next(has_lastrites_list)
                        if instructions is not None:
                            break
                        if not has_lastrites:
                            break

                    param = basic_param.copy()
                    param.update(
                        dict(
                            order_type="LPA",
                            num_executors=next(num_executors_list),
                            num_sub_executors=num_sub_executors,
                            relationship_status=next(relationship_statuses),
                            instructions=instructions,
                            has_lastrites=has_lastrites,
                            num_guardians=next(num_guardians_list),
                            num_beneficiaries=num_beneficiaries,
                            num_sub_beneficiaries=num_sub_beneficiaries,
                            AssetFactory=AssetFactory,
                        )
                    )
                    params.append(param)

    return params


def set_data(order):
    data = LPAOrderSerializer(order).data

    donees = list(
        filter(lambda person: "DONEE" in person["entity_roles"], data["people"])
    )

    replacement_donee = list(
        filter(
            lambda person: "REPLACEMENT_DONEE" in person["entity_roles"],
            data["people"],
        )
    )

    textfield_schema = {
        # donor details
        "(Full name as in ID)": data["user_details"].get("name", None),
        "(ID number)": data["user_details"].get("id_number", None),
        "(Date of birth  ddmmyyyy)": parse(
            data["user_details"].get("date_of_birth", None)
        ).strftime("%m/%d/%Y")
        if data["user_details"].get("date_of_birth", None)
        else None,
        "(Country of issue 1)": data["user_details"].get("country_of_issue", None),
        "id_document": data["user_details"].get("id_document", None),
        # Translator for Statement by Donor
        "(Name of translator)": "",
        "(ID number_2)": "",
        "(Languagedialect translated in)": "",
        # Donee details
        "(Full name as in ID_2)": donees[0]["entity_details"].get("name", None)
        if len(donees) >= 1
        else None,
        "(ID number_3)": donees[0]["entity_details"].get("id_number", None)
        if len(donees) >= 1
        else None,
        "(Country of issue)": donees[0]["entity_details"].get(
            "country_of_issue", None
        )
        if len(donees) >= 1
        else None,
        "(Date of birth ddmmyyyy)": parse(
            donees[0]["entity_details"].get("date_of_birth", None)
        ).strftime("%m/%d/%Y")
        if len(donees) >= 1 and donees[0]["entity_details"].get("date_of_birth", None)
        else None,
        "id_document_2": donees[0]["entity_details"].get("id_document", None)
        if len(donees) >= 1
        else None,
        # witness for donee 1
        "(Name of witness)": "",
        "(ID number_4)": "",
        "(Languagedialect translated in_2)": "",
        # Donee Details
        "(Full name as in ID_3)": donees[1]["entity_details"].get("name", None)
        if len(donees) > 1
        else None,
        "(ID number_5)": donees[1]["entity_details"].get("id_number", None)
        if len(donees) > 1
        else None,
        "(Country of issue_2)": donees[1]["entity_details"].get(
            "country_of_issue", None
        )
        if len(donees) > 1
        else None,
        "(Date of birth ddmmyyyy_2)": parse(
            donees[1]["entity_details"].get("date_of_birth", None)
        ).strftime("%m/%d/%Y")
        if len(donees) > 1
        else None,
        "id_document_2": donees[1]["entity_details"].get("id_document", None)
        if len(donees) > 1
        else None,
        # witness for donee 2
        "(Name of witness_2)": "",
        "(ID number_6)": "",
        "(Languagedialect translated in_3)": "",
        # replacement donee
        "(Full name as in ID_4)": replacement_donee[0]["entity_details"].get(
            "name", None
        )
        if replacement_donee
        else None,
        "(ID number_7)": replacement_donee[0]["entity_details"].get("id_number", None)
        if replacement_donee
        else None,
        "(Country of issue_3)": replacement_donee[0]["entity_details"].get(
            "country_of_issue", None
        )
        if replacement_donee
        else None,
        "(Date of birth ddmmyyyy_3)": parse(
            replacement_donee[0]["entity_details"].get("date_of_birth", None)
        ).strftime("%m/%d/%Y")
        if replacement_donee
        and replacement_donee[0]["entity_details"].get("date_of_birth", None)
        else None,
        "(undefined_10)": replacement_donee[0]["main_donee_details"][
            "entity_details"
        ]["name"]
        if replacement_donee
        and replacement_donee[0]["donee_powers"]["replacement_type"] == "(Named Donee"
        else None,
        "id_document_2": replacement_donee[0]["entity_details"].get(
            "id_document", None
        )
        if replacement_donee
        else None,
        # replacement donee witness
        "(Name of witness_3)": "",
        "(ID number_8)": "",
        "(Languagedialect translated in_4)": "",
        # residential property
        "(1)": "",
        "(2)": "",
        # money limitation
        "(within 1 calendar year)": "",
        # certificate issuer
        "(Full name as in ID_5)": "",
        "(MCRNRIC number)": "",
        "(Contact number)": "",
        "(Name of cliniclegal practice 1)": "",
        # donor details
        "(Text3)": data["user_details"].get("name", None),
        "(Text4)": data["user_details"].get("home_contact_number", None),
        "(Text5)": data["user_details"].get("office_contact_number", None),
        "(Text6)": data["user_details"].get("mobile_contact_number", None),
        "(Text7)": data["user_details"].get("email_address", None),
        "(Text8)": data["user_details"].get("address", None),
        "(Text9)": "",
        # donee1 details
        "(Text10)": donees[0]["entity_details"].get("name", None)
        if len(donees) >= 1
        else None,
        "(Text11)": donees[0]["entity_details"].get("home_contact_number", None)
        if len(donees) >= 1
        else None,
        "(Text12)": donees[0]["entity_details"].get("office_contact_number", None)
        if len(donees) >= 1
        else None,
        "(Text13)": donees[0]["entity_details"].get("mobile_contact_number", None)
        if len(donees) >= 1
        else None,
        "(Text14)": donees[0]["entity_details"].get("email_address", None)
        if len(donees) >= 1
        else None,
        "(Text15)": donees[0]["entity_details"].get("address", None)
        if len(donees) >= 1
        else None,
        "(Text16)": "",
        "(Text17)": donees[0]["entity_details"].get("relationship", None)
        if len(donees) >= 1
        and donees[0]["entity_details"].get("relationship", None) != "Other"
        else donees[0]["entity_details"].get("relationship_other", None)
        if len(donees) >= 1
        else None,
        # date of application
        "(Date4_af_date)": "",
        # donee2 details
        "(Text18)": donees[1]["entity_details"].get("name", None)
        if len(donees) > 1
        else None,
        "(Text19)": donees[1]["entity_details"].get("home_contact_number", None)
        if len(donees) > 1
        else None,
        "(Text20)": donees[1]["entity_details"].get("office_contact_number", None)
        if len(donees) > 1
        else None,
        "(Text21)": donees[1]["entity_details"].get("mobile_contact_number", None)
        if len(donees) > 1
        else None,
        "(Text22)": donees[1]["entity_details"].get("email_address", None)
        if len(donees) > 1
        else None,
        "(Text23)": donees[1]["entity_details"].get("address", None)
        if len(donees) > 1
        else None,
        "(Text24)": "",
        "(Text25)": donees[1]["entity_details"].get("relationship", None)
        if len(donees) > 1
        and donees[1]["entity_details"].get("relationship", None) != "Other"
        else donees[1]["entity_details"].get("relationship_other", None)
        if len(donees) > 1
        else None,
        # replacement donee details
        "(Text25A)": replacement_donee[0]["entity_details"].get("name", None)
        if replacement_donee
        else None,
        "(Text27)": replacement_donee[0]["entity_details"].get(
            "home_contact_number", None
        )
        if replacement_donee
        else None,
        "(Text26)": replacement_donee[0]["entity_details"].get(
            "office_contact_number", None
        )
        if replacement_donee
        else None,
        "(Text28)": replacement_donee[0]["entity_details"].get(
            "mobile_contact_number", None
        )
        if replacement_donee
        else None,
        "(Text29)": replacement_donee[0]["entity_details"].get("email_address", None)
        if replacement_donee
        else None,
        "(Text30)": replacement_donee[0]["entity_details"].get("address", None)
        if replacement_donee
        else None,
        "(Text31)": "",
        # collection of LPA
        "(Text32)": donees[0]["entity_details"].get("address", None)
        if len(donees) >= 1
        else None,
        "(Text33)": "",
        # Signature Box
        "(Text34)": "",
        "(Text35)": "",
        "(Text36)": "",
        "(Text38)": "",
        "(Text37)": "",
        # date signed
        "(Date5_af_date)": "",
        "(Date6_af_date)": "",
        "(Date7_af_date)": "",
        "(Date8_af_date)": "",
        "(Date9_af_date)": "",
    }

    checkbox_schema = {
        # translator is certificate issuer
        "(Donor_Translator)": False,
        # donee 1 powers
        "(Donee1Pwr_PW)": False,
        "(Donee1Pwr_PA)": False,
        "(Donee1Pwr_bth)": False,
        # donee 1 translator
        "(Donee1_translator)": False,
        # donee 2 translator
        "(Donee2_translator)": False,
        # donee 2 powers
        "(Donee2Pwr_PW)": False,
        "(Donee2Pwr_bth)": False,
        "(Donee2Pwr_PA)": False,
        # replacement donee
        "(Rdonee_any)": False,
        "(Rdonee_anypw)": False,
        "(Rdonee_anypa)": False,
        "(Rdonee_this)": False,
        # replacement donee translator
        "(RDonee_translator)": False,
        # powers personal welfare treatment
        "(3AbNo)": False,
        "(3AbYes)": False,
        # powers personal jointly
        "(3AcJ)": False,
        "(3Acjs)": False,
        # powers property
        "(3Bb)": False,
        # powers money restriction
        "(3Bcy2)": False,
        "(3Bcy1)": False,
        "(3Bcno)": False,
        # powers property jointly
        "(3BdJ)": False,
        "(3Bdjs)": False,
        # Applicant
        "(Check Box6)": False,
        "(Check Box7)": False,
        "(Check Box8)": False,
    }

    return {"textfield_schema": textfield_schema, "checkbox_schema": checkbox_schema}
