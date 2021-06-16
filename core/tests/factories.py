import uuid

import factory
from factory.django import DjangoModelFactory

from willcraft_auth.tests import factories as auth_factories
from ..models import WillOrder, WillRepo


class WillOrderFactory(DjangoModelFactory):
    class Meta:
        model = WillOrder

    user = factory.SubFactory(auth_factories.UserFactory)
    order_type = "WILL"

    order_number = factory.LazyAttribute(lambda x: str(uuid.uuid4())[:4])
    tncs = False
    disclaimer = False


class WillRepoFactory(DjangoModelFactory):
    class Meta:
        model = WillRepo

    order = factory.SubFactory(WillOrderFactory)
