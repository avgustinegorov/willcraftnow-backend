import os

from django.db import models
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


class FAQ(models.Model):
    """Defines a FAQ object that is used on the site for answering general
    commonly asked questions
    """

    # Auto-Now (add) fields to keep track of model changes
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)

    title = models.CharField(max_length=100)
    content = models.TextField()

    def __str__(self):
        return self.title

    class Admin:
        list_display = ["__all__"]


class TipsKeyWords(models.Model):
    """Defines a Tips and Key Words object that is used on the site for answering general commonly asked questions in the interface"""

    STEP_CHOICES = [
        ("YOUR_DETAILS", "Your Details"),
        ("SPECIFIC_ASSETS", "Specific Assets"),
        ("RESIDUAL_ASSETS", "Residual Assets"),
        ("APPOINTMENTS", "Appointments"),
        ("ARRANGEMENTS", "Arrangements"),
        ("SUMMARY", "Summary"),
        ("CHECKOUT", "Checkout"),
    ]

    ORDER_TYPE_CHOICES = [
        ("ALL", "All"),
        ("WILL", "WILL"),
    ]

    TIP_TYPE_CHOICES = [
        ("KEY_WORDS", "Key Words"),
        ("DID_YOU_KNOW", "Did You Know"),
    ]

    # Auto-Now (add) fields to keep track of model changes
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)

    title = models.CharField(max_length=100)
    content = models.TextField()

    step = models.CharField(max_length=20, choices=STEP_CHOICES)
    order_type = models.CharField(max_length=20, choices=ORDER_TYPE_CHOICES)
    tip_type = models.CharField(max_length=20, choices=TIP_TYPE_CHOICES)

    def __str__(self):
        return f"{self.title} ({self.order_type}-{self.step})"

    class Admin:
        list_display = ["__all__"]
