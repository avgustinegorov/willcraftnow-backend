import json
import uuid

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils.http import urlencode
from oauth2_provider.models import get_application_model

from persons.models import EntityType

User = get_user_model()


class TestBase(TestCase):
    def __init__(self, *args, **kwargs):
        self.main_user = None
        self.client_id = None
        self.partner_client_id = None
        self.session = None
        self.access_tokens = {}
        super().__init__(*args, **kwargs)

    def setUp(self):
        self.main_user = self.get_or_create_main_user()
        self.client_id = self.get_or_create_client().client_id
        self.partner_client_id = self.get_or_create_partner_client().client_id
        self.session = Client()
        self.oAuthParams = {"client_id": self.client_id, "grant_type": "password"}
        super().setUp()

    def get_access_token(self, user, force_create=False):
        if not force_create:
            access_token = self.access_tokens.get(user.email)
            if access_token:
                return access_token

        password = uuid.uuid4()
        user.set_password(password)
        user.save()

        data, response = self.login_user({"email": user.email, "password": password,})
        access_token = data["access_token"]
        self.access_tokens[user.email] = access_token
        return access_token

    def get_or_create_client(self):
        client, _ = get_application_model().objects.get_or_create(
            user=self.main_user,
            client_type="public",
            authorization_grant_type="password",
            redirect_uris="https://127.0.0.1/success/",
            name="WillCraft",
        )
        return client

    def get_or_create_partner_client(self):
        client, _ = get_application_model().objects.get_or_create(
            user=self.main_user,
            client_type="public",
            redirect_uris="https://127.0.0.1/success/",
            authorization_grant_type="authorization-code",
            client_id="fbFprqyz5ct7bFbZSxOlALp5uZkSDi1tRlYMqusD",
            name="TestPartner",
        )

        return client

    def get_or_create_main_user(self):
        user, created = User.objects.get_or_create(email="willcraft@gmail.com")
        if created:
            user.set_password("willcraft123")
            user.save()
        return user

    def login_user(self, login_details, partner_client_id=None):
        login_details.update(self.oAuthParams)
        url = f"{reverse('willcraft_auth:rest_login')}"
        if partner_client_id:
            login_details['partner_client_id'] = partner_client_id
        response = self.session.post(url, data=login_details)
        data = response.json()
        return data, response

    def register_user(self, registration_details, partner_client_id=None):
        registration_details.update(self.oAuthParams)
        url = f"{reverse('willcraft_auth:register')}"
        if partner_client_id:
            registration_details['partner_client_id'] = partner_client_id
        response = self.session.post(
            url, data=registration_details
        )
        data = response.json()
        return data, response

    def token_login_user(self, login_details, partner_client_id=None):
        login_details.update(self.oAuthParams)
        url = f"{reverse('willcraft_auth:rest_token_login')}"
        if partner_client_id:
            login_details['partner_client_id'] = partner_client_id
        response = self.session.post(
            url, data=login_details
        )
        data = response.json()
        return data, response

    def token_register_user(self, registration_details, partner_client_id=None):
        registration_details.update(self.oAuthParams)
        url = f"{reverse('willcraft_auth:token_register')}"
        if partner_client_id:
            registration_details['partner_client_id'] = partner_client_id
        response = self.session.post(
            url, data=registration_details
        )
        data = response.json()
        return data, response

    def create_test_entity_types(self):
        """ Creates the person types required for testing """
        entity_types = [
            "EXECUTOR",
            "SUB_EXECUTOR",
            "GUARDIAN",
            "SUB_GUARDIAN",
            "WITNESS",
            "BENEFICIARY",
            "DONEE",
            "REPLACEMENT_DONEE",
        ]

        for entity_type in entity_types:
            EntityType.objects.get_or_create(type_name=entity_type)
