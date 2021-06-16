from django.db.models import F
from django.utils import timezone
from django.utils.translation import gettext as _
from rest_framework import serializers, validators

from core.models import WillOrder
from utils.serializers import CustomModelSerializer
from .services import InvoiceService
from .models import Discount, Invoice


class DiscountDetailsSerializer(CustomModelSerializer):
    class Meta:
        model = Discount
        fields = "__all__"


class DiscountSerializer(serializers.Serializer):
    """ A Generic ModelSerializer for adding Discounts """

    discount_code = serializers.CharField()

    def validate(self, data):

        if not Discount.objects.filter(discount_code=data["discount_code"]).exists():
            raise serializers.ValidationError(
                {"discount_code": _("Discount Code does not exist!")}
            )

        if not Discount.objects.filter(
            discount_code=data["discount_code"], is_active=True
        ).exists():
            raise serializers.ValidationError(
                {"discount_code": _("Discount Code is currently not active!")}
            )

        if Discount.objects.filter(
            discount_code=data["discount_code"],
            expiry_date__isnull=False,
            expiry_date__lte=timezone.now(),
        ).exists():
            raise serializers.ValidationError(
                {"discount_code": _("Discount Code has expired!")}
            )

        if Discount.objects.filter(
            discount_code=data["discount_code"],
            max_redeemed__isnull=False,
            max_redeemed__lte=F("redeemed"),
        ).exists():
            raise serializers.ValidationError(
                {"discount_code": _("Discount Code has been redeemed!")}
            )

        return super().validate(data)

    def create(self, validated_data):
        """Updates the instance as per usual serializer behavior
        and then updates other serializer fields if a discount
        was added/removed
        """
        order = WillOrder.objects.get(id=self.context["order"])
        invoice = order.invoice.latest()
        discount = Discount.objects.get(
            discount_code=validated_data["discount_code"])
        invoice.discounts.clear()
        invoice.discounts.add(discount)
        invoice.update_invoice()
        invoice.save()

        return discount


class InvoiceLightSerializer(serializers.ModelSerializer):

    is_amended_invoice = serializers.BooleanField(read_only=True)

    class Meta:
        model = Invoice
        fields = ['id', "been_paid", "expiry_date", "is_amended_invoice"]


class InvoiceSerializer(CustomModelSerializer):  # pragma: no cover
    """ A Generic ModelSerializer for Invoices """

    # Turning the fields that can only be calculated into read-only fields
    # To prevent users from changing them dynamically
    gross_price = serializers.DecimalField(
        decimal_places=2, max_digits=100, required=False, read_only=True
    )
    net_price = serializers.DecimalField(
        decimal_places=2, max_digits=100, required=False, read_only=True
    )
    net_price_after_card_fees = serializers.DecimalField(
        decimal_places=2, max_digits=100, required=False, read_only=True
    )
    card_fees = serializers.DecimalField(
        decimal_places=2, max_digits=100, required=False, read_only=True
    )

    order = serializers.PrimaryKeyRelatedField(
        validators=[validators.UniqueValidator(
            queryset=WillOrder.objects.all())],
        read_only=True,
    )

    discounts = serializers.SlugRelatedField(
        many=True,
        read_only=False,
        slug_field="discount_code",
        queryset=Discount.objects.filter(is_active=True),
    )

    order_type = serializers.CharField(
        read_only=True, source="order.order_type")

    order_number = serializers.CharField(
        read_only=True, source="order.order_number")

    line_items = serializers.SerializerMethodField(read_only=True)

    is_amended_invoice = serializers.SerializerMethodField(read_only=True)

    def get_is_amended_invoice(self, instance):
        return instance.is_amended_invoice()

    def get_line_items(self, instance):
        return InvoiceService(instance.order).get_line_items()

    def update(self, instance, validated_data):
        """Updates the instance as per usual serializer behavior
        and then updates other serializer fields if a discount
        was added/removed
        """
        instance = super().update(instance, validated_data)

        if validated_data.get("discounts", None):
            instance.update_invoice()
            instance.save()

        return instance

    class Meta:
        model = Invoice
        fields = "__all__"
