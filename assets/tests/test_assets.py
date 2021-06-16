import json
import uuid

from ddt import data, ddt
from django.shortcuts import reverse
from django.test import Client
from rest_framework import status as http_status

from core.tests.test_core import CoreTestBase
from persons.models import EntityStore, EntityType
from persons.tests import factories as person_factories

from . import factories as asset_factories


@ddt
class AssetTestCase(CoreTestBase):
    """Contains all of the test cases related to
    Assets and Allocations
    """

    client = Client()

    def setUp(self):
        """A method that sets up all dependencies
        run at the start of every test
        """
        super().setUp()
        # Creating a user to authenticate requests
        self.create_test_entity_types()

        self.order = self.create_test_order("WILL")

    def create_person(self):
        return person_factories.PersonalDetailsFactory.create(user=self.user)

    def create_entity_store(self, order):
        entity_details = self.create_person()
        entity_store = person_factories.PersonFactory.create(
            entity_details=entity_details, order=order
        )

        return entity_details, entity_store

    def create_test_allocation(self, order):
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

    def create_asset(self):
        asset = asset_factories.RealEstateFactory.create(
            user=self.user, postal_code="12221",
        )
        return asset

    def create_asset_store(self, order):
        asset = self.create_asset()
        asset_store = asset_factories.AssetStoreFactory.create(
            order=order, asset=asset)
        return asset, asset_store

    def test_asset_creation(self):
        """ Tests the POST method for creating assets """
        url = reverse(
            "assets:create-asset",
            kwargs={"order_pk": self.order.id, "asset_type": "RealEstate"},
        )
        data = {
            "postal_code": "12221",
            "real_estate_type": "TERRACE",
            "mortgage": "MORTGAGE",
            "holding_type": "JOINT_TENANT",
            "country": "SG",
        }

        r = self.client.post(
            url, data=data, AUTHORIZATION=f"Bearer {self.user_access_token}"
        )

        self.assertEqual(
            r.status_code, http_status.HTTP_201_CREATED, r.content)

    def test_asset_creation_non_sg(self):
        """ Tests the POST method for creating assets """
        url = reverse(
            "assets:create-asset",
            kwargs={"order_pk": self.order.id, "asset_type": "RealEstate"},
        )
        data = {
            "address": "RealEstate Address",
            "postal_code": "12221",
            "real_estate_type": "HDB_FLAT",
            "mortgage": "MORTGAGE",
            "holding_type": "JOINT_TENANT",
            "country": "ID",
        }

        r = self.client.post(
            url, data=data, AUTHORIZATION=f"Bearer {self.user_access_token}"
        )

        self.assertEqual(
            r.status_code, http_status.HTTP_400_BAD_REQUEST, r.content)

    def test_asset_update(self):
        """ Tests the PUT method for updating assets """
        # Creating an asset for testing
        created_asset = self.create_asset()

        url = reverse(
            "assets:retrieve-update-destroy-asset",
            kwargs={
                "order_pk": self.order.id,
                "asset_pk": created_asset.id,
                "asset_type": "RealEstate",
            },
        )
        data = {"postal_code": "NewPostCode"}

        r = self.client.patch(
            url,
            data=json.dumps(data),
            content_type="application/json",
            AUTHORIZATION=f"Bearer {self.user_access_token}",
        )

        self.assertEqual(r.status_code, http_status.HTTP_200_OK, r.content)
        # To confirm a new asset wasnt created
        self.assertEqual(r.json()["id"], created_asset.id)
        self.assertEqual(r.json()["postal_code"], data["postal_code"])

    def test_asset_get_list(self):
        """ Tests the LIST GET Api for assets """
        # Creating an asset for testing
        self.create_asset()

        url = reverse(
            "assets:create-asset",
            kwargs={"order_pk": self.order.id, "asset_type": "RealEstate"},
        )

        r = self.client.get(
            url, AUTHORIZATION=f"Bearer {self.user_access_token}")

        self.assertEqual(r.status_code, http_status.HTTP_200_OK, r.content)

    def test_asset_get(self):
        created_asset = self.create_asset()

        url = reverse(
            "assets:retrieve-update-destroy-asset",
            kwargs={
                "order_pk": self.order.id,
                "asset_pk": created_asset.id,
                "asset_type": "RealEstate",
            },
        )

        r = self.client.get(
            url, AUTHORIZATION=f"Bearer {self.user_access_token}",)

        self.assertEqual(r.status_code, http_status.HTTP_200_OK, r.content)
        self.assertEqual(r.json()["id"], created_asset.id, r.content)

    def test_allocation_create(self):
        """ Tests the POST method for allocation creation """

        asset = self.create_asset()
        entity = self.create_person()

        url = reverse(
            "assets:create-allocations",
            kwargs={"order_pk": self.order.id, "asset_pk": asset.id},
        )

        data = {
            "entity": entity.id,
            "allocation_percentage": 100.00,
            "asset_store": asset.id,
        }

        r = self.client.post(
            url, data=data, AUTHORIZATION=f"Bearer {self.user_access_token}"
        )

        self.assertEqual(
            r.status_code, http_status.HTTP_201_CREATED, r.content)
        self.assertEqual(r.json()["entity"], entity.id)

    def test_allocation_create_invalid_percentage(self):
        """ Tests the POST method for allocation creation """
        # Creating an asset for testing
        created_asset = self.create_asset()

        # Adding a appointment into the order to create the allocation
        entity_store = EntityStore(order=self.order)
        entity_store.save()

        url = reverse(
            "assets:create-allocations",
            kwargs={"order_pk": self.order.id, "asset_pk": created_asset.id},
        )
        data = {
            "entity": entity_store.id,
            "allocation_percentage": 0,
            "asset": created_asset.id,
        }

        r = self.client.post(
            url, data=data, AUTHORIZATION=f"Bearer {self.user_access_token}"
        )

        self.assertEqual(
            r.status_code, http_status.HTTP_400_BAD_REQUEST, r.content)

    def test_second_allocation_create(self):
        """ Creates a sibling-entity allocation """
        # Creates the allocation for testing
        (
            asset,
            asset_store,
            person,
            appointment_store,
            allocation,
        ) = self.create_test_allocation(self.order)

        url = reverse(
            "assets:create-allocations",
            kwargs={"order_pk": self.order.id, "asset_pk": asset.id, },
        )
        data = {
            "person": person.id,
            "allocation_percentage": 100.00,
        }

        r = self.client.post(
            url, data=data, AUTHORIZATION=f"Bearer {self.user_access_token}"
        )

        self.assertEqual(
            r.status_code, http_status.HTTP_400_BAD_REQUEST, r.content)

    def test_sub_allocation_create(self):
        """ Creates a sub-entity allocation """
        # Creates the allocation for testing
        (
            asset,
            asset_store,
            person,
            appointment_store,
            allocation,
        ) = self.create_test_allocation(self.order)

        # Adding a person into the order to create the allocation
        entity = self.create_person()

        url = reverse(
            "assets:create-allocations",
            kwargs={"order_pk": self.order.id, "asset_pk": asset.id, },
        )
        data = {
            "entity": entity.id,
            "allocation_percentage": 100.00,
            "parent_allocation": allocation.id,
            "asset_store": asset.id,
        }

        r = self.client.post(
            url, data=data, AUTHORIZATION=f"Bearer {self.user_access_token}"
        )

        self.assertEqual(
            r.status_code, http_status.HTTP_201_CREATED, r.content)
        self.assertEqual(r.json()["entity"], entity.id)

    def test_sub_allocation_duplicated_entity(self):
        """
        When trying to add a person as sub entity more than once,
        it will fail.
        """
        (
            asset,
            asset_store,
            person,
            appointment_store,
            allocation,
        ) = self.create_test_allocation(self.order)
        sub_person, sub_appointment_store, sub_allocation = self.create_sub_allocation(
            self.order, asset_store, allocation
        )

        url = reverse(
            "assets:create-allocations",
            kwargs={"order_pk": self.order.id, "asset_pk": asset.id, },
        )
        data = {
            "entity": sub_allocation.entity_id,
            "allocation_percentage": 100.00,
            "parent_allocation": sub_allocation.parent_allocation_id,
            "asset_store": asset.id,
        }

        r = self.client.post(
            url, data=data, AUTHORIZATION=f"Bearer {self.user_access_token}"
        )
        self.assertEqual(
            r.status_code, http_status.HTTP_400_BAD_REQUEST, r.content)

    def test_sub_allocation_percentage_overflow(self):
        """
        trying to add another sub entity,
        when total allocation is more than 100%,
        it will fail.
        """
        (
            asset,
            asset_store,
            person,
            appointment_store,
            allocation,
        ) = self.create_test_allocation(self.order)
        sub_person, sub_appointment_store, sub_allocation = self.create_sub_allocation(
            self.order, asset_store, allocation
        )
        substitute_2 = self.create_person()

        url = reverse(
            "assets:create-allocations",
            kwargs={"order_pk": self.order.id, "asset_pk": asset.id, },
        )
        data = {
            "entity": substitute_2.id,
            "allocation_percentage": 10.00,
            "parent_allocation": sub_allocation.parent_allocation_id,
            "asset_store": asset.id,
        }

        r = self.client.post(
            url, data=data, AUTHORIZATION=f"Bearer {self.user_access_token}"
        )
        self.assertEqual(
            r.status_code, http_status.HTTP_400_BAD_REQUEST, r.content)

    def test_sub_allocation_amount_overflow(self):
        """
        trying to add another sub entity,
        when total allocation is more than actual asset amount,
        it will fail.
        """
        (
            asset,
            asset_store,
            person,
            appointment_store,
            allocation,
        ) = self.create_test_allocation(self.order)
        sub_person, sub_appointment_store, sub_allocation = self.create_sub_allocation(
            self.order, asset_store, allocation
        )
        sub_allocation.parent_allocation.allocation_amount = 100
        sub_allocation.parent_allocation.save()
        sub_allocation.allocation_amount = 60
        sub_allocation.save()

        substitute_2 = self.create_person()

        url = reverse(
            "assets:create-allocations",
            kwargs={"order_pk": self.order.id, "asset_pk": asset.id, },
        )
        data = {
            "entity": substitute_2.id,
            "allocation_amount": 60,
            "parent_allocation": sub_allocation.parent_allocation_id,
            "asset_store": asset.id,
        }

        r = self.client.post(
            url, data=data, AUTHORIZATION=f"Bearer {self.user_access_token}"
        )
        self.assertEqual(
            r.status_code, http_status.HTTP_400_BAD_REQUEST, r.content)

    def test_sub_allocation_follows_parent_to_use_percentage(self):
        """
        given parent allocation uses percentage,
        when creating sub-allocation that uses amount,
        it will fail.
        """
        (
            asset,
            asset_store,
            person,
            appointment_store,
            allocation,
        ) = self.create_test_allocation(self.order)
        substitute = self.create_person()

        url = reverse(
            "assets:create-allocations",
            kwargs={"order_pk": self.order.id, "asset_pk": asset.id, },
        )
        data = {
            "entity": substitute.id,
            "allocation_amount": 0,
            "parent_allocation": allocation.id,
            "asset_store": asset.id,
        }

        r = self.client.post(
            url, data=data, AUTHORIZATION=f"Bearer {self.user_access_token}"
        )
        self.assertEqual(
            r.status_code, http_status.HTTP_400_BAD_REQUEST, r.content)

    def test_sub_allocation_follows_parent_to_use_amount(self):
        """
        given parent allocation uses amount,
        when creating sub-allocation that have 0 amount,
        it will fail.
        """
        (
            asset,
            asset_store,
            person,
            appointment_store,
            allocation,
        ) = self.create_test_allocation(self.order)
        allocation.allocation_percentage = None
        allocation.allocation_amount = 10000
        allocation.save()
        substitute = self.create_person()

        url = reverse(
            "assets:create-allocations",
            kwargs={"order_pk": self.order.id, "asset_pk": asset.id, },
        )
        data = {
            "entity": substitute.id,
            "allocation_amount": 0,
            "parent_allocation": allocation.id,
            "asset_store": asset.id,
        }

        r = self.client.post(
            url, data=data, AUTHORIZATION=f"Bearer {self.user_access_token}"
        )
        self.assertEqual(
            r.status_code, http_status.HTTP_400_BAD_REQUEST, r.content)

    def test_entity_and_its_substitute_must_be_different(self):
        """
        given adding sub entity,
        when sub entity is the same as the entity,
        it will fail.
        """
        (
            asset,
            asset_store,
            person,
            appointment_store,
            allocation,
        ) = self.create_test_allocation(self.order)

        url = reverse(
            "assets:create-allocations",
            kwargs={"order_pk": self.order.id, "asset_pk": asset.id, },
        )
        data = {
            "entity": person.id,
            "allocation_percentage": 100,
            "parent_allocation": allocation.id,
            "asset_store": asset.id,
        }

        r = self.client.post(
            url, data=data, AUTHORIZATION=f"Bearer {self.user_access_token}"
        )
        self.assertEqual(
            r.status_code, http_status.HTTP_400_BAD_REQUEST, r.content)

    def test_total_allocation_must_not_be_more_than_100_percent(self):
        """
        Given adding more entity,
        when total allocation becomes more than 100%,
        it will fail
        """
        (
            asset,
            asset_store,
            person,
            appointment_store,
            allocation_1,
        ) = self.create_test_allocation(self.order)
        allocation_1.allocation_percentage = 50
        allocation_1.save()

        entity_2 = self.create_person()

        url = reverse(
            "assets:create-allocations",
            kwargs={"order_pk": self.order.id, "asset_pk": asset.id, },
        )

        data = {
            "entity": entity_2.id,
            "allocation_percentage": 60,
            "asset_store": asset.id,
        }

        r = self.client.post(
            url, data=data, AUTHORIZATION=f"Bearer {self.user_access_token}"
        )
        self.assertEqual(
            r.status_code, http_status.HTTP_400_BAD_REQUEST, r.content)

    def test_can_only_be_entity_to_the_same_asset_once(self):
        """
        Given adding more entity,
        when the person is already a entity of the asset,
        it will fail
        """
        (
            asset,
            asset_store,
            person,
            appointment_store,
            allocation,
        ) = self.create_test_allocation(self.order)
        allocation.allocation_percentage = 50
        allocation.save()

        url = reverse(
            "assets:create-allocations",
            kwargs={"order_pk": self.order.id, "asset_pk": asset.id, },
        )

        data = {
            "entity": person.id,
            "allocation_percentage": 50,
            "asset_store": asset.id,
        }

        r = self.client.post(
            url, data=data, AUTHORIZATION=f"Bearer {self.user_access_token}"
        )

        self.assertEqual(
            r.status_code, http_status.HTTP_400_BAD_REQUEST, r.content)

    def test_only_bank_account_asset_can_allocate_amount(self):
        """
        Given allocating asset to a entity,
        when the asset is not a bank account,
        it will fail.
        """
        asset = self.create_asset()
        entity = self.create_person()

        url = reverse(
            "assets:create-allocations",
            kwargs={"order_pk": self.order.id, "asset_pk": asset.id, },
        )
        data = {
            "entity": entity.id,
            "allocation_amount": 100000,
            "asset_store": asset.id,
        }

        r = self.client.post(
            url, data=data, AUTHORIZATION=f"Bearer {self.user_access_token}"
        )
        self.assertEqual(
            r.status_code, http_status.HTTP_400_BAD_REQUEST, r.content)

    def test_cannot_allocate_asset_to_witness(self):
        """
        Given allocating asset to a entity,
        when the entity is the witness of the will,
        it will fail.
        """
        asset, asset_store = self.create_asset_store(self.order)
        entity, entity_store = self.create_entity_store(self.order)
        entity_store.entity_roles.add(
            EntityType.objects.get(type_name="WITNESS")
        )

        url = reverse(
            "assets:create-allocations",
            kwargs={"order_pk": self.order.id, "asset_pk": asset.id, },
        )
        data = {
            "entity": entity.id,
            "allocation_percentage": 100,
            "asset_store": asset.id,
        }

        r = self.client.post(
            url, data=data, AUTHORIZATION=f"Bearer {self.user_access_token}"
        )
        self.assertEqual(
            r.status_code, http_status.HTTP_400_BAD_REQUEST, r.content)

    def test_allocation_delete(self):
        """ Tests the delete endpoint for allocations """
        # Creates the allocation for testing
        (
            asset,
            asset_store,
            person,
            appointment_store,
            allocation,
        ) = self.create_test_allocation(self.order)

        # Testing for an allocation percentage about 150
        url = reverse(
            "assets:retrieve-update-destroy-allocation",
            kwargs={"order_pk": self.order.id,
                    "allocation_pk": allocation.id, },
        )

        r = self.client.delete(
            url, AUTHORIZATION=f"Bearer {self.user_access_token}")
        self.assertEqual(r.status_code, 204)

    def test_allocation_update(self):
        """Tests the PUT method for allocation update
        Tests for an error case if percentage > 100
        and for a successful input
        """
        # Creates the allocation for testing
        (
            asset,
            asset_store,
            person,
            appointment_store,
            allocation,
        ) = self.create_test_allocation(self.order)

        # Testing for an allocation percentage about 150
        url = reverse(
            "assets:retrieve-update-destroy-allocation",
            kwargs={"order_pk": self.order.id,
                    "allocation_pk": allocation.id, },
        )
        data = {"allocation_percentage": 150.00}
        r = self.client.patch(
            url,
            data=json.dumps(data),
            content_type="application/json",
            AUTHORIZATION=f"Bearer {self.user_access_token}",
        )
        self.assertEqual(
            r.status_code, http_status.HTTP_400_BAD_REQUEST, r.content)

        # Testing for a correct update below 100
        data = {"allocation_percentage": 100.00}
        r = self.client.patch(
            url,
            data=json.dumps(data),
            content_type="application/json",
            AUTHORIZATION=f"Bearer {self.user_access_token}",
        )
        self.assertEqual(r.status_code, http_status.HTTP_200_OK, r.content)

    def test_allocation_list(self):
        """ Tests the GET method for allocation list retrieval """
        # Creates the allocation for testing
        (
            asset,
            asset_store,
            person,
            appointment_store,
            allocation,
        ) = self.create_test_allocation(self.order)

        url = reverse(
            "assets:create-allocations",
            kwargs={"order_pk": self.order.id, "asset_pk": asset.id, },
        )
        r = self.client.get(
            url, AUTHORIZATION=f"Bearer {self.user_access_token}")

        self.assertEqual(r.status_code, http_status.HTTP_200_OK, r.content)

    @data(0, 30, 101)
    def test_company_ownership_cannot_be_0_or_more_than_100_percent(self, percentage):
        """
        Given creating a company asset,
        when the share percentage is set to more than 100%, or less than or equal to 0,
        it will fail.
        when the share is more than 0 and less than or equal to 100%,
        it will succeed.
        """
        url = reverse(
            "assets:create-asset",
            kwargs={"order_pk": self.order.id, "asset_type": "Company"},
        )
        data = {
            "name": str(uuid.uuid4())[:4],
            "registration_number": str(uuid.uuid4())[:4],
            "shares_amount": 500000,
            "percentage": percentage,
            "incorporated_in": "SG",
        }

        r = self.client.post(
            url, data=data, AUTHORIZATION=f"Bearer {self.user_access_token}"
        )
        if 0 < percentage <= 100:
            self.assertEqual(
                r.status_code, http_status.HTTP_201_CREATED, r.content)
        else:
            self.assertEqual(
                r.status_code, http_status.HTTP_400_BAD_REQUEST, r.content)

    @data("SG", "ID")
    def test_company_cannot_be_incorporated_in_countries_other_than_sg(self, country):
        """
        Given creating a company asset,
        when the company incorporated in Singapore,
        it will succeed.
        Otherwise, it will fail.
        """
        url = reverse(
            "assets:create-asset",
            kwargs={"order_pk": self.order.id, "asset_type": "Company"},
        )
        data = {
            "name": str(uuid.uuid4())[:4],
            "registration_number": str(uuid.uuid4())[:4],
            "shares_amount": 500000,
            "percentage": 30,
            "incorporated_in": country,
        }

        r = self.client.post(
            url, data=data, AUTHORIZATION=f"Bearer {self.user_access_token}"
        )
        if country == "SG":
            self.assertEqual(
                r.status_code, http_status.HTTP_201_CREATED, r.content)
        else:
            self.assertEqual(
                r.status_code, http_status.HTTP_400_BAD_REQUEST, r.content)

    def test_residual_asset_can_only_be_one_per_order(self):
        """
        Given creating a residual asset,
        when the order already has a residual asset,
        it will fail.
        """
        asset_factories.ResidualFactory.create(user=self.user,)

        url = reverse(
            "assets:create-asset",
            kwargs={"order_pk": self.order.id, "asset_type": "Residual"},
        )

        r = self.client.post(
            url, AUTHORIZATION=f"Bearer {self.user_access_token}")
        self.assertEqual(
            r.status_code, http_status.HTTP_400_BAD_REQUEST, r.content)

    def test_create_residual_asset(self):
        """
        Given creating a residual asset,
        when the order has no residual asset,
        it will succeed.
        """
        url = reverse(
            "assets:create-asset",
            kwargs={"order_pk": self.order.id, "asset_type": "Residual"},
        )

        r = self.client.post(
            url, AUTHORIZATION=f"Bearer {self.user_access_token}")
        self.assertEqual(
            r.status_code, http_status.HTTP_201_CREATED, r.content)
