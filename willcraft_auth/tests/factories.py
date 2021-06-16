from uuid import uuid4

import factory
from django.conf import settings
from django.utils import timezone
from factory.django import DjangoModelFactory


class UserFactory(DjangoModelFactory):
    class Meta:
        model = settings.AUTH_USER_MODEL

    email = factory.LazyAttribute(lambda x: f"{uuid4()}@example.com")
    is_active = True
    personal_details = factory.SubFactory(
        "persons.tests.factories.PersonalDetailsFactory"
    )
    last_login = factory.LazyAttribute(lambda x: timezone.now())
