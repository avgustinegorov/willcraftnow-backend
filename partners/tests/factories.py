import uuid

import factory
from factory.django import DjangoModelFactory

from ..models import Partners, ApplicationStore


class PartnersFactory(DjangoModelFactory):
    class Meta:
        model = Partners

    name = factory.LazyAttribute(lambda x: str(uuid.uuid4())[:4])


class ApplicationStoreFactory(DjangoModelFactory):
    class Meta:
        model = ApplicationStore
