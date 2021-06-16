from django.urls import reverse
from rest_framework import status as http_status

from core.tests.test_core import CoreTestBase
from willcraft_auth.tests import factories as auth_factories
from . import factories as partner_factories
from .factories import ApplicationStoreFactory


class PartnersTestCase(CoreTestBase):
    def setUp(self):
        super().setUp()

    def test_create_partner_discount(self):
        partner_user_1 = auth_factories.UserFactory.create()

        partner = partner_factories.PartnersFactory.create()
        application = self.get_or_create_partner_client()
        ApplicationStoreFactory.create(
            partner=partner,
            application=application,
        )
        partner.agents.add(partner_user_1)

        url = reverse("partners:get_discount")
        data = {
            "user": partner_user_1.id,
            "application": application.id
        }
        response = self.client.post(
            url, data=data, AUTHORIZATION=f"Bearer {self.user_access_token}"
        )
        self.assertEqual(response.status_code, http_status.HTTP_201_CREATED)

    def test_user_not_linked_to_partner(self):
        url = reverse("partners:get_discount")
        data = {}
        response = self.client.post(
            url, data=data, AUTHORIZATION=f"Bearer {self.user_access_token}"
        )
        self.assertEqual(response.status_code, http_status.HTTP_400_BAD_REQUEST)

    def test_user_linked_to_multiple_partners(self):
        partner_user = auth_factories.UserFactory.create()

        partners_1 = partner_factories.PartnersFactory.create()
        partners_1.agents.add(partner_user)
        partners_2 = partner_factories.PartnersFactory.create()
        partners_2.agents.add(partner_user)

        url = reverse("partners:get_discount")
        data = {
            "user": partner_user.id,
        }
        response = self.client.post(
            url, data=data, AUTHORIZATION=f"Bearer {self.user_access_token}"
        )
        self.assertEqual(response.status_code, http_status.HTTP_400_BAD_REQUEST)

    def test_partner_cannot_be_found(self):
        partner_user = auth_factories.UserFactory.create()
        url = reverse("partners:get_discount")
        data = {
            "user": partner_user.id,
        }
        response = self.client.post(
            url, data=data, AUTHORIZATION=f"Bearer {self.user_access_token}"
        )
        self.assertEqual(response.status_code, http_status.HTTP_400_BAD_REQUEST)

    def test_invalid_discount(self):
        """
        tries to set non unique discount code
        """
        url = reverse("partners:get_discount")
        data = {}
        response = self.client.post(
            url, data=data, AUTHORIZATION=f"Bearer {self.user_access_token}"
        )
        self.assertEqual(response.status_code, http_status.HTTP_400_BAD_REQUEST)
