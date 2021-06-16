import uuid

from django.contrib.auth import get_user_model
from django.shortcuts import reverse
from django.utils.http import urlencode
from rest_framework import status as http_status

from persons.tests import factories as person_factories

# from core.tests import CoreUserTestCase
from WillCraft.tests import TestBase

# from core.tests import CoreTestCase
from . import factories as auth_factories

User = get_user_model()


class AuthTestCase(TestBase):
    """
    Contains all of the tests related to user authentication
    """

    def setUp(self):
        """
        Initial test setup run before every test in the suite
        """

        self.test_user_email = "testWillcraft@gmail.com"
        self.test_user_password = "timeTotest1234"
        super().setUp()

    def test_get_client_id(self):
        response = self.session.get(reverse("willcraft_auth:get-client-id"))
        data = response.json()
        self.assertEqual(response.status_code, http_status.HTTP_200_OK)
        self.assertTrue("client_id" in data)
        self.assertEqual(self.client_id, data["client_id"])

    def test_register_user(self):
        """
        Create user test
        """
        data, response = self.register_user(
            {
                "email": self.test_user_email,
                "password": self.test_user_password,
                "repeat_password": self.test_user_password,
            }
        )

        self.assertEqual(response.status_code, http_status.HTTP_200_OK)
        self.assertTrue("access_token" in data)

    def test_login_user(self):
        user = auth_factories.UserFactory.create()
        password = str(uuid.uuid4())[:4]
        user.set_password(password)
        user.save()

        data, response = self.login_user({"email": user.email, "password": password,})

        self.assertContains(response, "access_token", 1, http_status.HTTP_200_OK)

    def test_login_user_wrong_data(self):
        """
        Login user with wrong cred.
        """

        data, response = self.login_user(
            {
                "email": self.test_user_email + "1",
                "password": self.test_user_password + "1",
            }
        )
        self.assertEqual(response.status_code, 400)

    def test_token_register(self):
        """
        Register email via token registrations
        """

        data, response = self.token_register_user(
            {"email": self.test_user_email, "client_id": self.client_id}
        )

        self.assertEqual(response.status_code, http_status.HTTP_200_OK)
        self.assertTrue("access_token" in data)
        self.assertTrue("refresh_token" in data)

    def test_token_login(self):
        """
        First Register and then try to
        Login with token register cred.
        """

        data, _ = self.token_register_user(
            {"email": self.test_user_email, "client_id": self.client_id,}
        )

        data, response = self.token_login_user(
            {
                "email": self.test_user_email,
                "password": self.test_user_password,
                "repeat_password": self.test_user_password,
                "client_id": self.client_id,
                "token": data["access_token"]
            }
        )

        self.assertEqual(response.status_code, http_status.HTTP_200_OK)
        self.assertTrue("access_token" in data)
        self.assertTrue("refresh_token" in data)

    def test_token_login_with_normal_registered_user(self):
        """
        First Register and then try to
        Login with token register cred.
        """

        data, response = self.register_user(
            {
                "email": self.test_user_email,
                "password": self.test_user_password,
                "repeat_password": self.test_user_password,
            }
        )

        payload = {
            "email": self.test_user_email,
            "password": self.test_user_password,
            "repeat_password": self.test_user_password,
            "client_id": self.client_id,
        }
        data, response = self.token_login_user(payload)
        self.assertEqual(response.status_code, 400)

    def test_wrong_token_login(self):
        """
        Login with token register with wrong data.
        """

        data, response = self.token_register_user(
            {"email": self.test_user_email, "client_id": self.client_id,}
        )

        payload = {
            "email": self.test_user_email + "1",
            "password": self.test_user_password,
            "client_id": self.client_id,
        }
        data, response = self.token_login_user(payload)
        self.assertEqual(response.status_code, 400)

    # def test_authorize(self):
    #     data = {
    #         'allow': True,
    #         'email': 'testWillcraft@gmail.com',
    #         'client_id': self.client_id,
    #         'response_type': 'code'
    #     }
    #     url = f"{reverse('willcraft_auth:authorize')}"
    #     print(">>>>>>>>>>>>>>>>", url)
    #     response = self.session.post(url, data)
    #     data = response.json()
    #     print(">>>>>>>>>>>>>>>>",url,data)
    #     print(data, response.status_code)
    #     self.assertEqual(response.status_code, 200)

    def test_logout(self):
        url = reverse("willcraft_auth:rest_logout")
        response = self.session.post(url)
        data = response.json()
        self.assertEqual(response.status_code, http_status.HTTP_200_OK)

    def test_introspect(self):
        """
        Get token detail
        """

        data, response = self.register_user(
            {
                "email": self.test_user_email,
                "password": self.test_user_password,
                "repeat_password": self.test_user_password,
            }
        )

        url = f"{reverse('willcraft_auth:introspect')}?token={data['access_token']}"
        response = self.session.get(url)
        data = response.json()
        self.assertEqual(response.status_code, http_status.HTTP_200_OK)

    def test_get_client_id_2(self):
        """
        get Client id
        """
        from oauth2_provider.models import get_application_model

        url = f"{reverse('willcraft_auth:get-client-id')}"
        response = self.session.get(url)
        data = response.json()
        self.assertEqual(response.status_code, http_status.HTTP_200_OK)
        self.assertTrue("client_id" in data)

    def test_client_whois(self):
        """
        check the client id detal
        """

        url = f"{reverse('willcraft_auth:client_whois')}?client_id={self.client_id}"
        response = self.session.get(url)
        data = response.json()
        self.assertEqual(response.status_code, http_status.HTTP_200_OK)
        self.assertTrue("client_name" in data)

    def test_is_user_with_existing_email(self):
        """
        Check is email exit with exiting email
        """

        data, response = self.register_user(
            {
                "email": self.test_user_email,
                "password": self.test_user_password,
                "repeat_password": self.test_user_password,
            }
        )

        payload = {
            "email": self.test_user_email,
        }

        url = f"{reverse('willcraft_auth:is-user')}"
        response = self.session.post(url, payload)
        data = response.json()
        self.assertEqual(response.status_code, http_status.HTTP_200_OK)
        self.assertTrue("status" in data)
        self.assertTrue(data["status"] == "Registered")

    def test_is_user_with_new_email(self):
        """
        check is email existing with new email
        """

        payload = {
            "email": "TestNewEmail@gmail.com",
        }

        url = f"{reverse('willcraft_auth:is-user')}"
        response = self.session.post(url, payload)
        data = response.json()
        self.assertEqual(response.status_code, http_status.HTTP_200_OK)
        self.assertTrue("status" in data)
        self.assertTrue(data["status"] == "Not Registered")
