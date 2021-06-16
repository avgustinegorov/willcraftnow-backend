from datetime import datetime

from django.db.models import Q
from dateutil.relativedelta import relativedelta
from django.db import models, transaction
from django.utils.translation import ugettext_lazy as _
from django_countries import countries

# Create your models here.
from persons.enums import *
from utils.countries import COUNTRIES_CHOICES


class EntityType(models.Model):
    """Defines a person type that a single
    Person model instance can be
    """

    type_name = models.CharField(
        max_length=60, choices=PERSON_TYPES, blank=False, unique=True
    )

    def __str__(self):
        return self.type_name


class EntityQueryset(models.QuerySet):
    def filter_entity_type(self, entity_type=None, donee_type=None):
        queryset = self
        if entity_type:
            queryset = queryset.filter(
                entity_roles__type_name__in=[entity_type])
        if donee_type:
            queryset = queryset.filter().filter(
                Q(donee__powers=donee_type) | Q(donee__powers="BOTH")
            )
        return queryset


class EntityStoreManager(models.Manager):
    def get_queryset(self):
        return EntityQueryset(self.model, using=self._db)

    def of_entity_type(self, entity_type=None, donee_type=None):
        if not self.instance.__class__.__name__ == 'WillOrder':
            raise Exception("Cannot call this method")

        return self.get_queryset().filter_entity_type(entity_type=entity_type, donee_type=donee_type)


class EntityStore(models.Model):

    # Auto-Now (add) fields to keep track of model changes
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)

    entity_roles = models.ManyToManyField(EntityType, blank=True)
    # remember to update in code
    entity_details = models.ForeignKey(
        "Entity",
        on_delete=models.CASCADE,
        null=True,
        related_name="entity_store",
    )

    # The order this person should be related to
    order = models.ForeignKey(
        "core.WillOrder", on_delete=models.CASCADE, null=False)

    objects = EntityStoreManager()

    def __str__(self):
        return self.entity_details.__str__()

    def get_entity_roles(self):  # Update in the code
        return list(i.type_name for i in self.entity_roles.all())


class DoneePowers(models.Model):
    donee = models.OneToOneField(
        "persons.EntityStore",
        on_delete=models.CASCADE,
        null=False,
        related_name="donee_powers",
        related_query_name="donee",
        verbose_name=_("Donee"),
    )
    powers = models.CharField(
        max_length=20, choices=POWERS_CHOICES, verbose_name=_("Powers"), null=True
    )
    replacement_type = models.CharField(
        max_length=20,
        choices=REPLACEMENT_CHOICES,
        null=True,
        verbose_name=_("Replacement Type"),
    )
    named_main_donee = models.ForeignKey(
        "persons.EntityStore",
        on_delete=models.CASCADE,
        null=True,
        related_name="named_replacement_donee",
        verbose_name=_("Named Replacement"),
    )

    def is_replacement_donee(self):
        return self.replacement_type is not None

    def save(self, *args, **kwargs):
        with transaction.atomic():
            super().save(*args, **kwargs)
            donee_type, _ = EntityType.objects.get_or_create(type_name="DONEE")
            replacement_donee_type, _ = EntityType.objects.get_or_create(
                type_name="REPLACEMENT_DONEE"
            )
            if self.is_replacement_donee():
                self.donee.entity_roles.remove(donee_type)
                self.donee.entity_roles.add(replacement_donee_type)
            else:
                self.donee.entity_roles.remove(replacement_donee_type)
                self.donee.entity_roles.add(donee_type)

    def __str__(self):
        try:
            return _("{} ({} No. {})").format(
                self.donee.entity_details.person.name,
                _(self.donee.entity_details.person.id_document),
                self.donee.entity_details.person.id_number,
            )
        except:
            return self.donee.entity_details.person.name


class Entity(models.Model):
    # Auto-Now (add) fields to keep track of model changes
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)

    user = models.ForeignKey(
        "willcraft_auth.WillCraftUser", on_delete=models.CASCADE, null=True, related_name="entities",
    )

    # This is overridden in each derived class's save method
    # Update in the code
    entity_type = models.CharField(
        max_length=100, default="Person", blank=True, verbose_name=_("Entity Type")
    )

    def __str__(self):
        label_map = {"Person": "Person", "Charity": "Charity"}
        attr = getattr(self, label_map[self.entity_type].lower())
        return f"{attr}"

    def get_entity_store(self, order):
        try:
            return self.entity_store.get(order=order)
        except EntityStore.DoesNotExist:
            print("CREATING ENTITY STORE", order)
            return EntityStore.objects.create(order=order, entity_details=self)


class Charity(Entity):
    name = models.CharField(max_length=256, blank=False,
                            verbose_name=_("Name"))
    UEN = models.CharField(max_length=256, blank=False, verbose_name=_("UEN"))

    def save(self, *args, **kwargs):
        """ Updates the asset type to the class name """
        self.entity_type = "Charity"
        super().save(*args, **kwargs)

    def __str__(self):
        try:
            return _("{} (UEN No. {})").format(self.name, self.UEN)
        except:
            return self.name


class Person(Entity):
    # Personal Information Fields
    name = models.CharField(max_length=256, blank=False,
                            verbose_name=_("Name"))
    id_number = models.CharField(
        max_length=9, verbose_name=_("Identification Number"))
    id_document = models.CharField(
        max_length=100,
        choices=ID_DOCUMENT_CHOICES,
        verbose_name=_("Identification Document"),
        blank=False,
    )
    country_of_issue = models.CharField(
        default="SG", verbose_name=_("Country of Issue (Identification Document)"),
        choices=COUNTRIES_CHOICES, max_length=5
    )
    age = models.IntegerField(verbose_name=_("Age"), null=True)
    date_of_birth = models.DateField(
        null=True, verbose_name=_("Date of Birth"))
    real_estate_type = models.CharField(
        max_length=256,
        choices=REAL_ESTATE_TYPES,
        default="HDB_FLAT",
        verbose_name=_("Housing Type"),
    )
    _address = models.CharField(
        max_length=256, verbose_name=_("Address"), blank=True, null=True
    )
    block_number = models.CharField(
        max_length=256, verbose_name=_("Block No."), blank=True, null=True
    )
    floor_number = models.PositiveIntegerField(
        verbose_name=_("Floor No."), blank=True, null=True
    )
    unit_number = models.PositiveIntegerField(
        verbose_name=_("Unit No."), blank=False, null=True
    )
    street_name = models.CharField(
        max_length=256, verbose_name=_("Street Name"), blank=False, null=True
    )
    country = models.CharField(
        default="SG", verbose_name=_("Country of Residence"),
        choices=COUNTRIES_CHOICES, max_length=5
    )
    postal_code = models.CharField(
        max_length=255, blank=False, null=True, verbose_name=_("Postal Code")
    )

    # Strict Options Fields
    religion = models.CharField(
        max_length=100, choices=RELIGION_CHOICES, blank=True, verbose_name=_("Religion")
    )
    citizenship_status = models.CharField(
        max_length=100,
        choices=CITIZENSHIP_STATUS_CHOICES,
        default="Singapore Citizen",
        verbose_name=_("Citizenship Status"),
    )
    relationship_status = models.CharField(
        max_length=100,
        choices=RELATIONSHIP_CHOICES,
        blank=True,
        verbose_name=_("Relationship Status"),
    )
    underage_children = models.CharField(
        max_length=256,
        choices=BOOLEAN_CHOICES,
        blank=True,
        verbose_name=_("Underaged Children"),
    )
    gender = models.CharField(
        max_length=256, choices=GENDER_CHOICES, blank=True, verbose_name=_("Gender")
    )
    relationship = models.CharField(
        choices=RELATIONSHIP_WITH_USER_CHOICES,
        max_length=520,
        blank=True,
        verbose_name=_("Relationship"),
    )
    relationship_other = models.CharField(
        max_length=120, blank=True, null=True, verbose_name=_("Relationship (Other)")
    )
    contact_number = models.CharField(
        max_length=120, blank=True, verbose_name=_("Contact Number")
    )
    email = models.EmailField(
        max_length=150, blank=True, verbose_name=_("Email"))

    @property
    def age(self):
        return relativedelta(datetime.now().date(), self.date_of_birth).years

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
            # this is for legacy compatibility
            return self._address

    @property
    def is_private_housing(self):
        return self.real_estate_type in ["TERRACE", "SEMI_DETACHED", "BUNGALOW"]

    @property
    def address_block_only(self):
        required_fields = ["street_name", "address_block"]
        private_housing_required_fields = ["street_name", "unit_number"]

        if self.real_estate_type in ["TERRACE", "SEMI_DETACHED", "BUNGALOW"] and all(
            getattr(self, key) for key in private_housing_required_fields
        ):
            address_chain = [str(self.unit_number), self.street_name]
            return " ".join(address_chain)
        elif all(getattr(self, key) for key in required_fields):
            address_chain = [self.address_block, self.street_name]
            return ", ".join(address_chain)
        else:
            return self.street_name

    def __str__(self):
        try:
            return _("{} ({} No. {})").format(
                self.name, _(self.id_document), self.id_number
            )
        except:
            return self.name

    def save(self, *args, **kwargs):
        """ Updates the asset type to the class name """
        self.entity_type = "Person"
        super().save(*args, **kwargs)
