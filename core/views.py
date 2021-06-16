from django.shortcuts import get_object_or_404
from oauth2_provider.contrib.rest_framework import TokenHasScope
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.query_logger import query_debugger
from utils.views import SanitizeOrderPkMixin

from .models import *
from .parsers import ImageUploadParser
from .permissions import BaseOrderPermission
from .serializers import *
from billing.services import InvoiceService


class CreateOrderView(generics.CreateAPIView):
    """A Generic CREATE API view for WillOrders
    mainly used for creating blank orders through
    the serializer

    endpoint: /order/

    post: Create and return a new Order from the data provided in the request body
    """

    permission_classes = [TokenHasScope, BaseOrderPermission]
    required_scopes = ["read", "write"]

    def get_serializer_class(self):
        order_type = self.kwargs.get("order_type", 'WILL')
        if order_type.upper() == "WILL":
            return WillOrderSerializer
        elif order_type.upper() == "LPA":
            return LPAOrderSerializer
        elif order_type.upper() == "SCHEDULE_OF_ASSETS":
            return AssetScheduleOrderSerializer


class ListOrderView(generics.ListAPIView):
    """A Generic List API for the TipsKeyWords model

    endpoint: /TipsKeyWords/<order_type>/<step>

    GET: Returns a list of all TipsKeyWords instances filtered by order_type and step
    """

    permission_classes = [TokenHasScope, BaseOrderPermission]
    required_scopes = ["read"]
    serializer_class = OrderListSerializer

    def get_queryset(self):
        """Returns a list of orders belonging to the order
        filtered by user.
        """
        return WillOrder.objects.filter(user=self.request.user)


class RetrieveOrderView(SanitizeOrderPkMixin, generics.RetrieveAPIView):
    """A Generic DETAIL/UPDATE view for WillOrders
    that also provides update functionality for the order user from
    currently authorized user on PUT

    endpoint: /order/<order_pk>/

    get: Return a detailed representation of the given order

    """

    permission_classes = (BaseOrderPermission,)

    def get_serializer_class(self):
        if self.order_type.upper() == "WILL":
            return WillOrderSerializer
        elif self.order_type.upper() == "LPA":
            return LPAOrderSerializer
        elif self.order_type.upper() == "SCHEDULE_OF_ASSETS":
            return AssetScheduleOrderSerializer

    def get_object(self):
        """ Returns the order belonging to the given pk value """

        order = self.get_order_instance(
            prefetch_related=[
                "entitystore_set",
                "entitystore_set__entity_roles",
                "entitystore_set__entity_details",
                "entitystore_set__entity_details__charity",
                "entitystore_set__entity_details__person",
                "entitystore_set__donee_powers",
                "legal_services_witnessservice",
                "legal_services_witnessservice__firm",
                "invoice",
                "invoice__discounts",
            ],
            select_related=[
                "instructions",
                "last_rites",
                "user",
                "user__personal_details",
                "property_and_affairs_restrictions",
                "personal_welfare_restrictions",
            ],
        )

        # setting this for use in get_serializer_class
        self.order_type = order.order_type
        return order


class OrderViewValidationMixin:
    permission_classes = (BaseOrderPermission,)

    def validate_order(self, order):
        """ Validates that the order is ready for will generation """

        # Confirming that the user has a user
        assert order.user is not None, "Order doesn't have a linked user!"

        InvoiceService(order).validate()

        return order


class MyUploadView(APIView):  # pragma: no cover
    parser_class = (ImageUploadParser,)

    def put(self, request, format=None):
        if "file" not in request.data:
            raise ParseError("Empty content")

        f = request.data["file"]

        try:
            img = Image.open(f)
            img.verify()
        except:
            raise ParseError("Unsupported image type")

        mymodel.my_file_field.save(f.name, f, save=True)
        return Response(status=status.HTTP_201_CREATED)

    def delete(self, request, format=None):
        mymodel.my_file_field.delete(save=True)
        return Response(status=status.HTTP_204_NO_CONTENT)
