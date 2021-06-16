import factory
from factory.django import DjangoModelFactory

from core.tests import factories as core_factories
from ..models import WillInstructions, WillLastRites


class WillInstructionsFactory(DjangoModelFactory):
    class Meta:
        model = WillInstructions

    order = factory.SubFactory(core_factories.WillOrderFactory)
    crematorium_location = "MANDAI_CREMATORIUM_AND_COLUMBARIUM_COMPLEX"


class WillLastRitesFactory(DjangoModelFactory):
    class Meta:
        model = WillLastRites

    order = factory.SubFactory(core_factories.WillOrderFactory)
    funeral_duration = 2
