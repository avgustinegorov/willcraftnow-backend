from django.db.models import F, IntegerField, Subquery
from rest_framework import generics
from rest_framework.permissions import AllowAny

from .serializers import *


class FAQListView(generics.ListAPIView):
    """A Generic List API for the FAQ model

    endpoint: /faq/

    GET: Returns a list of all FAQ instances ordered by
            their last-update time
    """

    permission_classes = (AllowAny,)
    queryset = FAQ.objects.all().order_by("-last_updated_at")
    serializer_class = FAQSerializer


class TipsKeyWordsListView(generics.ListAPIView):
    """A Generic List API for the TipsKeyWords model

    endpoint: /TipsKeyWords/

    GET: Returns a list of all TipsKeyWords instances
    """

    permission_classes = (AllowAny,)
    queryset = TipsKeyWords.objects.all()
    serializer_class = TipsKeyWordsSerializer
