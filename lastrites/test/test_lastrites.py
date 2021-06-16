import json

from core.tests.test_core import CoreTestBase
from django.shortcuts import reverse
from rest_framework import status as http_status

from . import factories as lastrites_factories


class LastRitesTestCase(CoreTestBase):
    """Contains all of the tests directly related to
    orders, people or arrangements
    """

    def setUp(self):
        super().setUp()

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

    def create_test_arrangement_lastrites(self):
        created_order = self.create_test_order("WILL")
        lastrites = lastrites_factories.WillLastRitesFactory.create(
            order=created_order,
            funeral_location="",
            funeral_duration=0,
            funeral_religion="HINDU",
        )
        return lastrites

    def test_create_arrangement_lastrites(self):
        """ Tests the POST endpoint for creating lastrites """
        # Creating an order for testing
        created_order = self.create_test_order("WILL")

        url = reverse(
            "lastrites:arrangements-lastrites", kwargs={"order_pk": created_order.id}
        )

        data = {
            "funeral_location": "",
            "funeral_duration": 0,
            "funeral_religion": "HINDU",
            "order": created_order.id,
        }

        # r = self.client.patch(url, data=data, headers=self.headers)

        r = self.client.patch(
            url,
            data=json.dumps(data),
            content_type="application/json",
            AUTHORIZATION=f"Bearer {self.user_access_token}",
        )

        self.assertEqual(r.status_code, http_status.HTTP_200_OK, r.content)

    def create_test_arrangement_instructions(self):
        created_order = self.create_test_order("WILL")
        instructions = lastrites_factories.WillInstructionsFactory.create(
            order=created_order, instructions="BURIED", crematorium_location="",
        )
        return instructions

    def test_create_arrangement_instructions(self):
        """ Tests the POST endpoint for creating instructions """
        # Creating an order for testing
        created_order = self.create_test_order("WILL")

        url = reverse(
            "lastrites:arrangements-instructions", kwargs={"order_pk": created_order.id}
        )

        data = {
            "instructions": "BURIED",
            "crematorium_location": "",
            "order": created_order.id,
        }

        # r = self.client.patch(url, data=data, headers=self.headers)

        r = self.client.patch(
            url,
            data=json.dumps(data),
            content_type="application/json",
            AUTHORIZATION=f"Bearer {self.user_access_token}",
        )

        self.assertEqual(r.status_code, http_status.HTTP_200_OK, r.content)

    def test_get_arrangement_before_creation(self):
        """ Tests the GET endpoint for arrangements before creating and arrangement """
        # Creating an order for testing
        created_order = self.create_test_order("WILL")

        url = reverse(
            "lastrites:arrangements-lastrites", kwargs={"order_pk": created_order.id}
        )
        r = self.client.get(url, AUTHORIZATION=f"Bearer {self.user_access_token}")

        self.assertEqual(r.status_code, http_status.HTTP_200_OK)
        self.assertEqual(r.json()["order"], None)

        url = reverse(
            "lastrites:arrangements-instructions", kwargs={"order_pk": created_order.id}
        )
        r = self.client.get(url, AUTHORIZATION=f"Bearer {self.user_access_token}")

        self.assertEqual(r.status_code, http_status.HTTP_200_OK)
        self.assertEqual(r.json()["order"], None)

    def test_get_arrangement_after_creation(self):
        """ Tests the GET endpoint for arrangements after creating an arrangement """
        # Creating an order for testing
        created_arrangement = self.create_test_arrangement_lastrites()

        url = reverse(
            "lastrites:arrangements-lastrites",
            kwargs={"order_pk": created_arrangement.order_id},
        )
        r = self.client.get(url, AUTHORIZATION=f"Bearer {self.user_access_token}")

        self.assertEqual(r.status_code, http_status.HTTP_200_OK)

        created_arrangement = self.create_test_arrangement_instructions()

        url = reverse(
            "lastrites:arrangements-instructions",
            kwargs={"order_pk": created_arrangement.order_id},
        )
        r = self.client.get(url, AUTHORIZATION=f"Bearer {self.user_access_token}")

        self.assertEqual(r.status_code, http_status.HTTP_200_OK)
