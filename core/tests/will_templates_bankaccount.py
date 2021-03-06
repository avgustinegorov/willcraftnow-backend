WILL_BANK_ACCOUNT_ALLOCATIONS_TITLE_BLOCK_TEMPLATE = """
BANK ACCOUNT ALLOCATIONS
"""

WILL_BANK_ACCOUNT_1_AMOUNT_ALLOCATIONS_BLOCK_TEMPLATE = """
%(numbering)d.Subject to the payment of all my Expenses, I give ${allocation_amount:.2f} from the Bank Account held with {bank_name} with account number {bank_account_number} ("{bank_name} {bank_account_number}"), to {entity_1_name} (holder of NRIC No. {entity_1_nric}), residing at {entity_1_address} ("{entity_1_name}") absolutely and free from all encumbrances.
"""


def WILL_BANK_ACCOUNT_1_ALLOCATIONS_BLOCK_TEMPLATE(has_amount_allocation):
    return (
        "%(numbering)d."
        + (
            "Subject to clauses %(numbering_minus_beneficiaries)d to"
            " %(numbering_minus_1)d, and "
            if has_amount_allocation
            else "Subject "
        )
        + """
    to the payment of all my Expenses, I give 100.00%% of my interest in the Bank Account held with {bank_name} with account number {bank_account_number} ("{bank_name} {bank_account_number}"), to {entity_1_name}
    """
        + (
            ""
            if has_amount_allocation
            else " "
            + """
    (holder of NRIC No. {entity_1_nric}), residing at {entity_1_address} ("{entity_1_name}")
    """
        )
        + " "
        + """
    absolutely and free from all encumbrances.
    """.strip()
    )


def WILL_BANK_ACCOUNT_1_ALLOCATIONS_LT_100_BLOCK_TEMPLATE(has_amount_allocation):
    return (
        "%(numbering)d."
        + (
            "Subject to clauses %(numbering_minus_beneficiaries)d to"
            " %(numbering_minus_1)d, and "
            if has_amount_allocation
            else "Subject "
        )
        + """
    to the payment of all my Expenses, I give {allocation_percentage:.2f}%% of my interest in the Bank Account held with {bank_name} with account number {bank_account_number} ("{bank_name} {bank_account_number}"), to {entity_1_name}
    """
        + (
            ""
            if has_amount_allocation
            else " "
            + """
    (holder of NRIC No. {entity_1_nric}), residing at {entity_1_address} ("{entity_1_name}")
    """
        )
        + " "
        + """
    absolutely and free from all encumbrances, and the remainder shall be distributed as part of my Residual Estate.
    """.strip()
    )


def WILL_BANK_ACCOUNT_2_ALLOCATIONS_BLOCK_TEMPLATE(has_amount_allocation):
    return (
        "%(numbering)d."
        + (
            "Subject to clauses %(numbering_minus_beneficiaries)d to"
            " %(numbering_minus_1)d, and "
            if has_amount_allocation
            else "Subject "
        )
        + """
    to the payment of all my Expenses, I give my interest in the Bank Account held with {bank_name} with account number {bank_account_number} ("{bank_name} {bank_account_number}"), to the following persons in the corresponding proportions: i.{allocation_percentage:.2f}%% to {entity_1_name}
    """
        + (
            ""
            if has_amount_allocation
            else " "
            + """
    (holder of NRIC No. {entity_1_nric}), residing at {entity_1_address} ("{entity_1_name}")
    """
        )
        + " "
        + """
    absolutely and free from all encumbrances; and
    ii.{allocation_percentage:.2f}%% to {entity_2_name}
    """
        + (
            ""
            if has_amount_allocation
            else " "
            + """
    (holder of NRIC No. {entity_2_nric}), residing at {entity_2_address} ("{entity_2_name}")
    """
        )
        + " "
        + """
    absolutely and free from all encumbrances (for the purpose of clauses %(numbering)d to %(numbering_plus_2)d, together with the named Beneficiaries in sub-clause i above, the ???Main Substitutes???).
    """.strip()
    )


def WILL_BANK_ACCOUNT_2_ALLOCATIONS_LT_100_BLOCK_TEMPLATE(has_amount_allocation):
    return (
        "%(numbering)d."
        + (
            "Subject to clauses %(numbering_minus_beneficiaries)d to"
            " %(numbering_minus_1)d, and "
            if has_amount_allocation
            else "Subject "
        )
        + """
    to the payment of all my Expenses, I give my interest in the Bank Account held with {bank_name} with account number {bank_account_number} ("{bank_name} {bank_account_number}"), to the following persons in the corresponding proportions:
    i.{allocation_percentage:.2f}%% to {entity_1_name}
    """
        + (
            ""
            if has_amount_allocation
            else " "
            + """
    (holder of NRIC No. {entity_1_nric}), residing at {entity_1_address} ("{entity_1_name}")
    """
        )
        + " "
        + """
    absolutely and free from all encumbrances;
    ii.{allocation_percentage:.2f}%% to {entity_2_name}
    """
        + (
            ""
            if has_amount_allocation
            else " "
            + """
    (holder of NRIC No. {entity_2_nric}), residing at {entity_2_address} ("{entity_2_name}")
    """
        )
        + " "
        + """
    absolutely and free from all encumbrances (for the purpose of clauses %(numbering)d to %(numbering_plus_2)d, together with the named Beneficiaries in sub-clause i above, the ???Main Substitutes???); and
    iii.the remainder shall be distributed as part of my Residual Assets.
    """.strip()
    )


WILL_BANK_ACCOUNT_2_AMOUNT_ALLOCATIONS_BLOCK_TEMPLATE = """
%(numbering)d.Subject to the payment of all my Expenses, I give the following amounts from the Bank Account held with {bank_name} with account number {bank_account_number} ("{bank_name} {bank_account_number}"), to the following persons in the corresponding proportions:
i.${allocation_amount:.2f} to {entity_1_name} (holder of NRIC No. {entity_1_nric}), residing at {entity_1_address} ("{entity_1_name}") absolutely and free from all encumbrances; and
ii.${allocation_amount:.2f} to {entity_2_name} (holder of NRIC No. {entity_2_nric}), residing at {entity_2_address} ("{entity_2_name}") absolutely and free from all encumbrances (for the purpose of clauses %(numbering)d to %(numbering_plus_2)d, together with the named Beneficiaries in sub-clause i above, the ???Main Substitutes???).
""".strip()


def WILL_BANK_ACCOUNT_3_ALLOCATIONS_BLOCK_TEMPLATE(has_amount_allocation):
    return (
        "%(numbering)d."
        + (
            "Subject to clauses %(numbering_minus_beneficiaries)d to"
            " %(numbering_minus_1)d, and "
            if has_amount_allocation
            else "Subject "
        )
        + """
    to the payment of all my Expenses, I give my interest in the Bank Account held with {bank_name} with account number {bank_account_number} ("{bank_name} {bank_account_number}"), to the following persons in the corresponding proportions:
    i.{allocation_percentage:.2f}%% to {entity_1_name}
    """
        + (
            ""
            if has_amount_allocation
            else " "
            + """
    (holder of NRIC No. {entity_1_nric}), residing at {entity_1_address} ("{entity_1_name}")
    """
        )
        + " "
        + """
    absolutely and free from all encumbrances;
    ii.{allocation_percentage:.2f}%% to {entity_2_name}
    """
        + (
            ""
            if has_amount_allocation
            else " "
            + """
    (holder of NRIC No. {entity_2_nric}), residing at {entity_2_address} ("{entity_2_name}")
    """
        )
        + " "
        + """
    absolutely and free from all encumbrances;
    iii.{allocation_percentage:.2f}%% to {entity_3_name}
    """
        + (
            ""
            if has_amount_allocation
            else " "
            + """
    (holder of NRIC No. {entity_3_nric}), residing at {entity_3_address} ("{entity_3_name}")
    """
        )
        + " "
        + """
    absolutely and free from all encumbrances (for the purpose of clauses %(numbering)d to %(numbering_plus_3)d, together with the named Beneficiaries in sub-clauses i-ii above, the ???Main Substitutes???); and
    iv.the remainder shall be distributed as part of my Residual Assets.
    """.strip()
    )


WILL_BANK_ACCOUNT_3_ALLOCATIONS_LT_100_BLOCK_TEMPLATE = (
    WILL_BANK_ACCOUNT_3_ALLOCATIONS_BLOCK_TEMPLATE
)

WILL_BANK_ACCOUNT_3_AMOUNT_ALLOCATIONS_BLOCK_TEMPLATE = """
%(numbering)d.Subject to the payment of all my Expenses, I give the following amounts from the Bank Account held with {bank_name} with account number {bank_account_number} ("{bank_name} {bank_account_number}"), to the following persons in the corresponding proportions:
i.${allocation_amount:.2f} to {entity_1_name} (holder of NRIC No. {entity_1_nric}), residing at {entity_1_address} ("{entity_1_name}") absolutely and free from all encumbrances;
ii.${allocation_amount:.2f} to {entity_2_name} (holder of NRIC No. {entity_2_nric}), residing at {entity_2_address} ("{entity_2_name}") absolutely and free from all encumbrances; and
iii.${allocation_amount:.2f} to {entity_3_name} (holder of NRIC No. {entity_3_nric}), residing at {entity_3_address} ("{entity_3_name}") absolutely and free from all encumbrances (for the purpose of clauses %(numbering)d to %(numbering_plus_3)d, together with the named Beneficiaries in sub-clauses i-ii above, the ???Main Substitutes???).
""".strip()


def WILL_BANK_ACCOUNT_BENEFICIARY_1_DIES_BLOCK_TEMPLATE(num_beneficiaries, *args):
    return (
        """
    If {entity_1_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, then the interest in {bank_name} {bank_account_number} which {entity_1_name} would otherwise have received under this Will shall be distributed equally amongst {entity_1_name}'s surviving issues absolutely and free from all encumbrances so long as they survive me for more than thirty (30) days
    """.strip()
        + (
            ".\n"
            if num_beneficiaries == 1
            else """
    , and if {entity_1_name} does not have any issues who have survived me for more than thirty (30) days, then the same shall be distributed equally amongst all the Main Substitutes who have survived me for more than thirty (30) days.
    """
        ).strip()
    )


def WILL_BANK_ACCOUNT_AMOUNT_BENEFICIARY_1_DIES_BLOCK_TEMPLATE(
    num_beneficiaries, *args
):
    return (
        """
    If {entity_1_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, then the amount in {bank_name} {bank_account_number} which {entity_1_name} would otherwise have received under this Will shall be distributed equally amongst {entity_1_name}'s surviving issues absolutely and free from all encumbrances so long as they survive me for more than thirty (30) days
    """.strip()
        + (
            ".\n"
            if num_beneficiaries == 1
            else """
    , and if {entity_1_name} does not have any issues who have survived me for more than thirty (30) days, then the same shall be distributed equally amongst all the Main Substitutes who have survived me for more than thirty (30) days.
    """
        ).strip()
    )


def WILL_BANK_ACCOUNT_BENEFICIARY_2_DIES_BLOCK_TEMPLATE(*args):
    return """
    If {entity_2_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, then the interest in {bank_name} {bank_account_number} which {entity_2_name} would otherwise have received under this Will shall be distributed equally amongst {entity_2_name}'s surviving issues absolutely and free from all encumbrances so long as they survive me for more than thirty (30) days, and if {entity_2_name} does not have any issues who have survived me for more than thirty (30) days, then the same shall be distributed equally amongst all the Main Substitutes who have survived me for more than thirty (30) days.
    """.strip()


def WILL_BANK_ACCOUNT_AMOUNT_BENEFICIARY_2_DIES_BLOCK_TEMPLATE(*args):
    return """
    If {entity_2_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, then the amount in {bank_name} {bank_account_number} which {entity_2_name} would otherwise have received under this Will shall be distributed equally amongst {entity_2_name}'s surviving issues absolutely and free from all encumbrances so long as they survive me for more than thirty (30) days, and if {entity_2_name} does not have any issues who have survived me for more than thirty (30) days, then the same shall be distributed equally amongst all the Main Substitutes who have survived me for more than thirty (30) days.
    """.strip()


def WILL_BANK_ACCOUNT_BENEFICIARY_3_DIES_BLOCK_TEMPLATE(*args):
    return """
    If {entity_3_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, then the interest in {bank_name} {bank_account_number} which {entity_3_name} would otherwise have received under this Will shall be distributed equally amongst {entity_3_name}'s surviving issues absolutely and free from all encumbrances so long as they survive me for more than thirty (30) days, and if {entity_3_name} does not have any issues who have survived me for more than thirty (30) days, then the same shall be distributed equally amongst all the Main Substitutes who have survived me for more than thirty (30) days.
    """.strip()


def WILL_BANK_ACCOUNT_AMOUNT_BENEFICIARY_3_DIES_BLOCK_TEMPLATE(*args):
    return """
    If {entity_3_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, then the amount in {bank_name} {bank_account_number} which {entity_3_name} would otherwise have received under this Will shall be distributed equally amongst {entity_3_name}'s surviving issues absolutely and free from all encumbrances so long as they survive me for more than thirty (30) days, and if {entity_3_name} does not have any issues who have survived me for more than thirty (30) days, then the same shall be distributed equally amongst all the Main Substitutes who have survived me for more than thirty (30) days.
    """.strip()


def WILL_3_SUB_BENEFICIARIES_BANK_ACCOUNT_BENEFICIARY_1_DIES_BLOCK_TEMPLATE(
    num_beneficiaries, has_amount_allocation
):
    return (
        """
    If {entity_1_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, I give the interest in {bank_name} {bank_account_number} which {entity_1_name} would otherwise have received under this Will, to the following persons in the corresponding proportions:
    i.{sub_allocation_percentage:.02f}% (being {sub_entity_1_1_ea_pct:.02f}% of my total interest in the same) to {sub_entity_1_1_name}
    """.strip()
        + (
            ""
            if has_amount_allocation
            else " "
            + """
    (holder of NRIC No. {sub_entity_1_1_nric}), residing at {sub_entity_1_1_address} ("{sub_entity_1_1_name}")
    """
        )
        + " "
        + """
    absolutely and free from all encumbrances;
    ii.{sub_allocation_percentage:.02f}% (being {sub_entity_1_2_ea_pct:.02f}% of my total interest in the same) to {sub_entity_1_2_name}
    """
        + (
            ""
            if has_amount_allocation
            else " "
            + """
    (holder of NRIC No. {sub_entity_1_2_nric}), residing at {sub_entity_1_2_address} ("{sub_entity_1_2_name}")
    """
        )
        + " "
        + """
    absolutely and free from all encumbrances;
    iii.{sub_allocation_percentage:.02f}% (being {sub_entity_1_3_ea_pct:.02f}% of my total interest in the same) to {sub_entity_1_3_name}
    """
        + (
            ""
            if has_amount_allocation
            else " "
            + """
    (holder of NRIC No. {sub_entity_1_3_nric}), residing at {sub_entity_1_3_address} ("{sub_entity_1_3_name}")
    """
        )
        + " "
        + """
    absolutely and free from all encumbrances (for the purpose of this clause, together with the named Substitute Beneficiaries in sub-clauses i-ii above, the ???Applicable Substitutes???); and
    iv.the remainder shall be distributed as part of my Residual Assets.

    Provided Always that if any of the Applicable Substitutes, should die during my lifetime, or fail to survive me for more than thirty (30) days, then any gift devise or bequest of my interest in {bank_name} {bank_account_number} which that Applicable Substitute would otherwise have received under this Will shall be distributed equally amongst the issues of that Applicable Substitute so long as they survive me for more than thirty (30) days, and if that Applicable Substitute does not have any issues who have survived me for more than thirty (30) days, then the same shall be distributed equally amongst all the Applicable Substitutes who have survived me for more than thirty (30) days.
    """.strip()
    )


WILL_3_SUB_BENEFICIARIES_BANK_ACCOUNT_BENEFICIARY_1_DIES_LT_100_BLOCK_TEMPLATE = (
    WILL_3_SUB_BENEFICIARIES_BANK_ACCOUNT_BENEFICIARY_1_DIES_BLOCK_TEMPLATE
)


def WILL_3_SUB_BENEFICIARIES_BANK_ACCOUNT_AMOUNT_BENEFICIARY_1_DIES_BLOCK_TEMPLATE(
    *args,
):
    return """
    If {entity_1_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, I give the amount in {bank_name} {bank_account_number} which {entity_1_name} would otherwise have received under this Will, to the following persons in the corresponding proportions:
    i.${sub_allocation_amount:.2f} to {sub_entity_1_1_name} (holder of NRIC No. {sub_entity_1_1_nric}), residing at {sub_entity_1_1_address} ("{sub_entity_1_1_name}") absolutely and free from all encumbrances;
    ii.${sub_allocation_amount:.2f} to {sub_entity_1_2_name} (holder of NRIC No. {sub_entity_1_2_nric}), residing at {sub_entity_1_2_address} ("{sub_entity_1_2_name}") absolutely and free from all encumbrances; and
    iii.${sub_allocation_amount:.2f} to {sub_entity_1_3_name} (holder of NRIC No. {sub_entity_1_3_nric}), residing at {sub_entity_1_3_address} ("{sub_entity_1_3_name}") absolutely and free from all encumbrances (for the purpose of this clause, together with the named Substitute Beneficiaries in sub-clauses i-ii above, the ???Applicable Substitutes???).
    Provided Always that if any of the Applicable Substitutes, should die during my lifetime, or fail to survive me for more than thirty (30) days, then any gift devise or bequest of my amount in {bank_name} {bank_account_number} which that Applicable Substitute would otherwise have received under this Will shall be distributed equally amongst the issues of that Applicable Substitute so long as they survive me for more than thirty (30) days, and if that Applicable Substitute does not have any issues who have survived me for more than thirty (30) days, then the same shall be distributed equally amongst all the Applicable Substitutes who have survived me for more than thirty (30) days.
    """.strip()


def WILL_3_SUB_BENEFICIARIES_BANK_ACCOUNT_BENEFICIARY_2_DIES_BLOCK_TEMPLATE(
    num_beneficiaries, has_amount_allocation
):
    return (
        """
    If {entity_2_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, I give the interest in {bank_name} {bank_account_number} which {entity_2_name} would otherwise have received under this Will, to the following persons in the corresponding proportions:
    i.{sub_allocation_percentage:.02f}% (being {sub_entity_2_1_ea_pct:.02f}% of my total interest in the same) to {sub_entity_2_1_name}
    """.strip()
        + (
            ""
            if has_amount_allocation
            else " "
            + """
    (holder of NRIC No. {sub_entity_2_1_nric}), residing at {sub_entity_2_1_address} ("{sub_entity_2_1_name}")
    """
        )
        + " "
        + """
    absolutely and free from all encumbrances;
    ii.{sub_allocation_percentage:.02f}% (being {sub_entity_2_2_ea_pct:.02f}% of my total interest in the same) to {sub_entity_2_2_name}
    """
        + (
            ""
            if has_amount_allocation
            else " "
            + """
    (holder of NRIC No. {sub_entity_2_2_nric}), residing at {sub_entity_2_2_address} ("{sub_entity_2_2_name}")
    """
        )
        + " "
        + """
    absolutely and free from all encumbrances;
    iii.{sub_allocation_percentage:.02f}% (being {sub_entity_2_3_ea_pct:.02f}% of my total interest in the same) to {sub_entity_2_3_name}
    """
        + (
            ""
            if has_amount_allocation
            else " "
            + """
    (holder of NRIC No. {sub_entity_2_3_nric}), residing at {sub_entity_2_3_address} ("{sub_entity_2_3_name}")
    """
        )
        + " "
        + """
    absolutely and free from all encumbrances (for the purpose of this clause, together with the named Substitute Beneficiaries in sub-clauses i-ii above, the ???Applicable Substitutes???); and
    iv.the remainder shall be distributed as part of my Residual Assets.

    Provided Always that if any of the Applicable Substitutes, should die during my lifetime, or fail to survive me for more than thirty (30) days, then any gift devise or bequest of my interest in {bank_name} {bank_account_number} which that Applicable Substitute would otherwise have received under this Will shall be distributed equally amongst the issues of that Applicable Substitute so long as they survive me for more than thirty (30) days, and if that Applicable Substitute does not have any issues who have survived me for more than thirty (30) days, then the same shall be distributed equally amongst all the Applicable Substitutes who have survived me for more than thirty (30) days.
    """.strip()
    )


WILL_3_SUB_BENEFICIARIES_BANK_ACCOUNT_BENEFICIARY_2_DIES_LT_100_BLOCK_TEMPLATE = (
    WILL_3_SUB_BENEFICIARIES_BANK_ACCOUNT_BENEFICIARY_2_DIES_BLOCK_TEMPLATE
)


def WILL_3_SUB_BENEFICIARIES_BANK_ACCOUNT_AMOUNT_BENEFICIARY_2_DIES_BLOCK_TEMPLATE(
    *args,
):
    return """
    If {entity_2_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, I give the amount in {bank_name} {bank_account_number} which {entity_2_name} would otherwise have received under this Will, to the following persons in the corresponding proportions:
    i.${sub_allocation_amount:.2f} to {sub_entity_2_1_name} (holder of NRIC No. {sub_entity_2_1_nric}), residing at {sub_entity_2_1_address} ("{sub_entity_2_1_name}") absolutely and free from all encumbrances;
    ii.${sub_allocation_amount:.2f} to {sub_entity_2_2_name} (holder of NRIC No. {sub_entity_2_2_nric}), residing at {sub_entity_2_2_address} ("{sub_entity_2_2_name}") absolutely and free from all encumbrances; and
    iii.${sub_allocation_amount:.2f} to {sub_entity_2_3_name} (holder of NRIC No. {sub_entity_2_3_nric}), residing at {sub_entity_2_3_address} ("{sub_entity_2_3_name}") absolutely and free from all encumbrances (for the purpose of this clause, together with the named Substitute Beneficiaries in sub-clauses i-ii above, the ???Applicable Substitutes???).
    Provided Always that if any of the Applicable Substitutes, should die during my lifetime, or fail to survive me for more than thirty (30) days, then any gift devise or bequest of my amount in {bank_name} {bank_account_number} which that Applicable Substitute would otherwise have received under this Will shall be distributed equally amongst the issues of that Applicable Substitute so long as they survive me for more than thirty (30) days, and if that Applicable Substitute does not have any issues who have survived me for more than thirty (30) days, then the same shall be distributed equally amongst all the Applicable Substitutes who have survived me for more than thirty (30) days.
    """.strip()


def WILL_3_SUB_BENEFICIARIES_BANK_ACCOUNT_BENEFICIARY_3_DIES_BLOCK_TEMPLATE(
    num_beneficiaries, has_amount_allocation
):
    return (
        """
    If {entity_3_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, I give the interest in {bank_name} {bank_account_number} which {entity_3_name} would otherwise have received under this Will, to the following persons in the corresponding proportions:
    i.{sub_allocation_percentage:.02f}% (being {sub_entity_3_1_ea_pct:.02f}% of my total interest in the same) to {sub_entity_3_1_name}
    """.strip()
        + (
            ""
            if has_amount_allocation
            else " "
            + """
    (holder of NRIC No. {sub_entity_3_1_nric}), residing at {sub_entity_3_1_address} ("{sub_entity_3_1_name}")
    """
        )
        + " "
        + """
    absolutely and free from all encumbrances;
    ii.{sub_allocation_percentage:.02f}% (being {sub_entity_3_2_ea_pct:.02f}% of my total interest in the same) to {sub_entity_3_2_name}
    """
        + (
            ""
            if has_amount_allocation
            else " "
            + """
    (holder of NRIC No. {sub_entity_3_2_nric}), residing at {sub_entity_3_2_address} ("{sub_entity_3_2_name}")
    """
        )
        + " "
        + """
    absolutely and free from all encumbrances;
    iii.{sub_allocation_percentage:.02f}% (being {sub_entity_3_3_ea_pct:.02f}% of my total interest in the same) to {sub_entity_3_3_name}
    """
        + (
            ""
            if has_amount_allocation
            else " "
            + """
    (holder of NRIC No. {sub_entity_3_3_nric}), residing at {sub_entity_3_3_address} ("{sub_entity_3_3_name}")
    """
        )
        + " "
        + """
    absolutely and free from all encumbrances (for the purpose of this clause, together with the named Substitute Beneficiaries in sub-clauses i-ii above, the ???Applicable Substitutes???); and
    iv.the remainder shall be distributed as part of my Residual Assets.

    Provided Always that if any of the Applicable Substitutes, should die during my lifetime, or fail to survive me for more than thirty (30) days, then any gift devise or bequest of my interest in {bank_name} {bank_account_number} which that Applicable Substitute would otherwise have received under this Will shall be distributed equally amongst the issues of that Applicable Substitute so long as they survive me for more than thirty (30) days, and if that Applicable Substitute does not have any issues who have survived me for more than thirty (30) days, then the same shall be distributed equally amongst all the Applicable Substitutes who have survived me for more than thirty (30) days.
    """.strip()
    )


WILL_3_SUB_BENEFICIARIES_BANK_ACCOUNT_BENEFICIARY_3_DIES_LT_100_BLOCK_TEMPLATE = (
    WILL_3_SUB_BENEFICIARIES_BANK_ACCOUNT_BENEFICIARY_3_DIES_BLOCK_TEMPLATE
)


def WILL_3_SUB_BENEFICIARIES_BANK_ACCOUNT_AMOUNT_BENEFICIARY_3_DIES_BLOCK_TEMPLATE(
    *args,
):
    return """
    If {entity_3_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, I give the amount in {bank_name} {bank_account_number} which {entity_3_name} would otherwise have received under this Will, to the following persons in the corresponding proportions:
    i.${sub_allocation_amount:.2f} to {sub_entity_3_1_name} (holder of NRIC No. {sub_entity_3_1_nric}), residing at {sub_entity_3_1_address} ("{sub_entity_3_1_name}") absolutely and free from all encumbrances;
    ii.${sub_allocation_amount:.2f} to {sub_entity_3_2_name} (holder of NRIC No. {sub_entity_3_2_nric}), residing at {sub_entity_3_2_address} ("{sub_entity_3_2_name}") absolutely and free from all encumbrances; and
    iii.${sub_allocation_amount:.2f} to {sub_entity_3_3_name} (holder of NRIC No. {sub_entity_3_3_nric}), residing at {sub_entity_3_3_address} ("{sub_entity_3_3_name}") absolutely and free from all encumbrances (for the purpose of this clause, together with the named Substitute Beneficiaries in sub-clauses i-ii above, the ???Applicable Substitutes???).
    Provided Always that if any of the Applicable Substitutes, should die during my lifetime, or fail to survive me for more than thirty (30) days, then any gift devise or bequest of my amount in {bank_name} {bank_account_number} which that Applicable Substitute would otherwise have received under this Will shall be distributed equally amongst the issues of that Applicable Substitute so long as they survive me for more than thirty (30) days, and if that Applicable Substitute does not have any issues who have survived me for more than thirty (30) days, then the same shall be distributed equally amongst all the Applicable Substitutes who have survived me for more than thirty (30) days.
    """.strip()


def WILL_2_SUB_BENEFICIARIES_BANK_ACCOUNT_BENEFICIARY_1_DIES_BLOCK_TEMPLATE(
    num_beneficiaries, has_amount_allocation
):
    return (
        """
    If {entity_1_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, I give the interest in {bank_name} {bank_account_number} which {entity_1_name} would otherwise have received under this Will, to the following persons in the corresponding proportions:
    i.{sub_allocation_percentage:.02f}% (being {sub_entity_1_1_ea_pct:.02f}% of my total interest in the same) to {sub_entity_1_1_name}
    """.strip()
        + (
            ""
            if has_amount_allocation
            else " "
            + """
    (holder of NRIC No. {sub_entity_1_1_nric}), residing at {sub_entity_1_1_address} ("{sub_entity_1_1_name}")
    """
        )
        + " "
        + """
    absolutely and free from all encumbrances; and
    ii.{sub_allocation_percentage:.02f}% (being {sub_entity_1_2_ea_pct:.02f}% of my total interest in the same) to {sub_entity_1_2_name}
    """
        + (
            ""
            if has_amount_allocation
            else " "
            + """
    (holder of NRIC No. {sub_entity_1_2_nric}), residing at {sub_entity_1_2_address} ("{sub_entity_1_2_name}")
    """
        )
        + " "
        + """
    absolutely and free from all encumbrances (for the purpose of this clause, together with the named Substitute Beneficiaries in sub-clause i above, the ???Applicable Substitutes???).
    Provided Always that if any of the Applicable Substitutes, should die during my lifetime, or fail to survive me for more than thirty (30) days, then any gift devise or bequest of my interest in {bank_name} {bank_account_number} which that Applicable Substitute would otherwise have received under this Will shall be distributed equally amongst the issues of that Applicable Substitute so long as they survive me for more than thirty (30) days, and if that Applicable Substitute does not have any issues who have survived me for more than thirty (30) days, then the same shall be distributed equally amongst all the Applicable Substitutes who have survived me for more than thirty (30) days.
    """.strip()
    )


def WILL_2_SUB_BENEFICIARIES_BANK_ACCOUNT_BENEFICIARY_1_DIES_LT_100_BLOCK_TEMPLATE(
    num_beneficiaries, has_amount_allocation
):
    return (
        """
    If {entity_1_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, I give the interest in {bank_name} {bank_account_number} which {entity_1_name} would otherwise have received under this Will, to the following persons in the corresponding proportions:
    i.{sub_allocation_percentage:.02f}% (being {sub_entity_1_1_ea_pct:.02f}% of my total interest in the same) to {sub_entity_1_1_name}
    """.strip()
        + (
            ""
            if has_amount_allocation
            else " "
            + """
    (holder of NRIC No. {sub_entity_1_1_nric}), residing at {sub_entity_1_1_address} ("{sub_entity_1_1_name}")
    """
        )
        + " "
        + """
    absolutely and free from all encumbrances;
    ii.{sub_allocation_percentage:.02f}% (being {sub_entity_1_2_ea_pct:.02f}% of my total interest in the same) to {sub_entity_1_2_name}
    """
        + (
            ""
            if has_amount_allocation
            else " "
            + """
    (holder of NRIC No. {sub_entity_1_2_nric}), residing at {sub_entity_1_2_address} ("{sub_entity_1_2_name}")
    """
        )
        + " "
        + """
    absolutely and free from all encumbrances (for the purpose of this clause, together with the named Substitute Beneficiaries in sub-clause i above, the ???Applicable Substitutes???); and
    iii.the remainder shall be distributed as part of my Residual Assets.
    Provided Always that if any of the Applicable Substitutes, should die during my lifetime, or fail to survive me for more than thirty (30) days, then any gift devise or bequest of my interest in {bank_name} {bank_account_number} which that Applicable Substitute would otherwise have received under this Will shall be distributed equally amongst the issues of that Applicable Substitute so long as they survive me for more than thirty (30) days, and if that Applicable Substitute does not have any issues who have survived me for more than thirty (30) days, then the same shall be distributed equally amongst all the Applicable Substitutes who have survived me for more than thirty (30) days.
    """.strip()
    )


def WILL_2_SUB_BENEFICIARIES_BANK_ACCOUNT_AMOUNT_BENEFICIARY_1_DIES_BLOCK_TEMPLATE(
    len_amount_allocations, mentioned_sub_entity_codes, *args
):
    return (
        """
    If {entity_1_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, I give the amount in {bank_name} {bank_account_number} which {entity_1_name} would otherwise have received under this Will, to the following persons in the corresponding proportions:
    i.${sub_allocation_amount:.2f} to {sub_entity_1_1_name}
    """.strip()
        + (
            ""
            if "1_1" in mentioned_sub_entity_codes
            else """
    (holder of NRIC No. {sub_entity_1_1_nric}), residing at {sub_entity_1_1_address} ("{sub_entity_1_1_name}")
    """
        )
        + " "
        + """
    absolutely and free from all encumbrances; and
    ii.${sub_allocation_amount:.2f} to {sub_entity_1_2_name}
    """
        + (
            ""
            if "1_2" in mentioned_sub_entity_codes
            else """
    (holder of NRIC No. {sub_entity_1_2_nric}), residing at {sub_entity_1_2_address} ("{sub_entity_1_2_name}")
    """
        )
        + " "
        + """
    absolutely and free from all encumbrances (for the purpose of this clause, together with the named Substitute Beneficiaries in sub-clause i above, the ???Applicable Substitutes???).
    Provided Always that if any of the Applicable Substitutes, should die during my lifetime, or fail to survive me for more than thirty (30) days, then any gift devise or bequest of my amount in {bank_name} {bank_account_number} which that Applicable Substitute would otherwise have received under this Will shall be distributed equally amongst the issues of that Applicable Substitute so long as they survive me for more than thirty (30) days, and if that Applicable Substitute does not have any issues who have survived me for more than thirty (30) days, then the same shall be distributed equally amongst all the Applicable Substitutes who have survived me for more than thirty (30) days.
    """.strip()
    )


def WILL_2_SUB_BENEFICIARIES_BANK_ACCOUNT_BENEFICIARY_2_DIES_BLOCK_TEMPLATE(
    num_beneficiaries, has_amount_allocation
):
    return (
        """
    If {entity_2_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, I give the interest in {bank_name} {bank_account_number} which {entity_2_name} would otherwise have received under this Will, to the following persons in the corresponding proportions:
    i.{sub_allocation_percentage:.02f}% (being {sub_entity_2_1_ea_pct:.02f}% of my total interest in the same) to {sub_entity_2_1_name}
    """.strip()
        + (
            ""
            if has_amount_allocation
            else " "
            + """
    (holder of NRIC No. {sub_entity_2_1_nric}), residing at {sub_entity_2_1_address} ("{sub_entity_2_1_name}")
    """
        )
        + " "
        + """
    absolutely and free from all encumbrances; and
    ii.{sub_allocation_percentage:.02f}% (being {sub_entity_2_2_ea_pct:.02f}% of my total interest in the same) to {sub_entity_2_2_name}
    """
        + (
            ""
            if has_amount_allocation
            else " "
            + """
    (holder of NRIC No. {sub_entity_2_2_nric}), residing at {sub_entity_2_2_address} ("{sub_entity_2_2_name}")
    """
        )
        + " "
        + """
    absolutely and free from all encumbrances (for the purpose of this clause, together with the named Substitute Beneficiaries in sub-clause i above, the ???Applicable Substitutes???).
    Provided Always that if any of the Applicable Substitutes, should die during my lifetime, or fail to survive me for more than thirty (30) days, then any gift devise or bequest of my interest in {bank_name} {bank_account_number} which that Applicable Substitute would otherwise have received under this Will shall be distributed equally amongst the issues of that Applicable Substitute so long as they survive me for more than thirty (30) days, and if that Applicable Substitute does not have any issues who have survived me for more than thirty (30) days, then the same shall be distributed equally amongst all the Applicable Substitutes who have survived me for more than thirty (30) days.
    """.strip()
    )


def WILL_2_SUB_BENEFICIARIES_BANK_ACCOUNT_BENEFICIARY_2_DIES_LT_100_BLOCK_TEMPLATE(
    num_beneficiaries, has_amount_allocation
):
    return (
        """
    If {entity_2_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, I give the interest in {bank_name} {bank_account_number} which {entity_2_name} would otherwise have received under this Will, to the following persons in the corresponding proportions:
    i.{sub_allocation_percentage:.02f}% (being {sub_entity_2_1_ea_pct:.02f}% of my total interest in the same) to {sub_entity_2_1_name}
    """.strip()
        + (
            ""
            if has_amount_allocation
            else " "
            + """
    (holder of NRIC No. {sub_entity_2_1_nric}), residing at {sub_entity_2_1_address} ("{sub_entity_2_1_name}")
    """
        )
        + " "
        + """
    absolutely and free from all encumbrances;
    ii.{sub_allocation_percentage:.02f}% (being {sub_entity_2_2_ea_pct:.02f}% of my total interest in the same) to {sub_entity_2_2_name}
    """
        + (
            ""
            if has_amount_allocation
            else " "
            + """
    (holder of NRIC No. {sub_entity_2_2_nric}), residing at {sub_entity_2_2_address} ("{sub_entity_2_2_name}")
    """
        )
        + " "
        + """
    absolutely and free from all encumbrances (for the purpose of this clause, together with the named Substitute Beneficiaries in sub-clause i above, the ???Applicable Substitutes???); and
    iii.the remainder shall be distributed as part of my Residual Assets.
    Provided Always that if any of the Applicable Substitutes, should die during my lifetime, or fail to survive me for more than thirty (30) days, then any gift devise or bequest of my interest in {bank_name} {bank_account_number} which that Applicable Substitute would otherwise have received under this Will shall be distributed equally amongst the issues of that Applicable Substitute so long as they survive me for more than thirty (30) days, and if that Applicable Substitute does not have any issues who have survived me for more than thirty (30) days, then the same shall be distributed equally amongst all the Applicable Substitutes who have survived me for more than thirty (30) days.
    """.strip()
    )


def WILL_2_SUB_BENEFICIARIES_BANK_ACCOUNT_AMOUNT_BENEFICIARY_2_DIES_BLOCK_TEMPLATE(
    len_amount_allocations, mentioned_sub_entity_codes, *args
):
    return (
        """
    If {entity_2_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, I give the amount in {bank_name} {bank_account_number} which {entity_2_name} would otherwise have received under this Will, to the following persons in the corresponding proportions:
    i.${sub_allocation_amount:.2f} to {sub_entity_2_1_name}
    """.strip()
        + (
            ""
            if "2_1" in mentioned_sub_entity_codes
            else """
    (holder of NRIC No. {sub_entity_2_1_nric}), residing at {sub_entity_2_1_address} ("{sub_entity_2_1_name}")
    """
        )
        + " "
        + """
    absolutely and free from all encumbrances; and
    ii.${sub_allocation_amount:.2f} to {sub_entity_2_2_name}
    """
        + (
            ""
            if "2_2" in mentioned_sub_entity_codes
            else """
    (holder of NRIC No. {sub_entity_2_2_nric}), residing at {sub_entity_2_2_address} ("{sub_entity_2_2_name}")
    """
        )
        + " "
        + """
    absolutely and free from all encumbrances (for the purpose of this clause, together with the named Substitute Beneficiaries in sub-clause i above, the ???Applicable Substitutes???).
    Provided Always that if any of the Applicable Substitutes, should die during my lifetime, or fail to survive me for more than thirty (30) days, then any gift devise or bequest of my amount in {bank_name} {bank_account_number} which that Applicable Substitute would otherwise have received under this Will shall be distributed equally amongst the issues of that Applicable Substitute so long as they survive me for more than thirty (30) days, and if that Applicable Substitute does not have any issues who have survived me for more than thirty (30) days, then the same shall be distributed equally amongst all the Applicable Substitutes who have survived me for more than thirty (30) days.
    """.strip()
    )


def WILL_2_SUB_BENEFICIARIES_BANK_ACCOUNT_BENEFICIARY_3_DIES_BLOCK_TEMPLATE(
    num_beneficiaries, has_amount_allocation
):
    return (
        """
    If {entity_3_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, I give the interest in {bank_name} {bank_account_number} which {entity_3_name} would otherwise have received under this Will, to the following persons in the corresponding proportions:
    i.{sub_allocation_percentage:.02f}% (being {sub_entity_3_1_ea_pct:.02f}% of my total interest in the same) to {sub_entity_3_1_name}
    """.strip()
        + (
            ""
            if has_amount_allocation
            else " "
            + """
    (holder of NRIC No. {sub_entity_3_1_nric}), residing at {sub_entity_3_1_address} ("{sub_entity_3_1_name}")
    """
        )
        + " "
        + """
    absolutely and free from all encumbrances; and
    ii.{sub_allocation_percentage:.02f}% (being {sub_entity_3_2_ea_pct:.02f}% of my total interest in the same) to {sub_entity_3_2_name}
    """
        + (
            ""
            if has_amount_allocation
            else " "
            + """
    (holder of NRIC No. {sub_entity_3_2_nric}), residing at {sub_entity_3_2_address} ("{sub_entity_3_2_name}")
    """
        )
        + " "
        + """
    absolutely and free from all encumbrances (for the purpose of this clause, together with the named Substitute Beneficiaries in sub-clause i above, the ???Applicable Substitutes???).
    Provided Always that if any of the Applicable Substitutes, should die during my lifetime, or fail to survive me for more than thirty (30) days, then any gift devise or bequest of my interest in {bank_name} {bank_account_number} which that Applicable Substitute would otherwise have received under this Will shall be distributed equally amongst the issues of that Applicable Substitute so long as they survive me for more than thirty (30) days, and if that Applicable Substitute does not have any issues who have survived me for more than thirty (30) days, then the same shall be distributed equally amongst all the Applicable Substitutes who have survived me for more than thirty (30) days.
    """.strip()
    )


def WILL_2_SUB_BENEFICIARIES_BANK_ACCOUNT_BENEFICIARY_3_DIES_LT_100_BLOCK_TEMPLATE(
    num_beneficiaries, has_amount_allocation
):
    return (
        """
    If {entity_3_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, I give the interest in {bank_name} {bank_account_number} which {entity_3_name} would otherwise have received under this Will, to the following persons in the corresponding proportions:
    i.{sub_allocation_percentage:.02f}% (being {sub_entity_3_1_ea_pct:.02f}% of my total interest in the same) to {sub_entity_3_1_name}
    """.strip()
        + (
            ""
            if has_amount_allocation
            else " "
            + """
    (holder of NRIC No. {sub_entity_3_1_nric}), residing at {sub_entity_3_1_address} ("{sub_entity_3_1_name}")
    """
        )
        + " "
        + """
    absolutely and free from all encumbrances;
    ii.{sub_allocation_percentage:.02f}% (being {sub_entity_3_2_ea_pct:.02f}% of my total interest in the same) to {sub_entity_3_2_name}
    """
        + (
            ""
            if has_amount_allocation
            else " "
            + """
    (holder of NRIC No. {sub_entity_3_2_nric}), residing at {sub_entity_3_2_address} ("{sub_entity_3_2_name}")
    """
        )
        + " "
        + """
    absolutely and free from all encumbrances (for the purpose of this clause, together with the named Substitute Beneficiaries in sub-clause i above, the ???Applicable Substitutes???); and
    iii.the remainder shall be distributed as part of my Residual Assets.
    Provided Always that if any of the Applicable Substitutes, should die during my lifetime, or fail to survive me for more than thirty (30) days, then any gift devise or bequest of my interest in {bank_name} {bank_account_number} which that Applicable Substitute would otherwise have received under this Will shall be distributed equally amongst the issues of that Applicable Substitute so long as they survive me for more than thirty (30) days, and if that Applicable Substitute does not have any issues who have survived me for more than thirty (30) days, then the same shall be distributed equally amongst all the Applicable Substitutes who have survived me for more than thirty (30) days.
    """.strip()
    )


def WILL_2_SUB_BENEFICIARIES_BANK_ACCOUNT_AMOUNT_BENEFICIARY_3_DIES_BLOCK_TEMPLATE(
    *args,
):
    return """
    If {entity_3_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, I give the amount in {bank_name} {bank_account_number} which {entity_3_name} would otherwise have received under this Will, to the following persons in the corresponding proportions:
    i.${sub_allocation_amount:.02f} to {sub_entity_3_1_name} (holder of NRIC No. {sub_entity_3_1_nric}), residing at {sub_entity_3_1_address} ("{sub_entity_3_1_name}") absolutely and free from all encumbrances; and
    ii.${sub_allocation_amount:.02f} to {sub_entity_3_2_name} (holder of NRIC No. {sub_entity_3_2_nric}), residing at {sub_entity_3_2_address} ("{sub_entity_3_2_name}") absolutely and free from all encumbrances (for the purpose of this clause, together with the named Substitute Beneficiaries in sub-clause i above, the ???Applicable Substitutes???).
    Provided Always that if any of the Applicable Substitutes, should die during my lifetime, or fail to survive me for more than thirty (30) days, then any gift devise or bequest of my amount in {bank_name} {bank_account_number} which that Applicable Substitute would otherwise have received under this Will shall be distributed equally amongst the issues of that Applicable Substitute so long as they survive me for more than thirty (30) days, and if that Applicable Substitute does not have any issues who have survived me for more than thirty (30) days, then the same shall be distributed equally amongst all the Applicable Substitutes who have survived me for more than thirty (30) days.
    """.strip()


def WILL_1_SUB_BENEFICIARIES_BANK_ACCOUNT_BENEFICIARY_1_DIES_BLOCK_TEMPLATE(
    num_beneficiaries, has_amount_allocation
):
    return (
        """
    If {entity_1_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, I give {sub_allocation_percentage:.2f}% of the interest in {bank_name} {bank_account_number} which {entity_1_name} would otherwise have received under this Will (being {sub_entity_1_1_ea_pct:.2f}% of my total interest in the same) to {sub_entity_1_1_name}
    """.strip()
        + (
            ""
            if has_amount_allocation
            else " "
            + """
    (holder of NRIC No. {sub_entity_1_1_nric}), residing at {sub_entity_1_1_address} ("{sub_entity_1_1_name}")
    """
        )
        + " "
        + """
    absolutely and free from all encumbrances, provided always that if {sub_entity_1_1_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, then the same shall be distributed equally amongst {sub_entity_1_1_name}'s surviving issues absolutely and free from all encumbrances so long as they survive me for more than thirty (30) days
    """.strip()
        + (
            ".\n"
            if num_beneficiaries == 1
            else """
    , and if {sub_entity_1_1_name} does not have any issues who have survived me for more than thirty (30) days, then the same shall be distributed equally amongst all the Main Substitutes who have survived me for more than thirty (30) days.
    """.strip()
        )
    )


def WILL_1_SUB_BENEFICIARIES_BANK_ACCOUNT_BENEFICIARY_1_DIES_LT_100_BLOCK_TEMPLATE(
    num_beneficiaries, has_amount_allocation
):
    return (
        """
    If {entity_1_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, I give {sub_allocation_percentage:.2f}% of the interest in {bank_name} {bank_account_number} which {entity_1_name} would otherwise have received under this Will (being {sub_entity_1_1_ea_pct:.2f}% of my total interest in the same) to {sub_entity_1_1_name}
    """.strip()
        + (
            ""
            if has_amount_allocation
            else " "
            + """
    (holder of NRIC No. {sub_entity_1_1_nric}), residing at {sub_entity_1_1_address} ("{sub_entity_1_1_name}")
    """
        )
        + " "
        + """
    absolutely and free from all encumbrances, provided always that if {sub_entity_1_1_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, then the same shall be distributed equally amongst {sub_entity_1_1_name}'s surviving issues absolutely and free from all encumbrances so long as they survive me for more than thirty (30) days
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


def WILL_1_SUB_BENEFICIARIES_BANK_ACCOUNT_AMOUNT_BENEFICIARY_1_DIES_BLOCK_TEMPLATE(
    num_beneficiaries, *args
):
    return """
    If {entity_1_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, I give ${sub_allocation_amount:.2f} of the amount in {bank_name} {bank_account_number} which {entity_1_name} would otherwise have received under this Will to {sub_entity_1_1_name} (holder of NRIC No. {sub_entity_1_1_nric}), residing at {sub_entity_1_1_address} ("{sub_entity_1_1_name}") absolutely and free from all encumbrances, provided always that if {sub_entity_1_1_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, then the same shall be distributed equally amongst {sub_entity_1_1_name}'s surviving issues absolutely and free from all encumbrances so long as they survive me for more than thirty (30) days
    """.strip() + (
        ".\n"
        if num_beneficiaries == 1
        else """
    , and if {sub_entity_1_1_name} does not have any issues who have survived me for more than thirty (30) days, then the same shall be distributed equally amongst all the Main Substitutes who have survived me for more than thirty (30) days.
    """.strip()
    )


def WILL_1_SUB_BENEFICIARIES_BANK_ACCOUNT_BENEFICIARY_2_DIES_BLOCK_TEMPLATE(
    num_beneficiaries, has_amount_allocation
):
    return (
        """
    If {entity_2_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, I give {sub_allocation_percentage:.2f}% of the interest in {bank_name} {bank_account_number} which {entity_2_name} would otherwise have received under this Will (being {sub_entity_2_1_ea_pct:.2f}% of my total interest in the same) to {sub_entity_2_1_name}
    """.strip()
        + (
            ""
            if has_amount_allocation
            else " "
            + """
    (holder of NRIC No. {sub_entity_2_1_nric}), residing at {sub_entity_2_1_address} ("{sub_entity_2_1_name}")
    """
        )
        + " "
        + """
    absolutely and free from all encumbrances, provided always that if {sub_entity_2_1_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, then the same shall be distributed equally amongst {sub_entity_2_1_name}'s surviving issues absolutely and free from all encumbrances so long as they survive me for more than thirty (30) days, and if {sub_entity_2_1_name} does not have any issues who have survived me for more than thirty (30) days, then the same shall be distributed equally amongst all the Main Substitutes who have survived me for more than thirty (30) days.
    """.strip()
    )


def WILL_1_SUB_BENEFICIARIES_BANK_ACCOUNT_BENEFICIARY_2_DIES_LT_100_BLOCK_TEMPLATE(
    num_beneficiaries, has_amount_allocation
):
    return (
        """
    If {entity_2_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, I give {sub_allocation_percentage:.2f}% of the interest in {bank_name} {bank_account_number} which {entity_2_name} would otherwise have received under this Will (being {sub_entity_2_1_ea_pct:.2f}% of my total interest in the same) to {sub_entity_2_1_name}
    """.strip()
        + (
            ""
            if has_amount_allocation
            else " "
            + """
    (holder of NRIC No. {sub_entity_2_1_nric}), residing at {sub_entity_2_1_address} ("{sub_entity_2_1_name}")
    """
        )
        + " "
        + """
    absolutely and free from all encumbrances, provided always that if {sub_entity_2_1_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, then the same shall be distributed equally amongst {sub_entity_2_1_name}'s surviving issues absolutely and free from all encumbrances so long as they survive me for more than thirty (30) days, and if {sub_entity_2_1_name} does not have any issues who have survived me for more than thirty (30) days, then the same shall be distributed equally amongst all the Main Substitutes who have survived me for more than thirty (30) days, and the remainder shall be distributed as part of my Residual Assets.
    """.strip()
    )


def WILL_1_SUB_BENEFICIARIES_BANK_ACCOUNT_AMOUNT_BENEFICIARY_2_DIES_BLOCK_TEMPLATE(
    *args,
):
    return """
    If {entity_2_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, I give ${sub_allocation_amount:.2f} of the amount in {bank_name} {bank_account_number} which {entity_2_name} would otherwise have received under this Will to {sub_entity_2_1_name} (holder of NRIC No. {sub_entity_2_1_nric}), residing at {sub_entity_2_1_address} ("{sub_entity_2_1_name}") absolutely and free from all encumbrances, provided always that if {sub_entity_2_1_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, then the same shall be distributed equally amongst {sub_entity_2_1_name}'s surviving issues absolutely and free from all encumbrances so long as they survive me for more than thirty (30) days, and if {sub_entity_2_1_name} does not have any issues who have survived me for more than thirty (30) days, then the same shall be distributed equally amongst all the Main Substitutes who have survived me for more than thirty (30) days.
    """.strip()


def WILL_1_SUB_BENEFICIARIES_BANK_ACCOUNT_BENEFICIARY_3_DIES_BLOCK_TEMPLATE(
    num_beneficiaries, has_amount_allocation
):
    return (
        """
    If {entity_3_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, I give {sub_allocation_percentage:.2f}% of the interest in {bank_name} {bank_account_number} which {entity_3_name} would otherwise have received under this Will (being {sub_entity_3_1_ea_pct:.2f}% of my total interest in the same) to {sub_entity_3_1_name}
    """.strip()
        + (
            ""
            if has_amount_allocation
            else " "
            + """
    (holder of NRIC No. {sub_entity_3_1_nric}), residing at {sub_entity_3_1_address} ("{sub_entity_3_1_name}")
    """
        )
        + " "
        + """
    absolutely and free from all encumbrances, provided always that if {sub_entity_3_1_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, then the same shall be distributed equally amongst {sub_entity_3_1_name}'s surviving issues absolutely and free from all encumbrances so long as they survive me for more than thirty (30) days, and if {sub_entity_3_1_name} does not have any issues who have survived me for more than thirty (30) days, then the same shall be distributed equally amongst all the Main Substitutes who have survived me for more than thirty (30) days.
    """.strip()
    )


def WILL_1_SUB_BENEFICIARIES_BANK_ACCOUNT_BENEFICIARY_3_DIES_LT_100_BLOCK_TEMPLATE(
    num_beneficiaries, has_amount_allocation
):
    return (
        """
    If {entity_3_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, I give {sub_allocation_percentage:.2f}% of the interest in {bank_name} {bank_account_number} which {entity_3_name} would otherwise have received under this Will (being {sub_entity_3_1_ea_pct:.2f}% of my total interest in the same) to {sub_entity_3_1_name}
    """.strip()
        + (
            ""
            if has_amount_allocation
            else " "
            + """
    (holder of NRIC No. {sub_entity_3_1_nric}), residing at {sub_entity_3_1_address} ("{sub_entity_3_1_name}")
    """
        )
        + " "
        + """
    absolutely and free from all encumbrances, provided always that if {sub_entity_3_1_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, then the same shall be distributed equally amongst {sub_entity_3_1_name}'s surviving issues absolutely and free from all encumbrances so long as they survive me for more than thirty (30) days, and if {sub_entity_3_1_name} does not have any issues who have survived me for more than thirty (30) days, then the same shall be distributed equally amongst all the Main Substitutes who have survived me for more than thirty (30) days, and the remainder shall be distributed as part of my Residual Assets.
    """.strip()
    )


def WILL_1_SUB_BENEFICIARIES_BANK_ACCOUNT_AMOUNT_BENEFICIARY_3_DIES_BLOCK_TEMPLATE(
    *args,
):
    return """
    If {entity_3_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, I give ${sub_allocation_amount:.2f} of the amount in {bank_name} {bank_account_number} which {entity_3_name} would otherwise have received under this Will to {sub_entity_3_1_name} (holder of NRIC No. {sub_entity_3_1_nric}), residing at {sub_entity_3_1_address} ("{sub_entity_3_1_name}") absolutely and free from all encumbrances, provided always that if {sub_entity_3_1_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, then the same shall be distributed equally amongst {sub_entity_3_1_name}'s surviving issues absolutely and free from all encumbrances so long as they survive me for more than thirty (30) days, and if {sub_entity_3_1_name} does not have any issues who have survived me for more than thirty (30) days, then the same shall be distributed equally amongst all the Main Substitutes who have survived me for more than thirty (30) days.
    """.strip()
