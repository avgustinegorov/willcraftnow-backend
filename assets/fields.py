from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _
from utils.fields import PrimaryKeyRelatedField

from .models import *


class AssetsPrimaryKeyRelatedField(PrimaryKeyRelatedField):
    def to_internal_value(self, data):
        order = self.context.get("order", None)
        if self.pk_field is not None:
            data = self.pk_field.to_internal_value(data)
        try:
            return self.get_queryset().get(pk=data).get_asset_store(order)
        except ObjectDoesNotExist:
            self.fail("does_not_exist", pk_value=data)
        except (TypeError, ValueError):
            self.fail("incorrect_type", data_type=type(data).__name__)

    def to_representation(self, value):
        if self.pk_field is not None:
            return self.pk_field.to_representation(value.pk)
        try:
            return self.get_queryset().get(asset_store__id=value.pk).id
        except:
            return AssetStore.objects.get(id=value.pk).asset.id
