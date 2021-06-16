import uuid

import factory
from factory.django import DjangoModelFactory

from core.tests import factories as core_factories
from willcraft_auth.tests import factories as auth_factories
from ..models import CustomerBilling, Discount, Invoice


class CustomerBillingFactory(DjangoModelFactory):
    class Meta:
        model = CustomerBilling

    user = factory.SubFactory(auth_factories.UserFactory)
    customer_token = factory.LazyAttribute(lambda x: str(uuid.uuid4())[:4])


class DiscountFactory(DjangoModelFactory):
    class Meta:
        model = Discount

    discount_code = factory.LazyAttribute(lambda x: str(uuid.uuid4())[:4])
    discount_target = "WILL_PRICE"
    discount_type = "FIXED_PRICE"
    discount_amount = "9.90"
    expiry_date = None


class InvoiceFactory(DjangoModelFactory):
    class Meta:
        model = Invoice

    order = factory.SubFactory(core_factories.WillOrderFactory)
