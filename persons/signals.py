import logging

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.db.models.signals import m2m_changed

from .models import *

log = logging.getLogger(__name__)


@receiver(
    post_save,
    sender=EntityStore,
    dispatch_uid="entity_store_post_save_update_invoice",
)
def update_invoice(sender, instance, *args, **kwargs):
    """Updates the Substitute allocation if it is a main allocation"""
    # check if allocation is a substitute allocation
    invoice = instance.order.invoice.latest()
    invoice.update_invoice()
    invoice.save()


@receiver(
    post_save,
    sender=DoneePowers,
    dispatch_uid="donee_powers_post_save_update_invoice",
)
def update_invoice(sender, instance, *args, **kwargs):
    """Updates the Substitute allocation if it is a main allocation"""
    # check if allocation is a substitute allocation
    invoice = instance.donee.order.invoice.latest()
    invoice.update_invoice()
    invoice.save()


# triggered on updateing witness persontype to persons to delete all witness service instances.
# NB: a corresponding function to delete witness persontypes is put in update views function for the legal services mod.
@receiver(post_save, sender=EntityStore, dispatch_uid="witness_person_post_save_signal")
def update_witness_appointment_type(sender, instance, created, *args, **kwargs):
    """Updates the witness model to let it know that it's a person witness and not firm witness"""
    witness_entity_type, _ = EntityType.objects.get_or_create(
        type_name="WITNESS"
    )
    if witness_entity_type in instance.entity_roles.all() \
            and hasattr(instance.order, "legal_services_witnessservice"):
        instance.order.legal_services_witnessservice.all().delete()


@receiver(
    post_delete,
    sender=DoneePowers,
    dispatch_uid="update_power_restrictions_post_delete_signal",
)
def update_power_restrictions(sender, instance, *args, **kwargs):
    """Updates the power restrictions."""
    order = instance.donee.order
    if not order.entitystore_set.of_entity_type('DONEE', "PROPERTY_AND_AFFAIRS"):
        if getattr(order, "property_and_affairs_restrictions", None):
            order.property_and_affairs_restrictions.delete()
    if not order.entitystore_set.of_entity_type('DONEE', "PERSONAL_WELFARE"):
        if getattr(order, "personal_welfare_restrictions", None):
            order.personal_welfare_restrictions.delete()


@receiver(
    post_delete,
    sender=DoneePowers,
    dispatch_uid="update_appointment_types_post_delete_signal",
)
def update_entity_types(sender, instance, *args, **kwargs):
    """Updates the person types on delete of powers."""
    donee_type, _ = EntityType.objects.get_or_create(type_name="DONEE")
    replacement_donee_type, _ = EntityType.objects.get_or_create(
        type_name="REPLACEMENT_DONEE"
    )
    instance.donee.entity_roles.remove(replacement_donee_type)
    instance.donee.entity_roles.remove(donee_type)
    instance.donee.save()


@receiver(
    post_delete,
    sender=DoneePowers,
    dispatch_uid="delete_related_replacement_donee_powers_post_delete_signal",
)
def delete_related_replacement_donee_powers(sender, instance, *args, **kwargs):
    order = instance.donee.order
    remaining_main_donee_powers_q = DoneePowers.objects.filter(
        donee__order=order, replacement_type__isnull=True
    )
    main_donee_powers_exist = remaining_main_donee_powers_q.exists()

    rep_donee_powers_q = DoneePowers.objects.filter(
        donee__order=order, replacement_type__isnull=False
    )

    if not main_donee_powers_exist:
        rep_donee_powers_q.delete()
        return

    to_be_deleted_rep_powers = []

    for rep_donee_powers in rep_donee_powers_q:
        if rep_donee_powers.replacement_type == "ANY":
            continue

        if (
            rep_donee_powers.replacement_type == "NAMED"
            and remaining_main_donee_powers_q.filter(
                donee=rep_donee_powers.named_main_donee
            ).exists()
        ):
            continue

        if (
            rep_donee_powers.replacement_type == "PERSONAL_WELFARE"
            and remaining_main_donee_powers_q.filter(
                powers__in=["BOTH", "PERSONAL_WELFARE"]
            ).exists()
        ):
            continue

        if (
            rep_donee_powers.replacement_type == "PROPERTY_AND_AFFAIRS"
            and remaining_main_donee_powers_q.filter(
                powers__in=["BOTH", "PROPERTY_AND_AFFAIRS"]
            ).exists()
        ):
            continue

        to_be_deleted_rep_powers.append(rep_donee_powers.id)

    rep_donee_powers_q.filter(pk__in=to_be_deleted_rep_powers).delete()


# @receiver(
#     m2m_changed, sender=EntityStore.entity_roles.through, dispatch_uid="donee_person_post_save_signal"
# )
# def update_donee_appointment_type(sender, instance, *args, **kwargs):
#     """Deletes Donee Powers when Entity Type is deleted"""
#     if kwargs.get('action') != 'pre_remove':
#         return

#     donee_type, _ = EntityType.objects.get_or_create(
#         type_name="DONEE"
#     )
#     entity_types_set = kwargs.get('pk_set')
#     if donee_type.id in entity_types_set and instance.donee_powers:
#         instance.donee_powers.delete()

# TODO: Change this to use m2m_changed


@receiver(
    post_save, sender=EntityStore, dispatch_uid="sub_executor_person_post_save_signal"
)
def update_sub_executor_appointment_type(sender, instance, created, *args, **kwargs):
    """Deletes Sub_executors when executors are deleted"""
    subexecutor_type, _ = EntityType.objects.get_or_create(
        type_name="SUB_EXECUTOR"
    )
    subexecutors = EntityStore.objects.filter(
        entity_roles__in=[subexecutor_type])
    subexecutor_exists = subexecutors.exists()

    executor_type, _ = EntityType.objects.get_or_create(type_name="EXECUTOR")
    executors = EntityStore.objects.filter(entity_roles__in=[executor_type])
    executor_exists = executors.exists()

    if (
        subexecutor_type in instance.entity_roles.all()
        and subexecutor_exists
        and not executor_exists
    ):
        for subexecutor in subexecutors:
            subexecutor.entity_roles.remove(subexecutor_type)
            subexecutor.save()
