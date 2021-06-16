import uuid

import factory
from factory.django import DjangoModelFactory

from core.tests import factories as core_factories
from willcraft_auth.tests import factories as auth_factories

from ..models import Firm, WitnessService


class FirmFactory(DjangoModelFactory):
    class Meta:
        model = Firm

    name = factory.LazyAttribute(lambda x: str(uuid.uuid4())[:4])
    email = factory.LazyAttribute(lambda x: f"{uuid.uuid4()}@test.com")
    tncs_file = factory.LazyAttribute(lambda x: f"{uuid.uuid4()}.pdf")


class WitnessServiceFactory(DjangoModelFactory):
    class Meta:
        model = WitnessService

    service_type = "WITNESS"
    # person_1 = factory.SubFactory(auth_factories.UserFactory)
    # person_2 = factory.SubFactory(auth_factories.UserFactory)

    firm = factory.SubFactory(FirmFactory)
    order = factory.SubFactory(core_factories.WillOrderFactory)
