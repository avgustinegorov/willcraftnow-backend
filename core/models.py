import json
import random
import string
import requests

from django.db import transaction
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.http import HttpResponse


from core.enums import ORDER_TYPES
from services.s3.s3_interface import S3Interface
from utils.decorators import ExclusiveOrderType


def random_string_generator(size=8, chars=string.ascii_uppercase + string.digits):
    return "".join(random.choice(chars) for _ in range(size))


class WillOrder(models.Model):
    """Defines a model that represents a Will
    generated from User input.
    Collection of all individual parts of a wall -
    that is used to generate the PDF
    """

    # Auto-Now (add) fields to keep track of model changes
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)

    # User that created this order
    # This is nullable because a user is allowed to create an order before he's signed in
    # But this needs to be filled BEFORE billing
    user = models.ForeignKey(
        "willcraft_auth.WillCraftUser",
        on_delete=models.CASCADE,
        null=True,
        related_name="user_orders",
    )

    # Order details
    # Generated dynamically with a UID generator
    order_number = models.CharField(max_length=120, unique=True)
    order_type = models.CharField(
        max_length=120, choices=ORDER_TYPES, blank=False)

    tncs = models.BooleanField(default=False)  # Terms & Conditions
    disclaimer = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user}_{self.order_type}_{self.order_number}"

    def save(self, *args, **kwargs):
        # Setting the order number as a random uuid if it's not filled
        if not self.order_number:
            order_number = f"{self.order_type}-{random_string_generator()}"
            while WillOrder.objects.filter(order_number=order_number).exists():
                order_number = f"{self.order_type}-{random_string_generator()}"
            self.order_number = order_number

        super(WillOrder, self).save(*args, **kwargs)

    def success(self, json):
        return requests.post(
            'https://ry0zlvi1og.execute-api.ap-southeast-1.amazonaws.com/Prod/generator/',
            data=json,
            headers={'Content-Type': 'application/json'})


def get_pdf_will_upload_path(instance, filename):
    return f"will_repo/{filename}"


class WillRepoManager(models.Manager):

    def next_version(self):
        latest = self.latest('id')
        version = 1
        if latest:
            version = latest.version + 1
        return version

    def next_filename(self):
        if self.instance.__class__.__name__ == 'WillOrder':
            version = self.next_version()
            order_number = self.instance.order_number
            return f"will_repo/{order_number}_v{version}.pdf"

    def upload_url(self):
        if self.instance.__class__.__name__ == 'WillOrder':
            return S3Interface().get_put_presigned_url(self.next_filename())

    def download_url(self):
        if self.instance.__class__.__name__ == 'WillOrder':
            latest = self.latest()
            if latest:
                if settings.STAGE != "LOCAL":
                    filename = "media/" + latest.will.name
                    return S3Interface().get_download_presigned_url(filename)
                else:
                    return f"/media/{latest.will.name}"

            return None

    def latest(self, *args, **kwargs):
        # this is only for the related manager instance
        # where this is called: order.will_repo.latest()
        # the instance here is a WillOrder instance
        if self.instance.__class__.__name__ == 'WillOrder':
            queryset = self.get_queryset()
            if not queryset.exists():
                return None
            else:
                return queryset.latest(*args, **kwargs)

        return super().latest(*args, **kwargs)


class WillRepo(models.Model):

    REPO_TYPES = [
        ("GENERATED", "Generated Will"),
        ("USER_UPLOADED", "Uploaded Will"),
        ("LAWYER_AMENDED", "Lawyer Amended"),
    ]

    order = models.ForeignKey(
        "WillOrder", on_delete=models.CASCADE, null=True, related_name="will_repo"
    )
    type = models.CharField(
        max_length=120, choices=REPO_TYPES, default="GENERATED")
    will = models.FileField(upload_to=get_pdf_will_upload_path, null=True)
    content = models.TextField(null=True)
    version = models.IntegerField(default=1)
    downloaded = models.IntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    objects = WillRepoManager()

    class Meta:
        get_latest_by = ['id', 'version']

    def __str__(self):
        return str(f"[REPO]-{self.order}")

    def save(self, *args, **kwargs):

        if not self.content and self.type != "GENERATED":
            raise ValidationError("Will object is required.")

        if not self.pk:
            self.version = self.order.will_repo.next_version()

        super(WillRepo, self).save(*args, **kwargs)
