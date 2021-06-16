from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.signals import post_save, pre_delete, pre_save
from django.dispatch import receiver
from django.forms.models import model_to_dict
from django.utils.encoding import force_str

from assets.models import *
from billing.models import *
from core.models import *
from lastrites.models import *
from persons.models import *
from willcraft_auth.models import WillCraftUser

from .models import ChangeEvent

EXCLUDE_FIELDS = [
    "willcraft_auth.WillCraftUser.last_login",
    "billing.Invoice.pdf_invoice",
    "core.WillOrder.pdf_will",
]


@receiver(
    pre_save,
    sender=Person,
    dispatch_uid="personal_details_history_change_signal",
)
@receiver(pre_save, sender=EntityStore, dispatch_uid="person_history_change_signal")
@receiver(
    pre_save,
    sender=WillInstructions,
    dispatch_uid="will_instructions_history_change_signal",
)
@receiver(
    pre_save, sender=WillLastRites, dispatch_uid="will_lastrites_history_change_signal"
)
@receiver(pre_save, sender=WillOrder, dispatch_uid="will_order_history_change_signal")
@receiver(
    pre_save, sender=WillCraftUser, dispatch_uid="willcraft_user_history_change_signal"
)
@receiver(pre_save, sender=Discount, dispatch_uid="discount_history_change_signal")
@receiver(pre_save, sender=Invoice, dispatch_uid="invoice_history_change_signal")
@receiver(pre_save, sender=Allocation, dispatch_uid="allocation_history_change_signal")
@receiver(pre_save, sender=RealEstate, dispatch_uid="real_estate_history_change_signal")
@receiver(
    pre_save, sender=BankAccount, dispatch_uid="bank_account_history_change_signal"
)
@receiver(pre_save, sender=Insurance, dispatch_uid="insurance_history_change_signal")
@receiver(pre_save, sender=Investment, dispatch_uid="investment_history_change_signal")
@receiver(pre_save, sender=Company, dispatch_uid="company_history_change_signal")
@receiver(pre_save, sender=Residual, dispatch_uid="residual_history_change_signal")
def add_instance_history(sender, instance, using, **kwargs):
    """A signal that creates a new History instance that records  any changes
    made to any instance of the models the signal is attached to
    """
    # Getting the existing object in the database to get changed fields
    try:
        original_instance = sender.objects.get(id=instance.id)
    except sender.DoesNotExist:
        # Don't create history event if the original instance doessn't exist in the db
        return
    original_instance = model_to_dict(original_instance)

    changed_instance = model_to_dict(instance)

    # Fields that have auot_now set to True or the fields we should generally ignore
    auto_now_fields = [
        field.name
        for field in instance._meta.fields
        if getattr(field, "auto_now", False) or str(field) in EXCLUDE_FIELDS
    ]

    # Getting the changed fields while excluding the "auto_now" fields from diff
    diff = {
        field: value
        for field, value in changed_instance.items()
        if original_instance[field] != value and field not in auto_now_fields
    }

    # Skip creating the change event if no field was changed
    if not diff:
        return

    for key, value in diff.items():
        if hasattr(value, "__class__") and value.__class__.__name__ == "Country":
            diff[key] = force_str(value)

        if key == "entity_roles":
            diff[key] = [model_to_dict(x) for x in value]

    # Creating the ChangeEvent model
    change_event = ChangeEvent(
        change_type="UPDATE",
        changes=json.dumps(diff, cls=DjangoJSONEncoder),
        content_object=instance,
    )
    change_event.save()

    return


@receiver(
    post_save,
    sender=Person,
    dispatch_uid="personal_details_history_create_signal",
)
@receiver(post_save, sender=EntityStore, dispatch_uid="person_history_create_signal")
@receiver(
    post_save,
    sender=WillInstructions,
    dispatch_uid="will_instructions_history_create_signal",
)
@receiver(
    post_save, sender=WillLastRites, dispatch_uid="will_lastrites_history_create_signal"
)
@receiver(post_save, sender=WillOrder, dispatch_uid="will_order_history_create_signal")
@receiver(
    post_save, sender=WillCraftUser, dispatch_uid="willcraft_user_history_create_signal"
)
@receiver(post_save, sender=Discount, dispatch_uid="discount_history_create_signal")
@receiver(post_save, sender=Invoice, dispatch_uid="invoice_history_create_signal")
@receiver(post_save, sender=Allocation, dispatch_uid="allocation_history_create_signal")
@receiver(
    post_save, sender=RealEstate, dispatch_uid="real_estate_history_create_signal"
)
@receiver(
    post_save, sender=BankAccount, dispatch_uid="bank_account_history_create_signal"
)
@receiver(post_save, sender=Insurance, dispatch_uid="insurance_history_create_signal")
@receiver(post_save, sender=Investment, dispatch_uid="investment_history_create_signal")
@receiver(post_save, sender=Company, dispatch_uid="company_history_create_signal")
@receiver(post_save, sender=Residual, dispatch_uid="residual_history_create_signal")
def add_create_instance_history(sender, instance, using, **kwargs):
    """A signal that creates a new History instance that records  any changes
    made to any instance of the models the signal is attached to
    """
    # if its an update, skip
    if sender.objects.filter(id=instance.id).exists():
        return

    original_instance = model_to_dict(instance)

    # Fields that have auot_now set to True or the fields we should generally ignore
    auto_now_fields = [
        field.name
        for field in instance._meta.fields
        if getattr(field, "auto_now", False) or str(field) in EXCLUDE_FIELDS
    ]

    # Getting the changed fields while excluding the "auto_now" fields from diff
    diff = {
        field: value
        for field, value in model_to_dict(instance).items()
        if field not in auto_now_fields
    }

    # Skip creating the change event if no field was changed
    if not diff:
        return

    for key, value in diff.items():
        if hasattr(value, "__class__") and value.__class__.__name__ == "Country":
            diff[key] = force_str(value)

        if key == "entity_roles":
            diff[key] = [model_to_dict(x) for x in value]

    # Creating the ChangeEvent model
    change_event = ChangeEvent(
        change_type="CREATE",
        changes=json.dumps(diff, cls=DjangoJSONEncoder),
        content_object=instance,
    )
    change_event.save()

    return


@receiver(
    pre_delete,
    sender=Person,
    dispatch_uid="personal_details_history_delete_signal",
)
@receiver(pre_delete, sender=EntityStore, dispatch_uid="person_history_delete_signal")
@receiver(
    pre_delete,
    sender=WillInstructions,
    dispatch_uid="will_instructions_history_delete_signal",
)
@receiver(
    pre_delete,
    sender=WillLastRites,
    dispatch_uid="will_lastrites_history_delete_signal",
)
@receiver(pre_delete, sender=WillOrder, dispatch_uid="will_order_history_delete_signal")
@receiver(
    pre_delete,
    sender=WillCraftUser,
    dispatch_uid="willcraft_user_history_delete_signal",
)
@receiver(pre_delete, sender=Discount, dispatch_uid="discount_history_delete_signal")
@receiver(pre_delete, sender=Invoice, dispatch_uid="invoice_history_delete_signal")
@receiver(
    pre_delete, sender=Allocation, dispatch_uid="allocation_history_delete_signal"
)
@receiver(
    pre_delete, sender=RealEstate, dispatch_uid="real_estate_history_delete_signal"
)
@receiver(
    pre_delete, sender=BankAccount, dispatch_uid="bank_account_history_delete_signal"
)
@receiver(pre_delete, sender=Insurance, dispatch_uid="insurance_history_delete_signal")
@receiver(
    pre_delete, sender=Investment, dispatch_uid="investment_history_delete_signal"
)
@receiver(pre_delete, sender=Company, dispatch_uid="company_history_delete_signal")
@receiver(pre_delete, sender=Residual, dispatch_uid="residual_history_delete_signal")
def add_delete_instance_history(sender, instance, using, **kwargs):
    """A signal that creates a new History instance that records  any changes
    made to any instance of the models the signal is attached to
    """

    # Fields that have auot_now set to True or the fields we should generally ignore
    auto_now_fields = [
        field.name
        for field in instance._meta.fields
        if getattr(field, "auto_now", False) or str(field) in EXCLUDE_FIELDS
    ]

    # Getting the changed fields while excluding the "auto_now" fields from diff
    diff = {
        field: value
        for field, value in model_to_dict(instance).items()
        if field not in auto_now_fields
    }

    # Skip creating the change event if no field was changed
    if not diff:
        return

    for key, value in diff.items():
        if hasattr(value, "__class__") and value.__class__.__name__ == "Country":
            diff[key] = force_str(value)

        if key == "entity_types":
            diff[key] = [model_to_dict(x) for x in value]

        # fix serialize of m2m fields
        if isinstance(value, list):
            new_value = []
            for item in value:
                if hasattr(item, '_meta') and hasattr(item._meta, 'model'):
                    new_value.append(model_to_dict(item))
                else:
                    new_value.append(item)
            diff[key] = new_value

    # Creating the ChangeEvent model
    change_event = ChangeEvent(
        change_type="DELETE",
        changes=json.dumps(diff, cls=DjangoJSONEncoder),
        content_object=instance,
    )
    change_event.save()

    return
