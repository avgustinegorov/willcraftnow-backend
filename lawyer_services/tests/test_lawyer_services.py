import json
from datetime import timedelta

from django.shortcuts import reverse
from django.test import Client
from django.utils import timezone
from rest_framework import status as http_status

from core.models import WillOrder
from core.tests.test_core import CoreTestBase
from persons.models import EntityType
from persons.tests import factories as person_factories
from . import factories as legal_services_factory


class LawyerServicesTestCase(CoreTestBase):
    """Contains all of the tests directly related to
    orders, people or arrangements
    """

    def setUp(self):
        """ Called at the initialization of every test """
        super().setUp()
        self.client = Client()

        self.create_test_entity_types()
        # A set of generic personal details used for a few of the tests
        self.personal_details = {
            "name": "TestUser",
            "age": 20,
            "id_number": 10001,
            "id_document": "NRIC",
            "address": "TestAddr",
            "religion": "Christianity",
        }

    def test_update_witness_legal_services_not_allowed(self):
        """ Sends a request to the Witness POST endpoint with the given data """
        # Creating an order for testing
        created_order = self.create_test_order("WILL")
        firm = self.create_law_firm()

        data = {"order": created_order.id, "firm": firm.id}

        url = reverse(
            "lawyer_services:retrieve-update-destroy-witness",
            kwargs={"order_pk": created_order.id, "service_type": "witness", },
        )

        r = self.client.put(
            url,
            data=json.dumps(data),
            content_type="application/json",
            AUTHORIZATION=f"Bearer {self.user_access_token}",
        )

        self.assertEqual(
            r.status_code, http_status.HTTP_400_BAD_REQUEST, r.content)

    def test_create_witness_service(self):
        created_order = self.create_test_order("WILL")
        firm = self.create_law_firm()
        person_1 = person_factories.PersonFactory.create(
            order_id=created_order.id)
        person_1.entity_roles.add(EntityType.objects.get(type_name="WITNESS"))
        person_2 = person_factories.PersonFactory.create(
            order_id=created_order.id)
        person_2.entity_roles.add(EntityType.objects.get(type_name="WITNESS"))

        url = reverse(
            "lawyer_services:retrieve-update-destroy-witness",
            kwargs={"order_pk": created_order.id, "service_type": "witness", },
        )
        data = {
            "firm": firm.id,
            "service_type": "witness",
            "review_type": "EN",
        }
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type="application/json",
            AUTHORIZATION=f"Bearer {self.user_access_token}",
        )
        self.assertEqual(response.status_code, http_status.HTTP_201_CREATED)

    def test_delete_witness_service(self):
        created_order = self.create_test_order("WILL")
        legal_services_factory.WitnessServiceFactory.create(
            order_id=created_order.id)

        url = reverse(
            "lawyer_services:retrieve-update-destroy-witness",
            kwargs={"order_pk": created_order.id, "service_type": "witness", },
        )
        response = self.client.delete(
            url, AUTHORIZATION=f"Bearer {self.user_access_token}"
        )
        self.assertEqual(response.status_code, http_status.HTTP_204_NO_CONTENT)

    def test_delete_witness_service_not_allowed(self):
        created_order = self.create_test_order("WILL")
        order = WillOrder.objects.get(pk=created_order.id)
        invoice = order.invoice.latest()
        invoice.date_paid = timezone.now() + timedelta(minutes=1)
        invoice.been_paid = True
        invoice.save()
        legal_services_factory.WitnessServiceFactory.create(
            order_id=created_order.id)

        url = reverse(
            "lawyer_services:retrieve-update-destroy-witness",
            kwargs={"order_pk": created_order.id, "service_type": "witness", },
        )
        response = self.client.delete(
            url, AUTHORIZATION=f"Bearer {self.user_access_token}"
        )
        self.assertEqual(response.status_code,
                         http_status.HTTP_400_BAD_REQUEST)

    def test_delete_witness_service_paid_but_allowed(self):
        created_order = self.create_test_order("WILL")
        order = WillOrder.objects.get(pk=created_order.id)
        invoice = order.invoice.latest()
        invoice.date_paid = timezone.now() - timedelta(minutes=5)
        invoice.been_paid = True
        invoice.save()
        legal_services_factory.WitnessServiceFactory.create(
            order_id=created_order.id)

        url = reverse(
            "lawyer_services:retrieve-update-destroy-witness",
            kwargs={"order_pk": created_order.id, "service_type": "witness", },
        )
        response = self.client.delete(
            url, AUTHORIZATION=f"Bearer {self.user_access_token}"
        )
        self.assertEqual(response.status_code, http_status.HTTP_204_NO_CONTENT)

    def test_order_cannot_be_assigned_to_multiple_witness_services(self):
        created_order = self.create_test_order("WILL")
        firm = self.create_law_firm()
        legal_services_factory.WitnessServiceFactory.create(
            order_id=created_order.id)

        url = reverse(
            "lawyer_services:retrieve-update-destroy-witness",
            kwargs={"order_pk": created_order.id, "service_type": "witness", },
        )
        data = {
            "firm": firm.id,
            "review_type": "EN",
            "service_type": "witness",
        }
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type="application/json",
            AUTHORIZATION=f"Bearer {self.user_access_token}",
        )
        self.assertEqual(response.status_code,
                         http_status.HTTP_400_BAD_REQUEST)

    def test_create_review_service(self):
        created_order = self.create_test_order("WILL")
        firm = self.create_law_firm()
        url = reverse(
            "lawyer_services:retrieve-update-destroy-witness",
            kwargs={"order_pk": created_order.id, "service_type": "review", },
        )
        data = {
            "firm": firm.id,
            "review_type": "EN",
            "service_type": "review"
        }
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type="application/json",
            AUTHORIZATION=f"Bearer {self.user_access_token}",
        )

        self.assertEqual(response.status_code, http_status.HTTP_201_CREATED)

    def test_create_certificate_provider(self):
        created_order = self.create_test_order("WILL")
        firm = self.create_law_firm()
        url = reverse(
            "lawyer_services:retrieve-update-destroy-witness",
            kwargs={
                "order_pk": created_order.id,
                "service_type": "certificate_provider",
            },
        )
        data = {
            "firm": firm.id,
            "review_type": "EN",
            "service_type": "certificate_provider",
        }
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type="application/json",
            AUTHORIZATION=f"Bearer {self.user_access_token}",
        )

        self.assertEqual(response.status_code, http_status.HTTP_201_CREATED)
