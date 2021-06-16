from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _
from rest_framework.relations import PrimaryKeyRelatedField as DRFPrimaryKeyRelatedField
from rest_framework.serializers import EmailField as DRFEmailField, CharField as DRFCharField, BooleanField as DRFBooleanField


class PrimaryKeyRelatedField(DRFPrimaryKeyRelatedField):
    def __init__(self, *args, display=True, **kwargs):
        self.display = display
        super().__init__(*args, **kwargs)


class EmailField(DRFEmailField):
    def __init__(self, *args, display=True, **kwargs):
        self.display = display
        super().__init__(*args, **kwargs)


class CharField(DRFCharField):
    def __init__(self, *args, display=True, **kwargs):
        self.display = display
        super().__init__(*args, **kwargs)


class BooleanField(DRFBooleanField):
    def __init__(self, *args, display=True, **kwargs):
        self.display = display
        super().__init__(*args, **kwargs)
