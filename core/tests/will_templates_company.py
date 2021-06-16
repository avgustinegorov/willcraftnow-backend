WILL_COMPANY_ALLOCATIONS_TITLE_BLOCK_TEMPLATE = """
COMPANY SHARES ALLOCATIONS
""".lstrip()


def WILL_COMPANY_1_ALLOCATIONS_BLOCK_TEMPLATE(*args):
    return """
    %(numbering)d.Subject to the payment of all my Expenses, I give 100.00%% of my interest in the {company_shares_amount} Ordinary Share(s) (being {company_percentage:.02f}%% of the total issued Ordinary Shares) of {company_name}, a Company Incorporated in Singapore with registration number {company_registration_number} ("{company_name} {company_registration_number}"), to {entity_1_name} (holder of NRIC No. {entity_1_nric}), residing at {entity_1_address} ("{entity_1_name}") absolutely and free from all encumbrances.
    """.strip()


def WILL_COMPANY_1_ALLOCATIONS_LT_100_BLOCK_TEMPLATE(*args):
    return """
    %(numbering)d.Subject to the payment of all my Expenses, I give {allocation_percentage:.2f}%% of my interest in the {company_shares_amount} Ordinary Share(s) (being {company_percentage:.02f}%% of the total issued Ordinary Shares) of {company_name}, a Company Incorporated in Singapore with registration number {company_registration_number} ("{company_name} {company_registration_number}"), to {entity_1_name} (holder of NRIC No. {entity_1_nric}), residing at {entity_1_address} ("{entity_1_name}") absolutely and free from all encumbrances, and the remainder shall be distributed as part of my Residual Estate.
    """.strip()


def WILL_COMPANY_2_ALLOCATIONS_BLOCK_TEMPLATE(*args):
    return """
    %(numbering)d.Subject to the payment of all my Expenses, I give my interest in the {company_shares_amount} Ordinary Share(s) (being {company_percentage:.02f}%% of the total issued Ordinary Shares) of {company_name}, a Company Incorporated in Singapore with registration number {company_registration_number} ("{company_name} {company_registration_number}"), to the following persons in the corresponding proportions:
    i.{allocation_percentage:.2f}%% to {entity_1_name} (holder of NRIC No. {entity_1_nric}), residing at {entity_1_address} ("{entity_1_name}") absolutely and free from all encumbrances; and
    ii.{allocation_percentage:.2f}%% to {entity_2_name} (holder of NRIC No. {entity_2_nric}), residing at {entity_2_address} ("{entity_2_name}") absolutely and free from all encumbrances (for the purpose of clauses %(numbering)d to %(numbering_plus_2)d, together with the named Beneficiaries in sub-clause i above, the ﬁMain Substitutesﬂ).
    """.strip()


def WILL_COMPANY_2_ALLOCATIONS_LT_100_BLOCK_TEMPLATE(*args):
    return """
    %(numbering)d.Subject to the payment of all my Expenses, I give my interest in the {company_shares_amount} Ordinary Share(s) (being {company_percentage:.02f}%% of the total issued Ordinary Shares) of {company_name}, a Company Incorporated in Singapore with registration number {company_registration_number} ("{company_name} {company_registration_number}"), to the following persons in the corresponding proportions:
    i.{allocation_percentage:.2f}%% to {entity_1_name} (holder of NRIC No. {entity_1_nric}), residing at {entity_1_address} ("{entity_1_name}") absolutely and free from all encumbrances;
    ii.{allocation_percentage:.2f}%% to {entity_2_name} (holder of NRIC No. {entity_2_nric}), residing at {entity_2_address} ("{entity_2_name}") absolutely and free from all encumbrances (for the purpose of clauses %(numbering)d to %(numbering_plus_2)d, together with the named Beneficiaries in sub-clause i above, the ﬁMain Substitutesﬂ); and
    iii.the remainder shall be distributed as part of my Residual Assets.
    """.strip()


def WILL_COMPANY_3_ALLOCATIONS_BLOCK_TEMPLATE(*args):
    return """
    %(numbering)d.Subject to the payment of all my Expenses, I give my interest in the {company_shares_amount} Ordinary Share(s) (being {company_percentage:.02f}%% of the total issued Ordinary Shares) of {company_name}, a Company Incorporated in Singapore with registration number {company_registration_number} ("{company_name} {company_registration_number}"), to the following persons in the corresponding proportions:
    i.{allocation_percentage:.2f}%% to {entity_1_name} (holder of NRIC No. {entity_1_nric}), residing at {entity_1_address} ("{entity_1_name}") absolutely and free from all encumbrances;
    ii.{allocation_percentage:.2f}%% to {entity_2_name} (holder of NRIC No. {entity_2_nric}), residing at {entity_2_address} ("{entity_2_name}") absolutely and free from all encumbrances;
    iii.{allocation_percentage:.2f}%% to {entity_3_name} (holder of NRIC No. {entity_3_nric}), residing at {entity_3_address} ("{entity_3_name}") absolutely and free from all encumbrances (for the purpose of clauses %(numbering)d to %(numbering_plus_3)d, together with the named Beneficiaries in sub-clauses i-ii above, the ﬁMain Substitutesﬂ); and
    iv.the remainder shall be distributed as part of my Residual Assets.
    """.strip()


WILL_COMPANY_3_ALLOCATIONS_LT_100_BLOCK_TEMPLATE = (
    WILL_COMPANY_3_ALLOCATIONS_BLOCK_TEMPLATE
)


def WILL_COMPANY_BENEFICIARY_1_DIES_BLOCK_TEMPLATE(num_beneficiaries, *args):
    return (
        """
    If {entity_1_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, then the interest in {company_name} {company_registration_number} which {entity_1_name} would otherwise have received under this Will shall be distributed equally amongst {entity_1_name}'s surviving issues absolutely and free from all encumbrances so long as they survive me for more than thirty (30) days
    """.strip()
        + (
            "."
            if num_beneficiaries == 1
            else """
    , and if {entity_1_name} does not have any issues who have survived me for more than thirty (30) days, then the same shall be distributed equally amongst all the Main Substitutes who have survived me for more than thirty (30) days.
    """
        ).strip()
    )


def WILL_COMPANY_BENEFICIARY_2_DIES_BLOCK_TEMPLATE(*args):
    return """
    If {entity_2_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, then the interest in {company_name} {company_registration_number} which {entity_2_name} would otherwise have received under this Will shall be distributed equally amongst {entity_2_name}'s surviving issues absolutely and free from all encumbrances so long as they survive me for more than thirty (30) days, and if {entity_2_name} does not have any issues who have survived me for more than thirty (30) days, then the same shall be distributed equally amongst all the Main Substitutes who have survived me for more than thirty (30) days.
    """.strip()


def WILL_COMPANY_BENEFICIARY_3_DIES_BLOCK_TEMPLATE(*args):
    return """
    If {entity_3_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, then the interest in {company_name} {company_registration_number} which {entity_3_name} would otherwise have received under this Will shall be distributed equally amongst {entity_3_name}'s surviving issues absolutely and free from all encumbrances so long as they survive me for more than thirty (30) days, and if {entity_3_name} does not have any issues who have survived me for more than thirty (30) days, then the same shall be distributed equally amongst all the Main Substitutes who have survived me for more than thirty (30) days.
    """.strip()


def WILL_1_SUB_BENEFICIARIES_COMPANY_BENEFICIARY_1_DIES_BLOCK_TEMPLATE(
    num_beneficiaries, *args
):
    return """
    If {entity_1_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, I give {sub_allocation_percentage:.2f}% of the interest in {company_name} {company_registration_number} which {entity_1_name} would otherwise have received under this Will (being {sub_entity_1_1_ea_pct:.2f}% of my total interest in the same) to {sub_entity_1_1_name} (holder of NRIC No. {sub_entity_1_1_nric}), residing at {sub_entity_1_1_address} ("{sub_entity_1_1_name}") absolutely and free from all encumbrances, provided always that if {sub_entity_1_1_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, then the same shall be distributed equally amongst {sub_entity_1_1_name}'s surviving issues absolutely and free from all encumbrances so long as they survive me for more than thirty (30) days
    """.strip() + (
        ".\n"
        if num_beneficiaries == 1
        else """
    , and if {sub_entity_1_1_name} does not have any issues who have survived me for more than thirty (30) days, then the same shall be distributed equally amongst all the Main Substitutes who have survived me for more than thirty (30) days.
    """.strip()
    )


def WILL_1_SUB_BENEFICIARIES_COMPANY_BENEFICIARY_1_DIES_LT_100_BLOCK_TEMPLATE(
    num_beneficiaries, *args
):
    return (
        """
    If {entity_1_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, I give {sub_allocation_percentage:.2f}% of the interest in {company_name} {company_registration_number} which {entity_1_name} would otherwise have received under this Will (being {sub_entity_1_1_ea_pct:.2f}% of my total interest in the same) to {sub_entity_1_1_name} (holder of NRIC No. {sub_entity_1_1_nric}), residing at {sub_entity_1_1_address} ("{sub_entity_1_1_name}") absolutely and free from all encumbrances, provided always that if {sub_entity_1_1_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, then the same shall be distributed equally amongst {sub_entity_1_1_name}'s surviving issues absolutely and free from all encumbrances so long as they survive me for more than thirty (30) days
    """.strip()
        + (
            ""
            if num_beneficiaries == 1
            else """
    , and if {sub_entity_1_1_name} does not have any issues who have survived me for more than thirty (30) days, then the same shall be distributed equally amongst all the Main Substitutes who have survived me for more than thirty (30) days
    """.strip()
        )
        + ", and the remainder shall be distributed as part of my Residual Assets."
        .strip()
    )


def WILL_1_SUB_BENEFICIARIES_COMPANY_BENEFICIARY_2_DIES_BLOCK_TEMPLATE(*args):
    return """
    If {entity_2_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, I give {sub_allocation_percentage:.2f}% of the interest in {company_name} {company_registration_number} which {entity_2_name} would otherwise have received under this Will (being {sub_entity_2_1_ea_pct:.2f}% of my total interest in the same) to {sub_entity_2_1_name} (holder of NRIC No. {sub_entity_2_1_nric}), residing at {sub_entity_2_1_address} ("{sub_entity_2_1_name}") absolutely and free from all encumbrances, provided always that if {sub_entity_2_1_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, then the same shall be distributed equally amongst {sub_entity_2_1_name}'s surviving issues absolutely and free from all encumbrances so long as they survive me for more than thirty (30) days, and if {sub_entity_2_1_name} does not have any issues who have survived me for more than thirty (30) days, then the same shall be distributed equally amongst all the Main Substitutes who have survived me for more than thirty (30) days.
    """.strip()


def WILL_1_SUB_BENEFICIARIES_COMPANY_BENEFICIARY_2_DIES_LT_100_BLOCK_TEMPLATE(*args):
    return """
    If {entity_2_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, I give {sub_allocation_percentage:.2f}% of the interest in {company_name} {company_registration_number} which {entity_2_name} would otherwise have received under this Will (being {sub_entity_2_1_ea_pct:.2f}% of my total interest in the same) to {sub_entity_2_1_name} (holder of NRIC No. {sub_entity_2_1_nric}), residing at {sub_entity_2_1_address} ("{sub_entity_2_1_name}") absolutely and free from all encumbrances, provided always that if {sub_entity_2_1_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, then the same shall be distributed equally amongst {sub_entity_2_1_name}'s surviving issues absolutely and free from all encumbrances so long as they survive me for more than thirty (30) days, and if {sub_entity_2_1_name} does not have any issues who have survived me for more than thirty (30) days, then the same shall be distributed equally amongst all the Main Substitutes who have survived me for more than thirty (30) days, and the remainder shall be distributed as part of my Residual Assets.
    """.strip()


def WILL_1_SUB_BENEFICIARIES_COMPANY_BENEFICIARY_3_DIES_BLOCK_TEMPLATE(*args):
    return """
    If {entity_3_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, I give {sub_allocation_percentage:.2f}% of the interest in {company_name} {company_registration_number} which {entity_3_name} would otherwise have received under this Will (being {sub_entity_3_1_ea_pct:.2f}% of my total interest in the same) to {sub_entity_3_1_name} (holder of NRIC No. {sub_entity_3_1_nric}), residing at {sub_entity_3_1_address} ("{sub_entity_3_1_name}") absolutely and free from all encumbrances, provided always that if {sub_entity_3_1_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, then the same shall be distributed equally amongst {sub_entity_3_1_name}'s surviving issues absolutely and free from all encumbrances so long as they survive me for more than thirty (30) days, and if {sub_entity_3_1_name} does not have any issues who have survived me for more than thirty (30) days, then the same shall be distributed equally amongst all the Main Substitutes who have survived me for more than thirty (30) days.
    """.strip()


def WILL_1_SUB_BENEFICIARIES_COMPANY_BENEFICIARY_3_DIES_LT_100_BLOCK_TEMPLATE(*args):
    return """
    If {entity_3_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, I give {sub_allocation_percentage:.2f}% of the interest in {company_name} {company_registration_number} which {entity_3_name} would otherwise have received under this Will (being {sub_entity_3_1_ea_pct:.2f}% of my total interest in the same) to {sub_entity_3_1_name} (holder of NRIC No. {sub_entity_3_1_nric}), residing at {sub_entity_3_1_address} ("{sub_entity_3_1_name}") absolutely and free from all encumbrances, provided always that if {sub_entity_3_1_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, then the same shall be distributed equally amongst {sub_entity_3_1_name}'s surviving issues absolutely and free from all encumbrances so long as they survive me for more than thirty (30) days, and if {sub_entity_3_1_name} does not have any issues who have survived me for more than thirty (30) days, then the same shall be distributed equally amongst all the Main Substitutes who have survived me for more than thirty (30) days, and the remainder shall be distributed as part of my Residual Assets.
    """.strip()


def WILL_2_SUB_BENEFICIARIES_COMPANY_BENEFICIARY_1_DIES_BLOCK_TEMPLATE(*args):
    return """
    If {entity_1_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, I give the interest in {company_name} {company_registration_number} which {entity_1_name} would otherwise have received under this Will, to the following persons in the corresponding proportions:
    i.{sub_allocation_percentage:.2f}% (being {sub_entity_1_1_ea_pct:.2f}% of my total interest in the same) to {sub_entity_1_1_name} (holder of NRIC No. {sub_entity_1_1_nric}), residing at {sub_entity_1_1_address} ("{sub_entity_1_1_name}") absolutely and free from all encumbrances; and
    ii.{sub_allocation_percentage:.2f}% (being {sub_entity_1_2_ea_pct:.2f}% of my total interest in the same) to {sub_entity_1_2_name} (holder of NRIC No. {sub_entity_1_2_nric}), residing at {sub_entity_1_2_address} ("{sub_entity_1_2_name}") absolutely and free from all encumbrances (for the purpose of this clause, together with the named Substitute Beneficiaries in sub-clause i above, the ﬁApplicable Substitutesﬂ).

    Provided Always that if any of the Applicable Substitutes, should die during my lifetime, or fail to survive me for more than thirty (30) days, then any gift devise or bequest of my interest in {company_name} {company_registration_number} which that Applicable Substitute would otherwise have received under this Will shall be distributed equally amongst the issues of that Applicable Substitute so long as they survive me for more than thirty (30) days, and if that Applicable Substitute does not have any issues who have survived me for more than thirty (30) days, then the same shall be distributed equally amongst all the Applicable Substitutes who have survived me for more than thirty (30) days.
    """.strip()


def WILL_2_SUB_BENEFICIARIES_COMPANY_BENEFICIARY_1_DIES_LT_100_BLOCK_TEMPLATE(*args):
    return """
    If {entity_1_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, I give the interest in {company_name} {company_registration_number} which {entity_1_name} would otherwise have received under this Will, to the following persons in the corresponding proportions:
    i.{sub_allocation_percentage:.2f}% (being {sub_entity_1_1_ea_pct:.2f}% of my total interest in the same) to {sub_entity_1_1_name} (holder of NRIC No. {sub_entity_1_1_nric}), residing at {sub_entity_1_1_address} ("{sub_entity_1_1_name}") absolutely and free from all encumbrances;
    ii.{sub_allocation_percentage:.2f}% (being {sub_entity_1_2_ea_pct:.2f}% of my total interest in the same) to {sub_entity_1_2_name} (holder of NRIC No. {sub_entity_1_2_nric}), residing at {sub_entity_1_2_address} ("{sub_entity_1_2_name}") absolutely and free from all encumbrances (for the purpose of this clause, together with the named Substitute Beneficiaries in sub-clause i above, the ﬁApplicable Substitutesﬂ); and
    iii.the remainder shall be distributed as part of my Residual Assets.

    Provided Always that if any of the Applicable Substitutes, should die during my lifetime, or fail to survive me for more than thirty (30) days, then any gift devise or bequest of my interest in {company_name} {company_registration_number} which that Applicable Substitute would otherwise have received under this Will shall be distributed equally amongst the issues of that Applicable Substitute so long as they survive me for more than thirty (30) days, and if that Applicable Substitute does not have any issues who have survived me for more than thirty (30) days, then the same shall be distributed equally amongst all the Applicable Substitutes who have survived me for more than thirty (30) days.
    """.strip()


def WILL_2_SUB_BENEFICIARIES_COMPANY_BENEFICIARY_2_DIES_BLOCK_TEMPLATE(*args):
    return """
    If {entity_2_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, I give the interest in {company_name} {company_registration_number} which {entity_2_name} would otherwise have received under this Will, to the following persons in the corresponding proportions:
    i.{sub_allocation_percentage:.2f}% (being {sub_entity_2_1_ea_pct:.2f}% of my total interest in the same) to {sub_entity_2_1_name} (holder of NRIC No. {sub_entity_2_1_nric}), residing at {sub_entity_2_1_address} ("{sub_entity_2_1_name}") absolutely and free from all encumbrances; and
    ii.{sub_allocation_percentage:.2f}% (being {sub_entity_2_2_ea_pct:.2f}% of my total interest in the same) to {sub_entity_2_2_name} (holder of NRIC No. {sub_entity_2_2_nric}), residing at {sub_entity_2_2_address} ("{sub_entity_2_2_name}") absolutely and free from all encumbrances (for the purpose of this clause, together with the named Substitute Beneficiaries in sub-clause i above, the ﬁApplicable Substitutesﬂ).

    Provided Always that if any of the Applicable Substitutes, should die during my lifetime, or fail to survive me for more than thirty (30) days, then any gift devise or bequest of my interest in {company_name} {company_registration_number} which that Applicable Substitute would otherwise have received under this Will shall be distributed equally amongst the issues of that Applicable Substitute so long as they survive me for more than thirty (30) days, and if that Applicable Substitute does not have any issues who have survived me for more than thirty (30) days, then the same shall be distributed equally amongst all the Applicable Substitutes who have survived me for more than thirty (30) days.
    """.strip()


def WILL_2_SUB_BENEFICIARIES_COMPANY_BENEFICIARY_2_DIES_LT_100_BLOCK_TEMPLATE(*args):
    return """
    If {entity_2_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, I give the interest in {company_name} {company_registration_number} which {entity_2_name} would otherwise have received under this Will, to the following persons in the corresponding proportions:
    i.{sub_allocation_percentage:.2f}% (being {sub_entity_2_1_ea_pct:.2f}% of my total interest in the same) to {sub_entity_2_1_name} (holder of NRIC No. {sub_entity_2_1_nric}), residing at {sub_entity_2_1_address} ("{sub_entity_2_1_name}") absolutely and free from all encumbrances;
    ii.{sub_allocation_percentage:.2f}% (being {sub_entity_2_2_ea_pct:.2f}% of my total interest in the same) to {sub_entity_2_2_name} (holder of NRIC No. {sub_entity_2_2_nric}), residing at {sub_entity_2_2_address} ("{sub_entity_2_2_name}") absolutely and free from all encumbrances (for the purpose of this clause, together with the named Substitute Beneficiaries in sub-clause i above, the ﬁApplicable Substitutesﬂ); and
    iii.the remainder shall be distributed as part of my Residual Assets.

    Provided Always that if any of the Applicable Substitutes, should die during my lifetime, or fail to survive me for more than thirty (30) days, then any gift devise or bequest of my interest in {company_name} {company_registration_number} which that Applicable Substitute would otherwise have received under this Will shall be distributed equally amongst the issues of that Applicable Substitute so long as they survive me for more than thirty (30) days, and if that Applicable Substitute does not have any issues who have survived me for more than thirty (30) days, then the same shall be distributed equally amongst all the Applicable Substitutes who have survived me for more than thirty (30) days.
    """.strip()


def WILL_2_SUB_BENEFICIARIES_COMPANY_BENEFICIARY_3_DIES_BLOCK_TEMPLATE(*args):
    return """
    If {entity_3_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, I give the interest in {company_name} {company_registration_number} which {entity_3_name} would otherwise have received under this Will, to the following persons in the corresponding proportions:
    i.{sub_allocation_percentage:.2f}% (being {sub_entity_3_1_ea_pct:.2f}% of my total interest in the same) to {sub_entity_3_1_name} (holder of NRIC No. {sub_entity_3_1_nric}), residing at {sub_entity_3_1_address} ("{sub_entity_3_1_name}") absolutely and free from all encumbrances; and
    ii.{sub_allocation_percentage:.2f}% (being {sub_entity_3_2_ea_pct:.2f}% of my total interest in the same) to {sub_entity_3_2_name} (holder of NRIC No. {sub_entity_3_2_nric}), residing at {sub_entity_3_2_address} ("{sub_entity_3_2_name}") absolutely and free from all encumbrances (for the purpose of this clause, together with the named Substitute Beneficiaries in sub-clause i above, the ﬁApplicable Substitutesﬂ).

    Provided Always that if any of the Applicable Substitutes, should die during my lifetime, or fail to survive me for more than thirty (30) days, then any gift devise or bequest of my interest in {company_name} {company_registration_number} which that Applicable Substitute would otherwise have received under this Will shall be distributed equally amongst the issues of that Applicable Substitute so long as they survive me for more than thirty (30) days, and if that Applicable Substitute does not have any issues who have survived me for more than thirty (30) days, then the same shall be distributed equally amongst all the Applicable Substitutes who have survived me for more than thirty (30) days.
    """.strip()


def WILL_2_SUB_BENEFICIARIES_COMPANY_BENEFICIARY_3_DIES_LT_100_BLOCK_TEMPLATE(*args):
    return """
    If {entity_3_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, I give the interest in {company_name} {company_registration_number} which {entity_3_name} would otherwise have received under this Will, to the following persons in the corresponding proportions:
    i.{sub_allocation_percentage:.2f}% (being {sub_entity_3_1_ea_pct:.2f}% of my total interest in the same) to {sub_entity_3_1_name} (holder of NRIC No. {sub_entity_3_1_nric}), residing at {sub_entity_3_1_address} ("{sub_entity_3_1_name}") absolutely and free from all encumbrances;
    ii.{sub_allocation_percentage:.2f}% (being {sub_entity_3_2_ea_pct:.2f}% of my total interest in the same) to {sub_entity_3_2_name} (holder of NRIC No. {sub_entity_3_2_nric}), residing at {sub_entity_3_2_address} ("{sub_entity_3_2_name}") absolutely and free from all encumbrances (for the purpose of this clause, together with the named Substitute Beneficiaries in sub-clause i above, the ﬁApplicable Substitutesﬂ); and
    iii.the remainder shall be distributed as part of my Residual Assets.

    Provided Always that if any of the Applicable Substitutes, should die during my lifetime, or fail to survive me for more than thirty (30) days, then any gift devise or bequest of my interest in {company_name} {company_registration_number} which that Applicable Substitute would otherwise have received under this Will shall be distributed equally amongst the issues of that Applicable Substitute so long as they survive me for more than thirty (30) days, and if that Applicable Substitute does not have any issues who have survived me for more than thirty (30) days, then the same shall be distributed equally amongst all the Applicable Substitutes who have survived me for more than thirty (30) days.
    """.strip()


def WILL_3_SUB_BENEFICIARIES_COMPANY_BENEFICIARY_1_DIES_BLOCK_TEMPLATE(*args):
    return """
    If {entity_1_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, I give the interest in {company_name} {company_registration_number} which {entity_1_name} would otherwise have received under this Will, to the following persons in the corresponding proportions:
    i.{sub_allocation_percentage:.2f}% (being {sub_entity_1_1_ea_pct:.2f}% of my total interest in the same) to {sub_entity_1_1_name} (holder of NRIC No. {sub_entity_1_1_nric}), residing at {sub_entity_1_1_address} ("{sub_entity_1_1_name}") absolutely and free from all encumbrances;
    ii.{sub_allocation_percentage:.2f}% (being {sub_entity_1_2_ea_pct:.2f}% of my total interest in the same) to {sub_entity_1_2_name} (holder of NRIC No. {sub_entity_1_2_nric}), residing at {sub_entity_1_2_address} ("{sub_entity_1_2_name}") absolutely and free from all encumbrances;
    iii.{sub_allocation_percentage:.2f}% (being {sub_entity_1_3_ea_pct:.2f}% of my total interest in the same) to {sub_entity_1_3_name} (holder of NRIC No. {sub_entity_1_3_nric}), residing at {sub_entity_1_3_address} ("{sub_entity_1_3_name}") absolutely and free from all encumbrances (for the purpose of this clause, together with the named Substitute Beneficiaries in sub-clauses i-ii above, the ﬁApplicable Substitutesﬂ); and
    iv.the remainder shall be distributed as part of my Residual Assets.
    Provided Always that if any of the Applicable Substitutes, should die during my lifetime, or fail to survive me for more than thirty (30) days, then any gift devise or bequest of my interest in {company_name} {company_registration_number} which that Applicable Substitute would otherwise have received under this Will shall be distributed equally amongst the issues of that Applicable Substitute so long as they survive me for more than thirty (30) days, and if that Applicable Substitute does not have any issues who have survived me for more than thirty (30) days, then the same shall be distributed equally amongst all the Applicable Substitutes who have survived me for more than thirty (30) days.
    """.strip()


WILL_3_SUB_BENEFICIARIES_COMPANY_BENEFICIARY_1_DIES_LT_100_BLOCK_TEMPLATE = (
    WILL_3_SUB_BENEFICIARIES_COMPANY_BENEFICIARY_1_DIES_BLOCK_TEMPLATE
)


def WILL_3_SUB_BENEFICIARIES_COMPANY_BENEFICIARY_2_DIES_BLOCK_TEMPLATE(*args):
    return """
    If {entity_2_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, I give the interest in {company_name} {company_registration_number} which {entity_2_name} would otherwise have received under this Will, to the following persons in the corresponding proportions:
    i.{sub_allocation_percentage:.2f}% (being {sub_entity_2_1_ea_pct:.2f}% of my total interest in the same) to {sub_entity_2_1_name} (holder of NRIC No. {sub_entity_2_1_nric}), residing at {sub_entity_2_1_address} ("{sub_entity_2_1_name}") absolutely and free from all encumbrances;
    ii.{sub_allocation_percentage:.2f}% (being {sub_entity_2_2_ea_pct:.2f}% of my total interest in the same) to {sub_entity_2_2_name} (holder of NRIC No. {sub_entity_2_2_nric}), residing at {sub_entity_2_2_address} ("{sub_entity_2_2_name}") absolutely and free from all encumbrances;
    iii.{sub_allocation_percentage:.2f}% (being {sub_entity_2_3_ea_pct:.2f}% of my total interest in the same) to {sub_entity_2_3_name} (holder of NRIC No. {sub_entity_2_3_nric}), residing at {sub_entity_2_3_address} ("{sub_entity_2_3_name}") absolutely and free from all encumbrances (for the purpose of this clause, together with the named Substitute Beneficiaries in sub-clauses i-ii above, the ﬁApplicable Substitutesﬂ); and
    iv.the remainder shall be distributed as part of my Residual Assets.
    Provided Always that if any of the Applicable Substitutes, should die during my lifetime, or fail to survive me for more than thirty (30) days, then any gift devise or bequest of my interest in {company_name} {company_registration_number} which that Applicable Substitute would otherwise have received under this Will shall be distributed equally amongst the issues of that Applicable Substitute so long as they survive me for more than thirty (30) days, and if that Applicable Substitute does not have any issues who have survived me for more than thirty (30) days, then the same shall be distributed equally amongst all the Applicable Substitutes who have survived me for more than thirty (30) days.
    """.strip()


WILL_3_SUB_BENEFICIARIES_COMPANY_BENEFICIARY_2_DIES_LT_100_BLOCK_TEMPLATE = (
    WILL_3_SUB_BENEFICIARIES_COMPANY_BENEFICIARY_2_DIES_BLOCK_TEMPLATE
)


def WILL_3_SUB_BENEFICIARIES_COMPANY_BENEFICIARY_3_DIES_BLOCK_TEMPLATE(*args):
    return """
    If {entity_3_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, I give the interest in {company_name} {company_registration_number} which {entity_3_name} would otherwise have received under this Will, to the following persons in the corresponding proportions:
    i.{sub_allocation_percentage:.2f}% (being {sub_entity_3_1_ea_pct:.2f}% of my total interest in the same) to {sub_entity_3_1_name} (holder of NRIC No. {sub_entity_3_1_nric}), residing at {sub_entity_3_1_address} ("{sub_entity_3_1_name}") absolutely and free from all encumbrances;
    ii.{sub_allocation_percentage:.2f}% (being {sub_entity_3_2_ea_pct:.2f}% of my total interest in the same) to {sub_entity_3_2_name} (holder of NRIC No. {sub_entity_3_2_nric}), residing at {sub_entity_3_2_address} ("{sub_entity_3_2_name}") absolutely and free from all encumbrances;
    iii.{sub_allocation_percentage:.2f}% (being {sub_entity_3_3_ea_pct:.2f}% of my total interest in the same) to {sub_entity_3_3_name} (holder of NRIC No. {sub_entity_3_3_nric}), residing at {sub_entity_3_3_address} ("{sub_entity_3_3_name}") absolutely and free from all encumbrances (for the purpose of this clause, together with the named Substitute Beneficiaries in sub-clauses i-ii above, the ﬁApplicable Substitutesﬂ); and
    iv.the remainder shall be distributed as part of my Residual Assets.
    Provided Always that if any of the Applicable Substitutes, should die during my lifetime, or fail to survive me for more than thirty (30) days, then any gift devise or bequest of my interest in {company_name} {company_registration_number} which that Applicable Substitute would otherwise have received under this Will shall be distributed equally amongst the issues of that Applicable Substitute so long as they survive me for more than thirty (30) days, and if that Applicable Substitute does not have any issues who have survived me for more than thirty (30) days, then the same shall be distributed equally amongst all the Applicable Substitutes who have survived me for more than thirty (30) days.
    """.strip()


WILL_3_SUB_BENEFICIARIES_COMPANY_BENEFICIARY_3_DIES_LT_100_BLOCK_TEMPLATE = (
    WILL_3_SUB_BENEFICIARIES_COMPANY_BENEFICIARY_3_DIES_BLOCK_TEMPLATE
)
