from oauth2_provider.models import Application
from rest_framework import serializers
from utils.fields import PrimaryKeyRelatedField
from billing.models import DefaultDiscount
from billing.serializers import DiscountDetailsSerializer

from .models import *


class ApplicationSerialiser(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = [
            "id",
            "client_id",
            "client_type",
            "authorization_grant_type",
            "name",
            "skip_authorization",
        ]


class ApplicationStoreSerializer(serializers.ModelSerializer):
    application = ApplicationSerialiser(required=False, read_only=True)

    class Meta:
        model = ApplicationStore
        fields = "__all__"


class PartnerSerializer(serializers.ModelSerializer):
    application_stores = ApplicationStoreSerializer(
        many=True, required=False, read_only=True)

    class Meta:
        model = Partners
        fields = "__all__"


class PartnerDiscountSerializer(serializers.Serializer):
    """ Generic Model Serializer for Partners Discount Requests """

    user = PrimaryKeyRelatedField(
        required=True, display=False, queryset=WillCraftUser.objects.all())

    application = PrimaryKeyRelatedField(
        required=True, display=False, queryset=Application.objects.none())

    discount = DiscountDetailsSerializer(required=False, read_only=True)

    def __init__(self, *args, **kwargs):
        super(PartnerDiscountSerializer, self).__init__(*args, **kwargs)
        # performance
        if hasattr(self, 'initial_data'):
            user = self.initial_data.get('user', None)
            self.fields['application'].queryset = Application.objects.filter(
                application_store__partner__agents=user
            )

    def set_discount(self, validated_data):
        # getting default discount
        user = validated_data["user"]
        discount = DefaultDiscount.objects.get_default_discount_values(
            validated_data["application"]
        )
        discount["issued_by"] = user.id
        discount["issued_by_application"] = validated_data["application"].id

        # creating discount from default discount
        discount_serializer = DiscountDetailsSerializer(
            data=discount, partial=True
        )
        if discount_serializer.is_valid():
            return discount_serializer.save()

        raise serializers.ValidationError(  # pragma: no cover
            {"discount": discount_serializer.errors}
        )  # pragma: no cover

    def validate_user(self, user):
        if not Partners.objects.filter(agents__in=[user]).exists():
            raise serializers.ValidationError(
                "User does not belong to any Partner!")

        if len(Partners.objects.filter(agents__in=[user])) > 1:
            raise serializers.ValidationError(
                "User belongs to more than one Partner!")
        return user

    def create(self, validated_data):
        """Updates the instance as per usual serializer behavior
        and then updates other serializer fields if a discount
        was added/removed
        """
        validated_data["discount"] = self.set_discount(validated_data)
        return validated_data
