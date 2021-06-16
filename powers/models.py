from django.db import models
from django.utils.translation import ugettext_lazy as _

# Create your models here.
MODE_OF_ACTING_CHOICES = [
    ("JOINTLY", _("Jointly")),
    ("JOINTLY_AND_SEVERALLY", _("Jointly and Severally")),
]

BOOLEAN_CHOICES = [
    ("No", _("No")),
    ("Yes", _("Yes")),
]

RESTRICTION_CHOICES = [
    ("Unrestricted", _("Unrestricted")),
    ("Restricted", _("Restricted")),
    ("Not_Allowed", _("Not Allowed")),
]


class PropertyAndAffairs(models.Model):
    jointly_severally = models.CharField(
        max_length=30,
        choices=MODE_OF_ACTING_CHOICES,
        blank=True,
        null=True,
        verbose_name=_("Mode of Acting"),
        help_text=_(
            "Joint And Severally: Any one of your donees can make decisions for you."
            " <br/> Jointly: All decisions must be agreed by both donees. If they are"
            " unable to agree on a particular issue, then both donees cannot act on"
            " your behalf for that issue."
        ),
    )
    power_to_give_cash = models.CharField(
        max_length=30,
        choices=RESTRICTION_CHOICES,
        default="NO",
        verbose_name=_(
            "Power to Sell Non-residential Property and Give Cash Gifts"),
        help_text=_(
            "If you select Unrestricted, your donee may sell your non-residential"
            " property and make gifts on your behalf, but the remaining cash <u>must be"
            " sufficient for your financial support</u>."
        ),
    )
    cash_restriction = models.DecimalField(
        decimal_places=2,
        max_digits=10,
        blank=True,
        null=True,
        verbose_name=_("Restriction on Cash Gifts (Max Amount)"),
        help_text=_(
            "The total value of the gifts that your donee may make on your behalf in"
            " one calendar year is limited to this amount."
        ),
    )
    power_to_sell_property = models.CharField(
        max_length=30,
        choices=BOOLEAN_CHOICES,
        default="NO",
        verbose_name=_("Power to Sell/Rent/Mortgage Residential Property"),
        help_text=_(
            "If you select No, your donee would have to seek the court’s approval to"
            " sell, transfer, mortgage, or otherwise deal with and affect your interest"
            " in your residential property."
        ),
    )
    restricted_property = models.ForeignKey(
        "assets.RealEstate",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="restricted_property",
        verbose_name=_("Restricted Property"),
        help_text=_(
            "This property may not be sold, transfered, mortgaged, or otherwise dealt"
            " with without court approval."
        ),
    )
    restricted_asset = models.ForeignKey(
        "assets.AssetStore",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="restricted_asset",
        verbose_name=_("Restricted Property"),
        help_text=_(
            "This property may not be sold, transfered, mortgaged, or otherwise dealt"
            " with without court approval."
        ),
    )
    order = models.OneToOneField(
        "core.WillOrder",
        on_delete=models.CASCADE,
        null=False,
        related_name="property_and_affairs_restrictions",
    )

    def __str__(self):
        return f"Power of Property and Affairs - {self.order}"


class PersonalWelfare(models.Model):
    power_to_refuse = models.CharField(
        max_length=30,
        choices=BOOLEAN_CHOICES,
        verbose_name=_("Power to Refuse or Accept Medical Treatment"),
        help_text=_(
            "This includes power to give or refuse consent to start or continue your"
            " treatments, including clinical trials (which involve the testing of new"
            " health substances such as medication or medical devices)."
        ),
    )
    jointly_severally = models.CharField(
        max_length=30,
        choices=MODE_OF_ACTING_CHOICES,
        blank=True,
        null=True,
        verbose_name=_("Mode of Acting"),
        help_text=_(
            "Joint And Severally: Any one of your donees can make decisions for you."
            " <br/> Jointly: All decisions must be agreed by both donees. If they are"
            " unable to agree on a particular issue, then both donees cannot act on"
            " your behalf for that issue."
        ),
    )
    order = models.OneToOneField(
        "core.WillOrder",
        on_delete=models.CASCADE,
        null=False,
        related_name="personal_welfare_restrictions",
    )

    def __str__(self):
        return f"Power of Personal Welfare - {self.order}"
