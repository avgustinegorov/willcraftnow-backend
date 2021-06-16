from django.utils.translation import gettext
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from utils.serializers import CustomModelSerializer, CustomSerializer
from utils.fields import CharField
from utils.mixins import ListSerializerWithChildModelsMixin

from .fields import EntityStoresPrimaryKeyRelatedField
from .models import *
from .utils import get_entity_types, get_or_create_entity_types


class CharitySerializer(CustomModelSerializer):
    """ Generic Model Serializer for PersonalDetails """

    display_name = serializers.CharField(read_only=True, source="__str__")
    entity_type = CharField(display=False)

    def validate(self, data):
        user = self.context.get("user", None)
        if not user:
            raise Exception("Please provider user in Serializer context")
        data["user"] = user
        return data

    class Meta:
        model = Charity
        fields = ["id", "name", "UEN", "display_name", "entity_type"]


class PersonSerializer(CustomModelSerializer):
    """ Generic Model Serializer for PersonalDetails """

    block_only_address = serializers.SerializerMethodField(read_only=True)
    address = serializers.SerializerMethodField(read_only=True)
    display_name = serializers.CharField(read_only=True, source="__str__")
    email = serializers.SerializerMethodField(read_only=True)
    entity_type = CharField(display=False)
    is_user = serializers.SerializerMethodField(read_only=True)

    def get_is_user(self, instance):
        return hasattr(instance, "user_detail")

    def get_email(self, instance):
        if instance.email:
            return instance.email
        if hasattr(instance, "user_detail"):
            return instance.user_detail.email
        return None

    def get_block_only_address(self, instance):
        return instance.address_block_only

    def get_address(self, instance):
        return instance.address

    def validate_contact_number(self, contact_number):
        order = self.context["order"] if "order" in self.context else None
        if order and order.order_type == "LPA" and "+65" not in contact_number:
            raise serializers.ValidationError(
                _("Please provide a Singapore Contact Number.")
            )
        return contact_number

    def validate_country(self, country):
        order = self.context["order"] if "order" in self.context else None
        if order and order.order_type == "LPA" and country != "SG":
            raise serializers.ValidationError(
                _("Please provide a Singapore Mailing Address.")
            )
        return country

    def validate(self, data):
        user = self.context.get("user", None)
        if not user:
            raise Exception("Please provider user in Serializer context")
        data["user"] = user

        real_estate_types_not_has_floor_number = [
            "TERRACE",
            "SEMI_DETACHED",
            "BUNGALOW",
        ]
        real_estate_type = data.get("real_estate_type", None)
        if not real_estate_type:
            real_estate_type = self.instance.real_estate_type if self.instance else None

        if real_estate_type in real_estate_types_not_has_floor_number:
            if "floor_number" in data:
                raise serializers.ValidationError(
                    _(
                        "Floor number not allowed for TERRACE, SEMI_DETACHED, BUNGALOW"
                        " real estate types."
                    )
                )
            data["floor_number"] = None

        return data

    class Meta:
        model = Person
        fields = [
            "id",
            "is_user",
            "name",
            "id_number",
            "id_document",
            "country_of_issue",
            "date_of_birth",
            "address",
            "block_only_address",
            "real_estate_type",
            "block_number",
            "floor_number",
            "unit_number",
            "street_name",
            "country",
            "postal_code",
            "religion",
            "citizenship_status",
            "relationship_status",
            "underage_children",
            "gender",
            "relationship",
            "relationship_other",
            "contact_number",
            "email",
            "display_name",
            "is_private_housing",
            "entity_type"
        ]


class EntitySerializer(ListSerializerWithChildModelsMixin, CustomModelSerializer):

    class Meta:
        model = Entity
        fields = "__all__"
        serializer_map = {
            "Person": PersonSerializer,
            "Charity": CharitySerializer,
        }
        model_key = 'entity_type'


class DoneePowersSerializer(CustomModelSerializer):
    """ Generic Model Serializer for DoneePowers """

    is_replacement_donee = serializers.BooleanField(read_only=True)
    donee = EntityStoresPrimaryKeyRelatedField(
        read_only=False, queryset=Person.objects.all()
    )
    named_main_donee = EntityStoresPrimaryKeyRelatedField(
        read_only=False,
        queryset=Person.objects.all(),
        required=False,
        allow_null=True,
    )

    def validate_donee(self, donee):
        print("donee", donee)
        print(DoneePowers.objects.all())
        print([donee.id for donee in DoneePowers.objects.all()])
        if DoneePowers.objects.filter(donee_id=donee).exists():
            raise serializers.ValidationError(
                _("This Person is already a Donee. Please name another.")
            )

        age = donee.entity_details.age

        if age < 21:
            raise serializers.ValidationError(
                gettext("{}(s) cannot be less than 21 years old.").format(
                    gettext("Donee")
                )
            )

        return donee

    def validate_named_main_donee(self, named_main_donee):

        if named_main_donee and named_main_donee.entity_details.age < 21:
            raise serializers.ValidationError(
                gettext("{}(s) cannot be less than 21 years old.").format(
                    gettext("Donee")
                )
            )

        return named_main_donee

    def validate(self, data):

        donee = data.get("donee")
        named_main_donee = data.get("named_main_donee")
        replacement_type = data.get("replacement_type")

        if not replacement_type:
            return data

        main_powers_q = DoneePowers.objects.filter(
            donee__order=donee.order, replacement_type__isnull=True
        )

        if not main_powers_q.exists():
            raise serializers.ValidationError(
                _("Replacement donee must have main donee.")
            )

        if replacement_type in ["PERSONAL_WELFARE", "PROPERTY_AND_AFFAIRS"]:
            if not main_powers_q.filter(powers__in=[replacement_type, "BOTH"]).exists():
                raise serializers.ValidationError(
                    _("Replacement donee must have main donee of matching type.")
                )

        elif replacement_type == "NAMED":
            if not main_powers_q.filter(donee=named_main_donee).exists():
                raise serializers.ValidationError(
                    _("Named main donee not found."))

        return data

    class Meta:
        model = DoneePowers
        fields = [
            "donee",
            "powers",
            "replacement_type",
            "named_main_donee",
            "is_replacement_donee",
            "id",
        ]


class AppointmentSerializer(CustomSerializer):
    person = EntityStoresPrimaryKeyRelatedField(
        queryset=Entity.objects.all(), label=_("Person")
    )
    updated_type = serializers.CharField(required=True)

    def get_entity_store(self, instance):
        order = self.context.get("order")
        return instance.get_entity_store(order)

    def update(self, instance, validated_data):
        """#Overwrites the default update method to confirm that
        # a new PersonalDetails model isn't created for every new
        # update
        """

        updated_type, _ = EntityType.objects.get_or_create(
            type_name=validated_data["updated_type"]
        )

        validated_data['person'].entity_roles.add(updated_type)
        return validated_data

    def delete(self, instance, validated_data):
        """#Overwrites the default update method to confirm that
        # a new PersonalDetails model isn't created for every new
        # update
        """
        updated_type, _ = EntityType.objects.get_or_create(
            type_name=validated_data["updated_type"]
        )
        print(instance, validated_data['person'])
        self.get_entity_store(instance).entity_roles.remove(updated_type)

        return validated_data

    def validate(self, validated_data):
        if self.context["request"].method == "DELETE":
            return super().validate(validated_data)

        """ Limits the appointing of EntityTypes to a number defined.
        """
        person = validated_data["person"]
        order = self.context.get("order")
        initial_entity_type = list(
            person.entity_roles.all().values_list("id", flat=True)
        )
        beneficiary_type, executor_type, sub_executor_type, donee_type, replacement_donee_type = \
            get_or_create_entity_types()
        updated_type, _ = EntityType.objects.get_or_create(
            type_name=self.initial_data["updated_type"])

        for entity_type_key, entity_type_value in get_entity_types():
            if self.initial_data["updated_type"] == entity_type_key:
                # get total persons associated with the order who have the particular appointment
                total_entities = len(EntityStore.objects.filter(
                    order=order, entity_roles__type_name=entity_type_key
                )
                )
                # If the person type does not already exist in the person's appointment_type,
                # and its in the request (i.e. that he's trying to add it), then see if
                # it has hit the limit, and if so throw error.
                if total_entities == entity_type_value \
                        and updated_type.id not in initial_entity_type:
                    raise serializers.ValidationError(
                        {"person": gettext("You can't allocate more than {} {}.")
                            .format(entity_type_value,
                                    gettext(entity_type_key.title()),
                                    )
                         })

        # Find the type that user is trying to add and check for duplicates.
        if updated_type.id in initial_entity_type:
            raise serializers.ValidationError(
                {"person": gettext("This person is already an {}.").format(
                    gettext(updated_type.type_name.title()))
                 }
            )

        if updated_type.type_name == "DONEE" and replacement_donee_type.id in initial_entity_type:
            raise serializers.ValidationError(
                {"person": gettext("This person is already an {}.").format(
                    gettext(replacement_donee_type.type_name.title()))
                 }
            )

        if updated_type.type_name == "REPLACEMENT_DONEE" and donee_type.id in initial_entity_type:
            raise serializers.ValidationError(
                {"person": gettext("This person is already an {}.").format(
                    gettext(donee_type.type_name.title()))
                 }
            )

        # stop adding of witnesses to beneficiaries.
        if updated_type.type_name == "SUB_EXECUTOR" and executor_type.id in initial_entity_type:
            raise serializers.ValidationError(
                {"person": gettext(
                    "Executors cannot be appointed as Substitute Executors.")
                 }
            )

        # stop adding of witnesses to beneficiaries.
        if updated_type.type_name == "EXECUTOR" and sub_executor_type.id in initial_entity_type:
            raise serializers.ValidationError(
                {"person":
                    gettext(
                        "This person is Substitute Executor and cannot also be an Executor.")
                 }
            )

        # stop adding of witnesses to beneficiaries.
        if updated_type.type_name == "WITNESS" and beneficiary_type.id in initial_entity_type:
            raise serializers.ValidationError(
                {"person": gettext(
                    "Beneficiaries cannot be appointed as Witnesses.")}
            )

        if not hasattr(person.entity_details, "person"):
            raise serializers.ValidationError(
                {"person": 'Please provide a Person entity.'}
            )

        age = person.entity_details.person.age
        if updated_type.type_name != "BENEFICIARY" and age < 21:
            raise serializers.ValidationError(
                {"person": gettext("{}(s) cannot be less than 21 years old.").format(
                    gettext(updated_type.type_name.title()))
                 }
            )

        updated_type, _ = EntityType.objects.get_or_create(
            type_name=self.initial_data["updated_type"]
        )
        validated_data["updated_type"] = updated_type

        return super().validate(validated_data)


class EntityStoreSerializer(serializers.ModelSerializer):
    """A generic serializer for person(s)
    that supports automatic creation of a set of personal details
    as well as attachment to the order model
    """

    entity_roles = serializers.SlugRelatedField(
        many=True, read_only=True, required=False, slug_field="type_name"
    )
    entity = serializers.PrimaryKeyRelatedField(
        queryset=Entity.objects.all(), source='entity_details'
    )
    donee_powers = DoneePowersSerializer(required=False, read_only=True)

    class Meta:
        model = EntityStore
        fields = "__all__"
