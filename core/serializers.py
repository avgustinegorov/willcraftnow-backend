from django.contrib.auth.models import AnonymousUser
from django.core.files import File
from rest_framework import serializers
from rest_framework.renderers import JSONRenderer
from rest_framework.validators import UniqueValidator
from six import add_metaclass
from django.conf import settings
from services.s3.s3_interface import S3Interface
from assets.models import Residual
from assets.serializers import AllocationSerializer, AssetSerializer
from billing.serializers import InvoiceLightSerializer, InvoiceSerializer
from core.models import WillOrder
from lastrites.serializers import InstructionsSerializer, LastRitesSerializer
from lawyer_services.serializers import (
    LPACertificateServiceSerializer,
    ReviewServiceSerializer,
    WitnessServiceSerializer,
    FirmSerializer)
from persons.serializers import DoneePowersSerializer, EntityStoreSerializer, EntitySerializer
from powers.serializers import PersonalWelfareSerializer, PropertyAndAffairsSerializer
from utils.serializers import CustomModelSerializer
from willcraft_auth.serializers import WillCraftUserPersonalDetailsSerializer


@add_metaclass(serializers.SerializerMetaclass)
class GenericOrderSerializerMixin:

    latest_invoice = InvoiceLightSerializer(
        required=False, source="invoice.latest")

    pdf_url = serializers.CharField(
        read_only=True, source="will_repo.download_url")

    legal_services = serializers.SerializerMethodField(read_only=True)

    order_number = serializers.CharField(
        max_length=120,
        required=False,
        validators=[UniqueValidator(queryset=WillOrder.objects.all())],
    )

    def create(self, validated_data):
        """ Sets the request's user on the Order if it's present """
        # Getting the user from the request if it exists
        request = self.context.get("request", None)
        if request and request.user.is_authenticated:
            # And setting it as part of the data
            validated_data["user"] = request.user
        # If the user isn't there, trying to set the token
        elif request and request.session["token"]:
            validated_data["token_id"] = request.session["token"]["id"]
        # Raise a validation error if neither of the user/token was provided
        else:
            raise serializers.ValidationError(
                {"auth": "Either the user or token MUST BE PROVIDED!"}
            )

        order = WillOrder(**validated_data)
        order.save()

        return order

    def get_latest_instance(self, instance, attr):
        try:
            return getattr(instance, attr).latest("id")
        except:
            return None

    def get_legal_services(self, instance):
        legal_services = []
        review_service = self.get_latest_instance(
            instance, "legal_services_reviewservice"
        )
        if review_service:
            legal_services.append(ReviewServiceSerializer(review_service).data)
        witness_service = self.get_latest_instance(
            instance, "legal_services_witnessservice"
        )
        if witness_service:
            legal_services.append(
                WitnessServiceSerializer(witness_service).data)
        lpacertificate_service = self.get_latest_instance(
            instance, "legal_services_lpacertificateservice"
        )
        if lpacertificate_service:
            legal_services.append(
                LPACertificateServiceSerializer(lpacertificate_service).data
            )

        return legal_services


class OrderListSerializer(CustomModelSerializer):
    order_number = serializers.CharField(
        max_length=120,
        required=False,
        validators=[UniqueValidator(queryset=WillOrder.objects.all())],
    )

    latest_invoice = InvoiceLightSerializer(
        required=False, source="invoice.latest")

    pdf_url = serializers.CharField(
        read_only=True, source="will_repo.download_url")

    class Meta:
        fields = "__all__"
        model = WillOrder


class LPAOrderSerializer(GenericOrderSerializerMixin, CustomModelSerializer):
    persons = EntityStoreSerializer(
        required=False, many=True, source="entitystore_set.all", read_only=True)

    property_and_affairs_restrictions = PropertyAndAffairsSerializer(
        required=False, read_only=True
    )
    personal_welfare_restrictions = PersonalWelfareSerializer(
        required=False, read_only=True
    )

    replacement_donee = DoneePowersSerializer(required=False, read_only=True)

    class Meta:
        model = WillOrder
        fields = "__all__"


class WillOrderSerializer(GenericOrderSerializerMixin, CustomModelSerializer):
    """A Generic Order Serializer with functionality to
    set the user from the request's user
    """

    persons = EntityStoreSerializer(
        required=False, many=True, source="entitystore_set.all", read_only=True)
    allocations = AllocationSerializer(
        required=False, many=True, source="asset_store.allocations", read_only=True)
    last_rites = LastRitesSerializer(required=False, read_only=True)
    instructions = InstructionsSerializer(required=False, read_only=True)

    def create(self, validated_data):
        """ Sets the request's user on the Order if it's present """
        # Getting the user from the request if it exists
        order = super().create(validated_data)

        request = self.context.get("request", None)
        if not Residual.objects.filter(user=request.user).exists():
            Residual.objects.create(user=request.user)

        return order

    def update(self, instance, validated_data):
        """ Sets the order from the request's user if it's present """
        if instance.user is None:
            request = self.context.get("request", None)
            if request and request.user and type(request.user) != AnonymousUser:
                validated_data["user"] = request.user

        return super().update(instance, validated_data)

    class Meta:
        fields = "__all__"
        model = WillOrder


class AssetScheduleOrderSerializer(GenericOrderSerializerMixin, CustomModelSerializer):
    """A Generic Order Serializer with functionality to
    set the user from the request's user
    """

    assets = AssetSerializer(
        read_only=True, source="user.assets.all", many=True)

    class Meta:
        fields = "__all__"
        model = WillOrder


class OrderJsonSerializer(serializers.Serializer):
    upload_url = serializers.CharField(source="will_repo.upload_url")
    doc_filename = serializers.CharField(source="will_repo.next_filename")
    invoice_upload_url = serializers.SerializerMethodField()
    invoice_filename = serializers.SerializerMethodField()
    data = serializers.SerializerMethodField()
    invoice_data = InvoiceSerializer(source='invoice.latest')
    user = WillCraftUserPersonalDetailsSerializer(
        source="user.personal_details")
    assets = AssetSerializer(source="user.assets.all", many=True)
    entities = EntitySerializer(source="user.entities.all", many=True)
    doc_type = serializers.CharField(source="order_type")
    upload_docs = serializers.SerializerMethodField()

    def get_upload_docs(self, instance):
        # upload only when not local
        return settings.STAGE != "LOCAL"

    def get_invoice_upload_url(self, instance):
        invoice = instance.invoice.latest()
        if invoice:
            return invoice.invoice_repo.upload_url()

    def get_invoice_filename(self, instance):
        invoice = instance.invoice.latest()
        if invoice:
            return invoice.invoice_repo.next_filename()

    def get_serializer(self, order):
        schema = {
            'WILL': WillOrderSerializer,
            'LPA': LPAOrderSerializer,
            "SCHEDULE_OF_ASSETS": AssetScheduleOrderSerializer
        }
        return schema[order.order_type]

    def get_data(self, instance):
        serializer = self.get_serializer(instance)
        return serializer(instance, labels=False, context=self._context).data

    def save_to_repo(self, content=None, local=False, invoice_pdf=None, doc_pdf=None):
        invoice = self.instance.invoice.latest('id')
        order = self.instance
        will_repo_instance = order.will_repo.create(content=content)
        invoice_repo_instance = invoice.invoice_repo.create()

        doc_filename = self.data.get('doc_filename')
        invoice_filename = self.data.get('invoice_filename')

        if local:
            will_repo_instance.will.name = doc_filename
            if doc_pdf:
                will_repo_instance.will.content = File(doc_pdf)
            will_repo_instance.save()

            invoice_repo_instance.invoice_pdf.name = invoice_filename
            if invoice_pdf:
                invoice_repo_instance.invoice_pdf.content = File(invoice_pdf)
            invoice_repo_instance.save()

    @property
    def json(self):
        return JSONRenderer().render(self.data, renderer_context={'indent': 4})
