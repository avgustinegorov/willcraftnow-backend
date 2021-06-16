WILL_RESIDUAL_ALLOCATIONS_TITLE_BLOCK_TEMPLATE = """
RESIDUAL ALLOCATIONS
"""


def WILL_RESIDUAL_1_ALLOCATIONS_BLOCK_TEMPLATE(*args):
    return """
    %(numbering)d.I give all my Assets not distributed in the clauses above ("Residual Assets") to {entity_1_name} absolutely and free from all encumbrances.
    """.strip()


WILL_RESIDUAL_1_ALLOCATIONS_LT_100_BLOCK_TEMPLATE = (
    WILL_RESIDUAL_1_ALLOCATIONS_BLOCK_TEMPLATE
)


def WILL_RESIDUAL_2_ALLOCATIONS_BLOCK_TEMPLATE(*args):
    return """
    %(numbering)d.I give all my Assets not distributed in the clauses above ("Residual Assets")
    to the following persons in the corresponding proportions:
    i.{allocation_percentage:.2f}%% to {entity_1_name}
     absolutely and free from all encumbrances; and
    ii.{allocation_percentage:.2f}%% to {entity_2_name}
     absolutely and free from all encumbrances (for the purpose
    of clauses %(numbering)d to %(numbering_plus_2)d, together with the named Beneficiaries in sub-clause i
    above, the ﬁMain Substitutesﬂ).
    """.strip()


WILL_RESIDUAL_2_ALLOCATIONS_LT_100_BLOCK_TEMPLATE = (
    WILL_RESIDUAL_2_ALLOCATIONS_BLOCK_TEMPLATE
)


def WILL_RESIDUAL_3_ALLOCATIONS_BLOCK_TEMPLATE(*args):
    return """
    %(numbering)d.I give all my Assets not distributed in the clauses above ("Residual Assets") to the following persons in the corresponding proportions:
    i.{allocation_percentage:.2f}%% to {entity_1_name} absolutely and free from all encumbrances;
    ii.{allocation_percentage:.2f}%% to {entity_2_name} absolutely and free from all encumbrances; and
    iii.{allocation_percentage:.2f}%% to {entity_3_name} absolutely and free from all encumbrances (for the purpose of clauses %(numbering)d to %(numbering_plus_3)d, together with the named Beneficiaries in sub-clauses i-ii above, the ﬁMain Substitutesﬂ).
    """.strip()


WILL_RESIDUAL_3_ALLOCATIONS_LT_100_BLOCK_TEMPLATE = (
    WILL_RESIDUAL_3_ALLOCATIONS_BLOCK_TEMPLATE
)


def WILL_RESIDUAL_BENEFICIARY_1_DIES_BLOCK_TEMPLATE(num_beneficiaries, *args):
    return """
    If {entity_1_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, then the proportion of my Residual Assets which he would otherwise have received under this Will shall be distributed equally amongst his surviving issues absolutely and free from all encumbrances so long as they survive me for more than thirty (30) days
    """.strip() + (
        ".\n"
        if num_beneficiaries == 1
        else """
    , and if {entity_1_name} does not have any issues who have survived me for more than thirty (30) days, then the same shall be distributed equally amongst all the Main Substitutes who have survived me for more than thirty (30) days.
    """.strip()
    )


def WILL_RESIDUAL_BENEFICIARY_2_DIES_BLOCK_TEMPLATE(*args):
    return """
    If {entity_2_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, then the proportion of my Residual Assets which he would otherwise have received under this Will shall be distributed equally amongst his surviving issues absolutely and free from all encumbrances so long as they survive me for more than thirty (30) days, and if {entity_2_name} does not have any issues who have survived me for more than thirty (30) days, then the same shall be distributed equally amongst all the Main Substitutes who have survived me for more than thirty (30) days.
    """.strip()


def WILL_RESIDUAL_BENEFICIARY_3_DIES_BLOCK_TEMPLATE(*args):
    return """
    If {entity_3_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, then the proportion of my Residual Assets which he would otherwise have received under this Will shall be distributed equally amongst his surviving issues absolutely and free from all encumbrances so long as they survive me for more than thirty (30) days, and if {entity_3_name} does not have any issues who have survived me for more than thirty (30) days, then the same shall be distributed equally amongst all the Main Substitutes who have survived me for more than thirty (30) days.
    """.strip()


def WILL_3_SUB_BENEFICIARIES_RESIDUAL_BENEFICIARY_1_DIES_BLOCK_TEMPLATE(
    num_beneficiaries, *args
):
    return """
    If {entity_1_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, I give the interest in Residual Assets which he would otherwise have received under this Will, to the following persons in the corresponding proportions:
    i.{sub_allocation_percentage:.02f}% (being {sub_entity_1_1_ea_pct:.02f}% of my total interest in the same) to {sub_entity_1_1_name} absolutely and free from all encumbrances;
    ii.{sub_allocation_percentage:.02f}% (being {sub_entity_1_2_ea_pct:.02f}% of my total interest in the same) to {sub_entity_1_2_name} absolutely and free from all encumbrances;
    iii.{sub_allocation_percentage:.02f}% (being {sub_entity_1_3_ea_pct:.02f}% of my total interest in the same) to {sub_entity_1_3_name} absolutely and free from all encumbrances (for the purpose of this clause, together with the named Substitute Beneficiaries in sub-clauses i-ii above, the ﬁApplicable Substitutesﬂ); and
    Provided Always that if any of the Applicable Substitutes, should die during my lifetime, or fail to survive me for more than thirty (30) days, the proportion of my Residual Assets which that Applicable Substitute would otherwise have received under this Will shall be distributed equally amongst the issues of that Applicable Substitute so long as they survive me for more than thirty (30) days, and if that Applicable Substitute does not have any issues who have survived me for more than thirty (30) days, then the same shall be distributed equally amongst all the Applicable Substitutes who have survived me for more than thirty (30) days.
    """.strip()


WILL_3_SUB_BENEFICIARIES_RESIDUAL_BENEFICIARY_1_DIES_LT_100_BLOCK_TEMPLATE = (
    WILL_3_SUB_BENEFICIARIES_RESIDUAL_BENEFICIARY_1_DIES_BLOCK_TEMPLATE
)


def WILL_3_SUB_BENEFICIARIES_RESIDUAL_BENEFICIARY_2_DIES_BLOCK_TEMPLATE(*args):
    return """
    If {entity_2_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, I give the interest in Residual Assets which he would otherwise have received under this Will, to the following persons in the corresponding proportions:
    i.{sub_allocation_percentage:.02f}% (being {sub_entity_2_1_ea_pct:.02f}% of my total interest in the same) to {sub_entity_2_1_name} absolutely and free from all encumbrances;
    ii.{sub_allocation_percentage:.02f}% (being {sub_entity_2_2_ea_pct:.02f}% of my total interest in the same) to {sub_entity_2_2_name} absolutely and free from all encumbrances;
    iii.{sub_allocation_percentage:.02f}% (being {sub_entity_2_3_ea_pct:.02f}% of my total interest in the same) to {sub_entity_2_3_name} absolutely and free from all encumbrances (for the purpose of this clause, together with the named Substitute Beneficiaries in sub-clauses i-ii above, the ﬁApplicable Substitutesﬂ); and

    Provided Always that if any of the Applicable Substitutes, should die during my lifetime, or fail to survive me for more than thirty (30) days, the proportion of my Residual Assets which that Applicable Substitute would otherwise have received under this Will shall be distributed equally amongst the issues of that Applicable Substitute so long as they survive me for more than thirty (30) days, and if that Applicable Substitute does not have any issues who have survived me for more than thirty (30) days, then the same shall be distributed equally amongst all the Applicable Substitutes who have survived me for more than thirty (30) days.
    """.strip()


WILL_3_SUB_BENEFICIARIES_RESIDUAL_BENEFICIARY_2_DIES_LT_100_BLOCK_TEMPLATE = (
    WILL_3_SUB_BENEFICIARIES_RESIDUAL_BENEFICIARY_2_DIES_BLOCK_TEMPLATE
)


def WILL_3_SUB_BENEFICIARIES_RESIDUAL_BENEFICIARY_3_DIES_BLOCK_TEMPLATE(*args):
    return """
    If {entity_3_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, I give the interest in Residual Assets which he would otherwise have received under this Will, to the following persons in the corresponding proportions:
    i.{sub_allocation_percentage:.02f}% (being {sub_entity_3_1_ea_pct:.02f}% of my total interest in the same) to {sub_entity_3_1_name} absolutely and free from all encumbrances;
    ii.{sub_allocation_percentage:.02f}% (being {sub_entity_3_2_ea_pct:.02f}% of my total interest in the same) to {sub_entity_3_2_name} absolutely and free from all encumbrances;
    iii.{sub_allocation_percentage:.02f}% (being {sub_entity_3_3_ea_pct:.02f}% of my total interest in the same) to {sub_entity_3_3_name} absolutely and free from all encumbrances (for the purpose of this clause, together with the named Substitute Beneficiaries in sub-clauses i-ii above, the ﬁApplicable Substitutesﬂ); and
    Provided Always that if any of the Applicable Substitutes, should die during my lifetime, or fail to survive me for more than thirty (30) days, the proportion of my Residual Assets which that Applicable Substitute would otherwise have received under this Will shall be distributed equally amongst the issues of that Applicable Substitute so long as they survive me for more than thirty (30) days, and if that Applicable Substitute does not have any issues who have survived me for more than thirty (30) days, then the same shall be distributed equally amongst all the Applicable Substitutes who have survived me for more than thirty (30) days.
    """.strip()


WILL_3_SUB_BENEFICIARIES_RESIDUAL_BENEFICIARY_3_DIES_LT_100_BLOCK_TEMPLATE = (
    WILL_3_SUB_BENEFICIARIES_RESIDUAL_BENEFICIARY_3_DIES_BLOCK_TEMPLATE
)


def WILL_2_SUB_BENEFICIARIES_RESIDUAL_BENEFICIARY_1_DIES_BLOCK_TEMPLATE(
    num_beneficiaries, *args
):
    return """
    If {entity_1_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, I give the interest in Residual Assets which he would otherwise have received under this Will, to the following persons in the corresponding proportions:
    i.{sub_allocation_percentage:.02f}% (being {sub_entity_1_1_ea_pct:.02f}% of my total interest in the same) to {sub_entity_1_1_name}  absolutely and free from all encumbrances; and
    ii.{sub_allocation_percentage:.02f}% (being {sub_entity_1_2_ea_pct:.02f}% of my total interest in the same) to {sub_entity_1_2_name}  absolutely and free from all encumbrances (for the purpose of this clause, together with the named Substitute Beneficiaries in sub-clause i above, the ﬁApplicable Substitutesﬂ).
    Provided Always that if any of the Applicable Substitutes, should die during my lifetime, or fail to survive me for more than thirty (30) days, the proportion of my Residual Assets which that Applicable Substitute would otherwise have received under this Will shall be distributed equally amongst the issues of that Applicable Substitute so long as they survive me for more than thirty (30) days, and if that Applicable Substitute does not have any issues who have survived me for more than thirty (30) days, then the same shall be distributed equally amongst all the Applicable Substitutes who have survived me for more than thirty (30) days.
    """.strip()


def WILL_2_SUB_BENEFICIARIES_RESIDUAL_BENEFICIARY_1_DIES_LT_100_BLOCK_TEMPLATE(
    num_beneficiaries, *args
):
    return """
    If {entity_1_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, I give the interest in Residual Assets which he would otherwise have received under this Will, to the following persons in the corresponding proportions:
    i.{sub_allocation_percentage:.02f}% (being {sub_entity_1_1_ea_pct:.02f}% of my total interest in the same) to {sub_entity_1_1_name}  absolutely and free from all encumbrances;
    ii.{sub_allocation_percentage:.02f}% (being {sub_entity_1_2_ea_pct:.02f}% of my total interest in the same) to {sub_entity_1_2_name}  absolutely and free from all encumbrances (for the purpose of this clause, together with the named Substitute Beneficiaries in sub-clause i above, the ﬁApplicable Substitutesﬂ); and
    Provided Always that if any of the Applicable Substitutes, should die during my lifetime, or fail to survive me for more than thirty (30) days, the proportion of my Residual Assets which that Applicable Substitute would otherwise have received under this Will shall be distributed equally amongst the issues of that Applicable Substitute so long as they survive me for more than thirty (30) days, and if that Applicable Substitute does not have any issues who have survived me for more than thirty (30) days, then the same shall be distributed equally amongst all the Applicable Substitutes who have survived me for more than thirty (30) days.
    """.strip()


def WILL_2_SUB_BENEFICIARIES_RESIDUAL_BENEFICIARY_2_DIES_BLOCK_TEMPLATE(*args):
    return """
    If {entity_2_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, I give the interest in Residual Assets which he would otherwise have received under this Will, to the following persons in the corresponding proportions:
    i.{sub_allocation_percentage:.02f}% (being {sub_entity_2_1_ea_pct:.02f}% of my total interest in the same) to {sub_entity_2_1_name}  absolutely and free from all encumbrances; and
    ii.{sub_allocation_percentage:.02f}% (being {sub_entity_2_2_ea_pct:.02f}% of my total interest in the same) to {sub_entity_2_2_name}  absolutely and free from all encumbrances (for the purpose of this clause, together with the named Substitute Beneficiaries in sub-clause i above, the ﬁApplicable Substitutesﬂ).
    Provided Always that if any of the Applicable Substitutes, should die during my lifetime, or fail to survive me for more than thirty (30) days, the proportion of my Residual Assets which that Applicable Substitute would otherwise have received under this Will shall be distributed equally amongst the issues of that Applicable Substitute so long as they survive me for more than thirty (30) days, and if that Applicable Substitute does not have any issues who have survived me for more than thirty (30) days, then the same shall be distributed equally amongst all the Applicable Substitutes who have survived me for more than thirty (30) days.
    """.strip()


def WILL_2_SUB_BENEFICIARIES_RESIDUAL_BENEFICIARY_2_DIES_LT_100_BLOCK_TEMPLATE(
    num_beneficiaries, *args
):
    return """
    If {entity_2_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, I give the interest in Residual Assets which he would otherwise have received under this Will, to the following persons in the corresponding proportions:
    i.{sub_allocation_percentage:.02f}% (being {sub_entity_2_1_ea_pct:.02f}% of my total interest in the same) to {sub_entity_2_1_name}  absolutely and free from all encumbrances;
    ii.{sub_allocation_percentage:.02f}% (being {sub_entity_2_2_ea_pct:.02f}% of my total interest in the same) to {sub_entity_2_2_name}  absolutely and free from all encumbrances (for the purpose of this clause, together with the named Substitute Beneficiaries in sub-clause i above, the ﬁApplicable Substitutesﬂ); and
    Provided Always that if any of the Applicable Substitutes, should die during my lifetime, or fail to survive me for more than thirty (30) days, the proportion of my Residual Assets which that Applicable Substitute would otherwise have received under this Will shall be distributed equally amongst the issues of that Applicable Substitute so long as they survive me for more than thirty (30) days, and if that Applicable Substitute does not have any issues who have survived me for more than thirty (30) days, then the same shall be distributed equally amongst all the Applicable Substitutes who have survived me for more than thirty (30) days.
    """.strip()


def WILL_2_SUB_BENEFICIARIES_RESIDUAL_BENEFICIARY_3_DIES_BLOCK_TEMPLATE(*args):
    return """
    If {entity_3_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, I give the interest in Residual Assets which he would otherwise have received under this Will, to the following persons in the corresponding proportions:
    i.{sub_allocation_percentage:.02f}% (being {sub_entity_3_1_ea_pct:.02f}% of my total interest in the same) to {sub_entity_3_1_name}  absolutely and free from all encumbrances; and
    ii.{sub_allocation_percentage:.02f}% (being {sub_entity_3_2_ea_pct:.02f}% of my total interest in the same) to {sub_entity_3_2_name}  absolutely and free from all encumbrances (for the purpose of this clause, together with the named Substitute Beneficiaries in sub-clause i above, the ﬁApplicable Substitutesﬂ).
    Provided Always that if any of the Applicable Substitutes, should die during my lifetime, or fail to survive me for more than thirty (30) days, the proportion of my Residual Assets which that Applicable Substitute would otherwise have received under this Will shall be distributed equally amongst the issues of that Applicable Substitute so long as they survive me for more than thirty (30) days, and if that Applicable Substitute does not have any issues who have survived me for more than thirty (30) days, then the same shall be distributed equally amongst all the Applicable Substitutes who have survived me for more than thirty (30) days.
    """.strip()


def WILL_2_SUB_BENEFICIARIES_RESIDUAL_BENEFICIARY_3_DIES_LT_100_BLOCK_TEMPLATE(
    num_beneficiaries, *args
):
    return """
    If {entity_3_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, I give the interest in Residual Assets which he would otherwise have received under this Will, to the following persons in the corresponding proportions:
    i.{sub_allocation_percentage:.02f}% (being {sub_entity_3_1_ea_pct:.02f}% of my total interest in the same) to {sub_entity_3_1_name}  absolutely and free from all encumbrances;
    ii.{sub_allocation_percentage:.02f}% (being {sub_entity_3_2_ea_pct:.02f}% of my total interest in the same) to {sub_entity_3_2_name}  absolutely and free from all encumbrances (for the purpose of this clause, together with the named Substitute Beneficiaries in sub-clause i above, the ﬁApplicable Substitutesﬂ); and
    Provided Always that if any of the Applicable Substitutes, should die during my lifetime, or fail to survive me for more than thirty (30) days, the proportion of my Residual Assets which that Applicable Substitute would otherwise have received under this Will shall be distributed equally amongst the issues of that Applicable Substitute so long as they survive me for more than thirty (30) days, and if that Applicable Substitute does not have any issues who have survived me for more than thirty (30) days, then the same shall be distributed equally amongst all the Applicable Substitutes who have survived me for more than thirty (30) days.
    """.strip()


def WILL_1_SUB_BENEFICIARIES_RESIDUAL_BENEFICIARY_1_DIES_BLOCK_TEMPLATE(
    num_beneficiaries, *args
):
    return """
    If {entity_1_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, I give {sub_allocation_percentage:.2f}% (being {sub_entity_1_1_ea_pct:.02f}% of my total interest in the same) of the Residual Assets which he would otherwise have received under this Will to {sub_entity_1_1_name} absolutely and free from all encumbrances, provided always that if {sub_entity_1_1_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, then the same shall be distributed equally amongst his surviving issues absolutely and free from all encumbrances so long as they survive me for more than thirty (30) days
    """.strip() + (
        ".\n"
        if num_beneficiaries == 1
        else """
    , and if {sub_entity_1_1_name} does not have any issues who have survived me for more than thirty (30) days, then the same shall be distributed equally amongst all the Main Substitutes who have survived me for more than thirty (30) days.
    """.strip()
    )


def WILL_1_SUB_BENEFICIARIES_RESIDUAL_BENEFICIARY_1_DIES_LT_100_BLOCK_TEMPLATE(
    num_beneficiaries, *args
):
    return """
    If {entity_1_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, I give {sub_allocation_percentage:.02f}% (being {sub_entity_1_1_ea_pct:.02f}% of my total interest in the same) of the Residual Assets which he would otherwise have received under this Will to {sub_entity_1_1_name} absolutely and free from all encumbrances, provided always that if {sub_entity_1_1_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, then the same shall be distributed equally amongst his surviving issues absolutely and free from all encumbrances so long as they survive me for more than thirty (30) days
    """.strip() + (
        ".\n"
        if num_beneficiaries == 1
        else """
    , and if {sub_entity_1_1_name} does not have any issues who have survived me for more than thirty (30) days, then the same shall be distributed equally amongst all the Main Substitutes who have survived me for more than thirty (30) days.
    """.strip()
    )


def WILL_1_SUB_BENEFICIARIES_RESIDUAL_BENEFICIARY_2_DIES_BLOCK_TEMPLATE(
    num_beneficiaries, *args
):
    return """
    If {entity_2_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, I give {sub_allocation_percentage:.2f}% (being {sub_entity_2_1_ea_pct:.02f}% of my total interest in the same) of the Residual Assets which he would otherwise have received under this Will to {sub_entity_2_1_name} absolutely and free from all encumbrances, provided always that if {sub_entity_2_1_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, then the same shall be distributed equally amongst his surviving issues absolutely and free from all encumbrances so long as they survive me for more than thirty (30) days, and if {sub_entity_2_1_name} does not have any issues who have survived me for more than thirty (30) days, then the same shall be distributed equally amongst all the Main Substitutes who have survived me for more than thirty (30) days.
    """.strip()


def WILL_1_SUB_BENEFICIARIES_RESIDUAL_BENEFICIARY_2_DIES_LT_100_BLOCK_TEMPLATE(
    num_beneficiaries, *args
):
    return """
    If {entity_2_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, I give {sub_allocation_percentage:.02f}% (being {sub_entity_2_1_ea_pct:.02f}% of my total interest in the same) of the Residual Assets which he would otherwise have received under this Will to {sub_entity_2_1_name} absolutely and free from all encumbrances, provided always that if {sub_entity_2_1_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, then the same shall be distributed equally amongst his surviving issues absolutely and free from all encumbrances so long as they survive me for more than thirty (30) days, and if {sub_entity_2_1_name} does not have any issues who have survived me for more than thirty (30) days, then the same shall be distributed equally amongst all the Main Substitutes who have survived me for more than thirty (30) days.
    """.strip()


def WILL_1_SUB_BENEFICIARIES_RESIDUAL_BENEFICIARY_3_DIES_BLOCK_TEMPLATE(*args):
    return """
    If {entity_3_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, I give {sub_allocation_percentage:.2f}% (being {sub_entity_3_1_ea_pct:.02f}% of my total interest in the same) of the Residual Assets which he would otherwise have received under this Will to {sub_entity_3_1_name}  absolutely and free from all encumbrances, provided always that if {sub_entity_3_1_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, then the same shall be distributed equally amongst his surviving issues absolutely and free from all encumbrances so long as they survive me for more than thirty (30) days, and if {sub_entity_3_1_name} does not have any issues who have survived me for more than thirty (30) days, then the same shall be distributed equally amongst all the Main Substitutes who have survived me for more than thirty (30) days.
    """.strip()


def WILL_1_SUB_BENEFICIARIES_RESIDUAL_BENEFICIARY_3_DIES_LT_100_BLOCK_TEMPLATE(
    num_beneficiaries, *args
):
    return """
    If {entity_3_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, I give {sub_allocation_percentage:.02f}% (being {sub_entity_3_1_ea_pct:.02f}% of my total interest in the same) of the Residual Assets which he would otherwise have received under this Will to {sub_entity_3_1_name} absolutely and free from all encumbrances, provided always that if {sub_entity_3_1_name} should die during my lifetime, or fail to survive me for more than thirty (30) days, then the same shall be distributed equally amongst his surviving issues absolutely and free from all encumbrances so long as they survive me for more than thirty (30) days, and if {sub_entity_3_1_name} does not have any issues who have survived me for more than thirty (30) days, then the same shall be distributed equally amongst all the Main Substitutes who have survived me for more than thirty (30) days.
    """.strip()
