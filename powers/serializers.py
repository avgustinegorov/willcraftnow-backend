from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from assets.fields import AssetsPrimaryKeyRelatedField
from assets.models import RealEstate
from core.models import WillOrder
from utils.decorators import ExclusiveOrderType
from utils.serializers import CustomModelSerializer
from utils.fields import PrimaryKeyRelatedField
from .models import *


class PropertyAndAffairsSerializer(CustomModelSerializer):
    """ Generic Model Serializer for PropertyAndAffairs """

    order = PrimaryKeyRelatedField(
        queryset=WillOrder.objects.all(), display=False
    )
    authority = serializers.SerializerMethodField(read_only=True)
    restricted_asset = AssetsPrimaryKeyRelatedField(
        queryset=RealEstate.objects.all(),
        required=False,
        allow_null=True,
        label=_("Restricted Property"),
    )

    def validate_jointly_severally(self, jointly_severally):
        order = self.context["order"] if "order" in self.context else None
        donees = order.entitystore_set.of_entity_type(
            'DONEE', "PROPERTY_AND_AFFAIRS")
        if order and len(donees) < 2 and jointly_severally == "JOINTLY_AND_SEVERALLY":
            raise serializers.ValidationError(
                _(
                    "You only have one Donee that can made decisions on your Property"
                    " and Affairs."
                )
            )
        return jointly_severally

    def get_authority(self, instance):  # pragma: no cover
        return PropertyAndAffairs.objects.filter(order_id=instance.order).exists()

    class Meta:
        model = PropertyAndAffairs
        fields = [
            "id",
            "jointly_severally",
            "power_to_give_cash",
            "cash_restriction",
            "power_to_sell_property",
            "restricted_asset",
            "order",
            "authority",
        ]


class PersonalWelfareSerializer(CustomModelSerializer):
    """ Generic Model Serializer for PersonalWelfare """

    authority = serializers.SerializerMethodField(read_only=True)
    order = PrimaryKeyRelatedField(
        queryset=WillOrder.objects.all(), display=False
    )

    def validate_jointly_severally(self, jointly_severally):
        order = self.context["order"] if "order" in self.context else None
        donees = order.entitystore_set.of_entity_type(
            "DONEE", "PERSONAL_WELFARE")
        if order and len(donees) < 2 and jointly_severally == "JOINTLY_AND_SEVERALLY":
            raise serializers.ValidationError(
                _(
                    "You only have one Donee that can made decisions on your Personal"
                    " Welfare."
                )
            )
        return jointly_severally

    def get_authority(self, instance):  # pragma: no cover
        return PersonalWelfare.objects.filter(order_id=instance.order).exists()

    class Meta:
        model = PersonalWelfare
        fields = "__all__"
