from rest_framework import generics, status
from rest_framework.response import Response

from core.permissions import BaseOrderPermission
from persons.models import EntityStore, EntityType
from utils.views import CustomGetCreateUpdateView

from .serializers import *


class ListFirmView(generics.ListAPIView):
    permission_classes = (BaseOrderPermission,)
    serializer_class = SimpleFirmSerializer

    def get_queryset(self):
        """Returns a list of assets belonging to the order
        filtered by user.
        """
        return Firm.objects.all()

class LegalServicesSerializerProviderMixin:
    """A Mixin to provide a get_serializer_class method that
    can be used in all views that require serializer selection
    based on the the "asset_type" url parameter
    """

    permission_classes = (BaseOrderPermission,)

    def get_serializer_class(self):
        """Returns the serializer class for the provided
        asset type
        """
        serializer_map = {
            "witness": WitnessServiceSerializer,
            "review": ReviewServiceSerializer,
            "certificate_provider": LPACertificateServiceSerializer,
        }

        return serializer_map[self.kwargs.get("service_type", "witness")]


class RetrieveUpdateDestroyLegalServicesView(
    LegalServicesSerializerProviderMixin, CustomGetCreateUpdateView
):
    """A Generic RETRIEVE/CREATE/DESTRPY view for legal services

    endpoint: order/<str:order_pk>/service/<str:service_type>/<int:service_pk>/

    get: Return a detailed representation of the service

    post: Create the given service with the data in the requests body

    delete: Delete the allocation identified by the service pk url kwarg
    """

    def create(self, request, *args, **kwargs):
        additional_data = {
            "review_type": "CN" if self.request.LANGUAGE_CODE == "zh-cn" else "EN"
        }
        response = super().create(
            request, *args, additional_data=additional_data, **kwargs
        )

        # deleting witnesses person type from persons
        order = WillOrder.objects.get(id=self.kwargs["order_pk"])
        if order.order_type == "WILL":
            witness_entity_type, _ = EntityType.objects.get_or_create(
                type_name="WITNESS"
            )
            witnesses = EntityStore.objects.filter(
                order=order, entity_roles__in=[witness_entity_type]
            )
            if witnesses:
                for witness in witnesses:
                    witness.entity_roles.remove(witness_entity_type)
                    witness.save()

        return response

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.service_been_paid():
            return Response(
                data={"message": "Too late to delete"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        self.perform_destroy(obj)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_400_BAD_REQUEST)
