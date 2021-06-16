from rest_framework import serializers
from utils.serializers import CustomModelSerializer
from utils.fields import PrimaryKeyRelatedField
from utils.mixins import DisplayValuesMixin
from core.models import WillOrder
from .models import *


class LastRitesSerializer(DisplayValuesMixin, CustomModelSerializer):
    """A ModelSerializer for the WillArrangements class that
    also includes support for setting the order by primary key
    """

    order = PrimaryKeyRelatedField(
        display=False, queryset=WillOrder.objects.all(), write_only=True

    )

    class Meta:
        model = WillLastRites
        fields = "__all__"
        display_fields = ['funeral_religion']


class InstructionsSerializer(DisplayValuesMixin, CustomModelSerializer):
    """A ModelSerializer for the WillArrangements class that
    also includes support for setting the order by primary key
    """

    order = PrimaryKeyRelatedField(
        display=False, queryset=WillOrder.objects.all(), write_only=True
    )

    class Meta:
        model = WillInstructions
        fields = "__all__"
        display_fields = ['crematorium_location']
