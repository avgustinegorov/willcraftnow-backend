import uuid
from datetime import timedelta
from unittest.mock import MagicMock, patch

import stripe
from django.shortcuts import reverse
from django.test import Client, override_settings
from django.utils import timezone
from rest_framework import status as http_status

from core.models import *
from core.tests import factories as core_factories
from core.tests.test_core import CoreTestBase
from persons.tests import factories as person_factories
from persons.models import EntityType

from ..models import Invoice
from . import factories as billing_factories


@override_settings(DEFAULT_FILE_STORAGE="django.core.files.storage.FileSystemStorage")
class BillingTestCase(CoreTestBase):
    """Contains all of the test cases directly
    related to Invoices and Billing
    """

    client = Client()

    def setUp(self):
        """ Called at the initialization of every test """
        super().setUp()
        # setting up persontypes
        self.create_test_entity_types()
        # Creating an order for testing, which should also create an invoice
        # related to it
        self.order = core_factories.WillOrderFactory.create(
            order_type="WILL", user=self.user
        )

    def test_invoice_retrieve(self):
        """ Tests the detail endpoint for invoice retrieval """
        url = reverse(
            "billing:retrieve-update-latest-invoice", kwargs={"order_pk": self.order.id}
        )

        r = self.client.get(
            url, AUTHORIZATION=f"Bearer {self.user_access_token}")

        self.assertEqual(r.status_code, http_status.HTTP_200_OK, r.content)
        self.assertEqual(r.json()["order"], self.order.id)

    def test_discounted_invoice_retrieve(self):
        """
        Given there is a discounted invoice,
        when invoice info is requested,
        the discount info is also returned
        """
        discount = billing_factories.DiscountFactory.create()

        invoice = self.order.invoice.latest()
        invoice.discounts.clear()
        invoice.discounts.add(discount)
        invoice.update_invoice()
        invoice.save()

        url = reverse(
            "billing:retrieve-update-latest-invoice", kwargs={"order_pk": self.order.id}
        )

        r = self.client.get(
            url, AUTHORIZATION=f"Bearer {self.user_access_token}")

        self.assertEqual(r.status_code, http_status.HTTP_200_OK, r.content)
        content = r.json()
        self.assertEqual(content["order"], self.order.id)
        for discount_code in content["discounts"]:
            if discount_code == discount.discount_code:
                break
        else:
            self.fail("There is no matching discount.")

    def test_amended_invoice_retrieve(self):
        """
        Given there is an amended invoice,
        when the invoice info is requested,
        the amended status is also returned.
        """
        invoice = self.order.invoice.latest()
        invoice.been_paid = True
        invoice.date_paid = timezone.now()
        invoice.save()
        self.order.save()

        url = reverse(
            "billing:retrieve-update-latest-invoice", kwargs={"order_pk": self.order.id}
        )
        r = self.client.get(
            url, AUTHORIZATION=f"Bearer {self.user_access_token}")
        self.assertEqual(r.status_code, http_status.HTTP_200_OK, r.content)
        content = r.json()
        self.assertTrue(content["is_amended_invoice"])

    # NB: Should use the create discount view instead - test that!
    # def test_invoice_update(self):
    #     """ Tests the invoice update view for adding discounts """
    #     url = reverse("billing:retrieve-update-latest-invoice", kwargs={
    #         "order_pk": self.order.id
    #     })
    #
    #     discount = Discount.objects.create(
    #         discount_type="PERCENTAGE",
    #         discount_target="WILL_PRICE",
    #         discount_amount=40,
    #         discount_code="TEST_DISCOUNT"
    #     )
    #
    #     data = {
    #         "discounts": [discount.discount_code, ]
    #     }
    #
    #     r = self.client.patch(url, data=json.dumps(
    #         data), content_type="application/json")
    #
    #     self.assertEqual(r.status_code, self.success_code, r.content)
    #     self.assertEqual(len(r.json()["discounts"]), 1)

    def test_set_discount_to_invoice(self):
        order = self.create_test_order("WILL")
        url = reverse("billing:create-discount", kwargs={"order_pk": order.id})
        discount = billing_factories.DiscountFactory.create()
        data = {"discount_code": discount.discount_code}
        response = self.client.post(
            url, data=data, AUTHORIZATION=f"Bearer {self.user_access_token}"
        )
        self.assertEqual(response.status_code, http_status.HTTP_201_CREATED)

    def test_discount_code_not_active(self):
        order = self.create_test_order("WILL")
        url = reverse("billing:create-discount", kwargs={"order_pk": order.id})
        discount = billing_factories.DiscountFactory.create(is_active=False)
        data = {
            "discount_code": discount.discount_code,
        }
        response = self.client.post(
            url, data=data, AUTHORIZATION=f"Bearer {self.user_access_token}"
        )
        self.assertEqual(
            response.status_code, http_status.HTTP_400_BAD_REQUEST, response.content
        )

    def test_discount_code_invalid(self):
        order = self.create_test_order("WILL")
        url = reverse("billing:create-discount", kwargs={"order_pk": order.id})
        data = {
            "discount_code": str(uuid.uuid4())[:4],
        }
        response = self.client.post(
            url, data=data, AUTHORIZATION=f"Bearer {self.user_access_token}"
        )
        self.assertEqual(
            response.status_code, http_status.HTTP_400_BAD_REQUEST, response.content
        )

    def test_discount_code_expired(self):
        order = self.create_test_order("WILL")
        url = reverse("billing:create-discount", kwargs={"order_pk": order.id})
        discount = billing_factories.DiscountFactory.create(
            expiry_date=timezone.now() - timedelta(days=1)
        )
        data = {
            "discount_code": discount.discount_code,
        }
        response = self.client.post(
            url, data=data, AUTHORIZATION=f"Bearer {self.user_access_token}"
        )
        self.assertEqual(
            response.status_code, http_status.HTTP_400_BAD_REQUEST, response.content
        )

    def test_discount_code_redeemed(self):
        order = self.create_test_order("WILL")
        url = reverse("billing:create-discount", kwargs={"order_pk": order.id})
        discount = billing_factories.DiscountFactory.create(
            max_redeemed=3, redeemed=3)
        data = {
            "discount_code": discount.discount_code,
        }
        response = self.client.post(
            url, data=data, AUTHORIZATION=f"Bearer {self.user_access_token}"
        )
        self.assertEqual(
            response.status_code, http_status.HTTP_400_BAD_REQUEST, response.content
        )

    @patch("stripe.Charge.create")
    @patch("stripe.Customer.create")
    def test_charge_stripe(
        self,
        stripe_customer_create,
        stripe_charge_create,
    ):
        stripe_customer = MagicMock()
        stripe_customer.id = str(uuid.uuid4())[:4]
        stripe_customer_create.return_value = stripe_customer

        order = self.create_test_order("WILL")
        person_1 = person_factories.PersonFactory.create(order=order)
        person_1.entity_roles.add(EntityType.objects.get(type_name="WITNESS"))
        person_2 = person_factories.PersonFactory.create(order=order)
        person_2.entity_roles.add(EntityType.objects.get(type_name="WITNESS"))

        url = reverse("billing:stripe-one-off-charge",
                      kwargs={"order_pk": order.id})
        data = {"body": str(uuid.uuid4())[:4]}  # stripe token
        response = self.client.post(
            url, data=data, AUTHORIZATION=f"Bearer {self.user_access_token}"
        )
        self.assertEqual(response.status_code, http_status.HTTP_200_OK)

        stripe_charge_create.assert_called()

    @patch("stripe.Charge.create")
    @patch("stripe.Customer.create")
    def test_charge_stripe_failed(self, stripe_customer_create, stripe_charge_create):
        """
        Given the user making payment,
        when card error,
        payment will fail.
        """
        stripe_customer = MagicMock()
        stripe_customer.id = str(uuid.uuid4())[:4]
        stripe_customer_create.return_value = stripe_customer
        stripe_charge_create.side_effect = stripe.error.CardError({}, {}, 123)
        stripe_charge_create.side_effect.json_body = {}

        order = self.create_test_order("WILL")
        url = reverse("billing:stripe-one-off-charge",
                      kwargs={"order_pk": order.id})
        data = {"body": str(uuid.uuid4())[:4]}  # stripe token
        response = self.client.post(
            url, data=data, AUTHORIZATION=f"Bearer {self.user_access_token}"
        )
        self.assertEqual(response.status_code,
                         http_status.HTTP_400_BAD_REQUEST)

    def test_charge_full_discount(self):
        order = self.create_test_order("WILL")
        order = WillOrder.objects.get(id=order.id)
        invoice = order.invoice.latest()
        discount = billing_factories.DiscountFactory.create(
            discount_target="FULL_PRICE",
            discount_type="PERCENTAGE",
            discount_amount="100",
        )
        # invoice = billing_factories.InvoiceFactory.create(order_id=order.id)
        invoice.discounts.add(discount)

        url = reverse("billing:stripe-one-off-charge",
                      kwargs={"order_pk": order.id})
        data = {"body": str(uuid.uuid4())[:4]}  # stripe token
        response = self.client.post(
            url, data=data, AUTHORIZATION=f"Bearer {self.user_access_token}"
        )
        self.assertEqual(response.status_code, http_status.HTTP_200_OK)

    @patch("stripe.Charge.create")
    @patch("stripe.Customer.retrieve")
    def test_charge_stripe_existing_billing(
        self, stripe_customer_retrieve, stripe_charge_create
    ):
        billing = billing_factories.CustomerBillingFactory.create(
            user=self.user)
        stripe_customer = MagicMock()
        stripe_customer.id = billing.customer_token
        stripe_customer_retrieve.return_value = stripe_customer
        order = self.create_test_order("WILL")
        order = WillOrder.objects.get(id=order.id)
        person_1 = person_factories.PersonFactory.create(order=order)
        person_1.entity_roles.add(EntityType.objects.get(type_name="WITNESS"))
        person_2 = person_factories.PersonFactory.create(order=order)
        person_2.entity_roles.add(EntityType.objects.get(type_name="WITNESS"))

        url = reverse("billing:stripe-one-off-charge",
                      kwargs={"order_pk": order.id})
        data = {"body": str(uuid.uuid4())[:4]}  # stripe token
        response = self.client.post(
            url, data=data, AUTHORIZATION=f"Bearer {self.user_access_token}"
        )
        self.assertEqual(response.status_code, http_status.HTTP_200_OK)

        stripe_charge_create.assert_called()

    def test_charge_stripe_no_token(self):
        order = self.create_test_order("WILL")
        url = reverse("billing:stripe-one-off-charge",
                      kwargs={"order_pk": order.id})
        data = {}
        response = self.client.post(
            url, data=data, AUTHORIZATION=f"Bearer {self.user_access_token}"
        )
        self.assertEqual(response.status_code, http_status.HTTP_200_OK)
