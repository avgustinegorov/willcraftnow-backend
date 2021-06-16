from django.db import models
from django.utils.translation import ugettext_lazy as _

# Create your models here.


class WillInstructions(models.Model):
    """Represents a set of specific instructions
    that the User wants to leave behind in his Will
    for his death proceedings
    """

    CREMATION_INSTRUCTIONS = [
        ("CREMATED", _("Held at a crematorium")),
        ("BURIED", _("Buried in Singapore")),
        ("SCATTERED", _("Scattered in the Sea")),
    ]

    CREMATION_LOCATIONS = [
        (
            "MANDAI_CREMATORIUM_AND_COLUMBARIUM_COMPLEX",
            _("Mandai Crematorium and Columbarium Complex"),
        ),
        ("CHOA_CHU_KANG_COLUMBARIUM", _("Choa Chu Kang Columbarium")),
        ("TSE_TOH_AUM_TEMPLE", _("Tse Toh Aum Temple")),
        (
            "KONG_MENG_SAN_PHOR_KARK_SEE_MONASTERY",
            _("Kong Meng San Phor Kark See Monastery"),
        ),
    ]

    # Auto-Now (add) fields to keep track of model changes
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)

    # Arrangement details
    instructions = models.CharField(
        max_length=256,
        blank=True,
        choices=CREMATION_INSTRUCTIONS,
        verbose_name=_("Instructions"),
    )
    crematorium_location = models.CharField(
        max_length=256,
        choices=CREMATION_LOCATIONS,
        blank=True,
        null=True,
        verbose_name=_("Crematorium Location"),
    )

    # One to one field to WillOrders since a particular will can only have one arrangement
    order = models.OneToOneField(
        "core.WillOrder",
        on_delete=models.CASCADE,
        null=False,
        related_name="instructions",
    )


class WillLastRites(models.Model):
    """Represents a set of specific instructions
    that the User wants to leave behind in his Will
    for his last rites
    """

    RELIGION_OPTIONS = [
        ("NON_RELIGIOUS", _("Non-religious")),
        ("CHRISTIAN", _("Christian")),
        ("HINDU", _("Hindu")),
        ("BUDDHIST", _("Buddhist")),
        ("TAOIST", _("Taoist")),
        ("CATHOLIC", _("Catholic")),
        ("SIKH", _("Sikh")),
    ]

    # Auto-Now (add) fields to keep track of model changes
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)

    # Arrangement details
    funeral_religion = models.CharField(
        max_length=256,
        choices=RELIGION_OPTIONS,
        blank=True,
        verbose_name=_("Religion for Funeral Rites"),
    )
    funeral_location = models.CharField(
        max_length=256, blank=True, verbose_name=_("Location of Funeral")
    )
    funeral_duration = models.IntegerField(
        blank=True, null=True, verbose_name=_("Duration of Funeral (Days)")
    )

    # One to one field to WillOrders since a particular will can only have one arrangement
    order = models.OneToOneField(
        "core.WillOrder",
        on_delete=models.CASCADE,
        null=False,
        related_name="last_rites",
    )
