
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import *


@receiver(
    post_save,
    sender=WitnessService,
    dispatch_uid="witness_service_post_save_update_invoice",
)
@receiver(
    post_save,
    sender=ReviewService,
    dispatch_uid="review_service_post_save_update_invoice",
)
@receiver(
    post_save,
    sender=LPACertificateService,
    dispatch_uid="lpa_service_post_save_update_invoice",
)
def update_invoice(sender, instance, *args, **kwargs):
    """Updates the Substitute allocation if it is a main allocation"""
    # check if allocation is a substitute allocation
    invoice = instance.order.invoice.latest()
    invoice.update_invoice()
    invoice.save()
