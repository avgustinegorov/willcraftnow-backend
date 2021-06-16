from django.conf import settings
from django.db.models.signals import (m2m_changed, post_save, pre_delete,
                                      pre_save)
from django.dispatch import receiver
from django.utils import timezone

from assets.models import Allocation
from core.models import WillOrder
from lastrites.models import WillInstructions, WillLastRites
from partners.models import ApplicationStore, Partners
from persons.models import EntityStore

from .services import InvoiceService
from .discount_rule.discount_rule import discount_rules
from .models import Discount, Invoice, OrderLimit


@receiver(post_save, sender=Invoice, dispatch_uid="willorder_post_save_signal")
def update_willorder_limit(
    sender, instance, created, using, update_fields, *args, **kwargs
):
    """Updates the will order limit model when the invoice is paid with all the relevant details and the limits."""
    # only triggers when 'been_paid' is passed to the kwarg update field when calling save method on invoice
    if update_fields and "been_paid" in update_fields:
        order_details = InvoiceService(instance.order).limit_details
        # goes through all the current order_details and sets limits on them when the invoice is paid
        for order_detail, order_numbers in order_details.items():
            try:
                willorder_limit = OrderLimit.objects.get(
                    invoice=instance, detail=order_detail
                )
                if order_numbers > willorder_limit.limit:
                    willorder_limit.limit = order_numbers
                    willorder_limit.save()
            except OrderLimit.DoesNotExist:
                OrderLimit.objects.create(
                    invoice=instance, detail=order_detail, limit=order_numbers
                )

        # update discounts as redeemed when billed
        discounts = instance.discounts.all()
        # sets record on discounts when paid
        if discounts.exists():
            for discount in discounts:
                discount.redeemed += 1
                discount.save()
                discount.redeemed_by.add(instance.order.user)


@receiver(post_save, sender=WillOrder, dispatch_uid="willorder_create_invoice_signal")
@receiver(post_save, sender=Allocation, dispatch_uid="allocation_create_invoice_signal")
@receiver(
    post_save,
    sender=WillInstructions,
    dispatch_uid="willinstructions_create_invoice_signal",
)
@receiver(
    post_save, sender=WillLastRites, dispatch_uid="willlastrites_create_invoice_signal"
)
@receiver(post_save, sender=EntityStore, dispatch_uid="person_create_invoice_signal")
@receiver(
    m2m_changed,
    sender=EntityStore.entity_roles.through,
    dispatch_uid="person_update_invoice_signal",
)
@receiver(pre_delete, sender=WillOrder, dispatch_uid="willorder_delete_invoice_signal")
@receiver(
    pre_delete, sender=Allocation, dispatch_uid="allocation_delete_invoice_signal"
)
@receiver(
    pre_delete,
    sender=WillInstructions,
    dispatch_uid="willinstructions_delete_invoice_signal",
)
@receiver(
    pre_delete, sender=WillLastRites, dispatch_uid="willlastrites_delete_invoice_signal"
)
@receiver(pre_delete, sender=EntityStore, dispatch_uid="person_create_invoice_signal")
def create_order_amended_invoice(sender, instance, using, **kwargs):
    """Signal to create the Amended Invoice as soon as the WillOrder details exceeds the
    order limit and to delete if less. Only operates when there is an existing paid invoice."""

    sender_name = sender._meta.model.__name__

    if sender_name == "WillOrder":
        order = instance
    elif sender_name == "Allocation":
        order = instance.asset_store.order
    else:
        order = instance.order

    if Invoice.objects.filter(
        order=order, been_paid=True, parent_invoice=None
    ).exists():
        amended_invoice_required = False
        latest_paid_invoice = order.invoice.latest_paid()
        print("latest_paid_invoice", latest_paid_invoice)
        if latest_paid_invoice:
            order_details = InvoiceService(order).limit_details

            for order_detail, order_numbers in order_details.items():
                try:
                    willorder_limit = OrderLimit.objects.get(
                        invoice=latest_paid_invoice, detail=order_detail
                    )
                    if order_numbers > willorder_limit.limit:
                        amended_invoice_required = True
                except OrderLimit.DoesNotExist:
                    amended_invoice_required = True

        parent_invoice = Invoice.objects.get(order=order, parent_invoice=None)

        if amended_invoice_required:
            if Invoice.objects.filter(
                order=order, been_paid=False, parent_invoice=parent_invoice
            ).exists():
                print("UPDATE AMENDED INVOICE")
                order.invoice.latest().update_invoice()
            else:
                Invoice.objects.create(
                    order=order, parent_invoice=parent_invoice)
        else:
            print("DELETE AMENDED INVOICE")
            if Invoice.objects.filter(
                order=order, been_paid=False, parent_invoice=parent_invoice
            ).exists():
                Invoice.objects.get(
                    order=order, parent_invoice=parent_invoice, been_paid=False
                ).delete()


@receiver(
    post_save, sender=WillOrder, dispatch_uid="willorder_create_amended_invoice_signal"
)
def create_order_invoice(sender, instance, created, using, **kwargs):
    """Signal to create the Invoice as soon as the WillOrder is created"""

    # Create invoice if it doesn't already exist
    if (
        created
        and not Invoice.objects.filter(
            order__order_number=instance.order_number
        ).exists()
    ):
        invoice = Invoice(order=instance)
        # Saving it in reverse to avoid having this signal called again
        invoice.save()

        for slug, cls in discount_rules.get_all_discount_rules():
            if cls.can_user_have_access(instance.user, invoice):
                cls.apply_discount(instance.user, invoice)


@receiver(pre_save, sender=Invoice, dispatch_uid="willorder_set_paid_invoice_signal")
def set_paid_order_invoice(sender, instance, using, **kwargs):
    # signal to insert the payment date and expiry date at the time of payment
    try:
        existing_invoice = Invoice.objects.get(id=instance.id)
    except Invoice.DoesNotExist:
        existing_invoice = None

    if (
        existing_invoice
        and instance.been_paid
        and existing_invoice.been_paid != instance.been_paid
    ):
        # setting date paid if its not already there
        instance.date_paid = (
            timezone.now() if not instance.date_paid else instance.date_paid
        )
        # setting expiry time, if field is filled, defaults to settings
        expiry_time = (
            settings.WILL_EXPIRY if not instance.expiry_time else instance.expiry_time
        )
        instance.expiry_date = instance.date_paid + \
            timezone.timedelta(days=expiry_time)
