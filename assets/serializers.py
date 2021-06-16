from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from persons.fields import EntityStoresPrimaryKeyRelatedField
from persons.models import Entity, EntityStore, Person
from persons.serializers import CharitySerializer, PersonSerializer
from utils.serializers import CustomModelSerializer, CustomSerializer
from utils.fields import PrimaryKeyRelatedField
from utils.mixins import ListSerializerWithChildModelsMixin, DisplayValuesMixin
from .fields import AssetsPrimaryKeyRelatedField
from .models import *
from .mixins import AssetSerializerMixin


class AllocationSerializer(CustomModelSerializer):
    """A Nested Model Serializer for the allocation model
    with the entity and sub-entity fields
    being rendered in detail from the model and updated/saved
    in the same way
    """

    # TODO: change this entry, this shows up weird on the frontend
    asset_store = AssetsPrimaryKeyRelatedField(
        queryset=Asset.objects.all(), display=False
    )

    asset = serializers.PrimaryKeyRelatedField(
        source='asset_store.asset', read_only=True
    )
    entity = EntityStoresPrimaryKeyRelatedField(
        queryset=Entity.objects.all(), label=_("Beneficiary")
    )
    parent_allocation = PrimaryKeyRelatedField(
        queryset=Allocation.objects.all(), required=False, display=False
    )
    # Allocation amounts / percentages
    effective_allocation_percentage = serializers.DecimalField(
        read_only=True, max_digits=5, decimal_places=2
    )
    effective_allocation_amount = serializers.DecimalField(
        read_only=True, max_digits=15, decimal_places=2
    )

    class Meta:
        model = Allocation
        fields = '__all__'

    def validate_allocation_percentage(self, percentage):
        if percentage is not None and percentage > 100:
            raise serializers.ValidationError(
                _("Percentage can not be above 100%"))
        if percentage is not None and percentage <= 0:
            raise serializers.ValidationError(
                _("Percentage can not be 0% or below 0%"))
        return percentage

    def validate_entity(self, entity):
        if "WITNESS" in entity.entity_roles.all().values_list(
            "type_name", flat=True
        ):
            raise serializers.ValidationError(
                {"entity": _("A Witness can not be allocated to.")}
            )

        return entity

    def validate(self, data):
        # Confirming that the allocated percentages are valid
        asset_store = data.get("asset_store")

        percentage = data.get("allocation_percentage", None)
        entity = data.get("entity", None)
        amount = data.get("allocation_amount", None)
        parent_allocation = data.get("parent_allocation", None)
        previous_allocation = self.instance

        if previous_allocation:
            asset_store = previous_allocation.asset_store

        if asset_store and asset_store.asset.asset_type != "BankAccount" and amount:
            raise serializers.ValidationError(
                {
                    "allocation_amount": _(
                        "You cannot allocate a cash distribution for this asset."
                    )
                }
            )

        if parent_allocation:
            sub_beneficiaries = Allocation.objects.filter(
                parent_allocation=parent_allocation, asset_store=asset_store
            )
            if entity.id in [i.entity.id for i in sub_beneficiaries]:
                if (
                    not self.instance
                    or self.instance
                    and self.instance.entity != entity
                ):
                    raise serializers.ValidationError(
                        {
                            "entity": _(
                                "This person already is a Substitute entity,"
                                " delete the Substitute Allocation before proceeding."
                            )
                        }
                    )
            elif percentage and not Allocation.validate_sub_entity_allocation(
                percentage, previous_allocation, parent_allocation, "percentage"
            ):
                raise serializers.ValidationError(
                    {
                        "allocation_percentage": _(
                            "Total percentage allocated for sub-entities more than"
                            " 100."
                        )
                    }
                )
            elif amount and not Allocation.validate_sub_entity_allocation(
                amount, previous_allocation, parent_allocation, "amount"
            ):
                raise serializers.ValidationError(
                    {
                        "allocation_amount": _(
                            "Total amount allocated for sub-entities more than"
                            " than total"
                        )
                    }
                )
            elif (
                parent_allocation.allocation_percentage
                and not parent_allocation.allocation_amount
                and not percentage
            ):
                raise serializers.ValidationError(
                    {
                        "allocation_percentage": _(
                            "Only percentage allocations are allowed"
                        )
                    }
                )
            # Block that raises an error if the parent has amount, no percentage but sub has no amount
            elif (
                parent_allocation.allocation_amount
                and not parent_allocation.allocation_percentage
                and not amount
            ):
                raise serializers.ValidationError(
                    {"allocation_percentage": _(
                        "Can only have amount allocation")}
                )

            elif entity.id == parent_allocation.entity.id:
                raise serializers.ValidationError(
                    {
                        "entity": _(
                            "Cannot allocate a Substitute Allocation to the same"
                            " Entity."
                        )
                    }
                )
        else:
            if percentage:
                if not Allocation.validate_asset_allocation_percentage(
                    percentage, previous_allocation, asset_store
                ):
                    raise serializers.ValidationError(
                        {
                            "allocation_percentage": _(
                                "Total allocated percentage cannot be more than 100."
                            )
                        }
                    )

            if Allocation.validate_has_allocation(
                amount,
                percentage,
                asset_store,
                entity,
                parent_allocation=parent_allocation,
            ):
                if (
                    not self.instance
                    or self.instance
                    and self.instance.entity != entity
                ):
                    raise serializers.ValidationError(
                        {
                            "entity": _(
                                "You have already allocated to this Appointment."
                            )
                        }
                    )

        return super().validate(data)


class RealEstateSerializer(DisplayValuesMixin, AssetSerializerMixin, CustomModelSerializer):
    """Generic serializer for real estate that supports order update/saves
    through the AssetMixin
    """

    address = serializers.SerializerMethodField(read_only=True)

    def get_address(self, instance):
        return instance.address

    def validate(self, data):
        country = data.get("country", None)
        order = self.context.get("order")
        is_will_order = True if order and order.order_type == "WILL" else False

        if country and not country == "SG" and is_will_order:
            raise serializers.ValidationError(
                {
                    "country": _(
                        "This will only covers assets in Singapore, please include only"
                        " real estate located in Singapore."
                    )
                }
            )
        return super().validate(data)

    class Meta:
        model = RealEstate
        fields = [
            "id",
            "real_estate_type",
            "block_number",
            "floor_number",
            "unit_number",
            "street_name",
            "country",
            "postal_code",
            "mortgage",
            "address",
            "holding_type",
            'display_name',
            "asset_type"
        ]
        display_fields = ['real_estate_type']


class BankAccountSerializer(AssetSerializerMixin, CustomModelSerializer):
    """Generic serializer for bank accounts that supports order update/saves
    through the AssetMixin
    """

    class Meta:
        model = BankAccount
        exclude = ["user", "order", ]


class InsuranceSerializer(AssetSerializerMixin, CustomModelSerializer):
    """Generic serializer for insurances that supports order update/saves
    through the AssetMixin
    """

    class Meta:
        model = Insurance
        exclude = ["user", "order", ]


class InvestmentSerializer(AssetSerializerMixin, CustomModelSerializer):
    """Generic serializer for investments that supports order update/saves
    through the AssetMixin
    """

    class Meta:
        model = Investment
        exclude = ["user", "order", ]


class CompanySerializer(AssetSerializerMixin, CustomModelSerializer):
    """Generic serializer for companies that supports order update/saves
    through the AssetMixin
    """

    class Meta:
        model = Company
        exclude = ["user", "order", ]

    def validate_percentage(self, percentage):
        if percentage is not None and percentage > 100:
            raise serializers.ValidationError(
                _("Percentage can not be above 100%"))
        if percentage is not None and percentage <= 0:
            raise serializers.ValidationError(
                _("Percentage can not be 0% or below 0%"))
        return percentage

    def validate_incorporated_in(self, incorporated_in):
        if incorporated_in is not "SG":
            raise serializers.ValidationError(
                _(
                    "This Will only covers assets in Singapore, please include only"
                    " companies incorporated in Singapore."
                )
            )
        return incorporated_in


class ResidualSerializer(AssetSerializerMixin, CustomModelSerializer):
    """Generic serializer for companies that supports order update/saves
    through the AssetMixin
    """

    def validate(self, data):
        """
        Check for existing order
        """
        user = self.context.get("user")
        if Residual.objects.filter(user=user).exists():
            raise serializers.ValidationError(
                _("You can only have one residual asset per user")
            )
        return super().validate(data)

    class Meta:
        model = Residual
        exclude = ["user", "order", ]


class AssetSerializer(ListSerializerWithChildModelsMixin, serializers.ModelSerializer):

    class Meta:
        model = Asset
        fields = "__all__"
        serializer_map = {
            "RealEstate": RealEstateSerializer,
            "BankAccount": BankAccountSerializer,
            "Insurance": InsuranceSerializer,
            "Investment": InvestmentSerializer,
            "Company": CompanySerializer,
            "Residual": ResidualSerializer,
        }
        model_key = "asset_type"
