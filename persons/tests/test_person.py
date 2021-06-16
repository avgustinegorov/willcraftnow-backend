import json
from datetime import datetime

from ddt import data, ddt, unpack
from django.shortcuts import reverse
from django.test import Client
from rest_framework import status as http_status

from core.tests.test_core import CoreTestBase
from persons.models import EntityStore, DoneePowers, EntityType
from persons.tests import factories as person_factories


@ddt
class PersonsTestCase(CoreTestBase):
    """Contains all of the tests directly related to
    orders, people or arrangements
    """

    def setUp(self):
        """ Called at the initialization of every test """
        super().setUp()
        self.client = Client()

        self.user = self.create_test_user()
        self.create_test_entity_types()
        # A set of generic personal details used for a few of the tests
        self.personal_details = {
            "name": "TestUser",
            "age": 20,
            "id_number": 10001,
            "id_document": "NRIC",
            "address": "TestAddr",
            "religion": "Christianity",
            "country_of_issue": "SG",
            "country": "SG",
        }

    def create_test_person(self):
        personal_details = person_factories.PersonalDetailsFactory.create(
            user=self.user
        )
        return personal_details

    def create_test_appointment_store(self, order, type=None):
        entity_details = self.create_test_person()
        entity_store = person_factories.PersonFactory.create(
            entity_details=entity_details, order=order
        )
        if type:
            entity_store.entity_roles.add(
                EntityType.objects.get(type_name=type)
            )
        return entity_details, entity_store

    def test_create_blank_person(self):
        """ Tests the creation of people for a given order """
        # Creating an order for testing
        order = self.create_test_order("WILL")

        url = reverse("persons:list-create-people",
                      kwargs={"order_pk": order.id, })
        data = {**self.personal_details, 'entity_type': "Person"}

        r = self.client.post(
            url,
            data=json.dumps(data),
            content_type="application/json",
            AUTHORIZATION=f"Bearer {self.user_access_token}",
        )

        self.assertEqual(
            r.status_code, http_status.HTTP_201_CREATED, r.content)

    def test_invalid_personal_details(self):
        """
        Given person name is a required personal details field.
        When name is not specified, it will fail creating person info.
        """
        order = self.create_test_order("WILL")

        url = reverse("persons:list-create-people",
                      kwargs={"order_pk": order.id, })
        del self.personal_details["name"]
        data = {
            "personal_details": self.personal_details,
        }

        r = self.client.post(
            url,
            data=json.dumps(data),
            content_type="application/json",
            AUTHORIZATION=f"Bearer {self.user_access_token}",
        )

        self.assertEqual(
            r.status_code, http_status.HTTP_400_BAD_REQUEST, r.content)

    def test_create_executor(self):
        """ Tests the creation of people for a given order """
        # Creating an order for testing
        order = self.create_test_order("WILL")
        person = self.create_test_person()

        url = reverse("persons:update-appointment",
                      kwargs={"order_pk": order.id, })
        data = {
            "person": person.id,
            "updated_type": "EXECUTOR",
        }

        r = self.client.post(
            url,
            data=json.dumps(data),
            content_type="application/json",
            AUTHORIZATION=f"Bearer {self.user_access_token}",
        )

        self.assertEqual(r.status_code, http_status.HTTP_200_OK, r.content)

    def test_list_people(self):
        """ Tests the GET endpoint for people list """
        # Creating a person for testing
        order = self.create_test_order("WILL")

        (
            created_personal_details,
            created_appointment_store,
        ) = self.create_test_appointment_store(order)

        url = (
            reverse("persons:list-create-people",
                    kwargs={"order_pk": order.id, })
            + "?appointment_type=EXECUTOR"
        )
        r = self.client.get(
            url, AUTHORIZATION=f"Bearer {self.user_access_token}")

        self.assertEqual(r.status_code, http_status.HTTP_200_OK, r.content)

    def test_update_person(self):
        """ Tests the PUT endpoint for updating people """
        # Creating a person for testing
        order = self.create_test_order("WILL")

        (
            created_personal_details,
            created_appointment_store,
        ) = self.create_test_appointment_store(order)

        url = reverse(
            "persons:update-people",
            kwargs={"order_pk": order.id,
                    "person_pk": created_personal_details.id, },
        )

        # Updating the personal details
        data = self.personal_details

        r = self.client.patch(
            url,
            data=json.dumps(data),
            content_type="application/json",
            AUTHORIZATION=f"Bearer {self.user_access_token}",
        )

        self.assertEqual(r.status_code, http_status.HTTP_200_OK, r.content)
        self.assertEqual(r.json()["name"], data["name"])

    def test_delete_appointment(self):
        order = self.create_test_order("WILL")
        (
            created_personal_details,
            created_appointment_store,
        ) = self.create_test_appointment_store(order, type="EXECUTOR")
        url = reverse("persons:update-appointment",
                      kwargs={"order_pk": order.id, })
        data = {
            "person": created_personal_details.id,
            "updated_type": "EXECUTOR",
        }
        response = self.client.delete(
            url,
            data=json.dumps(data),
            content_type="application/json",
            AUTHORIZATION=f"Bearer {self.user_access_token}",
        )
        self.assertEqual(len(created_appointment_store.entity_roles.all()), 0)
        self.assertEqual(response.status_code, http_status.HTTP_200_OK)

    @data("1990-01-01", "2010-01-01")
    def test_create_appointment(self, date_of_birth):
        order = self.create_test_order("WILL")
        (
            created_personal_details,
            created_appointment_store,
        ) = self.create_test_appointment_store(order)
        created_personal_details.date_of_birth = datetime.strptime(
            date_of_birth, "%Y-%m-%d"
        ).date()
        created_personal_details.save()

        url = reverse("persons:update-appointment",
                      kwargs={"order_pk": order.id, })
        data = {
            "person": created_personal_details.id,
            "updated_type": "GUARDIAN",
        }
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type="application/json",
            AUTHORIZATION=f"Bearer {self.user_access_token}",
        )

        if created_personal_details.age < 21:
            self.assertEqual(response.status_code,
                             http_status.HTTP_400_BAD_REQUEST)
        else:
            self.assertEqual(response.status_code, http_status.HTTP_200_OK)

    def test_appointment_number_overflow(self):
        """
        Given there is already one guardian of a will.
        When trying to add another guardian to the will,
        it will fail.
        """
        order = self.create_test_order("WILL")

        (
            created_personal_details,
            created_appointment_store,
        ) = self.create_test_appointment_store(order, type="GUARDIAN")

        additional_guardian = self.create_test_person()

        url = reverse("persons:update-appointment",
                      kwargs={"order_pk": order.id, })
        data = {
            "person": additional_guardian.id,
            "updated_type": "GUARDIAN",
        }
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type="application/json",
            AUTHORIZATION=f"Bearer {self.user_access_token}",
        )
        self.assertEqual(response.status_code,
                         http_status.HTTP_400_BAD_REQUEST)

    def test_duplicate_appointment(self):
        """
        Given a person is already guardian of a will.
        When trying to add this person as the guardian of the same will again,
        it will fail.
        """
        order = self.create_test_order("WILL")
        (
            created_personal_details,
            created_appointment_store,
        ) = self.create_test_appointment_store(order, type="GUARDIAN")

        url = reverse("persons:update-appointment",
                      kwargs={"order_pk": order.id, })
        data = {
            "person": created_personal_details.id,
            "updated_type": "GUARDIAN",
        }
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type="application/json",
            AUTHORIZATION=f"Bearer {self.user_access_token}",
        )
        self.assertEqual(response.status_code,
                         http_status.HTTP_400_BAD_REQUEST)

    def test_replacement_donee_cannot_be_updated_as_donee(self):
        """
        Given a person is already the replacement donee of a will.
        When trying to set this person as the donee of the same will,
        it will fail.
        """
        order = self.create_test_order("WILL")
        person, appointment_store = self.create_test_appointment_store(
            order, type="REPLACEMENT_DONEE"
        )

        url = reverse("persons:update-appointment",
                      kwargs={"order_pk": order.id, })
        data = {
            "person": person.id,
            "updated_type": "DONEE",
        }
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type="application/json",
            AUTHORIZATION=f"Bearer {self.user_access_token}",
        )
        self.assertEqual(response.status_code,
                         http_status.HTTP_400_BAD_REQUEST)

    def test_donee_cannot_be_updated_as_replacement_donee(self):
        """
        Given a person is already the donee of a will.
        When trying to set this person as the replacement donee of the same will,
        it will fail.
        """
        order = self.create_test_order("WILL")
        person, appointment_store = self.create_test_appointment_store(
            order, type="DONEE"
        )

        url = reverse("persons:update-appointment",
                      kwargs={"order_pk": order.id, })
        data = {
            "person": person.id,
            "updated_type": "REPLACEMENT_DONEE",
        }
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type="application/json",
            AUTHORIZATION=f"Bearer {self.user_access_token}",
        )
        self.assertEqual(response.status_code,
                         http_status.HTTP_400_BAD_REQUEST)

    def test_executor_cannot_be_updated_as_sub_executor(self):
        """
        Given a person is already the executor of a will.
        When trying to set this person as the sub executor of the same will,
        it will fail.
        """
        order = self.create_test_order("WILL")
        person, appointment_store = self.create_test_appointment_store(
            order, type="EXECUTOR"
        )

        url = reverse("persons:update-appointment",
                      kwargs={"order_pk": order.id, })
        data = {
            "person": person.id,
            "updated_type": "SUB_EXECUTOR",
        }
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type="application/json",
            AUTHORIZATION=f"Bearer {self.user_access_token}",
        )
        self.assertEqual(response.status_code,
                         http_status.HTTP_400_BAD_REQUEST)

    def test_sub_executor_cannot_be_updated_as_executor(self):
        """
        Given a person is already the sub executor of a will.
        When trying to set this person as the executor of the same will,
        it will fail.
        """
        order = self.create_test_order("WILL")
        person, appointment_store = self.create_test_appointment_store(
            order, type="SUB_EXECUTOR"
        )

        url = reverse("persons:update-appointment",
                      kwargs={"order_pk": order.id, })
        data = {
            "person": person.id,
            "updated_type": "EXECUTOR",
        }
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type="application/json",
            AUTHORIZATION=f"Bearer {self.user_access_token}",
        )
        self.assertEqual(response.status_code,
                         http_status.HTTP_400_BAD_REQUEST)

    def test_beneficiary_cannot_be_updated_as_witness(self):
        """
        Given a person is already the beneficiary of a will.
        When trying to set this person as the witness of the same will,
        it will fail.
        """
        order = self.create_test_order("WILL")
        person, appointment_store = self.create_test_appointment_store(
            order, type="BENEFICIARY"
        )

        url = reverse("persons:update-appointment",
                      kwargs={"order_pk": order.id, })
        data = {
            "person": person.id,
            "updated_type": "WITNESS",
        }
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type="application/json",
            AUTHORIZATION=f"Bearer {self.user_access_token}",
        )
        self.assertEqual(response.status_code,
                         http_status.HTTP_400_BAD_REQUEST)

    def test_list_donee_powers(self):
        order = self.create_test_order("WILL")

        url = reverse(
            "persons:list-create-donee-powers", kwargs={"order_pk": order.id, }
        )
        response = self.client.get(
            url, AUTHORIZATION=f"Bearer {self.user_access_token}"
        )
        self.assertEqual(response.status_code, http_status.HTTP_200_OK)

    def test_get_donee_powers(self):
        order = self.create_test_order("WILL")
        (
            created_personal_details,
            created_appointment_store,
        ) = self.create_test_appointment_store(order)
        power = person_factories.DoneePowersFactory.create(
            donee=created_appointment_store
        )
        url = reverse(
            "persons:update-donee-powers",
            kwargs={"order_pk": order.id, "donee_powers_pk": power.id, },
        )
        response = self.client.get(
            url, AUTHORIZATION=f"Bearer {self.user_access_token}"
        )
        self.assertEqual(response.status_code, http_status.HTTP_200_OK)

    def test_delete_person(self):
        order = self.create_test_order("WILL")
        person = self.create_test_person()
        url = reverse(
            "persons:update-people",
            kwargs={"order_pk": order.id, "person_pk": person.id, },
        )
        response = self.client.delete(
            url, AUTHORIZATION=f"Bearer {self.user_access_token}"
        )
        self.assertEqual(response.status_code, http_status.HTTP_204_NO_CONTENT)

    def test_create_donee_powers(self):
        order = self.create_test_order("WILL")
        person = self.create_test_person()

        url = reverse(
            "persons:list-create-donee-powers", kwargs={"order_pk": order.id, }
        )
        data = {
            "donee": person.id,
        }
        response = self.client.post(
            url, data, AUTHORIZATION=f"Bearer {self.user_access_token}"
        )
        self.assertEqual(response.status_code, http_status.HTTP_201_CREATED)

    def test_create_donee_powers_with_named_main_donee(self):
        order = self.create_test_order("WILL")
        donee, donee_store = self.create_test_appointment_store(order)
        person_factories.DoneePowersFactory.create(
            donee_id=donee_store.id, powers="BOTH"
        )

        named_main_donee = self.create_test_person()

        url = reverse(
            "persons:list-create-donee-powers", kwargs={"order_pk": order.id, }
        )
        data = {
            "donee": named_main_donee.id,
            "powers": "BOTH",
            "replacement_type": "NAMED",
            "named_main_donee": donee.id,
        }
        response = self.client.post(
            url, data, AUTHORIZATION=f"Bearer {self.user_access_token}"
        )

        self.assertEqual(response.status_code, http_status.HTTP_201_CREATED)

    def test_replace_donee(self):
        order = self.create_test_order("WILL")

        donee, donee_store = self.create_test_appointment_store(order)

        power = person_factories.DoneePowersFactory.create(
            donee_id=donee_store.id)

        new_donee = self.create_test_person()

        url = reverse(
            "persons:update-donee-powers",
            kwargs={"order_pk": order.id, "donee_powers_pk": power.id},
        )
        data = {"donee": new_donee.id}

        r = self.client.patch(
            url,
            data=json.dumps(data),
            content_type="application/json",
            AUTHORIZATION=f"Bearer {self.user_access_token}",
        )

        self.assertEqual(r.status_code, http_status.HTTP_200_OK, r.content)

    def test_delete_donee_powers(self):
        order = self.create_test_order("WILL")
        (
            created_personal_details,
            created_appointment_store,
        ) = self.create_test_appointment_store(order)
        power = person_factories.DoneePowersFactory.create(
            donee_id=created_appointment_store.id
        )
        url = reverse(
            "persons:update-donee-powers",
            kwargs={"order_pk": order.id, "donee_powers_pk": power.id},
        )
        power.refresh_from_db()
        r = self.client.delete(
            url, AUTHORIZATION=f"Bearer {self.user_access_token}")
        self.assertEqual(
            r.status_code, http_status.HTTP_204_NO_CONTENT, r.content)
        try:
            power.refresh_from_db()
            self.fail("The DoneePowers object should not longer exist.")
        except DoneePowers.DoesNotExist:
            pass

    def test_delete_donee_powers_automatically_deletes_replacement(self):
        order = self.create_test_order("WILL")

        donee = person_factories.PersonFactory.create(order=order)
        power = person_factories.DoneePowersFactory.create(donee_id=donee.id)

        rep_donee = person_factories.PersonFactory.create(order=order)
        rep_power = person_factories.DoneePowersFactory.create(
            donee_id=rep_donee.id, replacement_type="ANY"
        )

        url = reverse(
            "persons:update-donee-powers",
            kwargs={"order_pk": order.id, "donee_powers_pk": power.id},
        )
        r = self.client.delete(
            url, AUTHORIZATION=f"Bearer {self.user_access_token}")
        self.assertEqual(
            r.status_code, http_status.HTTP_204_NO_CONTENT, r.content)

        try:
            rep_power.refresh_from_db()
            self.fail(
                "The replacement DoneePowers object should also be deleted.")
        except DoneePowers.DoesNotExist:
            pass

    @data(
        dict(deleted_powers="PERSONAL_WELFARE",
             kept_powers="PROPERTY_AND_AFFAIRS"),
        dict(deleted_powers="PROPERTY_AND_AFFAIRS",
             kept_powers="PERSONAL_WELFARE"),
    )
    @unpack
    def test_delete_donee_powers_auto_deletes_only_rep_powers_with_matching_type(
        self, deleted_powers=None, kept_powers=None
    ):
        order = self.create_test_order("WILL")

        donee_1 = person_factories.PersonFactory.create(order=order)
        power_1 = person_factories.DoneePowersFactory.create(
            donee_id=donee_1.id, powers=deleted_powers
        )

        donee_2 = person_factories.PersonFactory.create(order=order)
        power_2 = person_factories.DoneePowersFactory.create(
            donee_id=donee_2.id, powers=kept_powers
        )

        rep_donee_1 = person_factories.PersonFactory.create(order=order)
        rep_power_1 = person_factories.DoneePowersFactory.create(
            donee_id=rep_donee_1.id, replacement_type=deleted_powers
        )

        rep_donee_2 = person_factories.PersonFactory.create(order=order)
        rep_power_2 = person_factories.DoneePowersFactory.create(
            donee_id=rep_donee_2.id, replacement_type=kept_powers
        )

        url = reverse(
            "persons:update-donee-powers",
            kwargs={"order_pk": order.id, "donee_powers_pk": power_1.id},
        )
        r = self.client.delete(
            url, AUTHORIZATION=f"Bearer {self.user_access_token}")
        self.assertEqual(
            r.status_code, http_status.HTTP_204_NO_CONTENT, r.content)

        power_2.refresh_from_db()
        try:
            rep_power_1.refresh_from_db()
            self.fail(
                "The replacement DoneePowers object of the same type should also be"
                " deleted."
            )
        except DoneePowers.DoesNotExist:
            pass
        rep_power_2.refresh_from_db()

    @data(
        dict(deleted_powers="PERSONAL_WELFARE",
             kept_powers="PROPERTY_AND_AFFAIRS"),
        dict(deleted_powers="PROPERTY_AND_AFFAIRS",
             kept_powers="PERSONAL_WELFARE"),
    )
    @unpack
    def test_keep_replacements_of_type_any_when_a_donee_exists(
        self, deleted_powers=None, kept_powers=None
    ):
        order = self.create_test_order("WILL")

        donee_1 = person_factories.PersonFactory.create(order=order)
        power_1 = person_factories.DoneePowersFactory.create(
            donee_id=donee_1.id, powers=deleted_powers
        )

        donee_2 = person_factories.PersonFactory.create(order=order)
        power_2 = person_factories.DoneePowersFactory.create(
            donee_id=donee_2.id, powers=kept_powers
        )

        rep_donee = person_factories.PersonFactory.create(order=order)
        rep_power = person_factories.DoneePowersFactory.create(
            donee_id=rep_donee.id, replacement_type="ANY"
        )

        url = reverse(
            "persons:update-donee-powers",
            kwargs={"order_pk": order.id, "donee_powers_pk": power_1.id},
        )
        r = self.client.delete(
            url, AUTHORIZATION=f"Bearer {self.user_access_token}")
        self.assertEqual(
            r.status_code, http_status.HTTP_204_NO_CONTENT, r.content)

        power_2.refresh_from_db()
        rep_power.refresh_from_db()

    @data(
        dict(deleted_powers="PERSONAL_WELFARE",
             kept_powers="PROPERTY_AND_AFFAIRS"),
        dict(deleted_powers="PROPERTY_AND_AFFAIRS",
             kept_powers="PERSONAL_WELFARE"),
    )
    @unpack
    def test_keep_named_replacements_when_main_donee_exists(
        self, deleted_powers=None, kept_powers=None
    ):
        order = self.create_test_order("WILL")

        donee_1 = person_factories.PersonFactory.create(order=order)
        power_1 = person_factories.DoneePowersFactory.create(
            donee_id=donee_1.id, powers=deleted_powers
        )

        donee_2 = person_factories.PersonFactory.create(order=order)
        power_2 = person_factories.DoneePowersFactory.create(
            donee_id=donee_2.id, powers=kept_powers
        )

        rep_donee = person_factories.PersonFactory.create(order=order)
        rep_power = person_factories.DoneePowersFactory.create(
            donee_id=rep_donee.id, replacement_type="NAMED", named_main_donee=donee_2
        )

        url = reverse(
            "persons:update-donee-powers",
            kwargs={"order_pk": order.id, "donee_powers_pk": power_1.id},
        )
        r = self.client.delete(
            url, AUTHORIZATION=f"Bearer {self.user_access_token}")
        self.assertEqual(
            r.status_code, http_status.HTTP_204_NO_CONTENT, r.content)

        power_2.refresh_from_db()
        rep_power.refresh_from_db()

    def test_re_add_the_same_person_as_donee(self):
        """
        Given a person is already a donee.
        When settings that person as donee again,
        it will fail.
        """
        power = person_factories.DoneePowersFactory.create()
        url = reverse(
            "persons:list-create-donee-powers",
            kwargs={"order_pk": power.donee.order_id, },
        )

        data = {
            "donee": power.donee.entity_details
        }
        response = self.client.post(
            url, data, AUTHORIZATION=f"Bearer {self.user_access_token}"
        )
        self.assertEqual(response.status_code,
                         http_status.HTTP_400_BAD_REQUEST)

    def test_cannot_create_replacement_having_no_main_donee(self):
        order = self.create_test_order("WILL")
        donee = person_factories.PersonFactory.create(order_id=order.id)

        url = reverse(
            "persons:list-create-donee-powers", kwargs={"order_pk": order.id, }
        )

        data = {
            "donee": donee.id,
            "replacement_type": "ANY",
        }
        response = self.client.post(
            url, data, AUTHORIZATION=f"Bearer {self.user_access_token}"
        )
        self.assertEqual(response.status_code,
                         http_status.HTTP_400_BAD_REQUEST)

    @data(
        dict(main_powers="PERSONAL_WELFARE",
             replacement_powers="PROPERTY_AND_AFFAIRS"),
        dict(main_powers="PROPERTY_AND_AFFAIRS",
             replacement_powers="PERSONAL_WELFARE"),
    )
    @unpack
    def test_cannot_create_replacement_having_no_main_donee_of_the_same_type(
        self, main_powers=None, replacement_powers=None
    ):
        order = self.create_test_order("WILL")
        main_donee = person_factories.PersonFactory.create(order_id=order.id)
        person_factories.DoneePowersFactory.create(
            donee_id=main_donee.id, powers=main_powers
        )

        replacement_donee = person_factories.PersonFactory.create(
            order_id=order.id)

        url = reverse(
            "persons:list-create-donee-powers", kwargs={"order_pk": order.id, }
        )
        data = {
            "donee": replacement_donee.id,
            "replacement_type": replacement_powers,
        }
        response = self.client.post(
            url, data, AUTHORIZATION=f"Bearer {self.user_access_token}"
        )
        self.assertEqual(response.status_code,
                         http_status.HTTP_400_BAD_REQUEST)

    def test_replacing_invalid_named_main_donee(self):
        order = self.create_test_order("WILL")
        main_donee = person_factories.PersonFactory.create(order_id=order.id)
        person_factories.DoneePowersFactory.create(
            donee_id=main_donee.id, powers="BOTH"
        )

        invalid_main_donee = person_factories.PersonFactory.create(
            order_id=order.id)
        replacement_donee = person_factories.PersonFactory.create(
            order_id=order.id)

        url = reverse(
            "persons:list-create-donee-powers", kwargs={"order_pk": order.id, }
        )
        data = {
            "donee": replacement_donee.id,
            "replacement_type": "NAMED",
            "named_main_donee": invalid_main_donee.pk,
        }
        response = self.client.post(
            url, data, AUTHORIZATION=f"Bearer {self.user_access_token}"
        )

        self.assertEqual(response.status_code,
                         http_status.HTTP_400_BAD_REQUEST)

    @data(
        dict(main_powers="BOTH", replacement_powers="ANY"),
        dict(main_powers="BOTH", replacement_powers="PERSONAL_WELFARE"),
        dict(main_powers="BOTH", replacement_powers="PROPERTY_AND_AFFAIRS"),
        dict(main_powers="PERSONAL_WELFARE",
             replacement_powers="PERSONAL_WELFARE"),
        dict(main_powers="PERSONAL_WELFARE", replacement_powers="ANY"),
        dict(
            main_powers="PROPERTY_AND_AFFAIRS",
            replacement_powers="PROPERTY_AND_AFFAIRS",
        ),
        dict(main_powers="PROPERTY_AND_AFFAIRS", replacement_powers="ANY"),
    )
    @unpack
    def test_valid_donee_replacements(self, main_powers=None, replacement_powers=None):
        order = self.create_test_order("WILL")

        (
            main_donee_personal_details,
            main_donee_appointment_store,
        ) = self.create_test_appointment_store(order)

        donee_powers = person_factories.DoneePowersFactory.create(
            donee_id=main_donee_appointment_store.id, powers=main_powers
        )

        replacement_donee_personal_details = self.create_test_person()
        replacement_donee_store_before = len(
            replacement_donee_personal_details.entity_store.all()
        )

        url = reverse(
            "persons:update-donee-powers",
            kwargs={"order_pk": order.id, "donee_powers_pk": donee_powers.id},
        )
        data = {
            "donee": replacement_donee_personal_details.id,
            "replacement_type": replacement_powers,
        }
        response = self.client.patch(
            url,
            data,
            content_type="application/json",
            AUTHORIZATION=f"Bearer {self.user_access_token}",
        )

        replacement_donee_store_after = len(
            replacement_donee_personal_details.entity_store.all()
        )

        self.assertEqual(replacement_donee_store_before, 0)
        self.assertEqual(replacement_donee_store_after, 1)
        self.assertEqual(response.status_code, http_status.HTTP_200_OK)
