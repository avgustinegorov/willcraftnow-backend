from decimal import Decimal

""" Contains the an object of charges applied for different functionality """

SERVICES = {
    "ENGLISH_CERTIFICATE": Decimal(49.00).quantize(Decimal(".01")),
    "CHINESE_CERTIFICATE": Decimal(59.00).quantize(Decimal(".01")),
    "ENGLISH_WITNESS": Decimal(79.00).quantize(Decimal(".01")),
    "CHINESE_WITNESS": Decimal(89.00).quantize(Decimal(".01")),
    "ENGLISH_REVIEW": Decimal(49.00).quantize(Decimal(".01")),
    "CHINESE_REVIEW": Decimal(59.00).quantize(Decimal(".01")),
}
PACKAGES = {
    "WILL": {
        "ESSENTIALS": {
            "PRICE": Decimal(49.00).quantize(Decimal(".01")),
            "INCLUDED": {
                "EXECUTOR": 1,
                "SUB_EXECUTOR": 0,
                "GUARDIAN": 0,
                "BENEFICIARY": 1,
                "CHARITY_BENEFICIARY": 0,
                "LASTRITE": 0,
                "INSTRUCTION": 0,
            },
        },
        "BASIC": {
            "PRICE": Decimal(99.00).quantize(Decimal(".01")),
            "INCLUDED": {
                "EXECUTOR": 1,
                "SUB_EXECUTOR": 1,
                "GUARDIAN": 1,
                "BENEFICIARY": 2,
                "CHARITY_BENEFICIARY": 0,
                "LASTRITE": 1,
                "INSTRUCTION": 1,
            },
        },
        "PREMIUM": {"PRICE": Decimal(159.00).quantize(Decimal(".01")), "INCLUDED": {}},
    },
    "LPA": {
        "ESSENTIALS": {
            "PRICE": Decimal(39.00).quantize(Decimal(".01")),
            "INCLUDED": {
                "DONEE": 1,
                "REPLACEMENT_DONEE": 0,
                "PROPERTY_RESTRICTION": 0,
                "GIFTING_RESTRICTION": 0,
            },
        },
        "BASIC": {
            "PRICE": Decimal(49.00).quantize(Decimal(".01")),
            "INCLUDED": {
                "DONEE": 2,
                "REPLACEMENT_DONEE": 1,
                "PROPERTY_RESTRICTION": 1,
                "GIFTING_RESTRICTION": 1,
            },
        },
        "PREMIUM": {"PRICE": Decimal(109.00).quantize(Decimal(".01")), "INCLUDED": {}},
    },
    "SCHEDULE_OF_ASSETS": {
        "ESSENTIALS": {
            "PRICE": Decimal(39.00).quantize(Decimal(".01")),
            "INCLUDED": {},
        },
    },
}
GST = Decimal(7 / 100).quantize(Decimal(".01"))
""" Contains the an object of expiry being 7 days """
WILL_EXPIRY = 7
