WILL_OPENING_BLOCK_TEMPLATE = """
Private and Confidential
Dated this ________ of _______ {year}
Last Will and Testament
of
{testator_name}
www.willcraftnow.com
enquiries@willcraftnow.com
1.THIS IS THE LAST WILL AND TESTAMENT of me, {testator_name} (holder of {testator_id_document} No. {testator_id_number}), residing at {testator_address} ("{testator_name}") in respect of all my assets situated in the Republic of Singapore at the time of my death ("Assets").
2.I hereby revoke all former wills and testamentary dispositions made by me, and declare this to be my last will and testament ("Will") and that this Will and any codicil to it shall be construed and take effect in accordance with the laws of the Republic of Singapore.
"""

WILL_SIGN_BLOCK_TEMPLATE = """
SIGNED by the abovenamed Testator
) {testator_name}
)
as {testator_3rd_person} last Will and Testament
)
in the presence of us being present
)
at the same time and who at {testator_3rd_person} request
)
in {testator_3rd_person} presence and in the presence of each other
)
have hereunto subscribed our names as witnesses
)


WITNESSED BY:


Name:
{witness_1_name}
NRIC No.:
{witness_1_nric}
Address:
{witness_1_address}
Name:
{witness_2_name}
NRIC No.:
{witness_2_nric}
Address:
{witness_2_address}
"""

WILL_1_EXECUTOR_BLOCK_TEMPLATE = """
EXECUTOR
%(numbering)d.I appoint {executor_1_name} (holder of NRIC No. {executor_1_nric}), residing at {executor_1_address} ("{executor_1_name}") to be the sole Executor and Trustee of this Will ("Executor").
"""

WILL_2_EXECUTORS_BLOCK_TEMPLATE = """
EXECUTORS
%(numbering)d.I appoint the following persons as joint Executors and Trustees of this Will (each my "Executor" and collectively, my "Executors"):
i.{executor_1_name} (holder of NRIC No. {executor_1_nric}), residing at {executor_1_address} ("{executor_1_name}"); and
ii.{executor_2_name} (holder of NRIC No. {executor_2_nric}), residing at {executor_2_address} ("{executor_2_name}").
"""

WILL_3_EXECUTORS_BLOCK_TEMPLATE = """
EXECUTORS
%(numbering)d.I appoint the following persons as joint Executors and Trustees of this Will (each my "Executor" and collectively, my "Executors"):
i.{executor_1_name} (holder of NRIC No. {executor_1_nric}), residing at {executor_1_address} ("{executor_1_name}");
ii.{executor_2_name} (holder of NRIC No. {executor_2_nric}), residing at {executor_2_address} ("{executor_2_name}"); and
iii.{executor_3_name} (holder of NRIC No. {executor_3_nric}), residing at {executor_3_address} ("{executor_3_name}").
"""

WILL_4_EXECUTORS_BLOCK_TEMPLATE = """
EXECUTORS
%(numbering)d.I appoint the following persons as joint Executors and Trustees of this Will (each my "Executor" and collectively, my "Executors"):
i.{executor_1_name} (holder of NRIC No. {executor_1_nric}), residing at {executor_1_address} ("{executor_1_name}");
ii.{executor_2_name} (holder of NRIC No. {executor_2_nric}), residing at {executor_2_address} ("{executor_2_name}");
iii.{executor_3_name} (holder of NRIC No. {executor_3_nric}), residing at {executor_3_address} ("{executor_3_name}"); and
iv.{executor_4_name} (holder of NRIC No. {executor_4_nric}), residing at {executor_4_address} ("{executor_4_name}").
"""

WILL_1_EXECUTOR_CAP_337_BLOCK_TEMPLATE = """
The powers of my Executor named herein shall be in addition and in modification of the Executor's powers under the Trustees Act (Cap. 337) of Singapore, any re-enactment thereof and general terms of the laws of Singapore. For the avoidance of doubt, part IVA and IVB of the Trustees Act (Cap. 337) shall apply.
""".strip()

WILL_2_EXECUTORS_CAP_337_BLOCK_TEMPLATE = """
The powers of my Executors named herein shall be in addition and in modification of the Executor's powers under the Trustees Act (Cap. 337) of Singapore, any re-enactment thereof and general terms of the laws of Singapore. For the avoidance of doubt, part IVA and IVB of the Trustees Act (Cap. 337) shall apply.
""".strip()

WILL_1_EXECUTOR_POWERS_BLOCK_TEMPLATE = """
My Executor shall have full powers to give, sell for cash or upon such terms as he may deem fit, call in and convert into money, any of my Assets or such part or parts thereof as shall be of a saleable or convertible nature, at such time or times and in such manner as my Executor shall, in his absolute and uncontrolled discretion think fit, with power to postpone such sale, calling in and conversion of such property, or of such part or parts thereof for such period or periods as my Executor in his absolute and uncontrolled discretion think fit, and to the extent necessary, have full powers to pay all my liabilities, debts, mortgages, funeral and testamentary expenses, and any taxes payable by reason of my death from my Estate ("Expenses").
""".strip()

WILL_2_EXECUTORS_POWERS_BLOCK_TEMPLATE = """
My Executors shall have full powers to give, sell for cash or upon such terms as they may deem fit, call in and convert into money, any of my Assets or such part or parts thereof as shall be of a saleable or convertible nature, at such time or times and in such manner as my Executors shall, in Their absolute and uncontrolled discretion think fit, with power to postpone such sale, calling in and conversion of such property, or of such part or parts thereof for such period or periods as my Executors in Their absolute and uncontrolled discretion think fit, and to the extent necessary, have full powers to pay all my liabilities, debts, mortgages, funeral and testamentary expenses, and any taxes payable by reason of my death from my Estate ("Expenses").
""".strip()

WILL_1_SUB_EXECUTOR_BLOCK_TEMPLATE = """
%(numbering)d.If for any reason, my Executor is unable or unwilling to act as executor and trustee of this Will, I appoint {sub_executor_name} (holder of NRIC No. {sub_executor_nric}), residing at {sub_executor_address} ("{sub_executor_name}") as the sole Executor and Trustee of this Will ("Executor").
"""

WILL_1_SUB_EXECUTOR_JOINT_BLOCK_TEMPLATE = """
%(numbering)d.If for any reason, any one of my Executors is unable or unwilling to act as executor and trustee of this Will, I appoint {sub_executor_name} (holder of NRIC No. {sub_executor_nric}), residing at {sub_executor_address} ("{sub_executor_name}") as alternative Executor to act jointly with the remaining Executors appointed above ( "Executor" and jointly with the Executors named above, "Executors" ).
"""

WILL_GUARDIAN_BLOCK_TEMPLATE = """
It is my wish that {guardian_name} (holder of NRIC No. {guardian_nric}), residing at {guardian_address} ("{guardian_name}") be appointed as guardian of my child/children.
""".strip()

WILL_GUARDIAN_JOINT_BLOCK_TEMPLATE = """
It is my wish that {guardian_name} (holder of NRIC No. {guardian_nric}), residing at {guardian_address} ("{guardian_name}") be appointed as guardian of my child/children, as the case may be jointly with my spouse, or solely if my spouse is not able to act by reason of death or incapacity.
""".strip()

WILL_INSTRUCTIONS_BURIED_BLOCK_TEMPLATE = """
It is my wish to be buried in Singapore.
""".strip()

WILL_INSTRUCTIONS_SCATTERED_BLOCK_TEMPLATE = """
It is my wish to be cremated and my ashes to be scattered at sea.
""".strip()

WILL_INSTRUCTIONS_CREMATED_BLOCK_TEMPLATE = """
It is my wish to be cremated and my ashes to be kept at the crematorium at
Mandai Crematorium and Columbarium Complex.
""".strip()

WILL_LASTRITES_FUNERAL_BLOCK_TEMPLATE = """
It is my wish that a non-religious funeral be held at Santa's House for 2 days.
""".strip()
