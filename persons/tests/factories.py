import random
import string

import factory
from factory.django import DjangoModelFactory

from core.tests import factories as core_factories

from ..models import EntityStore, DoneePowers, Person


class PersonalDetailsFactory(DjangoModelFactory):
    class Meta:
        model = Person

    name = factory.lazy_attribute(
        lambda x: "".join(
            random.choice(string.ascii_uppercase + string.digits) for _ in range(6)
        )
    )

    id_number = factory.LazyAttribute(
        lambda x: "S"
        + "".join(random.choice(string.digits) for _ in range(7))
        + random.choice(string.ascii_uppercase)
    )

    date_of_birth = (
        str(random.randint(1986, 1996))
        + "-"
        + str(random.randint(1, 12))
        + "-"
        + str(random.randint(1, 28))
    )
    real_estate_type = "HDB_FLAT"
    postal_code = str(random.randint(100000, 200000))
    floor_number = str(random.randint(1, 20))
    unit_number = str(random.randint(1, 200))
    block_number = factory.lazy_attribute(
        lambda x: "".join(
            random.choice(string.ascii_uppercase + string.digits) for _ in range(3)
        )
    )
    gender = "Male"
    street_name = factory.lazy_attribute(
        lambda x: "".join(
            random.choice(string.ascii_uppercase + string.digits) for _ in range(10)
        )
    )
    country = "SG"

    id_document = "NRIC"


class PersonFactory(DjangoModelFactory):
    class Meta:
        model = EntityStore

    order = factory.SubFactory(core_factories.WillOrderFactory)
    entity_details = factory.SubFactory(PersonalDetailsFactory)


class DoneePowersFactory(DjangoModelFactory):
    class Meta:
        model = DoneePowers

    donee = factory.SubFactory(PersonFactory)
    named_main_donee = None


class DoneePowersReplacementFactory(DjangoModelFactory):
    class Meta:
        model = DoneePowers

    donee = factory.SubFactory(PersonFactory)
    named_main_donee = factory.SubFactory(PersonFactory)
