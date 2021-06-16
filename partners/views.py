from rest_framework import generics, permissions, status
from rest_framework.response import Response

from .models import Partners
from .serializers import *

# Create your views here.


class GetPartnerDiscount(generics.CreateAPIView):
    serializer_class = PartnerDiscountSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = PartnerDiscountSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )  # pragma: no cover


class PartnersListView(generics.ListAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = PartnerSerializer
    queryset = Partners.objects.filter(
        application_stores__application__authorization_grant_type__in=[
            "password"]
    )
