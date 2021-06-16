from core.permissions import BaseOrderPermission
from rest_framework import generics, status
from rest_framework.response import Response
from utils.views import CustomGetCreateUpdateView

from .serializers import *

# Create your views here.


class GetCreateUpdateLastRitesView(CustomGetCreateUpdateView):
    permission_classes = (BaseOrderPermission,)
    serializer_class = LastRitesSerializer


class GetCreateUpdateInstructionsView(CustomGetCreateUpdateView):
    permission_classes = (BaseOrderPermission,)
    serializer_class = InstructionsSerializer
