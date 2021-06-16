from django.core.exceptions import ObjectDoesNotExist
from utils.fields import PrimaryKeyRelatedField

from .models import *


class EntityStoresPrimaryKeyRelatedField(PrimaryKeyRelatedField):
    def to_internal_value(self, data):
        order = self.context.get("order", None)
        if self.pk_field is not None:
            data = self.pk_field.to_internal_value(data)
        try:
            return self.get_queryset().get(pk=data).get_entity_store(order)
        except ObjectDoesNotExist:
            self.fail("does_not_exist", pk_value=data)
        except (TypeError, ValueError):
            self.fail("incorrect_type", data_type=type(data).__name__)

    def to_representation(self, value):
        if self.pk_field is not None:
            return self.pk_field.to_representation(value.pk)
        try:
            return self.get_queryset().get(entity_store__id=value.pk).id
        except ObjectDoesNotExist:
            return EntityStore.objects.get(id=value.pk).entity_details.id
