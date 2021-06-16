from unittest.mock import MagicMock, patch

from django.shortcuts import reverse
from django.test import Client, TestCase
from rest_framework import status as http_status

from ..models import *


class ContentTestCase(TestCase):
    """ Contains all of the tests for the content views """

    client = Client()

    def setUp(self):
        """Run at the initialization of all tests container
        in this case
        """
        # Creating model instances for testing
        self.faq = FAQ.objects.create(title="test_faq")
        # self.contact_us = ContactUs.objects.create(name="test_contact", email="test@g.com",
        #                                            subject="test_subject")

    def test_faq_get(self):
        """ Tests the get endpoint for a faq list """
        url = reverse("content:faq-list")

        r = self.client.get(url)

        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.json()), 1)
