from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.files import File
from django.forms.models import model_to_dict
from .models import WillRepo
import json
from services.will_generator.will_generator import WillObjectGenerator
from services.LPA_generator.LPA_generator import LPAGenerator
from core.serializers import WillOrderSerializer
# from lambda_service import Generator


@receiver(pre_save, sender=WillRepo, dispatch_uid="generate_pdf_from_object")
def set_paid_order_invoice(sender, instance, using, **kwargs):
    if hasattr(instance, "skip_signal") and instance.skip_signal == True:
        return

    # signal to create and set pdf will on save from object.
    # if instance.order.order_type == "WILL":
    #     if not instance.content:
    #         instance.content = WillObjectGenerator(instance.order).generate_will_object(
    #             string=True, blocksOnly=False
    #         )

    #     will_object = json.loads(instance.content)
    #     pdf = WillObjectGenerator(
    #         instance.order).generate_pdf(will_object["blocks"])

    # elif instance.order.order_type == "LPA":
    #     pdf = LPAGenerator(instance.order).get_generated_pdf()

    # instance.will.save(instance.get_order_filename(), File(pdf), save=False)

    # if instance.order.order_type == "WILL":
    #     order_data = model_to_dict(instance.order)
    #     data = WillOrderSerializer(order, labels=False).data
    #     user_data = model_to_dict(instance.order.user)

    #     if not instance.content:
    #         instance.content = WillObjectGenerator(instance.order).generate_will_object(
    #             string=True, blocksOnly=False
    #         )

    #     will_object = json.loads(instance.content)
    #     pdf = WillObjectGenerator(
    #         instance.order).generate_pdf(will_object["blocks"])

    # elif instance.order.order_type == "LPA":
    #     pdf = LPAGenerator(instance.order).get_generated_pdf()

    # instance.will.save(instance.get_order_filename(), File(pdf), save=False)
