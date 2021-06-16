from rest_framework import serializers

from .models import *


class FAQSerializer(serializers.ModelSerializer):
    """ A Generic model serializer for FAQ instances """

    class Meta:
        model = FAQ
        fields = "__all__"


class TipsKeyWordsSerializer(serializers.ModelSerializer):
    """A Minimal model serializer that is used for the Tips and Key Words
    endpoint
    """

    class Meta:
        model = TipsKeyWords
        fields = ["id", "title", "content", "step", "order_type", "tip_type"]
