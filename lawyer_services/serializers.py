from django.utils.translation import gettext as _
from rest_framework import serializers
from six import add_metaclass
from utils.fields import PrimaryKeyRelatedField
from core.models import WillOrder
from utils.serializers import CustomModelSerializer
from .models import *
from utils.fields import CharField


class SimpleFirmSerializer(serializers.ModelSerializer):
    """ A Generic Model Serializer for firms """

    class Meta:
        model = Firm
        fields = "__all__"


class FirmSerializer(CustomModelSerializer):
    """ A Generic Model Serializer for firms """

    tncs_file_path = serializers.SerializerMethodField(read_only=True)

    def get_tncs_file_path(self, instance):
        return instance.tncs_file.name

    class Meta:
        model = Firm
        fields = "__all__"


@add_metaclass(serializers.SerializerMetaclass)
class LegalServicesSerializerMixin:
    """Generic serializer that contains all of the fields
    common to Asset model(s)
    """

    service_been_paid = serializers.BooleanField(read_only=True)
    order = PrimaryKeyRelatedField(
        display=False, queryset=WillOrder.objects.all()
    )
    firm = serializers.PrimaryKeyRelatedField(
        queryset=Firm.objects.all(), label=_("Firm")
    )
    firm_details = FirmSerializer(source='firm', read_only=True)
    service_type = CharField(display=False)

    def validate_order(self, order):
        if self.Meta.model.objects.filter(order=order).exists():
            raise serializers.ValidationError(
                _(f"Only one instance of {self.Meta.model} allowed.")
            )
        return order


class WitnessServiceSerializer(LegalServicesSerializerMixin, CustomModelSerializer):
    """Generic serializer for witness service that supports order create/saves
    through the LegalServicesSerializerMixin
    """

    class Meta:
        model = WitnessService
        fields = "__all__"


class ReviewServiceSerializer(LegalServicesSerializerMixin, CustomModelSerializer):
    """Generic serializer for review service"""

    class Meta:
        model = ReviewService
        fields = "__all__"


class LPACertificateServiceSerializer(
    LegalServicesSerializerMixin, CustomModelSerializer
):
    """Generic serializer for LPA Certificate Provider service"""

    class Meta:
        model = LPACertificateService
        fields = "__all__"
