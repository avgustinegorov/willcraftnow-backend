from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_countries import countries
# A Set of options for different holding choices
#   Defined as a global variable since it's common amongst multiple assets
from utils.countries import COUNTRIES_CHOICES

HOLDING_OPTIONS = [
    ("INDIVIDUALLY", _("In My Own Name")),
    ("JOINTLY", _("Jointly With Another")),
]

# Create your models here.


class Allocation(models.Model):
    """An allocation model that links a Entity/Sub Entity
    to an Asset
    """

    # Auto-Now (add) fields to keep track of model changes
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)

    # If this Entity isn't a top level Entity - the Entity's parent
    parent_allocation = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, related_name="child_allocation"
    )

    # The asset this allocation is linked to
    # NOT USED ANYMORE.
    asset = models.ForeignKey(
        "Asset",
        on_delete=models.CASCADE,
        related_name="allocation",
        null=True,
        related_query_name="asset",
    )

    # The asset this allocation is linked to
    asset_store = models.ForeignKey(
        "AssetStore", on_delete=models.CASCADE, null=True, related_name="allocation"
    )

    # The target user for this allocation
    # Note that the foreign key points at PersonalDetails, because a Entity is
    # Basically just a set of personal details
    entity = models.ForeignKey(
        "persons.EntityStore",
        on_delete=models.CASCADE,
        related_name="allocation",
        verbose_name=_("Entity"),
    )

    # Allocation amounts / percentages
    allocation_percentage = models.DecimalField(
        null=True,
        blank=False,
        max_digits=6,
        decimal_places=2,
        verbose_name=_("Allocation Percentage"),
    )
    allocation_amount = models.DecimalField(
        null=True, max_digits=15, decimal_places=2, verbose_name=_("Allocation Amount")
    )
    effective_allocation_percentage = models.DecimalField(
        null=True,
        max_digits=6,
        decimal_places=2,
        verbose_name=_("Effective Allocation Percentage"),
    )
    effective_allocation_amount = models.DecimalField(
        null=True,
        max_digits=15,
        decimal_places=2,
        verbose_name=_("Effective Allocation Amount"),
    )

    # TODO: enforce constraints => e.g.
    # class Meta:
    #     constraints = [
    #         models.UniqueConstraint(
    #             fields=['user', "block_number "
    #                     "floor_number"
    #                     "unit_number"
    #                     "street_name"
    #                     "country"
    #                     "postal_code"],  condition=Q(status='DRAFT'), name='unique_allocation'),
    #     ]

    def __str__(self, entity=False, allocation=False):
        if entity:
            return f"{self.entity.entity_details}"
        if allocation:
            return f"{self.get_allocation()}"
        return (
            f"[{self.id}] {self.asset_store.asset.asset_type} to"
            f" {self.entity.entity_details} ({self.get_allocation()}) -"
            f" ({self.asset_store.order})"
        )

    def is_sub_entity(self):
        return self.parent_allocation is not None

    def get_allocation(self):
        # mainly used for str method
        if self.allocation_percentage:
            return (
                f"{self.allocation_percentage}%"
                f" ({self.effective_allocation_percentage}%)"
            )
        if self.allocation_amount:
            return f"${self.allocation_amount} (${self.effective_allocation_amount})"
        else:
            return None

    @staticmethod
    def validate_asset_allocation_percentage(amount, entity, asset_store):
        """Checks to see if the amount that was passed in
        doesn't exceed 100 for all of the asset's allocation
        """
        # Filtering out the sub-entities to calculate this percentage
        entities = Allocation.objects.filter(
            asset_store__asset=asset_store.asset if asset_store else None,
            asset_store__order=asset_store.order if asset_store else None,
            parent_allocation__isnull=True,
            allocation_percentage__isnull=False,
        ).select_related("id", "allocation_percentage")

        if entity:
            entities = entities.exclude(id=entity.id)
        total_percentage = entities.values_list(
            "allocation_percentage", flat=True)

        return sum(total_percentage) + amount <= 100

    @staticmethod
    def validate_sub_entity_allocation(
        amount, sub_entity, parent_allocation, amount_type="percentage"
    ):
        """Checks to confirm that the total "percentage" or "amount"
        of the sub-beneficiaries of a entity doesn't
        a) exceed 100 if parent_allocation is allocated by percentages and
        b) exceed the parent entity's amount if it's allocated by amount
        Before adding a new sub-entity
        """
        sub_beneficiaries = Allocation.objects.filter(
            parent_allocation=parent_allocation
        )

        # Block for allocation percentage (<=100)
        if parent_allocation:
            if (
                parent_allocation.allocation_percentage is not None
                and amount_type == "percentage"
            ):
                if sub_entity:
                    sub_beneficiaries = sub_beneficiaries.exclude(
                        id=sub_entity.id)
                total_percentage = sub_beneficiaries.filter(
                    allocation_percentage__isnull=False
                ).values_list("allocation_percentage", flat=True)
                return sum(total_percentage) + amount <= 100

            elif (
                parent_allocation.allocation_amount is not None
                and amount_type == "amount"
            ):
                if sub_entity:
                    sub_beneficiaries = sub_beneficiaries.exclude(
                        id=sub_entity.id)
                total_amount = sub_beneficiaries.filter(
                    allocation_amount__isnull=False
                ).values_list("allocation_amount", flat=True)
                return sum(total_amount) + amount <= parent_allocation.allocation_amount

        return False

    @staticmethod
    def validate_has_allocation(
        amount, percentage, asset_store, entity, parent_allocation=None
    ):
        """Checks to see if the entity has already been allocated"""
        if (
            percentage
            and Allocation.objects.filter(
                asset_store=asset_store,
                parent_allocation=parent_allocation,
                entity=entity,
                allocation_percentage__isnull=False,
            ).exists()
        ):
            return True
        if (
            amount
            and Allocation.objects.filter(
                asset_store=asset_store,
                parent_allocation=parent_allocation,
                entity=entity,
                allocation_amount__isnull=False,
            ).exists()
        ):
            return True

        return False


class AssetStoreManager(models.Manager):
    def allocations(self):
        return Allocation.objects.filter(asset_store__in=self.get_queryset())

    def main_allocations(self):
        return self.allocations().filter(parent_allocation=None)

    def sub_allocations(self):
        return self.allocations().filter(parent_allocation__isnull=False)


class AssetStore(models.Model):
    # Auto-Now (add) fields to keep track of model changes
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)

    order = models.ForeignKey(
        "core.WillOrder",
        on_delete=models.CASCADE,
        related_name="asset_store",
        related_query_name="order",
        null=True,
    )

    asset = models.ForeignKey(
        "Asset", on_delete=models.CASCADE, null=True, related_name="asset_store"
    )

    objects = AssetStoreManager()

    def __str__(self):
        return self.asset.__str__()


class Asset(models.Model):
    """Defines an Abstract Asset model
    that all other Asset models must inherit from
    to implement Allocation and other such details
    """

    # Auto-Now (add) fields to keep track of model changes
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)

    # This is overridden in each derived class's save method
    asset_type = models.CharField(
        max_length=100,
        default="RealEstate",
        blank=True,
        verbose_name=_("Asset Category"),
    )

    user = models.ForeignKey(
        "willcraft_auth.WillCraftUser",
        on_delete=models.CASCADE,
        null=True,
        related_name="assets",
    )

    # The order this asset belongs to - links all assets directly to the order
    # --> And hence the allocations as well
    order = models.ForeignKey(
        "core.WillOrder",
        on_delete=models.CASCADE,
        null=True,
        related_name="assets",
        related_query_name="order",
    )

    def __str__(self):
        label_map = {
            "RealEstate": _("Real Estate"),
            "BankAccount": _("Bank Account"),
            "Insurance": _("Insurance Policy"),
            "Investment": _("Investment Account"),
            "Company": _("Company Ordinary Shares"),
            "Residual": _("Residual Assets"),
        }
        asset_type = self.asset_type
        attr = getattr(self, asset_type.lower())
        return f"{label_map[asset_type]}: {attr}"

    def get_asset_store(self, order):
        for asset_store in self.asset_store.all():
            if asset_store.order_id == order.id:
                return asset_store
        return AssetStore.objects.create(order=order, asset=self)


class RealEstate(Asset):
    """An Asset of type "RealEstate"
    Contains the fields generic to Assets and
    fields specific to real estates
    """

    REAL_ESTATE_TYPES = [
        ("HDB_FLAT", _("HDB Flat"),),
        ("HDB_EC", _("HDB Executive Condominium"),),
        ("PRIVATE_CONDOMINIUM", _("Private Condominium"),),
        ("TERRACE", _("Terrace"),),
        ("SEMI_DETACHED", _("Semi-Detached"),),
        ("BUNGALOW", _("Bungalow"),),
    ]

    MORTGAGE_OPTIONS = [
        ("NO_MORTGAGE", _("Fully Paid Up")),
        ("MORTGAGE", _("Still Under Mortgage")),
    ]

    REAL_ESTATE_HOLDING_OPTIONS = [
        ("SOLE_OWNER", _("Sole Owner")),
        ("JOINT_TENANT", _("Joint Tenant")),
        ("TENANT_IN_COMMON", _("Tenant in Common")),
    ]
    # Address Fields
    block_number = models.CharField(
        max_length=256, verbose_name=_("Block No."), blank=False, null=True
    )
    floor_number = models.PositiveIntegerField(
        verbose_name=_("Floor No."), blank=False, null=True
    )
    unit_number = models.PositiveIntegerField(
        verbose_name=_("Unit No."), blank=False, null=True
    )
    street_name = models.CharField(
        max_length=256, verbose_name=_("Street Name"), blank=False, null=True
    )
    country = models.CharField(
        default="SG", verbose_name=_("Country"),
        choices=COUNTRIES_CHOICES, max_length=5
    )
    postal_code = models.CharField(
        max_length=255, blank=False, null=True, verbose_name=_("Postal Code")
    )
    _address = models.CharField(
        max_length=256, blank=True, null=True, verbose_name=_("Address")
    )

    # Choice Fields
    real_estate_type = models.CharField(
        max_length=256,
        choices=REAL_ESTATE_TYPES,
        default="HDB_FLAT",
        verbose_name=_("Real Estate Type"),
    )
    mortgage = models.CharField(
        max_length=256,
        choices=MORTGAGE_OPTIONS,
        default="MORTGAGE",
        verbose_name=_("Mortgage"),
    )
    holding_type = models.CharField(
        blank=False,
        max_length=256,
        choices=REAL_ESTATE_HOLDING_OPTIONS,
        verbose_name=_("Holding Type"),
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', "block_number "
                        "floor_number"
                        "unit_number"
                        "street_name"
                        "country"
                        "postal_code"],  name='unique_real_estate'),
        ]

    def __str__(self):
        try:
            return (
                f"{next(x[1] for x in self.REAL_ESTATE_TYPES if x[0] == self.real_estate_type)}"
                f" - {next(x[1] for x in tuple(countries) if x[0] == self.country)}"
                f" ({self.postal_code})"
            )
        except:
            return f"{self.real_estate_type} - {self.country} ({self.postal_code})"

    @property
    def address_unit(self):
        unit_number = self.unit_number
        floor_number = self.floor_number

        if unit_number and int(unit_number) < 10:
            unit_number = f"0{unit_number}"

        if floor_number and int(floor_number) < 10:
            floor_number = f"0{floor_number}"

        if unit_number:
            if floor_number:
                return f"#{floor_number}-{unit_number}"
            else:
                return f"{unit_number}"

    @property
    def address_block(self):
        if (
            self.real_estate_type in ["HDB_FLAT",
                                      "HDB_EC", "PRIVATE_CONDOMINIUM"]
            and self.block_number
            and self.block_number != "-"
        ):
            return f"Blk {self.block_number}"
        else:
            return ""

    @property
    def address_street_postal_code(self):
        country = dict(countries)[self.country]
        return f"{self.street_name} {country}({self.postal_code})"

    @property
    def address(self):
        required_fields = ["street_name",
                           "country", "postal_code", "unit_number"]
        if all(getattr(self, key) for key in required_fields):
            address_chain = [
                self.address_unit,
                self.address_block,
                self.address_street_postal_code,
            ]
            return " ".join(address_chain)
        else:
            # this is for legacy compatibiilty
            return self._address

    def save(self, *args, **kwargs):
        """ Updates the asset type to the class name """
        self.asset_type = "RealEstate"
        super(RealEstate, self).save(*args, **kwargs)


class BankAccount(Asset):
    """An Asset of type "BankAccount"
    Contains the fields generic to Assets and
    fields specific to bank accounts
    """

    bank = models.CharField(max_length=256, blank=False,
                            verbose_name=_("Bank"))
    account_number = models.CharField(
        max_length=256, blank=False, verbose_name=_("Account Number")
    )
    holding_type = models.CharField(
        blank=False,
        max_length=256,
        choices=HOLDING_OPTIONS,
        verbose_name=_("Holding Type"),
    )

    constraints = [
        models.UniqueConstraint(
            fields=['user', 'bank', 'account_number'],  name='unique_bankaccount'),
    ]

    def __str__(self):
        return f"{self.bank} ({self.account_number[-4:]})"

    def save(self, *args, **kwargs):
        """ Updates the asset type to the class name """
        self.asset_type = "BankAccount"
        super(BankAccount, self).save(*args, **kwargs)


class Insurance(Asset):
    """An Asset of type "Insurance"
    Contains the fields generic to Assets and
    fields specific to insurances
    """

    EXISTING_NOMINATIONS_OPTIONS = [("NO", _("No")), ("YES", _("Yes"))]
    insurer = models.CharField(max_length=256, verbose_name=_("Insurer"))
    plan = models.CharField(
        max_length=256, blank=False, verbose_name=_("Insurance Plan")
    )
    policy_number = models.CharField(
        max_length=256, blank=False, verbose_name=_("Policy Number")
    )
    has_existing_nomination = models.CharField(
        blank=False,
        max_length=256,
        choices=EXISTING_NOMINATIONS_OPTIONS,
        verbose_name=_("Has Existing Nomination"),
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'insurer', 'policy_number'],  name='unique_insurance'),
        ]

    def __str__(self):
        return f"{self.plan} ({self.policy_number})"

    def save(self, *args, **kwargs):
        """ Updates the asset type to the class name """
        self.asset_type = "Insurance"
        super(Insurance, self).save(*args, **kwargs)


class Investment(Asset):
    """An Asset of type "Investment"
    Contains the fields generic to Assets and
    fields specific to investments
    """

    financial_institution = models.CharField(
        max_length=256, blank=False, verbose_name=_("Bank/Financial Institution")
    )
    account_number = models.CharField(
        max_length=256, blank=False, verbose_name=_("Investment Account Number")
    )
    holding_type = models.CharField(
        max_length=256,
        choices=HOLDING_OPTIONS,
        blank=False,
        verbose_name=_("Holding Type"),
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'financial_institution', 'account_number'],  name='unique_investment'),
        ]

    def __str__(self):
        return f"{self.financial_institution} ({self.account_number[-4:]})"

    def save(self, *args, **kwargs):
        """ Updates the asset type to the class name """
        self.asset_type = "Investment"
        super(Investment, self).save(*args, **kwargs)


class Company(Asset):
    """An Asset of type "Company"
    Contains the fields generic to Assets and
    fields specific to companies
    """

    name = models.CharField(max_length=256, blank=False,
                            verbose_name=_("Company Name"))
    registration_number = models.CharField(
        max_length=256, blank=False, verbose_name=_("Company Registration Number")
    )
    incorporated_in = models.CharField(
        blank=False, verbose_name=_("Country of Incorporation"),
        choices=COUNTRIES_CHOICES, max_length=5
    )

    shares_amount = models.IntegerField(
        verbose_name=_("Amount of Ordinary Shares"))
    percentage = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name=_("Percentage of Ordinary Shares Owned"),
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'registration_number',
                                            'incorporated_in'],  name='unique_company'),
        ]

    def __str__(self):
        return f"{self.name} ({self.registration_number})"

    def save(self, *args, **kwargs):
        """ Updates the asset type to the class name """
        self.asset_type = "Company"
        super(Company, self).save(*args, **kwargs)


class Residual(Asset):
    """An Asset of type "Residual"
    Contains the fields generic to Assets and
    fields specific to companies
    """

    constraints = [
        models.UniqueConstraint(fields=['user'],  name='unique_residual'),
    ]

    def __str__(self):
        return f"Default Allocation"

    def save(self, *args, **kwargs):
        """ Updates the asset type to the class name """
        self.asset_type = "Residual"
        super(Residual, self).save(*args, **kwargs)
