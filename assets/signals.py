from decimal import Decimal

from django.db.models.signals import post_save, pre_delete, pre_save
from django.dispatch import receiver

from persons.models import EntityType

from .models import Allocation


@receiver(pre_save, sender=Allocation, dispatch_uid="allocation_pre_save_person_signal")
def update_entity_appointment_type(sender, instance, *args, **kwargs):
    """Updates the person attached to the allocation to have the
    appointment_type of Entity
    """
    entity_type, _ = EntityType.objects.get_or_create(type_name="BENEFICIARY")
    if entity_type not in instance.entity.entity_roles.all():
        # Update the person types of the witness's person(s)
        instance.entity.entity_roles.add(entity_type)


@receiver(
    pre_delete, sender=Allocation, dispatch_uid="allocation_pre_delete_person_signal"
)
def remove_entity_appointment_type(sender, instance, *args, **kwargs):
    """Removes the person type of "Beneficary" attached to the allocation
    instance (if any)
    """
    if len(Allocation.objects.filter(entity=instance.entity)
            .exclude(id=instance.id)) == 0:

        # Removing the entity entity_type
        entity_type = EntityType.objects.get(type_name="BENEFICIARY")
        instance.entity.entity_roles.remove(entity_type)


@receiver(
    pre_save,
    sender=Allocation,
    dispatch_uid="allocation_pre_save_effective_allocation_signal",
)
def update_effective_allocation(sender, instance, *args, **kwargs):
    """Updates the allocation if it is a substitute allocation"""
    # check if allocation is a substitute allocation
    if instance.parent_allocation:
        parent_allocation = Allocation.objects.get(
            id=instance.parent_allocation.id)

        # calculate effective allocation percentage
        if instance.allocation_percentage:
            effective_allocation_percentage = (
                Decimal(instance.allocation_percentage)
                * Decimal(parent_allocation.allocation_percentage)
                / Decimal("100")
            )

            # check and correct rounding issues
            associated_sub_allocations = Allocation.objects.filter(
                parent_allocation=instance.parent_allocation.id
            ).values_list("allocation_percentage", flat=True)
            total_sub_allocations = sum(associated_sub_allocations)
            if 99.9 < total_sub_allocations + effective_allocation_percentage < 100:
                effective_allocation_percentage = 100 - total_sub_allocations

            instance.effective_allocation_percentage = effective_allocation_percentage

        if instance.allocation_amount:
            instance.effective_allocation_amount = instance.allocation_amount


@receiver(
    post_save,
    sender=Allocation,
    dispatch_uid="allocation_post_save_effective_allocation_signal",
)
def update_main_effective_allocation(sender, instance, *args, **kwargs):
    """Updates the Substitute allocation if it is a main allocation"""
    # check if allocation is a substitute allocation
    if not instance.parent_allocation:
        sub_entities = Allocation.objects.filter(
            parent_allocation=instance, asset=instance.asset
        )
        if sub_entities:
            for sub_entity in sub_entities:
                sub_entity.save()


@receiver(
    post_save,
    sender=Allocation,
    dispatch_uid="allocation_post_save_update_invoice",
)
def update_invoice(sender, instance, *args, **kwargs):
    """Updates the Substitute allocation if it is a main allocation"""
    # check if allocation is a substitute allocation
    invoice = instance.asset_store.order.invoice.latest()
    invoice.update_invoice()
    invoice.save()
