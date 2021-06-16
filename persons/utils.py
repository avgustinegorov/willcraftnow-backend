from persons.models import EntityType


def get_entity_types():
    return [
        ("EXECUTOR", 4,),
        ("SUB_EXECUTOR", 1,),
        ("GUARDIAN", 1,),
        ("SUB_GUARDIAN", 1,),
        ("DONEE", 2,),
        ("REPLACEMENT_DONEE", 1,),
        ("WITNESS", 2,),
    ]


def get_or_create_entity_types():
    # Get or create entity types and return.
    beneficiary_type, _ = EntityType.objects.get_or_create(type_name="BENEFICIARY")
    executor_type, _ = EntityType.objects.get_or_create(type_name="EXECUTOR")
    sub_executor_type, _ = EntityType.objects.get_or_create(type_name="SUB_EXECUTOR")
    donee_type, _ = EntityType.objects.get_or_create(type_name="DONEE")
    replacement_donee_type, _ = EntityType.objects.get_or_create(
        type_name="REPLACEMENT_DONEE"
    )

    entity_types = (beneficiary_type, executor_type, sub_executor_type, donee_type, replacement_donee_type)
    return entity_types
