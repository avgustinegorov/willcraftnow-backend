from django.utils.translation import ugettext_lazy as _

# Model EntityType
PERSON_TYPES = [
    ("EXECUTOR", _("Executor"),),
    ("SUB_EXECUTOR", _("Substutite Executor"),),
    ("GUARDIAN", _("Guardian"),),
    ("SUB_GUARDIAN", _("Substitute Guardian"),),
    ("WITNESS", _("Witness"),),
    ("BENEFICIARY", _("Beneficiary"),),
    ("DONEE", _("Donee"),),
    ("REPLACEMENT_DONEE", _("Replacement Donee"),),
    ("APPLICANT", _("Applicant"),),
]

# Model DoneePowers
REPLACEMENT_CHOICES = [
    ("ANY", _("Any Donee")),
    ("PERSONAL_WELFARE", _("Any Personal Welfare Donee")),
    ("PROPERTY_AND_AFFAIRS", _("Any Property and Affairs Donee")),
    ("NAMED", _("Named Donee")),
]

POWERS_CHOICES = [
    ("PERSONAL_WELFARE", _("Personal Welfare Only")),
    ("PROPERTY_AND_AFFAIRS", _("Property and Affairs Only")),
    ("BOTH", _("Personal Welfare and Property and Affairs")),
]

# Model Person
BOOLEAN_CHOICES = [
    ("No", _("No")),
    ("Yes", _("Yes")),
]

ID_DOCUMENT_CHOICES = [
    ("NRIC", _("NRIC")),
    ("FIN", _("FIN")),
    ("Passport", _("Passport")),
]

GENDER_CHOICES = [("Male", _("Male")), ("Female", _("Female"))]

RELATIONSHIP_CHOICES = [
    ("Married", _("Married")),
    ("Single", _("Single")),
    ("Divorced", _("Divorced")),
]

RELIGION_CHOICES = [
    ("Not Religious", _("Not Religious")),
    ("Christianity", _("Christian")),
    ("Hinduism", _("Hindu")),
    ("Buddhism", _("Buddhist")),
    ("Taoism", _("Taoist")),
    ("Catholism", _("Catholic")),
    ("Sikhism", _("Sikh")),
]

RELATIONSHIP_WITH_USER_CHOICES = [
    ("Wife", _("Wife")),
    ("Husband", _("Husband")),
    ("Son", _("Son")),
    ("Daughter", _("Daughter")),
    ("Aunt", _("Aunt")),
    ("Uncle", _("Uncle")),
    ("Brother", _("Brother")),
    ("Sister", _("Sister")),
    ("Father", _("Father")),
    ("Mother", _("Mother")),
    ("Grandfather", _("Grandfather")),
    ("Grandmother", _("Grandmother")),
    ("Cousin", _("Cousin")),
    ("Nephew", _("Nephew")),
    ("Niece", _("Niece")),
    ("Other", _("Other")),
]

CITIZENSHIP_STATUS_CHOICES = [
    ("Singapore Citizen", _("Singapore Citizen")),
    ("Singapore Permanent Resident", _("Singapore PR")),
    ("Foreigner", _("Foreigner")),
]

REAL_ESTATE_TYPES = [
    ("HDB_FLAT", _("HDB Flat"),),
    ("HDB_EC", _("HDB Executive Condominium"),),
    ("PRIVATE_CONDOMINIUM", _("Private Condominium"),),
    ("TERRACE", _("Terrace"),),
    ("SEMI_DETACHED", _("Semi-Detached"),),
    ("BUNGALOW", _("Bungalow"),),
]
