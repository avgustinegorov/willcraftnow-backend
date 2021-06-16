from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from six import add_metaclass


@add_metaclass(serializers.SerializerMetaclass)
class AssetSerializerMixin(object):

    asset_type = serializers.CharField(read_only=True)
    display_name = serializers.CharField(read_only=True, source="__str__")

    def validate(self, data):
        user = self.context.get("user")
        data["user"] = user
        return data
