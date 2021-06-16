import decimal
import difflib
import io
import os
import re
import uuid
from unittest.mock import MagicMock, patch

import PyPDF2
import requests
from ddt import data, ddt, unpack
from django.shortcuts import reverse
from django.test import Client, override_settings
from django.utils import timezone
from rest_framework import status as http_status

from billing.models import DefaultDiscount
from lastrites.models import *
from lastrites.tests import factories as lastrite_factories
from lawyer_services.tests import factories as lawyer_service_factories
from partners.models import ApplicationStore
from partners.tests.factories import PartnersFactory, ApplicationStoreFactory
from persons.tests import factories as person_factories
from persons.models import EntityType
from assets.models import Allocation
from billing.models import Invoice
from WillCraft.tests import TestBase
from willcraft_auth.tests import factories as auth_factories

from ..models import *
from . import factories as core_factories
from .will_templates import *

EXECUTION_PAGE_TO_FOLLOW_RE = re.compile(
    r"\(\s*Execution\s+Page\s+To\s+Follow\s*\)")
PAGE_GENERATED_AT_RE = re.compile(
    r"Page\s+\d+\s+Generated\s+At\s*:[^\r\n]+[\r\n]+Order\s*:\s*\S+[\r\n]+Last Will and"
    r" Testament of [^\r\n]+"
)


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)


class CoreTestBase(TestBase):
    """Contains all of the helper functions directly related to
    orders, people or arrangements. Does not include setUp function.
    """

    headers = {}

    def setUp(self):
        super().setUp()
        self.user = self.create_test_user()
        self.user_access_token = self.get_access_token(self.user)
        return self.user

    def create_application_store(self, partner, application):
        return ApplicationStoreFactory.create(
            partner=partner,
            application=application
        )

    def create_auto_disc_partner(self):
        partner = PartnersFactory.create()
        application = self.get_or_create_partner_client()
        self.create_application_store(
            partner, application
        )
        return partner

    def create_lpa_discount(self, application):
        return DefaultDiscount.objects.create(
            discount_category="PARTNER_DISCOUNT",
            discount_type="PERCENTAGE",
            discount_target="WILL_PRICE",
            discount_amount=9.90,
            application=application,
        )

    def authorize_client(self):
        """Authorizes the client - created to be able to replicate
        this test case
        """
        self.client.force_login(self.user)

    def create_person(self):
        return person_factories.PersonalDetailsFactory.create(user=self.user)

    def get_entity_type(self, type):
        return EntityType.objects.get(type_name=type)

    def create_entity_store(self, order, type=None):
        """ Creates a test person for witnesses """
        person = self.create_person()
        entity_store = person_factories.PersonFactory.create(
            order=order, entity_details=person
        )
        if type:
            type = self.get_entity_type(type)
            entity_store.entity_roles.add(type)
        return person, entity_store

    def create_allocation(self, order):
        asset, asset_store = self.create_asset_store(order)
        person, entity_store = self.create_entity_store(order)
        allocation = asset_factories.AllocationFactory.create(
            asset_store=asset_store,
            entity=entity_store,
            allocation_percentage=100.00,
        )
        return asset, asset_store, person, entity_store, allocation

    def create_sub_allocation(self, order, asset_store, allocation):
        person, entity_store = self.create_entity_store(order)
        sub_allocation = asset_factories.AllocationFactory.create(
            asset_store=asset_store,
            entity=entity_store,
            parent_allocation=allocation,
            allocation_percentage=100.00,
        )
        return person, entity_store, sub_allocation

    def create_asset(self, factory=None, details=None):
        if not details:
            details = {}
        if factory:
            return factory.create(user=self.user, **details)

        return asset_factories.RealEstateFactory.create(
            user=self.user, postal_code="12221",
        )

    def create_asset_store(self, order, factory=None, details=None):
        asset = self.create_asset(factory=factory, details=details)
        asset_store = asset_factories.AssetStoreFactory.create(
            order=order, asset=asset)
        return asset, asset_store

    def create_test_user(self):
        # Creating a user to authenticate requests
        user = auth_factories.UserFactory.create()
        return user

    def create_payment(self, order):
        # Paying an invoice for the order so that it can be tested
        invoice = order.invoice.latest()
        invoice.update_invoice()
        invoice.been_paid = True
        invoice.save()

    def create_pdf_details(self, order):
        """Creates all of the unrelated order testing details
        for pdf generation
        """

        # setting will constants
        appointment_type_list = {
            "EXECUTOR": 4,
            "SUB_EXECUTOR": 3,
            "GUARDIAN": 1,
            "SUB_GUARDIAN": 1,
            "WITNESS": 2,
        }

        person_list = []

        for key, value in appointment_type_list.items():
            for i in range(value):
                # Creating the test appointments
                person, entity_store = self.create_entity_store(
                    order, type=key
                )
                person_list.append(person)

        # Creating arrangements for the order
        last_rites = WillLastRites.objects.create(
            funeral_location="Anydaymwhere",
            funeral_duration=3,
            funeral_religion="CHRISTIAN",
            order=order,
        )

        instructions = WillInstructions.objects.create(
            instructions="CREMATED",
            crematorium_location="CHOA_CHU_KANG_COLUMBARIUM",
            order=order,
        )

        assetList = self.create_assert_list(order)

        for asset_store in assetList:
            test_percentage = random.randint(1, 90)
            allocation_percentages = [test_percentage, 90 - test_percentage]
            for i in range(3):
                # Creating the test executor
                parent_allocation, parent_allocation_store = self.create_entity_store(
                    order)
                parent_allocation_allocation = Allocation.objects.create(
                    entity=parent_allocation_store,
                    asset_store=asset_store,
                    allocation_percentage=allocation_percentages[i - 1],
                    effective_allocation_percentage=allocation_percentages[i - 1],
                )
                for j in range(3):
                    # Creating the test executor
                    sub_entity, sub_entity_store = self.create_entity_store(
                        order)
                    Allocation.objects.create(
                        parent_allocation=parent_allocation_allocation,
                        entity=sub_entity_store,
                        asset_store=asset_store,
                        allocation_percentage=allocation_percentages[j - 1],
                        effective_allocation_percentage=allocation_percentages[j - 1]
                        * allocation_percentages[j - 1],
                    )
        return

    def create_assert_list(self, order):
        assetList = []
        # Creating a real-estate for testing assets
        real_estate_1_store = self.create_real_estate(
            order,
            {"street_name": "Real Estate 1", "holding_type": "SOLE_OWNER"}
        )
        assetList.append(real_estate_1_store)
        # Creating a real-estate for testing assets
        real_estate_2_store = self.create_real_estate(
            order,
            {"street_name": "Real Estate 2", "holding_type": "JOINT_TENANT"}
        )
        assetList.append(real_estate_2_store)
        # Creating a real-estate for testing assets
        real_estate_3_store = self.create_real_estate(
            order,
            {"street_name": "Real Estate 3", "holding_type": "TENANT_IN_COMMON"}
        )
        assetList.append(real_estate_3_store)
        # Creating a real-estate for testing assets
        bank_account_1, bank_account_1_store = self.create_asset_store(
            order,
            factory=asset_factories.BankAccountFactory,
            details={
                "bank": "Bank Account 1",
                "account_number": "234123",
                "holding_type": "JOINTLY",
            },
        )
        assetList.append(bank_account_1_store)
        # Creating a real-estate for testing assets
        bank_account_2, bank_account_2_store = self.create_asset_store(
            order,
            factory=asset_factories.BankAccountFactory,
            details={
                "bank": "Bank Account 2",
                "account_number": "456234",
                "holding_type": "INDIVIDUALLY",
            },
        )
        assetList.append(bank_account_2_store)
        # Creating a real-estate for testing assets
        invest_account_1, invest_account_1_store = self.create_asset_store(
            order,
            factory=asset_factories.InvestmentFactory,
            details={
                "financial_institution": "Investment Account 1",
                "account_number": "456234",
                "holding_type": "JOINTLY",
            },
        )
        assetList.append(invest_account_1_store)
        # Creating a real-estate for testing assets
        invest_account_2, invest_account_2_store = self.create_asset_store(
            order,
            factory=asset_factories.InvestmentFactory,
            details={
                "financial_institution": "Investment Account 2",
                "account_number": "456234",
                "holding_type": "INDIVIDUALLY",
            },
        )
        assetList.append(invest_account_2_store)
        # Creating a real-estate for testing assets
        company_1, company_1_store = self.create_asset_store(
            order,
            factory=asset_factories.CompanyFactory,
            details={
                "name": "Company",
                "shares_amount": "1500",
                "percentage": "50",
                "registration_number": "123123",
                "incorporated_in": "SG",
            },
        )
        assetList.append(company_1_store)
        # Creating a real-estate for testing assets
        insurance_1, insurance_1_store = self.create_asset_store(
            order,
            factory=asset_factories.InsuranceFactory,
            details={
                "insurer": "Company",
                "plan": "Plan 1",
                "policy_number": "123123",
                "has_existing_nomination": "NO",
            },
        )
        assetList.append(insurance_1_store)
        # Creating a real-estate for testing assets
        residual, residual_store = self.create_asset_store(
            order, factory=asset_factories.ResidualFactory, details={}
        )
        assetList.append(residual_store)
        return assetList

    def create_real_estate(self, order, details={}):
        real_estate_details = {
            "postal_code": 123456,
            "floor_number": 23,
            "unit_number": 23,
            "block_number": "B123",
            "street_name": "Real Estate 1",
            "country": "SG",
            "real_estate_type": "HDB_FLAT",
            "mortgage": "NO_MORTGAGE",
            "holding_type": "SOLE_OWNER",
        }
        real_estate_details.update(details)
        real_estate, real_estate_store = self.create_asset_store(
            order,
            factory=asset_factories.RealEstateFactory,
            details=real_estate_details,
        )
        return real_estate_store

    def create_law_firm(self):
        """Tests the POST endpoint for creating a legal service with witness as a legal service"""
        # Creating a firm
        firm = lawyer_service_factories.FirmFactory.create()
        return firm

    def create_test_order(self, order_type):
        order = core_factories.WillOrderFactory.create(
            order_type=order_type, user=self.user
        )
        asset_factories.RealEstateFactory.create(order=order)
        return order


@ddt
@override_settings(
    DEFAULT_FILE_STORAGE="django.core.files.storage.FileSystemStorage",
    MEDIA_URL="/media/",
    MEDIA_ROOT=os.path.join(
        os.path.dirname(settings.BASE_DIR), "static_cdn", "media_root"
    ),
)
class CoreTestCase(CoreTestBase):
    """Contains all of the tests directly related to
    orders, people or arrangements
    """

    def setUp(self):
        """ Called at the initialization of every test """
        super().setUp()
        self.test_user_email = "testWill@gmail.com"
        self.test_user_password = "timeTotest12"
        self.client = Client()

        self.create_test_entity_types()
        # A set of generic personal details used for a few of the tests
        self.personal_details = {
            "name": "TestUser",
            "age": 20,
            "id_number": 10001,
            "id_document": "NRIC",
            "religion": "Christianity",
            "real_estate_type": "HDB_FLAT",
            "postal_code": 123456,
            "floor_number": 23,
            "unit_number": 23,
            "block_number": "B123",
            "street_name": "Crazy Street",
            "country": "SG",
        }

    @data("WILL", "LPA")
    def test_order_creation(self, order_type):
        self.order_creation(order_type)

    def register_partner_user(self):
        partner = self.create_auto_disc_partner()
        self.create_lpa_discount(
            partner.application_stores.first().application)

        # Register new user with the partner.
        data_, response = self.register_user(
            {
                "email": self.test_user_email,
                "password": self.test_user_password,
                "repeat_password": self.test_user_password,
                "client_id": self.client_id,
            },
            self.partner_client_id,
        )

        # Check if registration went well.
        self.assertEqual(response.status_code, http_status.HTTP_200_OK)
        self.assertTrue("access_token" in data_)

        # Assign the new access token.
        self.user_access_token = data_.get("access_token", "")

    @patch("stripe.Charge.create")
    @patch("stripe.Customer.create")
    def charge_stripe(self, stripe_customer_create, stripe_charge_create):
        stripe_customer = MagicMock()
        stripe_customer.id = str(uuid.uuid4())[:4]
        stripe_customer_create.return_value = stripe_customer

        url = reverse(
            "billing:stripe-one-off-charge", kwargs={"order_pk": self.order_id}
        )
        data_ = {"body": str(uuid.uuid4())[:4]}  # stripe token
        response = self.client.post(
            url, data=data_, AUTHORIZATION=f"Bearer {self.user_access_token}"
        )
        self.assertEqual(response.status_code, http_status.HTTP_200_OK)

        stripe_charge_create.assert_called()
        stripe_customer.reset_mock()

    def order_creation(self, order_type):
        """Creates a user/token (based on class) linked order with the given order type
        linked to the requesting user if provided
        """
        url = reverse("core:create-order", kwargs={"order_type": order_type})
        data_ = {
            "order_type": order_type  # Order type must be asserted in the serializer/view
        }

        r = self.client.post(
            url, data=data_, AUTHORIZATION=f"Bearer {self.user_access_token}"
        )

        self.assertEqual(
            r.status_code, http_status.HTTP_201_CREATED, r.content)
        # Save for feature using.
        self.order_id = r.json()["id"]
        self.assertTrue(r.json()["order_number"])

    def test_order_creation_with_auto_discount_partner(self):
        self.register_partner_user()
        # Create will order first.
        self.order_creation("WILL")
        # Make will order finished, payment.
        self.charge_stripe()
        # Make an LPA order.
        self.order_creation("LPA")
        # Check we already should have a partner discount.
        inv = Invoice.objects.last()
        # Check if invoice has applied.
        self.assertGreater(inv.gross_price, inv.net_price)

    def test_order_creation_with_auto_discount_partner_no_been(self):
        self.register_partner_user()
        # Create will order first.
        self.order_creation("WILL")
        # Create LPA order
        self.order_creation("LPA")
        # Check we already should have a partner discount.
        inv = Invoice.objects.last()
        # If no will paid no discount should be applied.
        self.assertEqual(inv.gross_price, inv.net_price)

    def test_order_creation_with_auto_discount_partner_no_will(self):
        # Add partner with auto discount.
        self.register_partner_user()
        # Create will order first.
        self.order_creation("LPA")
        # Make will order finished, payment.
        self.charge_stripe()
        # Check we already should have a partner discount.
        inv = Invoice.objects.last()
        # If no will paid no discount should be applied.
        self.assertEqual(inv.gross_price, inv.net_price)

    def test_order_creation_with_auto_discount_partner_try_second_time(self):
        # Add partner with auto discount.
        self.register_partner_user()
        # Create will order first time.
        self.order_creation("WILL")
        # Check that counter is in null.
        self.assertEqual(
            ApplicationStore.objects.all().last().discount_applied_times, 0
        )
        # Make will order finished.
        invoice = Invoice.objects.last()
        invoice.been_paid = True
        invoice.save()
        # Create LPA order.
        self.order_creation("LPA")
        # Check we already should have a partner discount.
        inv = Invoice.objects.last()
        # Discount should be applied the first time.
        self.assertGreater(inv.gross_price, inv.net_price)
        # Make a payment.
        self.charge_stripe()
        # The counter should increase.
        self.assertEqual(
            ApplicationStore.objects.all().last().discount_applied_times, 1
        )
        # Create another LPA order.
        self.order_creation("LPA")
        inv = Invoice.objects.last()
        # Discount shouldn't be applied this time.
        self.assertEqual(inv.gross_price, inv.net_price)

    # def test_order_will_upload(self):
    #     """ Tests the S3 Presigned URL get view for a
    #             Order and updating the same order with the uploaded
    #             file name
    #     """
    #     # Creating the base test order
    #     order = WillOrder.objects.create(
    #         user=self.user,
    #         order_type="WILL",
    #     )
    #
    #     url = reverse(
    #         "core:retrieve-update-order", kwargs={"order_pk": order.id})
    #
    #     data = {"filename": "TestOrder.pdf"}
    #
    #     self.authorize_client()
    #     r = self.client.post(url, data=data, headers=self.headers)
    #
    #     self.assertEqual(r.status_code, self.success_code, r.content)
    #     self.assertIn("presigned_url", r.json())
    #
    #     presigned_url = r.json()["presigned_url"]
    #     filename = r.json()["filename"]
    #
    #     with open(
    #             os.path.join(settings.TEST_FILES_DIR, "test_will.pdf"),
    #             'rb') as inf:
    #         file_obj = (None, inf, "application/pdf")
    #         formdata = {"file": file_obj}
    #         r = requests.put(presigned_url, files=formdata)
    #         self.assertTrue(r.status_code < 400, r.content)
    #
    #     # Updating the will with the uploaded filename
    #     data = {"pdf_will": filename}
    #     r = self.client.patch(
    #         url,
    #         data=json.dumps(data),
    #         content_type="application/json",
    #         headers=self.headers)
    #     self.assertEqual(r.status_code, self.success_code, r.content)
    #
    #     # Confirming that the file was set
    #     updated_order = WillOrder.objects.get(id=order.id)
    #     self.assertIn(filename, updated_order.pdf_will.name)

    # def test_order_pdf_generation(self):
    #     """ Tests the Will PDF Generation endpoint """
    #     self.user.personal_details = self.create_person()
    #     self.user.save()

    #     # Creating the base test order
    #     order = WillOrder.objects.create(user=self.user, order_type="WILL",)
    #     self.create_pdf_details(order)
    #     self.create_payment(order)

    #     # Sending the actual POST request
    #     url = reverse("core:generate-order-pdf", kwargs={"order_pk": order.id})
    #     self.authorize_client()
    #     r = self.client.get(
    #         url, AUTHORIZATION=f"Bearer {self.user_access_token}")

    #     self.assertEqual(r.status_code, http_status.HTTP_200_OK)
    #     self.assertIn(b"application/pdf", r.serialize_headers())

        # with open("TEST RESULT WILL.pdf", 'wb') as outf:
        #     outf.write(r.content)

    # def test_order_update(self):
    #     """ Tests updating the order with a logged in client """
    #     # Creating an order for testing
    #     created_order = self.test_order_creation()
    #
    #     # Creating a user, logging in client
    #     self.authorize_client()
    #
    #     # Sending the update request
    #     url = reverse(
    #         "core:retrieve-update-order",
    #         kwargs={"order_pk": created_order["id"]})
    #     data = created_order
    #     data["pdf_will"] = None
    #
    #     r = self.client.put(
    #         url,
    #         data=json.dumps(data),
    #         content_type="application/json",
    #         headers=self.headers)
    #
    #     self.assertEqual(r.status_code, self.success_code, r.content)
    #     self.assertEqual(r.json()["user"], self.user.pk, r.content)
    #
    #     return self.user, r.json()

    @data("WILL", "LPA")
    def test_order_retrieve(self, order_type):
        """ Tests the detail retrieval endpoint for orders """
        created_order = self.create_test_order(order_type)

        # Sending the GET request

        url = reverse("core:retrieve-order",
                      kwargs={"order_pk": created_order.id})
        r = self.client.get(
            url, AUTHORIZATION=f"Bearer {self.user_access_token}")

        self.assertEqual(r.status_code, http_status.HTTP_200_OK, r.content)
        self.assertEqual(r.json()["user"], created_order.user.id)

    @data("WILL", "LPA")
    def test_order_retrieve_list(self, order_type):
        """
        Test "order/list/" endpoint
        """
        self.create_test_order(order_type)

        # Sending the GET request
        url = reverse("core:retrieve-list-order")
        r = self.client.get(
            url, AUTHORIZATION=f"Bearer {self.user_access_token}")

        self.assertEqual(r.status_code, http_status.HTTP_200_OK, r.content)

    def get_wills_folder(self, type):
        wills_folder = os.path.join("core", "tests", "generated_wills", type)
        os.makedirs(wills_folder, exist_ok=True)
        return wills_folder

    def generate_pdf(self, order_id):
        url = reverse("lambda_service:generate-order-pdf",
                      kwargs={"order_pk": order_id})
        response = self.client.get(
            url, AUTHORIZATION=f"Bearer {self.user_access_token}", stream=True
        )
        self.assertEqual(
            response.status_code, http_status.HTTP_200_OK, response.content
        )
        return response.json()

    def extract_will_text_from_pdf(self, pdf_bytes):
        # if will_pdf_url[0:6] == "/media":
        #     will_pdf_url = settings.MEDIA_ROOT + will_pdf_url[6:]
        #     with open(will_pdf_url, "rb") as f:
        #         pdf_bytes = f.read()
        # else:
        #     response = requests.get(will_pdf_url)
        #     pdf_bytes = response.content

        f = io.BytesIO(pdf_bytes)
        pdf_reader = PyPDF2.PdfFileReader(f)
        if pdf_reader.isEncrypted:
            pdf_reader.decrypt(self.user.personal_details.id_number)
        num_pages = pdf_reader.numPages
        texts = []
        for i in range(num_pages):
            page = pdf_reader.getPage(i)
            texts.append(page.extractText())
        text = "".join(texts)
        text = EXECUTION_PAGE_TO_FOLLOW_RE.sub("", text)
        text = PAGE_GENERATED_AT_RE.sub("", text)

        # Write extracted text to a file, so we can check it manually when needed.
        wills_folder = self.get_wills_folder("text")
        with open(os.path.join(wills_folder, f"{self.id()}.txt"), "wt") as f_will_text:
            f_will_text.write(text)

        output_pdf = PyPDF2.PdfFileWriter()
        for p in range(pdf_reader.getNumPages()):
            output_pdf.addPage(pdf_reader.getPage(p))
        wills_folder = self.get_wills_folder("pdf")
        with open(os.path.join(wills_folder, f"{self.id()}.pdf"), "wb") as f_will_text:
            output_pdf.write(f_will_text)

        return text

    def get_will_template_text(self, will_template, params):
        template_text = str(will_template.format(**params))
        wills_folder = self.get_wills_folder("template_text")
        with open(os.path.join(wills_folder, f"{self.id()}.txt"), "wt") as f_will_text:
            f_will_text.write(template_text)
        return template_text

    def generate_will_template_context(
        self,
        order,
        witness_1,
        witness_2,
        guardians,
        executors,
        sub_executors,
        allocations,
        sub_allocations,
        residual_allocations,
        residual_sub_allocations,
        ref_allocations,
        total_allocation_amount,
        total_allocation_percentage,
        num_beneficiaries,
        AssetFactory,
    ):
        now = timezone.now()

        params = dict(
            year=now.year,
            order_id=order.order_number,
            testator_name=self.user.personal_details.name,
            testator_id_document=self.user.personal_details.id_document,
            testator_id_number=self.user.personal_details.id_number,
            testator_address=self.user.personal_details.address,
            testator_3rd_person="his",
            witness_1_name=witness_1.entity_details.name,
            witness_1_nric=witness_1.entity_details.id_number,
            witness_1_address=witness_1.entity_details.address,
            witness_2_name=witness_2.entity_details.name,
            witness_2_nric=witness_2.entity_details.id_number,
            witness_2_address=witness_2.entity_details.address,
        )

        num_guardians = len(guardians)
        if num_guardians == 1:
            params.update(
                dict(
                    guardian_name=guardians[0].entity_details.name,
                    guardian_nric=guardians[0].entity_details.id_number,
                    guardian_address=guardians[0].entity_details.address,
                )
            )

        num_executors = len(executors)
        for i in range(num_executors):
            params.update(
                {
                    f"executor_{i+1}_name": executors[i].entity_details.name,
                    f"executor_{i+1}_nric": executors[i].entity_details.id_number,
                    f"executor_{i+1}_address": executors[i].entity_details.address,
                }
            )

        num_sub_executors = len(sub_executors)
        if num_sub_executors == 1:
            params.update(
                dict(
                    sub_executor_name=sub_executors[0].entity_details.name,
                    sub_executor_nric=sub_executors[0].entity_details.id_number,
                    sub_executor_address=sub_executors[0].entity_details.address,
                )
            )

        params.update(
            AssetFactory.get_params(allocations)
        )

        params.update(
            dict(
                allocation_percentage=(total_allocation_percentage or 100)
                / num_beneficiaries,
                allocation_amount=(
                    total_allocation_amount or 0) / num_beneficiaries,
            )
        )

        len_allocations = len(ref_allocations)
        if len_allocations:
            for i in range(num_beneficiaries):
                allocation = ref_allocations[i]
                params.update(
                    {
                        f"entity_{i+1}_name": allocation.entity.entity_details.name,
                        f"entity_{i+1}_nric": allocation.entity.entity_details.id_number,
                        f"entity_{i+1}_address": allocation.entity.entity_details.address,
                    }
                )

                len_sub_allocations = len(sub_allocations[allocation.id])
                if len_sub_allocations:
                    sub_allocation_percentage = (
                        total_allocation_percentage or 100
                    ) / len_sub_allocations

                    params.update(
                        dict(
                            sub_allocation_percentage=sub_allocation_percentage,
                            sub_allocation_amount=(
                                total_allocation_amount or 0) / len_sub_allocations / len_allocations,
                        )
                    )

                    for j, sub_allocation in enumerate(sub_allocations[allocation.id]):
                        params.update(
                            {
                                f"sub_entity_{i+1}_{j+1}_name": sub_allocations[
                                    allocation.id
                                ][j].entity.entity_details.name,
                                f"sub_entity_{i+1}_{j+1}_nric": sub_allocations[
                                    allocation.id
                                ][j].entity.entity_details.id_number,
                                f"sub_entity_{i+1}_{j+1}_address": sub_allocations[
                                    allocation.id
                                ][j].entity.entity_details.address,
                                f"sub_entity_{i+1}_{j+1}_ea_pct": (
                                    sub_allocations[allocation.id][
                                        j
                                    ].effective_allocation_percentage
                                    or residual_sub_allocations[
                                        residual_allocations[i].id
                                    ][j].effective_allocation_percentage
                                ),
                                f"sub_entity_{i+1}_{j+1}_ea_amount": sub_allocations[
                                    allocation.id
                                ][
                                    j
                                ].effective_allocation_amount,
                            }
                        )

        # save params
        wills_folder = self.get_wills_folder("json")
        with open(os.path.join(wills_folder, f"{self.id()}.json"), "w") as fp:
            json.dump(params, fp, cls=DecimalEncoder)

        return params

    @data(*get_will_pdf_test_input_permutations())
    @unpack
    def test_generate_will(
        self,
        order_type=None,
        relationship_status=None,
        num_beneficiaries=None,
        num_sub_beneficiaries=None,
        total_allocation_percentage=None,
        total_allocation_amount=None,
        num_executors=None,
        num_sub_executors=None,
        num_guardians=None,
        instructions=None,
        has_lastrites=None,
        AssetFactory=None,
    ):
        """
        Given a PDF is generated using a set of input parameters,
        compare the text in the PDF with the expected text.
        The text extracted from the PDF is stored in folder core/tests/generated_wills
        """

        print()
        print(f"**" * 50)
        # print(f"***{self.id()}***")

        order = self.create_test_order(order_type)
        if self.user.personal_details.relationship_status != relationship_status:
            self.user.personal_details.relationship_status = relationship_status
            self.user.personal_details.save()

        executors = []
        for _i in range(num_executors):
            executor, executor_store = self.create_entity_store(
                order, type="EXECUTOR"
            )
            executors.append(executor_store)

        sub_executors = []
        for _i in range(num_sub_executors):
            sub_executor, sub_executor_store = self.create_entity_store(
                order, type="SUB_EXECUTOR"
            )
            sub_executors.append(sub_executor_store)

        guardians = []
        for _i in range(num_guardians):
            guardian, guardian_store = self.create_entity_store(
                order, type="GUARDIAN"
            )
            guardians.append(guardian_store)

        witness_1, witness_1_store = self.create_entity_store(
            order, type="WITNESS"
        )
        witness_2, witness_2_store = self.create_entity_store(
            order, type="WITNESS"
        )

        if instructions:
            lastrite_factories.WillInstructionsFactory.create(
                order=order, instructions=instructions
            )

        if has_lastrites:
            lastrite_factories.WillLastRitesFactory.create(order=order)

        allocations = []
        pct_allocations = []
        amount_allocations = []
        sub_allocations = {}
        if AssetFactory:
            asset, asset_store = self.create_asset_store(
                order, factory=AssetFactory)
            for _i in range(num_beneficiaries):
                entity, entity_store = self.create_entity_store(
                    order)
                sub_beneficiaries_store = []
                for _j in range(num_sub_beneficiaries):
                    (
                        sub_entity,
                        sub_entity_store,
                    ) = self.create_entity_store(order)
                    sub_beneficiaries_store.append(sub_entity_store)

                if total_allocation_amount:
                    params = dict(
                        asset_store=asset_store,
                        entity=entity_store,
                        allocation_amount=total_allocation_amount / num_beneficiaries,
                    )
                    allocation = asset_factories.AllocationFactory.create(
                        **params)
                    allocations.append(allocation)
                    amount_allocations.append(allocation)
                    sub_allocations[allocation.id] = []

                    for _j in range(num_sub_beneficiaries):
                        params = dict(
                            asset_store=asset_store,
                            parent_allocation=allocation,
                            entity=sub_beneficiaries_store[_j],
                            allocation_amount=total_allocation_amount
                            / num_sub_beneficiaries
                            / num_beneficiaries,
                        )
                        sub_allocation = asset_factories.AllocationFactory.create(
                            **params
                        )
                        sub_allocations[allocation.id].append(sub_allocation)

                if total_allocation_percentage:
                    params = dict(
                        asset_store=asset_store,
                        entity=entity_store,
                        allocation_percentage=total_allocation_percentage
                        / num_beneficiaries,
                    )
                    allocation = asset_factories.AllocationFactory.create(
                        **params)
                    allocations.append(allocation)
                    pct_allocations.append(allocation)
                    sub_allocations[allocation.id] = []

                    for _j in range(num_sub_beneficiaries):
                        params = dict(
                            asset_store=asset_store,
                            parent_allocation=allocation,
                            entity=sub_beneficiaries_store[_j],
                            allocation_percentage=total_allocation_percentage
                            / num_sub_beneficiaries,
                        )
                        sub_allocation = asset_factories.AllocationFactory.create(
                            **params
                        )
                        sub_allocations[allocation.id].append(sub_allocation)

        ref_allocations = amount_allocations or pct_allocations
        residual_allocations = []
        residual_sub_allocations = {}
        asset, asset_store = self.create_asset_store(
            order, factory=asset_factories.ResidualFactory
        )
        for _i in range(num_beneficiaries):
            params = dict(
                asset_store=asset_store,
                entity=ref_allocations[_i].entity,
                allocation_percentage=(total_allocation_percentage or 100)
                / num_beneficiaries,
            )
            allocation = asset_factories.AllocationFactory.create(**params)
            residual_allocations.append(allocation)
            residual_sub_allocations[allocation.id] = []

            for _j in range(num_sub_beneficiaries):
                params = dict(
                    asset_store=asset_store,
                    parent_allocation=allocation,
                    entity=sub_allocations[ref_allocations[_i].id][_j].entity,
                    allocation_percentage=(total_allocation_percentage or 100)
                    / num_sub_beneficiaries,
                )
                sub_allocation = asset_factories.AllocationFactory.create(
                    **params)
                residual_sub_allocations[allocation.id].append(sub_allocation)

        core_factories.WillRepoFactory.create(order=order)

        invoice = order.invoice.latest()
        invoice.been_paid = True
        invoice.save()

        # Generate PDF
        # response_obj = self.generate_pdf(order.id)
        url = reverse("lambda_service:generate-order-pdf",
                      kwargs={"order_pk": order.id})
        response = self.client.get(
            url, AUTHORIZATION=f"Bearer {self.user_access_token}"
        )

        # Extract texts from the generated PDF
        text = self.extract_will_text_from_pdf(response.content)

        # Check PDF texts

        will_template = get_will_template(
            relationship_status,
            total_allocation_percentage,
            total_allocation_amount,
            num_executors,
            num_sub_executors,
            num_guardians,
            instructions,
            has_lastrites,
            AssetFactory,
            allocations,
            sub_allocations,
            residual_allocations,
            residual_sub_allocations,
        )

        params = self.generate_will_template_context(
            order,
            witness_1_store,
            witness_2_store,
            guardians,
            executors,
            sub_executors,
            allocations,
            sub_allocations,
            residual_allocations,
            residual_sub_allocations,
            ref_allocations,
            total_allocation_amount,
            total_allocation_percentage,
            num_beneficiaries,
            AssetFactory,
        )

        formatted_template = self.get_will_template_text(will_template, params)

        self.compare_word_for_word(
            re.sub(r"[ ]{2,}", " ", text.strip().replace(
                "\n", " ").replace("\r", " ")),
            re.sub(
                r"[ ]{2,}",
                " ",
                formatted_template.strip().replace("\n", " ").replace("\r", " "),
            ),
        )

        self.assertEqual(
            re.sub(r"[ ]{2,}", " ", text.strip().replace(
                "\n", " ").replace("\r", " ")),
            re.sub(
                r"[ ]{2,}",
                " ",
                formatted_template.strip().replace("\n", " ").replace("\r", " "),
            ),
        )

        print(f"**" * 50)
        print()

    def compare_word_for_word(self, pdf, text):
        deleteStart = 0
        deleteWords = ""
        deleteEnd = 0
        addStart = 0
        addWords = ""
        addEnd = 0
        for i, s in enumerate(difflib.ndiff(pdf, text)):
            if deleteWords and deleteEnd + 1 != i:
                self.print_compare_result(
                    pdf,
                    text,
                    addStart,
                    addEnd,
                    deleteStart,
                    deleteEnd,
                    deleteWords,
                    addWords,
                )
                deleteStart = 0
                deleteWords = ""
            if addWords and addEnd + 1 != i:
                self.print_compare_result(
                    pdf,
                    text,
                    addStart,
                    addEnd,
                    deleteStart,
                    deleteEnd,
                    deleteWords,
                    addWords,
                )
                addStart = 0
                addWords = ""

            if s[0] == " ":
                continue
            elif s[0] == "-":
                if deleteStart == 0:
                    deleteStart = i
                    deleteEnd = i
                deleteEnd = i
                deleteWords += s[-1]
            elif s[0] == "+":
                if addStart == 0:
                    addStart = i
                    addEnd = i
                addEnd = i
                addWords += s[-1]

    def print_compare_result(
        self, pdf, text, addStart, addEnd, deleteStart, deleteEnd, deleteWords, addWords
    ):
        if addStart != addEnd or deleteStart != deleteEnd:
            if addWords and addStart != addEnd:
                print(f"--" * 50)
                print(f"Add To PDF : {addWords}")
                print(f"--" * 50)
                print(f"FROM PDF")
                print(pdf[addStart - 100: addEnd + 100])
                print(f"FROM TEXT")
                print(text[addStart - 100: addEnd + 100])
            if deleteWords and deleteStart != deleteEnd:
                print(f"--" * 50)
                print(f"Delete From Pdf : {deleteWords}")
                print(f"--" * 50)
                print(f"FROM PDF")
                print(pdf[deleteStart - 100: deleteEnd + 100])
                print(f"FROM TEXT")
                print(text[deleteStart - 100: deleteEnd + 100])

    def test_generate_will_cross_entity(self):
        """
        Given there are 3 persons, A, B, and C, and
        there is a testator who has a bank account to be allocated to two beneficiaries, A and B.
        If A dies, the account allocation will be substituted by B and C.
        If B dies, the account allocation will be substituted by A and C.
        """

        print()
        print(f"**" * 50)
        print(f"***{self.id()}***")

        order = self.create_test_order("WILL")

        bank_account, bank_account_store = self.create_asset_store(
            order, factory=asset_factories.BankAccountFactory
        )
        residual_asset, residual_asset_store = self.create_asset_store(
            order, factory=asset_factories.ResidualFactory
        )

        witness_1, witness_1_store = self.create_entity_store(
            order, type="WITNESS"
        )
        witness_2, witness_2_store = self.create_entity_store(
            order, type="WITNESS"
        )

        core_factories.WillRepoFactory.create(order=order)

        executor, executor_store = self.create_entity_store(
            order, type="EXECUTOR")

        entity_a, entity_a_store = self.create_entity_store(
            order)
        entity_b, entity_b_store = self.create_entity_store(
            order)
        entity_c, entity_c_store = self.create_entity_store(
            order)

        self.allocations = []
        self.pct_allocations = []
        self.amount_allocations = []
        self.sub_allocations = {}
        self.residual_allocations = []
        self.residual_sub_allocations = {}

        self.total_allocation_amount = 1000
        self.total_allocation_percentage = 100

        # Create bank account amount allocations
        self.create_bank_account_amount_allocations(
            bank_account_store, entity_a_store,
            entity_b_store, entity_c_store
        )

        # Create bank account interest allocations
        self.create_bank_account_interest_allocations(
            bank_account_store, entity_a_store,
            entity_b_store, entity_c_store
        )

        # Create residual allocations
        self.create_residual_allocations(
            entity_a_store, entity_b_store,
            entity_c_store, residual_asset_store
        )

        # Generate PDF
        # response_obj = self.generate_pdf(order.id)
        url = reverse("lambda_service:generate-order-pdf",
                      kwargs={"order_pk": order.id})
        response = self.client.get(
            url, AUTHORIZATION=f"Bearer {self.user_access_token}"
        )

        # Extract texts from the generated PDF
        text = self.extract_will_text_from_pdf(response.content)

        # Check PDF texts

        will_template = get_will_template(
            "Married",
            100,
            1000,
            1,
            0,
            0,
            None,
            False,
            asset_factories.BankAccountFactory,
            self.allocations,
            self.sub_allocations,
            self.residual_allocations,
            self.residual_sub_allocations,
        )

        params = self.generate_will_template_context(
            order,
            witness_1_store,
            witness_2_store,
            [],
            [executor_store],
            [],
            self.allocations,
            self.sub_allocations,
            self.residual_allocations,
            self.residual_sub_allocations,
            self.amount_allocations or self.pct_allocations,
            1000,
            100,
            2,
            asset_factories.BankAccountFactory,
        )

        formatted_template = self.get_will_template_text(will_template, params)

        self.compare_word_for_word(
            re.sub(r"[ ]{2,}", " ", text.strip().replace(
                "\n", " ").replace("\r", " ")),
            re.sub(
                r"[ ]{2,}",
                " ",
                formatted_template.strip().replace("\n", " ").replace("\r", " "),
            ),
        )

        self.assertEqual(
            re.sub(r"[ ]{2,}", " ", text.strip().replace(
                "\n", " ").replace("\r", " ")),
            re.sub(
                r"[ ]{2,}",
                " ",
                formatted_template.strip().replace("\n", " ").replace("\r", " "),
            ),
        )

        print(f"**" * 50)
        print()

    def create_residual_allocations(self, entity_a_store, entity_b_store, entity_c_store,
                                    residual_asset_store):
        residual_allocation_a = asset_factories.AllocationFactory.create(
            asset_store=residual_asset_store,
            entity=entity_a_store,
            allocation_percentage=self.total_allocation_percentage / 2,
        )
        self.residual_allocations.append(residual_allocation_a)
        self.residual_sub_allocations[residual_allocation_a.id] = []
        residual_allocation_b = asset_factories.AllocationFactory.create(
            asset_store=residual_asset_store,
            entity=entity_b_store,
            allocation_percentage=self.total_allocation_percentage / 2,
        )
        self.residual_allocations.append(residual_allocation_b)
        self.residual_sub_allocations[residual_allocation_b.id] = []
        residual_allocation_a_b = asset_factories.AllocationFactory.create(
            asset_store=residual_asset_store,
            parent_allocation=residual_allocation_a,
            entity=entity_b_store,
            allocation_percentage=self.total_allocation_percentage / 2,
        )
        self.residual_sub_allocations[residual_allocation_a.id].append(
            residual_allocation_a_b
        )
        residual_allocation_a_c = asset_factories.AllocationFactory.create(
            asset_store=residual_asset_store,
            parent_allocation=residual_allocation_a,
            entity=entity_c_store,
            allocation_percentage=self.total_allocation_percentage / 2,
        )
        self.residual_sub_allocations[residual_allocation_a.id].append(
            residual_allocation_a_c
        )
        residual_allocation_b_a = asset_factories.AllocationFactory.create(
            asset_store=residual_asset_store,
            parent_allocation=residual_allocation_b,
            entity=entity_a_store,
            allocation_percentage=self.total_allocation_percentage / 2,
        )
        self.residual_sub_allocations[residual_allocation_b.id].append(
            residual_allocation_b_a
        )
        residual_allocation_b_c = asset_factories.AllocationFactory.create(
            asset_store=residual_asset_store,
            parent_allocation=residual_allocation_b,
            entity=entity_c_store,
            allocation_percentage=self.total_allocation_percentage / 2,
        )
        self.residual_sub_allocations[residual_allocation_b.id].append(
            residual_allocation_b_c
        )

    def create_bank_account_interest_allocations(self, bank_account_store, entity_a_store, entity_b_store,
                                                 entity_c_store):
        pct_allocation_a = asset_factories.AllocationFactory.create(
            asset_store=bank_account_store,
            entity=entity_a_store,
            allocation_percentage=self.total_allocation_percentage / 2,
        )
        self.allocations.append(pct_allocation_a)
        self.pct_allocations.append(pct_allocation_a)
        self.sub_allocations[pct_allocation_a.id] = []
        pct_allocation_b = asset_factories.AllocationFactory.create(
            asset_store=bank_account_store,
            entity=entity_b_store,
            allocation_percentage=self.total_allocation_percentage / 2,
        )
        self.allocations.append(pct_allocation_b)
        self.pct_allocations.append(pct_allocation_b)
        self.sub_allocations[pct_allocation_b.id] = []
        pct_allocation_a_b = asset_factories.AllocationFactory.create(
            asset_store=bank_account_store,
            parent_allocation=pct_allocation_a,
            entity=entity_b_store,
            allocation_percentage=self.total_allocation_percentage / 2,
        )
        self.sub_allocations[pct_allocation_a.id].append(pct_allocation_a_b)
        pct_allocation_a_c = asset_factories.AllocationFactory.create(
            asset_store=bank_account_store,
            parent_allocation=pct_allocation_a,
            entity=entity_c_store,
            allocation_percentage=self.total_allocation_percentage / 2,
        )
        self.sub_allocations[pct_allocation_a.id].append(pct_allocation_a_c)
        pct_allocation_b_a = asset_factories.AllocationFactory.create(
            asset_store=bank_account_store,
            parent_allocation=pct_allocation_b,
            entity=entity_a_store,
            allocation_percentage=self.total_allocation_percentage / 2,
        )
        self.sub_allocations[pct_allocation_b.id].append(pct_allocation_b_a)
        pct_allocation_b_c = asset_factories.AllocationFactory.create(
            asset_store=bank_account_store,
            parent_allocation=pct_allocation_b,
            entity=entity_c_store,
            allocation_percentage=self.total_allocation_percentage / 2,
        )
        self.sub_allocations[pct_allocation_b.id].append(pct_allocation_b_c)

    def create_bank_account_amount_allocations(self, bank_account_store, entity_a_store, entity_b_store,
                                               entity_c_store):
        amount_allocation_a = asset_factories.AllocationFactory.create(
            asset_store=bank_account_store,
            entity=entity_a_store,
            allocation_amount=self.total_allocation_amount / 2,
        )
        self.allocations.append(amount_allocation_a)
        self.amount_allocations.append(amount_allocation_a)
        self.sub_allocations[amount_allocation_a.id] = []
        amount_allocation_b = asset_factories.AllocationFactory.create(
            asset_store=bank_account_store,
            entity=entity_b_store,
            allocation_amount=self.total_allocation_amount / 2,
        )
        self.allocations.append(amount_allocation_b)
        self.amount_allocations.append(amount_allocation_b)
        self.sub_allocations[amount_allocation_b.id] = []
        amount_allocation_a_b = asset_factories.AllocationFactory.create(
            asset_store=bank_account_store,
            parent_allocation=amount_allocation_a,
            entity=entity_b_store,
            allocation_amount=self.total_allocation_amount / 2 / 2,
        )
        self.sub_allocations[amount_allocation_a.id].append(
            amount_allocation_a_b)
        amount_allocation_a_c = asset_factories.AllocationFactory.create(
            asset_store=bank_account_store,
            parent_allocation=amount_allocation_a,
            entity=entity_c_store,
            allocation_amount=self.total_allocation_amount / 2 / 2,
        )
        self.sub_allocations[amount_allocation_a.id].append(
            amount_allocation_a_c)
        amount_allocation_b_a = asset_factories.AllocationFactory.create(
            asset_store=bank_account_store,
            parent_allocation=amount_allocation_b,
            entity=entity_a_store,
            allocation_amount=self.total_allocation_amount / 2 / 2,
        )
        self.sub_allocations[amount_allocation_b.id].append(
            amount_allocation_b_a)
        amount_allocation_b_c = asset_factories.AllocationFactory.create(
            asset_store=bank_account_store,
            parent_allocation=amount_allocation_b,
            entity=entity_c_store,
            allocation_amount=self.total_allocation_amount / 2 / 2,
        )
        self.sub_allocations[amount_allocation_b.id].append(
            amount_allocation_b_c)

    @data("WILL")
    def test_generate_will_witnessed_by_firm(self, order_type):
        order = self.create_test_order(order_type)
        core_factories.WillRepoFactory.create(order=order)
        lawyer_service_factories.WitnessServiceFactory.create(order=order)

        url = reverse("lambda_service:generate-order-pdf",
                      kwargs={"order_pk": order.id})

        response = self.client.get(
            url, AUTHORIZATION=f"Bearer {self.user_access_token}"
        )
        self.assertEqual(
            response.status_code, http_status.HTTP_200_OK, response.content
        )


# class CoreTokenTestCase(CoreUserTestCase):
#     """ Tests all of the core endpoints but uses
#             Token for authentication instead of users
#     """
#
#     def setUp(self):
#         """ Run before all tests initialization
#                 Creates the token before the regular setup
#         """
#         self.token = EmailToken(email="test@gg.com")
#         self.token.save()
#
#         self.headers = {"X-Token": self.token.token}
#
#         super().setUp()
#
#     def authorize_client(self):
#         """ Overriding authorize method to NOT
#                 authorize client with the user
#         """
#         pass
#
#     def test_order_pdf_generation(self):
#         """ Tests the Will PDF Generation endpoint
#                 Overridden to use the token and expect a 400 Response
#         """
#         self.user.personal_details = self.create_test_personal_details()
#         self.user.save()
#
#         # Creating the base test order
#         order = WillOrder.objects.create(
#             token=self.token,
#             order_type="WILL",
#         )
#         self.create_pdf_details(order)
#         self.create_payment(order)
#
#         # Sending the actual POST request
#         url = reverse("core:generate-order-pdf", kwargs={"order_pk": order.id})
#         self.authorize_client()
#         r = self.client.get(url, headers=self.headers)
#
#         self.assertEqual(r.status_code, 400, r.content)
#         self.assertIn(b"have a linked user!", r.content)

# def test_order_will_upload(self):
#     """ Tests the S3 Presigned URL get view for a
#             Order and updating the same order with the uploaded
#             file name
#             Overridden to get an error since the order doesn't have a user
#     """
#     # Creating the base test order
#     order = WillOrder.objects.create(
#         token=self.token,
#         order_type="WILL",
#     )
#
#     url = reverse(
#         "core:retrieve-update-order", kwargs={"order_pk": order.id})
#
#     data = {"filename": "TestOrder.pdf"}
#
#     self.authorize_client()
#     r = self.client.post(url, data=data, headers=self.headers)
#
#     self.assertEqual(r.status_code, 403, r.content)
#     self.assertEqual(
#         r.json(), {"user": "This field must not be null to upload a will"})
