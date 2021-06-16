import copy
import inspect
import traceback
from collections import OrderedDict
from collections.abc import Mapping

from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import models
from django.db.models import DurationField as ModelDurationField
from django.db.models.fields import Field as DjangoModelField
from django.db.models.fields import FieldDoesNotExist
from django.http import Http404
from django.utils import timezone
from django.utils.encoding import force_str
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions, serializers
from rest_framework.compat import postgres_fields
from rest_framework.exceptions import ErrorDetail, ValidationError
from rest_framework.fields import (
    ChoiceField,
    SerializerMethodField,
    SkipField,
    get_error_detail,
    set_value,
)
from rest_framework.metadata import SimpleMetadata
from rest_framework.relations import PKOnlyObject, PrimaryKeyRelatedField
from rest_framework.request import clone_request
from rest_framework.settings import api_settings
from rest_framework.utils import html, model_meta, representation
from rest_framework.utils.field_mapping import ClassLookupDict
from rest_framework.utils.serializer_helpers import (
    BindingDict, BoundField, JSONBoundField, NestedBoundField, ReturnDict,
    ReturnList
)
from rest_framework.fields import (  # NOQA # isort:skip
    CreateOnlyDefault, CurrentUserDefault, SkipField, empty
)
from rest_framework.serializers import as_serializer_error, BaseSerializer
from .query_logger import query_debugger


class LabelsMixin:
    def __init__(self, *args, **kwargs):

        labels = kwargs.pop("labels", True)

        super().__init__(*args, **kwargs)

        if "labels" in self.fields:
            raise RuntimeError(
                "You cant have labels field defined while using CustomModelSerializer"
            )

        if labels:
            self.fields["labels"] = SerializerMethodField()

    def get_labels(self, *args):
        labels = {}

        if hasattr(self, "Meta"):
            for field in self.Meta.model._meta.get_fields():
                if field.name in self.fields:
                    try:
                        labels[field.name] = field.verbose_name
                    except:
                        labels[field.name] = field.name

        return labels


class CustomSerializer(LabelsMixin, serializers.Serializer):
    pass


class CustomModelSerializer(LabelsMixin, serializers.ModelSerializer):
    pass


class CustomMetaData(SimpleMetadata):
    def get_field_info(self, field):  # pragma: no cover
        """
        Given an instance of a serializer field, return a dictionary
        of metadata about it.
        """
        meta_data = super().get_field_info(field)
        meta_data['isPK'] = isinstance(field, PrimaryKeyRelatedField)
        meta_data['display'] = field.display if hasattr(
            field, "display") else True

        return meta_data
