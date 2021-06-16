from rest_framework import generics, status
from rest_framework.response import Response

from core.permissions import BaseOrderPermission
from utils.views import CustomGetCreateUpdateView, SanitizeOrderPkMixin

from .models import Allocation, Asset
from .serializers import *
# Create your views here.


class ListAssetView(generics.ListAPIView):
    permission_classes = (BaseOrderPermission,)
    serializer_class = AssetSerializer

    def get_queryset(self):
        """Returns a list of assets belonging to the order
        filtered by user.
        """
        return self.request.user.assets.all()


class RetrieveUpdateDestroyAssetView(CustomGetCreateUpdateView):
    """A Generic RETRIEVE/UPDATE view for Assets that supports
    all kinds of predefined assets (but are not capable of updating the order through the URL)
    The order must be provided in the request body if it needs to be updated

    endpoint: order/<order_pk>/assets/<asset_type>/<asset_pk>/

    get: Return a detailed representation of the asset

    put: Update the given asset with the data in the request's body

    patch: Partially Update the given asset with the data provided in the request's body

    delete: Delete the allocation identified by the asset pk url kwarg
    """

    permission_classes = (BaseOrderPermission,)

    def get_serializer_class(self):
        """Returns the serializer class for the provided
        asset type
        """
        serializer_map = {
            "RealEstate": RealEstateSerializer,
            "BankAccount": BankAccountSerializer,
            "Insurance": InsuranceSerializer,
            "Investment": InvestmentSerializer,
            "Company": CompanySerializer,
            "Residual": ResidualSerializer,
        }

        return serializer_map[self.kwargs.get("asset_type", "RealEstate")]

    def get_object(self):
        if "asset_pk" in self.kwargs:
            model = self.get_serializer_class().Meta.model
            return model.objects.get(id=self.kwargs["asset_pk"])


class RetrieveUpdateDestroyAllocationView(CustomGetCreateUpdateView):
    """A Generic update view for allocations meant to be
    used for updating an allocation's percentages/person assignment

    endpoint: order/<order_pk>/allocations/<allocation_pk>/

    put: Update the given allocation with the data provided in the request's body

    patch: Partially update the given allocation with the data provided in the request's body

    delete: Delete the allocation identified by the allocation pk url kwarg
    """

    permission_classes = (BaseOrderPermission,)
    serializer_class = AllocationSerializer

    def get_object(self):
        if "allocation_pk" in self.kwargs:
            return Allocation.objects.get(id=self.kwargs["allocation_pk"])
