After Billing, you store the order limit, because there is a free 7 day edit period where the person can go and edit the order. In this time, if the order it edited such that the order limit is higher than the package, then an additional invoice will be generated and payment will be required for the difference.

Order -----> Core: WillRepo v1 PDF
      -----> Core: WillRepo v2 PDF
      -----> Core: WillRepo v2 PDF

      -----> Billing: Invoice     -------> Billing: InvoiceRepo v1 PDF
                                  -------> Billing: InvoiceRepo v2 PDF


Users can have multiple order, multiple assets, and multiple People

User  -----> Core: Orders (LPA)
      -----> Core: Orders (Will)
      -----> Core: Orders (Schedule of Assets)

      -----> Persons: Beneficiary (PersonalDetails)
      -----> Persons: Beneficiary (Charity)

      -----> Assets: Asset (RealEstate)
      -----> Assets: Asset (InvestmentAccount)
      -----> Assets: Asset (BankAccount)
      -----> Assets: Asset (Insurance)
      -----> Assets: Asset (Company)
      -----> Assets: Asset (Residual)

*** Example ***
Give 100% of Asset A to Person B
Give 100% of Asset A to Person B BUT if Person B dies before me, give to Person A

*** Will ***
Order ------> Assets: AssetStore             -------> Assets: 1 Asset
                     [As Many As Possible]   -------> Assets: 1 Allocation    -------> Persons: 1 Appointment                          -------> persons: Beneficiary (Charity/PD)
                                                                              -------> Assets: 1 Parent Beneficiary (Allocation/Self)

      ------> lastrites: 1 WillInstructions
      ------> lastrites: 1 WillLastRites


      ------> persons: Appointment            -------> persons: 1 PersonalDetails
                                              -------> persons: 1 AppointmentType

      ------> lawyerservices: 1 LegalServices


*** LPA ***
Order ------> persons: DoneePowers            ------> persons: Appointment            -------> persons: 1 PersonalDetails
                                                                                      -------> persons: 1 AppointmentType

      ------> powers: 1 PropertyAndAffairs
      ------> powers: 1 PersonalWelfare

      ------> lawyerservices: 1 LegalServices

*** Schedule of Assets ***
Order ------> Assets: Asset
